"""Two-node prismatic element formulations, local loads and exact UDL recovery."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .model import Element, Model

Array = NDArray[np.float64]


@dataclass
class ElementMatrices:
    element: Element
    length: float
    cosine: float
    sine: float
    EA: float
    EI: float
    area: float
    inertia: float
    extreme_fiber: float | None
    local: Array
    transform: Array
    indices: list[int]

    @property
    def global_matrix(self) -> Array:
        return self.transform.T @ self.local @ self.transform


def bending_matrix(EI: float, length: float) -> Array:
    L = length
    return (
        EI
        / L**3
        * np.array(
            [
                [12, 6 * L, -12, 6 * L],
                [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                [-12, -6 * L, 12, -6 * L],
                [6 * L, 2 * L * L, -6 * L, 4 * L * L],
            ],
            dtype=float,
        )
    )


def matrices(model: Model) -> list[ElementMatrices]:
    nodes = {n.id: n for n in model.nodes}
    positions = {n.id: i for i, n in enumerate(model.nodes)}
    materials = {m.id: m for m in model.materials}
    sections = {s.id: s for s in model.sections}
    nd = len(model.dofs)
    result = []
    for el in model.elements:
        a, b = nodes[el.start], nodes[el.end]
        dx, dy = b.x - a.x, b.y - a.y
        L = float(np.hypot(dx, dy))
        c, s = dx / L, dy / L
        sec, mat = sections[el.section], materials[el.material]
        EA, EI = mat.E * sec.A, mat.E * (sec.I or 0)
        axial = EA / L * np.array([[1.0, -1.0], [-1.0, 1.0]])
        if model.kind == "bar":
            k, T = axial, np.diag([c, c])
        elif model.kind == "truss":
            k = axial
            T = np.array([[c, s, 0, 0], [0, 0, c, s]])
        elif model.kind == "beam":
            k, T = bending_matrix(EI, L), np.diag([c, 1.0, c, 1.0])
        else:
            k = np.zeros((6, 6))
            k[np.ix_([0, 3], [0, 3])] = axial
            k[np.ix_([1, 2, 4, 5], [1, 2, 4, 5])] = bending_matrix(EI, L)
            rotation = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1.0]])
            T = np.zeros((6, 6))
            T[:3, :3] = T[3:, 3:] = rotation
        ids = [positions[n] * nd + d for n in (el.start, el.end) for d in range(nd)]
        result.append(ElementMatrices(el, L, c, s, EA, EI, sec.A, sec.I or 0, sec.c, k, T, ids))
    return result


def local_load(kind: str, L: float, qx: float, qy: float) -> Array:
    if kind in ("bar", "truss"):
        return np.array([qx * L / 2, qx * L / 2])
    bend = np.array([qy * L / 2, qy * L**2 / 12, qy * L / 2, -qy * L**2 / 12])
    if kind == "beam":
        return bend
    result = np.zeros(6)
    result[[0, 3]] = qx * L / 2
    result[[1, 2, 4, 5]] = bend
    return result


def recover(
    kind: str, em: ElementMatrices, u: Array, qx: float, qy: float, samples: int = 41
) -> dict[str, Array]:
    """Section N is tensile-positive, M sagging-positive, V = dM/dx, local axes."""
    L = em.length
    x = np.linspace(0, L, samples)
    t = x / L
    end = em.local @ u - local_load(kind, L, qx, qy)
    zero = np.zeros(samples)
    axial_disp, transverse, N, V, M = (zero.copy() for _ in range(5))
    if kind in ("bar", "truss", "frame"):
        j = 3 if kind == "frame" else 1
        axial_disp = (1 - t) * u[0] + t * u[j] + qx * x * (L - x) / (2 * em.EA)
        N = -end[0] - qx * x
    if kind in ("beam", "frame"):
        ids = [0, 1, 2, 3] if kind == "beam" else [1, 2, 4, 5]
        a = u[ids]
        transverse = (1 - 3 * t**2 + 2 * t**3) * a[0] + L * (t - 2 * t**2 + t**3) * a[1]
        transverse += (3 * t**2 - 2 * t**3) * a[2] + L * (-(t**2) + t**3) * a[3]
        transverse += qy * x**2 * (L - x) ** 2 / (24 * em.EI)
        V = end[ids[0]] + qy * x
        M = -end[ids[1]] + end[ids[0]] * x + qy * x**2 / 2
    axial_stress = N / em.area
    result = {
        "x": x,
        "axial_displacement": axial_disp,
        "transverse_displacement": transverse,
        "axial_force": N,
        "shear": V,
        "moment": M,
        "axial_stress": axial_stress,
        "local_end_forces": end,
        "local_displacements": u,
    }
    if em.extreme_fiber is not None and em.inertia > 0:
        result["stress_top"] = axial_stress - M * em.extreme_fiber / em.inertia
        result["stress_bottom"] = axial_stress + M * em.extreme_fiber / em.inertia
    return result
