# Integration Log — Issue 10: Integration Pass

All changes below enforce cross-notebook consistency per SPEC.md, NOTEBOOK_STYLE_GUIDE.md, CONTRACT.md, and COLAB_SETUP.md. No content was rewritten; only structural inconsistencies were patched.

---

## Package Review

All eight package modules reviewed. **No changes needed.**

| Module | Status | Notes |
|---|---|---|
| `colors.py` | OK | All 6 hex values + SURFACE_ALPHA match SPEC §10.1 |
| `core.py` | OK | API matches CONTRACT.md (ColumnSpace, Projection, HatMatrix, Ellipsoid, frisch_waugh_lovell, angle_between, demean) |
| `data.py` | OK | Seed=42, 2000 rows, CEO outlier index 0, hidden influential index 1 |
| `plots.py` | OK | 18 public functions, uses `colors` module |
| `interactive.py` | OK | 18 shared + 5 interactive-only functions, signature parity with plots.py |
| `scoreboard.py` | OK | ALL_GAUGES = ["theta", "kappa", "leverage", "residual_norm", "r_squared"], thresholds match SPEC |
| `exercises.py` | OK | Three difficulty levels (easy/medium/hard), predict_first/diagnose_first/memo/reveal |
| `cheatsheet.py` | OK | 11 entries, correctly flags statsmodels SSR/SSE naming confusion |

---

## Notebook Changes

### Nb 00 — `00_python_for_this_course.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `setup` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance |

### Nb 01 — `01_where_do_coefficients_come_from.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `setup` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance |

### Nb 02 — `02_the_right_angle.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `setup` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance |

### Nb 03 — `03_pythagoras_runs_a_regression.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `cell-1` | Replaced entire setup cell with COLAB pattern including rendering backend toggle | Was hardcoded `import regression_geometry.plots as viz`; needed INTERACTIVE toggle + COLAB pip install |
| (new) | Inserted epigraph cell after `cell-0`: *"Three squared lengths, one right angle — the rest is commentary."* | STYLE_GUIDE §1.1 requires epigraph in Cell 2 |
| `cell-18` | Changed "Let's push this idea" → "Push this idea" | Voice rule: no "let's" (STYLE_GUIDE §2) |
| `cell-23` | Converted Back to Statsmodels from code-comment format to markdown table | STYLE_GUIDE §1.9 requires table format |
| `cell-31` | Added bold italic key insight: `***R² = cos²θ — ...***` | STYLE_GUIDE §1.8 requires bold italic key insight in Summary |

### Nb 04 — `04_peeling_apart_the_variables.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `cell-1` | Replaced entire setup cell with COLAB pattern including rendering backend toggle | Was hardcoded `import regression_geometry.plots as viz`; needed INTERACTIVE toggle + COLAB pip install |
| (new) | Inserted epigraph cell after `cell-0`: *"To see what one variable does, first remove what the others explain."* | STYLE_GUIDE §1.1 requires epigraph |
| `cell-25` | Converted Back to Statsmodels from code-comment format to markdown table | STYLE_GUIDE §1.9 |
| `cell-31` | Added bold italic key insight: `***"Controlling for" is not a statistical incantation — ...***` | STYLE_GUIDE §1.8 |

### Nb 05 — `05_who_controls_the_shadow.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `cell-1` | Replaced entire setup cell with COLAB pattern including rendering backend toggle | Was hardcoded `import regression_geometry.plots as viz`; needed INTERACTIVE toggle + COLAB pip install |
| (new) | Inserted epigraph cell after `cell-0`: *"Not all hands pull with equal force on the rope."* | STYLE_GUIDE §1.1 requires epigraph |
| `cell-30` | Changed key insight from italic to bold italic: `***Influence = leverage × surprise...***` | STYLE_GUIDE §1.8 |

### Nb 06 — `06_when_the_geometry_lies.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `setup` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance |
| `clean-regression` | Changed `"condition_number"` → `"kappa"` in active_gauges | **Bug fix**: scoreboard ALL_GAUGES uses "kappa", not "condition_number" |
| `collinearity-slider` | Changed `"condition_number"` → `"kappa"` in active_gauges | Same bug fix |
| `health-check` | Changed `"condition_number"` → `"kappa"` in active_gauges | Same bug fix |
| `both-projections` | Changed `"condition_number"` → `"kappa"` in active_gauges | Same bug fix |

### Nb 07 — `07_constraining_the_shadow.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `setup` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance (rendering toggle already present) |

### Nb 08 — `08_testing_with_geometry.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `setup` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance (rendering toggle already present) |

### Nb 09 — `09_reading_the_instruments.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `cell-0` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance (rendering toggle already present) |

### Nb 10 — `10_what_the_geometry_cannot_see.ipynb`

| Cell | Change | Reason |
|---|---|---|
| `cell-0` | Added COLAB_SETUP.md pattern: standardized header, `import sys`, try/except pip install block | COLAB_SETUP.md compliance (rendering toggle already present) |

---

## Verification Checks Performed

### Scoreboard active_gauges unlocking schedule

| Notebook | Expected Gauges | Status |
|---|---|---|
| Nb 01 | `['theta', 'r_squared']` | OK |
| Nb 02 | `['theta', 'r_squared', 'leverage']` | OK |
| Nb 03 | `['theta', 'r_squared', 'leverage', 'residual_norm']` | OK |
| Nb 04 | `['theta', 'r_squared', 'leverage', 'residual_norm']` | OK |
| Nb 05-10 | All five: `['theta', 'r_squared', 'leverage', 'residual_norm', 'kappa']` | OK (Nb 06 fixed) |

### Meridian dataset values

Computed from `load_meridian()` with seed=42:
- Experience coefficient (simple regression): $4,151 (SPEC says ≈ $4,200) — notebooks use computed values, not hardcoded
- Gender coefficient (short model, no department): -$6,892 (SPEC says ≈ -$7,500) — computed
- Gender coefficient (long model, with department): -$1,052 (SPEC says ≈ -$1,100) — computed
- Corr(experience, education): 0.4222 (SPEC says ≈ 0.4) — computed
- No hardcoded value mismatches found; all notebooks use f-strings with model output

### Rendering backend toggle

All 11 notebooks now have the INTERACTIVE toggle pattern. Nb 00-02 use `from regression_geometry import plots as viz` directly (no interactive features used). Nb 03-10 use the full if/else toggle.

### Voice and style

- No remaining instances of "let's" or "we" as subject
- Epigraphs present in all notebooks
- Summary sections use bold italic key insight (`***text***`)
- Back to Statsmodels sections use markdown table format
- Exercise blocks use standardized 🛑 PREDICT FIRST / DIAGNOSE FIRST / ✍️ The Memo formats

---

## Items NOT Changed (by design)

- No function signatures modified in any package module
- No notebook content rewritten — only structural/consistency patches
- No new exercises or visualizations added
- No color values, thresholds, or dataset parameters changed
- plots.py / interactive.py signature parity confirmed but not modified
