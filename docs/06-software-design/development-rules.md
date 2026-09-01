# Rules for reliable changes

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


These rules protect the numerical meaning and evidence of the project.

1. Keep the numerical code separate from interface code.
2. Store Model and SolveResult values in SI. Convert only at input and display boundaries.
3. Do not form an explicit inverse of the stiffness matrix.
4. Do not hide an unstable model by adding artificial stiffness.
5. Keep the original system for reaction recovery. Report spring reactions separately.
6. Preserve load-case separation and prescribed support movements.
7. Reject invalid or unsupported inputs with a useful message.
8. Use meaningful checks against expected physical or numerical behavior.
9. Keep synthetic, analytical, reference-solver and measured evidence distinct.
10. Never invent tests, measurements, authorship, review or admissions outcomes.

## When you change behavior

Explain the problem, the change and its effect. Update the affected examples, tests and documentation together.

A numerical test should compare with a hand solution, an independent implementation or a physical identity such as equilibrium. A test that repeats the same implementation formula may miss the same error twice.

If a result changes, investigate before replacing the expected result.

## Writing and records

Use simple English for documentation, interface messages and reports. Define technical terms. Do not rename established JSON or Python fields only to make the prose simpler.

Keep stable assistant instructions in [AGENTS](../../AGENTS.md). Record changing status in [working memory](../09-project-records/working-memory.md). Record important design choices in [decision notes](decisions/README.md).

## Before sharing a change

Run the [checks](../07-testing-and-evidence/verification.md). Review private data, licenses and author details. Public release is a separate action, not an automatic result of finishing code.

## Read next

- [Rules for a clear interface](interface-design.md)
- [Design decision guide](decisions/README.md)
