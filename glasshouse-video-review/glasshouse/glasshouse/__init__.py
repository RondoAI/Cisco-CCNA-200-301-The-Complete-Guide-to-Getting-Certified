"""Glasshouse — an ethical event-intelligence engine.

Track events, not people. Verify, don't surveil. Show the receipts.
"""

from .models import Confidence, Event, Source, SourceKind  # noqa: F401
from .store import EventStore  # noqa: F401
from .verify import verify  # noqa: F401

__all__ = ["Event", "Source", "SourceKind", "Confidence", "EventStore", "verify"]
__version__ = "0.1.0"
