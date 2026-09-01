"""Reviewed terminology. This is the single source for app help and the glossary."""

import re
from dataclasses import dataclass
from html import escape


@dataclass(frozen=True)
class Term:
    label: str
    meaning: str
    guide: str = "03-engineering-knowledge/numerical-methods.md"
    aliases: tuple[str, ...] = ()


TERMS = {
    "fem": Term(
        "FEM",
        "Finite element method: split a model into connected pieces, write their equations, and solve them together.",
        aliases=("finite element method",),
    ),
    "node": Term(
        "Node",
        "A point where members connect and movements or loads are represented.",
        aliases=("nodes", "nodal"),
    ),
    "element": Term(
        "Element",
        "One small part of the mathematical model. Here it is a straight bar, truss, beam or frame member.",
        aliases=("elements", "member", "members"),
    ),
    "dof": Term(
        "Degree of freedom",
        "One movement or rotation represented at a node.",
        aliases=("DOF", "DOFs", "degrees of freedom"),
    ),
    "ux": Term(
        "ux", "Movement in the global x direction. Positive means right; measured in m or mm."
    ),
    "uy": Term("uy", "Movement in the global y direction. Positive means up; measured in m or mm."),
    "rz": Term(
        "rz",
        "Rotation about the out-of-plane z axis. Positive means counterclockwise; measured in radians.",
    ),
    "rotation": Term(
        "Rotation",
        "A change in angle. One radian is about 57.3 degrees.",
        aliases=("rotations", "radian", "radians", "rad"),
    ),
    "translation": Term(
        "Translation",
        "A movement along an axis, without referring to rotation.",
        aliases=("translations",),
    ),
    "displacement": Term(
        "Displacement",
        "How far a point moves from its original position, with a direction and a unit.",
        aliases=("displacements", "movement"),
    ),
    "deflection": Term(
        "Deflection", "Movement across a member, often called the bending movement of a beam."
    ),
    "constraint": Term(
        "Constraint",
        "A rule that sets a node movement or rotation to a known value.",
        aliases=("constraints", "restraint", "restraints"),
    ),
    "prescribed": Term(
        "Prescribed displacement",
        "A movement or rotation whose value you set instead of asking the solver to find it. It may be zero or a support settlement.",
        aliases=("prescribed movements", "prescribed DOF", "settlement"),
    ),
    "support": Term(
        "Support",
        "A connection to the surroundings that restrains movement or resists it with a spring.",
        aliases=("supports",),
    ),
    "fixed": Term(
        "Fixed support",
        "A support that prevents every movement and rotation available in this element family.",
    ),
    "pin": Term(
        "Pinned support",
        "A support that prevents translations but allows rotation where the model includes rotation.",
        aliases=("pin",),
    ),
    "roller": Term(
        "Roller",
        "A support that prevents one translation and allows movement in the other direction. This app uses global-axis rollers.",
    ),
    "spring": Term(
        "Support spring",
        "A support that can move. Its restoring force or moment equals minus stiffness times movement or rotation.",
        aliases=("spring", "springs"),
    ),
    "load": Term("Load", "A force or moment applied to the model.", aliases=("loads",)),
    "case": Term(
        "Load case",
        "One named set of loads solved independently. Loads in different cases are not automatically added.",
    ),
    "udl": Term(
        "Distributed load",
        "Force spread along a member. This engine supports a constant force per unit length in local directions.",
        aliases=("distributed loads", "UDL", "uniform load"),
    ),
    "qx": Term("qx", "Uniform force per unit length along the member's local x axis; N/m or N/mm."),
    "qy": Term("qy", "Uniform force per unit length along the member's local y axis; N/m or N/mm."),
    "material": Term(
        "Material",
        "The substance represented by a stiffness value E, such as an ideal elastic steel.",
        aliases=("materials",),
    ),
    "section": Term(
        "Section",
        "The cross section of a member, described here by area A, bending property I and optional fiber distance c.",
        aliases=("sections", "cross section"),
    ),
    "E": Term(
        "Young's modulus E",
        "Material stiffness: stress divided by strain for the elastic model. A larger E means less stretch under the same stress.",
        aliases=("Young's modulus",),
    ),
    "A": Term(
        "Area A",
        "The area of the member's cross section, in m² or mm². It is used for axial stiffness and stress.",
    ),
    "I": Term(
        "Second moment of area I",
        "A geometric measure of how area is spread about the bending axis. It is measured in m⁴ or mm⁴, not mass units.",
        aliases=("second moment of area",),
    ),
    "fiber": Term(
        "Fiber distance c",
        "Distance from the section's reference bending axis to the top or bottom location where normal stress is reported. It does not fully define the section shape.",
        aliases=("fiber distance", "top fiber", "bottom fiber"),
    ),
    "EA": Term(
        "EA",
        "Axial rigidity: material stiffness E times cross-section area A. The axial element stiffness also depends on its length.",
    ),
    "EI": Term(
        "EI",
        "How strongly a beam resists bending. It combines material stiffness E and section property I. Its unit is N m² or N mm².",
        aliases=("flexural rigidity",),
    ),
    "strain": Term("Strain", "Change in length divided by original length. It has no length unit."),
    "stress": Term(
        "Normal stress",
        "Force per area acting normal to a section. Positive means tension in this engine; negative means compression.",
        aliases=("stress", "stresses", "axial stress"),
    ),
    "axial": Term(
        "Axial force",
        "Internal force along a member. Positive stretches it; negative compresses it.",
        aliases=("axial", "axial forces"),
    ),
    "shear": Term(
        "Shear force",
        "Internal force across a member. Its sign follows the local member convention.",
        aliases=("shear",),
    ),
    "moment": Term(
        "Bending moment",
        "The turning effect that bends a member. Its unit is force times length.",
        aliases=("moment", "moments"),
    ),
    "sagging": Term(
        "Sagging",
        "Positive bending in the engine's local convention: the top side is compressed and the bottom side is stretched.",
    ),
    "reaction": Term(
        "Reaction", "A force or moment supplied by a support.", aliases=("reactions",)
    ),
    "elastic": Term(
        "Elastic",
        "An ideal material that returns to its original state when the load is removed. This engine uses a straight stress–strain relation.",
    ),
    "static": Term(
        "Static", "Loads are treated as steady. Acceleration and vibration are not included."
    ),
    "bar": Term(
        "Bar",
        "A horizontal element that resists stretching or shortening only. Its node movement is ux.",
    ),
    "truss": Term(
        "Truss",
        "A system of straight members that carry axial force only, with ideal pin joints and loads at nodes.",
    ),
    "beam": Term(
        "Beam",
        "A member model that carries transverse load through bending. This engine's beam family is horizontal.",
    ),
    "frame": Term(
        "Frame",
        "Members that carry both axial force and bending, connected by rigid joints in this engine.",
    ),
    "euler": Term(
        "Euler–Bernoulli",
        "Beam theory that includes bending but leaves out shear deformation. It is most useful when shear movement is small.",
    ),
    "timoshenko": Term(
        "Timoshenko",
        "Beam theory that also includes shear deformation. It is a reference or future method, not an element in this engine.",
    ),
    "idealization": Term(
        "Idealization",
        "A simplified mathematical description of a real object, including what behavior is left out.",
        aliases=("modeling assumptions",),
    ),
    "stiffness": Term(
        "Stiffness", "How much force or moment is needed to produce a movement or rotation."
    ),
    "matrix": Term(
        "Stiffness matrix",
        "A table of coefficients connecting node movements to the forces needed to produce them.",
        aliases=("matrix", "matrices"),
    ),
    "local": Term(
        "Local axes",
        "Directions attached to a member: x from its start to its end, and y 90 degrees counterclockwise from x.",
        aliases=("local directions",),
    ),
    "global": Term(
        "Global axes",
        "The shared directions for the whole model: x right and y up.",
        aliases=("global directions",),
    ),
    "cosine": Term(
        "Direction cosine",
        "The cosine of the angle from global x to local x. It is a direction number, not the section's fiber distance c.",
        aliases=("cosine",),
    ),
    "sine": Term(
        "Direction sine",
        "The sine of the angle from global x to the member's local x axis.",
        aliases=("sine",),
    ),
    "transform": Term(
        "Coordinate transformation",
        "A change between member directions and the shared directions of the structure. T maps global movements to local movements.",
        aliases=("transformation",),
    ),
    "assembly": Term(
        "Assembly",
        "Adding the element equations at shared node movements to form the whole structure's equations.",
    ),
    "free": Term(
        "Free DOF",
        "A movement or rotation that has not been prescribed. The solver must find its value.",
        aliases=("free DOFs",),
    ),
    "rhs": Term(
        "Right-hand side",
        "The known force terms in an equation, including the effect of prescribed support movements.",
        aliases=("RHS",),
    ),
    "sparse": Term(
        "Sparse matrix",
        "A matrix stored mainly by its nonzero entries, saving space when most entries are zero.",
        aliases=("sparse", "sparsity", "COO", "CSR"),
    ),
    "lu": Term(
        "LU factorization",
        "A standard way to split a matrix into triangular parts so equations can be solved without forming an inverse.",
        aliases=("LU",),
    ),
    "residual": Term(
        "Residual",
        "The imbalance left after solving the equations. A small value checks the calculation, not structural safety.",
        aliases=("scaled residual", "scaled backward error"),
    ),
    "eigenvalue": Term(
        "Scaled eigenvalue",
        "A number used to check the stiffness equations after scaling. A tiny value can indicate an unsupported movement or a difficult numerical system.",
        aliases=("eigenvalue",),
    ),
    "energy": Term(
        "Strain energy",
        "Elastic energy stored by the model's nodal stiffness and its support springs; reported in joules. The displayed check uses this same discrete system.",
    ),
    "equilibrium": Term(
        "Equilibrium",
        "Applied forces and support reactions balance; their moments must balance too.",
    ),
    "mechanism": Term(
        "Mechanism",
        "A movement that the model cannot resist. Check connections and real supports instead of adding artificial stiffness.",
        aliases=("unstable",),
    ),
    "conditioning": Term(
        "Ill-conditioned",
        "Small input or rounding changes can strongly affect the answer. Inspect support choices and very different stiffness values.",
    ),
    "shape": Term(
        "Shape function",
        "A function that describes movement inside an element from its node movements.",
        aliases=("shape functions", "Hermite", "interpolation"),
    ),
    "consistent": Term(
        "Consistent nodal loads",
        "Equivalent end loads calculated with the same shape functions as the element, including end moments where needed.",
    ),
    "mesh": Term("Mesh", "The collection of elements and nodes used to represent the structure."),
    "convergence": Term(
        "Convergence",
        "Checking whether a real approximation error decreases as the model is refined. More elements do not fix wrong physical assumptions.",
    ),
    "magnification": Term(
        "Deformation magnification",
        "The factor used to enlarge movement in the drawing. It changes the picture, not the calculated result.",
    ),
    "si": Term(
        "SI",
        "The internal unit system: metres, newtons and pascals, with rotations in radians.",
    ),
    "newton": Term(
        "Newton (N)",
        "The unit of force used here. Moments use force times length, such as N m.",
        aliases=("newton", "newtons"),
    ),
    "pascal": Term(
        "Pascal (Pa)",
        "One newton per square metre. It is a unit of stress and Young's modulus.",
        aliases=("Pa", "pascal", "pascals"),
    ),
    "megapascal": Term(
        "Megapascal (MPa)",
        "One million pascals, equal to one newton per square millimetre. Used with N–mm–MPa display units.",
        aliases=("MPa", "megapascal"),
    ),
    "json": Term(
        "JSON",
        "A text file format that stores named data. Model files include a version and declared units.",
        "04-user-guide/python-and-json.md",
    ),
    "csv": Term(
        "CSV", "A text table whose values are separated by commas.", "04-user-guide/exports.md"
    ),
    "compliance": Term(
        "Clamp compliance",
        "Clamp rotation per unit applied moment, in rad/(N m). Zero means a rigid clamp.",
        "05-research-and-experiments/research-question.md",
        ("compliance",),
    ),
    "gamma": Term(
        "Dimensionless clamp compliance",
        "A scaled clamp compliance: gamma = EI_reference × C / length. It compares support rotation with beam bending without carrying units.",
    ),
    "sensitivity": Term(
        "Sensitivity", "How much a predicted measurement changes when a model parameter changes."
    ),
    "rank": Term(
        "Rank",
        "The number of independent parameter effects the measurements can distinguish. Two unknown parameters need two independent effects.",
    ),
    "singular": Term(
        "Singular values",
        "Numbers measuring how clearly different parameter combinations affect the data. A very small value means weak information.",
    ),
    "correlation": Term(
        "Parameter correlation",
        "How strongly fitted parameters can trade off against each other. Values near minus or plus one suggest they are hard to separate.",
    ),
    "bootstrap": Term(
        "Parametric bootstrap",
        "Repeat the fit using simulated measurement errors to estimate uncertainty under the chosen noise model.",
        aliases=("bootstrap",),
    ),
    "uncertainty": Term(
        "Uncertainty",
        "A stated range of doubt in a measurement or estimate. The range depends on the assumptions used to calculate it.",
    ),
    "noise": Term(
        "Noise",
        "Random variation added to or present in measurements. Here its size is declared relative to a characteristic displacement.",
    ),
    "characteristic": Term(
        "Characteristic displacement",
        "A declared reference movement used to set the noise size consistently across measurements.",
    ),
    "rmse": Term(
        "RMSE",
        "Root mean square error: a measure of typical prediction error, with the same units as the measured movement.",
    ),
    "holdout": Term(
        "Reserved cases",
        "Measurements kept out of fitting and used afterward to check predictions.",
        aliases=("holdout", "reserved-case", "reserved prediction cases"),
    ),
    "train": Term(
        "Training observations", "Measurements used to estimate the parameters.", aliases=("train",)
    ),
    "synthetic": Term(
        "Synthetic", "Generated by equations or software. These are not actual bench measurements."
    ),
    "measured": Term(
        "Measured",
        "Read from a real physical test, with specimen details and measurement uncertainty.",
    ),
    "unidentifiable": Term(
        "Unidentifiable",
        "The supplied data cannot uniquely separate the requested parameters. The app must not invent a unique estimate.",
    ),
    "calibration": Term(
        "Calibration",
        "Checking an instrument against a known reference before interpreting its readings.",
    ),
    "zero": Term(
        "Zero reading",
        "An unloaded reference reading subtracted from a later reading to remove the initial offset.",
    ),
    "provenance": Term(
        "Provenance", "Where data came from, such as a real test or a stated synthetic generator."
    ),
    "nonlinear": Term(
        "Nonlinear",
        "A model where response is not proportional to input because geometry, material behavior or contact changes.",
    ),
    "buckling": Term(
        "Buckling",
        "Loss of stability under compression. This linear static solver does not calculate a buckling load.",
    ),
    "yielding": Term(
        "Yielding",
        "Permanent material deformation beyond its elastic range. This engine does not model it.",
    ),
    "continuum": Term(
        "Continuum model",
        "A model that represents an area or volume, rather than only member centerlines, to study more detailed stress patterns.",
    ),
}


TERM_CSS = """
.fem-copy{line-height:1.7;color:#13243a;margin:.4rem 0 1rem}
.fem-term{display:inline-block;position:relative;vertical-align:baseline}
.fem-term details{display:inline}
.fem-term summary{display:inline;cursor:help;border-bottom:1px dotted #2563eb;list-style:none;color:inherit}
.fem-term summary::-webkit-details-marker{display:none}
.fem-term summary:focus-visible{outline:2px solid #2563eb;outline-offset:3px}
.fem-tip{display:none;position:fixed;left:50%;transform:translateX(-50%);bottom:24px;top:auto;z-index:9999;width:min(480px,calc(100vw - 40px));box-sizing:border-box;
background:#13243a;color:white;padding:12px 14px;border-radius:8px;box-shadow:0 6px 18px #13243a35;
font:14px/1.5 Arial,sans-serif;white-space:normal;text-align:left}
.fem-term:hover>.fem-tip,.fem-term:focus-within>.fem-tip,.fem-term:has(details[open])>.fem-tip{display:block}
body:has(.fem-term:hover) .fem-term:not(:hover)>.fem-tip{display:none}
body:has(.fem-term:focus-within):not(:has(.fem-term:hover)) .fem-term:not(:focus-within)>.fem-tip{display:none}
body:has(.fem-term summary:focus-visible) .fem-term:not(:has(summary:focus-visible))>.fem-tip{display:none!important}
.fem-term:has(summary:focus-visible)>.fem-tip{display:block!important}
.fem-key{padding:10px 14px;background:#edf4ff;border-radius:8px;line-height:2}
"""


def help_text(key: str) -> str:
    return TERMS[key].meaning


def term_html(key: str, label: str | None = None) -> str:
    term = TERMS[key]
    return (
        '<div class="fem-term"><details name="fem-help"><summary role="button" tabindex="0" aria-label="'
        + escape((label or term.label) + ": " + term.meaning, quote=True)
        + '">'
        + escape(label or term.label)
        + '</summary></details><span class="fem-tip"><strong>'
        + escape(term.label)
        + "</strong><br>"
        + escape(term.meaning)
        + "</span></div>"
    )


# Only multi-letter terms are matched in prose. E, I, A, c and N require explicit context.
_ALIASES = {
    label.lower(): key
    for key, term in TERMS.items()
    for label in (term.label, *term.aliases)
    if len(label) > 1
}
_PATTERN = re.compile(
    r"(?<![\w])("
    + "|".join(re.escape(s) for s in sorted(_ALIASES, key=len, reverse=True))
    + r")(?![\w])",
    re.IGNORECASE,
)


def annotate(text: str) -> str:
    """Escape all input; annotate known prose terms without matching short symbols."""
    pieces: list[str] = []
    offset = 0
    for match in _PATTERN.finditer(text):
        pieces.extend(
            (escape(text[offset : match.start()]), term_html(_ALIASES[match[0].lower()], match[0]))
        )
        offset = match.end()
    pieces.append(escape(text[offset:]))
    return '<div class="fem-copy">' + "".join(pieces) + "</div>"
