# Glasshouse

**An open, verifiable platform for understanding the world and holding public power
accountable.** Sunlight, not surveillance. *Don't trust us — here's the receipt.*

Glasshouse fuses open data — conflict events, government records, news, economics,
weather, public movement telemetry — into one legible, verified, beautifully
visualized picture of what is happening on Earth, and what the people in power are
actually doing. Built so anyone, anywhere, can be informed without taking a
pundit's or a government's word for it.

---

## Scope boundary — read this first

Glasshouse builds **situational awareness and accountability**: understanding
events, and making the public record of public power legible.

Glasshouse does **not** build operational military capability. No course-of-action
or force-employment planning, no targeting, no weapons/munition identification, no
ISR that supports a kill chain, no profiling of private individuals. These are
hard gates, enforced in code review, not preferences. See **[CHARTER.md](CHARTER.md)**.

We take visual *inspiration* from dense command interfaces (instant legibility, a
live map, a readable timeline) — but we build our own design for *informing*, never
for striking.

---

## The documents (the thinking, get these right before coding)

- **[VISION.md](VISION.md)** — where this is going: the intelligence hub for the
  public, bigger than Palantir but for the people. *Governed by the Charter.*
- **[CHARTER.md](CHARTER.md)** — the binding ethical gates (CI-enforced).
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — the spine + data model + roadmap.
- **[DOMAINS.md](DOMAINS.md)** — the intelligence layers and their open sources.
- **[DECISIONS.md](DECISIONS.md)** — the decision log: what's settled, what's open.
- **[docs/FOUNDATION.md](docs/FOUNDATION.md)** — data-source catalog, agent swarm, and the infra/storage setup.
- **[docs/specs/](docs/specs/)** — the interface reference library: teardowns of command-UI videos (legibility we adopt; targeting we reject), condensed into component specs.
- **[docs/ENGINE.md](docs/ENGINE.md)** — the running verification engine's readme.

## What runs today (seed, not the system)

A working verification engine — the part where bugs hurt real people, so it is
built first and most carefully:

```bash
pip install -r requirements.txt
python run.py                    # dashboard + API at http://127.0.0.1:8000
GLASSHOUSE_LIVE=1 python run.py  # pulls the real U.S. roster + county election map
pytest -q                        # 36 tests: verification, privacy, learning, enrichment, the record, elections
```

- `glasshouse/models.py` — events, not people; provenance baked in
- `glasshouse/verify.py` — corroboration + recycled-media + audit trail
- `glasshouse/privacy.py` — source-protection at intake
- `glasshouse/learning.py` — Bayesian source-reputation feedback loop
- `glasshouse/enrich.py` — geocode / classify / dedupe pipeline
- `glasshouse/record.py` — **THE RECORD (Pillar 1):** officials, bills, votes,
  promises, the sourced promise→vote→outcome edge, and the money layer
  (`Donor`/`FundingFlow`, FARA foreign-principal tracing) (`/api/record/...`).
  Public power only; provenance mandatory; charter-guarded in code.
- `glasshouse/congress.py` — **the real U.S. roster:** every current Senator and
  Representative (all states), party, district, term end and next-election year,
  from the keyless `unitedstates/congress-legislators` dataset.
  `/api/record/summary` lays out the whole country; `/api/record/officials?state=CA`
  filters it. (Live with `GLASSHOUSE_LIVE=1`; offline sample otherwise.)
- `glasshouse/elections.py` — **the political map:** real county-level
  presidential results (every county, 2020 + 2024), with per-county winner,
  signed margin, lean bucket, state/national rollups, closest races and
  cross-cycle **flips** — FIPS-keyed to join the county GeoJSON for a zoomable
  choropleth. `/api/elections/map`, `/national`, `/state/{s}`, `/county/{fips}`,
  `/flips`. (Keyless `tonmcg` dataset; live with `GLASSHOUSE_LIVE=1`.)
- `web/index.html` — the world-intelligence console (map + signals feed + the receipt + timeline)
- `web/engine-dashboard.html` — the engine's API-connected view

> Current layout is a single package (the seed). The target monorepo
> (`packages/spine`, `packages/watch`, `packages/record`, …) is in ARCHITECTURE.md
> and is a migration to do early in Claude Code, not a thing to fake now.

## Status

Groundwork + a running, tested verification seed. **Not** production. The
verification and privacy code needs adversarial review and a security audit
before anyone relies on what it says about a real event.

---

## Begin work: push this to GitHub, then build in Claude Code

This folder is already a git repo with an initial commit.

```bash
# 1. create the repo on GitHub (using the GitHub CLI)
gh repo create glasshouse --private --source=. --remote=origin

#    …or create it in the browser, then:
git remote add origin https://github.com/<you>/glasshouse.git
git branch -M main
git push -u origin main
```

Then open the folder in **Claude Code** (your terminal) and build incrementally —
that's the tool that holds a persistent environment across sessions, runs the
database, and grows this for real. Start from the first sprint in ARCHITECTURE.md
once the open decisions in DECISIONS.md are settled.
