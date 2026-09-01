"""Application-level smoke checks without relying on browser rendering internals."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_views_and_synthetic_ambiguity():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=30
    ).run()
    assert not app.exception
    next(r for r in app.radio if r.label == "Workspace").set_value("3 · Solve and discuss").run()
    next(b for b in app.button if b.label == "Solve").click().run()
    assert app.metric[0].value.endswith("mm")
    next(r for r in app.radio if r.label == "Workspace").set_value("2 · Understand").run()
    assert not app.exception
    next(r for r in app.radio if r.label == "Workspace").set_value("1 · Define").run()
    assert not app.exception
    next(r for r in app.radio if r.label == "Workspace").set_value("Stiffness study").run()
    assert not app.exception
    next(r for r in app.radio if r.label == "Measurement positions").set_value(1)
    next(s for s in app.selectbox if s.label == "Load pattern").set_value("amplitudes")
    app.run()
    assert not app.exception
    assert any("Insufficient information" in e.value for e in app.error)
