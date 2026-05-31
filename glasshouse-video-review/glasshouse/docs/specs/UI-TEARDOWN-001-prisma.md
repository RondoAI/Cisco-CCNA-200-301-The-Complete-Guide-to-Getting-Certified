# UI-TEARDOWN-001 — "PRISMA / Operation Steel Horizon" command console

**Source:** a ~35s broadcast b-roll clip (CNN bug) showing a dramatized
intelligence/operations console branded **PRISMA**, scenario **"OPERATION STEEL
HORIZON"**, dated `2030-05-15`. Shown in two color treatments (amber/green desk
monitor; cyan video-wall) plus cutaways of an analyst and hands on a keyboard.
This is **dramatized/concept footage**, not a real shipping product.

> **Scope & ethics (read first).** This teardown studies the *software craft* —
> information density, the map mechanics, the real-time chrome, the panel grid.
> A large part of PRISMA's **function is strike/mission planning** (mission
> planner, "kamikaze package," firing solution, rules-of-engagement, fleet/strike
> status). **That targeting function is out of scope for Glasshouse and is
> rejected on the record here** — we do not build targeting, course-of-action, or
> any kill-chain capability (`CHARTER.md`, `DECISIONS.md` D2). We keep the
> legibility; we drop the trigger. Every element below is tagged
> **ADOPT / ADAPT / REJECT** with the charter reason.

This is a *living* spec. As more videos arrive, each becomes a `UI-TEARDOWN-NNN`
and the durable patterns condense into `docs/specs/components.ts` and a future
master "reference console" spec. See `docs/specs/README.md`.

---

## 1. Scene inventory (what is actually on screen)

| t (approx) | Shot | Content |
|---|---|---|
| 0–9s | PRISMA on a desk monitor (amber/green) | The full console, hero shot — readable. |
| 9–14s | Analyst in low light + screens | B-roll; green line-charts on a tablet. |
| 14–17s | Cyan dashboard, angled | Same PRISMA layout, cyan theme. |
| 17–27s | Hands typing, keyboard | B-roll, shallow depth of field. |
| 27–35s | Cyan **video-wall**, analyst gesturing | Same PRISMA console at wall scale. |

Net: **one interface**, two themes. Everything below describes that one console.

---

## 2. Global chrome (frame, always-on)

- **Top header bar**, three zones:
  - *Left:* product mark **`PRISMA`** + a small tagline/version subline.
  - *Center:* mission banner **`OPERATION STEEL HORIZON`**, subline
    **`PHASE III // 40 RAVEN // 0=12 // ROE GREEN`** (operation name, phase, an
    AO/callsign, a count, rules-of-engagement state). → **REJECT** the
    operational framing; **ADAPT** to a neutral *situation banner* (e.g.
    `SITUATION: Red Sea shipping disruption · CORROBORATED · AO: Bab-el-Mandeb`).
  - *Right:* a large **live clock `23:07:29`**, a date/sync line
    `2030-05-15 LOCAL / STRATUM-3 SYNC`, and a row of **status pills**
    (`STRIKE ✓`, `FLEET 5/1`, `COMMS`, `AUTH 15:42`, …) — small KPI chips with
    green/amber/red states. → **ADOPT** clock + sync + "as-of" discipline;
    **ADAPT** the pills to *data-health* (sources live, feeds synced, verification
    queue depth, coverage %), not strike/fleet/auth.
- **Secondary toolbar** under the header: per-panel actions —
  `LOAD CSV · REPLAY · ANALYSIS · CLEAR` (left panel) and
  `LOAD · RESET · CLEAR · PLOT ✓ · MAX` (right panel). → **ADOPT** (load data,
  replay a time window, expand/maximize, clear) — generic, charter-neutral.
- **Footer status strip:** `UPLOAD COMPLETE`, sync glyphs, `T0-XX`, small icons.
  → **ADAPT** to ingestion/sync status + dataset "as-of".

Design language: near-black background, monospaced type, hairline grid borders,
phosphor accent per theme (amber-green or cyan), heavy use of tiny status chips
and section rules. This is the classic dense **single-pane-of-glass** SOC/C2 look.

---

## 3. Panel grid (the body)

Roughly a 3-band grid: a wide top band of two coordinated map/plot panels flanked
by rail tables/charts, then a bottom band split into a log and an analytics strip.

### 3.1 Left map — "STRIKE HISTORY · AO RAVEN"  → **ADAPT (shell), REJECT (label)**
A dense **scatter/heat plot on a coordinate grid** with axis ticks and a
**crosshair reticle**: historical point-events colored by category, clustered
into a bright mass. Reads as "every past event in this area, over time."
- *Mechanics:* a 2-D plane (projected lon/lat or an abstract X/Y), thousands of
  points, color = class, density = heat, reticle = current focus; a time control
  ("REPLAY") animates history.
- *Glasshouse analog:* **Event-history view** — verified events in a region over
  time (conflict/unrest/maritime), color by confidence, replay over a window.
  Drop "strike."

### 3.2 Right map — "MISSION PLANNER · STRIKE PKG · KAMIKAZE"  → **REJECT (function); ADAPT (map shell only)**
A dark **geographic vector map**: coastlines/borders, **labeled place markers**
(readable city labels in a Black-Sea/SW-Russia theatre — Kharkiv, Luhansk,
Mariupol, Rostov, Volgograd, Volgodonsk, Krasnodar, Astrakhan…), **node/waypoint
markers joined by route lines**, a **radial "solution" overlay** (concentric
arcs/contours like range-rings or a probability field), a crosshair reticle, and
a floating **`MISSION SOLUTION`** sub-panel of computed fields
(`LON/LAT`, `WAYPOINT`, `LIVE FEED`, `UPLOAD TO C-CODES`, numeric solution).
- **This is the targeting core — REJECT entirely:** no mission planning, no
  package/asset assignment, no firing solution, no "upload to" command path.
- **What we *do* keep — only the map shell:** a dark geographic map with named
  places, the ability to draw routes/movements, and an **analytic overlay**
  capability. Re-pointed, the concentric "solution" becomes e.g. an **isochrone**
  ("how far has this disruption spread in 6h") or a **confidence/coverage
  contour** — descriptive, never a strike solution. The floating panel becomes an
  **event dossier** (the "receipt"), not a fire-control readout.

### 3.3 Left rail — "ACTIVE TRACKS" table  → **ADAPT**
A tall **virtualized table** of coded rows with colored status cells (a classic
track list from air-defense/maritime systems). → Glasshouse: **active
signals/events** list — each row an *event or a published movement*, never a
person or a target. Sortable, status-colored, selects → focuses the map.

### 3.4 Right rail — status table + "SIGNAL CHART" + "FLEET STATUS / UNITS"  → **ADOPT / ADAPT**
- A small **red/green status table** (coded rows). → feed/source status.
- **`SIGNAL CHART`**: a **line waveform + bar histogram** of a signal over time.
  → **ADOPT**: source/event *volume* over time (e.g. reports/hour), with a
  histogram of categories.
- **`FLEET STATUS · UNITS-X`**: a list of units and states. → **ADAPT**: *feed/
  adapter* status (which ingestors are live) — or, for maritime OSINT, *published*
  vessel movements (open AIS). **Never our own assets or strike units.**

### 3.5 Bottom-left — **console / event log**  → **ADOPT**
A scrolling, timestamped **append-only log** (`[23:07:xx] …` lines). → This maps
*exactly* to Glasshouse's existing **verification audit trail / receipts** — every
check and state change, streamed live. Keep as-is in spirit.

### 3.6 Bottom-right — "STRIKE ANALYTICS"  → **ADAPT (rename + re-point)**
A big KPI number (**`157`**), two **circular % gauges** (`94%`, `92%`), and a
**horizontal multi-segment timeline bar**. → Glasshouse: **verification
analytics** — events tracked, corroboration rate, source-agreement % — i.e. the
"instrument cluster" from DESIGN-REVIEW, at dashboard scale. The segmented bar →
a phase/coverage timeline of *reporting*, not an operation.

---

## 4. The map, in depth (what it represents & how it works)

Two coordinated map surfaces — a **history/analytic plane** (3.1) and a
**geographic situation map** (3.2) — sharing a selection and a time cursor. The
mechanics worth reproducing (charter-neutral):

1. **Base layer** — a dark, label-light geographic basemap (borders, coastlines,
   graticule), styled to recede so data pops.
2. **Place layer** — named markers (cities/ports/regions) at low opacity, with
   collision-aware labels (labels hide/show by zoom and density).
3. **Entity/track layer** — many points/markers (events, published movements),
   GPU-instanced so thousands render at 60fps; color = class, ring/pulse =
   freshness or severity, size = magnitude.
4. **Connection layer** — arcs/lines for *movements/relationships* (a vessel's
   track, a funding flow, a trade route). In PRISMA these are routes; for us they
   are *observed* movements or *graph* edges — never planned strikes.
5. **Analytic overlay** — the concentric "solution" field. Honest analogs:
   isochrones (spread over time), heat/KDE (density), or confidence contours.
   Server-computed, rendered as a contour/heatmap layer.
6. **Reticle + focus** — a crosshair/selection that ties map ↔ tables ↔ dossier ↔
   timeline (click anywhere, everything else focuses).
7. **Time** — a global time cursor + "replay" that animates history across all
   layers from one clock (the header's live clock is the "now" anchor).

The defining quality is **coordination + density**: one clock, one selection,
many synchronized dense views — and it stays legible. That is the bar to hit.

---

## 5. How a console like this is actually built (research)

Real systems with this look (Palantir Gotham, air-defense/maritime C2, big SOC
walls, finance ops floors) are built from roughly this stack:

**Rendering (the map & charts)**
- **GPU map rendering:** `MapLibre GL JS` (open) for the vector basemap +
  **`deck.gl`** (Uber, WebGL2/WebGPU) for high-density data layers
  (`ScatterplotLayer`, `ArcLayer`, `HeatmapLayer`, `ContourLayer`, `TripsLayer`
  for animated movement). For a bespoke "wall" look, custom WebGL/`regl`/Three.js.
- **Vector tiles (MVT):** basemap + own data tiled from **PostGIS** via
  `Martin` / `pg_tileserv` / `Tegola`, or pre-baked with `planetiler` from
  OpenStreetMap. Tiles → CDN/object storage.
- **High-frequency charts:** `uPlot`/`regl` (not SVG) for thousands of points;
  **virtualized tables** (`react-window`/TanStack Virtual) for big track lists.
- **Binary transport:** Apache **Arrow** / Protobuf over the wire, not JSON, at
  scale; level-of-detail + clustering (`supercluster`) for zoomed-out density.

**Real-time spine**
- A **message bus** (`Kafka` / `NATS` / Redis Streams) carrying events/positions.
- A **stream processor** (`Flink` / Kafka Streams / `Materialize`) maintaining
  live aggregates and the "as-of" view.
- **Push to UI** via WebSocket/SSE; the client keeps a windowed live store.
- **Time discipline:** NTP (the dramatized `STRATUM-3 SYNC` nods to NTP strata) —
  everything stamped to one clock so replay and corroboration are exact.

**Data model & fusion**
- **Spatiotemporal store:** PostGIS + **TimescaleDB** (or **ClickHouse**) for
  track/position time-series; an entity/graph layer for relationships.
- **"Tracks":** each entity is a series of timestamped states (the air-defense/
  AIS/ADS-B pattern). Entity resolution + dedup at ingest.
- **Object storage (S3/R2):** imagery, media, snapshots (TBs→PBs over time).

**Services & app**
- Ingestion adapters (one per source) → fusion/scoring → **API gateway**
  (GraphQL/REST) → React front end with a design-token system for the dense dark
  theme; auth/RBAC (the `AUTH` pill).
- **For Glasshouse specifically:** every one of these flows through the existing
  **verification engine** before it reaches a user — that gate is the difference
  between this and a propaganda wall.

---

## 6. Realistic data to function "at that level or better"

To make a console this dense *credible* (not a movie prop), the gap is **scale +
streaming + GPU viz** on top of the model + verification we already have:

| Layer | Realistic volume (order of magnitude) | Store/approach |
|---|---|---|
| Officials (THE RECORD) | US federal ~535; +US state ~7.4k; global politicians on Wikidata ~1M+ | Postgres + graph |
| Bills / votes | ~10–15k bills per Congress; millions of historical votes | Postgres |
| Campaign finance (FEC) | hundreds of millions of contribution records | columnar (ClickHouse) |
| Conflict/events (GDELT/ACLED) | GDELT ~hundreds of thousands/day; ACLED millions historical | Timescale/ClickHouse |
| Air/sea telemetry (ADS-B/AIS) | tens of thousands of craft; millions of positions/day | Timescale + tiles |
| Imagery/media | TBs→PBs accumulating | object storage (R2/S3) |

Implications: a streaming ingestion+fusion pipeline; a spatiotemporal columnar
store; vector tiles + deck.gl for the map; Arrow transport + virtualization for
the dense panels; and **the verification engine gating publish**. Build
incrementally — the seed already has the data model, provenance, and verification;
this teardown defines the *target* the visualization and scale work aims at.

---

## 7. Adopt / adapt / reject — summary

**ADOPT (build toward):** live clock + sync + "as-of"; data-health status pills;
coordinated dual views with one selection + time cursor; dense GPU map layers;
signal-over-time charts; virtualized track/event tables; the streaming
append-only **log = receipts**; analytics gauges (re-pointed to verification).

**ADAPT (re-point to accountability/awareness):** "strike history" → event
history; mission map *shell* → situational map of events/movements; "solution"
overlay → isochrone/heat/confidence contour; "active tracks" → active
events/published movements; "fleet/units" → feed/source status or *published*
vessel movements; "strike analytics" → verification analytics; mission banner →
situation banner.

**REJECT (never build):** mission/course-of-action planning; package/asset/strike
assignment; firing "solution" and "upload to C-codes"; rules-of-engagement /
fleet command; anything that identifies, tracks, or supports harming a person,
unit, or asset (`CHARTER.md`, `DECISIONS.md` D2; `DOMAINS.md` hard line).

---

*The craftsmanship is the lesson: one clock, one selection, many dense
synchronized views, and it stays legible. We aim there — pointed at truth and
accountability, never at a target.*
