# Glasshouse

**An ethical event-intelligence engine.** Track *events*, not people. Verify,
don't surveil. Show the receipts.

Glasshouse fuses open conflict/event feeds (GDELT, ACLED-style NGO data, news,
and *targeted* citizen footage) into confidence-scored events with a full,
inspectable verification trail. The differentiation is not collection — feeds
are commodities — it is **verification + source protection + provenance**, and
those principles live in the code, not on a values page.

## Why this design is the moat
A competitor can copy your data sources in a weekend. What they cannot cheaply
copy is a verification stack that institutions, newsrooms and courts *trust*.
So three commitments are structural here, enforced at the boundary:

1. **Events, not people.** There is no person/profile/watchlist entity anywhere
   in the model (`models.py`). Adding one would be a change of mission, not a
   feature. The system can only describe what happened, where, and how we know.
2. **Source protection at intake.** Citizen-media identity (handle, phone,
   device, IP…) is stripped *before* it ever becomes a `Source`
   (`privacy.py`). Only what verifies the footage is kept, plus a one-way dedup
   token from which the handle cannot be recovered. In Sudan or Iran, surfacing
   the filmer can get them killed — so this is not a toggle.
3. **Provenance is mandatory.** Every event carries its sources and an
   append-only audit trail of every check that ran (`verify.py`). You can always
   answer "how do we know this?"

## Architecture
```
ingest.py   GDELT / RSS / citizen adapters  →  everything enters here
privacy.py  identity stripping for citizen media (the ethical boundary)
models.py   Event, Source, audit trail — provenance baked in, no person entity
verify.py   ordered checks → confidence score + audit trail  ← the moat
store.py    in-memory store; merges nearby same-day events; tracks media hashes
api.py      FastAPI read-only public surface + citizen ingest
web/        editorial dashboard: map + feed + provenance "receipts" drawer
```

### The verification pipeline (`verify.py`)
Runs in order, each step appending to the audit trail:
`has_sources → independent_corroboration → source_quality →
recency_consistency → recycled_media`. Independent corroboration counts
*distinct domains* (one outlet reposting another isn't corroboration). A hard
failure — recycled footage, a source predating the event — marks an event
**DISPUTED**, which corroboration cannot silently override. That last guarantee
is the difference between journalism and a viral-misinformation amplifier.

## Run it
```bash
pip install -r requirements.txt
python run.py          # → http://127.0.0.1:8000   (dashboard + API)
pytest -q              # 7 tests: privacy + verification
```
Runs fully offline on representative seed data (including a rigged recycled-clip
case so you can watch the pipeline flag it). To pull live global events:
```bash
GLASSHOUSE_LIVE=1 python run.py     # fetches the rolling GDELT 2.0 export
```

## What's real vs. stubbed
**Real:** the data model, the privacy boundary, the verification pipeline +
scoring + audit trail, event merging/dedup, the GDELT 2.0 fetch/parse, the
FastAPI surface, the dashboard.
**Stubbed for you to deepen (interfaces are stable, swap the bodies):**
- `verify.py` checks → perceptual-hash media matching, satellite/landmark
  **geolocation**, shadow-based **chronolocation**, model-assisted disinfo flags.
- `ingest.py` RSS → real feed parsing + NER + geocoding.
- Citizen intake → a *licensed* provider for targeted location/keyword/time
  pulls (deliberately **not** a Twitter/X firehose scraper — narrower, cheaper,
  defensible).
- `store.py` → Postgres/PostGIS.

## Hard rules for whoever builds on this
- Never add a per-person profile, tracker, or watchlist.
- Never store recoverable uploader identity. The redaction tests must stay green.
- Provenance is non-negotiable: no event ships without its audit trail.
- Incorporate as a PBC; the binding acceptable-use policy and an oversight board
  with veto power are what protect this from your own future cash-crunch.
```
Intentions don't survive a funding crunch. Structure does.
```
