"""Check the installed wheel's core and learning helpers in a separate environment."""

import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

import fem_solver
from fem_solver import solve_linear
from fem_solver.examples import NAMES, example
from fem_solver.export import identification_report
from fem_solver.identification import (
    IdentificationConfig,
    Observation,
    analytical_deflection,
    fit_cantilever,
)
from fem_solver.learning import (
    ProblemBrief,
    build_guide,
    discuss,
    fingerprint,
    learning_report,
    project_from_dict,
    project_to_dict,
)
from fem_solver.terms import TERMS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Do not mistake an editable checkout for an installed distribution.
    if not Path(fem_solver.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError("Run this check with a wheel installed in a separate environment.")
    checked = []
    for name in NAMES:
        model = example(name)
        brief = ProblemBrief()
        guide = build_guide(model, brief, "default")
        result = solve_linear(model)
        discussion = discuss(model, result, brief)
        assert all(check.passed for check in discussion.checks)
        restored, restored_brief = project_from_dict(project_to_dict(model, brief))
        assert fingerprint(restored, "default") == fingerprint(model, "default")
        assert restored_brief == brief
        report = learning_report(model, result, brief, guide, discussion)
        assert "Plain-English glossary" in report and "<script src=" not in report
        assert "Sampled member ranges in SI" in report and '<th scope="col">' in report
        checked.append({"family": model.kind, "example": name, "status": "passed"})
    observations = [
        Observation(
            str(i),
            x,
            a,
            2.0,
            float(analytical_deflection(x, a, 2.0, 1000.0, 2e-5)),
            1e-6,
            "holdout" if a == 0.5 else "train",
        )
        for i, (a, x) in enumerate((a, x) for a in [1.0, 0.75, 0.5] for x in [0.25, 0.5, 0.75, 1.0])
    ]
    fit = fit_cantilever(observations, IdentificationConfig(bootstrap_samples=0))
    assert fit.status == "identified"
    np.testing.assert_allclose([fit.EI, fit.clamp_compliance], [1000.0, 2e-5], rtol=1e-8)
    assert fit.holdout_rmse < 1e-12
    identification_html = identification_report(fit, {"provenance": "synthetic wheel check"})
    assert "Estimates and prediction errors" in identification_html
    assert "Information supplied by the observations" in identification_html
    record = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Local wheel installation: core and UI-independent learning helpers. No physical experiment or separate-environment browser test.",
        "python": platform.python_version(),
        "solver": fem_solver.__version__,
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "families": checked,
        "checks": [
            "solve",
            "balance discussion",
            "project round trip",
            "learning report with readable member table and local glossary",
            "readable identification report",
        ],
        "synthetic_identification": "passed, including reserved predictions",
        "terminology_entries": len(TERMS),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
