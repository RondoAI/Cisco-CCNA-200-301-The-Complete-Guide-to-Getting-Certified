/**
 * index.ts — the spec library manifest (code-form, not prose).
 * ============================================================================
 * We are NOT shipping product here. We accumulate precise, typed CODE notes so
 * an implementing model has exact structure and does not improvise. Every note
 * lives in code; this manifest indexes them and states the working rule.
 */

export type NoteKind = "teardown" | "layout" | "components" | "principles";
export type NoteStatus = "analyzed" | "spec'd" | "condensing";

export interface SpecNote {
  id: string;
  kind: NoteKind;
  file: string;
  source: string;
  summary: string;
  status: NoteStatus;
  charterNote?: string;     // where the charter line bites
}

export const WORKING_RULE = {
  mode: "code-mode notes only — no prose notes, no premature builds",
  why: "precise typed specs give the implementing model exact structure; it builds what the code says, not what it assumes",
  flow: "reference (video/brief) -> code-form note here -> condense into components.ts -> LATER, deliberate implementation",
  charter: "adopt legibility; reject targeting/kill-chain/person-tracking — rejections are written into the code, not assumed",
  prototypes: "where a working prototype exists (e.g. glasshouse/elections.py) it is PROOF the layout is real, not the finished product",
} as const;

export const LIBRARY: SpecNote[] = [
  {
    id: "PRINCIPLES-001",
    kind: "principles",
    file: "./principles_sutton.spec.ts",
    source: "Rich Sutton — 'AI creativity & discovery' / Bitter Lesson / Era of Experience",
    summary: "the Sutton frame as binding principles: discover-don't-store, bitter lesson, " +
      "continual experience, verification-as-ground-truth reward, search+learning, " +
      "scaffolding-to-replace, and the 'glass-box bitter lesson' divergence",
    status: "spec'd",
    charterNote: "scale learning BUT keep every judgment auditable (D3/D5)",
  },
  {
    id: "UI-TEARDOWN-001",
    kind: "teardown",
    file: "./console_prisma.spec.ts",
    source: "video: 'PRISMA / Operation Steel Horizon' dramatized C2 console",
    summary: "layout grid, every panel (data contract + cadence + source), map layers, real build stack, data volumes",
    status: "analyzed",
    charterNote: "strike/mission-planning functions REJECTED in-code; map shell + chrome ADAPTED",
  },
  {
    id: "LAYOUT-001",
    kind: "layout",
    file: "./political_geography.spec.ts",
    source: "brief: zoomable U.S. political/election map",
    summary: "zoom hierarchy, confirmed data sources, CountyResult schema + store contract, map layers, API routes, real 2020/2024 findings",
    status: "spec'd",
    charterNote: "public aggregate returns only — votes by place, never about a voter",
  },
  {
    id: "COMPONENTS",
    kind: "components",
    file: "./components.ts",
    source: "condensation of all teardowns",
    summary: "reusable console component contracts (clock, pills, map surface, dossier, track table, receipts log, analytics) + explicit REJECTED list",
    status: "condensing",
  },
];

/** Next notes to add (code-form), as more references arrive — not today's build. */
export const BACKLOG = [
  "UI-TEARDOWN-002 — next video",
  "LAYOUT-002 — money/funding map (donor -> official -> vote -> foreign principal)",
  "LAYOUT-003 — global officials & public-statement timeline (Wikidata/IPU Parline)",
] as const;
