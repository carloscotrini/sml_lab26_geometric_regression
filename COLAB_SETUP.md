# COLAB_SETUP.md — Colab Installation Convention

## The Problem

This course ships as a GitHub repo containing a custom Python package (`regression_geometry`) and 11 Jupyter notebooks. The notebooks import from the package. In a local JupyterLab environment, the student runs `pip install -e .` once and everything works. In Google Colab, the package doesn't exist — it must be installed at the top of every notebook.

## The Solution

Every notebook's **Cell 1** must begin with a Colab-aware installation block. This block:
1. Detects whether the notebook is running in Colab
2. If yes, installs the package from GitHub
3. If no, assumes the package is already installed locally
4. Works silently — the student doesn't need to understand it

## The Standard Setup Cell

**Every notebook must use this exact Cell 1 pattern.** Copy it verbatim. Do not improvise.

```python
# ============================================================
# Notebook NN: "[Title]"
# Regression from the Inside: Seeing the Geometry of Linear Models
# ============================================================

# --- Environment setup (run this cell first) ---
import sys

# Install regression_geometry package if not available
try:
    import regression_geometry
except ImportError:
    # Running in Colab or fresh environment — install from GitHub
    print("Installing regression_geometry package...")
    !pip install -q git+https://github.com/YOUR_USERNAME/regression-geometry-course.git
    print("Done! If you see import errors below, restart the runtime (Runtime → Restart) and run this cell again.")

# --- Standard imports ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import linalg
from scipy import stats

import statsmodels.api as sm
from statsmodels.stats.outliers_influence import OLSInfluence

from regression_geometry.core import ColumnSpace, Projection, HatMatrix, Ellipsoid
from regression_geometry.core import frisch_waugh_lovell, angle_between, demean
from regression_geometry.data import load_meridian
from regression_geometry.colors import *

# --- Rendering backend toggle ---
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

# --- Reproducibility ---
np.random.seed(42)
```

## Rules

1. **Replace `YOUR_USERNAME`** with the actual GitHub username or org before release. During development, leave it as a placeholder — the Integration Pass (Issue 10) will do a global find-and-replace.

2. **The `!pip install -q` line uses the `!` shell syntax** which works in both Colab and Jupyter. The `-q` flag keeps output minimal.

3. **The try/except pattern** means local users who already have the package installed see no installation output. Colab users see one line of install output.

4. **Restart warning:** After first install in Colab, the runtime sometimes needs a restart for imports to work. The print message tells the student what to do. This is a known Colab quirk.

5. **Do not add `%pip install` inside the try block.** Use `!pip install`. The `%pip` magic has inconsistent behavior across Jupyter versions.

6. **Not every notebook needs every import.** Notebook 0 (Python prereqs) doesn't need `ColumnSpace` or `load_meridian`. Trim imports to what's actually used — but keep the installation block and the rendering toggle in every notebook.

## What About the Meridian CSV?

The `load_meridian()` function loads the CSV from within the installed package. When installed via `pip install git+...`, the CSV is included in the package (it's inside `regression_geometry/data/meridian.csv`). This works automatically — the student doesn't need to download the CSV separately.

**Important for `pyproject.toml`:** The package must include the CSV as package data. Verify that `pyproject.toml` or `setup.cfg` includes:

```toml
[tool.setuptools.package-data]
regression_geometry = ["data/*.csv"]
```

If this is missing, `load_meridian()` will fail in Colab because the CSV won't be bundled with the pip install.

## Testing Colab Compatibility

During the Testing Pass (Issue 11), verify for every notebook:
1. Open a fresh Colab runtime (no previous installs)
2. Run Cell 1 — the package installs without errors
3. Run all remaining cells — no ImportErrors
4. Restart runtime, run Cell 1 again — still works (no stale state)
