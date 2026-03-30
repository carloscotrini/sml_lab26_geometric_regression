"""Canonical color palette for all course visualizations.

These colors are inviolable. See SPEC.md §10.1.
Both plots.py and interactive.py import from here.
"""

# Primary semantic colors
COLUMN_SPACE = '#3B82F6'   # Blue — planes, subspaces, basis vectors
RESPONSE_Y = '#F59E0B'     # Gold — the data vector y
PROJECTION = '#10B981'     # Green — fitted values, ŷ
RESIDUAL = '#EF4444'       # Red — residuals, errors
CONSTRAINT = '#8B5CF6'     # Purple — regularization boundaries
SECONDARY = '#6B7280'      # Gray — axes, labels, grids

# Alpha values for translucent surfaces
SURFACE_ALPHA = 0.25
VECTOR_ALPHA = 0.9

# Matplotlib style overrides
FIGURE_BG = 'white'
AXES_BG = 'white'
FONT_FAMILY = 'sans-serif'
TITLE_SIZE = 14
LABEL_SIZE = 11
TICK_SIZE = 9
