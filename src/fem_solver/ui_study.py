"""Local-only application. Run with: python -m streamlit run app.py"""

import hashlib
import json
from dataclasses import asdict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fem_solver import ModelError
from fem_solver.export import identification_report
from fem_solver.identification import (
    CSV_COLUMNS,
    IdentificationConfig,
    fit_cantilever,
    observations_csv,
    read_observations_csv,
    select_measurement_positions,
    validate_measurement_metadata,
)
from fem_solver.study import synthetic_observations

from .terms import help_text
from .ui_common import (
    diagnostic_table,
    explain,
    intervals_table,
    observation_columns,
    readable_table,
    term_key,
)


def study_view():
    st.title("Estimate beam stiffness.")
    explain(
        "Can a few deflection measurements separate beam bending from clamp rotation? These local calculations use stated assumptions and report when the data are insufficient."
    )
    term_key(
        "EI",
        "compliance",
        "gamma",
        "noise",
        "characteristic",
        "sensitivity",
        "uncertainty",
        "rmse",
        "holdout",
        "train",
        "bootstrap",
        "synthetic",
        "measured",
    )
    controls, body = st.columns([1, 2.4], gap="large")
    with controls:
        source = st.radio("Observation source", ["Synthetic experiment", "Measured CSV"])
        support = st.selectbox(
            "Assumed support", ["flexible", "rigid"], help=help_text("compliance")
        )
        observations = None
        context = {}
        if source == "Synthetic experiment":
            explain("SYNTHETIC DATA · GENERATED FROM EQUATIONS, NOT MEASURED")
            EI = st.number_input(
                "True EI (N m²)", min_value=1.0, value=1000.0, step=100.0, help=help_text("EI")
            )
            gamma = st.slider(
                "Dimensionless clamp compliance", 0.0, 0.2, 0.02, 0.005, help=help_text("gamma")
            )
            noise = st.select_slider(
                "Noise / characteristic displacement",
                [0.0, 0.0025, 0.01, 0.03],
                value=0.0025,
                format_func=lambda x: f"{100 * x:g}%",
            )
            count = st.radio("Measurement positions", [1, 2, 4], horizontal=True, index=2)
            design = st.selectbox(
                "Load pattern",
                ["locations", "single", "amplitudes"],
                format_func=lambda value: {
                    "locations": "Different load positions",
                    "single": "One tip load",
                    "amplitudes": "Different load magnitudes",
                }[value],
            )
            optimized = st.checkbox(
                "Select positions by sensitivity",
                value=False,
                disabled=count != 2,
                help=help_text("sensitivity"),
            )
            positions = {1: [1.0], 2: [0.5, 1.0], 4: [0.25, 0.5, 0.75, 1.0]}[count]
            if optimized and count == 2:
                positions, _ = select_measurement_positions(
                    1.0,
                    [0.25, 0.5, 0.75, 1.0],
                    2,
                    [(1.0, 1.0)] if design != "locations" else [(0.75, 1.0), (1.0, 1.0)],
                    EI,
                )
            observations = synthetic_observations(EI, gamma / EI, noise, positions, design)
            length, reference = 1.0, EI
            context = {
                "generator": "independent analytical Euler-Bernoulli cantilever",
                "true_EI": EI,
                "true_clamp_compliance": gamma / EI,
                "seed": 2027,
                "noise_fraction": noise,
                "positions_m": positions,
            }
        else:
            st.info(
                "Real test results are pending until you import actual measurements. Deflection and force are positive downward."
            )
            length = st.number_input("Measured free length (m)", min_value=0.001, value=1.0)
            reference = st.number_input(
                "EI scaling reference (N m²)", min_value=0.001, value=1000.0
            )
            file = st.file_uploader(
                "Readings, uncertainty and reserved prediction cases", type="csv"
            )
            metadata_file = st.file_uploader(
                "Test details: specimen, fixture and calibration", type="json"
            )
            st.download_button(
                "Empty SI measurement template",
                ",".join(CSV_COLUMNS) + "\n",
                "measurements.csv",
                "text/csv",
            )
            if file and metadata_file:
                try:
                    observations = read_observations_csv(file.getvalue().decode("utf-8-sig"))
                    if any(o.provenance != "measured" for o in observations):
                        raise ModelError(
                            "Measured mode only accepts rows labeled measured. Use the synthetic mode for demonstrations."
                        )
                    metadata = json.loads(metadata_file.getvalue())
                    if not isinstance(metadata, dict) or not metadata:
                        raise ModelError(
                            "Supply the specimen, fixture and calibration details; an empty file is not enough."
                        )
                    validate_measurement_metadata(metadata, length)
                    context = {
                        "metadata": metadata,
                        "input_sha256": hashlib.sha256(file.getvalue()).hexdigest(),
                    }
                except (ValueError, ModelError) as exc:
                    st.error(str(exc))
                    observations = None
    with body:
        if observations:
            try:
                config = IdentificationConfig(length, reference, support, 200)
                fitted = fit_cantilever(observations, config)
                context["configuration"] = asdict(config)
                if fitted.status == "unidentifiable":
                    st.error(
                        "Insufficient information to estimate beam stiffness and clamp flexibility separately."
                    )
                    for note in fitted.warnings:
                        st.warning(note)
                else:
                    a, b, c = st.columns(3)
                    a.metric("Estimated EI", f"{fitted.EI:,.2f} N m²")
                    b.metric(
                        "Clamp compliance (rad/N m)",
                        f"{fitted.clamp_compliance:.3e}",
                        help="rad per N m; zero represents a rigid clamp",
                    )
                    c.metric(
                        "Reserved-case error (RMSE)",
                        f"{1000 * fitted.holdout_rmse:.5f} mm"
                        if fitted.holdout_rmse is not None
                        else "Not evaluated",
                    )
                    fig = go.Figure()
                    for split, color, symbol in [
                        ("train", "#2563EB", "circle"),
                        ("holdout", "#D97706", "diamond"),
                    ]:
                        indices = [i for i, o in enumerate(observations) if o.split == split]
                        fig.add_trace(
                            go.Scatter(
                                x=[observations[i].displacement * 1000 for i in indices],
                                y=[fitted.predictions[i] * 1000 for i in indices],
                                mode="markers",
                                name="Used for fitting"
                                if split == "train"
                                else "Reserved prediction check",
                                marker=dict(color=color, symbol=symbol, size=10),
                                text=[observations[i].id for i in indices],
                                hovertemplate="%{text}<br>Observed movement=%{x:.6g} mm<br>Predicted movement=%{y:.6g} mm<extra>%{fullData.name}</extra>",
                            )
                        )
                    values = [o.displacement * 1000 for o in observations] + [
                        p * 1000 for p in fitted.predictions
                    ]
                    lo, hi = min(values), max(values)
                    fig.add_trace(
                        go.Scatter(
                            x=[lo, hi],
                            y=[lo, hi],
                            mode="lines",
                            name="Perfect agreement",
                            line=dict(color="#94A3B8", dash="dot"),
                        )
                    )
                    fig.update_layout(
                        template="plotly_white",
                        height=370,
                        xaxis_title="Observed deflection (mm)",
                        yaxis_title="Predicted deflection (mm)",
                        legend=dict(orientation="h"),
                    )
                    st.plotly_chart(fig, width="stretch")
                    st.markdown("**Approximate 95% uncertainty ranges**")
                    explain(
                        "These ranges come from repeated simulated observations (a parametric bootstrap). They depend on the stated model and noise assumptions. RMSE measures typical prediction error on observations not used for fitting."
                    )
                    intervals_table(fitted.intervals)
                    for note in fitted.warnings:
                        explain(note)
                with st.expander("Parameter sensitivity and observation details", expanded=False):
                    diagnostic_table(fitted)
                    st.dataframe(
                        pd.DataFrame([asdict(o) for o in observations]),
                        hide_index=True,
                        column_config=observation_columns(),
                    )
                    readable_table(
                        pd.DataFrame([asdict(o) for o in observations]), "Study observations (SI)"
                    )
                a, b = st.columns(2)
                a.download_button(
                    "Download observation CSV",
                    observations_csv(observations),
                    "observations.csv",
                    "text/csv",
                )
                b.download_button(
                    "Download identification report",
                    identification_report(fitted, context),
                    "identification.html",
                    "text/html",
                )
            except ModelError as exc:
                st.error(str(exc))
        else:
            st.markdown("### Keep readings and their test details together.")
            st.write(
                "Upload the raw SI readings and the test details. Enter the zero reading and a positive standard uncertainty for each observation. Save some load cases for prediction checks before fitting."
            )
            explain(
                "No real measurements are included. See docs/05-research-and-experiments/bench-protocol.md for preparation and safety checks."
            )
    st.stop()
