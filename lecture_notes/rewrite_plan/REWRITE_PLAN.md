# Rewrite Plan: lecture_notes_v3.tex

## The Four-Beat Rhythm

Every major result follows this pattern:

1. **Toy Story** -- A tiny, concrete, everyday scenario (3-8 sentences). No jargon. A 16-year-old should get it.
2. **The Math** -- The rigorous theorem/proof/derivation. Keep all existing math. Improve connective prose.
3. **Visualization Spec** -- A `\begin{visualization}...\end{visualization}` block describing an interactive web viz.
4. **Numerical Example** -- A hand-computable 2x2 or 3x3 example with a geometric verification step.

## Box Rebranding

| Old name | New name |
|---|---|
| `keyinsight` | `keyinsight` (keep) |
| `warning` | `warning` (keep) |
| `metaphor` | `toystory` (new box type, amber/gold) |
| `stopandthink` | `stopandthink` (keep) |
| `misconception` | `thetrap` (rename for more punch) |

Add new environment:
- `\begin{vizspec}...\end{vizspec}` -- blue-purple box for visualization specifications

## Section-by-Section Plan

### Section 1: Prologue
- **KEEP** the Ceres story (it's excellent)
- **ADD** toy story for the Projection Theorem (bus shelter in the rain)
- **ADD** viz spec: "Closest Point on a Subspace" (draggable y, alternative point s on line)
- **KEEP** existing Stop-and-Think exercise
- Improve transition prose to be more conversational

### Section 2: Where Coefficients Come From
- **ADD** toy story for OLS (mixing paint to match a color swatch)
- **ADD** toy story for Normal Equations (tuning a radio with two knobs)
- **KEEP** Example 1 ("Your First Regression in R³") -- excellent
- **ADD** viz spec: "Point, Plane, Shadow" (3D projection with orbit controls)
- **ADD** viz spec: "X'e = 0: The Right-Angle Condition" (beta slider + dot-product bar chart)
- Improve transition prose

### Section 3: Hat Matrix and the Right Angle
- **ADD** toy story for Hat Matrix (photocopier "reduce to fit" button)
- **ADD** toy story for Idempotency (shadow of a shadow)
- **ADD** toy story for Annihilator (coffee filter)
- **KEEP** Example 2 (hat matrix numerical) -- good
- **ADD** viz spec: "Shadow of a Shadow" (project button, counter, oblique toggle)
- **ADD** numerical example for M = I - H (compute M, verify M*y = e, M^2 = M)
- Rename "Misconception Alert" boxes to "The Trap"

### Section 4: Pythagoras Runs a Regression
- **ADD** toy story for Variance Decomposition (3-4-5 walking to school)
- **ADD** toy story for R² as angle (pencil shadow on wall)
- **ADD** toy story for Gauss-Markov (thermometer in the wind)
- **ADD** toy story for R² Monotonicity (adding walls to catch more shadow)
- **ADD** toy story for Adjusted R² (locksmith with 10,000 keys)
- **ADD** toy story for Degrees of Freedom (10 friends, average constraint)
- **KEEP** Example 3 ("Pythagoras Checks Out") -- excellent
- **ADD** viz spec: "SST = SSR + SSE: A Right Triangle" (Pythagorean squares)
- **ADD** viz spec: "Sweeping Theta, Watching R²" (angle slider + cos² curve)
- **ADD** viz spec: "Adding a Dimension to Col(X)" (R² monotonicity animation)
- **ADD** numerical examples for: Adjusted R², Gauss-Markov illustration

### Section 5: Frisch-Waugh-Lovell
- **ADD** toy story for FWL (fertilizer and sunlight for tomato plants)
- **ADD** toy story for predictor correlation (two friends carrying a couch)
- **KEEP** Example 4 ("FWL by Hand") -- excellent but long, keep as-is
- **ADD** viz spec: "Two-Step Projection" (step toggle, correlation slider)
- **ADD** viz spec: "Shrinking the Residualized Predictor" (correlation vs SE)
- **ADD** numerical example for SE inflation with correlation

### Section 6: Leverage and Influence
- **ADD** toy story for Leverage (kid at end of tug-of-war rope)
- **KEEP** seesaw analogy for Cook's Distance (already excellent, minor reframe)
- **ADD** viz spec: "Moving a Point in Predictor Space" (draggable point, h_ii bar chart)
- **ADD** viz spec: "Leverage x Surprise = Influence" (2D drag, leave-one-out line)
- **ADD** numerical example for Cook's Distance

### Section 7: When the Geometry Fails
- **ADD** toy story for Multicollinearity (church and steeple directions)
- **ADD** toy story for OVB (tracing shadow on tilted wall)
- **ADD** viz spec: "The Pancake Column Space" (angle slider, perturbation experiment)
- **ADD** viz spec: "Wrong vs Right Column Space" (OVB with correlation/beta_2 sliders)
- **ADD** numerical example for condition number and eigenvalue spread
- **ADD** numerical example for OVB bias formula

### Section 8: Regularisation
- **KEEP/EXTEND** telescope analogy for Ridge (already good)
- **ADD** toy story for LASSO (packing a sparse suitcase with weight limit)
- **ADD** toy story for Ridge vs LASSO (round vs diamond coin purse)
- **KEEP** Example 5 ("Ridge Shrinkage Direction by Direction") -- excellent
- **ADD** viz spec: "Eigenvalue Shrinkage with Lambda Slider"
- **ADD** viz spec: "Ellipses Meet the Diamond" (LASSO)
- **ADD** viz spec: "Circle vs Diamond" (side-by-side Ridge/LASSO)
- **ADD** numerical example for LASSO (2D, show corner solution)

### Section 9: The F-Test
- **ADD** toy story for F-test (rehanging a picture with/without tools)
- **ADD** toy story for Confidence Ellipsoids (darts with wobbly elbow)
- **ADD** viz spec: "Is the Extra Projection Worth It?" (signal slider, F distribution)
- **ADD** viz spec: "The Shape of Uncertainty" (eigenvalue sliders, ellipsoid)
- **ADD** numerical example for F-test (restricted vs unrestricted, compute F)
- **ADD** numerical example for confidence ellipsoid (axes from eigenvalues)

### Section 10: Limits of the Geometric Framework
- **ADD** toy story (flashlight can't tell you three things)
- No viz spec needed (philosophical section)
- Improve prose to be a satisfying conclusion

## Existing Examples Audit

| # | Name | Concept | Verdict |
|---|------|---------|---------|
| 1 | Your First Regression in R³ | OLS projection, normal equations | KEEP (excellent) |
| 2 | Hat matrix for Example 1 | Hat matrix, leverages, idempotency | KEEP (good) |
| 3 | Pythagoras Checks Out | Variance decomposition, R² | KEEP (excellent) |
| 4 | FWL by Hand | Frisch-Waugh-Lovell | KEEP (thorough) |
| 5 | Ridge Shrinkage Direction by Direction | Ridge eigenvalue shrinkage | KEEP (excellent) |

## New Examples Needed

1. **Annihilator M**: Using Example 1 data, compute M = I - H, verify M*y = e, M^2 = M
2. **Gauss-Markov illustration**: Show an alternative estimator has higher variance (2D)
3. **Adjusted R²**: Extend Example 3 with adding a noise column, show R² up but adj-R² down
4. **Cook's Distance**: 4 points, one high-leverage outlier, compute D_i
5. **Condition Number**: 2 predictors at various angles, show eigenvalue ratio
6. **OVB**: Short vs long regression on 4 data points, compute bias = Gamma * beta_2
7. **LASSO**: 2D coefficient space, show RSS contours touching diamond corner
8. **F-test**: Restricted (intercept only) vs unrestricted (intercept + slope), compute F
9. **Confidence Ellipsoid**: 2D coefficients, compute ellipsoid axes from eigenvalues

## Prose Style Guide

- **Voice**: Second person ("you"), present tense, conversational but not sloppy
- **Humor**: Occasional dry wit, never forced. Surprise and delight, not jokes.
- **Transitions**: Every section ends with a question that the next section answers
- **Before dense math**: Always a "why should you care?" paragraph
- **After dense math**: Always a "what just happened?" paragraph
- **Keep**: All existing TikZ figures (they are excellent)
- **Tone model**: Like a brilliant friend explaining math over coffee -- rigorous but warm, precise but not pedantic
