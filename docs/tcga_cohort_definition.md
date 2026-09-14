# TCGA-BRCA clinical cohort definition

This document freezes the modelling-cohort decisions made after the structural
audit. It prevents silent changes to the clinical question while the project is
developed.

## Clinical question

Estimate overall survival from information available at or close to the initial
diagnosis. Survival analysis is the primary task. Binary survival beyond 36
months is a secondary task.

This project is exploratory and educational. It is not a medical device and
must not be used for clinical decisions.

## Analysis unit

- Unit: one patient.
- Source grain: sample-level, with 818 samples for 817 patient identifiers in
  the initial audit.
- Duplicate handling: first prefer a row with complete overall-survival data,
  then a primary tumour sample, then the lexicographically first Sample ID.
- Patient and sample identifiers are retained only for traceability and group
  separation. They are never model features.

## Primary endpoint

- Duration: Overall Survival (Months).
- Event: Overall Survival Status.
- Event value 1: deceased.
- Event value 0: living/censored.
- A missing duration or event excludes the patient from the survival cohort.
- A negative duration is treated as a blocking data-quality error.
- A zero-month duration is retained but flagged for review.

## Secondary 36-month endpoint

The binary endpoint is defined only when status at 36 months is observable:

| Observation | Label |
| --- | --- |
| Death on or before 36 months | 0 |
| Observed follow-up or death after 36 months | 1 |
| Living/censored on or before 36 months | Missing |

The third group must not be labelled as surviving beyond 36 months. It is
excluded from ordinary binary classification unless a censoring-aware method is
used.

## Candidate baseline predictors

| Output feature | Source field | Type |
| --- | --- | --- |
| age_at_diagnosis | Diagnosis Age | Numeric |
| ajcc_stage | Neoplasm Disease Stage AJCC Code | Categorical |
| ajcc_t | AJCC Tumor Stage Code | Categorical |
| ajcc_n | AJCC Lymph Node Stage Code | Categorical |
| ajcc_m | AJCC Metastasis Stage Code | Categorical |
| er_status | ER Status By IHC | Categorical |
| pr_status | PR status by IHC | Categorical |
| her2_status | IHC-HER2 | Categorical |
| histology | Neoplasm Histologic Type Name | Categorical |
| menopause_status | Menopause Status | Categorical |
| nodes_examined | Lymph Node(s) Examined Number | Numeric |
| nodes_positive | Positive lymph nodes by H&E count | Numeric |

AJCC overall stage and the T/N/M components are retained in the prepared
cohort. The modelling stage must compare a composite-stage specification with a
T/N/M specification rather than blindly using redundant variables together.

## Missing-data and leakage policy

Cohort preparation standardises fields but does not learn imputation values,
rare-category groupings, scaling parameters or encodings. Those operations must
be fitted inside each training fold or inside a scikit-learn pipeline after the
train/test split.

The raw event, survival duration and the secondary 36-month label are never
predictors. Patient-level grouping must be respected in every split.

## Deliberate exclusions from the first clinical model

- Follow-up, death-date, disease-free and recurrence fields: outcome leakage.
- Treatment, radiotherapy and surgical fields: not reliably available at
  initial diagnosis.
- Mutation Count, TMB and Fraction Genome Altered: reserved for a later,
  separately labelled clinical-plus-genomic experiment.
- Race and ethnicity: retained for future fairness assessment, not used as
  predictors in the first model.
- PAM50 subtype, tumour size in millimetres and histologic grade: not present as
  validated fields in this export and therefore not reconstructed or invented.
- Extremely sparse receptor-detail fields: excluded in favour of the main
  ER/PR/HER2 status variables.

## Reproducible commands

From the repository root, with the virtual environment active:

~~~powershell
python -m pip install -r requirements-dev.txt
python -m pytest
python -m src.tcga_preprocessing
~~~

The last command creates:

- data/processed/tcga_brca_clinical_cohort.csv: local patient-level cohort;
- reports/tcga_cohort_summary.md: aggregate report safe to review and commit.

Both raw and processed patient-level datasets remain outside Git.
