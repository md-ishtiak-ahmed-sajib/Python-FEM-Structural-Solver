# What the software must do

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


A requirement says what the project must provide. A test or review checks whether it does so.

## Main tasks

1. Create or load a structure, solve it and save the results.
2. Follow a result back to the element matrix and assembled equations.
3. Estimate beam stiffness and clamp flexibility from deflection observations.
4. Repeat a numerical study without using the browser.
5. Keep generated data separate from real measurements.

## Requirements

| ID | Requirement | Where to understand or check it |
|---|---|---|
| FR-001 | Solve bar, truss, beam and frame models | [FEM basics](../03-engineering-knowledge/fem-basics.md) |
| FR-002 | Apply supports, known movements, springs and separate load cases | [Units and supports](../03-engineering-knowledge/units-and-signs.md) |
| FR-003 | Calculate movement, reactions, member forces and normal stress | [Equations](../03-engineering-knowledge/numerical-methods.md) |
| FR-004 | Show matrices, coordinate changes and boundary conditions | [App guide](../04-user-guide/app-guide.md) |
| FR-005 | Read and write model files with a version and declared units | [Python and JSON](../04-user-guide/python-and-json.md) |
| FR-006 | Estimate EI and clamp compliance, and report uncertainty or failure | [Research question](../05-research-and-experiments/research-question.md) |
| FR-007 | Check real-measurement files and their test details | [Bench protocol](../05-research-and-experiments/bench-protocol.md) |
| FR-008 | Repeat studies with saved settings and seeds | [Study protocol](../05-research-and-experiments/study-protocol.md) |

## Supported model

The first version assumes elastic material, small movement and static loads. Static means that acceleration is not included. Each model uses one element family. A frame element already combines axial and bending behavior.

Loads can be nodal forces or moments. Beam and frame members can also carry uniform distributed loads. Supports act along the listed global degrees of freedom.

## Not included

There are no internal member hinges or end releases, inclined rollers, linked-node constraints, mixed element families, nonlinear analysis, dynamics, buckling, plate/shell elements or 3D solids. No design-code or real-structure safety approval is provided.

## Software conditions

The tested Python version is 3.12. Internal calculations use SI units. The app runs at localhost, which means your own computer. It needs no account, database or paid API.

Invalid models must produce clear errors. The solver must not hide an unstable structure by adding imaginary stiffness.

## Completion rule

A feature is complete when its relevant tests and documentation are complete. Software completion does not mean that a physical experiment has been completed.

The 26-week guide is optional study material. Development has no weekly waiting periods.

## Read next

- [Why we built this project](vision-and-goals.md)
- [Features and their current status](features.md)
