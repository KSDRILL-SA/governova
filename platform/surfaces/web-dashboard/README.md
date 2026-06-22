# Governova — Web Dashboard

**Status:** Alpha — working (v0.1)
**Surface:** self-contained HTML governance dashboard

A single standalone HTML page that visualises a repository's governance posture —
**no server, no external assets, no JavaScript**. It composes the artifacts the engine
already produces:

- **Governova Score** + grade + Governova Certified status (§18.1 / §18.2)
- **Enforcement Coverage** — rules, blocking/advisory split, % of anti-patterns enforceable
- **Red / Amber / Green** per constitutional area (§18.3)
- **Governance events** — amendments, ADRs, runbooks

## Generate it

```bash
governova dashboard --out dashboard.html   # open it in any browser
```

The monthly governance workflow publishes `dashboard.html` as an artifact alongside the
Board-Level Report and the System Bible. Because it is a single self-contained file, it
drops straight into GitHub Pages, an S3 bucket, or an email attachment.

## Implementation

`governova_dashboard` (`scripts/governova_dashboard/`): pure rendering over the compiled
index, the Governova Score, and the Board Report — inline CSS, deterministic output.
