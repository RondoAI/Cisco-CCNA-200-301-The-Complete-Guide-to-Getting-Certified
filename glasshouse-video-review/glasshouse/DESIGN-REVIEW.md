# Design Review — Palantir command interfaces as charter-bounded inspiration

**Branch:** `claude/video-review`  ·  **Scope:** UI/UX + feature ideas for the
Glasshouse console, mined from Palantir reference material and filtered through
`CHARTER.md`. Nothing in here loosens a gate. Where a Palantir pattern only makes
sense as an operational/targeting capability, it is **rejected on the record**,
not quietly dropped.

> The governing line is already settled in `DECISIONS.md` **D2**: *"we take the
> interface ambition, not the targeting function."* This document is the concrete
> application of that decision.

---

## 1. What was reviewed

**Screenshots (the strongest design signal):**

- **`1000006359.png`** — a Gotham/AIP maritime operations screen: a live map of
  the South China Sea with tracked vessels, an entity-detail card ("Ship
  detection model") reading out a structured spec sheet, and an instrument
  cluster along the bottom (EO/IR feed, capture-angle compass, sensor dials).
- **`1000006360.png`** — a Gotham "Global Overview" with a `UNCLASSIFIED //
  NOTIONAL DATA` banner: a situation ("Threats to US Embassy in Ziarovo") on the
  left, a **course-of-action panel** on the right with **Approve / Reject /
  Comment**, asset requirements, a feasibility/complexity readout, and a phased
  **Gantt timeline** along the bottom.

**Videos (Palantir channel):**

- *"Magical on the Front Lines | Intro at AIPCon 9"* — operational/defense AI on
  the edge.
- *"Alex Karp Opening Remarks | AIPCon 9"* — the mission/strategy framing.
- *"Actionable Intelligence from Every Tenant Interaction | Healthpeak at Paragon
  2025"* — the same ontology+agent operating system pointed at an **enterprise,
  non-defense** vertical (real-estate operations); "learn from every
  interaction."

> **Method note / limitation:** YouTube's player blocked automated transcription
> from this environment (bot-check on every `watch?v=` fetch). Titles, channel,
> and dates were confirmed via the oEmbed endpoint and web search; video content
> is characterized from public descriptions plus Palantir's well-documented
> Gotham/AIP/Foundry patterns. **The two screenshots are the primary, first-hand
> design reference** and carry most of the weight below. If you want claims tied
> to specific timestamps, drop the transcripts in and I'll revise.

---

## 2. The reframe (why these are safe to learn from)

Palantir's genius here is **legibility under pressure**: a dense situation made
instantly readable, every object inspectable, a decision surface attached to the
data. That ambition is exactly what Glasshouse wants. The danger is that
Palantir's *decision surface* is a **kill chain** — approve a course of action,
assign assets, strike.

So the rule for every pattern below:

> **Adopt the legibility. Re-point the decision surface from *force employment* to
> *verification and public accountability*.** Glasshouse's "action" is never "do
> X to a target" — it is "confirm / dispute / corroborate / cite this claim."

---

## 3. Pattern-by-pattern: adopt / adapt / reject

| # | Palantir pattern (source) | Verdict | Glasshouse adaptation | Charter check |
|---|---|---|---|---|
| A | `NOTIONAL DATA` banner (shot 2) | **Adopt** | Already present as `SAMPLE · NOTIONAL DATA`. Keep it loud; never let sample data read as fact. | Gate 4 (show the receipt) — reinforces it. |
| B | Entity-detail card with structured spec readout (shot 1) | **Adapt** | The dossier already does this for events. Keep it about the **event and its provenance**, never a person or a unit's order-of-battle. The existing "Reference — identify & cite only" card is the correct ceiling. | Gate 1 (events, not people). |
| C | Instrument cluster — EO feed, capture-angle compass, sensor dials (shot 1) | **Adapt** | **Implemented:** a "Verification instruments" row of gauges (confidence score, distinct sources, checks passed). Same glanceable aesthetic, but the needles measure *how we know*, not *what a sensor sees*. | Gate 4. **Rejected:** any live sensor/ISR feed — that is collection that can feed a kill chain (`DOMAINS.md` hard line). |
| D | Course-of-action panel: **Approve / Reject / Comment** + asset assignment (shot 2) | **Adapt (the control), reject (the meaning)** | **Implemented:** an **Accountability-review** row — **Confirm / Needs corroboration / Dispute** — that flags the *record* and appends to the audit trail. It is explicitly *not* a command surface; it assigns no assets and triggers no action. | Gate 3 (no persuasion/operational engine); **D2**. This is the single most important reframe in the review. |
| E | Feasibility / complexity / time-to-execute scoring (shot 2) | **Adapt** | Re-point "feasibility" → **verifiability**: the confidence score decomposed into its audit checks. We already have the math; the gauges now make it glanceable. | Gate 4 — score must always decompose to a receipt (D3, D5). |
| F | Phased **Gantt timeline** of an operation (shot 2) | **Adapt** | Glasshouse's timeline tracks **when events were reported and corroborated**, not when to execute phases of an operation. Roadmap: enrich the current 24h dot-strip into a multi-track "report → corroboration → dispute/resolution" timeline. | Gate 2 (track events). |
| G | Global map + left situation rail + right detail drawer (both shots) | **Adopt** | This is already Glasshouse's exact layout (feed / map / dossier). Validates the existing shell; the review tightens it rather than rebuilds it. | — |
| H | Command palette / global search ("⌘K", "On Sea") | **Adopt** | **Implemented:** the search box now filters the live feed; `⌘K`/`Ctrl-K` focuses it, `Esc` clears it / closes the dossier. | — |
| I | Layer toggles (sensor/asset layers) | **Adapt** | **Implemented:** the confidence legend doubles as a **filter** — click a tier to show/hide it; counts update live. Same affordance, pointed at *confidence tiers* instead of weapon/sensor layers. | Gate 4 — lets a user isolate "what's only emerging/unverified." |
| J | AIP **agentic operating system** — "actionable intelligence from every interaction" (Healthpeak/Paragon) | **Adapt, carefully** | The allowed analog already lives in `ARCHITECTURE.md §4`: **grounded RAG over the public record** ("everything Senator X said about Iran, with sources"). "Learn from every interaction" → the **Bayesian source-reputation loop** (`learning.py`), which already learns — interpretably (D5). | Gates 3 & 4 — agents may *inform and cite*, never *persuade* or act. No autonomous action on the world. |
| K | "Front lines" / force-employment framing (AIPCon 9) | **Reject** | Out of scope by definition. Recorded here so the boundary is explicit, not assumed. | **D2** — hard gate. |
| L | Karp keynote's "us vs. them" institutional framing | **Note, don't adopt** | Glasshouse's stance is **nonpartisan by standard** (Gate 5). We borrow the conviction that the tool's *values must be structural*, which we already encode as a CI-enforced charter — arguably a stronger version of the same idea. | Gate 5. |

---

## 4. What this PR implements (in `web/index.html`)

All additions are pure front-end, on the existing sample data, and run offline:

1. **Status strip** — `N tracked · N shown · N disputed` (the Gotham "overview"
   read), updating live with the filter.
2. **Confidence legend as a filter** (pattern I) — click any tier to toggle it;
   filtered-out events stay on the map but dim to 12% so the picture never
   silently loses pins.
3. **Working search** (pattern H) — filters by headline / region / tags; `⌘K`
   focuses, `Esc` clears or closes the dossier.
4. **Verification instruments** (pattern C/E) — a three-gauge row in the dossier:
   confidence score, distinct sources, checks-passed, each with a bar.
5. **Accountability-review actions** (pattern D) — **Confirm / Needs
   corroboration / Dispute**, each appending a timestamped `analyst_review` line
   to the event's audit trail and re-rendering the receipt. A standing caption
   states plainly that these flag the record and never trigger an operational
   action.

Deliberately **not** built: any sensor feed, any asset/COA assignment, any
person entity, any "execute" affordance.

---

## 5. Proposed next steps (folded into the planning docs)

See the new entries in `DECISIONS.md` (proposed D8–D10) and `ARCHITECTURE.md §8`:

- **D8** — adopt the "verification instruments" pattern as a first-class dossier
  element across both web surfaces.
- **D9** — make the accountability-review action a real **human-in-the-loop
  queue** wired to `learning.py` (this is also the recommended resolution to open
  question **O2**), so a reviewer's Confirm/Dispute updates source reputation
  through the existing Bayesian loop — interpretably (D5).
- **D10** — pursue the AIP-style agent layer only in its allowed form: grounded,
  cite-backed RAG over the record (`ARCHITECTURE.md §4`); never persuasion or
  autonomous action.
- Open question **O3** (visual identity): the two surfaces we have — the dark
  "operations" console (`index.html`) and the light "editorial/paper"
  dashboard (`engine-dashboard.html`) — are a good answer. Keep **both**, for
  different audiences, sharing one component vocabulary.

---

## 6. One-paragraph verdict

Palantir is the right north star for *legibility* and the wrong one for *purpose*.
The screenshots prove a dense, live, inspectable picture can be beautiful and
fast; we should steal that without apology. But the moment the interface offers
an action, ours must point at **the record** — confirm it, dispute it, corroborate
it, cite it — never at a target. The charter already says this; this PR makes the
UI say it too.
