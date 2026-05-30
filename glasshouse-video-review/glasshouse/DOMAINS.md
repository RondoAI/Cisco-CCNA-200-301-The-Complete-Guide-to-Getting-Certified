# Glasshouse — Platform Domains

This generalizes the earlier "two pillars" framing. Glasshouse is a **global
intelligence hub**: a common spine plus pluggable domain layers. Politics and
conflict are the main focus, but the design lets you add any domain — news,
weather, trade, air/sea movements — without re-architecting.

> The moat is the **spine**, not the number of feeds. Aggregator dashboards
> already relay 60+ public feeds cheaply. If we only relay feeds, we have no
> moat. We win on verification, the entity graph, and accountability depth.

---

## The spine (build once, build deep)

Everything below plugs into this shared core:

1. **Entity graph** — countries, regions, governments, leaders, agencies, orgs,
   parties, alliances. Canonical IDs from **Wikidata QIDs** so every layer speaks
   the same vocabulary and data fuses instead of fragmenting.
2. **Verification + provenance engine** — the existing `glasshouse/` engine.
   *Every layer's data passes through it.* Confidence score + audit trail or it
   does not publish.
3. **Unified space-time index** — every datum is stamped `where` + `when`, so any
   combination of layers overlays on one map and one timeline.
4. **Source-reliability tiering** — sources ranked by track record (wire/NGO/
   official/citizen/aggregator), surfaced to the user, factored into scoring.
5. **Visualization shell** — map + timeline + entity dashboards that any layer
   renders into. This is where "beautifully visualized" is won.

---

## The layers (domains)

Each layer is just an adapter that resolves entities to the graph, stamps
space-time, runs verification, and renders into the shell. Add or remove freely.

### Tier-1 — build these deep first (the differentiators)

**Conflict & events** — the war/instability core.
`GDELT 2.0` · `ACLED` · `UCDP`. Already prototyped in `packages/watch`.

**Governance & accountability** — *The Record* (officials, votes, bills,
statements, funding, promise-vs-action) + instability indices: `V-Dem`,
`World Bank Worldwide Governance Indicators`, `Fragile States Index`.
This is the depth no aggregator has. (See `ARCHITECTURE.md` §2.)

**News** — wire + RSS + curated channels, **reliability-tiered and verified**,
not "trust us instead of the media." Show the source, show corroboration.

### Tier-2 — layer in for breadth once the spine is solid

**Weather & natural hazards** — `NOAA / NWS`, `Open-Meteo`, `ECMWF`;
`NASA FIRMS` (active fires), `USGS` (earthquakes), `NASA EONET` (storms/volcanoes).

**Air traffic** — `OpenSky Network` (free, open ADS-B; commercial use needs a
license, blocks cloud scrapers — cache + respect rate limits), `adsb.lol`
(military aircraft). Useful signal: callsign/squawk anomalies, unusual movements.

**Maritime** — `aisstream.io` (open AIS), `Global Fishing Watch`; pair with
published fleet reports (e.g., USNI) for editorial context. Track tankers,
naval movements near chokepoints (Hormuz, Bab-el-Mandeb).

**Space** — `CelesTrak` TLE orbital data for satellite tracking.

**Economy & trade** — `World Bank Open Data` / WDI, `IMF`, `UN Comtrade`
(trade flows), `EIA` / `IEA` (energy). Ties votes and conflicts to economics.

**Military & defense** — `SIPRI` (military expenditure + arms transfers, the open
authority). **Published/telemetry data only.** See the hard line below.

**Infrastructure & cyber** — internet outages (`Cloudflare Radar`, `IODA`),
undersea cables, GPS jamming/spoofing anomalies derived from ADS-B.

---

## Hard line for the military/defense & movement layers

These layers aggregate data that is **already publicly broadcast** (aircraft and
ship transponders) or **already published** (SIPRI figures, fleet reports). That
is legitimate OSINT — unifying public telemetry, the same thing World Monitor and
Shadowbroker do openly.

It is **not**, and must never become:
- operational or real-time **targeting** of any person, unit, or asset;
- intercepting private communications, or anything requiring a hack/breach;
- tracking **private individuals** (the charter's gate #1 still governs every
  layer — a private person's boat or plane is not content here).

We map *what is happening* (a naval deployment near Hormuz, a fire, a GPS-jamming
zone). We do not produce a kill chain. If a layer's output would give meaningful
uplift to harming a target, it does not ship. (`CHARTER.md` governs all layers.)

---

## Build order (extends ARCHITECTURE.md §6)

Spine first → Tier-1 layers deep (conflict, governance, news) → then Tier-2
layers one at a time, each behind the same verification contract. Resist the urge
to light up all 25 layers shallowly; depth + trust is the whole product.
