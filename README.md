# Freddie-Mac-IFRS9-Stress-Testing-Engine
An end-to-end IFRS 9 Stress-Testing Engine built on 54M Freddie Mac loan records. Features a macro-sensitive XGBoost PD model, dynamic LGD, and an interactive Streamlit dashboard for real-time staging simulation. Fully validated to SR 11-7 standards.

# Freddie Mac IFRS 9 Stress-Testing Engine

An end-to-end Quantitative Credit Risk pipeline built on 54 million loan-month observations (2006–2023). This project demonstrates the full model development lifecycle: rigorous Data Auditing, Champion/Challenger PD Modeling (XGBoost vs. Logistic Regression), and a Macro-Sensitive IFRS 9 ECL Engine with Dynamic LGD.

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-1.7-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red.svg)

## Overview
This repository contains a production-grade stress-testing engine designed to calculate IFRS 9 Expected Credit Loss (ECL) under varying macroeconomic scenarios. Using 18 years of Freddie Mac single-family loan data, the engine models the GFC (2008) and COVID (2020) shocks to demonstrate how banks dynamically provision capital across Stage 1, Stage 2, and Stage 3.

## Model Validation & Governance
This project was developed to **SR 11-7 / PRA SS1/23 standards**. Before trusting the ECL engine, the delinquency pipeline was audited using Transition Matrices, and the model was backtested Out-of-Time (2017–2023).

> **Validation Rating: 9.5 / 10 (FIT FOR USE)** 
> 
> *   **Out-of-Time Gini:** 0.5070 (Top Quartile for Mortgages)
> *   **Data Integrity:** 0.00% skip-trace rate across 54M rows.
> *   **Macro-Sensitivity:** Verified via Empirical Lifetime PD curves (accurately capturing the GFC and COVID shocks).

📄 **[Click here to read the full Model Validation Report](docs/validation/freddie_mac_validation_v1.md)**

## Interactive Dashboard
The Streamlit app allows you to adjust individual loan characteristics (FICO, LTV, DTI) while holding the macroeconomic scenario constant. Watch how the IFRS 9 Stage and Expected Credit Loss (ECL) update in real-time based on business-rule overrides and model predictions.

**Stage 1: Performing (Strong Credit Profile)**
<img src="reports/screenshots/streamlit_stage1.png" width="100%">

**Stage 2: SICR (Significant Increase in Credit Risk)**
<img src="reports/screenshots/streamlit_stage2.png" width="100%">

**Stage 3: Default (Extreme Stress / High LTV)**
<img src="reports/screenshots/streamlit_stage3.png" width="100%">

## Credit Diagnostics (Visual EDA)
No black-box model is trustworthy without understanding the underlying data mechanics. Below is the empirical Lifetime PD curve, proving the data behaves as credit theory dictates (e.g., the 2016 vintage spiking at month 40 due to COVID).

<img src="reports/figures/lifetime_pd_curves.png" width="100%">
*Figure 1: Empirical Lifetime PD Curves. The red lines show the slow GFC bleed, while the blue line shows the sudden COVID shock hitting the 2016 vintage.*

### Transition Matrices & Roll Rates
We audited the delinquency pipeline to ensure loans don't "skip trace" directly from Current to Foreclosure. Below are the monthly transition matrices for the 2008 GFC, 2016 Benign, and 2020 COVID vintages.

| 2008 (GFC) | 2016 (Benign) | 2020 (COVID) |
| :---: | :---: | :---: |
| <img src="reports/figures/transition_matrix_2008.png" width="100%"> | <img src="reports/figures/transition_matrix_2016.png" width="100%"> | <img src="reports/figures/transition_matrix_2020.png" width="100%"> |

## The Macro-Sensitive ECL Engine
The engine applies a Dynamic Loss Given Default (LGD) based on House Price Index (HPI) movements. When HPI declines (e.g., 2008 GFC or 2022 rate shock), LGD jumps from 20% to 30%, forcing the bank to provision capital dynamically. 

<img src="reports/figures/ifrs9_ecl_provision_trend.png" width="100%">
*Figure 2: IFRS 9 ECL Provision trend, accurately reflecting the GFC spike (2006-2008), the benign period, the COVID forbearance dip, and the post-2022 rate shock.*

## Technical Architecture
1. **Data ETL:** Processed 21 annual Parquet files (54M rows). Cleaned sentinel values (`9999`), handled right-censoring, and merged macro data.
2. **Feature Engineering:** Selected 14 key features (FICO, LTV, DTI, Macro). Handled missing data via `SimpleImputer` (Challenger) and native NaNs (XGBoost).
3. **Modeling:** 3-Tier Temporal Split (Train: 06-14, Val: 15-16, OOT: 17-23). Champion (XGBoost) calibrated against `scale_pos_weight`.
4. **IFRS 9 Engine:** Implemented 3-stage logic with business rule overrides. ECL = `EAD * PD * Dynamic_LGD`.

### How to Run Locally
```bash
# 1. Clone the repo
git clone https://github.com/raymondsibanda/Freddie-Mac-IFRS9-Stress-Testing-Engine.git

# 2. Launch the Streamlit Dashboard
streamlit run freddie_mac_app.py

Author: Raymond Sibanda | LinkedIn
FRM | BSc Mathematics | BCom Honors Accounting

### How to Run Locally
```bash
# 1. Clone the repo
git clone https://github.com/raymondsibanda/Freddie-Mac-IFRS9-Stress-Testing-Engine.git

# 2. Launch the Streamlit Dashboard
streamlit run freddie_mac_app.py
