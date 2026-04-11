"""
Survival prediction models for TCGA-BRCA.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from lifelines import CoxPHFitter
from lifelines.utils import concordance_index

def train_random_forest(X_train, y_train, n_estimators=200, random_state=42):
    model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
    model.fit(X_train, y_train)
    return model

def evaluate(model, X_test, y_test):
    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    return {"auc": round(auc, 4), "probabilities": proba}

def train_cox(df_cox, duration_col="os_months", event_col="os_status"):
    cph = CoxPHFitter()
    cph.fit(df_cox, duration_col=duration_col, event_col=event_col)
    c_idx = concordance_index(
        df_cox[duration_col],
        -cph.predict_partial_hazard(df_cox),
        df_cox[event_col]
    )
    return cph, round(c_idx, 4)
