# CONTRACT.md — Public API for `regression_geometry.core`

**Version:** 1.0
**Status:** Ratified — all downstream modules (`plots.py`, `interactive.py`, `scoreboard.py`) and all notebooks (0–10) program against this contract. Changes are extremely expensive.

---

## Dependencies

`regression_geometry.core` uses **only**:
- `numpy` (>=1.24)
- `scipy` (>=1.11)
- `dataclasses` (stdlib)

No visualization imports (matplotlib, plotly, ipywidgets) are permitted.

---

## Class 1: `ColumnSpace`

```python
class ColumnSpace:
    """Represents the column space of a design matrix X."""

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
            If X has fewer than 2 observations.
        UserWarning
            If X is rank-deficient.
        """

    @property
    def X(self) -> np.ndarray:
        """The full design matrix (with intercept if added). Shape (n, p)."""

    @property
    def n(self) -> int:
        """Number of observations."""

    @property
    def p(self) -> int:
        """Number of columns in X (including intercept if added)."""

    @property
    def rank(self) -> int:
        """Numerical rank of X."""

    def project(self, y: np.ndarray) -> 'Projection':
        """Project y onto the column space of X.

        Parameters
        ----------
        y : np.ndarray, shape (n,)

        Returns
        -------
        Projection

        Raises
        ------
        ValueError
            If y.shape[0] != self.n
        """

    def residual(self, y: np.ndarray) -> np.ndarray:
        """Shortcut: returns (I - H)y. Shape (n,).

        Raises
        ------
        ValueError
            If y.shape[0] != self.n
        """

    def hat_matrix(self) -> np.ndarray:
        """Compute H = X(X'X)^{-1}X'. Shape (n, n).

        Uses scipy.linalg.lstsq internally for numerical stability.
        Never computes np.linalg.inv(X'X).
        """

    def eigenvalues(self) -> np.ndarray:
        """Eigenvalues of X'X, sorted descending. Shape (p,).

        Guarantee: always sorted in descending order.
        Uses np.linalg.eigvalsh (symmetric eigenvalue solver).
        """

    def eigenvectors(self) -> np.ndarray:
        """Eigenvectors of X'X as columns, matching eigenvalue order. Shape (p, p).

        Guarantee: column order matches eigenvalues() order (descending).
        """

    def condition_number(self) -> float:
        """Ratio of largest to smallest eigenvalue of X'X.

        Guarantee: returns np.inf if smallest eigenvalue < 1e-12.
        """

    def relevant_triangle(self, y: np.ndarray, j: int) -> dict:
        """Extract the 2D plane relevant to the j-th coefficient.

        Parameters
        ----------
        y : np.ndarray, shape (n,)
        j : int — column index in self.X (0-indexed, counting intercept if present).

        Returns
        -------
        dict with keys:
            'y_resid': np.ndarray — y residualized against X_{-j}
            'xj_resid': np.ndarray — x_j residualized against X_{-j}
            'beta_j': float — the j-th coefficient (matches full OLS)
            'se_j': float — standard error of beta_j
            'angle': float — angle in radians between y_resid and xj_resid

        Raises
        ------
        ValueError
            If y shape or j index is invalid.
        """

    def orthogonal_complement(self) -> np.ndarray:
        """Compute M = I - H, the annihilator matrix. Shape (n, n)."""

    def basis(self) -> np.ndarray:
        """Orthonormal basis for C(X) via QR decomposition. Shape (n, r)
        where r = rank(X)."""
```

### Behavioral Guarantees — ColumnSpace

- If `add_intercept=True`, a column of ones is **prepended** (leftmost column).
- `eigenvalues()` are **always sorted descending**.
- `eigenvectors()` columns match the eigenvalue ordering.
- `hat_matrix()` uses `scipy.linalg.lstsq` — never `np.linalg.inv(X.T @ X)`.
- `condition_number()` returns `np.inf` when smallest eigenvalue < 1e-12.
- `relevant_triangle()` uses `frisch_waugh_lovell()` internally; `beta_j` matches the j-th coefficient from full OLS.
- Constructor **warns** (does not crash) on rank-deficient X.
- Constructor **raises ValueError** on fewer than 2 observations.

---

## Class 2: `Projection` (dataclass)

```python
@dataclass
class Projection:
    """Result of projecting y onto a column space. Read-only data object."""

    y: np.ndarray           # Original response vector, shape (n,)
    y_hat: np.ndarray       # Projected (fitted) values, shape (n,)
    residuals: np.ndarray   # e = y - y_hat, shape (n,)
    coefficients: np.ndarray  # beta_hat, shape (p,)
    H: np.ndarray           # Hat matrix, shape (n, n)

    @property
    def theta(self) -> float:
        """Angle between y (demeaned) and y_hat (demeaned) in radians.
        theta = arccos(sqrt(R²))"""

    @property
    def theta_degrees(self) -> float:
        """Angle in degrees."""

    @property
    def r_squared(self) -> float:
        """R² = SSR/SST. Returns 0.0 if SST == 0."""

    @property
    def sst(self) -> float:
        """Total sum of squares: ||y - y_bar||²"""

    @property
    def ssr(self) -> float:
        """Regression (explained) sum of squares: ||y_hat - y_bar||²"""

    @property
    def sse(self) -> float:
        """Residual sum of squares: ||e||²"""

    @property
    def residual_norm(self) -> float:
        """||e|| = sqrt(SSE)"""

    @property
    def relative_residual_norm(self) -> float:
        """||e|| / ||y|| — used by the Geometric Scoreboard."""

    def verify_pythagorean(self, tol: float = 1e-8) -> bool:
        """Check that SST = SSR + SSE within tolerance."""

    def verify_orthogonality(self, X: np.ndarray, tol: float = 1e-8) -> bool:
        """Check that X'e ≈ 0 within tolerance."""
```

### Behavioral Guarantees — Projection

- `r_squared` returns **0.0** (not NaN) when SST == 0 (constant y).
- `r_squared` is **clipped to [0, 1]** for numerical safety.
- `theta` is computed as `arccos(sqrt(R²))` using demeaned vectors.
- `verify_pythagorean()` checks `|SST - (SSR + SSE)| < tol * max(SST, 1.0)`.
- `verify_orthogonality()` checks `|X'e| < tol * max(||y||, 1.0)` element-wise.
- All sums of squares use demeaned vectors (SST = ||y - ȳ||², SSR = ||ŷ - ȳ||²).

---

## Class 3: `HatMatrix`

```python
class HatMatrix:
    """Wrapper around the hat matrix H with diagnostic methods."""

    def __init__(self, H: np.ndarray):
        """
        Parameters
        ----------
        H : np.ndarray, shape (n, n) — must be square.
        """

    @property
    def matrix(self) -> np.ndarray:
        """The raw H matrix."""

    def diagonal(self) -> np.ndarray:
        """Leverage values h_ii. Shape (n,)."""

    def trace(self) -> float:
        """tr(H) = sum of leverages = p."""

    def average_leverage(self) -> float:
        """tr(H) / n = p/n."""

    def high_leverage_mask(self, threshold: float = None) -> np.ndarray:
        """Boolean mask for high-leverage observations.
        Default threshold: 2 * tr(H) / n."""

    def cooks_distance(self, residuals: np.ndarray, mse: float, p: int) -> np.ndarray:
        """Cook's distance for each observation.
        D_i = (e_i² / (p * MSE)) * (h_ii / (1 - h_ii)²)

        Parameters
        ----------
        residuals : np.ndarray, shape (n,)
        mse : float — mean squared error (SSE / (n-p))
        p : int — number of parameters

        Returns
        -------
        np.ndarray, shape (n,)
        """

    def verify_idempotent(self, tol: float = 1e-8) -> bool:
        """Check H² ≈ H."""

    def verify_symmetric(self, tol: float = 1e-8) -> bool:
        """Check H' ≈ H."""
```

### Behavioral Guarantees — HatMatrix

- `trace()` equals p (number of parameters) for a valid projection matrix.
- `high_leverage_mask()` default threshold is `2 * tr(H) / n` (standard 2p/n rule).
- `cooks_distance()` returns `np.inf` array when MSE < 1e-15.
- Division by zero in `(1 - h_ii)²` is protected (clamped to 1e-15).

---

## Class 4: `Ellipsoid`

```python
class Ellipsoid:
    """Represents the eigenvalue ellipsoid of X'X."""

    def __init__(self, XtX: np.ndarray):
        """
        Parameters
        ----------
        XtX : np.ndarray, shape (p, p) — must be symmetric.

        Raises
        ------
        ValueError
            If XtX is not square or not symmetric.
        """

    @property
    def eigenvalues(self) -> np.ndarray:
        """Eigenvalues sorted descending."""

    @property
    def eigenvectors(self) -> np.ndarray:
        """Eigenvectors as columns, matching eigenvalue order."""

    @property
    def axis_lengths(self) -> np.ndarray:
        """Semi-axis lengths = sqrt(eigenvalues)."""

    @property
    def condition_number(self) -> float:
        """max(eigenvalue) / min(eigenvalue). np.inf if degenerate."""

    def shrinkage_factors(self, lam: float) -> np.ndarray:
        """Ridge shrinkage factors: lambda_k / (lambda_k + lam).

        Raises
        ------
        ValueError
            If lam < 0.
        """

    def ridge_coefficients(self, beta_ols: np.ndarray, lam: float) -> np.ndarray:
        """Ridge coefficients via eigendecomposition.
        beta_ridge = Q @ diag(lambda_k / (lambda_k + lam)) @ Q' @ beta_ols

        Raises
        ------
        ValueError
            If beta_ols shape mismatch or lam < 0.
        """
```

### Behavioral Guarantees — Ellipsoid

- Eigenvalues are **always sorted descending**.
- `axis_lengths` clamps negative eigenvalues to 0 before taking sqrt.
- `condition_number` returns `np.inf` when min eigenvalue < 1e-12.
- `shrinkage_factors(0.0)` returns all ones (no shrinkage).
- `ridge_coefficients(beta_ols, 0.0)` returns `beta_ols` unchanged.

---

## Utility Functions

```python
def frisch_waugh_lovell(X: np.ndarray, y: np.ndarray, j: int) -> dict:
    """Frisch-Waugh-Lovell decomposition for column j.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    j : int — column index

    Returns
    -------
    dict with keys:
        'y_resid', 'xj_resid', 'beta_j', 'residuals_full', 'residuals_partial'

    Guarantee: beta_j matches the j-th coefficient from full OLS.
    """

def angle_between(u: np.ndarray, v: np.ndarray) -> float:
    """Angle in radians between two vectors.
    Returns 0.0 if either vector is zero (norm < 1e-15)."""

def demean(v: np.ndarray) -> np.ndarray:
    """Subtract the mean from a vector."""
```

---

## Color System (from SPEC.md §10.1)

These colors are **inviolable**. Every visualization must use this palette:

| Element | Color | Hex | Usage |
|---|---|---|---|
| Column space | Blue | `#3B82F6` | Planes, subspaces, basis vectors |
| Response vector y | Gold | `#F59E0B` | The data vector, always prominent |
| Projection ŷ | Green | `#10B981` | Fitted values, shadow on the wall |
| Residuals e | Red | `#EF4444` | Error vectors, residual bars |
| Constraints | Purple | `#8B5CF6` | Regularization boundaries, L1/L2 balls |
| Secondary | Gray | `#6B7280` | Axes, labels, grids, annotations |

Python constants for downstream use:

```python
COLORS = {
    "column_space": "#3B82F6",
    "y": "#F59E0B",
    "y_hat": "#10B981",
    "residuals": "#EF4444",
    "constraints": "#8B5CF6",
    "secondary": "#6B7280",
}
```

---

## Geometric Scoreboard Quantities (from SPEC.md §6.5)

The Scoreboard displays five gauges. The `core` module provides the raw values; `scoreboard.py` handles display and color-coding.

| Gauge | Quantity | Source | Green | Yellow | Red |
|---|---|---|---|---|---|
| θ | Angle between y and ŷ | `proj.theta_degrees` | < 45° | 45°–70° | > 70° |
| κ | Condition number of X'X | `cs.condition_number()` | < 30 | 30–100 | > 100 |
| tr(H)/n | Average leverage | `HatMatrix(proj.H).average_leverage()` | Informational (= p/n) | — | — |
| ‖e‖/‖y‖ | Relative residual norm | `proj.relative_residual_norm` | < 0.5 | 0.5–0.8 | > 0.8 |
| R² | Coefficient of determination | `proj.r_squared` | Displayed alongside θ | — | — |

---

## Usage Example

```python
import numpy as np
from regression_geometry.core import ColumnSpace, HatMatrix, Ellipsoid

# Generate some data
np.random.seed(42)
n, k = 100, 3
X = np.random.randn(n, k)
beta_true = np.array([2.0, -1.0, 0.5])
y = X @ beta_true + np.random.randn(n) * 0.5

# Create column space (auto-adds intercept)
cs = ColumnSpace(X)

# Project y onto C(X)
proj = cs.project(y)
print(proj.r_squared)           # R²
print(proj.theta_degrees)       # angle in degrees
print(proj.verify_pythagorean())  # True

# Hat matrix diagnostics
hm = HatMatrix(proj.H)
print(hm.diagonal())            # leverage values
mse = proj.sse / (cs.n - cs.p)
print(hm.cooks_distance(proj.residuals, mse, cs.p))

# Eigenvalue ellipsoid
ell = Ellipsoid(cs.X.T @ cs.X)
print(ell.condition_number)
print(ell.shrinkage_factors(lam=1.0))

# Frisch-Waugh-Lovell
rt = cs.relevant_triangle(y, j=1)
print(rt['beta_j'])              # matches proj.coefficients[1]
```

---

## Numerical Stability Rules

1. **Never** use `np.linalg.inv(X.T @ X)`. Always solve via `lstsq`.
2. Use `np.linalg.eigh` (not `eig`) for symmetric matrices (X'X).
3. Use `np.linalg.eigvalsh` when only eigenvalues are needed.
4. Clip `cos(theta)` to [-1, 1] before `arccos` to avoid NaN.
5. Return `0.0` for R² when SST < 1e-15 (constant y).
6. Return `np.inf` for condition number when min eigenvalue < 1e-12.
