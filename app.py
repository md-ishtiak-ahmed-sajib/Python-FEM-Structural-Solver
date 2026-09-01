"""Local learning application. Run: python -m streamlit run app.py."""

from copy import deepcopy
from html import escape

import streamlit as st

from fem_solver.examples import example_data
from fem_solver.model import ModelError, model_from_dict
from fem_solver.ui_common import glossary_view, style
from fem_solver.ui_design import stage_progress
from fem_solver.ui_home import home_view
from fem_solver.ui_learning import define_view, install_draft, solve_view, understand_view
from fem_solver.ui_study import study_view

st.set_page_config(
    page_title="FEM · Structural Lab",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
style()

if "draft" not in st.session_state:
    install_draft(st.session_state.get("model_data", example_data("Axial bar")))

pending_navigation = st.session_state.pop("_pending_navigation", None)
if pending_navigation:
    pending_mode = st.session_state.get("navigation_mode", "Guided learning")
    pending_index = 0 if pending_mode == "Guided learning" else 1
    st.session_state["workspace_" + pending_mode] = pending_navigation[pending_index]


def keep_editor():
    # Widget state is removed when its page disappears. Keep the actual draft separately.
    st.session_state.editor_base = deepcopy(st.session_state.draft)
    st.session_state.revision += 1


with st.sidebar:
    st.markdown(
        '<div class="fem-brand"><div class="fem-brand-mark"><span class="fem-brand-logo">◈</span>'
        '<span>FEM / Structural Lab</span></div><div class="fem-brand-sub">Engineering studio</div></div>'
        '<div class="fem-local-row"><span class="fem-local-dot"></span>Local and ready · no cloud</div>',
        unsafe_allow_html=True,
    )
    with st.container(key="mode-switch"):
        mode = st.radio(
            "Navigation",
            ["Guided learning", "Direct access"],
            key="navigation_mode",
            horizontal=True,
            label_visibility="collapsed",
            on_change=keep_editor,
        )
    routes = (
        {
            "Home": home_view,
            "1 · Define": define_view,
            "2 · Understand": understand_view,
            "3 · Solve and discuss": solve_view,
            "Stiffness study": study_view,
            "Glossary": glossary_view,
        }
        if mode == "Guided learning"
        else {
            "Home": home_view,
            "Model": define_view,
            "Inside FEM": understand_view,
            "Results": solve_view,
            "Stiffness study": study_view,
            "Glossary": glossary_view,
        }
    )
    with st.container(key="workspace-nav"):
        view = st.radio("Workspace", list(routes), key="workspace_" + mode, on_change=keep_editor)

    try:
        current = model_from_dict(st.session_state.draft)
        snapshot = f"{current.kind.title()} · {st.session_state.draft.get('units', 'N-m-Pa')}"
        title = current.title
    except ModelError:
        title = str(st.session_state.draft.get("title", "Incomplete draft"))
        snapshot = "Needs input changes"
    st.markdown(
        '<div class="st-key-project-snapshot"><div class="fem-side-label">Current project</div>'
        '<div class="fem-side-project">'
        + escape(title)
        + '</div><div class="fem-side-meta">'
        + escape(snapshot)
        + "</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="fem-safety"><b>Educational use</b><br>This app explains linear static FEM. '
        "It does not certify structural safety.</div>",
        unsafe_allow_html=True,
    )

stage_by_view = {
    "1 · Define": 1,
    "Model": 1,
    "2 · Understand": 2,
    "Inside FEM": 2,
    "3 · Solve and discuss": 3,
    "Results": 3,
}
if view in stage_by_view:
    stage_progress(stage_by_view[view])
routes[view]()
