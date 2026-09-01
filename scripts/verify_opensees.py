"""Independent benchmark environment; never imported by the app or solver."""

import json
from pathlib import Path

import numpy as np
import openseespy.opensees as ops
from numpy.testing import assert_allclose

from fem_solver import solve_linear
from fem_solver.examples import NAMES, example
from fem_solver.model import Constraint, Spring


def reference(model):
    ops.wipe()
    ndm = 1 if model.kind == "bar" else 2
    ndf = 1 if model.kind == "bar" else 2 if model.kind == "truss" else 3
    directions = {"ux": 1, "uy": 2, "rz": 3}
    ops.model("basic", "-ndm", ndm, "-ndf", ndf)
    nodes = {n.id: i + 1 for i, n in enumerate(model.nodes)}
    materials = {m.id: m.E for m in model.materials}
    sections = {s.id: s for s in model.sections}
    for n in model.nodes:
        ops.node(nodes[n.id], *([n.x] if ndm == 1 else [n.x, n.y]))
        fixed = [0] * ndf
        if model.kind == "beam":
            fixed[0] = 1
        for c in model.constraints:
            if c.node == n.id and c.value == 0:
                fixed[directions[c.dof] - 1] = 1
        ops.fix(nodes[n.id], *fixed)
    if model.kind in ("beam", "frame"):
        ops.geomTransf("Linear", 1)
    elements = {}
    for i, e in enumerate(model.elements, 1):
        elements[e.id] = i
        s, E = sections[e.section], materials[e.material]
        if model.kind in ("bar", "truss"):
            ops.uniaxialMaterial("Elastic", i, E)
            ops.element("Truss", i, nodes[e.start], nodes[e.end], s.A, i)
        else:
            ops.element("elasticBeamColumn", i, nodes[e.start], nodes[e.end], s.A, E, s.I, 1)
    for i, spring in enumerate(model.springs, 1):
        node = next(n for n in model.nodes if n.id == spring.node)
        ground, tag = len(nodes) + i, len(elements) + i
        ops.node(ground, *([node.x] if ndm == 1 else [node.x, node.y]))
        ops.fix(ground, *([1] * ndf))
        ops.uniaxialMaterial("Elastic", 10000 + i, spring.stiffness)
        ops.element(
            "zeroLength",
            tag,
            nodes[node.id],
            ground,
            "-mat",
            10000 + i,
            "-dir",
            directions[spring.dof],
        )
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    for c in model.constraints:
        if c.value:
            ops.sp(nodes[c.node], directions[c.dof], c.value)
    for load in model.loads:
        vector = [0.0] * ndf
        vector[directions[load.dof] - 1] = load.value
        ops.load(nodes[load.node], *vector)
    for load in model.distributed_loads:
        ops.eleLoad("-ele", elements[load.element], "-type", "-beamUniform", load.qy, load.qx)
    ops.constraints("Transformation")
    ops.numberer("RCM")
    ops.system("BandGeneral")
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    if ops.analyze(1) != 0:
        raise RuntimeError("OpenSees analysis failed")
    ops.reactions()
    u = np.array(
        [ops.nodeDisp(nodes[n.id], directions[d]) for n in model.nodes for d in model.dofs]
    )
    reactions = np.array(
        [
            ops.nodeReaction(nodes[n.id], directions[d])
            if any(c.node == n.id and c.dof == d for c in model.constraints)
            else 0.0
            for n in model.nodes
            for d in model.dofs
        ]
    )
    return u, reactions


def timoshenko(slenderness):
    E, nu, b, L = 70e9, 0.3, 0.02, 1.0
    h = L / slenderness
    A, I = b * h, b * h**3 / 12  # noqa: E741
    G = E / (2 * (1 + nu))
    ops.wipe()
    ops.model("basic", "-ndm", 2, "-ndf", 3)
    ops.node(1, 0.0, 0.0)
    ops.node(2, L, 0.0)
    ops.fix(1, 1, 1, 1)
    ops.geomTransf("Linear", 1)
    ops.element("ElasticTimoshenkoBeam", 1, 1, 2, E, G, A, I, (5 / 6) * A, 1)
    ops.timeSeries("Constant", 1)
    ops.pattern("Plain", 1, 1)
    ops.load(2, 0.0, -1.0, 0.0)
    ops.constraints("Plain")
    ops.numberer("Plain")
    ops.system("BandGeneral")
    ops.algorithm("Linear")
    ops.integrator("LoadControl", 1.0)
    ops.analysis("Static")
    if ops.analyze(1) != 0:
        raise RuntimeError("Timoshenko reference failed")
    exact = L**3 / (3 * E * I) + L / ((5 / 6) * G * A)
    computed = -ops.nodeDisp(2, 2)
    assert_allclose(computed, exact, rtol=1e-8)
    return {
        "slenderness": slenderness,
        "analytical_m": exact,
        "OpenSees_m": computed,
        "relative_error": abs(computed / exact - 1),
    }


def main():
    cases = [example(name) for name in NAMES]
    spring = example("Cantilever beam")
    spring.title = "Beam with rotational support spring"
    spring.constraints = [Constraint("A", "uy")]
    spring.springs = [Spring("A", "rz", 2e6)]
    cases.append(spring)
    results = []
    for model in cases:
        own = solve_linear(model)
        u, r = reference(model)
        assert_allclose(own.displacements, u, rtol=1e-6, atol=1e-11)
        assert_allclose(own.constraint_reactions, r, rtol=1e-6, atol=1e-6)
        results.append(
            {
                "case": model.title,
                "status": "passed",
                "max_displacement_absolute_error": float(np.max(np.abs(own.displacements - u))),
                "max_constraint_reaction_absolute_error": float(
                    np.max(np.abs(own.constraint_reactions - r))
                ),
            }
        )
    report = {
        "reference": "OpenSeesPy",
        "OpenSees_engine_version": ops.version(),
        "provenance": "independent numerical comparison",
        "note": "Displacements include m/rad and reactions N/Nm; mixed-component maxima are descriptive, not normalized physical norms.",
        "cases": results,
        "timoshenko": [timoshenko(n) for n in [10, 20, 50, 100]],
    }
    output = Path("reports/verification")
    output.mkdir(parents=True, exist_ok=True)
    (output / "opensees.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
