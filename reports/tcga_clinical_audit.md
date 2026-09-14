# TCGA-BRCA clinical data audit

> Aggregate structural audit only. No patient-level rows are reproduced.

## Source summary

| Measure | Value |
| --- | --- |
| Input path | data/raw/tcga-brca/brca_tcga_pub2015_clinical_data.tsv |
| File size | 724,142 bytes |
| Rows | 818 |
| Columns | 110 |
| Exact duplicate rows | 0 |
| Missing cells | 37,657 (41.9%) |
| Generated at | 2026-09-14 16:00:35 UTC |

## Probable table grain

Probable sample-level table: 818 unique samples for 817 unique patients.

## Identifier candidates

| Column | Non-missing | Unique | Repeated values |
| --- | --- | --- | --- |
| Patient ID | 818 | 817 | 1 |
| Sample ID | 818 | 818 | 0 |
| Days to Sample Collection. | 816 | 584 | 232 |
| Other Patient ID | 818 | 817 | 1 |
| Other Sample ID | 817 | 817 | 0 |
| Did patient start adjuvant postoperative radiotherapy? | 52 | 2 | 50 |
| Number of Samples Per Patient | 818 | 2 | 816 |
| Sample Type | 818 | 2 | 816 |

## Survival and outcome candidates

| Column | Inferred type | Non-missing | Unique | Summary |
| --- | --- | --- | --- | --- |
| Death from Initial Pathologic Diagnosis Date | numeric | 85 | 83 | min=158; median=1.51e+03; max=4.46e+03 |
| Days to Last Followup | numeric | 732 | 511 | min=-7; median=365; max=7.07e+03 |
| Disease Free (Months) | numeric | 740 | 595 | min=0; median=25; max=281 |
| Disease Free Status | categorical | 741 | 2 | 0:DiseaseFree (656); 1:Recurred/Progressed (85) |
| Overall Survival (Months) | numeric | 817 | 647 | min=0; median=28.8; max=283 |
| Overall Survival Status | categorical | 818 | 2 | 0:LIVING (697); 1:DECEASED (121) |

## Candidate clinical predictors

- Diagnosis Age
- American Joint Committee on Cancer Metastasis Stage Code
- Neoplasm Disease Lymph Node Stage American Joint Committee on Cancer Code
- Neoplasm Disease Stage American Joint Committee on Cancer Code
- American Joint Committee on Cancer Tumor Stage Code
- ER positivity scale other
- ER positivity scale used
- ER Status By IHC
- ER Status IHC Percent Positive
- Ethnicity Category
- HER2 and cent17 cells count
- HER2 and cent17 scale other
- HER2 cent17 ratio
- HER2 copy number
- HER2 fish method
- HER2 fish status
- HER2 ihc percent positive
- HER2 ihc score
- HER2 positivity method text
- HER2 positivity scale other
- Neoplasm Histologic Type Name
- Tumor Other Histologic Subtype
- International Classification of Diseases for Oncology, Third Edition ICD-O-3 Histology Code
- IHC-HER2
- Primary Lymph Node Presentation Assessment Ind-3
- Positive Finding Lymph Node Hematoxylin and Eosin Staining Microscopy Count
- Positive Finding Lymph Node Keratin Immunohistochemistry Staining Method Count
- Lymph Node(s) Examined Number
- Menopause Status
- Metastatic tumor indicator
- Nte cent 17 HER2 ratio
- Nte er ihc intensity score
- Nte er status
- Nte er status ihc positive
- Nte HER2 fish status
- Nte HER2 positivity ihc score
- Nte HER2 status
- Nte HER2 status ihc positive
- Nte pr ihc intensity score
- Nte pr status by ihc
- Nte pr status ihc positive
- Primary Tumor Site
- PR positivity define method
- PR positivity ihc intensity score
- PR positivity scale other
- PR positivity scale used
- PR status by ihc
- PR status ihc percent positive
- Race Category
- Tumor Disease Anatomic Site

## Complete column-quality inventory

| Column | Inferred type | Non-missing | Missing | Unique | Numeric parse rate |
| --- | --- | --- | --- | --- | --- |
| Study ID | categorical | 818 | 0.0% | 1 | 0% |
| Patient ID | categorical | 818 | 0.0% | 817 | 0% |
| Sample ID | categorical | 818 | 0.0% | 818 | 0% |
| Diagnosis Age | numeric | 817 | 0.1% | 64 | 100% |
| American Joint Committee on Cancer Metastasis Stage Code | categorical | 818 | 0.0% | 4 | 0% |
| Neoplasm Disease Lymph Node Stage American Joint Committee on Cancer Code | categorical | 818 | 0.0% | 16 | 0% |
| Neoplasm Disease Stage American Joint Committee on Cancer Code | categorical | 809 | 1.1% | 12 | 0% |
| American Joint Committee on Cancer Publication Version Type | categorical | 721 | 11.9% | 5 | 0% |
| American Joint Committee on Cancer Tumor Stage Code | categorical | 818 | 0.0% | 12 | 0% |
| Brachytherapy first reference point administered total dose | categorical | 188 | 77.0% | 48 | 0% |
| Cancer Type | categorical | 818 | 0.0% | 1 | 0% |
| Cancer Type Detailed | categorical | 817 | 0.1% | 4 | 0% |
| Cent17 Copy Number | numeric | 66 | 91.9% | 41 | 98% |
| Birth from Initial Pathologic Diagnosis Date | numeric | 804 | 1.7% | 786 | 100% |
| Days to Sample Collection. | numeric | 816 | 0.2% | 584 | 100% |
| Death from Initial Pathologic Diagnosis Date | numeric | 85 | 89.6% | 83 | 100% |
| Last Alive Less Initial Pathologic Diagnosis Date Calculated Day Value | numeric | 817 | 0.1% | 1 | 100% |
| Days to Last Followup | numeric | 732 | 10.5% | 511 | 100% |
| Disease Free (Months) | numeric | 740 | 9.5% | 595 | 100% |
| Disease Free Status | categorical | 741 | 9.4% | 2 | 0% |
| Disease code | categorical | 5 | 99.4% | 1 | 0% |
| ER positivity scale other | categorical | 206 | 74.8% | 47 | 12% |
| ER positivity scale used | categorical | 94 | 88.5% | 2 | 0% |
| ER Status By IHC | categorical | 778 | 4.9% | 3 | 0% |
| ER Status IHC Percent Positive | categorical | 307 | 62.5% | 10 | 0% |
| Ethnicity Category | categorical | 682 | 16.6% | 2 | 0% |
| First surgical procedure other | categorical | 229 | 72.0% | 61 | 0% |
| Form completion date | categorical | 818 | 0.0% | 234 | 0% |
| Fraction Genome Altered | numeric | 817 | 0.1% | 754 | 100% |
| HER2 and cent17 cells count | numeric | 65 | 92.1% | 18 | 100% |
| HER2 and cent17 scale other | categorical | 2 | 99.8% | 2 | 0% |
| HER2 cent17 ratio | numeric | 169 | 79.3% | 63 | 100% |
| HER2 copy number | categorical | 74 | 91.0% | 50 | 86% |
| HER2 fish method | categorical | 27 | 96.7% | 18 | 0% |
| HER2 fish status | categorical | 315 | 61.5% | 4 | 0% |
| HER2 ihc percent positive | categorical | 132 | 83.9% | 10 | 0% |
| HER2 ihc score | numeric | 465 | 43.2% | 4 | 100% |
| HER2 positivity method text | categorical | 38 | 95.4% | 12 | 0% |
| HER2 positivity scale other | categorical | 10 | 98.8% | 7 | 20% |
| Neoplasm Histologic Type Name | categorical | 817 | 0.1% | 8 | 0% |
| Tumor Other Histologic Subtype | categorical | 23 | 97.2% | 13 | 0% |
| Neoadjuvant Therapy Type Administered Prior To Resection Text | categorical | 816 | 0.2% | 2 | 0% |
| Prior Cancer Diagnosis Occurence | categorical | 817 | 0.1% | 2 | 0% |
| ICD-10 Classification | categorical | 818 | 0.0% | 7 | 0% |
| International Classification of Diseases for Oncology, Third Edition ICD-O-3 Histology Code | categorical | 818 | 0.0% | 17 | 0% |
| International Classification of Diseases for Oncology, Third Edition ICD-O-3 Site Code | categorical | 818 | 0.0% | 6 | 0% |
| IHC-HER2 | categorical | 683 | 16.5% | 4 | 0% |
| IHC Score | numeric | 129 | 84.2% | 5 | 100% |
| Informed consent verified | categorical | 818 | 0.0% | 1 | 0% |
| Year Cancer Initial Diagnosis | numeric | 816 | 0.2% | 26 | 100% |
| Is FFPE | categorical | 817 | 0.1% | 1 | 0% |
| Primary Lymph Node Presentation Assessment Ind-3 | categorical | 539 | 34.1% | 2 | 0% |
| Positive Finding Lymph Node Hematoxylin and Eosin Staining Microscopy Count | numeric | 687 | 16.0% | 27 | 100% |
| Positive Finding Lymph Node Keratin Immunohistochemistry Staining Method Count | numeric | 239 | 70.8% | 5 | 100% |
| Lymph Node(s) Examined Number | numeric | 718 | 12.2% | 42 | 100% |
| Margin status reexcision | categorical | 47 | 94.3% | 3 | 0% |
| Menopause Status | categorical | 763 | 6.7% | 4 | 0% |
| Metastatic Site | categorical | 13 | 98.4% | 5 | 0% |
| Metastatic Site Other | categorical | 5 | 99.4% | 5 | 0% |
| Metastatic tumor indicator | categorical | 364 | 55.5% | 2 | 0% |
| First Pathologic Diagnosis Biospecimen Acquisition Method Type | categorical | 741 | 9.4% | 7 | 0% |
| First Pathologic Diagnosis Biospecimen Acquisition Other Method Type | categorical | 54 | 93.4% | 9 | 0% |
| Micromet detection by ihc | categorical | 534 | 34.7% | 2 | 0% |
| Mutation Count | numeric | 817 | 0.1% | 164 | 100% |
| New Neoplasm Event Post Initial Therapy Indicator | categorical | 62 | 92.4% | 2 | 0% |
| Nte cent 17 HER2 ratio | numeric | 2 | 99.8% | 2 | 100% |
| Nte er ihc intensity score | categorical | 1 | 99.9% | 1 | 0% |
| Nte er status | categorical | 10 | 98.8% | 2 | 0% |
| Nte er status ihc positive | categorical | 4 | 99.5% | 3 | 0% |
| Nte HER2 fish status | categorical | 3 | 99.6% | 1 | 0% |
| Nte HER2 positivity ihc score | categorical | 3 | 99.6% | 2 | 0% |
| Nte HER2 status | categorical | 7 | 99.1% | 1 | 0% |
| Nte HER2 status ihc positive | categorical | 2 | 99.8% | 1 | 0% |
| Nte pr ihc intensity score | numeric | 1 | 99.9% | 1 | 100% |
| Nte pr status by ihc | categorical | 9 | 98.9% | 2 | 0% |
| Nte pr status ihc positive | categorical | 2 | 99.8% | 1 | 0% |
| Oct embedded | categorical | 817 | 0.1% | 2 | 0% |
| Oncotree Code | categorical | 818 | 0.0% | 4 | 0% |
| Overall Survival (Months) | numeric | 817 | 0.1% | 647 | 100% |
| Overall Survival Status | categorical | 818 | 0.0% | 2 | 0% |
| Other Patient ID | categorical | 818 | 0.0% | 817 | 0% |
| Other Sample ID | categorical | 817 | 0.1% | 817 | 0% |
| Pathology Report File Name | categorical | 817 | 0.1% | 817 | 0% |
| Disease Surgical Margin Status | categorical | 769 | 6.0% | 3 | 0% |
| Adjuvant Postoperative Pharmaceutical Therapy Administered Indicator | categorical | 52 | 93.6% | 2 | 0% |
| Primary Tumor Site | categorical | 817 | 0.1% | 42 | 0% |
| Project code | categorical | 5 | 99.4% | 1 | 0% |
| Tissue Prospective Collection Indicator | categorical | 817 | 0.1% | 2 | 0% |
| PR positivity define method | categorical | 181 | 77.9% | 53 | 0% |
| PR positivity ihc intensity score | categorical | 123 | 85.0% | 5 | 20% |
| PR positivity scale other | categorical | 186 | 77.3% | 47 | 10% |
| PR positivity scale used | categorical | 89 | 89.1% | 2 | 0% |
| PR status by ihc | categorical | 777 | 5.0% | 3 | 0% |
| PR status ihc percent positive | categorical | 289 | 64.7% | 10 | 0% |
| Race Category | categorical | 741 | 9.4% | 4 | 0% |
| Did patient start adjuvant postoperative radiotherapy? | categorical | 52 | 93.6% | 2 | 0% |
| Tissue Retrospective Collection Indicator | categorical | 817 | 0.1% | 2 | 0% |
| Number of Samples Per Patient | numeric | 818 | 0.0% | 2 | 100% |
| Sample Type | categorical | 818 | 0.0% | 2 | 0% |
| Sex | categorical | 818 | 0.0% | 2 | 0% |
| Somatic Status | categorical | 818 | 0.0% | 1 | 0% |
| Staging System | categorical | 650 | 20.5% | 5 | 0% |
| Staging System.1 | categorical | 17 | 97.9% | 16 | 0% |
| Surgery for positive margins | categorical | 40 | 95.1% | 4 | 0% |
| Surgery for positive margins other | categorical | 11 | 98.7% | 11 | 0% |
| Surgical procedure first | categorical | 785 | 4.0% | 4 | 0% |
| Tissue Source Site | categorical | 817 | 0.1% | 24 | 0% |
| TMB (nonsynonymous) | numeric | 817 | 0.1% | 163 | 100% |
| Person Neoplasm Status | categorical | 731 | 10.6% | 2 | 0% |
| Tumor Disease Anatomic Site | categorical | 817 | 0.1% | 1 | 0% |

## Automatic alerts

- Exact duplicate rows: **0**.
- No entirely missing column detected.
- Columns with at least 40% missing values: Nte er ihc intensity score (99.9%), Nte pr ihc intensity score (99.9%), HER2 and cent17 scale other (99.8%), Nte cent 17 HER2 ratio (99.8%), Nte HER2 status ihc positive (99.8%), Nte pr status ihc positive (99.8%), Nte HER2 fish status (99.6%), Nte HER2 positivity ihc score (99.6%), Nte er status ihc positive (99.5%), Disease code (99.4%), Metastatic Site Other (99.4%), Project code (99.4%), Nte HER2 status (99.1%), Nte pr status by ihc (98.9%), HER2 positivity scale other (98.8%), Nte er status (98.8%), Surgery for positive margins other (98.7%), Metastatic Site (98.4%), Staging System.1 (97.9%), Tumor Other Histologic Subtype (97.2%), HER2 fish method (96.7%), HER2 positivity method text (95.4%), Surgery for positive margins (95.1%), Margin status reexcision (94.3%), Adjuvant Postoperative Pharmaceutical Therapy Administered Indicator (93.6%), Did patient start adjuvant postoperative radiotherapy? (93.6%), First Pathologic Diagnosis Biospecimen Acquisition Other Method Type (93.4%), New Neoplasm Event Post Initial Therapy Indicator (92.4%), HER2 and cent17 cells count (92.1%), Cent17 Copy Number (91.9%), HER2 copy number (91.0%), Death from Initial Pathologic Diagnosis Date (89.6%), PR positivity scale used (89.1%), ER positivity scale used (88.5%), PR positivity ihc intensity score (85.0%), IHC Score (84.2%), HER2 ihc percent positive (83.9%), HER2 cent17 ratio (79.3%), PR positivity define method (77.9%), PR positivity scale other (77.3%), Brachytherapy first reference point administered total dose (77.0%), ER positivity scale other (74.8%), First surgical procedure other (72.0%), Positive Finding Lymph Node Keratin Immunohistochemistry Staining Method Count (70.8%), PR status ihc percent positive (64.7%), ER Status IHC Percent Positive (62.5%), HER2 fish status (61.5%), Metastatic tumor indicator (55.5%), HER2 ihc score (43.2%).

## Decisions required before modelling

1. Confirm whether one row represents a patient or a tumour sample.
2. Validate the overall-survival duration and event columns.
3. Define inclusion, exclusion and duplicate-handling rules.
4. Identify patients censored before the 36-month horizon.
5. Select clinically defensible predictors available at diagnosis.
6. Decide which missing-data rules are acceptable before splitting the cohort.
