"""Three teaching stages, each using the same public computational package."""

import io
import json
from dataclasses import asdict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .export import result_dict, results_csv
from .learning import (
    FAMILY,
    Change,
    Comparison,
    ProblemBrief,
    apply_change,
    build_guide,
    check_brief,
    compare_results,
    discuss,
    fingerprint,
    learning_report,
    member_summary,
    project_to_dict,
)
from .model import DOFS, UNITS, ModelError, model_from_dict, model_to_dict
from .solver import SolveOptions, assemble, solve_linear
from .terms import help_text, term_html
from .ui_common import TABLE_TERMS, TABLES, editor_columns, explain, readable_table, term_key
from .ui_design import (
    PLOT_CONFIG,
    apply_plot_theme,
    badges,
    empty_state,
    metric_cards,
    navigate,
    page_header,
    section_title,
    status_message,
    step_map,
)
from .visualization import member_figure, member_quantity, model_figure, structure_figure


def invalidate():
    for name in ("solution", "comparison", "solve_error"):
        st.session_state.pop(name, None)


def install_draft(data, brief=None):
    st.session_state.draft = data
    st.session_state.editor_base = data
    st.session_state.brief = asdict(brief or ProblemBrief())
    st.session_state.revision = st.session_state.get("revision", 0) + 1
    st.session_state.edit_units = data["units"]
    for name in ("active_case", "selected_member"):
        st.session_state.pop(name, None)
    invalidate()


def change_units():
    data = st.session_state.draft
    units = st.session_state.edit_units
    try:
        if not any(data.get(key) for key in TABLES):
            converted = dict(data, units=units)
        else:
            converted = model_to_dict(model_from_dict(data), units)
        brief = ProblemBrief(**st.session_state.brief)
        install_draft(converted, brief)
        st.session_state.pop("unit_error", None)
    except ModelError as exc:
        st.session_state.edit_units = data["units"]
        st.session_state.unit_error = "Finish or correct the draft before converting units. " + str(
            exc
        )


def get_model():
    try:
        return model_from_dict(st.session_state.draft)
    except (ModelError, ValueError) as exc:
        st.error("The current draft is not ready: " + str(exc))
        explain(
            "Return to Define and correct the inputs. Your draft is kept; no earlier result is substituted."
        )
        return None


def current_brief():
    return ProblemBrief(**st.session_state.brief)


def case_control(model):
    if st.session_state.get("active_case") not in model.cases:
        st.session_state.active_case = model.cases[0]
    return st.selectbox(
        "Load case", model.cases, key="active_case", help=help_text("case"), on_change=invalidate
    )


def member_control(model):
    ids = [e.id for e in model.elements]
    if st.session_state.get("selected_member") not in ids:
        st.session_state.selected_member = (
            current_brief().target_member if current_brief().target_member in ids else ids[0]
        )
    return st.selectbox("Inspect member", ids, key="selected_member", help=help_text("element"))


def define_view():
    page_header(
        "Define your structural problem",
        "Describe the real structure before asking the engine for an answer. Your incomplete work stays in this session.",
        "STAGE 1 OF 3 · DEFINE",
    )
    data = st.session_state.draft
    revision = st.session_state.revision
    units = st.selectbox(
        "Input / export units",
        list(UNITS),
        key="edit_units",
        on_change=change_units,
        help=help_text("si"),
    )
    if "unit_error" in st.session_state:
        st.warning(st.session_state.unit_error)
    data = st.session_state.draft
    revision = st.session_state.revision
    units = data["units"]
    brief = current_brief()
    badges([(data["kind"].title(), "blue"), (units, ""), ("Draft", "amber")])
    top_left, top_right = st.columns([1.5, 1])
    with top_left:
        title = st.text_input(
            "Project title", data.get("title", "My structural problem"), key=f"title_{revision}"
        )
        question = st.text_input("Engineering question", brief.question, key=f"question_{revision}")
    with top_right:
        scope = st.selectbox(
            "Structure extent",
            ["Whole structure", "Selected portion"],
            index=0 if brief.scope == "Whole structure" else 1,
            key=f"scope_{revision}",
        )
        st.caption(FAMILY[data["kind"]])
    notes = brief.boundary_notes
    if scope == "Selected portion":
        notes = st.text_area(
            "Cut-boundary forces and restraints",
            brief.boundary_notes,
            key=f"boundary_{revision}",
            help="Describe what the removed part does to this portion. Do not assume a cut is fixed.",
        )
        if not notes.strip():
            st.warning(
                "Add cut-boundary notes before moving to theory or solving. We will not invent the missing boundary conditions."
            )
    term_key(
        "node",
        "element",
        "dof",
        "ux",
        "uy",
        "rz",
        "E",
        "A",
        "I",
        "fiber",
        "constraint",
        "spring",
        "case",
        "qx",
        "qy",
    )
    categories = {
        "Geometry": ["nodes", "elements"],
        "Properties": ["materials", "sections"],
        "Supports": ["constraints", "springs"],
        "Loads": ["loads", "distributed_loads"],
    }
    candidate = {
        "schema_version": 1,
        "units": units,
        "kind": data["kind"],
        "title": title,
        **{table: list(data.get(table, [])) for table in TABLES},
    }
    editor, preview = st.columns([1.45, 1])
    with editor:
        section_title("Model inputs", "Edit one category at a time")
        category = st.segmented_control(
            "Model category",
            list(categories),
            default="Geometry",
            key=f"model_category_{revision}",
            width="stretch",
        )
        for table in categories[category or "Geometry"]:
            st.markdown("#### " + table.replace("_", " ").title())
            st.markdown(term_html(TABLE_TERMS[table]), unsafe_allow_html=True)
            frame = pd.DataFrame(data.get(table, []), columns=TABLES[table])
            for col in frame.columns:
                if col in (
                    "id",
                    "start",
                    "end",
                    "material",
                    "section",
                    "node",
                    "element",
                    "dof",
                    "case",
                ):
                    frame[col] = frame[col].astype("string")
                else:
                    frame[col] = frame[col].astype("float64")
            edited = st.data_editor(
                frame,
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                key=f"table_{table}_{revision}",
                column_config=editor_columns(table, units, DOFS[data["kind"]]),
            )
            candidate[table] = [
                {k: v for k, v in row.items() if v is not None}
                for row in edited.astype(object)
                .where(pd.notna(edited), None)
                .to_dict(orient="records")
                if any(v is not None for v in row.values())
            ]
            headings = {
                key: config.get("label", key)
                for key, config in editor_columns(table, units, DOFS[data["kind"]]).items()
            }
            readable_table(
                edited.rename(columns=headings),
                "Model " + table.replace("_", " ") + " (" + units + ")",
            )
        if category == "Supports":
            term_key("fixed", "pin", "roller", "prescribed")
            explain(
                "Add one row for every movement that a support prevents. A spring resists movement instead of fixing it."
            )
        if category == "Loads":
            explain(
                "Nodal translations use forces. Nodal rotations use moments. Distributed loads follow the member's local axes."
            )
    if candidate != st.session_state.draft:
        st.session_state.draft = candidate
        invalidate()
    st.session_state.brief = asdict(
        ProblemBrief(
            question, scope, notes, brief.target_node, brief.target_member, brief.prediction
        )
    )
    model = None
    error = None
    try:
        model = model_from_dict(candidate)
    except (ModelError, ValueError) as exc:
        error = str(exc)
    with preview:
        section_title("Geometry preview", "No analysis runs here")
        with st.container(key="preview-panel"):
            if model:
                status_message(
                    "Input checks passed",
                    "The model can be inspected. Structural stability is checked only during Solve.",
                )
                with st.expander("Result focus", expanded=True):
                    node_options = [""] + [n.id for n in model.nodes]
                    member_options = [""] + [e.id for e in model.elements]
                    for key, options, label in [
                        ("target_node", node_options, "Node of interest"),
                        ("target_member", member_options, "Member of interest"),
                    ]:
                        widget_key = f"{key}_{revision}"
                        if st.session_state.get(widget_key) not in options:
                            saved = st.session_state.brief[key]
                            st.session_state[widget_key] = saved if saved in options else ""
                        st.session_state.brief[key] = st.selectbox(
                            label,
                            options,
                            key=widget_key,
                            format_func=lambda value: value or "No preference",
                        )
                case = case_control(model)
                figure = apply_plot_theme(
                    model_figure(model, case, units, st.session_state.brief["target_member"]), 350
                )
                st.plotly_chart(figure, width="stretch", config=PLOT_CONFIG)
                st.caption(
                    "Undeformed geometry. Triangles mark known movements; diamonds mark support springs."
                )
            else:
                status_message(
                    "Draft needs input changes",
                    error or "Complete the model tables to see its geometry.",
                    "warning",
                )
                empty_state(
                    "Preview waiting for a valid model",
                    "Your draft is still saved. Correct the named input and the preview will return.",
                    "◇",
                )

    with st.container(key="action-bar"):
        status_col, check_col, next_col = st.columns([1.4, 1, 1])
        status_col.caption(
            "Valid input · stability not checked" if model else "Draft saved · input changes needed"
        )
        if check_col.button("Save and check", type="primary", width="stretch"):
            if error:
                st.error("Draft saved, but input checks did not pass: " + error)
            else:
                st.success("Input checks passed. Stability and the solution have not been checked.")
        if next_col.button("Continue to Understand", disabled=model is None, width="stretch"):
            navigate("2 · Understand", "Inside FEM")

    if model:
        with st.expander("Export this draft"):
            st.download_button(
                "Download model JSON",
                json.dumps(model_to_dict(model, units), indent=2),
                "model.json",
                "application/json",
            )
            st.download_button(
                "Download learning project",
                json.dumps(project_to_dict(model, current_brief()), indent=2),
                "learning-project.json",
                "application/json",
            )
    try:
        draft_json = json.dumps(candidate, indent=2, allow_nan=False)
    except ValueError:
        st.warning(
            "The draft stays in this session. Replace nonfinite numbers before downloading JSON."
        )
    else:
        st.download_button(
            "Download draft JSON (may be incomplete)",
            draft_json,
            "draft.json",
            "application/json",
        )
    with st.expander("Does this problem need another method?"):
        explain(
            "This release has no plates, shells, solids, dynamics, buckling, nonlinear materials or member end releases. Use an appropriate solver for those behaviors. The learning notes explain possible next methods but do not calculate unsupported results."
        )


def inspect_assembly(model, trace, case, selected):
    em = next(e for e in trace.element_matrices if e.element.id == selected)
    material = next(m for m in model.materials if m.id == em.element.material)
    section = next(s for s in model.sections if s.id == em.element.section)
    properties = [
        ("Length", em.length, "m"),
        ("Direction cosine", em.cosine, "1"),
        ("Direction sine", em.sine, "1"),
        ("Young's modulus E", material.E, "Pa"),
    ]
    if model.kind != "beam":
        properties.extend([("Area A", section.A, "m²"), ("EA", em.EA, "N")])
    if model.kind in ("beam", "frame"):
        properties.extend([("Second moment of area I", section.I, "m⁴"), ("EI", em.EI, "N m²")])
    term_key("matrix", "transform", "assembly", "free", "rhs", "sparse")
    labels = [trace.labels[i] for i in em.indices]
    local_labels = {
        "bar": ["u1", "u2"],
        "truss": ["u1", "u2"],
        "beam": ["v1", "theta1", "v2", "theta2"],
        "frame": ["u1", "v1", "theta1", "u2", "v2", "theta2"],
    }[model.kind]
    summary, lab = st.columns([0.75, 1.75])
    with summary:
        st.markdown("#### Member " + selected)
        st.dataframe(
            pd.DataFrame(
                [
                    {"Property": name, "Value": f"{value:.6g}", "Unit": unit}
                    for name, value, unit in properties
                ]
            ),
            hide_index=True,
            width="stretch",
        )
        st.caption("Global DOF map: " + ", ".join(labels))
    with lab:
        view = st.segmented_control(
            "Matrix laboratory",
            ["Element", "Transformation", "Assembly", "Boundary system"],
            default="Element",
            width="stretch",
            key="matrix_lab_" + selected,
        )
        if view == "Element":
            explain(
                "This matrix connects the member-end movements to the member-end forces in local directions."
            )
            st.latex(r"f_e=k_eu_e")
            frame = pd.DataFrame(em.local, index=local_labels, columns=local_labels)
            st.dataframe(frame, width="stretch")
            readable_table(frame, "Local stiffness", True)
        elif view == "Transformation":
            explain(
                "The transformation connects local member directions to the shared global directions."
            )
            st.latex(r"K_e=T^{\mathsf T}k_eT")
            frame = pd.DataFrame(em.transform, index=local_labels, columns=labels)
            st.dataframe(frame, width="stretch")
            readable_table(frame, "Coordinate transformation", True)
        elif view == "Assembly":
            explain("Assembly adds every member contribution at the matching structure movements.")
            contribution = pd.DataFrame(em.global_matrix, index=labels, columns=labels)
            with st.expander("Selected member contribution"):
                st.dataframe(contribution, width="stretch")
            stiffness = trace.stiffness
            if len(trace.labels) <= 120:
                figure = go.Figure(
                    go.Heatmap(
                        z=stiffness.toarray(),
                        x=trace.labels,
                        y=trace.labels,
                        colorscale="RdBu",
                        zmid=0,
                        colorbar=dict(title="Raw SI"),
                        hovertemplate="Row %{y}<br>Column %{x}<br>Coefficient %{z}<extra></extra>",
                    )
                )
            else:
                coo = stiffness.tocoo()
                figure = go.Figure(
                    go.Scattergl(
                        x=coo.col,
                        y=coo.row,
                        mode="markers",
                        marker=dict(size=3, color="#246bfe"),
                        hovertemplate="Nonzero entry<br>Column %{x}<br>Row %{y}<extra></extra>",
                    )
                )
            apply_plot_theme(figure, 380)
            figure.update_yaxes(autorange="reversed")
            st.plotly_chart(figure, width="stretch", config=PLOT_CONFIG)
            entries = stiffness.tocoo()
            readable_table(
                pd.DataFrame(
                    {
                        "Row DOF": [trace.labels[i] for i in entries.row],
                        "Column DOF": [trace.labels[i] for i in entries.col],
                        "Stiffness coefficient (raw SI)": entries.data,
                    }
                ),
                "Nonzero global stiffness entries",
            )
        else:
            explain(
                "Known support movements are separated from the movements that the solver must find."
            )
            st.latex(r"K_{ff}u_f=F_f-K_{fc}u_c")
            free, fixed = trace.free, list(trace.prescribed)
            prescribed = np.array(list(trace.prescribed.values()))
            rhs = trace.loads[case][free] - trace.stiffness[free][:, fixed] @ prescribed
            reduced_labels = [trace.labels[i] for i in free]
            if len(free) <= 120:
                frame = pd.DataFrame(
                    trace.stiffness[free][:, free].toarray(),
                    index=reduced_labels,
                    columns=reduced_labels,
                )
                st.dataframe(frame, width="stretch")
                readable_table(frame, "Reduced stiffness", True)
            right_side = pd.DataFrame(
                {
                    "Free DOF": reduced_labels,
                    "Known right-hand side": rhs,
                    "Unit": ["N m" if label.endswith(":rz") else "N" for label in reduced_labels],
                }
            )
            st.dataframe(right_side, hide_index=True, width="stretch")
            readable_table(right_side, "Known right-hand side and units")
            st.caption("The unknown movements are still blank. Stage 3 performs the solve.")


def understand_view():
    page_header(
        "Understand the method",
        "Follow the calculation from physical assumptions to checks. Open details only when you need them.",
        "STAGE 2 OF 3 · UNDERSTAND",
    )
    model = get_model()
    if model is None:
        return
    badges(
        [
            (model.kind.title(), "blue"),
            (st.session_state.draft["units"], ""),
            ("Not solved", "amber"),
        ]
    )
    st.write("**Engineering question:** " + current_brief().question)
    case = case_control(model)
    try:
        trace = assemble(model)
        guide = build_guide(model, current_brief(), case, trace)
    except ModelError as exc:
        st.error(str(exc))
        return
    metric_cards(
        [
            ("Nodes", str(len(model.nodes)), "Geometry points"),
            ("Members", str(len(model.elements)), model.kind.title()),
            ("DOFs", str(len(trace.labels)), "Before restraints"),
            ("Known movements", str(len(trace.prescribed)), "Supports and prescribed values"),
        ],
        "Model summary",
    )
    explain(guide.introduction)
    section_title("Eight-step method map", "Select a step below for the reasoning")
    step_map([title for title, _ in guide.steps])
    for title, body in guide.steps:
        with st.expander(title):
            explain(body)
            if title.startswith("2."):
                for note in guide.support_notes:
                    explain(note)
    section_title("Choose a suitable method", "A good calculation begins with a suitable model")
    method_columns = st.columns(min(3, max(1, len(guide.methods))))
    for index, (title, body) in enumerate(guide.methods):
        with method_columns[index % len(method_columns)]:
            with st.container(border=True):
                st.markdown("#### " + title)
                explain(body)
    with st.expander("Matching analytical check"):
        if guide.hand_check:
            explain(str(guide.hand_check["scope"]))
            st.code(guide.hand_check["formula"], language=None)
            st.write(f"{guide.hand_check['label']} = {guide.hand_check['value']:.6g} m")
        else:
            explain(
                "No built-in formula matches this exact model. The app will not use an unrelated textbook answer."
            )
    section_title("Make a prediction", "Optional, but useful for checking physical sense")
    with st.container(border=True):
        st.session_state.brief["prediction"] = st.text_area(
            "What movement or change do you expect, and why?",
            current_brief().prediction,
            key=f"prediction_{st.session_state.revision}",
        )
    selected = member_control(model)
    figure = apply_plot_theme(model_figure(model, case, selected=selected), 380)
    st.plotly_chart(figure, width="stretch", config=PLOT_CONFIG)
    section_title("Matrix laboratory", "Actual values from the selected member and model")
    inspect_assembly(model, trace, case, selected)
    if st.button("Continue to Solve", type="primary"):
        navigate("3 · Solve and discuss", "Results")


def comparison_controls(model, result):
    with st.expander("Change one thing and compare"):
        explain(
            "Keep the current result as the baseline. Change one setting and compare movements. Shared material or section properties affect every member using that ID. The baseline is never edited."
        )
        choices = (
            ["load_factor", "E"]
            + (["A"] if model.kind != "beam" else [])
            + (["I"] if model.kind in ("beam", "frame") else [])
        )
        if model.constraints:
            choices += ["constraint_value", "release"]
        if model.springs:
            choices += ["spring"]
        names = {
            "load_factor": "Applied-load multiplier",
            "E": "Material E",
            "A": "Section area A",
            "I": "Section property I",
            "constraint_value": "One known support movement",
            "release": "Release one held movement",
            "spring": "One support spring stiffness",
        }
        kind = st.selectbox("Change to investigate", choices, format_func=lambda v: names[v])
        target, old = "", 1.0
        if kind in ("E", "A", "I"):
            items = model.materials if kind == "E" else model.sections
            target = st.selectbox("Property owner", [item.id for item in items])
            old = getattr(next(item for item in items if item.id == target), kind)
        elif kind in ("constraint_value", "release", "spring"):
            supports = model.springs if kind == "spring" else model.constraints
            target = st.selectbox("Support movement", [f"{s.node}:{s.dof}" for s in supports])
            item = next(s for s in supports if f"{s.node}:{s.dof}" == target)
            old = item.stiffness if kind == "spring" else item.value
        unit = {
            "load_factor": "dimensionless",
            "E": "Pa",
            "A": "m²",
            "I": "m⁴",
            "constraint_value": "rad" if target.endswith(":rz") else "m",
            "spring": "N m/rad" if target.endswith(":rz") else "N/m",
            "release": "no value",
        }[kind]
        value = st.number_input(
            "New value (" + unit + ")",
            value=float(2 * old if kind in ("load_factor", "E", "A", "I", "spring") else old),
            format="%.6g",
            key=f"change_{fingerprint(model, result.case)}_{kind}_{target}",
            disabled=kind == "release",
        )
        if st.button("Run comparison"):
            try:
                changed_model, description = apply_change(
                    model, result.case, Change(kind, target, value)
                )
                try:
                    changed_result = solve_linear(changed_model, SolveOptions(case=result.case))
                    st.session_state.comparison = compare_results(
                        model, result, changed_result, description
                    )
                except ModelError as exc:
                    st.session_state.comparison = Comparison(
                        description, fingerprint(model, result.case), error=str(exc)
                    )
            except ModelError as exc:
                st.session_state.comparison = Comparison(
                    f"Requested {names[kind]} for {target}: {value:g} {unit}",
                    fingerprint(model, result.case),
                    error=str(exc),
                )
        comparison = st.session_state.get("comparison")
        if comparison and comparison.baseline_fingerprint == fingerprint(model, result.case):
            st.caption("Last completed comparison. Press Run comparison to apply new settings.")
            explain(comparison.description)
            if comparison.error:
                st.error("Comparison did not solve: " + comparison.error)
                explain(
                    "The baseline is unchanged. A released support may leave a mechanism; this is a useful modeling finding, not a reason to add artificial stiffness."
                )
            else:
                st.dataframe(pd.DataFrame(comparison.rows), hide_index=True)
                readable_table(pd.DataFrame(comparison.rows), "Comparison movements")
                explain(
                    "Compare the directions and differences with your prediction. Proportional load scaling is expected only when all other driving terms, including prescribed support movements, permit it. Near-zero baseline values should be compared by absolute difference."
                )
        return comparison


def solve_view():
    page_header(
        "Solve and discuss",
        "Run the checked model, inspect the response, test the equations, and state what the result cannot prove.",
        "STAGE 3 OF 3 · SOLVE",
    )
    model = get_model()
    if model is None:
        return
    st.write("**Engineering question:** " + current_brief().question)
    case = case_control(model)
    stamp = fingerprint(model, case)
    solution_state = st.session_state.get("solution")
    if solution_state is not None and solution_state[0] != stamp:
        invalidate()
    try:
        check_brief(current_brief(), model)
    except ModelError as exc:
        st.error(str(exc))
        return
    if "solution" not in st.session_state and "solve_error" not in st.session_state:
        badges(
            [
                (model.kind.title(), "blue"),
                (st.session_state.draft["units"], ""),
                (case, ""),
                ("Ready", "green"),
            ]
        )
        metric_cards(
            [
                ("Nodes", str(len(model.nodes)), "Geometry points"),
                ("Members", str(len(model.elements)), model.kind.title()),
                ("Load case", case, "Selected for this solve"),
                ("State", "Not solved", "No result is being reused"),
            ],
            "Model ready to solve",
        )
        empty_state(
            "Ready when you are",
            "The engine will assemble the equations, apply the known movements, solve the unknown movements, and recover forces and reactions.",
            "▶",
        )
    if "solution" not in st.session_state:
        if st.button("Solve model", type="primary", width="stretch"):
            invalidate()
            try:
                st.session_state.solution = (stamp, solve_linear(model, SolveOptions(case=case)))
            except ModelError as exc:
                st.session_state.solve_error = str(exc)
            st.rerun()
    if "solve_error" in st.session_state:
        status_message(
            "The model did not solve",
            st.session_state.solve_error,
            "error",
        )
        explain(
            "Check the units, connected nodes and real supports. A mechanism has a movement that the model cannot resist. The engine did not add artificial stiffness."
        )
        if st.button("Return to Define"):
            navigate("1 · Define", "Model")
        return
    if "solution" not in st.session_state:
        return
    result = st.session_state.solution[1]
    badges([(model.kind.title(), "blue"), (case, ""), ("Solved", "green")])
    toolbar = st.columns(4)
    toolbar[0].text_input("Model", model.title, disabled=True)
    toolbar[1].text_input("Case", result.case, disabled=True)
    selected = member_control(model)
    member = result.members[selected]
    with toolbar[2]:
        st.text_input("Selected member", selected, disabled=True)
    with toolbar[3]:
        display_units = st.selectbox("Display units", list(UNITS), index=1, help=help_text("si"))
    unit, factor = ("m", 1) if display_units == "N-m-Pa" else ("mm", 1000)
    translational = [i for i, label in enumerate(result.labels) if not label.endswith(":rz")]
    metric_cards(
        [
            (
                "Peak nodal translation",
                f"{max(abs(result.displacements[translational])) * factor:.8g} {unit}",
                "Largest absolute translation component",
            ),
            ("Degrees of freedom", str(len(result.labels)), "Solved structure movements"),
            (
                "Strain energy",
                f"{result.diagnostics['strain_energy_J']:.8g} J",
                "Elastic energy stored by the model",
            ),
            (
                "Scaled residual",
                f"{result.diagnostics['scaled_backward_error']:.6e}",
                "Equation imbalance after scaling",
            ),
        ],
        "Primary results",
    )
    term_key(
        "translation",
        "dof",
        "energy",
        "residual",
        "reaction",
        "magnification",
        "stress",
        "axial",
        "shear",
        "moment",
        "sagging",
        "fiber",
    )
    figure_controls = st.columns([1, 1, 2])
    with figure_controls[0]:
        magnification = st.slider(
            "Deformation magnification", 0, 500, 50, 5, help=help_text("magnification")
        )
    with figure_controls[1]:
        color = st.selectbox(
            "Color field", ["Deformed shape", "Normal stress"], help=help_text("stress")
        )
    with figure_controls[2]:
        st.caption(
            "Dotted geometry is the original shape. Equal axis scales preserve structural proportions."
        )
    fig = apply_plot_theme(
        structure_figure(model, result, magnification, selected, color, display_units), 470
    )
    st.plotly_chart(fig, width="stretch", key="structure", config=PLOT_CONFIG)
    st.caption(
        f"Deformed geometry ×{magnification}. Tension is positive. Stress color is a line-element result, not a continuum stress contour."
    )
    quantities = (
        ["axial_force", "axial_stress"]
        if model.kind in ("bar", "truss")
        else ["axial_force", "shear", "moment", "transverse_displacement", "axial_stress"]
    )
    if "stress_top" in member:
        quantities += ["stress_top", "stress_bottom"]
    quantity = st.selectbox(
        "Member diagram",
        quantities,
        index=2 if model.kind in ("beam", "frame") else 0,
        format_func=lambda name: member_quantity(name, display_units)[0],
    )
    section_title("Selected-member insight", "Member " + selected)
    insight, diagram = st.columns([0.72, 1.5])
    with insight:
        sampled = np.asarray(member[quantity])
        quantity_title, quantity_unit, quantity_factor = member_quantity(quantity, display_units)
        metric_cards(
            [
                ("Minimum", f"{sampled.min() * quantity_factor:.7g}", quantity_unit),
                ("Maximum", f"{sampled.max() * quantity_factor:.7g}", quantity_unit),
            ],
            "Selected-member sampled range",
        )
        st.caption(
            "These values are sampled along the member. They are not claimed as exact interior extrema."
        )
    with diagram:
        member_fig = apply_plot_theme(member_figure(member, quantity, display_units), 340)
        st.plotly_chart(member_fig, width="stretch", config=PLOT_CONFIG)

    sampled_rows = [row for row in member_summary(model, result) if row["Member"] == selected]
    brief = current_brief()
    # Inspection selection controls which member is discussed; saved learning target stays unchanged.
    discussion_brief = ProblemBrief(**(asdict(brief) | {"target_member": selected}))
    discussion = discuss(model, result, discussion_brief)
    check_table = pd.DataFrame(
        [
            {
                "Check": v.name,
                "Imbalance": v.imbalance,
                "Tolerance": v.tolerance,
                "Unit": v.unit,
                "Outcome": "Passed" if v.passed else "Failed",
            }
            for v in discussion.checks
        ]
    )
    table = pd.read_csv(io.StringIO(results_csv(result, display_units)))
    movements = table[["degree_of_freedom", "displacement", "displacement_unit"]]
    reactions = table[
        ["degree_of_freedom", "constraint_reaction", "spring_reaction", "reaction_unit"]
    ]
    result_tabs = st.tabs(["Movements", "Reactions", "Member results", "Checks"])
    with result_tabs[0]:
        st.dataframe(movements, hide_index=True, width="stretch")
        readable_table(movements, "Node movements")
    with result_tabs[1]:
        st.dataframe(reactions, hide_index=True, width="stretch")
        readable_table(reactions, "Support and spring reactions")
    with result_tabs[2]:
        member_frame = pd.DataFrame(sampled_rows)
        st.dataframe(member_frame, hide_index=True, width="stretch")
        readable_table(member_frame, "Selected member sampled ranges (SI)")
    with result_tabs[3]:
        term_key("equilibrium", "energy", "eigenvalue", "conditioning")
        st.dataframe(check_table, hide_index=True, width="stretch")
        readable_table(check_table, "Force, moment and energy checks")
        meanings = {
            "dofs": help_text("dof"),
            "free_dofs": help_text("free"),
            "smallest_scaled_eigenvalue": help_text("eigenvalue"),
            "scaled_backward_error": help_text("residual"),
            "strain_energy_J": help_text("energy"),
            "constraint_work_term_J": "Work from prescribed support movements in the energy identity.",
        }
        with st.expander("Numerical diagnostics"):
            st.table(
                pd.DataFrame(
                    [
                        {
                            "Quantity": key.replace("_", " "),
                            "Value": str(value),
                            "Meaning": meanings.get(key, "See the numerical methods guide."),
                        }
                        for key, value in result.diagnostics.items()
                    ]
                )
            )

    section_title("Discuss the result", "Meanings, checks and limits are kept separate")
    interpretation, calculation, limits = st.columns(3)
    with interpretation:
        with st.container(border=True):
            st.markdown("#### Interpretation")
            if brief.prediction:
                st.write("**Your prediction:** " + brief.prediction)
            for observation in discussion.observations:
                explain(observation)
    with calculation:
        with st.container(border=True):
            st.markdown("#### Calculation checks")
            if all(value.passed for value in discussion.checks):
                status_message(
                    "Equation checks passed",
                    "The reported force, moment and energy imbalances are within their tolerances.",
                )
            else:
                status_message(
                    "A calculation check failed",
                    "Investigate the model and calculation before using this result.",
                    "error",
                )
            explain(
                "A small residual checks the equations. It does not prove that the model represents the real structure."
            )
            for note in result.warnings:
                st.warning(note)
    with limits:
        with st.container(border=True):
            st.markdown("#### Limits and next steps")
            for note in discussion.limitations + discussion.next_steps:
                explain(note)

    section_title("Change one thing and compare", "The solved baseline remains unchanged")
    comparison = comparison_controls(model, result)
    with st.expander("Save this calculation and explanation"):
        st.download_button(
            "Results JSON",
            json.dumps(result_dict(model, result), indent=2, allow_nan=False),
            "results.json",
            "application/json",
        )
        st.download_button("Nodal CSV", results_csv(result, display_units), "nodes.csv", "text/csv")
        st.download_button(
            "Learning project JSON",
            json.dumps(project_to_dict(model, brief), indent=2),
            "learning-project.json",
            "application/json",
        )
        report = learning_report(
            model,
            result,
            brief,
            build_guide(model, brief, case, result.trace),
            discussion,
            comparison,
            fig.to_html(full_html=False, include_plotlyjs=True),
        )
        st.download_button("Learning report HTML", report, "learning-report.html", "text/html")
        st.download_button(
            "Interactive figure HTML",
            fig.to_html(include_plotlyjs=True),
            "structure.html",
            "text/html",
        )
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        exportfig, axis = plt.subplots(figsize=(7, 4), layout="constrained")
        title, quantity_unit, quantity_factor = member_quantity(quantity, display_units)
        axis.plot(member["x"] * factor, member[quantity] * quantity_factor, color="#2563EB")
        axis.set(
            xlabel=f"Local distance ({unit})",
            ylabel=f"{title} ({quantity_unit})",
            title=f"Member {selected}",
        )
        buffer = io.BytesIO()
        exportfig.savefig(buffer, format="png", dpi=180)
        plt.close(exportfig)
        st.download_button("Member figure PNG", buffer.getvalue(), "member.png", "image/png")
