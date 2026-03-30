# SPEC.md — Course Bible

## Regression from the Inside: Seeing the Geometry of Linear Models

**Tagline:** "You've been reading regression output your whole career. This course teaches you to see it."

**Version:** 1.0 (ratified by all five brainstorming agents)

---

## 1. What This Course Is

An interactive course (10 notebooks + 1 optional prerequisite notebook) that teaches ordinary least squares regression through the lens of geometric intuition. Every concept in OLS is revealed as a consequence of the Projection Theorem — the student literally *sees* regression as a perpendicular projection of a data vector onto the column space of the design matrix.

This is NOT a variation, supplement, or companion to the "Regression Autopsy: Eight Ways Your Model Is Lying to You" course. The two courses share no organizing principle, no pedagogical mechanism, and no emotional structure. A student could take both and experience them as completely different intellectual journeys.

| Dimension | Autopsy Course | This Course |
|---|---|---|
| Organizing principle | Eight failure modes | One theorem (the Projection Theorem) |
| Pedagogical mechanism | Productive failure (mistake → correction) | Spatial revelation (blindness → sight) |
| Emotional arc | Forensic — dissecting what went wrong | Perceptual — developing a new way of seeing |
| Core metaphor | Autopsy / diagnosis | Flashlight, shadow, wall |
| Structure | Six-beat per module (Trap → Reveal → Formalize → Destroy → Repair → Limit) | Regression question → geometric answer → theorem → practice |

---

## 2. Organizing Principle

**The Projection Theorem.** One theorem, ten notebooks. Every concept in OLS is a corollary of the following:

> **The Projection Theorem:** Let S be a closed subspace of an inner product space, and let y be a vector. There exists a unique ŷ ∈ S such that ‖y − ŷ‖ ≤ ‖y − s‖ for all s ∈ S. Moreover, ŷ is characterized by the property that (y − ŷ) ⊥ S.

OLS is the Projection Theorem applied to the column space of X. Gauss-Markov is its uniqueness clause. The residual properties are its orthogonality condition. Frisch-Waugh-Lovell is the theorem applied in a quotient space. R² is a metric on how close y is to S. The F-test is a comparison of two applications of the theorem. Regularization is what happens when you modify the norm or constrain the domain.

The student doesn't learn ten different things. They learn one thing from ten different angles.

---

## 3. Core Metaphor

**Regression is a shadow.**

- The **flashlight** is the projection operator.
- The **object** is the data vector y (all n observed values stacked as a single vector in ℝⁿ).
- The **wall** is the column space of X.
- The **shadow** is ŷ — the fitted values.
- The **distance from object to shadow** is the residual vector e.
- The shadow always falls at a **right angle** — the residual is perpendicular to the wall.

Aiming the flashlight at the **wrong wall** (wrong column space) gives the wrong answer — this is omitted variable bias.

A wall that is **paper-thin** (near-degenerate column space) makes the shadow skate around wildly — this is multicollinearity.

---

## 4. Audience

**Primary audience:** Someone who has run at least 20 regressions and has never taken a linear algebra course, OR someone who took linear algebra and never connected it to statistics.

Concrete personas:
- Empirical social scientists (economists, political scientists, sociologists) who use `lm()` in R or `statsmodels` in Python daily but treat OLS as a black box.
- Public health researchers and epidemiologists running regressions on observational data.
- Business analysts who run regressions in Excel, Python, or R and report coefficients to management.
- Engineering and CS graduates who learned vector spaces abstractly but never connected them to statistics.

**Prerequisites:** The student can interpret a regression coefficient ("a one-unit increase in X is associated with a β-unit change in Y") and knows what a vector is, even vaguely ("a list of numbers" is sufficient). No prior linear algebra course required. The course teaches the linear algebra it needs, when it needs it, motivated by regression questions.

**Non-audience:** Pure mathematicians who already think geometrically about statistics. Students who have never run a regression (they should take an introductory course first).

---

## 5. Emotional Arc

The course follows a five-act structure:

| Act | Notebooks | Emotion | Student's Inner Voice |
|---|---|---|---|
| I. Wonder | 0, 1, 2 | Awe, curiosity | "I had no idea regression looked like this." |
| II. Power | 3, 4, 5 | Competence, excitement | "I can see things I couldn't see before." |
| III. Betrayal | 6 | Shock, humility | "I trusted the geometry and it couldn't save me." |
| IV. Deepening | 7, 8 | Determination, sophistication | "I need more geometry, and I need to know its limits." |
| V. Mastery | 9, 10 | Confidence, wisdom | "I see the geometry instantly AND I know when to look beyond it." |

The arc moves from **opacity to transparency** — the student starts seeing regression as a black box formula, and frame by frame, the box becomes glass. There is an emotional valley (Act III) where the geometric intuition the student has built actively fails to detect a causal confounder. This valley is essential: without it, the course is a museum exhibit (admirable, forgettable).

---

## 6. Pedagogical Mechanisms

Six mechanisms, all distinct from the Autopsy course:

### 6.1 Spatial Revelation
The primary mechanism. The student gains a new mode of perception. Every notebook reveals a new geometric fact that makes previously opaque algebra transparent.

### 6.2 The Relevant Triangle
**Principle:** Every scalar property of OLS (a coefficient, its standard error, R², etc.) can be expressed as a function of angles and lengths in a triangle embedded in a 2D plane within ℝⁿ. The regression geometry never requires more than 3 dimensions of "active" geometry at once.

This solves the "n = 3 prison" problem: the student doesn't need to imagine ℝ¹⁰⁰⁰. They identify the relevant 2D or 3D slice within it. The `project_to_relevant_plane()` function in the library makes this computational, not just conceptual.

### 6.3 Predict First / Diagnose First
Three structured exercise cells per notebook, alternating between:
- **Predict First:** "We're about to [change something]. Before running the next cell, predict what will happen to [geometric quantity]. Write your prediction below."
- **Diagnose First:** "Here's a statsmodels summary. Before seeing the geometry, answer: [geometric question about the regression]."

These cells are marked with "🛑 PREDICT FIRST" or "🛑 DIAGNOSE FIRST" headers. They are not optional. The markdown says "STOP — write your prediction in the cell below before scrolling."

### 6.4 The Memo
Every notebook closes with a cell called **"The Memo."** The student writes a 3-sentence memo to a non-technical manager at Meridian Analytics explaining what they just learned. No geometric vocabulary allowed. This forces translation from geometric insight to substantive interpretation.

### 6.5 The Geometric Scoreboard
A persistent horizontal display showing five quantities with color-coded status:

| Gauge | Quantity | Green | Yellow | Red |
|---|---|---|---|---|
| θ | Angle between y and ŷ | < 45° | 45°–70° | > 70° |
| κ | Condition number of X'X | < 30 | 30–100 | > 100 |
| tr(H)/n | Average leverage | Informational (always = k/n) | — | — |
| ‖e‖/‖y‖ | Relative residual norm | < 0.5 | 0.5–0.8 | > 0.8 |
| R² | Coefficient of determination | Displayed alongside θ | — | — |

The Scoreboard first appears in Notebook 1 (Cell 18), grayed out with a note: "You can't read these yet." It is progressively "unlocked" through the course. By Notebook 9, all five gauges are active and the student uses them for diagnosis.

### 6.6 Workflow Traps
At least two moments where the student's own judgment fails:
- **Notebook 3:** Polynomial overfitting. R² climbs in-sample, predictions explode out-of-sample. The geometry says "better" but the model is worse.
- **Notebook 5:** The student removes an obvious outlier (the CEO) but misses a subtle high-influence observation hiding in an unusual predictor combination.

---

## 7. Notebook Sequence

### Notebook 0: "Python for This Course"
- **Act:** — (prerequisite)
- **Duration:** 20 min
- **Register:** N/A
- **Core content:** numpy arrays, the `@` operator, matplotlib basics, five statsmodels commands (`OLS`, `.fit()`, `.summary()`, `.fittedvalues`, `.resid`), how to interact with ipywidgets. No regression content.
- **Purpose:** Eliminate the failure mode where a student understands the geometry but can't engage with the notebooks due to Python syntax barriers.

### Notebook 1: "Where Do Coefficients Come From?"
- **Act:** I (Wonder)
- **Duration:** 45 min
- **Register:** 1 (Visual-Intuitive)
- **Core theorem:** The normal equations X'e = 0 are the orthogonality condition of the Projection Theorem.
- **Core insight:** β̂ is the coordinates of the foot of the perpendicular.
- **"Theorem Without Algebra":** The normal equations derived from a picture of a perpendicular meeting a plane.
- **Key constraint:** No linear algebra vocabulary for the first 20 minutes. No "vector space," no "column space," no "projection operator." Start with sklearn, a tiny dataset, and the question "where did these numbers come from?" Introduce vocabulary only AFTER the student has understood the concept through the flashlight metaphor.
- **Meridian dataset:** First encounter — simple regression of salary on experience. Coefficient = ~$4,200/year.
- **Scoreboard:** First appearance, grayed out.
- **Scaffolding for the ℝⁿ concept:** Build incrementally: 2 data points → ℝ² (plottable), 3 data points → ℝ³ (plottable), then "for 15 data points, we need 15 axes — you can't draw it, but the math is identical." Do NOT jump from scatter plots to ℝ¹⁵ in one cell.

### Notebook 2: "The Right Angle That Explains Everything"
- **Act:** I (Wonder)
- **Duration:** 50 min
- **Register:** 1→2 transition
- **Core theorem:** The hat matrix H = X(X'X)⁻¹X' is a projection operator (H² = H, H' = H).
- **Core insight:** Idempotency means "projecting twice changes nothing" — the shadow of a shadow is itself. Symmetry means the projection works the same from any direction.
- **Key interactive:** Verify X'e = 0 numerically on the Meridian dataset. Show that orthogonality is by *construction*, not by good luck.
- **Meridian dataset:** Run the wage regression. Verify orthogonality. Ask: "does orthogonality mean the model is correct?" (No.)

### Notebook 3: "Pythagoras Runs a Regression"
- **Act:** II (Power)
- **Duration:** 55 min
- **Register:** 2
- **Core theorems:** SST = SSR + SSE (Pythagorean theorem). R² = cos²θ. Gauss-Markov theorem. R² monotonicity.
- **Core insight:** R² is literally an angle. Variance decomposition is literally Pythagoras. BLUE means "closest point in the subspace."
- **"Theorems Without Algebra":** (1) Pythagorean decomposition as a right triangle, (2) Gauss-Markov as "the orthogonal projection is the shortest path," (3) R² monotonicity as "a bigger subspace catches more of y."
- **Workflow Trap:** Polynomial overfitting — add experience², experience³, etc. to the Meridian regression. R² climbs. θ shrinks. Scoreboard says "better." Out-of-sample predictions are terrible. Lesson: R² describes the projection's quality in this sample, not the flashlight's quality.
- **"Back to statsmodels":** Map θ → `np.arccos(np.sqrt(model.rsquared))`, SSR → `model.ess`, SSE → `model.ssr` (note the confusing statsmodels naming).

### Notebook 4: "Peeling Apart the Variables"
- **Act:** II (Power)
- **Duration:** 55 min
- **Register:** 2
- **Core theorem:** Frisch-Waugh-Lovell.
- **Core insight:** Partialling out = projecting onto the orthogonal complement. The multiple regression coefficient equals the simple regression slope in the residualized subspace.
- **"Theorem Without Algebra":** FWL as sequential orthogonal projections — one diagram with two subspaces and two projections.
- **Key interactive:** The "peeling" animation. Start with the full 3D column space (a plane). "Peel" out x₁ by projecting everything onto the orthogonal complement. The plane collapses to a line. The coefficient of x₂ on the line equals its multiple regression coefficient. Slider: correlation between x₁ and x₂. As correlation increases, the residualized vector M₁x₂ shrinks — the unique contribution vanishes.
- **Meridian dataset:** Peel out experience and education. Examine the residualized gender coefficient. Watch how it changes as controls are added/removed.
- **Added variable plots:** Generated from the same FWL geometry.

### Notebook 5: "Who Controls the Shadow?"
- **Act:** II (Power)
- **Duration:** 55 min
- **Register:** 2
- **Core theorem:** Hat matrix diagonal hᵢᵢ measures leverage; Cook's distance measures influence.
- **Core insight:** Leverage is the "arm length" of an observation in the column space. Influence = leverage × residual — how much pull an observation exerts on the projection.
- **Key interactive:** Click on any data point → see its hat value visualized as a vector length. Drag a point outward → watch hᵢᵢ increase, Cook's distance grow, the projection plane tilt.
- **Workflow Trap:** Student removes the CEO (obvious outlier, high leverage). Coefficients barely change. The real problem: a subtle observation with moderate leverage but high influence, sitting in an unusual predictor combination, is quietly torquing the education coefficient. Student missed it because they were distracted by the flashy outlier.
- **Meridian dataset:** Identify influential employees. Remove them and watch the geometry shift.
- **"Back to statsmodels":** hᵢᵢ → `OLSInfluence(model).hat_matrix_diag`, Cook's D → `OLSInfluence(model).cooks_distance`.

### Notebook 6: "When the Geometry Lies"
- **Act:** III (Betrayal)
- **Duration:** 60 min
- **Register:** 2→3 transition
- **Core insight:** Multicollinearity = degenerate column space (visible to geometry). Omitted variable bias = wrong column space (invisible to geometry).
- **Two-part betrayal structure:**
  1. **Part 1 — Multicollinearity (the geometry breaks):** A clean-looking regression. Increase correlation between two predictors from 0.5 to 0.98. The column space collapses into a thin sliver. Coefficients swing wildly on tiny perturbations. The Scoreboard goes red. *The geometry warned you.*
  2. **Part 2 — OVB (the geometry can't warn you):** A regression with a well-conditioned column space. All geometric diagnostics green. But the regression is *wrong* — a confounder (department) is omitted, biasing the gender coefficient. The geometry says "clean regression." The causal structure says "Simpson's paradox." *The geometry worked perfectly and still couldn't save you.*
- **Meridian dataset:** Salary ~ experience + education + gender → gender coefficient = -$7,500. Add department → gender coefficient shrinks to -$1,100 (shrinkage, NOT sign reversal — per Adversary's note). Both regressions have healthy Scoreboards.
- **OVB formula, geometrically:** β̂_short = β_long + Γ·δ shown as the gap between two projections onto different column spaces.
- **"Which wall?" exercise:** Show two column spaces (with and without department). Ask: "which wall should you aim the flashlight at? The geometry can't tell you. You need to know the story of the data." (This replaces a DAG widget, keeping the language in the geometric metaphor.)
- **The Memo:** "Write a memo to Meridian's CEO. The previous analyst reported a $7,500 gender pay gap. Your analysis shows $1,100. Explain the discrepancy without using 'omitted variable bias,' 'confounding,' 'projection,' or 'column space.'"

### Notebook 7: "Constraining the Shadow"
- **Act:** IV (Deepening)
- **Duration:** 55 min
- **Register:** 3
- **Core insight:** Ridge regression is NOT an orthogonal projection — it's a constrained projection. LASSO sparsity is a geometric corner solution.
- **Formal content:** Ridge estimator via eigendecomposition: β̂_ridge = Q diag(λₖ/(λₖ+λ)) Q'β̂_OLS. Each eigencomponent shrunk by factor λₖ/(λₖ+λ). LASSO as projection onto an L1 ball — corners produce exact zeros.
- **Key interactive:** Draggable constraint boundary. Student resizes the L2 sphere (Ridge) or L1 diamond (LASSO). Watch Ridge coefficients shrink smoothly toward zero. Watch LASSO coefficients hit zero and snap — sparsity as a corner solution.
- **Warning icon:** This notebook explicitly marks where the Relevant Triangle principle breaks down. Regularization requires reasoning about the full eigenstructure of X'X, not just pairwise angles.

### Notebook 8: "Testing with Geometry"
- **Act:** IV (Deepening)
- **Duration:** 55 min
- **Register:** 3
- **Core insight:** Hypothesis testing is comparing two projections. The F-test measures whether the gap between restricted and unrestricted projections is "surprising" given residual noise.
- **Formal content:** Nested column spaces C(X_R) ⊂ C(X). The F-statistic proportional to the squared distance between projections, normalized by residual variance.
- **"Theorem Without Algebra":** The F-test as two concentric subspaces with the gap between projections.
- **Key interactive:** Nested column spaces with both projections visible. The distance between them is the numerator of the F-statistic. Monte Carlo: 20 animated samples showing projection pairs under the null. The distribution of distances builds before the student's eyes.
- **Confidence ellipsoids:** Shown as the region where β̂ would fall under repeated sampling.

### Notebook 9: "Reading the Instruments"
- **Act:** V (Mastery)
- **Duration:** 60 min
- **Register:** All three, synthesized
- **Core activity:** The student receives a messy, unfamiliar real dataset (NOT Meridian — something they haven't seen before). They run a regression, consult the Geometric Scoreboard, diagnose problems using only geometric reasoning, and fix them.
- **"Diagnose First" protocol:** Student sees statsmodels summary → must sketch the geometry before seeing it. What shape is the column space? Where is y relative to it? Is the projection stable?
- **Capstone deliverable:** The Rosetta Stone cheat sheet — a two-column reference mapping geometric concepts to statsmodels/sklearn API calls. Auto-generated as a downloadable PDF or HTML.
- **The cheat sheet mappings:**
  - Column space of X → `np.linalg.matrix_rank(X)`, `scipy.linalg.orth(X)`
  - Projection ŷ = Hy → `model.fittedvalues`
  - Residual e = y − ŷ → `model.resid`
  - Hat matrix diagonal hᵢᵢ → `OLSInfluence(model).hat_matrix_diag`
  - Angle θ → `np.arccos(np.sqrt(model.rsquared))`
  - Condition number → `np.linalg.cond(X)`
  - Eigenvalues of X'X → `np.linalg.eigvalsh(X.T @ X)`
  - Cook's distance → `OLSInfluence(model).cooks_distance`
  - Residual norm → `np.linalg.norm(model.resid)`
  - FWL residualized vectors → `OLS(x2, sm.add_constant(X1)).fit().resid`

### Notebook 10: "What the Geometry Cannot See"
- **Act:** V (Mastery)
- **Duration:** 40 min
- **Register:** 2 (deliberately stepping back for reflection)
- **Core insight:** OLS geometry is the geometry of a specific inner product space. The choice of inner product encodes statistical assumptions. Endogeneity is invisible. Heteroscedasticity means the inner product is wrong.
- **Opens with:** "Choose Your Own Regression" sandbox — student picks any subset of Meridian variables, sees the full geometry, the Scoreboard, and the statsmodels output simultaneously. A victory lap using all tools at once.
- **Then transitions to:** Reflection on limits. What GLS and IV do (in geometric language), without teaching them. Points the student toward what comes next.
- **The Memo:** "Write a one-page letter to yourself six months from now. What will you see differently when you run a regression on Tuesday morning?"
- **Does NOT teach:** GLS derivation, IV estimation procedure, Bayesian regression. It names these as "what's beyond the wall" and closes the course.

---

## 8. Recurring Elements

### 8.1 The Meridian Analytics Dataset

A fictional mid-size tech company. 2,000 employees. The dataset threads through Notebooks 1, 2, 4, 5, 6, 9, and 10.

**Variables:**

| Variable | Type | Range | Notes |
|---|---|---|---|
| `salary` | Continuous | $35K–$280K | Right-skewed. DV in most regressions. |
| `experience` | Continuous | 0–35 years | |
| `education` | Continuous | 0–10 years post-secondary | |
| `department` | Categorical | Engineering, Sales, Marketing, HR, Operations | Correlated with gender. |
| `performance` | Ordinal | 1–5 | Compressed: most values between 3–4. |
| `gender` | Binary | 0/1 | Correlated with department. |
| `job_level` | Ordinal | 1–5 | Caused by experience + department. Causes salary. |

**Data-Generating Process (must be implemented exactly):**

The causal structure is:

```
department ──► job_level ──► salary
    │              ▲
    │              │
    ▼          experience
  gender
    │
    └──────────────────────► salary (small direct effect)
```

Key structural properties:
1. **Simpson's paradox:** The gender coefficient in salary ~ experience + education + gender is approximately -$7,500 (significant). Adding department, it shrinks to approximately -$1,100 (non-significant). This is a shrinkage, NOT a sign reversal.
2. **experience and education** are correlated (r ≈ 0.4) but not collinear.
3. **The CEO outlier:** One observation with salary = ~$2.1M, experience = 32, job_level = 5. Extreme leverage point. Removing it barely changes coefficients (high leverage, low influence because the observation is in line with the general trend).
4. **The hidden influential observation:** A junior employee (experience = 2, education = 8, job_level = 2) in an unusual department (Engineering, where most employees have low education). This observation has moderate leverage but high influence — it quietly torques the education coefficient. Removing it changes the education coefficient noticeably.
5. **Performance ratings are compressed:** Little variance (most between 3 and 4), making performance a weak predictor with a small, noisy coefficient.

The dataset is generated by a **seed-locked** Python script (numpy seed = 42 or similar fixed seed) so it is perfectly reproducible. Stored as a CSV in the package.

### 8.2 Five "Theorems Without Algebra"

Each proved using only a geometric diagram and the properties of orthogonal projection:

| # | Theorem | Notebook | One-sentence geometric proof |
|---|---|---|---|
| 1 | Normal equations | 1 | "The residual is perpendicular to the column space — that's what makes it the closest point." |
| 2 | SST = SSR + SSE | 3 | "The Pythagorean theorem applied to the right triangle (y, ŷ, e)." |
| 3 | Gauss-Markov (OLS is BLUE) | 3 | "Any other linear unbiased estimator reaches past the closest point and grabs extra noise." |
| 4 | R² monotonicity | 3 | "A bigger subspace catches more of y — the projection can only get closer." |
| 5 | Frisch-Waugh-Lovell | 4 | "Successive projections onto orthogonal complements — the order doesn't matter." |
| 6 | F-test | 8 | "Two nested projections — the F-statistic measures the gap between them." |

### 8.3 Notebook Cell Flow

Every notebook follows this structure (with variations in ordering):

1. **Title + Epigraph** — single-sentence quote in serif italic.
2. **Setup** — imports, dataset loading, `interactive_mode()` toggle.
3. **Regression Question** — a concrete statistical question the student can't answer with current tools.
4. **🛑 PREDICT FIRST** — student commits a prediction.
5. **Geometric Revelation** — the interactive/static visualization that answers the question.
6. **Formalization** — the theorem stated precisely, with the geometric proof.
7. **Going Deeper (collapsible)** — algebraic proof at a higher register.
8. **🛑 DIAGNOSE FIRST** — student interprets a statsmodels summary geometrically.
9. **Back to statsmodels** — connecting the geometry to real API calls.
10. **🛑 PREDICT FIRST** — second prediction exercise.
11. **Additional content** — extensions, edge cases, interactive exploration.
12. **The Memo** — plain-English translation exercise.
13. **Geometric Scoreboard** — current state of the five gauges.
14. **Summary and Bridge** — what was learned, what's next.

Not every notebook has all 14 elements, but every notebook has at least: one Predict First, one Diagnose First, one Memo, one Scoreboard display, and one "Back to statsmodels" section.

---

## 9. Mathematical Registers

Three registers, explicitly declared per notebook:

### Register 1 — Visual-Intuitive
Arguments by picture. "You can see that the residual is perpendicular." No notation beyond what's necessary to label the picture. Notebooks 1–2 live primarily here.

### Register 2 — Semi-Formal
Matrix notation and precise theorem statements, but proofs are geometric. Example: "By the Projection Theorem, ŷ = Hy, and since H is idempotent, e = (I−H)y is orthogonal to C(X). Here's the picture." Notebooks 3–6 primarily operate here.

### Register 3 — Fully Formal
Complete proofs using inner product space axioms, eigenvalue arguments, spectral decomposition. Example: "β̂_ridge = Q(Λ+λI)⁻¹ΛQ'β̂_OLS, showing each eigenvector component shrunk by λₖ/(λₖ+λ)." Notebooks 7–8 reach this register. Notebooks 9–10 synthesize all three.

Every notebook has a **"Going Deeper"** appendix (collapsible) that takes the main results up one register. Students who want to stay in Register 1 can do so for the first half of the course. Students who want full proofs can find them.

---

## 10. Visual Design Language

### 10.1 Color System

These colors are inviolable. Every visualization across all notebooks uses this palette:

| Element | Color | Hex | Usage |
|---|---|---|---|
| Column space | Blue | #3B82F6 | Planes, subspaces, basis vectors |
| Response vector y | Gold | #F59E0B | The data vector, always prominent |
| Projection ŷ | Green | #10B981 | Fitted values, shadow on the wall |
| Residuals e | Red | #EF4444 | Error vectors, residual bars |
| Constraints | Purple | #8B5CF6 | Regularization boundaries, L1/L2 balls |
| Secondary | Gray | #6B7280 | Axes, labels, grids, annotations |

### 10.2 3D Scene Conventions

- Default camera: 30° elevation, 45° azimuth.
- Interactive scenes allow free rotation.
- Static fallbacks show THREE canonical views: front (elev=0°, azim=0°), side (elev=0°, azim=90°), top-down (elev=90°, azim=0°).
- Column space rendered as translucent surface (alpha ≈ 0.3).
- Vectors rendered as arrows with arrowheads.
- Right angles marked with a small square symbol at the foot of perpendiculars.

### 10.3 Typography

- Each notebook opens with a single-sentence **epigraph** in serif italic.
- Body text in clean sans-serif.
- Mathematical notation rendered via LaTeX in markdown cells.
- Code cells use monospace with syntax highlighting.
- "🛑 PREDICT FIRST" and "🛑 DIAGNOSE FIRST" headers in bold with the stop sign emoji.
- "The Memo" header in bold italic.

---

## 11. Technical Infrastructure

### 11.1 Package: `regression_geometry`

```
regression_geometry/
├── __init__.py
├── core.py          # ColumnSpace, Projection, HatMatrix, Ellipsoid classes
├── plots.py         # Static matplotlib figures (Layer 1 — mandatory)
├── interactive.py   # Plotly + ipywidgets scenes (Layer 2 — optional)
├── scoreboard.py    # The five-gauge Geometric Scoreboard widget
├── data.py          # Meridian Analytics dataset generator + loader
├── exercises.py     # Predict First / Diagnose First cell templates
├── cheatsheet.py    # Rosetta Stone PDF/HTML generator
└── tests/
    ├── test_core.py
    ├── test_data.py
    ├── test_plots.py
    └── test_scoreboard.py
```

### 11.2 Two-Layer Rendering Architecture

**Layer 1 (mandatory, static):** Every visualization exists first as a Matplotlib figure generated by a pure Python function. No JavaScript, no widgets, no fragility. If everything else breaks, the student still sees a clear, labeled, publication-quality figure.

**Layer 2 (optional, interactive):** For environments that support it, Plotly 3D scenes with ipywidgets overlays. Draggable vectors, live-updating projections, sliders.

The toggle at the top of each notebook:
```python
INTERACTIVE = True  # Set to False if widgets aren't working
from regression_geometry import plots, interactive
viz = interactive if INTERACTIVE else plots
```

Every plotting function exists in both modules with **identical signatures**. The student never changes any code below the toggle.

### 11.3 Graceful Degradation

Every notebook must work in three environments:
1. **Google Colab** — full interactive support.
2. **JupyterLab local** — full interactive support.
3. **Static nbviewer rendering** — all interactive cells show their static matplotlib fallback with a note: "Run this notebook in Colab or Jupyter for the interactive version."

The Scoreboard degrades to a simple printed table in static environments.

### 11.4 Key Classes (specified in CONTRACT.md)

**`ColumnSpace(X)`**
- `.project(y)` → `Projection` object
- `.residual(y)` → residual vector
- `.hat_matrix()` → H matrix (n×n)
- `.eigenvalues()` → eigenvalues of X'X
- `.condition_number()` → ratio of max to min eigenvalue
- `.relevant_triangle(y, j)` → extracts the 2D plane relevant to the j-th coefficient
- `.plot_3d(**kwargs)` → 3D visualization
- `.plot_static(**kwargs)` → static matplotlib figure

**`Projection` (dataclass)**
- `.y_hat` → fitted values vector
- `.residuals` → residual vector
- `.H` → hat matrix
- `.theta` → angle between y and ŷ
- `.r_squared` → cos²(θ)
- `.ssr`, `.sse`, `.sst` → sums of squares

**`HatMatrix(H)`**
- `.diagonal()` → leverage values
- `.trace()` → sum of leverages (= k)
- `.cooks_distance(residuals, mse, k)` → Cook's D for each observation

**`Ellipsoid(eigenvalues, eigenvectors)`**
- `.axis_lengths()` → semi-axis lengths
- `.condition_number()` → ratio of max to min
- `.plot(**kwargs)` → ellipsoid visualization

---

## 12. Build Order

Priority order for development:

1. **SPEC.md** (this document)
2. **core.py + CONTRACT.md** — the API every other module depends on
3. **data.py** — the Meridian dataset (needed for all notebook demos)
4. **plots.py** — static rendering backend (needed before notebooks can be tested)
5. **interactive.py** — interactive backend (can be developed in parallel with notebooks)
6. **scoreboard.py** — the Scoreboard widget
7. **Notebooks 0, 1, 2 + NOTEBOOK_STYLE_GUIDE.md** — Act I (establishes all conventions)
8. **Notebooks 3, 4, 5** — Act II (parallel with items 9–11)
9. **Notebook 6** — Act III (parallel)
10. **Notebooks 7, 8** — Act IV (parallel)
11. **Notebooks 9, 10 + exercises.py + cheatsheet.py** — Act V (parallel)
12. **Integration pass** — full sequential read + fixes
13. **Testing pass** — three-environment verification

Items 8–11 can all run in parallel after item 7 is complete.

---

## 13. What This Course Does NOT Cover

Explicitly out of scope (mentioned in Notebook 10 as "beyond the wall"):

- **GLS / WLS derivation** — the course notes that heteroscedasticity changes the inner product but does not teach the GLS estimator.
- **IV estimation** — mentioned as what you need when the column space is causally incomplete.
- **Bayesian regression** — mentioned as "coefficients become distributions" but not taught.
- **Time series geometry** — reserved for potential v2.0 (autocorrelation as path structure).
- **Interaction terms as geometric objects** — reserved for potential v2.0.
- **Causal inference methodology** — the course teaches that geometry can't see causality but doesn't teach DAGs, potential outcomes, or identification strategies.

---

## 14. Quality Bar

A notebook is "done" when:

1. Every code cell executes without errors in Colab.
2. Every interactive cell has a working static fallback.
3. There are at least three Predict First / Diagnose First cells.
4. There is one Memo cell at the end.
5. The Scoreboard appears with correct values.
6. The "Back to statsmodels" section maps at least two geometric concepts to API calls.
7. The Meridian dataset (if used) produces the same numbers as in other notebooks using the same variables.
8. The notebook follows NOTEBOOK_STYLE_GUIDE.md conventions.
9. A reader who has never seen the course bible can understand the notebook's core insight from the notebook alone.
10. The emotional beat of the relevant Act is present and felt.
