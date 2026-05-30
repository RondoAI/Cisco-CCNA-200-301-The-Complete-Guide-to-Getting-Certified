"""Glasshouse — an ethical event-intelligence engine.

Track events, not people. Verify, don't surveil. Show the receipts.
"""

from .models import Confidence, Event, Source, SourceKind  # noqa: F401
from .record import (Bill, Fulfillment, Official, Promise,  # noqa: F401
                     PromiseAssessment, RecordStore, Statement, Vote,
                     assess_promise, assert_charter_safe)
from .store import EventStore  # noqa: F401
from .verify import verify  # noqa: F401

__all__ = [
    "Event", "Source", "SourceKind", "Confidence", "EventStore", "verify",
    # THE RECORD (Pillar 1)
    "Official", "Bill", "Vote", "Statement", "Promise", "PromiseAssessment",
    "Fulfillment", "RecordStore", "assess_promise", "assert_charter_safe",
]
__version__ = "0.2.0"
