"""
Notional seed for THE RECORD so the accountability view runs offline.

Everything here is CLEARLY NOTIONAL — an invented official and invented bills —
exactly as the events seed is. In production these rows come from official,
primary sources (Congress.gov for federal votes/bills, FEC/OpenSecrets for money,
Wikidata for the entity spine), each carrying its real source URL through the
same provenance contract.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import Source, SourceKind
from .record import (Bill, BillStatus, Fulfillment, Official, Promise,
                     RecordStore, Statement, StatementType, Vote, VotePosition,
                     assess_promise)

NOW = datetime.now(timezone.utc)


def _src(kind, domain, days_ago=0, url=None):
    return Source(kind=kind, domain=domain, url=url,
                  published_at=NOW - timedelta(days=days_ago))


def seed_record(store: RecordStore) -> RecordStore:
    # --- A notional official (PUBLIC ROLE DATA ONLY) --------------------------
    avery = store.add_official(Official(
        name="Sen. Jordan Avery (NOTIONAL)", office="U.S. Senator",
        body="U.S. Senate", jurisdiction="State of Notiona", party="Independent",
        qid="Q000000",
        source=_src(SourceKind.OFFICIAL, "congress.gov", 400,
                    url="https://www.congress.gov/member/notional")))

    # --- Bills (each sourced to an official record) ---------------------------
    vets = store.add_bill(Bill(
        title="Veterans Health Expansion Act (NOTIONAL)",
        summary="Expands VA healthcare funding and rural clinic access.",
        status=BillStatus.ENACTED, subjects=["veterans", "healthcare"],
        when=NOW - timedelta(days=120),
        sources=[_src(SourceKind.OFFICIAL, "congress.gov", 120,
                      url="https://www.congress.gov/bill/notional-vets")]))

    budget = store.add_bill(Bill(
        title="Budget Reconciliation Act (NOTIONAL)",
        summary="Omnibus budget that includes phased reductions to Social "
                "Security cost-of-living adjustments.",
        status=BillStatus.PASSED, subjects=["budget", "social_security"],
        when=NOW - timedelta(days=40),
        sources=[_src(SourceKind.OFFICIAL, "congress.gov", 40,
                      url="https://www.congress.gov/bill/notional-budget")]))

    # --- Promises (public statements) -----------------------------------------
    p_vets = store.add_statement(Promise(
        official_id=avery.id, type=StatementType.SPEECH, topic="veterans",
        text="I will vote to expand healthcare funding for our veterans.",
        when=NOW - timedelta(days=300),
        sources=[_src(SourceKind.WIRE, "reuters.com", 300,
                      url="https://reuters.com/notional-vets-promise")]))

    p_ss = store.add_statement(Promise(
        official_id=avery.id, type=StatementType.FLOOR, topic="social_security",
        text="I will protect Social Security from any cuts.",
        when=NOW - timedelta(days=250),
        sources=[_src(SourceKind.OFFICIAL, "congress.gov", 250,
                      url="https://www.congress.gov/notional-ss-floor")]))

    p_cf = store.add_statement(Promise(
        official_id=avery.id, type=StatementType.PRESS,
        topic="campaign_finance",
        text="I will pass campaign-finance transparency this term.",
        when=NOW - timedelta(days=200),
        sources=[_src(SourceKind.OUTLET, "example-news.com", 200,
                      url="https://example-news.com/notional-cf")]))

    # --- Recorded votes (the 'did') -------------------------------------------
    v_vets = store.add_vote(Vote(
        official_id=avery.id, bill_id=vets.id, position=VotePosition.YEA,
        when=NOW - timedelta(days=121),
        sources=[_src(SourceKind.OFFICIAL, "congress.gov", 121,
                      url="https://www.congress.gov/vote/notional-vets")]))

    v_budget = store.add_vote(Vote(
        official_id=avery.id, bill_id=budget.id, position=VotePosition.YEA,
        when=NOW - timedelta(days=41),
        sources=[_src(SourceKind.OFFICIAL, "congress.gov", 41,
                      url="https://www.congress.gov/vote/notional-budget")]))

    # --- The killer edge: promise vs. recorded action -------------------------
    store.add_assessment(assess_promise(
        p_vets, Fulfillment.FULFILLED,
        "Voted YEA on the Veterans Health Expansion Act, which expanded VA "
        "funding — consistent with the promise.",
        votes=[v_vets], bills=[vets]))

    store.add_assessment(assess_promise(
        p_ss, Fulfillment.CONTRADICTED,
        "Promised to protect Social Security from cuts, then voted YEA on the "
        "Budget Reconciliation Act, which phases down COLA — the recorded vote "
        "contradicts the stated promise. (Both receipts linked.)",
        votes=[v_budget], bills=[budget]))

    store.add_assessment(assess_promise(
        p_cf, Fulfillment.UNRESOLVED,
        "No bill or vote on campaign-finance transparency is on the record yet "
        "this term. Stated, not yet acted on — labelled unresolved, not broken."))

    return store
