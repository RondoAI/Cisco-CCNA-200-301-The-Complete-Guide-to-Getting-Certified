"""
Congress adapter — the real United States roster for THE RECORD.

Pulls every current U.S. Senator and Representative (all states) from the open,
keyless `unitedstates/congress-legislators` dataset — the canonical community
source built from official Bioguide / GPO / C-SPAN data. No API key required.

Like the GDELT adapter, it goes live only with GLASSHOUSE_LIVE=1 (so a plain
import stays fast and offline-safe); otherwise it returns a small bundled sample
and the live pull fills in the full ~535-member roster on demand. Records may
also be injected directly (tests, or a cached snapshot).

What this gives us today, sourced and real: who is in office, their chamber,
state, party, House district, term end, and the year their seat is next
contested. Voting records, statements and funding are layered on next through
the keyed Congress.gov / FEC adapters — the data model and endpoints are already
here waiting for them.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from .models import Source, SourceKind
from .record import Level, Official

LIVE = os.environ.get("GLASSHOUSE_LIVE") == "1"

CURRENT_URL = ("https://unitedstates.github.io/congress-legislators/"
               "legislators-current.json")

# Tiny offline fallback so the roster is never empty without network. Kept to
# stable facts (name, chamber, state, party); term/election left null offline.
OFFLINE_SAMPLE = [
    {"name": {"official_full": "Maria Cantwell"},
     "id": {"bioguide": "C000127", "wikidata": "Q22255"},
     "terms": [{"type": "sen", "state": "WA", "party": "Democrat"}]},
    {"name": {"official_full": "Alex Padilla"},
     "id": {"bioguide": "P000145", "wikidata": "Q120365"},
     "terms": [{"type": "sen", "state": "CA", "party": "Democrat"}]},
    {"name": {"official_full": "Ted Cruz"},
     "id": {"bioguide": "C001098", "wikidata": "Q2036942"},
     "terms": [{"type": "sen", "state": "TX", "party": "Republican"}]},
    {"name": {"official_full": "Rick Scott"},
     "id": {"bioguide": "S001217", "wikidata": "Q4504850"},
     "terms": [{"type": "sen", "state": "FL", "party": "Republican"}]},
]


class CongressAdapter:
    name = "congress-legislators"

    def __init__(self, records: list[dict] | None = None):
        self._records = records  # injected snapshot (tests / cache)

    def _raw(self) -> list[dict]:
        if self._records is not None:
            return self._records
        if not LIVE:
            return OFFLINE_SAMPLE
        try:
            req = Request(CURRENT_URL, headers={"User-Agent": "glasshouse/0.2"})
            return json.loads(urlopen(req, timeout=30).read())
        except Exception as e:  # never crash bootstrap on a network hiccup
            print(f"[congress] live fetch failed, using offline sample: {e}")
            return OFFLINE_SAMPLE

    def fetch(self) -> list[Official]:
        return [self._to_official(r) for r in self._raw()]

    @staticmethod
    def _to_official(r: dict) -> Official:
        term = r["terms"][-1]
        is_sen = term.get("type") == "sen"
        end = _parse_date(term.get("end"))
        ids = r.get("id", {})
        return Official(
            name=(r.get("name", {}).get("official_full")
                  or f"{r.get('name', {}).get('first', '')} "
                     f"{r.get('name', {}).get('last', '')}".strip()),
            office="U.S. Senator" if is_sen else "U.S. Representative",
            body="U.S. Senate" if is_sen else "U.S. House of Representatives",
            jurisdiction=term.get("state", ""),
            level=Level.FEDERAL,
            party=term.get("party", ""),
            district=(str(term["district"])
                      if not is_sen and term.get("district") is not None else None),
            term_end=end,
            next_election=(end.year - 1 if end else None),
            qid=ids.get("wikidata"),
            bioguide=ids.get("bioguide"),
            source=Source(
                kind=SourceKind.OFFICIAL, domain="unitedstates.github.io",
                url=CURRENT_URL, published_at=datetime.now(timezone.utc)),
        )


def _parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
