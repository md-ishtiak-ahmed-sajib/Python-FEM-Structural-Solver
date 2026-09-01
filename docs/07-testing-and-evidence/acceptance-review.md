# Plan audit and remaining reviews

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)

This page compares the accepted plan with the actual software. **Implemented** means the feature exists. **Checked locally** means the listed checks ran on this PC. Neither phrase means that a real structure has been tested.

## Implementation and evidence

| Planned work | Status and evidence |
|---|---|
| Bar, truss, beam and frame engine | Implemented; analytical tests and separate OpenSees comparisons |
| Sparse assembly, transformations, prescribed movements and springs | Implemented; symmetry, equilibrium, energy and orientation tests |
| Independent load cases and SI conversion | Implemented; unit round trips and load-case state tests |
| Reject bad properties, malformed inputs and mechanisms | Implemented; invalid-model and failed-solve tests; no artificial stiffness |
| Blank, example and imported starting models | Implemented in Define; incomplete table drafts remain in the session |
| Problem question, scope and node/member target | Implemented; selected portions require cut-boundary notes |
| Separate check and solve actions | Checked by tests that forbid solving in Define and Understand |
| Eight-step method and actual matrix inspection | Implemented; family-specific rules, element values, DOF maps and equations |
| Fair method comparison and guarded hand checks | Implemented; tests reject formulas for mismatching structures |
| Optional prediction without scores | Implemented; saved with the learning project |
| Results, units, reactions, stress, checks and limits | Implemented; sampled extrema are labeled; balance does not mean safety |
| One-change comparison without changing the baseline | Implemented; load, property, support and failure tests |
| No stale model or load-case result | Checked by app tests; a new solve is required after changes |
| Shared terminology and deeper reading | 99 shared definitions; searchable glossary and related guide downloads |
| Hover, focus and activation help | Hover, focus display and pointer activation checked; full keyboard and device reviews remain below |
| Read results without canvas or hover | HTML text tables added for inputs, matrices, results, comparisons and research values |
| Existing JSON plus a separate learning-project wrapper | Implemented; version and type checks; imported results are not trusted |
| Self-contained learning report | Includes problem, method, nodal results, sampled member/stress ranges, checks, comparisons and limits |
| Readable stiffness report | Estimates, units, uncertainty and diagnostic meanings precede the raw reproduction record |
| README equations and three kinds of visuals | Implemented; original family diagram, flowchart and reproducible convergence graph |
| Correct convergence claim | Caption measures the cubic Hermite field before exact uniform-load correction |
| Nine linked documentation folders | Preserved; root index and section links are checked automatically |
| Optional 26-week curriculum | Preserved as reading, never a development delay |
| EI and clamp-compliance study | Implemented; inverse recovery, rank failure, boundary and prediction tests |
| Full synthetic grid | Recorded 2,304 configurations, 200 planned trials each; synthetic only |
| Bench importer, protocol and reports | Implemented; empty templates are rejected; physical findings remain pending |
| Runtime offline behavior | All four guided family workflows, comparisons, study and glossary tested with Python network access blocked |
| Source/wheel installation and packaging | Release script plus separate wheel-installation checks; see current records |

Read [verification](verification.md) for commands, tolerances and test scope. The [current evidence page](evidence-status.md) separates numerical checks, physical validation, independent reproduction and release.

## What remains outside the completed local checks

1. **Full keyboard-only review.** The browser tool shows focus help, but it has not confirmed native Tab, Enter and Space operation. Do not call that a passed keyboard review.
2. **Screen-reader review.** Real HTML headers, captions and readable alternatives are present. A user must still review the workflow with a screen reader such as Narrator or NVDA. The editable grid belongs to Streamlit and needs particular attention.
3. **Physical touchscreen review.** Pointer activation is checked. Test tap, scroll and closing definitions on an actual touch device before claiming touch testing.
4. **Full network-outage review.** Python network calls are blocked in the automated tests. The PC's network adapter was not disabled. This is a separate, optional stronger check.
5. **Physical validation.** Obtain equipment/specimen details, choose feasible loads, calibrate instruments and supply actual readings. The software cannot create this evidence.
6. **Reproduction by another person.** A different person must install the released source and record what they did. A second run by this assistant does not count.

The public repository and CI status are recorded in the [release guide](../08-contributing-and-release/release-guide.md). Publication does not close any physical or accessibility review.

## A repeatable manual accessibility review

Use a supplied example. Record the operating system, browser, screen reader or device, date, steps and observed problems. Do not enter a pass until the action is observed.

- [ ] Use only Tab, Shift+Tab, Enter, Space and arrow keys to select a workspace and an example.
- [ ] Reach a dotted term, hear or read its meaning, activate it and close it. Check that the focus marker is visible.
- [ ] Read a model text table and change one value in the editor. Confirm that the updated value appears in the text table.
- [ ] Save and check the model, inspect its equations, then press Solve explicitly.
- [ ] Read nodal results, sampled member values and every balance check without using chart hover.
- [ ] Run a successful comparison and a released-support failure. Confirm that the original result remains unchanged.
- [ ] Search the glossary, open a definition and save its related guide.
- [ ] With a screen reader, check headings, table headers, units, errors and download-button names.
- [ ] On a touch device, tap definitions and controls, scroll wide text tables and inspect a result plot.

Record findings in a new dated review file. Keep failed steps visible and report the device actually used.

## Read next

- [Use the app](../04-user-guide/app-guide.md)
- [How to contribute a useful check](../08-contributing-and-release/how-to-contribute.md)
- [Prepare a real bench test](../05-research-and-experiments/bench-protocol.md)
