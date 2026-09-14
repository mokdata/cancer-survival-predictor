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

## Categorical level distributions

Levels with fewer than 10 patients are flagged as rare candidates. Missing values are listed separately.

| Feature | Level | Patients | Cohort share | Below 10 patients |
| --- | --- | --- | --- | --- |
| ajcc_stage | IIA | 269 | 33.0% | No |
| ajcc_stage | IIB | 188 | 23.0% | No |
| ajcc_stage | IIIA | 112 | 13.7% | No |
| ajcc_stage | I | 75 | 9.2% | No |
| ajcc_stage | IA | 60 | 7.4% | No |
| ajcc_stage | IIIC | 48 | 5.9% | No |
| ajcc_stage | IIIB | 22 | 2.7% | No |
| ajcc_stage | IV | 13 | 1.6% | No |
| ajcc_stage | X | 10 | 1.2% | No |
| ajcc_stage | <missing> | 9 | 1.1% | — |
| ajcc_stage | IB | 5 | 0.6% | Yes |
| ajcc_stage | II | 3 | 0.4% | Yes |
| ajcc_stage | III | 2 | 0.2% | Yes |
| ajcc_t | T2 | 457 | 56.0% | No |
| ajcc_t | T1C | 173 | 21.2% | No |
| ajcc_t | T3 | 104 | 12.7% | No |
| ajcc_t | T1 | 34 | 4.2% | No |
| ajcc_t | T4B | 26 | 3.2% | No |
| ajcc_t | T1B | 11 | 1.3% | No |
| ajcc_t | T4 | 5 | 0.6% | Yes |
| ajcc_t | T4D | 2 | 0.2% | Yes |
| ajcc_t | T1A | 1 | 0.1% | Yes |
| ajcc_t | T2B | 1 | 0.1% | Yes |
| ajcc_t | T3A | 1 | 0.1% | Yes |
| ajcc_t | TX | 1 | 0.1% | Yes |
| ajcc_n | N0 | 250 | 30.6% | No |
| ajcc_n | N0I | 131 | 16.1% | No |
| ajcc_n | N1A | 125 | 15.3% | No |
| ajcc_n | N1 | 91 | 11.2% | No |
| ajcc_n | N2A | 49 | 6.0% | No |
| ajcc_n | N3A | 38 | 4.7% | No |
| ajcc_n | N2 | 36 | 4.4% | No |
| ajcc_n | N1B | 30 | 3.7% | No |
| ajcc_n | N1MI | 29 | 3.6% | No |
| ajcc_n | N3 | 18 | 2.2% | No |
| ajcc_n | NX | 14 | 1.7% | No |
| ajcc_n | N1C | 2 | 0.2% | Yes |
| ajcc_n | N0MOL | 1 | 0.1% | Yes |
| ajcc_n | N3B | 1 | 0.1% | Yes |
| ajcc_n | N3C | 1 | 0.1% | Yes |
| ajcc_m | M0 | 705 | 86.4% | No |
| ajcc_m | MX | 96 | 11.8% | No |
| ajcc_m | M1 | 13 | 1.6% | No |
| ajcc_m | CM0I | 2 | 0.2% | Yes |
| er_status | positive | 601 | 73.7% | No |
| er_status | negative | 175 | 21.4% | No |
| er_status | <missing> | 38 | 4.7% | — |
| er_status | indeterminate | 2 | 0.2% | Yes |
| pr_status | positive | 522 | 64.0% | No |
| pr_status | negative | 251 | 30.8% | No |
| pr_status | <missing> | 39 | 4.8% | — |
| pr_status | indeterminate | 4 | 0.5% | Yes |
| her2_status | negative | 417 | 51.1% | No |
| her2_status | equivocal | 136 | 16.7% | No |
| her2_status | <missing> | 133 | 16.3% | — |
| her2_status | positive | 121 | 14.8% | No |
| her2_status | indeterminate | 9 | 1.1% | Yes |
| histology | infiltrating_ductal_carcinoma | 598 | 73.3% | No |
| histology | infiltrating_lobular_carcinoma | 143 | 17.5% | No |
| histology | other_specify | 28 | 3.4% | No |
| histology | mixed_histology_please_specify | 23 | 2.8% | No |
| histology | mucinous_carcinoma | 14 | 1.7% | No |
| histology | medullary_carcinoma | 5 | 0.6% | Yes |
| histology | metaplastic_carcinoma | 3 | 0.4% | Yes |
| histology | <missing> | 1 | 0.1% | — |
| histology | infiltrating_carcinoma_nos | 1 | 0.1% | Yes |
| menopause_status | post_prior_bilateral_ovariectomy_or_12_mo_since_lmp_with_no_prior_hysterectomy | 538 | 65.9% | No |
| menopause_status | pre_6_months_since_lmp_and_no_prior_bilateral_ovariectomy_and_not_on_estrogen_replacement | 164 | 20.1% | No |
| menopause_status | <missing> | 55 | 6.7% | — |
| menopause_status | peri_6_12_months_since_last_menstrual_period | 30 | 3.7% | No |
| menopause_status | indeterminate_neither_pre_or_postmenopausal | 29 | 3.6% | No |

These flags are descriptive only. Frequency-based grouping must be fitted inside each training fold.

## Aggregate data-quality flags

| Check | Count |
| --- | --- |
| Zero-month OS durations retained for review | 12 |
| Zero-month OS durations with observed death | 0 |
| Zero-month OS durations with censored observation | 12 |
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
