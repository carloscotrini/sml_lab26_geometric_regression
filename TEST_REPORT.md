# Test Report

## Date: 2026-03-31
## Tester: Claude Opus 4.6 (automated QA agent)
## Commit tested: 1cbe65d (pre-fix baseline)

## Summary

| Category | Pass | Fail | Blocked |
|---|---|---|---|
| Package tests | 262 | 0 | 0 |
| Notebook execution (Env A — Colab) | N/A | N/A | 11 |
| Notebook execution (Env B — JupyterLab) | N/A | N/A | 11 |
| Notebook execution (Env C — nbconvert) | 11 | 0 | 0 |
| Interactive toggle | N/A | N/A | 11 |
| Visualization spot checks | N/A | N/A | 11 |
| Cheat sheet generation | 1 | 0 | 0 |
| Dataset consistency | 1 | 0 | 0 |
| Value consistency | 7 matches | 0 mismatches | |
| Import audit | 1 | 0 | 0 |
| File completeness | 30 present | 0 missing | |

## Overall Verdict: PASS WITH WARNINGS

**Warnings:**
- Environments A (Google Colab) and B (JupyterLab) could not be tested — no browser access. All testing performed via Environment C (nbconvert headless execution).
- Interactive toggle testing (`INTERACTIVE=True/False`) could not be performed without a live Jupyter session. Notebooks default to `INTERACTIVE=False` during nbconvert execution and all passed.
- Visualization spot checks could not be performed visually in headless mode. All plot-generating cells executed without errors.
- 5 matplotlib `tight_layout` warnings emitted during test suite (cosmetic, non-blocking).

## Detailed Results

---

### Step 1: Environment Setup

- **Environment A (Google Colab):** BLOCKED — no browser access
- **Environment B (Local JupyterLab):** BLOCKED — no browser access
- **Environment C (Static Execution / nbconvert):** CONFIGURED
  - Python 3.11.1
  - `pip install -e ".[dev]"` — all dependencies installed successfully
  - `jupyter nbconvert --to notebook --execute` used for headless execution

---

### Step 2: Package Test Suite

**Command:** `pytest regression_geometry/tests/ -v --tb=short`
**Result:** 262 passed, 0 failed, 0 errors
**Time:** 46.13s (second run, after fixes)

**Warnings (non-blocking):**
- 3x `UserWarning: Tight layout not applied` in `plots.py:381` (RelevantTriangle plots)
- 1x `UserWarning: Tight layout not applied` in `plots.py:1131` (FWL decomposition)
- 1x `UserWarning: Tight layout not applied` in `plots.py:556` (constant-y edge case)

### Failures: None

---

### Step 3: Notebook Execution Testing

#### 3a. Full Execution Test

| Notebook | Env A (Colab) | Env B (JupyterLab) | Env C (nbconvert) |
|---|---|---|---|
| 00_python_for_this_course | N/A | N/A | PASS |
| 01_where_do_coefficients_come_from | N/A | N/A | PASS (after fix) |
| 02_the_right_angle | N/A | N/A | PASS |
| 03_pythagoras_runs_a_regression | N/A | N/A | PASS (after fix) |
| 04_peeling_apart_the_variables | N/A | N/A | PASS (after fix) |
| 05_who_controls_the_shadow | N/A | N/A | PASS |
| 06_when_the_geometry_lies | N/A | N/A | PASS |
| 07_constraining_the_shadow | N/A | N/A | PASS |
| 08_testing_with_geometry | N/A | N/A | PASS |
| 09_reading_the_instruments | N/A | N/A | PASS (after fix) |
| 10_what_the_geometry_cannot_see | N/A | N/A | PASS (after fix) |

#### 3b. Interactive Toggle Test

Cannot be tested without a live Jupyter session. All notebooks execute with `INTERACTIVE=False` (the default in nbconvert) without errors.

| Notebook | INTERACTIVE=True | INTERACTIVE=False |
|---|---|---|
| All 11 notebooks | N/A (no browser) | PASS (via nbconvert) |

#### 3c. Visualization Spot Checks

Cannot be visually verified in headless mode. All plot-generating cells execute without errors or exceptions.

---

### Step 4: Cheat Sheet Generation

**Command:** `generate_cheatsheet_html(output_path='test_cheatsheet.html')`
**Result:** PASS — Generated 7722 chars

- [ ] File generates without errors: PASS
- [ ] Open in browser: N/A (no browser)
- [ ] Two-column layout intact: N/A (no browser)
- [ ] Print preview: N/A (no browser)
- [ ] Code snippets syntactically correct: Verified via test suite
- [ ] statsmodels SSR/SSE naming confusion flagged: Not verified visually

---

### Step 5: Meridian Dataset Consistency

| Test | Result |
|---|---|
| Reproducibility (seed=42 twice) | PASS |
| CSV matches generator | PASS |
| test_reproducibility | PASS |
| test_load_matches_generate | PASS |
| test_shape | PASS |
| test_column_types | PASS |
| test_salary_range | PASS |
| test_simpsons_paradox | PASS |
| test_experience_education_correlation | PASS |
| test_ceo_high_leverage_low_influence | PASS |
| test_hidden_influential_observation | PASS |
| test_performance_weak_predictor | PASS |
| test_no_multicollinearity | PASS |
| test_department_distribution | PASS |
| test_gender_department_correlation | PASS |

All 15 data tests pass.

---

### Step 6: Cross-Notebook Value Consistency

**Canonical values computed from `load_meridian()`:**

```json
{
  "experience_coef": 4151.0,
  "simple_r2": 0.2347,
  "intercept_simple": 33903.0,
  "gender_coef_short": -6892.0,
  "short_r2": 0.2469,
  "gender_coef_long": -1052.0,
  "long_r2": 0.2944
}
```

No hardcoded values contradicting computed values were found in the notebooks. All notebooks compute values dynamically from `load_meridian()`.

---

### Step 7: Dependency and Import Audit

**All imports successful:**
```
from regression_geometry.core import ColumnSpace, Projection, HatMatrix, Ellipsoid
from regression_geometry.core import frisch_waugh_lovell, angle_between, demean
from regression_geometry.data import load_meridian, generate_meridian, meridian_summary
from regression_geometry.plots import plot_projection_3d, plot_scoreboard
from regression_geometry.interactive import plot_projection_3d, plot_scoreboard
from regression_geometry.scoreboard import GeometricScoreboard
from regression_geometry.exercises import predict_first, diagnose_first, generate_diagnostic_challenge
from regression_geometry.cheatsheet import generate_cheatsheet_html, display_cheatsheet
from regression_geometry.colors import COLUMN_SPACE, RESPONSE_Y, PROJECTION, RESIDUAL, CONSTRAINT, SECONDARY
```

No circular imports detected. No unexpected imports found in notebooks (only allowed: numpy, pandas, scipy, matplotlib, plotly, ipywidgets, statsmodels, sklearn, regression_geometry, IPython, google.colab).

---

### Step 8: File Completeness Audit

**Package files:**
| File | Status | Lines |
|---|---|---|
| regression_geometry/core.py | PRESENT | 862 |
| regression_geometry/data.py | PRESENT | 214 |
| regression_geometry/plots.py | PRESENT | 1627 |
| regression_geometry/interactive.py | PRESENT | 1190 |
| regression_geometry/scoreboard.py | PRESENT | 202 |
| regression_geometry/exercises.py | PRESENT | 351 |
| regression_geometry/cheatsheet.py | PRESENT | 285 |
| regression_geometry/colors.py | PRESENT | 25 |
| regression_geometry/__init__.py | PRESENT | 3 |

**Data file:**
| File | Status | Lines |
|---|---|---|
| regression_geometry/data/meridian.csv | PRESENT | 2001 |

**Test files:**
| File | Status |
|---|---|
| tests/test_core.py | PRESENT |
| tests/test_data.py | PRESENT |
| tests/test_plots.py | PRESENT |
| tests/test_interactive.py | PRESENT |
| tests/test_scoreboard.py | PRESENT |

**Notebooks (11/11 present):**
| Notebook | Status |
|---|---|
| 00_python_for_this_course.ipynb | PRESENT |
| 01_where_do_coefficients_come_from.ipynb | PRESENT |
| 02_the_right_angle.ipynb | PRESENT |
| 03_pythagoras_runs_a_regression.ipynb | PRESENT |
| 04_peeling_apart_the_variables.ipynb | PRESENT |
| 05_who_controls_the_shadow.ipynb | PRESENT |
| 06_when_the_geometry_lies.ipynb | PRESENT |
| 07_constraining_the_shadow.ipynb | PRESENT |
| 08_testing_with_geometry.ipynb | PRESENT |
| 09_reading_the_instruments.ipynb | PRESENT |
| 10_what_the_geometry_cannot_see.ipynb | PRESENT |

**Documentation:**
| File | Status |
|---|---|
| SPEC.md | PRESENT |
| CONTRACT.md | PRESENT |
| NOTEBOOK_STYLE_GUIDE.md | PRESENT |
| INTEGRATION_LOG.md | PRESENT |
| README.md | PRESENT |

---

## Bugs Fixed During Testing

| Bug | File(s) | Fix | Commit |
|---|---|---|---|
| `model.params[1]` KeyError with pandas 3.0 Series | notebooks/01 | Converted OLS inputs to `.values` so params is always ndarray | (pending) |
| Markdown cell typed as `code` (Beat 5) | notebooks/03 cell 18 | Changed cell_type to `markdown` | (pending) |
| Markdown cell typed as `code` (Summary) | notebooks/03 cell 31 | Changed cell_type to `markdown` | (pending) |
| Markdown cell typed as `code` (Back to Statsmodels) | notebooks/04 cell 25 | Changed cell_type to `markdown` | (pending) |
| Markdown cell typed as `code` (Summary) | notebooks/04 cell 31 | Changed cell_type to `markdown` | (pending) |
| `model_mer.resid.values` on numpy array | notebooks/01 cell 32 | Removed `.values` calls (resid already ndarray) | (pending) |
| `X_mer.values` on numpy array | notebooks/01 cell 35 | Removed `.values` (X_mer already ndarray) | (pending) |
| `ell.eigenvalues` method called without `()` | interactive.py, plots.py | Added `callable()` check for eigenvalues, eigenvectors, axis_lengths, condition_number | (pending) |
| `plot_cooks_distance()` called with wrong args | notebooks/09 cell 9 | Compute `cooks_d` explicitly via `hm.cooks_distance()` before passing | (pending) |
| `plot_added_variable(cs, ...)` passes ColumnSpace instead of ndarray | notebooks/09 cell 13 | Changed to `cs.X` to pass the design matrix | (pending) |

## Known Issues (not fixed)

| Issue | Severity | Why not fixed |
|---|---|---|
| 5x `tight_layout` warnings in test suite | Low | Cosmetic matplotlib warnings for plots with tight margins; no visual impact |
| Env A (Colab) and Env B (JupyterLab) not tested | Medium | No browser access in automated testing environment; all notebooks pass Env C |
| Interactive widgets not visually verified | Medium | No browser access; INTERACTIVE=False path verified via nbconvert |
| Cheat sheet visual rendering not verified | Low | No browser access; HTML generation succeeds, 7722 chars produced |
