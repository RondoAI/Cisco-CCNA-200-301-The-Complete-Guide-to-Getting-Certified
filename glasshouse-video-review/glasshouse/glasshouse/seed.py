"""
Seed data so the system runs and demonstrates itself offline.

These mimic the shape of real GDELT/ACLED/citizen inputs. One case is rigged to
show the pipeline DOING ITS JOB: a recycled clip reattached to a new event, which
the verifier marks DISPUTED instead of letting corroboration paper over it.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .ingest import CitizenMediaAdapter
from .models import Event, Source, SourceKind

NOW = datetime.now(timezone.utc)


def _src(kind, domain, days_ago=0, content_hash=None, url=None):
    return Source(kind=kind, domain=domain, url=url,
                  published_at=NOW - timedelta(days=days_ago),
                  content_hash=content_hash)


def seed_events() -> list[Event]:
    events: list[Event] = []

    # 1) Strongly corroborated: wire + NGO + outlet, independent domains.
    events.append(Event(
        headline="Reported airstrike on market, El Fasher",
        lat=13.6279, lon=25.3494, region="Sudan", occurred_at=NOW,
        sources=[
            _src(SourceKind.WIRE, "reuters.com", 0, url="https://reuters.com/x"),
            _src(SourceKind.NGO, "acleddata.com", 0),
            _src(SourceKind.OUTLET, "aljazeera.com", 0),
        ],
    ))

    # 2) Emerging: a single citizen clip, geotagged, uploader already stripped.
    citizen = CitizenMediaAdapter(raw_records=[{
        "claim": "Protest dispersal reported near Azadi Tower, Tehran",
        "lat": 35.6997, "lon": 51.3380, "region": "Iran",
        "occurred_at": NOW,
        "platform": "telegram", "post_url": "https://t.me/channel/123",
        "content_hash": "hash_tehran_clip_A",
        # raw identifying junk that MUST be dropped:
        "handle": "@eyewitness_user", "phone": "+98...", "device_id": "abc123",
    }]).fetch()
    events.extend(citizen)

    # 3) DISPUTED on purpose: a clip whose content hash matches an event from
    #    days ago (recycled footage), reattached as if fresh.
    old_hash = "hash_recycled_2021"
    events.append(Event(
        headline="Old footage (baseline event, days ago)",
        lat=33.3152, lon=44.3661, region="Iraq", occurred_at=NOW - timedelta(days=900),
        sources=[_src(SourceKind.OUTLET, "example-news.com", 900,
                      content_hash=old_hash)],
    ))
    events.append(Event(
        headline="VIRAL: 'breaking' clip near Baghdad (actually recycled)",
        lat=33.3152, lon=44.3661, region="Iraq", occurred_at=NOW,
        sources=[
            _src(SourceKind.CITIZEN, "x.com", 0, content_hash=old_hash),
            _src(SourceKind.AGGREGATOR, "viralfeed.example", 0,
                 content_hash=old_hash),
        ],
    ))

    return events
