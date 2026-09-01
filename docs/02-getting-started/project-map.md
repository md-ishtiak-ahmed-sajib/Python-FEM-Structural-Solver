# Where files and folders belong

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


The repository is the full project folder. Its root README is the main entrance.

~~~text
Python-FEM-Structural-Solver/
├── README.md             Main guide and full documentation index
├── docs/                 Explanations, instructions and project records
├── src/fem_solver/       Python calculation package
├── app.py                Local browser interface
├── examples/             Small models and clearly labeled synthetic data
├── tests/                Automatic checks with expected results
├── scripts/              Study, reference, documentation and release tools
├── data/bench/           Empty templates for future real measurements
├── reports/              Selected numerical results that readers can inspect
├── results/              Local working outputs; not included in Git
├── .streamlit/           Local app settings
├── .github/workflows/    Checks to run after publication on GitHub
└── run-local.cmd         Windows launcher
~~~

## Where should I add something?

| Your change | Place |
|---|---|
| Explain a civil engineering idea | [Engineering knowledge](../03-engineering-knowledge/README.md) |
| Explain why the project matters | [Project vision](../01-project-vision/README.md) |
| Add a small model someone can repeat | examples/, with a link in the [user guide](../04-user-guide/README.md) |
| Change a calculation | src/fem_solver/, with a meaningful check in tests/ |
| Record a software design decision | [Design decisions](../06-software-design/decisions/README.md) |
| Record completed work | [Project records](../09-project-records/README.md) |
| Prepare a physical test | [Research and experiments](../05-research-and-experiments/README.md) |
| Save a temporary export | results/ |

## Folders that are not part of the public source

.venv and .reference-venv contain installed Python tools. build and dist contain package files. results contains local work.

These folders are excluded from Git. Real bench files are also excluded by default; only empty templates are included. A person must review permission, privacy and evidence before sharing real data.

## Why standard files stay at the root

GitHub and other tools expect [CONTRIBUTING](../../CONTRIBUTING.md), [SECURITY](../../SECURITY.md), [LICENSE](../../LICENSE), [CITATION.cff](../../CITATION.cff) and [CHANGELOG](../../CHANGELOG.md) here.

[AGENTS](../../AGENTS.md) contains stable instructions for coding assistants. Changing project status belongs in working memory, not in those instructions.

## Read next

- [Your first bar calculation](first-model.md)
