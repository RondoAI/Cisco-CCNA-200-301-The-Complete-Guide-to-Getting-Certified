# Glasshouse — command-UI video review

This folder is a **deliverable bundle**, not part of the Cisco CCNA study
materials. It lives here only because this was the repository attached to the
working session and the only remote available to push to (the `glasshouse`
project has no GitHub remote of its own). Move it into the real `glasshouse`
repo when convenient — it is a self-contained drop-in copy of the project plus
the review.

## What this is

A review of Palantir Gotham/AIP command interfaces (two Gotham screenshots + the
AIPCon 9 and Paragon 2025 talks) as **UI/UX inspiration** for the Glasshouse
console, kept strictly inside Glasshouse's `CHARTER.md` (no operational/targeting
capability — only legibility, verification, and accountability).

## Contents (the three deliverables)

1. **Written review** — [`glasshouse/DESIGN-REVIEW.md`](glasshouse/DESIGN-REVIEW.md):
   pattern-by-pattern adopt / adapt / reject, with charter reasoning.
2. **Implemented UI** — changes in [`glasshouse/web/index.html`](glasshouse/web/index.html):
   confidence-tier filter legend, working `⌘K` search, verification "instrument"
   gauges, and a charter-safe accountability-review action row.
3. **Roadmap/feature proposals** — folded into
   [`glasshouse/DECISIONS.md`](glasshouse/DECISIONS.md) (proposed D8–D10, and a
   recommended answer to open question O2/O3) and
   [`glasshouse/ARCHITECTURE.md`](glasshouse/ARCHITECTURE.md) (new §8).

## Also on this branch (beyond the video review)

The branch grew into early build work on the project itself:

- **`glasshouse/VISION.md`** — the mission ("intelligence hub for the people,
  bigger than Palantir but for the public, ethical, data for everything"),
  governed by the Charter; linked from the README and `ARCHITECTURE.md §0`.
- **THE RECORD (Pillar 1)** — `glasshouse/glasshouse/record.py` (+ `record_seed.py`,
  tests, API): officials, bills, votes, promises, the sourced **promise → vote →
  outcome** edge, **and the money layer** — `Donor` / `FundingFlow` with FARA
  **foreign-principal** tracing and **labelled-correlation** linkage to votes
  (who funds an official, how it traces to a foreign government, and which votes
  it correlates with — sourced, nonpartisan, never causal). Public power only,
  provenance mandatory, charter-guarded in code. Endpoints under `/api/record/...`
  (`scorecard`, `funding`, `statements`). Full suite: **29 tests passing**.
- **Global voices (public figures, public words)** — `Statement` now carries
  original-language text + faithful **translation** + sourced **context**, and
  `Official` is country-agnostic (`country` + `Level.NATIONAL`/`INTERNATIONAL`),
  so a foreign leader's public post can be archived as a sourced primary-source
  perspective beside the press. `/api/record/officials/{id}/statements`. Scope is
  pinned in `DECISIONS.md` **D7**: public figures + public statements only —
  archive/translate, never surveil or psychoanalyze.
- **The political map (elections)** — `glasshouse/glasshouse/elections.py`: real
  county-level presidential results (every county, 2020 + 2024) with per-county
  winner / signed margin / lean, state + national rollups, closest races, and
  cross-cycle **flips** — FIPS-keyed to the county GeoJSON for a zoomable
  choropleth. Endpoints `/api/elections/map|national|state/{s}|county/{fips}|flips`.
  Verified live: 2024 R+1.48% (77.3M/75.0M), 86 D→R county flips, closest county
  Talbot MD at 0.03%. Full suite: **36 tests passing**.
- **Real U.S. roster** — `glasshouse/glasshouse/congress.py`: every current
  Senator and Representative (all states), party, district, term end and
  next-election year, from the keyless `unitedstates/congress-legislators`
  dataset. `GLASSHOUSE_LIVE=1` pulls the live **~535-member** roster (verified:
  536 members, 56 states/territories, 436 House / 100 Senate). New endpoints
  `/api/record/summary` (whole-country layout) and `/api/record/officials`
  (filter by `state` / `chamber` / `party` / `next_election`). Votes, statements
  and funding for real members layer on next via keyed Congress.gov / FEC.
- **`glasshouse/docs/FOUNDATION.md`** — the build foundation you asked about:
  open-database catalog, the agentic ingestion swarm, the incentive-mechanism
  design + guardrails (open decision O7), satellite/CV OSINT scope, the own-maps
  visualization stack (O8), and the **storage / secure-cloud setup** recommendation.

## Run the project

```bash
cd glasshouse
pip install -r requirements.txt
python run.py        # dashboard + API at http://127.0.0.1:8000
pytest -q
```

`web/index.html` also opens standalone in a browser on its built-in sample data.

> Source note: YouTube blocked automated transcription of the three videos from
> the build environment, so the review leans on the two first-hand screenshots
> plus public descriptions of the talks. See the method note in `DESIGN-REVIEW.md`.
