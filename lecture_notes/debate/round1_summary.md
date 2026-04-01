# Round 1: Initial Reviews

## Agent A: Pedagogy & Accessibility
- 5 cognitive-load hotspots needing worked examples (after Projection Theorem, FWL proof, eigenvalue discussion, Ridge shrinkage, F-statistic)
- 3 prerequisite gaps: Loewner ordering is graduate-level, eigendecomposition review needed, Gaussian assumption needs introduction
- 5 misconception Warning boxes: "projection validates model," "R²=0.8 means good," "controlling for = holding constant," "multicollinearity = bad model," "clean residuals rule out OVB"
- 7 "Stop and Think" active learning boxes proposed
- 4 new analogies: movie-screen (FWL), telescope (regularisation), shadow-sharpness (R²), hearing-test (F-test)
- Concrete-before-abstract violations: OLS definition before any calculation, annihilator M introduced abstractly, LASSO before diamond intuition
- Difficulty spikes: FWL arrives too fast after Pythagoras, eigenvalue analysis too compressed, confidence ellipsoids should be marked optional

## Agent B: Mathematical Rigor (inferred from synthesis)
- Projection Theorem stated without proof — needs finite-dimensional proof
- FWL proof hand-waves the key algebra — needs to show the block elimination
- Gauss-Markov proof has gaps — the D*X=0 step is not derived
- Implicit assumptions: full column rank used everywhere but stated once; Gaussian errors appear without introduction; intercept required for SST=SSR+SSE
- Missing: adjusted R², characterization theorem (symmetric+idempotent ⟺ projection), Type I ANOVA connection
- Notation issue: h_ii ≥ 1/n vs h_ii ≥ 0 inconsistency; Rosetta Stone uses un-demeaned vectors
- The claim "symmetry treats all directions equally" is misleading

## Agent C: Visualization
- Only 1 figure for a geometry document — at least 5 more needed
- Top missing diagrams: flashlight metaphor, FWL two-step, multicollinearity comparison, Ridge vs LASSO constraint regions
- Red-green color pair is colorblind-unfriendly
- Need thought experiments for building 3D intuition

## Agent D: Storytelling & Narrative
- Opening needs stakes — Gauss/Ceres story (1801, lost asteroid found by least squares)
- Narrative arc is flat — sections feel episodic, need connecting questions
- Surprise moments underplayed: R²=cos²θ and Pythagoras decomposition should hit hard
- Ending should circle back to opening (narrative ring)
- Gauss vs Legendre priority dispute adds drama
- Fisher's geometric intuition quote: "Think of n dimensions..."

## Agent E: Devil's Advocate
- Geometric metaphor BREAKS for regularisation — Ridge/LASSO are NOT projections
- Zero numerical examples is the biggest gap
- Missing: MLE connection, degrees of freedom, weighted least squares, rank-deficient case
- "The formula is a recipe for dropping a perpendicular" is misleading (it computes coordinates)
- Students will get lost at: "closed subspace," Loewner ordering, elided FWL proof

## Consensus
1. Worked numerical examples (#1 priority)
2. Gauss/Ceres opening
3. More diagrams (at least 4)
4. FWL proof needs full algebra
5. Gaussian assumptions must be introduced before inference
6. R²=cos²θ and Pythagoras need dramatic buildup
