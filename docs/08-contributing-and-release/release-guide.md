# Prepare a release or project presentation

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


A release is a reviewed version that other people can obtain. It is separate from finishing the local software.

## Check before packaging

From the project root:

~~~powershell
.\.venv\Scripts\python scripts/verify_release.py
.\.venv\Scripts\python scripts/build_learning_docs.py --check
.\.reference-venv\Scripts\python scripts/verify_opensees.py
.\.venv\Scripts\python scripts/reproduce_artifacts.py
.\.venv\Scripts\python scripts/package_source.py
~~~

Review the output of each command. Do not treat a failed check as complete.

The source archive is dist/Python-FEM-Structural-Solver-source.zip. It includes source, documents, templates and selected numerical results. It excludes environments and private bench records.

The wheel contains the Python package. Use the repository or source archive for the app, examples and full documentation.

For the learning update, test Define, Understand, explicit Solve, a failed support comparison, glossary help and learning-report export. Record pointer, keyboard and touch checks separately; do not mark an unperformed browser check as complete. Include the shared glossary and element-family figures in the source archive.

## Review names, permissions and claims

Check [LICENSE](../../LICENSE), [CITATION.cff](../../CITATION.cff), [authorship](ai-and-authorship.md) and [third-party software](../../THIRD_PARTY.md).

Use the real public author details. Remove credentials, private metadata, unnecessary machine paths and data without permission.

Check that synthetic figures still say synthetic. Keep physical validation and another person's reproduction pending until evidence exists.

## Owner's public destination

The owner selected [md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver](https://github.com/md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver). The reviewed source was committed with the public account identity and pushed to its main branch. Issues are enabled, the wiki is disabled and private vulnerability reporting is enabled.

The [v0.1.0 release](https://github.com/md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver/releases/tag/v0.1.0) was published after its exact commit passed the Windows, Ubuntu and independent OpenSees jobs. It includes the installable numerical-package wheel, the reviewed full-source archive and SHA-256 checksums.

Publishing source does not prove that another person reproduced it. That evidence needs a separate run by another person.

## A simple project demonstration

1. State the engineering question and assumptions.
2. Show the bar hand calculation and software answer.
3. Show a frame's loads, supports and enlarged displacement.
4. Follow a member result into its stiffness matrix.
5. Recover EI from several synthetic observations.
6. Show the one-sensor ambiguity case.
7. Explain why bench findings are still pending.

A demonstration should show both a useful result and a limitation.

## A graduate application summary

Explain the problem, your actual contribution, the evidence and the remaining work in your own words. Link the project only where the application permits it.

Do not assume a reviewer will install the software. A short clear figure and explanation can help, but follow the official submission rules. Recheck the relevant application year using [official references](../03-engineering-knowledge/references.md).

## Read next

- [Explain authorship and AI assistance](ai-and-authorship.md)
