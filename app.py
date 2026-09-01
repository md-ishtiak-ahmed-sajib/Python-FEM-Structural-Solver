"""Local learning application. Run: python -m streamlit run app.py."""

import json
from copy import deepcopy

import streamlit as st

from fem_solver.examples import NAMES, example_data
from fem_solver.learning import blank_data, project_from_dict
from fem_solver.model import ModelError, model_to_dict
from fem_solver.ui_common import explain, glossary_view, style
from fem_solver.ui_learning import define_view, install_draft, solve_view, understand_view
from fem_solver.ui_study import study_view

st.set_page_config(page_title="FEM · Structural Lab", page_icon="◈", layout="wide")
style()

if "draft" not in st.session_state:
    install_draft(st.session_state.get("model_data", example_data("Axial bar")))


def keep_editor():
    # Widget state is removed when its page disappears. Keep the actual draft separately.
    st.session_state.editor_base = deepcopy(st.session_state.draft)
    st.session_state.revision += 1


with st.sidebar:
    st.markdown("### ◈ FEM / Structural Lab")
    st.caption("DEFINE · UNDERSTAND · SOLVE")
    mode = st.radio("Navigation", ["Guided learning", "Direct access"], on_change=keep_editor)
    routes = (
        {
            "1 · Define": define_view,
            "2 · Understand": understand_view,
            "3 · Solve and discuss": solve_view,
            "Stiffness study": study_view,
            "Glossary": glossary_view,
        }
        if mode == "Guided learning"
        else {
            "Model": define_view,
            "Inside FEM": understand_view,
            "Results": solve_view,
            "Stiffness study": study_view,
            "Glossary": glossary_view,
        }
    )
    view = st.radio("Workspace", list(routes), key="workspace_" + mode, on_change=keep_editor)
    st.divider()
    with st.expander("Start or import a problem"):
        chosen = st.selectbox("Example structure", NAMES, index=3)
        if st.button("Load example", width="stretch"):
            install_draft(example_data(chosen))
            st.rerun()
        family = st.selectbox("Blank model family", ["bar", "truss", "beam", "frame"])
        if st.button("Start blank model", width="stretch"):
            install_draft(blank_data(family))
            st.rerun()
        uploaded = st.file_uploader("Import model or learning project JSON", type=["json"])
        if uploaded and st.button("Open uploaded project", width="stretch"):
            try:
                model, brief = project_from_dict(json.loads(uploaded.getvalue()))
                install_draft(model_to_dict(model), brief)
                st.rerun()
            except (ModelError, ValueError) as exc:
                st.error(str(exc))
    st.divider()
    st.caption("RUNS ON YOUR COMPUTER")
    explain("Hover or tap dotted terms for help. You can also search the glossary.")
    st.warning("For learning and research. This app does not certify structural safety.")

st.markdown(
    '<div class="stage-band">DEFINE THE PROBLEM → UNDERSTAND THE METHOD → SOLVE AND DISCUSS</div>',
    unsafe_allow_html=True,
)
routes[view]()
