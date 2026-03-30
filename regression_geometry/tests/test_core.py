"""Comprehensive test suite for regression_geometry.core.

Covers: projection accuracy, Pythagorean theorem, orthogonality, R²=cos²θ,
hat matrix properties, leverage sum, Cook's distance, FWL, relevant triangle,
condition number, Ridge coefficients, edge cases, and intercept handling.
"""

import warnings

import numpy as np
import pytest
import statsmodels.api as sm
from sklearn.linear_model import Ridge
from statsmodels.stats.outliers_influence import OLSInfluence

from regression_geometry.core import (
    ColumnSpace,
    Ellipsoid,
    HatMatrix,
    Projection,
    angle_between,
    demean,
    frisch_waugh_lovell,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_data(n=50, k=3, seed=None):
    """Generate random X (n, k) and y with known beta."""
    rng = np.random.RandomState(seed)
    X = rng.randn(n, k)
    beta = rng.randn(k)
    y = X @ beta + rng.randn(n) * 0.5
    return X, y, beta


# ---------------------------------------------------------------------------
# 1. Projection accuracy
# ---------------------------------------------------------------------------

class TestProjectionAccuracy:
    """Verify coefficients match np.linalg.lstsq and statsmodels.OLS."""

    @pytest.mark.parametrize("seed", [0, 1, 2])
    def test_coefficients_match_lstsq(self, seed):
        X, y, _ = _random_data(seed=seed)
        cs = ColumnSpace(X)
        proj = cs.project(y)
        expected, _, _, _ = np.linalg.lstsq(cs.X, y, rcond=None)
        np.testing.assert_allclose(proj.coefficients, expected, atol=1e-10)

    @pytest.mark.parametrize("seed", [0, 1, 2])
    def test_coefficients_match_statsmodels(self, seed):
        X, y, _ = _random_data(seed=seed)
        X_with_const = sm.add_constant(X)
        model = sm.OLS(y, X_with_const).fit()
        cs = ColumnSpace(X)
        proj = cs.project(y)
        np.testing.assert_allclose(proj.coefficients, model.params, atol=1e-10)


# ---------------------------------------------------------------------------
# 2. Pythagorean theorem
# ---------------------------------------------------------------------------

class TestPythagorean:
    """Verify SST = SSR + SSE for random datasets."""

    @pytest.mark.parametrize("seed", range(10))
    def test_pythagorean(self, seed):
        X, y, _ = _random_data(seed=seed)
        cs = ColumnSpace(X)
        proj = cs.project(y)
        assert proj.verify_pythagorean(), (
            f"SST={proj.sst}, SSR={proj.ssr}, SSE={proj.sse}, "
            f"diff={abs(proj.sst - proj.ssr - proj.sse)}"
        )


# ---------------------------------------------------------------------------
# 3. Orthogonality
# ---------------------------------------------------------------------------

class TestOrthogonality:
    """Verify X'e ≈ 0 for random datasets."""

    @pytest.mark.parametrize("seed", range(10))
    def test_orthogonality(self, seed):
        X, y, _ = _random_data(seed=seed)
        cs = ColumnSpace(X)
        proj = cs.project(y)
        assert proj.verify_orthogonality(cs.X)


# ---------------------------------------------------------------------------
# 4. R² = cos²(θ)
# ---------------------------------------------------------------------------

class TestRSquaredAngle:
    """Verify R² ≈ cos²(θ) for random datasets."""

    @pytest.mark.parametrize("seed", range(10))
    def test_r_squared_cos_squared_theta(self, seed):
        X, y, _ = _random_data(seed=seed)
        cs = ColumnSpace(X)
        proj = cs.project(y)
        np.testing.assert_allclose(
            proj.r_squared,
            np.cos(proj.theta) ** 2,
            atol=1e-10,
        )


# ---------------------------------------------------------------------------
# 5. Hat matrix properties
# ---------------------------------------------------------------------------

class TestHatMatrixProperties:
    """Verify idempotent and symmetric for random X."""

    @pytest.mark.parametrize("seed", range(5))
    def test_idempotent(self, seed):
        X, _, _ = _random_data(seed=seed)
        cs = ColumnSpace(X)
        H = cs.hat_matrix()
        hm = HatMatrix(H)
        assert hm.verify_idempotent()

    @pytest.mark.parametrize("seed", range(5))
    def test_symmetric(self, seed):
        X, _, _ = _random_data(seed=seed)
        cs = ColumnSpace(X)
        H = cs.hat_matrix()
        hm = HatMatrix(H)
        assert hm.verify_symmetric()


# ---------------------------------------------------------------------------
# 6. Leverage sum
# ---------------------------------------------------------------------------

class TestLeverageSum:
    """Verify tr(H) ≈ p for random X."""

    @pytest.mark.parametrize("seed", range(5))
    def test_trace_equals_p(self, seed):
        X, _, _ = _random_data(seed=seed)
        cs = ColumnSpace(X)
        H = cs.hat_matrix()
        hm = HatMatrix(H)
        np.testing.assert_allclose(hm.trace(), cs.p, atol=1e-8)


# ---------------------------------------------------------------------------
# 7. Cook's distance
# ---------------------------------------------------------------------------

class TestCooksDistance:
    """Compare Cook's D against statsmodels OLSInfluence."""

    @pytest.mark.parametrize("seed", [0, 1, 2])
    def test_cooks_distance_matches_statsmodels(self, seed):
        X, y, _ = _random_data(n=80, k=3, seed=seed)
        X_with_const = sm.add_constant(X)
        model = sm.OLS(y, X_with_const).fit()
        influence = OLSInfluence(model)
        expected_cooks = influence.cooks_distance[0]

        cs = ColumnSpace(X)
        proj = cs.project(y)
        hm = HatMatrix(proj.H)
        mse = proj.sse / (cs.n - cs.p)
        our_cooks = hm.cooks_distance(proj.residuals, mse, cs.p)

        np.testing.assert_allclose(our_cooks, expected_cooks, atol=1e-8)


# ---------------------------------------------------------------------------
# 8. Frisch-Waugh-Lovell
# ---------------------------------------------------------------------------

class TestFrischWaughLovell:
    """Verify FWL beta_j matches j-th coefficient from full OLS."""

    @pytest.mark.parametrize("seed", range(5))
    def test_fwl_matches_full_ols(self, seed):
        X, y, _ = _random_data(n=60, k=4, seed=seed)
        cs = ColumnSpace(X)
        proj = cs.project(y)
        for j in range(cs.p):
            result = frisch_waugh_lovell(cs.X, y, j)
            np.testing.assert_allclose(
                result["beta_j"], proj.coefficients[j], atol=1e-8,
                err_msg=f"FWL mismatch at j={j}"
            )


# ---------------------------------------------------------------------------
# 9. Relevant triangle
# ---------------------------------------------------------------------------

class TestRelevantTriangle:
    """Verify relevant_triangle beta_j matches full OLS coefficients."""

    @pytest.mark.parametrize("seed", range(5))
    def test_relevant_triangle_beta(self, seed):
        X, y, _ = _random_data(n=60, k=3, seed=seed)
        cs = ColumnSpace(X)
        proj = cs.project(y)
        for j in range(cs.p):
            rt = cs.relevant_triangle(y, j)
            np.testing.assert_allclose(
                rt["beta_j"], proj.coefficients[j], atol=1e-8,
                err_msg=f"Relevant triangle mismatch at j={j}"
            )


# ---------------------------------------------------------------------------
# 10. Condition number
# ---------------------------------------------------------------------------

class TestConditionNumber:
    """Verify cond(X'X) ≈ cond(X)² (numpy's cond is on X)."""

    @pytest.mark.parametrize("seed", range(5))
    def test_condition_number_relationship(self, seed):
        X, _, _ = _random_data(n=50, k=3, seed=seed)
        cs = ColumnSpace(X, add_intercept=False)
        our_cond = cs.condition_number()
        numpy_cond = np.linalg.cond(X)
        np.testing.assert_allclose(our_cond, numpy_cond ** 2, rtol=1e-6)


# ---------------------------------------------------------------------------
# 11. Ridge coefficients
# ---------------------------------------------------------------------------

class TestRidgeCoefficients:
    """Verify Ellipsoid.ridge_coefficients matches sklearn Ridge."""

    @pytest.mark.parametrize("seed", [0, 1, 2])
    @pytest.mark.parametrize("lam", [0.1, 1.0, 10.0])
    def test_ridge_matches_sklearn(self, seed, lam):
        rng = np.random.RandomState(seed)
        n, k = 100, 3
        X = rng.randn(n, k)
        y = X @ rng.randn(k) + rng.randn(n) * 0.5

        # sklearn Ridge (no intercept to keep it simple)
        ridge = Ridge(alpha=lam, fit_intercept=False)
        ridge.fit(X, y)
        expected = ridge.coef_

        # Our implementation
        XtX = X.T @ X
        beta_ols, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        ell = Ellipsoid(XtX)
        our_ridge = ell.ridge_coefficients(beta_ols, lam)

        np.testing.assert_allclose(our_ridge, expected, atol=1e-8)


# ---------------------------------------------------------------------------
# 12. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge cases: constant y, perfect fit, single predictor, rank-deficient X."""

    def test_constant_y_r_squared_zero(self):
        """Constant y => R² = 0."""
        rng = np.random.RandomState(0)
        X = rng.randn(30, 2)
        y = np.full(30, 5.0)
        cs = ColumnSpace(X)
        proj = cs.project(y)
        assert proj.r_squared == 0.0

    def test_perfect_fit_r_squared_one(self):
        """y in C(X) => R² = 1."""
        rng = np.random.RandomState(0)
        X = rng.randn(30, 2)
        cs = ColumnSpace(X)
        # y is a linear combination of columns of cs.X
        beta = np.array([1.0, 2.0, 3.0])  # intercept + 2 predictors
        y = cs.X @ beta
        proj = cs.project(y)
        np.testing.assert_allclose(proj.r_squared, 1.0, atol=1e-10)

    def test_single_predictor(self):
        """1D X should work (simple regression)."""
        rng = np.random.RandomState(0)
        x = rng.randn(50)
        y = 2.0 * x + 1.0 + rng.randn(50) * 0.1
        cs = ColumnSpace(x)
        proj = cs.project(y)
        assert proj.r_squared > 0.9
        assert proj.verify_pythagorean()

    def test_rank_deficient_warns(self):
        """Rank-deficient X should issue a warning."""
        X = np.ones((20, 2))  # both columns identical
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            cs = ColumnSpace(X, add_intercept=False)
            assert len(w) >= 1
            assert "rank-deficient" in str(w[0].message).lower()

    def test_single_observation_raises(self):
        """Single observation should raise ValueError."""
        X = np.array([[1.0, 2.0]])
        with pytest.raises(ValueError, match="at least 2"):
            ColumnSpace(X)


# ---------------------------------------------------------------------------
# 13. Intercept handling
# ---------------------------------------------------------------------------

class TestInterceptHandling:
    """Verify results match: add_intercept=True vs manually prepending ones."""

    @pytest.mark.parametrize("seed", [0, 1, 2])
    def test_intercept_equivalence(self, seed):
        X, y, _ = _random_data(n=50, k=2, seed=seed)

        # Auto intercept
        cs_auto = ColumnSpace(X, add_intercept=True)
        proj_auto = cs_auto.project(y)

        # Manual intercept
        X_manual = np.column_stack([np.ones(50), X])
        cs_manual = ColumnSpace(X_manual, add_intercept=False)
        proj_manual = cs_manual.project(y)

        np.testing.assert_allclose(
            proj_auto.coefficients, proj_manual.coefficients, atol=1e-10
        )
        np.testing.assert_allclose(
            proj_auto.y_hat, proj_manual.y_hat, atol=1e-10
        )
        np.testing.assert_allclose(
            proj_auto.r_squared, proj_manual.r_squared, atol=1e-10
        )


# ---------------------------------------------------------------------------
# Additional utility tests
# ---------------------------------------------------------------------------

class TestUtilities:
    """Test angle_between and demean."""

    def test_angle_orthogonal(self):
        u = np.array([1.0, 0.0, 0.0])
        v = np.array([0.0, 1.0, 0.0])
        np.testing.assert_allclose(angle_between(u, v), np.pi / 2, atol=1e-12)

    def test_angle_parallel(self):
        u = np.array([1.0, 2.0, 3.0])
        np.testing.assert_allclose(angle_between(u, u), 0.0, atol=1e-12)

    def test_angle_antiparallel(self):
        u = np.array([1.0, 0.0])
        v = np.array([-1.0, 0.0])
        np.testing.assert_allclose(angle_between(u, v), np.pi, atol=1e-12)

    def test_angle_zero_vector(self):
        u = np.array([0.0, 0.0])
        v = np.array([1.0, 0.0])
        assert angle_between(u, v) == 0.0

    def test_demean(self):
        v = np.array([1.0, 2.0, 3.0])
        result = demean(v)
        np.testing.assert_allclose(result, [-1.0, 0.0, 1.0], atol=1e-12)
        np.testing.assert_allclose(result.mean(), 0.0, atol=1e-15)

    def test_angle_shape_mismatch(self):
        with pytest.raises(ValueError, match="Shape mismatch"):
            angle_between(np.array([1, 2]), np.array([1, 2, 3]))


class TestEllipsoidBasic:
    """Basic Ellipsoid tests."""

    def test_shrinkage_zero_lambda(self):
        XtX = np.diag([4.0, 1.0])
        ell = Ellipsoid(XtX)
        sf = ell.shrinkage_factors(0.0)
        np.testing.assert_allclose(sf, [1.0, 1.0], atol=1e-12)

    def test_ridge_zero_lambda_returns_ols(self):
        XtX = np.diag([4.0, 1.0])
        ell = Ellipsoid(XtX)
        beta = np.array([2.0, 3.0])
        result = ell.ridge_coefficients(beta, 0.0)
        np.testing.assert_allclose(result, beta, atol=1e-12)

    def test_condition_number_diagonal(self):
        XtX = np.diag([100.0, 1.0])
        ell = Ellipsoid(XtX)
        assert ell.condition_number == 100.0

    def test_axis_lengths(self):
        XtX = np.diag([9.0, 4.0])
        ell = Ellipsoid(XtX)
        np.testing.assert_allclose(ell.axis_lengths, [3.0, 2.0], atol=1e-12)

    def test_negative_lambda_raises(self):
        XtX = np.diag([1.0, 1.0])
        ell = Ellipsoid(XtX)
        with pytest.raises(ValueError, match="lam must be >= 0"):
            ell.shrinkage_factors(-1.0)

    def test_non_symmetric_raises(self):
        XtX = np.array([[1.0, 2.0], [3.0, 4.0]])
        with pytest.raises(ValueError, match="symmetric"):
            Ellipsoid(XtX)
