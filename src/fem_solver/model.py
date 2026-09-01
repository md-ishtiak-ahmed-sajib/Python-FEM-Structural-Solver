"""Typed models, strict JSON exchange and dimensional conversion."""

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np

DOFS = {"bar": ("ux",), "truss": ("ux", "uy"), "beam": ("uy", "rz"), "frame": ("ux", "uy", "rz")}
UNITS = {"N-m-Pa": 1.0, "N-mm-MPa": 0.001}


class ModelError(ValueError):
    """Invalid or unsupported model; safe to display to the user."""


@dataclass(frozen=True)
class Node:
    id: str
    x: float
    y: float = 0.0


@dataclass(frozen=True)
class Material:
    id: str
    E: float


@dataclass(frozen=True)
class Section:
    id: str
    A: float
    I: float | None = None  # noqa: E741 - conventional second moment of area
    c: float | None = None


@dataclass(frozen=True)
class Element:
    id: str
    start: str
    end: str
    material: str
    section: str


@dataclass(frozen=True)
class Constraint:
    node: str
    dof: str
    value: float = 0.0


@dataclass(frozen=True)
class Spring:
    node: str
    dof: str
    stiffness: float


@dataclass(frozen=True)
class Load:
    node: str
    dof: str
    value: float
    case: str = "default"


@dataclass(frozen=True)
class DistributedLoad:
    element: str
    qx: float = 0.0
    qy: float = 0.0
    case: str = "default"


@dataclass
class Model:
    kind: str
    nodes: list[Node]
    materials: list[Material]
    sections: list[Section]
    elements: list[Element]
    constraints: list[Constraint] = field(default_factory=list)
    springs: list[Spring] = field(default_factory=list)
    loads: list[Load] = field(default_factory=list)
    distributed_loads: list[DistributedLoad] = field(default_factory=list)
    title: str = "Untitled structure"

    @property
    def dofs(self) -> tuple[str, ...]:
        return DOFS[self.kind]

    @property
    def cases(self) -> list[str]:
        return sorted(
            ({v.case for v in self.loads} | {v.case for v in self.distributed_loads}) or {"default"}
        )


def _finite(value: Any, label: str, positive: bool = False) -> None:
    if isinstance(value, (bool, str)) or not isinstance(value, (int, float, np.number)):
        raise ModelError(f"{label} must be a finite number.")
    if not np.isfinite(value) or (positive and value <= 0):
        raise ModelError(f"{label} must be {'positive and ' if positive else ''}finite.")


def validate(model: Model) -> None:
    if model.kind not in DOFS:
        raise ModelError("kind must be bar, truss, beam or frame.")
    if not isinstance(model.title, str):
        raise ModelError("title must be text.")
    if not model.nodes or not model.elements:
        raise ModelError("At least two nodes and one element are required.")
    if len(model.nodes) > 10000 or len(model.elements) > 20000:
        raise ModelError(
            "Model exceeds this local application's 10,000 node / 20,000 element limit."
        )
    for name in ("nodes", "materials", "sections", "elements"):
        objects = getattr(model, name)
        ids = [obj.id for obj in objects]
        if any(not isinstance(v, str) or not v.strip() for v in ids):
            raise ModelError(f"{name}: IDs must be nonempty strings.")
        if len(set(ids)) != len(ids):
            raise ModelError(f"{name}: duplicate IDs.")
    nodes = {n.id: n for n in model.nodes}
    mats = {m.id: m for m in model.materials}
    sections = {s.id: s for s in model.sections}
    elements = {e.id: e for e in model.elements}
    for node in model.nodes:
        _finite(node.x, f"Node {node.id} x")
        _finite(node.y, f"Node {node.id} y")
    for mat in model.materials:
        _finite(mat.E, f"Material {mat.id} E", True)
    for sec in model.sections:
        _finite(sec.A, f"Section {sec.id} A", True)
        if model.kind in ("beam", "frame") or sec.I is not None:
            _finite(sec.I, f"Section {sec.id} I", True)
        if sec.c is not None:
            _finite(sec.c, f"Section {sec.id} c", True)
    used: set[str] = set()
    for el in model.elements:
        if el.start not in nodes or el.end not in nodes:
            raise ModelError(f"Element {el.id}: unknown endpoint.")
        if el.material not in mats or el.section not in sections:
            raise ModelError(f"Element {el.id}: unknown material or section.")
        a, b = nodes[el.start], nodes[el.end]
        length = np.hypot(b.x - a.x, b.y - a.y)
        if length <= 0:
            raise ModelError(f"Element {el.id}: zero length.")
        if model.kind in ("bar", "beam") and abs(b.y - a.y) > 1e-12 * length:
            raise ModelError(
                "Bar and beam models must be horizontal. Use truss or frame for inclined members."
            )
        used.update((el.start, el.end))
    if used != set(nodes):
        raise ModelError(f"Unused nodes: {sorted(set(nodes) - used)}.")
    seen: set[tuple[str, str]] = set()
    nodal_items: list[Constraint | Spring | Load] = [
        *model.constraints,
        *model.springs,
        *model.loads,
    ]
    for item in nodal_items:
        if item.node not in nodes or item.dof not in model.dofs:
            raise ModelError(
                f"Unknown node or unsupported degree of freedom: {item.node}:{item.dof}."
            )
        if isinstance(item, Spring):
            _finite(item.stiffness, "Spring stiffness", True)
        else:
            _finite(item.value, "Constraint/load value")
        if isinstance(item, Constraint):
            key = (item.node, item.dof)
            if key in seen:
                raise ModelError(f"Duplicate or conflicting constraint: {key}.")
            seen.add(key)
    for load in model.distributed_loads:
        if load.element not in elements:
            raise ModelError(f"Unknown distributed-load element: {load.element}.")
        _finite(load.qx, "Distributed qx")
        _finite(load.qy, "Distributed qy")
        if (
            model.kind == "truss"
            or (model.kind == "bar" and load.qy != 0)
            or (model.kind == "beam" and load.qx != 0)
        ):
            raise ModelError(
                "Distributed load components are incompatible with this element family."
            )
    all_loads: list[Load | DistributedLoad] = [*model.loads, *model.distributed_loads]
    for case_load in all_loads:
        if not isinstance(case_load.case, str) or not case_load.case.strip():
            raise ModelError("Load case names must be nonempty strings.")


def model_from_dict(data: dict[str, Any]) -> Model:
    """Read schema 1; input units are declared, returned object is SI."""
    if (
        not isinstance(data, dict)
        or type(data.get("schema_version")) is not int
        or data.get("schema_version") != 1
    ):
        raise ModelError("Expected a JSON object with schema_version: 1.")
    unit = data.get("units")
    if not isinstance(unit, str) or unit not in UNITS:
        raise ModelError("Declare units as N-m-Pa or N-mm-MPa.")
    length = UNITS[unit]
    classes = {
        "nodes": Node,
        "materials": Material,
        "sections": Section,
        "elements": Element,
        "constraints": Constraint,
        "springs": Spring,
        "loads": Load,
        "distributed_loads": DistributedLoad,
    }
    allowed = set(classes) | {"schema_version", "units", "kind", "title"}
    if set(data) - allowed:
        raise ModelError(f"Unknown model fields: {sorted(set(data) - allowed)}.")
    fields: dict[str, Any] = {}
    try:
        for name, cls in classes.items():
            rows = data.get(name, [])
            if not isinstance(rows, list):
                raise ModelError(f"{name} must be an array.")
            converted = []
            for row in rows:
                if not isinstance(row, dict):
                    raise ModelError(f"{name} entries must be objects.")
                row = dict(row)
                factors = {
                    "nodes": {"x": length, "y": length},
                    "materials": {"E": length**-2},
                    "sections": {"A": length**2, "I": length**4, "c": length},
                    "distributed_loads": {"qx": 1 / length, "qy": 1 / length},
                }.get(name, {})
                if name == "constraints":
                    factors = {"value": 1 if row.get("dof") == "rz" else length}
                if name == "loads":
                    factors = {"value": length if row.get("dof") == "rz" else 1}
                if name == "springs":
                    factors = {"stiffness": length if row.get("dof") == "rz" else 1 / length}
                for key, factor in factors.items():
                    if key in row and row[key] is not None:
                        _finite(row[key], f"{name}.{key}")
                        row[key] *= factor
                converted.append(cls(**row))
            fields[name] = converted
        model = Model(kind=data["kind"], title=data.get("title", "Untitled structure"), **fields)
        validate(model)
        return model
    except (KeyError, TypeError) as exc:
        raise ModelError(f"Invalid model fields: {exc}") from exc


def model_to_dict(model: Model, units: str = "N-m-Pa") -> dict[str, Any]:
    validate(model)
    if units not in UNITS:
        raise ModelError("Unsupported units.")
    data = {"schema_version": 1, "units": "N-m-Pa", **asdict(model)}
    if units == "N-m-Pa":
        return data
    # Conversion is the inverse of the input factors; do not change the model.
    for row in data["nodes"]:
        row["x"] *= 1000
        row["y"] *= 1000
    for row in data["materials"]:
        row["E"] /= 1e6
    for row in data["sections"]:
        row["A"] *= 1e6
        if row["I"] is not None:
            row["I"] *= 1e12
        if row["c"] is not None:
            row["c"] *= 1000
    for row in data["constraints"]:
        row["value"] *= 1 if row["dof"] == "rz" else 1000
    for row in data["loads"]:
        row["value"] *= 1000 if row["dof"] == "rz" else 1
    for row in data["springs"]:
        row["stiffness"] *= 1000 if row["dof"] == "rz" else 0.001
    for row in data["distributed_loads"]:
        row["qx"] /= 1000
        row["qy"] /= 1000
    data["units"] = units
    return data
