# Foundation — data sources, the agent swarm, and the infra setup

How Glasshouse is built: **plug into every credible open database, build our own
software layer on top.** We don't reinvent primitives (geo, tiles, CV models); we
spend our effort on the layer no one else has — verified, connected, legible
truth. Everything here is governed by `CHARTER.md`; where a source or technique
would profile a private individual or feed a kill chain, it does not ship.

---

## 1. Open databases to plug into (the inputs)

All are public/open or have open tiers. Each adapter resolves entities to the
**Wikidata** spine, stamps space-time, and runs the verification engine before
anything publishes.

**Public power & money (THE RECORD)**
- `api.congress.gov`, GovInfo, GovTrack — federal bills, votes, members, record.
- **FEC**, **OpenSecrets** — campaign finance (the money layer; built).
- **FARA** (`efile.fara.gov`), **OpenSanctions** — foreign-principal ties; how a
  lobby's money traces back to a foreign government. Public filings only.
- **Wikidata** — the cross-language entity spine (officials, offices, terms,
  parties). **IPU Parline**, **World Bank DPI** — global parliaments.
- State/local: **Open States** (legislatures), **LegiScan**, municipal open-data
  portals — for the governor and **mayor**-level tracking.

**World events & the ground (THE WATCH)**
- **GDELT 2.0**, **ACLED**, **UCDP** — conflict/event feeds (wired).
- Wire/RSS + curated channels — reliability-tiered, verified.
- *Targeted, licensed* citizen footage — never a firehose scrape; identity
  stripped at intake (`privacy.py`).

**Imagery & geospatial OSINT**
- **Sentinel-2 / Sentinel Hub**, **NASA** (Landsat, FIRMS active fires, EONET),
  **USGS** (earthquakes) — open satellite/Earth-observation.
- **OpenStreetMap** — base geography for our own maps.
- **OpenSky Network** / **adsb.lol** (ADS-B), **aisstream.io** / **Global Fishing
  Watch** (AIS) — *already-broadcast* air/sea telemetry.

**Context**
- **World Bank / IMF / UN Comtrade / EIA** — economy, trade, oil flows.
- **V-Dem**, **WGI**, **Fragile States Index** — governance/instability indices.

> The catalog grows, but the rule is fixed (`DOMAINS.md`): prefer the most
> **official, primary** source; store the source URL; verify before publish.

---

## 2. Our own software layer (what we build, not borrow)

- **Verification + provenance engine** — the moat (`verify.py`, `learning.py`).
- **Entity graph** — Wikidata-anchored, our schema (`record.py` + the events model).
- **Unified space-time index** — every datum `where`+`when` for one map/timeline.
- **Our maps & visualization** — see §6. We design the look; we own the detail.

We reuse: geospatial primitives (PostGIS, MapLibre, deck.gl), CV/ML model weights
(open), tile rendering. We build: everything that makes the truth *trustworthy and
legible*.

---

## 3. Agentic ingestion swarm

Multiple agents, each a thin **adapter + extractor**, fanning out across the
sources above:

```
[discovery agents] → [extraction agents] → [entity-resolution agents]
        → THE VERIFICATION GATE (verify.py) → store → map/timeline/graph
```

- Agents *find, fetch, extract, and resolve* — they never assert. Nothing reaches
  a user without passing verification + provenance.
- **No autonomous action on the world** (CHARTER gate #3). Agents inform; they do
  not act, persuade, or target.
- Output is cite-backed RAG over the record (ARCHITECTURE.md §4) — every sentence
  traces to a primary doc.

---

## 4. Incentivized contribution (Bittensor-style) — OPEN DECISION, with guardrails

The idea: reward contributors/agents for *valued, verified* data (a Bittensor-like
subnet, or agents operating one). It is promising **but it collides with the one
rule we never bend — source protection.** Logged as decision **O7**; do not build
until resolved. Hard constraints if we ever do:

1. **Identity-pay vs. source-protection.** Paying a contributor usually needs a
   wallet/identity. A filmer in Iran/Sudan linked to a payable identity can be
   killed. Any incentive layer must **separate reward from identity** (e.g. pay
   verification *nodes/agents* that process open data, not on-the-ground filmers;
   or one-way, unlinkable reward tokens). The privacy tests stay green, always.
2. **Perverse incentives.** Paying for data incentivizes fabrication. The
   verification engine + Bayesian reputation (`learning.py`) is the defense; a
   contribution earns only *after* it survives corroboration, never on submission.
3. **Sybil/poisoning resistance** and a public methodology for how rewards are
   scored. Incentives must reward *truth that verifies*, not volume.

---

## 5. Imagery, satellite & computer vision (OSINT, not surveillance)

- **Allowed:** analyzing *open/published* satellite & aerial imagery with CV to
  describe what is publicly visible — a flooded district, a port's congestion, a
  burn scar, a visible military buildup. Geolocation/chronolocation of footage to
  verify it. This is the verification deepening already stubbed in `verify.py`.
- **Not allowed:** operating our own drones/sensors to collect on people, or any
  imagery analysis that tracks a *private individual* or gives targeting uplift
  (CHARTER gate #1, `DOMAINS.md` hard line). We analyze the world's open imagery;
  we don't run an ISR collection program.
- Open building blocks: Sentinel/Landsat, OpenCV, segmentation/detection model
  weights from open libraries — applied to events and places, never to persons.

---

## 6. Visualization & "our own maps" (rich, dense, PhD-level)

- **Base maps:** **MapLibre GL** + our own vector tiles from **OpenStreetMap**
  (self-hosted via `tilemaker`/`planetiler`) — so the map is *ours*, styled and
  controlled, not a rented basemap. (The seed uses Leaflet + Carto tiles as a
  placeholder; this is the upgrade path.)
- **Data overlays:** **deck.gl** for high-density layers (arcs for funding/trade
  flows, heat for events, time-animated movement) on top of MapLibre.
- **Graph:** force-directed money-and-power graph (donor → official → vote →
  foreign principal) — D3 / sigma.js / Cytoscape.
- **Time:** a shared multi-track timeline (promise → vote → outcome; report →
  corroboration → resolution).
- **Design language:** dark "operations" console + light "editorial" surface, one
  component vocabulary (see DECISIONS O3 and `web/`).

---

## 7. Storage & infrastructure setup (the "secure cloud" answer)

**Start simple; the schema is already cloud-portable.** Recommended foundation:

| Concern | Recommendation |
|---|---|
| Relational + geo | **PostgreSQL + PostGIS** (events/officials/votes/flows; spatial queries) |
| Vector / RAG | **pgvector** in the same Postgres (grounded search over the record) |
| Graph relationships | **Apache AGE** on Postgres to start (one DB), **Neo4j** if the graph outgrows it |
| Object storage | **S3-compatible** (AWS S3, or **Cloudflare R2** — no egress fees) for imagery/footage/snapshots |
| Tiles | self-hosted vector tiles (planetiler → R2/S3 → MapLibre) |
| Ingestion | Python workers (one adapter per source) + a queue (Redis/RabbitMQ) for the agent swarm |
| API | **FastAPI** (already) behind a CDN |
| Secrets/keys | a managed secrets manager; never in the repo |

**On "secure cloud" + source protection (the part that actually matters):**
- The sensitive asset is **citizen-media intake**. Keep it in a **separate,
  hardened ingestion service** that strips identity *before* anything is stored
  (already the design in `privacy.py`), so the main database never holds
  recoverable identity to subpoena or breach.
- **Data residency / jurisdiction** is a real decision (logged **O6**): where the
  intake service runs determines its exposure to subpoenas. Favor a jurisdiction
  and a provider that support the source-protection promise; encrypt at rest and
  in transit; minimize what is retained.
- Default recommendation to start: a single managed Postgres (e.g. on a provider
  with PostGIS support) + R2/S3 object storage + the FastAPI service, with the
  citizen-intake stripper isolated. Scale to a hardened/segregated deployment as
  real (non-notional) data comes online. **Don't provision the secure tier until
  there's real source data to protect** — but design for it now (we have).

---

## 8. Regional & cultural-context layer

Depth others lack: not "they are Shia" but the cultural, sectarian, historical and
economic frame. Built as a sourced **context layer** on the entity graph —
explainers attached to regions/groups, each cite-backed to scholarship and primary
material, surfaced beside the live events from that region. Plain-language, sourced,
nonpartisan; correlation labelled as correlation. (A Tier-1 governance/news sibling
in `DOMAINS.md`.)

---

*Foundation rule: open inputs, our own trusted layer. Everything passes the
verification gate; nothing crosses the charter line. Intentions don't survive a
funding crunch — structure does.*
