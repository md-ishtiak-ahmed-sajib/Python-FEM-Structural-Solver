# Features and their current status

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


**Complete** means the software exists and its listed checks passed. It does not mean that the results have been confirmed by physical tests.

| ID | Feature | Status | Evidence |
|---|---|---|---|
| F-001 | Bar and truss calculations | Complete | Hand solutions, stress checks and OpenSees comparison |
| F-002 | Beam and frame calculations | Complete | Beam formulas, frame comparison and member-direction checks |
| F-003 | Supports, known movements and springs | Complete | Settlement, reaction and energy checks |
| F-004 | JSON model files and unit conversion | Complete | File round trips and invalid-input checks |
| F-005 | Local model and results views | Complete | App tests and browser review |
| F-006 | Calculation inspection | Complete | Element matrices, coordinate changes and equations shown |
| F-007 | Stiffness estimates and failure messages | Complete | Known-parameter recovery and ambiguous-case checks |
| F-008 | Repeatable synthetic study | Complete | Full study run and repeatability checks |
| F-009 | Result exports | Complete | JSON, CSV, HTML and figure checks |
| F-010 | Real-measurement import and reporting | Complete | File and metadata validation; empty templates rejected |
| F-011 | Physical validation | Pending | Real equipment, calibration and observations are needed |
| F-012 | Another person's reproduction | Pending | No independent user run is claimed |
| F-013 | Public GitHub repository | Complete | [Public source repository](https://github.com/md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver), reviewed attribution and security reporting |
| F-014 | Define, Understand, Solve learning route | Implemented and locally checked | All four family workflows; no hidden solve; draft and stale-result tests |
| F-015 | Shared terminology help and glossary | Implemented; broader accessibility review pending | 99 shared terms; browser hover, focus, pointer activation and narrow-window checks |
| F-016 | One-change comparisons | Complete for checked cases | Baseline preservation, load/property changes and visible mechanism failures |
| F-017 | Learning-project and learning-report exports | Complete for checked cases | Versioned wrapper, recomputation rules, escaped text and embedded plotting code |
| F-018 | Connected theory and README visuals | Complete | Engine equations, original family diagram, reproducible convergence graph and documentation link checks |

## How the parts depend on each other

The stiffness study depends on the checked beam solver. A physical comparison depends on that study, the measurement importer and real test records.

Read [verification](../07-testing-and-evidence/verification.md) for check methods and [evidence status](../07-testing-and-evidence/evidence-status.md) for what the results can support.

A future change must update this page only after its checks are complete.

## Read next

- [What the software must do](requirements.md)
