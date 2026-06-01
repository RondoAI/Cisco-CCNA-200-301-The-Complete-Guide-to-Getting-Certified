/**
 * political_geography.spec.ts — CODE-FORM NOTE (LAYOUT-001, not a build).
 * ============================================================================
 * The zoomable U.S. political map, specified as code so the implementing model
 * has exact schema, sources, map layers, API contract and findings — and does
 * not improvise. A working reference prototype exists (`glasshouse/elections.py`)
 * that proves this layout produces real, correct numbers; this file is the spec
 * it (and the eventual frontend) construct from.
 *
 * CHARTER: public AGGREGATE returns only — votes by place, never about a voter.
 */

export type Party = "R" | "D" | "T";
export type CharterStatus = "adopt" | "adapt" | "reject";

/* ── Zoom hierarchy ───────────────────────────────────────────────────────── */
export interface ZoomLevel { level: string; unit: string; key: string; status: string; }
export const ZOOM: ZoomLevel[] = [
  { level: "nation",   unit: "USA",                 key: "—",               status: "rollup ✓" },
  { level: "state",    unit: "50 + territories",    key: "state/USPS",      status: "rollup ✓" },
  { level: "county",   unit: "~3,150",              key: "FIPS5",           status: "results ✓ (2020,2024)" },
  { level: "precinct", unit: "~175,000",            key: "VTD id",          status: "future (VEST/MEDSL)" },
  { level: "place",    unit: "city/town",           key: "Census place FIPS", status: "future" },
];
// FIPS5 is THE join key: results <-> GeoJSON <-> Census demographics <-> officials.

/* ── Data sources (knowledge: reachability confirmed in-sandbox) ──────────── */
export interface DataSource {
  id: string; gives: string; keyless: boolean; reachable: boolean | "partial"; note: string;
}
export const SOURCES: DataSource[] = [
  { id: "tonmcg/US_County_Level_Election_Results_08-24", gives: "county pres. results 2008-2024",
    keyless: true, reachable: true, note: "3,160 rows/cycle; cols below; upstream = state election offices" },
  { id: "plotly/datasets:geojson-counties-fips", gives: "county polygons keyed by FIPS",
    keyless: true, reachable: true, note: "3,221 features; join target for choropleth" },
  { id: "census/TIGER", gives: "official county/state/precinct boundaries", keyless: true,
    reachable: "partial", note: "authoritative shapes; tile these" },
  { id: "MIT/MEDSL", gives: "precinct + validated returns", keyless: true, reachable: "partial",
    note: "primary-source upgrade" },
  { id: "VEST/RDH", gives: "precinct boundaries + returns", keyless: false, reachable: "partial",
    note: "the precinct layer" },
  { id: "wikidata+openstates", gives: "governors, state legislators", keyless: true,
    reachable: "partial", note: "SPARQL endpoint up; query TBD" },
];
export const COUNTY_CSV_COLUMNS = [
  "state_name", "county_fips", "county_name", "votes_gop", "votes_dem",
  "total_votes", "diff", "per_gop", "per_dem", "per_point_diff",
] as const;

/* ── Schema layout (the data contract) ────────────────────────────────────── */
export interface CountyResult {
  fips: string;            // 5-digit, the join key
  county: string; state: string; year: number;
  votes_dem: number; votes_gop: number; total_votes: number;
  sources: string[];       // provenance mandatory
  // derived:
  winner: Party;
  margin_pct: number;      // signed: + = R lean, - = D lean
  lean: string;            // `${"tossup"|"lean"|"solid"}_${Party}` | "tied"
}
/** Store contract (mirrors elections.py — keep in sync). */
export interface ElectionStoreContract {
  add(r: CountyResult): CountyResult;                         // throws if no source
  years(): number[];
  by_year(year: number): CountyResult[];
  county_history(fips: string): CountyResult[];              // across cycles -> trend
  map_data(year: number): MapDatum[];                        // choropleth feed
  state_rollup(year: number): Record<string, StateRollup>;
  national_totals(year: number): NationalTotals;
  closest_counties(year: number, n: number): CountyResult[];
  flips(fromYear: number, toYear: number): Flip[];           // where the map moved
}
export interface MapDatum { fips: string; winner: Party; margin_pct: number; lean: string; total_votes: number; }
export interface StateRollup { votes_dem: number; votes_gop: number; total_votes: number; counties: number; winner: Party; margin_pct: number; }
export interface NationalTotals { year: number; votes_dem: number; votes_gop: number; total_votes: number; winner: Party; counties: number; margin_pct: number; }
export interface Flip { fips: string; county: string; state: string; from: Party; to: Party; from_margin: number; to_margin: number; }

// Fields to enrich later: turnout_pct, votes_other, swing_vs_prev,
// demographics (Census ACS join), and generalize CountyResult ->
// Election{office: 'president'|'senate'|'governor'|'house'|'local'} + Result.

/* ── Map design (layout) ──────────────────────────────────────────────────── */
export interface MapLayerSpec { id: string; renders: string; encoding: string; impl: string; }
export const MAP_LAYERS: MapLayerSpec[] = [
  { id: "basemap",   renders: "dark, label-light base", encoding: "—", impl: "MapLibre + OSM/TIGER tiles" },
  { id: "choropleth",renders: "county polygons", encoding: "fill = margin_pct (diverging R↔white↔D); opacity = total_votes", impl: "join GeoJSON.id == fips" },
  { id: "flips",     renders: "outline/hatch flipped counties", encoding: "toggle by direction D→R / R→D", impl: "from flips()" },
  { id: "labels",    renders: "place labels by zoom", encoding: "name + margin on hover", impl: "collision-aware" },
];
export const MAP_INTERACTIONS = {
  select: "click county -> dossier: history across cycles + its officials + funding (THE RECORD)",
  time: "cycle slider 2008..2024 animates the choropleth ('watch the map move')",
  coordination: "map <-> state-rollup table <-> closest-races list <-> dossier share one selection",
} as const;

/* ── API contract ─────────────────────────────────────────────────────────── */
export interface ApiRoute { method: "GET"; path: string; params: string[]; returns: string; }
export const API: ApiRoute[] = [
  { method: "GET", path: "/api/elections/years",          params: [],                     returns: "{years:number[]}" },
  { method: "GET", path: "/api/elections/map",            params: ["year"],               returns: "{year,count,counties:MapDatum[]}" },
  { method: "GET", path: "/api/elections/national",       params: ["year"],               returns: "{totals:NationalTotals, closest_counties:CountyResult[]}" },
  { method: "GET", path: "/api/elections/state/{state}",  params: ["state", "year"],      returns: "{state,year,rollup:StateRollup,counties:CountyResult[]}" },
  { method: "GET", path: "/api/elections/county/{fips}",  params: ["fips"],               returns: "{fips,county,state,history:CountyResult[]}" },
  { method: "GET", path: "/api/elections/flips",          params: ["from_year","to_year"],returns: "{from,to,flips:Flip[]}" },
];

/* ── Knowledge captured (real findings — sanity that the layout is correct) ── */
export const FINDINGS_2020_2024 = {
  national: {
    2020: { winner: "D", margin_pct: -4.45, votes_dem: 81264994, votes_gop: 74208196, counties: 3152 },
    2024: { winner: "R", margin_pct: 1.48,  votes_dem: 75006739, votes_gop: 77294799, counties: 3160 },
  },
  flips_2020_to_2024: { count: 86, direction: { "D->R": 86, "R->D": 0 } },
  closest_2024: [
    { county: "Talbot County", state: "Maryland",     margin_pct: 0.03 },
    { county: "Bucks County",  state: "Pennsylvania", margin_pct: 0.07 },
    { county: "Tippecanoe County", state: "Indiana",  margin_pct: 0.15 },
  ],
  florida_2024: { winner: "R", margin_pct: 13.1, counties: 67 },
} as const;

/* ── Scale + next enrichments (notes, not today's tasks) ──────────────────── */
export const SCALE = {
  counties: "~3,150 x cycles (in-memory ok)",
  precincts: "~175k x cycles (needs PostGIS + tiles)",
  geojson: "simplify/tile for smooth nation<->county zoom",
} as const;
export const NEXT_ENRICHMENTS = [
  "precinct layer (VEST/MEDSL) for city-level zoom",
  "generalize CountyResult -> Election/Result (senate/governor/house/local)",
  "join Census ACS demographics + turnout",
  "wire county select -> officials + funding from THE RECORD",
  "tile the county GeoJSON",
] as const;
