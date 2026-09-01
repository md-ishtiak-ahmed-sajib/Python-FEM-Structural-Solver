# Prepare and process real measurements

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


**No physical experiment is claimed in this repository.** This page is a preparation guide and data-processing workflow. Empty templates are not measurements.

## 1. Check feasibility before choosing loads

Work with suitable laboratory supervision. Borrow a beam, a secure fixture, a displacement instrument, calipers and calibrated loading equipment.

Record specimen material, section dimensions at several points, free length, fixture details, instrument range and resolution, and how the force is checked.

Choose physical loads only after checking the specimen, fixture, instrument limits, elastic stress range and small-movement assumption. The synthetic unit forces are not safe-load recommendations.

Do not loosen or weaken a fixture to create an unsafe flexible support. Stop if you see slip, permanent deformation, instability or unexplained differences between loading and unloading.

## 2. Check the measurement system

Calibration means comparing an instrument with a suitable reference. Record the calibration method and date.

Check whether the indicator's contact force changes the movement of a flexible specimen. Check fixture translation separately because the fitted model allows clamp rotation but assumes no clamp translation.

Take a zero reading before loading at each measurement position. Watch for zero drift after unloading.

## 3. Plan observations before fitting

Candidate sensing locations are 0.25L, 0.5L, 0.75L and L. Candidate load locations are 0.5L, 0.75L and L. Record actual locations, not only nominal ones.

Reserve the 0.5L load arrangement for checking predictions. Do not use those values to tune the fitted parameters.

Repeat loading and unloading cycles. Record readings before loading, under load and after unloading. Securely remove and remount the specimen if the supervised setup allows it, then repeat to study mounting effects.

One indicator can be moved between positions for a static test. Those readings are not simultaneous. Record timing, drift and run IDs.

## 4. Keep raw data and test details

Use these files as empty starting points:

- [Measurement CSV template](../../data/bench/measurements-template.csv).
- [Specimen and equipment metadata template](../../data/bench/metadata-template.json).

Metadata means details about the test. Fill specimen dimensions, fixture checks, instrument calibration, load calibration and the uncertainty method.

Keep raw instrument readings unchanged in a separate file. Record any excluded reading and the reason. Never replace a missing reading with a model prediction.

The importer subtracts zero_m from raw_displacement_m. Positive force and deflection are downward. Enter positions and readings in SI units.

Set provenance to measured only for actual observations. Set split to train or holdout before fitting. Give each observation and test run a clear ID.

## 5. State measurement uncertainty

sigma_m must be a positive standard uncertainty in metres. Estimate it using calibration information and repeated readings; instrument resolution alone may not describe the full error.

Also record uncertainty in dimensions, load values and positions. The current fitted intervals do not propagate those uncertainties.

Errors from the same run may be correlated. The current bootstrap assumes independent errors. Compare remounting runs separately before combining them or claiming general agreement.

## 6. Import and analyze

Use Measured CSV in the app and upload both files. The importer rejects incomplete metadata and wrong column names.

You can also run this example command after replacing the paths with your real files:

~~~powershell
.\.venv\Scripts\python -m fem_solver fit results/my-test/readings.csv --metadata results/my-test/metadata.json --length 1 --ei-reference 1000 --output results/my-test/flexible-fit
~~~

Here --length must equal the measured free length in the metadata. --ei-reference is a numerical scale, not an assumed measured EI. Replace these example numbers with suitable values for the recorded specimen.

Repeat with --support rigid to compare assumptions. Review parameter intervals, sensitivity, reserved-case prediction errors and differences between mounting runs.

The report records the input-file fingerprint. Do not overwrite your raw file with the corrected observation export.

## 7. Report honestly

A small error does not prove that the clamp behaves as a linear rotational spring. If the model fails, keep the result and explain possible causes.

Report effective EI and C. Do not infer E and I separately, claim damage, or certify structural safety.

Keep physical findings pending until real records are supplied and reviewed. Before publishing, check permission, privacy and laboratory rules. The public source includes templates only.

## Read next

- [Repeat the synthetic study](study-protocol.md)
- [Read the generated research report](research-report.md)
