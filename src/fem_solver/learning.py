"""Deterministic teaching rules; independent of Streamlit, Plotly and network services."""

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from html import escape
from typing import Any

import numpy as np

from . import __version__
from .export import html_table
from .model import Model, ModelError, model_from_dict, model_to_dict
from .solver import AssemblyTrace, SolveResult, assemble
from .terms import TERMS


@dataclass(frozen=True)
class ProblemBrief:
    question: str = "Find the movements, support reactions and member forces."
    scope: str = "Whole structure"
    boundary_notes: str = ""
    target_node: str = ""
    target_member: str = ""
    prediction: str = ""


@dataclass(frozen=True)
class MethodGuide:
    introduction: str
    steps: list[tuple[str, str]]
    support_notes: list[str]
    methods: list[tuple[str, str]]
    hand_check: dict[str, str | float] | None


@dataclass(frozen=True)
class BalanceCheck:
    name: str
    imbalance: float
    tolerance: float
    unit: str

    @property
    def passed(self) -> bool:
        return abs(self.imbalance) <= self.tolerance


@dataclass(frozen=True)
class Discussion:
    observations: list[str]
    checks: list[BalanceCheck]
    limitations: list[str]
    next_steps: list[str]


@dataclass(frozen=True)
class Change:
    kind: str  # load_factor, E, A, I, constraint_value, release, spring
    target: str = ""  # material/section ID, or node:DOF
    value: float = 1.0  # factor for loads; new SI value otherwise


@dataclass
class Comparison:
    description: str
    baseline_fingerprint: str
    rows: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


FAMILY = {
    "bar": "A bar carries axial force only. Its horizontal movement is ux; it has no bending stiffness.",
    "truss": "Truss members carry axial force only. Ideal joints rotate freely; loads act at nodes. The model does not represent joint bending.",
    "beam": "An Euler–Bernoulli beam bends in its plane. Its movements are uy and rz. Shear deformation and axial stretching are not part of this family.",
    "frame": "A frame member combines axial stretching and bending. Nodes have ux, uy and rz. Joints are rigid; member end releases are not supported.",
}
MOVEMENT = {
    "ux": "horizontal movement",
    "uy": "vertical movement",
    "rz": "counterclockwise rotation",
}


def fingerprint(model: Model, case: str) -> str:
    return hashlib.sha256(
        json.dumps({"model": model_to_dict(model), "case": case}, sort_keys=True).encode()
    ).hexdigest()


def check_brief(brief: ProblemBrief, model: Model, require_boundary: bool = True) -> None:
    if any(not isinstance(value, str) for value in asdict(brief).values()):
        raise ModelError("Problem brief fields must be text.")
    if brief.scope not in ("Whole structure", "Selected portion"):
        raise ModelError("Choose a whole structure or a selected portion.")
    if require_boundary and brief.scope == "Selected portion" and not brief.boundary_notes.strip():
        raise ModelError(
            "Describe the forces and restraints at the cut boundaries. A cut is not automatically fixed."
        )
    for label, value, valid in (
        ("node", brief.target_node, {n.id for n in model.nodes}),
        ("member", brief.target_member, {e.id for e in model.elements}),
    ):
        if value and value not in valid:
            raise ModelError(f"The target {label} {value!r} is not in this model. Select it again.")


def project_to_dict(model: Model, brief: ProblemBrief) -> dict:
    check_brief(brief, model, require_boundary=False)
    return {"learning_project_version": 1, "model": model_to_dict(model), "brief": asdict(brief)}


def project_from_dict(data: dict) -> tuple[Model, ProblemBrief]:
    if not isinstance(data, dict):
        raise ModelError("Import a model or learning project JSON object.")
    if "learning_project_version" not in data:
        return model_from_dict(data), ProblemBrief()
    if type(data["learning_project_version"]) is not int or data["learning_project_version"] != 1:
        raise ModelError("Expected learning_project_version: 1.")
    if set(data) != {"learning_project_version", "model", "brief"}:
        raise ModelError(
            "A learning project contains only its version, model and brief. Results must be recomputed."
        )
    try:
        model = model_from_dict(data["model"])
        brief = ProblemBrief(**data["brief"])
        check_brief(brief, model, require_boundary=False)
        return model, brief
    except TypeError as exc:
        raise ModelError(f"Invalid problem brief: {exc}") from exc


def blank_data(kind: str) -> dict:
    if kind not in FAMILY:
        raise ModelError("Choose bar, truss, beam or frame.")
    return {
        "schema_version": 1,
        "units": "N-m-Pa",
        "kind": kind,
        "title": "My structural problem",
        **{
            key: []
            for key in (
                "nodes",
                "elements",
                "materials",
                "sections",
                "constraints",
                "springs",
                "loads",
                "distributed_loads",
            )
        },
    }


def analytical_check(model: Model, case: str) -> dict[str, str | float] | None:
    """Conservative match: one horizontal, left-clamped bar/beam with end load and UDL."""
    if (
        model.kind not in ("bar", "beam")
        or len(model.elements) != 1
        or len(model.nodes) != 2
        or model.springs
    ):
        return None
    el = model.elements[0]
    nodes = {n.id: n for n in model.nodes}
    a, b = nodes[el.start], nodes[el.end]
    L = b.x - a.x
    if L <= 0 or a.y != b.y:
        return None
    expected = {(a.id, dof, 0.0) for dof in model.dofs}
    if {(c.node, c.dof, c.value) for c in model.constraints} != expected:
        return None
    dof = "ux" if model.kind == "bar" else "uy"
    loads = [v for v in model.loads if v.case == case]
    if any(v.node != b.id or v.dof != dof for v in loads):
        return None
    P = sum(v.value for v in loads)
    distributed = [v for v in model.distributed_loads if v.case == case]
    mat = next(m for m in model.materials if m.id == el.material)
    sec = next(s for s in model.sections if s.id == el.section)
    if model.kind == "bar":
        q = sum(v.qx for v in distributed)
        value = P * L / (mat.E * sec.A) + q * L**2 / (2 * mat.E * sec.A)
        formula = "u_tip = P L / (EA) + qx L² / (2 EA)"
    else:
        assert sec.I is not None
        q = sum(v.qy for v in distributed)
        value = P * L**3 / (3 * mat.E * sec.I) + q * L**4 / (8 * mat.E * sec.I)
        formula = "v_tip = P L³ / (3 EI) + qy L⁴ / (8 EI)"
    return {
        "label": f"{b.id}:{dof}",
        "value": value,
        "unit": "m",
        "formula": formula,
        "scope": "One constant-section horizontal member, fixed at the left end, with only an end force and/or uniform load. Signs follow global axes.",
    }


def build_guide(
    model: Model, brief: ProblemBrief, case: str, trace: AssemblyTrace | None = None
) -> MethodGuide:
    check_brief(brief, model)
    trace = trace or assemble(model)
    if case not in model.cases:
        raise ModelError("Select a load case in this model.")
    support_notes = [
        f"At {c.node}, {MOVEMENT[c.dof]} is prescribed as {c.value:g} {'rad' if c.dof == 'rz' else 'm'}."
        for c in model.constraints
    ]
    support_notes += [
        f"At {s.node}, a spring resists {MOVEMENT[s.dof]} with stiffness {s.stiffness:g} {'N m/rad' if s.dof == 'rz' else 'N/m'}. It is not a fixed support."
        for s in model.springs
    ]
    if not support_notes:
        support_notes = [
            "No supports are defined. Check how the real object is held; a free structure normally has a mechanism."
        ]
    if brief.scope == "Selected portion":
        support_notes.append(
            "Cut-boundary description supplied by the student: " + brief.boundary_notes
        )
    loads = sum(v.case == case for v in model.loads)
    udls = sum(v.case == case for v in model.distributed_loads)
    steps = [
        (
            "1. State the assumptions",
            FAMILY[model.kind]
            + " All materials are linear elastic; movements are small and loads are static.",
        ),
        (
            "2. Draw the loads and supports",
            f"Case {case!r} contains {loads} nodal loads and {udls} distributed loads. Check the arrows, units and support movements against the real problem. Different cases are solved separately.",
        ),
        (
            "3. Build each element equation",
            f"There are {len(model.elements)} elements. "
            + {
                "bar": "Each uses its own length, E and A. Axial stiffness scales with EA/L.",
                "truss": "Each uses its own length, E and A. Axial stiffness scales with EA/L.",
                "beam": "Each bending matrix uses its own length, E and I. Bending stiffness scales with EI/L³. Area A does not set bending stiffness.",
                "frame": "Each uses its own length, E, A and I. Axial stiffness scales with EA/L; bending stiffness scales with EI/L³.",
            }[model.kind],
        ),
        (
            "4. Use shared directions",
            "Use local axes to describe each member. A coordinate transformation relates its movements and forces to the global axes. Inspect the selected member's T matrix below.",
        ),
        (
            "5. Assemble and apply known movements",
            f"Assembly gives {len(trace.labels)} DOFs: {len(trace.free)} free and {len(trace.prescribed)} prescribed. Springs add diagonal stiffness. The equation is Kff uf = Ff − Kfc uc. This step forms equations; it does not solve them.",
        ),
        (
            "6. Solve the unknown movements",
            "In Stage 3, the engine scales the free equations and uses sparse LU factorization. It rejects mechanisms; it does not add artificial restraints or calculate an explicit inverse.",
        ),
        (
            "7. Recover member results",
            "Use the solved movements to recover end forces, subtract consistent nodal loads, and calculate the member force diagrams. Normal stress uses N/A and, where applicable, ±Mc/I.",
        ),
        (
            "8. Check and interpret",
            "Check force and moment equilibrium, the energy identity and numerical residual. Compare a matching hand solution when available. Then review the assumptions: balanced equations do not prove structural safety.",
        ),
    ]
    methods = [
        (
            "Equilibrium and hand formulas",
            "Start with a free-body diagram. A matching textbook formula is fast and easy to check. Equilibrium alone does not determine every displacement or every force in an indeterminate structure.",
        ),
        (
            "Direct stiffness FEM",
            "Useful for connected members, several supports, springs or prescribed movements. It handles compatibility and equilibrium together under the selected assumptions.",
        ),
        (
            "Avoid the wrong element family",
            "A truss cannot carry member bending. Euler–Bernoulli theory leaves out shear movement. More elements cannot restore physics the element does not contain.",
        ),
        (
            "Avoid unnecessary numerical work",
            "Do not explicitly invert K. Sparse factorization is more practical for large systems. Do not add fake stiffness to hide an unsupported movement.",
        ),
    ]
    return MethodGuide(
        FAMILY[model.kind], steps, support_notes, methods, analytical_check(model, case)
    )


def discuss(model: Model, result: SolveResult, brief: ProblemBrief) -> Discussion:
    check_brief(brief, model)
    external = result.applied_loads + result.constraint_reactions + result.spring_reactions
    nodes = {n.id: n for n in model.nodes}
    force_x, force_y, moment = [], [], []
    scale_x: list[float] = []
    scale_y: list[float] = []
    scale_m: list[float] = []
    for i, label in enumerate(result.labels):
        node_id, dof = label.rsplit(":", 1)
        node = nodes[node_id]
        parts = [
            result.applied_loads[i],
            result.constraint_reactions[i],
            result.spring_reactions[i],
        ]
        if dof == "ux":
            force_x.append(float(external[i]))
            scale_x.extend(abs(v) for v in parts)
            moment.append(float(-node.y * external[i]))
            scale_m.extend(abs(node.y * v) for v in parts)
        elif dof == "uy":
            force_y.append(float(external[i]))
            scale_y.extend(abs(v) for v in parts)
            moment.append(float(node.x * external[i]))
            scale_m.extend(abs(node.x * v) for v in parts)
        else:
            moment.append(float(external[i]))
            scale_m.extend(abs(v) for v in parts)
    energy = float(result.diagnostics["strain_energy_J"])
    work = float(result.displacements @ (result.applied_loads + result.constraint_reactions))
    checks = [
        BalanceCheck(name, sum(values), 1e-9 + 1e-8 * sum(scale), unit)
        for name, values, scale, unit in [
            ("Horizontal force balance", force_x, scale_x, "N"),
            ("Vertical force balance", force_y, scale_y, "N"),
            ("Moment balance about the origin", moment, scale_m, "N m"),
        ]
    ]
    checks.append(
        BalanceCheck(
            "Discrete energy identity: 2U − uᵀ(F + Rc)",
            2 * energy - work,
            1e-12 + 1e-8 * max(abs(2 * energy), abs(work)),
            "J",
        )
    )
    translations = [i for i, name in enumerate(result.labels) if not name.endswith(":rz")]
    peak = max(translations, key=lambda i: abs(result.displacements[i]))
    observations = [
        f"Largest absolute nodal translation component: {result.labels[peak]} = {result.displacements[peak]:.6g} m. This is a component, not the movement vector length.",
        "Positive ux is right, positive uy is up, and positive rz is counterclockwise. A negative value means the opposite direction.",
        "Support reactions include prescribed-support reactions and spring reactions separately. Both are needed for external equilibrium.",
    ]
    if brief.target_node:
        observations.extend(
            f"Target {label}: {result.displacements[i]:.6g} {'rad' if label.endswith(':rz') else 'm'}."
            for i, label in enumerate(result.labels)
            if label.rsplit(":", 1)[0] == brief.target_node
        )
    selected = brief.target_member or model.elements[0].id
    fields = result.members[selected]
    for key, name, unit in [
        ("axial_force", "axial force", "N"),
        ("shear", "shear force", "N"),
        ("moment", "bending moment", "N m"),
    ]:
        if model.kind in ("bar", "truss") and key != "axial_force":
            continue
        values = fields[key]
        index = int(np.argmax(np.abs(values)))
        observations.append(
            f"Member {selected}, largest sampled absolute {name}: {values[index]:.6g} {unit} at local x = {fields['x'][index]:.6g} m. This is a sampled value, not a proof of the exact maximum."
        )
    hand = analytical_check(model, result.case)
    if hand:
        value = result.displacements[result.labels.index(str(hand["label"]))]
        observations.append(
            f"Matching analytical tip displacement: {hand['value']:.6g} m; FEM minus reference = {value - float(hand['value']):.3g} m."
        )
    limitations = [
        "These results describe the supplied mathematical model, not a certified structure. Material strength, design codes, damage and buckling capacity are not checked.",
        "Only linear elastic, small-displacement static behavior is included. Model boundaries and applied loads may be uncertain in a real test.",
        "Line-element section stresses do not resolve local stress concentrations near joints or load contacts.",
    ]
    if model.kind in ("beam", "frame"):
        limitations.append(
            "Euler–Bernoulli bending leaves out shear deformation. A, I and optional fiber distance do not fully describe the section; element length is not necessarily the physical member's unsupported length. No slenderness classification is inferred here."
        )
        if any(s.c is None for s in model.sections):
            limitations.append(
                "Some sections have no fiber distance c. Their bending normal stress cannot be reported; an axial stress value alone is not the total normal stress."
            )
    if any(c.value != 0 for c in model.constraints):
        limitations.append(
            "Known support movements do work. Scaling only the applied loads does not necessarily scale the whole response."
        )
    next_steps = [
        "Check real support movement and uncertain loads through measurements and reserved prediction cases.",
        "Refine the mesh only to investigate an approximation error within the same theory, or to represent changes in geometry, properties or loading.",
        "If shear movement matters, use a shear-deformable beam method such as Timoshenko. If movement changes the geometry, use geometric nonlinear analysis.",
        "For yielding, buckling or local joint stresses, use suitable material, stability or continuum analysis. These methods are outside this release; increasing one stiffness value does not replace them.",
    ]
    return Discussion(observations, checks, limitations, next_steps)


def apply_change(model: Model, case: str, change: Change) -> tuple[Model, str]:
    if not np.isfinite(change.value):
        raise ModelError("The changed value must be finite.")
    data = deepcopy(model_to_dict(model))
    if case not in model.cases:
        raise ModelError("Choose an existing load case.")
    if change.kind == "load_factor":
        for table in ("loads", "distributed_loads"):
            for row in data[table]:
                if row["case"] == case:
                    for key in ("value",) if table == "loads" else ("qx", "qy"):
                        row[key] *= change.value
        description = f"Multiply applied loads in case {case!r} by {change.value:g}; prescribed movements are unchanged."
    elif change.kind in ("E", "A", "I"):
        table = "materials" if change.kind == "E" else "sections"
        found = next((r for r in data[table] if r["id"] == change.target), None)
        if (
            found is None
            or (change.kind == "I" and model.kind in ("bar", "truss"))
            or (change.kind == "A" and model.kind == "beam")
        ):
            raise ModelError("Select a property used by this model.")
        old = found[change.kind]
        found[change.kind] = change.value
        description = f"Set {change.target} {change.kind} from {old:g} to {change.value:g} in SI. All members sharing it change; other section properties stay unchanged."
    elif change.kind in ("constraint_value", "release", "spring"):
        table = "springs" if change.kind == "spring" else "constraints"
        matches = [r for r in data[table] if f"{r['node']}:{r['dof']}" == change.target]
        if len(matches) != 1:
            raise ModelError(
                "Select exactly one existing support setting. Duplicate springs must first be combined in the model."
            )
        row = matches[0]
        if change.kind == "release":
            data[table].remove(row)
            description = (
                f"Release the prescribed movement at {change.target}. No new stiffness is added."
            )
        else:
            key = "stiffness" if change.kind == "spring" else "value"
            old = row[key]
            row[key] = change.value
            description = f"Change {change.target} {key} from {old:g} to {change.value:g} in SI."
    else:
        raise ModelError("Unsupported comparison change.")
    return model_from_dict(data), description


def compare_results(
    model: Model, baseline: SolveResult, changed: SolveResult, description: str
) -> Comparison:
    if baseline.labels != changed.labels or baseline.case != changed.case:
        raise ModelError("Comparison requires the same DOFs and load case.")
    rows = [
        {
            "DOF": label,
            "Baseline": float(a),
            "Changed": float(b),
            "Difference": float(b - a),
            "Unit": "rad" if label.endswith(":rz") else "m",
        }
        for label, a, b in zip(
            baseline.labels, baseline.displacements, changed.displacements, strict=True
        )
    ]
    return Comparison(description, fingerprint(model, baseline.case), rows)


def member_summary(model: Model, result: SolveResult) -> list[dict[str, Any]]:
    """Report sampled ranges separately for each physical quantity, in SI."""
    quantities = [("axial_force", "Axial force", "N"), ("axial_stress", "Axial stress", "Pa")]
    if model.kind in ("beam", "frame"):
        quantities += [
            ("shear", "Shear force", "N"),
            ("moment", "Bending moment", "N m"),
            ("transverse_displacement", "Transverse movement", "m"),
            ("stress_top", "Top normal stress", "Pa"),
            ("stress_bottom", "Bottom normal stress", "Pa"),
        ]
    rows = []
    for name, member in result.members.items():
        for key, label, unit in quantities:
            if key not in member:
                continue
            values = member[key]
            low, high = int(np.argmin(values)), int(np.argmax(values))
            rows.append(
                {
                    "Member": name,
                    "Quantity": label,
                    "Sampled minimum": float(values[low]),
                    "Minimum at x (m)": float(member["x"][low]),
                    "Sampled maximum": float(values[high]),
                    "Maximum at x (m)": float(member["x"][high]),
                    "Unit": unit,
                    "Sample count": len(values),
                }
            )
    return rows


def learning_report(
    model: Model,
    result: SolveResult,
    brief: ProblemBrief,
    guide: MethodGuide,
    discussion: Discussion,
    comparison: Comparison | None = None,
    figure_html: str = "",
) -> str:
    """Self-contained text plus optional trusted Plotly HTML. Escape every user string."""

    def bullets(items: list[str]) -> str:
        return "<ul>" + "".join("<li>" + escape(v) + "</li>" for v in items) + "</ul>"

    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>FEM learning report</title><style>body{max-width:1100px;margin:32px auto;padding:24px;font:16px/1.65 Arial;color:#13243a}h1,h2{color:#1d4ed8}pre{white-space:pre-wrap;background:#eef3fa;padding:16px}.fem-table{overflow:auto}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #cbd5e1}caption{text-align:left;font-weight:bold}</style></head><body>",
        "<h1>" + escape(model.title) + "</h1>",
        f"<p>Numerical model result, not a measured experiment. Solver {escape(__version__)}. Case: {escape(result.case)}.</p>",
        "<p>Model and case SHA-256: " + fingerprint(model, result.case) + "</p>",
        "<h2>1. Define</h2>"
        + bullets(
            [
                brief.question,
                brief.scope,
                brief.boundary_notes or "No cut-boundary notes supplied.",
                "Prediction: " + (brief.prediction or "Not entered."),
            ]
        ),
        "<h2>2. Understand</h2>"
        + bullets([heading + ": " + body for heading, body in guide.steps])
        + bullets(guide.support_notes),
        "<h2>3. Solve and discuss</h2>" + bullets(discussion.observations),
        figure_html,
        "<h2>Checks</h2>"
        + bullets(
            [
                f"{c.name}: imbalance {c.imbalance:.6g} {c.unit}; tolerance {c.tolerance:.6g} {c.unit}; {'passed' if c.passed else 'failed'}."
                for c in discussion.checks
            ]
        ),
        "<h2>Limitations</h2>" + bullets(discussion.limitations),
        "<h2>Next investigations</h2>" + bullets(discussion.next_steps),
    ]
    if comparison:
        parts += [
            "<h2>Change one thing</h2><p>" + escape(comparison.description) + "</p>",
            "<p>Baseline model and case: " + escape(comparison.baseline_fingerprint) + "</p>",
            "<p>Comparison failed: " + escape(comparison.error) + "</p>"
            if comparison.error
            else html_table(comparison.rows, "Baseline and changed movements"),
        ]
    parts += [
        "<h2>Method choices</h2>" + bullets([title + ": " + body for title, body in guide.methods])
    ]
    parts += [
        "<h2>Node movements and support/spring reactions</h2><p>SI values; moments and rotations have their own units.</p>",
        html_table(
            [
                {
                    "DOF": label,
                    "Movement": float(result.displacements[i]),
                    "Movement unit": "rad" if label.endswith(":rz") else "m",
                    "Prescribed reaction": float(result.constraint_reactions[i]),
                    "Spring reaction": float(result.spring_reactions[i]),
                    "Reaction unit": "N m" if label.endswith(":rz") else "N",
                }
                for i, label in enumerate(result.labels)
            ],
            "Node movements and support reactions",
        ),
        "<h2>Member results</h2><p>These are sampled ranges, not exact maximum values. Local x runs from the member's start to its end. Tension and sagging moment are positive. No stress concentration or strength check is included.</p>",
        html_table(member_summary(model, result), "Sampled member ranges in SI"),
    ]
    parts += [
        "<details><summary>Plain-English glossary</summary>",
        "<dl>"
        + "".join(
            "<dt><strong>"
            + escape(term.label)
            + "</strong></dt><dd>"
            + escape(term.meaning)
            + "</dd>"
            for term in sorted(TERMS.values(), key=lambda t: t.label.lower())
        )
        + "</dl></details>",
    ]
    parts += [
        "<h2>Reproduce the problem</h2><p>Units inside this record are SI. Recompute results after import.</p><pre>",
        escape(json.dumps(project_to_dict(model, brief), indent=2)),
        "</pre></body></html>",
    ]
    return "".join(parts)
