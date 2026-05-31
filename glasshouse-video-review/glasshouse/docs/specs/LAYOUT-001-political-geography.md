# LAYOUT-001 — Political geography & the election map

**Type:** layout + knowledge note (not a build). Captures the schema layout, map
design, data-source knowledge and API surface for the zoomable U.S. political map,
so the eventual implementation is fast and richly informed. A working *reference
prototype* exists (`glasshouse/elections.py`) — treat it as proof the layout is
sound and the data is real, not as the finished product.

---

## 1. What this layer is

The map people zoom through to understand the political system: **nation → state →
county → (later) precinct / city / town**. At each level: who won, by how much,
how it leans, how it changed across cycles, and — wired to THE RECORD — who
represents it and where their money comes from.

## 2. Zoom hierarchy (the layout)

| Level | Unit | Key | Status |
|---|---|---|---|
| Nation | USA | — | results ✓ |
| State | 50 + territories | state name / USPS | rollup ✓ |
| County | ~3,150 | 5-digit **FIPS** | results ✓ (2020, 2024) |
| Precinct | ~175k | VTD id | future (VEST dataset) |
| City / town | place | Census place FIPS | future |

FIPS is the join key: county results ↔ county GeoJSON ↔ Census demographics ↔
officials by district. Everything keys off it.

## 3. Data sources (knowledge — reachability confirmed)

| Source | Gives | Keyless? | Reachable | Notes |
|---|---|---|---|---|
| `tonmcg/US_County_Level_Election_Results_08-24` | county pres. results 2008–2024 | yes | ✓ | 3,160 rows/cycle; cols below |
| `plotly/datasets` `geojson-counties-fips` | county polygons by FIPS | yes | ✓ | 3,221 features |
| Census TIGER/Line | official county/state/precinct shapes | yes | — | authoritative boundaries |
| MIT MEDSL | precinct + validated returns | yes | — | primary-source upgrade |
| VEST (Redistricting Data Hub) | precinct boundaries + returns | reg. | — | the precinct layer |
| Wikidata / Open States | governors, state legislators | yes | partial | SPARQL endpoint up; query TBD |

**County results CSV columns (knowledge):** `state_name, county_fips,
county_name, votes_gop, votes_dem, total_votes, diff, per_gop, per_dem,
per_point_diff`. (Primary source upstream = state election offices.)

## 4. Schema layout (code-shaped note)

```
CountyResult                      # one county, one cycle; PUBLIC AGGREGATE ONLY
  fips: str (5)                   # join key
  county, state: str
  year: int
  votes_dem, votes_gop, total_votes: int
  sources: [Source]              # provenance mandatory
  # derived:
  winner: "R"|"D"|"T"
  margin_pct: float              # signed: + = R lean, - = D lean
  lean: "tossup_|lean_|solid_" + winner

ElectionStore                     # keyed by (year, fips)
  by_year(year)            -> [CountyResult]
  county_history(fips)     -> [CountyResult across cycles]   # the trend
  map_data(year)           -> [{fips, winner, margin_pct, lean, total_votes}]
  state_rollup(year)       -> {state: {votes, winner, margin_pct, counties}}
  national_totals(year)    -> {votes_dem, votes_gop, winner, margin_pct}
  closest_counties(year,n) -> tightest races
  flips(from,to)           -> counties that changed party  # "where it moved"
```

Future fields to enrich: turnout %, third-party votes, margin *swing* vs. prior
cycle, demographic joins (Census), and an `Election`/`Candidate` generalization
beyond president (Senate/Governor/House/local) keyed on the same FIPS spine.

## 5. Map design (layout note)

- **Basemap:** dark, label-light (MapLibre + OSM/TIGER tiles).
- **Choropleth layer:** county polygons shaded by `margin_pct` on a diverging
  red↔white↔blue ramp; opacity by `total_votes` so big counties read stronger.
- **Flip overlay:** outline/hatch counties returned by `flips()`; toggle by
  direction (D→R / R→D).
- **Labels:** collision-aware place labels by zoom; county name + margin on hover.
- **Selection:** click county → dossier (history across cycles + its officials
  from THE RECORD + their funding) — ties the map to accountability.
- **Time:** cycle selector / slider (2008…2024) animating the choropleth =
  "watch the map move."
- **Coordination:** map ↔ state rollup table ↔ closest-races list ↔ dossier, one
  selection (the coordination pattern from UI-TEARDOWN-001).

## 6. API surface (documented contract)

```
GET /api/elections/years
GET /api/elections/map?year=2024            -> choropleth rows (join on FIPS)
GET /api/elections/national?year=2024       -> totals + closest counties
GET /api/elections/state/{state}?year=2024  -> rollup + county list
GET /api/elections/county/{fips}            -> history across cycles
GET /api/elections/flips?from_year=&to_year= -> party changes
```

## 7. Realistic data scale

Counties ~3,150 × cycles (cheap, in-memory fine). Precincts ~175k × cycles (needs
a real store — PostGIS + tiles). GeoJSON simplification/tiling needed for smooth
zoom. Demographic joins push storage up but stay well within a single Postgres +
object-store for tiles.

## 8. Knowledge captured (real findings, 2020 vs 2024)

- National: 2020 **D +4.45%** (81.3M / 74.2M) → 2024 **R +1.48%** (77.3M / 75.0M).
- **86 counties flipped — all D→R**; none R→D in this pair.
- Tightest 2024 counties: Talbot MD (0.03%), Bucks PA (0.07%), Tippecanoe IN (0.15%).
- Florida 2024: **R +13.1%** across all 67 counties.

These are sanity checks that the layout + sources produce real, correct numbers —
the foundation the eventual map renders.

## 9. What enriches the build next (notes, not tasks-for-today)

- Add the **precinct** layer (VEST/MEDSL) for city-level zoom.
- Generalize `CountyResult` → `Election`/`Result` for Senate/Governor/local.
- Join **demographics** (Census ACS) and **turnout**.
- Wire county → **officials + funding** (THE RECORD) on select.
- Tile the GeoJSON for smooth nation↔county zoom.
