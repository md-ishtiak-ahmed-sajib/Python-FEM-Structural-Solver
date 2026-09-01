# Engineering and software glossary

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)

These definitions are shared with the app. Hover, focus or tap dotted terms for help. You can also use the searchable Glossary view.

This page is generated from [the reviewed terminology source](../../src/fem_solver/terms.py). Edit that source, then run `python scripts/build_learning_docs.py`. Do not edit generated definitions here.

## Area A

The area of the member's cross section, in m² or mm². It is used for axial stiffness and stress.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Assembly

Adding the element equations at shared node movements to form the whole structure's equations.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Axial force

Internal force along a member. Positive stretches it; negative compresses it.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Bar

A horizontal element that resists stretching or shortening only. Its node movement is ux.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Beam

A member model that carries transverse load through bending. This engine's beam family is horizontal.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Bending moment

The turning effect that bends a member. Its unit is force times length.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Buckling

Loss of stability under compression. This linear static solver does not calculate a buckling load.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Calibration

Checking an instrument against a known reference before interpreting its readings.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Characteristic displacement

A declared reference movement used to set the noise size consistently across measurements.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Clamp compliance

Clamp rotation per unit applied moment, in rad/(N m). Zero means a rigid clamp.

[Read more](../05-research-and-experiments/research-question.md)

## Consistent nodal loads

Equivalent end loads calculated with the same shape functions as the element, including end moments where needed.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Constraint

A rule that sets a node movement or rotation to a known value.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Continuum model

A model that represents an area or volume, rather than only member centerlines, to study more detailed stress patterns.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Convergence

Checking whether a real approximation error decreases as the model is refined. More elements do not fix wrong physical assumptions.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Coordinate transformation

A change between member directions and the shared directions of the structure. T maps global movements to local movements.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## CSV

A text table whose values are separated by commas.

[Read more](../04-user-guide/exports.md)

## Deflection

Movement across a member, often called the bending movement of a beam.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Deformation magnification

The factor used to enlarge movement in the drawing. It changes the picture, not the calculated result.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Degree of freedom

One movement or rotation represented at a node.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Dimensionless clamp compliance

A scaled clamp compliance: gamma = EI_reference × C / length. It compares support rotation with beam bending without carrying units.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Direction cosine

The cosine of the angle from global x to local x. It is a direction number, not the section's fiber distance c.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Direction sine

The sine of the angle from global x to the member's local x axis.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Displacement

How far a point moves from its original position, with a direction and a unit.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Distributed load

Force spread along a member. This engine supports a constant force per unit length in local directions.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## EA

Axial rigidity: material stiffness E times cross-section area A. The axial element stiffness also depends on its length.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## EI

How strongly a beam resists bending. It combines material stiffness E and section property I. Its unit is N m² or N mm².

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Elastic

An ideal material that returns to its original state when the load is removed. This engine uses a straight stress–strain relation.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Element

One small part of the mathematical model. Here it is a straight bar, truss, beam or frame member.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Equilibrium

Applied forces and support reactions balance; their moments must balance too.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Euler–Bernoulli

Beam theory that includes bending but leaves out shear deformation. It is most useful when shear movement is small.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## FEM

Finite element method: split a model into connected pieces, write their equations, and solve them together.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Fiber distance c

Distance from the section's reference bending axis to the top or bottom location where normal stress is reported. It does not fully define the section shape.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Fixed support

A support that prevents every movement and rotation available in this element family.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Frame

Members that carry both axial force and bending, connected by rigid joints in this engine.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Free DOF

A movement or rotation that has not been prescribed. The solver must find its value.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Global axes

The shared directions for the whole model: x right and y up.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Idealization

A simplified mathematical description of a real object, including what behavior is left out.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Ill-conditioned

Small input or rounding changes can strongly affect the answer. Inspect support choices and very different stiffness values.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## JSON

A text file format that stores named data. Model files include a version and declared units.

[Read more](../04-user-guide/python-and-json.md)

## Load

A force or moment applied to the model.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Load case

One named set of loads solved independently. Loads in different cases are not automatically added.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Local axes

Directions attached to a member: x from its start to its end, and y 90 degrees counterclockwise from x.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## LU factorization

A standard way to split a matrix into triangular parts so equations can be solved without forming an inverse.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Material

The substance represented by a stiffness value E, such as an ideal elastic steel.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Measured

Read from a real physical test, with specimen details and measurement uncertainty.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Mechanism

A movement that the model cannot resist. Check connections and real supports instead of adding artificial stiffness.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Megapascal (MPa)

One million pascals, equal to one newton per square millimetre. Used with N–mm–MPa display units.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Mesh

The collection of elements and nodes used to represent the structure.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Newton (N)

The unit of force used here. Moments use force times length, such as N m.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Node

A point where members connect and movements or loads are represented.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Noise

Random variation added to or present in measurements. Here its size is declared relative to a characteristic displacement.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Nonlinear

A model where response is not proportional to input because geometry, material behavior or contact changes.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Normal stress

Force per area acting normal to a section. Positive means tension in this engine; negative means compression.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Parameter correlation

How strongly fitted parameters can trade off against each other. Values near minus or plus one suggest they are hard to separate.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Parametric bootstrap

Repeat the fit using simulated measurement errors to estimate uncertainty under the chosen noise model.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Pascal (Pa)

One newton per square metre. It is a unit of stress and Young's modulus.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Pinned support

A support that prevents translations but allows rotation where the model includes rotation.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Prescribed displacement

A movement or rotation whose value you set instead of asking the solver to find it. It may be zero or a support settlement.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Provenance

Where data came from, such as a real test or a stated synthetic generator.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## qx

Uniform force per unit length along the member's local x axis; N/m or N/mm.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## qy

Uniform force per unit length along the member's local y axis; N/m or N/mm.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Rank

The number of independent parameter effects the measurements can distinguish. Two unknown parameters need two independent effects.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Reaction

A force or moment supplied by a support.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Reserved cases

Measurements kept out of fitting and used afterward to check predictions.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Residual

The imbalance left after solving the equations. A small value checks the calculation, not structural safety.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Right-hand side

The known force terms in an equation, including the effect of prescribed support movements.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## RMSE

Root mean square error: a measure of typical prediction error, with the same units as the measured movement.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Roller

A support that prevents one translation and allows movement in the other direction. This app uses global-axis rollers.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Rotation

A change in angle. One radian is about 57.3 degrees.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## rz

Rotation about the out-of-plane z axis. Positive means counterclockwise; measured in radians.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Sagging

Positive bending in the engine's local convention: the top side is compressed and the bottom side is stretched.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Scaled eigenvalue

A number used to check the stiffness equations after scaling. A tiny value can indicate an unsupported movement or a difficult numerical system.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Second moment of area I

A geometric measure of how area is spread about the bending axis. It is measured in m⁴ or mm⁴, not mass units.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Section

The cross section of a member, described here by area A, bending property I and optional fiber distance c.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Sensitivity

How much a predicted measurement changes when a model parameter changes.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Shape function

A function that describes movement inside an element from its node movements.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Shear force

Internal force across a member. Its sign follows the local member convention.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## SI

The internal unit system: metres, newtons and pascals, with rotations in radians.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Singular values

Numbers measuring how clearly different parameter combinations affect the data. A very small value means weak information.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Sparse matrix

A matrix stored mainly by its nonzero entries, saving space when most entries are zero.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Static

Loads are treated as steady. Acceleration and vibration are not included.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Stiffness

How much force or moment is needed to produce a movement or rotation.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Stiffness matrix

A table of coefficients connecting node movements to the forces needed to produce them.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Strain

Change in length divided by original length. It has no length unit.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Strain energy

Elastic energy stored by the model's nodal stiffness and its support springs; reported in joules. The displayed check uses this same discrete system.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Support

A connection to the surroundings that restrains movement or resists it with a spring.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Support spring

A support that can move. Its restoring force or moment equals minus stiffness times movement or rotation.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Synthetic

Generated by equations or software. These are not actual bench measurements.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Timoshenko

Beam theory that also includes shear deformation. It is a reference or future method, not an element in this engine.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Training observations

Measurements used to estimate the parameters.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Translation

A movement along an axis, without referring to rotation.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Truss

A system of straight members that carry axial force only, with ideal pin joints and loads at nodes.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Uncertainty

A stated range of doubt in a measurement or estimate. The range depends on the assumptions used to calculate it.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Unidentifiable

The supplied data cannot uniquely separate the requested parameters. The app must not invent a unique estimate.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## ux

Movement in the global x direction. Positive means right; measured in m or mm.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## uy

Movement in the global y direction. Positive means up; measured in m or mm.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Yielding

Permanent material deformation beyond its elastic range. This engine does not model it.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Young's modulus E

Material stiffness: stress divided by strain for the elastic model. A larger E means less stretch under the same stress.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Zero reading

An unloaded reference reading subtracted from a later reading to remove the initial offset.

[Read more](../03-engineering-knowledge/numerical-methods.md)

## Read next

- [How to approach a structural problem](problem-solving.md)
- [Use the guided app](../04-user-guide/app-guide.md)
