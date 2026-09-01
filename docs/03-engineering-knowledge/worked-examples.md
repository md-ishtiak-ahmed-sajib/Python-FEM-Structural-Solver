# Bar and beam calculations by hand

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


These examples use the supplied model files. They are calculations for learning, not proposed physical loads or certified designs.

## Example 1: the axial bar

Open [axial_bar.json](../../examples/axial_bar.json). The inputs are L=2 m, E=200 GPa, A=0.003 m² and P=10,000 N.

~~~text
EA/L = 300,000,000 N/m

K = 300,000,000 × [[ 1, -1],
                   [-1,  1]]

u_A = 0
300,000,000 × u_B = 10,000

u_B = 0.0000333333 m = 0.0333333 mm
stress = P/A = 3.33333333 MPa
reaction at A = -10,000 N
~~~

Only the right-end movement is unknown. Applying the left support removes the rigid translation of the bar.

The elastic strain energy is P u_B / 2 = 0.1666667 J. Here the support does not move, so no support-work term is needed.

## Example 2: a cantilever beam with two loads

Open [cantilever_beam.json](../../examples/cantilever_beam.json). The beam has L=3 m, E=200 GPa and I=8 × 10⁻⁶ m⁴. Thus EI=1,600,000 N m².

It carries a downward tip force P=1,000 N and a downward uniform load w=500 N/m. We use positive magnitudes in these hand formulas, then apply the global signs.

For a fixed cantilever, the two tip-deflection magnitudes add:

~~~text
tip deflection = P L³/(3 EI) + w L⁴/(8 EI)
               = 0.005625 + 0.0031640625
               = 0.0087890625 m
               = 8.7890625 mm downward

tip rotation magnitude = P L²/(2 EI) + w L³/(6 EI)
                       = 0.0028125 + 0.00140625
                       = 0.00421875 rad

vertical support reaction = P + w L = 2,500 N upward
support reaction moment = P L + w L²/2 = 5,250 N m counterclockwise
~~~

In the app, tip uy and rz are negative. The vertical reaction and reaction moment at the fixed end are positive.

The member moment at the fixed end is -5,250 N m, which is hogging bending. The support reaction moment has the opposite sign because it acts on the structure from outside.

## Why a single beam element can work here

For this uniform beam and these loads, the nodal results can match the closed-form solution very closely. The displayed interior deflection also includes an exact term for the uniform load.

That does not mean one element is exact for all beam problems. The [equations page](numerical-methods.md) explains the correction. The [verification page](../07-testing-and-evidence/verification.md) explains what the convergence study actually measures.

## Compare your answers

Use the same units, force directions and support conditions in both calculations. If they differ, first check I, length units and the load sign. Use a small absolute tolerance when the expected answer is zero.

## Read next

- [Units, axes, supports and signs](units-and-signs.md)
- [Equations used in the solver](numerical-methods.md)
