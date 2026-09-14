# TCGA-BRCA modelling cohort summary

> Aggregate report only. No patient-level rows are reproduced.

## Source and cohort rules

- Source: data/raw/tcga-brca/brca_tcga_pub2015_clinical_data.tsv
- Analysis unit: one patient.
- Duplicate rule: prefer a row with complete overall-survival data, then a primary tumour sample, then Sample ID order.
- Primary endpoint: Overall Survival (Months) with Overall Survival Status.

## Cohort flow

| Measure | Value |
| --- | --- |
| Raw sample rows | 818 |
| Unique patient IDs in source | 817 |
| Repeated patient rows | 1 |
| Rows after patient deduplication | 817 |
| Patients excluded: missing OS duration/status | 1 |
| Final patient-level cohort | 816 |
| Observed deaths | 119 |
| Censored observations | 697 |
| Observed event rate | 14.6% |

## Secondary binary endpoint at 36 months

| Observed state | Patients | Binary label |
| --- | --- | --- |
| Death on or before 36 months | 54 | 0 |
| Observed survival beyond 36 months | 329 | 1 |
| Censored on or before 36 months | 433 | Missing: excluded from binary modelling |

Patients censored before the horizon remain unresolved. They are not labelled as survivors.

## Candidate baseline predictors

| Feature | Type | Non-missing | Missing | Unique |
| --- | --- | --- | --- | --- |
| age_at_diagnosis | numeric | 815 | 0.1% | 64 |
| nodes_examined | numeric | 716 | 12.3% | 42 |
| nodes_positive | numeric | 685 | 16.1% | 27 |
| ajcc_stage | categorical | 807 | 1.1% | 12 |
| ajcc_t | categorical | 816 | 0.0% | 12 |
| ajcc_n | categorical | 816 | 0.0% | 15 |
| ajcc_m | categorical | 816 | 0.0% | 4 |
| er_status | categorical | 778 | 4.7% | 3 |
| pr_status | categorical | 777 | 4.8% | 3 |
| her2_status | categorical | 683 | 16.3% | 4 |
| histology | categorical | 815 | 0.1% | 8 |
| menopause_status | categorical | 761 | 6.7% | 4 |

No imputation, category grouping, scaling or encoding is fitted during cohort construction. Those transformations must be fitted inside each training fold.

## Aggregate data-quality flags

| Check | Count |
| --- | --- |
| Zero-month OS durations retained for review | 12 |
| Ages outside [18, 120] set to missing | 0 |
| Negative lymph-node counts set to missing | 0 |
| Rows with positive nodes above examined nodes | 0 |

## Variables deliberately excluded from the first model

- Patient and sample identifiers: tracking only, never predictors.
- DFS/PFS and follow-up fields: outcomes or outcome-derived fields.
- Treatment and surgical fields: unavailable at initial diagnosis.
- Mutation count, TMB and fraction genome altered: reserved for a separate genomic model.
- Race and ethnicity: reserved for fairness assessment, not used as predictors in the first clinical model.
- PAM50 subtype, tumour size and histologic grade: not present as validated fields in this clinical export.
