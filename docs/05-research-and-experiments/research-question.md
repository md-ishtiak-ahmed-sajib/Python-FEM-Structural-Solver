# Understand the stiffness research question

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


**When can a few static-deflection measurements separate beam bending stiffness from clamp flexibility?**

A cantilever is fixed at one end and free at the other. A real clamp may rotate slightly. If we assume the clamp is perfectly fixed, we may blame all extra movement on the beam.

## Two causes of movement

~~~mermaid
flowchart LR
    A["Downward load"] --> B["Beam bends: depends on EI"]
    A --> C["Clamp rotates: depends on C"]
    B --> D["Measured downward movement"]
    C --> D
    D --> E["Can the observations separate both effects?"]
~~~

EI is flexural rigidity: Young's modulus E times second moment of area I. C is rotational clamp compliance: rotation per unit moment. A larger C means a more flexible clamp.

For this model:

~~~text
measured movement = bending contribution + clamp-rotation contribution
v(x) = P B(x,a)/EI + P a x C
~~~

P is force, a is load position and x is measurement position. The [equation guide](../03-engineering-knowledge/numerical-methods.md) defines B.

## Why more readings may not solve the problem

With one sensor and one load position, both effects appear in one number. Several pairs of EI and C may give that number.

Repeating the same arrangement with twice the force simply doubles both effects in a linear model. It does not add a second independent relation.

Changing the measurement or load position may help because bending and clamp rotation vary differently along the beam. The program checks this using a sensitivity matrix.

## The three comparisons

| Approach | Unknowns | What it helps us study |
|---|---|---|
| Assume a rigid clamp | EI | Error caused by an incorrect support assumption |
| Allow a flexible clamp | EI and C | Whether both effects can be estimated |
| Choose sensor positions using sensitivity | EI and C | Whether the available observations can separate them better |

Sensitivity-based selection uses the assumed model before reading the observations. It does not choose sensors after seeing which measurements give a preferred answer.

## What a result means

An **identified** result means a fit was possible under the chosen assumptions. It does not prove that the real beam and clamp follow those assumptions.

An **unidentifiable** result means the information is not enough for unique estimates. The program gives no unique parameter pair.

An **uncertainty interval** shows how estimates vary under the assumed random measurement errors. It does not include every possible error. Force, geometry, zero drift and clamp translation may need separate treatment.

If the interval for C reaches zero, a rigid clamp is still consistent with that resolution. Report a compliance range rather than a very large, falsely precise spring stiffness.

## What we must not conclude

Bending observations identify EI, not E and I independently. An estimated stiffness is not proof of damage. A good fit is not a safety certificate.

The current report uses synthetic data: values generated from equations. It contains no experimental agreement. See [evidence status](../07-testing-and-evidence/evidence-status.md).

## Try it

In the Stiffness study view, compare four measurement positions with one. Then compare changing load positions with changing only load magnitude.

Read the [study protocol](study-protocol.md) for the full settings and the [research report](research-report.md) for computed results.

## Read next

- [Repeat the synthetic study](study-protocol.md)
