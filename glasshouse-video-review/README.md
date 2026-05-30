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
   [`glasshouse/DECISIONS.md`](glasshouse/DECISIONS.md) (proposed D7–D9, and a
   recommended answer to open question O2/O3) and
   [`glasshouse/ARCHITECTURE.md`](glasshouse/ARCHITECTURE.md) (new §8).

## Also on this branch (beyond the video review)

The branch grew into early build work on the project itself:

- **`glasshouse/VISION.md`** — the mission ("intelligence hub for the people,
  bigger than Palantir but for the public, ethical, data for everything"),
  governed by the Charter; linked from the README and `ARCHITECTURE.md §0`.
- **THE RECORD (Pillar 1), first slice** — `glasshouse/glasshouse/record.py`
  (+ `record_seed.py`, tests, API): officials, bills, votes, promises, and the
  sourced **promise → vote → outcome** edge. Public power only, provenance
  mandatory, charter-guarded in code. New endpoints under `/api/record/...`;
  the offline scorecard returns fulfilled / contradicted / unresolved with both
  receipts. Full suite: **19 tests passing**.

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
