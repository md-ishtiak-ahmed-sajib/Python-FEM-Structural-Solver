# Decision 2: fit beam and clamp compliance

[Project home](../../../README.md) · [Documentation map](../../README.md) · [Section guide](README.md)


Status: accepted.

## Need

A rigid clamp has zero rotational compliance but infinite rotational stiffness. Fitting stiffness directly would make that limit awkward.

For the selected cantilever, movement is linear in 1/EI and clamp compliance C. We can use that structure instead of a more complicated nonlinear search.

## Choice

Fit beta=EI_ref/EI and gamma=EI_ref C/L using bounded weighted least squares. The bounds keep the fitted compliances nonnegative. A gamma of zero represents a rigid clamp.

The normal fit builds sensitivity columns using FEM solutions. Separate analytical equations check those columns.

## Alternatives considered

A general nonlinear optimizer would add unnecessary difficulty for this particular equation. Adding regularization to an ambiguous case could hide the fact that the observations do not give a unique answer.

The solver therefore reports rank failure without inventing a unique parameter pair.

## Effects of the choice

This fitting API applies to the stated cantilever assumptions, not arbitrary frame updating.

Intervals still depend on the assumed model and measurement-error distribution. The full synthetic study uses analytical influence functions and a separately checked fast bounded estimator to reduce run time.

## Read next

- [Decision 1: local Python and browser app](ADR-0001-local-python.md)
