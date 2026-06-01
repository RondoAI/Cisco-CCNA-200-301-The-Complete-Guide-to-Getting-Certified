"""
Enrichment pipeline — "refine and enrich the data from each plugin."

Every plugin's raw output flows through an ordered list of Enrichers before it
becomes a trusted event. Each enricher does ONE job, learns from existing
knowledge (the gazetteer, the label map, the hashes already seen), and records
WHAT it added into event.enrichment — so enrichment, like verification, is a
receipt, not magic.

The bodies here are deliberately simple/stubbed but the interface is the real
one: swap a gazetteer for a geocoding API, the keyword map for a classifier, the
hash set for perceptual-hash matching — the pipeline doesn't change.
"""

from __future__ import annotations

from typing import Protocol

from .models import Event


class Enricher(Protocol):
    name: str
    def apply(self, event: Event, knowledge: "Knowledge") -> None: ...


class Knowledge:
    """Accumulated state the enrichers learn from. Grows as plugins feed data."""
    def __init__(self) -> None:
        # tiny gazetteer: place -> (lat, lon). Real version: a geocoding service.
        self.gazetteer: dict[str, tuple[float, float]] = {
            "el fasher": (13.6279, 25.3494), "tehran": (35.6997, 51.3380),
            "khartoum": (15.5007, 32.5599), "baghdad": (33.3152, 44.3661),
        }
        # CAMEO-ish event-type keywords. Real version: a trained classifier.
        self.labels: dict[str, list[str]] = {
            "armed_conflict": ["airstrike", "shelling", "explosion", "clashes"],
            "protest": ["protest", "demonstration", "rally", "dispersal"],
            "diplomacy": ["talks", "summit", "agreement", "deal", "sanctions"],
        }
        self.seen_hashes: set[str] = set()


class GeocodeEnricher:
    name = "geocode"
    def apply(self, event: Event, k: Knowledge) -> None:
        if event.lat or event.lon:
            return
        hay = f"{event.headline} {event.region}".lower()
        for place, (lat, lon) in k.gazetteer.items():
            if place in hay:
                event.lat, event.lon = lat, lon
                event.enrichment["geocode"] = f"matched '{place}'"
                return


class ClassifyEnricher:
    name = "classify"
    def apply(self, event: Event, k: Knowledge) -> None:
        hay = event.headline.lower()
        for label, kws in k.labels.items():
            if any(kw in hay for kw in kws) and label not in event.tags:
                event.tags.append(label)
        if event.tags:
            event.enrichment["classify"] = event.tags.copy()


class DedupEnricher:
    """Learns from existing data: if a clip's media hash was already seen on a
    PRIOR event, flag it recycled so the scorer can dispute it."""
    name = "dedup"
    def apply(self, event: Event, k: Knowledge) -> None:
        hashes = [s.content_hash for s in event.sources if s.content_hash]
        if any(h in k.seen_hashes for h in hashes):
            event.enrichment["recycled"] = True
        for h in hashes:
            k.seen_hashes.add(h)


DEFAULT_PIPELINE: list[Enricher] = [
    GeocodeEnricher(), ClassifyEnricher(), DedupEnricher()]


def enrich(event: Event, knowledge: Knowledge,
           pipeline: list[Enricher] | None = None) -> Event:
    for enricher in (pipeline or DEFAULT_PIPELINE):
        enricher.apply(event, knowledge)
    return event
