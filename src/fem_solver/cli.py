"""Reproduce a solve, identification, or synthetic study without the browser."""

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from .export import identification_report, save_solution
from .identification import (
    IdentificationConfig,
    fit_cantilever,
    read_observations_csv,
    validate_measurement_metadata,
)
from .model import ModelError, model_from_dict
from .solver import SolveOptions, solve_linear
from .study import run_study


def main():
    parser = argparse.ArgumentParser(
        description="Solve a local structural model or estimate beam stiffness from observations."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    solve = sub.add_parser("solve", help="Calculate movements and forces from a JSON model.")
    solve.add_argument(
        "model", type=Path, help="Path to a version-1 JSON model with declared units."
    )
    solve.add_argument(
        "--case", default=None, help="Load-case name; default is the first case in the model."
    )
    solve.add_argument(
        "--output",
        type=Path,
        default=Path("results/solve"),
        help="Folder for the model, results and nodal CSV.",
    )
    study = sub.add_parser("study", help="Repeat the study using synthetic, not measured, data.")
    study.add_argument(
        "--trials",
        type=int,
        default=200,
        help="Planned repeated fits per configuration; default 200.",
    )
    study.add_argument(
        "--seed",
        type=int,
        default=2027,
        help="Random-number seed for repeatable noise; default 2027.",
    )
    study.add_argument(
        "--quick",
        action="store_true",
        help="Run a smaller check instead of the full research grid.",
    )
    study.add_argument(
        "--output",
        type=Path,
        default=Path("results/study"),
        help="Folder for the summary, settings and figures.",
    )
    fit = sub.add_parser("fit", help="Estimate EI and, optionally, clamp flexibility from a CSV.")
    fit.add_argument(
        "observations", type=Path, help="Observation CSV using the supplied SI column format."
    )
    fit.add_argument("--length", type=float, required=True, help="Beam free length in metres.")
    fit.add_argument(
        "--ei-reference",
        type=float,
        required=True,
        help="Positive EI scale in N m^2; it is not a measured result.",
    )
    fit.add_argument(
        "--support",
        choices=["rigid", "flexible"],
        default="flexible",
        help="Clamp model used for the fit; default flexible.",
    )
    fit.add_argument(
        "--bootstrap",
        type=int,
        default=200,
        help="Simulated fits for uncertainty ranges; 0 disables intervals.",
    )
    fit.add_argument(
        "--metadata",
        type=Path,
        help="JSON specimen, fixture and calibration details; required for real data.",
    )
    fit.add_argument(
        "--output",
        type=Path,
        default=Path("results/identification"),
        help="Folder for the fitted values and HTML report.",
    )
    args = parser.parse_args()
    try:
        if args.command == "solve":
            model = model_from_dict(json.loads(args.model.read_text(encoding="utf-8-sig")))
            result = solve_linear(model, SolveOptions(case=args.case or model.cases[0]))
            save_solution(args.output, model, result)
            print(json.dumps(result.diagnostics, indent=2))
        elif args.command == "study":
            print(json.dumps(run_study(args.output, args.trials, args.seed, args.quick), indent=2))
        else:
            raw = args.observations.read_bytes()
            observations = read_observations_csv(raw.decode("utf-8-sig"))
            metadata = json.loads(args.metadata.read_text()) if args.metadata else {}
            if any(o.provenance == "measured" for o in observations) and not metadata:
                raise ModelError(
                    "Measured-data analysis requires --metadata documenting the specimen, fixture and calibration."
                )
            config = IdentificationConfig(
                args.length, args.ei_reference, args.support, args.bootstrap
            )
            if any(o.provenance == "measured" for o in observations):
                validate_measurement_metadata(metadata, args.length)
            identified = fit_cantilever(observations, config)
            context = {
                "configuration": asdict(config),
                "input_sha256": hashlib.sha256(raw).hexdigest(),
                "metadata": metadata,
            }
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / "report.html").write_text(
                identification_report(identified, context), encoding="utf-8"
            )
            (args.output / "identification.json").write_text(
                json.dumps(
                    {"context": context, "result": asdict(identified)}, indent=2, allow_nan=False
                ),
                encoding="utf-8",
            )
            print(identified.status)
    except (ModelError, ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
