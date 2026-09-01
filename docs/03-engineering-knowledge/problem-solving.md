# How to approach a structural problem

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)

A useful FEM project starts with a question, not with a colorful result. Ask what you need to find, what behavior matters, and what you can check independently.

## 1. Define the physical problem

Sketch the geometry, loads and connections. Mark dimensions and units. Decide which part of the real structure you will represent.

For a selected portion, the removed part still affects the remaining part. You need appropriate forces, movements or support stiffness at the cut. A cut boundary is not automatically a fixed support. The app asks you to describe this choice; it cannot verify the real connection from your notes.

Choose a family by the behavior you need:

| Family | Represents | Does not represent |
|---|---|---|
| Bar | Horizontal axial stretching | Bending or transverse movement |
| Truss | Planar axial members with ideal pin joints | Bending inside members or rigid joint moments |
| Beam | Horizontal Euler–Bernoulli bending | Axial stretching or shear deformation |
| Frame | Planar axial action and bending with rigid joints | Member end releases, 3D action or shear deformation |

Do not choose a family just because its picture resembles your structure. A truss and a frame with the same geometry can have different stiffness because their joints and member behavior differ.

## 2. Choose and understand a method

Start with equilibrium: draw a free-body diagram and ask which forces balance. Use a textbook formula when geometry, support conditions and loading match that formula.

FEM is useful when many members and unknown movements must satisfy equilibrium and compatibility together. Compatibility means connected parts have matching movements. The direct stiffness method builds each member equation, changes coordinates, assembles contributions, applies known movements and solves the remaining equations.

The app uses sparse factorization, not an explicit inverse of the stiffness matrix. Sparse storage is useful because most distant nodes do not connect directly.

An unsupported movement is a modeling problem to investigate. Adding an arbitrary support or tiny stiffness simply to get an answer changes the problem. The engine rejects such mechanisms instead of hiding them.

## 3. Predict before solving

Write a short prediction. Which direction should the structure move? Which member might be in tension? What would happen if E increased?

For a bar with a fixed left end and tip force P, the tip movement is PL/(EA). Doubling P doubles movement. Doubling E or A halves movement. These statements assume the other inputs stay unchanged.

If supports have prescribed nonzero movements, scaling only the applied loads may not scale the whole response. A more complex frame may redistribute forces when one stiffness changes. Check the actual result rather than memorizing a universal rule.

## 4. Explain the result

Read the units, axes and signs before comparing numbers. A negative uy means downward movement in the structural solver. The separate stiffness study uses downward-positive observations and states that convention on screen.

Inspect support reactions, member diagrams and selected node movements. Compare the total applied actions with the support reactions. Spring reactions are external actions too.

The energy identity is a check of the discrete equations, including support springs and prescribed-movement work. A small residual is another numerical check. Neither proves that a real structure is safe.

Member extrema are taken from the sampled diagram points and are labeled accordingly. A sampled maximum is not automatically the exact maximum between samples.

## 5. Improve the model for a reason

| Concern | A possible next investigation |
|---|---|
| Uncertain support movement | Measure the connection or compare reasonable support stiffness values |
| Shear movement matters | Use a shear-deformable beam theory such as Timoshenko |
| Large changes in geometry | Use geometric nonlinear analysis |
| Material yielding | Use a suitable nonlinear material model |
| Compression stability | Perform an appropriate buckling or stability analysis |
| Detailed joint or contact stresses | Use a suitable continuum model and local boundary conditions |
| Approximation error within the selected theory | Perform a real mesh-convergence study |

These advanced analyses are outside the current engine. Increasing I, changing E or adding elements does not automatically fix missing physics. The app does not infer member slenderness from element length and an incomplete section description.

## Read next

- [Use the three learning stages](../04-user-guide/app-guide.md)
- [Equations used in the engine](numerical-methods.md)
- [Worked examples](worked-examples.md)
- [Verification and its limits](../07-testing-and-evidence/verification.md)
