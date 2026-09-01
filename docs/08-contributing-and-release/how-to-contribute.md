# Contribute as a student or developer

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


You do not need to write a new FEM element to help. A clear explanation, checked example or useful bug report can improve the project.

## Choose a contribution

| Your experience | Useful first task |
|---|---|
| Early BSc civil engineering | Find an unclear term and suggest a plain-English explanation |
| Strength of materials | Check a supplied bar or beam result by hand |
| Structural analysis | Add a small stable truss or frame example with an expected answer |
| Python beginner | Improve an input message or document a command |
| Numerical methods | Check reactions, energy, unit changes or difficult support cases |
| Laboratory work | Review the measurement protocol without inventing measurements |
| Research writing | Explain a limitation or connect a claim to a suitable source |

Read [project goals](../01-project-vision/vision-and-goals.md) and [limits](../01-project-vision/requirements.md) before proposing a large feature.

## A good first contribution

Work through [the axial bar example](../02-getting-started/first-model.md). Then explain what should happen when area doubles while force stays the same.

A useful submission includes the changed model, hand calculation, units, expected displacement/stress and the actual result. State that it is a numerical example, not a real experiment.

## How to report a problem

Describe what you tried, what you expected and what happened. Include the smallest model or input file that shows the issue, your Python version and the command or app steps.

For a numerical issue, include an analytical or trustworthy matching reference where possible. Screenshots can help, but they should not replace the input file.

Do not post credentials, private lab data or restricted material. Read [security guidance](../../SECURITY.md) for sensitive issues.

## How to propose a code or document change

If you are working locally, make a separate Git branch with a clear name. After the public repository exists, contributors can use a fork and pull request.

A **pull request** is a proposed change for review. Explain:

1. The problem or missing explanation.
2. What changed and why.
3. The expected behavior or learning benefit.
4. The checks you ran.
5. Any limits, sources or AI assistance.

Keep one change focused. Do not include your virtual environment or temporary results.

## Check your work

For a documentation-only change:

~~~powershell
.\.venv\Scripts\python scripts/check_docs.py
~~~

Read the changed page from the root README and follow its related links. Ask whether a BSc student could understand the first paragraph.

For a code change, also run the [software checks](../07-testing-and-evidence/verification.md). A numerical change needs an appropriate test, not just a screenshot.

## Review expectations

To improve a term definition, edit the shared [terminology source](../../src/fem_solver/terms.py), then run `python scripts/build_learning_docs.py`. The glossary is generated from that source. Check the meaning in the app, including table headings and keyboard use.

To add a teaching rule, use the [learning module](../../src/fem_solver/learning.py). State the conditions under which the explanation or hand formula applies. Test both a matching model and a similar model that must not receive the formula. Keep numerical explanations separate from interface code and do not infer missing physical properties.

New examples can include a question, prediction and one-change comparison. Explain the expected benefit for a student and keep the original model intact. See [the problem-solving guide](../03-engineering-knowledge/problem-solving.md).

Do not change expected results just to make a failed test pass. Do not remove a warning without understanding it. Keep code, examples and explanations consistent.

A new physical claim needs real data and permission to share it. A new method should be described with sources and clear limits.

See [authorship and AI assistance](ai-and-authorship.md) and [documentation rules](../09-project-records/documentation-guide.md).

## Read next

- [Explain authorship and AI assistance](ai-and-authorship.md)
