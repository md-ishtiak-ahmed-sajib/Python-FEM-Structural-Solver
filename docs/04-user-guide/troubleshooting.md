# Understand errors and unexpected results

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


Start with a small model you can check by hand. Do not remove a warning or add a support only to make an answer appear.

| What you see | Possible reason | What to check |
|---|---|---|
| Python or pip command not found | Wrong interpreter path or incomplete installation | Follow the exact [installation commands](../02-getting-started/installation.md) |
| App address does not open | Server is stopped or still starting | Keep its terminal open and read the printed address |
| Port 8501 already in use | Another copy may be running | Use the existing app or stop your earlier server |
| Import error after changing package code | A running server may hold an old imported module | Stop the server with Ctrl+C and start it again |
| Unknown field or wrong schema version | JSON does not follow this model format | Compare it with a supplied example |
| Unknown node or unused node | IDs or connectivity do not match | Check every member endpoint |
| Zero-length member | Both endpoints occupy the same point | Correct coordinates or remove the unintended member |
| Unsupported DOF | The element family has no such movement | Check the DOF table in [FEM basics](../03-engineering-knowledge/fem-basics.md) |
| Singular or unstable model | Missing restraint, disconnected part or mechanism | Draw the free-body diagram and inspect possible motion |
| Ill-conditioned system | Very large stiffness differences or weak restraints | Check units and whether the chosen idealization is suitable |
| Result is 1,000 or much more times too large | Mixed length, modulus, area or I units | Check the full [unit table](../03-engineering-knowledge/units-and-signs.md) |
| Large movement in the picture | Deformation magnification is high | Read the numerical displacement and magnification |
| No bending stress result | Missing fiber distance c, or an axial-only member | Check section data and the chosen element family |
| Stiffness fit is unidentifiable | Measurements do not separate beam and clamp effects | Change sensor or load positions, not only load magnitude |
| Clamp interval includes zero | The data cannot resolve clamp flexibility | Report a compliance range; do not claim a precise spring stiffness |
| Measured file is rejected | Missing units, positive uncertainty, data origin or test details | Use the exact templates and [bench protocol](../05-research-and-experiments/bench-protocol.md) |

## Ask for help with evidence

Provide the smallest model that shows the issue, the command or app steps, the actual result and the expected answer. State units and sign conventions.

For a numerical issue, include a hand calculation or a trustworthy matching reference where possible. Do not post private laboratory details.

See [how to contribute](../08-contributing-and-release/how-to-contribute.md).

## Read next

- [Save results and run commands](exports.md)
