"""Interactive Plotly + ipywidgets rendering backend (Layer 2 — optional).

Every public function in plots.py has a matching function here with the
identical name, parameters, and defaults, plus an optional
``interactive_extras`` keyword.  Return types are Plotly Figures or
ipywidgets containers.
"""

from __future__ import annotations

import numpy as np

# Graceful import — sets AVAILABLE flag
try:
    import plotly.graph_objects as go
    import ipywidgets as widgets
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

from regression_geometry.core import (
    ColumnSpace, Projection, HatMatrix, Ellipsoid,
    frisch_waugh_lovell, angle_between, demean,
)
from regression_geometry import colors

# ---------------------------------------------------------------------------
# Layout defaults (per spec)
# ---------------------------------------------------------------------------

DEFAULT_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="sans-serif", size=12),
    margin=dict(l=50, r=50, t=60, b=50),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)

DEFAULT_SCENE = dict(
    camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
    xaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    yaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    zaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    aspectmode="data",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_extras(fig, extras):
    if extras:
        fig.update_layout(**extras)


def _vec3_trace(origin, vec, color, name, dash=None):
    """Scatter3d + Cone arrowhead for a vector arrow."""
    o = np.asarray(origin, dtype=float)
    v = np.asarray(vec, dtype=float)
    end = o + v
    length = np.linalg.norm(v)
    line_trace = go.Scatter3d(
        x=[o[0], end[0]], y=[o[1], end[1]], z=[o[2], end[2]],
        mode="lines+text",
        line=dict(color=color, width=5, dash=dash),
        text=["", name],
        textposition="top center",
        name=name,
        hovertemplate=(
            f"<b>{name}</b><br>"
            f"components: [{v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}]<br>"
            f"length: {length:.3f}<extra></extra>"
        ),
    )
    if length > 1e-10:
        direction = v / length
        cone = go.Cone(
            x=[end[0]], y=[end[1]], z=[end[2]],
            u=[direction[0]], v=[direction[1]], w=[direction[2]],
            sizemode="absolute", sizeref=length * 0.08,
            colorscale=[[0, color], [1, color]], showscale=False,
            hoverinfo="skip", name="",
        )
        return [line_trace, cone]
    return [line_trace]


def _plane_mesh(cs, scale=None, color=colors.COLUMN_SPACE, opacity=0.25):
    """Mesh3d trace for the column space plane (n=3)."""
    Q = cs.basis()
    r = Q.shape[1]
    if scale is None:
        scale = 2.0
    if r == 0:
        return []
    if r == 1:
        t = np.linspace(-scale, scale, 20)
        pts = np.outer(t, Q[:, 0])
        return [go.Scatter3d(
            x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
            mode="lines", line=dict(color=color, width=4),
            name="Column Space (line)", hoverinfo="skip",
        )]
    s = np.linspace(-scale, scale, 10)
    t = np.linspace(-scale, scale, 10)
    S, T = np.meshgrid(s, t)
    pts = S[..., None] * Q[:, 0] + T[..., None] * Q[:, 1]
    xx, yy, zz = pts[:, :, 0].ravel(), pts[:, :, 1].ravel(), pts[:, :, 2].ravel()
    from scipy.spatial import Delaunay
    try:
        tri = Delaunay(np.column_stack([S.ravel(), T.ravel()]))
        i, j, k = tri.simplices[:, 0], tri.simplices[:, 1], tri.simplices[:, 2]
    except Exception:
        return []
    return [go.Mesh3d(
        x=xx, y=yy, z=zz, i=i, j=j, k=k,
        color=color, opacity=opacity,
        name="Column Space", hoverinfo="skip",
    )]


def _right_angle_trace(foot, v1, v2, size=0.15, color=colors.SECONDARY):
    d1 = v1 / (np.linalg.norm(v1) + 1e-15) * size
    d2 = v2 / (np.linalg.norm(v2) + 1e-15) * size
    pts = np.array([foot, foot + d1, foot + d1 + d2, foot + d2, foot])
    return go.Scatter3d(
        x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
        mode="lines", line=dict(color=color, width=3),
        name="Right Angle", hoverinfo="skip", showlegend=False,
    )


# ===================================================================
# Shared functions — signature parity with plots.py
# ===================================================================

def plot_projection_3d(
    cs: ColumnSpace,
    y: np.ndarray,
    title: str = "Projection onto Column Space",
    figsize: tuple = (10, 8),
    views: str = "default",
    show_right_angle: bool = True,
    show_labels: bool = True,
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    y = np.asarray(y, dtype=float).ravel()
    proj = cs.project(y)
    y_hat = proj.y_hat
    e = proj.residuals

    vecs = np.array([y, y_hat])
    scale = float(np.max(np.abs(vecs))) * 1.3
    if scale < 1e-10:
        scale = 2.0

    def _build(cam=None):
        fig = go.Figure()
        for tr in _plane_mesh(cs, scale=scale, color=colors.COLUMN_SPACE):
            fig.add_trace(tr)
        for tr in _vec3_trace([0, 0, 0], y, colors.RESPONSE_Y, "y" if show_labels else ""):
            fig.add_trace(tr)
        for tr in _vec3_trace([0, 0, 0], y_hat, colors.PROJECTION, "\u0177" if show_labels else ""):
            fig.add_trace(tr)
        for tr in _vec3_trace(y_hat, e, colors.RESIDUAL, "e" if show_labels else ""):
            fig.add_trace(tr)
        if show_right_angle and np.linalg.norm(e) > 1e-10 and np.linalg.norm(y_hat) > 1e-10:
            fig.add_trace(_right_angle_trace(y_hat, -y_hat, e, size=scale * 0.06))
        scene = dict(DEFAULT_SCENE)
        if cam:
            scene["camera"] = cam
        fig.update_layout(**DEFAULT_LAYOUT, title=title,
                          width=figsize[0] * 80, height=figsize[1] * 80,
                          scene=scene)
        _apply_extras(fig, interactive_extras)
        return fig

    if views == "three_panel":
        cams = [
            dict(eye=dict(x=1.5, y=1.5, z=1.2)),
            dict(eye=dict(x=2.0, y=0.0, z=0.0)),
            dict(eye=dict(x=0.0, y=0.0, z=2.5)),
        ]
        figs = [_build(c) for c in cams]
        outs = []
        for f in figs:
            out = widgets.Output()
            with out:
                f.show()
            outs.append(out)
        return widgets.HBox(outs)
    if views == "top_down":
        return _build(dict(eye=dict(x=0.0, y=0.0, z=2.5)))
    return _build()


def plot_relevant_triangle(
    cs: ColumnSpace,
    y: np.ndarray,
    j: int,
    title: str = None,
    figsize: tuple = (8, 6),
    show_beta: bool = True,
    show_se: bool = True,
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    if title is None:
        title = f"Relevant Triangle for x_{j}"
    tri = cs.relevant_triangle(y, j)
    y_resid = tri["y_resid"]
    xj_resid = tri["xj_resid"]
    beta_j = tri["beta_j"]
    se_j = tri["se_j"]
    ang = tri["angle"]

    xj_norm = np.linalg.norm(xj_resid)
    if xj_norm < 1e-15:
        e1 = np.zeros_like(xj_resid); e1[0] = 1.0
    else:
        e1 = xj_resid / xj_norm
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
    xj_2d = np.array([np.dot(xj_resid, e1), np.dot(xj_resid, e2)])
    yr_2d = np.array([np.dot(y_resid, e1), np.dot(y_resid, e2)])
    proj_2d = np.array([np.dot(y_resid, e1), 0.0])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, yr_2d[0]], y=[0, yr_2d[1]], mode="lines+markers",
                             line=dict(color=colors.RESPONSE_Y, width=3), name="y_resid"))
    fig.add_trace(go.Scatter(x=[0, xj_2d[0]], y=[0, xj_2d[1]], mode="lines+markers",
                             line=dict(color=colors.COLUMN_SPACE, width=3), name=f"x_{j}_resid"))
    fig.add_trace(go.Scatter(x=[0, proj_2d[0]], y=[0, proj_2d[1]], mode="lines+markers",
                             line=dict(color=colors.PROJECTION, width=2), name="proj"))
    resid_vec = yr_2d - proj_2d
    fig.add_trace(go.Scatter(x=[proj_2d[0], yr_2d[0]], y=[proj_2d[1], yr_2d[1]], mode="lines",
                             line=dict(color=colors.RESIDUAL, width=2, dash="dash"), name="resid"))

    annotations = []
    if show_beta:
        annotations.append(f"beta_{j} = {beta_j:.4f}")
    if show_se:
        se_str = f"{se_j:.4f}" if np.isfinite(se_j) else "inf"
        annotations.append(f"SE(beta_{j}) = {se_str}")
    if ang > 1e-6:
        annotations.append(f"theta = {np.degrees(ang):.1f} deg")

    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      yaxis=dict(scaleanchor="x"),
                      annotations=[dict(x=0.02, y=0.98, xref="paper", yref="paper",
                                        text="<br>".join(annotations), showarrow=False,
                                        font=dict(size=11))] if annotations else [])
    _apply_extras(fig, interactive_extras)
    return fig


def plot_projection_2d(
    x: np.ndarray,
    y: np.ndarray,
    title: str = "Simple Regression as Projection",
    figsize: tuple = (8, 6),
    show_residuals: bool = True,
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    cs = ColumnSpace(x, add_intercept=True)
    proj = cs.project(y)
    b0, b1 = proj.coefficients
    r2 = proj.r_squared

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers",
                             marker=dict(color=colors.SECONDARY, opacity=0.6, size=6),
                             name="Data"))
    x_sorted = np.sort(x)
    fig.add_trace(go.Scatter(x=x_sorted, y=b0 + b1 * x_sorted, mode="lines",
                             line=dict(color=colors.PROJECTION, width=2),
                             name="Regression line"))
    if show_residuals:
        y_hat = proj.y_hat
        for i in range(len(x)):
            fig.add_trace(go.Scatter(x=[x[i], x[i]], y=[y[i], y_hat[i]], mode="lines",
                                     line=dict(color=colors.RESIDUAL, width=1),
                                     showlegend=False, hoverinfo="skip"))
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title="x", yaxis_title="y")
    fig.add_annotation(x=0.02, y=0.98, xref="paper", yref="paper",
                       text=f"y = {b0:.2f} + {b1:.2f}x<br>R² = {r2:.3f}",
                       showarrow=False, font=dict(size=11))
    _apply_extras(fig, interactive_extras)
    return fig


def plot_pythagorean_triangle(
    proj: Projection,
    title: str = "Pythagorean Theorem: SST = SSR + SSE",
    figsize: tuple = (8, 6),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    sst, ssr, sse = proj.sst, proj.ssr, proj.sse
    sqrt_sst = np.sqrt(sst)
    sqrt_ssr = np.sqrt(ssr)
    sqrt_sse = np.sqrt(sse)
    r2 = proj.r_squared
    theta = proj.theta_degrees

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, sqrt_ssr], y=[0, 0], mode="lines",
                             line=dict(color=colors.PROJECTION, width=3),
                             name=f"||y_hat-ybar|| = {sqrt_ssr:.2f}"))
    fig.add_trace(go.Scatter(x=[sqrt_ssr, sqrt_ssr], y=[0, sqrt_sse], mode="lines",
                             line=dict(color=colors.RESIDUAL, width=3),
                             name=f"||e|| = {sqrt_sse:.2f}"))
    fig.add_trace(go.Scatter(x=[0, sqrt_ssr], y=[0, sqrt_sse], mode="lines",
                             line=dict(color=colors.RESPONSE_Y, width=3),
                             name=f"||y-ybar|| = {sqrt_sst:.2f}"))
    fig.add_annotation(x=0.02, y=0.98, xref="paper", yref="paper",
                       text=f"R² = cos²θ = {r2:.3f}<br>θ = {theta:.1f}°",
                       showarrow=False, font=dict(size=11))
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      yaxis=dict(scaleanchor="x"))
    _apply_extras(fig, interactive_extras)
    return fig


def plot_r_squared_angle(
    proj: Projection,
    title: str = "R² as an Angle",
    figsize: tuple = (6, 6),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    theta = proj.theta
    r2 = proj.r_squared

    fig = go.Figure()
    # Unit circle
    t = np.linspace(0, 2 * np.pi, 200)
    fig.add_trace(go.Scatter(x=np.cos(t), y=np.sin(t), mode="lines",
                             line=dict(color=colors.SECONDARY, width=1), opacity=0.4,
                             showlegend=False))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 0], mode="lines",
                             line=dict(color=colors.PROJECTION, width=2.5),
                             name="y_hat direction"))
    fig.add_trace(go.Scatter(x=[0, np.cos(theta)], y=[0, np.sin(theta)], mode="lines",
                             line=dict(color=colors.RESPONSE_Y, width=2.5),
                             name="y direction"))
    # Angle arc
    arc_t = np.linspace(0, theta, 50)
    fig.add_trace(go.Scatter(x=0.2 * np.cos(arc_t), y=0.2 * np.sin(arc_t), mode="lines",
                             line=dict(color=colors.SECONDARY, width=2), name="angle",
                             hovertemplate=f"θ = {np.degrees(theta):.1f}°<br>R² = {r2:.3f}<extra></extra>"))
    fig.add_annotation(x=0.02, y=0.98, xref="paper", yref="paper",
                       text=f"R² = cos²θ = {r2:.3f}",
                       showarrow=False, font=dict(size=11))
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      yaxis=dict(scaleanchor="x"),
                      xaxis=dict(range=[-1.3, 1.3]), yaxis_range=[-1.3, 1.3])
    _apply_extras(fig, interactive_extras)
    return fig


def plot_leverage(
    hm: HatMatrix,
    threshold: float = None,
    title: str = "Leverage Values (Hat Matrix Diagonal)",
    figsize: tuple = (10, 4),
    highlight_indices: list = None,
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    h = hm.diagonal()
    n = len(h)
    if threshold is None:
        threshold = 2.0 * hm.average_leverage()
    bar_colors = [colors.RESIDUAL if h[i] > threshold else colors.SECONDARY for i in range(n)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(n)), y=h, marker_color=bar_colors, name="h_ii",
                         hovertemplate="Obs %{x}<br>h_ii = %{y:.4f}<extra></extra>"))
    fig.add_hline(y=threshold, line_dash="dash", line_color=colors.RESIDUAL,
                  annotation_text=f"Threshold = {threshold:.3f}")
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title="Observation index", yaxis_title="Leverage h_ii")
    _apply_extras(fig, interactive_extras)
    return fig


def plot_cooks_distance(
    cooks_d: np.ndarray,
    title: str = "Cook's Distance",
    figsize: tuple = (10, 4),
    threshold: float = None,
    highlight_indices: list = None,
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    cooks_d = np.asarray(cooks_d, dtype=float).ravel()
    n = len(cooks_d)
    if threshold is None:
        threshold = 4.0 / n
    bar_colors = [colors.RESIDUAL if cooks_d[i] > threshold else colors.SECONDARY for i in range(n)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(n)), y=cooks_d, marker_color=bar_colors, name="Cook's D",
                         hovertemplate="Obs %{x}<br>Cook's D = %{y:.4f}<extra></extra>"))
    fig.add_hline(y=threshold, line_dash="dash", line_color=colors.RESIDUAL,
                  annotation_text=f"Threshold = {threshold:.3f}")
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title="Observation index", yaxis_title="Cook's Distance")
    _apply_extras(fig, interactive_extras)
    return fig


def plot_influence_diagram(
    hm: HatMatrix,
    residuals: np.ndarray,
    mse: float,
    p: int,
    title: str = "Leverage vs. Residual (Influence Diagram)",
    figsize: tuple = (8, 6),
    highlight_indices: list = None,
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    h = hm.diagonal()
    residuals = np.asarray(residuals, dtype=float).ravel()
    e2 = residuals ** 2
    cd = hm.cooks_distance(residuals, mse, p)
    cd_finite = np.where(np.isfinite(cd), cd, 0.0)
    max_cd = max(cd_finite.max(), 1e-15)
    sizes = 5 + 25 * (cd_finite / max_cd)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=h, y=e2, mode="markers",
        marker=dict(size=sizes, color=colors.COLUMN_SPACE, opacity=0.6,
                    line=dict(color=colors.SECONDARY, width=0.5)),
        name="Observations",
        hovertemplate="Obs %{pointNumber}<br>Leverage: %{x:.4f}<br>e²: %{y:.4f}<extra></extra>",
    ))
    lev_threshold = 2.0 * hm.average_leverage()
    fig.add_vline(x=lev_threshold, line_dash="dot", line_color=colors.RESIDUAL,
                  annotation_text=f"Lev = {lev_threshold:.3f}")
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title="Leverage h_ii", yaxis_title="Squared Residual e²")
    _apply_extras(fig, interactive_extras)
    return fig


def plot_eigenvalue_ellipsoid(
    ell: Ellipsoid,
    title: str = "Eigenvalue Ellipsoid of X'X",
    figsize: tuple = (8, 8),
    views: str = "default",
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    _evals = ell.eigenvalues() if callable(ell.eigenvalues) else ell.eigenvalues
    p = len(_evals)
    if p > 3:
        return plot_eigenvalue_bar(ell, title=title, figsize=figsize, **kwargs)

    lengths = ell.axis_lengths() if callable(getattr(ell, 'axis_lengths', None)) else ell.axis_lengths
    Q = ell.eigenvectors() if callable(ell.eigenvectors) else ell.eigenvectors

    fig = go.Figure()
    if p == 3:
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        sx = lengths[0] * np.outer(np.cos(u), np.sin(v))
        sy = lengths[1] * np.outer(np.sin(u), np.sin(v))
        sz = lengths[2] * np.outer(np.ones_like(u), np.cos(v))
        shape = sx.shape
        xyz = np.stack([sx.ravel(), sy.ravel(), sz.ravel()])
        rotated = Q @ xyz
        sx, sy, sz = rotated[0].reshape(shape), rotated[1].reshape(shape), rotated[2].reshape(shape)
        fig.add_trace(go.Surface(x=sx, y=sy, z=sz, opacity=colors.SURFACE_ALPHA,
                                 colorscale=[[0, colors.CONSTRAINT], [1, colors.CONSTRAINT]],
                                 showscale=False, name="Ellipsoid"))
        fig.update_layout(scene=DEFAULT_SCENE)
    elif p == 2:
        t = np.linspace(0, 2 * np.pi, 200)
        pts = np.column_stack([lengths[0] * np.cos(t), lengths[1] * np.sin(t)])
        rotated = pts @ Q.T
        fig.add_trace(go.Scatter(x=rotated[:, 0], y=rotated[:, 1], mode="lines",
                                 line=dict(color=colors.COLUMN_SPACE, width=2), name="Ellipse"))
    else:
        fig.add_trace(go.Scatter(x=[-lengths[0], lengths[0]], y=[0, 0], mode="lines",
                                 line=dict(color=colors.COLUMN_SPACE, width=3), name="Line"))
    cond = ell.condition_number() if callable(ell.condition_number) else ell.condition_number
    cond_str = f"{cond:.1f}" if np.isfinite(cond) else "inf"
    fig.update_layout(**DEFAULT_LAYOUT, title=f"{title}<br>Condition number: {cond_str}",
                      width=figsize[0] * 80, height=figsize[1] * 80)
    _apply_extras(fig, interactive_extras)
    return fig


def plot_eigenvalue_bar(
    ell: Ellipsoid,
    title: str = "Eigenvalues of X'X",
    figsize: tuple = (8, 4),
    log_scale: bool = False,
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    evals = ell.eigenvalues() if callable(ell.eigenvalues) else ell.eigenvalues
    p = len(evals)
    max_e = evals[0] if evals[0] > 0 else 1.0
    bar_colors = []
    for ev in evals:
        frac = ev / max_e if max_e > 1e-15 else 0.0
        bar_colors.append(colors.PROJECTION if frac > 0.3 else
                          colors.RESPONSE_Y if frac > 0.1 else
                          colors.RESIDUAL)
    fig = go.Figure(data=[go.Bar(
        x=list(range(p)), y=evals, marker_color=bar_colors,
        hovertemplate="Component %{x}<br>Eigenvalue: %{y:.4f}<extra></extra>",
    )])
    cond = ell.condition_number() if callable(ell.condition_number) else ell.condition_number
    cond_str = f"{cond:.1f}" if np.isfinite(cond) else "inf"
    fig.add_annotation(x=0.98, y=0.95, xref="paper", yref="paper",
                       text=f"kappa = {cond_str}", showarrow=False, font=dict(size=11))
    yaxis_kw = dict(type="log") if (log_scale and all(evals > 0)) else {}
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title="Eigenvalue index", yaxis_title="Eigenvalue",
                      yaxis=yaxis_kw)
    _apply_extras(fig, interactive_extras)
    return fig


def plot_collinearity_comparison(
    cs_low: ColumnSpace,
    cs_high: ColumnSpace,
    y: np.ndarray,
    titles: tuple = ("Low Collinearity", "High Collinearity"),
    figsize: tuple = (14, 6),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    from plotly.subplots import make_subplots
    y = np.asarray(y, dtype=float).ravel()
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "scene"}, {"type": "scene"}]],
                        subplot_titles=list(titles))
    for col, (cs, subtitle) in enumerate([(cs_low, titles[0]), (cs_high, titles[1])], 1):
        proj = cs.project(y)
        vecs = np.array([y, proj.y_hat])
        scale = float(np.max(np.abs(vecs))) * 1.3
        if scale < 1e-10:
            scale = 2.0
        scene_key = f"scene{col}" if col > 1 else "scene"
        for tr in _plane_mesh(cs, scale=scale, color=colors.COLUMN_SPACE):
            tr.update(scene=scene_key)
            fig.add_trace(tr, row=1, col=col)
        for tr in _vec3_trace([0, 0, 0], y, colors.RESPONSE_Y, "y"):
            tr.update(scene=scene_key)
            fig.add_trace(tr, row=1, col=col)
        for tr in _vec3_trace([0, 0, 0], proj.y_hat, colors.PROJECTION, "\u0177"):
            tr.update(scene=scene_key)
            fig.add_trace(tr, row=1, col=col)
        for tr in _vec3_trace(proj.y_hat, proj.residuals, colors.RESIDUAL, "e"):
            tr.update(scene=scene_key)
            fig.add_trace(tr, row=1, col=col)
    fig.update_layout(**DEFAULT_LAYOUT, title="Collinearity Comparison",
                      width=figsize[0] * 80, height=figsize[1] * 80)
    for key in ["scene", "scene2"]:
        fig.update_layout(**{key: DEFAULT_SCENE})
    _apply_extras(fig, interactive_extras)
    return fig


def plot_fwl_decomposition(
    X: np.ndarray,
    y: np.ndarray,
    j: int,
    title: str = None,
    figsize: tuple = (14, 5),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    if title is None:
        title = f"Frisch-Waugh-Lovell: Isolating x_{j}"
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    fwl = frisch_waugh_lovell(X, y, j)
    coef_full, _, _, _ = np.linalg.lstsq(X, y, rcond=None)

    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=3, subplot_titles=["Full Regression", "Added Variable Plot", "Relevant Triangle"])
    # Panel 1
    xj = X[:, j]
    y_hat_full = X @ coef_full
    sort_idx = np.argsort(xj)
    fig.add_trace(go.Scatter(x=xj, y=y, mode="markers",
                             marker=dict(color=colors.SECONDARY, opacity=0.5, size=4),
                             name="Data"), row=1, col=1)
    fig.add_trace(go.Scatter(x=xj[sort_idx], y=y_hat_full[sort_idx], mode="lines",
                             line=dict(color=colors.PROJECTION, width=2),
                             name=f"beta_{j}={coef_full[j]:.4f}"), row=1, col=1)
    # Panel 2
    y_resid = fwl["y_resid"]
    xj_resid = fwl["xj_resid"]
    beta_j = fwl["beta_j"]
    sort_idx2 = np.argsort(xj_resid)
    fig.add_trace(go.Scatter(x=xj_resid, y=y_resid, mode="markers",
                             marker=dict(color=colors.SECONDARY, opacity=0.5, size=4),
                             name="Residualized"), row=1, col=2)
    fig.add_trace(go.Scatter(x=xj_resid[sort_idx2], y=beta_j * xj_resid[sort_idx2], mode="lines",
                             line=dict(color=colors.PROJECTION, width=2),
                             name=f"slope={beta_j:.4f}"), row=1, col=2)
    # Panel 3: simplified relevant triangle
    xj_n = np.linalg.norm(xj_resid)
    if xj_n > 1e-15:
        e1 = xj_resid / xj_n
    else:
        e1 = np.zeros_like(xj_resid); e1[0] = 1.0
    y_on_e1 = np.dot(y_resid, e1)
    y_comp = y_resid - y_on_e1 * e1
    y_comp_n = np.linalg.norm(y_comp)
    if y_comp_n > 1e-15:
        e2 = y_comp / y_comp_n
    else:
        e2 = np.zeros_like(e1); e2[min(1, len(e2) - 1)] = 1.0
    xj_2d = np.array([np.dot(xj_resid, e1), np.dot(xj_resid, e2)])
    yr_2d = np.array([np.dot(y_resid, e1), np.dot(y_resid, e2)])
    proj_2d = np.array([y_on_e1, 0.0])
    fig.add_trace(go.Scatter(x=[0, yr_2d[0]], y=[0, yr_2d[1]], mode="lines",
                             line=dict(color=colors.RESPONSE_Y, width=2), name="y_r"), row=1, col=3)
    fig.add_trace(go.Scatter(x=[0, xj_2d[0]], y=[0, xj_2d[1]], mode="lines",
                             line=dict(color=colors.COLUMN_SPACE, width=2), name=f"x_{j}_r"), row=1, col=3)
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80)
    _apply_extras(fig, interactive_extras)
    return fig


def plot_added_variable(
    X: np.ndarray,
    y: np.ndarray,
    j: int,
    title: str = None,
    figsize: tuple = (7, 6),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    if title is None:
        title = f"Added Variable Plot for x_{j}"
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    fwl = frisch_waugh_lovell(X, y, j)
    y_resid = fwl["y_resid"]
    xj_resid = fwl["xj_resid"]
    beta_j = fwl["beta_j"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xj_resid, y=y_resid, mode="markers",
                             marker=dict(color=colors.SECONDARY, opacity=0.5, size=5),
                             name="Data"))
    sort_idx = np.argsort(xj_resid)
    fig.add_trace(go.Scatter(x=xj_resid[sort_idx], y=beta_j * xj_resid[sort_idx], mode="lines",
                             line=dict(color=colors.PROJECTION, width=2),
                             name=f"slope = beta_{j} = {beta_j:.4f}"))
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title=f"M_(-{j}) x_{j}", yaxis_title=f"M_(-{j}) y")
    _apply_extras(fig, interactive_extras)
    return fig


def plot_ridge_lasso_constraint(
    beta_ols: np.ndarray,
    lam_values: list = None,
    title: str = "Ridge vs. LASSO Constraints",
    figsize: tuple = (14, 6),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    beta_ols = np.asarray(beta_ols, dtype=float).ravel()
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=["L2 (Ridge)", "L1 (LASSO)"])
    ols_norm_l2 = np.linalg.norm(beta_ols)
    ols_norm_l1 = np.sum(np.abs(beta_ols))
    r_l2 = max(ols_norm_l2 * 0.6, 1e-10)
    r_l1 = max(ols_norm_l1 * 0.6, 1e-10)

    t = np.linspace(0, 2 * np.pi, 200)
    for col, (radius, norm_type) in enumerate([(r_l2, "ridge"), (r_l1, "lasso")], 1):
        if norm_type == "ridge":
            cx, cy = radius * np.cos(t), radius * np.sin(t)
        else:
            cx = np.array([radius, 0, -radius, 0, radius], dtype=float)
            cy = np.array([0, radius, 0, -radius, 0], dtype=float)
        fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines",
                                 line=dict(color=colors.CONSTRAINT, width=2),
                                 name=norm_type.title()), row=1, col=col)
        fig.add_trace(go.Scatter(x=[float(beta_ols[0])], y=[float(beta_ols[1]) if len(beta_ols) > 1 else 0],
                                 mode="markers", marker=dict(color=colors.PROJECTION, size=8),
                                 name="OLS"), row=1, col=col)
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80)
    _apply_extras(fig, interactive_extras)
    return fig


def plot_shrinkage_path(
    ell: Ellipsoid,
    beta_ols: np.ndarray,
    lam_range: np.ndarray = None,
    title: str = "Ridge Shrinkage Path",
    figsize: tuple = (10, 6),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    beta_ols = np.asarray(beta_ols, dtype=float).ravel()
    if lam_range is None:
        lam_range = np.logspace(-2, 4, 200)
    p = len(beta_ols)
    paths = np.zeros((len(lam_range), p))
    for i, lam_val in enumerate(lam_range):
        paths[i] = ell.ridge_coefficients(beta_ols, lam_val)

    import plotly.express as px
    cmap = px.colors.qualitative.Plotly
    fig = go.Figure()
    for k in range(p):
        fig.add_trace(go.Scatter(
            x=np.log10(lam_range), y=paths[:, k], mode="lines",
            line=dict(color=cmap[k % len(cmap)], width=1.5),
            name=f"beta_{k}",
            hovertemplate="log10(lambda)=%{x:.2f}<br>beta=%{y:.4f}<extra></extra>",
        ))
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title="log10(lambda)", yaxis_title="Coefficient value")
    _apply_extras(fig, interactive_extras)
    return fig


def plot_nested_projections(
    cs_restricted: ColumnSpace,
    cs_full: ColumnSpace,
    y: np.ndarray,
    title: str = "F-test: Comparing Two Projections",
    figsize: tuple = (10, 8),
    views: str = "default",
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    y = np.asarray(y, dtype=float).ravel()
    proj_r = cs_restricted.project(y)
    proj_f = cs_full.project(y)
    vecs = np.array([y, proj_r.y_hat, proj_f.y_hat])
    scale = float(np.max(np.abs(vecs))) * 1.3
    if scale < 1e-10:
        scale = 2.0

    fig = go.Figure()
    for tr in _plane_mesh(cs_full, scale=scale, color=colors.COLUMN_SPACE, opacity=0.15):
        fig.add_trace(tr)
    for tr in _vec3_trace([0, 0, 0], y, colors.RESPONSE_Y, "y"):
        fig.add_trace(tr)
    for tr in _vec3_trace([0, 0, 0], proj_r.y_hat, colors.PROJECTION, "y_hat_restricted"):
        fig.add_trace(tr)
    for tr in _vec3_trace([0, 0, 0], proj_f.y_hat, colors.COLUMN_SPACE, "y_hat_full"):
        fig.add_trace(tr)
    gap = proj_f.y_hat - proj_r.y_hat
    for tr in _vec3_trace(proj_r.y_hat, gap, colors.CONSTRAINT, "gap"):
        fig.add_trace(tr)
    for tr in _vec3_trace(proj_f.y_hat, proj_f.residuals, colors.RESIDUAL, "e_full"):
        fig.add_trace(tr)

    sse_r, sse_f = proj_r.sse, proj_f.sse
    df1 = cs_full.p - cs_restricted.p
    df2 = cs_full.n - cs_full.p
    if df1 > 0 and df2 > 0 and sse_f > 1e-15:
        f_stat = ((sse_r - sse_f) / df1) / (sse_f / df2)
        fig.add_annotation(x=0.02, y=0.95, xref="paper", yref="paper",
                           text=f"F = {f_stat:.2f}", showarrow=False, font=dict(size=12))
    fig.update_layout(**DEFAULT_LAYOUT, title=title,
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      scene=DEFAULT_SCENE)
    _apply_extras(fig, interactive_extras)
    return fig


def plot_confidence_ellipse(
    beta: np.ndarray,
    cov: np.ndarray,
    confidence: float = 0.95,
    indices: tuple = (0, 1),
    title: str = "Confidence Ellipse",
    figsize: tuple = (7, 7),
    interactive_extras: dict = None,
    **kwargs,
) -> "go.Figure":
    from scipy import stats
    beta = np.asarray(beta, dtype=float).ravel()
    cov = np.asarray(cov, dtype=float)
    i, j_idx = indices
    sub_cov = cov[np.ix_([i, j_idx], [i, j_idx])]
    center = np.array([beta[i], beta[j_idx]])
    vals, vecs = np.linalg.eigh(sub_cov)
    vals = np.maximum(vals, 0.0)
    chi2_val = stats.chi2.ppf(confidence, df=2)
    t = np.linspace(0, 2 * np.pi, 200)
    ell = vecs @ np.diag(np.sqrt(vals * chi2_val)) @ np.array([np.cos(t), np.sin(t)])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ell[0] + center[0], y=ell[1] + center[1], mode="lines",
                             line=dict(color=colors.COLUMN_SPACE, width=2),
                             name="Confidence Ellipse", fill="toself",
                             fillcolor=f"rgba(59,130,246,0.15)"))
    fig.add_trace(go.Scatter(x=[float(center[0])], y=[float(center[1])], mode="markers",
                             marker=dict(color=colors.PROJECTION, size=8), name="beta_hat"))
    fig.update_layout(**DEFAULT_LAYOUT,
                      title=f"{title} ({confidence*100:.0f}%)",
                      width=figsize[0] * 80, height=figsize[1] * 80,
                      xaxis_title=f"beta_{i}", yaxis_title=f"beta_{j_idx}",
                      yaxis=dict(scaleanchor="x"))
    _apply_extras(fig, interactive_extras)
    return fig


def plot_scoreboard(
    proj: Projection,
    cs: ColumnSpace,
    active_gauges: list = None,
    title: str = "Geometric Scoreboard",
    figsize: tuple = (12, 1.5),
    interactive_extras: dict = None,
    **kwargs,
) -> "widgets.HBox":
    from regression_geometry.scoreboard import GeometricScoreboard
    sb = GeometricScoreboard(proj=proj, cs=cs, active_gauges=active_gauges, mode="widget")
    return sb.display()


# ===================================================================
# Interactive-only functions (no equivalent in plots.py)
# ===================================================================

def plot_projection_3d_draggable(
    cs: ColumnSpace,
    y: np.ndarray,
    title: str = "Drag y to Explore the Projection",
    figsize: tuple = (10, 8),
    **kwargs,
) -> "widgets.VBox":
    """Draggable y vector with live-updating projection via sliders."""
    y = np.asarray(y, dtype=float).ravel()
    sliders = [
        widgets.FloatSlider(value=float(y[i]), min=-5, max=5, step=0.1,
                            description=f"y[{i}]", continuous_update=True)
        for i in range(min(len(y), 3))
    ]
    readout = widgets.HTML(value="")
    fig_output = widgets.Output()

    def _rebuild():
        yv = np.array([s.value for s in sliders])
        if len(yv) < cs.n:
            yv = np.concatenate([yv, np.zeros(cs.n - len(yv))])
        proj = cs.project(yv)
        yh = proj.y_hat
        ev = proj.residuals
        vecs = np.array([yv, yh])
        scale = float(np.max(np.abs(vecs))) * 1.3
        if scale < 1e-10:
            scale = 2.0
        fig = go.Figure()
        for tr in _plane_mesh(cs, scale=scale, color=colors.COLUMN_SPACE):
            fig.add_trace(tr)
        for tr in _vec3_trace([0, 0, 0], yv[:3], colors.RESPONSE_Y, "y"):
            fig.add_trace(tr)
        for tr in _vec3_trace([0, 0, 0], yh[:3], colors.PROJECTION, "\u0177"):
            fig.add_trace(tr)
        for tr in _vec3_trace(yh[:3], ev[:3], colors.RESIDUAL, "e"):
            fig.add_trace(tr)
        if np.linalg.norm(ev) > 1e-10 and np.linalg.norm(yh) > 1e-10:
            fig.add_trace(_right_angle_trace(yh[:3], -yh[:3], ev[:3], size=scale * 0.06))
        fig.update_layout(**DEFAULT_LAYOUT, title=title,
                          width=figsize[0] * 80, height=figsize[1] * 80,
                          scene=DEFAULT_SCENE)
        fig_output.clear_output(wait=True)
        with fig_output:
            fig.show()
        readout.value = (
            f"<b>\u03b2\u0302</b> = [{', '.join(f'{b:.3f}' for b in proj.coefficients)}] &nbsp; "
            f"<b>R\u00b2</b> = {proj.r_squared:.3f} &nbsp; "
            f"<b>\u03b8</b> = {proj.theta_degrees:.1f}\u00b0 &nbsp; "
            f"<b>||e||</b> = {proj.residual_norm:.3f}"
        )

    def on_change(change):
        _rebuild()

    for s in sliders:
        s.observe(on_change, names="value")
    _rebuild()
    return widgets.VBox([*sliders, fig_output, readout])


def plot_collinearity_slider(
    n: int = 100,
    seed: int = 42,
    title: str = "Collinearity Explorer",
    figsize: tuple = (14, 6),
    **kwargs,
) -> "widgets.VBox":
    slider = widgets.FloatSlider(value=0.0, min=0.0, max=0.99, step=0.01,
                                 description="r(x1,x2)", continuous_update=False)
    readout = widgets.HTML(value="")
    fig_output = widgets.Output()

    def _update(change=None):
        r = slider.value
        rng = np.random.RandomState(seed)
        cov_mat = [[1, r], [r, 1]]
        data = rng.multivariate_normal([0, 0], cov_mat, n)
        x1, x2 = data[:, 0], data[:, 1]
        X = np.column_stack([x1, x2])
        y_vec = 1.0 + 2.0 * x1 + 3.0 * x2 + rng.randn(n) * 0.5
        cs = ColumnSpace(X, add_intercept=True)
        proj = cs.project(y_vec)
        kappa = cs.condition_number()
        evals = cs.eigenvalues()

        # 3D viz uses first 3 obs
        X3 = cs.X[:3]
        y3 = y_vec[:3]
        cs3 = ColumnSpace(X3, add_intercept=False)
        proj3 = cs3.project(y3)
        vecs = np.array([y3, proj3.y_hat])
        scale = float(np.max(np.abs(vecs))) * 1.3
        if scale < 1e-10:
            scale = 2.0

        fig = go.Figure()
        for tr in _plane_mesh(cs3, scale=scale, color=colors.COLUMN_SPACE):
            fig.add_trace(tr)
        for tr in _vec3_trace([0, 0, 0], y3, colors.RESPONSE_Y, "y"):
            fig.add_trace(tr)
        for tr in _vec3_trace([0, 0, 0], proj3.y_hat, colors.PROJECTION, "\u0177"):
            fig.add_trace(tr)
        fig.update_layout(**DEFAULT_LAYOUT, title=title,
                          width=figsize[0] * 80, height=figsize[1] * 80,
                          scene=DEFAULT_SCENE)
        fig_output.clear_output(wait=True)
        with fig_output:
            fig.show()

        vif1 = 1.0 / (1.0 - r ** 2 + 1e-15)
        readout.value = (
            f"<b>\u03ba</b> = {kappa:.1f} &nbsp; "
            f"<b>Eigenvalues</b>: [{', '.join(f'{e:.2f}' for e in evals)}] &nbsp; "
            f"<b>VIF</b> = {vif1:.1f} &nbsp; "
            f"<b>\u03b2\u0302</b> = [{', '.join(f'{b:.3f}' for b in proj.coefficients)}]"
        )

    slider.observe(_update, names="value")
    _update()
    return widgets.VBox([slider, fig_output, readout])


def plot_ridge_lasso_interactive(
    X: np.ndarray,
    y: np.ndarray,
    title: str = "Regularization Explorer",
    figsize: tuple = (14, 6),
    **kwargs,
) -> "widgets.VBox":
    lam_slider = widgets.FloatLogSlider(value=1.0, base=10, min=-2, max=2, step=0.1,
                                        description="lambda", continuous_update=True)
    toggle = widgets.ToggleButtons(options=["Ridge", "LASSO"], value="Ridge")
    readout = widgets.HTML(value="")
    fig_output = widgets.Output()
    cs = ColumnSpace(X, add_intercept=False)
    proj_ols = cs.project(y)
    beta_ols = proj_ols.coefficients[:2]
    ell = Ellipsoid(X.T @ X)

    def _update(change=None):
        lam_val = lam_slider.value
        penalty = toggle.value.lower()
        if penalty == "ridge":
            beta_reg = ell.ridge_coefficients(proj_ols.coefficients, lam_val)
        else:
            from sklearn.linear_model import Lasso
            model = Lasso(alpha=lam_val / (2 * X.shape[0]), fit_intercept=False, max_iter=1000)
            model.fit(X, y)
            beta_reg = model.coef_

        t = np.linspace(0, 2 * np.pi, 200)
        radius = np.linalg.norm(beta_reg[:2])
        if penalty == "ridge":
            cx, cy = radius * np.cos(t), radius * np.sin(t)
        else:
            cx = np.array([radius, 0, -radius, 0, radius], dtype=float)
            cy = np.array([0, radius, 0, -radius, 0], dtype=float)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines",
                                 line=dict(color=colors.CONSTRAINT, width=2), name="Constraint"))
        fig.add_trace(go.Scatter(x=[float(beta_ols[0])],
                                 y=[float(beta_ols[1]) if len(beta_ols) > 1 else 0],
                                 mode="markers", marker=dict(color=colors.PROJECTION, size=10),
                                 name="OLS"))
        fig.add_trace(go.Scatter(x=[float(beta_reg[0])],
                                 y=[float(beta_reg[1]) if len(beta_reg) > 1 else 0],
                                 mode="markers", marker=dict(color=colors.CONSTRAINT, size=10, symbol="diamond"),
                                 name=f"{penalty.title()} solution"))
        fig.update_layout(**DEFAULT_LAYOUT, title=title,
                          width=figsize[0] * 80, height=figsize[1] * 80,
                          yaxis=dict(scaleanchor="x"),
                          xaxis_title="beta_0", yaxis_title="beta_1")
        fig_output.clear_output(wait=True)
        with fig_output:
            fig.show()
        readout.value = (
            f"<b>{penalty.title()}</b> (lambda = {lam_val:.3f}): "
            f"beta = [{', '.join(f'{b:.3f}' for b in beta_reg[:2])}]"
        )

    lam_slider.observe(_update, names="value")
    toggle.observe(_update, names="value")
    _update()
    return widgets.VBox([widgets.HBox([toggle, lam_slider]), fig_output, readout])


def plot_fwl_peeling(
    X: np.ndarray,
    y: np.ndarray,
    title: str = "Frisch-Waugh-Lovell: Peeling Animation",
    figsize: tuple = (10, 8),
    **kwargs,
) -> "widgets.VBox":
    step_counter = widgets.IntSlider(value=1, min=1, max=3, step=1, description="Step")
    step_label = widgets.HTML(value="<b>Step 1/3</b>")
    readout = widgets.HTML(value="")
    fig_output = widgets.Output()

    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float).ravel()
    cs_full = ColumnSpace(X, add_intercept=False)
    proj_full = cs_full.project(y)
    beta_full = proj_full.coefficients
    fwl = frisch_waugh_lovell(X, y, 1)
    x1_resid = fwl["xj_resid"]
    y_resid = fwl["y_resid"]
    beta2_partial = fwl["beta_j"]

    def _update(change=None):
        step = step_counter.value
        step_label.value = f"<b>Step {step}/3</b>"
        fig = go.Figure()
        if step == 1:
            vecs = np.array([y[:3], proj_full.y_hat[:3]])
            scale = float(np.max(np.abs(vecs))) * 1.3
            if scale < 1e-10:
                scale = 2.0
            for tr in _plane_mesh(cs_full, scale=scale, color=colors.COLUMN_SPACE):
                fig.add_trace(tr)
            for tr in _vec3_trace([0, 0, 0], y[:3], colors.RESPONSE_Y, "y"):
                fig.add_trace(tr)
            for tr in _vec3_trace([0, 0, 0], proj_full.y_hat[:3], colors.PROJECTION, "\u0177"):
                fig.add_trace(tr)
            for tr in _vec3_trace(proj_full.y_hat[:3], proj_full.residuals[:3], colors.RESIDUAL, "e"):
                fig.add_trace(tr)
            readout.value = f"<b>Full regression:</b> beta = [{', '.join(f'{b:.3f}' for b in beta_full)}]"
        elif step == 2:
            for tr in _vec3_trace([0, 0, 0], x1_resid[:3], colors.COLUMN_SPACE, "M1*x2"):
                fig.add_trace(tr)
            for tr in _vec3_trace([0, 0, 0], y_resid[:3], colors.RESPONSE_Y, "M1*y"):
                fig.add_trace(tr)
            readout.value = "<b>Step 2:</b> Projected onto orthogonal complement of x1. Plane collapses to line."
        else:
            for tr in _vec3_trace([0, 0, 0], x1_resid[:3], colors.COLUMN_SPACE, "M1*x2"):
                fig.add_trace(tr)
            for tr in _vec3_trace([0, 0, 0], y_resid[:3], colors.RESPONSE_Y, "M1*y"):
                fig.add_trace(tr)
            proj_resid = beta2_partial * x1_resid
            for tr in _vec3_trace([0, 0, 0], proj_resid[:3], colors.PROJECTION, f"beta2={beta2_partial:.3f}"):
                fig.add_trace(tr)
            b1_full = beta_full[1] if len(beta_full) > 1 else float("nan")
            readout.value = (
                f"<b>Step 3:</b> beta2_partial = {beta2_partial:.3f}, "
                f"beta2_full = {b1_full:.3f} (FWL confirmed!)"
            )
        fig.update_layout(**DEFAULT_LAYOUT, title=title,
                          width=figsize[0] * 80, height=figsize[1] * 80, scene=DEFAULT_SCENE)
        fig_output.clear_output(wait=True)
        with fig_output:
            fig.show()

    step_counter.observe(_update, names="value")
    _update()
    return widgets.VBox([widgets.HBox([step_label, step_counter]), fig_output, readout])


def plot_monte_carlo_projections(
    cs: ColumnSpace,
    beta_true: np.ndarray,
    sigma: float,
    n_samples: int = 20,
    seed: int = 42,
    title: str = "Sampling Distribution of Projections",
    figsize: tuple = (10, 8),
    **kwargs,
) -> "widgets.VBox":
    rng = np.random.RandomState(seed)
    X = cs.X
    all_proj = []
    for _ in range(n_samples):
        eps = rng.randn(cs.n) * sigma
        y_sample = X @ beta_true + eps
        all_proj.append(cs.project(y_sample))

    sample_idx = [0]
    collected_yhat = []
    collected_betas = []
    next_btn = widgets.Button(description="Next Sample")
    run_all_btn = widgets.Button(description="Run All")
    readout = widgets.HTML(value="")
    fig_output = widgets.Output()

    def _redraw():
        fig = go.Figure()
        for tr in _plane_mesh(cs, color=colors.COLUMN_SPACE):
            fig.add_trace(tr)
        for i, yh in enumerate(collected_yhat):
            fig.add_trace(go.Scatter3d(
                x=[yh[0]], y=[yh[1]], z=[yh[2]], mode="markers",
                marker=dict(color=colors.PROJECTION, size=4),
                name="", showlegend=False,
                hovertemplate=f"Sample {i+1}<br>y_hat = [{yh[0]:.2f}, {yh[1]:.2f}, {yh[2]:.2f}]<extra></extra>",
            ))
        fig.update_layout(**DEFAULT_LAYOUT, title=title,
                          width=figsize[0] * 80, height=figsize[1] * 80, scene=DEFAULT_SCENE)
        fig_output.clear_output(wait=True)
        with fig_output:
            fig.show()

    def _add_sample():
        idx = sample_idx[0]
        if idx >= n_samples:
            return
        proj = all_proj[idx]
        yh = proj.y_hat[:3]
        collected_yhat.append(yh)
        collected_betas.append(proj.coefficients)
        sample_idx[0] = idx + 1
        _redraw()
        mean_beta = np.mean(collected_betas, axis=0)
        readout.value = (
            f"<b>Samples:</b> {sample_idx[0]}/{n_samples} &nbsp; "
            f"<b>Mean beta_hat:</b> [{', '.join(f'{b:.3f}' for b in mean_beta)}] &nbsp; "
            f"<b>beta_true:</b> [{', '.join(f'{b:.3f}' for b in beta_true)}]"
        )

    def on_next(btn):
        _add_sample()

    def on_run_all(btn):
        while sample_idx[0] < n_samples:
            _add_sample()

    next_btn.on_click(on_next)
    run_all_btn.on_click(on_run_all)
    _redraw()
    return widgets.VBox([widgets.HBox([next_btn, run_all_btn]), fig_output, readout])
