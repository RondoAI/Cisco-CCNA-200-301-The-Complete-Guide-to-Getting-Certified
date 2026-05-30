"""
Core data model for Glasshouse.

Design principle #1 — TRACK EVENTS, NOT PEOPLE.
There is deliberately NO entity here for profiling a person: no "subject",
no "watchlist", no per-individual dossier. An Event describes *something that
happened at a place and time*, supported by Sources. That is the whole world
this system is allowed to model. Adding a person-profile table would not be a
feature request; it would be a change of mission.

Design principle #2 — PROVENANCE IS NOT OPTIONAL.
Every Event carries the Sources that support it and an append-only audit
trail of every verification check that ran. You can always answer "how do we
know this?" because the answer is a field, not a vibe.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class SourceKind(str, Enum):
    WIRE = "wire"            # established news agency (Reuters, AP, AFP...)
    OUTLET = "outlet"        # named publication / broadcaster
    NGO = "ngo"              # humanitarian / monitoring org (ACLED, etc.)
    OFFICIAL = "official"    # government / IGO statement
    CITIZEN = "citizen"      # on-the-ground media (the cell-phone clip)
    AGGREGATOR = "aggregator"  # GDELT-style automated feed


# Rough trust weighting by source kind. Tunable. Citizen media is NOT
# distrusted — it is treated as high-value but unverified-until-corroborated.
KIND_WEIGHT: dict[SourceKind, float] = {
    SourceKind.WIRE: 1.0,
    SourceKind.NGO: 0.9,
    SourceKind.OFFICIAL: 0.7,   # official != neutral; weighted with care
    SourceKind.OUTLET: 0.6,
    SourceKind.AGGREGATOR: 0.4,
    SourceKind.CITIZEN: 0.5,
}


@dataclass
class Source:
    """One piece of evidence supporting an event.

    For CITIZEN media the uploader's identity must already be stripped before
    a Source is constructed — see privacy.redact_uploader(). The only thing we
    keep about a citizen source is what we need to verify the *footage*:
    domain/platform, a capture timestamp, a content hash (for recycled-media
    detection), and a one-way dedup token. Never the handle, never the contact.
    """
    kind: SourceKind
    domain: str                      # e.g. "reuters.com" or "telegram" (platform, not user)
    url: Optional[str] = None
    published_at: datetime = field(default_factory=_now)
    content_hash: Optional[str] = None   # perceptual/file hash for recycled-media checks
    dedup_token: Optional[str] = None    # salted one-way token; identity NOT recoverable
    id: str = field(default_factory=lambda: _id("src"))

    @property
    def weight(self) -> float:
        return KIND_WEIGHT.get(self.kind, 0.3)


@dataclass
class CheckResult:
    """One entry in the provenance / audit trail."""
    name: str
    passed: bool
    detail: str
    score_delta: float = 0.0
    at: datetime = field(default_factory=_now)


class Confidence(str, Enum):
    UNVERIFIED = "unverified"   # single uncorroborated source
    EMERGING = "emerging"       # some corroboration, not yet solid
    CORROBORATED = "corroborated"
    CONFIRMED = "confirmed"     # multiple independent + high-trust sources
    DISPUTED = "disputed"       # a check actively flagged a problem


@dataclass
class Event:
    """Something that happened. Not someone."""
    headline: str
    lat: float
    lon: float
    occurred_at: datetime
    sources: list[Source] = field(default_factory=list)
    audit: list[CheckResult] = field(default_factory=list)   # append-only
    score: float = 0.0
    confidence: Confidence = Confidence.UNVERIFIED
    region: str = ""
    tags: list[str] = field(default_factory=list)        # event-type labels (enrichment)
    enrichment: dict = field(default_factory=dict)       # provenance of what enrichers added
    id: str = field(default_factory=lambda: _id("evt"))
    ingested_at: datetime = field(default_factory=_now)

    def independent_domains(self) -> set[str]:
        return {s.domain for s in self.sources}

    def to_public_dict(self) -> dict:
        """What an API consumer is allowed to see. Note: no uploader fields
        exist to leak, by construction."""
        return {
            "id": self.id,
            "headline": self.headline,
            "lat": self.lat,
            "lon": self.lon,
            "region": self.region,
            "tags": self.tags,
            "enrichment": self.enrichment,
            "occurred_at": self.occurred_at.isoformat(),
            "confidence": self.confidence.value,
            "score": round(self.score, 3),
            "source_count": len(self.sources),
            "independent_sources": len(self.independent_domains()),
            "sources": [
                {"kind": s.kind.value, "domain": s.domain, "url": s.url,
                 "published_at": s.published_at.isoformat()}
                for s in self.sources
            ],
            "audit_trail": [
                {"check": c.name, "passed": c.passed, "detail": c.detail,
                 "score_delta": round(c.score_delta, 3), "at": c.at.isoformat()}
                for c in self.audit
            ],
        }
