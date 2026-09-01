# Repeat the synthetic study

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


A protocol records the settings before interpreting results. Synthetic observations come from equations, not physical measurements.

## Research question

Can static movements separate EI from clamp compliance C? How do noise, support assumptions and missing shear deformation affect the answer?

This is an established research area. This project provides an open implementation and a study that can be repeated. It does not assume publication novelty.

## Fixed settings

| Item | Values |
|---|---|
| Beam length L | 1 m |
| Rectangular width | 0.02 m |
| Young's modulus E | 70 GPa |
| Poisson's ratio nu | 0.3 |
| Slenderness L/h | 10, 20, 50, 100 |
| Dimensionless clamp compliance gamma=EI C/L | 0, 0.01, 0.1 |
| Data generators | Analytical Euler–Bernoulli and Timoshenko formulas |
| Timoshenko shear factor | 5/6 for the rectangular reference |
| Noise standard deviation | 0%, 0.25%, 1%, 3% of the defined characteristic displacement |
| Random seed | 2027 |
| Planned repeats for each configuration | 200 |

Depth h follows from L/h. These material and section values are chosen synthetic inputs, not measured specimen properties.

Euler–Bernoulli leaves out shear deformation. Timoshenko includes it. Fitting an Euler–Bernoulli model to Timoshenko-generated data tests the effect of omitted physics.

## Measurement positions

Compare four layouts: tip only; two fixed positions at 0.5L and L; two positions chosen from 0.25L, 0.5L, 0.75L and L; and all four positions.

The chosen pair maximizes the smallest singular value with fixed parameter scaling. This is called E-optimal selection. In simple terms, it chooses the pair that best separates the weakest parameter-information direction within the candidate set and assumed model.

## Training and prediction loads

Use one of three training patterns:

1. A unit force at the tip.
2. Forces of 1, 2 and 3 at the tip.
3. A unit force at 0.75L and at L.

Reserve the unit force at 0.5L for prediction checks. Reserved, or holdout, observations do not affect the fit or the sensor choice.

These normalized force values are computational settings, not suggested bench loads.

## Noise definition

Characteristic displacement is the Euler–Bernoulli tip deflection under a unit tip force for the same EI and clamp.

Noise has a zero-mean Gaussian distribution and is independent between observations. At 0% noise, no random perturbation is added. A tiny positive numerical weight scale is still used.

The study treats force and geometry as exact. Real tests will also have errors in these quantities.

## Fit and compare

Fit both rigid and flexible support models to the same observations in each configuration. The full combination has 2,304 configurations.

A configuration with insufficient sensitivity rank gets no parameter estimate. Count it separately. In the recorded run, 192 configurations were unidentifiable and 422,400 trials were estimated.

The large study uses analytical influence functions and a fast bounded estimator. The app normally builds the influence functions using FEM. Tests compare both influence calculations and compare the fast estimator with SciPy. This difference must remain visible in reports.

## Read the output

Report relative EI bias and RMSE, clamp-compliance bias, reserved-case prediction error, sensitivity measures and failed cases.

Bias is average signed error. RMSE measures typical error size. Reserved-case movement errors are divided by the stated characteristic displacement.

The app uses bootstrap simulation to estimate parameter intervals. These are approximate and depend on the chosen model, fixed geometry/forces and independent Gaussian errors. Near a parameter limit, interval interpretation needs extra care.

## Repeat or change the study

Use the commands in [exports and repetition](../04-user-guide/exports.md). Keep the seed and original settings if reproducing the existing report.

If you change a setting, record the reason before interpreting the new results. Keep failures and negative results. Never change a synthetic data label to measured.

## Read next

- [Understand the stiffness research question](research-question.md)
- [Prepare and process real measurements](bench-protocol.md)
