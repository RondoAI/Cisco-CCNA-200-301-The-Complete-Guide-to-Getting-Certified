"""
Elections layer for THE RECORD — the political geography of the country.

Real, county-level presidential results (every county, multiple cycles) so the
map can zoom from nation → state → county and show where the votes actually went,
how counties lean, and which ones flipped between cycles. Public aggregate
returns only — vote totals by place, never anything about an individual voter.

Data: the open, keyless `tonmcg/US_County_Level_Election_Results_08-24` dataset,
which standardizes official county returns (ultimately the state election
offices). Live with GLASSHOUSE_LIVE=1; a small clearly-labelled SAMPLE otherwise,
and rows can be injected directly for tests.
"""

from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from .models import Source, SourceKind

LIVE = os.environ.get("GLASSHOUSE_LIVE") == "1"

SOURCE_TMPL = ("https://raw.githubusercontent.com/tonmcg/"
               "US_County_Level_Election_Results_08-24/master/"
               "{year}_US_County_Level_Presidential_Results.csv")

CYCLES = [2008, 2012, 2016, 2020, 2024]

# Offline placeholder — FAKE counties (FIPS 99xxx) so we never assert wrong real
# numbers without network. One flips D->R between cycles to exercise the logic.
OFFLINE_SAMPLE = {
    2020: [
        {"county_fips": "99001", "county_name": "Sample County A",
         "state_name": "Sample State", "votes_dem": "5200", "votes_gop": "4800",
         "total_votes": "10000"},
        {"county_fips": "99003", "county_name": "Sample County B",
         "state_name": "Sample State", "votes_dem": "3000", "votes_gop": "7000",
         "total_votes": "10000"},
    ],
    2024: [
        {"county_fips": "99001", "county_name": "Sample County A",
         "state_name": "Sample State", "votes_dem": "4700", "votes_gop": "5300",
         "total_votes": "10000"},   # flipped D -> R
        {"county_fips": "99003", "county_name": "Sample County B",
         "state_name": "Sample State", "votes_dem": "2800", "votes_gop": "7200",
         "total_votes": "10000"},
    ],
}


@dataclass
class CountyResult:
    fips: str
    county: str
    state: str
    year: int
    votes_dem: int
    votes_gop: int
    total_votes: int
    sources: list[Source] = field(default_factory=list)

    @property
    def winner(self) -> str:
        return "R" if self.votes_gop > self.votes_dem else (
            "D" if self.votes_dem > self.votes_gop else "T")

    @property
    def margin_pct(self) -> float:
        """Signed margin: positive = Republican lean, negative = Democratic."""
        if not self.total_votes:
            return 0.0
        return round((self.votes_gop - self.votes_dem) / self.total_votes * 100, 2)

    @property
    def lean(self) -> str:
        m = abs(self.margin_pct)
        bucket = "tossup" if m < 5 else "lean" if m < 15 else "solid"
        return f"{bucket}_{self.winner}" if self.winner != "T" else "tied"

    def to_public_dict(self) -> dict:
        return {"fips": self.fips, "county": self.county, "state": self.state,
                "year": self.year, "votes_dem": self.votes_dem,
                "votes_gop": self.votes_gop, "total_votes": self.total_votes,
                "winner": self.winner, "margin_pct": self.margin_pct,
                "lean": self.lean,
                "sources": [{"kind": s.kind.value, "domain": s.domain,
                             "url": s.url} for s in self.sources]}


class ElectionStore:
    def __init__(self) -> None:
        self._by_key: dict[tuple[int, str], CountyResult] = {}

    def add(self, r: CountyResult) -> CountyResult:
        if not r.sources:
            raise ValueError("CountyResult needs a source — provenance is mandatory")
        self._by_key[(r.year, r.fips)] = r
        return r

    def years(self) -> list[int]:
        return sorted({y for (y, _) in self._by_key})

    def by_year(self, year: int) -> list[CountyResult]:
        return [r for (y, _), r in self._by_key.items() if y == year]

    def county_history(self, fips: str) -> list[CountyResult]:
        return sorted((r for (y, f), r in self._by_key.items() if f == fips),
                      key=lambda r: r.year)

    def map_data(self, year: int) -> list[dict]:
        """Choropleth-ready: one row per county for the given cycle, keyed by
        FIPS to match the county GeoJSON. Drives the zoomable election map."""
        return [{"fips": r.fips, "winner": r.winner, "margin_pct": r.margin_pct,
                 "lean": r.lean, "total_votes": r.total_votes}
                for r in self.by_year(year)]

    def state_rollup(self, year: int) -> dict:
        states: dict[str, dict] = {}
        for r in self.by_year(year):
            s = states.setdefault(r.state, {"votes_dem": 0, "votes_gop": 0,
                                            "total_votes": 0, "counties": 0})
            s["votes_dem"] += r.votes_dem
            s["votes_gop"] += r.votes_gop
            s["total_votes"] += r.total_votes
            s["counties"] += 1
        for s in states.values():
            s["winner"] = "R" if s["votes_gop"] > s["votes_dem"] else "D"
            s["margin_pct"] = (round((s["votes_gop"] - s["votes_dem"])
                                     / s["total_votes"] * 100, 2)
                               if s["total_votes"] else 0.0)
        return dict(sorted(states.items()))

    def national_totals(self, year: int) -> dict:
        d = g = t = 0
        for r in self.by_year(year):
            d += r.votes_dem; g += r.votes_gop; t += r.total_votes
        return {"year": year, "votes_dem": d, "votes_gop": g, "total_votes": t,
                "winner": "R" if g > d else "D", "counties": len(self.by_year(year)),
                "margin_pct": round((g - d) / t * 100, 2) if t else 0.0}

    def closest_counties(self, year: int, n: int = 10) -> list[dict]:
        ranked = sorted(self.by_year(year), key=lambda r: abs(r.margin_pct))
        return [r.to_public_dict() for r in ranked[:n]]

    def flips(self, from_year: int, to_year: int) -> list[dict]:
        """Counties whose winner changed between two cycles — 'where it moved'."""
        out = []
        for (y, fips), r in self._by_key.items():
            if y != to_year:
                continue
            prev = self._by_key.get((from_year, fips))
            if prev and prev.winner != r.winner and "T" not in (prev.winner, r.winner):
                out.append({"fips": fips, "county": r.county, "state": r.state,
                            "from": prev.winner, "to": r.winner,
                            "from_margin": prev.margin_pct, "to_margin": r.margin_pct})
        return sorted(out, key=lambda x: (x["state"], x["county"]))


class CountyResultsAdapter:
    name = "tonmcg-county-presidential"

    def __init__(self, years: list[int] | None = None,
                 rows_by_year: dict[int, list[dict]] | None = None):
        self.years = years or [2020, 2024]   # two cycles -> current map + flips
        self._rows = rows_by_year            # injected (tests / offline)

    def fetch(self) -> list[CountyResult]:
        results: list[CountyResult] = []
        for year in self.years:
            for row in self._rows_for(year):
                r = self._to_result(row, year)
                if r:
                    results.append(r)
        return results

    def _rows_for(self, year: int) -> list[dict]:
        if self._rows is not None:
            return self._rows.get(year, [])
        if not LIVE:
            return OFFLINE_SAMPLE.get(year, [])
        try:
            url = SOURCE_TMPL.format(year=year)
            req = Request(url, headers={"User-Agent": "glasshouse/0.3"})
            raw = urlopen(req, timeout=45).read().decode("utf-8", "ignore")
            return list(csv.DictReader(io.StringIO(raw)))
        except Exception as e:
            print(f"[elections] live fetch {year} failed, using sample: {e}")
            return OFFLINE_SAMPLE.get(year, [])

    @staticmethod
    def _to_result(row: dict, year: int) -> CountyResult | None:
        try:
            fips = str(row.get("county_fips", "")).zfill(5)
            if not fips or fips == "00000":
                return None
            return CountyResult(
                fips=fips,
                county=row.get("county_name", ""),
                state=row.get("state_name", ""),
                year=year,
                votes_dem=int(float(row.get("votes_dem", 0))),
                votes_gop=int(float(row.get("votes_gop", 0))),
                total_votes=int(float(row.get("total_votes", 0))),
                sources=[_dataset_source(year)],
            )
        except (ValueError, TypeError):
            return None


def _dataset_source(year: int) -> Source:
    return Source(kind=SourceKind.AGGREGATOR, domain="github.com/tonmcg",
                  url=SOURCE_TMPL.format(year=year),
                  published_at=datetime.now(timezone.utc))
