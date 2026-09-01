from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose

from fem_solver import ModelError, assemble, model_from_dict, model_to_dict, solve_linear
from fem_solver.examples import NAMES, example, example_data
from fem_solver.model import Constraint, DistributedLoad, Load, Spring
from fem_solver.solver import SolveOptions


def beam():
    m = example("Cantilever beam")
    m.distributed_loads = []
    return m


def test_bar_analytical_and_stress():
    m = example("Axial bar")
    r = solve_linear(m)
    assert_allclose(r.displacements, [0, 10000 * 2 / (200e9 * 0.003)], rtol=1e-10)
    assert_allclose(r.constraint_reactions, [-10000, 0], atol=1e-8)
    assert_allclose(r.members["AB"]["axial_stress"], 10000 / 0.003)


def test_cantilever_tip_and_rotation():
    m = beam()
    r = solve_linear(m)
    EI, L, P = 200e9 * 8e-6, 3.0, -1000.0
    assert_allclose(r.displacements, [0, 0, P * L**3 / (3 * EI), P * L**2 / (2 * EI)], atol=1e-12)
    assert_allclose(r.constraint_reactions[:2], [-P, -P * L])
    assert_allclose(r.members["AB"]["moment"][[0, -1]], [P * L, 0], atol=1e-8)


def test_cantilever_udl_and_exact_interior_recovery():
    m = beam()
    m.loads = []
    m.distributed_loads = [DistributedLoad("AB", qy=-500)]
    r = solve_linear(m)
    EI, L, q = 200e9 * 8e-6, 3.0, -500.0
    assert_allclose(r.displacements[2], q * L**4 / (8 * EI), rtol=1e-10)
    x = r.members["AB"]["x"]
    exact = q * x**2 * (6 * L**2 - 4 * L * x + x * x) / (24 * EI)
    assert_allclose(r.members["AB"]["transverse_displacement"], exact, atol=1e-12)


def test_simply_supported_udl():
    m = beam()
    m.loads = []
    m.constraints = [Constraint("A", "uy"), Constraint("B", "uy")]
    m.distributed_loads = [DistributedLoad("AB", qy=-500)]
    r = solve_linear(m)
    assert_allclose(r.constraint_reactions[[0, 2]], [750, 750])
    assert_allclose(
        r.members["AB"]["transverse_displacement"][20], -5 * 500 * 3**4 / (384 * 200e9 * 8e-6)
    )
    assert_allclose(r.members["AB"]["moment"][20], 500 * 3**2 / 8)


def test_truss_hand_equilibrium():
    m = example("Triangular truss")
    r = solve_linear(m)
    assert_allclose(r.constraint_reactions[[1, 3]], [10000, 10000], atol=1e-8)
    assert_allclose(r.members["AC"]["axial_force"], -10000 * np.sqrt(13) / 3)
    assert_allclose(r.members["AB"]["axial_force"], 20000 / 3)


def test_rotational_spring_and_energy():
    m = beam()
    m.constraints = [Constraint("A", "uy")]
    k = 2e6
    m.springs = [Spring("A", "rz", k)]
    r = solve_linear(m)
    assert_allclose(r.displacements[2], -1000 * 3**3 / (3 * 200e9 * 8e-6) - 1000 * 3**2 / k)
    assert_allclose(r.spring_reactions[1], 3000)
    assert_allclose(r.constraint_reactions[1], 0)
    assert_allclose(2 * r.diagnostics["strain_energy_J"], r.displacements @ r.applied_loads)


def test_prescribed_displacement_work_and_translation_spring():
    m = example("Axial bar")
    m.constraints = [Constraint("A", "ux", 0.002)]
    m.springs = [Spring("B", "ux", 1e6)]
    r = solve_linear(m)
    k = 200e9 * 0.003 / 2
    assert_allclose(r.displacements[1], (10000 + k * 0.002) / (k + 1e6))
    assert_allclose(
        sum(r.applied_loads + r.constraint_reactions + r.spring_reactions), 0, atol=1e-6
    )
    assert_allclose(
        2 * r.diagnostics["strain_energy_J"],
        r.displacements @ (r.applied_loads + r.constraint_reactions),
    )


@pytest.mark.parametrize("name", NAMES)
def test_symmetry_units_and_reordering(name):
    m = example(name)
    a = assemble(m)
    assert_allclose(a.stiffness.toarray(), a.stiffness.toarray().T, atol=1e-8)
    r = solve_linear(m)
    other = solve_linear(model_from_dict(model_to_dict(m, "N-mm-MPa")))
    assert_allclose(r.displacements, other.displacements, rtol=1e-10, atol=1e-13)
    m.nodes.reverse()
    m.elements.reverse()
    other = solve_linear(m)
    assert_allclose(
        r.displacements,
        [dict(zip(other.labels, other.displacements, strict=True))[k] for k in r.labels],
        atol=1e-12,
    )


@pytest.mark.parametrize("name", NAMES)
def test_reversed_member_orientation(name):
    m = example(name)
    reference = solve_linear(m)
    m.elements = [replace(e, start=e.end, end=e.start) for e in m.elements]
    m.distributed_loads = [replace(q, qx=-q.qx, qy=-q.qy) for q in m.distributed_loads]
    result = solve_linear(m)
    assert_allclose(reference.displacements, result.displacements, atol=1e-12)
    assert_allclose(reference.constraint_reactions, result.constraint_reactions, atol=1e-7)


def test_case_superposition():
    m = beam()
    m.loads = [Load("B", "uy", -1000, "one"), Load("B", "uy", -2000, "two")]
    a = solve_linear(m, SolveOptions(case="one"))
    b = solve_linear(m, SolveOptions(case="two"))
    assert_allclose(b.displacements, 2 * a.displacements)


def test_rigid_body_modes():
    m = example("Portal frame")
    K = assemble(m).structural_stiffness
    for v in ([1, 0, 0] * 4, [0, 1, 0] * 4, [q for n in m.nodes for q in (-n.y, n.x, 1)]):
        assert_allclose(K @ np.array(v), 0, atol=1e-6)


@pytest.mark.parametrize(
    "mutation",
    ["zero_length", "negative_E", "unused", "duplicate", "nonfinite", "constraint", "invalid_dof"],
)
def test_invalid_models(mutation):
    d = example_data("Axial bar")
    if mutation == "zero_length":
        d["nodes"][1]["x"] = 0
    if mutation == "negative_E":
        d["materials"][0]["E"] = -1
    if mutation == "unused":
        d["nodes"].append({"id": "X", "x": 4})
    if mutation == "duplicate":
        d["nodes"][1]["id"] = "A"
    if mutation == "nonfinite":
        d["loads"][0]["value"] = float("nan")
    if mutation == "constraint":
        d["constraints"] *= 2
    if mutation == "invalid_dof":
        d["loads"][0]["dof"] = "rz"
    with pytest.raises(ModelError):
        model_from_dict(d)


@pytest.mark.parametrize("name", NAMES)
def test_unrestrained_models_fail(name):
    m = example(name)
    m.constraints = []
    with pytest.raises(ModelError, match="[Uu]nstable|singular|Unrestrained"):
        solve_linear(m)


def test_fully_prescribed_structure():
    m = beam()
    m.constraints += [Constraint("B", "uy", 0.001), Constraint("B", "rz")]
    result = solve_linear(m)
    assert_allclose(result.displacements, [0, 0, 0.001, 0])
