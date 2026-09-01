# Python functions and model files

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


An API is a set of functions another program can call. The browser app uses the same calculation package described here.

## Solve an example in Python

~~~python
from fem_solver import assemble, solve_linear, SolveOptions
from fem_solver.examples import example

model = example("Portal frame")
trace = assemble(model)
result = solve_linear(model, SolveOptions(case="default", samples=41))

print(result.labels)
print(result.displacements)  # metres for translations, radians for rotations
~~~

A **Model** stores the geometry, properties, supports and loads. All values in a Model use SI units.

**AssemblyTrace** stores the element matrices, DOF labels, full stiffness, spring stiffness, load vectors and boundary-condition maps.

**SolveResult** stores movements, reactions, member fields, warnings and numerical checks. Use labels to identify array entries instead of guessing their order.

The samples option sets how many points are used for member-result diagrams. It does not add finite elements.

## Fit a cantilever

~~~python
from pathlib import Path
from fem_solver import fit_cantilever, IdentificationConfig
from fem_solver.identification import read_observations_csv

text = Path("examples/synthetic_observations.csv").read_text()
observations = read_observations_csv(text)
configuration = IdentificationConfig(length=1.0, EI_reference=1000.0)
fit = fit_cantilever(observations, configuration)

print(fit.status)
print(fit.EI)
print(fit.clamp_compliance)
~~~

This example reads clearly labeled synthetic data. IdentificationResult also contains sensitivity rank, singular values, parameter correlation, predictions, errors and uncertainty intervals.

A status of unidentifiable means no unique estimate was returned. Missing estimates use None. EI_reference is a numerical scale in N m², not a claim that the unknown EI already equals that value.

For actual measurements, use the CLI with metadata or the measured-data app view. The low-level fitting function checks observations, but it does not collect laboratory metadata by itself.

## JSON model format, version 1

JSON is a text format containing named fields, lists and numbers. Start with a supplied example rather than an empty file.

Required top-level information includes schema_version=1, units and kind. Model collections are:

| Collection | Fields |
|---|---|
| nodes | id, x, y; y defaults to 0 |
| materials | id, E |
| sections | id, A, I and c; I is required for beam/frame, c is optional |
| elements | id, start, end, material, section |
| constraints | node, dof, value; value defaults to 0 |
| springs | node, dof, stiffness |
| loads | node, dof, value, case |
| distributed_loads | element, qx, qy, case |

title is optional. Load case defaults to default. qx and qy default to zero. Unknown fields are rejected.

IDs must be unique nonempty strings. Two nodes at the same coordinates are not connected unless the members use the same node ID.

kind is bar, truss, beam or frame. units is N-m-Pa or N-mm-MPa. See [units and supports](../03-engineering-knowledge/units-and-signs.md).

~~~python
import json
from pathlib import Path
from fem_solver import model_from_dict, model_to_dict

data = json.loads(Path("examples/axial_bar.json").read_text())
model = model_from_dict(data)  # Converts declared input units to SI
converted = model_to_dict(model, "N-mm-MPa")
~~~

## Results and display units

Learning projects use a separate wrapper; see the following section. Model and result files keep their original schema.

JSON result files always declare N-m-Pa. Rotations are radians and moments are N m.

The optional presentation functions structure_figure, member_figure and results_csv accept N-m-Pa or N-mm-MPa. This changes display values, not the stored model or solution.

Normal-stress fields describe line-element sections. They are not continuum stresses.

## Learning projects, version 1

The numerical functions and model schema remain unchanged. The optional learning layer adds a separate wrapper:

~~~python
from fem_solver.learning import ProblemBrief, project_to_dict, project_from_dict

brief = ProblemBrief(question="What happens when area doubles?", prediction="Movement halves.")
project = project_to_dict(model, brief)
loaded_model, loaded_brief = project_from_dict(project)
~~~

The wrapper has learning_project_version=1, model and brief. The brief contains question, scope, boundary_notes, target_node, target_member and prediction. Scope is Whole structure or Selected portion. A selected portion needs boundary notes before theory or solving. Missing targets use empty strings.

Results are not stored in this wrapper and must be recomputed. The loader also accepts the original model JSON. Unknown fields and invalid brief types are rejected. The CLI still expects a model file, not the learning wrapper.

The independent learning helpers build a MethodGuide, a Discussion and one-change comparisons from typed model and result objects. They do not import Streamlit or call an online model.

## Observation CSV format

Use the exact columns in the [empty template](../../data/bench/measurements-template.csv):

~~~text
id,x_m,load_position_m,force_N,raw_displacement_m,zero_m,sigma_m,split,provenance,run_id
~~~

Corrected displacement is raw_displacement_m minus zero_m. sigma_m is a positive measurement standard uncertainty. split is train or holdout. provenance is synthetic or measured.

The fit refuses mixed data origins. Holdout values never affect the parameter estimates. Read the [bench protocol](../05-research-and-experiments/bench-protocol.md) before importing real data.

## Errors

ModelError means the model or observation settings are invalid or unsupported. Read the message, fix the input and retry. Uploaded files are data only; Python expressions and pickle files are not supported.

## Read next

- [Use the three-stage learning app](app-guide.md)
- [Save results and run commands](exports.md)
