"""Portable, explicit-unit outputs. Exported HTML escapes user-controlled text."""

import csv
import hashlib
import io
import json
from dataclasses import asdict
from html import escape
from pathlib import Path
from typing import Any

from . import __version__
from .identification import IdentificationResult
from .model import UNITS, Model, ModelError, model_to_dict
from .report_design import report_end, report_start
from .solver import SolveResult
from .terms import TERMS


def html_table(rows: list[dict[str, Any]], caption: str) -> str:
    """A readable HTML table with explicit headers and escaped user text."""
    if not rows:
        return "<p>No rows.</p>"

    def cell(value: Any) -> str:
        if value is None:
            return "Not available"
        return escape(f"{value:.6g}" if isinstance(value, float) else str(value))

    columns = list(rows[0])
    return (
        '<div class="fem-table" role="region" tabindex="0" aria-label="'
        + escape(caption, quote=True)
        + '"><table><caption>'
        + escape(caption)
        + "</caption><thead><tr>"
        + "".join('<th scope="col">' + escape(k) + "</th>" for k in columns)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join("<td>" + cell(row[k]) + "</td>" for k in columns) + "</tr>"
            for row in rows
        )
        + "</tbody></table></div>"
    )


def result_dict(model: Model, result: SolveResult) -> dict:
    encoded = model_to_dict(model)
    digest = hashlib.sha256(json.dumps(encoded, sort_keys=True).encode()).hexdigest()
    return {
        "schema_version": 1,
        "solver_version": __version__,
        "units": "N-m-Pa",
        "model_sha256": digest,
        "case": result.case,
        "labels": result.labels,
        "displacements": result.displacements.tolist(),
        "constraint_reactions": result.constraint_reactions.tolist(),
        "spring_reactions": result.spring_reactions.tolist(),
        "applied_loads": result.applied_loads.tolist(),
        "members": {
            key: {name: value.tolist() for name, value in member.items()}
            for key, member in result.members.items()
        },
        "diagnostics": result.diagnostics,
        "warnings": result.warnings,
        "limitation": "Elastic line elements, static loads and small movements. This result does not certify structural safety.",
    }


def safe_cell(value):
    return (
        "'" + value
        if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\t", "\r"))
        else value
    )


def results_csv(result: SolveResult, units: str = "N-m-Pa") -> str:
    if units not in UNITS:
        raise ModelError("Choose N-m-Pa or N-mm-MPa for result display.")
    factor = 1 / UNITS[units]
    length_unit = "m" if units == "N-m-Pa" else "mm"
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(
        [
            "degree_of_freedom",
            "displacement",
            "displacement_unit",
            "constraint_reaction",
            "spring_reaction",
            "reaction_unit",
        ]
    )
    for i, label in enumerate(result.labels):
        rotation = label.endswith(":rz")
        writer.writerow(
            [
                safe_cell(label),
                result.displacements[i] * (1 if rotation else factor),
                "rad" if rotation else length_unit,
                result.constraint_reactions[i] * (factor if rotation else 1),
                result.spring_reactions[i] * (factor if rotation else 1),
                f"N {length_unit}" if rotation else "N",
            ]
        )
    return out.getvalue()


def identification_report(result: IdentificationResult, context: dict) -> str:
    payload = {"solver_version": __version__, "context": context, "identification": asdict(result)}
    estimates = [
        {"Quantity": "Effective EI", "Value": result.EI, "Unit": "N m²"},
        {"Quantity": "Clamp compliance", "Value": result.clamp_compliance, "Unit": "rad/(N m)"},
        {"Quantity": "Training RMSE", "Value": result.train_rmse, "Unit": "m"},
        {"Quantity": "Reserved prediction RMSE", "Value": result.holdout_rmse, "Unit": "m"},
    ]
    intervals = [
        {
            "Parameter": "EI" if key.startswith("EI") else "Clamp compliance",
            "Lower": values[0],
            "Upper": values[1],
            "Unit": "N m²" if key.startswith("EI") else "rad/(N m)",
        }
        for key, values in result.intervals.items()
    ]
    diagnostics = [
        {"Quantity": TERMS[key].label, "Value": value, "Meaning": TERMS[key].meaning}
        for key, value in [
            ("rank", result.rank),
            ("singular", result.singular_values),
            ("correlation", result.correlation),
        ]
    ]
    warnings = "".join("<li>" + escape(note) + "</li>" for note in result.warnings)
    return (
        report_start(
            "Stiffness identification report",
            "Estimate effective beam bending rigidity and clamp compliance while keeping uncertainty and identifiability visible.",
            result.provenance.title() + " evidence",
            [
                ("status", "Status"),
                ("estimates", "Estimates"),
                ("uncertainty", "Uncertainty"),
                ("warnings", "Warnings"),
                ("record", "Raw record"),
            ],
        )
        + "<section class='card' id='status'><h2>Evidence and status</h2><p>Evidence: <strong>"
        + escape(result.provenance)
        + "</strong>. Status: "
        + escape(result.status)
        + ".</p><p>EI describes beam bending stiffness. Clamp compliance describes rotation per unit moment. Estimates depend on the chosen model and data quality. They do not prove damage or structural safety.</p></section>"
        + (
            "<p>The data cannot separate the requested parameters. No unique estimates are reported.</p>"
            if result.status == "unidentifiable"
            else ""
        )
        + "<section id='estimates'><h2>Estimates and prediction errors</h2>"
        + html_table(estimates, "Estimates and prediction errors")
        + "</section><section class='card' id='uncertainty'><h2>Uncertainty</h2><p>These approximate 95% ranges depend on the stated model and noise assumptions. A range reaching zero compliance does not prove a perfectly rigid clamp.</p>"
        + html_table(intervals, "Approximate uncertainty ranges")
        + html_table(diagnostics, "Information supplied by the observations")
        + "</section><section class='card' id='warnings'><h2>Warnings and limits</h2><ul>"
        + warnings
        + "</ul>"
        + "<p>Synthetic means generated by a calculation. Holdout means observations reserved for prediction checks. RMSE measures typical prediction error, in the same units as displacement. Measurement error, support assumptions and geometry errors can affect the estimates.</p>"
        + "</section><details id='record'><summary>Raw record for reproduction</summary><p>Field names are unchanged.</p><pre>"
        + escape(json.dumps(payload, indent=2, allow_nan=False))
        + "</pre></details>"
        + report_end()
    )


def save_solution(directory: str | Path, model: Model, result: SolveResult):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "model.json").write_text(
        json.dumps(model_to_dict(model), indent=2, allow_nan=False), encoding="utf-8"
    )
    (directory / "results.json").write_text(
        json.dumps(result_dict(model, result), indent=2, allow_nan=False), encoding="utf-8"
    )
    (directory / "nodes.csv").write_text(results_csv(result), encoding="utf-8")
