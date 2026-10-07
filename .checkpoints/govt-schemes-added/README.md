# 🎓 EduLoan Compare — Education Loan Comparison & Student Planning Platform

> A transparent education-financing decision-support system that helps students
> and parents compare education loans with clarity.

## 🎯 What Is This?

This is **not** just an EMI calculator. It is a research-backed, transparent platform
that brings together:

- ✅ EMI calculation with full mathematical explanation
- ✅ Multi-lender comparison across 8+ lenders
- ✅ Complete amortization (repayment) schedule with visualization
- ✅ Moratorium impact simulator (interest-paid vs. capitalized)
- ✅ Total cost estimation including fees and charges
- ✅ Scenario comparison (up to 4 configurations)
- ✅ Interest rate & tenure sensitivity analysis
- ✅ Education cost estimator
- ✅ International education currency planning
- ✅ Destination updates (visa, education, work)
- ✅ Source transparency with verification dates

## 🏗️ Architecture

```
USER
 ↓
Student Profile / Education Cost
 ↓
Required Loan Amount
 ↓
Loan Database (CSV/JSON — sourced & dated)
 ↓
Calculation Engine
├── EMI (reducing-balance formula)
├── Amortization Schedule
├── Moratorium Impact
├── Total Cost (fees + charges)
├── Scenario Analysis
└── Sensitivity Analysis
 ↓
Comparison Engine
 ↓
Dashboard (Streamlit)
├── Loan Comparison Cards & Tables
├── Amortization Charts
├── Cost Breakdown (Donut chart)
├── Sensitivity Charts
└── Destination Updates
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone or download the project
cd education-loan-platform

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Run Tests

```bash
python -m pytest tests/test_calculations.py -v
```

## 📁 Project Structure

```
education-loan-platform/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                 # Theme configuration
├── data/
│   ├── loans.csv                   # Curated lender dataset (8 lenders)
│   ├── countries.json              # Target country reference data
│   └── destination_updates.json    # Sample destination updates
├── calculations/
│   ├── __init__.py
│   ├── emi.py                      # EMI calculation engine
│   ├── repayment.py                # Amortization schedule generator
│   ├── moratorium.py               # Moratorium impact calculator
│   ├── total_cost.py               # Total cost aggregator
│   ├── scenarios.py                # Scenario comparison engine
│   ├── sensitivity.py              # Rate & tenure sensitivity
│   └── education_cost.py           # Education cost + currency
├── components/
│   ├── __init__.py
│   ├── loan_card.py                # Loan card UI components
│   ├── charts.py                   # All Plotly chart functions
│   ├── comparison.py               # Comparison table components
│   ├── destination_updates.py      # Destination update cards
│   └── explainers.py               # "How is this calculated?" sections
├── research/
│   ├── sources.md                  # Data sources documentation
│   ├── literature_review.md        # Literature review
│   └── gap_analysis.md             # Gap analysis & novelty
└── tests/
    ├── __init__.py
    └── test_calculations.py        # Unit tests (35+ tests)
```

## 📊 Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit 1.35.0 |
| Language | Python 3.12 |
| Visualization | Plotly 5.22 |
| Data | CSV / JSON (curated, sourced) |
| Calculations | Pure Python (unit tested) |
| Testing | pytest |

## ⚠️ Data Disclaimer

This prototype uses a **manually curated and dated dataset** collected from
publicly available official sources. Interest rates, fees, and loan terms are
subject to change. Always verify directly with the lender before making
financial decisions.

Where information was not available from the source, it is marked as
**"Not Available"** rather than assumed to be zero.

## 🎯 SDG Alignment

- **SDG 4 — Quality Education**: Supporting informed access to education financing
- **SDG 10 — Reduced Inequalities**: Improving access to understandable financial information

## 📈 PML Roadmap

| Phase | PML Level | Status |
|-------|-----------|--------|
| Problem Research, Architecture, Working Prototype | PML 1–3 | ✅ Current |
| Real Data, User Testing, Research Paper | PML 4–5 | 🔜 Planned |
| Live MVP, Partnerships, Publication | PML 6–9 | 📋 Future |

## 📄 License

This project is developed for educational and research purposes as part of
a university Project Expo competition.

---

*This platform provides information for educational purposes and is not financial advice.*
