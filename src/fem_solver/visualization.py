"""Optional Plotly views; no UI dependency in the numerical solver."""

import numpy as np
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

from .model import UNITS, Model
from .solver import SolveResult
from .terms import help_text

BLUE = "#2563EB"
INK = "#13243A"


def _geometry_ranges(x_values, y_values):
    """Return readable equal-scale ranges, including explicit depth for a straight line."""
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    x_span = max(x_max - x_min, 1.0)
    y_span = y_max - y_min
    x_pad = 0.08 * x_span
    if y_span <= 1e-9 * x_span:
        y_mid = (y_min + y_max) / 2
        y_pad = 0.14 * x_span
        return [x_min - x_pad, x_max + x_pad], [y_mid - y_pad, y_mid + y_pad]
    y_pad = 0.08 * max(y_span, x_span * 0.2)
    return [x_min - x_pad, x_max + x_pad], [y_min - y_pad, y_max + y_pad]


def model_figure(model: Model, case: str, units: str = "N-m-Pa", selected: str | None = None):
    """Draw only declared geometry and actions. No solution or fabricated result is needed."""
    factor = 1 / UNITS[units]
    unit = "m" if units == "N-m-Pa" else "mm"
    nodes = {n.id: n for n in model.nodes}
    fig = go.Figure()
    for member in model.elements:
        a, b = nodes[member.start], nodes[member.end]
        fig.add_trace(
            go.Scatter(
                x=[a.x * factor, b.x * factor],
                y=[a.y * factor, b.y * factor],
                mode="lines+markers",
                name=member.id,
                line=dict(
                    color=BLUE if selected == member.id else "#0f766e",
                    width=5 if selected == member.id else 3,
                ),
                hovertemplate="Member centerline: connects two nodes.<br>x=%{x} "
                + unit
                + "<br>y=%{y} "
                + unit
                + "<extra>%{fullData.name}</extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[n.x * factor for n in model.nodes],
            y=[n.y * factor for n in model.nodes],
            text=[n.id for n in model.nodes],
            mode="markers+text",
            textposition="top center",
            name="Nodes",
            hovertemplate="Node: a point where movements and loads are represented.<br>%{text}<extra></extra>",
        )
    )
    for c in model.constraints:
        n = nodes[c.node]
        value = c.value * (1 if c.dof == "rz" else factor)
        fig.add_trace(
            go.Scatter(
                x=[n.x * factor],
                y=[n.y * factor],
                mode="markers",
                marker=dict(symbol="triangle-up", color=INK, size=14),
                showlegend=False,
                text=[f"{c.node}: {c.dof} = {value:g} {'rad' if c.dof == 'rz' else unit}"],
                hovertemplate="Known support movement<br>%{text}<extra></extra>",
            )
        )
    for spring in model.springs:
        n = nodes[spring.node]
        stiffness = spring.stiffness * (factor if spring.dof == "rz" else 1 / factor)
        spring_unit = f"N {unit}/rad" if spring.dof == "rz" else f"N/{unit}"
        fig.add_trace(
            go.Scatter(
                x=[n.x * factor],
                y=[n.y * factor],
                mode="markers",
                marker=dict(symbol="diamond-open", color="#b45309", size=21),
                showlegend=False,
                text=[f"{spring.node}: {spring.dof}, k={stiffness:g} {spring_unit}"],
                hovertemplate="Spring: allows movement and supplies restoring action.<br>%{text}<extra></extra>",
            )
        )
    for load in model.loads:
        if load.case != case:
            continue
        n = nodes[load.node]
        sign = 1 if load.value >= 0 else -1
        if load.dof == "rz":
            fig.add_annotation(
                x=n.x * factor,
                y=n.y * factor,
                text=f"Moment {load.value * factor:g} N {unit}",
                yshift=32,
                showarrow=False,
                hovertext=help_text("moment"),
                captureevents=True,
            )
        else:
            fig.add_annotation(
                x=n.x * factor,
                y=n.y * factor,
                text=f"{load.value:g} N",
                showarrow=True,
                ax=-sign * 60 if load.dof == "ux" else 0,
                ay=sign * 60 if load.dof == "uy" else 0,
                arrowhead=2,
                arrowcolor="#b45309",
                hovertext=help_text("load"),
                captureevents=True,
            )
    for distributed in model.distributed_loads:
        if distributed.case != case:
            continue
        el = next(e for e in model.elements if e.id == distributed.element)
        a, b = nodes[el.start], nodes[el.end]
        fig.add_annotation(
            x=(a.x + b.x) * factor / 2,
            y=(a.y + b.y) * factor / 2,
            text=f"Local qx={distributed.qx / factor:g}, qy={distributed.qy / factor:g} N/{unit}",
            showarrow=False,
            yshift=45,
            hovertext=help_text("udl") + " " + help_text("local"),
            captureevents=True,
        )
    x_range, y_range = _geometry_ranges(
        [node.x * factor for node in model.nodes], [node.y * factor for node in model.nodes]
    )
    fig.update_layout(
        template="plotly_white",
        height=410,
        margin=dict(l=30, r=30, t=50, b=35),
        xaxis_title=f"Global x ({unit})",
        yaxis_title=f"Global y ({unit})",
        xaxis=dict(range=x_range, constrain="domain"),
        yaxis=dict(range=y_range, scaleanchor="x", scaleratio=1, constrain="domain"),
        legend=dict(orientation="h", y=-0.2),
    )
    return fig


def structure_figure(
    model: Model,
    result: SolveResult,
    magnification=50.0,
    selected=None,
    color_by="Deformed shape",
    units="N-m-Pa",
):
    fig = go.Figure()
    length_factor = 1 / UNITS[units]
    length_unit = "m" if units == "N-m-Pa" else "mm"
    stress_factor = 1 if units == "N-m-Pa" else 1e-6
    stress_unit = "Pa" if units == "N-m-Pa" else "MPa"
    nodes = {n.id: n for n in model.nodes}
    stress_values = (
        np.concatenate([r.get("stress_top", r["axial_stress"]) for r in result.members.values()])
        * stress_factor
    )
    maxstress = max(float(np.max(np.abs(stress_values))), 1e-12)
    for em in result.trace.element_matrices:
        el, r = em.element, result.members[em.element.id]
        a, b = nodes[el.start], nodes[el.end]
        x, y = a.x + em.cosine * r["x"], a.y + em.sine * r["x"]
        fig.add_trace(
            go.Scatter(
                x=[a.x * length_factor, b.x * length_factor],
                y=[a.y * length_factor, b.y * length_factor],
                mode="lines",
                line=dict(color="#B4C1D2", width=3, dash="dot"),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        if model.kind == "truss":
            u = result.displacements[em.indices].reshape(2, 2)
            t = r["x"] / em.length
            dx, dy = (1 - t) * u[0, 0] + t * u[1, 0], (1 - t) * u[0, 1] + t * u[1, 1]
        else:
            axial, transverse = r["axial_displacement"], r["transverse_displacement"]
            dx = em.cosine * axial - em.sine * transverse
            dy = em.sine * axial + em.cosine * transverse
        xx, yy = (x + magnification * dx) * length_factor, (y + magnification * dy) * length_factor
        stress = r.get("stress_top", r["axial_stress"]) * stress_factor
        custom = np.column_stack(
            [r["x"] * length_factor, r["axial_force"], r["moment"] * length_factor, stress]
        )
        if color_by == "Normal stress":
            for i in range(len(xx) - 1):
                color = sample_colorscale("RdBu", [(stress[i] / maxstress + 1) / 2])[0]
                fig.add_trace(
                    go.Scatter(
                        x=xx[i : i + 2],
                        y=yy[i : i + 2],
                        mode="lines",
                        line=dict(color=color, width=5),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )
        fig.add_trace(
            go.Scatter(
                x=xx,
                y=yy,
                mode="lines",
                name=el.id,
                line=dict(
                    color=BLUE if el.id == selected else "#0F766E",
                    width=5 if el.id == selected else 3,
                ),
                opacity=0.03 if color_by == "Normal stress" else 1,
                customdata=custom,
                hovertemplate="s=%{customdata[0]:.4g} "
                + length_unit
                + "<br>Axial force (stretching positive)=%{customdata[1]:.4g} N<br>Bending moment (turning effect)=%{customdata[2]:.4g} N "
                + length_unit
                + "<br>Normal stress (force per area)=%{customdata[3]:.4g} "
                + stress_unit
                + "<extra>%{fullData.name}</extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[n.x * length_factor for n in model.nodes],
            y=[n.y * length_factor for n in model.nodes],
            mode="markers+text",
            text=[n.id for n in model.nodes],
            textposition="top center",
            name="Nodes",
            marker=dict(color=INK, size=9, line=dict(color="white", width=2)),
        )
    )
    supports = sorted({c.node for c in model.constraints})
    if supports:
        fig.add_trace(
            go.Scatter(
                x=[nodes[n].x * length_factor for n in supports],
                y=[nodes[n].y * length_factor for n in supports],
                mode="markers",
                name="Prescribed DOF",
                marker=dict(symbol="triangle-up", size=17, color=INK),
                text=[
                    ", ".join(
                        f"{c.dof}={c.value:g} {'rad' if c.dof == 'rz' else 'm'}"
                        for c in model.constraints
                        if c.node == n
                    )
                    for n in supports
                ],
                hovertemplate="%{text}<extra>Support</extra>",
            )
        )
    if model.springs:
        fig.add_trace(
            go.Scatter(
                x=[nodes[s.node].x * length_factor for s in model.springs],
                y=[nodes[s.node].y * length_factor for s in model.springs],
                mode="markers",
                name="Spring",
                marker=dict(symbol="diamond-open", size=22, color="#D97706"),
                text=[
                    f"{s.dof}: k={s.stiffness:g} {'N m/rad' if s.dof == 'rz' else 'N/m'}"
                    for s in model.springs
                ],
                hovertemplate="%{text}<extra>Spring</extra>",
            )
        )
    for load in model.loads:
        if load.case != result.case:
            continue
        node = nodes[load.node]
        if load.dof == "rz":
            fig.add_annotation(
                x=node.x * length_factor,
                y=node.y * length_factor,
                text=f"M={load.value * length_factor:g} N {length_unit}",
                showarrow=False,
                yshift=30,
                font=dict(color="#B45309"),
            )
        else:
            direction = 1 if load.value >= 0 else -1
            fig.add_annotation(
                x=node.x * length_factor,
                y=node.y * length_factor,
                text=f"{load.value:g} N",
                showarrow=True,
                arrowhead=2,
                ax=-direction * 65 if load.dof == "ux" else 0,
                ay=direction * 65 if load.dof == "uy" else 0,
                arrowcolor="#B45309",
                font=dict(color="#B45309"),
            )
    for distributed in model.distributed_loads:
        if distributed.case != result.case:
            continue
        el = next(e for e in model.elements if e.id == distributed.element)
        a, b = nodes[el.start], nodes[el.end]
        fig.add_annotation(
            x=(a.x + b.x) * length_factor / 2,
            y=(a.y + b.y) * length_factor / 2,
            text=f"q(local)=({distributed.qx / length_factor:g}, {distributed.qy / length_factor:g}) N/{length_unit}",
            showarrow=False,
            yshift=32,
            font=dict(color="#B45309", size=12),
        )
    if color_by == "Normal stress":
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                showlegend=False,
                marker=dict(
                    colorscale="RdBu",
                    cmin=-maxstress,
                    cmax=maxstress,
                    color=[0],
                    showscale=True,
                    colorbar=dict(title=f"Normal<br>stress<br>({stress_unit})"),
                ),
            )
        )
    plotted_x = [float(value) for trace in fig.data for value in trace.x if value is not None]
    plotted_y = [float(value) for trace in fig.data for value in trace.y if value is not None]
    x_range, y_range = _geometry_ranges(plotted_x, plotted_y)
    fig.update_layout(
        template="plotly_white",
        height=490,
        margin=dict(l=35, r=35, t=20, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial", color=INK),
        legend=dict(orientation="h", y=-0.15),
        xaxis_title=f"x ({length_unit})",
        yaxis_title=f"y ({length_unit})",
        xaxis=dict(range=x_range, constrain="domain"),
        yaxis=dict(range=y_range, scaleanchor="x", scaleratio=1, constrain="domain"),
        uirevision=model.title,
    )
    return fig


def member_quantity(quantity, units="N-m-Pa"):
    length_unit = "m" if units == "N-m-Pa" else "mm"
    length_factor = 1 / UNITS[units]
    stress_unit = "Pa" if units == "N-m-Pa" else "MPa"
    stress_factor = 1 if units == "N-m-Pa" else 1e-6
    names = {
        "axial_force": ("Axial force", "N", 1),
        "shear": ("Shear force", "N", 1),
        "moment": ("Bending moment", f"N {length_unit}", length_factor),
        "transverse_displacement": ("Local transverse deflection", length_unit, length_factor),
        "axial_stress": ("Axial stress", stress_unit, stress_factor),
        "stress_top": ("Top fiber normal stress", stress_unit, stress_factor),
        "stress_bottom": ("Bottom fiber normal stress", stress_unit, stress_factor),
    }
    return names[quantity]


def member_figure(member, quantity, units="N-m-Pa"):
    title, unit, factor = member_quantity(quantity, units)
    length_unit = "m" if units == "N-m-Pa" else "mm"
    fig = go.Figure(
        go.Scatter(
            x=member["x"] / UNITS[units],
            y=member[quantity] * factor,
            mode="lines",
            fill="tozeroy",
            line=dict(color=BLUE, width=3),
            fillcolor="rgba(37,99,235,.1)",
        )
    )
    fig.update_layout(
        template="plotly_white",
        height=290,
        title=title,
        xaxis_title=f"Local distance ({length_unit})",
        yaxis_title=unit,
        margin=dict(l=35, r=25, t=45, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig
