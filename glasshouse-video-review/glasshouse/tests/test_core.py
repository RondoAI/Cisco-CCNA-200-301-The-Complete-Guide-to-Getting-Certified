"""Tests for the two things that define the product: source protection and
verification. If these pass, the ethics are not aspirational — they hold."""

from datetime import datetime, timedelta, timezone

from glasshouse.models import Confidence, Event, Source, SourceKind
from glasshouse.privacy import citizen_source, redact_uploader
from glasshouse.store import EventStore
from glasshouse.verify import verify

NOW = datetime.now(timezone.utc)


def test_uploader_identity_is_stripped():
    raw = {"handle": "@witness", "phone": "+1", "device_id": "d1",
           "platform": "telegram", "content_hash": "h", "lat": 1, "lon": 2}
    safe = redact_uploader(raw)
    for leaky in ("handle", "phone", "device_id", "username", "ip"):
        assert leaky not in safe
    assert safe["platform"] == "telegram"          # verification data kept
    assert "dedup_token" in safe                    # one-way token only
    assert "@witness" not in safe["dedup_token"]    # not recoverable
    assert "handle" in safe["_redacted_fields"]     # provably dropped


def test_citizen_source_carries_no_identity():
    src = citizen_source({"handle": "@x", "platform": "x.com",
                          "content_hash": "h1"})
    assert src.kind == SourceKind.CITIZEN
    assert src.domain == "x.com"          # platform, not user
    # the Source dataclass has no field that could even hold a handle
    assert not hasattr(src, "uploader")


def test_single_source_is_unverified():
    ev = Event("lone claim", 0, 0, NOW,
               sources=[Source(SourceKind.CITIZEN, "telegram")])
    verify(ev)
    assert ev.confidence in (Confidence.UNVERIFIED, Confidence.EMERGING)
    assert ev.score < 0.5


def test_independent_corroboration_raises_confidence():
    ev = Event("airstrike", 13.6, 25.3, NOW, sources=[
        Source(SourceKind.WIRE, "reuters.com"),
        Source(SourceKind.NGO, "acleddata.com"),
        Source(SourceKind.OUTLET, "aljazeera.com"),
    ])
    verify(ev)
    assert ev.confidence in (Confidence.CORROBORATED, Confidence.CONFIRMED)
    assert ev.independent_domains() == {"reuters.com", "acleddata.com", "aljazeera.com"}


def test_recycled_media_is_disputed_not_trusted():
    """Even with two sources, reused footage must be flagged, not corroborated."""
    seen = {"recycled_hash"}
    ev = Event("viral breaking clip", 33.3, 44.3, NOW, sources=[
        Source(SourceKind.CITIZEN, "x.com", content_hash="recycled_hash"),
        Source(SourceKind.AGGREGATOR, "viral.example", content_hash="recycled_hash"),
    ])
    verify(ev, seen_hashes=seen)
    assert ev.confidence == Confidence.DISPUTED
    assert any(c.name == "recycled_media" and not c.passed for c in ev.audit)


def test_audit_trail_is_populated():
    ev = Event("x", 0, 0, NOW, sources=[Source(SourceKind.WIRE, "reuters.com")])
    verify(ev)
    names = {c.name for c in ev.audit}
    assert {"has_sources", "independent_corroboration", "source_quality",
            "recency_consistency", "recycled_media"} <= names


def test_store_merges_nearby_same_day_events():
    store = EventStore()
    a = Event("blast", 13.60, 25.30, NOW, sources=[Source(SourceKind.WIRE, "reuters.com")])
    b = Event("blast", 13.601, 25.301, NOW, sources=[Source(SourceKind.NGO, "acleddata.com")])
    store.ingest(a)
    store.ingest(b)
    assert len(store.all()) == 1                       # merged
    assert len(store.all()[0].independent_domains()) == 2  # corroboration grew
