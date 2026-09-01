"""Exercise teaching stages through the app, including failures and stale state."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from fem_solver.examples import NAMES

FAMILY_FOR_EXAMPLE = {
    "Axial bar": "bar",
    "Triangular truss": "truss",
    "Cantilever beam": "beam",
    "Portal frame": "frame",
}


def widget(items, label):
    return next(item for item in items if item.label == label)


def start():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=30
    ).run()
    assert not app.exception
    return app


def visit(app, page):
    widget(app.radio, "Workspace").set_value(page).run()
    assert not app.exception


def open_example(app, name):
    widget(
        [button for button in app.button if button.key == "example_" + FAMILY_FOR_EXAMPLE[name]],
        "Open example",
    ).click().run()
    assert not app.exception
    assert widget(app.radio, "Workspace").value == "1 · Define"


@pytest.mark.parametrize("name", NAMES)
def test_guided_workflow_and_comparison(name):
    app = start()
    open_example(app, name)
    widget(app.button, "Save and check").click().run()
    assert "not been checked" in app.success[0].value
    assert "solution" not in app.session_state
    visit(app, "2 · Understand")
    assert "solution" not in app.session_state
    widget(app.text_area, "What movement or change do you expect, and why?").set_value(
        "Twice the load should double movement."
    ).run()
    visit(app, "3 · Solve and discuss")
    assert not app.metric
    widget(app.button, "Solve model").click().run()
    assert not app.exception
    assert any("Peak nodal translation" in item.value for item in app.markdown)
    baseline = app.session_state.solution[1].displacements.copy()
    widget(app.button, "Run comparison").click().run()
    assert not app.exception
    comparison = app.session_state.comparison
    assert comparison.error is None
    assert comparison.rows[-1]["Changed"] == pytest.approx(2 * comparison.rows[-1]["Baseline"])
    assert (baseline == app.session_state.solution[1].displacements).all()
    assert app.session_state.brief["prediction"].startswith("Twice")


def test_no_hidden_solve_and_draft_retention(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Stage 1 or 2 attempted to solve.")

    monkeypatch.setattr("fem_solver.ui_learning.solve_linear", forbidden)
    monkeypatch.setattr("fem_solver.solver.solve_linear", forbidden)
    app = start()
    visit(app, "1 · Define")
    widget(app.text_input, "Project title").set_value("My retained draft").run()
    visit(app, "2 · Understand")
    visit(app, "1 · Define")
    assert widget(app.text_input, "Project title").value == "My retained draft"
    visit(app, "Home")
    next(button for button in app.button if button.key == "blank_bar").click().run()
    assert not app.exception
    widget(app.button, "Save and check").click().run()
    assert "Draft saved" in app.error[0].value
    visit(app, "2 · Understand")
    assert "current draft is not ready" in app.error[0].value
    visit(app, "1 · Define")
    assert not app.session_state.draft["nodes"]


def test_edit_invalidates_result_and_portion_requires_notes():
    app = start()
    visit(app, "3 · Solve and discuss")
    widget(app.button, "Solve model").click().run()
    assert "solution" in app.session_state
    visit(app, "1 · Define")
    widget(app.text_input, "Project title").set_value("Changed problem").run()
    assert "solution" not in app.session_state
    widget(app.selectbox, "Structure extent").set_value("Selected portion").run()
    visit(app, "2 · Understand")
    assert any("cut boundaries" in e.value for e in app.error)
    visit(app, "3 · Solve and discuss")
    assert not any(b.label == "Solve model" for b in app.button)


def test_release_failure_and_direct_access():
    app = start()
    widget(app.radio, "Navigation").set_value("Direct access").run()
    visit(app, "Results")
    widget(app.button, "Solve model").click().run()
    widget(app.selectbox, "Change to investigate").set_value("release").run()
    widget(app.button, "Run comparison").click().run()
    assert app.session_state.comparison.error is not None
    assert "solution" in app.session_state
    visit(app, "Glossary")
    widget(app.text_input, "Search a term or meaning").set_value("compliance").run()
    assert any("compliance" in e.label.lower() for e in app.expander)


def test_study_ambiguity_and_measured_empty_state():
    app = start()
    visit(app, "Stiffness study")
    widget(app.radio, "Measurement positions").set_value(1)
    widget(app.selectbox, "Load pattern").set_value("amplitudes")
    app.run()
    assert not app.exception
    assert any("Unidentifiable configuration" in item.value for item in app.markdown)
    widget(app.radio, "Observation source").set_value("Measured CSV").run()
    assert not app.exception
    assert not app.metric


def test_table_edit_survives_navigation_and_unit_conversion():
    app = start()
    visit(app, "1 · Define")
    widget(app.segmented_control, "Model category").set_value("Properties").run()
    revision = app.session_state.revision
    app.session_state[f"table_materials_{revision}"] = {
        "edited_rows": {0: {"E": 100e9}},
        "added_rows": [],
        "deleted_rows": [],
    }
    app.run()
    assert not app.exception
    assert app.session_state.draft["materials"][0]["E"] == 100e9
    visit(app, "2 · Understand")
    visit(app, "1 · Define")
    assert app.session_state.draft["materials"][0]["E"] == 100e9
    widget(app.selectbox, "Input / export units").set_value("N-mm-MPa").run()
    assert not app.exception
    assert app.session_state.draft["materials"][0]["E"] == 100e3
    visit(app, "3 · Solve and discuss")
    widget(app.button, "Solve model").click().run()
    assert not app.exception
    assert app.session_state.solution[1].displacements[-1] == pytest.approx(
        10000 * 2 / (100e9 * 0.003)
    )


def test_load_case_change_removes_previous_result():
    app = start()
    data = dict(app.session_state.draft)
    data["loads"] = list(data["loads"]) + [
        {"node": "B", "dof": "ux", "value": 3000, "case": "second"}
    ]
    app.session_state.draft = data
    visit(app, "3 · Solve and discuss")
    widget(app.button, "Solve model").click().run()
    assert "solution" in app.session_state
    widget(app.selectbox, "Load case").set_value("second").run()
    assert "solution" not in app.session_state
    assert not app.metric
    widget(app.button, "Solve model").click().run()
    assert app.session_state.solution[1].case == "second"
