"""Geometric Scoreboard — five-gauge display for regression diagnostics.

Provides both ipywidgets (interactive) and matplotlib (static) modes.
"""

from __future__ import annotations

import numpy as np
from regression_geometry.core import Projection, ColumnSpace, HatMatrix
from regression_geometry import colors

try:
    import ipywidgets as widgets
    _HAS_WIDGETS = True
except ImportError:
    _HAS_WIDGETS = False

ALL_GAUGES = ["theta", "kappa", "leverage", "residual_norm", "r_squared"]

GAUGE_META = {
    "theta":         {"label": "\u03b8"},
    "kappa":         {"label": "\u03ba"},
    "leverage":      {"label": "tr(H)/n"},
    "residual_norm": {"label": "\u2016e\u2016/\u2016y\u2016"},
    "r_squared":     {"label": "R\u00b2"},
}

# Scoreboard threshold colors (per SPEC.md §6.5)
_GREEN = colors.PROJECTION   # #10B981
_YELLOW = colors.RESPONSE_Y  # #F59E0B
_RED = colors.RESIDUAL        # #EF4444
_GRAY = colors.SECONDARY      # #6B7280


def _format_value(name: str, val: float) -> str:
    if name == "theta":
        return f"{val:.1f}\u00b0"
    if name == "kappa":
        if not np.isfinite(val):
            return "\u221e"
        if val < 1e4:
            return f"{val:.1f}"
        return f"{val:.1e}"
    return f"{val:.3f}"


def _gauge_color(name: str, val: float) -> str:
    if name == "theta":
        if val < 45:
            return _GREEN
        if val < 70:
            return _YELLOW
        return _RED
    if name == "kappa":
        if not np.isfinite(val) or val > 100:
            return _RED
        if val > 30:
            return _YELLOW
        return _GREEN
    if name == "residual_norm":
        if val < 0.5:
            return _GREEN
        if val < 0.8:
            return _YELLOW
        return _RED
    # leverage and r_squared are informational
    return _GREEN


def _compute_values(proj: Projection, cs: ColumnSpace = None) -> dict:
    hm = HatMatrix(proj.H)
    return {
        "theta": proj.theta_degrees,
        "kappa": cs.condition_number() if cs is not None else 1.0,
        "leverage": hm.average_leverage(),
        "residual_norm": proj.relative_residual_norm,
        "r_squared": proj.r_squared,
    }


class GeometricScoreboard:
    """Five-gauge Geometric Scoreboard.

    Parameters
    ----------
    proj : Projection, optional
        Initialize gauge values from this projection.
    cs : ColumnSpace, optional
        Used to compute condition number.
    active_gauges : list of str, optional
        Which gauges are unlocked. None means all active.
    mode : str
        "widget" for ipywidgets, "static" for matplotlib.
    """

    def __init__(
        self,
        proj: Projection = None,
        cs: ColumnSpace = None,
        active_gauges: list = None,
        mode: str = "widget",
    ):
        self._active = set(active_gauges) if active_gauges is not None else set(ALL_GAUGES)
        self._mode = mode
        self._values: dict = {}
        self._gauge_widgets: dict = {}
        if proj is not None:
            self._values = _compute_values(proj, cs)

    def update(self, proj: Projection, cs: ColumnSpace = None):
        self._values = _compute_values(proj, cs)
        if self._mode == "widget" and self._gauge_widgets:
            self._refresh_widgets()

    def unlock(self, gauge_name: str):
        self._active.add(gauge_name)
        if self._mode == "widget" and self._gauge_widgets:
            self._refresh_widgets()

    def lock(self, gauge_name: str):
        self._active.discard(gauge_name)
        if self._mode == "widget" and self._gauge_widgets:
            self._refresh_widgets()

    def display(self):
        if self._mode == "static":
            return self._display_static()
        return self._display_widget()

    def _display_widget(self):
        if not _HAS_WIDGETS:
            return self._display_static()
        gauge_boxes = []
        for name in ALL_GAUGES:
            html_w = widgets.HTML(value=self._gauge_html(name))
            self._gauge_widgets[name] = html_w
            gauge_boxes.append(html_w)
        return widgets.HBox(
            gauge_boxes,
            layout=widgets.Layout(
                width="700px", border="1px solid #E5E7EB",
                padding="8px", justify_content="space-around",
            ),
        )

    def _display_static(self):
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 5, figsize=(12, 1.5))
        fig.suptitle("Geometric Scoreboard", fontsize=colors.TITLE_SIZE, y=1.05)
        for ax, name in zip(axes, ALL_GAUGES):
            active = name in self._active
            val = self._values.get(name, 0)
            c = _gauge_color(name, val) if active else _GRAY
            val_str = _format_value(name, val) if active else "?"
            meta = GAUGE_META[name]
            alpha = 1.0 if active else 0.4
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            ax.add_patch(plt.Rectangle((0.1, 0.0), 0.8, 0.15, color=c))
            ax.text(0.5, 0.7, meta["label"], ha="center", va="center",
                    fontsize=12, fontweight="bold", alpha=alpha)
            ax.text(0.5, 0.4, val_str, ha="center", va="center",
                    fontsize=10, alpha=alpha)
        fig.tight_layout()
        plt.close(fig)
        return fig

    def _gauge_html(self, name: str) -> str:
        meta = GAUGE_META[name]
        active = name in self._active
        val = self._values.get(name, 0)
        c = _gauge_color(name, val) if active else _GRAY
        val_str = _format_value(name, val) if active else "?"
        opacity = "1.0" if active else "0.4"
        return (
            f'<div style="width:130px;height:80px;text-align:center;font-family:sans-serif;">'
            f'<div style="font-weight:bold;font-size:14px;opacity:{opacity};margin-top:5px;">{meta["label"]}</div>'
            f'<div style="font-size:13px;opacity:{opacity};margin:4px 0;">{val_str}</div>'
            f'<div style="height:6px;background:{c};border-radius:3px;margin:0 15px;"></div>'
            f'</div>'
        )

    def _refresh_widgets(self):
        for name, w in self._gauge_widgets.items():
            w.value = self._gauge_html(name)


# ---------------------------------------------------------------------------
# Convenience function (signature parity with plots.plot_scoreboard)
# ---------------------------------------------------------------------------

def plot_scoreboard(
    proj: Projection,
    cs: ColumnSpace,
    active_gauges: list = None,
    title: str = "Geometric Scoreboard",
    figsize: tuple = (12, 1.5),
    **kwargs,
) -> "widgets.HBox":
    sb = GeometricScoreboard(proj=proj, cs=cs, active_gauges=active_gauges, mode="widget")
    return sb.display()
