import json
import socket
from pathlib import Path

import pytest
from numpy.testing import assert_allclose
from streamlit.testing.v1 import AppTest

from fem_solver import ModelError, model_from_dict, solve_linear
from fem_solver.examples import NAMES, example, example_data
from fem_solver.identification import validate_measurement_metadata


def test_metadata_template_is_not_evidence():
    template = json.loads(Path("data/bench/metadata-template.json").read_text())
    with pytest.raises(ModelError):
        validate_measurement_metadata(template, 1.0)


@pytest.mark.parametrize("unit", [None, [], {}, "N-mm-Pa"])
def test_malformed_units_fail_cleanly(unit):
    data = example_data("Axial bar")
    data["units"] = unit
    with pytest.raises(ModelError):
        model_from_dict(data)


@pytest.mark.parametrize("name", NAMES)
def test_sparse_solution_matches_dense_reference(name):
    import numpy as np

    result = solve_linear(example(name))
    t = result.trace
    free, fixed = t.free, list(t.prescribed)
    rhs = result.applied_loads[free] - t.stiffness[free][:, fixed] @ result.displacements[fixed]
    dense = np.linalg.solve(t.stiffness[free][:, free].toarray(), rhs)
    assert_allclose(result.displacements[free], dense, atol=1e-12)


@pytest.mark.parametrize("name", NAMES)
def test_application_workflows_without_network(monkeypatch, name):
    def denied(*args, **kwargs):
        raise AssertionError("A runtime network connection was attempted.")

    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=30
    ).run()
    assert not app.exception
    next(s for s in app.selectbox if s.label == "Example structure").set_value(name)
    next(b for b in app.button if b.label == "Load example").click().run()
    next(b for b in app.button if b.label == "Save and check model").click().run()
    assert "solution" not in app.session_state
    next(r for r in app.radio if r.label == "Workspace").set_value("2 · Understand").run()
    assert not app.exception
    next(r for r in app.radio if r.label == "Workspace").set_value("3 · Solve and discuss").run()
    next(b for b in app.button if b.label == "Solve").click().run()
    assert not app.exception
    next(b for b in app.button if b.label == "Run comparison").click().run()
    assert app.session_state.comparison.error is None
    assert not app.exception
    next(r for r in app.radio if r.label == "Workspace").set_value("Stiffness study").run()
    assert not app.exception
    next(r for r in app.radio if r.label == "Workspace").set_value("Glossary").run()
    assert not app.exception
