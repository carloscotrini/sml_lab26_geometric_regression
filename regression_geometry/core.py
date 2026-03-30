"""Core mathematical engine for the regression geometry course.

Provides classes for column space projection, hat matrix diagnostics,
and eigenvalue ellipsoid analysis. Pure computation — no visualization.

Dependencies: numpy, scipy, dataclasses (stdlib).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import scipy.linalg


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def angle_between(u: np.ndarray, v: np.ndarray) -> float:
    """Angle in radians between two vectors.

    Parameters
    ----------
    u, v : np.ndarray
        Vectors of the same shape.

    Returns
    -------
    float
        Angle in radians in [0, pi].

    Raises
    ------
    ValueError
        If vectors have different shapes.
    """
    u = np.asarray(u, dtype=float).ravel()
    v = np.asarray(v, dtype=float).ravel()
    if u.shape != v.shape:
        raise ValueError(f"Shape mismatch: u has shape {u.shape}, v has shape {v.shape}.")
    norm_u = np.linalg.norm(u)
    norm_v = np.linalg.norm(v)
    if norm_u < 1e-15 or norm_v < 1e-15:
        return 0.0
    cos_theta = np.clip(np.dot(u, v) / (norm_u * norm_v), -1.0, 1.0)
    return float(np.arccos(cos_theta))


def demean(v: np.ndarray) -> np.ndarray:
    """Subtract the mean from a vector.

    Parameters
    ----------
    v : np.ndarray, shape (n,)

    Returns
    -------
    np.ndarray, shape (n,)
    """
    v = np.asarray(v, dtype=float).ravel()
    return v - v.mean()


def frisch_waugh_lovell(X: np.ndarray, y: np.ndarray, j: int) -> dict:
    """Perform the Frisch-Waugh-Lovell decomposition for column j.

    Partitions X into x_j and X_{-j}, residualizes both y and x_j
    against X_{-j}, and returns the components.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
        Full design matrix (with intercept if desired).
    y : np.ndarray, shape (n,)
    j : int
        Column index to isolate (0-indexed).

    Returns
    -------
    dict with keys:
        'y_resid': residualized y (M_{-j} @ y)
        'xj_resid': residualized x_j (M_{-j} @ x_j)
        'beta_j': coefficient on x_j (should match full OLS)
        'residuals_full': residuals from the full regression
        'residuals_partial': residuals from the partial regression

    Raises
    ------
    ValueError
        If shapes are inconsistent or j is out of range.
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    if X.ndim != 2:
        raise ValueError(f"X must be 2D, got {X.ndim}D.")
    n, p = X.shape
    if y.shape[0] != n:
        raise ValueError(
            f"Expected y with shape ({n},), got ({y.shape[0]},)."
        )
    if j < 0 or j >= p:
        raise ValueError(f"Column index j={j} out of range [0, {p}).")

    xj = X[:, j]
    # X_{-j}: all columns except j
    cols = list(range(p))
    cols.remove(j)
    X_other = X[:, cols]

    # Residualize y and x_j against X_{-j}
    if X_other.shape[1] == 0:
        # No other columns — residuals are the vectors themselves
        y_resid = y.copy()
        xj_resid = xj.copy()
    else:
        coef_y, _, _, _ = np.linalg.lstsq(X_other, y, rcond=None)
        y_resid = y - X_other @ coef_y
        coef_xj, _, _, _ = np.linalg.lstsq(X_other, xj, rcond=None)
        xj_resid = xj - X_other @ coef_xj

    # beta_j from partial regression
    denom = np.dot(xj_resid, xj_resid)
    if denom < 1e-15:
        beta_j = 0.0
    else:
        beta_j = float(np.dot(xj_resid, y_resid) / denom)

    # Full regression residuals
    coef_full, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    residuals_full = y - X @ coef_full

    # Partial regression residuals
    residuals_partial = y_resid - xj_resid * beta_j

    return {
        "y_resid": y_resid,
        "xj_resid": xj_resid,
        "beta_j": beta_j,
        "residuals_full": residuals_full,
        "residuals_partial": residuals_partial,
    }


# ---------------------------------------------------------------------------
# Projection dataclass
# ---------------------------------------------------------------------------

@dataclass
class Projection:
    """Result of projecting y onto a column space.

    All attributes are computed at construction time and cached.
    This is a read-only data object.
    """

    y: np.ndarray               # Original response vector, shape (n,)
    y_hat: np.ndarray           # Projected (fitted) values, shape (n,)
    residuals: np.ndarray       # e = y - y_hat, shape (n,)
    coefficients: np.ndarray    # beta_hat, shape (p,)
    H: np.ndarray               # Hat matrix, shape (n, n)

    @property
    def theta(self) -> float:
        """Angle between y (demeaned) and y_hat (demeaned) in radians.

        Uses demeaned vectors so the angle corresponds to R².
        theta = arccos(sqrt(R²))

        Returns
        -------
        float
        """
        r2 = self.r_squared
        return float(np.arccos(np.clip(np.sqrt(r2), -1.0, 1.0)))

    @property
    def theta_degrees(self) -> float:
        """Angle in degrees.

        Returns
        -------
        float
        """
        return float(np.degrees(self.theta))

    @property
    def r_squared(self) -> float:
        """R² = cos²(theta) = SSR/SST.

        Computed from demeaned vectors. Returns 0.0 if SST == 0.

        Returns
        -------
        float
        """
        sst = self.sst
        if sst < 1e-15:
            return 0.0
        return float(np.clip(self.ssr / sst, 0.0, 1.0))

    @property
    def sst(self) -> float:
        """Total sum of squares: ||y - y_bar||².

        Returns
        -------
        float
        """
        y_dm = demean(self.y)
        return float(np.dot(y_dm, y_dm))

    @property
    def ssr(self) -> float:
        """Regression (explained) sum of squares: ||y_hat - y_bar||².

        Returns
        -------
        float
        """
        yhat_dm = demean(self.y_hat)
        return float(np.dot(yhat_dm, yhat_dm))

    @property
    def sse(self) -> float:
        """Residual sum of squares: ||e||².

        Returns
        -------
        float
        """
        return float(np.dot(self.residuals, self.residuals))

    @property
    def residual_norm(self) -> float:
        """||e|| = sqrt(SSE).

        Returns
        -------
        float
        """
        return float(np.sqrt(self.sse))

    @property
    def relative_residual_norm(self) -> float:
        """||e|| / ||y|| — used by the Geometric Scoreboard.

        Returns
        -------
        float
        """
        y_norm = np.linalg.norm(self.y)
        if y_norm < 1e-15:
            return 0.0
        return float(self.residual_norm / y_norm)

    def verify_pythagorean(self, tol: float = 1e-8) -> bool:
        """Check that SST = SSR + SSE within tolerance.

        Parameters
        ----------
        tol : float, default 1e-8

        Returns
        -------
        bool
        """
        return bool(abs(self.sst - (self.ssr + self.sse)) < tol * max(self.sst, 1.0))

    def verify_orthogonality(self, X: np.ndarray, tol: float = 1e-8) -> bool:
        """Check that X'e ≈ 0 within tolerance.

        Verifies the fundamental orthogonality condition.

        Parameters
        ----------
        X : np.ndarray, shape (n, p)
        tol : float, default 1e-8

        Returns
        -------
        bool
        """
        X = np.asarray(X, dtype=float)
        cross = X.T @ self.residuals
        return bool(np.all(np.abs(cross) < tol * max(np.linalg.norm(self.y), 1.0)))


# ---------------------------------------------------------------------------
# ColumnSpace
# ---------------------------------------------------------------------------

class ColumnSpace:
    """Represents the column space of a design matrix X.

    Handles intercept logic: if add_intercept=True (default), prepends
    a column of ones to X before computing. Stores both the original X
    and the augmented X internally.
    """

    def __init__(self, X: np.ndarray, add_intercept: bool = True):
        """
        Parameters
        ----------
        X : np.ndarray, shape (n, k) or (n,)
            Design matrix. If 1D, treated as a single predictor.
        add_intercept : bool, default True
            Whether to prepend a column of ones.

        Raises
        ------
        ValueError
            If X has fewer than 2 observations or has incompatible shape.
        """
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if X.ndim != 2:
            raise ValueError(f"X must be 1D or 2D, got {X.ndim}D.")
        if X.shape[0] < 2:
            raise ValueError(
                f"Need at least 2 observations, got {X.shape[0]}."
            )

        self._X_original = X.copy()
        self._add_intercept = add_intercept

        if add_intercept:
            ones = np.ones((X.shape[0], 1))
            self._X = np.hstack([ones, X])
        else:
            self._X = X.copy()

        # Warn if rank-deficient
        r = int(np.linalg.matrix_rank(self._X))
        if r < self._X.shape[1]:
            warnings.warn(
                f"Design matrix is rank-deficient: rank={r}, columns={self._X.shape[1]}. "
                f"Results may be unreliable.",
                stacklevel=2,
            )

    @property
    def X(self) -> np.ndarray:
        """The full design matrix (with intercept if added). Shape (n, p).

        Returns
        -------
        np.ndarray
        """
        return self._X

    @property
    def n(self) -> int:
        """Number of observations.

        Returns
        -------
        int
        """
        return self._X.shape[0]

    @property
    def p(self) -> int:
        """Number of columns in X (including intercept if added).

        Returns
        -------
        int
        """
        return self._X.shape[1]

    @property
    def rank(self) -> int:
        """Numerical rank of X.

        Returns
        -------
        int
        """
        return int(np.linalg.matrix_rank(self._X))

    def project(self, y: np.ndarray) -> Projection:
        """Project y onto the column space of X.

        Parameters
        ----------
        y : np.ndarray, shape (n,)

        Returns
        -------
        Projection
            Contains y_hat, residuals, hat matrix, angle, R², sums of squares.

        Raises
        ------
        ValueError
            If y.shape[0] != self.n
        """
        y = np.asarray(y, dtype=float).ravel()
        if y.shape[0] != self.n:
            raise ValueError(
                f"Expected y with shape ({self.n},), got ({y.shape[0]},). "
                f"Did you pass a column vector? Use y.ravel()."
            )
        X = self._X
        coefficients, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        y_hat = X @ coefficients
        residuals = y - y_hat
        H = self.hat_matrix()
        return Projection(
            y=y.copy(),
            y_hat=y_hat,
            residuals=residuals,
            coefficients=coefficients,
            H=H,
        )

    def residual(self, y: np.ndarray) -> np.ndarray:
        """Shortcut: returns (I - H)y. Shape (n,).

        Parameters
        ----------
        y : np.ndarray, shape (n,)

        Returns
        -------
        np.ndarray, shape (n,)

        Raises
        ------
        ValueError
            If y.shape[0] != self.n
        """
        y = np.asarray(y, dtype=float).ravel()
        if y.shape[0] != self.n:
            raise ValueError(
                f"Expected y with shape ({self.n},), got ({y.shape[0]},). "
                f"Did you pass a column vector? Use y.ravel()."
            )
        X = self._X
        coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
        return y - X @ coef

    def hat_matrix(self) -> np.ndarray:
        """Compute H = X(X'X)^{-1}X'. Shape (n, n).

        Uses scipy.linalg.lstsq internally for numerical stability.
        Does NOT compute (X'X)^{-1} explicitly via np.linalg.inv.

        Returns
        -------
        np.ndarray, shape (n, n)
        """
        X = self._X
        I_n = np.eye(self.n)
        C, _, _, _ = scipy.linalg.lstsq(X, I_n)
        H = X @ C
        return H

    def eigenvalues(self) -> np.ndarray:
        """Eigenvalues of X'X, sorted descending. Shape (p,).

        Returns
        -------
        np.ndarray
        """
        XtX = self._X.T @ self._X
        vals = np.linalg.eigvalsh(XtX)
        return np.sort(vals)[::-1]

    def eigenvectors(self) -> np.ndarray:
        """Eigenvectors of X'X as columns, matching eigenvalue order. Shape (p, p).

        Returns
        -------
        np.ndarray
        """
        XtX = self._X.T @ self._X
        vals, vecs = np.linalg.eigh(XtX)
        idx = np.argsort(vals)[::-1]
        return vecs[:, idx]

    def condition_number(self) -> float:
        """Ratio of largest to smallest eigenvalue of X'X.

        If smallest eigenvalue < 1e-12, return np.inf.

        Returns
        -------
        float
        """
        evals = self.eigenvalues()
        if evals[-1] < 1e-12:
            return np.inf
        return float(evals[0] / evals[-1])

    def relevant_triangle(self, y: np.ndarray, j: int) -> dict:
        """Extract the 2D plane relevant to the j-th coefficient.

        Implements the Relevant Triangle principle (SPEC.md §6.2):
        residualizes y and x_j against all other columns, then returns
        the two residualized vectors (which live in a 2D plane).

        Parameters
        ----------
        y : np.ndarray, shape (n,)
        j : int
            Column index in self.X (0-indexed, counting intercept if present).

        Returns
        -------
        dict with keys:
            'y_resid': np.ndarray — y residualized against X_{-j}
            'xj_resid': np.ndarray — x_j residualized against X_{-j}
            'beta_j': float — the j-th coefficient (= slope of y_resid on xj_resid)
            'se_j': float — standard error of beta_j
            'angle': float — angle in radians between y_resid and xj_resid

        Raises
        ------
        ValueError
            If y shape or j index is invalid.
        """
        y = np.asarray(y, dtype=float).ravel()
        if y.shape[0] != self.n:
            raise ValueError(
                f"Expected y with shape ({self.n},), got ({y.shape[0]},)."
            )
        if j < 0 or j >= self.p:
            raise ValueError(f"Column index j={j} out of range [0, {self.p}).")

        fwl = frisch_waugh_lovell(self._X, y, j)
        y_resid = fwl["y_resid"]
        xj_resid = fwl["xj_resid"]
        beta_j = fwl["beta_j"]

        # Standard error: se(beta_j) = sqrt(s² / ||xj_resid||²)
        # where s² = ||y_resid - beta_j * xj_resid||² / (n - p)
        partial_resid = y_resid - beta_j * xj_resid
        df = self.n - self.p
        if df > 0:
            s2 = float(np.dot(partial_resid, partial_resid) / df)
        else:
            s2 = 0.0
        xj_norm_sq = float(np.dot(xj_resid, xj_resid))
        if xj_norm_sq < 1e-15:
            se_j = np.inf
        else:
            se_j = float(np.sqrt(s2 / xj_norm_sq))

        ang = angle_between(y_resid, xj_resid)

        return {
            "y_resid": y_resid,
            "xj_resid": xj_resid,
            "beta_j": beta_j,
            "se_j": se_j,
            "angle": ang,
        }

    def orthogonal_complement(self) -> np.ndarray:
        """Compute M = I - H, the annihilator matrix. Shape (n, n).

        Returns
        -------
        np.ndarray, shape (n, n)
        """
        return np.eye(self.n) - self.hat_matrix()

    def basis(self) -> np.ndarray:
        """Orthonormal basis for C(X) via QR decomposition. Shape (n, r).

        Where r = rank(X). Returns the first r columns of Q.

        Returns
        -------
        np.ndarray
        """
        Q, R = np.linalg.qr(self._X, mode="reduced")
        r = self.rank
        return Q[:, :r]


# ---------------------------------------------------------------------------
# HatMatrix
# ---------------------------------------------------------------------------

class HatMatrix:
    """Wrapper around the hat matrix H with diagnostic methods."""

    def __init__(self, H: np.ndarray):
        """
        Parameters
        ----------
        H : np.ndarray, shape (n, n)
            Must be symmetric and idempotent (within tolerance).

        Raises
        ------
        ValueError
            If H is not square.
        """
        H = np.asarray(H, dtype=float)
        if H.ndim != 2 or H.shape[0] != H.shape[1]:
            raise ValueError(f"H must be square, got shape {H.shape}.")
        self._H = H

    @property
    def matrix(self) -> np.ndarray:
        """The raw H matrix.

        Returns
        -------
        np.ndarray
        """
        return self._H

    def diagonal(self) -> np.ndarray:
        """Leverage values h_ii. Shape (n,).

        Returns
        -------
        np.ndarray
        """
        return np.diag(self._H)

    def trace(self) -> float:
        """tr(H) = sum of leverages = p (number of parameters).

        Returns
        -------
        float
        """
        return float(np.trace(self._H))

    def average_leverage(self) -> float:
        """tr(H) / n = p/n.

        Returns
        -------
        float
        """
        n = self._H.shape[0]
        return float(self.trace() / n)

    def high_leverage_mask(self, threshold: float = None) -> np.ndarray:
        """Boolean mask for high-leverage observations.

        Default threshold: 2 * tr(H) / n (standard rule of thumb: 2p/n).

        Parameters
        ----------
        threshold : float, optional

        Returns
        -------
        np.ndarray, shape (n,), dtype bool
        """
        h = self.diagonal()
        if threshold is None:
            threshold = 2.0 * self.average_leverage()
        return h > threshold

    def cooks_distance(self, residuals: np.ndarray, mse: float, p: int) -> np.ndarray:
        """Cook's distance for each observation.

        D_i = (e_i² / (p * MSE)) * (h_ii / (1 - h_ii)²)

        Parameters
        ----------
        residuals : np.ndarray, shape (n,)
        mse : float
            Mean squared error (SSE / (n-p)).
        p : int
            Number of parameters.

        Returns
        -------
        np.ndarray, shape (n,)
            Cook's D for each observation.

        Raises
        ------
        ValueError
            If residuals shape doesn't match H.
        """
        residuals = np.asarray(residuals, dtype=float).ravel()
        n = self._H.shape[0]
        if residuals.shape[0] != n:
            raise ValueError(
                f"Expected residuals with shape ({n},), got ({residuals.shape[0]},)."
            )
        h = self.diagonal()
        if mse < 1e-15:
            return np.full(n, np.inf)
        denom = (1.0 - h) ** 2
        denom = np.where(denom < 1e-15, 1e-15, denom)
        D = (residuals ** 2 / (p * mse)) * (h / denom)
        return D

    def verify_idempotent(self, tol: float = 1e-8) -> bool:
        """Check H² ≈ H.

        Parameters
        ----------
        tol : float, default 1e-8

        Returns
        -------
        bool
        """
        H2 = self._H @ self._H
        return bool(np.allclose(H2, self._H, atol=tol))

    def verify_symmetric(self, tol: float = 1e-8) -> bool:
        """Check H' ≈ H.

        Parameters
        ----------
        tol : float, default 1e-8

        Returns
        -------
        bool
        """
        return bool(np.allclose(self._H, self._H.T, atol=tol))


# ---------------------------------------------------------------------------
# Ellipsoid
# ---------------------------------------------------------------------------

class Ellipsoid:
    """Represents the eigenvalue ellipsoid of X'X.

    Used to visualize multicollinearity: the ellipsoid's axis lengths
    are proportional to eigenvalues. A thin ellipsoid = near-collinear.
    """

    def __init__(self, XtX: np.ndarray):
        """
        Parameters
        ----------
        XtX : np.ndarray, shape (p, p)
            The X'X matrix. Must be symmetric positive semi-definite.

        Raises
        ------
        ValueError
            If XtX is not square or not symmetric.
        """
        XtX = np.asarray(XtX, dtype=float)
        if XtX.ndim != 2 or XtX.shape[0] != XtX.shape[1]:
            raise ValueError(f"XtX must be square, got shape {XtX.shape}.")
        if not np.allclose(XtX, XtX.T, atol=1e-10):
            raise ValueError("XtX must be symmetric.")

        vals, vecs = np.linalg.eigh(XtX)
        idx = np.argsort(vals)[::-1]
        self._eigenvalues = vals[idx]
        self._eigenvectors = vecs[:, idx]

    @property
    def eigenvalues(self) -> np.ndarray:
        """Eigenvalues sorted descending.

        Returns
        -------
        np.ndarray
        """
        return self._eigenvalues.copy()

    @property
    def eigenvectors(self) -> np.ndarray:
        """Eigenvectors as columns, matching eigenvalue order.

        Returns
        -------
        np.ndarray
        """
        return self._eigenvectors.copy()

    @property
    def axis_lengths(self) -> np.ndarray:
        """Semi-axis lengths of the ellipsoid = sqrt(eigenvalues).

        Returns
        -------
        np.ndarray
        """
        return np.sqrt(np.maximum(self._eigenvalues, 0.0))

    @property
    def condition_number(self) -> float:
        """max(eigenvalue) / min(eigenvalue). np.inf if degenerate.

        Returns
        -------
        float
        """
        if self._eigenvalues[-1] < 1e-12:
            return np.inf
        return float(self._eigenvalues[0] / self._eigenvalues[-1])

    def shrinkage_factors(self, lam: float) -> np.ndarray:
        """Ridge shrinkage factors: lambda_k / (lambda_k + lam) for each eigenvalue.

        Used in Notebook 7 to show how Ridge shrinks each component.

        Parameters
        ----------
        lam : float
            Ridge penalty parameter (lambda >= 0).

        Returns
        -------
        np.ndarray, shape (p,)

        Raises
        ------
        ValueError
            If lam < 0.
        """
        if lam < 0:
            raise ValueError(f"Ridge penalty lam must be >= 0, got {lam}.")
        return self._eigenvalues / (self._eigenvalues + lam)

    def ridge_coefficients(self, beta_ols: np.ndarray, lam: float) -> np.ndarray:
        """Compute Ridge coefficients via eigendecomposition.

        beta_ridge = Q @ diag(lambda_k / (lambda_k + lam)) @ Q' @ beta_ols

        Parameters
        ----------
        beta_ols : np.ndarray, shape (p,)
            OLS coefficients.
        lam : float
            Ridge penalty parameter.

        Returns
        -------
        np.ndarray, shape (p,)

        Raises
        ------
        ValueError
            If beta_ols shape doesn't match or lam < 0.
        """
        beta_ols = np.asarray(beta_ols, dtype=float).ravel()
        if beta_ols.shape[0] != self._eigenvectors.shape[0]:
            raise ValueError(
                f"beta_ols has shape ({beta_ols.shape[0]},), "
                f"expected ({self._eigenvectors.shape[0]},)."
            )
        if lam < 0:
            raise ValueError(f"Ridge penalty lam must be >= 0, got {lam}.")
        sf = self.shrinkage_factors(lam)
        Q = self._eigenvectors
        return Q @ (sf * (Q.T @ beta_ols))
