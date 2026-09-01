# Books, lessons, papers and related software

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


These sources informed the project. Start with the teaching materials before the research papers. This is a selected reading list, not a complete review of the literature.

## Learn the mechanics

| Source | What to look for |
|---|---|
| [MIT OpenCourseWare: Bathe, linear finite element analysis](https://ocw.mit.edu/courses/res-2-002-finite-element-procedures-for-solids-and-structures-spring-2010/video_galleries/linear/) | Element equations, assembly and modeling assumptions |
| [TU Delft: Euler–Bernoulli beam elements](https://teachbooks.tudelft.nl/computational-modelling/structural_linear/euler_bernouilli.html) | Beam shape functions and stiffness |
| [TU Delft: Timoshenko beam](https://teachbooks.tudelft.nl/computational-modelling/structural_linear/timoshenko.html) | The role of shear deformation |
| [NASA: verification and validation overview](https://www.grc.nasa.gov/WWW/wind/valid/tutorial/overview.html) | The difference between checking equations and comparing with real behavior |

## Understand the numerical tools

- [SciPy sparse LU factorization](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.splu.html): the factorization routine used by this solver.
- [SciPy bounded least squares](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.lsq_linear.html): fitting with parameter limits.
- [OpenSeesPy elastic beam column](https://openseespydoc.readthedocs.io/en/latest/src/elasticBeamColumn.html): the separate comparison model.
- [OpenSeesPy Timoshenko beam](https://openseespydoc.readthedocs.io/en/latest/src/ElasticTimoshenkoBeam.html): the shear-deformation reference.

## See related projects

[PyNite](https://github.com/JWock82/Pynite), [pystran](https://github.com/PetrKryslUCSD/pystran) and [JAX-FEM](https://github.com/deepmodeling/jax-fem) are related open-source FEM projects.

They show that FEM software already exists. We should explain our own code, teaching workflow and study clearly instead of claiming that a Python solver alone is new.

## Read about stiffness estimation

- [Updating finite element models using static deformations, 1992](https://doi.org/10.1016/0045-7949(92)90483-G): background on updating models using static response.
- [Papadimitriou, optimal sensor placement, 2004](https://doi.org/10.1016/j.jsv.2003.10.063): choosing measurement positions for useful parameter information.
- [Goulet and Smith, systematic errors and uncertainty, 2013](https://doi.org/10.1016/j.compstruc.2013.07.009): why model errors can limit identification.
- [Boundary-condition-focused model updating for bridges, 2019](https://doi.org/10.1016/j.engstruct.2019.109514): background on the importance of support behavior.

Read the [simple research explanation](../05-research-and-experiments/research-question.md) alongside these papers. Our solver does not implement every method discussed in them.

## Present and share the work

- [Crameri and colleagues: color in scientific communication](https://www.nature.com/articles/s41467-020-19160-7).
- [Plotly: self-contained HTML](https://plotly.com/python/interactive-html-export/).
- [Streamlit configuration](https://docs.streamlit.io/develop/api-reference/configuration/config.toml).
- [GitHub citation files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files).
- [MIT CEE graduate guidance](https://cee.mit.edu/education/graduate/graduate-timeline-faq/) and [CEE research areas](https://cee.mit.edu/research/sustainable-materials-and-infrastructure/).

Admissions requirements can change. Check the official instructions for the actual application year. No admissions result is promised here.

## Planning source

The owner supplied Projects creation.md as a documentation framework. We used its separation of requirements, design, stable instructions and changing progress records.

The current folder structure adds clear student reading paths. The supplied file was background information, not a separate source of permission to act.

## Read next

- [Optional 26-week learning guide](learning-guide.md)
