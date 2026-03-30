> **⚠️ CRITICAL: Every notebook Cell 1 must follow the Colab installation pattern in COLAB_SETUP.md. Read that file before editing any notebook.**

# NOTEBOOK_STYLE_GUIDE.md

## Regression from the Inside: Seeing the Geometry of Linear Models

This document codifies every convention for all 11 notebooks (0–10). Follow it exactly. Downstream agents building Notebooks 3–10 must not deviate from these patterns without explicit approval.

---

## 1. Setup Cell Convention

Every notebook begins with a standardized setup cell (Cell 1, always a code cell). Include only the imports actually used in that notebook, but the structure and ordering are fixed:

```python
# Notebook N: "Title"
# Regression from the Inside: Seeing the Geometry of Linear Models
# ====================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import linalg

import statsmodels.api as sm
from statsmodels.stats.outliers_influence import OLSInfluence

from regression_geometry.core import ColumnSpace, Projection, HatMatrix, Ellipsoid
from regression_geometry.core import frisch_waugh_lovell, angle_between, demean
from regression_geometry.data import load_meridian
from regression_geometry.colors import *

# Rendering backend toggle
INTERACTIVE = True
try:
    from regression_geometry import interactive as viz_mod
    if not viz_mod.AVAILABLE:
        INTERACTIVE = False
except ImportError:
    INTERACTIVE = False

if INTERACTIVE:
    from regression_geometry import interactive as viz
else:
    from regression_geometry import plots as viz

from regression_geometry.scoreboard import GeometricScoreboard

# Reproducibility
np.random.seed(42)
```

**Rules:**

- Not all imports are needed in every notebook. Include only what's used.
- The rendering backend toggle block is **always present**, always in the same form.
- Notebook 0 is the sole exception: it uses minimal imports (numpy, matplotlib, statsmodels, ipywidgets) and has no toggle block.
- The `np.random.seed(42)` line is always last in setup.

---

## 2. Epigraph Convention

The second cell of every notebook (Cell 2, always a markdown cell) contains a single-sentence epigraph in blockquote italics. It sets the tone without giving away the punchline.

**Format:**

```markdown
> *"[Quote or original sentence relevant to the notebook's theme]"*
```

**Rules:**

- Under 20 words.
- NOT a famous statistics quote. Write original sentences that feel literary.
- Evocative, not explanatory.

**Examples (assigned — do not reuse):**

| Notebook | Epigraph |
|---|---|
| 0 | *"The best tool is the one that disappears while you use it."* |
| 1 | *"Every formula is a fossil — it remembers the shape of the idea that made it."* |
| 2 | *"The right angle is the most important angle in statistics."* |

Notebooks 3–10 must create their own epigraphs following these rules.

---

## 3. Voice and Tone

- **Second person:** "you" not "we" or "one."
- **Present tense:** "the residual IS perpendicular" not "the residual WILL BE perpendicular."
- **Conversational but precise:** contractions are fine ("you'll", "that's", "don't"), but mathematical statements are exact.
- **No exclamation marks** except in genuine moments of surprise (maximum 2 per notebook).
- **No "let's"** — the student is the agent, not a passenger. "Try this" not "let's try this."
- **No "recall that" or "remember that"** — if the student needs context, provide it fresh.
- **Short paragraphs:** 2–4 sentences max. Use whitespace generously.
- **Direct questions encouraged:** "What do you think will happen?" "Does this look right to you?"

---

## 4. Code Cell Conventions

- Every code cell has a **comment on line 1** explaining what it does: `# Generate 15 data points and fit OLS`
- Output should be meaningful: don't just print raw arrays. Format output with f-strings and labels: `print(f"Coefficient: {beta:.4f}")`
- **Limit code cells to 15 lines** where possible. Split long computations across cells with markdown explanation between them.
- **Variable naming:** use descriptive names (`salary`, `experience`) not single letters (`x`, `y`) EXCEPT in geometric demonstrations where x and y are the mathematical objects themselves.
- When calling viz functions, **always assign the result:** `fig = viz.plot_projection_3d(cs, y)`. Do not rely on implicit display.
- Always use the `viz.` prefix for visualization calls (compatible with the interactive/static toggle).

---

## 5. Predict First / Diagnose First Convention

### 🛑 PREDICT FIRST

A markdown cell with this exact format:

```markdown
---
### 🛑 PREDICT FIRST

[1–3 sentences describing what is about to happen.]

**Before running the next cell, write your prediction below:**

[Specific question the student should answer]

---
```

Followed by an empty code cell with a comment:

```python
# YOUR PREDICTION:
#
#
```

**Rules:**

- Minimum 2, maximum 4 per notebook (target: 3).
- The prediction must be **specific and falsifiable:** "what will happen to R²?" not "what do you think?"
- The reveal cell immediately follows and should reference the prediction: "Compare this to your prediction above."
- Space them roughly evenly through the notebook — one in the first third, one in the middle, one in the final third.

### 🛑 DIAGNOSE FIRST

Same structure but with a statsmodels summary or numerical output shown, and the student is asked to **infer the geometry** from the numbers:

```markdown
---
### 🛑 DIAGNOSE FIRST

Here's the regression output:

[statsmodels summary or selected statistics]

**Before seeing the visualization, answer:**

[Specific geometric question]

---
```

**Rules:**

- Minimum 1 per notebook (starting from Notebook 2).
- Notebook 1 may have 0 Diagnose First cells since the student hasn't learned enough geometry yet to diagnose anything — though one introductory Diagnose First at the end is acceptable.

---

## 6. The Memo Convention

The second-to-last substantive cell in every notebook. Always a markdown cell:

```markdown
---
### ✍️ The Memo

You're writing a memo to [specific person at Meridian Analytics — vary the recipient across notebooks].

In 3 sentences, explain [specific insight from this notebook].

**Rules:** Do not use the words [list 3–5 geometric/technical terms that are banned for this memo]. Write in plain English that a non-technical manager would understand.

---
```

Followed by an empty code cell:

```python
# YOUR MEMO:
#
#
#
```

**Rules:**

- The banned words should be the core geometric vocabulary from that notebook, forcing the student to translate.
- Vary the recipient across notebooks (VP of HR, Head of Data Science, CEO, CFO, etc.).
- The memo topic should be the single most important practical insight from the notebook.

---

## 7. Geometric Scoreboard Convention

Appears near the end of every notebook (after The Memo, before Summary and Bridge).

```python
# Geometric Scoreboard
scoreboard = GeometricScoreboard(
    proj=proj,
    cs=cs,
    active_gauges=['theta', 'r_squared'],  # only unlocked gauges
    mode='widget' if INTERACTIVE else 'static'
)
scoreboard.display()
```

**Unlocking schedule (mandatory):**

| Notebook | Active Gauges | Newly Unlocked |
|---|---|---|
| 1 | `['theta', 'r_squared']` | θ, R² |
| 2 | `['theta', 'r_squared', 'leverage']` | tr(H)/n |
| 3 | `['theta', 'r_squared', 'leverage', 'residual_norm']` | ‖e‖/‖y‖ |
| 5 | all five | κ |
| 6–10 | all five | — |

Notebooks 0 and 4 do not display the Scoreboard.

**Markdown after the Scoreboard cell:**

- In Notebook 1: "These five numbers are your instruments. You can't read most of them yet. By Notebook 9, you'll glance at these gauges and diagnose any regression instantly."
- In later notebooks: a 1–2 sentence comment on what the newly unlocked gauge reveals about the current model.

---

## 8. Summary and Bridge Convention

The **final cell** of every notebook. Always a markdown cell:

```markdown
---
### Summary

**What you learned:**
- [Bullet point 1 — one sentence]
- [Bullet point 2 — one sentence]
- [Bullet point 3 — one sentence, optional]

**Key geometric insight:** ***[One sentence in bold italics]***

### Next

[1–2 sentences previewing the next notebook without spoiling the surprise. Frame it as a question that creates curiosity.]

---
```

**Rules:**

- Exactly 2–3 "What you learned" bullets.
- The key geometric insight is always one sentence, bold and italic.
- The "Next" section asks a question, never answers one.

---

## 9. Back to Statsmodels Convention

At least one section per notebook (starting from Notebook 2) explicitly connects the geometric insight to real statsmodels/sklearn code.

```markdown
---
### 🔗 Back to Statsmodels

| Geometric concept | Code |
|---|---|
| [concept 1] | `[api call]` |
| [concept 2] | `[api call]` |

---
```

Followed by a code cell demonstrating the connection on the Meridian dataset or the current notebook's data.

**Rules:**

- Do NOT put this in a collapsible/optional section. It is mandatory and visible.
- Map at least two geometric concepts to API calls.
- The code cell must be runnable and produce labeled output.

---

## 10. Going Deeper Convention (Collapsible)

Optional algebraic proofs or deeper mathematical content. Rendered as a collapsed HTML details block:

```html
<details>
<summary><b>Going Deeper:</b> [Topic — e.g., "Algebraic proof of the normal equations"]</summary>

[Full proof in LaTeX-rendered markdown]

</details>
```

**Rules:**

- Never required to understand the main narrative.
- Always labeled clearly as optional.
- Contains content **one register above** the notebook's primary register.
- Maximum 2 per notebook.

---

## 11. File Naming and Cell Count Targets

### File Naming

Pattern: `NN_short_snake_case_title.ipynb`

```
00_python_for_this_course.ipynb
01_where_do_coefficients_come_from.ipynb
02_the_right_angle.ipynb
03_pythagoras_runs_a_regression.ipynb
04_peeling_apart_the_variables.ipynb
05_who_controls_the_shadow.ipynb
06_when_the_geometry_lies.ipynb
07_constraining_the_shadow.ipynb
08_testing_with_geometry.ipynb
09_reading_the_instruments.ipynb
10_what_the_geometry_cannot_see.ipynb
```

### Cell Count Targets

| Notebook | Target | Range |
|---|---|---|
| 0 | 15 | 13–18 |
| 1–2 | 22 | 18–25 |
| 3–8 | 25 | 20–30 |
| 9–10 | 22 | 20–25 |

These are targets, not hard limits. Quality over quantity.

### Notebook Metadata

Every `.ipynb` file must include standard Jupyter metadata:

```json
{
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "name": "python",
      "version": "3.9.0"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

---

## 12. Color System (Reference)

These colors are inviolable across all notebooks and visualizations. They are available via `from regression_geometry.colors import *`:

| Element | Constant Name | Hex | Usage |
|---|---|---|---|
| Column space | `COLUMN_SPACE` | #3B82F6 | Planes, subspaces, basis vectors |
| Response vector y | `RESPONSE_Y` | #F59E0B | The data vector, always prominent |
| Projection ŷ | `PROJECTION` | #10B981 | Fitted values, shadow on the wall |
| Residuals e | `RESIDUAL` | #EF4444 | Error vectors, residual bars |
| Constraints | `CONSTRAINT` | #8B5CF6 | Regularization boundaries, L1/L2 balls |
| Secondary | `SECONDARY` | #6B7280 | Axes, labels, grids, annotations |

Additional constants: `SURFACE_ALPHA` (0.25), `VECTOR_ALPHA` (0.9), `TITLE_SIZE` (14), `LABEL_SIZE` (11), `TICK_SIZE` (9).

---

## 13. Notebook Cell Flow (Reference)

Every notebook follows this general structure, with variations in ordering:

1. **Setup** — imports, dataset loading, rendering toggle
2. **Epigraph** — single-sentence quote
3. **Regression Question** — a concrete question the student can't yet answer
4. **🛑 PREDICT FIRST** — student commits a prediction
5. **Geometric Revelation** — visualization that answers the question
6. **Formalization** — theorem stated precisely with geometric proof
7. **Going Deeper (collapsible)** — algebraic proof at a higher register
8. **🛑 DIAGNOSE FIRST** — student interprets statsmodels output geometrically
9. **🔗 Back to Statsmodels** — connecting geometry to API calls
10. **🛑 PREDICT FIRST** — second prediction exercise
11. **Additional content** — extensions, edge cases, interactive exploration
12. **✍️ The Memo** — plain-English translation exercise
13. **Geometric Scoreboard** — current state of the gauges
14. **Summary and Bridge** — what was learned, what's next

Not every notebook has all 14 elements, but every notebook (except Notebook 0) has at least: one Predict First, one Memo, one Scoreboard display, one "Back to Statsmodels" section, and one Summary and Bridge.

Notebook 0 has: Setup, Epigraph, content cells, and a closing cell. No Scoreboard, no Memo, no Predict First, no Back to Statsmodels.

---

## 14. API Reference (for notebook authors)

### Core classes (`regression_geometry.core`)

- `ColumnSpace(X, add_intercept=True)` — wraps a design matrix. If `add_intercept=True` (default), prepends a column of ones. Pass `add_intercept=False` if X already has an intercept column.
  - `.project(y)` → `Projection` object
  - `.residual(y)` → residual vector
  - `.hat_matrix()` → H matrix (n×n)
  - `.eigenvalues()` → sorted descending
  - `.condition_number()` → ratio of max to min eigenvalue
  - `.relevant_triangle(y, j)` → dict with residualized vectors
  - `.basis()` → orthonormal basis via QR
  - `.X`, `.n`, `.p`, `.rank` — properties

- `Projection` (dataclass) — returned by `ColumnSpace.project(y)`
  - `.y`, `.y_hat`, `.residuals`, `.coefficients`, `.H`
  - `.theta`, `.theta_degrees`, `.r_squared`
  - `.sst`, `.ssr`, `.sse`, `.residual_norm`, `.relative_residual_norm`
  - `.verify_orthogonality(X)`, `.verify_pythagorean()`

- `HatMatrix(H)` — wraps an n×n hat matrix
  - `.diagonal()`, `.trace()`, `.average_leverage()`
  - `.cooks_distance(residuals, mse, p)`
  - `.verify_idempotent()`, `.verify_symmetric()`

### Visualization (`regression_geometry.plots` / `regression_geometry.interactive`)

All viz functions are called via the `viz.` prefix after the toggle. Key signatures:

- `viz.plot_projection_3d(cs, y, title=..., views=..., show_right_angle=True)` — cs is a `ColumnSpace` (n=3 only)
- `viz.plot_projection_2d(x, y, title=..., show_residuals=True)` — raw x, y arrays (creates ColumnSpace internally)
- `viz.plot_relevant_triangle(cs, y, j, title=...)` — the Relevant Triangle
- `viz.plot_pythagorean_triangle(proj, title=...)` — takes a `Projection`
- `viz.plot_leverage(hm, title=...)` — takes a `HatMatrix`
- `viz.plot_scoreboard(proj, cs, active_gauges=...)` — static scoreboard
