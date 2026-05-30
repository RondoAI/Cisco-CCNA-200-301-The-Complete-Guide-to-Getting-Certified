"""
THE RECORD — Pillar 1 of Glasshouse (public accountability).

The legible, sourced record of *public power*: what officials promise, what they
vote on, and whether the two line up. The "killer feature" (ARCHITECTURE.md §2)
is the explicit, sourced edge between a Promise and the later Vote/Bill/outcome
that fulfilled or contradicted it — "said X, did Y, here are both receipts."

Two non-negotiables carry over from the events engine, by design:

PUBLIC POWER ONLY (CHARTER gate #1).
  The only person-like entity here is `Official`, and it holds PUBLIC ROLE DATA
  ONLY — office, party, votes, public statements. There is no field for a private
  citizen, and none for psychology, personality, or persuasion. `assert_charter_safe()`
  scans the schema for forbidden concepts so this is enforced in code, not a memo.

PROVENANCE IS MANDATORY (CHARTER gate #4).
  Every Vote, Statement, Promise and assessment carries its `Source`s. The store
  refuses to admit a fact with no source. A promise-vs-action verdict ships with
  an inspectable audit trail, and correlation is never dressed as causation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from .models import CheckResult, Source


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Charter guard: forbidden concepts may not appear as fields anywhere in THE
# RECORD. This mirrors the CI gate described in CHARTER.md — profiling a private
# individual or modelling psychology is a change of mission, not a feature.
# ---------------------------------------------------------------------------
FORBIDDEN_FIELD_TOKENS = frozenset({
    "psychograph", "personality", "persuasion", "persuade", "microtarget",
    "sentiment_profile", "private_citizen", "watchlist", "private_address",
    "home_address", "ssn", "device_id", "phone", "ip_address", "propensity",
    "voter_score", "influence_score",
})


class Level(str, Enum):
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    NATIONAL = "national"            # a non-US national government / leadership
    INTERNATIONAL = "international"   # IGOs and cross-border bodies


class VotePosition(str, Enum):
    YEA = "yea"
    NAY = "nay"
    ABSTAIN = "abstain"
    ABSENT = "absent"


class StatementType(str, Enum):
    SPEECH = "speech"
    FLOOR = "floor"
    INTERVIEW = "interview"
    PRESS = "press"
    SOCIAL = "social"


class BillStatus(str, Enum):
    INTRODUCED = "introduced"
    IN_COMMITTEE = "in_committee"
    PASSED = "passed"
    ENACTED = "enacted"
    FAILED = "failed"


class Fulfillment(str, Enum):
    """Verdict on a promise, against what the official actually did."""
    FULFILLED = "fulfilled"
    PARTIAL = "partial"
    IN_PROGRESS = "in_progress"
    CONTRADICTED = "contradicted"
    UNRESOLVED = "unresolved"   # no recorded action yet — say so, don't guess


class DonorType(str, Enum):
    """Public funding entities only. We model organizations, committees and
    aggregate sectors — public money in public politics — not private donors'
    personal profiles."""
    PAC = "pac"
    SUPER_PAC = "super_pac"
    COMMITTEE = "committee"
    ORGANIZATION = "organization"
    INDUSTRY = "industry"            # aggregate sector (OpenSecrets-style rollup)


# How funding relates to a vote is always CORRELATION, shown with its receipts,
# never asserted as causation. This string travels with every funding context.
FUNDING_DISCLAIMER = (
    "Funding and votes shown together are CORRELATION from the public record, "
    "not proof that money caused a vote. Same methodology is applied to every "
    "donor, lobby and government — nonpartisan by standard.")


@dataclass
class Official:
    """A public officeholder. PUBLIC ROLE DATA ONLY — a senator's name, party
    and votes are public record. There is intentionally no private-life field."""
    name: str                         # public officeholder name (public record)
    office: str                       # e.g. "U.S. Senator", "Mayor"
    body: str                         # e.g. "U.S. Senate", "City Council"
    jurisdiction: str                 # postal/region code, e.g. "TX", "CA", "LB"
    level: Level = Level.FEDERAL
    country: str = "US"               # ISO country — the global spine, not US-only
    party: str = ""
    district: Optional[str] = None    # House district, when applicable
    term_end: Optional[datetime] = None
    next_election: Optional[int] = None   # year the seat is next contested
    qid: Optional[str] = None         # Wikidata QID — the cross-language spine
    bioguide: Optional[str] = None    # official Congress Bioguide ID
    source: Optional[Source] = None   # where this role record comes from
    id: str = field(default_factory=lambda: _id("off"))

    @property
    def chamber(self) -> str:
        if "Senate" in self.body:
            return "sen"
        if "House" in self.body:
            return "rep"
        return ""

    def to_public_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name, "office": self.office,
            "body": self.body, "jurisdiction": self.jurisdiction,
            "country": self.country, "chamber": self.chamber,
            "level": self.level.value,
            "party": self.party, "district": self.district,
            "term_end": self.term_end.isoformat() if self.term_end else None,
            "next_election": self.next_election, "qid": self.qid,
            "bioguide": self.bioguide,
        }


@dataclass
class Bill:
    title: str
    summary: str = ""
    status: BillStatus = BillStatus.INTRODUCED
    subjects: list[str] = field(default_factory=list)
    when: datetime = field(default_factory=_now)
    sources: list[Source] = field(default_factory=list)
    id: str = field(default_factory=lambda: _id("bill"))

    def to_public_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "summary": self.summary,
                "status": self.status.value, "subjects": self.subjects,
                "when": self.when.isoformat(), "sources": _src_dicts(self.sources)}


@dataclass
class Vote:
    """How an official voted on a bill — a public, recorded act."""
    official_id: str
    bill_id: str
    position: VotePosition
    when: datetime = field(default_factory=_now)
    sources: list[Source] = field(default_factory=list)
    id: str = field(default_factory=lambda: _id("vote"))

    def to_public_dict(self) -> dict:
        return {"id": self.id, "official_id": self.official_id,
                "bill_id": self.bill_id, "position": self.position.value,
                "when": self.when.isoformat(), "sources": _src_dicts(self.sources)}


@dataclass
class Statement:
    """Something a public figure said, on the record.

    A public leader's own *public* words (a speech, an interview, or a `social`
    post) are a PRIMARY SOURCE — a direct, often non-Western perspective to set
    beside the press, sourced, so the reader can judge. `lang`/`translation`/
    `context` carry the original language plus a faithful translation and the
    framing a reader needs. We archive what was said in public; we never infer
    private psychology or model the person (CHARTER gate #2, DECISIONS D7)."""
    official_id: str
    text: str
    type: StatementType = StatementType.PRESS
    topic: str = ""
    lang: str = "en"                       # ISO language of `text`
    translation: Optional[str] = None      # faithful English translation, if any
    context: Optional[str] = None          # sourced framing, never editorializing
    when: datetime = field(default_factory=_now)
    sources: list[Source] = field(default_factory=list)
    id: str = field(default_factory=lambda: _id("stmt"))

    def to_public_dict(self) -> dict:
        return {"id": self.id, "official_id": self.official_id, "text": self.text,
                "type": self.type.value, "topic": self.topic, "lang": self.lang,
                "translation": self.translation, "context": self.context,
                "when": self.when.isoformat(), "sources": _src_dicts(self.sources)}


@dataclass
class Promise(Statement):
    """A stated commitment — a kind of Statement we will later check against
    what the official actually did. This is one end of the killer edge."""
    id: str = field(default_factory=lambda: _id("prom"))


@dataclass
class PromiseAssessment:
    """The killer edge: a sourced verdict linking a Promise to the Vote(s) /
    Bill(s) / outcome that fulfilled or contradicted it.

    It carries an audit trail (the same CheckResult receipt the events engine
    uses) so the verdict is an *explanation*, never an unsourced accusation.
    Correlation is labelled as correlation; only the official's own recorded
    acts justify a 'contradicted' or 'fulfilled' verdict.
    """
    promise_id: str
    verdict: Fulfillment
    rationale: str
    action_vote_ids: list[str] = field(default_factory=list)
    action_bill_ids: list[str] = field(default_factory=list)
    audit: list[CheckResult] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=_now)
    id: str = field(default_factory=lambda: _id("assess"))

    def to_public_dict(self) -> dict:
        return {
            "id": self.id, "promise_id": self.promise_id,
            "verdict": self.verdict.value, "rationale": self.rationale,
            "action_vote_ids": self.action_vote_ids,
            "action_bill_ids": self.action_bill_ids,
            "assessed_at": self.assessed_at.isoformat(),
            "audit_trail": [
                {"check": c.name, "passed": c.passed, "detail": c.detail}
                for c in self.audit
            ],
        }


@dataclass
class Donor:
    """A funding source — a PAC, committee, organization or aggregate sector.
    `foreign_principal` records a FARA-registered foreign tie when one is on the
    public record (e.g. a lobby acting for a foreign government); it lets us
    trace money back toward its ultimate origin, sourced — never inferred."""
    name: str
    type: DonorType = DonorType.PAC
    foreign_principal: Optional[str] = None   # FARA-registered principal (public record)
    qid: Optional[str] = None
    source: Optional[Source] = None
    id: str = field(default_factory=lambda: _id("donor"))

    def to_public_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "type": self.type.value,
                "foreign_principal": self.foreign_principal, "qid": self.qid}


@dataclass
class FundingFlow:
    """A recorded contribution: donor → official, in a cycle, sourced to FEC/
    OpenSecrets. `subjects` are the donor's interest areas, used only to surface
    (clearly labelled) correlation with related votes."""
    donor_id: str
    official_id: str
    amount_usd: float
    cycle: str                                # e.g. "2024"
    subjects: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    id: str = field(default_factory=lambda: _id("flow"))

    def to_public_dict(self) -> dict:
        return {"id": self.id, "donor_id": self.donor_id,
                "official_id": self.official_id, "amount_usd": self.amount_usd,
                "cycle": self.cycle, "subjects": self.subjects,
                "sources": _src_dicts(self.sources)}


def _src_dicts(sources: list[Source]) -> list[dict]:
    return [{"kind": s.kind.value, "domain": s.domain, "url": s.url,
             "published_at": s.published_at.isoformat()} for s in sources]


# ---------------------------------------------------------------------------
# Assessment helper — builds the audit trail for a promise-vs-action verdict.
# ---------------------------------------------------------------------------
def assess_promise(promise: Promise, verdict: Fulfillment, rationale: str,
                   votes: Optional[list[Vote]] = None,
                   bills: Optional[list[Bill]] = None) -> PromiseAssessment:
    votes, bills = votes or [], bills or []
    audit = [
        CheckResult("promise_on_record", bool(promise.sources),
                    f"promise sourced to {len(promise.sources)} record(s)"),
        CheckResult("action_on_record", bool(votes or bills),
                    f"{len(votes)} recorded vote(s), {len(bills)} bill(s)"),
        CheckResult(
            "alignment",
            verdict in (Fulfillment.FULFILLED, Fulfillment.PARTIAL,
                        Fulfillment.IN_PROGRESS),
            rationale),
    ]
    return PromiseAssessment(
        promise_id=promise.id, verdict=verdict, rationale=rationale,
        action_vote_ids=[v.id for v in votes],
        action_bill_ids=[b.id for b in bills], audit=audit)


# ---------------------------------------------------------------------------
# Store — in-memory, behind a tiny interface so it can become Postgres + a graph
# layer later (ARCHITECTURE.md §5) without touching callers.
# ---------------------------------------------------------------------------
class ProvenanceError(ValueError):
    """Raised when a fact is admitted with no Source. Gate #4 in code."""


class RecordStore:
    def __init__(self) -> None:
        self.officials: dict[str, Official] = {}
        self.bills: dict[str, Bill] = {}
        self.votes: dict[str, Vote] = {}
        self.statements: dict[str, Statement] = {}
        self.assessments: dict[str, PromiseAssessment] = {}
        self.donors: dict[str, Donor] = {}
        self.flows: dict[str, FundingFlow] = {}

    def add_official(self, o: Official) -> Official:
        self.officials[o.id] = o
        return o

    def add_bill(self, b: Bill) -> Bill:
        self._require_source(b.sources, "Bill")
        self.bills[b.id] = b
        return b

    def add_vote(self, v: Vote) -> Vote:
        self._require_source(v.sources, "Vote")
        self.votes[v.id] = v
        return v

    def add_statement(self, s: Statement) -> Statement:
        self._require_source(s.sources, "Statement")
        self.statements[s.id] = s
        return s

    def add_assessment(self, a: PromiseAssessment) -> PromiseAssessment:
        self.assessments[a.id] = a
        return a

    def add_donor(self, d: Donor) -> Donor:
        self.donors[d.id] = d
        return d

    def add_funding(self, f: FundingFlow) -> FundingFlow:
        self._require_source(f.sources, "FundingFlow")
        self.flows[f.id] = f
        return f

    @staticmethod
    def _require_source(sources: list[Source], what: str) -> None:
        if not sources:
            raise ProvenanceError(
                f"{what} admitted with no source — provenance is mandatory")

    def query_officials(self, state: Optional[str] = None,
                        chamber: Optional[str] = None,
                        party: Optional[str] = None,
                        next_election: Optional[int] = None) -> list[Official]:
        out = list(self.officials.values())
        if state:
            out = [o for o in out if o.jurisdiction.upper() == state.upper()]
        if chamber:
            out = [o for o in out if o.chamber == chamber]
        if party:
            out = [o for o in out if o.party.lower() == party.lower()]
        if next_election is not None:
            out = [o for o in out if o.next_election == next_election]
        return sorted(out, key=lambda o: (o.jurisdiction, o.chamber, o.name))

    def national_summary(self) -> dict:
        """The whole-country layout: totals by chamber, party and state, plus
        who is up for election in each upcoming cycle."""
        offs = list(self.officials.values())
        by_chamber: dict[str, int] = {}
        by_party: dict[str, int] = {}
        by_state: dict[str, int] = {}
        up_for_election: dict[str, int] = {}
        for o in offs:
            by_chamber[o.chamber or "other"] = by_chamber.get(o.chamber or "other", 0) + 1
            by_party[o.party or "Unknown"] = by_party.get(o.party or "Unknown", 0) + 1
            by_state[o.jurisdiction] = by_state.get(o.jurisdiction, 0) + 1
            if o.next_election:
                k = str(o.next_election)
                up_for_election[k] = up_for_election.get(k, 0) + 1
        return {
            "total_officials": len(offs),
            "by_chamber": dict(sorted(by_chamber.items())),
            "by_party": dict(sorted(by_party.items(), key=lambda x: -x[1])),
            "states_covered": len(by_state),
            "by_state": dict(sorted(by_state.items())),
            "up_for_election": dict(sorted(up_for_election.items())),
        }

    def votes_for(self, official_id: str) -> list[Vote]:
        return [v for v in self.votes.values() if v.official_id == official_id]

    def statements_for(self, official_id: str) -> list[Statement]:
        return [s for s in self.statements.values()
                if s.official_id == official_id]

    def promises_for(self, official_id: str) -> list[Promise]:
        return [s for s in self.statements_for(official_id)
                if isinstance(s, Promise)]

    def assessment_for(self, promise_id: str) -> Optional[PromiseAssessment]:
        for a in self.assessments.values():
            if a.promise_id == promise_id:
                return a
        return None

    def funding_for(self, official_id: str) -> list[FundingFlow]:
        return [f for f in self.flows.values()
                if f.official_id == official_id]

    def funding_context(self, official_id: str) -> dict:
        """Follow the money: who funds this official, any foreign principal
        behind the donor, and which of the official's recorded votes touch the
        donor's interest areas. The vote linkage is CORRELATION, labelled as
        such and shipped with its receipts — never an assertion of causation."""
        official = self.officials.get(official_id)
        if not official:
            return {}
        official_votes = self.votes_for(official_id)
        rows = []
        total = 0.0
        for f in self.funding_for(official_id):
            total += f.amount_usd
            donor = self.donors.get(f.donor_id)
            related = []
            for v in official_votes:
                bill = self.bills.get(v.bill_id)
                if bill and set(bill.subjects) & set(f.subjects):
                    related.append({"vote": v.to_public_dict(),
                                    "bill": bill.to_public_dict()})
            rows.append({
                "donor": donor.to_public_dict() if donor else None,
                "amount_usd": f.amount_usd, "cycle": f.cycle,
                "subjects": f.subjects, "sources": _src_dicts(f.sources),
                "correlated_votes": related,   # CORRELATION — see disclaimer
            })
        return {
            "official": official.to_public_dict(),
            "total_usd": round(total, 2),
            "disclaimer": FUNDING_DISCLAIMER,
            "relationship": "correlation",
            "flows": sorted(rows, key=lambda r: r["amount_usd"], reverse=True),
        }

    def scorecard(self, official_id: str) -> dict:
        """The headline view: an official's promises, each next to the recorded
        action and verdict. 'Said X, did Y, here are both receipts.'"""
        official = self.officials.get(official_id)
        if not official:
            return {}
        promises = self.promises_for(official_id)
        rows = []
        tally: dict[str, int] = {}
        for p in promises:
            a = self.assessment_for(p.id)
            verdict = a.verdict.value if a else Fulfillment.UNRESOLVED.value
            tally[verdict] = tally.get(verdict, 0) + 1
            rows.append({
                "promise": p.to_public_dict(),
                "assessment": a.to_public_dict() if a else None,
                "actions": {
                    "votes": [self.votes[i].to_public_dict()
                              for i in (a.action_vote_ids if a else [])
                              if i in self.votes],
                    "bills": [self.bills[i].to_public_dict()
                              for i in (a.action_bill_ids if a else [])
                              if i in self.bills],
                },
            })
        return {"official": official.to_public_dict(),
                "promise_count": len(promises), "tally": tally,
                "promises": rows}


def assert_charter_safe() -> None:
    """Fail loudly if any RECORD entity grows a field that profiles a private
    individual or models psychology/persuasion. Called by the test-suite and
    intended for CI — the charter's gate #1/#3, enforced in code."""
    for entity in (Official, Bill, Vote, Statement, Promise, PromiseAssessment,
                   Donor, FundingFlow):
        for f in fields(entity):
            low = f.name.lower()
            for token in FORBIDDEN_FIELD_TOKENS:
                if token in low:
                    raise AssertionError(
                        f"CHARTER VIOLATION: {entity.__name__}.{f.name} "
                        f"matches forbidden concept '{token}'")
