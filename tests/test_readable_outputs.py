"""Check engineering content and accessible structure, not just rendering code."""

from dataclasses import replace

import pytest

from fem_solver import ModelError, solve_linear
from fem_solver.examples import example
from fem_solver.export import html_table, identification_report
from fem_solver.identification import IdentificationConfig, Observation, fit_cantilever
from fem_solver.learning import Change, apply_change, member_summary
from fem_solver.study import synthetic_observations


def test_member_ranges_have_stress_units_and_actual_sample_positions():
    model = example("Cantilever beam")
    result = solve_linear(model)
    rows = member_summary(model, result)
    moment = next(row for row in rows if row["Quantity"] == "Bending moment")
    stress = next(row for row in rows if row["Quantity"] == "Top normal stress")
    values = result.members[model.elements[0].id]
    assert moment["Sampled minimum"] == min(values["moment"])
    assert stress["Sampled maximum"] == max(values["stress_top"])
    assert moment["Unit"] == "N m" and stress["Unit"] == "Pa"
    assert 0 <= moment["Minimum at x (m)"] <= max(values["x"])
    assert moment["Sample count"] == len(values["x"])
    model.sections[0] = replace(model.sections[0], c=None)
    assert not any(
        "normal stress" in row["Quantity"] for row in member_summary(model, solve_linear(model))
    )


def test_beam_comparison_rejects_area_as_a_bending_stiffness_change():
    model = example("Cantilever beam")
    with pytest.raises(ModelError, match="property used"):
        apply_change(model, "default", Change("A", model.sections[0].id, 1.0))


def test_html_table_preserves_small_values_and_escapes_user_text():
    html = html_table(
        [{"<name>": "<img src=x>", "I (m⁴)": 8e-6, "Missing": None}], 'Values "for review"'
    )
    assert '<th scope="col">' in html and "<caption>" in html
    assert 'tabindex="0"' in html
    assert "8e-06" in html and "Not available" in html
    assert "<img" not in html and "&lt;img" in html and "&lt;name&gt;" in html


def test_identification_report_explains_success_and_ambiguity_without_json_only():
    data = synthetic_observations(1000.0, 2e-5, 0.0025, [0.25, 0.5, 0.75, 1.0])
    fit = fit_cantilever(data, IdentificationConfig(bootstrap_samples=20))
    html = identification_report(fit, {"note": "<script>bad</script>"})
    for text in [
        "Estimates and prediction errors",
        "Approximate uncertainty ranges",
        "Raw record for reproduction",
        "rad/(N m)",
    ]:
        assert text in html
    assert "<script>bad" not in html and "&lt;script&gt;bad" in html
    ambiguous = fit_cantilever([Observation("one", 1.0, 1.0, 1.0, 0.001, 1e-6)])
    html = identification_report(ambiguous, {})
    assert "No unique estimates" in html and "Not available" in html
