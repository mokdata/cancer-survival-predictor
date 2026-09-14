#!/usr/bin/env python
"""Audit the local TCGA-BRCA clinical TSV without exposing patient-level rows.

The raw dataset stays outside Git. This script reads it in place and writes an
aggregate Markdown report that can be reviewed before any modelling decision.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_INPUT = Path(
    "data/raw/tcga-brca/brca_tcga_pub2015_clinical_data.tsv"
)
DEFAULT_REPORT = Path("reports/tcga_clinical_audit.md")

MISSING_VALUES = [
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

COLUMN_PATTERNS = {
    "identifier": [
        r"(^|_)(patient|sample|case)(_.*)?id($|_)",
        r"(^|_)(patient|sample|case)($|_)",
        r"submitter_id",
    ],
    "survival": [
        r"(^|_)os($|_)",
        r"overall_survival",
        r"vital_status",
        r"death",
        r"follow.?up",
        r"(^|_)(dfs|pfs|rfs|dss)($|_)",
        r"disease.?free",
        r"progression.?free",
        r"recurrence.?free",
    ],
    "clinical_feature": [
        r"age",
        r"stage",
        r"grade",
        r"histolog",
        r"tumou?r",
        r"node",
        r"(^|_)er($|_)",
        r"estrogen",
        r"(^|_)pr($|_)",
        r"progesterone",
        r"her2",
        r"subtype",
        r"pam50",
        r"menopaus",
        r"race",
        r"ethnic",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an aggregate audit report for TCGA-BRCA clinical data."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"TSV path (default: {DEFAULT_INPUT.as_posix()})",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Markdown output path (default: {DEFAULT_REPORT.as_posix()})",
    )
    return parser.parse_args()


def normalise_name(value: object) -> str:
    """Normalise a column name for resilient keyword matching."""
    text = re.sub(r"[^A-Za-z0-9]+", "_", str(value).strip())
    return text.strip("_").lower()


def markdown_escape(value: object) -> str:
    """Escape values used inside Markdown tables."""
    text = str(value).replace("\n", " ").replace("\r", " ")
    return text.replace("|", "\\|").strip()


def markdown_table(headers: Iterable[str], rows: Iterable[Iterable[object]]) -> str:
    headers = [markdown_escape(value) for value in headers]
    body = [[markdown_escape(value) for value in row] for row in rows]
    separator = ["---"] * len(headers)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def read_tsv(path: Path) -> pd.DataFrame:
    """Read a cBioPortal-style TSV while preserving identifiers as strings."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Input file not found: {path}\n"
            "Keep the raw TSV at the expected path or pass --input PATH."
        )

    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            frame = pd.read_csv(
                path,
                sep="\t",
                dtype=str,
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
        raise ValueError(f"Unable to decode {path}") from last_error

    if frame.shape[1] == 1:
        raise ValueError(
            "Only one column was detected. Confirm that the input is a "
            "tab-separated clinical export."
        )

    frame.columns = [str(column).strip() for column in frame.columns]
    if frame.columns.duplicated().any():
        duplicates = frame.columns[frame.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names detected: {duplicates}")

    for column in frame.columns:
        frame[column] = frame[column].str.strip()

    return frame


def select_candidates(columns: Iterable[str], group: str) -> list[str]:
    patterns = COLUMN_PATTERNS[group]
    return [
        column
        for column in columns
        if any(re.search(pattern, normalise_name(column)) for pattern in patterns)
    ]


def preferred_column(columns: Iterable[str], exact_names: Iterable[str]) -> str | None:
    lookup = {normalise_name(column): column for column in columns}
    for name in exact_names:
        match = lookup.get(normalise_name(name))
        if match is not None:
            return match
    return None


def infer_series_type(series: pd.Series) -> tuple[str, pd.Series, float]:
    non_missing = series.dropna()
    if non_missing.empty:
        return "empty", pd.Series(dtype=float), 0.0

    numeric = pd.to_numeric(non_missing, errors="coerce")
    numeric_share = float(numeric.notna().mean())
    if numeric_share >= 0.90:
        return "numeric", numeric.dropna(), numeric_share
    return "categorical", numeric.dropna(), numeric_share


def compact_counts(series: pd.Series, limit: int = 10) -> str:
    counts = series.dropna().astype(str).value_counts().head(limit)
    if counts.empty:
        return "—"
    values = [
        f"{value[:60]} ({int(count)})"
        for value, count in counts.items()
    ]
    suffix = "; …" if series.dropna().nunique() > limit else ""
    return "; ".join(values) + suffix


def build_report(df: pd.DataFrame, input_path: Path) -> str:
    row_count, column_count = df.shape
    total_cells = int(df.size)
    missing_cells = int(df.isna().sum().sum())
    missing_pct = (100 * missing_cells / total_cells) if total_cells else 0.0
    duplicate_rows = int(df.duplicated().sum())

    identifier_columns = select_candidates(df.columns, "identifier")
    survival_columns = select_candidates(df.columns, "survival")
    clinical_columns = select_candidates(df.columns, "clinical_feature")

    patient_id = preferred_column(
        df.columns,
        ["PATIENT_ID", "Patient ID", "CASE_ID", "Case ID"],
    )
    sample_id = preferred_column(
        df.columns,
        ["SAMPLE_ID", "Sample ID", "SAMPLE_IDENTIFIER"],
    )

    quality_rows = []
    all_missing_columns = []
    high_missing_columns = []

    for column in df.columns:
        series = df[column]
        non_missing = int(series.notna().sum())
        column_missing_pct = 100 * float(series.isna().mean())
        unique_values = int(series.nunique(dropna=True))
        inferred_type, _, numeric_share = infer_series_type(series)

        quality_rows.append(
            [
                column,
                inferred_type,
                non_missing,
                f"{column_missing_pct:.1f}%",
                unique_values,
                f"{numeric_share:.0%}" if inferred_type != "empty" else "—",
            ]
        )

        if non_missing == 0:
            all_missing_columns.append(column)
        if column_missing_pct >= 40.0:
            high_missing_columns.append((column, column_missing_pct))

    id_rows = []
    for column in identifier_columns:
        series = df[column]
        non_missing = int(series.notna().sum())
        unique_values = int(series.nunique(dropna=True))
        repeated_values = int(series.dropna().duplicated().sum())
        id_rows.append([column, non_missing, unique_values, repeated_values])

    outcome_rows = []
    for column in survival_columns:
        series = df[column]
        inferred_type, numeric_values, numeric_share = infer_series_type(series)
        non_missing = int(series.notna().sum())
        unique_values = int(series.nunique(dropna=True))

        if inferred_type == "numeric" and not numeric_values.empty:
            summary = (
                f"min={numeric_values.min():.3g}; "
                f"median={numeric_values.median():.3g}; "
                f"max={numeric_values.max():.3g}"
            )
        else:
            summary = compact_counts(series)

        outcome_rows.append(
            [column, inferred_type, non_missing, unique_values, summary]
        )

    if patient_id and sample_id:
        unique_patients = int(df[patient_id].nunique(dropna=True))
        unique_samples = int(df[sample_id].nunique(dropna=True))
        if unique_samples == row_count and unique_patients < row_count:
            grain = (
                f"Probable sample-level table: {unique_samples} unique samples "
                f"for {unique_patients} unique patients."
            )
        elif unique_patients == row_count:
            grain = (
                f"Probable patient-level table: {unique_patients} unique patients. "
                f"A sample identifier is also present ({unique_samples} unique values)."
            )
        else:
            grain = (
                f"Grain remains ambiguous: {unique_patients} unique patients and "
                f"{unique_samples} unique samples across {row_count} rows."
            )
    elif patient_id:
        unique_patients = int(df[patient_id].nunique(dropna=True))
        grain = (
            f"Patient identifier detected: {unique_patients} unique values "
            f"across {row_count} rows."
        )
    elif sample_id:
        unique_samples = int(df[sample_id].nunique(dropna=True))
        grain = (
            f"Sample identifier detected: {unique_samples} unique values "
            f"across {row_count} rows."
        )
    else:
        grain = "No standard patient or sample identifier was detected automatically."

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    source_rows = [
        ["Input path", input_path.as_posix()],
        ["File size", f"{input_path.stat().st_size:,} bytes"],
        ["Rows", f"{row_count:,}"],
        ["Columns", f"{column_count:,}"],
        ["Exact duplicate rows", f"{duplicate_rows:,}"],
        ["Missing cells", f"{missing_cells:,} ({missing_pct:.1f}%)"],
        ["Generated at", generated_at],
    ]

    report = [
        "# TCGA-BRCA clinical data audit",
        "",
        "> Aggregate structural audit only. No patient-level rows are reproduced.",
        "",
        "## Source summary",
        "",
        markdown_table(["Measure", "Value"], source_rows),
        "",
        "## Probable table grain",
        "",
        grain,
        "",
        "## Identifier candidates",
        "",
    ]

    if id_rows:
        report.append(
            markdown_table(
                ["Column", "Non-missing", "Unique", "Repeated values"],
                id_rows,
            )
        )
    else:
        report.append("No identifier candidate was detected automatically.")

    report.extend(["", "## Survival and outcome candidates", ""])
    if outcome_rows:
        report.append(
            markdown_table(
                ["Column", "Inferred type", "Non-missing", "Unique", "Summary"],
                outcome_rows,
            )
        )
    else:
        report.append("No survival or outcome candidate was detected automatically.")

    report.extend(["", "## Candidate clinical predictors", ""])
    if clinical_columns:
        report.extend(f"- {markdown_escape(column)}" for column in clinical_columns)
    else:
        report.append("No candidate clinical predictor was detected automatically.")

    report.extend(
        [
            "",
            "## Complete column-quality inventory",
            "",
            markdown_table(
                [
                    "Column",
                    "Inferred type",
                    "Non-missing",
                    "Missing",
                    "Unique",
                    "Numeric parse rate",
                ],
                quality_rows,
            ),
            "",
            "## Automatic alerts",
            "",
            f"- Exact duplicate rows: **{duplicate_rows:,}**.",
        ]
    )

    if all_missing_columns:
        report.append(
            "- Entirely missing columns: "
            + ", ".join(markdown_escape(column) for column in all_missing_columns)
            + "."
        )
    else:
        report.append("- No entirely missing column detected.")

    if high_missing_columns:
        formatted = ", ".join(
            f"{markdown_escape(column)} ({percentage:.1f}%)"
            for column, percentage in sorted(
                high_missing_columns,
                key=lambda item: item[1],
                reverse=True,
            )
        )
        report.append(f"- Columns with at least 40% missing values: {formatted}.")
    else:
        report.append("- No column has at least 40% missing values.")

    if not survival_columns:
        report.append(
            "- **Blocking:** survival duration/status columns require manual identification."
        )

    report.extend(
        [
            "",
            "## Decisions required before modelling",
            "",
            "1. Confirm whether one row represents a patient or a tumour sample.",
            "2. Validate the overall-survival duration and event columns.",
            "3. Define inclusion, exclusion and duplicate-handling rules.",
            "4. Identify patients censored before the 36-month horizon.",
            "5. Select clinically defensible predictors available at diagnosis.",
            "6. Decide which missing-data rules are acceptable before splitting the cohort.",
            "",
        ]
    )

    return "\n".join(report)


def main() -> None:
    args = parse_args()
    df = read_tsv(args.input)
    report = build_report(df, args.input)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")

    print("TCGA-BRCA clinical audit completed")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")
    print(f"Report: {args.report.as_posix()}")


if __name__ == "__main__":
    main()
