"""Meridian Analytics dataset generator and loader.

Provides the canonical 2,000-employee dataset used throughout the
regression geometry course.  The dataset is generated from a fixed
seed (42) and stored as CSV for perfect reproducibility.

Dependencies: numpy, pandas, pathlib (stdlib).
"""

from pathlib import Path

import numpy as np
import pandas as pd

_DATA_DIR = Path(__file__).parent / "data"
_CSV_PATH = _DATA_DIR / "meridian.csv"

# Department configuration
_DEPARTMENTS = ["Engineering", "Sales", "Marketing", "HR", "Operations"]
_DEPT_PROBS = [0.35, 0.25, 0.15, 0.15, 0.10]
_DEPT_GENDER_PROBS = {
    "Engineering": 0.30,
    "Sales": 0.50,
    "Marketing": 0.60,
    "HR": 0.65,
    "Operations": 0.40,
}
_DEPT_JOB_OFFSET = {
    "Engineering": 0.8,
    "Sales": 0.3,
    "Marketing": 0.0,
    "HR": -0.2,
    "Operations": 0.1,
}
_DEPT_SALARY_OFFSET = {
    "Engineering": 0.15,
    "Sales": 0.05,
    "Marketing": 0.0,
    "HR": -0.05,
    "Operations": -0.03,
}


def generate_meridian(seed: int = 42) -> pd.DataFrame:
    """Generate the Meridian Analytics dataset from scratch.

    This function implements the full DGP.  It is called once to produce
    the CSV that load_meridian() reads.  It can also be called with different
    seeds for Monte Carlo exercises, but the canonical dataset uses seed=42.

    Parameters
    ----------
    seed : int, default 42
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame with 2000 rows and 7 columns:
        salary, experience, education, department, performance, gender, job_level.
    """
    n = 2000
    rng = np.random.default_rng(seed=seed)

    # Step 1 — Department and Gender
    department = rng.choice(_DEPARTMENTS, size=n, p=_DEPT_PROBS)
    gender = np.array(
        [rng.binomial(1, _DEPT_GENDER_PROBS[d]) for d in department]
    )

    # Step 2 — Experience and Education
    experience = rng.normal(12, 7, size=n)
    experience = np.clip(np.maximum(experience, 0), 0, 28)
    experience = np.round(experience, 1)

    education = rng.normal(4, 1.5, size=n) + 0.3 * (experience - 12) / 7 * 2.5
    education = np.clip(np.maximum(education, 0), 0, 10)
    education = np.round(education, 1)

    # Step 3 — Performance
    perf_raw = rng.normal(3.5, 0.6, size=n)
    performance = np.clip(np.round(perf_raw), 1, 5).astype(int)

    # Step 4 — Job Level
    dept_job_offsets = np.array([_DEPT_JOB_OFFSET[d] for d in department])
    job_score = 0.12 * experience + dept_job_offsets + rng.normal(0, 0.5, size=n)
    job_level = np.clip(np.round(job_score), 1, 5).astype(int)

    # Step 5 — Salary (log scale)
    dept_salary_offsets = np.array([_DEPT_SALARY_OFFSET[d] for d in department])
    log_salary = (
        10.5
        + 0.025 * experience
        + 0.015 * education
        + 0.18 * job_level
        + dept_salary_offsets
        + 0.003 * performance
        - 0.010 * gender
        + rng.normal(0, 0.12, size=n)
    )
    salary = np.exp(log_salary).astype(int)

    # Step 6 — CEO Outlier (index 0)
    salary[0] = 2_100_000
    experience[0] = 32
    education[0] = 8
    department[0] = "Engineering"
    gender[0] = 0
    performance[0] = 3
    job_level[0] = 5

    # Step 7 — Hidden Influential Observation (index 1)
    salary[1] = 700_000
    experience[1] = 2
    education[1] = 10
    department[1] = "Engineering"
    gender[1] = 1
    performance[1] = 4
    job_level[1] = 2

    df = pd.DataFrame(
        {
            "salary": salary,
            "experience": experience,
            "education": education,
            "department": department,
            "performance": performance,
            "gender": gender,
            "job_level": job_level,
        }
    )
    return df


def load_meridian() -> pd.DataFrame:
    """Load the Meridian Analytics employee dataset.

    Returns a DataFrame with 2,000 rows and 7 columns:
        salary: int — annual compensation in dollars
        experience: float — years of work experience
        education: float — years of post-secondary education
        department: str — one of 'Engineering', 'Sales', 'Marketing', 'HR', 'Operations'
        performance: int — rating 1-5
        gender: int — 0 or 1
        job_level: int — ordinal 1-5

    The dataset is loaded from a pre-generated CSV bundled with the package.
    It is perfectly reproducible (generated with numpy seed 42).

    Example
    -------
    >>> from regression_geometry.data import load_meridian
    >>> df = load_meridian()
    >>> df.shape
    (2000, 7)
    """
    if not _CSV_PATH.exists():
        raise FileNotFoundError(
            f"Canonical dataset not found at {_CSV_PATH}. "
            "Run generate_meridian() and save to CSV first."
        )
    df = pd.read_csv(_CSV_PATH)
    # Ensure correct dtypes
    df["salary"] = df["salary"].astype(int)
    df["performance"] = df["performance"].astype(int)
    df["gender"] = df["gender"].astype(int)
    df["job_level"] = df["job_level"].astype(int)
    return df


def meridian_summary() -> str:
    """Print a summary of the Meridian Analytics dataset.

    Includes: shape, column types, salary statistics, department counts,
    gender distribution, and correlation matrix of numeric variables.

    Useful as a quick orientation cell in notebooks.
    """
    df = load_meridian()
    numeric_cols = ["salary", "experience", "education", "performance", "job_level"]
    lines = [
        "=== Meridian Analytics Employee Dataset ===",
        f"Shape: {df.shape[0]} rows × {df.shape[1]} columns",
        "",
        "--- Column Types ---",
        str(df.dtypes),
        "",
        "--- Salary Statistics ---",
        f"  Mean:   ${df['salary'].mean():,.0f}",
        f"  Median: ${df['salary'].median():,.0f}",
        f"  Std:    ${df['salary'].std():,.0f}",
        f"  Min:    ${df['salary'].min():,}",
        f"  Max:    ${df['salary'].max():,}",
        "",
        "--- Department Counts ---",
        str(df["department"].value_counts()),
        "",
        "--- Gender Distribution ---",
        str(df["gender"].value_counts()),
        "",
        "--- Correlation Matrix (numeric) ---",
        str(df[numeric_cols].corr().round(3)),
    ]
    summary = "\n".join(lines)
    print(summary)
    return summary


if __name__ == "__main__":
    # Generate and save the canonical dataset
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = generate_meridian(seed=42)
    df.to_csv(_CSV_PATH, index=False)
    print(f"Saved {len(df)} rows to {_CSV_PATH}")
    meridian_summary()
