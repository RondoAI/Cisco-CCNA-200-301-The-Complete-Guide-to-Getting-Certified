"""
Verification pipeline — this is the moat.

Collection is commoditized; anyone can pull a feed. The defensible thing is
turning a messy pile of claims into a confidence-scored event with the receipts
shown. Each check appends to the event's append-only audit trail, so the output
is not just a number but an explanation a journalist or court could inspect.

Checks run in order. Some adjust the score; any check that fails hard can mark
the event DISPUTED, which no amount of corroboration silently overrides.

The functions here are deliberately transparent rule-based checks. The real
product swaps the bodies for stronger implementations (perceptual-hash matching,
satellite/landmark geolocation, shadow-based chronolocation, model-assisted
disinfo flags) WITHOUT changing this interface or the audit contract.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Callable

from .models import CheckResult, Confidence, Event, SourceKind

Check = Callable[[Event], CheckResult]


def check_has_sources(ev: Event) -> CheckResult:
    ok = len(ev.sources) > 0
    return CheckResult(
        "has_sources", ok,
        f"{len(ev.sources)} source(s) attached" if ok else "no sources — cannot stand",
        score_delta=0.0,
    )


def check_independent_corroboration(ev: Event) -> CheckResult:
    """The core test: do *independent* sources (distinct domains) agree?
    One outlet reposting another is not corroboration."""
    n = len(ev.independent_domains())
    delta = {0: 0.0, 1: 0.15}.get(n, min(0.15 + 0.18 * (n - 1), 0.7))
    ok = n >= 2
    return CheckResult(
        "independent_corroboration", ok,
        f"{n} independent domain(s)", score_delta=delta,
    )


def check_source_quality(ev: Event) -> CheckResult:
    """Weight by source kind. A wire + an NGO beats five anonymous reposts."""
    if not ev.sources:
        return CheckResult("source_quality", False, "no sources", 0.0)
    best = max(s.weight for s in ev.sources)
    avg = sum(s.weight for s in ev.sources) / len(ev.sources)
    delta = 0.15 * best + 0.10 * avg
    ok = best >= 0.5
    return CheckResult(
        "source_quality", ok,
        f"best-source weight {best:.2f}, avg {avg:.2f}", score_delta=delta,
    )


def check_recency_consistency(ev: Event) -> CheckResult:
    """Sources published wildly after the event, or before it, are suspicious.
    A clip 'from today' whose earliest sighting is years old is the classic
    recycled-footage tell."""
    if not ev.sources:
        return CheckResult("recency_consistency", False, "no sources", 0.0)
    spread = max(s.published_at for s in ev.sources) - min(
        s.published_at for s in ev.sources)
    earliest = min(s.published_at for s in ev.sources)
    pre_event = ev.occurred_at - earliest
    if pre_event > timedelta(days=2):
        return CheckResult(
            "recency_consistency", False,
            f"a source predates the event by {pre_event.days}d — likely recycled",
            score_delta=-0.4,
        )
    ok = spread <= timedelta(days=3)
    return CheckResult(
        "recency_consistency", ok,
        f"source time-spread {spread}", score_delta=0.05 if ok else -0.05,
    )


def check_recycled_media(ev: Event, seen_hashes: set[str] | None = None) -> CheckResult:
    """If a citizen clip's content hash was already attached to a *different*
    earlier event, it is being recycled. Hard flag."""
    seen_hashes = seen_hashes or set()
    hashes = [s.content_hash for s in ev.sources if s.content_hash]
    reused = [h for h in hashes if h in seen_hashes]
    if reused:
        return CheckResult(
            "recycled_media", False,
            f"{len(reused)} media hash(es) seen on an earlier event — recycled",
            score_delta=-0.5,
        )
    return CheckResult(
        "recycled_media", True,
        f"{len(hashes)} media hash(es), none previously seen", score_delta=0.0,
    )


def _confidence_from(score: float, disputed: bool) -> Confidence:
    if disputed:
        return Confidence.DISPUTED
    if score >= 0.75:
        return Confidence.CONFIRMED
    if score >= 0.5:
        return Confidence.CORROBORATED
    if score >= 0.25:
        return Confidence.EMERGING
    return Confidence.UNVERIFIED


def verify(ev: Event, seen_hashes: set[str] | None = None) -> Event:
    """Run the pipeline, mutating the event's score, confidence and audit trail.
    Returns the same event for convenience."""
    ev.audit.clear()
    score = 0.0
    disputed = False

    ordered = [
        check_has_sources(ev),
        check_independent_corroboration(ev),
        check_source_quality(ev),
        check_recency_consistency(ev),
        check_recycled_media(ev, seen_hashes),
    ]
    for result in ordered:
        ev.audit.append(result)
        score += result.score_delta
        # A hard failure on an integrity check disputes the event outright.
        if not result.passed and result.name in {
                "recency_consistency", "recycled_media", "has_sources"}:
            disputed = True

    ev.score = max(0.0, min(score, 1.0))
    ev.confidence = _confidence_from(ev.score, disputed)
    return ev
