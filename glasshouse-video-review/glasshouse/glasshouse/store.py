"""
Storage. In-memory for the MVP, behind a tiny interface so it can be swapped for
Postgres/PostGIS later without touching the rest of the system.

The store also tracks every content hash it has ever seen, which is what lets the
recycled-media check catch a clip being reattached to a fresher event.
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from .models import Event
from .verify import verify


def _haversine_km(a: Event, b: Event) -> float:
    dlat, dlon = radians(b.lat - a.lat), radians(b.lon - a.lon)
    h = sin(dlat / 2) ** 2 + cos(radians(a.lat)) * cos(radians(b.lat)) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


class EventStore:
    def __init__(self) -> None:
        self._events: dict[str, Event] = {}
        self._seen_hashes: set[str] = set()

    def ingest(self, event: Event, merge_radius_km: float = 5.0) -> Event:
        """Verify, then either merge into a nearby same-day event (adding its
        sources strengthens corroboration) or store as new."""
        match = self._find_nearby(event, merge_radius_km)
        if match:
            match.sources.extend(event.sources)
            verify(match, self._seen_hashes)
            self._register_hashes(event)
            return match

        verify(event, self._seen_hashes)
        self._events[event.id] = event
        self._register_hashes(event)
        return event

    def _register_hashes(self, event: Event) -> None:
        for s in event.sources:
            if s.content_hash:
                self._seen_hashes.add(s.content_hash)

    def _find_nearby(self, event: Event, radius_km: float) -> Event | None:
        for e in self._events.values():
            same_day = abs((e.occurred_at - event.occurred_at).days) == 0
            if same_day and _haversine_km(e, event) <= radius_km:
                return e
        return None

    def all(self) -> list[Event]:
        return sorted(self._events.values(),
                      key=lambda e: e.occurred_at, reverse=True)

    def get(self, event_id: str) -> Event | None:
        return self._events.get(event_id)
