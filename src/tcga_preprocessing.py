#!/usr/bin/env python
"""Build a reproducible patient-level TCGA-BRCA clinical cohort.

The raw and processed patient-level files stay local. Only aggregate reports are
intended to be committed to Git.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable

import pandas as pd


DEFAULT_INPUT = Path(
    "data/raw/tcga-brca/brca_tcga_pub2015_clinical_data.tsv"
)
DEFAULT_OUTPUT = Path("data/processed/tcga_brca_clinical_cohort.csv")
DEFAULT_REPORT = Path("reports/tcga_cohort_summary.md")
DEFAULT_HORIZON_MONTHS = 36.0

MISSING_VALUES: Final = [
    "",
    "NA",
    "N/A",
    "NaN",
    "nan",
    "NULL",
    "null",
    "Not Available",
    "[Not Available]",
    "Not Applicable",
    "[Not Applicable]",
    "Unknown",
    "[Unknown]",
]

SOURCE_TO_OUTPUT: Final = {
    "Patient ID": "patient_id",
    "Sample ID": "sample_id",
    "Sample Type": "sample_type",
    "Overall Survival (Months)": "duration_months",
    "Overall Survival Status": "event",
    "Diagnosis Age": "age_at_diagnosis",
    "American Joint Committee on Cancer Metastasis Stage Code": "ajcc_m",
    (
        "Neoplasm Disease Lymph Node Stage American Joint Committee "
        "on Cancer Code"
    ): "ajcc_n",
    (
        "Neoplasm Disease Stage American Joint Committee on Cancer Code"
    ): "ajcc_stage",
    "American Joint Committee on Cancer Tumor Stage Code": "ajcc_t",
    "ER Status By IHC": "er_status",
    "PR status by ihc": "pr_status",
    "IHC-HER2": "her2_status",
    "Neoplasm Histologic Type Name": "histology",
    "Menopause Status": "menopause_status",
    "Lymph Node(s) Examined Number": "nodes_examined",
    (
        "Positive Finding Lymph Node Hematoxylin and Eosin "
        "Staining Microscopy Count"
    ): "nodes_positive",
}

NUMERIC_FEATURES: Final = (
    "age_at_diagnosis",
    "nodes_examined",
    "nodes_positive",
)

CATEGORICAL_FEATURES: Final = (
    "ajcc_stage",
    "ajcc_t",
    "ajcc_n",
    "ajcc_m",
    "er_status",
    "pr_status",
    "her2_status",
    "histology",
    "menopause_status",
)

MODEL_FEATURES: Final = NUMERIC_FEATURES + CATEGORICAL_FEATURES

OUTPUT_COLUMNS: Final = (
    "patient_id",
    "sample_id",
    "sample_type",
    "duration_months",
    "event",
    "survived_36_months",
) + MODEL_FEATURES


@dataclass(frozen=True)
class CohortSummary:
    """Aggregate counters describing cohort construction."""

    raw_rows: int
    raw_unique_patients: int
    repeated_patient_rows: int
    rows_after_patient_deduplication: int
    rows_excluded_missing_outcome: int
    final_patients: int
    events: int
    censored: int
    event_rate: float
    horizon_months: float
    deaths_by_horizon: int
    known_survivors_at_horizon: int
    censored_by_horizon: int
    zero_duration_rows: int
    ages_out_of_range_set_missing: int
    negative_node_counts_set_missing: int
    positive_nodes_above_examined: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the patient-level TCGA-BRCA modelling cohort."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def _clean_string_series(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()
    missing_tokens = {value.strip().lower() for value in MISSING_VALUES}
    missing_mask = values.str.lower().isin(missing_tokens)
    return values.mask(missing_mask, pd.NA)


def _clean_raw_strings(frame: pd.DataFrame) -> pd.DataFrame:
    clean = frame.copy()
    clean.columns = [str(column).strip() for column in clean.columns]

    if clean.columns.duplicated().any():
        duplicates = clean.columns[clean.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names detected: {duplicates}")

    for column in clean.columns:
        clean[column] = _clean_string_series(clean[column])
    return clean


def validate_source_schema(frame: pd.DataFrame) -> None:
    missing = [
        column for column in SOURCE_TO_OUTPUT if column not in frame.columns
    ]
    if missing:
        formatted = ", ".join(missing)
        raise ValueError(f"Missing required TCGA columns: {formatted}")


def load_tcga_clinical(path: str | Path = DEFAULT_INPUT) -> pd.DataFrame:
    """Load the cBioPortal TSV as strings and validate its source schema."""
    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {input_path}. "
            "Keep the raw TSV locally or pass --input PATH."
        )

    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            frame = pd.read_csv(
                input_path,
                sep="\t",
                dtype="string",
                comment="#",
                keep_default_na=True,
                na_values=MISSING_VALUES,
                low_memory=False,
                encoding=encoding,
            )
            break
        except UnicodeDecodeError as error:
            last_error = error
    else:
        raise ValueError(f"Unable to decode {input_path}") from last_error

    if frame.shape[1] == 1:
        raise ValueError(
            "Only one column was detected. Confirm that the input is TSV."
        )

    frame = _clean_raw_strings(frame)
    validate_source_schema(frame)
    return frame


def _parse_numeric(series: pd.Series, column_name: str) -> pd.Series:
    clean = _clean_string_series(series)
    numeric = pd.to_numeric(clean, errors="coerce")
    invalid = clean.notna() & numeric.isna()
    if invalid.any():
        count = int(invalid.sum())
        raise ValueError(
            f"{column_name} contains {count} non-numeric non-missing value(s)."
        )
    return numeric.astype("Float64")


def _parse_event_status(series: pd.Series) -> pd.Series:
    clean = _clean_string_series(series).str.upper()
    living = clean.str.fullmatch(r"(0(?::.*)?|LIVING|ALIVE)", na=False)
    deceased = clean.str.fullmatch(
        r"(1(?::.*)?|DECEASED|DEAD)", na=False
    )

    unknown = clean.notna() & ~(living | deceased)
    if unknown.any():
        values = sorted(clean.loc[unknown].dropna().unique().tolist())
        raise ValueError(
            "Unrecognised Overall Survival Status value(s): "
            + ", ".join(values)
        )

    event = pd.Series(pd.NA, index=series.index, dtype="Int8")
    event.loc[living] = 0
    event.loc[deceased] = 1
    return event


def _normalise_category(series: pd.Series) -> pd.Series:
    values = _clean_string_series(series).str.lower()
    values = values.str.replace(r"[^a-z0-9]+", "_", regex=True)
    values = values.str.strip("_")
    return values.mask(values.eq(""), pd.NA)


def _normalise_stage(series: pd.Series) -> pd.Series:
    values = _clean_string_series(series).str.upper()
    values = values.str.replace(r"^STAGE[\s_-]*", "", regex=True)
    values = values.str.replace(r"[^A-Z0-9]+", "", regex=True)
    return values.mask(values.eq(""), pd.NA)


def _sample_priority(series: pd.Series) -> pd.Series:
    values = _normalise_category(series).fillna("")
    priority = pd.Series(3, index=series.index, dtype="int64")
    priority.loc[values.str.contains("primary", regex=False)] = 0
    priority.loc[values.str.contains("recurrent", regex=False)] = 1
    priority.loc[values.str.contains("metast", regex=False)] = 2
    return priority


def _mask_out_of_range(
    series: pd.Series,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> tuple[pd.Series, int]:
    invalid = pd.Series(False, index=series.index)
    if minimum is not None:
        invalid |= series.notna() & series.lt(minimum)
    if maximum is not None:
        invalid |= series.notna() & series.gt(maximum)
    return series.mask(invalid, pd.NA), int(invalid.sum())


def build_horizon_target(
    duration_months: pd.Series,
    event: pd.Series,
    horizon_months: float = DEFAULT_HORIZON_MONTHS,
) -> pd.Series:
    """Create a leakage-safe binary endpoint at a fixed time horizon.

    0 means death occurred on or before the horizon.
    1 means survival beyond the horizon is observed.
    Missing means censoring occurred on or before the horizon.
    """
    if horizon_months <= 0:
        raise ValueError("horizon_months must be strictly positive.")

    target = pd.Series(pd.NA, index=duration_months.index, dtype="Int8")
    target.loc[event.eq(1) & duration_months.le(horizon_months)] = 0
    target.loc[duration_months.gt(horizon_months)] = 1
    return target


def prepare_tcga_cohort(
    raw_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, CohortSummary]:
    """Select, clean and deduplicate the 36-month TCGA clinical cohort."""

    raw = _clean_raw_strings(raw_frame)
    validate_source_schema(raw)

    work = raw.loc[:, list(SOURCE_TO_OUTPUT)].rename(
        columns=SOURCE_TO_OUTPUT
    )

    if work["patient_id"].isna().any():
        count = int(work["patient_id"].isna().sum())
        raise ValueError(f"Patient ID is missing for {count} row(s).")

    duplicate_sample_ids = int(
        work["sample_id"].dropna().duplicated().sum()
    )
    if duplicate_sample_ids:
        raise ValueError(
            f"Sample ID contains {duplicate_sample_ids} duplicate value(s)."
        )

    work["duration_months"] = _parse_numeric(
        work["duration_months"],
        "Overall Survival (Months)",
    )
    if work["duration_months"].dropna().lt(0).any():
        count = int(work["duration_months"].dropna().lt(0).sum())
        raise ValueError(
            f"Overall Survival (Months) contains {count} negative value(s)."
        )

    work["event"] = _parse_event_status(work["event"])
    work["_outcome_missing"] = (
        work["duration_months"].isna() | work["event"].isna()
    ).astype("int8")
    work["_sample_priority"] = _sample_priority(work["sample_type"])
    work["_source_order"] = range(len(work))

    raw_rows = len(work)
    raw_unique_patients = int(work["patient_id"].nunique())
    repeated_patient_rows = raw_rows - raw_unique_patients

    work = work.sort_values(
        [
            "patient_id",
            "_outcome_missing",
            "_sample_priority",
            "sample_id",
            "_source_order",
        ],
        kind="mergesort",
        na_position="last",
    )
    patient_frame = work.drop_duplicates("patient_id", keep="first").copy()
    rows_after_deduplication = len(patient_frame)

    missing_outcome = (
        patient_frame["duration_months"].isna()
        | patient_frame["event"].isna()
    )
    rows_excluded_missing_outcome = int(missing_outcome.sum())
    cohort = patient_frame.loc[~missing_outcome].copy()

    cohort["age_at_diagnosis"] = _parse_numeric(
        cohort["age_at_diagnosis"],
        "Diagnosis Age",
    )
    cohort["nodes_examined"] = _parse_numeric(
        cohort["nodes_examined"],
        "Lymph Node(s) Examined Number",
    )
    cohort["nodes_positive"] = _parse_numeric(
        cohort["nodes_positive"],
        "Positive lymph-node count",
    )

    cohort["age_at_diagnosis"], invalid_ages = _mask_out_of_range(
        cohort["age_at_diagnosis"],
        minimum=18,
        maximum=120,
    )
    cohort["nodes_examined"], invalid_examined = _mask_out_of_range(
        cohort["nodes_examined"],
        minimum=0,
    )
    cohort["nodes_positive"], invalid_positive = _mask_out_of_range(
        cohort["nodes_positive"],
        minimum=0,
    )

    for column in ("ajcc_stage", "ajcc_t", "ajcc_n", "ajcc_m"):
        cohort[column] = _normalise_stage(cohort[column])

    for column in (
        "sample_type",
        "er_status",
        "pr_status",
        "her2_status",
        "histology",
        "menopause_status",
    ):
        cohort[column] = _normalise_category(cohort[column])

    cohort["survived_36_months"] = build_horizon_target(
        cohort["duration_months"],
        cohort["event"],
        DEFAULT_HORIZON_MONTHS,
    )

    positive_above_examined = int(
        (
            cohort["nodes_positive"].notna()
            & cohort["nodes_examined"].notna()
            & cohort["nodes_positive"].gt(cohort["nodes_examined"])
        ).sum()
    )

    cohort = (
        cohort.loc[:, list(OUTPUT_COLUMNS)]
        .sort_values("patient_id", kind="mergesort")
        .reset_index(drop=True)
    )

    if cohort["patient_id"].duplicated().any():
        raise AssertionError("Patient-level deduplication failed.")

    events = int(cohort["event"].sum())
    final_patients = len(cohort)
    target = cohort["survived_36_months"]

    summary = CohortSummary(
        raw_rows=raw_rows,
        raw_unique_patients=raw_unique_patients,
        repeated_patient_rows=repeated_patient_rows,
        rows_after_patient_deduplication=rows_after_deduplication,
        rows_excluded_missing_outcome=rows_excluded_missing_outcome,
        final_patients=final_patients,
        events=events,
        censored=final_patients - events,
        event_rate=(events / final_patients) if final_patients else 0.0,
        horizon_months=DEFAULT_HORIZON_MONTHS,
        deaths_by_horizon=int(target.eq(0).sum()),
        known_survivors_at_horizon=int(target.eq(1).sum()),
        censored_by_horizon=int(target.isna().sum()),
        zero_duration_rows=int(cohort["duration_months"].eq(0).sum()),
        ages_out_of_range_set_missing=invalid_ages,
        negative_node_counts_set_missing=(
            invalid_examined + invalid_positive
        ),
        positive_nodes_above_examined=positive_above_examined,
    )
    return cohort, summary


def _markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _markdown_table(
    headers: Iterable[str],
    rows: Iterable[Iterable[object]],
) -> str:
    clean_headers = [_markdown_escape(value) for value in headers]
    clean_rows = [
        [_markdown_escape(value) for value in row] for row in rows
    ]
    lines = [
        "| " + " | ".join(clean_headers) + " |",
        "| " + " | ".join(["---"] * len(clean_headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in clean_rows)
    return "\n".join(lines)


def build_cohort_report(
    cohort: pd.DataFrame,
    summary: CohortSummary,
    input_path: str | Path = DEFAULT_INPUT,
) -> str:
    """Create an aggregate report without reproducing patient-level rows."""
    source = Path(input_path)
    source_label = source.name if source.is_absolute() else source.as_posix()

    flow_rows = [
        ["Raw sample rows", f"{summary.raw_rows:,}"],
        ["Unique patient IDs in source", f"{summary.raw_unique_patients:,}"],
        ["Repeated patient rows", f"{summary.repeated_patient_rows:,}"],
        [
            "Rows after patient deduplication",
            f"{summary.rows_after_patient_deduplication:,}",
        ],
        [
            "Patients excluded: missing OS duration/status",
            f"{summary.rows_excluded_missing_outcome:,}",
        ],
        ["Final patient-level cohort", f"{summary.final_patients:,}"],
        ["Observed deaths", f"{summary.events:,}"],
        ["Censored observations", f"{summary.censored:,}"],
        ["Observed event rate", f"{summary.event_rate:.1%}"],
    ]

    horizon = f"{summary.horizon_months:g}"
    horizon_rows = [
        [
            f"Death on or before {horizon} months",
            f"{summary.deaths_by_horizon:,}",
            "0",
        ],
        [
            f"Observed survival beyond {horizon} months",
            f"{summary.known_survivors_at_horizon:,}",
            "1",
        ],
        [
            f"Censored on or before {horizon} months",
            f"{summary.censored_by_horizon:,}",
            "Missing: excluded from binary modelling",
        ],
    ]

    feature_rows = []
    for feature in MODEL_FEATURES:
        series = cohort[feature]
        non_missing = int(series.notna().sum())
        feature_rows.append(
            [
                feature,
                "numeric" if feature in NUMERIC_FEATURES else "categorical",
                f"{non_missing:,}",
                f"{series.isna().mean():.1%}",
                f"{series.nunique(dropna=True):,}",
            ]
        )

    quality_rows = [
        ["Zero-month OS durations retained for review", summary.zero_duration_rows],
        [
            "Ages outside [18, 120] set to missing",
            summary.ages_out_of_range_set_missing,
        ],
        [
            "Negative lymph-node counts set to missing",
            summary.negative_node_counts_set_missing,
        ],
        [
            "Rows with positive nodes above examined nodes",
            summary.positive_nodes_above_examined,
        ],
    ]

    return "\n".join(
        [
            "# TCGA-BRCA modelling cohort summary",
            "",
            "> Aggregate report only. No patient-level rows are reproduced.",
            "",
            "## Source and cohort rules",
            "",
            f"- Source: {source_label}",
            "- Analysis unit: one patient.",
            (
                "- Duplicate rule: prefer a row with complete overall-survival "
                "data, then a primary tumour sample, then Sample ID order."
            ),
            (
                "- Primary endpoint: Overall Survival (Months) with "
                "Overall Survival Status."
            ),
            "",
            "## Cohort flow",
            "",
            _markdown_table(["Measure", "Value"], flow_rows),
            "",
            f"## Secondary binary endpoint at {horizon} months",
            "",
            _markdown_table(
                ["Observed state", "Patients", "Binary label"],
                horizon_rows,
            ),
            "",
            (
                "Patients censored before the horizon remain unresolved. "
                "They are not labelled as survivors."
            ),
            "",
            "## Candidate baseline predictors",
            "",
            _markdown_table(
                ["Feature", "Type", "Non-missing", "Missing", "Unique"],
                feature_rows,
            ),
            "",
            "No imputation, category grouping, scaling or encoding is fitted "
            "during cohort construction. Those transformations must be fitted "
            "inside each training fold.",
            "",
            "## Aggregate data-quality flags",
            "",
            _markdown_table(["Check", "Count"], quality_rows),
            "",
            "## Variables deliberately excluded from the first model",
            "",
            "- Patient and sample identifiers: tracking only, never predictors.",
            "- DFS/PFS and follow-up fields: outcomes or outcome-derived fields.",
            "- Treatment and surgical fields: unavailable at initial diagnosis.",
            (
                "- Mutation count, TMB and fraction genome altered: reserved "
                "for a separate genomic model."
            ),
            (
                "- Race and ethnicity: reserved for fairness assessment, not "
                "used as predictors in the first clinical model."
            ),
            (
                "- PAM50 subtype, tumour size and histologic grade: not present "
                "as validated fields in this clinical export."
            ),
            "",
        ]
    )


def write_outputs(
    cohort: pd.DataFrame,
    summary: CohortSummary,
    *,
    input_path: str | Path,
    output_path: str | Path = DEFAULT_OUTPUT,
    report_path: str | Path = DEFAULT_REPORT,
) -> None:
    output = Path(output_path)
    report = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    cohort.to_csv(output, index=False)
    report.write_text(
        build_cohort_report(cohort, summary, input_path),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    raw = load_tcga_clinical(args.input)
    cohort, summary = prepare_tcga_cohort(raw)
    write_outputs(
        cohort,
        summary,
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
    )

    print("TCGA-BRCA cohort preparation completed")
    print(f"Final patients: {summary.final_patients:,}")
    print(f"Observed deaths: {summary.events:,}")
    print(
        "Unresolved at "
        f"{summary.horizon_months:g} months: "
        f"{summary.censored_by_horizon:,}"
    )
    print(f"Local cohort: {args.output.as_posix()}")
    print(f"Aggregate report: {args.report.as_posix()}")


if __name__ == "__main__":
    main()
