# Decision Log

This is deliberate, consequential work. Decisions get recorded here — what we
settled and *why* — so we don't drift, and so anyone joining sees the reasoning.
Slowing down to write these is the point.

Format: each decision is **Settled** or **Open**. Settled ones can be revisited,
but only by adding a new entry that supersedes the old — never by quietly changing
course.

---

## Settled

**D1 — Events, not people.** The system models what happened, where, and how we
know. No private-individual profiles. *Why:* it is the difference between
accountability and surveillance, and it is our only durable moat (trust).

**D2 — Sunlight, not surveillance; no operational military capability.** No
targeting, force-employment/course-of-action planning, weapons identification, or
ISR that supports a kill chain. *Why:* this is where a tool like this does
irreversible harm; building it would make us the thing we set out to hold
accountable. (Reaffirmed when reviewing Palantir Gotham as a UI reference: we take
the interface ambition, not the targeting function.)

**D3 — Show the receipt.** Every claim links to a primary source; every score
decomposes into an inspectable audit trail. No "trust us instead of the media."
*Why:* nothing to discredit when it's their own record.

**D4 — Architecture is a spine + pluggable layers.** Build the spine (entity
graph, verification, space-time index, visualization shell) deep; snap domains on
over time. *Why:* lets the platform grow without re-architecting.

**D5 — Verification learns, but stays interpretable.** Bayesian source reputation +
independence-aware corroboration, never a black box. *Why:* a learned score is
only trustworthy if it's still a receipt.

**D6 — Build order favors depth over breadth.** Spine + 3–4 killer layers deep,
not 25 shallow feeds. *Why:* aggregator dashboards already relay feeds cheaply; our
edge is depth and trust.

**D7 — Public figures' public statements are in scope; surveillance is not.** A
public figure's own *public* words — a head of state, parliamentarian, party/
faction leader, government spokesperson, or official institution, including
verified public social-media posts — are a **primary source** we archive,
translate and contextualize, and set beside the press so the reader weighs a
genuinely global range of perspectives (gate 4). This sharpens, never weakens,
the gates and is bounded hard: **(a)** public figures only — never private
citizens; **(b)** only what they said *in public* — no private/DM/hacked content;
**(c)** we archive and translate, we **never** infer private psychology or model
a person to predict or change behavior (gate 2); **(d)** a curated set of
public-figure accounts, not a platform firehose; **(e)** public figures need no
source protection, but citizen media is still stripped at intake (gate 5). *Why:*
hearing leaders in Iran, Lebanon or anywhere in their own words is informing, not
spying — and it is the antidote to a single-narrative view. (Implemented:
`Statement` with original-language + translation + context; foreign `Official`s
via `country`/`Level.NATIONAL`.)

---

## Open (resolve before building further)

**O1 — Which is the first killer layer to build deep?** Candidates: conflict/events
(seed exists), governance/accountability (the public-record graph), verified news.
*Pick one to take all the way through first.*

**O2 — Confirmation source for the learning loop.** Automated ground-truth anchors,
a human-review queue, or both. (Recommendation in prior discussion: both, humans in
the loop until automated anchors earn their own reputation.)

**O3 — Public-facing visual identity.** Clean/editorial (matches the "transparency"
brand) vs. dense/dark "operations" view (matches the live-monitoring feel). May be
both, for different surfaces.

**O4 — License.** Repo currently defaults to all-rights-reserved. Open-source was a
stated value; AGPL-3.0 is a strong candidate (open, auditable, anti-lock-in,
copyleft). *Needs a real decision before any public release.*

**O5 — Corporate + governance structure.** PBC + independent oversight board with
charter-veto power (per CHARTER.md). When to incorporate.

**O6 — Hosting / data residency.** Where this runs, and how source-protection
survives the infrastructure choices (subpoenas, jurisdiction). *See the storage
recommendation in `docs/FOUNDATION.md` §7 — isolate citizen intake, strip before
store, decide jurisdiction before real source data lands.*

**O7 — Contribution incentive mechanism (Bittensor-style).** Whether to reward
contributors/agents for verified data, and how. *Hard constraint:* reward must be
**unlinkable to on-the-ground source identity** (paying a filmer can expose them —
the privacy tests stay green), and a contribution earns only *after* it survives
verification, never on submission. *Do not build until resolved.* See
`docs/FOUNDATION.md` §4.

**O8 — Own maps & visualization stack.** Recommendation on the table: MapLibre GL
+ self-hosted OSM vector tiles + deck.gl overlays + a force-directed money/power
graph, replacing the seed's Leaflet/Carto placeholder. Confirm before investing.
See `docs/FOUNDATION.md` §6.

**O9 — On-the-ground & imagery scope.** OSINT analysis of *open/published*
satellite/aerial imagery and *licensed, identity-stripped* citizen footage is in
scope; operating our own collection (drones/sensors) or any imagery that tracks a
private individual is **out** (CHARTER gate #1, DOMAINS hard line). Recorded so
the line is explicit before anyone builds toward it.

---

## Proposed (from the command-UI video review — not yet ratified)

Raised in `DESIGN-REVIEW.md` after reviewing Palantir Gotham/AIP screens and
AIPCon/Paragon material as *interface* references. Recorded here as proposals so
they get the same deliberate treatment as everything else; promote to **Settled**
only on a real decision.

**D8 (proposed) — Verification instruments are a first-class dossier element.**
Render the confidence score and its audit decomposition as a glanceable gauge
cluster (score / distinct sources / checks-passed) on every event, on both web
surfaces. *Why:* it borrows Gotham's instrument-cluster legibility while keeping
the needles pointed at *how we know*, not at sensors. Prototyped in
`web/index.html`. Honours D3/D5 — the gauge always decomposes back to the receipt.

**D9 (proposed, and a recommended answer to O2) — The accountability-review
action becomes a real human-in-the-loop queue.** The dossier's Confirm / Needs
corroboration / Dispute controls (the charter-safe analog of Gotham's
Approve/Reject/Comment) should write through to `learning.py`, so a reviewer's
verdict updates source reputation via the existing Bayesian loop. *Why:* it gives
us the "humans in the loop until automated anchors earn their reputation" answer
O2 was looking for — interpretably (D5), and never as an operational action (D2).

**D10 (proposed) — Pursue the AIP-style agent layer only in its allowed form.**
"Actionable intelligence from every interaction" (Paragon/Healthpeak) maps to
*grounded, cite-backed RAG over the public record* (ARCHITECTURE.md §4) — never
persuasion, microtargeting, or any autonomous action on the world. *Why:* Gate 3
and Gate 4 govern any agent we ship; an agent may inform and cite, full stop.

**On O3 (visual identity) — leaning resolved.** Keep *both* existing surfaces:
the dark "operations" console (`web/index.html`) and the light "editorial/paper"
dashboard (`web/engine-dashboard.html`), sharing one component vocabulary, for
different audiences. The review found this dual-surface answer is a feature, not
indecision.
