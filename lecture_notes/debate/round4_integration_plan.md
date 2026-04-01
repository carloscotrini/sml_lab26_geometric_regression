# Round 4: Definitive Integration Plan

## Document Identity (Governing Decision)

**This document is: "Supplementary lecture notes for a 90-minute lecture on the geometry of OLS, targeted at second-year undergraduates with basic linear algebra (matrix multiplication, inverses, eigenvalues) but no real analysis."**

Every decision below flows from this identity. The document should be readable in a single sitting (~60-90 minutes). The target length is **~1600 lines** (a 50% expansion from the original 1077). All material that exceeds this scope goes to an appendix or is cut entirely.

---

## Conflict Resolutions

### 1. Length vs. Completeness

**Target: ~1600 lines** (original 1077 + ~520 net new lines).

| Category | Include inline | Move to appendix | Cut entirely |
|---|---|---|---|
| **Proofs** | Gauss-Markov (builds intuition), FWL (essential algebra) | Projection Theorem proof, Characterisation Theorem proof | -- |
| **Examples** | Ex 1 (R^3 regression, shortened), Ex 2 (Pythagoras), Ex 3 (FWL, corrected), Ex 6 (Ridge, shortened) | -- | Ex 4 (multicollinearity -- redundant with existing Section 7.1 prose), Ex 5 (leverage -- too long, scratch-calculation passage) |
| **Stop-and-Think** | S&T 1 (after Projection Thm), S&T 3 (adding noise columns/R^2), S&T 4 (FWL limiting cases), S&T 7 (LASSO corners) | -- | S&T 2 (leverage calculation -- trivial), S&T 5 (ranking influence -- covered by prose), S&T 6 (Ridge limits -- covered by Ex 6) |
| **Misconceptions** | Misc 1 (projection validates model), Misc 2 (R^2=0.8 is good), Misc 4 (multicollinearity = bad) | -- | Misc 3 (controlling for -- too long, 40 lines), Misc 5 (clean residuals rule out OVB -- too long, 25 lines; condense to 2-sentence remark in OVB subsection) |
| **Analogies** | Telescope (regularisation), Shadow-sharpness (R^2) -- both short and vivid | -- | Movie-screen (FWL -- redundant with existing "three-dimensional room" analogy), Hearing-test (F-test -- too cute, adds length without geometric insight) |
| **Figures** | All 6 TikZ figures | -- | -- |
| **Prerequisites** | Eigendecomposition review (before multicollinearity), Gaussian prerequisite (before F-test) | -- | Loewner ordering review (readers can follow the proof without it; the boxed result is self-explanatory) |
| **Transitions** | All 8 transition sentences (they are 3-4 lines each, negligible cost, major cohesion benefit) | -- | -- |
| **New subsections** | Adjusted R^2 (geometric reading only), Degrees of freedom | -- | -- |

**Estimated line budget:**
- Original retained (after replacements): ~950 lines
- Prologue (round3 revision): +100 lines (replacing ~50 original preamble lines)
- 4 inline examples (shortened): +300 lines (Ex 1: 90, Ex 2: 60, Ex 3: 80, Ex 6: 70)
- 4 Stop-and-Think boxes: +80 lines
- 3 Misconception boxes: +55 lines
- 2 Analogies: +25 lines
- 6 TikZ figures: +350 lines (but figures are mostly whitespace in PDF)
- 2 inline proofs (FWL, Gauss-Markov): +130 lines (replacing ~30 lines of sketches)
- Transitions, fixes, new subsections: +80 lines
- Appendix (2 proofs + cut examples): +250 lines
- Cuts from original (see below): -120 lines
- **Total: ~1600 lines main body + ~250 lines appendix = ~1850 lines total file**

This is within the envelope. The main narrative reads at ~1600 lines; the appendix is clearly marked as optional.

### 2. Proof Depth

| Proof | Decision | Rationale |
|---|---|---|
| **Gauss-Markov** | **INLINE** | The proof builds genuine geometric intuition. The constraint DX=0 ("the excess must be orthogonal to the column space") is the geometric heart of BLUE. The remark after the proof is one of the best paragraphs in the entire document. |
| **FWL (block elimination)** | **INLINE** | The original hand-waves ("solve and substitute... one obtains"). Students need to see the M_1 factorisation emerge from the algebra. This is a teaching moment, not a technicality. |
| **Projection Theorem** | **APPENDIX** | Uses infimum, compactness, parallelogram law -- graduate analysis tools. The target audience takes this on faith. The one-line statement ("a closest point exists and is unique, characterised by orthogonality") suffices for the main narrative. |
| **Characterisation Theorem** | **APPENDIX** | Important mathematics but a supporting lemma. Keep the 10-line remark inline ("idempotency makes it a projection; symmetry makes it orthogonal"). Move the 50-line proof to the appendix. |

### 3. Tone

**Unified voice: "Knowledgeable guide."** Warm but precise. The narrator is a lecturer who tells stories to motivate, then explains clearly, then proves when the proof teaches something.

**Specific rules:**
1. The Gauss/Ceres prologue sets the tone: historically grounded, vivid but not fictional. Use the round3 revision (which removed "The clouds parted" and other fiction).
2. Theorem-proof blocks use clear, step-labelled prose (not terse analysis style). Every proof step gets a one-sentence plain-English summary before the formula.
3. Examples use a direct second-person register ("Step 1: Compute..."). No "Wait -- let me re-examine" scratch-pad passages.
4. Remove "Let us begin." from the end of the prologue (identified as a cliche in round 3).
5. Transition sentences use italics to signal a shift in topic, providing a question that the next section answers.
6. Key Insight boxes and Takeaway boxes are the only places where the tone rises to emphasis. These are the "punchlines."

**Smoothing the Gauss-to-theorems transition:**
After the prologue's narrative conclusion ("And it was, at its mathematical heart, an orthogonal projection"), the flashlight metaphor box provides a concrete bridge. Then the Projection Theorem statement (finite-dimensional, not general) lands cleanly. The transition sentence after the theorem ("The Projection Theorem guarantees... But how do we compute it?") carries the reader forward without tonal whiplash.

### 4. Redundancy

Each insight appears ONCE, definitively, in the location specified below:

| Insight | Definitive location | Remove from |
|---|---|---|
| "Shadow of shadow is itself" (idempotency) | Section 3, "Geometric meaning" paragraph (round2_math Item 5c replacement) | Ex 1 Step 5 last sentence, Characterisation Theorem remark (move to appendix anyway), any other occurrence |
| Multicollinearity = pancake | Section 7.1 prose (original, which has the best narrative) + Figure 4 caption (visual reinforcement is not redundancy) | Ex 4 (cut entirely) |
| Influence = leverage x surprise | Section 6 Key Insight box (original) | Ex 5 Takeaway (cut with Ex 5), Cook's distance definition block (keep formula, remove narrative restatement) |
| Roadmap previews | **Rewrite roadmap items as questions only, without one-sentence geometric answers.** Let each section deliver its own punchline. | Current roadmap items that give away the answer (e.g., "R^2 turns out to equal the squared cosine...") |

### 5. Regularisation Framing

**The specific transition paragraph** to replace lines 788-790 of lecture_notes.tex (the opening of Section 7, "Constraining the Shadow"):

```latex
\begin{warning}
\textbf{Where the projection framework reaches its limits.}
Everything in the preceding sections was a consequence of the Projection
Theorem: find the closest point in a subspace.  Ridge and LASSO are
\emph{not} projections.  They deliberately move away from the closest
point, accepting bias in exchange for stability.

The Ridge operator
$\bH_{\text{ridge}} = \bX(\bX^\top\bX + \lambda\bI)^{-1}\bX^\top$
is \emph{not} idempotent and is \emph{not} an orthogonal projection
onto any subspace.  Ridge regression does not ``drop a
perpendicular''---it \emph{pulls the shadow inward}, toward the origin.

The geometric language of shadows and right angles served us well for
OLS.  For regularisation, we need a different picture:
\textbf{constrained optimisation}, where the solution is the tangency
between the RSS contour ellipsoids and a constraint region (a sphere
for Ridge, a diamond for LASSO).
\end{warning}
```

Additionally, in the Rosetta Stone table (Section 10), change:
- Ridge: "Constrained projection (sphere)" --> "Constrained optimisation (sphere)"
- LASSO: "Constrained projection (diamond)" --> "Constrained optimisation (diamond)"

### 6. Document Identity

Resolved above. This is "supplementary lecture notes for a 90-minute lecture on the geometry of OLS, targeted at undergraduates with basic linear algebra." The subtitle on the title page should read:

> *Supplementary notes for the lecture on linear regression. Read these after the lecture to deepen your geometric understanding.*

---

## Ordered Operations

The following operations are to be performed on `lecture_notes.tex`, using content from the round 2 and round 3 source files. Each operation specifies WHAT, WHERE, and SOURCE. Line numbers refer to the current `lecture_notes.tex` (1077 lines).

### Phase 0: Preamble additions

**OP-0.1** INSERT new box definitions.
- WHAT: Insert `stopandthink` and `misconception` tcolorbox definitions.
- WHERE: After line 60 (after the `\metaphor` box definition), in the preamble.
- SOURCE: `round3_pedagogy.tex`, Part 1 (lines 15-26).
- MODIFICATION: None needed.

### Phase 1: Prologue (Section 1)

**OP-1.1** REPLACE the entire prologue section.
- WHAT: Replace lines 120-163 (the current Section 1 "Prologue: One Theorem, Ten Perspectives") with the round 3 revised prologue.
- WHERE: Lines 120-163.
- SOURCE: `round3_prologue.tex` (entire file, 155 lines).
- MODIFICATIONS:
  - Delete "Let us begin." from the final line (round 3 already removed this; confirm).
  - In the roadmap, **strip the geometric-insight sentences** from each item, keeping only the question and the section reference. Specifically:
    - Item 1: Keep "Where do the coefficients come from?" and the section ref. Remove "The OLS coefficients... columns of X."
    - Item 2: Keep "How good is the fit?" and the section ref. Remove "The Pythagorean theorem decomposes... angle between y and yhat."
    - Item 3: Keep "What does each variable contribute on its own?" and the section ref. Remove the sentence about FWL.
    - Item 4: Keep "What can go wrong, and how do we fix it?" and the section ref. Remove the sentences about multicollinearity, OVB, leverage, regularisation.
    - Item 5: Keep "How do we test whether the shadow is real?" and the section ref. Remove the F-test description.
  - Keep the closing paragraph ("By the time you reach the end... measuring the gap that remains.") unchanged.

**OP-1.2** INSERT Figure 1 (flashlight metaphor).
- WHAT: Insert the flashlight TikZ figure.
- WHERE: After the metaphor box in the prologue (after the "shadow cast at right angles" paragraph).
- SOURCE: `round2_figures.tex`, Figure 1 (lines 12-61).
- MODIFICATION: None.

**OP-1.3** INSERT transition sentence (Prologue -> Section 2).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After the Projection Theorem statement and the "seed from which these notes grow" sentence, before Stop-and-Think 1.
- SOURCE: `round3_pedagogy.tex`, Transition Section 1->2 (lines 645-651).
- MODIFICATION: None.

**OP-1.4** INSERT Stop-and-Think 1.
- WHAT: Insert the R^2 projection exercise.
- WHERE: After the transition sentence from OP-1.3, before Section 2 heading.
- SOURCE: `round3_pedagogy.tex`, S&T 1 (lines 37-53).
- MODIFICATION: None.

### Phase 2: Section 2 (Where Coefficients Come From)

**OP-2.1** INSERT Standing Assumption box.
- WHAT: Insert the full-column-rank assumption box.
- WHERE: At the beginning of Section 2, immediately after the section heading (line 154), before the current subsection "Setup and notation" (line 157).
- SOURCE: `round2_math.tex`, Item 5a (lines 391-412).
- MODIFICATION: None.

**OP-2.2** INSERT Example 1 (shortened).
- WHAT: Insert the R^3 regression example.
- WHERE: After line 228 (end of subsection "Building intuition"), before the transition to Section 3.
- SOURCE: `round2_examples.tex`, Example 1 (lines 12-125).
- MODIFICATIONS:
  - **Delete Step 5** (hat matrix computation and H^2 verification, lines 84-112). This is 28 lines of matrix multiplication that adds little -- the idempotency is verified conceptually in Section 3. Keep "The geometry" and "Takeaway" paragraphs (lines 114-124).
  - **Delete the sentence** "Applying the projection a second time does nothing---the shadow of a shadow is itself." (line 112) -- this is the first of the 4x redundancy.
  - Estimated result: ~90 lines.

**OP-2.3** INSERT Figure 2 (Projection in R^3).
- WHAT: Insert the R^3 projection TikZ figure.
- WHERE: Immediately after Example 1.
- SOURCE: `round2_figures.tex`, Figure 2 (lines 67-122).
- MODIFICATION: None.

**OP-2.4** INSERT transition sentence (Section 2 -> Section 3).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After Figure 2, before Section 3 heading.
- SOURCE: `round3_pedagogy.tex`, Transition Section 2->3 (lines 658-664).
- MODIFICATION: None.

### Phase 3: Section 3 (The Hat Matrix)

**OP-3.1** REPLACE the "Geometric meaning" paragraph.
- WHAT: Replace the paragraph starting "Symmetry says the projection treats all directions equally..." (approximately lines 264-268).
- WHERE: After the proof of Proposition (Properties of H), before the annihilator subsection.
- SOURCE: `round2_math.tex`, Item 5c (lines 464-477).
- MODIFICATION: None. This is the definitive "idempotency + symmetry" paragraph.

**OP-3.2** INSERT the Characterisation Theorem **remark only** (not the proof).
- WHAT: Insert the remark from the Characterisation Theorem block.
- WHERE: After OP-3.1 (the new Geometric meaning paragraph), before the annihilator subsection.
- SOURCE: `round2_math.tex`, Item 4 -- remark only (lines 364-381).
- MODIFICATIONS:
  - Remove the reference to Theorem~\ref{thm:proj-char} (since the theorem statement will be in the appendix). Instead write: "A fundamental theorem (proved in Appendix~\ref{app:proofs}) states that a matrix is an orthogonal projection onto its column space if and only if it is symmetric and idempotent."
  - Remove the bullet about oblique projections (line 375-379) -- this duplicates what the geometric meaning paragraph just said.
  - Estimated result: ~10 lines.

**OP-3.3** INSERT Misconception 1 ("Projection validates the model").
- WHAT: Insert the misconception box.
- WHERE: After the existing Warning box at the end of Section 3 (after line 292).
- SOURCE: `round3_pedagogy.tex`, Misconception 1 (lines 258-275).
- MODIFICATION: None.

**OP-3.4** INSERT transition sentence (Section 3 -> Section 4).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After Misconception 1, before Section 4 heading.
- SOURCE: `round3_pedagogy.tex`, Transition Section 3->4 (lines 671-677).
- MODIFICATION: None.

### Phase 4: Section 4 (Pythagoras / R^2 / Gauss-Markov)

**OP-4.1** INSERT Remark on SST=SSR+SSE requiring intercept.
- WHAT: Insert the remark about the intercept requirement.
- WHERE: After the variance decomposition equation SST = SSR + SSE (approximately line 330), before the R^2 subsection.
- SOURCE: `round2_math.tex`, Item 5d (lines 487-516).
- MODIFICATION: Shorten by removing the "In models without an intercept, R^2 can be negative" sentence (line 514-515) -- it is a tangent. Keep the rest. Estimated: ~25 lines.

**OP-4.2** INSERT Example 2 (Pythagoras Checks Out).
- WHAT: Insert the Pythagoras verification example.
- WHERE: After the R^2 Key Insight box (approximately line 406), before the Gauss-Markov subsection.
- SOURCE: `round2_examples.tex`, Example 2 (lines 132-195).
- MODIFICATION: None needed. This is already concise (~60 lines).

**OP-4.3** INSERT shadow-sharpness analogy.
- WHAT: Insert the R^2 shadow-sharpness analogy paragraph.
- WHERE: After Example 2, before Misconception 2.
- SOURCE: `round3_pedagogy.tex`, Analogy 3 (lines 471-485).
- MODIFICATION: None.

**OP-4.4** INSERT Misconception 2 ("R^2 = 0.8 means good").
- WHAT: Insert the misconception box.
- WHERE: After the shadow-sharpness analogy, before the Gauss-Markov subsection.
- SOURCE: `round3_pedagogy.tex`, Misconception 2 (lines 282-304).
- MODIFICATION: None.

**OP-4.5** INSERT Stop-and-Think 3 (adding noise columns).
- WHAT: Insert the R^2 inflation thought experiment.
- WHERE: After Misconception 2, before the Gauss-Markov subsection.
- SOURCE: `round3_pedagogy.tex`, S&T 3 (lines 83-105).
- MODIFICATION: None.

**OP-4.6** REPLACE the Gauss-Markov proof sketch.
- WHAT: Replace lines 417-430 (current "Geometric proof sketch") with the full proof from round 2.
- WHERE: Lines 417-430.
- SOURCE: `round2_math.tex`, Item 3 (lines 191-292, theorem statement + proof + geometric remark).
- MODIFICATIONS:
  - Change the label from `\label{thm:gm-full}` to `\label{thm:gm}` to preserve existing references.
  - This is ~100 lines replacing ~14 lines, net +86 lines.

**OP-4.7** INSERT Adjusted R^2 subsection (geometric reading only).
- WHAT: Insert the adjusted R^2 subsection.
- WHERE: After the R^2 monotonicity subsection (after line 451), before Section 5.
- SOURCE: `round2_math.tex`, Item 6 (lines 525-570).
- MODIFICATIONS:
  - **Delete the "Algebraic reading" paragraph** (lines 540-548) -- pure formula manipulation, no geometric insight. Keep only the definition and the "Geometric reading" paragraph.
  - Estimated result: ~30 lines.

**OP-4.8** INSERT Degrees of Freedom subsection.
- WHAT: Insert the degrees-of-freedom subsection.
- WHERE: After the adjusted R^2 subsection, before Section 5.
- SOURCE: `round2_math.tex`, Item 7 (lines 581-651).
- MODIFICATIONS:
  - **Delete the "Degrees-of-freedom bookkeeping" remark** (lines 630-651) -- this is the redundant bookkeeping the Devil's Advocate flagged. The d.f. decomposition n-1 = (p-1) + (n-p) is in every textbook.
  - Keep the definition, geometric interpretation, and "Why divide by n-p" remark.
  - Estimated result: ~40 lines.

**OP-4.9** INSERT transition sentence (Section 4 -> Section 5).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After the degrees-of-freedom subsection, before Section 5 heading.
- SOURCE: `round3_pedagogy.tex`, Transition Section 4->5 (lines 685-693).
- MODIFICATION: None.

### Phase 5: Section 5 (FWL)

**OP-5.1** REPLACE the FWL proof.
- WHAT: Replace lines 495-509 (current hand-wave proof) with the full block-elimination proof.
- WHERE: Lines 495-509.
- SOURCE: `round2_math.tex`, Item 2 (lines 101-182).
- MODIFICATION: None. This is ~80 lines replacing ~15 lines, net +65.

**OP-5.2** INSERT Example 3 (FWL by hand, corrected).
- WHAT: Insert the FWL worked example with arithmetic corrections.
- WHERE: After the FWL theorem and proof, after the Key Insight box (approximately line 517).
- SOURCE: `round2_examples.tex`, Example 3 (lines 201-327).
- MODIFICATIONS:
  - Apply Correction 1 from `round3_verification.tex` Part D (lines 517-546): fix Step B3 intermediate values from (2,4) to (2,2), projection from (6,2,6,2) to (4,2,4,2), and residualised y from (-4,1,0,-1) to (-2,1,2,-1). Update Step B4 numerator calculation accordingly.
  - Shorten the "What happened geometrically?" paragraph to 3 sentences (remove overlap with the Key Insight box above).
  - Estimated result: ~80 lines.

**OP-5.3** INSERT Figure 3 (FWL two-step projection).
- WHAT: Insert the FWL TikZ figure.
- WHERE: After Example 3.
- SOURCE: `round2_figures.tex`, Figure 3 (lines 128-213).
- MODIFICATION: None.

**OP-5.4** INSERT Stop-and-Think 4 (FWL limiting cases).
- WHAT: Insert the S&T box about orthogonal predictors and perfect collinearity.
- WHERE: After Figure 3, before the "effect of predictor correlation" subsection.
- SOURCE: `round3_pedagogy.tex`, S&T 4 (lines 112-142).
- MODIFICATION: None.

**OP-5.5** INSERT transition sentence (Section 5 -> Section 6).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After the end of Section 5, before Section 6 heading.
- SOURCE: `round3_pedagogy.tex`, Transition Section 5->6 (lines 701-707).
- MODIFICATION: None.

### Phase 6: Section 6 (Leverage and Influence)

**OP-6.1** REPLACE the leverage definition.
- WHAT: Replace the current leverage definition (approximately lines 590-595) with the corrected version that distinguishes the intercept case.
- WHERE: Lines 590-595.
- SOURCE: `round2_math.tex`, Item 5b (lines 422-449).
- MODIFICATIONS:
  - Keep the Definition and the first paragraph of the Remark (the bound h_ii >= 1/n with intercept).
  - **Delete the Cauchy-Schwarz derivation** (lines 435-448) -- too technical for the target audience. Replace with: "This can be proved using the Cauchy--Schwarz inequality applied to the rows of $\bH$; the proof is in Appendix~\ref{app:proofs}." Move the derivation to the appendix.
  - Estimated result: ~15 lines (replacing ~6 lines).

**OP-6.2** DELETE the redundant "concrete example" paragraph.
- WHAT: Delete lines 700-706 (the verbal sketch "$x_2 = x_1 + \epsilon$, on Monday $(5,3)$, on Tuesday $(50,-42)$").
- WHERE: Lines 700-706.
- SOURCE: N/A (pure deletion).
- RATIONALE: This is now redundant with the multicollinearity Figure 4 and the original Section 7.1 prose.

**OP-6.3** DO NOT insert Example 5 (Leverage and Influence).
- RATIONALE: This example is 150 lines, contains a scratch-calculation passage ("Wait -- this doesn't show the expected pattern clearly"), and the Cook's distance table is formula exercise, not geometric insight. The existing prose + the leverage definition fix + Figure 4 caption suffice.

### Phase 7: Section 7 (When the Geometry Fails)

**OP-7.1** INSERT eigendecomposition prerequisite review.
- WHAT: Insert the eigendecomposition review remark.
- WHERE: After the "What multicollinearity means" paragraph (approximately line 708), before "The eigenvalue perspective" paragraph.
- SOURCE: `round3_pedagogy.tex`, Prerequisite 2 (lines 556-585).
- MODIFICATION: None.

**OP-7.2** INSERT Figure 4 (multicollinearity circle vs. pancake).
- WHAT: Insert the multicollinearity TikZ figure.
- WHERE: After the eigenvalue discussion in Section 7.1 (approximately line 740).
- SOURCE: `round2_figures.tex`, Figure 4 (lines 219-317).
- MODIFICATIONS:
  - Shorten the caption to remove the phrase "the column space collapses to a thin sliver" (already said in the main text). Replace with a brief 2-sentence caption.

**OP-7.3** INSERT Misconception 4 ("Multicollinearity = bad").
- WHAT: Insert the misconception box.
- WHERE: After Figure 4, before the OVB subsection.
- SOURCE: `round3_pedagogy.tex`, Misconception 4 (lines 348-370).
- MODIFICATION: Remove the last paragraph ("The geometric picture makes this clear...") -- it repeats what Section 7.1 already says. Keep the bullet list only. Estimated: ~15 lines.

**OP-7.4** CONDENSE Misconception 5 into a 2-sentence remark.
- WHAT: Instead of the full 25-line misconception box, add a 2-sentence remark at the end of the OVB subsection.
- WHERE: After line 781 (end of OVB discussion).
- SOURCE: Derived from `round3_pedagogy.tex`, Misconception 5 (lines 378-402).
- CONTENT:
  ```latex
  \begin{remark}
  Residual diagnostics cannot detect omitted variable bias. Both the
  ``short'' and ``long'' regressions produce residuals orthogonal to
  their respective column spaces---by construction, not by virtue of
  model correctness. The only safeguards against OVB are domain
  knowledge and causal reasoning.
  \end{remark}
  ```
- Estimated: ~6 lines.

**OP-7.5** INSERT transition sentence (Section 7 -> Section 8).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After OP-7.4, before Section 8 heading.
- SOURCE: `round3_pedagogy.tex`, Transition Section 6->7 (lines 714-720).
- MODIFICATION: None.

### Phase 8: Section 8 (Regularisation)

**OP-8.1** REPLACE the opening paragraph of Section 8.
- WHAT: Replace lines 788-790 (current opening: "When the column space is nearly degenerate...") with the regularisation warning box.
- WHERE: Lines 788-790.
- SOURCE: The specific transition paragraph from Conflict Resolution #5 above (from `round3_devils_advocate.md` lines 157-183, adapted).
- MODIFICATION: Use the exact text specified in Conflict Resolution #5 above.

**OP-8.2** SHORTEN the Ridge "Geometric interpretation" paragraph.
- WHAT: Shorten lines 825-832 to a 2-sentence reference to Figure 5.
- WHERE: Lines 825-832.
- SOURCE: N/A (editorial reduction).
- REPLACEMENT:
  ```latex
  \noindent\textbf{Geometric interpretation.}
  The Ridge solution is the point where the smallest RSS contour
  ellipsoid is tangent to the $L^2$ sphere
  $\|\bm{\beta}\|^2 \le t$ (Figure~\ref{fig:ridge-lasso}).
  Because the sphere has no corners, the tangent point generically
  has all coefficients nonzero.
  ```

**OP-8.3** INSERT Figure 5 (Ridge vs. LASSO constraint regions).
- WHAT: Insert the Ridge/LASSO TikZ figure.
- WHERE: After the LASSO subsection (approximately line 860), before the Comparison subsection.
- SOURCE: `round2_figures.tex`, Figure 5 (lines 323-395).
- MODIFICATION: None.

**OP-8.4** INSERT Stop-and-Think 7 (why LASSO corners attract).
- WHAT: Insert the S&T box.
- WHERE: After Figure 5, before the Comparison subsection.
- SOURCE: `round3_pedagogy.tex`, S&T 7 (lines 221-246).
- MODIFICATION: None.

**OP-8.5** INSERT Example 6 (Ridge shrinkage, shortened).
- WHAT: Insert the Ridge eigendecomposition example.
- WHERE: After the Comparison subsection (approximately line 878), before the Gaussian prerequisite.
- SOURCE: `round2_examples.tex`, Example 6 (lines 611-713).
- MODIFICATIONS:
  - Delete the "Verification for lambda=1" block (lines 672-683) -- students can verify this themselves.
  - Delete the "Geometric picture" paragraph (lines 694-704) -- it restates the table.
  - Estimated result: ~70 lines.

**OP-8.6** INSERT telescope analogy.
- WHAT: Insert the telescope analogy paragraph for regularisation.
- WHERE: After Example 6, before the Gaussian prerequisite remark.
- SOURCE: `round3_pedagogy.tex`, Analogy 2 (lines 440-462).
- MODIFICATION: Shorten to the first two paragraphs only (the telescope + tightening the mount). Cut the Ridge/LASSO elaboration (lines 454-462) -- too long, and the distinction is already made by Figure 5. Estimated: ~12 lines.

**OP-8.7** INSERT Gaussian prerequisite remark.
- WHAT: Insert the "Where the Gaussian enters" prerequisite.
- WHERE: After the telescope analogy, before Section 9.
- SOURCE: `round3_pedagogy.tex`, Prerequisite 3 (lines 595-631).
- MODIFICATION: None.

**OP-8.8** INSERT transition sentence (Section 8 -> Section 9).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After the Gaussian prerequisite remark, before Section 9 heading.
- SOURCE: `round3_pedagogy.tex`, Transition Section 7->8 (lines 728-735).
- MODIFICATION: None.

### Phase 9: Section 9 (F-test)

**OP-9.1** INSERT Figure 6 (F-test gap between projections).
- WHAT: Insert the F-test TikZ figure.
- WHERE: After the F-statistic definition (approximately line 920), before the confidence ellipsoids subsection.
- SOURCE: `round2_figures.tex`, Figure 6 (lines 401-498).
- MODIFICATION: None.

**OP-9.2** INSERT transition sentence (Section 9 -> Section 10).
- WHAT: Insert the italicised transition paragraph.
- WHERE: After the confidence ellipsoids subsection, before Section 10.
- SOURCE: `round3_pedagogy.tex`, Transition Section 8->9 (lines 743-749).
- MODIFICATION: None.

### Phase 10: Section 11 (Rosetta Stone)

**OP-10.1** REPLACE Rosetta Stone table entries for Ridge and LASSO.
- WHAT: Change "Constrained projection (sphere)" to "Constrained optimisation (sphere)" and "Constrained projection (diamond)" to "Constrained optimisation (diamond)".
- WHERE: In the Rosetta Stone table (Section 10, approximately lines 1030-1050).
- SOURCE: Conflict Resolution #5.
- MODIFICATION: Search-and-replace within the table.

### Phase 11: Appendix

**OP-11.1** CREATE new Appendix section.
- WHAT: Add `\appendix` and a new section "Proofs for the Mathematically Curious" at the end of the document, before `\end{document}`.
- WHERE: After Section 10 (Rosetta Stone), before `\end{document}`.
- SOURCE: Assembled from round2_math.tex.
- CONTENT:
  ```latex
  \appendix
  \section{Proofs for the Mathematically Curious}\label{app:proofs}

  These proofs are included for completeness and for readers who want
  to verify the foundations. They are not required for following the
  main narrative.
  ```

**OP-11.2** INSERT Projection Theorem proof into appendix.
- WHAT: Insert the full Projection Theorem proof.
- WHERE: In the appendix, after the appendix introduction.
- SOURCE: `round2_math.tex`, Item 1 (lines 20-93).
- MODIFICATION: Add a header: `\subsection{Proof of the Projection Theorem (Theorem~\ref{thm:projection})}`.

**OP-11.3** INSERT Characterisation Theorem statement and proof into appendix.
- WHAT: Insert the full Characterisation Theorem (statement + proof).
- WHERE: In the appendix, after the Projection Theorem proof.
- SOURCE: `round2_math.tex`, Item 4 (lines 304-381) -- theorem statement and proof only; the remark is already inline per OP-3.2.
- MODIFICATION: Add a header: `\subsection{Characterisation of Orthogonal Projections (Theorem~\ref{thm:proj-char})}`.

**OP-11.4** INSERT h_ii >= 1/n Cauchy-Schwarz derivation into appendix.
- WHAT: Insert the full Cauchy-Schwarz derivation for the leverage bound.
- WHERE: In the appendix, after the Characterisation Theorem proof.
- SOURCE: `round2_math.tex`, Item 5b (lines 435-448).
- MODIFICATION: Add a header: `\subsection{Proof that $h_{ii} \ge 1/n$ when an intercept is present (Remark~\ref{rem:hii-intercept})}`.

### Phase 12: Arithmetic corrections

**OP-12.1** APPLY Example 3 arithmetic correction.
- WHAT: In Example 3 (inserted in OP-5.2), ensure Step B3 uses the corrected values.
- WHERE: Within the inserted Example 3 content.
- SOURCE: `round3_verification.tex`, Part D, Correction 1 (lines 517-546).
- DETAILS:
  - Change `(\bX_1^\top\bX_1)^{-1}\bX_1^\top\by = (2, 4)` to `(2, 2)`.
  - Change projection from `(6,2,6,2)` to `(4,2,4,2)`.
  - Change residualised y from `(-4, 1, 0, -1)` to `(-2, 1, 2, -1)`.
  - Update Step B4 numerator: `(-1/2)(-2) + (1/2)(1) + (1/2)(2) + (-1/2)(-1) = 1 + 1/2 + 1 + 1/2 = 3`.

**OP-12.2** Note: Example 4 (Multicollinearity) is CUT entirely, so Correction 2 from round3_verification.tex is moot.

### Phase 13: Final editorial pass

**OP-13.1** SEARCH-AND-DESTROY redundant "shadow of shadow" occurrences.
- WHAT: After all insertions, grep for "shadow of a shadow" and "projecting twice". Ensure it appears exactly once, in the Geometric meaning paragraph (OP-3.1). Remove all other occurrences.

**OP-13.2** SEARCH-AND-DESTROY redundant "influence = leverage x surprise" restatements.
- WHAT: Ensure this formula/phrase appears only in the Section 6 Key Insight box. Remove narrative restatements elsewhere.

**OP-13.3** VERIFY the Gauss-Markov label.
- WHAT: Confirm that the label is `\label{thm:gm}` (not `thm:gm-full`) and that all `\ref{thm:gm}` references resolve.

**OP-13.4** ADD subtitle to title block.
- WHAT: Add the document identity subtitle.
- WHERE: In the `\maketitle` block (lines 110-115).
- CONTENT: `\subtitle{Supplementary notes for the lecture on linear regression}`
  (or use `\vspace{0.5em}{\large\itshape Supplementary notes...}` if `\subtitle` is not defined).

**OP-13.5** VERIFY line count.
- WHAT: After all operations, count lines. Target: 1550-1650 main body, plus ~250 appendix.
- If over budget, cut the telescope analogy and the shadow-sharpness analogy first (they are nice-to-have, not essential).
- If under budget, consider reinstating Example 4 (Multicollinearity) with corrections from round3_verification.tex, shortened to ~60 lines by removing the "self-correction" passage and the detailed determinant computation.

---

## Summary of What Gets In, What Gets Cut

### IN (main body):
- Round 3 revised prologue (with stripped roadmap)
- 4 examples: Ex 1 (shortened), Ex 2, Ex 3 (corrected), Ex 6 (shortened)
- 4 Stop-and-Think boxes: S&T 1, 3, 4, 7
- 3 Misconception boxes: Misc 1, 2, 4
- 2 Analogies: telescope, shadow-sharpness
- 2 inline proofs: Gauss-Markov (full), FWL (full)
- 6 TikZ figures
- 2 prerequisite reviews: eigendecomposition, Gaussian
- 8 transition sentences
- New subsections: adjusted R^2, degrees of freedom
- Standing assumption box (full column rank)
- Regularisation warning box (honest framing)
- All fixes: leverage definition, geometric meaning paragraph, SST intercept remark
- Rosetta Stone table corrections

### IN (appendix):
- Projection Theorem proof
- Characterisation Theorem (statement + proof)
- Cauchy-Schwarz derivation for h_ii >= 1/n

### CUT:
- Example 4 (Multicollinearity) -- redundant with existing prose + figure
- Example 5 (Leverage) -- too long, scratch-calculation passage
- Stop-and-Think 2 (leverage calculation) -- trivial
- Stop-and-Think 5 (ranking influence) -- covered by prose
- Stop-and-Think 6 (Ridge limits) -- covered by Example 6
- Misconception 3 (controlling for) -- too long (40 lines)
- Misconception 5 (clean residuals rule out OVB) -- condensed to 6-line remark
- Movie-screen analogy (FWL) -- redundant with existing room analogy
- Hearing-test analogy (F-test) -- too cute, adds length
- Loewner ordering prerequisite -- unnecessary for target audience
- Degrees-of-freedom bookkeeping remark -- textbook material
- Adjusted R^2 algebraic reading -- formula manipulation
- "Let us begin." -- cliche
- Roadmap geometric-insight sentences -- let sections deliver their own punchlines
- Various redundant restatements (shadow of shadow 3x, influence formula 2x, multicollinearity metaphor 1x)
