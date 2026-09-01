"""Seeded synthetic study with independent analytical EB/Timoshenko generators."""

import csv
import json
from pathlib import Path

import numpy as np

from .identification import (
    IdentificationConfig,
    Observation,
    analytical_deflection,
    design_matrix,
    select_measurement_positions,
)


def synthetic_observations(
    EI=1000.0,
    compliance=2e-5,
    noise_fraction=0.0025,
    positions=(0.25, 0.5, 0.75, 1.0),
    load_design="locations",
    seed=2027,
):
    rng = np.random.default_rng(seed)
    if load_design == "single":
        patterns = [(1.0, 1.0)]
    elif load_design == "amplitudes":
        patterns = [(1.0, f) for f in [1.0, 2.0, 3.0]]
    else:
        patterns = [(0.75, 1.0), (1.0, 1.0)]
    scale = float(analytical_deflection(1.0, 1.0, 1.0, EI, compliance))
    sigma = max(abs(scale) * noise_fraction, abs(scale) * 1e-10)
    data: list[Observation] = []
    for split, cases in [("train", patterns), ("holdout", [(0.5, 1.0)])]:
        for a, force in cases:
            for x in positions:
                value = float(analytical_deflection(x, a, force, EI, compliance))
                observed = value + rng.normal(0, sigma) if noise_fraction else value
                data.append(Observation(str(len(data)), x, a, force, observed, sigma, split))
    return data


def run_study(output: str | Path, trials=200, seed=2027, quick=False) -> dict:
    """Run a declared grid; vectorized positive least squares, exact active boundaries.

    Fast study estimator is independently tested against the public bounded SciPy fit.
    Primary UI/API uses FEM influence functions; this runner uses the analytical
    influence matrix, cross-verified by tests and the independent reference script.
    """
    if trials < 1:
        raise ValueError("trials must be positive")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    rows = []
    slendernesses = [20, 100] if quick else [10, 20, 50, 100]
    designs = ["single", "amplitudes", "locations"]
    for slenderness in slendernesses:
        L, E, nu, width = 1.0, 70e9, 0.3, 0.02
        height = L / slenderness
        area = width * height
        EI = E * width * height**3 / 12
        G = E / (2 * (1 + nu))
        for gamma in [0.0, 0.01, 0.1]:
            compliance = gamma * L / EI
            for theory in ["Euler-Bernoulli", "Timoshenko"]:
                for design in designs:
                    selected, _ = select_measurement_positions(
                        L,
                        [0.25, 0.5, 0.75, 1.0],
                        2,
                        [(1.0, 1.0)] if design != "locations" else [(0.75, 1.0), (1.0, 1.0)],
                        EI,
                    )
                    sensor_sets = {
                        "one": [1.0],
                        "two_uniform": [0.5, 1.0],
                        "two_selected": selected,
                        "four": [0.25, 0.5, 0.75, 1.0],
                    }
                    for sensors, positions in sensor_sets.items():
                        template = synthetic_observations(EI, compliance, 0.0, positions, design)
                        train = np.array([o.split == "train" for o in template])
                        true_y = np.array([o.displacement for o in template])
                        if theory == "Timoshenko":
                            true_y += np.array(
                                [
                                    o.force * min(o.x, o.load_position) / ((5 / 6) * G * area)
                                    for o in template
                                ]
                            )
                        characteristic = float(analytical_deflection(L, L, 1.0, EI, compliance))
                        for noise in [0.0, 0.0025, 0.01, 0.03]:
                            sigma = max(characteristic * noise, characteristic * 1e-10)
                            observed = true_y[:, None] + (
                                rng.normal(0, sigma, (len(template), trials))
                                if noise
                                else np.zeros((len(template), trials))
                            )
                            for support in ["rigid", "flexible"]:
                                config = IdentificationConfig(L, EI, support, 0, seed, "analytical")
                                X = design_matrix(template, config)
                                A = X[train] / sigma
                                s = np.linalg.svd(A, compute_uv=False)
                                rank = int(np.sum(s > s[0] * 1e-10))
                                row = {
                                    "provenance": "synthetic",
                                    "slenderness": slenderness,
                                    "gamma": gamma,
                                    "generator": theory,
                                    "load_design": design,
                                    "sensors": sensors,
                                    "sensor_positions": ";".join(map(str, positions)),
                                    "noise_fraction": noise,
                                    "support_model": support,
                                    "trials": trials,
                                    "rank": rank,
                                    "status": "identified"
                                    if rank == X.shape[1]
                                    else "unidentifiable",
                                }
                                if rank == X.shape[1]:
                                    beta = batch_compliance_fit(A, observed[train] / sigma)
                                    estimates = EI / beta[0]
                                    predicted = X @ beta
                                    row.update(
                                        {
                                            "EI_relative_bias": float(np.mean(estimates / EI - 1)),
                                            "EI_relative_rmse": float(
                                                np.sqrt(np.mean((estimates / EI - 1) ** 2))
                                            ),
                                            "holdout_relative_rmse": float(
                                                np.sqrt(
                                                    np.mean(
                                                        (predicted[~train] - true_y[~train, None])
                                                        ** 2
                                                    )
                                                )
                                                / characteristic
                                            ),
                                            "compliance_absolute_bias": float(
                                                np.mean(beta[1] * L / EI - compliance)
                                            )
                                            if len(beta) == 2
                                            else -compliance,
                                        }
                                    )
                                rows.append(row)
    columns = list(dict.fromkeys(k for row in rows for k in row))
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "provenance": "synthetic",
        "seed": seed,
        "trials_per_configuration": trials,
        "configurations": len(rows),
        "planned_fit_trials": len(rows) * trials,
        "estimated_fit_trials": sum(r["status"] == "identified" for r in rows) * trials,
        "unidentifiable_configurations": sum(r["status"] == "unidentifiable" for r in rows),
        "quick": quick,
        "noise_scale": "Euler-Bernoulli tip movement under a unit tip force for the same EI and clamp",
        "uncertainty": "Independent Gaussian movement noise; geometry and force are exact. No comparison with real measurements is claimed.",
        "note": "A unit force only scales this linear calculation. It is not a suggested bench load.",
    }
    (output / "manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _study_plot(rows, output)
    return summary


def batch_compliance_fit(A, B):
    """Exact active-set solution for 1/2 variables, matching the public bounds."""
    lower = np.zeros((A.shape[1], 1))
    lower[0] = 1e-12
    shifted = B - A @ lower
    unconstrained = np.linalg.lstsq(A, shifted, rcond=None)[0]
    candidates = [np.maximum(unconstrained, 0), np.zeros_like(unconstrained)]
    for j in range(A.shape[1]):
        candidate = np.zeros_like(unconstrained)
        candidate[j] = np.maximum(A[:, j] @ shifted / (A[:, j] @ A[:, j]), 0)
        candidates.append(candidate)
    costs = np.array([np.sum((A @ c - shifted) ** 2, axis=0) for c in candidates])
    stack = np.stack(candidates)
    best = np.argmin(costs, axis=0)
    return stack[best, :, np.arange(B.shape[1])].T + lower


def _study_plot(rows, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5), layout="constrained")
    for support, color in [("rigid", "#E69F00"), ("flexible", "#0072B2")]:
        selected = [
            r
            for r in rows
            if r["slenderness"] == 20
            and r["gamma"] == 0.1
            and r["generator"] == "Euler-Bernoulli"
            and r["load_design"] == "locations"
            and r["sensors"] == "four"
            and r["support_model"] == support
        ]
        ax.plot(
            [100 * r["noise_fraction"] for r in selected],
            [100 * r["EI_relative_rmse"] for r in selected],
            "o-",
            label=support + " support fit",
            color=color,
        )
    ax.set(
        xlabel="Displacement noise / characteristic displacement (%)",
        ylabel="EI relative RMSE (%)",
        title="Synthetic study · support assumptions and stiffness error",
    )
    ax.grid(alpha=0.2)
    ax.legend()
    fig.savefig(output / "stiffness_error.png", dpi=180)
    fig.savefig(output / "stiffness_error.svg")
    plt.close(fig)
