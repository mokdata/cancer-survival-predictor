"""
Data loader for TCGA-BRCA cancer survival dataset.
"""
import pandas as pd
import numpy as np
import os

def load_data(path: str = "data/brca_clinical.csv") -> pd.DataFrame:
    """Load BRCA clinical dataset."""
    df = pd.read_csv(path)
    return df

def generate_synthetic_brca(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic TCGA-BRCA dataset based on published distributions.
    Reference: Comprehensive molecular portraits of human breast tumours (Nature, 2012)
    """
    np.random.seed(seed)
    age = np.random.normal(58, 13, n).clip(25, 90).astype(int)
    stage = np.random.choice(["I", "II", "III", "IV"], n, p=[0.20, 0.48, 0.25, 0.07])
    subtype = np.random.choice(
        ["Luminal_A", "Luminal_B", "HER2", "Basal", "Normal"],
        n, p=[0.40, 0.20, 0.15, 0.20, 0.05]
    )
    grade = np.random.choice([1, 2, 3], n, p=[0.15, 0.40, 0.45])
    er_status = np.where(np.isin(subtype, ["Luminal_A", "Luminal_B"]),
                         np.random.choice([0,1], n, p=[0.05, 0.95]),
                         np.random.choice([0,1], n, p=[0.85, 0.15]))
    pr_status = (er_status * np.random.binomial(1, 0.75, n))
    her2_status = np.where(subtype == "HER2",
                           np.random.choice([0,1], n, p=[0.05, 0.95]),
                           np.random.choice([0,1], n, p=[0.85, 0.15]))
    tumor_size = np.random.lognormal(3.2, 0.5, n).clip(5, 120).astype(int)
    nodes_pos = np.random.choice([0, 1, 2, 3, 4], n, p=[0.45, 0.20, 0.15, 0.12, 0.08])

    def survival_time(stage, subtype, grade):
        base = {"I": 120, "II": 90, "III": 60, "IV": 24}[stage]
        factor = {"Luminal_A": 1.3, "Luminal_B": 1.0, "HER2": 0.9, "Basal": 0.75, "Normal": 1.2}[subtype]
        grade_factor = {1: 1.2, 2: 1.0, 3: 0.8}[grade]
        return np.random.weibull(1.5) * base * factor * grade_factor

    os_months = np.array([survival_time(s, st, g) for s, st, g in zip(stage, subtype, grade)])
    os_months = os_months.clip(1, 200).astype(int)
    followup = np.random.uniform(12, 150, n)
    os_status = (os_months <= followup).astype(int)
    os_months_observed = np.minimum(os_months, followup).astype(int)

    return pd.DataFrame({
        "patient_id": [f"BRCA_{i:04d}" for i in range(n)],
        "age_at_diagnosis": age,
        "stage": stage,
        "subtype": subtype,
        "grade": grade,
        "er_status": er_status,
        "pr_status": pr_status,
        "her2_status": her2_status,
        "tumor_size_mm": tumor_size,
        "nodes_positive": nodes_pos,
        "os_months": os_months_observed,
        "os_status": os_status
    })
