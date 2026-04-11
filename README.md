# 🎗️ TCGA-BRCA Cancer Survival Predictor

> Prédiction de survie à 3 ans sur le cancer du sein — Portfolio Data Science Senior

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange)](https://scikit-learn.org)
[![Lifelines](https://img.shields.io/badge/lifelines-0.27-green)](https://lifelines.readthedocs.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)](https://streamlit.io)

## Contexte

Ce projet simule un workflow complet de data science appliqué à la recherche contre le cancer du sein, basé sur les distributions cliniques du dataset TCGA-BRCA (The Cancer Genome Atlas — Breast Carcinoma).

**Question clinique :** Peut-on prédire, au moment du diagnostic, si un patient survivra plus de 36 mois, en utilisant uniquement des variables cliniques et biologiques de routine ?

---

## Données

Dataset synthétique généré à partir des distributions publiées dans :
- *Comprehensive molecular portraits of human breast tumours*, Nature 2012 (TCGA)
- *The molecular taxonomy of primary prostate cancer*, Cell 2015

**Variables** : âge, stade TNM, sous-type PAM50, grade histologique, statuts ER/PR/HER2, taille tumorale, ganglions positifs, survie globale (OS)

**n = 1000 patients** | 56.8% d'événements (décès) | Suivi médian : 41 mois

---

## Modèles implémentés

| Modèle | AUC Test | CV AUC (5-fold) |
|--------|----------|-----------------|
| Logistic Regression | 0.759 | 0.674 ± 0.042 |
| Random Forest | 0.749 | 0.646 ± 0.033 |
| Gradient Boosting | 0.737 | 0.617 ± 0.032 |
| **Cox PH (C-index)** | **0.664** | — |

**Variables les plus prédictives** : stade tumoral, sous-type moléculaire, grade histologique

---

## Structure

```
cancer-survival-predictor/
├── data/
│   ├── brca_clinical.csv          # Dataset principal
│   ├── metrics.json               # Résultats modèles
│   └── figures/                   # Visualisations
│       ├── 01_exploration.png     # EDA dashboard
│       ├── 02_kaplan_meier.png    # Courbes KM
│       └── 03_modeling.png        # ROC + Feature importance
├── src/
│   ├── data_loader.py             # Chargement et génération données
│   ├── preprocessing.py           # Pipeline de prétraitement
│   └── model.py                   # Entraînement et évaluation
├── app/
│   └── streamlit_app.py           # Interface interactive
├── requirements.txt
└── README.md
```

---

## Lancer l'app

```bash
git clone https://github.com/[username]/cancer-survival-predictor
cd cancer-survival-predictor
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

---

## Points techniques clés

- **Analyse de survie** : courbes Kaplan-Meier, log-rank test, modèle de Cox PH
- **Classification** : Random Forest, Gradient Boosting, Logistic Regression
- **Validation** : cross-validation stratifiée 5-fold, AUC-ROC, C-index
- **Feature importance** : RandomForest + coefficients Cox (exp(coef) = Hazard Ratio)
- **Interprétabilité clinique** : les résultats sont discutés en termes médicaux

---

## Limites & perspectives

- Dataset synthétique : validation sur données réelles TCGA nécessaire
- Ajout de données génomiques (expression ARN, mutations) pour modèles multimodaux
- Déploiement sur GCP Cloud Run + monitoring MLflow
- Intégration SHAP pour explicabilité individuelle des prédictions

---

*Mokdata Portfolio | Chams-Eddine | 2024*
