import json
from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose

from fem_solver.examples import NAMES, example
from fem_solver.learning import (
    Change,
    ProblemBrief,
    analytical_check,
    apply_change,
    build_guide,
    compare_results,
    discuss,
    fingerprint,
    learning_report,
    project_from_dict,
    project_to_dict,
)
from fem_solver.model import Constraint, Load, ModelError, Spring, model_from_dict, model_to_dict
from fem_solver.solver import SolveOptions, solve_linear
from fem_solver.terms import TERMS, annotate, term_html
from fem_solver.ui_common import FIELD_TERMS, TABLE_TERMS


@pytest.mark.parametrize("name", NAMES)
def test_guides_and_balances(name):
    model = example(name)
    brief = ProblemBrief(target_node=model.nodes[-1].id, target_member=model.elements[-1].id)
    guide = build_guide(model, brief, "default")
    assert len(guide.steps) == 8
    result = solve_linear(model)
    discussion = discuss(model, result, brief)
    assert all(check.passed for check in discussion.checks)
    assert any("sampled" in note for note in discussion.observations)
    assert any("not a certified structure" in note for note in discussion.limitations)


@pytest.mark.parametrize("name", ["Axial bar", "Cantilever beam"])
def test_guarded_hand_check(name):
    model = example(name)
    hand = analytical_check(model, "default")
    assert hand is not None
    result = solve_linear(model)
    assert_allclose(
        result.displacements[result.labels.index(hand["label"])], hand["value"], rtol=1e-8
    )
    model.constraints[0] = replace(model.constraints[0], value=0.001)
    assert analytical_check(model, "default") is None
    model = example(name)
    model.springs.append(Spring(model.nodes[-1].id, model.dofs[0], 1000))
    assert analytical_check(model, "default") is None
    model = example(name)
    model.elements[0] = replace(model.elements[0], start="B", end="A")
    assert analytical_check(model, "default") is None


def test_portion_and_learning_project_validation():
    model = example("Portal frame")
    with pytest.raises(ModelError, match="cut boundaries"):
        build_guide(model, ProblemBrief(scope="Selected portion"), "default")
    brief = ProblemBrief(
        scope="Selected portion",
        boundary_notes="The removed foundation supplies the recorded restraints.",
        prediction="Check sway.",
    )
    data = json.loads(json.dumps(project_to_dict(model, brief)))
    loaded, loaded_brief = project_from_dict(data)
    assert fingerprint(loaded, "default") == fingerprint(model, "default")
    assert loaded_brief == brief
    with pytest.raises(ModelError, match="recomputed"):
        project_from_dict(data | {"results": {"displacement": 0}})
    with pytest.raises(ModelError, match="must be text"):
        project_from_dict(data | {"brief": {"prediction": ["bad"]}})
    legacy, _ = project_from_dict(model_to_dict(model, "N-mm-MPa"))
    assert_allclose(solve_linear(legacy).displacements, solve_linear(model).displacements)


def test_comparison_scaling_and_baseline_isolation():
    model = example("Axial bar")
    before = model_to_dict(model)
    baseline = solve_linear(model)
    for change, ratio in [
        (Change("load_factor", value=2), 2),
        (Change("E", "steel", 400e9), 0.5),
        (Change("A", "section", 0.006), 0.5),
    ]:
        other, description = apply_change(model, "default", change)
        result = solve_linear(other)
        assert_allclose(result.displacements, baseline.displacements * ratio)
        comparison = compare_results(model, baseline, result, description)
        assert comparison.baseline_fingerprint == fingerprint(model, "default")
        assert model_to_dict(model) == before
    released, _ = apply_change(model, "default", Change("release", "A:ux"))
    with pytest.raises(ModelError, match="singular"):
        solve_linear(released)
    with pytest.raises(ModelError):
        apply_change(model, "default", Change("E", "steel", -1))
    with pytest.raises(ModelError):
        apply_change(model, "default", Change("load_factor", value=float("nan")))


def test_settlements_springs_and_case_specific_scaling():
    model = example("Axial bar")
    model.constraints = [Constraint("A", "ux", 0.001)]
    model.springs = [Spring("B", "ux", 1e6)]
    model.loads.append(Load("B", "ux", 5000, "other"))
    result = solve_linear(model)
    discussion = discuss(model, result, ProblemBrief())
    assert all(c.passed for c in discussion.checks)
    assert any("does not necessarily scale" in note for note in discussion.limitations)
    changed, _ = apply_change(model, "default", Change("load_factor", value=2))
    assert changed.loads[-1].value == 5000
    assert changed.constraints[0].value == 0.001
    assert not np.allclose(
        solve_linear(changed, SolveOptions(case="default")).displacements, result.displacements * 2
    )


def test_report_and_help_escape_user_content():
    model = example("Axial bar")
    model.title = '<script>alert("bad")</script>'
    brief = ProblemBrief(prediction="<img src=x onerror=bad>")
    result = solve_linear(model)
    report = learning_report(
        model, result, brief, build_guide(model, brief, "default"), discuss(model, result, brief)
    )
    assert "<script>" not in report and "<img src=x" not in report
    assert "&lt;script&gt;" in report
    assert "not a measured experiment" in report
    assert fingerprint(model, "default") in report
    html = annotate("A and I and c are symbols; a reaction and <script> are different.")
    assert "<script>" not in html
    assert html.count('class="fem-term"') == 1
    assert "aria-label=" in term_html("EI")
    assert "direction" in TERMS["cosine"].meaning
    assert "section" in TERMS["fiber"].meaning
    assert set(FIELD_TERMS.values()) | set(TABLE_TERMS.values()) <= TERMS.keys()


def test_bad_target_and_bad_case_are_actionable():
    model = example("Axial bar")
    with pytest.raises(ModelError, match="target node"):
        build_guide(model, ProblemBrief(target_node="missing"), "default")
    with pytest.raises(ModelError, match="load case"):
        build_guide(model, ProblemBrief(), "missing")
    data = model_to_dict(model)
    data["sections"][0]["c"] = None
    model_from_dict(data)


def test_self_contained_report_has_safe_plot_and_readable_tables():
    from fem_solver.visualization import structure_figure

    model = example("Axial bar")
    model.title = "</script><script>unsafe_marker()</script>"
    result = solve_linear(model)
    brief = ProblemBrief()
    figure = structure_figure(model, result).to_html(full_html=False, include_plotlyjs=True)
    html = learning_report(
        model,
        result,
        brief,
        build_guide(model, brief, "default"),
        discuss(model, result, brief),
        figure_html=figure,
    )
    assert "<script>unsafe_marker()" not in html
    assert "<script src=" not in html
    assert "support/spring reactions" in html
    assert "Plain-English glossary" in html
    assert "plotly.js" in html.lower()
