# Why we built this project

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


This project connects structural mechanics, mathematics and Python. It helps a civil engineering student see how a structural model becomes a set of equations, and how those equations give displacement, force and stress.

## The engineering goal

A structural engineer must choose a model before solving it. The choice matters. A pin, a fixed support and a flexible clamp can give different answers even when the beam and load are unchanged.

We built a small solver so that these choices are visible. You can inspect the stiffness of one member, follow its contribution to the whole structure, and check the final result.

## What we have built

| Part | What it does | Why it helps |
|---|---|---|
| Bar and truss solver | Calculates axial movement, force and stress | Connects equilibrium and material stiffness |
| Beam and frame solver | Calculates bending, rotation and member forces | Connects beam theory to matrix methods |
| Local browser app | Shows models, results and calculation steps | Makes the calculation easier to explore |
| Stiffness study | Estimates beam stiffness and clamp flexibility | Shows why a good numerical fit may still be uncertain |
| Tests and reports | Compare results with known answers | Give readers evidence they can check |

The solver runs on your computer. The calculation code does not depend on the browser interface.

## The research goal

Can a few beam-deflection measurements tell us whether the beam is flexible, the clamp is flexible, or both?

This is useful because an incorrect support assumption can lead to an incorrect stiffness estimate. The project studies that problem using computer-generated data. The tools for real measurements are ready, but real bench tests are still pending.

Read the [research question](../05-research-and-experiments/research-question.md) for a simple explanation.

## Benefits and honest limits

Students can compare hand calculations with code, teachers can explain assembly, and contributors can check or extend a small codebase. These are intended uses; this repository does not claim measured teaching outcomes or adoption by other institutions.

FEM and stiffness identification already exist. Our contribution is an open implementation that connects calculations, explanations, tests and one repeatable study. We do not claim to have invented FEM or a new identification method.

This is not a building-design or safety-checking tool. It does not check design codes, buckling, earthquakes, yielding or large movement.

## Graduate application purpose

The owner intends to use this work as part of a graduate application. The useful evidence is the question, the decisions, the checks, the limitations and the owner's real contribution.

The first implementation used substantial AI assistance. Personal work must be described honestly. A project does not guarantee admission. See the [authorship record](../08-contributing-and-release/ai-and-authorship.md).

## Goals that remain open

Complete supervised bench measurements, ask another person to repeat the software workflow, and prepare the public repository. These are separate tasks. See [current evidence](../07-testing-and-evidence/evidence-status.md).

## Read next

- [What the software must do](requirements.md)
