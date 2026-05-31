/**
 * console_prisma.spec.ts — CODE-FORM NOTE (not a build, not prose).
 * ============================================================================
 * A precise, typed teardown of the reference console seen in the "PRISMA /
 * Operation Steel Horizon" video. Encoded as code so an implementing model has
 * exact structure and does not improvise. Nothing here renders or executes —
 * it is the specification we construct from later.
 *
 * CHARTER: we adopt legibility, never the targeting function. Every element is
 * tagged charter: "adopt" | "adapt" | "reject". Rejected elements are listed
 * explicitly (REJECTED) so the boundary is in the code, not assumed.
 */

export type CharterStatus = "adopt" | "adapt" | "reject";
export type Cadence = "static" | "on-select" | "poll:30s" | "stream";

export interface Region { id: string; gridArea: string; desc: string; }
export interface DataField { name: string; type: string; note?: string; }
export interface Panel {
  id: string;
  region: string;                 // Region.id
  title: string;                  // as seen on screen
  purpose: string;                // what the analyst reads from it
  charter: CharterStatus;
  cadence: Cadence;
  derivedFrom: string;            // the PRISMA element
  dataContract: DataField[];      // the shape it needs (re-pointed to our domain)
  glasshouse: string;             // our charter-safe analog
}
export interface MapLayer {
  id: string; kind: string; renders: string; charter: CharterStatus; impl: string;
}
export interface BuildLayer { concern: string; tech: string; note?: string; }
export interface DataVolume { layer: string; magnitude: string; store: string; }

export const CONSOLE_META = {
  id: "UI-TEARDOWN-001",
  source: "broadcast b-roll, dramatized console 'PRISMA / OPERATION STEEL HORIZON' (2030)",
  themes: ["amber-green desk monitor", "cyan video-wall"],
  framesCommitted: false,         // third-party footage; described, not stored
  lookAndFeel: {
    bg: "near-black", type: "monospace", borders: "hairline grid",
    accentByTheme: { mono: "#e8a13a / phosphor-green", wall: "#22d3ee cyan" },
    pattern: "dense single-pane-of-glass SOC/C2",
  },
} as const;

/** 3-band grid: top map band + rails, then log + analytics. */
export const LAYOUT_GRID: Region[] = [
  { id: "header",   gridArea: "top, full-width",        desc: "product mark + situation banner + clock/sync + status pills" },
  { id: "toolbar",  gridArea: "under header, full",      desc: "per-panel actions (load/replay/analysis/clear/max)" },
  { id: "railL",    gridArea: "left column",             desc: "active tracks/events table" },
  { id: "mapHist",  gridArea: "center-left, large",      desc: "history scatter/heat plane" },
  { id: "mapGeo",   gridArea: "center-right, large",     desc: "geographic situation map + floating dossier" },
  { id: "railR",    gridArea: "right column",            desc: "status table + signal chart + feed status" },
  { id: "log",      gridArea: "bottom-left",             desc: "streaming append-only log" },
  { id: "analytics",gridArea: "bottom-right",            desc: "KPI + gauges + segmented timeline" },
  { id: "footer",   gridArea: "very bottom, full",       desc: "ingest/sync status, as-of" },
];

export const PANELS: Panel[] = [
  {
    id: "situationBanner", region: "header", title: "OPERATION STEEL HORIZON / PHASE III / ROE GREEN",
    purpose: "name + state of the active situation", charter: "adapt", cadence: "on-select",
    derivedFrom: "mission banner + ROE",
    glasshouse: "neutral situation banner: title + region + confidence",
    dataContract: [
      { name: "title", type: "string", note: "e.g. 'Red Sea shipping disruption'" },
      { name: "area", type: "string" },
      { name: "confidence", type: "'confirmed'|'corroborated'|'emerging'|'unverified'|'disputed'" },
    ],
  },
  {
    id: "clockBar", region: "header", title: "23:07:29 / 2030-05-15 LOCAL / STRATUM-3 SYNC",
    purpose: "single 'now' anchor + data freshness + sync health", charter: "adopt", cadence: "stream",
    derivedFrom: "live clock + sync line",
    glasshouse: "clock + as-of + sync ok (NTP/stream health)",
    dataContract: [
      { name: "utc", type: "ISO8601", note: "the replay anchor" },
      { name: "asOf", type: "ISO8601", note: "dataset freshness" },
      { name: "syncOk", type: "boolean" },
    ],
  },
  {
    id: "statusPills", region: "header", title: "STRIKE ✓ / FLEET 5-1 / AUTH 15:42",
    purpose: "at-a-glance system state", charter: "adapt", cadence: "poll:30s",
    derivedFrom: "strike/fleet/auth chips",
    glasshouse: "DATA-HEALTH chips: sources-live, verify-queue, coverage%",
    dataContract: [
      { name: "label", type: "string" }, { name: "value", type: "string" },
      { name: "state", type: "'ok'|'warn'|'alert'" },
    ],
  },
  {
    id: "trackTable", region: "railL", title: "ACTIVE TRACKS",
    purpose: "scannable list of live items; selects -> focus map", charter: "adapt", cadence: "stream",
    derivedFrom: "active tracks list (air-defense pattern)",
    glasshouse: "ACTIVE EVENTS / published movements — never a person or target",
    dataContract: [
      { name: "id", type: "string" }, { name: "kind", type: "'event'|'published_movement'" },
      { name: "label", type: "string" }, { name: "status", type: "string", note: "color-coded" },
      { name: "ts", type: "ISO8601" }, { name: "virtualized", type: "true", note: "1000s of rows @60fps" },
    ],
  },
  {
    id: "mapHistory", region: "mapHist", title: "STRIKE HISTORY · AO RAVEN",
    purpose: "all past point-events over an area + time", charter: "adapt", cadence: "on-select",
    derivedFrom: "history scatter/heat plane w/ reticle",
    glasshouse: "EVENT-HISTORY scatter/heat of verified events; replay over a window",
    dataContract: [
      { name: "points", type: "{lon,lat,class,ts,weight}[]" },
      { name: "colorBy", type: "'confidence'|'class'" }, { name: "replayWindow", type: "Duration" },
    ],
  },
  {
    id: "mapGeo", region: "mapGeo", title: "MISSION PLANNER · STRIKE PKG · KAMIKAZE",
    purpose: "geographic plane: places, routes, analytic overlay", charter: "adapt",
    cadence: "stream", derivedFrom: "geo map shell (KEEP) + mission planning (REJECT)",
    glasshouse: "SITUATION MAP shell: places + observed movements + analytic overlay; NO planning",
    dataContract: [
      { name: "basemap", type: "vector(dark)" }, { name: "places", type: "{name,lon,lat}[]" },
      { name: "entities", type: "{id,lon,lat,class,freshness}[]", note: "events/movements, not targets" },
      { name: "connections", type: "{from,to,kind}[]", note: "OBSERVED movement / graph edge" },
      { name: "overlay", type: "'isochrone'|'heat'|'confidence-contour'", note: "NOT a firing solution" },
    ],
  },
  {
    id: "dossier", region: "mapGeo", title: "MISSION SOLUTION (floating)",
    purpose: "detail on the selected map object", charter: "adapt", cadence: "on-select",
    derivedFrom: "firing-solution readout (function REJECTED; panel re-pointed)",
    glasshouse: "EVENT DOSSIER = the receipt: fields + sources + audit trail",
    dataContract: [
      { name: "fields", type: "Record<string,string>" }, { name: "sources", type: "Url[]" },
      { name: "auditTrail", type: "string[]" },
    ],
  },
  {
    id: "signalChart", region: "railR", title: "SIGNAL CHART",
    purpose: "a signal over time + histogram", charter: "adopt", cadence: "stream",
    derivedFrom: "waveform + bar chart",
    glasshouse: "reports/hour or events/hour line + category histogram",
    dataContract: [
      { name: "series", type: "{t:ISO8601, v:number}[]" }, { name: "histogram", type: "{bucket,count}[]" },
      { name: "renderer", type: "'uPlot'|'regl'", note: "canvas/GPU, not SVG, at scale" },
    ],
  },
  {
    id: "feedStatus", region: "railR", title: "FLEET STATUS · UNITS-X",
    purpose: "status of many units", charter: "adapt", cadence: "poll:30s",
    derivedFrom: "fleet/units list",
    glasshouse: "FEED/ADAPTER health — or PUBLISHED vessel movements (open AIS). Never our assets.",
    dataContract: [
      { name: "rows", type: "{id,label,state:'ok'|'warn'|'down'}[]" },
    ],
  },
  {
    id: "receiptsLog", region: "log", title: "console log [23:07:xx] …",
    purpose: "live narrative of what happened", charter: "adopt", cadence: "stream",
    derivedFrom: "scrolling timestamped console",
    glasshouse: "VERIFICATION AUDIT TRAIL / receipts — append-only, streamed",
    dataContract: [
      { name: "lines", type: "{ts:ISO8601, level, msg, sources?:Url[]}[]" },
      { name: "appendOnly", type: "true" },
    ],
  },
  {
    id: "analytics", region: "analytics", title: "STRIKE ANALYTICS · 157 · 94% · 92%",
    purpose: "headline KPI + gauges + segmented timeline", charter: "adapt", cadence: "poll:30s",
    derivedFrom: "big number + circular gauges + segmented bar",
    glasshouse: "VERIFICATION ANALYTICS: events tracked, corroboration %, source-agreement %",
    dataContract: [
      { name: "headlineCount", type: "number" }, { name: "gauges", type: "{label,pct}[]" },
      { name: "timeline", type: "{label,from,to,color}[]", note: "reporting phases, not an operation" },
    ],
  },
];

/** The map, as composable layers (deck.gl-style). Shared selection + time cursor. */
export const MAP_LAYERS: MapLayer[] = [
  { id: "basemap",     kind: "vector basemap",  renders: "borders/coastline/graticule, label-light", charter: "adopt", impl: "MapLibre GL + OSM/TIGER MVT tiles" },
  { id: "places",      kind: "labeled markers", renders: "cities/ports, collision-aware labels",      charter: "adopt", impl: "deck.gl TextLayer + collision filter" },
  { id: "entities",    kind: "point/instanced", renders: "events/published movements; color=class",   charter: "adapt", impl: "deck.gl ScatterplotLayer (GPU instanced)" },
  { id: "connections", kind: "arcs/trips",       renders: "OBSERVED movement / graph edges",           charter: "adapt", impl: "deck.gl ArcLayer/TripsLayer" },
  { id: "overlay",     kind: "field",            renders: "isochrone / heat / confidence contour",     charter: "adapt", impl: "deck.gl Contour/HeatmapLayer (server-computed)" },
  { id: "reticle",     kind: "selection",        renders: "crosshair tying map<->table<->dossier",     charter: "adopt", impl: "custom overlay; shared selection state" },
];

/** How a console like this is really built (research, in code form). */
export const BUILD_STACK: BuildLayer[] = [
  { concern: "map render",     tech: "MapLibre GL JS + deck.gl (WebGL2/WebGPU)" },
  { concern: "vector tiles",   tech: "PostGIS -> Martin/pg_tileserv/Tegola, or planetiler(OSM) -> CDN" },
  { concern: "hi-freq charts", tech: "uPlot / regl", note: "canvas/GPU not SVG" },
  { concern: "big tables",     tech: "react-window / TanStack Virtual" },
  { concern: "wire format",    tech: "Apache Arrow / Protobuf", note: "not JSON at scale" },
  { concern: "stream bus",     tech: "Kafka / NATS / Redis Streams" },
  { concern: "stream compute", tech: "Flink / Kafka Streams / Materialize", note: "live aggregates, as-of view" },
  { concern: "push to UI",     tech: "WebSocket / SSE" },
  { concern: "time sync",      tech: "NTP (dramatized 'STRATUM-3'); one clock for replay/corroboration" },
  { concern: "spatiotemporal", tech: "PostGIS + TimescaleDB, or ClickHouse" },
  { concern: "entities/tracks",tech: "entity = timestamped state series; resolution+dedup at ingest" },
  { concern: "object store",   tech: "S3 / Cloudflare R2 (imagery/media/snapshots)" },
  { concern: "gate",           tech: "glasshouse verification engine before publish", note: "the difference from a propaganda wall" },
];

export const DATA_VOLUMES: DataVolume[] = [
  { layer: "officials",        magnitude: "US ~535 fed; +~7.4k state; ~1M+ global (Wikidata)", store: "Postgres + graph" },
  { layer: "bills/votes",      magnitude: "~10-15k bills/Congress; millions of votes",          store: "Postgres" },
  { layer: "campaign finance", magnitude: "hundreds of millions of records",                    store: "ClickHouse" },
  { layer: "events",           magnitude: "GDELT ~100k+/day; ACLED millions",                   store: "Timescale/ClickHouse" },
  { layer: "air/sea telemetry",magnitude: "10k+ craft; millions of positions/day",              store: "Timescale + tiles" },
  { layer: "imagery/media",    magnitude: "TB -> PB over time",                                  store: "object storage" },
];

/** Never build. In the code so the line cannot quietly erode. */
export const REJECTED = [
  "MissionPlanner — course-of-action / strike-package planning",
  "FiringSolution — 'MISSION SOLUTION' / upload-to-C-codes / targeting",
  "AssetAssignment — fleet/unit/strike assignment & command",
  "ROEControl — rules-of-engagement state",
  "PersonTrack — any per-person identification or tracking",
] as const;
