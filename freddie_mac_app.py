# freddie_mac_app.py
# Run this via cmd: streamlit run freddie_mac_app.py

import streamlit as st
import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path
import matplotlib.pyplot as plt

# --- 1. DYNAMIC PATH SETUP ---
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "freddie" / "xgb_champion.json"

@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        return None
    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    return model

xgb_model = load_model()

FEATURES = ['CLASSIC FICO', 'ORIGINAL DEBT-TO-INCOME (DTI) RATIO', 'ORIGINAL LOAN-TO-VALUE (LTV)', 
            'ORIGINAL UPB', 'ORIGINAL INTEREST RATE', 'LOAN AGE', 'CURRENT ACTUAL UPB', 
            'CHANNEL', 'PROPERTY TYPE', 'LOAN PURPOSE', 'OCCUPANCY STATUS', 
            'GDP_Growth', 'Unemployment', 'HPI_YoY']
CAT_FEATURES = ['CHANNEL', 'PROPERTY TYPE', 'LOAN PURPOSE', 'OCCUPANCY STATUS']

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Freddie Mac IFRS 9 Engine", layout="wide")

if xgb_model is None:
    st.error(f"❌ Model not found at: {MODEL_PATH}")
    st.stop()

st.title("🏦 Freddie Mac IFRS 9 Stress-Testing Engine")
st.markdown("This dashboard demonstrates a **Macro-Sensitive IFRS 9 ECL Engine**. Adjust the **Loan Profile** on the left to see how a borrower migrates between Stage 1, 2, and 3. The **Macro Scenario** represents the systemic economic environment and applies to the whole portfolio.")

# ==========================================
# SIDEBAR INPUTS
# ==========================================
with st.sidebar:
    st.header("👤 Individual Loan Profile")
    fico = st.slider("Classic FICO", 300, 850, 720)
    ltv = st.slider("Original LTV (%)", 10, 130, 80)
    dti = st.slider("Original DTI (%)", 1, 60, 35)
    loan_age = st.slider("Loan Age (Months)", 1, 360, 24)
    
    orig_upb = st.number_input("Original UPB ($)", 10000, 1000000, 250000)
    current_upb = st.number_input("Current UPB ($)", 10000, 1000000, 240000)
    int_rate = st.slider("Original Interest Rate (%)", 1.0, 15.0, 4.5)
    
    channel = st.selectbox("Channel", ["R (Retail)", "B (Broker)", "C (Correspondent)", "T (TPO)"])
    prop_type = st.selectbox("Property Type", ["SF (Single Family)", "CO (Condo)", "PU (PUD)", "MH (Manufactured)"])
    purpose = st.selectbox("Loan Purpose", ["P (Purchase)", "C (Cash-out Refi)", "N (No-cash Refi)"])
    occupancy = st.selectbox("Occupancy", ["P (Primary)", "I (Investor)", "S (Second Home)"])

    st.divider()
    
    st.header("🌍 Systemic Macro Scenario")
    st.caption("These variables apply to the entire economy, not just this borrower.")
    gdp = st.slider("GDP Growth (%)", -5.0, 5.0, 2.0, 0.1)
    unemp = st.slider("Unemployment Rate (%)", 3.0, 15.0, 4.5, 0.1)
    hpi = st.slider("HPI YoY Growth (%)", -15.0, 15.0, 3.0, 0.5)

# Parse categorical selections
ch_map = {"R (Retail)": "R", "B (Broker)": "B", "C (Correspondent)": "C", "T (TPO)": "T"}
pt_map = {"SF (Single Family)": "SF", "CO (Condo)": "CO", "PU (PUD)": "PU", "MH (Manufactured)": "MH"}
lp_map = {"P (Purchase)": "P", "C (Cash-out Refi)": "C", "N (No-cash Refi)": "N"}
occ_map = {"P (Primary)": "P", "I (Investor)": "I", "S (Second Home)": "S"}

# ==========================================
# MODEL INFERENCE
# ==========================================
input_dict = {
    'CLASSIC FICO': fico,
    'ORIGINAL DEBT-TO-INCOME (DTI) RATIO': dti,
    'ORIGINAL LOAN-TO-VALUE (LTV)': ltv,
    'ORIGINAL UPB': orig_upb,
    'ORIGINAL INTEREST RATE': int_rate,
    'LOAN AGE': loan_age,
    'CURRENT ACTUAL UPB': current_upb,
    'CHANNEL': ch_map[channel],
    'PROPERTY TYPE': pt_map[prop_type],
    'LOAN PURPOSE': lp_map[purpose],
    'OCCUPANCY STATUS': occ_map[occupancy],
    'GDP_Growth': gdp,
    'Unemployment': unemp,
    'HPI_YoY': hpi
}

input_df = pd.DataFrame([input_dict])[FEATURES]

for col in CAT_FEATURES:
    input_df[col] = input_df[col].astype('category')

# Score & Calibrate
raw_pd_1m = xgb_model.predict_proba(input_df)[0][1]
calibrated_pd_1m = np.clip(raw_pd_1m / 19.4, 0.0001, 0.9999)
pd_12m = np.clip(1 - (1 - calibrated_pd_1m)**12, 0, 1)
pd_lifetime = np.clip(1 - (1 - calibrated_pd_1m)**60, 0, 1)

# Dynamic LGD
base_lgd = 0.20
if hpi < -5.0:
    dynamic_lgd = base_lgd + 0.10
elif hpi < 0:
    dynamic_lgd = base_lgd + 0.05
else:
    dynamic_lgd = base_lgd

# IFRS 9 Staging with Business Rule Overrides
# Stage 3 Trigger: PD > 30% OR FICO < 550 OR LTV > 100
# Stage 2 Trigger: PD > 10% OR LTV > 90
if pd_12m > 0.30 or fico < 550 or ltv > 100:
    stage = "Stage 3 (Default)"
    effective_pd = 1.0  # Force 100% PD for defaulted
elif pd_12m > 0.10 or ltv > 90:
    stage = "Stage 2 (SICR)"
    effective_pd = pd_lifetime
else:
    stage = "Stage 1 (Performing)"
    effective_pd = pd_12m

# ECL Calculation
ecl = effective_pd * dynamic_lgd * current_upb

# ==========================================
# MAIN DASHBOARD UI
# ==========================================
st.subheader("📊 Loan-Level Results")

col1, col2, col3, col4 = st.columns(4)
col1.metric("IFRS 9 Stage", stage)
col2.metric("12-Month PD", f"{pd_12m:.2%}")
col3.metric("Lifetime PD", f"{pd_lifetime:.2%}")
col4.metric("Expected Credit Loss (ECL)", f"${ecl:,.2f}")

# Interpretation Box
if stage == "Stage 3 (Default)":
    st.error(f"**Interpretation:** This loan has triggered the **Stage 3 (Default)** override because either FICO < 550, LTV > 100%, or PD > 30%. The bank assumes a 100% probability of loss and provisions **${ecl:,.2f}** using a Dynamic LGD of **{dynamic_lgd:.1%}**.")
elif stage == "Stage 2 (SICR)":
    st.warning(f"**Interpretation:** The 12-month PD is **{pd_12m:.2%}** (or LTV > 90%). Because this represents a Significant Increase in Credit Risk (SICR), the loan is classified as **{stage}**. Using a Dynamic LGD of **{dynamic_lgd:.1%}**, the bank must provision **${ecl:,.2f}**.")
else:
    st.info(f"**Interpretation:** The 12-month PD is **{pd_12m:.2%}**, which is below the 10% SICR threshold and LTV is under 90%. The loan is classified as **{stage}**. Using a Dynamic LGD of **{dynamic_lgd:.1%}**, the bank must provision **${ecl:,.2f}**.")

st.divider()

# ECL Provision Trend Chart
st.subheader("📈 Portfolio ECL Provision Trend (Historical Backtest)")
st.markdown("This chart shows how the IFRS 9 engine provisions capital across the GFC, Benign, COVID, and Rate-Shock periods.")

years = list(range(2006, 2024))
historical_ecl = [52677, 49761, 33890, 13096, 13398, 12217, 13081, 12822, 11083, 15842, 16169, 14652, 12735, 10376, 8994, 12898, 27430, 29252]
historical_coverage = [10.83, 10.73, 8.38, 2.48, 2.51, 2.24, 1.80, 1.92, 2.00, 2.51, 2.45, 2.72, 3.28, 2.59, 1.41, 1.90, 4.73, 6.80]

fig, ax1 = plt.subplots(figsize=(12, 5))
ax1.bar(years, historical_ecl, color='#4C72B0', alpha=0.7, label='Total ECL Provision ($M)')
ax1.set_ylabel('ECL Provision ($ Millions)', color='#4C72B0', fontsize=12)
ax1.tick_params(axis='y', labelcolor='#4C72B0')

ax2 = ax1.twinx()
ax2.plot(years, historical_coverage, color='black', marker='o', linewidth=2, label='Coverage Ratio (%)')
ax2.set_ylabel('Coverage Ratio (%)', color='black', fontsize=12)
ax2.tick_params(axis='y', labelcolor='black')

plt.title('Freddie Mac Portfolio ECL & Coverage (2006-2023)', fontsize=14)
plt.xticks(years, rotation=45)
fig.tight_layout()
st.pyplot(fig)