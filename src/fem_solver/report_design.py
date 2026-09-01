"""Shared self-contained design for exported HTML evidence."""

from __future__ import annotations

from html import escape

REPORT_CSS = """
:root{--canvas:#f5f7fa;--surface:#fff;--ink:#0b1f33;--muted:#5b6b7f;--line:#d8e1ea;--blue:#246bfe;--green:#087f5b;--amber:#b86b00}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:linear-gradient(180deg,#faf9f6,#f5f7fa 32rem);color:var(--ink);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1120px;margin:auto;padding:32px 28px 72px}.report-head{padding:36px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(135deg,#fff,#edf5ff);box-shadow:0 12px 36px #0b1f3312}.brand{font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;color:#164fc5;font-weight:800}.report-head h1{font-size:clamp(2rem,5vw,3.25rem);letter-spacing:-.045em;line-height:1.08;margin:.65rem 0}.report-head p{color:var(--muted);max-width:760px}.evidence{display:inline-block;padding:.35rem .65rem;border:1px solid #bfe6d6;border-radius:999px;background:#e6f6ef;color:#086c4e;font-size:.75rem;font-weight:750}
.toc,.card{margin:20px 0;border:1px solid var(--line);border-radius:16px;background:rgba(255,255,255,.92);padding:20px;box-shadow:0 4px 18px #0b1f330b}.toc a{display:inline-block;margin:.3rem .8rem .3rem 0;color:#164fc5;font-weight:650}h2{margin-top:2.3rem;letter-spacing:-.03em}h3{letter-spacing:-.02em}a{color:#164fc5}ul{padding-left:1.25rem}.fem-table{max-width:100%;overflow:auto;border-radius:12px;margin:1rem 0}.fem-table:focus{outline:3px solid #246bfe55}.fem-table table,table{width:100%;border-collapse:collapse;background:#fff;font-size:.9rem}.fem-table caption,caption{text-align:left;font-weight:750;padding:.7rem 0}.fem-table th,.fem-table td,th,td{padding:.7rem;border:1px solid var(--line);text-align:left}.fem-table th,th{background:#eef3f8;color:#40546a}pre{overflow:auto;white-space:pre-wrap;background:#eef3f8;border:1px solid var(--line);padding:18px;border-radius:12px}details{border:1px solid var(--line);background:#fff;border-radius:12px;padding:.7rem 1rem;margin:1rem 0}summary{cursor:pointer;font-weight:700;min-height:34px}.plotly-graph-div{max-width:100%!important}.warning{border-left:4px solid var(--amber);background:#fff4dc;padding:1rem;border-radius:10px}.status{color:var(--muted);font-size:.9rem}.footer{margin-top:3rem;border-top:1px solid var(--line);padding-top:1rem;color:var(--muted);font-size:.84rem}
@media(max-width:640px){main{padding:16px 12px 48px}.report-head{padding:22px 18px}.toc,.card{padding:15px}.fem-table{overscroll-behavior-inline:contain}h2{font-size:1.4rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
"""


def report_start(title: str, summary: str, evidence: str, sections: list[tuple[str, str]]) -> str:
    links = "".join(
        f'<a href="#{escape(anchor)}">{escape(label)}</a>' for anchor, label in sections
    )
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>"
        + escape(title)
        + "</title><style>"
        + REPORT_CSS
        + "</style></head><body><main><header class='report-head'><div class='brand'>"
        "FEM / Structural Lab · Local engineering evidence</div><h1>"
        + escape(title)
        + "</h1><p>"
        + escape(summary)
        + "</p><span class='evidence'>"
        + escape(evidence)
        + "</span></header><nav class='toc' aria-label='Report contents'><strong>Contents</strong><br>"
        + links
        + "</nav>"
    )


def report_end() -> str:
    return (
        "<footer class='footer'>Generated locally by FEM / Structural Lab. "
        "Recompute imported models before relying on a result.</footer></main></body></html>"
    )
