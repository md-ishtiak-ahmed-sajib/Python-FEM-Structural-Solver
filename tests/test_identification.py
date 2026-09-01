from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose

from fem_solver.identification import (
    IdentificationConfig,
    Observation,
    analytical_deflection,
    design_matrix,
    fit_cantilever,
    observations_csv,
    read_observations_csv,
    select_measurement_positions,
)
from fem_solver.model import ModelError


def observations():
    return [
        Observation(
            str(i),
            x,
            a,
            2.0,
            float(analytical_deflection(x, a, 2.0, 1000.0, 2e-5)),
            1e-6,
            "holdout" if a == 0.5 else "train",
        )
        for i, (a, x) in enumerate((a, x) for a in [1.0, 0.75, 0.5] for x in [0.25, 0.5, 0.75, 1.0])
    ]


def test_fem_influence_matches_independent_analytical():
    data = observations()
    assert_allclose(
        design_matrix(data, IdentificationConfig()),
        design_matrix(data, IdentificationConfig(backend="analytical")),
        rtol=1e-9,
        atol=1e-14,
    )


def test_noiseless_recovery_and_holdout():
    r = fit_cantilever(observations(), IdentificationConfig(bootstrap_samples=0))
    assert r.status == "identified"
    assert_allclose(r.EI, 1000, rtol=1e-8)
    assert_allclose(r.clamp_compliance, 2e-5, rtol=1e-8)
    assert r.holdout_rmse < 1e-12


def test_repeating_amplitude_does_not_add_rank():
    data = [Observation(str(i), 1.0, 1.0, float(i), 0.001 * i, 1e-6) for i in [1, 2, 3]]
    r = fit_cantilever(data)
    assert r.status == "unidentifiable"
    assert r.EI is None and r.predictions == []


def test_holdout_does_not_leak_into_estimate():
    data = observations()
    changed = [replace(o, displacement=1.0) if o.split == "holdout" else o for o in data]
    a = fit_cantilever(data, IdentificationConfig(bootstrap_samples=0))
    b = fit_cantilever(changed, IdentificationConfig(bootstrap_samples=0))
    assert a.EI == b.EI
    assert b.holdout_rmse > 0.9


def test_bootstrap_reproducible_and_noise_sensitive():
    data = observations()
    config = IdentificationConfig(bootstrap_samples=100)
    a, b = fit_cantilever(data, config), fit_cantilever(data, config)
    assert a.intervals == b.intervals
    c = fit_cantilever([replace(o, sigma=o.sigma * 10) for o in data], config)
    assert np.ptp(c.intervals["EI_N_m2"]) > np.ptp(a.intervals["EI_N_m2"])


def test_rigid_clamp_boundary():
    data = [
        replace(o, displacement=float(analytical_deflection(o.x, o.load_position, o.force, 1000.0)))
        for o in observations()
    ]
    r = fit_cantilever(data)
    assert r.clamp_compliance < 1e-12
    assert any("indistinguishable" in text for text in r.warnings)


def test_csv_roundtrip_and_mixed_provenance():
    data = observations()
    assert read_observations_csv(observations_csv(data)) == data
    data[0] = replace(data[0], provenance="measured")
    with pytest.raises(ModelError, match="mix"):
        fit_cantilever(data)


def test_sensor_selection_and_bad_uncertainty():
    positions, score = select_measurement_positions(
        1.0, [0.25, 0.5, 0.75, 1.0], 2, [(1.0, 1.0)], 1000.0
    )
    assert len(positions) == 2 and score > 0
    with pytest.raises(ModelError, match="sigma"):
        fit_cantilever([replace(o, sigma=0.0) for o in observations()])
