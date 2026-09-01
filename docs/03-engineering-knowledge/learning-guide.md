# Optional 26-week learning guide

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


This is a reading guide, not a software schedule. The project assumes the owner has already learned the prerequisites. No development task must wait for a particular week.

A student may follow these topics in order, skip familiar topics or use them for revision.

At any point, use [the three-stage app](../04-user-guide/app-guide.md) and [problem-solving guide](problem-solving.md): define a problem, understand the method, predict, solve and compare. No stage requires completing a numbered week.

| Optional week | Topic | Try to explain or do |
|---|---|---|
| 1 | Project purpose and related software | Explain our contribution without saying FEM is new |
| 2 | Units and assumptions | Convert one model between the two unit systems |
| 3 | Virtual work | Derive the axial stiffness matrix |
| 4 | Shape functions | Explain movement and strain between nodes |
| 5 | Assembly | Add the stiffness of two bars by hand |
| 6 | Supports | Separate known and unknown movements |
| 7 | Coordinate changes | Turn a truss member without changing its physical behavior |
| 8 | Truss checks | Find member forces using equilibrium |
| 9 | Beam theory | Explain when neglecting shear deformation may matter |
| 10 | Hermite functions | Relate end movement and rotation to curvature |
| 11 | Distributed loads | Find equivalent end loads |
| 12 | Member results | Explain why end force is not simply k times d under a UDL |
| 13 | Frames | Combine axial and bending stiffness |
| 14 | Springs and work | Check support reactions and elastic energy |
| 15 | Sparse equations | Explain scaling and why mechanisms are rejected |
| 16 | Evidence | Distinguish numerical checks from physical validation |
| 17 | Convergence | Measure how approximation error changes with more elements |
| 18 | Inverse problems | Explain why bending observations identify EI |
| 19 | Identifiability | Show why one sensor with repeated load magnitudes can be ambiguous |
| 20 | Sensor placement | Compare fixed positions with positions chosen by sensitivity |
| 21 | Noise and parameter limits | Explain the bounded fit |
| 22 | Uncertainty | Explain what an interval includes and leaves out |
| 23 | Measurement quality | Check calibration, contact force, zeros and drift |
| 24 | Prediction | Keep reserved observations out of fitting |
| 25 | Repetition | Rebuild results from saved inputs and a seed |
| 26 | Communication | Present an unsuccessful case and an honest conclusion |

## Reading route

Start with [FEM basics](fem-basics.md), [worked examples](worked-examples.md) and [the equations](numerical-methods.md). Then read the [research question](../05-research-and-experiments/research-question.md) and [bench protocol](../05-research-and-experiments/bench-protocol.md).

Use [references](references.md) for deeper lessons. Use [milestones](../09-project-records/milestones.md) for actual software progress.

## Read next

- [Engineering and software glossary](glossary.md)
- [Books, lessons, papers and related software](references.md)
