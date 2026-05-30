"""
Ingestion adapters.

All external data enters through an Adapter so the rest of the system never
talks to the raw internet directly. This is also where policy is enforced at the
boundary: citizen media is stripped of identity here, before it becomes a Source.

GDELT is the open backbone (free, global, real-time, CAMEO-coded). The fetch
code below is the real GDELT 2.0 "last 15 minutes" export shape. In a sandbox
without network access it falls back to bundled samples, so the pipeline always
runs; flip GLASSHOUSE_LIVE=1 in a networked environment to pull live.

Twitter/X note: there is intentionally no firehose scraper. Citizen footage is
pulled *targeted* — by location/keyword/time around a developing event — via a
licensed provider, then sanitized. That is cheaper, narrower, and defensible.
"""

from __future__ import annotations

import csv
import io
import os
import zipfile
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from urllib.request import urlopen

from .models import Event, Source, SourceKind
from .privacy import citizen_source

LIVE = os.environ.get("GLASSHOUSE_LIVE") == "1"


class Adapter(ABC):
    name: str

    @abstractmethod
    def fetch(self) -> list[Event]:
        ...


class GDELTAdapter(Adapter):
    """Pulls the rolling GDELT 2.0 Events export. Each row already encodes
    actors, an action, a geolocation and source URLs — we map a subset."""
    name = "gdelt"
    LATEST = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

    def fetch(self) -> list[Event]:
        if not LIVE:
            return []  # offline: seed.py provides representative GDELT-style events
        try:
            listing = urlopen(self.LATEST, timeout=20).read().decode()
            export_url = next(
                line.split()[-1] for line in listing.splitlines()
                if "export.CSV.zip" in line)
            blob = urlopen(export_url, timeout=30).read()
            z = zipfile.ZipFile(io.BytesIO(blob))
            raw = z.read(z.namelist()[0]).decode("utf-8", "ignore")
            return self._parse(raw)
        except Exception as e:  # network/format issues never crash ingestion
            print(f"[gdelt] live fetch failed, skipping: {e}")
            return []

    def _parse(self, raw: str) -> list[Event]:
        events: list[Event] = []
        for row in csv.reader(io.StringIO(raw), delimiter="\t"):
            try:
                lat, lon = float(row[56]), float(row[57])
                when = datetime.strptime(row[1], "%Y%m%d").replace(tzinfo=timezone.utc)
                url = row[60]
                domain = url.split("/")[2] if "//" in url else "gdelt"
                events.append(Event(
                    headline=f"{row[6] or 'Actor'} — event code {row[26]}",
                    lat=lat, lon=lon, occurred_at=when,
                    region=row[51] or "",
                    sources=[Source(kind=SourceKind.AGGREGATOR, domain=domain,
                                    url=url, published_at=when)],
                ))
            except (ValueError, IndexError):
                continue
        return events


class RSSAdapter(Adapter):
    """Generic outlet/NGO RSS intake. Stub kept minimal; real version parses
    feeds and runs NER + geocoding to place the event."""
    name = "rss"

    def __init__(self, feeds: list[str] | None = None):
        self.feeds = feeds or []

    def fetch(self) -> list[Event]:
        return []  # wire up feedparser + geocoder here


class CitizenMediaAdapter(Adapter):
    """Targeted citizen-footage intake. Receives raw records (from a licensed
    provider, NOT a firehose scrape) and routes EACH through privacy stripping
    before anything else can see it."""
    name = "citizen"

    def __init__(self, raw_records: list[dict] | None = None):
        self.raw_records = raw_records or []

    def fetch(self) -> list[Event]:
        events: list[Event] = []
        for raw in self.raw_records:
            src = citizen_source(raw)  # identity gone at the boundary
            events.append(Event(
                headline=raw.get("claim", "Citizen-reported incident"),
                lat=float(raw["lat"]), lon=float(raw["lon"]),
                occurred_at=raw.get("occurred_at", datetime.now(timezone.utc)),
                region=raw.get("region", ""),
                sources=[src],
            ))
        return events
