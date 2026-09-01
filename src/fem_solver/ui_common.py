"""Presentation helpers. Import only from the optional application layer."""

from pathlib import Path

import pandas as pd
import streamlit as st

from .export import html_table
from .terms import TERMS, annotate, help_text
from .ui_design import badges, inject_design, key_terms, page_header


def explain(message: str):
    st.markdown(annotate(message), unsafe_allow_html=True)


def term_key(*keys: str):
    key_terms(keys)


def readable_table(frame: pd.DataFrame, label: str, include_index: bool = False):
    """Offer real HTML rows alongside canvas tables, with bounded page length."""
    with st.expander("Read as text: " + label):
        st.caption(
            "Read-only values. Use the model editor to change inputs. Focus wide tables to scroll sideways."
        )
        if include_index:
            frame = frame.rename_axis("Row").reset_index()
        pages = max(1, (len(frame) + 49) // 50)
        page = st.number_input("Text page: " + label, 1, pages, 1) if pages > 1 else 1
        view = frame.iloc[(page - 1) * 50 : page * 50]
        view = view.astype(object).where(pd.notna(view), None)
        st.markdown(html_table(view.to_dict(orient="records"), label), unsafe_allow_html=True)
        if pages > 1:
            st.caption(f"Page {page} of {pages}; {len(frame)} rows in total.")


def style():
    inject_design()


TABLES = {
    "nodes": ["id", "x", "y"],
    "elements": ["id", "start", "end", "material", "section"],
    "materials": ["id", "E"],
    "sections": ["id", "A", "I", "c"],
    "constraints": ["node", "dof", "value"],
    "springs": ["node", "dof", "stiffness"],
    "loads": ["node", "dof", "value", "case"],
    "distributed_loads": ["element", "qx", "qy", "case"],
}
TABLE_TERMS = {
    "nodes": "node",
    "elements": "element",
    "materials": "material",
    "sections": "section",
    "constraints": "constraint",
    "springs": "spring",
    "loads": "load",
    "distributed_loads": "udl",
}
FIELD_TERMS = {
    "node": "node",
    "element": "element",
    "material": "material",
    "section": "section",
    "E": "E",
    "A": "A",
    "I": "I",
    "c": "fiber",
    "dof": "dof",
    "stiffness": "stiffness",
    "case": "case",
    "qx": "qx",
    "qy": "qy",
}


def editor_columns(table: str, units: str, dofs: tuple[str, ...]):
    length = "m" if units == "N-m-Pa" else "mm"
    descriptions = {
        "id": "A unique name used to connect rows. Keep names short and clear.",
        "x": f"Global horizontal coordinate ({length}).",
        "y": f"Global vertical coordinate ({length}).",
        "start": "ID of the start node. The local x axis points from start to end.",
        "end": "ID of the end node. Reversing a member changes its local signs, not the physical answer.",
    }
    number_units = {
        "x": length,
        "y": length,
        "E": "Pa" if length == "m" else "MPa",
        "A": length + "²",
        "I": length + "⁴",
        "c": length,
        "qx": "N/" + length,
        "qy": "N/" + length,
    }
    if table == "constraints":
        descriptions["value"] = (
            f"Prescribed movement ({length}) for ux/uy, or rotation (rad) for rz. Zero means held."
        )
    elif table == "loads":
        descriptions["value"] = (
            f"Force (N) for ux/uy, or moment (N {length}) for rz. Positive is right/up/counterclockwise."
        )
    descriptions["stiffness"] = (
        f"Spring stiffness: N/{length} for translation; N {length}/rad for rotation. Must be positive."
    )
    result = {}
    for column in TABLES[table]:
        description = descriptions.get(
            column, help_text(FIELD_TERMS[column]) if column in FIELD_TERMS else ""
        )
        if column == "dof":
            result[column] = st.column_config.SelectboxColumn(
                "DOF",
                options=list(dofs),
                help=help_text("dof") + " ux: right; uy: up; rz: counterclockwise.",
            )
        elif column in number_units or column in ("value", "stiffness"):
            label = column + (
                f" ({number_units[column]})" if column in number_units else " (units by DOF)"
            )
            result[column] = st.column_config.NumberColumn(label, help=description, format="%.6g")
        else:
            result[column] = st.column_config.TextColumn(column, help=description)
    return result


def intervals_table(intervals):
    rows = [
        {
            "Parameter": "EI" if key.startswith("EI") else "Clamp compliance",
            "Lower": values[0],
            "Upper": values[1],
            "Unit": "N m²" if key.startswith("EI") else "rad/(N m)",
        }
        for key, values in intervals.items()
    ]
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        column_config={
            "Lower": st.column_config.NumberColumn(
                help="Lower end of the approximate 95% interval under the stated assumptions."
            ),
            "Upper": st.column_config.NumberColumn(
                help="Upper end of that interval. A bound near zero is not proof of a perfectly rigid clamp."
            ),
        },
    )
    readable_table(pd.DataFrame(rows), "Uncertainty ranges")


def diagnostic_table(fitted):
    term_key("rank", "singular", "correlation", "unidentifiable")
    st.table(
        pd.DataFrame(
            [
                {"Quantity": TERMS[key].label, "Value": str(value), "Meaning": help_text(key)}
                for key, value in [
                    ("rank", fitted.rank),
                    ("singular", fitted.singular_values),
                    ("correlation", fitted.correlation),
                ]
            ]
        )
    )


def observation_columns():
    definitions = {
        "id": "A unique reading name.",
        "x": "Measurement position from the clamp, in m.",
        "load_position": "Load position from the clamp, in m.",
        "force": "Applied force in N; positive downward for this study.",
        "displacement": "Observed deflection in m; positive downward for this study.",
        "sigma": "Positive standard uncertainty in m.",
        "split": help_text("holdout") + " Train rows enter the fit.",
        "provenance": help_text("provenance"),
        "run_id": "Name of the test run or synthetic run that produced this reading.",
        "zero": help_text("zero"),
    }
    return {
        name: st.column_config.Column(name, help=description)
        for name, description in definitions.items()
    }


def glossary_view():
    page_header(
        "Find a simple explanation",
        "Search the same vocabulary used in fields, charts, matrices, warnings and research results.",
        "GLOSSARY",
    )
    badges([("Keyboard friendly", "green"), ("Tap friendly", "blue"), ("Local definitions", "")])
    explain(
        "Hover a dotted term, focus it with the keyboard, or tap it to read its meaning. This glossary is also available without hovering."
    )
    query = st.text_input("Search a term or meaning").strip().lower()
    groups = {
        "Model": {
            "node",
            "element",
            "dof",
            "ux",
            "uy",
            "rz",
            "constraint",
            "prescribed",
            "support",
            "fixed",
            "pin",
            "roller",
            "spring",
            "load",
            "case",
            "udl",
            "bar",
            "truss",
            "beam",
            "frame",
        },
        "Mechanics": {
            "translation",
            "rotation",
            "displacement",
            "deflection",
            "material",
            "section",
            "E",
            "A",
            "I",
            "fiber",
            "EA",
            "EI",
            "strain",
            "stress",
            "axial",
            "shear",
            "moment",
            "reaction",
            "elastic",
            "static",
            "euler",
            "timoshenko",
        },
        "Calculation": {
            "idealization",
            "stiffness",
            "matrix",
            "local",
            "global",
            "cosine",
            "sine",
            "transform",
            "assembly",
            "free",
            "rhs",
            "sparse",
            "lu",
            "residual",
            "eigenvalue",
            "energy",
            "equilibrium",
            "mechanism",
            "conditioning",
            "shape",
            "consistent",
            "mesh",
            "convergence",
            "magnification",
            "si",
        },
        "Research": {
            "compliance",
            "gamma",
            "sensitivity",
            "rank",
            "singular",
            "correlation",
            "bootstrap",
            "uncertainty",
            "noise",
            "characteristic",
            "rmse",
            "holdout",
            "train",
            "synthetic",
            "measured",
            "unidentifiable",
            "calibration",
            "zero",
            "provenance",
        },
    }
    group = st.pills(
        "Filter by topic",
        ["All", "Model", "Mechanics", "Calculation", "Research"],
        default="All",
        width="stretch",
    )
    matches = [
        (key, term)
        for key, term in TERMS.items()
        if (group == "All" or key in groups[group or "Model"])
        and (
            not query
            or query in (term.label + " " + term.meaning + " " + " ".join(term.aliases)).lower()
        )
    ]
    columns = st.columns(2)
    for index, (key, term) in enumerate(sorted(matches, key=lambda pair: pair[1].label.lower())):
        with columns[index % 2]:
            with st.expander(term.label):
                st.write(term.meaning)
                path = Path(__file__).resolve().parents[2] / "docs" / term.guide
                # Editable installs live under src; wheel installs may have no source docs.
                if not path.exists():
                    path = Path.cwd() / "docs" / term.guide
                if path.is_file():
                    st.download_button(
                        "Save the related guide",
                        path.read_text(encoding="utf-8"),
                        path.name,
                        "text/markdown",
                        key="guide_" + key,
                    )
                st.caption("Read more: docs/" + term.guide)
    if not matches:
        st.info("No matching term. Try a shorter word.")
