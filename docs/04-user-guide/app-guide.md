# Use the three-stage learning app

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)

Start the local app using [installation](../02-getting-started/installation.md). The first screen is **Home**, a project launchpad. Guided learning is the default. Direct access uses the names Model, Inside FEM and Results for the same stages; it does not bypass input checks.

## Home: choose a starting point

Home has one card for Bar, Truss, Beam and Frame. Each card shows the movements that family can represent and a typical use. **Start blank** creates an empty draft. **Open example** loads a small model but does not solve it. You can also import model JSON or learning-project JSON.

**Continue current project** returns to the draft kept in this Streamlit session. “Current” does not mean that the app scans files on your computer. Export JSON before closing the app if you want to keep the project.

## 1. Define the problem

Choose a project on Home. Starting or loading another model replaces the current draft, so download work you want to keep first.

Write your question. Choose the whole structure or a selected portion. For a portion, describe the forces and restraints at the cut boundaries. The app requires these notes before theory or solving, but it cannot confirm whether they describe the real connection correctly.

The main inputs and the unsolved preview form a split workspace on a wide screen. Choose **Geometry**, **Properties**, **Supports** or **Loads** to edit one model category at a time. Finish each cell edit with Enter or by leaving the cell. On a phone the editor and preview stack into one column. The draft stays in session when you change views. Invalid and incomplete drafts are kept instead of silently restoring an old model.

Hover a table heading for its meaning and units. Open **Key terms** for E, A, I, fiber distance, DOFs and support conditions. Important first uses still have dotted definitions. A frame pin holds ux and uy; a fixed support also holds rz. A roller holds one global translation. A spring has stiffness and can move.

**Save and check** checks inputs only. It does not solve or prove stability. A complete valid model gets an undeformed geometry preview and can continue to Understand. Choose a load case and a node or member of interest in **Result focus**. Triangles mark prescribed movements; diamonds mark springs. Hover to read the actual values.

Changing input units converts a valid draft without changing the physics. Finish invalid entries before conversion. Blank models have no preselected supports or material values.

## 2. Understand the method

Read the explanation built from this model's family, supports and loads. The eight-step map gives the complete route at a glance. Open a step to see its model-specific explanation and detailed mathematics. The method comparison explains when hand calculations are useful and why an unsuitable element or artificial restraint can give a misleading answer.

The optional hand check appears only for a matching single-member, left-clamped bar or beam with an end force and/or uniform load. Other structures do not receive an unrelated formula.

Enter a prediction if you wish. There is no score or required quiz. Select a member, then choose **Element**, **Transformation**, **Assembly** or **Boundary system** in the matrix laboratory. The selected member, properties, DOF map and matrices stay connected.

The free equations and known right-hand side are available before solving. Small systems show full matrices; systems over 120 DOFs use a sparsity plot. Matrix entries have different units because translation and rotation DOFs are different. No displacement solution is calculated in this stage.

Use **Read as text** beside tables and matrices if the interactive grid is difficult to read. These alternatives use real HTML headers, captions and rows. Wide tables can be focused and scrolled sideways. Large tables are split into pages of 50 rows. They are read-only; change inputs in the model editor.

## 3. Solve and discuss

Before a solve, the page shows the active model and one **Solve model** action. After solving, choose a member, display units, deformation magnification and result diagram. Changing the picture scale does not change the solution. Original geometry stays visible and geometry axes have equal scales. A one-dimensional model receives a small symmetric vertical viewing range so its line remains readable; that range does not represent physical depth.

Positive ux is right, uy is up and rz is counterclockwise. Tension and sagging moment are positive. The stress picture shows top-fiber normal stress when fiber distance is available; otherwise it shows axial stress only. It is not a continuum stress contour.

Full values appear in responsive result cards. Use the Movements, Reactions, Member results and Checks tabs for detailed tables. The selected-member panel labels its extrema as sampled values. Read the separate Interpretation, Calculation checks and Limits cards below the plots. Discussion values and balance checks use SI; plots and result tables state their own display units.

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

Dotted first-use terms support pointer hover and keyboard focus. Activate a term to keep its definition open; activate it again to close it. Open the compact **Key terms** control for the vocabulary used on the current page. Use **Glossary** to search definitions or filter them by Model, Mechanics, Calculation and Research. See the [review limits](../07-testing-and-evidence/verification.md) for what has been tested.

## Save the problem and its explanation

- Model JSON remains the original versioned computational model.
- Learning-project JSON adds the question, boundary notes, targets and optional prediction. It contains no cached results; import and solve again.
- Draft JSON can be saved as a backup even when incomplete. Correct its missing or invalid model entries before importing it as a model. Nonfinite numbers must be replaced before JSON download; the draft remains in the session.
- Learning-report HTML includes a branded header, table of contents, method, result discussion, checks, limitations, comparison and an interactive figure with its plotting code embedded. Its responsive styles and plotting code are stored inside the file.
- Results JSON, nodal CSV, standalone figure HTML and member PNG exports remain available.

Session storage is temporary. Downloads preserve your work after closing the browser or restarting the server. See [exports](exports.md).

## Read next

- [How to approach a structural problem](../03-engineering-knowledge/problem-solving.md)
- [Equations and assumptions](../03-engineering-knowledge/numerical-methods.md)
- [Python and JSON interfaces](python-and-json.md)
- [Troubleshooting](troubleshooting.md)
