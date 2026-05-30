"""Glasshouse — an ethical event-intelligence engine.

Track events, not people. Verify, don't surveil. Show the receipts.
"""

from .congress import CongressAdapter  # noqa: F401
from .models import Confidence, Event, Source, SourceKind  # noqa: F401
from .record import (Bill, Donor, DonorType, Fulfillment,  # noqa: F401
                     FundingFlow, Official, Promise, PromiseAssessment,
                     RecordStore, Statement, Vote, assess_promise,
                     assert_charter_safe)
from .store import EventStore  # noqa: F401
from .verify import verify  # noqa: F401

__all__ = [
    "Event", "Source", "SourceKind", "Confidence", "EventStore", "verify",
    # THE RECORD (Pillar 1)
    "Official", "Bill", "Vote", "Statement", "Promise", "PromiseAssessment",
    "Fulfillment", "Donor", "DonorType", "FundingFlow", "RecordStore",
    "assess_promise", "assert_charter_safe", "CongressAdapter",
]
__version__ = "0.2.0"
