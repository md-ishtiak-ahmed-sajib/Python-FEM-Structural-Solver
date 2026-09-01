"""Interaction checks for the engineering-studio application shell."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def start():
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception
    return app


def workspace(app):
    return next(radio for radio in app.radio if radio.label == "Workspace")


@pytest.mark.parametrize(
    ("kind", "example_title"),
    [
        ("bar", "Axial bar"),
        ("truss", "Triangular truss"),
        ("beam", "Cantilever beam"),
        ("frame", "Portal frame"),
    ],
)
def test_launchpad_blank_and_example_actions_do_not_solve(kind, example_title):
    blank = start()
    next(button for button in blank.button if button.key == "blank_" + kind).click().run()
    assert not blank.exception
    assert workspace(blank).value == "1 · Define"
    assert blank.session_state.draft["kind"] == kind
    assert "solution" not in blank.session_state

    example = start()
    next(button for button in example.button if button.key == "example_" + kind).click().run()
    assert not example.exception
    assert workspace(example).value == "1 · Define"
    assert example.session_state.draft["title"] == example_title
    assert "solution" not in example.session_state


def test_home_resume_navigation_modes_and_stage_indicators():
    app = start()
    assert workspace(app).value == "Home"
    assert "solution" not in app.session_state
    next(
        button for button in app.button if button.label == "Continue current project"
    ).click().run()
    assert workspace(app).value == "1 · Define"

    for route, stage in [
        ("1 · Define", 1),
        ("2 · Understand", 2),
        ("3 · Solve and discuss", 3),
    ]:
        workspace(app).set_value(route).run()
        progress = next(
            item.value for item in app.markdown if 'aria-label="Learning stages"' in item.value
        )
        assert 'aria-current="step"' in progress
        assert f"Stage {stage} of 3 ·" in progress

    next(radio for radio in app.radio if radio.label == "Navigation").set_value(
        "Direct access"
    ).run()
    assert workspace(app).options == [
        "Home",
        "Model",
        "Inside FEM",
        "Results",
        "Stiffness study",
        "Glossary",
    ]


def test_semantic_metrics_keep_complete_values_and_glossary_filters():
    app = start()
    workspace(app).set_value("3 · Solve and discuss").run()
    next(button for button in app.button if button.label == "Solve model").click().run()
    metric_markup = next(
        item.value for item in app.markdown if 'aria-label="Primary results"' in item.value
    )
    assert "Scaled residual" in metric_markup
    assert "..." not in metric_markup
    assert "…" not in metric_markup

    workspace(app).set_value("Glossary").run()
    topic = next(group for group in app.get("button_group") if group.label == "Filter by topic")
    topic.set_value("Research").run()
    labels = {expander.label for expander in app.expander}
    assert "Clamp compliance" in labels
    assert "Node" not in labels


def test_progressive_term_help_is_present_without_large_term_strip():
    app = start()
    workspace(app).set_value("1 · Define").run()
    term_cards = [item.value for item in app.markdown if "fem-popover-term" in item.value]
    assert any("Degree of freedom" in value for value in term_cards)
    assert not any('class="fem-key"' in item.value for item in app.markdown)


def test_mechanism_stays_a_visible_failed_solve():
    app = start()
    unstable = dict(app.session_state.draft)
    unstable["constraints"] = []
    app.session_state.draft = unstable
    workspace(app).set_value("3 · Solve and discuss").run()
    next(button for button in app.button if button.label == "Solve model").click().run()
    assert not app.exception
    assert "solution" not in app.session_state
    assert "solve_error" in app.session_state
    assert any("The model did not solve" in item.value for item in app.markdown)
    assert any("artificial" in item.value for item in app.markdown)


def test_design_token_text_pairs_meet_wcag_aa():
    def luminance(color):
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        values = [
            value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
            for value in channels
        ]
        return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]

    def contrast(first, second):
        high, low = sorted((luminance(first), luminance(second)), reverse=True)
        return (high + 0.05) / (low + 0.05)

    pairs = [
        ("#0b1f33", "#faf9f6"),
        ("#5b6b7f", "#ffffff"),
        ("#ffffff", "#246bfe"),
        ("#164fc5", "#ffffff"),
        ("#086c4e", "#e6f6ef"),
        ("#8d5200", "#fff4dc"),
        ("#9b293a", "#fdecef"),
    ]
    assert all(contrast(foreground, background) >= 4.5 for foreground, background in pairs)
