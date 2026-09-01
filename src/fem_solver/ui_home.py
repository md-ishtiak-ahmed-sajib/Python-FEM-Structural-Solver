"""Project launchpad for the local engineering studio."""

from __future__ import annotations

import json
from html import escape

import streamlit as st

from .examples import example_data
from .learning import blank_data, project_from_dict
from .model import ModelError, model_from_dict, model_to_dict
from .ui_design import badges, navigate, section_title, status_message
from .ui_learning import install_draft

FAMILIES = {
    "bar": {
        "name": "Bar",
        "example": "Axial bar",
        "use": "Straight members that carry force along their length.",
        "moves": "Movement: horizontal translation",
        "svg": """<svg viewBox='0 0 180 64' role='img' aria-label='Axial bar with a fixed left end and a force at the right end'><path d='M31 9v46M23 13l8-4m-8 13l8-4m-8 13l8-4m-8 13l8-4m-8 13l8-4' stroke='#5b6b7f' stroke-width='2'/><path d='M32 32h105' stroke='#246bfe' stroke-width='8' stroke-linecap='round'/><path d='M137 32h25m-10-9 10 9-10 9' fill='none' stroke='#0b1f33' stroke-width='2.5'/></svg>""",
    },
    "truss": {
        "name": "Truss",
        "example": "Triangular truss",
        "use": "Pin-connected members that carry axial tension or compression.",
        "moves": "Movements: horizontal and vertical",
        "svg": """<svg viewBox='0 0 180 64' role='img' aria-label='Triangular planar truss'><path d='M24 51L90 10l66 41H24M24 51l132 0' fill='none' stroke='#246bfe' stroke-width='5' stroke-linejoin='round'/><g fill='#fff' stroke='#0b1f33' stroke-width='2'><circle cx='24' cy='51' r='5'/><circle cx='90' cy='10' r='5'/><circle cx='156' cy='51' r='5'/></g></svg>""",
    },
    "beam": {
        "name": "Beam",
        "example": "Cantilever beam",
        "use": "Slender members that resist transverse load by bending.",
        "moves": "Movements: vertical translation and rotation",
        "svg": """<svg viewBox='0 0 180 64' role='img' aria-label='Cantilever beam with a downward load'><path d='M28 7v50M19 12l9-5m-9 15l9-5m-9 15l9-5m-9 15l9-5m-9 15l9-5' stroke='#5b6b7f' stroke-width='2'/><path d='M30 39h126' stroke='#246bfe' stroke-width='7' stroke-linecap='round'/><path d='M145 7v22m-8-10 8 10 8-10' fill='none' stroke='#0b1f33' stroke-width='2.5'/></svg>""",
    },
    "frame": {
        "name": "Frame",
        "example": "Portal frame",
        "use": "Connected beams and columns that carry axial force and bending.",
        "moves": "Movements: horizontal, vertical and rotation",
        "svg": """<svg viewBox='0 0 180 64' role='img' aria-label='Two-dimensional portal frame'><path d='M38 55V12h104v43' fill='none' stroke='#246bfe' stroke-width='7' stroke-linejoin='round'/><path d='M24 56h28m76 0h28' stroke='#5b6b7f' stroke-width='2.5'/><path d='M72 24h32m-10-8 10 8-10 8' fill='none' stroke='#0b1f33' stroke-width='2.5'/></svg>""",
    },
}


def _open(model_data: dict) -> None:
    install_draft(model_data)
    st.session_state["project_started"] = True
    navigate("1 · Define", "Model")


def _family_card(kind: str, details: dict[str, str]) -> None:
    st.markdown(
        '<div class="fem-family-card"><div class="fem-family-art">'
        + details["svg"]
        + "</div><h3>"
        + escape(details["name"])
        + "</h3><p>"
        + escape(details["use"])
        + '</p><p class="fem-family-dofs">'
        + escape(details["moves"])
        + "</p></div>",
        unsafe_allow_html=True,
    )
    left, right = st.columns(2)
    if left.button("Start blank", key="blank_" + kind, width="stretch"):
        _open(blank_data(kind))
    if right.button("Open example", key="example_" + kind, width="stretch", type="primary"):
        _open(example_data(details["example"]))


def home_view() -> None:
    """Show deliberate starting points without running the solver."""
    st.markdown(
        '<section class="fem-hero"><div class="fem-eyebrow">LOCAL ENGINEERING WORKSPACE</div>'
        "<h1>Build the model. See the method. Explain the answer.</h1>"
        "<p>Choose a structural family, begin from a checked example, or continue your current draft. "
        "Nothing is solved until you ask the engine to solve it.</p></section>",
        unsafe_allow_html=True,
    )
    badges([("Runs locally", "green"), ("Works offline", "blue"), ("No account", "")])

    section_title("Start a structural problem", "Four linear static element families")
    columns = st.columns(4)
    for column, (kind, details) in zip(columns, FAMILIES.items(), strict=True):
        with column:
            with st.container(key="family_" + kind):
                _family_card(kind, details)

    current, importer = st.columns([1.35, 1])
    with current:
        section_title("Current session")
        draft = st.session_state.get("draft")
        if draft:
            try:
                model = model_from_dict(draft)
                title = model.title
                family = model.kind.title()
                units = str(draft.get("units", "N-m-Pa"))
                valid = True
            except ModelError:
                title = str(draft.get("title", "Incomplete draft"))
                family = str(draft.get("kind", "Unknown")).title()
                units = str(draft.get("units", "Units not set"))
                valid = False
            solve_state = "Solved" if st.session_state.get("solution") is not None else "Not solved"
            check_state = "Input checked" if valid else "Needs input changes"
            st.markdown(
                '<div class="fem-panel"><div class="fem-current-project">'
                '<div class="fem-current-icon" aria-hidden="true">◇</div><div><h3>'
                + escape(title)
                + "</h3><p>"
                + escape(f"{family} · {units} · {check_state} · {solve_state}")
                + "</p></div></div></div>",
                unsafe_allow_html=True,
            )
            if st.button("Continue current project", type="primary", width="stretch"):
                navigate("1 · Define", "Model")
        else:
            status_message(
                "No current draft", "Start blank, open an example, or import a project.", "warning"
            )

    with importer:
        section_title("Import a project")
        with st.container(border=True):
            st.write("Open a model JSON or learning-project JSON from your computer.")
            uploaded = st.file_uploader(
                "Choose a JSON file", type=["json"], label_visibility="collapsed"
            )
            if uploaded and st.button("Open imported project", type="primary", width="stretch"):
                try:
                    model, brief = project_from_dict(json.loads(uploaded.getvalue()))
                    install_draft(model_to_dict(model), brief)
                    st.session_state["project_started"] = True
                    navigate("1 · Define", "Model")
                except (ModelError, ValueError, json.JSONDecodeError) as exc:
                    st.error(str(exc))

    st.caption(
        "The current session lives only in this browser session. Export JSON when you want a reusable file."
    )
