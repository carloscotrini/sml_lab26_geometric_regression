"""Tests for the Meridian Analytics dataset.

Verifies reproducibility, schema, salary ranges, and all six
pedagogical properties required by the course notebooks.
"""

import numpy as np
import pandas as pd
import pytest
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from regression_geometry.data import generate_meridian, load_meridian


@pytest.fixture(scope="module")
def df():
    """Load the canonical Meridian dataset once for the test module."""
    return load_meridian()


@pytest.fixture(scope="module")
def df_generated():
    """Generate the dataset from scratch (seed=42)."""
    return generate_meridian(seed=42)


# --- Reproducibility ---


def test_reproducibility():
    """generate_meridian(seed=42) called twice yields identical DataFrames."""
    df1 = generate_meridian(seed=42)
    df2 = generate_meridian(seed=42)
    pd.testing.assert_frame_equal(df1, df2)


def test_load_matches_generate(df, df_generated):
    """load_meridian() matches generate_meridian(seed=42)."""
    pd.testing.assert_frame_equal(df, df_generated)


# --- Shape and types ---


def test_shape(df):
    assert df.shape == (2000, 7)


def test_column_types(df):
    assert df["salary"].dtype == np.int64
    assert df["experience"].dtype == np.float64
    assert df["education"].dtype == np.float64
    assert pd.api.types.is_string_dtype(df["department"])
    assert df["performance"].dtype == np.int64
    assert df["gender"].dtype == np.int64
    assert df["job_level"].dtype == np.int64


# --- Salary range ---


def test_salary_range(df):
    non_ceo = df["salary"].iloc[1:]
    assert non_ceo.min() > 30_000
    assert df["salary"].max() == 2_100_000  # CEO
    median = df["salary"].median()
    assert 60_000 < median < 90_000


# --- Property 1: Simpson's Paradox Shrinkage ---


def test_simpsons_paradox(df):
    """Gender coefficient shrinks and loses significance when department is added."""
    y = df["salary"].astype(float)

    # Short regression (without department)
    X_short = sm.add_constant(df[["experience", "education", "gender"]].astype(float))
    model_short = sm.OLS(y, X_short).fit()
    beta_gender_short = model_short.params["gender"]
    p_gender_short = model_short.pvalues["gender"]

    # Long regression (with department dummies)
    X_long = pd.get_dummies(
        df[["experience", "education", "gender", "department"]],
        columns=["department"],
        drop_first=True,
    ).astype(float)
    X_long = sm.add_constant(X_long)
    model_long = sm.OLS(y, X_long).fit()
    beta_gender_long = model_long.params["gender"]
    p_gender_long = model_long.pvalues["gender"]

    # Short regression: significant, large negative
    assert -9_000 < beta_gender_short < -6_000
    assert p_gender_short < 0.05

    # Long regression: not significant, small negative
    assert -2_000 < beta_gender_long < -500
    assert p_gender_long > 0.10

    # Coefficient shrinks (does not flip sign)
    assert beta_gender_short < beta_gender_long < 0


# --- Property 2: Experience-Education Correlation ---


def test_experience_education_correlation(df):
    r = np.corrcoef(df["experience"], df["education"])[0, 1]
    assert 0.30 < r < 0.50


# --- Property 3: CEO is High Leverage, Low Influence ---


def test_ceo_high_leverage_low_influence(df):
    """CEO (index 0) has highest leverage but removing it barely changes coefficients."""
    y = np.log(df["salary"].astype(float))
    X = sm.add_constant(df[["experience"]].astype(float))

    model_with = sm.OLS(y, X).fit()
    leverage = model_with.get_influence().hat_matrix_diag

    # CEO should have top-3 leverage
    rank = int(np.where(np.argsort(-leverage) == 0)[0][0]) + 1
    assert rank <= 3, f"CEO leverage rank is {rank}, expected top 3"

    # Removing CEO should change no coefficient by more than 5%
    model_without = sm.OLS(
        np.delete(y.values, 0), np.delete(X.values, 0, axis=0)
    ).fit()
    for i, name in enumerate(model_with.params.index):
        pct_change = (
            abs(model_with.params.iloc[i] - model_without.params[i])
            / abs(model_with.params.iloc[i])
        )
        assert pct_change < 0.05, (
            f"Removing CEO changed {name} by {pct_change:.1%} (> 5%)"
        )


# --- Property 4: Hidden Observation is High Influence ---


def test_hidden_influential_observation(df):
    """Removing observation 1 changes education coefficient by at least 15%."""
    y = np.log(df["salary"].astype(float))
    X = sm.add_constant(df[["experience", "education"]].astype(float))

    model_with = sm.OLS(y, X).fit()
    model_without = sm.OLS(
        np.delete(y.values, 1), np.delete(X.values, 1, axis=0)
    ).fit()

    edu_idx = list(X.columns).index("education")
    pct_change = (
        abs(model_with.params["education"] - model_without.params[edu_idx])
        / abs(model_with.params["education"])
    )
    assert pct_change > 0.15, (
        f"Education coefficient changed by {pct_change:.1%} (< 15%)"
    )


# --- Property 5: Performance is a Weak Predictor ---


def test_performance_weak_predictor(df):
    """Performance has p-value between 0.05 and 0.50 in the full log-salary model."""
    y = np.log(df["salary"].astype(float))
    X = pd.get_dummies(
        df[["experience", "education", "gender", "performance", "job_level", "department"]],
        columns=["department"],
        drop_first=True,
    ).astype(float)
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()

    p_perf = model.pvalues["performance"]
    assert 0.05 < p_perf < 0.50, (
        f"Performance p-value is {p_perf:.4f}, expected between 0.05 and 0.50"
    )


# --- Property 6: No Severe Multicollinearity ---


def test_no_multicollinearity(df):
    """All VIFs below 10 in the long regression model."""
    X = pd.get_dummies(
        df[["experience", "education", "gender", "department"]],
        columns=["department"],
        drop_first=True,
    ).astype(float)
    X = sm.add_constant(X)

    vifs = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    # Skip VIF for the constant term (index 0)
    for name, vif in zip(X.columns[1:], vifs[1:]):
        assert vif < 10, f"VIF for {name} is {vif:.2f} (>= 10)"


# --- Department distribution ---


def test_department_distribution(df):
    """Department percentages are within ±5 pp of targets."""
    pcts = df["department"].value_counts(normalize=True) * 100
    targets = {
        "Engineering": 35,
        "Sales": 25,
        "Marketing": 15,
        "HR": 15,
        "Operations": 10,
    }
    for dept, target in targets.items():
        assert abs(pcts[dept] - target) < 5, (
            f"{dept}: {pcts[dept]:.1f}% vs target {target}%"
        )


# --- Gender-department correlation ---


def test_gender_department_correlation(df):
    """Gender proportions differ across departments (chi-squared test, p < 0.01)."""
    from scipy.stats import chi2_contingency

    contingency = pd.crosstab(df["department"], df["gender"])
    chi2, p, dof, expected = chi2_contingency(contingency)
    assert p < 0.01, f"Chi-squared p-value is {p:.4f}, expected < 0.01"
