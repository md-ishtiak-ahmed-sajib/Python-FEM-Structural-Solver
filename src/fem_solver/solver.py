"""Sparse direct stiffness method with constraint partitioning and explicit failures."""

import warnings
from dataclasses import dataclass, field

import numpy as np
from scipy import linalg, sparse
from scipy.sparse.linalg import MatrixRankWarning, splu

from .elements import Array, ElementMatrices, local_load, matrices, recover
from .model import Model, ModelError, validate


@dataclass
class AssemblyTrace:
    stiffness: sparse.csr_matrix
    structural_stiffness: sparse.csr_matrix
    spring_diagonal: Array
    loads: dict[str, Array]
    element_matrices: list[ElementMatrices]
    labels: list[str]
    free: list[int]
    prescribed: dict[int, float]


@dataclass
class SolveOptions:
    case: str = "default"
    samples: int = 41


@dataclass
class SolveResult:
    case: str
    labels: list[str]
    displacements: Array
    constraint_reactions: Array
    spring_reactions: Array
    applied_loads: Array
    members: dict[str, dict[str, Array]]
    trace: AssemblyTrace
    diagnostics: dict[str, float | str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


def assemble(model: Model) -> AssemblyTrace:
    validate(model)
    n = len(model.nodes) * len(model.dofs)
    labels = [f"{node.id}:{dof}" for node in model.nodes for dof in model.dofs]
    lookup = {
        (node.id, dof): i * len(model.dofs) + j
        for i, node in enumerate(model.nodes)
        for j, dof in enumerate(model.dofs)
    }
    elements = matrices(model)
    rows, cols, values = [], [], []
    loads = {case: np.zeros(n) for case in model.cases}
    for em in elements:
        k = em.global_matrix
        if not np.all(np.isfinite(k)):
            raise ModelError(
                f"Element {em.element.id}: stiffness exceeds floating-point range; check geometry and units."
            )
        for i, row in enumerate(em.indices):
            for j, col in enumerate(em.indices):
                rows.append(row)
                cols.append(col)
                values.append(k[i, j])
        for load in model.distributed_loads:
            if load.element == em.element.id:
                f = em.transform.T @ local_load(model.kind, em.length, load.qx, load.qy)
                loads[load.case][em.indices] += f
    structural = sparse.coo_matrix((values, (rows, cols)), shape=(n, n)).tocsr()
    for nodal_load in model.loads:
        loads[nodal_load.case][lookup[nodal_load.node, nodal_load.dof]] += nodal_load.value
    spring = np.zeros(n)
    for item in model.springs:
        spring[lookup[item.node, item.dof]] += item.stiffness
    prescribed = {lookup[c.node, c.dof]: c.value for c in model.constraints}
    free = [i for i in range(n) if i not in prescribed]
    if (
        not np.all(np.isfinite(structural.data))
        or any(not np.all(np.isfinite(v)) for v in loads.values())
        or not np.all(np.isfinite(spring))
    ):
        raise ModelError(
            "Assembled values exceed floating-point range; check input magnitudes and units."
        )
    total = structural + sparse.diags(spring, format="csr")
    if not np.all(np.isfinite(total.data)):
        raise ModelError("Combined structure and spring stiffness exceeds floating-point range.")
    return AssemblyTrace(
        total,
        structural,
        spring,
        loads,
        elements,
        labels,
        free,
        prescribed,
    )


def solve_linear(model: Model, options: SolveOptions | None = None) -> SolveResult:
    options = options or SolveOptions(case=model.cases[0])
    if options.samples < 2 or options.samples > 1001:
        raise ModelError("Choose between 2 and 1001 samples per element.")
    trace = assemble(model)
    if options.case not in trace.loads:
        raise ModelError(f"Unknown load case: {options.case}.")
    K, F = trace.stiffness, trace.loads[options.case]
    u = np.zeros(K.shape[0])
    fixed = list(trace.prescribed)
    u[fixed] = list(trace.prescribed.values())
    free = trace.free
    diagnostic: dict[str, float | str] = {"dofs": len(u), "free_dofs": len(free)}
    notes = []
    if free:
        Kff = K[free][:, free].tocsc()
        rhs = F[free] - K[free][:, fixed] @ u[fixed]
        diagonal = Kff.diagonal()
        if np.any(diagonal <= 0):
            bad = [trace.labels[free[i]] for i in np.where(diagonal <= 0)[0]]
            raise ModelError(f"Unrestrained degrees of freedom without stiffness: {bad}.")
        scale = 1 / np.sqrt(diagonal)
        D = sparse.diags(scale)
        A = (D @ Kff @ D).tocsc()
        b = scale * rhs
        if len(free) <= 300:
            eigen_min = float(linalg.eigvalsh(A.toarray(), subset_by_index=(0, 0))[0])
            diagnostic["smallest_scaled_eigenvalue"] = eigen_min
            if eigen_min <= 1e-12:
                raise ModelError(
                    "Unstable or numerically singular structure. Check supports, connectivity and mechanisms."
                )
            if eigen_min < 1e-8:
                notes.append("Ill-conditioned stiffness: inspect supports and stiffness contrasts.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", MatrixRankWarning)
                lu = splu(A)
                pivots = np.abs(lu.U.diagonal())
                if np.min(pivots) < 1e-12 * np.max(pivots):
                    raise ModelError(
                        "Numerically singular structure; no artificial stabilization was applied."
                    )
                y = lu.solve(b)
            if not np.all(np.isfinite(y)):
                raise ModelError("The solver returned nonfinite displacements.")
            u[free] = scale * y
            denom = float(np.linalg.norm(abs(A) @ np.abs(y), np.inf) + np.linalg.norm(b, np.inf))
            residual = float(np.linalg.norm(A @ y - b, np.inf) / max(denom, np.finfo(float).tiny))
            if residual > 1e-8:
                raise ModelError(
                    "Linear system residual exceeds the numerical acceptance threshold."
                )
            diagnostic["scaled_backward_error"] = residual
        except (RuntimeError, MatrixRankWarning) as exc:
            raise ModelError(
                "Singular structure: check restraints and member connectivity."
            ) from exc
    else:
        diagnostic["scaled_backward_error"] = 0.0
    residual_vector = K @ u - F
    reactions = np.zeros_like(u)
    reactions[fixed] = residual_vector[fixed]
    spring_reactions = -trace.spring_diagonal * u
    members = {}
    for em in trace.element_matrices:
        qx = sum(
            v.qx
            for v in model.distributed_loads
            if v.element == em.element.id and v.case == options.case
        )
        qy = sum(
            v.qy
            for v in model.distributed_loads
            if v.element == em.element.id and v.case == options.case
        )
        members[em.element.id] = recover(
            model.kind, em, em.transform @ u[em.indices], qx, qy, options.samples
        )
    diagnostic["strain_energy_J"] = float(u @ (K @ u) / 2)
    diagnostic["constraint_work_term_J"] = float(u @ reactions)
    return SolveResult(
        options.case,
        trace.labels,
        u,
        reactions,
        spring_reactions,
        F.copy(),
        members,
        trace,
        diagnostic,
        notes,
    )
