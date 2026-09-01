# Equations used in the solver

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


Read [FEM basics](fem-basics.md) and [units and signs](units-and-signs.md) first. This page gives the equations used in the code. The explanations are simple, but the equations keep their technical meaning.

## 1. Assumptions and symbols

The model is elastic, static and based on small movement. Each member has constant properties. Split a member into more elements if its properties change.

E is Young's modulus, A is area, I is second moment of area, and L is element length. u and v are local axial and transverse movements. theta is rotation. See the [glossary](glossary.md).

## 2. Bar stiffness

For end movements d=[u1,u2], the axial strain is (u2-u1)/L. Stress equals E times strain. Multiplying stress by area gives the axial force.

The resulting element equation uses:

~~~text
k = EA/L × [[ 1, -1],
            [-1,  1]]
~~~

If both ends move by the same amount, the bar does not stretch. Its internal axial force is zero.

## 3. Truss coordinate change

A truss member may be inclined. Let c=cos(angle) and s=sin(angle), measured from global x. In this paragraph, c is a direction cosine, not a section depth.

~~~text
T = [[c, s, 0, 0],
     [0, 0, c, s]]

local axial movements = T × global nodal movements
global element stiffness = transpose(T) × k × T
~~~

The member only resists axial stretching. It does not provide member bending stiffness.

## 4. Beam stiffness

Euler–Bernoulli theory leaves out shear deformation. Its local end movements are [v1,theta1,v2,theta2], where theta=dv/dx.

Cubic Hermite functions describe the movement between the ends. With t=x/L:

~~~text
H = [1-3t²+2t³, L(t-2t²+t³), 3t²-2t³, L(-t²+t³)]

v(x) = H × d

k = integral(EI × transpose(H'') × H'' dx)
  = EI/L³ ×
    [[ 12,   6L, -12,   6L],
     [ 6L, 4L²,  -6L, 2L²],
     [-12,  -6L,  12,  -6L],
     [ 6L, 2L²,  -6L, 4L²]]
~~~

H'' means the second derivative with respect to x. It relates the end movements to curvature. Integrating the bending-energy expression gives the stiffness matrix.

## 5. Frame stiffness

A frame combines axial bar stiffness and beam bending stiffness. Its local end vector is [u1,v1,theta1,u2,v2,theta2].

The axial block goes into positions [0,3]. The bending block goes into [1,2,4,5]. These are zero-based Python positions.

At each node, the coordinate change is:

~~~text
[[ c, s, 0],
 [-s, c, 0],
 [ 0, 0, 1]]
~~~

In-plane rotation does not change when the x-y axes are rotated this way.

## 6. Assembly and supports

The solver adds element terms at their shared global DOFs. It first stores row, column and value entries, called COO storage, then converts them to CSR sparse storage. A support spring adds its stiffness to the appropriate diagonal.

Separate the DOFs into free values f and prescribed values c:

~~~text
Kff × uf = Ff - Kfc × uc
~~~

The right side includes the effect of known support movements. The solver keeps the original system for reaction recovery. It never calculates an explicit inverse of K.

To reduce numerical scaling problems, it scales equations using the diagonal stiffness before sparse LU solution. LU is a standard factorization method provided by SciPy.

For up to 300 free DOFs, it also checks the smallest eigenvalue of the scaled matrix. A value at or below 10⁻¹² is rejected. Small LU pivots are checked too. These are numerical limits, not a classification of real structural safety. Large stiffness differences may need a better model.

## 7. Loads and member results

A constant local transverse load qy gives the beam end-load vector:

~~~text
[qy L/2, qy L²/12, qy L/2, -qy L²/12]
~~~

A constant local axial load qx gives qx L/2 at each axial end DOF.

These are **consistent nodal loads**: equivalent end loads obtained using the same shape functions. Therefore member end forces are:

~~~text
end forces = k × d - equivalent nodal loads
~~~

Using the left-end force components and local distance x:

~~~text
N(x) = -f_i_axial - qx x
V(x) =  f_i_transverse + qy x
M(x) = -f_i_moment + f_i_transverse x + qy x²/2
~~~

Normal stress is N/A for axial action. With bending, top and bottom fiber stresses are N/A minus or plus Mc/I. Here c is the section-fiber distance.

These are member-section stresses. They are not 2D or 3D continuum stress contours.

## 8. Interior movement under uniform load

A cubic beam interpolation alone cannot represent the quartic deflection caused by a constant distributed load. For a uniform member, the displayed field adds:

~~~text
extra transverse term = qy x² (L-x)² / (24 EI)
extra axial term      = qx x (L-x) / (2 EA)
~~~

These terms preserve the element's end movements. The bending term also preserves end rotations.

The convergence study measures the cubic field **before** this exact load correction. Measuring an already exact field would not show meaningful approximation improvement.

## 9. Reactions and energy

~~~text
prescribed-support reactions = constrained entries of (Ktotal u - F)
spring reactions             = -kspring × u
elastic strain energy U      = 0.5 × transpose(u) × Ktotal × u
~~~

Ktotal includes springs. Add applied loads, prescribed reactions and spring reactions to check external equilibrium.

For known support movements, the correct work check is:

~~~text
2U = transpose(u) × (F + prescribed-support reactions)
~~~

Using only applied-load work would miss the work from moving supports.

This is the energy of the discrete nodal stiffness system, including support springs. It is not a separate integration of the corrected interior displacement field. The learning app labels the energy identity accordingly.

## 10. Beam stiffness identification

For a downward point load P at position a, the downward movement at x is:

~~~text
v = P B(x,a)/EI + P a x C

B(x,a) = x²(3a-x)/6  when x <= a
         a²(3x-a)/6  when x >= a
~~~

C is rotational clamp compliance in rad/(N m). The clamp has no translation.

The code fits beta=EI_ref/EI and gamma=EI_ref C/L. For this cantilever, movement is linear in these two quantities. Both must be nonnegative; beta has a small positive numerical lower limit of 10⁻¹².

The normal app uses two FEM solutions to form its sensitivity columns: a rigid clamp and a known rotational spring. Their difference isolates the clamp-rotation effect. Separate analytical formulas check those columns.

A singular-value test checks whether the observations contain independent information. Rank failure gives no unique two-parameter estimate. Even with full rank, wide intervals or strong parameter correlation may make the estimates weak.

Read the [research explanation](../05-research-and-experiments/research-question.md) before interpreting a fitted EI or C.

## Read next

- [Bar and beam calculations by hand](worked-examples.md)
- [Engineering and software glossary](glossary.md)
