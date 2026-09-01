# Decision 1: use a Python package and a local browser app

[Project home](../../../README.md) · [Documentation map](../../README.md) · [Section guide](README.md)


Status: accepted.

An ADR is a short architecture decision record. It explains a choice so future contributors know why it was made.

## Need

The owner needs a solver that runs on a local PC and exposes its calculations. The same numerical code should work in the app, scripts and research runs.

## Choice

Write the FEM engine directly in Python. Use NumPy and SciPy for numerical operations. Use Streamlit and Plotly for the optional local interface.

Use JSON and CSV files. Do not add a database, account system or cloud service. Keep OpenSees in a separate comparison environment.

## Alternatives considered

A native desktop interface and a separate JavaScript frontend would add interface and packaging work. Wrapping another FEM engine would not meet the goal of implementing the element calculations directly.

## Effects of the choice

Installation needs Python packages. The core can run without the app. Very large models may be slow to draw. Remote access and login protection are not provided.

## Read next

- [Design decision guide](README.md)
- [Decision 2: fit compliance](ADR-0002-compliance-identification.md)
