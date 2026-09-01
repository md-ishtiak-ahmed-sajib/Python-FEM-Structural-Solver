# Save results and run commands

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


Exporting saves a result outside the current app session. A saved image alone is not enough to repeat a calculation; save the model and settings too.

## Files from the app

| Export | Contents | Best use |
|---|---|---|
| Model JSON | Input geometry, properties, supports, loads and units | Repeat or share the model |
| Learning-project JSON | Model, question, boundary notes, targets and prediction | Resume the learning problem and recompute results |
| Draft JSON | Current editor inputs, which may be incomplete | Back up unfinished entries; correct them before model import |
| Learning-report HTML | Method, nodal results, sampled member/stress ranges, checks, comparison, limits and an embedded interactive figure | Read the calculation and its explanation offline |
| Results JSON | SI results, warnings, checks and a model fingerprint | Read exact numerical output |
| Nodal CSV | Movements and separate support/spring reactions | Inspect a table |
| Interactive HTML | The structure plot and its bundled Plotly code | Open the figure without an internet asset download |
| Member PNG | A static member diagram with units | Add a figure to a report |
| Observation CSV | Observation values used for fitting | Repeat the fit |
| Identification HTML | Readable estimates, uncertainty, errors and warning tables, followed by the raw reproduction record | Review the study result |

For real tests, keep the original raw CSV separately. The observation download contains corrected movements with zero set to zero; it does not replace your original instrument readings or zero log.

## Run a calculation without the browser

Run commands from the project root after installing the full environment:

~~~powershell
.\.venv\Scripts\python -m fem_solver solve examples/portal_frame.json --output results/portal
.\.venv\Scripts\python -m fem_solver fit examples/synthetic_observations.csv --length 1 --ei-reference 1000 --output results/fit
.\.venv\Scripts\python -m fem_solver study --trials 200 --seed 2027 --output results/study
~~~

The solve command writes model.json, results.json and nodes.csv. The fit command writes identification.json and report.html. The study writes summary.csv, a manifest and study figures.

Use --help after fem_solver or a command name to see its options. A CLI is simply a command-line interface.

## Repeat the public numerical report

~~~powershell
.\.venv\Scripts\python scripts/reproduce_artifacts.py
~~~

This rewrites the example files, empty bench templates, synthetic results, convergence figure and generated [research report](../05-research-and-experiments/research-report.md). Do not store real observations in template files.

OpenSees comparisons use a separate environment. Follow [verification](../07-testing-and-evidence/verification.md).

## Generate complete example learning reports

~~~powershell
.\.venv\Scripts\python scripts/export_learning_examples.py
~~~

This writes bar.html, truss.html, beam.html, frame.html and identification.html in results/learning-reports. Each structural report includes a comparison with twice the applied load. The study report uses a declared synthetic generator, not real readings. Open the HTML files locally; their plots include the needed JavaScript.

## Before sharing

Rebuild the shared glossary and original element-family diagrams with `python scripts/build_learning_docs.py`. Check that the generated glossary matches the app with `python scripts/build_learning_docs.py --check`.

Learning HTML records the model/case fingerprint and solver version. Its figures bundle Plotly locally. User text is escaped, and a comparison failure stays visible in the report. Keep the learning-project JSON too; a report is not a replacement for reproducible input.

Keep units, signs, model assumptions, file versions and warnings. Label generated observations as synthetic.

Check permission before sharing lab data or photographs. Temporary outputs go in results/, which is excluded from Git. Review every file selected for a release.

## Read next

- [Python functions and model files](python-and-json.md)
- [Understand errors and unexpected results](troubleshooting.md)
