"""
TCGA-BRCA Survival Predictor — Streamlit App
Mokdata Portfolio | Chams-Eddine
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from lifelines import KaplanMeierFitter

st.set_page_config(
    page_title="BRCA Survival Predictor",
    page_icon="🎗️",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #0f1117; color: #e8e8e8; }
.metric-card { background: #1a1d27; border-radius: 10px; padding: 20px; border: 1px solid #2a2d3a; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_train():
    from src.data_loader import generate_synthetic_brca
    from src.preprocessing import preprocess, FEATURES
    df = generate_synthetic_brca(1000)
    X, y, le_stage, le_subtype = preprocess(df)
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X, y)
    return df, model, le_stage, le_subtype, FEATURES

df, model, le_stage, le_subtype, FEATURES = load_and_train()

st.title("🎗️ TCGA-BRCA Survival Predictor")
st.caption("Prédiction de survie à 3 ans — Cancer du sein | Données synthétiques basées sur TCGA-BRCA")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Patients", f"{len(df):,}")
col2.metric("Décès observés", f"{df.os_status.sum():,}")
col3.metric("Survie médiane", f"{df.os_months.median():.0f} mois")
col4.metric("Variables", str(len(FEATURES)))

st.divider()

tab1, tab2, tab3 = st.tabs(["🔮 Prédiction patient", "📊 Analyse cohorte", "📈 Courbes KM"])

with tab1:
    st.subheader("Prédire la survie à 3 ans (36 mois)")
    c1, c2, c3 = st.columns(3)
    with c1:
        age   = st.slider("Âge au diagnostic", 25, 90, 55)
        stage = st.selectbox("Stade tumoral", ["I","II","III","IV"])
        grade = st.selectbox("Grade histologique", [1, 2, 3])
    with c2:
        subtype = st.selectbox("Sous-type moléculaire", ["Luminal_A","Luminal_B","HER2","Basal","Normal"])
        er_status  = st.selectbox("ER Status", [("Positif",1),("Négatif",0)], format_func=lambda x: x[0])[1]
        pr_status  = st.selectbox("PR Status", [("Positif",1),("Négatif",0)], format_func=lambda x: x[0])[1]
    with c3:
        her2       = st.selectbox("HER2 Status", [("Positif",1),("Négatif",0)], format_func=lambda x: x[0])[1]
        tumor_size = st.slider("Taille tumorale (mm)", 5, 120, 25)
        nodes      = st.slider("Ganglions positifs", 0, 4, 0)

    if st.button("🔮 Prédire", type="primary"):
        stage_enc   = le_stage.transform([stage])[0]
        subtype_enc = le_subtype.transform([subtype])[0]
        X_input = pd.DataFrame([[age, stage_enc, subtype_enc, grade, 
                                  er_status, pr_status, her2, tumor_size, nodes]],
                                columns=FEATURES)
        proba = model.predict_proba(X_input)[0][1]
        risk = "🟢 Faible risque" if proba > 0.6 else ("🟡 Risque modéré" if proba > 0.4 else "🔴 Risque élevé")
        st.markdown(f"### {risk}")
        st.progress(proba)
        st.metric("Probabilité de survie > 36 mois", f"{proba*100:.1f}%")

with tab2:
    st.subheader("Distribution de la cohorte")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.patch.set_facecolor('#0f1117')
    for ax in axes:
        ax.set_facecolor('#1a1d27')
        ax.tick_params(colors='#e8e8e8')
        for s in ['top','right']: ax.spines[s].set_visible(False)
        for s in ['bottom','left']: ax.spines[s].set_color('#2a2d3a')

    df['stage'].value_counts().reindex(['I','II','III','IV']).plot(
        kind='bar', ax=axes[0], color=['#a8ff78','#00d4ff','#ffd700','#ff6b9d'], edgecolor='none')
    axes[0].set_title("Stades", color='white'); axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=0)
    
    df['subtype'].value_counts().plot(kind='barh', ax=axes[1], color='#00d4ff', edgecolor='none')
    axes[1].set_title("Sous-types", color='white')
    
    axes[2].hist(df['age_at_diagnosis'], bins=20, color='#a8ff78', edgecolor='#0f1117')
    axes[2].axvline(df['age_at_diagnosis'].median(), color='#ffd700', linestyle='--', linewidth=2)
    axes[2].set_title("Âge au diagnostic", color='white')
    
    for ax in axes:
        ax.yaxis.label.set_color('#e8e8e8')
        ax.xaxis.label.set_color('#e8e8e8')
    plt.tight_layout()
    st.pyplot(fig)

with tab3:
    st.subheader("Courbes de Kaplan-Meier")
    group_col = st.radio("Grouper par :", ["stage", "subtype"], horizontal=True)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#1a1d27')
    
    palette = ['#00d4ff','#a8ff78','#ffd700','#ff6b9d','#ff8c42']
    for i, group in enumerate(sorted(df[group_col].unique())):
        mask = df[group_col] == group
        kmf = KaplanMeierFitter()
        kmf.fit(df[mask]['os_months'], df[mask]['os_status'], label=str(group))
        kmf.plot_survival_function(ax=ax, color=palette[i % len(palette)], linewidth=2.5, ci_show=False)
    
    ax.tick_params(colors='#e8e8e8')
    ax.set_xlabel("Mois", color='#e8e8e8')
    ax.set_ylabel("Probabilité de survie", color='#e8e8e8')
    for s in ['top','right']: ax.spines[s].set_visible(False)
    for s in ['bottom','left']: ax.spines[s].set_color('#2a2d3a')
    ax.grid(color='#2a2d3a', alpha=0.4)
    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_facecolor('#1a1d27')
        for t in legend.get_texts(): t.set_color('#e8e8e8')
    st.pyplot(fig)

st.divider()
st.caption("Portfolio Mokdata | Chams-Eddine | TCGA-BRCA Synthetic Data | CC-BY 4.0")
