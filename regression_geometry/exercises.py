"""Utilities for creating standardized exercise cells in notebooks."""

import numpy as np
from IPython.display import display, HTML


# ---------------------------------------------------------------------------
# Exercise display functions
# ---------------------------------------------------------------------------

def predict_first(description: str, question: str) -> None:
    """Display a formatted Predict First exercise block.

    Parameters
    ----------
    description : str
        1-3 sentences describing what is about to happen.
    question : str
        The specific prediction the student should make.
    """
    html = f"""
    <div style="border: 2px solid #EF4444; border-radius: 8px; padding: 16px 20px;
                margin: 16px 0; background: #FEF2F2; font-family: sans-serif;">
        <div style="font-size: 16px; font-weight: bold; color: #B91C1C; margin-bottom: 10px;">
            &#x1F6D1; PREDICT FIRST
        </div>
        <p style="color: #1F2937; margin: 8px 0; line-height: 1.5;">{description}</p>
        <p style="color: #1F2937; font-weight: 600; margin: 12px 0 8px 0;">
            Before running the next cell, write your prediction below:
        </p>
        <p style="color: #991B1B; font-style: italic; margin: 8px 0;">{question}</p>
        <textarea rows="3" style="width: 100%; border: 1px solid #D1D5DB; border-radius: 4px;
                  padding: 8px; font-family: sans-serif; font-size: 13px; resize: vertical;"
                  placeholder="Your prediction..."></textarea>
    </div>
    """
    display(HTML(html))


def diagnose_first(summary_text: str, question: str) -> None:
    """Display a formatted Diagnose First exercise block.

    Parameters
    ----------
    summary_text : str
        A statsmodels summary or numerical output to display.
    question : str
        The geometric question the student should answer.
    """
    html = f"""
    <div style="border: 2px solid #EF4444; border-radius: 8px; padding: 16px 20px;
                margin: 16px 0; background: #FEF2F2; font-family: sans-serif;">
        <div style="font-size: 16px; font-weight: bold; color: #B91C1C; margin-bottom: 10px;">
            &#x1F6D1; DIAGNOSE FIRST
        </div>
        <pre style="background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 4px;
                    padding: 12px; font-size: 12px; overflow-x: auto; line-height: 1.4;
                    font-family: 'Courier New', monospace;">{summary_text}</pre>
        <p style="color: #1F2937; font-weight: 600; margin: 12px 0 8px 0;">
            Before looking at any visualizations, answer:
        </p>
        <p style="color: #991B1B; font-style: italic; margin: 8px 0;">{question}</p>
        <textarea rows="4" style="width: 100%; border: 1px solid #D1D5DB; border-radius: 4px;
                  padding: 8px; font-family: sans-serif; font-size: 13px; resize: vertical;"
                  placeholder="Your diagnosis..."></textarea>
    </div>
    """
    display(HTML(html))


def memo(recipient: str, task: str, banned_words: list) -> None:
    """Display a formatted Memo exercise block.

    Parameters
    ----------
    recipient : str
        e.g., "Meridian's VP of HR"
    task : str
        e.g., "explain why the gender coefficient changed"
    banned_words : list of str
        Words the student cannot use.
    """
    banned_str = ", ".join(f"<em>{w}</em>" for w in banned_words)
    html = f"""
    <div style="border: 2px solid #8B5CF6; border-radius: 8px; padding: 16px 20px;
                margin: 16px 0; background: #F5F3FF; font-family: sans-serif;">
        <div style="font-size: 16px; font-weight: bold; color: #6D28D9; margin-bottom: 10px;">
            &#x270D;&#xFE0F; The Memo
        </div>
        <p style="color: #1F2937; margin: 8px 0; line-height: 1.5;">
            You're writing a memo to <strong>{recipient}</strong>.
        </p>
        <p style="color: #1F2937; margin: 8px 0; line-height: 1.5;">
            In 3 sentences, {task}.
        </p>
        <p style="color: #6D28D9; font-weight: 600; margin: 12px 0 4px 0;">
            Banned words: {banned_str}
        </p>
        <p style="color: #6B7280; font-size: 12px; margin: 4px 0 8px 0;">
            Write in plain English a non-technical manager would understand.
        </p>
        <textarea rows="5" style="width: 100%; border: 1px solid #D1D5DB; border-radius: 4px;
                  padding: 8px; font-family: sans-serif; font-size: 13px; resize: vertical;"
                  placeholder="Your memo..."></textarea>
    </div>
    """
    display(HTML(html))


def reveal(text: str, label: str = "Compare to your prediction above") -> None:
    """Display a reveal block after a Predict First exercise.

    Parameters
    ----------
    text : str
        The reveal explanation.
    label : str
        Header label for the reveal box.
    """
    html = f"""
    <div style="border-left: 4px solid #10B981; padding: 12px 16px; margin: 16px 0;
                background: #F0FDF4; font-family: sans-serif; border-radius: 0 8px 8px 0;">
        <div style="font-size: 14px; font-weight: bold; color: #065F46; margin-bottom: 8px;">
            {label}
        </div>
        <p style="color: #1F2937; line-height: 1.5; margin: 0;">{text}</p>
    </div>
    """
    display(HTML(html))


# ---------------------------------------------------------------------------
# Diagnostic challenge generator
# ---------------------------------------------------------------------------

def _standardize(x):
    """Standardize a vector to mean 0, std 1."""
    s = x.std()
    if s < 1e-12:
        return x - x.mean()
    return (x - x.mean()) / s


def _generate_easy(rng):
    """House prices with one extreme leverage point."""
    n = 80
    sqft = rng.normal(1800, 400, n)
    sqft = np.clip(sqft, 600, 4000)
    bedrooms = rng.poisson(3, n).astype(float)
    bedrooms = np.clip(bedrooms, 1, 6)

    noise = rng.normal(0, 25000, n)
    price = 50000 + 120 * sqft + 15000 * bedrooms + noise

    # Inject one extreme leverage point: a mansion
    sqft[-1] = 15000.0
    bedrooms[-1] = 12.0
    price[-1] = 50000 + 120 * 15000 + 15000 * 12 + rng.normal(0, 25000)

    # Standardize predictors for meaningful condition numbers
    sqft_z = _standardize(sqft)
    bedrooms_z = _standardize(bedrooms)
    X = np.column_stack([sqft_z, bedrooms_z])
    y = price

    return {
        "X": X,
        "y": y,
        "feature_names": ["sqft", "bedrooms"],
        "true_issues": [
            "Extreme leverage point: the last observation (the mansion) is ~8 standard "
            "deviations from the mean in sqft. It dominates the projection.",
            "High Cook's distance confirms it is influential, "
            "not just high-leverage.",
        ],
        "hints": [
            "Look at the leverage stem plot — one observation towers above the rest.",
            "Check Cook's distance — does high leverage translate to high influence here?",
            "The mansion's residual determines whether it's influential or just far away.",
        ],
        "description": (
            "City housing data: 80 recent home sales with square footage, "
            "number of bedrooms, and sale price (predictors standardized). "
            "One property in the dataset is considerably larger than the rest."
        ),
    }


def _generate_medium(rng):
    """Employee productivity with collinearity + influential observation."""
    n = 120
    experience = rng.normal(10, 4, n)
    experience = np.clip(experience, 0, 30)

    # Tenure is highly correlated with experience (r ≈ 0.96)
    tenure = 0.95 * experience + rng.normal(0, 0.5, n)
    tenure = np.clip(tenure, 0, 25)

    training_hours = rng.normal(40, 10, n)
    training_hours = np.clip(training_hours, 5, 80)

    noise = rng.normal(0, 8, n)
    productivity = 30 + 1.5 * experience + 1.2 * tenure + 0.3 * training_hours + noise

    # Inject one influential observation: moderate leverage, large residual
    idx_inf = 0
    experience[idx_inf] = 25.0
    tenure[idx_inf] = 3.0  # unusually low tenure for high experience
    training_hours[idx_inf] = 70.0
    productivity[idx_inf] = 120.0  # much higher than model expects

    # Standardize predictors for meaningful condition numbers
    exp_z = _standardize(experience)
    ten_z = _standardize(tenure)
    trn_z = _standardize(training_hours)
    X = np.column_stack([exp_z, ten_z, trn_z])
    y = productivity

    return {
        "X": X,
        "y": y,
        "feature_names": ["experience", "tenure", "training_hours"],
        "true_issues": [
            "Multicollinearity: experience and tenure are correlated at r \u2248 0.90. "
            "The condition number is elevated (~20). The eigenvalue bar chart "
            "shows one direction much thinner than the others.",
            "Influential observation: observation 0 has extreme experience but very low "
            "tenure (unusual combination) and very high productivity. "
            "Moderate leverage combined with a large residual produces high Cook's distance.",
        ],
        "hints": [
            "Check the eigenvalue bar chart \u2014 is one eigenvalue much smaller than the others?",
            "The condition number \u03ba tells you how thin the column space is.",
            "Look for observations with both notable leverage AND large residuals.",
            "The Relevant Triangle for 'experience' will show a short residualized "
            "vector \u2014 most of its information is shared with tenure.",
        ],
        "description": (
            "Employee productivity study: 120 employees at a manufacturing firm. "
            "Predictors are years of experience, years of tenure at the company, "
            "and annual training hours (all standardized). "
            "Response is a productivity index (0\u2013150)."
        ),
    }


def _generate_hard(rng):
    """Student test scores with OVB — geometry looks healthy but coefficients are biased."""
    n = 200

    # Confounding variable: socioeconomic status (SES)
    ses = rng.normal(50, 15, n)
    ses = np.clip(ses, 10, 90)

    # SES drives tutoring access
    tutoring = 0.4 * ses + rng.normal(0, 8, n)
    tutoring = np.clip(tutoring, 0, 60)

    # Study hours — weakly related to SES
    study_hours = rng.normal(15, 5, n) + 0.05 * ses
    study_hours = np.clip(study_hours, 2, 40)

    # Class size — unrelated to SES
    class_size = rng.normal(25, 5, n)
    class_size = np.clip(class_size, 10, 45)

    # True DGP: SES is the primary driver, tutoring has a small true effect
    noise = rng.normal(0, 5, n)
    test_score = 20 + 0.6 * ses + 0.1 * tutoring + 0.3 * study_hours - 0.2 * class_size + noise

    # What the student sees: tutoring, study_hours, class_size (SES omitted)
    # Standardize so condition number reflects actual collinearity, not scaling
    tut_z = _standardize(tutoring)
    study_z = _standardize(study_hours)
    class_z = _standardize(class_size)
    X = np.column_stack([tut_z, study_z, class_z])
    y = test_score

    return {
        "X": X,
        "y": y,
        "feature_names": ["tutoring_hours", "study_hours", "class_size"],
        "true_issues": [
            "Omitted variable bias: socioeconomic status (SES) is omitted from the model. "
            "SES drives both tutoring access (r ≈ 0.65) and test scores. The coefficient "
            "on tutoring_hours is biased upward — it absorbs the effect of SES.",
            "All geometric diagnostics look healthy. The condition number is low, "
            "no extreme leverage points, the Scoreboard is green. The geometry "
            "cannot detect that the projection is onto the wrong column space.",
        ],
        "hints": [
            "The cover story mentions test scores and tutoring. What else might drive "
            "both tutoring access AND test scores?",
            "Think about Notebook 6: when a confounder is omitted, the coefficient "
            "on a correlated predictor absorbs its effect.",
            "The geometry can diagnose HOW WELL you're projecting. It cannot diagnose "
            "WHETHER you're projecting onto the right wall.",
            "This is the one problem the Scoreboard has no gauge for: 'right wall.'",
        ],
        "description": (
            "Education study: 200 students across several schools. Predictors are "
            "weekly tutoring hours, self-reported study hours, and class size "
            "(all standardized). Response is standardized test score. The researchers "
            "noted that tutoring programs are more common in affluent districts, "
            "but did not collect household income data."
        ),
    }


def generate_diagnostic_challenge(
    seed: int = None,
    difficulty: str = "medium",
) -> dict:
    """Generate a random regression scenario for diagnostic exercises.

    Creates a dataset with known properties that the student must
    diagnose using geometric tools.

    Parameters
    ----------
    seed : int, optional
        Random seed for reproducibility.
    difficulty : str
        'easy': one clear problem (extreme leverage point)
        'medium': two issues (collinearity + influential observation)
        'hard': subtle OVB — geometry looks healthy but coefficients are biased

    Returns
    -------
    dict with keys:
        'X': np.ndarray — design matrix (WITHOUT intercept)
        'y': np.ndarray — response vector
        'feature_names': list of str
        'true_issues': list of str — the problems baked into the data
        'hints': list of str — hints for the student
        'description': str — a cover story for the data
    """
    rng = np.random.default_rng(seed)

    generators = {
        "easy": _generate_easy,
        "medium": _generate_medium,
        "hard": _generate_hard,
    }

    if difficulty not in generators:
        raise ValueError(
            f"difficulty must be one of {list(generators.keys())}, got '{difficulty}'"
        )

    return generators[difficulty](rng)
