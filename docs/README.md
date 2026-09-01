# Documentation map

[Project home](../README.md)


This documentation is written for BSc civil engineering students. You do not need to read every page before trying the app.

## Choose a reading path

| You want to... | Follow this path |
|---|---|
| Understand what was built and why | [Vision](01-project-vision/vision-and-goals.md) → [Features](01-project-vision/features.md) → [Evidence](07-testing-and-evidence/evidence-status.md) |
| Run your first model | [Install](02-getting-started/installation.md) → [Bar example](02-getting-started/first-model.md) → [App guide](04-user-guide/app-guide.md) |
| Learn the calculations | [FEM basics](03-engineering-knowledge/fem-basics.md) → [Units](03-engineering-knowledge/units-and-signs.md) → [Worked examples](03-engineering-knowledge/worked-examples.md) → [Equations](03-engineering-knowledge/numerical-methods.md) |
| Understand the research | [Question](05-research-and-experiments/research-question.md) → [Study plan](05-research-and-experiments/study-protocol.md) → [Report](05-research-and-experiments/research-report.md) |
| Help improve the project | [Contribution guide](08-contributing-and-release/how-to-contribute.md) → [Code map](06-software-design/architecture.md) → [Checks](07-testing-and-evidence/verification.md) |

## Ordered sections

| Folder | Purpose |
|---|---|
| [01-project-vision](01-project-vision/README.md) | Why this project exists and what it can do |
| [02-getting-started](02-getting-started/README.md) | Install the software and understand your first result |
| [03-engineering-knowledge](03-engineering-knowledge/README.md) | Learn the ideas behind the calculations |
| [04-user-guide](04-user-guide/README.md) | Use the app, Python functions and exported files |
| [05-research-and-experiments](05-research-and-experiments/README.md) | Study beam stiffness and prepare honest physical tests |
| [06-software-design](06-software-design/README.md) | Understand how the code works and why it was written this way |
| [07-testing-and-evidence](07-testing-and-evidence/README.md) | Check calculations and understand what the evidence proves |
| [08-contributing-and-release](08-contributing-and-release/README.md) | Help improve the project and prepare a public release |
| [09-project-records](09-project-records/README.md) | Track work and keep the documentation useful |

## How the pages connect

~~~mermaid
flowchart LR
    A["Project home"] --> B["Section guide"]
    B --> C["Topic page"]
    C --> D["Example, equation or evidence"]
    C --> E["Related topic"]
    C --> A
~~~

Start at the project home, choose a section, and open a topic. Topic pages link to examples, evidence and related pages. Every page has a way back home.

The [root README](../README.md) contains the complete page index. The [project map](02-getting-started/project-map.md) explains the code and data folders.

The 26-week guide is optional learning material. Physical findings are pending until real data exists.

## Read next

- [Project vision](01-project-vision/vision-and-goals.md)
- [Your first calculation](02-getting-started/first-model.md)
