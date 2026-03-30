"""Generate the Rosetta Stone cheat sheet — geometric concept <-> code."""

from __future__ import annotations

from pathlib import Path

from IPython.display import display, HTML

from regression_geometry import colors

CHEATSHEET_ENTRIES = [
    {
        "geometric_concept": "Column space of X",
        "what_it_means": "The set of all possible predictions from the model",
        "code": [
            "np.linalg.matrix_rank(X)",
            "scipy.linalg.orth(X)",
        ],
    },
    {
        "geometric_concept": "Projection \u0177 = Hy",
        "what_it_means": "Fitted values \u2014 the shadow on the wall",
        "code": ["model.fittedvalues"],
    },
    {
        "geometric_concept": "Residual e = y \u2212 \u0177",
        "what_it_means": "The perpendicular gap between data and prediction",
        "code": ["model.resid"],
    },
    {
        "geometric_concept": "Orthogonality X\u2032e = 0",
        "what_it_means": "Residuals are perpendicular to every predictor (by construction)",
        "code": ["X.T @ model.resid  # \u2248 0"],
    },
    {
        "geometric_concept": "Hat matrix diagonal h\u1d62\u1d62",
        "what_it_means": "Leverage \u2014 how much pull observation i has on the projection",
        "code": ["OLSInfluence(model).hat_matrix_diag"],
    },
    {
        "geometric_concept": "Angle \u03b8 between y and \u0177",
        "what_it_means": "How far the data is from the column space",
        "code": ["np.arccos(np.sqrt(model.rsquared))"],
    },
    {
        "geometric_concept": "R\u00b2 = cos\u00b2\u03b8",
        "what_it_means": "Proportion of variance explained = cosine squared of the angle",
        "code": ["model.rsquared"],
    },
    {
        "geometric_concept": "Condition number \u03ba",
        "what_it_means": "How thin the column space is \u2014 stability of the projection",
        "code": ["np.linalg.cond(X)"],
    },
    {
        "geometric_concept": "Eigenvalues of X\u2032X",
        "what_it_means": "Widths of the column space in each principal direction",
        "code": ["np.linalg.eigvalsh(X.T @ X)"],
    },
    {
        "geometric_concept": "Cook\u2019s distance D\u1d62",
        "what_it_means": "Influence = leverage \u00d7 surprise (how much obs i moves the projection)",
        "code": ["OLSInfluence(model).cooks_distance[0]"],
    },
    {
        "geometric_concept": "FWL residualized vectors",
        "what_it_means": "\u201cPeeling out\u201d other variables to isolate one coefficient",
        "code": ["sm.OLS(x_j, sm.add_constant(X_others)).fit().resid"],
    },
    {
        "geometric_concept": "SST = SSR + SSE",
        "what_it_means": "Pythagorean theorem \u2014 squared lengths of a right triangle",
        "code": [
            "model.centered_tss  # SST",
            "model.ess           # SSR (explained)",
            "model.ssr           # SSE (residual \u2014 confusing naming!)",
        ],
    },
]


def generate_cheatsheet_html(
    output_path: str = None,
    title: str = "Regression Geometry \u2014 Rosetta Stone",
    subtitle: str = "Geometric Concept \u2194 Python Code",
) -> str:
    """Generate the cheat sheet as a self-contained HTML file.

    Parameters
    ----------
    output_path : str, optional
        If provided, write the HTML to this file path.
    title : str
        Title at the top of the cheat sheet.
    subtitle : str
        Subtitle below the title.

    Returns
    -------
    str
        The complete HTML content.
    """
    rows_html = []
    for entry in CHEATSHEET_ENTRIES:
        code_lines = "<br>".join(
            f"<code>{line}</code>" for line in entry["code"]
        )
        rows_html.append(f"""
        <tr>
            <td class="concept">
                <div class="concept-name">{entry['geometric_concept']}</div>
                <div class="concept-desc">{entry['what_it_means']}</div>
            </td>
            <td class="code-col">{code_lines}</td>
        </tr>""")

    table_rows = "\n".join(rows_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                     'Helvetica Neue', Arial, sans-serif;
        color: #1F2937;
        background: #FFFFFF;
        line-height: 1.4;
        padding: 24px 32px;
    }}

    .header {{
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 3px solid {colors.COLUMN_SPACE};
    }}

    .header h1 {{
        font-size: 22px;
        font-weight: 700;
        color: {colors.COLUMN_SPACE};
        margin-bottom: 4px;
    }}

    .header .subtitle {{
        font-size: 14px;
        color: {colors.SECONDARY};
        font-weight: 400;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 16px;
    }}

    thead th {{
        background: {colors.COLUMN_SPACE};
        color: white;
        padding: 8px 12px;
        text-align: left;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    thead th:first-child {{ width: 50%; border-radius: 4px 0 0 0; }}
    thead th:last-child {{ border-radius: 0 4px 0 0; }}

    tbody tr {{
        border-bottom: 1px solid #E5E7EB;
    }}

    tbody tr:nth-child(even) {{
        background: #F9FAFB;
    }}

    td {{
        padding: 8px 12px;
        vertical-align: top;
        font-size: 13px;
    }}

    .concept-name {{
        font-weight: 600;
        color: #111827;
        margin-bottom: 2px;
    }}

    .concept-desc {{
        color: {colors.SECONDARY};
        font-size: 12px;
        font-style: italic;
    }}

    .code-col code {{
        font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 12px;
        background: #F3F4F6;
        padding: 2px 6px;
        border-radius: 3px;
        color: #1E40AF;
        display: inline-block;
        margin: 1px 0;
    }}

    .footer {{
        text-align: center;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid #E5E7EB;
        font-size: 11px;
        color: {colors.SECONDARY};
    }}

    .footer .course {{
        font-style: italic;
    }}

    /* Print-friendly styles */
    @media print {{
        body {{
            padding: 12px 16px;
            font-size: 11px;
        }}

        .header h1 {{ font-size: 18px; }}
        .header .subtitle {{ font-size: 12px; }}
        .header {{ margin-bottom: 12px; padding-bottom: 10px; }}

        table {{ page-break-inside: auto; }}
        tr {{ page-break-inside: avoid; page-break-after: auto; }}

        td {{ padding: 5px 8px; font-size: 11px; }}
        .concept-desc {{ font-size: 10px; }}
        .code-col code {{ font-size: 10px; padding: 1px 4px; }}

        thead th {{ font-size: 11px; padding: 6px 8px; }}

        .footer {{ font-size: 9px; margin-top: 10px; }}
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="subtitle">{subtitle}</div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Geometric Concept</th>
                <th>Python Code</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>

    <div class="footer">
        <div class="course">From: Regression from the Inside &mdash; Seeing the Geometry of Linear Models</div>
        <div>Built on the Projection Theorem</div>
    </div>
</body>
</html>"""

    if output_path is not None:
        Path(output_path).write_text(html, encoding="utf-8")

    return html


def display_cheatsheet() -> None:
    """Display the cheat sheet inline in a Jupyter notebook."""
    html = generate_cheatsheet_html()
    display(HTML(html))
