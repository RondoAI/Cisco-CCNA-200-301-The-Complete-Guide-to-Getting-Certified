/**
 * components.ts — SPEC, NOT A BUILD ("a note of code").
 * ----------------------------------------------------------------------------
 * A condensed, machine-shaped record of the console components worth building
 * toward, distilled from the UI teardowns in this folder (currently
 * UI-TEARDOWN-001 — "PRISMA"). It is intentionally types + annotations only:
 * each component's data contract, refresh cadence, source, and CHARTER status.
 * No rendering, no logic. We enrich this as more videos arrive, then implement
 * deliberately later — never "build the whole thing on the spot."
 *
 * CHARTER LINE: we capture the *legibility* of command consoles, never the
 * targeting function. Components are tagged:
 *   "adopt"  — build as-is (charter-neutral craft)
 *   "adapt"  — keep the shell, re-point from force-employment to accountability
 *   "reject" — never build (targeting / kill-chain / person-tracking)
 * Rejected components are listed so the boundary is explicit, not assumed.
 */

export type CharterStatus = "adopt" | "adapt" | "reject";

/** How often a panel's data refreshes. */
export type Cadence = "static" | "on-select" | "poll:30s" | "stream";

/** Provenance is mandatory for anything that makes a claim (CHARTER gate #4). */
export interface Sourced {
  /** primary-source URLs / feed ids; empty only for pure-chrome components */
  sources: string[];
  /** the verification verdict that gates publish (reuse glasshouse engine) */
  confidence?: "confirmed" | "corroborated" | "emerging" | "unverified" | "disputed";
}

/** Base spec every console component shares. */
export interface ComponentSpec {
  id: string;
  /** what the analyst reads from it, in one line */
  purpose: string;
  charter: CharterStatus;
  cadence: Cadence;
  /** the PRISMA element this derives from, for traceability */
  derivedFrom: string;
  /** if adapt/reject: the re-pointing or the reason it's out of bounds */
  note?: string;
}

/* ── Global chrome ───────────────────────────────────────────────────────── */

/** Live clock + data "as-of" + sync state. Anchors replay across all panels. */
export interface ClockBar extends ComponentSpec {
  charter: "adopt";
  utc: string;            // ISO; the single "now" anchor
  asOf: string;           // dataset freshness timestamp
  syncOk: boolean;        // NTP/stream health (PRISMA: "STRATUM-3 SYNC")
}

/** Small KPI chips. PRISMA showed STRIKE/FLEET/AUTH — we show DATA HEALTH. */
export interface StatusPill extends ComponentSpec {
  charter: "adapt";       // re-pointed from strike/fleet to data-health
  label: string;          // e.g. "SOURCES LIVE", "VERIFY QUEUE", "COVERAGE"
  value: string;          // e.g. "42/45", "7", "93%"
  state: "ok" | "warn" | "alert";
}

/** Neutral situation banner (replaces PRISMA's "OPERATION … / ROE" banner). */
export interface SituationBanner extends ComponentSpec {
  charter: "adapt";
  title: string;          // e.g. "Red Sea shipping disruption"
  area: string;           // AO/region label
  confidence: NonNullable<Sourced["confidence"]>;
}

/* ── Map surfaces (the core) ─────────────────────────────────────────────── */

export type MapLayerKind =
  | "basemap"      // dark vector basemap (MapLibre + OSM tiles)
  | "places"       // collision-aware named markers
  | "entities"     // GPU-instanced events / published movements (deck.gl Scatter)
  | "connections"  // observed movements / graph edges (deck.gl Arc/Trips)
  | "overlay";     // isochrone / heat / confidence contour (deck.gl Contour/Heatmap)

/** A coordinated map surface. Two of these (history + situation) share a
 *  selection + time cursor. The geographic shell is "adapt"; any targeting/
 *  mission-planning behavior on it is "reject" (see MissionPlanner_REJECTED). */
export interface MapSurface extends ComponentSpec {
  charter: "adapt";
  layers: MapLayerKind[];
  sharesSelectionWith: string[];   // table/dossier/timeline ids
  timeCursor: boolean;             // global replay anchor
  /** entities are events/movements — NEVER persons or targets (gate #1/#2) */
  entityKind: "event" | "published_movement";
}

/** Floating detail panel on map select = the RECEIPT, not a fire-control readout. */
export interface Dossier extends ComponentSpec, Sourced {
  charter: "adapt";       // PRISMA's "MISSION SOLUTION" -> our event dossier
  fields: Record<string, string>;
  auditTrail: string[];   // the verification receipts
}

/* ── Rails, log, analytics ───────────────────────────────────────────────── */

/** Tall virtualized list of events/published movements (PRISMA "ACTIVE TRACKS"). */
export interface TrackTable extends ComponentSpec {
  charter: "adapt";
  rowKind: "event" | "published_movement";  // never a person/target
  virtualized: true;       // thousands of rows at 60fps (react-window/TanStack)
}

/** Line + histogram of signal/event volume over time (PRISMA "SIGNAL CHART"). */
export interface SignalChart extends ComponentSpec {
  charter: "adopt";
  metric: "reports_per_hour" | "events_per_hour" | "source_activity";
  renderer: "uPlot" | "regl"; // canvas/GPU, not SVG, at scale
}

/** Feed/adapter health, or PUBLISHED vessel movements — never our assets. */
export interface FeedStatus extends ComponentSpec {
  charter: "adapt";
  note: "PRISMA 'FLEET STATUS/UNITS' -> source/feed health or open AIS movements";
}

/** Streaming append-only log = verification audit trail (PRISMA console log). */
export interface ReceiptsLog extends ComponentSpec, Sourced {
  charter: "adopt";
  cadence: "stream";
  appendOnly: true;
}

/** KPI + circular gauges + segmented bar (PRISMA "STRIKE ANALYTICS"). */
export interface VerificationAnalytics extends ComponentSpec {
  charter: "adapt";       // re-pointed: events tracked, corroboration %, agreement %
  headlineCount: number;
  gauges: { label: string; pct: number }[];
}

/* ── Explicitly REJECTED (never build) ───────────────────────────────────── */
/**
 * Catalogued so the boundary is on the record. None of these get an
 * implementation, ever. (CHARTER.md; DECISIONS.md D2; DOMAINS.md hard line.)
 *
 *  MissionPlanner_REJECTED   — course-of-action / strike-package planning
 *  FiringSolution_REJECTED   — "MISSION SOLUTION" / upload-to-C-codes / targeting
 *  AssetAssignment_REJECTED  — fleet/unit/strike assignment & command
 *  ROEControl_REJECTED       — rules-of-engagement state
 *  PersonTrack_REJECTED      — any per-person identification or tracking
 *
 * If a future video tempts one of these in, the answer is no — we build the
 * legibility around it, never the trigger.
 */
export type RejectedComponent =
  | "MissionPlanner_REJECTED"
  | "FiringSolution_REJECTED"
  | "AssetAssignment_REJECTED"
  | "ROEControl_REJECTED"
  | "PersonTrack_REJECTED";
