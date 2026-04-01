# Round 3: Devil's Advocate Critique

## 1. Length Concern: This Is Becoming a Textbook

**The numbers are damning.** The original document is 1,077 lines. The new
additions total approximately 2,025 lines of content (163 + 651 + 713 + 498),
of which roughly 300 lines are comments and insertion directives, leaving ~1,725
lines of actual LaTeX. Even accounting for the ~100 lines the new content is
meant to *replace* (the old Gauss-Markov sketch, the old FWL proof, the old
leverage definition, the old "geometric meaning" paragraph), the combined
document lands in the range of **2,700 lines**.

That is 2.5x the original. This is no longer "lecture notes." It is a
monograph. A student handed this before a 90-minute lecture will not read it.
They will skim the first section, skip to the summary table, and ignore
everything in between.

**What should be CUT to stay under ~1,400 lines (a 30% expansion, which is
already generous):**

- The Projection Theorem proof (round2_math, Item 1, ~70 lines). This is
  a standard real-analysis result. A one-line reference to any linear algebra
  textbook suffices. Students at the level of this course have seen it or can
  look it up. The proof adds rigour but zero geometric intuition, which is the
  document's stated purpose.

- The Characterisation Theorem for orthogonal projections (round2_math, Item 4,
  ~80 lines). Again, this is important mathematics, but it is a supporting
  lemma, not a geometric insight. The remark after it is excellent; keep the
  remark (10 lines), cut the proof (50 lines).

- Example 5 (Leverage and Influence, ~150 lines). This example is *far* too
  long. The mid-example "Wait---this doesn't show the expected pattern clearly.
  Let me re-examine" passage (lines 548-560 of round2_examples.tex) reads like
  a scratch calculation that was never cleaned up. Either fix the example to
  flow cleanly or cut it to 60 lines by removing the Cook's distance table
  (which is a formula exercise, not a geometric insight).

- The degrees-of-freedom bookkeeping remark (round2_math, Item 7, last remark,
  ~20 lines). The d.f. decomposition $n-1 = (p-1) + (n-p)$ is stated in
  every introductory statistics textbook. The geometric insight is in the
  preceding paragraphs; this remark is bookkeeping redundancy.

- The adjusted R^2 subsection (round2_math, Item 6, ~50 lines). The algebraic
  reading is pure formula manipulation. Keep only the geometric reading (which
  is genuinely illuminating) and the definition. Cut the algebraic paragraph.

These cuts save approximately 350-400 lines and bring the document back toward
a manageable size.


## 2. Tone Inconsistency: The Gauss/Ceres Narrative vs. Theorem-Proof Style

The prologue (round2_prologue.tex) is vivid, dramatic, historically evocative
prose. "Then disaster struck." "The computation was ferocious." "The clouds
parted." This is excellent science writing.

Then the reader turns the page and hits:

> **Step 1: Existence.** Let $d = \inf_{s \in S} \|y - s\|$. Choose any
> $s_0 \in S$...

The tonal whiplash is severe. The prologue promises a story; the body delivers
a graduate analysis course. Neither register is wrong, but their juxtaposition
creates a document with a split personality.

**Specific whiplash moments:**

1. The prologue's "metaphor" box (flashlight/shadow/wall) is warm and
   accessible. The very next block is a formal Projection Theorem statement
   followed by a three-step existence-uniqueness proof using infimum arguments
   and the parallelogram law. The student who was happily following the
   flashlight metaphor has just been dropped into a cold pool.

2. The FWL section in the original has a lovely "three-dimensional room"
   analogy. The new FWL proof (round2_math, Item 2) is a page of block matrix
   elimination. These live side by side. The analogy reader and the proof reader
   are different students; only one of them is being served at any given moment.

3. The worked examples (round2_examples.tex) are in a third register: chatty
   textbook with "Takeaway" boxes. This is fine on its own but clashes with
   both the narrative prologue and the theorem-proof spine.

**Recommendation:** Pick a lane or mark the lanes explicitly. One option:
move all proofs to an appendix or to clearly marked "Proof (for the
mathematically curious)" blocks that students can skip without losing the
geometric story. The main text should sustain the intuitive register
established by the prologue.


## 3. Redundancy: The Same Insight Stated Three (or Four) Times

The document has a serious echo-chamber problem. The following geometric
insight is stated in at least four places:

> "Idempotency means the shadow of a shadow is itself."

- Original, Section 3, after Proposition (Properties of H): "Idempotency
  says: projecting twice is the same as projecting once."
- round2_math, Item 5c, the replacement paragraph: "Idempotency says: *the
  shadow of a shadow is itself.*"
- round2_examples, Example 1, line 112: "Applying the projection a second time
  does nothing---the shadow of a shadow is itself."
- round2_math, Item 4, Remark: "Idempotency makes it a projection; symmetry
  makes it orthogonal."

This repetition is not reinforcement; it is padding. The phrase loses its
punch by the third occurrence.

**Other redundancies:**

- The "multicollinearity = pancake" metaphor appears in (a) the original
  Section 7.1, (b) Example 4 (round2_examples), and (c) Figure 4's caption
  (round2_figures). The Example and the Figure caption essentially restate the
  original section's analogy with numbers attached.

- The "influence = leverage x surprise" formula is in (a) the original Key
  Insight box in Section 6, (b) Example 5's "Takeaway" in round2_examples,
  and (c) the Cook's distance definition block in the original. Three times.

- The roadmap in the prologue previews every section's geometric insight. Each
  section then opens with roughly the same insight again. And each example
  closes with a "Takeaway" that... states the same insight a third time.

**Recommendation:** The roadmap should be a *teaser*, not a summary. Cut the
one-sentence geometric descriptions from the roadmap enumeration (e.g., replace
"$R^2$ turns out to equal the squared cosine of the angle between $y$ and
$\hat{y}$" with just "How good is the fit?"). Let the section itself deliver
the punchline for the first time.


## 4. The Regularisation Problem: Ridge and LASSO Are NOT Projections

The document's thesis is "regression = projection." The Rosetta Stone table in
Section 10 lists Ridge as "Constrained projection (sphere)" and LASSO as
"Constrained projection (diamond)." But this is misleading. Ridge and LASSO
are *not* projections in any standard mathematical sense:

- The Ridge operator $(\mathbf{X}^\top\mathbf{X} + \lambda\mathbf{I})^{-1}
  \mathbf{X}^\top$ is neither idempotent nor symmetric in the data space.
  It does not satisfy the characterisation theorem (round2_math, Item 4)
  that the document itself introduces.
- The LASSO solution is not even linear in $\mathbf{y}$.

The current Section 8 does contain the sentence "Neither Ridge nor LASSO is an
orthogonal projection" (line 876), but this is a throwaway line buried after
two subsections that frame both methods in projection language ("constraining
the shadow," "constrained projection"). A student who has been trained for
seven sections to think "regression = projection" will naturally assume that
regularisation is a kind of projection too. The single disclaimer sentence is
too little, too late.

**Suggested LaTeX rewording for Section 7 (Regularisation):**

Replace the current opening paragraph:

```latex
% CURRENT (lines 788-790):
% When the column space is nearly degenerate, the OLS projection is
% ``optimal'' but unstable. Regularisation deliberately introduces bias
% to gain stability.

% PROPOSED REPLACEMENT:
\begin{warning}
\textbf{Where the projection framework reaches its limits.}
Everything in Sections 1--7 was a consequence of the Projection Theorem:
find the closest point in a subspace.  Ridge and LASSO are \emph{not}
projections.  They deliberately move away from the closest point,
accepting bias in exchange for stability.

The hat matrix $\bH_{\text{ridge}} = \bX(\bX^\top\bX+\lambda\bI)^{-1}\bX^\top$
is \emph{not} idempotent ($\bH_{\text{ridge}}^2 \ne \bH_{\text{ridge}}$) and
is \emph{not} an orthogonal projection onto any subspace.
By the Characterisation Theorem (Theorem~\ref{thm:proj-char}), this means
Ridge regression does not ``drop a perpendicular''---it \emph{pulls the
shadow inward}, toward the origin, away from the foot of the perpendicular.

The geometric language of shadows and right angles served us well for OLS.
For regularisation, we need a different picture: that of \textbf{constrained
optimisation}, where the solution is determined not by orthogonality but by
the tangency between an objective function's level sets and a constraint region.
\end{warning}
```

Additionally, the Rosetta Stone table entries for Ridge and LASSO should be
changed from "Constrained projection" to something honest, e.g.:

| Ridge | Constrained optimisation (sphere) | Shrink toward origin |
| LASSO | Constrained optimisation (diamond) | Corner solutions = sparsity |


## 5. What Is STILL Missing After All Additions

Even after 2,000 lines of new material, several gaps remain:

1. **No treatment of the intercept's geometric role.** The document assumes an
   intercept throughout (the SST = SSR + SSE decomposition requires it, as
   round2_math Item 5d correctly notes). But it never explains *what the
   intercept does geometrically*: including a column of ones in $\mathbf{X}$
   means the column space contains the "all-equal" direction, which forces
   the projection to pass through the sample mean. This is fundamental and
   missing.

2. **No connection to maximum likelihood / Gaussian assumptions.** The document
   mentions Gaussian assumptions for the F-test (line 909) but never explains
   why OLS = MLE under Gaussian errors, or what the Gaussian assumption adds
   beyond Gauss-Markov. A single remark would suffice.

3. **No visual for the Pythagoras decomposition.** There are TikZ figures for
   the flashlight, for projection in R^3, for FWL, for multicollinearity, for
   Ridge/LASSO, and for the F-test. But there is no figure for the Pythagorean
   decomposition SST = SSR + SSE, which is arguably the most important single
   equation in applied statistics. This is a surprising omission given that the
   document already has six figures.

4. **No discussion of what happens when n < p.** The standing assumption
   (round2_math, Item 5a) explicitly requires $n \ge p$ and full column rank.
   But modern statistics lives in the $p > n$ world. A single paragraph
   acknowledging this and pointing toward PCA / penalised methods would
   prevent the document from feeling dated.

5. **No exercises or self-check questions.** Lecture notes without exercises
   are a monologue. Even three or four "verify this" problems would transform
   the document from something students read passively into something they
   engage with.


## 6. The Single Biggest Remaining Problem

**The document does not know what it is.**

Is it a self-contained reference text (like Christensen's *Plane Answers*)?
Then it needs more proofs, more exercises, and an index. Is it lecture notes
for a 90-minute class? Then it is three times too long and needs ruthless
cutting. Is it a supplementary reading to accompany slides? Then the prologue
is perfect but the theorem-proof blocks are redundant with any standard
textbook.

This identity crisis manifests everywhere:
- The prologue is written for the widest audience (anyone with calculus).
- The proofs assume comfort with infimum arguments and the parallelogram law
  (upper-division real analysis).
- The examples assume the reader needs to be shown how to multiply a 2x2
  matrix (introductory linear algebra).

These three audiences do not overlap. The document tries to serve all of them
and ends up with a jarring mix of hand-holding and abstraction.

**The fix:** Decide on the target student. If it is a second-year undergraduate
in a statistics/ML course (which the original tone suggests), then:
- Cut all proofs except the Gauss-Markov proof (which has genuine geometric
  content).
- Keep the worked examples but shorten them by 40%.
- Keep the prologue, the figures, the Key Insight boxes, the Warning boxes,
  and the Rosetta Stone table.
- Move everything else to an appendix labelled "For the curious."

This would produce a ~50-page document that a student might actually read
before class.


## 7. Specific Cuts in the ORIGINAL Document

Now that better versions exist in the new content, the following passages in
`lecture_notes.tex` can be shortened or removed:

1. **Lines 417-430 (Gauss-Markov "Geometric proof sketch"):** Replace entirely
   with the full proof from round2_math Item 3. The current sketch is too
   compressed to be useful as a proof and too formal to be useful as intuition.
   It sits in an uncomfortable middle ground. The new version is complete and
   has a far superior geometric remark.

2. **Lines 495-509 (FWL proof):** Replace with the full proof from round2_math
   Item 2. The current proof says "solve the first block for $\hat\beta_1$ and
   substitute into the second. After simplification... one obtains (5.1)." This
   is a proof by handwaving. Either give the full derivation (as the new
   version does) or delete the proof entirely and just state the theorem with
   a geometric explanation.

3. **Lines 590-595 (Leverage definition with the incorrect bound):** The
   original states $1/n \le h_{ii} \le 1$ without qualification. Round2_math
   Item 5b correctly identifies that $1/n$ requires an intercept. The original
   definition should be replaced by the corrected version.

4. **Lines 700-706 (Multicollinearity "concrete example"):** This paragraph
   ($x_2 = x_1 + \epsilon$, then "on Monday you might get $(5,3)$; on Tuesday
   $(50, -42)$") is a verbal sketch of exactly what Example 4
   (round2_examples) demonstrates numerically. Now that the worked example
   exists, this paragraph is redundant. Either cut it entirely or reduce it to
   a single sentence pointing to Example 4.

5. **Lines 825-832 (Ridge "Geometric interpretation" paragraph):** This
   paragraph describes the constrained-optimisation picture (sphere, RSS
   contour ellipse touching the sphere). Figure 5 (round2_figures) now
   illustrates this far more effectively. The paragraph can be shortened to
   two sentences that reference the figure, rather than re-describing what the
   figure shows.


---

**Summary verdict:** The Round 2 additions are individually excellent---the
proofs are correct, the examples are well-chosen, the figures are beautiful.
But the document is drowning in its own ambition. The most urgent need is not
more content; it is an editorial pass that cuts 30-40% of the combined material,
resolves the tonal inconsistencies, eliminates the redundancies, and honestly
confronts the regularisation section's intellectual dishonesty about the
projection framework's limits.
