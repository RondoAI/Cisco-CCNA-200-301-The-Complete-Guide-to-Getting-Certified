"""Tests for the learning + enrichment layer."""

from datetime import datetime, timezone

from glasshouse.enrich import Knowledge, enrich
from glasshouse.learning import (ReputationStore, independent_clusters,
                                 learn_from_outcome, score_event)
from glasshouse.models import Event, Source, SourceKind, Confidence

NOW = datetime.now(timezone.utc)


def test_reputation_rises_with_confirmations_and_falls_with_debunks():
    reps = ReputationStore()
    good = Source(SourceKind.OUTLET, "reliable.example")
    bad = Source(SourceKind.AGGREGATOR, "rumor.example")
    g0, b0 = reps.get(good).trust, reps.get(bad).trust
    for _ in range(10):
        learn_from_outcome(Event("e", 0, 0, NOW, sources=[good]), reps,
                           confirmed=True, by="ground_truth")
        learn_from_outcome(Event("e", 0, 0, NOW, sources=[bad]), reps,
                           confirmed=False)
    assert reps.get(good).trust > g0      # learned to trust it more
    assert reps.get(bad).trust < b0       # learned to trust it less
    assert reps.get(good).trust > reps.get(bad).trust


def test_reposts_do_not_count_as_independent():
    # one wire + two reposts of the SAME media => one independent voice
    h = "same_clip"
    sources = [
        Source(SourceKind.WIRE, "reuters.com", content_hash=h),
        Source(SourceKind.OUTLET, "repost-a.example", content_hash=h),
        Source(SourceKind.OUTLET, "repost-b.example", content_hash=h),
    ]
    clusters = independent_clusters(sources)
    assert len(clusters) == 1             # echo chamber collapsed to one voice


def test_syndicated_sources_cluster_together():
    sources = [Source(SourceKind.WIRE, "apnews.com"),
               Source(SourceKind.OUTLET, "abcnews.go.com")]  # both AP
    assert len(independent_clusters(sources)) == 1


def test_score_uses_learned_reputation_and_independence():
    reps = ReputationStore()
    # genuinely independent, distinct sources
    ev = Event("airstrike on market", 13.6, 25.3, NOW, sources=[
        Source(SourceKind.WIRE, "reuters.com"),
        Source(SourceKind.NGO, "acleddata.com"),
    ])
    score_event(ev, reps)
    assert ev.confidence in (Confidence.CORROBORATED, Confidence.CONFIRMED)
    assert any(c.name.startswith("reputation:") for c in ev.audit)
    assert any(c.name == "independent_clusters" for c in ev.audit)


def test_recycled_media_disputes_even_with_two_sources():
    reps = ReputationStore()
    ev = Event("viral clip", 33.3, 44.3, NOW, sources=[
        Source(SourceKind.CITIZEN, "x.com", content_hash="old"),
        Source(SourceKind.AGGREGATOR, "viral.example", content_hash="old"),
    ])
    ev.enrichment["recycled"] = True       # set by DedupEnricher upstream
    score_event(ev, reps)
    assert ev.confidence == Confidence.DISPUTED


def test_enrichment_geocodes_classifies_and_flags_recycled():
    k = Knowledge()
    e1 = Event("Airstrike reported in El Fasher", 0, 0, NOW,
               sources=[Source(SourceKind.WIRE, "reuters.com",
                               content_hash="clipX")])
    enrich(e1, k)
    assert (e1.lat, e1.lon) == (13.6279, 25.3494)     # geocoded from gazetteer
    assert "armed_conflict" in e1.tags                # classified
    assert not e1.enrichment.get("recycled")          # first sighting

    e2 = Event("Same clip resurfaces", 1, 1, NOW,
               sources=[Source(SourceKind.CITIZEN, "x.com",
                               content_hash="clipX")])
    enrich(e2, k)
    assert e2.enrichment.get("recycled") is True      # learned from e1
