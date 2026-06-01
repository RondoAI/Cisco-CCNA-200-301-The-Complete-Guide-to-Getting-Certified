"""
The learning layer — how Glasshouse gets smarter as plugins feed it data.

This is the "algorithm that learns from the data" — but deliberately NOT a black
box. Two ideas, both interpretable:

1. SOURCE REPUTATION (Bayesian, Beta-Binomial). Every source domain has a track
   record: times its claims were later confirmed vs. debunked. We do not hand-set
   trust; we LEARN it. New sources start from a prior derived from their kind
   (a wire is trusted more than an anonymous aggregator *to begin with*), then the
   data moves them. Reputation is reported with its observation count, so "trust"
   always comes with "how much evidence."

2. INDEPENDENCE-AWARE corroboration. Fifty outlets reposting one wire is ONE
   independent voice, not fifty. We cluster correlated/syndicated/identical-media
   sources and count each cluster once — this is what stops the echo chamber from
   manufacturing false confidence.

The scorer emits CheckResults (the same audit-trail type the rest of the system
uses), so every learned contribution remains a receipt you can show.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

from .models import KIND_WEIGHT, CheckResult, Confidence, Event, Source

# Sources known to share a parent / syndicate. Same cluster => counted once.
# In production this is learned/maintained, not hard-coded; this is the seed.
SYNDICATION: dict[str, str] = {
    "apnews.com": "ap", "abcnews.go.com": "ap",        # AP wire + repubs
    "reuters.com": "reuters",
}


@dataclass
class SourceReputation:
    """Beta-Binomial belief about one source's reliability."""
    domain: str
    alpha: float = 1.0   # pseudo-successes
    beta: float = 1.0    # pseudo-failures
    observations: int = 0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def std(self) -> float:
        a, b = self.alpha, self.beta
        return sqrt(a * b / ((a + b) ** 2 * (a + b + 1)))

    @property
    def trust(self) -> float:
        """Conservative reliability: mean minus one std. A source with few
        observations is trusted cautiously even if its mean is high."""
        return max(0.0, self.mean - self.std)


class ReputationStore:
    def __init__(self) -> None:
        self._reps: dict[str, SourceReputation] = {}

    def get(self, source: Source) -> SourceReputation:
        if source.domain not in self._reps:
            # Prior from source kind: wire starts strong, aggregator weak.
            w = KIND_WEIGHT.get(source.kind, 0.3)
            pseudo = 4.0
            self._reps[source.domain] = SourceReputation(
                source.domain, alpha=1 + pseudo * w, beta=1 + pseudo * (1 - w))
        return self._reps[source.domain]

    def record(self, source: Source, success: bool, weight: float = 1.0) -> None:
        rep = self.get(source)
        if success:
            rep.alpha += weight
        else:
            rep.beta += weight
        rep.observations += 1


# ---- the learning feedback loop -------------------------------------------

def learn_from_outcome(event: Event, reps: ReputationStore, confirmed: bool,
                       by: str = "corroboration") -> None:
    """Update the reputation of every source that backed an event, once we learn
    whether the event was real. Ground-truth confirmation counts for more than
    mere agreement between sources, so consensus can't bootstrap its own trust."""
    weight = 2.0 if by == "ground_truth" else 1.0
    for s in event.sources:
        reps.record(s, success=confirmed, weight=weight)


# ---- independence-aware corroboration -------------------------------------

def _cluster_key(s: Source) -> str:
    if s.content_hash:                      # identical media = same origin
        return f"media:{s.content_hash}"
    if s.domain in SYNDICATION:             # known syndication group
        return f"synd:{SYNDICATION[s.domain]}"
    return f"domain:{s.domain}"


def independent_clusters(sources: list[Source]) -> list[list[Source]]:
    groups: dict[str, list[Source]] = {}
    for s in sources:
        groups.setdefault(_cluster_key(s), []).append(s)
    return list(groups.values())


# ---- the learned, still-transparent scorer --------------------------------

def score_event(event: Event, reps: ReputationStore) -> Event:
    """Reputation-weighted, independence-aware verification. Produces a confidence
    plus a full audit trail. Supersedes the static verify.verify() once a
    ReputationStore exists, without changing the audit contract."""
    event.audit.clear()
    clusters = independent_clusters(event.sources)

    # 1) independent voices (clusters), not raw source count
    n = len(clusters)
    corro = {0: 0.0, 1: 0.15}.get(n, min(0.15 + 0.18 * (n - 1), 0.7))
    event.audit.append(CheckResult(
        "independent_clusters", n >= 2,
        f"{n} independent voice(s) from {len(event.sources)} source(s)", corro))

    # 2) learned reputation of the best independent cluster
    best_trust = 0.0
    for cluster in clusters:
        rep = max((reps.get(s) for s in cluster), key=lambda r: r.trust)
        best_trust = max(best_trust, rep.trust)
        event.audit.append(CheckResult(
            f"reputation:{rep.domain}", rep.trust >= 0.5,
            f"learned trust {rep.trust:.2f} (mean {rep.mean:.2f}, "
            f"n={rep.observations})", 0.0))
    event.audit.append(CheckResult(
        "reputation_weight", best_trust >= 0.5,
        f"best independent-source trust {best_trust:.2f}", 0.25 * best_trust))

    # 3) recycled-media hard flag still disputes outright
    disputed = False
    if any(s.content_hash and event.enrichment.get("recycled") for s in event.sources):
        event.audit.append(CheckResult(
            "recycled_media", False, "media seen on an earlier event", -0.5))
        disputed = True

    score = max(0.0, min(sum(c.score_delta for c in event.audit), 1.0))
    event.score = score
    if disputed:
        event.confidence = Confidence.DISPUTED
    elif score >= 0.75:
        event.confidence = Confidence.CONFIRMED
    elif score >= 0.5:
        event.confidence = Confidence.CORROBORATED
    elif score >= 0.25:
        event.confidence = Confidence.EMERGING
    else:
        event.confidence = Confidence.UNVERIFIED
    return event
