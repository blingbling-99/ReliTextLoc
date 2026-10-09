"""Shared visual style for the ReliTextLoc main-paper figures.

The palette deliberately uses restrained, print-friendly colours.  The method
identity is stable across every generated figure.
"""
from __future__ import annotations

import matplotlib as mpl

FONT = "DejaVu Sans"
TEXT = "#26333c"
MUTED = "#62717b"
GRID = "#dce3e7"
BORDER = "#9eafb9"
BASELINE = "#66788a"       # Text2Loc++
EXTERNAL = "#bc7a4f"       # Text2Loc / CMMLoc
OURS = "#287d78"           # ReliTextLoc
OURS_LIGHT = "#dcefe9"
ORANGE_LIGHT = "#f7eadf"
BLUE_LIGHT = "#eaf2f7"
PURPLE_LIGHT = "#eee9f6"
RED = "#b94a48"
GREEN = "#2f8b63"


def apply_style() -> None:
    """Install deterministic, editable Matplotlib defaults."""
    mpl.rcParams.update({
        "font.family": FONT,
        "font.size": 8,
        "text.color": TEXT,
        "axes.labelcolor": TEXT,
        "axes.edgecolor": BORDER,
        "axes.linewidth": 0.65,
        "axes.labelsize": 8,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "relitextloc-main-figures-20260922",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })
