"""Tests for THE RECORD (Pillar 1). They pin the two things that make this
accountability and not just a database: the promise-vs-action edge with both
receipts, and the charter gates (public power only, provenance mandatory)."""

import pytest

from glasshouse.models import Source, SourceKind
from glasshouse.record import (Bill, Donor, DonorType, Fulfillment,
                               FundingFlow, Official, Promise, ProvenanceError,
                               RecordStore, StatementType, Vote, VotePosition,
                               assert_charter_safe)
from glasshouse.record_seed import seed_record


def _src(domain="congress.gov"):
    return Source(SourceKind.OFFICIAL, domain)


def test_charter_schema_has_no_forbidden_fields():
    # No RECORD entity may model a private citizen or psychology/persuasion.
    assert_charter_safe()


def test_facts_require_a_source():
    store = RecordStore()
    with pytest.raises(ProvenanceError):
        store.add_vote(Vote("off_1", "bill_1", VotePosition.YEA))  # no source
    with pytest.raises(ProvenanceError):
        store.add_bill(Bill("Unsourced Act"))                      # no source


def test_scorecard_links_promise_to_action_with_both_receipts():
    store = seed_record(RecordStore())
    official_id = next(iter(store.officials))
    card = store.scorecard(official_id)

    assert card["promise_count"] == 3
    verdicts = {row["assessment"]["verdict"] for row in card["promises"]
                if row["assessment"]}
    assert {"fulfilled", "contradicted", "unresolved"} <= verdicts

    # The contradiction row must carry BOTH receipts: the promise's source and
    # the recorded vote's source. "Said X, did Y" with provenance on each side.
    contra = next(r for r in card["promises"]
                  if r["assessment"] and r["assessment"]["verdict"] == "contradicted")
    assert contra["promise"]["sources"], "promise must cite a source"
    assert contra["actions"]["votes"], "contradiction must point at a recorded vote"
    assert contra["actions"]["votes"][0]["sources"], "the vote must cite a source"


def test_unresolved_is_not_called_broken():
    """A promise with no recorded action yet is 'unresolved', never 'contradicted'
    — we state what's on the record, we don't guess intent."""
    store = seed_record(RecordStore())
    official_id = next(iter(store.officials))
    card = store.scorecard(official_id)
    unresolved = [r for r in card["promises"]
                  if r["assessment"] and r["assessment"]["verdict"] == "unresolved"]
    assert unresolved
    assert unresolved[0]["actions"]["votes"] == []


def test_assessment_carries_an_inspectable_audit_trail():
    store = seed_record(RecordStore())
    pid = next(p for p in store.assessments.values()).promise_id
    a = store.assessment_for(pid)
    names = {c["check"] for c in a.to_public_dict()["audit_trail"]}
    assert {"promise_on_record", "action_on_record", "alignment"} <= names


def test_funding_requires_a_source():
    store = RecordStore()
    with pytest.raises(ProvenanceError):
        store.add_funding(FundingFlow("d1", "o1", 1000.0, "2024"))  # no source


def test_funding_context_labels_correlation_and_carries_receipts():
    store = seed_record(RecordStore())
    official_id = next(iter(store.officials))
    ctx = store.funding_context(official_id)

    # Correlation must be labelled, never dressed as causation.
    assert ctx["relationship"] == "correlation"
    assert "correlation" in ctx["disclaimer"].lower()
    assert "nonpartisan" in ctx["disclaimer"].lower()
    assert ctx["total_usd"] == 165000.0
    # Every flow ships with its sources (FEC/OpenSecrets/FARA).
    assert all(f["sources"] for f in ctx["flows"])


def test_foreign_principal_is_traceable_when_on_record():
    store = seed_record(RecordStore())
    ctx = store.funding_context(next(iter(store.officials)))
    foreign = [f for f in ctx["flows"]
               if f["donor"] and f["donor"]["foreign_principal"]]
    assert foreign, "a FARA foreign principal should be surfaced when present"


def test_funding_correlates_to_votes_only_via_shared_subjects():
    store = seed_record(RecordStore())
    ctx = store.funding_context(next(iter(store.officials)))
    # The veterans PAC shares the 'veterans' subject with the enacted vets bill,
    # so a correlated vote should surface — clearly as correlation, not proof.
    vet_flow = next(f for f in ctx["flows"]
                    if f["donor"] and "Veterans" in f["donor"]["name"])
    assert vet_flow["correlated_votes"]


def test_promises_are_statements_but_typed():
    store = RecordStore()
    o = store.add_official(Official("Notional Member", "Rep", "House", "Nowhere"))
    store.add_statement(Promise(official_id=o.id, text="I will do X",
                                type=StatementType.SPEECH, sources=[_src()]))
    assert len(store.promises_for(o.id)) == 1
