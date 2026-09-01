# Use the three-stage learning app

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)

Start the local app using [installation](../02-getting-started/installation.md). Guided learning is the default. Direct access uses the names Model, Inside FEM and Results for the same stages; it does not bypass input checks.

## 1. Define the problem

Open **Start or import a problem** in the sidebar. Load an example, start a blank bar/truss/beam/frame, or import a model or learning-project JSON file. Starting or loading another model replaces the current draft, so download work you want to keep first.

Write your question. Choose the whole structure or a selected portion. For a portion, describe the forces and restraints at the cut boundaries. The app requires these notes before theory or solving, but it cannot confirm whether they describe the real connection correctly.

Enter nodes, members, materials, sections, supports and loads in the four table tabs. Finish each cell edit with Enter or by leaving the cell. The draft stays in session when you change views. Invalid and incomplete drafts are kept instead of silently restoring an old model.

Hover a table heading for its meaning and units. Use the dotted term key for explanations of E, A, I, fiber distance, DOFs and support conditions. A frame pin holds ux and uy; a fixed support also holds rz. A roller holds one global translation. A spring has stiffness and can move.

**Save and check model** checks inputs only. It does not solve or prove stability. A complete valid model gets an undeformed geometry preview. Choose a load case and a node or member of interest. Triangles mark prescribed movements; diamonds mark springs. Hover to read the actual values.

Changing input units converts a valid draft without changing the physics. Finish invalid entries before conversion. Blank models have no preselected supports or material values.

## 2. Understand the method

Read the explanation built from this model's family, supports and loads. Follow the eight steps from assumptions to result checks. The method comparison explains when hand calculations are useful and why an unsuitable element or artificial restraint can give a misleading answer.

The optional hand check appears only for a matching single-member, left-clamped bar or beam with an end force and/or uniform load. Other structures do not receive an unrelated formula.

Enter a prediction if you wish. There is no score or required quiz. Select a member to inspect its geometry, stiffness, local matrix, coordinate transformation and assembly contribution.

The free equations and known right-hand side are available before solving. Small systems show full matrices; systems over 120 DOFs use a sparsity plot. Matrix entries have different units because translation and rotation DOFs are different. No displacement solution is calculated in this stage.

Use **Read as text** beside tables and matrices if the interactive grid is difficult to read. These alternatives use real HTML headers, captions and rows. Wide tables can be focused and scrolled sideways. Large tables are split into pages of 50 rows. They are read-only; change inputs in the model editor.

## 3. Solve and discuss

Press **Solve**. Choose a member, display units, deformation magnification and result diagram. Changing the picture scale does not change the solution. Original geometry stays visible and geometry axes have equal scales.

Positive ux is right, uy is up and rz is counterclockwise. Tension and sagging moment are positive. The stress picture shows top-fiber normal stress when fiber distance is available; otherwise it shows axial stress only. It is not a continuum stress contour.

Read the discussion below the plots. It reports the largest nodal translation component, selected member's sampled force extrema, target-node movements and matching analytical checks when available. Discussion values and balance checks use SI; plots and result tables state their own display units.

Force and moment checks include prescribed-support reactions and spring reactions. The discrete energy check includes work from nonzero prescribed movements. Numerical accuracy is not structural safety.

If a solve fails, the error stays visible and old results are not shown as current. Editing a model or changing load case removes its previous result and comparison; press Solve again. A changed prediction does not change the physics.

## Predict, change one thing, compare

Open **Change one thing and compare**. Change one applied-load multiplier, E, A, I, known support movement or spring stiffness. You can also release one prescribed support movement. This releases a ground restraint, not a member end connection.

Property and support values are entered in the stated SI units. A shared material or section change affects all members using that ID. Other properties remain unchanged: changing I does not automatically change A or the shape of a real section.

A does not set bending stiffness in the beam-only family, so its comparison offers E and I instead. The last completed comparison remains labeled with its actual change until **Run comparison** is pressed again.

The comparison lists baseline, changed movement and difference for each DOF. The original model and result remain unchanged. If the modified structure has a mechanism, the comparison records that failure without adding stiffness.

## Stiffness study and terminology

The separate **Stiffness study** compares beam EI and clamp compliance. Synthetic observations are generated from equations. Training readings enter the fit; reserved readings check predictions. Uncertainty intervals depend on the stated model and noise assumptions. The app reports unidentifiable cases instead of inventing unique estimates.

The study uses downward-positive force and deflection. **Measured CSV** requires real readings plus specimen, fixture, calibration and uncertainty details. No physical measurements are supplied with this project.

Dotted terms support pointer hover and keyboard focus. Activate a term to keep its definition open; activate it again to close the saved disclosure. The definition still appears while the term has focus or the pointer is over it. Native disclosure controls also support tap. Definitions appear in a fixed panel so long text stays inside narrow windows. Use **Glossary** to search definitions without hovering and download related guides when the source documentation is installed. See the [review limits](../07-testing-and-evidence/verification.md) for what has been tested.

## Save the problem and its explanation

- Model JSON remains the original versioned computational model.
- Learning-project JSON adds the question, boundary notes, targets and optional prediction. It contains no cached results; import and solve again.
- Draft JSON can be saved as a backup even when incomplete. Correct its missing or invalid model entries before importing it as a model. Nonfinite numbers must be replaced before JSON download; the draft remains in the session.
- Learning-report HTML includes the method, result discussion, checks, limitations, comparison and an interactive figure with its plotting code embedded.
- Results JSON, nodal CSV, standalone figure HTML and member PNG exports remain available.

Session storage is temporary. Downloads preserve your work after closing the browser or restarting the server. See [exports](exports.md).

## Read next

- [How to approach a structural problem](../03-engineering-knowledge/problem-solving.md)
- [Equations and assumptions](../03-engineering-knowledge/numerical-methods.md)
- [Python and JSON interfaces](python-and-json.md)
- [Troubleshooting](troubleshooting.md)
