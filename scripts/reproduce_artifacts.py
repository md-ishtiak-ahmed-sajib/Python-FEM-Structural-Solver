"""Regenerate public examples, convergence evidence and synthetic research report."""

import csv
import hashlib
import json
import platform
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fem_solver import __version__, model_from_dict, solve_linear
from fem_solver.examples import NAMES, example_data
from fem_solver.identification import CSV_COLUMNS, observations_csv
from fem_solver.study import run_study, synthetic_observations


def examples():
    folder = Path("examples")
    folder.mkdir(exist_ok=True)
    for name in NAMES:
        (folder / (name.lower().replace(" ", "_") + ".json")).write_text(
            json.dumps(example_data(name), indent=2), encoding="utf-8"
        )
    (folder / "synthetic_observations.csv").write_text(
        observations_csv(synthetic_observations()), encoding="utf-8"
    )
    folder = Path("data/bench")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "measurements-template.csv").write_text(
        ",".join(CSV_COLUMNS) + "\n", encoding="utf-8"
    )
    metadata = {
        "provenance": "measured",
        "specimen": {"description": "", "free_length_m": None, "width_m": None, "depth_m": None},
        "fixture": {"description": "", "translation_check": ""},
        "instrument": {"description": "", "resolution_m": None, "calibration_record": ""},
        "load_calibration": "",
        "uncertainty_method": "",
        "processing_notes": "",
    }
    (folder / "metadata-template.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def convergence():
    rows = []
    EI, L, q = 1.6e6, 3.0, -1000.0
    for count in [1, 2, 4, 8, 16]:
        data = {
            "schema_version": 1,
            "units": "N-m-Pa",
            "kind": "beam",
            "nodes": [{"id": str(i), "x": L * i / count} for i in range(count + 1)],
            "materials": [{"id": "m", "E": 200e9}],
            "sections": [{"id": "s", "A": 0.003, "I": 8e-6}],
            "elements": [
                {"id": str(i), "start": str(i), "end": str(i + 1), "material": "m", "section": "s"}
                for i in range(count)
            ],
            "constraints": [{"node": "0", "dof": "uy"}, {"node": "0", "dof": "rz"}],
            "distributed_loads": [{"element": str(i), "qy": q} for i in range(count)],
        }
        result = solve_linear(model_from_dict(data))
        error_integral, exact_integral = 0.0, 0.0
        for i in range(count):
            d = result.members[str(i)]["local_displacements"]
            h = L / count
            t = np.linspace(0, 1, 101)
            x = (i + t) * h
            interpolant = (1 - 3 * t * t + 2 * t**3) * d[0] + h * (t - 2 * t * t + t**3) * d[1]
            interpolant += (3 * t * t - 2 * t**3) * d[2] + h * (-t * t + t**3) * d[3]
            exact = q * x * x * (6 * L * L - 4 * L * x + x * x) / (24 * EI)
            error_integral += np.trapezoid((interpolant - exact) ** 2, x)
            exact_integral += np.trapezoid(exact**2, x)
        rows.append(
            {
                "elements": count,
                "relative_L2_Hermite_error": float(np.sqrt(error_integral / exact_integral)),
            }
        )
    folder = Path("reports/verification")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "convergence.json").write_text(
        json.dumps(
            {
                "field": "unenriched Hermite displacement",
                "note": "The exported field includes an exact uniform-load correction for this constant-section beam.",
                "results": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    fig, ax = plt.subplots(figsize=(7, 4), layout="constrained")
    ax.loglog(
        [r["elements"] for r in rows],
        [r["relative_L2_Hermite_error"] for r in rows],
        "o-",
        color="#2563EB",
    )
    ax.set(
        xlabel="Number of elements",
        ylabel="Relative L2 displacement error",
        title="Beam deflection error before the uniform-load correction",
    )
    ax.grid(which="both", alpha=0.2)
    fig.savefig(folder / "convergence.png", dpi=180)
    plt.close(fig)
    return rows


def report(manifest, convergence_rows):
    with Path("reports/synthetic/summary.csv").open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    selected = [
        r
        for r in rows
        if r["slenderness"] == "20"
        and r["gamma"] == "0.1"
        and r["generator"] == "Euler-Bernoulli"
        and r["load_design"] == "locations"
        and r["sensors"] == "four"
    ]
    table = "\n".join(
        f"| {100 * float(r['noise_fraction']):g}% | {r['support_model']} | {100 * float(r['EI_relative_bias']):.5f}% | {100 * float(r['EI_relative_rmse']):.5f}% | {100 * float(r['holdout_relative_rmse']):.5f}% |"
        for r in selected
    )
    convergence_table = "\n".join(
        f"| {r['elements']} | {r['relative_L2_Hermite_error']:.8e} |" for r in convergence_rows
    )
    source_hash = hashlib.sha256(
        b"".join(p.read_bytes() for p in sorted(Path("src/fem_solver").glob("*.py")))
    ).hexdigest()
    text = f"""# Read the generated research report

[Project home](../../README.md) · [Documentation map](../README.md) · [Research guide](README.md)

**Data source: synthetic.** All observations in this report came from equations. No real beam measurements or reproduction by another person are claimed.

## What we asked

Can a few static beam-deflection observations separate beam bending stiffness EI from rotational clamp compliance C?

A clamp that rotates can make a beam appear more flexible. If the model assumes a perfectly rigid clamp, it may compensate by estimating an EI that is too low.

This is an established structural-identification problem. Our contribution is the connected software, open settings, clear failure cases and repeatable results.

## Read this before the numbers

EI is E multiplied by I. These observations do not identify E and I separately.

C is rotation per unit moment at the clamp. The fitted model assumes the clamp does not translate. For a downward load P at a and an observation at x:

~~~text
v(x) = P B(x,a)/EI + P a x C
~~~

The [equation guide](../03-engineering-knowledge/numerical-methods.md) defines B. The [simple research explanation](research-question.md) explains why one sensor can be ambiguous.

## How the study was run

The [study protocol](study-protocol.md) specifies {manifest["configurations"]:,} configurations and {manifest["trials_per_configuration"]} planned repeats per configuration, using random seed {manifest["seed"]}.

Of these, {manifest["unidentifiable_configurations"]} configurations lacked enough independent information and received no estimates. The study estimated parameters in {manifest["estimated_fit_trials"]:,} trials.

The study compares four slenderness ratios, three clamp-flexibility values, four sensor layouts, three load patterns and four noise levels. It generates data using separate Euler–Bernoulli and Timoshenko formulas. Timoshenko includes shear deformation; the fitted beam model does not.

The large study uses analytical influence functions and a fast bounded fitting method checked against SciPy. The app normally obtains its influence functions from FEM calculations. Tests compare the analytical and FEM versions.

Sensor selection uses the assumed model before fitting. Reserved load cases do not influence the fit. Both support models receive the same observations in a configuration.

The added noise is independent and Gaussian. Its size is a percentage of the stated characteristic displacement. At 0% noise, no perturbation is added. Force and geometry are exact in this synthetic study.

## One planned comparison

This table selects L/h=20, gamma=0.1, four sensors, varied training load positions and Euler–Bernoulli-generated observations. The numbers come from the saved output.

**Bias** is average signed error. A negative EI bias means underestimation. **RMSE** measures typical error size. The last column compares reserved-case movement errors with the characteristic displacement.

| Noise | Fitted support | EI relative bias | EI relative RMSE | Reserved-case normalized RMSE |
|---|---|---|---|---|
{table}

![Synthetic study comparing EI errors under rigid and flexible support assumptions](../../reports/synthetic/stiffness_error.png)

In the zero-noise row shown here, the rigid-support fit underestimates EI, while the flexible-support fit recovers the chosen synthetic parameters closely. In this selected comparison, larger noise increases the flexible fit's error. This is not a guarantee for every configuration or real specimen.

Read the full [summary CSV](../../reports/synthetic/summary.csv) and [settings file](../../reports/synthetic/manifest.json), not only this figure.

A flexible fit has an extra unknown. Compare uncertainty and reserved-case error as well as agreement on training observations. Differences with Timoshenko-generated data can reveal missing shear effects; they are not automatically an error in the Euler–Bernoulli code.

## A useful failure case

One sensor with one load position and repeated load magnitudes is a negative control: a case expected to lack enough information.

Increasing force scales both bending and clamp rotation together. The sensitivity rows remain proportional. The software reports that it cannot give a unique two-parameter estimate.

Failure to identify the parameters is a useful result, not a reason to hide the case.

## Checks against known answers

[OpenSees results](../../reports/verification/opensees.json) contain matching bar, truss, beam, frame and spring comparisons, plus Timoshenko references.

Automatic tests also check reactions, work, units, member directions and invalid models. See [verification](../07-testing-and-evidence/verification.md).

## Does a finer mesh reduce approximation error?

The table below measures the cubic Hermite displacement field before the exact uniform-load correction. It compares that field with the analytical quartic solution.

The exported field already includes the correction for this uniform-beam case. Testing that corrected field would not be a meaningful demonstration of convergence.

| Elements | Relative L2 error of the cubic field |
|---|---|
{convergence_table}

![Reduction of actual displacement approximation error with more beam elements](../../reports/verification/convergence.png)

Relative L2 error compares the size of the error over the beam with the size of the exact deflection field. The results show how this particular interpolation error decreases with a finer mesh.

## How much confidence should we place in estimates?

The app uses repeated simulated observations, called a parametric bootstrap, to report approximate intervals. The intervals depend on the beam model, fixed geometry and force values, and independent Gaussian measurement errors.

They do not include unknown zero drift, force error, dimension error, clamp translation or all effects missing from the model.

Near a rigid clamp, the compliance interval may include zero. Report a compliance range. Do not turn a near-zero estimate into a falsely precise very large spring stiffness.

Full sensitivity rank is necessary for a unique fit, but it does not guarantee useful precision. Strong parameter correlation or wide intervals can still make estimates weak.

## Physical work is still pending

The [bench protocol](bench-protocol.md) covers specimen measurements, a secure fixture, calibration, zero readings, repeated loading, remounting and reserved prediction cases.

The CSV importer and report writer are ready. Empty templates do not count as data. A later small experimental residual would still not prove that the clamp is a linear rotational spring.

No damage detection or structural safety conclusion is made.

## Repeat this report

From the project root, run python scripts/reproduce_artifacts.py in the installed full environment. Run the OpenSees script in its separate environment.

Software version: {__version__}. Python: {platform.python_version()}. Platform: {platform.system()} {platform.machine()}.

Core-source SHA-256: {source_hash}.

The hash is a fingerprint of the source files used for this report. It helps detect changes; it is not evidence of physical correctness.

## Read next

- [Study protocol](study-protocol.md).
- [Bench preparation](bench-protocol.md).
- [What the evidence supports](../07-testing-and-evidence/evidence-status.md).
- [Sources](../03-engineering-knowledge/references.md) and [AI assistance](../08-contributing-and-release/ai-and-authorship.md).
"""
    Path("docs/05-research-and-experiments/research-report.md").write_text(text, encoding="utf-8")


def main():
    examples()
    convergence_rows = convergence()
    manifest = run_study("reports/synthetic", trials=200)
    report(manifest, convergence_rows)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
