# Rules for a clear interface

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


The interface should help a student understand an engineering result. Decoration must not hide units, signs, warnings or assumptions.

## Visual rules

Use a light background, white result panels, navy text and blue controls. The main colors are #F7F9FC, #FFFFFF, #13243A and #2563EB. Use local fonts; do not require a remote font service.

Use clear headings and short sentences. Keep technical names when useful, but explain them nearby or in the glossary.

The default route is Define → Understand → Solve and Discuss. Direct access uses the same components. Do not hide an automatic solve inside model saving or matrix inspection.

Use the shared terminology source for dotted prose terms, native table-header help and plot explanations. Definitions support hover, keyboard focus and native disclosure activation. A fixed definition panel stays within narrow windows. Keep a searchable glossary for people who do not use hover.

Show actual diagnostic values with a plain-English meaning. Preserve machine-readable keys in downloads. Do not replace the interface with unexplained raw JSON.

Offer **Read as text** alternatives for model values, matrices, results, checks and research tables. Use HTML captions and column headers, retain units and small values, escape user text and paginate long tables. These additions help access, but they do not replace a real keyboard and screen-reader review.

Do not use color alone to distinguish training and reserved observations. The plots also use circles, diamonds and legend labels.

## Scientific plots

Keep equal geometry-axis scales. Always show deformation magnification and the original geometry. Show units on axes and signs in captions.

Use a signed, diverging scale for normal stress. Explain whether the value is top-fiber stress or axial stress. Do not suggest that a line-element plot is a detailed continuum stress field.

The unsolved preview follows input units. Support and spring hover labels on the solved structure keep their explicitly shown SI units. Other result plots and tables support both declared display systems. JSON results, the discussion and matrix inspection remain SI.

## Calculation inspection

Member selection should connect a member to its properties, matrix and results. For up to 120 DOFs, show a full global matrix. For larger models, show nonzero positions instead of unreadably small entries.

Large models are better handled through Python or the CLI because drawing many member traces can be slow.

## Failure and empty states

Explain why a model failed and what the user should check. Do not label a successful fit as physically validated or structurally safe.

The measured-data view must say that findings are pending when there are no actual readings.

## Documentation rules

Use the same terms in the app and the documents. Keep stable field names such as EI, schema_version and holdout, and explain their meaning in simple English.

See [writing and navigation rules](../09-project-records/documentation-guide.md).

## Read next

- [How the code is organized](architecture.md)
- [Rules for reliable changes](development-rules.md)
