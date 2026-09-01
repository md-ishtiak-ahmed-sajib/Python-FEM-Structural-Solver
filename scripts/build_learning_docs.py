"""Build shared glossary and original element diagrams; --check detects glossary drift."""

import argparse
from pathlib import Path

from fem_solver.terms import TERMS

ROOT = Path(__file__).resolve().parents[1]


def glossary_text():
    lines = [
        "# Engineering and software glossary",
        "",
        "[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)",
        "",
        "These definitions are shared with the app. Hover, focus or tap dotted terms for help. You can also use the searchable Glossary view.",
        "",
        "This page is generated from [the reviewed terminology source](../../src/fem_solver/terms.py). Edit that source, then run `python scripts/build_learning_docs.py`. Do not edit generated definitions here.",
        "",
    ]
    for _key, term in sorted(TERMS.items(), key=lambda item: item[1].label.lower()):
        lines += [f"## {term.label}", "", term.meaning, "", f"[Read more](../{term.guide})", ""]
    lines += [
        "## Read next",
        "",
        "- [How to approach a structural problem](problem-solving.md)",
        "- [Use the guided app](../04-user-guide/app-guide.md)",
        "",
    ]
    return "\n".join(lines)


def diagrams():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Arc

    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), layout="constrained")
    fig.patch.set_facecolor("#f7f9fc")
    for ax in axes.flat:
        ax.set_aspect("equal")
        ax.set_xlim(-0.6, 3.7)
        ax.set_ylim(-0.65, 2.5)
        ax.axis("off")

    def line(ax, xs, ys):
        ax.plot(xs, ys, "o-", color="#2563eb", linewidth=3, markersize=7)

    def arrow(ax, x, y, dx, dy, label):
        ax.annotate(
            "",
            xy=(x + dx, y + dy),
            xytext=(x, y),
            arrowprops=dict(arrowstyle="->", color="#0f766e", lw=1.8),
        )
        ax.text(x + dx + 0.06, y + dy + 0.06, label, fontsize=10, color="#0f766e")

    def rotation(ax, x, y):
        ax.add_patch(Arc((x, y), 0.9, 0.9, theta1=20, theta2=145, color="#b45309", lw=1.8))
        ax.annotate(
            "",
            xy=(x - 0.37, y + 0.26),
            xytext=(x - 0.27, y + 0.37),
            arrowprops=dict(arrowstyle="->", color="#b45309"),
        )
        ax.text(x - 0.65, y + 0.62, "rz (+ CCW)", fontsize=10, color="#b45309")

    ax = axes[0, 0]
    ax.set_title("BAR · axial movement", loc="left", fontweight="bold", color="#13243a")
    line(ax, [0, 2.5], [0.5, 0.5])
    arrow(ax, 0, 0.5, 0.65, 0, "ux")
    arrow(ax, 2.5, 0.5, 0.65, 0, "ux")
    ax.text(0, -0.25, "Horizontal member · stretching only", fontsize=10)

    ax = axes[0, 1]
    ax.set_title("TRUSS · axial member forces", loc="left", fontweight="bold", color="#13243a")
    line(ax, [0, 2.6, 1.3, 0], [0, 0, 1.7, 0])
    arrow(ax, 2.6, 0, 0.6, 0, "ux")
    arrow(ax, 2.6, 0, 0, 0.75, "uy")
    ax.text(0, -0.45, "Ideal pin joints · no member bending", fontsize=10)

    ax = axes[1, 0]
    ax.set_title("BEAM · bending", loc="left", fontweight="bold", color="#13243a")
    line(ax, [0, 2.5], [0.5, 0.5])
    arrow(ax, 2.5, 0.5, 0, 0.8, "uy")
    rotation(ax, 0, 0.5)
    ax.text(0, -0.35, "At each node: uy and rz · no axial DOF", fontsize=10)

    ax = axes[1, 1]
    ax.set_title("FRAME · axial action + bending", loc="left", fontweight="bold", color="#13243a")
    line(ax, [0, 0, 2.5, 2.5], [0, 1.5, 1.5, 0])
    arrow(ax, 2.5, 1.5, 0.6, 0, "ux")
    arrow(ax, 2.5, 1.5, 0, 0.65, "uy")
    rotation(ax, 0, 1.5)
    ax.text(0, -0.45, "At each node: ux, uy and rz · rigid joints", fontsize=10)
    fig.suptitle(
        "Four model families — global x right, y up; rotation counterclockwise",
        fontsize=13,
        color="#13243a",
    )
    folder = ROOT / "reports/figures"
    folder.mkdir(parents=True, exist_ok=True)
    for extension in ("svg", "png"):
        fig.savefig(
            folder / f"element_families.{extension}",
            dpi=180,
            metadata={"Date": None} if extension == "svg" else None,
        )
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "docs/03-engineering-knowledge/glossary.md"
    expected = glossary_text()
    if args.check:
        if path.read_text(encoding="utf-8") != expected:
            raise SystemExit("Glossary is out of date. Run python scripts/build_learning_docs.py.")
        print(f"Shared glossary checked: {len(TERMS)} definitions.")
    else:
        path.write_text(expected, encoding="utf-8")
        diagrams()
        print(f"Built {len(TERMS)} glossary definitions and element diagrams.")


if __name__ == "__main__":
    main()
