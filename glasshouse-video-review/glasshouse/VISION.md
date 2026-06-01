# Glasshouse — Vision

**A monopoly of trust, for the people.** In an age where AI and data are being
consolidated into tools that serve states and corporations, Glasshouse is the
opposite bet: the world's most rigorous, most *legible* hub of public-interest
intelligence — owned by no government, beholden to no party, and built so an
ordinary person can understand the world and the power that shapes their life.

> Palantir built the definitive intelligence platform **for institutions**.
> Glasshouse intends to be bigger — the definitive intelligence platform **for
> the public**. Same ambition for legibility and rigor; opposite master.

## What we are building toward

A single place where anyone can come and get **real information and real data** —
verified, sourced, and beautifully visualized — to research the world and make
real-world decisions. The way Polymarket has a market for everything, Glasshouse
aims to have **trustworthy data and context for everything**:

- **Public power.** What our governments and officials *promise*, what they
  *personally vote on* — in Congress and at the local level — and what they
  actually *deliver*. Promise → vote → outcome, with both receipts. (Built first;
  see `record.py` and `ARCHITECTURE.md` §2.)
- **The world, on the ground.** What's actually happening in the Middle East and
  everywhere else — a verified, "events, not people" feed of conflict, unrest,
  and movement, each claim corroborated and provenance shown. (`packages/watch`.)
- **States and their militaries.** What countries are doing, what weapons are
  being used and by whom, drawn entirely from **public, published, and broadcast
  data** (SIPRI, documented equipment use, AIS/ADS-B telemetry, satellite
  imagery, conflict feeds). We **document and explain** conflict; we never direct
  it. (See the hard line below.)
- **Context for all of it.** Economy, trade, governance indices, weather, markets
  — the layers that turn an event into understanding (`DOMAINS.md`).

The technical bar is **state-of-the-art, PhD-level**. We build on the best open
technology that already exists (Wikidata, GDELT, ACLED, Congress.gov, FEC,
open AIS/ADS-B, open weather/seismic feeds) and build our **own** software — the
verification engine, the entity graph, the visualization — on top. We intend to
be the best in the world at verification and legibility. One day the API itself
is a product. The build is hard on purpose; the moat is depth and trust, not
volume.

## Better than Wikipedia, Palantir and Polymarket — at the thing each misses

- **Wikipedia** has breadth and trust but no live signal, no verification engine,
  no money-and-power graph, and flat presentation. We keep its sourcing ethic and
  add *real-time*, *verified*, *richly visualized*, *connected* intelligence.
- **Palantir** has the legibility and the live picture but serves institutions and
  can target. We take the legibility, serve the public, and never target.
- **Polymarket** proves people crave a live signal on *everything* — but it bets
  on outcomes; it doesn't *track the record*. No one is tracking, with great
  software and UI, a politician's **campaign-trail promises vs. what they actually
  did** — at the presidential, governor (e.g. California), or **mayor** level. We
  are. (Built first: `record.py`.)

## The depth that is the moat

- **Follow the money.** Who funds an official — AIPAC or another lobby — and how
  those dollars trace back through FARA filings toward a foreign principal
  (Israel, Saudi Arabia, Qatar, an oil interest, anyone), and how that correlates
  with their votes. All public record (FEC, OpenSecrets, FARA, OpenSanctions),
  shown as **labelled correlation with receipts, nonpartisan by standard** —
  never a causal accusation. (Built: `FundingFlow`, `/api/record/.../funding`.)
- **Regional & cultural context.** Not just "they're Shia" but what that *means*
  in context — the cultural, sectarian, historical and economic frame most
  outlets flatten. Knowledge of regions others don't have, sourced and explained.
- **The ground truth.** Targeted, *licensed* on-the-ground footage and real-time
  video of events as they happen — run through verification and **source
  protection** (the filmer's identity is stripped at intake; in Iran or Sudan
  this is life-or-death, not a setting).
- **Everything connected.** Money ↔ votes ↔ conflict ↔ trade ↔ oil ↔ statements,
  on one map and one timeline — so a person gets a *universal* view instead of
  being stuck in a box because the information is scattered and shattered.

## How we build it (state-of-the-art, on open foundations)

We plug into every credible open database and build our **own software layer** on
top — our own maps, our own visualization, our own verification, our own entity
graph. We use the best open technology (open satellite imagery, computer-vision
libraries, open geospatial stacks) rather than reinventing primitives, and spend
our genius on the layer no one else has: **verified, connected, legible truth.**
Agentic ingestion (multiple agents swarming open sources) and a possible
contribution-incentive mechanism are on the table — both strictly behind the
verification gate and the source-protection rule. The build path, data-source
catalog, and infrastructure/storage setup are in
**[docs/FOUNDATION.md](docs/FOUNDATION.md)**.

## What makes it different (and durable)

The data sources are commodities — a competitor can copy them in a weekend. The
two things they cannot cheaply copy are why this wins:

1. **Verification + provenance.** Every claim ships with its sources and an
   inspectable audit trail. We never say "trust us instead of the media" — we
   show the actual vote, filing, footage, or transcript and let people judge.
2. **Nonpartisan rigor as structure, not slogan.** The ethics are enforced in
   code and governance (`CHARTER.md`), not promised on a values page.

This is also what lets it be **big, powerful, and valuable** without curdling
into the thing it was built to watch. Trust is the asset. Structure protects it.

## The line that makes us "for the people" (non-negotiable)

Glasshouse builds **situational awareness and accountability**. It does **not**
build operational capability:

- ✅ *Document and explain* — "this weapon system is being used in this theater;
  here is the satellite image, the SIPRI figure, the recorded vote, the receipt."
- ❌ *Direct or target* — no real-time targeting of any person/unit/asset, no
  course-of-action/force-employment planning, no profiling of private
  individuals, nothing that gives meaningful uplift to harming a target.

That boundary is the difference between empowering the public and arming a power.
It is the whole point, and it is enforced — see **[CHARTER.md](CHARTER.md)**,
**[DECISIONS.md](DECISIONS.md)** (D1, D2), and the hard line in
**[DOMAINS.md](DOMAINS.md)**.

---

*Intentions don't survive a funding crunch. Structure does. This vision is
governed by the Charter; where they ever appear to conflict, the Charter wins.*
