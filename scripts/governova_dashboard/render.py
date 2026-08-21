"""Render a self-contained governance dashboard as a single HTML document.

No server, no external assets, no JavaScript: everything (styles included) is inline,
so the file opens standalone in any browser or embeds in a static site.
"""

from __future__ import annotations

import html
from typing import Any

from governova_report.model import AMBER, GREEN, RED, BoardReport

_AREA_COLOUR = {GREEN: "#16a34a", AMBER: "#d97706", RED: "#dc2626"}


def _score_colour(score: int) -> str:
    if score >= 85:
        return "#16a34a"
    if score >= 70:
        return "#65a30d"
    if score >= 60:
        return "#d97706"
    return "#dc2626"


def _esc(text: object) -> str:
    return html.escape(str(text))


def _area_counts(report: BoardReport) -> str:
    """Green/amber/red area counts, as coloured dots with spoken labels.

    These were three emoji. `S4.17` prohibits that, and the rule bound to it in
    the same change caught this line — the emoji is the only carrier of the
    distinction, so the counts render differently on every platform and reach a
    screen reader as three bare numbers. The dot is the component this
    stylesheet already had; the label is what the emoji was standing in for.
    """
    parts = [
        (GREEN, "Green", report.areas_green),
        (AMBER, "Amber", report.areas_amber),
        (RED, "Red", report.areas_red),
    ]
    return " · ".join(
        f'<span class="dot" style="background:{_AREA_COLOUR[status]}" aria-hidden="true"></span>'
        f'<span class="sr">{name}: </span>{_esc(count)}'
        for status, name, count in parts
    )


def to_html(report: BoardReport, coverage: dict[str, Any]) -> str:
    s = report.score
    # ADR-012 — below quorum the badge states the assessment is partial rather
    # than reporting a repository as below a threshold it was never measured
    # against.
    if s.headline is None:
        cert = f"Partial assessment — {s.assessed_weight}% of the model"
        cert_bg = "#6b7280"
    else:
        cert = "Governova Certified eligible" if s.certified_eligible else "Below certification (85)"
        cert_bg = "#16a34a" if s.certified_eligible else "#6b7280"
    area_cards = "\n".join(
        f'''      <div class="area" style="border-left:5px solid {_AREA_COLOUR[a.status]}">
        <div class="area-top"><span class="dot" style="background:{_AREA_COLOUR[a.status]}"></span>
          <strong>{_esc(a.constitution_id)}</strong> {_esc(a.name)}</div>
        <div class="muted">{_esc(a.standards)} standards · {_esc(a.summary)}</div>
      </div>'''
        for a in report.areas
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Governova — Governance Dashboard</title>
<style>
  :root {{ color-scheme: light dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
         background:#0b1020; color:#e5e7eb; }}
  .wrap {{ max-width: 1040px; margin: 0 auto; padding: 32px 20px 64px; }}
  header {{ display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; }}
  h1 {{ font-size: 22px; margin:0; letter-spacing:.3px; }}
  .sub {{ color:#9ca3af; font-size: 13px; margin-top:4px; }}
  .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-top:24px; }}
  .card {{ background:#121a30; border:1px solid #1f2a44; border-radius:14px; padding:20px; }}
  .score {{ font-size:54px; font-weight:800; line-height:1; }}
  .grade {{ font-size:18px; font-weight:700; color:#9ca3af; }}
  .badge {{ display:inline-block; padding:5px 12px; border-radius:999px; color:#fff; font-size:12px; font-weight:700; }}
  .label {{ color:#9ca3af; font-size:12px; text-transform:uppercase; letter-spacing:.6px; }}
  .big {{ font-size:30px; font-weight:800; margin-top:6px; }}
  .bar {{ height:10px; background:#1f2a44; border-radius:999px; overflow:hidden; margin-top:10px; }}
  .bar > span {{ display:block; height:100%; background:#3b82f6; }}
  h2 {{ font-size:14px; text-transform:uppercase; letter-spacing:.6px; color:#9ca3af; margin:32px 0 12px; }}
  .areas {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(300px,1fr)); gap:12px; }}
  .area {{ background:#121a30; border:1px solid #1f2a44; border-radius:12px; padding:14px 16px; }}
  .area-top {{ display:flex; align-items:center; gap:8px; }}
  .dot {{ width:10px; height:10px; border-radius:999px; display:inline-block; }}
  /* Visible to a screen reader, not to the eye. The area counts read as three
     bare numbers without it, because the colour carrying their meaning is not
     something a screen reader can announce. */
  .sr {{ position:absolute; width:1px; height:1px; overflow:hidden;
        clip:rect(0 0 0 0); white-space:nowrap; }}
  .muted {{ color:#9ca3af; font-size:13px; margin-top:6px; }}
  footer {{ color:#6b7280; font-size:12px; margin-top:40px; }}
  a {{ color:#60a5fa; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>Governova — Governance Dashboard</h1>
      <div class="sub">Generated {_esc(report.generated_on)} · model: master.md §18</div>
    </div>
    <span class="badge" style="background:{cert_bg}">{_esc(cert)}</span>
  </header>

  <div class="grid">
    <div class="card">
      <div class="label">Governova Score</div>
      <div class="score" style="color:{_score_colour(s.score) if s.headline is not None else "#9ca3af"}">{s.score if s.headline is not None else "—"}<span style="font-size:22px">{"/100" if s.headline is not None else ""}</span></div>
      <div class="grade">Grade {_esc(s.grade)}</div>
    </div>
    <div class="card">
      <div class="label">Constitutional areas</div>
      <div class="big">{_area_counts(report)}</div>
      <div class="muted">{len(report.areas)} areas assessed</div>
    </div>
    <div class="card">
      <div class="label">Enforcement coverage</div>
      <div class="big">{_esc(coverage.get("coverage_pct"))}%</div>
      <div class="muted">{_esc(coverage.get("enforceable_anti_patterns"))} of {_esc(coverage.get("total_anti_patterns"))} anti-patterns ·
        {_esc(coverage.get("blocking_rules"))} blocking / {_esc(coverage.get("advisory_rules"))} advisory rules</div>
      <div class="bar"><span style="width:{min(100.0, float(coverage.get("coverage_pct", 0)))}%"></span></div>
    </div>
    <div class="card">
      <div class="label">Governance events</div>
      <div class="big">{report.events.amendments + report.events.adrs + report.events.runbooks}</div>
      <div class="muted">{report.events.amendments} amendments · {report.events.adrs} ADRs · {report.events.runbooks} runbooks</div>
    </div>
  </div>

  <h2>Red / Amber / Green by constitutional area</h2>
  <div class="areas">
{area_cards}
  </div>

  <footer>
    Generated automatically by Governova. Score trend and AI-action volume await runtime
    instrumentation. Nobody else generates this automatically.
  </footer>
</div>
</body>
</html>
"""
