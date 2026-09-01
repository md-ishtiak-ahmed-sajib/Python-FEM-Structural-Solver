import csv
import io
import json
from dataclasses import asdict

import numpy as np
from numpy.testing import assert_allclose

from fem_solver import solve_linear
from fem_solver.examples import example
from fem_solver.export import identification_report, result_dict, results_csv, save_solution
from fem_solver.identification import IdentificationConfig, _estimate, fit_cantilever
from fem_solver.study import batch_compliance_fit, run_study, synthetic_observations
from fem_solver.visualization import member_figure, structure_figure


def test_vectorized_bounded_fit_against_scipy():
    rng = np.random.default_rng(93)
    for columns in [1, 2]:
        A = rng.uniform(0.1, 1.0, (6, columns))
        B = rng.normal(0, 2.0, (6, 100))
        fast = batch_compliance_fit(A, B)
        reference = np.column_stack([_estimate(A, b) for b in B.T])
        assert_allclose(fast, reference, atol=1e-10)


def test_study_reproducibility_and_generators(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    manifest = run_study(first, trials=3, quick=True)
    run_study(second, trials=3, quick=True)
    assert (first / "summary.csv").read_bytes() == (second / "summary.csv").read_bytes()
    assert manifest["unidentifiable_configurations"] > 0
    assert manifest["provenance"] == "synthetic"
    assert (first / "stiffness_error.png").exists()


def test_export_roundtrip_and_escape(tmp_path):
    model = example("Portal frame")
    result = solve_linear(model)
    save_solution(tmp_path, model, result)
    exported = json.loads((tmp_path / "results.json").read_text())
    assert_allclose(exported["displacements"], result.displacements)
    assert exported["model_sha256"] == result_dict(model, result)["model_sha256"]
    assert "reaction_unit" in results_csv(result)
    identified = fit_cantilever(synthetic_observations(), IdentificationConfig(bootstrap_samples=0))
    html = identification_report(identified, {"title": "<script>alert(1)</script>"})
    assert "<script>" not in html and "&lt;script&gt;" in html
    json.dumps(asdict(identified), allow_nan=False)


def test_display_unit_conversion_preserves_physical_results():
    model = example("Portal frame")
    result = solve_linear(model)
    before = result.displacements.copy()
    si = list(csv.DictReader(io.StringIO(results_csv(result))))
    mm = list(csv.DictReader(io.StringIO(results_csv(result, "N-mm-MPa"))))
    for first, second in zip(si, mm, strict=True):
        rotation = first["displacement_unit"] == "rad"
        assert_allclose(
            float(second["displacement"]), float(first["displacement"]) * (1 if rotation else 1000)
        )
        assert_allclose(
            float(second["constraint_reaction"]),
            float(first["constraint_reaction"]) * (1000 if rotation else 1),
        )
    plot_m = structure_figure(model, result)
    plot_mm = structure_figure(model, result, units="N-mm-MPa")
    assert_allclose(plot_mm.data[0].x, np.array(plot_m.data[0].x) * 1000)
    assert plot_mm.layout.yaxis.scaleanchor == "x"
    first_member = next(iter(result.members.values()))
    diagram = member_figure(first_member, "moment", "N-mm-MPa")
    assert_allclose(diagram.data[0].y, first_member["moment"] * 1000)
    stress = member_figure(first_member, "stress_top", "N-mm-MPa")
    assert_allclose(stress.data[0].y, first_member["stress_top"] / 1e6)
    assert_allclose(result.displacements, before)
    html = plot_mm.to_html(include_plotlyjs=True)
    assert '<script src="http' not in html
