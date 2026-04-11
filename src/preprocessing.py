"""
Preprocessing pipeline for BRCA survival prediction.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

FEATURES = [
    "age_at_diagnosis", "stage_enc", "subtype_enc", "grade",
    "er_status", "pr_status", "her2_status", "tumor_size_mm", "nodes_positive"
]

def preprocess(df: pd.DataFrame, survival_threshold: int = 36):
    """
    Encode categorical variables, create binary target, return features + target.
    Target: 1 = survived > threshold months (or censored), 0 = died within threshold.
    """
    df = df.copy()
    le_stage = LabelEncoder().fit(["I", "II", "III", "IV"])
    le_subtype = LabelEncoder()
    df["stage_enc"] = le_stage.transform(df["stage"])
    df["subtype_enc"] = le_subtype.fit_transform(df["subtype"])
    df["target"] = ((df["os_months"] > survival_threshold) | (df["os_status"] == 0)).astype(int)
    X = df[FEATURES]
    y = df["target"]
    return X, y, le_stage, le_subtype
