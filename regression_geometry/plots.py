"""Static Matplotlib visualization backend (Layer 1).

Every function returns a matplotlib.figure.Figure. None call plt.show().
All colors come from colors.py — no hardcoded hex values.

This module defines the canonical function signatures that interactive.py
must match exactly.
"""

from __future__ import annotations

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import art3d  # noqa: F401 — needed for 3D

from regression_geometry import colors
from regression_geometry.core import (
    ColumnSpace,
    Projection,
    HatMatrix,
    Ellipsoid,
    frisch_waugh_lovell,
    angle_between,
    demean,
)

# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

_TEXT_BBOX = dict(boxstyle='round', facecolor='white', alpha=0.8)


def _apply_style(fig: Figure) -> None:
    """Apply shared style settings to a figure."""
    fig.patch.set_facecolor(colors.FIGURE_BG)
    for ax in fig.axes:
        ax.set_facecolor(colors.AXES_BG)
        ax.tick_params(labelsize=colors.TICK_SIZE)


def _draw_right_angle_2d(ax, vertex, v1, v2, size=0.1):
    """Draw a small square at *vertex* indicating a right angle.

    Parameters
    ----------
    ax : matplotlib Axes (2D)
    vertex : array-like, length 2
    v1, v2 : unit-direction arrays (length 2) along the two legs
    size : float — side length of the square
    """
    vertex = np.asarray(vertex, dtype=float)
    v1 = np.asarray(v1, dtype=float)
    v2 = np.asarray(v2, dtype=float)
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-15 or n2 < 1e-15:
        return
    v1 = v1 / n1 * size
    v2 = v2 / n2 * size
    pts = [vertex, vertex + v1, vertex + v1 + v2, vertex + v2]
    square = plt.Polygon(pts, closed=True, fill=False,
                         edgecolor=colors.SECONDARY, linewidth=1.0)
    ax.add_patch(square)


def _draw_right_angle_3d(ax, vertex, v1, v2, size=0.1):
    """Draw a small square at *vertex* in 3-D indicating a right angle."""
    vertex = np.asarray(vertex, dtype=float)
    v1 = np.asarray(v1, dtype=float)
    v2 = np.asarray(v2, dtype=float)
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-15 or n2 < 1e-15:
        return
    v1 = v1 / n1 * size
    v2 = v2 / n2 * size
    pts = np.array([vertex, vertex + v1, vertex + v1 + v2, vertex + v2])
    poly = art3d.Poly3DCollection([pts], alpha=0.6,
                                   facecolor=colors.SECONDARY,
                                   edgecolor=colors.SECONDARY,
                                   linewidths=1.0)
    ax.add_collection3d(poly)


def _arrow_2d(ax, origin, vec, color, label=None, **kw):
    """Draw a 2-D arrow using annotate."""
    ox, oy = origin
    dx, dy = vec
    ax.annotate(
        '', xy=(ox + dx, oy + dy), xytext=(ox, oy),
        arrowprops=dict(arrowstyle='->', color=color, lw=2,
                        mutation_scale=15),
    )
    if label:
        mid_x = ox + dx * 0.5
        mid_y = oy + dy * 0.5
        ax.text(mid_x, mid_y, label, fontsize=colors.LABEL_SIZE,
                color=color, bbox=_TEXT_BBOX, ha='center', va='bottom')


def _arrow_3d(ax, origin, vec, color, label=None, **kw):
    """Draw a 3-D arrow using quiver."""
    o = np.asarray(origin, dtype=float)
    v = np.asarray(vec, dtype=float)
    ax.quiver(*o, *v, color=color, arrow_length_ratio=0.1,
              linewidth=2, alpha=colors.VECTOR_ALPHA)
    if label:
        tip = o + v
        ax.text(tip[0], tip[1], tip[2], f' {label}', fontsize=colors.LABEL_SIZE,
                color=color, bbox=_TEXT_BBOX)


def _setup_3d_ax(ax, elev=30, azim=45):
    """Common 3D axes setup."""
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel('$x_1$', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel('$x_2$', fontsize=colors.LABEL_SIZE)
    ax.set_zlabel('$x_3$', fontsize=colors.LABEL_SIZE)


def _draw_column_space_plane(ax, cs, scale=None):
    """Draw the column space as a translucent plane through the origin (3D).

    Works for n=3 only.
    """
    Q = cs.basis()  # shape (3, r)
    r = Q.shape[1]
    if scale is None:
        scale = 2.0
    if r == 1:
        # Line
        t = np.linspace(-scale, scale, 50)
        line = np.outer(t, Q[:, 0])
        ax.plot(line[:, 0], line[:, 1], line[:, 2],
                color=colors.COLUMN_SPACE, linewidth=2, alpha=0.7)
    elif r >= 2:
        # Plane spanned by first two basis vectors
        s = np.linspace(-scale, scale, 10)
        t = np.linspace(-scale, scale, 10)
        S, T = np.meshgrid(s, t)
        plane = (S[..., np.newaxis] * Q[:, 0] + T[..., np.newaxis] * Q[:, 1])
        ax.plot_surface(
            plane[:, :, 0], plane[:, :, 1], plane[:, :, 2],
            color=colors.COLUMN_SPACE, alpha=colors.SURFACE_ALPHA,
            edgecolor='none',
        )


# ===================================================================
# 3.1  Core Projection Visualizations
# ===================================================================

def plot_projection_3d(
    cs: ColumnSpace,
    y: np.ndarray,
    title: str = "Projection onto Column Space",
    figsize: tuple = (10, 8),
    views: str = "default",
    show_right_angle: bool = True,
    show_labels: bool = True,
    **kwargs,
) -> Figure:
    """The flagship visualization. Shows y, y_hat, e, and the column space in 3D.

    ONLY works when the column space can be embedded in R^3 — meaning n=3.

    Elements rendered:
    - Column space as a translucent blue plane (or line if rank 1)
    - y as a gold arrow from origin
    - y_hat as a green arrow from origin (on the plane)
    - e as a red arrow from y_hat to y
    - Right angle marker at the foot of the perpendicular
    - Labels for y, y_hat, e with their numerical values

    Parameters
    ----------
    cs : ColumnSpace — must have n=3
    y : np.ndarray, shape (3,)
    title : str
    figsize : tuple
    views : str — "default" for single view at (30, 45),
        "three_panel" for front/side/top-down, "top_down" for overhead
    show_right_angle : bool — draw the perpendicularity marker
    show_labels : bool — annotate vectors with names and values
    **kwargs : passed through (e.g. dpi)
    """
    y = np.asarray(y, dtype=float).ravel()
    proj = cs.project(y)
    y_hat = proj.y_hat
    e = proj.residuals

    # Determine auto-scale for column space plane
    vecs = np.array([y, y_hat])
    scale = float(np.max(np.abs(vecs))) * 1.3
    if scale < 1e-10:
        scale = 2.0

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}

    if views == "three_panel":
        fig = plt.figure(figsize=figsize, **dpi_kw)
        view_params = [
            (30, 45, "Default"),
            (0, 0, "Front"),
            (90, 0, "Top-down"),
        ]
        for i, (elev, azim, vtitle) in enumerate(view_params):
            ax = fig.add_subplot(1, 3, i + 1, projection='3d')
            _draw_column_space_plane(ax, cs, scale=scale)
            _arrow_3d(ax, [0, 0, 0], y, colors.RESPONSE_Y,
                      label='y' if show_labels else None)
            _arrow_3d(ax, [0, 0, 0], y_hat, colors.PROJECTION,
                      label='ŷ' if show_labels else None)
            _arrow_3d(ax, y_hat, e, colors.RESIDUAL,
                      label='e' if show_labels else None)
            if show_right_angle:
                _draw_right_angle_3d(ax, y_hat, -y_hat, e,
                                     size=scale * 0.06)
            _setup_3d_ax(ax, elev=elev, azim=azim)
            ax.set_title(vtitle, fontsize=colors.LABEL_SIZE)
        fig.suptitle(title, fontsize=colors.TITLE_SIZE)
    else:
        fig = plt.figure(figsize=figsize, **dpi_kw)
        ax = fig.add_subplot(111, projection='3d')
        _draw_column_space_plane(ax, cs, scale=scale)
        _arrow_3d(ax, [0, 0, 0], y, colors.RESPONSE_Y,
                  label='y' if show_labels else None)
        _arrow_3d(ax, [0, 0, 0], y_hat, colors.PROJECTION,
                  label='ŷ' if show_labels else None)
        _arrow_3d(ax, y_hat, e, colors.RESIDUAL,
                  label='e' if show_labels else None)
        if show_right_angle:
            _draw_right_angle_3d(ax, y_hat, -y_hat, e,
                                 size=scale * 0.06)
        if views == "top_down":
            _setup_3d_ax(ax, elev=90, azim=0)
        else:
            _setup_3d_ax(ax, elev=30, azim=45)
        ax.set_title(title, fontsize=colors.TITLE_SIZE)

        if show_labels:
            textstr = (f"||y|| = {np.linalg.norm(y):.2f}   "
                       f"||ŷ|| = {np.linalg.norm(y_hat):.2f}   "
                       f"||e|| = {np.linalg.norm(e):.2f}")
            fig.text(0.5, 0.02, textstr, ha='center',
                     fontsize=colors.LABEL_SIZE, bbox=_TEXT_BBOX)

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_relevant_triangle(
    cs: ColumnSpace,
    y: np.ndarray,
    j: int,
    title: str = None,
    figsize: tuple = (8, 6),
    show_beta: bool = True,
    show_se: bool = True,
    **kwargs,
) -> Figure:
    """The Relevant Triangle for coefficient j.

    Calls cs.relevant_triangle(y, j) to get the residualized vectors,
    then plots them in 2D. Works regardless of the ambient dimension n.

    Elements rendered:
    - y_resid as a gold arrow
    - xj_resid as a blue arrow
    - The projection of y_resid onto xj_resid as a green point/arrow
    - The residual as a red perpendicular
    - The angle between y_resid and xj_resid labeled
    - beta_j and SE(beta_j) displayed as text annotations

    Parameters
    ----------
    cs : ColumnSpace
    y : np.ndarray, shape (n,)
    j : int — column index in cs.X
    title : str — default "Relevant Triangle for x_{j}"
    figsize : tuple
    show_beta : bool
    show_se : bool
    **kwargs
    """
    if title is None:
        title = f"Relevant Triangle for $x_{{{j}}}$"

    tri = cs.relevant_triangle(y, j)
    y_resid = tri['y_resid']
    xj_resid = tri['xj_resid']
    beta_j = tri['beta_j']
    se_j = tri['se_j']
    ang = tri['angle']

    # Project into 2D using xj_resid direction and the orthogonal complement
    xj_norm = np.linalg.norm(xj_resid)
    if xj_norm < 1e-15:
        e1 = np.zeros_like(xj_resid)
        e1[0] = 1.0
    else:
        e1 = xj_resid / xj_norm

    # Orthogonal direction in the plane of (y_resid, xj_resid)
    y_comp = y_resid - np.dot(y_resid, e1) * e1
    y_comp_norm = np.linalg.norm(y_comp)
    if y_comp_norm < 1e-15:
        e2 = np.zeros_like(e1)
        idx = 0 if abs(e1[0]) < 0.9 else 1
        e2[idx] = 1.0
        e2 = e2 - np.dot(e2, e1) * e1
        n2 = np.linalg.norm(e2)
        if n2 > 1e-15:
            e2 = e2 / n2
    else:
        e2 = y_comp / y_comp_norm

    # 2D coordinates
    xj_2d = np.array([np.dot(xj_resid, e1), np.dot(xj_resid, e2)])
    yr_2d = np.array([np.dot(y_resid, e1), np.dot(y_resid, e2)])
    proj_2d = np.array([np.dot(y_resid, e1), 0.0])  # projection onto xj line

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    # Draw arrows from origin
    _arrow_2d(ax, (0, 0), yr_2d, colors.RESPONSE_Y, label='$y_{resid}$')
    _arrow_2d(ax, (0, 0), xj_2d, colors.COLUMN_SPACE, label=f'$x_{{{j},resid}}$')
    _arrow_2d(ax, (0, 0), proj_2d, colors.PROJECTION, label='proj')

    # Residual: from projection to y_resid
    resid_vec = yr_2d - proj_2d
    _arrow_2d(ax, proj_2d, resid_vec, colors.RESIDUAL, label='resid')

    # Right angle marker at projection foot
    if np.linalg.norm(resid_vec) > 1e-10 and np.linalg.norm(proj_2d) > 1e-10:
        ra_size = max(np.linalg.norm(yr_2d), np.linalg.norm(xj_2d)) * 0.05
        _draw_right_angle_2d(ax, proj_2d, -proj_2d, resid_vec, size=ra_size)

    # Angle arc
    if ang > 1e-6:
        arc_r = min(np.linalg.norm(yr_2d), np.linalg.norm(xj_2d)) * 0.2
        if arc_r > 1e-10:
            theta1 = 0.0
            theta2 = np.degrees(ang)
            arc = mpatches.Arc((0, 0), 2 * arc_r, 2 * arc_r,
                               angle=0, theta1=theta1, theta2=theta2,
                               color=colors.SECONDARY, linewidth=1.5)
            ax.add_patch(arc)
            mid_ang = ang / 2
            ax.text(arc_r * 1.3 * np.cos(mid_ang),
                    arc_r * 1.3 * np.sin(mid_ang),
                    f'θ={np.degrees(ang):.1f}°',
                    fontsize=colors.TICK_SIZE, color=colors.SECONDARY,
                    bbox=_TEXT_BBOX)

    # Annotations
    annotations = []
    if show_beta:
        annotations.append(f'$\\beta_{{{j}}}$ = {beta_j:.4f}')
    if show_se:
        se_str = f'{se_j:.4f}' if np.isfinite(se_j) else '∞'
        annotations.append(f'SE($\\beta_{{{j}}}$) = {se_str}')
    if annotations:
        ax.text(0.02, 0.98, '\n'.join(annotations),
                transform=ax.transAxes, fontsize=colors.LABEL_SIZE,
                verticalalignment='top', bbox=_TEXT_BBOX)

    ax.set_aspect('equal', adjustable='datalim')
    ax.axhline(0, color=colors.SECONDARY, linewidth=0.5, alpha=0.3)
    ax.axvline(0, color=colors.SECONDARY, linewidth=0.5, alpha=0.3)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_projection_2d(
    x: np.ndarray,
    y: np.ndarray,
    title: str = "Simple Regression as Projection",
    figsize: tuple = (8, 6),
    show_residuals: bool = True,
    **kwargs,
) -> Figure:
    """Simple 2D scatter plot with regression line and residual bars.

    This is the "familiar" view before the geometric revelation.

    Elements rendered:
    - Scatter points in gray
    - Regression line in green
    - Vertical residual bars in red (if show_residuals=True)
    - Equation and R^2 displayed as text

    Parameters
    ----------
    x : np.ndarray, shape (n,) — single predictor
    y : np.ndarray, shape (n,) — response
    title : str
    figsize : tuple
    show_residuals : bool
    **kwargs
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()

    cs = ColumnSpace(x, add_intercept=True)
    proj = cs.project(y)
    b0, b1 = proj.coefficients
    r2 = proj.r_squared

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    ax.scatter(x, y, color=colors.SECONDARY, alpha=0.6, s=30, zorder=3)

    x_sorted = np.sort(x)
    ax.plot(x_sorted, b0 + b1 * x_sorted, color=colors.PROJECTION,
            linewidth=2, zorder=2, label='Regression line')

    if show_residuals:
        y_hat = proj.y_hat
        for i in range(len(x)):
            ax.plot([x[i], x[i]], [y[i], y_hat[i]],
                    color=colors.RESIDUAL, linewidth=1, alpha=0.6, zorder=1)

    eq_text = f'$y = {b0:.2f} + {b1:.2f}x$\n$R^2 = {r2:.3f}$'
    ax.text(0.02, 0.98, eq_text, transform=ax.transAxes,
            fontsize=colors.LABEL_SIZE, verticalalignment='top',
            bbox=_TEXT_BBOX)

    ax.set_xlabel('x', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel('y', fontsize=colors.LABEL_SIZE)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


# ===================================================================
# 3.2  Decomposition and R^2 Visualizations
# ===================================================================

def plot_pythagorean_triangle(
    proj: Projection,
    title: str = "Pythagorean Theorem: SST = SSR + SSE",
    figsize: tuple = (8, 6),
    **kwargs,
) -> Figure:
    """The right triangle showing variance decomposition.

    Draws a right triangle with:
    - Hypotenuse labeled ||y - y_bar|| (sqrt(SST)) in gold
    - Adjacent side labeled ||y_hat - y_bar|| (sqrt(SSR)) in green
    - Opposite side labeled ||e|| (sqrt(SSE)) in red
    - Right angle marker at the corner between y_hat and e
    - theta labeled at the corner between y and y_hat
    - Text box: R^2 = cos^2(theta)
    - Text box: SST = SSR + SSE

    Parameters
    ----------
    proj : Projection
    title : str
    figsize : tuple
    **kwargs
    """
    sst, ssr, sse = proj.sst, proj.ssr, proj.sse
    r2 = proj.r_squared
    theta = proj.theta_degrees

    sqrt_sst = np.sqrt(sst)
    sqrt_ssr = np.sqrt(ssr)
    sqrt_sse = np.sqrt(sse)

    # Triangle vertices: right angle at B
    # A = origin, B = (sqrt_ssr, 0), C = (sqrt_ssr, sqrt_sse)
    A = np.array([0.0, 0.0])
    B = np.array([sqrt_ssr, 0.0])
    C = np.array([sqrt_ssr, sqrt_sse])

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    # Draw the three sides
    ax.plot([A[0], B[0]], [A[1], B[1]], color=colors.PROJECTION, linewidth=2.5)
    ax.plot([B[0], C[0]], [B[1], C[1]], color=colors.RESIDUAL, linewidth=2.5)
    ax.plot([A[0], C[0]], [A[1], C[1]], color=colors.RESPONSE_Y, linewidth=2.5)

    # Labels on sides
    ref = max(sqrt_sst, 1e-10)
    mid_AB = (A + B) / 2
    ax.text(mid_AB[0], mid_AB[1] - ref * 0.06,
            f'||ŷ − ȳ|| = {sqrt_ssr:.2f} (√SSR)',
            fontsize=colors.TICK_SIZE, color=colors.PROJECTION,
            ha='center', va='top', bbox=_TEXT_BBOX)

    mid_BC = (B + C) / 2
    ax.text(mid_BC[0] + ref * 0.06, mid_BC[1],
            f'||e|| = {sqrt_sse:.2f} (√SSE)',
            fontsize=colors.TICK_SIZE, color=colors.RESIDUAL,
            ha='left', va='center', bbox=_TEXT_BBOX)

    mid_AC = (A + C) / 2
    ax.text(mid_AC[0] - ref * 0.06, mid_AC[1] + ref * 0.02,
            f'||y − ȳ|| = {sqrt_sst:.2f} (√SST)',
            fontsize=colors.TICK_SIZE, color=colors.RESPONSE_Y,
            ha='right', va='bottom', bbox=_TEXT_BBOX)

    # Right angle marker at B
    ra_size = ref * 0.04
    if ra_size > 1e-10:
        _draw_right_angle_2d(ax, B, A - B, C - B, size=ra_size)

    # Theta angle arc at A
    if theta > 0.1:
        arc_r = ref * 0.12
        if arc_r > 1e-10:
            theta_rad = np.radians(theta)
            arc = mpatches.Arc(A, 2 * arc_r, 2 * arc_r,
                               angle=0, theta1=0, theta2=theta,
                               color=colors.SECONDARY, linewidth=1.5)
            ax.add_patch(arc)
            ax.text(arc_r * 1.4 * np.cos(theta_rad / 2),
                    arc_r * 1.4 * np.sin(theta_rad / 2),
                    f'θ = {theta:.1f}°',
                    fontsize=colors.TICK_SIZE, color=colors.SECONDARY,
                    bbox=_TEXT_BBOX)

    # Text boxes
    textstr = f'$R^2 = \\cos^2\\theta = {r2:.3f}$'
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes,
            fontsize=colors.LABEL_SIZE, verticalalignment='top',
            bbox=_TEXT_BBOX)

    decomp = f'SST = SSR + SSE: {sst:.1f} = {ssr:.1f} + {sse:.1f}'
    ax.text(0.02, 0.88, decomp, transform=ax.transAxes,
            fontsize=colors.TICK_SIZE, verticalalignment='top',
            bbox=_TEXT_BBOX)

    ax.set_aspect('equal', adjustable='datalim')
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.axis('off')

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_r_squared_angle(
    proj: Projection,
    title: str = "R² as an Angle",
    figsize: tuple = (6, 6),
    **kwargs,
) -> Figure:
    """A unit-circle style diagram showing theta and cos^2(theta) = R^2.

    Parameters
    ----------
    proj : Projection
    title : str
    figsize : tuple
    **kwargs
    """
    r2 = proj.r_squared
    theta = proj.theta

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    # Unit circle
    angles = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(angles), np.sin(angles), color=colors.SECONDARY,
            linewidth=1, alpha=0.4)

    # y direction (at angle theta from x-axis)
    ax.plot([0, np.cos(theta)], [0, np.sin(theta)],
            color=colors.RESPONSE_Y, linewidth=2.5, label='y direction')
    # y_hat direction (along x-axis)
    ax.plot([0, 1], [0, 0], color=colors.PROJECTION, linewidth=2.5,
            label='ŷ direction')

    # cos(theta) projection
    cos_t = np.cos(theta)
    ax.plot([cos_t, cos_t], [0, np.sin(theta)],
            color=colors.RESIDUAL, linewidth=1.5, linestyle='--', alpha=0.7)
    ax.plot([0, cos_t], [0, 0], color=colors.PROJECTION,
            linewidth=4, alpha=0.5)

    # Angle arc
    if theta > 0.01:
        arc = mpatches.Arc((0, 0), 0.4, 0.4, angle=0,
                           theta1=0, theta2=np.degrees(theta),
                           color=colors.SECONDARY, linewidth=2)
        ax.add_patch(arc)
        ax.text(0.25 * np.cos(theta / 2), 0.25 * np.sin(theta / 2),
                f'θ={np.degrees(theta):.1f}°',
                fontsize=colors.LABEL_SIZE, color=colors.SECONDARY,
                ha='center', bbox=_TEXT_BBOX)

    # Annotations
    ax.text(0.5, -0.15, f'cos θ = {np.cos(theta):.3f}',
            fontsize=colors.TICK_SIZE, ha='center',
            color=colors.PROJECTION, bbox=_TEXT_BBOX)
    ax.text(0.02, 0.98, f'$R^2 = \\cos^2\\theta = {r2:.3f}$',
            transform=ax.transAxes, fontsize=colors.LABEL_SIZE,
            verticalalignment='top', bbox=_TEXT_BBOX)

    ax.set_aspect('equal')
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.axhline(0, color=colors.SECONDARY, linewidth=0.5, alpha=0.3)
    ax.axvline(0, color=colors.SECONDARY, linewidth=0.5, alpha=0.3)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.grid(True, alpha=0.15)

    _apply_style(fig)
    fig.tight_layout()
    return fig


# ===================================================================
# 3.3  Hat Matrix and Influence Visualizations
# ===================================================================

def plot_leverage(
    hm: HatMatrix,
    threshold: float = None,
    title: str = "Leverage Values (Hat Matrix Diagonal)",
    figsize: tuple = (10, 4),
    highlight_indices: list = None,
    **kwargs,
) -> Figure:
    """Stem plot of leverage values h_ii.

    Elements:
    - Vertical stems colored by leverage (gray below threshold, red above)
    - Horizontal dashed threshold line (default 2p/n)
    - Highlighted indices labeled with their index number

    Parameters
    ----------
    hm : HatMatrix
    threshold : float, optional — default 2*tr(H)/n
    title : str
    figsize : tuple
    highlight_indices : list of int, optional
    **kwargs
    """
    h = hm.diagonal()
    n = len(h)
    if threshold is None:
        threshold = 2.0 * hm.average_leverage()

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    for i in range(n):
        c = colors.RESIDUAL if h[i] > threshold else colors.SECONDARY
        ax.vlines(i, 0, h[i], colors=c, linewidth=1.5)
        ax.plot(i, h[i], 'o', color=c, markersize=4)

    ax.axhline(threshold, color=colors.RESIDUAL, linestyle='--',
               linewidth=1, alpha=0.7, label=f'Threshold = {threshold:.3f}')

    if highlight_indices:
        for idx in highlight_indices:
            if 0 <= idx < n:
                ax.annotate(str(idx), (idx, h[idx]),
                            textcoords="offset points", xytext=(0, 8),
                            fontsize=colors.TICK_SIZE, ha='center',
                            color=colors.RESIDUAL, fontweight='bold')

    ax.set_xlabel('Observation index', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel('Leverage $h_{ii}$', fontsize=colors.LABEL_SIZE)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.legend(fontsize=colors.TICK_SIZE)
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_cooks_distance(
    cooks_d: np.ndarray,
    title: str = "Cook's Distance",
    figsize: tuple = (10, 4),
    threshold: float = None,
    highlight_indices: list = None,
    **kwargs,
) -> Figure:
    """Stem plot of Cook's distance.

    Default threshold line at 4/n.

    Parameters
    ----------
    cooks_d : np.ndarray, shape (n,)
    title : str
    figsize : tuple
    threshold : float, optional — default 4/n
    highlight_indices : list of int, optional
    **kwargs
    """
    cooks_d = np.asarray(cooks_d, dtype=float).ravel()
    n = len(cooks_d)
    if threshold is None:
        threshold = 4.0 / n

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    for i in range(n):
        c = colors.RESIDUAL if cooks_d[i] > threshold else colors.SECONDARY
        ax.vlines(i, 0, cooks_d[i], colors=c, linewidth=1.5)
        ax.plot(i, cooks_d[i], 'o', color=c, markersize=4)

    ax.axhline(threshold, color=colors.RESIDUAL, linestyle='--',
               linewidth=1, alpha=0.7, label=f'Threshold = {threshold:.3f}')

    if highlight_indices:
        for idx in highlight_indices:
            if 0 <= idx < n:
                ax.annotate(str(idx), (idx, cooks_d[idx]),
                            textcoords="offset points", xytext=(0, 8),
                            fontsize=colors.TICK_SIZE, ha='center',
                            color=colors.RESIDUAL, fontweight='bold')

    ax.set_xlabel('Observation index', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel("Cook's Distance", fontsize=colors.LABEL_SIZE)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.legend(fontsize=colors.TICK_SIZE)
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_influence_diagram(
    hm: HatMatrix,
    residuals: np.ndarray,
    mse: float,
    p: int,
    title: str = "Leverage vs. Residual (Influence Diagram)",
    figsize: tuple = (8, 6),
    highlight_indices: list = None,
    **kwargs,
) -> Figure:
    """Scatter plot of leverage (x-axis) vs. squared residual (y-axis).

    Point size proportional to Cook's distance.
    Contour lines for constant Cook's distance.

    Parameters
    ----------
    hm : HatMatrix
    residuals : np.ndarray, shape (n,)
    mse : float — mean squared error
    p : int — number of parameters
    title : str
    figsize : tuple
    highlight_indices : list of int, optional
    **kwargs
    """
    h = hm.diagonal()
    residuals = np.asarray(residuals, dtype=float).ravel()
    e2 = residuals ** 2
    cooks_d = hm.cooks_distance(residuals, mse, p)

    # Cap infinite Cook's D for sizing
    cooks_finite = np.where(np.isfinite(cooks_d), cooks_d, 0.0)
    max_cd = max(cooks_finite.max(), 1e-15)
    sizes = 20 + 200 * (cooks_finite / max_cd)

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    ax.scatter(h, e2, s=sizes, color=colors.COLUMN_SPACE, alpha=0.6,
               edgecolors=colors.SECONDARY, linewidths=0.5)

    # Contour lines for constant Cook's D
    h_grid = np.linspace(1e-6, min(h.max() * 1.2, 0.999), 100)
    for D_val in [0.5, 1.0]:
        with np.errstate(divide='ignore', invalid='ignore'):
            e2_contour = D_val * p * mse * (1 - h_grid) ** 2 / h_grid
        valid = np.isfinite(e2_contour) & (e2_contour >= 0)
        if valid.any():
            ax.plot(h_grid[valid], e2_contour[valid],
                    color=colors.CONSTRAINT, linestyle='--', alpha=0.5,
                    linewidth=1, label=f"Cook's D = {D_val}")

    # Threshold lines
    lev_threshold = 2.0 * hm.average_leverage()
    ax.axvline(lev_threshold, color=colors.RESIDUAL, linestyle=':',
               alpha=0.5, label=f'Leverage = {lev_threshold:.3f}')

    if highlight_indices:
        for idx in highlight_indices:
            if 0 <= idx < len(h):
                ax.annotate(str(idx), (h[idx], e2[idx]),
                            textcoords="offset points", xytext=(5, 5),
                            fontsize=colors.TICK_SIZE,
                            color=colors.RESIDUAL, fontweight='bold')

    ax.set_xlabel('Leverage $h_{ii}$', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel('Squared Residual $e_i^2$', fontsize=colors.LABEL_SIZE)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.legend(fontsize=colors.TICK_SIZE, loc='upper right')
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


# ===================================================================
# 3.4  Eigenvalue and Collinearity Visualizations
# ===================================================================

def plot_eigenvalue_ellipsoid(
    ell: Ellipsoid,
    title: str = "Eigenvalue Ellipsoid of X'X",
    figsize: tuple = (8, 8),
    views: str = "default",
    **kwargs,
) -> Figure:
    """3D ellipsoid showing the shape of X'X.

    Only works for p <= 3. For p > 3, falls back to plot_eigenvalue_bar.

    Parameters
    ----------
    ell : Ellipsoid
    title : str
    figsize : tuple
    views : str — "default" for single 3D view
    **kwargs
    """
    p = len(ell.eigenvalues)
    if p > 3:
        return plot_eigenvalue_bar(ell, title=title, figsize=figsize, **kwargs)

    axes_len = ell.axis_lengths
    Q = ell.eigenvectors

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig = plt.figure(figsize=figsize, **dpi_kw)

    if p == 3:
        ax = fig.add_subplot(111, projection='3d')
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 20)
        sx = axes_len[0] * np.outer(np.cos(u), np.sin(v))
        sy = axes_len[1] * np.outer(np.sin(u), np.sin(v))
        sz = axes_len[2] * np.outer(np.ones_like(u), np.cos(v))

        # Rotate by eigenvectors
        for ii in range(sx.shape[0]):
            for jj in range(sx.shape[1]):
                pt = Q @ np.array([sx[ii, jj], sy[ii, jj], sz[ii, jj]])
                sx[ii, jj], sy[ii, jj], sz[ii, jj] = pt

        ax.plot_surface(sx, sy, sz, color=colors.CONSTRAINT,
                        alpha=colors.SURFACE_ALPHA, edgecolor=colors.COLUMN_SPACE,
                        linewidth=0.3)
        # Draw axes
        for k in range(3):
            direction = Q[:, k] * axes_len[k]
            ax.quiver(0, 0, 0, *direction, color=colors.COLUMN_SPACE,
                      arrow_length_ratio=0.1, linewidth=2)
        _setup_3d_ax(ax, elev=30, azim=45)
    elif p == 2:
        ax = fig.add_subplot(111)
        theta = np.linspace(0, 2 * np.pi, 200)
        pts = np.column_stack([axes_len[0] * np.cos(theta),
                               axes_len[1] * np.sin(theta)])
        rotated = pts @ Q.T
        ax.plot(rotated[:, 0], rotated[:, 1], color=colors.COLUMN_SPACE,
                linewidth=2)
        ax.fill(rotated[:, 0], rotated[:, 1], color=colors.CONSTRAINT,
                alpha=colors.SURFACE_ALPHA)
        for k in range(2):
            d = Q[:, k] * axes_len[k]
            ax.annotate('', xy=d, xytext=(0, 0),
                        arrowprops=dict(arrowstyle='->', color=colors.COLUMN_SPACE, lw=2))
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2)
    else:
        # p == 1 — degenerate, just a line
        ax = fig.add_subplot(111)
        ax.plot([-axes_len[0], axes_len[0]], [0, 0],
                color=colors.COLUMN_SPACE, linewidth=3)
        ax.set_aspect('equal')

    cond = ell.condition_number
    cond_str = f'{cond:.1f}' if np.isfinite(cond) else '∞'
    ax.set_title(f'{title}\nCondition number: {cond_str}',
                 fontsize=colors.TITLE_SIZE)

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_eigenvalue_bar(
    ell: Ellipsoid,
    title: str = "Eigenvalues of X'X",
    figsize: tuple = (8, 4),
    log_scale: bool = False,
    **kwargs,
) -> Figure:
    """Bar chart of eigenvalues (works for any p).

    Bars colored on a gradient from green (large) to red (small).

    Parameters
    ----------
    ell : Ellipsoid
    title : str
    figsize : tuple
    log_scale : bool — if True, use log y-axis
    **kwargs
    """
    evals = ell.eigenvalues
    p = len(evals)

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    max_e = evals[0] if evals[0] > 0 else 1.0
    bar_colors = []
    for ev in evals:
        frac = ev / max_e if max_e > 1e-15 else 0.0
        bar_colors.append(colors.PROJECTION if frac > 0.3 else
                          colors.RESPONSE_Y if frac > 0.1 else
                          colors.RESIDUAL)

    ax.bar(range(p), evals, color=bar_colors, edgecolor=colors.SECONDARY,
           linewidth=0.5)

    if log_scale and all(evals > 0):
        ax.set_yscale('log')

    cond = ell.condition_number
    cond_str = f'{cond:.1f}' if np.isfinite(cond) else '∞'
    ax.text(0.98, 0.95, f'κ = {cond_str}',
            transform=ax.transAxes, fontsize=colors.LABEL_SIZE,
            ha='right', va='top', bbox=_TEXT_BBOX)

    ax.set_xlabel('Eigenvalue index', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel('Eigenvalue', fontsize=colors.LABEL_SIZE)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.set_xticks(range(p))
    ax.grid(True, alpha=0.2, axis='y')

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_collinearity_comparison(
    cs_low: ColumnSpace,
    cs_high: ColumnSpace,
    y: np.ndarray,
    titles: tuple = ("Low Collinearity", "High Collinearity"),
    figsize: tuple = (14, 6),
    **kwargs,
) -> Figure:
    """Side-by-side 3D projections showing stable vs. unstable column spaces.

    Only works for n=3.

    Parameters
    ----------
    cs_low : ColumnSpace — well-conditioned
    cs_high : ColumnSpace — nearly-collinear
    y : np.ndarray, shape (3,)
    titles : tuple of two strings
    figsize : tuple
    **kwargs
    """
    y = np.asarray(y, dtype=float).ravel()

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig = plt.figure(figsize=figsize, **dpi_kw)

    for i, (cs, subtitle) in enumerate([(cs_low, titles[0]), (cs_high, titles[1])]):
        ax = fig.add_subplot(1, 2, i + 1, projection='3d')
        proj = cs.project(y)
        y_hat = proj.y_hat
        e = proj.residuals

        vecs = np.array([y, y_hat])
        scale = float(np.max(np.abs(vecs))) * 1.3
        if scale < 1e-10:
            scale = 2.0

        _draw_column_space_plane(ax, cs, scale=scale)
        _arrow_3d(ax, [0, 0, 0], y, colors.RESPONSE_Y, label='y')
        _arrow_3d(ax, [0, 0, 0], y_hat, colors.PROJECTION, label='ŷ')
        _arrow_3d(ax, y_hat, e, colors.RESIDUAL, label='e')
        _setup_3d_ax(ax, elev=30, azim=45)

        cond = cs.condition_number()
        cond_str = f'{cond:.1f}' if np.isfinite(cond) else '∞'
        ax.set_title(f'{subtitle}\nκ = {cond_str}', fontsize=colors.LABEL_SIZE)

    fig.suptitle("Collinearity Comparison", fontsize=colors.TITLE_SIZE)
    _apply_style(fig)
    fig.tight_layout()
    return fig


# ===================================================================
# 3.5  Frisch-Waugh-Lovell Visualizations
# ===================================================================

def plot_fwl_decomposition(
    X: np.ndarray,
    y: np.ndarray,
    j: int,
    title: str = None,
    figsize: tuple = (14, 5),
    **kwargs,
) -> Figure:
    """Three-panel FWL visualization.

    Panel 1: Full regression scatter for variable j
    Panel 2: Added variable plot (residualized y vs. residualized x_j)
    Panel 3: The Relevant Triangle (geometric view)

    Parameters
    ----------
    X : np.ndarray, shape (n, p) — design matrix (with intercept if desired)
    y : np.ndarray, shape (n,)
    j : int — column index to isolate
    title : str — default "Frisch-Waugh-Lovell: Isolating x_{j}"
    figsize : tuple
    **kwargs
    """
    if title is None:
        title = f"Frisch-Waugh-Lovell: Isolating $x_{{{j}}}$"

    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()

    fwl = frisch_waugh_lovell(X, y, j)
    coef_full, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    y_hat_full = X @ coef_full

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, axes = plt.subplots(1, 3, figsize=figsize, **dpi_kw)

    # Panel 1: Full regression — scatter of x_j vs y
    ax1 = axes[0]
    xj = X[:, j]
    ax1.scatter(xj, y, color=colors.SECONDARY, alpha=0.5, s=20)
    sort_idx = np.argsort(xj)
    ax1.plot(xj[sort_idx], y_hat_full[sort_idx], color=colors.PROJECTION,
             linewidth=2, alpha=0.7)
    ax1.set_xlabel(f'$x_{{{j}}}$', fontsize=colors.LABEL_SIZE)
    ax1.set_ylabel('y', fontsize=colors.LABEL_SIZE)
    ax1.set_title('Full Regression', fontsize=colors.LABEL_SIZE)
    ax1.text(0.02, 0.98, f'$\\beta_{{{j}}}$ = {coef_full[j]:.4f}',
             transform=ax1.transAxes, fontsize=colors.TICK_SIZE,
             va='top', bbox=_TEXT_BBOX)
    ax1.grid(True, alpha=0.2)

    # Panel 2: Added variable plot
    ax2 = axes[1]
    y_resid = fwl['y_resid']
    xj_resid = fwl['xj_resid']
    beta_j = fwl['beta_j']
    ax2.scatter(xj_resid, y_resid, color=colors.SECONDARY, alpha=0.5, s=20)
    sort_idx2 = np.argsort(xj_resid)
    ax2.plot(xj_resid[sort_idx2], beta_j * xj_resid[sort_idx2],
             color=colors.PROJECTION, linewidth=2)
    ax2.set_xlabel(f'$M_{{-{j}}} x_{{{j}}}$', fontsize=colors.LABEL_SIZE)
    ax2.set_ylabel(f'$M_{{-{j}}} y$', fontsize=colors.LABEL_SIZE)
    ax2.set_title('Added Variable Plot', fontsize=colors.LABEL_SIZE)
    ax2.text(0.02, 0.98, f'slope = {beta_j:.4f}',
             transform=ax2.transAxes, fontsize=colors.TICK_SIZE,
             va='top', bbox=_TEXT_BBOX)
    ax2.grid(True, alpha=0.2)

    # Panel 3: Relevant Triangle (inline, simplified)
    ax3 = axes[2]
    xj_norm = np.linalg.norm(xj_resid)
    if xj_norm > 1e-15:
        e1 = xj_resid / xj_norm
    else:
        e1 = np.zeros_like(xj_resid)
        e1[0] = 1.0

    y_on_e1 = np.dot(y_resid, e1)
    y_comp = y_resid - y_on_e1 * e1
    y_comp_norm = np.linalg.norm(y_comp)
    if y_comp_norm > 1e-15:
        e2 = y_comp / y_comp_norm
    else:
        e2 = np.zeros_like(e1)
        e2[min(1, len(e2) - 1)] = 1.0

    xj_2d = np.array([np.dot(xj_resid, e1), np.dot(xj_resid, e2)])
    yr_2d = np.array([np.dot(y_resid, e1), np.dot(y_resid, e2)])
    proj_2d = np.array([y_on_e1, 0.0])

    _arrow_2d(ax3, (0, 0), yr_2d, colors.RESPONSE_Y, label='$y_r$')
    _arrow_2d(ax3, (0, 0), xj_2d, colors.COLUMN_SPACE, label=f'$x_{{{j},r}}$')
    _arrow_2d(ax3, (0, 0), proj_2d, colors.PROJECTION)
    _arrow_2d(ax3, proj_2d, yr_2d - proj_2d, colors.RESIDUAL)
    ax3.set_aspect('equal', adjustable='datalim')
    ax3.set_title('Relevant Triangle', fontsize=colors.LABEL_SIZE)
    ax3.grid(True, alpha=0.2)

    fig.suptitle(title, fontsize=colors.TITLE_SIZE)
    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_added_variable(
    X: np.ndarray,
    y: np.ndarray,
    j: int,
    title: str = None,
    figsize: tuple = (7, 6),
    **kwargs,
) -> Figure:
    """Added variable plot (partial regression plot) for variable j.

    Scatter of M_{-j}y vs. M_{-j}x_j with the partial regression line.

    Parameters
    ----------
    X : np.ndarray, shape (n, p)
    y : np.ndarray, shape (n,)
    j : int
    title : str — default "Added Variable Plot for x_{j}"
    figsize : tuple
    **kwargs
    """
    if title is None:
        title = f"Added Variable Plot for $x_{{{j}}}$"

    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    fwl = frisch_waugh_lovell(X, y, j)
    y_resid = fwl['y_resid']
    xj_resid = fwl['xj_resid']
    beta_j = fwl['beta_j']

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    ax.scatter(xj_resid, y_resid, color=colors.SECONDARY, alpha=0.5, s=20)
    sort_idx = np.argsort(xj_resid)
    ax.plot(xj_resid[sort_idx], beta_j * xj_resid[sort_idx],
            color=colors.PROJECTION, linewidth=2,
            label=f'slope = $\\beta_{{{j}}}$ = {beta_j:.4f}')

    ax.set_xlabel(f'$M_{{-{j}}} x_{{{j}}}$', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel(f'$M_{{-{j}}} y$', fontsize=colors.LABEL_SIZE)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.legend(fontsize=colors.TICK_SIZE)
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


# ===================================================================
# 3.6  Regularization Visualizations
# ===================================================================

def plot_ridge_lasso_constraint(
    beta_ols: np.ndarray,
    lam_values: list = None,
    title: str = "Ridge vs. LASSO Constraints",
    figsize: tuple = (14, 6),
    **kwargs,
) -> Figure:
    """Side-by-side 2D plots showing Ridge (L2 circle) and LASSO (L1 diamond).

    Only works for p=2.

    Parameters
    ----------
    beta_ols : np.ndarray, shape (2,)
    lam_values : list, optional — if provided show path of solutions
    title : str
    figsize : tuple
    **kwargs
    """
    beta_ols = np.asarray(beta_ols, dtype=float).ravel()

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, axes = plt.subplots(1, 2, figsize=figsize, **dpi_kw)

    ols_norm_l2 = np.linalg.norm(beta_ols)
    ols_norm_l1 = np.sum(np.abs(beta_ols))
    r_l2 = max(ols_norm_l2 * 0.6, 1e-10)
    r_l1 = max(ols_norm_l1 * 0.6, 1e-10)

    for idx, (ax, norm_type, radius) in enumerate(
        [(axes[0], 'L2 (Ridge)', r_l2), (axes[1], 'L1 (LASSO)', r_l1)]
    ):
        # Draw RSS contours
        theta = np.linspace(0, 2 * np.pi, 200)
        for scale in [0.3, 0.6, 1.0, 1.5, 2.0]:
            r = scale * max(ols_norm_l2, 1e-10) * 0.4
            cx = beta_ols[0] + r * np.cos(theta)
            cy = beta_ols[1] + r * np.sin(theta)
            ax.plot(cx, cy, color=colors.SECONDARY, alpha=0.2, linewidth=0.8)

        # Draw constraint region
        if idx == 0:  # L2 circle
            cx = radius * np.cos(theta)
            cy = radius * np.sin(theta)
            ax.plot(cx, cy, color=colors.CONSTRAINT, linewidth=2)
            ax.fill(cx, cy, color=colors.CONSTRAINT, alpha=0.1)
        else:  # L1 diamond
            diamond_x = [radius, 0, -radius, 0, radius]
            diamond_y = [0, radius, 0, -radius, 0]
            ax.plot(diamond_x, diamond_y, color=colors.CONSTRAINT, linewidth=2)
            ax.fill(diamond_x, diamond_y, color=colors.CONSTRAINT, alpha=0.1)

        # Mark OLS solution
        ax.plot(*beta_ols, 'o', color=colors.PROJECTION, markersize=8,
                zorder=5, label='OLS')

        # Mark constrained solution (approximate)
        if idx == 0:
            if ols_norm_l2 > 1e-15:
                beta_ridge = beta_ols * (radius / ols_norm_l2)
            else:
                beta_ridge = beta_ols
            ax.plot(*beta_ridge, 's', color=colors.CONSTRAINT,
                    markersize=8, zorder=5, label='Ridge')
        else:
            if np.abs(beta_ols[0]) > np.abs(beta_ols[1]):
                beta_lasso = np.array([np.sign(beta_ols[0]) * radius, 0.0])
            else:
                beta_lasso = np.array([0.0, np.sign(beta_ols[1]) * radius])
            ax.plot(*beta_lasso, 's', color=colors.CONSTRAINT,
                    markersize=8, zorder=5, label='LASSO')

        if lam_values is not None and idx == 0:
            path = [beta_ols * (1 / (1 + lam)) for lam in lam_values]
            path_arr = np.array(path)
            ax.plot(path_arr[:, 0], path_arr[:, 1], '--',
                    color=colors.RESPONSE_Y, linewidth=1.5, alpha=0.7)

        ax.axhline(0, color=colors.SECONDARY, linewidth=0.5, alpha=0.3)
        ax.axvline(0, color=colors.SECONDARY, linewidth=0.5, alpha=0.3)
        ax.set_xlabel('$\\beta_1$', fontsize=colors.LABEL_SIZE)
        ax.set_ylabel('$\\beta_2$', fontsize=colors.LABEL_SIZE)
        ax.set_title(norm_type, fontsize=colors.LABEL_SIZE)
        ax.set_aspect('equal')
        ax.legend(fontsize=colors.TICK_SIZE)
        ax.grid(True, alpha=0.15)

    fig.suptitle(title, fontsize=colors.TITLE_SIZE)
    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_shrinkage_path(
    ell: Ellipsoid,
    beta_ols: np.ndarray,
    lam_range: np.ndarray = None,
    title: str = "Ridge Shrinkage Path",
    figsize: tuple = (10, 6),
    **kwargs,
) -> Figure:
    """Coefficient values as a function of lambda.

    X-axis: log(lambda). Y-axis: coefficient value.
    One line per coefficient.

    Parameters
    ----------
    ell : Ellipsoid
    beta_ols : np.ndarray, shape (p,)
    lam_range : np.ndarray, optional — default logspace(-2, 4, 200)
    title : str
    figsize : tuple
    **kwargs
    """
    beta_ols = np.asarray(beta_ols, dtype=float).ravel()
    if lam_range is None:
        lam_range = np.logspace(-2, 4, 200)

    p = len(beta_ols)
    paths = np.zeros((len(lam_range), p))
    for i, lam in enumerate(lam_range):
        paths[i] = ell.ridge_coefficients(beta_ols, lam)

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    cmap = plt.cm.tab10
    for k in range(p):
        ax.plot(np.log10(lam_range), paths[:, k],
                color=cmap(k % 10), linewidth=1.5,
                label=f'$\\beta_{{{k}}}$')

    ax.axhline(0, color=colors.SECONDARY, linewidth=0.5, alpha=0.5)
    ax.set_xlabel('$\\log_{10}(\\lambda)$', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel('Coefficient value', fontsize=colors.LABEL_SIZE)
    ax.set_title(title, fontsize=colors.TITLE_SIZE)
    ax.legend(fontsize=colors.TICK_SIZE, loc='upper right')
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


# ===================================================================
# 3.7  F-test and Inference Visualizations
# ===================================================================

def plot_nested_projections(
    cs_restricted: ColumnSpace,
    cs_full: ColumnSpace,
    y: np.ndarray,
    title: str = "F-test: Comparing Two Projections",
    figsize: tuple = (10, 8),
    views: str = "default",
    **kwargs,
) -> Figure:
    """Shows the restricted and unrestricted projections in 3D.

    Only works for n=3.

    Parameters
    ----------
    cs_restricted : ColumnSpace — smaller model
    cs_full : ColumnSpace — larger model
    y : np.ndarray, shape (3,)
    title : str
    figsize : tuple
    views : str
    **kwargs
    """
    y = np.asarray(y, dtype=float).ravel()

    proj_r = cs_restricted.project(y)
    proj_f = cs_full.project(y)

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig = plt.figure(figsize=figsize, **dpi_kw)
    ax = fig.add_subplot(111, projection='3d')

    vecs = np.array([y, proj_r.y_hat, proj_f.y_hat])
    scale = float(np.max(np.abs(vecs))) * 1.3
    if scale < 1e-10:
        scale = 2.0

    # Full column space
    _draw_column_space_plane(ax, cs_full, scale=scale)

    # y vector
    _arrow_3d(ax, [0, 0, 0], y, colors.RESPONSE_Y, label='y')

    # Restricted projection (dark green)
    dark_green = colors.PROJECTION  # use semantic color
    ax.plot(*proj_r.y_hat, 'o', color=dark_green, markersize=8, zorder=5)
    _arrow_3d(ax, [0, 0, 0], proj_r.y_hat, dark_green, label='ŷ_restricted')

    # Full projection
    _arrow_3d(ax, [0, 0, 0], proj_f.y_hat, colors.COLUMN_SPACE, label='ŷ_full')

    # Gap between projections
    gap = proj_f.y_hat - proj_r.y_hat
    _arrow_3d(ax, proj_r.y_hat, gap, colors.CONSTRAINT, label='gap')

    # Residuals from full
    _arrow_3d(ax, proj_f.y_hat, proj_f.residuals, colors.RESIDUAL, label='e_full')

    _setup_3d_ax(ax, elev=30, azim=45)

    # F-statistic
    sse_r = proj_r.sse
    sse_f = proj_f.sse
    df1 = cs_full.p - cs_restricted.p
    df2 = cs_full.n - cs_full.p
    if df1 > 0 and df2 > 0 and sse_f > 1e-15:
        f_stat = ((sse_r - sse_f) / df1) / (sse_f / df2)
        ax.text2D(0.02, 0.95, f'F = {f_stat:.2f}',
                  transform=ax.transAxes, fontsize=colors.LABEL_SIZE,
                  bbox=_TEXT_BBOX)

    ax.set_title(title, fontsize=colors.TITLE_SIZE)

    _apply_style(fig)
    fig.tight_layout()
    return fig


def plot_confidence_ellipse(
    beta: np.ndarray,
    cov: np.ndarray,
    confidence: float = 0.95,
    indices: tuple = (0, 1),
    title: str = "Confidence Ellipse",
    figsize: tuple = (7, 7),
    **kwargs,
) -> Figure:
    """2D confidence ellipse for a pair of coefficients.

    Parameters
    ----------
    beta : np.ndarray — coefficient vector
    cov : np.ndarray — covariance matrix of coefficients
    confidence : float — confidence level (default 0.95)
    indices : tuple — which two coefficients to plot
    title : str
    figsize : tuple
    **kwargs
    """
    from scipy import stats

    beta = np.asarray(beta, dtype=float).ravel()
    cov = np.asarray(cov, dtype=float)
    i, j_idx = indices

    # Extract 2x2 sub-covariance
    sub_cov = cov[np.ix_([i, j_idx], [i, j_idx])]
    center = np.array([beta[i], beta[j_idx]])

    # Eigendecomposition for ellipse
    vals, vecs = np.linalg.eigh(sub_cov)
    vals = np.maximum(vals, 0.0)

    # Chi-squared quantile for confidence
    chi2_val = stats.chi2.ppf(confidence, df=2)
    angle = np.degrees(np.arctan2(vecs[1, 1], vecs[0, 1]))
    width = 2 * np.sqrt(vals[1] * chi2_val)
    height = 2 * np.sqrt(vals[0] * chi2_val)

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, ax = plt.subplots(figsize=figsize, **dpi_kw)

    ellipse = mpatches.Ellipse(center, width, height, angle=angle,
                                fill=True, facecolor=colors.COLUMN_SPACE,
                                alpha=0.2, edgecolor=colors.COLUMN_SPACE,
                                linewidth=2)
    ax.add_patch(ellipse)

    # Center point
    ax.plot(*center, 'o', color=colors.PROJECTION, markersize=8, zorder=5,
            label=f'$\\hat{{\\beta}}$ = ({center[0]:.3f}, {center[1]:.3f})')

    # Eigenvector axes
    for k in range(2):
        direction = vecs[:, k] * np.sqrt(vals[k] * chi2_val)
        ax.annotate('', xy=center + direction, xytext=center,
                    arrowprops=dict(arrowstyle='->', color=colors.CONSTRAINT,
                                    lw=1.5, linestyle='--'))

    # Marginal CIs
    se_i = np.sqrt(sub_cov[0, 0])
    se_j = np.sqrt(sub_cov[1, 1])
    z = stats.norm.ppf((1 + confidence) / 2)
    ax.axvline(center[0] - z * se_i, color=colors.SECONDARY,
               linestyle=':', alpha=0.5)
    ax.axvline(center[0] + z * se_i, color=colors.SECONDARY,
               linestyle=':', alpha=0.5)
    ax.axhline(center[1] - z * se_j, color=colors.SECONDARY,
               linestyle=':', alpha=0.5)
    ax.axhline(center[1] + z * se_j, color=colors.SECONDARY,
               linestyle=':', alpha=0.5)

    ax.set_xlabel(f'$\\beta_{{{i}}}$', fontsize=colors.LABEL_SIZE)
    ax.set_ylabel(f'$\\beta_{{{j_idx}}}$', fontsize=colors.LABEL_SIZE)
    ax.set_title(f'{title} ({confidence*100:.0f}%)', fontsize=colors.TITLE_SIZE)
    ax.set_aspect('equal', adjustable='datalim')
    ax.legend(fontsize=colors.TICK_SIZE)
    ax.grid(True, alpha=0.2)

    _apply_style(fig)
    fig.tight_layout()
    return fig


# ===================================================================
# 3.8  The Geometric Scoreboard (Static Version)
# ===================================================================

def plot_scoreboard(
    proj: Projection,
    cs: ColumnSpace,
    active_gauges: list = None,
    title: str = "Geometric Scoreboard",
    figsize: tuple = (12, 1.5),
    **kwargs,
) -> Figure:
    """Static rendering of the five-gauge Geometric Scoreboard.

    Displays five horizontal gauges in a single row:
    theta, kappa (condition number), tr(H)/n, ||e||/||y||, R^2.

    Each gauge is color-coded per the thresholds in SPEC.md §6.5.

    Parameters
    ----------
    proj : Projection
    cs : ColumnSpace
    active_gauges : list of str, optional
        Which gauges are "unlocked". Options: ['theta', 'kappa', 'leverage',
        'residual_norm', 'r_squared'].
        If None, all are active.
        Inactive gauges render grayed out with "?" instead of a value.
    title : str
    figsize : tuple
    **kwargs
    """
    all_gauges = ['theta', 'kappa', 'leverage', 'residual_norm', 'r_squared']
    if active_gauges is None:
        active_gauges = all_gauges

    hm = HatMatrix(proj.H)

    # Compute values
    theta_deg = proj.theta_degrees
    kappa = cs.condition_number()
    avg_lev = hm.average_leverage()
    rel_resid = proj.relative_residual_norm
    r2 = proj.r_squared

    def _theta_color(v):
        if v < 45:
            return colors.PROJECTION
        elif v < 70:
            return colors.RESPONSE_Y
        else:
            return colors.RESIDUAL

    def _kappa_color(v):
        if not np.isfinite(v) or v > 100:
            return colors.RESIDUAL
        elif v > 30:
            return colors.RESPONSE_Y
        else:
            return colors.PROJECTION

    def _resid_color(v):
        if v < 0.5:
            return colors.PROJECTION
        elif v < 0.8:
            return colors.RESPONSE_Y
        else:
            return colors.RESIDUAL

    gauge_defs = [
        ('theta', 'θ', theta_deg, f'{theta_deg:.1f}°', _theta_color),
        ('kappa', 'κ', kappa,
         f'{kappa:.1f}' if np.isfinite(kappa) else '∞', _kappa_color),
        ('leverage', 'tr(H)/n', avg_lev, f'{avg_lev:.3f}', lambda v: colors.COLUMN_SPACE),
        ('residual_norm', '||e||/||y||', rel_resid, f'{rel_resid:.3f}', _resid_color),
        ('r_squared', 'R²', r2, f'{r2:.3f}', lambda v: colors.PROJECTION),
    ]

    dpi_kw = {k: v for k, v in kwargs.items() if k == 'dpi'}
    fig, axes = plt.subplots(1, 5, figsize=figsize, **dpi_kw)

    for ax, (key, label, val, val_str, color_fn) in zip(axes, gauge_defs):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        is_active = key in active_gauges

        if is_active:
            gauge_color = color_fn(val)
            display_val = val_str
        else:
            gauge_color = colors.SECONDARY
            display_val = '?'

        # Background bar
        ax.barh(0.5, 1.0, height=0.35, color=colors.SECONDARY, alpha=0.15,
                left=0)

        # Filled portion
        if key == 'theta':
            fill = min(val / 90.0, 1.0) if is_active else 0
        elif key == 'kappa':
            fill = min(np.log10(max(val, 1)) / 3.0, 1.0) if (is_active and np.isfinite(val)) else (1.0 if is_active else 0)
        elif key == 'leverage':
            fill = min(val * 5, 1.0) if is_active else 0
        elif key == 'residual_norm':
            fill = min(val, 1.0) if is_active else 0
        else:  # r_squared
            fill = val if is_active else 0

        ax.barh(0.5, fill, height=0.35, color=gauge_color, alpha=0.6,
                left=0)

        # Label
        ax.text(0.5, 0.95, label, ha='center', va='top',
                fontsize=colors.TICK_SIZE, fontweight='bold',
                color=colors.SECONDARY if not is_active else 'black')
        ax.text(0.5, 0.15, display_val, ha='center', va='bottom',
                fontsize=colors.LABEL_SIZE, fontweight='bold',
                color=gauge_color)

    fig.suptitle(title, fontsize=colors.TITLE_SIZE, y=1.05)
    _apply_style(fig)
    fig.tight_layout()
    return fig
