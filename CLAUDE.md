# Claude Context — sml_lab26_geometric_regression

## Live site
The `visualizations/` folder is served via GitHub Pages at
**https://carloscotrini.github.io/sml_lab26_geometric_regression/**.
`.github/workflows/pages.yml` redeploys on every push to `main` — uploads
`visualizations/` as the Pages artifact. No build step.

## Lecture notes — multiple versions
- `lecture_notes/lecture_notes.tex` — original
- `lecture_notes/lecture_notes_v2.tex` — enriched version (34pp, on main, tracked PDF)
- `lecture_notes/lecture_notes_v3.tex` — **on branch `claude/improve-lecture-notes-GO0Ov`, not main**.
  This is where the 12 `\begin{vizspec}{…}` blocks live. They're
  purple-bordered tcolorbox specification cards, not working code.
  Search with `git show origin/claude/improve-lecture-notes-GO0Ov:lecture_notes/lecture_notes_v3.tex | grep -n vizspec`.

## The 12 visualizations
Each is a **self-contained** HTML file — D3.js v7 or Three.js loaded from CDN,
inline CSS+JS, no build. Files are `visualizations/01_*.html` through `12_*.html`
plus `index.html` (gallery). Built by dispatching 6 parallel sub-agents (2 viz each)
from the vizspec blocks.

## Visual design conventions (used consistently across all 12)
- Background: `#1a1a2e` (dark navy); gallery page: `#0f0f1a`
- Column space / predictors: **blue** `#4a90d9`
- Data vector `y` / active element: **gold** `#e6a817`
- Projection `ŷ`: **green** `#50c878`
- Residual `e`: **red** `#e74c3c` (dashed)
- Constraints / alternatives / eigendirections: **purple** `#9b59b6`
- Secondary / inactive: **gray** `#888`

Use Unicode math symbols directly (ŷ, β̂, ‖·‖, λ, θ) rather than MathJax —
keeps files small and loads instantly.

## Related repos the user works with (came up in session)
- `git_llm_lab` (eth-ainit-fs26/llm_lab) — CAS BMAI LLM presentation proposals
- `git_sml_experiment/Bayesianism_study` — different lecture notes (v3 there is
  NOT the same as v3 here; naming collision caused confusion once)

## Gotchas
- `vizspec` environment is **only** defined on branch `claude/improve-lecture-notes-GO0Ov`.
  Searching main for it returns nothing — fetch first.
- The PDF `lecture_notes_v2.pdf` is tracked in git (not gitignored); recompile
  and commit when the `.tex` changes.
