"""Small, reproducible examples. Values are engineering illustrations, not designs."""

from .model import model_from_dict


def example_data(name: str) -> dict:
    common = {
        "schema_version": 1,
        "units": "N-m-Pa",
        "materials": [{"id": "steel", "E": 200e9}],
        "sections": [{"id": "section", "A": 0.003, "I": 8e-6, "c": 0.08}],
    }

    def member(id, a, b):
        return {"id": id, "start": a, "end": b, "material": "steel", "section": "section"}

    def fix(node, *dofs):
        return [{"node": node, "dof": dof, "value": 0.0} for dof in dofs]

    if name == "Axial bar":
        return common | {
            "kind": "bar",
            "title": name,
            "nodes": [{"id": "A", "x": 0}, {"id": "B", "x": 2}],
            "elements": [member("AB", "A", "B")],
            "constraints": fix("A", "ux"),
            "loads": [{"node": "B", "dof": "ux", "value": 10000}],
        }
    if name == "Triangular truss":
        return common | {
            "kind": "truss",
            "title": name,
            "nodes": [
                {"id": "A", "x": 0, "y": 0},
                {"id": "B", "x": 4, "y": 0},
                {"id": "C", "x": 2, "y": 3},
            ],
            "elements": [member("AB", "A", "B"), member("AC", "A", "C"), member("BC", "B", "C")],
            "constraints": fix("A", "ux", "uy") + fix("B", "uy"),
            "loads": [{"node": "C", "dof": "uy", "value": -20000}],
        }
    if name == "Cantilever beam":
        return common | {
            "kind": "beam",
            "title": name,
            "nodes": [{"id": "A", "x": 0}, {"id": "B", "x": 3}],
            "elements": [member("AB", "A", "B")],
            "constraints": fix("A", "uy", "rz"),
            "loads": [{"node": "B", "dof": "uy", "value": -1000}],
            "distributed_loads": [{"element": "AB", "qy": -500}],
        }
    if name == "Portal frame":
        return common | {
            "kind": "frame",
            "title": name,
            "nodes": [
                {"id": "A", "x": 0, "y": 0},
                {"id": "B", "x": 0, "y": 3},
                {"id": "C", "x": 4, "y": 3},
                {"id": "D", "x": 4, "y": 0},
            ],
            "elements": [member("AB", "A", "B"), member("BC", "B", "C"), member("DC", "D", "C")],
            "constraints": fix("A", "ux", "uy", "rz") + fix("D", "ux", "uy", "rz"),
            "loads": [{"node": "B", "dof": "ux", "value": 5000}],
            "distributed_loads": [{"element": "BC", "qy": -3000}],
        }
    raise ValueError(f"Unknown example: {name}")


NAMES = ["Portal frame", "Triangular truss", "Cantilever beam", "Axial bar"]


def example(name: str):
    return model_from_dict(example_data(name))
