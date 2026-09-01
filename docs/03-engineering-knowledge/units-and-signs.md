# Units, axes, supports and signs

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


Use one declared unit system for each input model. The program converts the input to SI units before calculation.

## The two input and display systems

| Quantity | N-m-Pa | N-mm-MPa |
|---|---|---|
| Length and translation | m | mm |
| Force | N | N |
| Moment | N m | N mm |
| Young's modulus and normal stress | Pa | MPa |
| Area | m² | mm² |
| Second moment of area I | m⁴ | mm⁴ |
| Distributed force | N/m | N/mm |
| Translational spring stiffness | N/m | N/mm |
| Rotational spring stiffness | N m/rad | N mm/rad |
| Rotation | rad | rad |

For example, 0.003 m² = 3,000 mm², and 8 × 10⁻⁶ m⁴ = 8,000,000 mm⁴. A fourth-power conversion is easy to miss.

All model/result objects in Python use SI. JSON result files and the Inside FEM view keep SI. Plot and CSV display conversion does not change the calculation.

## Global and local directions

Global x points right, global y points up, and positive rz is counterclockwise.

A member's local x points from its start node to its end node. Local y is 90 degrees counterclockwise from local x. Distributed member loads use these local directions.

The stiffness study uses a separate, clearly stated convention: force and deflection are positive **downward**. Do not copy its signs into a global uy load without changing the sign.

## Support conditions

| Support in a frame | Restrained movements |
|---|---|
| Fixed support | ux, uy and rz |
| Pin support | ux and uy |
| Roller against vertical movement | uy only |
| Roller against horizontal movement | ux only |
| Known support settlement | A chosen translation with a nonzero prescribed value |

For a beam, a fixed end restrains uy and rz. A simple beam support restrains uy. A bar only has ux.

Only the available global DOFs can be restrained. Inclined rollers and linked constraints are not included. A spring adds a force proportional to movement; it does not impose zero movement.

## Member-force signs

N is positive in tension. Positive M is sagging bending. V follows dM/dx. Local positive y defines the top fiber, so:

~~~text
top normal stress    = N/A - M c/I
bottom normal stress = N/A + M c/I
~~~

Here c is the distance from the neutral axis to the reported fiber. It is not the direction cosine used in coordinate transformations.

## Read results correctly

A negative displacement is a direction, not an error. A negative normal stress means compression. Support reactions oppose the loads when required by equilibrium.

Spring reactions and reactions at prescribed supports are reported separately. Do not count the same support force twice.

Figures show the deformation magnification. The enlarged shape is a display choice, not the actual motion.

## Read next

- [FEM explained from the beginning](fem-basics.md)
- [Bar and beam calculations by hand](worked-examples.md)
