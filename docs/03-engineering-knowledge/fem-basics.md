# FEM explained from the beginning

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


The **finite element method**, or FEM, is a way to approximate the behavior of a structure using smaller connected parts.

In this project, each part is a bar, truss member, beam or frame member. The connection points are called **nodes**.

## Start with something familiar

For a spring, force equals stiffness times movement:

~~~text
F = k u
~~~

For a structure, there are many forces and movements. We put them in columns of numbers, called vectors:

~~~text
K u = F
~~~

K is the stiffness matrix. It describes how movement at one node affects forces at the nodes. u contains unknown movements and rotations. F contains forces and moments.

## What is a degree of freedom?

A **degree of freedom**, or DOF, is one independent movement in the model.

| Element family | Movements at each node | Main behavior |
|---|---|---|
| 1D bar | ux | Stretching along global x |
| 2D truss | ux, uy | Axial stretching of members in a plane |
| Beam | uy, rz | Vertical movement and bending rotation |
| 2D frame | ux, uy, rz | Axial stretching and bending in a plane |

ux means horizontal movement. uy means vertical movement. rz means rotation in the plane.

A truss joint does not transfer member bending moment in this model. A frame joint does. A support pin is a different concept from an internal member hinge.

## The calculation path

~~~mermaid
flowchart LR
    A["Geometry, material and loads"] --> B["Stiffness of each member"]
    B --> C["Add member contributions"]
    C --> D["Apply supports"]
    D --> E["Solve for movements"]
    E --> F["Calculate reactions, forces and stress"]
~~~

If the diagram does not render in your editor, read it left to right: inputs, element stiffness, assembly, supports, movements, then forces and stress.

**Assembly** means adding member contributions at shared nodes. **Boundary conditions** describe supports and known movements.

## Why supports matter

A free bar can translate without stretching. That movement produces no restoring force. The equations cannot give a unique position until suitable supports are added.

The same issue can occur in a truss mechanism. The solver reports it instead of adding artificial stiffness.

## What the model assumes

Material stays elastic. Movement is small enough that we use the original geometry for equilibrium. Loads are static. A beam follows Euler–Bernoulli theory, which leaves out shear deformation.

These assumptions can be reasonable for some problems and poor for others. A precise numerical answer can still come from an unsuitable model.

Continue with [units and signs](units-and-signs.md), then [worked examples](worked-examples.md).

## Read next

- [Units, axes, supports and signs](units-and-signs.md)
