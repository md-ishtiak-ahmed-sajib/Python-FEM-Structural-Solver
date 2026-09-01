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
    st.title("1. Define your structural problem.")
    explain(
        "Start with a question, then describe the geometry, supports and loads. Edits stay in your session, including incomplete drafts. Download a file to keep work after closing the app."
    )
    data = st.session_state.editor_base
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
    data = st.session_state.editor_base
    revision = st.session_state.revision
    units = data["units"]
    brief = current_brief()
    with st.expander("What do you want to learn?", expanded=True):
        question = st.text_input(
            "Your engineering question", brief.question, key=f"question_{revision}"
        )
        scope = st.selectbox(
            "Model extent",
            ["Whole structure", "Selected portion"],
            index=0 if brief.scope == "Whole structure" else 1,
            key=f"scope_{revision}",
        )
        notes = st.text_area(
            "For a selected portion: explain the cut-boundary forces and restraints",
            brief.boundary_notes,
            key=f"boundary_{revision}",
            help="Describe what the removed part does to this portion. Do not assume a cut is fixed.",
        )
        if scope == "Selected portion" and not notes.strip():
            st.warning(
                "Add cut-boundary notes before moving to theory or solving. We will not invent the missing boundary conditions."
            )
    title = st.text_input(
        "Model title", data.get("title", "My structural problem"), key=f"title_{revision}"
    )
    explain(FAMILY[data["kind"]])
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
    tabs = st.tabs(["Geometry", "Material and section", "Supports", "Loads"])
    layout = {
        "nodes": 0,
        "elements": 0,
        "materials": 1,
        "sections": 1,
        "constraints": 2,
        "springs": 2,
        "loads": 3,
        "distributed_loads": 3,
    }
    candidate = {"schema_version": 1, "units": units, "kind": data["kind"], "title": title}
    for table, tab in layout.items():
        with tabs[tab]:
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
    with tabs[2]:
        term_key("fixed", "pin", "roller", "prescribed")
        explain(
            "Enter one constraint row for each held movement. A frame fixed support holds ux, uy and rz; a pin holds ux and uy; an axis-aligned roller holds one translation. A beam has only uy and rz. Springs supply resistance rather than prescribing a movement."
        )
    with tabs[3]:
        explain(
            "Use N for translational nodal forces. A load at rz is a moment in N times the selected length unit. Distributed loads use the member's local directions. Use separate case names for independent loading conditions."
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
    if st.button("Save and check model", type="primary"):
        if error:
            st.error("Draft saved in this session, but input checks did not pass: " + error)
        else:
            st.success(
                "Input checks passed. The draft is saved in this session. Stability and the solution have not been checked."
            )
    if model:
        left, right = st.columns(2)
        node_options = [""] + [n.id for n in model.nodes]
        member_options = [""] + [e.id for e in model.elements]
        for key, options, container, label in [
            ("target_node", node_options, left, "Node of interest"),
            ("target_member", member_options, right, "Member of interest"),
        ]:
            widget_key = f"{key}_{revision}"
            if st.session_state.get(widget_key) not in options:
                st.session_state[widget_key] = (
                    st.session_state.brief[key] if st.session_state.brief[key] in options else ""
                )
            value = container.selectbox(
                label, options, key=widget_key, format_func=lambda v: v or "No preference"
            )
            st.session_state.brief[key] = value
        case = case_control(model)
        st.plotly_chart(
            model_figure(model, case, units, st.session_state.brief["target_member"]),
            width="stretch",
        )
        explain(
            "Undeformed geometry only; no solve has run. Axes use equal scales. Triangles mark prescribed movements; diamonds mark springs. Hover supports to see exactly what is held."
        )
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
    else:
        st.info("Complete the tables to preview the geometry. " + (error or ""))
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
    with st.expander("Does your problem need another method?"):
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
    term_key(
        "E",
        "A",
        "I",
        "EA",
        "EI",
        "local",
        "global",
        "cosine",
        "sine",
        "transform",
        "assembly",
        "free",
        "rhs",
        "sparse",
    )
    left, right = st.columns([1, 1.2])
    with left:
        st.subheader("Selected member: " + selected)
        st.table(
            pd.DataFrame(
                [
                    {"Property": name, "Value": f"{value:.6g}", "Unit": unit}
                    for name, value, unit in properties
                ]
            )
        )
        labels = [trace.labels[i] for i in em.indices]
        st.caption("Global DOF map: " + ", ".join(labels))
        local_labels = {
            "bar": ["u1", "u2"],
            "truss": ["u1", "u2"],
            "beam": ["v1", "theta1", "v2", "theta2"],
            "frame": ["u1", "v1", "theta1", "u2", "v2", "theta2"],
        }[model.kind]
        explain(
            "Local u is axial movement, v is transverse movement and theta is rotation. Subscripts 1 and 2 refer to the start and end nodes."
        )
        st.markdown(term_html("matrix", "Local stiffness kₑ"), unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame(em.local, index=local_labels, columns=local_labels), width="stretch"
        )
        readable_table(
            pd.DataFrame(em.local, index=local_labels, columns=local_labels),
            "Local stiffness",
            True,
        )
        st.markdown(term_html("transform", "Coordinate transformation T"), unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame(em.transform, index=local_labels, columns=labels), width="stretch"
        )
        readable_table(
            pd.DataFrame(em.transform, index=local_labels, columns=labels),
            "Coordinate transformation",
            True,
        )
        st.latex(r"K_e=T^{\mathsf T}k_eT")
        with st.expander("Selected element's contribution to global assembly"):
            st.dataframe(pd.DataFrame(em.global_matrix, index=labels, columns=labels))
            readable_table(
                pd.DataFrame(em.global_matrix, index=labels, columns=labels),
                "Element assembly contribution",
                True,
            )
    with right:
        st.subheader("Global stiffness")
        K = trace.stiffness
        if len(trace.labels) <= 120:
            fig = go.Figure(
                go.Heatmap(
                    z=K.toarray(),
                    x=trace.labels,
                    y=trace.labels,
                    colorscale="RdBu",
                    zmid=0,
                    colorbar=dict(title="Raw SI"),
                    hovertemplate="Row %{y}<br>Column %{x}<br>Stiffness coefficient %{z}<extra></extra>",
                )
            )
        else:
            coo = K.tocoo()
            fig = go.Figure(
                go.Scattergl(
                    x=coo.col,
                    y=coo.row,
                    mode="markers",
                    marker=dict(size=2, color="#2563eb"),
                    hovertemplate="Nonzero entry<br>Column %{x}<br>Row %{y}<extra></extra>",
                )
            )
        fig.update_layout(height=400, yaxis=dict(autorange="reversed"), template="plotly_white")
        st.plotly_chart(fig, width="stretch")
        entries = K.tocoo()
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
        explain(
            "Small systems show all entries; larger systems show only nonzero positions. Translations use metres and rotations use radians, so raw matrix entries have different units. The solver scales equations for its numerical checks."
        )
    st.latex(r"K_{ff}u_f=F_f-K_{fc}u_c")
    free, fixed = trace.free, list(trace.prescribed)
    rhs = trace.loads[case][free] - trace.stiffness[free][:, fixed] @ np.array(
        list(trace.prescribed.values())
    )
    if len(free) <= 120:
        with st.expander("Reduced stiffness Kff"):
            labels = [trace.labels[i] for i in free]
            st.dataframe(
                pd.DataFrame(trace.stiffness[free][:, free].toarray(), index=labels, columns=labels)
            )
            readable_table(
                pd.DataFrame(
                    trace.stiffness[free][:, free].toarray(), index=labels, columns=labels
                ),
                "Reduced stiffness",
                True,
            )
    right_side = pd.DataFrame(
        {
            "Free DOF": [trace.labels[i] for i in free],
            "Known right-hand side": rhs,
            "Unit": ["N m" if trace.labels[i].endswith(":rz") else "N" for i in free],
        }
    )
    st.dataframe(
        right_side,
        hide_index=True,
        column_config={
            "Free DOF": st.column_config.TextColumn(help=help_text("free")),
            "Known right-hand side": st.column_config.NumberColumn(help=help_text("rhs")),
        },
    )
    readable_table(right_side, "Known right-hand side and units")
    explain(
        "The unknown movements have not been filled in. Stage 3 performs the solve. A complete assembled matrix can still describe an unstable structure."
    )


def understand_view():
    st.title("2. Understand the method.")
    model = get_model()
    if model is None:
        return
    st.write("Your question: " + current_brief().question)
    case = case_control(model)
    try:
        trace = assemble(model)
        guide = build_guide(model, current_brief(), case, trace)
    except ModelError as exc:
        st.error(str(exc))
        return
    explain(guide.introduction)
    for title, body in guide.steps:
        st.subheader(title)
        explain(body)
        if title.startswith("2."):
            for note in guide.support_notes:
                explain(note)
    with st.expander("Choose methods and avoid common mistakes", expanded=False):
        for title, body in guide.methods:
            st.subheader(title)
            explain(body)
    with st.expander("A matching hand check"):
        if guide.hand_check:
            explain(str(guide.hand_check["scope"]))
            st.code(guide.hand_check["formula"], language=None)
            st.write(f"{guide.hand_check['label']} = {guide.hand_check['value']:.6g} m")
        else:
            explain(
                "No built-in analytical formula matches this exact model. Use equilibrium, the inspected equations and appropriate independent comparisons. The app will not apply a cantilever formula to a different structure."
            )
    st.session_state.brief["prediction"] = st.text_area(
        "Optional prediction: what movement or change do you expect, and why?",
        current_brief().prediction,
        key=f"prediction_{st.session_state.revision}",
    )
    selected = member_control(model)
    st.plotly_chart(model_figure(model, case, selected=selected), width="stretch")
    with st.expander("Inside FEM: actual matrices and equations", expanded=True):
        inspect_assembly(model, trace, case, selected)


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
    st.title("3. Solve and discuss.")
    model = get_model()
    if model is None:
        return
    st.write("Your question: " + current_brief().question)
    case = case_control(model)
    stamp = fingerprint(model, case)
    if st.session_state.get("solution", (None,))[0] != stamp:
        invalidate()
    try:
        check_brief(current_brief(), model)
    except ModelError as exc:
        st.error(str(exc))
        return
    if st.button("Solve", type="primary"):
        invalidate()
        try:
            st.session_state.solution = (stamp, solve_linear(model, SolveOptions(case=case)))
        except ModelError as exc:
            st.session_state.solve_error = str(exc)
    if "solve_error" in st.session_state:
        st.error(st.session_state.solve_error)
        explain(
            "Check the units, connected nodes and real support restraints. A mechanism has a movement the model cannot resist. No artificial stabilization was applied."
        )
        return
    if "solution" not in st.session_state:
        explain(
            "Press Solve when you are ready. No previous model's results are shown. You can visit Understand first or solve directly."
        )
        return
    result = st.session_state.solution[1]
    selected = member_control(model)
    member = result.members[selected]
    display_units = st.selectbox("Result display units", list(UNITS), index=1, help=help_text("si"))
    unit, factor = ("m", 1) if display_units == "N-m-Pa" else ("mm", 1000)
    translational = [i for i, label in enumerate(result.labels) if not label.endswith(":rz")]
    a, b, c, d = st.columns(4)
    a.metric(
        "Peak nodal translation",
        f"{max(abs(result.displacements[translational])) * factor:.5g} {unit}",
        help="Largest absolute translation component at a node, not vector magnitude.",
    )
    b.metric("Degrees of freedom", str(len(result.labels)), help=help_text("dof"))
    c.metric(
        "Strain energy", f"{result.diagnostics['strain_energy_J']:.4g} J", help=help_text("energy")
    )
    d.metric(
        "Scaled residual",
        f"{result.diagnostics['scaled_backward_error']:.1e}",
        help=help_text("residual"),
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
    magnification = st.slider(
        "Deformation magnification", 0, 500, 50, 5, help=help_text("magnification")
    )
    color = st.selectbox(
        "Color field", ["Deformed shape", "Normal stress"], help=help_text("stress")
    )
    fig = structure_figure(model, result, magnification, selected, color, display_units)
    st.plotly_chart(fig, width="stretch", key="structure")
    explain(
        f"Deformed geometry ×{magnification}. Dotted lines show original geometry; axes have equal scales. Stress coloring uses top fiber stress when c is supplied, otherwise axial stress only. Tension is positive. The drawing is not a continuum stress contour."
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
    left, right = st.columns(2)
    with left:
        st.plotly_chart(member_figure(member, quantity, display_units), width="stretch")
    with right:
        st.subheader("Node movements and support reactions")
        table = pd.read_csv(io.StringIO(results_csv(result, display_units)))
        st.dataframe(
            table,
            hide_index=True,
            column_config={
                "degree_of_freedom": st.column_config.TextColumn(help=help_text("dof")),
                "displacement": st.column_config.NumberColumn(help=help_text("displacement")),
                "constraint_reaction": st.column_config.NumberColumn(help=help_text("reaction")),
                "spring_reaction": st.column_config.NumberColumn(help=help_text("spring")),
            },
        )
        readable_table(table, "Node movements and reactions")
    sampled_rows = [row for row in member_summary(model, result) if row["Member"] == selected]
    readable_table(pd.DataFrame(sampled_rows), "Selected member sampled ranges (SI)")
    brief = current_brief()
    # Inspection selection controls which member is discussed; saved learning target stays unchanged.
    discussion_brief = ProblemBrief(**(asdict(brief) | {"target_member": selected}))
    discussion = discuss(model, result, discussion_brief)
    st.subheader("What the result means")
    if brief.prediction:
        st.write("Your prediction: " + brief.prediction)
    explain(
        "The discussion below uses SI so its values can be compared directly with the equations. Plot and table display units are shown separately."
    )
    for observation in discussion.observations:
        explain(observation)
    st.subheader("Check the calculation")
    term_key("equilibrium", "energy", "eigenvalue", "conditioning")
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
    st.dataframe(check_table, hide_index=True)
    readable_table(check_table, "Force, moment and energy checks")
    if any(not v.passed for v in discussion.checks):
        st.error(
            "A balance check failed. Do not use these results without investigating the model and calculation."
        )
    for note in result.warnings:
        st.warning(note)
    with st.expander("Numerical diagnostics"):
        meanings = {
            "dofs": help_text("dof"),
            "free_dofs": help_text("free"),
            "smallest_scaled_eigenvalue": help_text("eigenvalue"),
            "scaled_backward_error": help_text("residual"),
            "strain_energy_J": help_text("energy"),
            "constraint_work_term_J": "Work term from prescribed support movements; included in the energy identity.",
        }
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
    st.subheader("Limitations and next investigations")
    for note in discussion.limitations + discussion.next_steps:
        explain(note)
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
