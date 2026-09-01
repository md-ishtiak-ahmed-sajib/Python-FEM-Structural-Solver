# Changelog

[Project home](README.md) · [Milestones](docs/09-project-records/milestones.md) · [Evidence status](docs/07-testing-and-evidence/evidence-status.md)

## 2026-09-01: engineering-studio redesign for v0.2.0

Added a permanent Home launchpad with original Bar, Truss, Beam and Frame diagrams, blank/example actions, import and current-session resume. Rebuilt the sidebar, responsive stage indicator, Define split workspace, eight-step Understand map, four-part matrix laboratory, Solve result dashboard, stiffness-study dashboard and filtered glossary around one shared local design system.

Replaced clipped Streamlit metrics with complete semantic result cards, large term strips with a compact Key terms control, and document-like result pages with progressive panels and result tabs. Added an explicit viewing range for one-dimensional geometry while preserving equal axis scales. No numerical interface, JSON format or solver equation changed.

Learning and stiffness reports now share a responsive, self-contained engineering-studio design with a header, evidence label and table of contents. Added launchpad, navigation, stage, stale-state, metric, glossary and report tests. Browser review covers 1440, 1024, 760 and 390 pixel widths; screen-reader and physical touchscreen review remain pending. The [v0.2.0 release](https://github.com/md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver/releases/tag/v0.2.0) was published after its exact commit passed [Windows, Ubuntu and independent OpenSees jobs](https://github.com/md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver/actions/runs/33475674805).

## 2026-09-01: public v0.1.0 release

Committed the reviewed 117-file source set with the owner's verified public GitHub identity and published it at [md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver](https://github.com/md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver). Added repository metadata, public citation details, topics and private vulnerability reporting. Updated the workflow to the current Node 24 action generation after the first clean remote run reported a deprecation warning. The clean Windows, Ubuntu and OpenSees jobs then passed, and [v0.1.0](https://github.com/md-ishtiak-ahmed-sajib/Python-FEM-Structural-Solver/releases/tag/v0.1.0) was published with the wheel, source archive and checksums. Physical validation and another person's reproduction remain pending.

## 2026-08-31: acceptance audit and readable outputs

Added a requirement-by-requirement audit and a manual accessibility checklist. Added read-only HTML table alternatives for model data, matrices, results, comparisons and study outputs. Tables have captions, column headers, declared units and small-number formatting.

Learning reports now include sampled member-force and stress ranges. Identification reports now show estimates, uncertainty, errors and diagnostic meanings before the raw record. Added a repeatable script for all four learning reports and a synthetic study report. Beam-only comparisons no longer suggest changing A to change bending stiffness.

Expanded runtime network-blocking checks to all four guided families, comparisons and glossary. Physical measurements and independent-person reproduction are still not claimed.

## 2026-08-31: guided engineering learning

Added Define, Understand, and Solve and Discuss stages with direct access. Draft saving and equation inspection no longer solve automatically. Added problem briefs, cut-boundary notes, optional predictions, guarded analytical explanations, balance checks and one-change comparisons that preserve the baseline.

Added a shared glossary with hover, focus and activation help, readable diagnostics, learning-project JSON and self-contained learning reports. Model JSON and the public solve, assembly and fitting interfaces remain compatible.

Added engine equations, a workflow diagram, original element-family drawings and the accurately labeled convergence graph to the root README. Updated linked student guides and the glossary-generation check. No new physical measurements or public-release claims were added.

## 2026-08-31: documentation and language update

Grouped documentation into nine ordered topic folders. Added section guides, root links, related-page navigation and a full root index.

Added student explanations, a glossary, hand-worked bar and beam examples, reading paths, troubleshooting and a contribution guide. Updated generated-report paths and language so repeated studies keep the new organization.

Preserved equations, file formats, numerical assumptions and the distinction between synthetic and measured evidence. The 26-week guide remains optional learning material.

## 0.1.0: initial local implementation

Added bar, truss, Euler–Bernoulli beam and 2D frame calculations, sparse assembly, supports, springs, separate load cases, member forces, stresses, units and JSON files.

Added the local app, exports, repeatable synthetic study, separate reference comparisons and preparation for real measurements.

Physical validation and another person's reproduction remain separate pending tasks. Public repository status is recorded in the release guide.
