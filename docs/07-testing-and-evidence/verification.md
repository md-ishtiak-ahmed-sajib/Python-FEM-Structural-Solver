# Run tests and compare results

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


Verification asks: **does the software solve its stated equations correctly?**

Physical validation asks a different question: **does the model describe a real test well enough?** Numerical checks do not replace measurements.

## Run the software checks

From the project root:

~~~powershell
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m mypy
.\.venv\Scripts\python scripts/check_docs.py
.\.venv\Scripts\python scripts/build_learning_docs.py --check
~~~

pytest checks behavior and numerical answers. Ruff checks code style. mypy checks type use. check_docs checks documentation links and navigation.

For the full release check, including dependency checks and a package build:

~~~powershell
.\.venv\Scripts\python scripts/verify_release.py
~~~

The current Windows/Python 3.12 suite has 81 passing tests. Read [the recorded check results](../../reports/verification/software_checks.json) and [current evidence status](evidence-status.md) for scope. Local logs go to results/.

## What the numerical tests cover

| Check | What it can reveal |
|---|---|
| Bar extension and stress | Wrong axial stiffness or units |
| Beam tip, rotation and UDL fields | Wrong bending terms, load conversion or interior recovery |
| Hand-solvable truss | Wrong directions, connectivity or equilibrium |
| Frame comparison | Errors when axial and bending behavior are combined |
| Support springs and settlements | Incorrect reactions or known-movement handling |
| Matrix symmetry and rigid motion | Assembly and element consistency problems |
| Force, moment and energy balance | Incorrect loading, reactions or work terms |
| Unit conversion and node/member order | Answers that depend on file order or display units |
| Invalid and unstable models | Silent failure or artificial stabilization |
| Inverse recovery and ambiguous cases | Incorrect fitting or unsupported certainty |
| Reserved observations | Information leaking from prediction checks into fitting |
| App and exports | Broken workflows, units or output files |

The fast study estimator is also compared with SciPy on constrained cases, including parameter boundaries.

## Learning workflow checks

The learning tests exercise all four element families through Define, Understand, Solve and comparison. They prevent hidden solves in the first two stages, check draft retention, reject missing cut-boundary notes, and ensure model edits clear earlier results. Comparison tests check proportional loading, stiffness changes, prescribed movements and released-support failures without modifying the baseline.

Hand checks are tested against matching analytical models and refused for unsupported variations. Export tests cover escaped user text, model fingerprints, explicit evidence labels and rejection of cached results in learning-project imports.

The [browser review record](../../reports/verification/guided_browser.json) covers the guided bar workflow, successful and unstable comparisons, pointer hover, focus help, definition activation and narrow-window layout. The automated tests cover all four families. Native disclosure controls support touch use, but a pointer activation test is not a physical touchscreen test. A full keyboard-only and screen-reader review is still needed; focus visibility was checked, but Enter/Space activation could not be confirmed through the browser tool.

## How close should the answers be?

For well-conditioned analytical examples, target relative error at or below 10⁻⁸. For matching independent models, target 10⁻⁶.

Relative error compares the error with the size of the expected answer. Near zero, use an absolute tolerance stated in that quantity's units. Do not divide by zero or combine metres and radians as if they were the same quantity.

A small solver residual means the numerical equations are balanced. It does not prove that the chosen supports or beam theory are physically correct.

## Compare with OpenSees

Create a separate environment so the reference solver is not part of the application:

~~~powershell
py -3.12 -m venv .reference-venv
.\.reference-venv\Scripts\python -m pip install -r reference-requirements.lock
.\.reference-venv\Scripts\python -m pip install -e . --no-deps
.\.reference-venv\Scripts\python scripts/verify_opensees.py
~~~

The script compares the four element families, a rotational support spring and four Timoshenko slenderness cases. Its [result file](../../reports/verification/opensees.json) identifies the reference.

Use identical units, supports and theory when comparing solvers. Different assumptions can give different correct answers.

## Convergence: measure a real approximation error

The convergence script compares the cubic Hermite deflection field with the analytical quartic solution under UDL.

It measures the cubic field before the exact UDL correction used in the displayed result. Otherwise this uniform-beam example would already be exact and would not show useful convergence.

Read [the generated report](../05-research-and-experiments/research-report.md) for values and the figure.

## Offline and installation checks

The app binds to 127.0.0.1 and disables usage telemetry. A test blocks Python socket connections while running results and identification views. Browser review found local assets. Plotly HTML includes its required plotting code.

The OS internet adapter was not disabled. These checks do not claim that every browser was tested under a full network outage.

The built wheel was installed into a fresh Python 3.12 environment, where solve and fit commands ran. This is a local installation check. Linux CI is configured, but no completed remote CI run is claimed.

The [learning installation check](../../reports/verification/learning_install.json) also runs each family, its explanation, balance checks, learning-project round trip and report in a separate environment. It checks synthetic fitting and reserved predictions. It does not install the optional browser app in that environment. To repeat it after installing the wheel, use that environment's Python:

~~~powershell
python scripts/verify_learning_install.py --output reports/verification/learning_install.json
~~~

## Read next

- [What has and has not been checked](evidence-status.md)
