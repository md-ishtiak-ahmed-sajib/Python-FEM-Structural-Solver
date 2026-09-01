# Your first bar calculation

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


Start here after installation. This example connects a familiar mechanics formula to the app.

## The structure

A straight bar is 2 m long. Its left end is fixed against axial movement. A 10,000 N force pulls its right end to the right.

| Quantity | Value |
|---|---|
| Young's modulus E | 200,000,000,000 Pa |
| Area A | 0.003 m² |
| Length L | 2 m |
| Force P | 10,000 N |

These are example values, not a proposed physical test or a safe-load recommendation.

## Calculate the expected answer

For a uniform elastic bar:

~~~text
extension = P L / (E A)
          = 10,000 × 2 / (200,000,000,000 × 0.003)
          = 0.0000333333 m
          = 0.0333333 mm

normal stress = P / A
              = 3,333,333.33 Pa
              = 3.33333333 MPa
~~~

The support reaction is -10,000 N along global x. Its sign is negative because it acts to the left. The applied force and reaction balance.

## Find this in the app

1. Open **Start or import a problem** and choose **Axial bar** in Example structure.
2. Click **Load example**.
3. Use **1 · Define** to inspect the nodes, material, section, support and force. Save and check the inputs.
4. Read **2 · Understand** and write an optional prediction. Then open **3 · Solve and discuss**, press **Solve**, and choose N-mm-MPa for results in mm and MPa.
5. Inspect member AB and choose the axial stress diagram.
6. Return to the Inside FEM panel in **2 · Understand** to see the two-node stiffness matrix and the support condition. Direct access uses the alternative names Model, Inside FEM and Results for these same stages.

A bar model has only axial movement, called ux. It does not represent bending or lateral movement.

## Understand the picture

The deformed shape is enlarged so that you can see it. A magnification of 50 means the drawing shows 50 times the calculated movement. The actual result remains 0.0333333 mm.

The dotted line shows the original position. Always read the units and scale.

## Try a useful change

Open **Change one thing and compare**, keep the applied-load multiplier at 2, and run the comparison. The movement should double while the baseline stays unchanged. Doubling force also doubles stress for this model; inspect a separately edited model if you want its full stress diagram. This is a learning check, not a physical load test.

For a second example, work through the [cantilever beam](../03-engineering-knowledge/worked-examples.md).

## Read next

- [Install and run the project](installation.md)
- [Where files and folders belong](project-map.md)
