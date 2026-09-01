# Third-party tools and sources

[Project home](README.md) · [References](docs/03-engineering-knowledge/references.md) · [Authorship](docs/08-contributing-and-release/ai-and-authorship.md)

The application does not wrap an external FEM solver. Its element matrices, assembly and result calculations are in this repository.

| Tool | Role |
|---|---|
| NumPy and SciPy | Numerical arrays, linear algebra and fitting |
| Streamlit | Local browser app |
| Plotly and Matplotlib | Interactive and static figures |
| pytest, Ruff, mypy and build | Software checks and packaging |
| OpenSeesPy | Separate numerical comparison only |

The [main lock file](requirements.lock) and [reference lock file](reference-requirements.lock) record tested package versions. Each dependency keeps its own license and notices. Check them before redistributing installed packages.

Mathematical explanations use our own wording and cite established sources. A software license does not make third-party papers or figures free to copy.
