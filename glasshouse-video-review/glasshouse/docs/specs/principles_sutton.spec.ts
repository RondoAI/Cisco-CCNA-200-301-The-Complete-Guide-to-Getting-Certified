/**
 * principles_sutton.spec.ts — PRINCIPLES-001 (code-form note, not a build).
 * ============================================================================
 * "Think like this." The frame from Rich Sutton — "AI creativity & discovery"
 * (YouTube K5LAFEjTlBA), The Bitter Lesson, the Era of Experience, the Alberta
 * Plan — translated into binding design principles for Glasshouse. Encoded as
 * code so it steers the build precisely, not as a vibe.
 *
 * Core Sutton claims we are adopting:
 *   - "We want agents that can DISCOVER like we can, not which CONTAIN what we
 *      have discovered."
 *   - Bitter Lesson: general methods that scale with computation (SEARCH +
 *     LEARNING) beat hand-encoded human knowledge in the long run.
 *   - Era of Experience: learn from on-the-job experience + reward, not static
 *     data; imitation is a weak prior because it "lacks ground truth."
 *   - Build "algorithms for acquiring & organizing knowledge," not the knowledge.
 *
 * The Glasshouse twist (where we extend, and where we diverge — see DIVERGENCE):
 *   verification MANUFACTURES the ground truth Sutton says imitation lacks, so
 *   our verification engine is not just a filter — it is the reward channel for
 *   continual learning. And every learned judgment stays a receipt (charter D5).
 */

export type Maturity = "seed-exists" | "stub" | "todo";

export interface SuttonPrinciple {
  id: string;
  suttonIdea: string;
  glasshouseApplication: string;
  inCodeToday: string;          // where the wedge already is
  maturity: Maturity;
  scalingBet: string;           // what improves with more data/compute
  charterTension?: string;      // honest friction with our gates
  resolution?: string;          // how we keep both
}

/** The reward signal — the heart of the fit. Verification = ground truth. */
export const REWARD_SIGNAL = {
  claim: "Glasshouse manufactures the ground truth that imitation lacks.",
  positive: "independent corroboration; human-review confirmation; a prediction later borne out",
  negative: "recycled-media hit; source predates event; disputed; human-review rejection; prediction falsified",
  consumes: "learning.py (Bayesian source reputation) — already updates trust from outcomes",
  extendTo: ["entity-resolution confidence", "which sources/areas to fetch next",
             "anomaly/contradiction salience", "geolocation/chronolocation scorers"],
  rule: "reward is earned only AFTER verification, never on submission (prevents fabrication)",
} as const;

export const PRINCIPLES: SuttonPrinciple[] = [
  {
    id: "P1-discover-not-store",
    suttonIdea: "discover like we can, don't merely contain what's been discovered",
    glasshouseApplication:
      "the product's edge is DISCOVERY — surface promise↔vote contradictions, " +
      "funding↔vote correlations, recycled media, county flips, anomalies — not a " +
      "static encyclopedia of known facts (that's 'better Wikipedia', which we reject)",
    inCodeToday: "verify.py contradiction/recycled checks; record.assess_promise; elections.flips()",
    maturity: "seed-exists",
    scalingBet: "a search+learning layer over the entity/space-time graph that finds the unfound",
  },
  {
    id: "P2-bitter-lesson",
    suttonIdea: "scale general methods (search+learning); hand-coded knowledge caps scaling",
    glasshouseApplication:
      "treat hand-tuned source weights and hand-written rules as SCAFFOLDING to be " +
      "replaced by learned components as data accrues; bet on methods that improve " +
      "with more events, more cycles, more compute",
    inCodeToday: "learning.py learns source trust instead of trusting KIND_WEIGHT forever",
    maturity: "seed-exists",
    scalingBet: "every hand-coded constant gets a learned successor with a fallback",
    charterTension: "learned > hand-coded can become a black box",
    resolution: "see DIVERGENCE — glass-box bitter lesson (charter D5)",
  },
  {
    id: "P3-continual-experience",
    suttonIdea: "learn continually from on-the-job experience streams, not frozen training",
    glasshouseApplication:
      "the ingestion/verification loop is the experience stream; each processed event " +
      "updates the system online — reputation, salience, what-to-fetch — never a frozen model",
    inCodeToday: "store.ingest -> verify -> (learning.py) update; runs per event",
    maturity: "seed-exists",
    scalingBet: "online updates compound; the system gets sharper the longer it runs",
  },
  {
    id: "P4-ground-truth-not-imitation",
    suttonIdea: "imitation lacks ground truth; reward-grounded experience is stronger",
    glasshouseApplication:
      "use VERIFICATION outcomes (corroboration, human review, later-confirmed predictions) " +
      "as the reward signal — see REWARD_SIGNAL; do not learn by imitating one outlet's framing",
    inCodeToday: "verify.py audit verdicts; human-review queue is the planned anchor (DECISIONS O2)",
    maturity: "stub",
    scalingBet: "more verified outcomes => a richer, self-correcting reward channel",
  },
  {
    id: "P5-search-plus-learning",
    suttonIdea: "search and learning are the two primitives that scale",
    glasshouseApplication:
      "SEARCH over the graph/space-time index (paths: funder→official→vote→foreign principal; " +
      "place→events→trend) + LEARNING over outcomes; agents plan what to fetch next",
    inCodeToday: "graph/queries (record.funding_context, elections.county_history) = search seed",
    maturity: "stub",
    scalingBet: "agentic swarm = experiential search; reward shapes the search policy",
  },
  {
    id: "P6-algorithms-over-knowledge",
    suttonIdea: "build algorithms for acquiring & organizing knowledge, not the knowledge",
    glasshouseApplication:
      "invest in the spine (verification, entity resolution, space-time index, the reward loop), " +
      "not in hand-curating facts; facts arrive via adapters and are organized by the algorithms",
    inCodeToday: "the spine (models/verify/store/record/elections adapters) vs. tiny hand seeds",
    maturity: "seed-exists",
    scalingBet: "the spine is the moat; facts are commodities that flow through it",
  },
];

/** Hand-coded constants/rules to graduate into learned components over time. */
export const SCAFFOLDING_TO_REPLACE = [
  { handCoded: "models.KIND_WEIGHT (source-kind trust)", learnedBy: "learning.py per-domain reputation", status: "in progress" },
  { handCoded: "verify.py fixed score deltas/thresholds", learnedBy: "calibrated weights from verified outcomes", status: "todo" },
  { handCoded: "confidence cutoffs (_confidence_from)", learnedBy: "calibration against ground-truth base rates", status: "todo" },
  { handCoded: "elections lean buckets (5/15%)", learnedBy: "data-driven thresholds per office/era", status: "todo" },
  { handCoded: "what to fetch (static adapters/seeds)", learnedBy: "a search policy rewarded by yield of verified, novel signal", status: "todo" },
] as const;

/** How thinking-like-this changes priorities (not today's build — direction). */
export const BUILD_ORDER_SHIFT = {
  from: "ship more hand-curated layers/feeds (storage-shaped)",
  to: "deepen the reward loop + search so the system DISCOVERS and improves with scale",
  firstMoves: [
    "close the loop: human-review verdicts -> learning.py (DECISIONS O2/D9-proposed)",
    "define REWARD_SIGNAL formally and log it as experience per event",
    "a search/agent policy that picks next fetches by expected verified-novelty",
    "a discovery surface: rank contradictions/anomalies/flips by salience, with receipts",
  ],
} as const;

/** The one deliberate divergence from pure Sutton. */
export const DIVERGENCE = {
  name: "glass-box bitter lesson",
  sutton: "accepts black-box scale if it wins",
  glasshouse: "scale search+learning, BUT every learned judgment must decompose to a receipt",
  why: "charter D3 (show the receipt) + D5 (learning stays interpretable); a learned score is " +
       "only trustworthy to the public if it is still auditable",
  consequence: "prefer interpretable learners (Bayesian reputation, calibrated weights, " +
       "attention with citations) over opaque ones; keep the audit trail mandatory",
} as const;

export const SOURCES = [
  "Rich Sutton — 'AI creativity & discovery' (YouTube K5LAFEjTlBA)",
  "Sutton, 'The Bitter Lesson' (2019)",
  "Silver & Sutton, 'Era of Experience' (2024)",
  "The Alberta Plan for AI Research",
] as const;
