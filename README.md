# Freddie-Mac-IFRS9-Stress-Testing-Engine
An end-to-end IFRS 9 Stress-Testing Engine built on 54M Freddie Mac loan records. Features a macro-sensitive XGBoost PD model, dynamic LGD, and an interactive Streamlit dashboard for real-time staging simulation. Fully validated to SR 11-7 standards.

# 🏦 Freddie Mac IFRS 9 Stress-Testing Engine

**An end-to-end Quantitative Credit Risk pipeline built on 54 million loan-month observations (2006–2023).**

This project demonstrates the full model development lifecycle: rigorous Data Auditing, Champion/Challenger PD Modeling (XGBoost vs. Logistic Regression), and a Macro-Sensitive IFRS 9 ECL Engine with Dynamic LGD.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7-orange.svg)](https://xgboost.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red.svg)](https://streamlit.io/)

---

## 📊 The Dashboard

The interactive Streamlit app allows you to adjust loan characteristics (FICO, LTV, DTI) and macroeconomic scenarios (GDP, HPI, Unemployment) to watch the IFRS 9 Stage and Expected Credit Loss (ECL) update in real-time.

| Stage 1: Performing | Stage 2: SICR | Stage 3: Default |
| :---: | :---: | :---: |
| ![Stage 1](reports/screenshots/streamlit_stage1.png) | ![Stage 2](reports/screenshots/streamlit_stage2.png) | ![Stage 3](reports/screenshots/streamlit_stage3.png) |

---

## 🏆 Model Validation & Governance

This project was developed to **SR 11-7 / PRA SS1/23 standards**. Before trusting the ECL engine, the delinquency pipeline was audited using Transition Matrices, and the model was backtested Out-of-Time (2017–2023).

> **Validation Rating: 9.5 / 10 (FIT FOR USE)** 
> 
> *   **Out-of-Time Gini:** 0.5070 (Top Quartile for Mortgages)
> *   **Data Integrity:** 0.00% skip-trace rate across 54M rows.
> *   **Macro-Sensitivity:** Verified via Empirical Lifetime PD curves (accurately capturing the GFC and COVID shocks).

📄 **[Click here to read the full Model Validation Report](docs/validation/freddie_mac_validation_v1.md)**

---

## 🔬 Credit Diagnostics (Visual EDA)

No black-box model is trustworthy without understanding the underlying data mechanics. Below is the empirical Lifetime PD curve, proving the data behaves as credit theory dictates (e.g., the 2016 vintage spiking at month 40 due to COVID).

![Lifetime PD Curves](reports/figures/lifetime_pd_curves.png)

### Transition Matrices & Roll Rates
We audited the delinquency pipeline to ensure loans don't "skip trace" directly from Current to Foreclosure. Below are the monthly transition matrices for the 2008 GFC, 2016 Benign, and 2020 COVID vintages.

| 2008 (GFC) | 2016 (Benign) | 2020 (COVID) |
| :---: | :---: | :---: |
| ![2008 Matrix](reports/figures/transition_matrix_2008.png) | ![2016 Matrix](reports/figures/transition_matrix_2016.png) | ![2020 Matrix](reports/figures/transition_matrix_2020.png) |

---

## 📈 The Macro-Sensitive ECL Engine

The engine applies a Dynamic Loss Given Default (LGD) based on House Price Index (HPI) movements. When HPI declines (e.g., 2008 GFC or 2022 rate shock), LGD jumps from 20% to 30%, forcing the bank to provision capital dynamically. 

![ECL Provision Trend](reports/figures/ifrs9_ecl_provision_trend.png)

*The chart above shows the ECL Provision trend, accurately reflecting the GFC spike (2006-2008), the benign period, the COVID forbearance dip, and the post-2022 rate shock.*

---

## 🛠️ Technical Architecture

1. **Data ETL:** Processed 21 annual Parquet files (54M rows). Cleaned sentinel values (`9999`), handled right-censoring, and merged macro data.
2. **Feature Engineering:** Selected 14 key features (FICO, LTV, DTI, Macro). Handled missing data via `SimpleImputer` (Challenger) and native NaNs (XGBoost).
3. **Modeling:** 3-Tier Temporal Split (Train: 06-14, Val: 15-16, OOT: 17-23). Champion (XGBoost) calibrated against `scale_pos_weight`.
4. **IFRS 9 Engine:** Implemented 3-stage logic. Stage 2 trigger is `PD_12M > 15%`. ECL = `EAD * PD * Dynamic_LGD`.

### How to Run Locally
```bash
# 1. Clone the repo
git clone https://github.com/yourusername/freddie-mac-ifrs9.git

# 2. Launch the Streamlit Dashboard
streamlit run freddie_mac_app.py
