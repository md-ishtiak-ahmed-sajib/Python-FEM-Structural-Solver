# Security and safe use

[Project home](README.md) · [Installation](docs/02-getting-started/installation.md) · [Release guide](docs/08-contributing-and-release/release-guide.md)

## Keep the app local

Run on 127.0.0.1, which is your own computer. Do not expose the app to a network or the internet without a separate security review. There is no login protection.

## Treat files as data

Models use JSON and observations use CSV. Do not execute uploaded expressions or add pickle support.

Uploads are limited to 5 MB. Models are limited to 10,000 nodes and 20,000 members. Observations are limited to 10,000 rows, and bootstrap runs to 5,000 samples. These limits reduce accidental large requests; they are not a complete defense against misuse.

## Protect private information

No credentials are required. Do not commit passwords, personal test details or private institutional data. Real bench files are ignored by Git unless deliberately selected for publication.

Reports escape user text so it is not read as HTML. Nodal CSV exports protect labels that start like spreadsheet formulas. Still review files before opening or sharing them.

Interactive HTML contains Plotly JavaScript. Treat unknown HTML from other people as code that can run in a browser. The app does not accept arbitrary HTML uploads.

## Report sensitive issues

Before publishing, the owner should enable GitHub private vulnerability reporting and choose a maintainer contact. No contact address is invented here. Use private reporting when available instead of posting sensitive exploit details publicly.

This is not certified engineering software. Keep numerical warnings and physical limits visible.
