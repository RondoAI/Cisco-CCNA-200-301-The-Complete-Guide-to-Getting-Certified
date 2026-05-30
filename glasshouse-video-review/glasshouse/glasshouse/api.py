"""
HTTP API. Read-only by design for the public surface: consumers see events,
confidence and the full audit trail — never anything that could identify a
source, because no such field exists on the public representation.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from .ingest import CitizenMediaAdapter, GDELTAdapter
from .record import RecordStore
from .record_seed import seed_record
from .seed import seed_events
from .store import EventStore

store = EventStore()
record = RecordStore()


def bootstrap() -> None:
    """Load live GDELT if networked, otherwise representative seed data."""
    for ev in GDELTAdapter().fetch():
        store.ingest(ev)
    for ev in seed_events():
        store.ingest(ev)
    seed_record(record)   # THE RECORD — notional officials/promises/votes


app = FastAPI(title="Glasshouse", version="0.1.0",
              description="Ethical event-intelligence. Events, not people.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

bootstrap()

_WEB = Path(__file__).resolve().parent.parent / "web" / "index.html"


@app.get("/")
def dashboard():
    return FileResponse(_WEB) if _WEB.exists() else {"service": "glasshouse"}


@app.get("/api/events")
def list_events(region: str | None = None, min_confidence: str | None = None):
    events = store.all()
    if region:
        events = [e for e in events if e.region.lower() == region.lower()]
    if min_confidence:
        order = ["disputed", "unverified", "emerging", "corroborated", "confirmed"]
        floor = order.index(min_confidence) if min_confidence in order else 0
        events = [e for e in events if order.index(e.confidence.value) >= floor]
    return {"count": len(events), "events": [e.to_public_dict() for e in events]}


@app.get("/api/events/{event_id}")
def get_event(event_id: str):
    ev = store.get(event_id)
    if not ev:
        raise HTTPException(404, "event not found")
    return ev.to_public_dict()


@app.post("/api/ingest/citizen")
def ingest_citizen(payload: dict):
    """Accept a raw citizen-media record. Identity is stripped at the adapter
    boundary before the event is ever stored or scored."""
    events = CitizenMediaAdapter(raw_records=[payload]).fetch()
    stored = [store.ingest(e).to_public_dict() for e in events]
    return {"ingested": stored}


# --- THE RECORD (Pillar 1) — public accountability, read-only ----------------
@app.get("/api/record/officials")
def list_officials():
    return {"count": len(record.officials),
            "officials": [o.to_public_dict() for o in record.officials.values()]}


@app.get("/api/record/officials/{official_id}/votes")
def official_votes(official_id: str):
    if official_id not in record.officials:
        raise HTTPException(404, "official not found")
    return {"votes": [v.to_public_dict() for v in record.votes_for(official_id)]}


@app.get("/api/record/officials/{official_id}/scorecard")
def official_scorecard(official_id: str):
    """Said vs. did: each promise next to the recorded action and verdict,
    with both receipts. The headline accountability view."""
    card = record.scorecard(official_id)
    if not card:
        raise HTTPException(404, "official not found")
    return card
