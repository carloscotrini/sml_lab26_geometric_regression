# Round 3: Cross-Critique Summary

## Files produced:
- `round3_prologue.tex` — Revised prologue (historian, pedagogy, literary editor critique)
- `round3_verification.tex` — Math verification with 2 errors found and corrected
- `round3_pedagogy.tex` — All pedagogical additions (Stop&Think, misconceptions, analogies, transitions)
- `round3_devils_advocate.md` — Ruthless critique of the whole project

## Key findings:

### Prologue (Round 3 revision):
- Fixed: "barely one percent" → "barely three percent" of orbit
- Added: contrast with other astronomers' failed predictions (10+ degrees off)
- Removed: "The clouds parted" (fiction), "Let us begin" (cliché)
- Fixed: flashlight shines onto "table" not "wall" (physical consistency)
- Simplified: Projection Theorem to finite-dimensional case in prologue
- Consolidated: roadmap from 7 to 5 items

### Math verification:
- Example 3 (FWL): arithmetic error in (X₁'X₁)⁻¹X₁'y — should be (2,2)' not (2,4)'
- Example 4 (Multicollinearity): perturbed solution off by factor ~1.5
- All 4 proofs verified CORRECT and complete
- Label suggestion: use \label{thm:gm} for replacement Gauss-Markov theorem
- Corrected LaTeX provided

### Pedagogy boxes:
- 7 "Stop and Think" boxes written with placement instructions
- 5 misconception Warning boxes written
- 4 analogies (movie-screen, telescope, shadow-sharpness, hearing-test) written
- 3 prerequisite reviews (Loewner ordering, eigendecomposition, Gaussian) written
- 9 transition sentences between sections written

### Devil's Advocate concerns:
1. LENGTH: Combined document ~2700 lines (2.5x original). Must cut ~400 lines.
2. IDENTITY CRISIS: Document doesn't know if it's lecture notes, reference text, or textbook
3. TONE: Gauss drama → graduate analysis → chatty textbook = three incompatible registers
4. REDUNDANCY: "shadow of shadow = itself" appears 4x; multicollinearity metaphor 3x; influence formula 3x
5. REGULARISATION: Honestly acknowledge Ridge/LASSO break the projection framework
6. STILL MISSING: Intercept's geometric role, MLE connection, p>n regime, exercises
7. SPECIFIC CUTS: 5 passages in original that can be replaced by improved versions

## Decisions for Round 4:
- Fix the 2 arithmetic errors
- Address the identity crisis: target "lecture companion" for undergrads (90-min read)
- Move Projection Theorem proof and Characterisation Theorem to appendix
- Cut redundancies (consolidate repeated insights)
- Reframe regularisation section honestly
- Integrate all pieces into a coherent document structure
