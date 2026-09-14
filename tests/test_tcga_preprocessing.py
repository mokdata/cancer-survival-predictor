"""Tests for the TCGA-BRCA cohort construction pipeline."""

import pandas as pd
import pytest

from src.tcga_preprocessing import (
    MODEL_FEATURES,
    build_cohort_report,
    build_horizon_target,
    prepare_tcga_cohort,
)


def make_raw_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Patient ID": ["P1", "P1", "P2", "P3", "P4", "P5"],
            "Sample ID": [
                "S1_PRIMARY",
                "S1_MET",
                "S2",
                "S3",
                "S4",
                "S5",
            ],
            "Sample Type": [
                "Primary Solid Tumor",
                "Metastatic",
                "Primary Solid Tumor",
                "Primary Solid Tumor",
                "Primary Solid Tumor",
                "Primary Solid Tumor",
            ],
            "Overall Survival (Months)": [
                "12",
                "12",
                "20",
                "48",
                "60",
                pd.NA,
            ],
            "Overall Survival Status": [
                "1:DECEASED",
                "1:DECEASED",
                "0:LIVING",
                "0:LIVING",
                "1:DECEASED",
                "0:LIVING",
            ],
            "Diagnosis Age": ["50", "50", "61", "44", "73", "55"],
            (
                "American Joint Committee on Cancer Metastasis Stage Code"
            ): ["M0", "M0", "M0", "M0", "M1", "M0"],
            (
                "Neoplasm Disease Lymph Node Stage American Joint "
                "Committee on Cancer Code"
            ): ["N1", "N1", "N0", "N2", "N1", "N0"],
            (
                "Neoplasm Disease Stage American Joint Committee "
                "on Cancer Code"
            ): [
                "STAGE IIA",
                "STAGE IIA",
                "STAGE I",
                "STAGE IIIA",
                "STAGE IV",
                "STAGE I",
            ],
            (
                "American Joint Committee on Cancer Tumor Stage Code"
            ): ["T2", "T2", "T1", "T3", "T2", "T1"],
            "ER Status By IHC": [
                "Positive",
                "Positive",
                "Negative",
                "Positive",
                "Negative",
                "Positive",
            ],
            "PR status by ihc": [
                "Positive",
                "Positive",
                "Negative",
                "Negative",
                "Negative",
                "Positive",
            ],
            "IHC-HER2": [
                "Negative",
                "Negative",
                "Positive",
                "Negative",
                "Equivocal",
                "Negative",
            ],
            "Neoplasm Histologic Type Name": [
                "Infiltrating Ductal Carcinoma",
                "Infiltrating Ductal Carcinoma",
                "Infiltrating Lobular Carcinoma",
                "Infiltrating Ductal Carcinoma",
                "Infiltrating Ductal Carcinoma",
                "Infiltrating Lobular Carcinoma",
            ],
            "Menopause Status": [
                "Post",
                "Post",
                "Post",
                "Pre",
                "Post",
                "Pre",
            ],
            "Lymph Node(s) Examined Number": [
                "10",
                "10",
                "3",
                "15",
                "8",
                "4",
            ],
            (
                "Positive Finding Lymph Node Hematoxylin and Eosin "
                "Staining Microscopy Count"
            ): ["2", "2", "0", "4", "1", "0"],
        }
    )


def test_preparation_builds_one_row_per_patient_and_correct_horizon() -> None:
    cohort, summary = prepare_tcga_cohort(make_raw_frame())

    assert summary.raw_rows == 6
    assert summary.raw_unique_patients == 5
    assert summary.repeated_patient_rows == 1
    assert summary.rows_after_patient_deduplication == 5
    assert summary.rows_excluded_missing_outcome == 1
    assert summary.final_patients == 4
    assert summary.events == 2
    assert not cohort["patient_id"].duplicated().any()

    selected_sample = cohort.loc[
        cohort["patient_id"].eq("P1"), "sample_id"
    ].item()
    assert selected_sample == "S1_PRIMARY"

    labels = cohort.set_index("patient_id")["survived_36_months"]
    assert labels.loc["P1"] == 0
    assert pd.isna(labels.loc["P2"])
    assert labels.loc["P3"] == 1
    assert labels.loc["P4"] == 1


def test_horizon_boundary_respects_censoring() -> None:
    duration = pd.Series([36.0, 36.0, 36.1], dtype="Float64")
    event = pd.Series([1, 0, 0], dtype="Int8")

    target = build_horizon_target(duration, event)

    assert target.iloc[0] == 0
    assert pd.isna(target.iloc[1])
    assert target.iloc[2] == 1


def test_categories_and_stages_are_normalised() -> None:
    cohort, _ = prepare_tcga_cohort(make_raw_frame())
    first = cohort.set_index("patient_id").loc["P1"]

    assert first["ajcc_stage"] == "IIA"
    assert first["er_status"] == "positive"
    assert first["sample_type"] == "primary_solid_tumor"


def test_report_breaks_down_zero_durations_and_lists_categories() -> None:
    raw = make_raw_frame()
    duration_column = "Overall Survival (Months)"
    raw.loc[0, duration_column] = "0"
    raw.loc[2, duration_column] = "0"

    cohort, summary = prepare_tcga_cohort(raw)
    report = build_cohort_report(cohort, summary)

    assert summary.zero_duration_rows == 2
    assert summary.zero_duration_events == 1
    assert summary.zero_duration_censored == 1
    assert (
        summary.zero_duration_rows
        == summary.zero_duration_events + summary.zero_duration_censored
    )
    assert "## Categorical level distributions" in report
    assert "| er_status | positive | 2 | 50.0% | Yes |" in report
    assert "| ajcc_stage | IIA | 1 | 25.0% | Yes |" in report
    assert "| Zero-month OS durations with observed death | 1 |" in report
    assert (
        "| Zero-month OS durations with censored observation | 1 |"
        in report
    )


def test_unknown_event_status_fails_loudly() -> None:
    raw = make_raw_frame()
    raw.loc[0, "Overall Survival Status"] = "PENDING"

    with pytest.raises(ValueError, match="Unrecognised"):
        prepare_tcga_cohort(raw)


def test_negative_survival_duration_fails_loudly() -> None:
    raw = make_raw_frame()
    raw.loc[0, "Overall Survival (Months)"] = "-1"

    with pytest.raises(ValueError, match="negative"):
        prepare_tcga_cohort(raw)


def test_missing_required_source_column_fails_loudly() -> None:
    raw = make_raw_frame().drop(columns=["Diagnosis Age"])

    with pytest.raises(ValueError, match="Missing required TCGA columns"):
        prepare_tcga_cohort(raw)


def test_report_is_aggregate_and_model_features_exclude_identifiers() -> None:
    cohort, summary = prepare_tcga_cohort(make_raw_frame())
    report = build_cohort_report(cohort, summary)

    assert "P1" not in report
    assert "S1_PRIMARY" not in report
    assert "Final patient-level cohort" in report
    assert "Censored on or before 36 months" in report
    assert "patient_id" not in MODEL_FEATURES
    assert "sample_id" not in MODEL_FEATURES
    assert "duration_months" not in MODEL_FEATURES
    assert "event" not in MODEL_FEATURES
