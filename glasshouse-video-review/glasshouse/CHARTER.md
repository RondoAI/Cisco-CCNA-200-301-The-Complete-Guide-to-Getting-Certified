# Glasshouse Charter

This file is law, not aspiration. It is committed to the repo and enforced in CI.
A pull request that violates it does not merge — regardless of who wrote it, how
much revenue it promises, or how good the intentions are. The whole value of the
company is trust; this charter is what protects that trust from our own future
desperation.

> Intentions don't survive a funding crunch. Structure does.

## The five gates

**1. Public power only.**
We collect and analyze the *public conduct of public officials and institutions*:
votes, bills, public statements, official acts, campaign finance. We do not build
profiles of private citizens. Ever. There is no "every person" database here.

**2. Sunlight, not surveillance.**
We track events and the public record — what happened, what was said on the
record, how someone voted. We never infer private psychology, personality, or
intent, and never model anyone to predict or change their behavior.

**3. No persuasion engine.**
No microtargeting, no psychographic segmentation, no "how to move this voter,"
no election-influence tooling. If a feature's value depends on changing how
someone votes rather than informing them, it does not ship. We inform; we do not
manipulate.

**4. Show the receipt.**
Every claim links to a primary source. We never ask the user to trust us instead
of "the media" — we show the actual vote, filing, or transcript and let them
judge. No event, figure, or accusation ships without its provenance and audit
trail. Correlation is labeled as correlation, never dressed as causation.

**5. Protect sources; protect the public.**
Citizen-media identity is stripped at intake and never stored recoverably
(the privacy tests must stay green). Nonpartisan by standard: we apply the same
scrutiny across all parties and governments. A public methodology and a
corrections policy are part of the product, not optional.

## Enforcement

- **Code:** no schema, field, model, or pipeline may identify or profile a
  private individual, or model anyone's psychology. CI scans for forbidden
  concepts (person-profiling tables, psychographic fields, persuasion targets).
- **Governance:** incorporate as a Public Benefit Corporation. An independent
  oversight board holds veto power over uses that breach this charter.
- **Amendment:** this charter can be strengthened freely. Weakening any gate
  requires board approval on the public record — because the moment we quietly
  loosen it, we have become the thing we were built to hold accountable.
