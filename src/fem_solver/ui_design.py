"""Shared visual language for the local Streamlit application.

This module renders presentation only. It must not import or alter the FEM solver.
"""

from __future__ import annotations

from html import escape
from typing import Iterable, Sequence

import streamlit as st

from .terms import TERM_CSS, TERMS, term_html

PLOT_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
}


DESIGN_CSS = r"""
:root{
  --fem-canvas:#f5f7fa;
  --fem-canvas-warm:#faf9f6;
  --fem-surface:#ffffff;
  --fem-surface-soft:#edf3f8;
  --fem-surface-blue:#eaf2ff;
  --fem-ink:#0b1f33;
  --fem-muted:#5b6b7f;
  --fem-faint:#8190a3;
  --fem-line:#d8e1ea;
  --fem-blue:#246bfe;
  --fem-blue-deep:#164fc5;
  --fem-cyan:#0f9fae;
  --fem-green:#087f5b;
  --fem-green-soft:#e6f6ef;
  --fem-amber:#b86b00;
  --fem-amber-soft:#fff4dc;
  --fem-red:#b9384a;
  --fem-red-soft:#fdecef;
  --fem-radius-sm:9px;
  --fem-radius-md:14px;
  --fem-radius-lg:20px;
  --fem-shadow:0 12px 36px rgba(11,31,51,.07);
  --fem-shadow-soft:0 4px 18px rgba(11,31,51,.045);
}

html,body,[class*="css"]{
  font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI Variable Text","Segoe UI",sans-serif;
}
.stApp{
  color:var(--fem-ink);
  background:
    radial-gradient(circle at 92% 2%,rgba(36,107,254,.055),transparent 25rem),
    linear-gradient(180deg,var(--fem-canvas-warm) 0,var(--fem-canvas) 34rem);
}
[data-testid="stMainBlockContainer"]{
  max-width:1480px;
  padding:2.25rem 3.25rem 5rem;
}
[data-testid="stSidebar"]{
  width:280px!important;
  min-width:280px!important;
  background:linear-gradient(180deg,#edf3f8 0%,#e8eff6 100%);
  border-right:1px solid var(--fem-line);
  box-shadow:8px 0 30px rgba(11,31,51,.035);
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding:1.2rem .8rem 1.4rem}

h1,h2,h3{color:var(--fem-ink);letter-spacing:-.035em}
h1{font-size:clamp(2.15rem,3vw,3.15rem)!important;line-height:1.07!important;margin-bottom:.65rem!important}
h2{font-size:1.6rem!important;line-height:1.2!important}
h3{font-size:1.15rem!important;line-height:1.3!important;letter-spacing:-.018em}
p,li{line-height:1.68}

button,[role="button"],input,textarea,[data-baseweb="select"]{transition:border-color .16s ease,box-shadow .16s ease,background .16s ease,transform .16s ease}
button:focus-visible,[role="button"]:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible{
  outline:3px solid rgba(36,107,254,.3)!important;
  outline-offset:2px!important;
}
[data-testid="stButton"]>button,[data-testid="stDownloadButton"]>button{
  min-height:44px;
  border-radius:10px;
  border-color:#cbd7e3;
  font-weight:650;
  padding-inline:1.05rem;
  box-shadow:none;
}
[data-testid="stButton"]>button[kind="primary"]{
  background:linear-gradient(135deg,var(--fem-blue) 0%,#1859df 100%);
  border:0;
  box-shadow:0 7px 18px rgba(36,107,254,.22);
}
[data-testid="stButton"]>button[kind="primary"]:hover{transform:translateY(-1px);box-shadow:0 10px 24px rgba(36,107,254,.26)}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]>div,[data-testid="stNumberInput"] input{
  background:rgba(255,255,255,.94)!important;
  border-color:var(--fem-line)!important;
  border-radius:10px!important;
}

[data-testid="stExpander"]{
  background:rgba(255,255,255,.76);
  border:1px solid var(--fem-line)!important;
  border-radius:var(--fem-radius-md)!important;
  overflow:hidden;
}
[data-testid="stExpander"] summary{min-height:46px;font-weight:630;color:var(--fem-ink)}
[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:.35rem;background:#eaf0f6;border-radius:12px;padding:.3rem}
[data-testid="stTabs"] [role="tab"]{border-radius:9px;padding:.62rem 1rem;height:auto;font-weight:620}
[data-testid="stTabs"] [aria-selected="true"]{background:white;box-shadow:var(--fem-shadow-soft)}
[data-testid="stDataFrame"]{border:1px solid var(--fem-line);border-radius:12px;overflow:hidden;background:white}

.fem-brand{padding:.35rem .45rem .85rem}
.fem-brand-mark{display:flex;align-items:center;gap:.72rem;font-size:1.02rem;font-weight:780;color:var(--fem-ink)}
.fem-brand-logo{display:grid;place-items:center;width:36px;height:36px;border-radius:11px;background:linear-gradient(145deg,var(--fem-blue),#123d9a);color:white;box-shadow:0 7px 16px rgba(36,107,254,.22)}
.fem-brand-sub{margin:.42rem 0 0 3rem;color:var(--fem-muted);font-size:.76rem;letter-spacing:.055em;text-transform:uppercase}
.fem-local-row{display:flex;align-items:center;gap:.45rem;margin:.75rem .45rem 1rem;color:var(--fem-muted);font-size:.78rem}
.fem-local-dot{width:8px;height:8px;border-radius:50%;background:var(--fem-green);box-shadow:0 0 0 4px rgba(8,127,91,.12)}

.st-key-mode-switch [role="radiogroup"]{display:flex;flex-direction:row!important;gap:.25rem;background:#dfe8f1;padding:.25rem;border-radius:11px}
.st-key-mode-switch label{flex:1;border-radius:8px;padding:.5rem .55rem!important;justify-content:center;margin:0!important}
.st-key-mode-switch label[data-selected="true"]{background:white;box-shadow:var(--fem-shadow-soft)}
.st-key-mode-switch label>div>div>div:first-child{display:none}
.st-key-mode-switch p{font-size:.78rem!important;font-weight:650!important;white-space:nowrap}

.st-key-workspace-nav [role="radiogroup"]{gap:.22rem}
.st-key-workspace-nav label{position:relative;min-height:43px;padding:.58rem .7rem!important;border-radius:10px;margin:0!important;border:1px solid transparent}
.st-key-workspace-nav label:hover{background:rgba(255,255,255,.68);border-color:#d3dee9}
.st-key-workspace-nav label[data-selected="true"]{background:white;border-color:#cbd9e8;box-shadow:var(--fem-shadow-soft)}
.st-key-workspace-nav label>div>div>div:first-child{display:none}
.st-key-workspace-nav label:has(input:focus-visible){outline:3px solid rgba(36,107,254,.3);outline-offset:1px}
.st-key-workspace-nav p{font-size:.86rem!important;font-weight:610!important}
.st-key-workspace-nav label:nth-child(1) p::before{content:"⌂"}.st-key-workspace-nav label:nth-child(2) p::before{content:"◇"}.st-key-workspace-nav label:nth-child(3) p::before{content:"≡"}.st-key-workspace-nav label:nth-child(4) p::before{content:"▶"}.st-key-workspace-nav label:nth-child(5) p::before{content:"⌁"}.st-key-workspace-nav label:nth-child(6) p::before{content:"?"}
.st-key-workspace-nav p::before{display:inline-grid;place-items:center;width:20px;height:20px;margin-right:.45rem;border-radius:6px;background:#e7eef6;color:#405a73;font-size:.72rem;font-weight:800}
.st-key-workspace-nav label[data-selected="true"] p::before{background:var(--fem-surface-blue);color:var(--fem-blue-deep)}
.st-key-project-snapshot{background:rgba(255,255,255,.68);border:1px solid #d4dfe9;border-radius:13px;padding:.8rem .85rem;margin-top:.6rem}
.fem-side-label{font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--fem-faint);font-weight:740;margin-bottom:.35rem}
.fem-side-project{font-weight:720;color:var(--fem-ink);overflow-wrap:anywhere}
.fem-side-meta{font-size:.77rem;color:var(--fem-muted);margin-top:.2rem}
.fem-safety{font-size:.76rem;line-height:1.5;color:var(--fem-muted);padding:.75rem .45rem 0;border-top:1px solid #d3dde7;margin-top:1rem}

.fem-page-head{margin:.15rem 0 1.45rem;max-width:930px}
.fem-eyebrow{font-size:.73rem;letter-spacing:.105em;text-transform:uppercase;color:var(--fem-blue-deep);font-weight:780;margin-bottom:.62rem}
.fem-page-title{font-size:clamp(2.15rem,3vw,3.15rem);line-height:1.07;letter-spacing:-.042em;font-weight:790;color:var(--fem-ink);margin:0}
.fem-page-summary{font-size:1.02rem;color:var(--fem-muted);max-width:780px;margin:.75rem 0 0;line-height:1.68}

.fem-stage{display:grid!important;width:100%;grid-template-columns:repeat(3,1fr);gap:.7rem;margin:.1rem 0 1.55rem!important;max-width:980px;padding:0!important;list-style:none!important}
.fem-stage-step{position:relative;display:flex!important;align-items:center;gap:.7rem;padding:.68rem .8rem!important;margin:0!important;border:1px solid var(--fem-line);border-radius:12px;background:rgba(255,255,255,.62);color:var(--fem-muted);font-size:.81rem;font-weight:650;list-style:none!important}
.fem-stage-step::after{content:"";position:absolute;left:.8rem;right:.8rem;bottom:-1px;height:2px;background:transparent}
.fem-stage-number{display:grid;place-items:center;min-width:26px;height:26px;border-radius:8px;background:#e4ebf2;color:#587085;font-size:.75rem}
.fem-stage-step.is-current{background:white;border-color:#bcd0f1;color:var(--fem-ink);box-shadow:var(--fem-shadow-soft)}
.fem-stage-step.is-current::after{background:var(--fem-blue)}
.fem-stage-step.is-current .fem-stage-number{background:var(--fem-blue);color:white}
.fem-stage-step.is-done .fem-stage-number{background:var(--fem-green-soft);color:var(--fem-green)}

.fem-badges{display:flex;flex-wrap:wrap;gap:.45rem;margin:.3rem 0 .8rem}
.fem-badge{display:inline-flex;align-items:center;gap:.35rem;border-radius:999px;padding:.31rem .63rem;font-size:.72rem;font-weight:740;letter-spacing:.018em;border:1px solid #d5e0eb;background:white;color:var(--fem-muted)}
.fem-badge.blue{background:var(--fem-surface-blue);border-color:#c9dcff;color:#174eac}
.fem-badge.green{background:var(--fem-green-soft);border-color:#bfe6d6;color:#086c4e}
.fem-badge.amber{background:var(--fem-amber-soft);border-color:#f0d9a7;color:#8d5200}
.fem-badge.red{background:var(--fem-red-soft);border-color:#f1c7cf;color:#9b293a}

.fem-hero{position:relative;overflow:hidden;border:1px solid #d5e1ec;border-radius:22px;background:linear-gradient(135deg,#fff 0%,#f5f9ff 70%,#edf5ff 100%);padding:clamp(1.35rem,3vw,2.6rem);box-shadow:var(--fem-shadow);margin-bottom:1.25rem}
.fem-hero::before{content:"";position:absolute;width:360px;height:360px;border:1px solid rgba(36,107,254,.09);border-radius:50%;right:-190px;top:-190px;box-shadow:0 0 0 40px rgba(36,107,254,.025),0 0 0 80px rgba(36,107,254,.018)}
.fem-hero h1{position:relative;margin:0 0 .65rem!important;max-width:820px}
.fem-hero p{position:relative;color:var(--fem-muted);font-size:1.04rem;max-width:720px;margin:0}

.fem-section-title{display:flex;align-items:end;justify-content:space-between;gap:1rem;margin:1.7rem 0 .85rem}
.fem-section-title h2{margin:0!important}
.fem-section-title p{color:var(--fem-muted);margin:0;font-size:.88rem}
.fem-panel{background:rgba(255,255,255,.86);border:1px solid var(--fem-line);border-radius:var(--fem-radius-lg);padding:1rem 1.1rem;box-shadow:var(--fem-shadow-soft)}
.fem-panel-title{font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;font-weight:760;color:var(--fem-faint);margin-bottom:.55rem}

.fem-family-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.9rem;margin:.9rem 0 1.2rem}
.fem-family-card{min-height:205px;background:rgba(255,255,255,.9);border:1px solid var(--fem-line);border-radius:18px;padding:1rem;box-shadow:var(--fem-shadow-soft);overflow:hidden}
.fem-family-art{height:76px;border-radius:12px;background:linear-gradient(135deg,#f4f8fd,#eaf2fb);display:grid;place-items:center;margin-bottom:.78rem}
.fem-family-card h3{margin:.1rem 0 .25rem!important}
.fem-family-card p{font-size:.82rem;color:var(--fem-muted);margin:0;line-height:1.5}
.fem-family-dofs{font-size:.72rem!important;color:var(--fem-blue-deep)!important;font-weight:690;margin-top:.5rem!important}
[class*="st-key-family_"]{background:rgba(255,255,255,.9);border:1px solid var(--fem-line);border-radius:18px;padding:.8rem;box-shadow:var(--fem-shadow-soft);min-height:330px}
[class*="st-key-family_"] .fem-family-card{border:0;box-shadow:none;padding:.25rem;min-height:205px;background:transparent}
[class*="st-key-family_"] [data-testid="stHorizontalBlock"]{gap:.45rem}
[class*="st-key-family_"] [data-testid="stButton"]>button{font-size:.78rem;padding-inline:.55rem}
.fem-current-project{display:grid;grid-template-columns:auto 1fr;gap:.8rem;align-items:center}
.fem-current-icon{display:grid;place-items:center;width:46px;height:46px;border-radius:13px;background:var(--fem-surface-blue);color:var(--fem-blue);font-size:1.25rem}
.fem-current-project h3{margin:0!important}.fem-current-project p{margin:.2rem 0 0;color:var(--fem-muted);font-size:.82rem}

.fem-metric-grid{display:grid;grid-template-columns:repeat(var(--metric-count,4),minmax(0,1fr));gap:.8rem;margin:.8rem 0 1.1rem}
.fem-metric{background:rgba(255,255,255,.94);border:1px solid var(--fem-line);border-radius:16px;padding:1rem 1.05rem;min-width:0;box-shadow:var(--fem-shadow-soft)}
.fem-metric dt{font-size:.74rem;color:var(--fem-muted);font-weight:680;line-height:1.35;margin:0 0 .45rem}
.fem-metric dd{font-size:clamp(1.18rem,2vw,1.72rem);line-height:1.18;font-weight:730;letter-spacing:-.025em;color:var(--fem-ink);margin:0;overflow-wrap:anywhere;word-break:normal}
.fem-metric small{display:block;margin-top:.4rem;color:var(--fem-faint);font-size:.7rem;line-height:1.4}

.fem-empty{border:1px dashed #b9c9d8;border-radius:20px;background:linear-gradient(145deg,rgba(255,255,255,.85),rgba(238,244,250,.82));padding:2.2rem;text-align:center;margin:1rem 0}
.fem-empty-icon{width:58px;height:58px;display:grid;place-items:center;border-radius:18px;background:var(--fem-surface-blue);color:var(--fem-blue);font-size:1.6rem;margin:0 auto .9rem}
.fem-empty h2{margin:.2rem 0 .45rem!important}
.fem-empty p{max-width:610px;color:var(--fem-muted);margin:.3rem auto}

.fem-step-map{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.65rem;margin:.8rem 0 1.2rem}
.fem-step-card{background:white;border:1px solid var(--fem-line);border-radius:14px;padding:.85rem;min-height:112px;box-shadow:var(--fem-shadow-soft)}
.fem-step-card b{display:grid;place-items:center;width:27px;height:27px;border-radius:8px;background:var(--fem-surface-blue);color:var(--fem-blue-deep);font-size:.75rem;margin-bottom:.5rem}
.fem-step-card span{font-size:.81rem;line-height:1.4;font-weight:650;color:var(--fem-ink)}

.fem-status{display:flex;gap:.75rem;align-items:flex-start;border-radius:14px;padding:.9rem 1rem;border:1px solid var(--fem-line);background:white;margin:.7rem 0}
.fem-status-symbol{display:grid;place-items:center;width:28px;height:28px;flex:0 0 28px;border-radius:9px;font-weight:800}
.fem-status strong{display:block;margin:.05rem 0 .18rem}
.fem-status p{font-size:.82rem;color:var(--fem-muted);line-height:1.5;margin:0}
.fem-status.success{background:var(--fem-green-soft);border-color:#bfe6d6}.fem-status.success .fem-status-symbol{background:#ccecdf;color:#087653}
.fem-status.warning{background:var(--fem-amber-soft);border-color:#f0d9a7}.fem-status.warning .fem-status-symbol{background:#f6dfaf;color:#8d5200}
.fem-status.error{background:var(--fem-red-soft);border-color:#f1c7cf}.fem-status.error .fem-status-symbol{background:#f5d1d7;color:#a22d3f}

.fem-copy{font-size:.96rem}
.fem-key-trigger{font-size:.82rem;color:var(--fem-muted)}
.fem-popover-term{padding:.52rem 0;border-bottom:1px solid #e5eaf0}
.fem-popover-term:last-child{border-bottom:0}
.fem-popover-term b{color:var(--fem-ink)}
.fem-popover-term span{display:block;color:var(--fem-muted);font-size:.78rem;line-height:1.45;margin-top:.15rem}

.fem-table{overflow:auto;max-width:100%;border-radius:12px}
.fem-table:focus-visible{outline:3px solid rgba(36,107,254,.35);outline-offset:3px}
.fem-table table{border-collapse:separate;border-spacing:0;width:100%;font-size:.84rem;background:white}
.fem-table caption{text-align:left;font-weight:740;color:var(--fem-ink);padding:.7rem 0}
.fem-table th{background:#eef3f8;color:#40546a;font-size:.73rem;text-transform:none;letter-spacing:.015em}
.fem-table th,.fem-table td{border-right:1px solid var(--fem-line);border-bottom:1px solid var(--fem-line);padding:.65rem .72rem;text-align:left}
.fem-table th:first-child,.fem-table td:first-child{border-left:1px solid var(--fem-line)}
.fem-table tr:first-of-type th{border-top:1px solid var(--fem-line)}

.st-key-action-bar{position:sticky;bottom:.7rem;z-index:90;background:rgba(255,255,255,.88);backdrop-filter:blur(14px);border:1px solid #d1deea;border-radius:15px;padding:.65rem .75rem;box-shadow:0 12px 36px rgba(11,31,51,.12);margin:1rem 0}
.st-key-study-controls,.st-key-preview-panel,.st-key-result-card{background:rgba(255,255,255,.86);border:1px solid var(--fem-line);border-radius:18px;padding:1rem;box-shadow:var(--fem-shadow-soft)}

@media(max-width:1100px){
  [data-testid="stMainBlockContainer"]{padding-inline:2rem}
  .fem-family-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
  [data-testid="stHorizontalBlock"]:has(.st-key-family_bar){flex-wrap:wrap!important}
  [data-testid="stHorizontalBlock"]:has(.st-key-family_bar)>[data-testid="stColumn"]{width:calc(50% - .55rem)!important;flex:1 1 calc(50% - .55rem)!important}
  .fem-step-map{grid-template-columns:repeat(2,minmax(0,1fr))}
  .fem-metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media(min-width:761px) and (max-width:1100px){
  [data-testid="stSidebar"]{position:fixed!important;inset:0 auto 0 0!important;z-index:999!important;box-shadow:16px 0 36px rgba(11,31,51,.14)}
  [data-testid="stMain"]{position:absolute!important;inset:0!important;width:100vw!important;max-width:100vw!important;margin-left:0!important;flex:1 1 100%!important}
}
@media(max-width:760px){
  [data-testid="stMainBlockContainer"]{padding:1.6rem 1rem 4rem}
  [data-testid="stSidebar"]{width:min(300px,86vw)!important;min-width:min(300px,86vw)!important}
  [data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:.65rem!important}
  [data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{width:100%!important;flex:1 1 100%!important;min-width:0!important}
  [data-testid="stHorizontalBlock"]:has(.st-key-family_bar)>[data-testid="stColumn"]{width:100%!important;flex:1 1 100%!important}
  .fem-page-title{font-size:2.08rem;line-height:1.08}
  .fem-page-summary{font-size:.94rem}
  .fem-stage{display:block!important;margin-bottom:1.15rem!important}
  .fem-stage-step{display:none!important}
  .fem-stage-step.is-current{display:flex!important;padding:.58rem .7rem!important}
  .fem-stage-step.is-current .fem-stage-label::before{content:attr(data-mobile);margin-right:.35rem;color:var(--fem-blue-deep)}
  .fem-family-grid{grid-template-columns:1fr}
  .fem-step-map{grid-template-columns:1fr 1fr}
  .fem-metric-grid{grid-template-columns:1fr 1fr}
  .fem-metric{padding:.85rem}
  .fem-metric dd{font-size:1.2rem}
  .fem-hero{padding:1.3rem}
  .fem-empty{padding:1.4rem 1rem}
  .st-key-action-bar{bottom:.35rem}
  [data-testid="stPlotlyChart"]{max-width:100%;overflow:hidden}
}
@media(max-width:430px){
  .fem-step-map,.fem-metric-grid{grid-template-columns:1fr}
  .fem-section-title{display:block}.fem-section-title p{margin-top:.25rem}
}
@media(prefers-reduced-motion:reduce){
  *,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}
}
"""


def inject_design() -> None:
    """Install the local theme once per Streamlit rerun."""
    st.markdown("<style>" + TERM_CSS + DESIGN_CSS + "</style>", unsafe_allow_html=True)


def page_header(title: str, summary: str, eyebrow: str) -> None:
    st.markdown(
        '<header class="fem-page-head"><div class="fem-eyebrow">'
        + escape(eyebrow)
        + '</div><h1 class="fem-page-title">'
        + escape(title)
        + '</h1><p class="fem-page-summary">'
        + escape(summary)
        + "</p></header>",
        unsafe_allow_html=True,
    )


def stage_progress(active: int) -> None:
    labels = ("Define the problem", "Understand the method", "Solve and discuss")
    items = []
    for number, label in enumerate(labels, 1):
        state = "is-current" if number == active else "is-done" if number < active else ""
        current = ' aria-current="step"' if number == active else ""
        items.append(
            f'<li class="fem-stage-step {state}"{current}>'
            f'<span class="fem-stage-number">{number}</span>'
            f'<span class="fem-stage-label" data-mobile="Stage {number} of 3 ·">{escape(label)}</span></li>'
        )
    st.markdown(
        '<ol class="fem-stage" aria-label="Learning stages">' + "".join(items) + "</ol>",
        unsafe_allow_html=True,
    )


def badges(items: Sequence[tuple[str, str]]) -> None:
    st.markdown(
        '<div class="fem-badges">'
        + "".join(
            f'<span class="fem-badge {escape(tone)}">{escape(label)}</span>'
            for label, tone in items
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def section_title(title: str, note: str = "") -> None:
    st.markdown(
        '<div class="fem-section-title"><h2>'
        + escape(title)
        + "</h2>"
        + ("<p>" + escape(note) + "</p>" if note else "")
        + "</div>",
        unsafe_allow_html=True,
    )


def key_terms(keys: Iterable[str], label: str = "Key terms") -> None:
    unique = list(dict.fromkeys(keys))
    with st.popover(label, icon=":material/menu_book:"):
        st.caption("Simple meanings used in this view")
        for key in unique:
            term = TERMS[key]
            st.markdown(
                '<div class="fem-popover-term"><b>'
                + escape(term.label)
                + "</b><span>"
                + escape(term.meaning)
                + "</span></div>",
                unsafe_allow_html=True,
            )


def metric_cards(items: Sequence[tuple[str, str, str]], label: str = "Key results") -> None:
    count = min(max(len(items), 1), 4)
    cards = []
    for name, value, note in items:
        cards.append(
            '<div class="fem-metric"><dt>'
            + escape(name)
            + "</dt><dd>"
            + escape(value)
            + "</dd>"
            + ("<small>" + escape(note) + "</small>" if note else "")
            + "</div>"
        )
    st.markdown(
        f'<dl class="fem-metric-grid" style="--metric-count:{count}" aria-label="{escape(label)}">'
        + "".join(cards)
        + "</dl>",
        unsafe_allow_html=True,
    )


def empty_state(title: str, message: str, icon: str = "◎") -> None:
    st.markdown(
        '<section class="fem-empty"><div class="fem-empty-icon" aria-hidden="true">'
        + escape(icon)
        + "</div><h2>"
        + escape(title)
        + "</h2><p>"
        + escape(message)
        + "</p></section>",
        unsafe_allow_html=True,
    )


def status_message(title: str, message: str, tone: str = "success") -> None:
    symbols = {"success": "✓", "warning": "!", "error": "×"}
    st.markdown(
        f'<div class="fem-status {escape(tone)}" role="status">'
        f'<span class="fem-status-symbol" aria-hidden="true">{symbols.get(tone, "i")}</span>'
        "<div><strong>" + escape(title) + "</strong><p>" + escape(message) + "</p></div></div>",
        unsafe_allow_html=True,
    )


def step_map(titles: Sequence[str]) -> None:
    cards = []
    for index, title in enumerate(titles, 1):
        short = title.split(". ", 1)[-1]
        cards.append(f'<div class="fem-step-card"><b>{index}</b><span>{escape(short)}</span></div>')
    st.markdown('<div class="fem-step-map">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def term_inline(key: str, label: str | None = None) -> str:
    """Expose the shared term renderer to presentation modules."""
    return term_html(key, label)


def apply_plot_theme(figure, height: int | None = None):
    """Apply the quiet engineering-studio theme to a Plotly figure."""
    layout: dict[str, object] = {
        "font": {"family": "Segoe UI, system-ui, sans-serif", "color": "#0b1f33"},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "#ffffff",
        "colorway": ["#246bfe", "#0f9fae", "#b86b00", "#b9384a", "#6c5ce7"],
        "hoverlabel": {"bgcolor": "#0b1f33", "font": {"color": "#ffffff", "size": 12}},
        "margin": {"l": 48, "r": 26, "t": 52, "b": 48},
        "legend": {"bgcolor": "rgba(255,255,255,.88)", "bordercolor": "#d8e1ea", "borderwidth": 1},
    }
    if height is not None:
        layout["height"] = height
    figure.update_layout(**layout)
    figure.update_xaxes(gridcolor="#e7edf3", zerolinecolor="#cbd7e3")
    figure.update_yaxes(gridcolor="#e7edf3", zerolinecolor="#cbd7e3")
    return figure


def navigate(guided: str, direct: str | None = None) -> None:
    st.session_state["_pending_navigation"] = (guided, direct or guided)
    st.rerun()
