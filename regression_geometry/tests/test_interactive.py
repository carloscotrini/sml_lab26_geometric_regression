"""Tests for regression_geometry/interactive.py."""

import inspect
import numpy as np
import pytest
import plotly.graph_objects as go
import ipywidgets as widgets

from regression_geometry.core import ColumnSpace, Projection, HatMatrix, Ellipsoid
from regression_geometry import plots, interactive, colors


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rng():
    return np.random.RandomState(42)


@pytest.fixture
def small_cs_y(rng):
    """n=3, k=2 (with intercept -> p=3)."""
    X = rng.randn(3, 2)
    cs = ColumnSpace(X, add_intercept=False)
    y = rng.randn(3)
    return cs, y


@pytest.fixture
def medium_X_y(rng):
    """n=20, k=3 (no intercept)."""
    X = rng.randn(20, 3)
    y = rng.randn(20)
    return X, y


@pytest.fixture
def proj_cs(small_cs_y):
    cs, y = small_cs_y
    return cs.project(y), cs


# ---------------------------------------------------------------------------
# Function lists
# ---------------------------------------------------------------------------

SHARED_FUNCTIONS = [
    "plot_projection_3d", "plot_relevant_triangle", "plot_projection_2d",
    "plot_pythagorean_triangle", "plot_r_squared_angle", "plot_leverage",
    "plot_cooks_distance", "plot_influence_diagram", "plot_eigenvalue_ellipsoid",
    "plot_eigenvalue_bar", "plot_collinearity_comparison", "plot_fwl_decomposition",
    "plot_added_variable", "plot_ridge_lasso_constraint", "plot_shrinkage_path",
    "plot_nested_projections", "plot_confidence_ellipse", "plot_scoreboard",
]

INTERACTIVE_ONLY = [
    "plot_projection_3d_draggable", "plot_collinearity_slider",
    "plot_ridge_lasso_interactive", "plot_fwl_peeling",
    "plot_monte_carlo_projections",
]


# ---------------------------------------------------------------------------
# 1. Signature parity
# ---------------------------------------------------------------------------

class TestSignatureParity:

    @pytest.mark.parametrize("fname", SHARED_FUNCTIONS)
    def test_function_exists(self, fname):
        assert hasattr(interactive, fname)

    @pytest.mark.parametrize("fname", SHARED_FUNCTIONS)
    def test_params_match(self, fname):
        plots_sig = inspect.signature(getattr(plots, fname))
        inter_sig = inspect.signature(getattr(interactive, fname))
        for p_name in plots_sig.parameters:
            if p_name == "kwargs":
                continue
            assert p_name in inter_sig.parameters, f"{fname}: missing param '{p_name}'"

    @pytest.mark.parametrize("fname", SHARED_FUNCTIONS)
    def test_defaults_match(self, fname):
        plots_sig = inspect.signature(getattr(plots, fname))
        inter_sig = inspect.signature(getattr(interactive, fname))
        for p_name, pparam in plots_sig.parameters.items():
            if p_name == "kwargs" or pparam.default is inspect.Parameter.empty:
                continue
            iparam = inter_sig.parameters.get(p_name)
            if iparam is None or iparam.default is inspect.Parameter.empty:
                continue
            assert pparam.default == iparam.default, (
                f"{fname}.{p_name}: plots={pparam.default!r} != interactive={iparam.default!r}"
            )


# ---------------------------------------------------------------------------
# 2. Return types
# ---------------------------------------------------------------------------

class TestReturnTypes:

    def test_projection_3d(self, small_cs_y):
        cs, y = small_cs_y
        assert isinstance(interactive.plot_projection_3d(cs, y), go.Figure)

    def test_projection_3d_three_panel(self, small_cs_y):
        cs, y = small_cs_y
        assert isinstance(interactive.plot_projection_3d(cs, y, views="three_panel"), widgets.HBox)

    def test_relevant_triangle(self, small_cs_y):
        cs, y = small_cs_y
        assert isinstance(interactive.plot_relevant_triangle(cs, y, j=0), go.Figure)

    def test_projection_2d(self, rng):
        x = rng.randn(20)
        y = rng.randn(20)
        assert isinstance(interactive.plot_projection_2d(x, y), go.Figure)

    def test_pythagorean(self, proj_cs):
        proj, cs = proj_cs
        assert isinstance(interactive.plot_pythagorean_triangle(proj), go.Figure)

    def test_r_squared_angle(self, proj_cs):
        proj, cs = proj_cs
        assert isinstance(interactive.plot_r_squared_angle(proj), go.Figure)

    def test_leverage(self, proj_cs):
        proj, cs = proj_cs
        hm = HatMatrix(proj.H)
        assert isinstance(interactive.plot_leverage(hm), go.Figure)

    def test_cooks_distance(self, proj_cs):
        proj, cs = proj_cs
        hm = HatMatrix(proj.H)
        mse = proj.sse / max(cs.n - cs.p, 1)
        cd = hm.cooks_distance(proj.residuals, mse, cs.p)
        assert isinstance(interactive.plot_cooks_distance(cd), go.Figure)

    def test_influence_diagram(self, proj_cs):
        proj, cs = proj_cs
        hm = HatMatrix(proj.H)
        mse = proj.sse / max(cs.n - cs.p, 1)
        assert isinstance(interactive.plot_influence_diagram(hm, proj.residuals, mse, cs.p), go.Figure)

    def test_eigenvalue_ellipsoid(self, small_cs_y):
        cs, _ = small_cs_y
        ell = Ellipsoid(cs.X.T @ cs.X)
        assert isinstance(interactive.plot_eigenvalue_ellipsoid(ell), go.Figure)

    def test_eigenvalue_bar(self, small_cs_y):
        cs, _ = small_cs_y
        ell = Ellipsoid(cs.X.T @ cs.X)
        assert isinstance(interactive.plot_eigenvalue_bar(ell), go.Figure)

    def test_collinearity_comparison(self, rng):
        X_low = rng.randn(3, 2)
        X_high = rng.randn(3, 2)
        cs_low = ColumnSpace(X_low, add_intercept=False)
        cs_high = ColumnSpace(X_high, add_intercept=False)
        y = rng.randn(3)
        assert isinstance(interactive.plot_collinearity_comparison(cs_low, cs_high, y), go.Figure)

    def test_fwl_decomposition(self, medium_X_y):
        X, y = medium_X_y
        assert isinstance(interactive.plot_fwl_decomposition(X, y, j=1), go.Figure)

    def test_added_variable(self, medium_X_y):
        X, y = medium_X_y
        assert isinstance(interactive.plot_added_variable(X, y, j=1), go.Figure)

    def test_ridge_lasso_constraint(self, rng):
        beta = rng.randn(2)
        assert isinstance(interactive.plot_ridge_lasso_constraint(beta), go.Figure)

    def test_shrinkage_path(self, medium_X_y):
        X, y = medium_X_y
        ell = Ellipsoid(X.T @ X)
        coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        assert isinstance(interactive.plot_shrinkage_path(ell, coef, lam_range=np.logspace(-1, 2, 20)), go.Figure)

    def test_nested_projections(self, small_cs_y):
        cs, y = small_cs_y
        cs_r = ColumnSpace(cs.X[:, :1], add_intercept=False)
        assert isinstance(interactive.plot_nested_projections(cs_r, cs, y), go.Figure)

    def test_confidence_ellipse(self, rng):
        beta = rng.randn(3)
        cov = np.eye(3)
        assert isinstance(interactive.plot_confidence_ellipse(beta, cov), go.Figure)

    def test_scoreboard(self, proj_cs):
        proj, cs = proj_cs
        assert isinstance(interactive.plot_scoreboard(proj, cs), widgets.HBox)


# ---------------------------------------------------------------------------
# 3. Interactive-only functions
# ---------------------------------------------------------------------------

class TestInteractiveOnly:

    @pytest.mark.parametrize("fname", INTERACTIVE_ONLY)
    def test_exists(self, fname):
        assert hasattr(interactive, fname) and callable(getattr(interactive, fname))

    def test_draggable(self, small_cs_y):
        cs, y = small_cs_y
        assert isinstance(interactive.plot_projection_3d_draggable(cs, y), widgets.VBox)

    def test_collinearity_slider(self):
        assert isinstance(interactive.plot_collinearity_slider(n=20, seed=42), widgets.VBox)

    def test_ridge_lasso_interactive(self, medium_X_y):
        X, y = medium_X_y
        assert isinstance(interactive.plot_ridge_lasso_interactive(X, y), widgets.VBox)

    def test_fwl_peeling(self, rng):
        X = rng.randn(3, 2)
        y = rng.randn(3)
        assert isinstance(interactive.plot_fwl_peeling(X, y), widgets.VBox)

    def test_monte_carlo(self, small_cs_y):
        cs, _ = small_cs_y
        beta_true = np.ones(cs.p)
        assert isinstance(interactive.plot_monte_carlo_projections(cs, beta_true, sigma=0.5, n_samples=3), widgets.VBox)


# ---------------------------------------------------------------------------
# 4. Color compliance
# ---------------------------------------------------------------------------

class TestColorCompliance:

    def test_column_space_color_in_projection_3d(self, small_cs_y):
        cs, y = small_cs_y
        fig = interactive.plot_projection_3d(cs, y)
        assert colors.COLUMN_SPACE in fig.to_json()


# ---------------------------------------------------------------------------
# 5. No crash on random data
# ---------------------------------------------------------------------------

class TestNoCrash:

    @pytest.mark.parametrize("seed", [0, 1, 2])
    def test_all_shared_no_crash(self, seed):
        rng = np.random.RandomState(seed)
        # n=3 data
        X3 = rng.randn(3, 2)
        y3 = rng.randn(3)
        cs3 = ColumnSpace(X3, add_intercept=False)
        proj3 = cs3.project(y3)
        hm3 = HatMatrix(proj3.H)
        ell3 = Ellipsoid(cs3.X.T @ cs3.X)
        mse3 = proj3.sse / max(cs3.n - cs3.p, 1)
        cd3 = hm3.cooks_distance(proj3.residuals, mse3, cs3.p)
        # n=20 data
        X20 = rng.randn(20, 3)
        y20 = rng.randn(20)

        interactive.plot_projection_3d(cs3, y3)
        interactive.plot_relevant_triangle(cs3, y3, j=0)
        interactive.plot_projection_2d(rng.randn(20), rng.randn(20))
        interactive.plot_pythagorean_triangle(proj3)
        interactive.plot_r_squared_angle(proj3)
        interactive.plot_leverage(hm3)
        interactive.plot_cooks_distance(cd3)
        interactive.plot_influence_diagram(hm3, proj3.residuals, mse3, cs3.p)
        interactive.plot_eigenvalue_ellipsoid(ell3)
        interactive.plot_eigenvalue_bar(ell3)
        cs3b = ColumnSpace(rng.randn(3, 2), add_intercept=False)
        interactive.plot_collinearity_comparison(cs3, cs3b, y3)
        interactive.plot_fwl_decomposition(X20, y20, j=1)
        interactive.plot_added_variable(X20, y20, j=1)
        interactive.plot_ridge_lasso_constraint(rng.randn(2))
        ell20 = Ellipsoid(X20.T @ X20)
        coef20, _, _, _ = np.linalg.lstsq(X20, y20, rcond=None)
        interactive.plot_shrinkage_path(ell20, coef20, lam_range=np.logspace(-1, 2, 10))
        cs_r = ColumnSpace(cs3.X[:, :1], add_intercept=False)
        interactive.plot_nested_projections(cs_r, cs3, y3)
        interactive.plot_confidence_ellipse(rng.randn(3), np.eye(3))
        interactive.plot_scoreboard(proj3, cs3)


# ---------------------------------------------------------------------------
# 6. AVAILABLE flag
# ---------------------------------------------------------------------------

class TestAvailableFlag:
    def test_available(self):
        assert interactive.AVAILABLE is True
