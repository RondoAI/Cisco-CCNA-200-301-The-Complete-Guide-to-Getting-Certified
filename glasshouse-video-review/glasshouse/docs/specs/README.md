# Specs — the interface reference library

A growing, **condensing** knowledge base for the software we want to build —
distilled from reference videos, not copied from them. The method matches the
brief: *look, analyze, write down in full detail what it does and how it works,
research how it's really built and the realistic data needed — then keep
enriching over time.* We do **not** build the whole thing from one clip.

## How it works

1. **Each video → one teardown.** `UI-TEARDOWN-NNN-<name>.md`: scene inventory,
   every panel, the map mechanics in depth, how such systems are really built,
   and realistic data volumes. Each element tagged **adopt / adapt / reject**.
2. **Durable patterns condense into `components.ts`** — a "note of code" (types +
   annotations, no implementation): each component's data contract, refresh
   cadence, source, and charter status. This is the part that gets *denser* as
   more videos come in.
3. **Later, deliberate implementation.** When a pattern is well-specified and
   decided, it graduates into the real frontend (`web/`) — never on the spot.

## The charter line (non-negotiable)

Reference footage often shows **operational/targeting** software. We study the
*legibility* — density, coordination, real-time chrome, map craft — and we
**reject** the targeting/kill-chain/person-tracking functions explicitly, on the
record, in every teardown. We build the level of detail; we never build the
trigger. (`../../CHARTER.md`, `../../DECISIONS.md` D2, `../../DOMAINS.md`.)

## Index

| ID | Source | What it is | Status |
|----|--------|-----------|--------|
| [UI-TEARDOWN-001](UI-TEARDOWN-001-prisma.md) | "PRISMA / Operation Steel Horizon" (broadcast b-roll) | Dense dark C2 console: dual coordinated maps, track tables, signal charts, streaming log, analytics. Strike-planning functions **rejected**; map shell + chrome **adapted**. | analyzed |

> Source frames are **not committed** (third-party broadcast footage). Teardowns
> describe them; send more videos and they become the next entries.

## Reading order

Start with `UI-TEARDOWN-001` §4 (the map, in depth) and §5 (how it's built),
then `components.ts` for the condensed contracts, then `../FOUNDATION.md` for the
data sources and infrastructure those components run on.
