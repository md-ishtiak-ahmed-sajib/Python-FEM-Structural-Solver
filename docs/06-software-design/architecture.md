# How the code is organized

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


The calculation package is separate from the interface. This lets a student use the same equations from the browser, a Python script or a repeatable study.

## Main code files

| File | Responsibility |
|---|---|
| [model.py](../../src/fem_solver/model.py) | Stores model data, checks inputs and converts units |
| [elements.py](../../src/fem_solver/elements.py) | Builds element matrices and calculates member results |
| [solver.py](../../src/fem_solver/solver.py) | Assembles equations, applies supports, solves and recovers reactions |
| [identification.py](../../src/fem_solver/identification.py) | Fits EI and clamp compliance and reports uncertainty |
| [study.py](../../src/fem_solver/study.py) | Runs repeatable synthetic comparisons |
| [export.py](../../src/fem_solver/export.py) | Writes result tables and reports |
| [visualization.py](../../src/fem_solver/visualization.py) | Creates optional plots |
| [cli.py](../../src/fem_solver/cli.py) | Provides terminal commands |
| [app.py](../../app.py) | Provides the local browser interface |
| [learning.py](../../src/fem_solver/learning.py) | Builds reviewed explanations, checks, comparisons and learning reports without UI imports |
| [terms.py](../../src/fem_solver/terms.py) | Supplies shared term meanings and escaped HTML help |
| [ui_learning.py](../../src/fem_solver/ui_learning.py) | Renders Define, Understand, and Solve and Discuss |
| [ui_common.py](../../src/fem_solver/ui_common.py) | Renders help, table headings and the searchable glossary |
| [ui_study.py](../../src/fem_solver/ui_study.py) | Renders the separate stiffness-identification study |

The core uses NumPy and SciPy for numerical operations. Streamlit, Plotly and Matplotlib handle presentation. OpenSees is installed separately and is only a comparison tool.

## Structural calculation

~~~mermaid
flowchart LR
    A["JSON file or app tables"] --> B["Check input and convert to SI"]
    B --> C["Build Model"]
    C --> D["Assemble sparse equations"]
    D --> E["Solve one load case"]
    E --> F["Recover forces and reactions"]
    F --> G["Tables, plots and exports"]
~~~

There is no second solver hidden inside the app. Interface changes must not change the underlying equations.

## Stiffness study

The input CSV is read, explicit zero readings are subtracted, and data-origin labels are checked. Only training observations enter the fit. Reserved observations check predictions afterward.

The fit reports failure if the observations cannot separate the requested parameters. It does not silently add assumed information to produce a unique answer.

## Data ownership

App edits, including incomplete drafts, stay in session independently of page widgets. Input validation and solving are separate. Define previews the model; Understand calls assembly without solving; Solve calls the unchanged public solver only after an explicit action.

An editor base is retained while a table is active, and the current draft is preserved when changing views. Changing the model or load case clears cached results and comparisons. A model-and-case SHA-256 fingerprint prevents a result being displayed for different inputs.

The comparison helper copies the model and changes one setting. It never writes back to the baseline. A failed comparison is a recorded error, not a stabilized solution.

Learning projects wrap the unchanged model format with a problem brief and prediction. They never accept cached results. Download files to keep work beyond the current session. CLI results go to a chosen output folder.

Imported files are not modified. There is no database or account system.

## Explanation rules

ProblemBrief, MethodGuide, Discussion and Change are typed objects in the learning module. Explanations use the actual family, loads, restraints and results. They do not use an LLM, remote API or hidden physical assumptions.

Analytical checks have conservative matching rules: a single horizontal bar or beam, left clamp, no springs or settlement, and only tip force and/or uniform loading. A different model receives general methodology instead of an unrelated formula.

The glossary is generated from the term registry, avoiding a second copy of definitions. Native disclosure elements provide hover, focus and activation help; the searchable view provides a non-hover alternative. User text is escaped before HTML export or annotation.

The export module supplies a shared HTML table writer. The learning report adds sampled member ranges with separate units; the stiffness report shows estimates and diagnostic meanings before its raw record. The UI uses the same escaped HTML table structure for read-only alternatives to canvas grids. The helper never changes model or result values.

## Model boundaries

A bar uses ux; a truss uses ux and uy; a beam uses uy and rz; a frame uses all three.

Bar and beam members must be horizontal in this version. Use a truss or frame for inclined members. Frame joints are rigid, with no member end releases.

See [design decisions](decisions/README.md) and [the Python interface](../04-user-guide/python-and-json.md).

## Read next

- [Rules for a clear interface](interface-design.md)
