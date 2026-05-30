# Glasshouse — Groundwork

**A public accountability and world-intelligence platform.**
Sunlight, not surveillance. *Don't trust us — here's the receipt.*

This is the architecture you walk into Claude Code with. It is not a one-push
build; it is a phased monorepo where each module is built, tested, and grown over
many sessions. Pillar 2 already exists in seed form (the `glasshouse/`
verification engine shipped earlier) — this document folds it into the larger
system and lays out Pillar 1.

---

## 0. What this is — and is not

**Is:** an organized, sourced, verifiable record of what people in public power
*say* versus what they *do* — votes, bills, public statements, who funds them —
set against the economic and political context of their countries, and a verified
feed of world events. Built so the person in rural Alabama (or Khartoum, or
anywhere) can understand what their representatives are actually doing, in one
beautiful, legible place, with the primary source one click away.

**Is not:** an election-influence machine, a psychographic profiler, a tool that
tracks private citizens, or a partisan news outlet that asks for trust. We never
model "how someone thinks" to move votes. We never profile the public. We never
ask you to take our word — we show you the record and let you decide. These are
not preferences; they are enforced gates (see `CHARTER.md`).

> The full ambition — the public's intelligence hub, "data for everything,"
> bigger than Palantir but for the people — is in **[VISION.md](VISION.md)**.
> This document is how we build toward it; the Charter is the line we don't cross.

The product's only durable moat is **trust**, and trust comes from sourcing,
verification, and nonpartisanship — not from volume or hot takes.

---

## 1. Two pillars, one graph

### Pillar 1 — THE RECORD (public accountability)
The legible dossier of public power: officials, offices, parties, governments;
their votes, bills, public statements, and funding; promises vs. actions.

### Pillar 2 — THE WATCH (world-events intelligence)
The verified, "events not people" feed already prototyped in `glasshouse/`:
GDELT/ACLED/news/targeted-citizen footage → confidence-scored events with audit
trails and source protection.

**They connect.** A vote ("send funds to Israel," "close a deal with Iran") is an
edge in THE RECORD that links to the real-world events in THE WATCH. That linkage
— *this official cast this vote, here is what was happening on the ground, here is
who funds them* — is the thing no existing site does.

---

## 2. Core data model (THE RECORD)

Canonical IDs come from **Wikidata QIDs** wherever possible, so entities resolve
across languages and countries. Every fact is timestamped and carries Source(s)
that run through the Pillar-2 verification engine.

```
Person(official)      Wikidata QID; PUBLIC ROLE DATA ONLY. No private citizens.
  └─ holds → Position (with term qualifier: which parliament/term)
Body                  legislature / government / agency / political party
Position/Office       seat, role, term span
Statement             {type: speech|interview|floor|social|press}, text, when,
                      source_url, verification → for "said vs did"
Vote                  {bill_id, official_id, position: yea|nay|abstain, when}
Bill / Measure        title, summary, status, subject tags, sponsors
FundingFlow           Donor/PAC → Committee → Official  (FEC/OpenSecrets)
Promise               a stated commitment (a kind of Statement)
  └─ fulfilled_by / contradicted_by → Vote | Bill | outcome   ← killer edge
EconomyContext        country node: GDP, trade, budget (World Bank/IMF/Comtrade)
Source                (reused from glasshouse.models) — sourced & verified
```

**The killer feature** is the explicit, sourced edge between a `Promise` and the
later `Vote`/`Bill`/outcome that fulfilled or contradicted it. "Said X, did Y,
here are both receipts." Everything else is table stakes; this is the product.

---

## 3. Data sources (verified current)

**US legislative (primary, official):**
- `api.congress.gov` — official bills, votes, members, the Congressional Record
- GovInfo — official documents
- GovTrack — clean enrichment / historical votes (verify license)
- ProPublica Congress + Campaign Finance APIs — near-real-time (verify terms)

**Money in politics (US):**
- **FEC** — the official source for campaign finance
- **OpenSecrets** — bulk data + API over FEC/lobbying (registration; credit
  required; nonpartisan)

**Global officials & parliaments:**
- **Wikidata** — the entity spine (WikiProject "every politician" data model:
  officials, positions, parliamentary terms, parties)
- **IPU Parline** — 600+ data points direct from national parliaments
- **World Bank Database of Political Institutions** — ~180 countries, 40 years
- Comparative / Global Legislators Databases — academic enrichment

**Economic & trade context:**
- World Bank Open Data / World Development Indicators
- IMF data; UN Comtrade (trade flows)

**World events (Pillar 2, already wired):** GDELT 2.0, ACLED, news/RSS, plus
*targeted, licensed* citizen footage (never a firehose scrape).

> Rule: prefer the most **official, primary** source available, then enrich.
> Always store the source URL and run it through verification. Never present a
> derived figure without a path back to the primary filing.

---

## 4. The model/AI layer — the ALLOWED kind

Analysis of the public record. Never modeling of private psychology or persuasion.

- **RAG over the record** — "Everything Senator X said about Iran since 2020,
  with sources" → grounded answers, every sentence cite-backed to a primary doc.
- **Voting-pattern analysis** — cluster officials by how they actually vote
  (descriptive, not predictive-of-persuasion).
- **Contradiction detection** — flag where a present statement conflicts with a
  past one, or a promise conflicts with a vote. Surface both, let the user judge.
- **Funding-to-vote surfacing** — show correlations between funders and votes,
  *clearly labeled correlation, never causal/defamatory inference.*
- **Plain-language explainers** — turn a 200-page bill into "here's what it does,"
  always linking the actual text.

**Forbidden in the model layer:** psychographic/personality profiling, persuasion
or microtargeting, any modeling of private individuals, any "how to move this
voter." If a feature's value depends on changing how someone votes rather than
informing them, it does not ship.

---

## 5. Tech stack (pragmatic monorepo)

```
glasshouse/                  monorepo root
  CHARTER.md                 binding ethics gates (CI-enforced)
  ARCHITECTURE.md            this doc, kept living
  packages/
    record/                  Pillar 1: entity graph + ingestion
    watch/                   Pillar 2: the existing verification engine
    shared/                  Source model, verification, provenance (shared)
    api/                     FastAPI gateway over both pillars
    web/                     React visualization frontend
  workers/                   scheduled ingestion jobs (Congress, FEC, GDELT…)
  infra/                     docker-compose, migrations, deploy
```

- **Storage:** Postgres + PostGIS (events/geo) + **pgvector** (RAG) +
  a graph layer (Postgres+Apache AGE, or Neo4j) for THE RECORD's relationships.
- **Ingestion:** Python workers, one adapter per source, all writing through the
  shared verification/provenance layer (extend `glasshouse/ingest.py`).
- **Entity resolution:** match incoming names/IDs to Wikidata QIDs; dedupe.
- **Backend:** FastAPI gateway exposing read APIs + RAG endpoints.
- **Frontend:** React + a serious viz layer — timelines (promise vs. action),
  force-directed funding graphs, vote maps, country dashboards. This is where
  "beautifully visualized" is won; treat design as a first-class workstream.

---

## 6. Phased roadmap (Claude Code, milestone-by-milestone)

**Phase 0 — Foundation (commit the philosophy first).**
Monorepo + `CHARTER.md` + a CI check that fails the build if forbidden concepts
(person-profiling tables, psychographic fields) appear. Move the existing
`glasshouse/` engine into `packages/watch`. *Ethics become a gate, not a memo.*

**Phase 1 — THE RECORD, one country deep (US).**
Entity layer (Wikidata spine) → Congress.gov ingestion (members, bills, votes) →
the data model above → basic API. Goal: query any current US member's real
voting record, sourced.

**Phase 2 — Follow the money.**
FEC + OpenSecrets ingestion → FundingFlow edges → "who funds this official, and
how did they vote on related bills" (correlation, clearly labeled).

**Phase 3 — Said vs. did.**
Statement + Promise ingestion (speeches, floor remarks, interviews) → the
fulfilled_by / contradicted_by edges → contradiction detection. The headline
feature.

**Phase 4 — Context + RAG.**
World Bank / IMF / Comtrade economy nodes → RAG over the record with strict
source-grounded answers.

**Phase 5 — Go global.**
Generalize the ingestion to other parliaments via Wikidata + IPU Parline.
Sudan, UK, EU, etc. The data model was built country-agnostic for exactly this.

**Phase 6 — The product.**
The visualization frontend: official dashboards, funding graphs, promise-vs-action
timelines, the linked world-events feed. Ship for the non-expert.

**Cross-cutting from day one:** nonpartisan editorial standards, a public
methodology page, corrections policy, and the PBC + oversight-board structure.

---

## 7. First sprint (literally start here)

1. `git init` the monorepo; commit `CHARTER.md` and this file.
2. Move `packages/watch` ← the existing engine; tests green.
3. Stand up Postgres + the graph layer in `infra/docker-compose`.
4. Build the `Person/Position/Body/Vote/Bill` schema in `packages/record`.
5. Write the Congress.gov adapter (members + recent votes) through the shared
   Source/verification layer.
6. One API endpoint: `GET /record/official/{id}/votes` — sourced, verified.

When that returns a real, sourced voting record for one senator, you have proof
the whole system works. Everything after is repetition and scale.

---

## 8. Interface patterns adopted from the command-UI review (charter-bounded)

A review of dense command interfaces (Palantir Gotham/AIP) for *legibility*
inspiration — written up in `DESIGN-REVIEW.md`, governed by `CHARTER.md` and
`DECISIONS.md` **D2**. The principle: **adopt the legibility, re-point every
decision surface from force-employment to verification and accountability.**

Adopted into the visualization shell (§5 frontend, §1 spine item 5):

- **Verification instruments** — the confidence score decomposed into a glanceable
  gauge cluster on each event (score / distinct sources / checks-passed). The
  Gotham instrument aesthetic, pointed at *how we know* rather than at sensors.
- **Accountability-review queue** — a Confirm / Needs-corroboration / Dispute
  control on each event (the charter-safe analog of Approve/Reject/Comment). It
  flags the **record** and writes to the audit trail; it assigns no assets and
  triggers no action. Wire it through `packages/watch` → `learning.py` so a
  reviewer's verdict updates source reputation interpretably (resolves open O2).
- **Confidence-tier layer toggles + global filter/search** — layer controls
  re-pointed at confidence tiers, and a `⌘K` command-style filter over the feed.
- **Report→corroboration→resolution timeline** — enrich the single-track event
  timeline into a multi-track view of *when a claim was reported and how its
  verification evolved* (not an operation's execution phases).

Explicitly **out of bounds** (recorded so the line stays bright): live sensor/ISR
feeds, asset/course-of-action assignment, any "execute" affordance, any person or
order-of-battle entity. See `DOMAINS.md` "Hard line" and `CHARTER.md`.

```
Intentions don't survive a funding crunch. Structure does.
```
