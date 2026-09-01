# Instructions for coding assistants

[Project home](README.md) · [Code design](docs/06-software-design/architecture.md) · [Current state](docs/09-project-records/working-memory.md)

This is an educational and research FEM project with a local Streamlit app.

Before significant changes, read the [architecture](docs/06-software-design/architecture.md), [equations](docs/03-engineering-knowledge/numerical-methods.md), [checks](docs/07-testing-and-evidence/verification.md) and [working memory](docs/09-project-records/working-memory.md).

- Keep the numerical core separate from Streamlit, Plotly and reference FEM libraries.
- Store internal quantities in SI. Do not combine translations and rotations in one error measure without suitable scaling.
- Do not add artificial stiffness to mechanisms, invert stiffness matrices or hide failed solves.
- Keep analytical, synthetic, reference-solver and measured evidence distinct.
- Never invent measurements, authorship, completed checks or admissions claims.
- The 26-week guide is optional reading, never a scheduling condition.
- Write user-facing text in simple English. Define technical terms without changing equations or file keys.
- Keep every documentation page linked from the root README and back to it. Follow the [documentation guide](docs/09-project-records/documentation-guide.md).
- Run pytest, Ruff lint/format and mypy after relevant code changes. Run scripts/check_docs.py after documentation changes. Use the project environment.
- Update actual status in [working memory](docs/09-project-records/working-memory.md) and [milestones](docs/09-project-records/milestones.md). Keep these permanent instructions stable.
- Do not publish, add cloud services or contact people without the user's authorization.
