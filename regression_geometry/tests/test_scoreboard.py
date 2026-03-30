"""Tests for regression_geometry/scoreboard.py."""

import inspect
import numpy as np
import pytest
import ipywidgets as widgets
from matplotlib.figure import Figure

from regression_geometry.core import ColumnSpace, HatMatrix
from regression_geometry.scoreboard import (
    GeometricScoreboard, plot_scoreboard, _gauge_color, ALL_GAUGES,
)
from regression_geometry import colors, interactive, plots


@pytest.fixture
def rng():
    return np.random.RandomState(42)


@pytest.fixture
def proj_cs(rng):
    X = rng.randn(5, 2)
    cs = ColumnSpace(X, add_intercept=True)
    y = rng.randn(5)
    return cs.project(y), cs


def _make_proj_with_theta(theta_deg: float):
    """Construct data so that proj.theta_degrees ~ theta_deg.

    Projection.theta uses demeaned vectors, so we construct y such that
    the angle between demean(y) and demean(y_hat) equals theta_deg.
    """
    theta_rad = np.radians(theta_deg)
    # Use 4 observations with intercept to get demeaning right
    n = 4
    X = np.ones((n, 1))  # intercept only
    cs = ColumnSpace(X, add_intercept=False)
    # y_hat = mean(y) * ones (projection onto intercept)
    # demean(y_hat) = 0, demean(y) = y - mean(y)
    # So R^2 = 0, theta = 90 deg always with intercept-only.
    # Instead, use a 2-column design with intercept + x
    x = np.array([1.0, 2.0, 3.0, 4.0])
    cs = ColumnSpace(x, add_intercept=True)
    # We want R^2 = cos^2(theta_deg), so generate y accordingly
    r2_target = np.cos(theta_rad) ** 2
    # y = b0 + b1*x + noise; choose noise level to achieve target R^2
    y_hat_part = 1.0 + 0.5 * x
    y_hat_dm = y_hat_part - y_hat_part.mean()
    # ||y_hat_dm||^2 / (||y_hat_dm||^2 + ||noise||^2) = r2_target
    # => ||noise||^2 = ||y_hat_dm||^2 * (1/r2_target - 1)
    ss_yhat = np.dot(y_hat_dm, y_hat_dm)
    if r2_target > 1e-10:
        ss_noise_target = ss_yhat * (1.0 / r2_target - 1.0)
    else:
        ss_noise_target = ss_yhat * 100
    # noise orthogonal to column space
    noise_raw = np.array([1.0, -1.0, 1.0, -1.0])
    M = cs.orthogonal_complement()
    noise = M @ noise_raw
    noise_norm = np.linalg.norm(noise)
    if noise_norm > 1e-15:
        noise = noise * np.sqrt(ss_noise_target) / noise_norm
    y = y_hat_part + noise
    proj = cs.project(y)
    return proj, cs


# ---------------------------------------------------------------------------
# Widget creation
# ---------------------------------------------------------------------------

class TestWidgetCreation:
    def test_returns_widget(self, proj_cs):
        proj, cs = proj_cs
        sb = GeometricScoreboard(proj=proj, cs=cs, mode="widget")
        assert isinstance(sb.display(), widgets.HBox)

    def test_five_children(self, proj_cs):
        proj, cs = proj_cs
        sb = GeometricScoreboard(proj=proj, cs=cs, mode="widget")
        assert len(sb.display().children) == 5


# ---------------------------------------------------------------------------
# Static creation
# ---------------------------------------------------------------------------

class TestStaticCreation:
    def test_returns_figure(self, proj_cs):
        proj, cs = proj_cs
        sb = GeometricScoreboard(proj=proj, cs=cs, mode="static")
        assert isinstance(sb.display(), Figure)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_values_change(self, proj_cs, rng):
        proj, cs = proj_cs
        sb = GeometricScoreboard(proj=proj, cs=cs, mode="widget")
        sb.display()
        old = dict(sb._values)
        y_new = rng.randn(cs.n) * 10
        sb.update(cs.project(y_new), cs)
        assert sb._values != old


# ---------------------------------------------------------------------------
# Locking / Unlocking
# ---------------------------------------------------------------------------

class TestLocking:
    def test_partial_active(self, proj_cs):
        proj, cs = proj_cs
        sb = GeometricScoreboard(proj=proj, cs=cs, active_gauges=["theta"], mode="widget")
        box = sb.display()
        assert "?" not in box.children[0].value  # theta
        assert "?" in box.children[1].value       # kappa locked

    def test_unlock(self, proj_cs):
        proj, cs = proj_cs
        sb = GeometricScoreboard(proj=proj, cs=cs, active_gauges=["theta"], mode="widget")
        sb.display()
        sb.unlock("kappa")
        assert "?" not in sb._gauge_widgets["kappa"].value

    def test_lock(self, proj_cs):
        proj, cs = proj_cs
        sb = GeometricScoreboard(proj=proj, cs=cs, mode="widget")
        sb.display()
        sb.lock("kappa")
        assert "?" in sb._gauge_widgets["kappa"].value


# ---------------------------------------------------------------------------
# Threshold colors
# ---------------------------------------------------------------------------

class TestThresholdColors:
    def test_theta_green(self):
        proj, cs = _make_proj_with_theta(30.0)
        assert _gauge_color("theta", proj.theta_degrees) == colors.PROJECTION

    def test_theta_yellow(self):
        proj, cs = _make_proj_with_theta(55.0)
        assert _gauge_color("theta", proj.theta_degrees) == colors.RESPONSE_Y

    def test_theta_red(self):
        proj, cs = _make_proj_with_theta(80.0)
        assert _gauge_color("theta", proj.theta_degrees) == colors.RESIDUAL

    def test_kappa_green(self):
        assert _gauge_color("kappa", 10) == colors.PROJECTION

    def test_kappa_yellow(self):
        assert _gauge_color("kappa", 50) == colors.RESPONSE_Y

    def test_kappa_red(self):
        assert _gauge_color("kappa", 200) == colors.RESIDUAL

    def test_residual_norm_green(self):
        assert _gauge_color("residual_norm", 0.3) == colors.PROJECTION

    def test_residual_norm_yellow(self):
        assert _gauge_color("residual_norm", 0.6) == colors.RESPONSE_Y

    def test_residual_norm_red(self):
        assert _gauge_color("residual_norm", 0.9) == colors.RESIDUAL


# ---------------------------------------------------------------------------
# Signature parity
# ---------------------------------------------------------------------------

class TestSignatureParity:
    def test_params_match(self):
        plots_sig = inspect.signature(plots.plot_scoreboard)
        inter_sig = inspect.signature(interactive.plot_scoreboard)
        for pname, pparam in plots_sig.parameters.items():
            if pname == "kwargs":
                continue
            assert pname in inter_sig.parameters
            if pparam.default is not inspect.Parameter.empty:
                iparam = inter_sig.parameters[pname]
                if iparam.default is not inspect.Parameter.empty:
                    assert pparam.default == iparam.default


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

class TestConvenienceFunction:
    def test_returns_widget(self, proj_cs):
        proj, cs = proj_cs
        assert isinstance(plot_scoreboard(proj, cs), widgets.HBox)

    def test_with_active_gauges(self, proj_cs):
        proj, cs = proj_cs
        assert isinstance(plot_scoreboard(proj, cs, active_gauges=["theta", "r_squared"]), widgets.HBox)
