"""Create self-contained reports for every family and a synthetic identification example."""

import argparse
from pathlib import Path

from fem_solver import solve_linear
from fem_solver.examples import NAMES, example
from fem_solver.export import identification_report
from fem_solver.identification import IdentificationConfig, fit_cantilever
from fem_solver.learning import (
    Change,
    ProblemBrief,
    apply_change,
    build_guide,
    compare_results,
    discuss,
    learning_report,
)
from fem_solver.study import synthetic_observations
from fem_solver.visualization import structure_figure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/learning-reports"))
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        model = example(name)
        brief = ProblemBrief(
            prediction="Twice the applied load should double movement for this example."
        )
        result = solve_linear(model)
        changed, description = apply_change(model, result.case, Change("load_factor", value=2.0))
        comparison = compare_results(model, result, solve_linear(changed), description)
        report = learning_report(
            model,
            result,
            brief,
            build_guide(model, brief, result.case),
            discuss(model, result, brief),
            comparison,
            structure_figure(model, result, magnification=50).to_html(
                full_html=False, include_plotlyjs=True
            ),
        )
        target = output / f"{model.kind}.html"
        target.write_text(report, encoding="utf-8")
        print(target)
    observations = synthetic_observations()
    result = fit_cantilever(observations, IdentificationConfig())
    target = output / "identification.html"
    target.write_text(
        identification_report(
            result, {"source": "Default synthetic generator; seed 2027. No physical measurements."}
        ),
        encoding="utf-8",
    )
    print(target)


if __name__ == "__main__":
    main()
