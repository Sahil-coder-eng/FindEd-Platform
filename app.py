"""
Education Loan Comparison & Student Planning Platform
=====================================================
A transparent education-financing decision-support system that helps
students and parents compare education loans with clarity.

This is the main Streamlit application entry point.

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

# ── Calculation imports ─────────────────────────────────────────────
from calculations.emi import calculate_emi
from calculations.repayment import generate_amortization_schedule, get_yearly_summary
from calculations.moratorium import calculate_moratorium_impact
from calculations.total_cost import calculate_total_cost
from calculations.scenarios import compare_scenarios, find_scenario_differences
from calculations.sensitivity import rate_sensitivity, tenure_sensitivity
from calculations.education_cost import (
    estimate_education_cost, convert_currency, currency_sensitivity,
)

# ── Component imports ───────────────────────────────────────────────
from components.loan_card import render_loan_card, render_source_badge, _format_amount
from components.charts import (
    plot_emi_comparison, plot_amortization_breakdown, plot_principal_decline,
    plot_rate_sensitivity, plot_tenure_sensitivity, plot_cost_breakdown,
    plot_moratorium_timeline, plot_scenario_comparison, plot_currency_sensitivity,
)
from components.comparison import (
    render_comparison_table, render_scenario_table, build_lender_comparison_df,
)
from components.destination_updates import (
    render_updates, get_available_countries, get_available_categories,
)
from components.explainers import (
    explain_emi, explain_amortization, explain_moratorium,
    explain_total_cost, explain_sensitivity, explain_currency,
)

# ── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Find Ed — Education Loan Comparison Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Apple Design System ─────────────────────────────────────── */
    /* Token references:
       primary: #0066cc  |  primary-on-dark: #2997ff
       ink: #1d1d1f      |  body-muted: #cccccc
       canvas: #ffffff   |  canvas-parchment: #f5f5f7
       surface-tile-1: #272729  |  surface-black: #000000
       hairline: #e0e0e0 |  divider-soft: #f0f0f0
    */

    /* SF Pro → Inter substitute with Apple-matching tracking */
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,600;0,14..32,700;1,14..32,400&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: "SF Pro Text", "SF Pro Display", system-ui, -apple-system,
                     BlinkMacSystemFont, "Inter", sans-serif !important;
        background-color: #ffffff !important;
        color: #1d1d1f !important;
        -webkit-font-smoothing: antialiased;
    }

    /* ── Hide Streamlit chrome ───────────────────────────────────── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stToolbar"] { display: none; }
    [data-testid="stDecoration"] { display: none; }

    /* ── Sidebar ─────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0f 0%, #111118 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
        min-width: 330px !important;
        max-width: 330px !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f5f5f7 !important;
    }
    /* Hide the default radio buttons label and circle */
    section[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 6px !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 4px 6px !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 17px !important;
        font-weight: 500 !important;
        letter-spacing: -0.2px !important;
        line-height: 1.4 !important;
        color: #b0b0c2 !important;
        padding: 13px 18px !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all 0.16s ease !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin-bottom: 2px !important;
        border: 1px solid transparent !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
        transform: translateX(3px) !important;
    }
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 17px !important;
        font-weight: 500 !important;
        color: inherit !important;
        margin: 0 !important;
    }
    /* nav radio selected state */
    section[data-testid="stSidebar"] .stRadio label:has(input:checked),
    section[data-testid="stSidebar"] .stRadio label[aria-checked="true"],
    section[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div label {
        background: rgba(41, 151, 255, 0.18) !important;
        color: #38bdf8 !important;
        font-weight: 600 !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        box-shadow: 0 2px 12px rgba(41, 151, 255, 0.15) !important;
    }
    section[data-testid="stSidebar"] .stRadio label:has(input:checked) p,
    section[data-testid="stSidebar"] .stRadio label[aria-checked="true"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    /* hide the actual radio dot and circles */
    section[data-testid="stSidebar"] .stRadio label > div:first-of-type {
        display: none !important;
    }
    section[data-testid="stSidebar"] .stRadio input[type="radio"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* ── Main canvas ─────────────────────────────────────────────── */
    .main .block-container {
        padding-top: 48px !important;
        padding-left: 48px !important;
        padding-right: 48px !important;
        max-width: 1100px !important;
        background-color: #ffffff !important;
    }

    /* ── Apple hero title ────────────────────────────────────────── */
    /* typography.display-lg: 40px / 600 / lh 1.10 / ls 0 */
    .hero-title {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 40px;
        font-weight: 600;
        line-height: 1.10;
        letter-spacing: 0px;
        color: #1d1d1f;
        margin: 0 0 16px 0;
        background: none !important;
        -webkit-background-clip: unset !important;
        -webkit-text-fill-color: #1d1d1f !important;
    }

    /* typography.lead: 28px / 400 / lh 1.14 / ls 0.196px */
    .hero-subtitle {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 21px;
        font-weight: 400;
        line-height: 1.47;
        letter-spacing: -0.374px;
        color: #7a7a7a;
        max-width: 700px;
        margin-bottom: 32px;
    }

    /* ── Section headers ─────────────────────────────────────────── */
    /* typography.tagline: 21px / 600 / lh 1.19 / ls 0.231px */
    .section-header {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 21px;
        font-weight: 600;
        line-height: 1.19;
        letter-spacing: 0.231px;
        color: #1d1d1f;
        margin: 48px 0 16px 0;
        padding-bottom: 0;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 12px;
        background: none;
    }

    /* ── Metric cards ────────────────────────────────────────────── */
    /* store-utility-card: white bg, 1px hairline, rounded 18px, pad 24px */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 18px;
        padding: 24px;
        text-align: left;
        margin-bottom: 12px;
    }
    .metric-value {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 34px;
        font-weight: 600;
        line-height: 1.47;
        letter-spacing: -0.374px;
        color: #1d1d1f;
    }
    .metric-label {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 14px;
        font-weight: 400;
        line-height: 1.43;
        letter-spacing: -0.224px;
        color: #7a7a7a;
        margin-top: 4px;
    }

    /* ── Feature cards ───────────────────────────────────────────── */
    /* store-utility-card pattern */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 12px;
        transition: transform 0.18s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    .feature-card:hover {
        transform: scale(0.99);
    }
    .feature-card h4 {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.374px;
        color: #1d1d1f !important;
    }
    .feature-card p {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 14px;
        font-weight: 400;
        letter-spacing: -0.224px;
        color: #7a7a7a !important;
    }

    /* ── Disclaimer / data note ──────────────────────────────────── */
    .disclaimer {
        background: #f5f5f7;
        border: none;
        border-radius: 11px;
        padding: 14px 18px;
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 12px;
        font-weight: 400;
        line-height: 1.0;
        letter-spacing: -0.12px;
        color: #7a7a7a;
        margin: 16px 0;
    }

    /* ── Streamlit native widget overrides ───────────────────────── */
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f5f5f7;
        border-radius: 9999px;
        padding: 4px;
        border: none;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 9999px;
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 14px;
        font-weight: 400;
        letter-spacing: -0.224px;
        color: #1d1d1f;
        padding: 8px 16px;
        border: none;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff !important;
        color: #0066cc !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 24px;
    }

    /* Buttons — pill shape */
    .stButton > button {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 17px !important;
        font-weight: 400 !important;
        line-height: 1.47 !important;
        letter-spacing: -0.374px !important;
        color: #ffffff !important;
        background-color: #0066cc !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 11px 22px !important;
        cursor: pointer;
        transition: transform 0.12s ease;
    }
    .stButton > button:active {
        transform: scale(0.95) !important;
    }
    .stButton > button:focus {
        outline: 2px solid #0071e3 !important;
        outline-offset: 2px !important;
    }

    /* Inputs */
    .stNumberInput input, .stTextInput input, .stSelectbox select {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 17px !important;
        letter-spacing: -0.374px !important;
        color: #1d1d1f !important;
        background: #ffffff !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #0066cc !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(0,102,204,0.15) !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        background: #ffffff !important;
    }

    /* Radio */
    .stRadio label {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 17px !important;
        letter-spacing: -0.374px !important;
        color: #1d1d1f !important;
    }

    /* Slider */
    .stSlider [data-testid="stSlider"] {
        accent-color: #0066cc;
    }

    /* Native st.metric */
    [data-testid="metric-container"] {
        background: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        letter-spacing: -0.224px !important;
        color: #7a7a7a !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 28px !important;
        font-weight: 600 !important;
        letter-spacing: -0.374px !important;
        color: #1d1d1f !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 14px !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #e0e0e0 !important;
        border-radius: 11px !important;
        overflow: hidden !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid #e0e0e0 !important;
        border-radius: 11px !important;
        background: #fafafc !important;
    }

    /* Info / warning / success boxes */
    [data-testid="stInfo"], .stInfo {
        background: #f5f5f7 !important;
        border: none !important;
        border-left: 3px solid #0066cc !important;
        border-radius: 0 8px 8px 0 !important;
        color: #1d1d1f !important;
    }
    [data-testid="stWarning"], .stWarning {
        background: #f5f5f7 !important;
        border: none !important;
        border-left: 3px solid #ff6b00 !important;
        border-radius: 0 8px 8px 0 !important;
        color: #1d1d1f !important;
    }

    /* Caption */
    .stCaption, [data-testid="stCaptionContainer"] {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 12px !important;
        font-weight: 400 !important;
        letter-spacing: -0.12px !important;
        color: #7a7a7a !important;
    }

    /* Multiselect */
    [data-baseweb="tag"] {
        background-color: #0066cc !important;
        border-radius: 9999px !important;
        color: #ffffff !important;
    }

    /* Markdown body text */
    .stMarkdown p, .stMarkdown li {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 17px !important;
        font-weight: 400 !important;
        line-height: 1.47 !important;
        letter-spacing: -0.374px !important;
        color: #1d1d1f !important;
    }
    .stMarkdown h1, .stMarkdown h2 {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 34px !important;
        font-weight: 600 !important;
        letter-spacing: -0.374px !important;
        color: #1d1d1f !important;
    }
    .stMarkdown h3 {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 21px !important;
        font-weight: 600 !important;
        letter-spacing: 0.231px !important;
        color: #1d1d1f !important;
    }
    .stMarkdown a {
        color: #0066cc !important;
        text-decoration: none !important;
    }
    .stMarkdown a:hover {
        text-decoration: underline !important;
    }

    /* Sidebar logo block */
    .sidebar-logo {
        padding: 28px 20px 22px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 16px;
        display: flex;
        align-items: flex-start;
        gap: 14px;
    }
    .sidebar-logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #1a6fff 0%, #0a3fd4 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 16px rgba(26,111,255,0.45);
        flex-shrink: 0;
    }
    .sidebar-logo-text h2 {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin: 0 0 4px 0;
        line-height: 1;
    }
    .sidebar-logo-text p {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 12px;
        font-weight: 400;
        letter-spacing: -0.1px;
        color: #9da3b4 !important;
        margin: 0;
        line-height: 1.35;
        text-transform: none !important;
    }

    /* Nav section label */
    .sidebar-nav-label {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.9px;
        color: #5a5a70;
        text-transform: uppercase;
        padding: 10px 20px 6px 20px;
        margin-top: 6px;
    }

    /* ── Destination Updates Card Styles ─────────────────────────── */
    .destination-update-card {
        background: linear-gradient(145deg, #1e2533 0%, #131722 100%) !important;
        border-radius: 14px !important;
        padding: 22px 24px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.22) !important;
    }
    .destination-update-headline,
    .destination-update-card h4 {
        color: #ffffff !important;
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 19px !important;
        font-weight: 700 !important;
        line-height: 1.35 !important;
        letter-spacing: -0.2px !important;
        margin: 0 0 10px 0 !important;
    }
    .destination-update-body,
    .destination-update-card p,
    .destination-update-card .card-text {
        color: #e2e8f0 !important;
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        letter-spacing: -0.1px !important;
        margin: 0 0 16px 0 !important;
    }
    .destination-update-card .destination-update-meta,
    .destination-update-card .destination-update-source {
        color: #94a3b8 !important;
        font-size: 13px !important;
    }
    .destination-update-link {
        color: #38bdf8 !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        text-decoration: none !important;
    }
    .destination-update-link:hover {
        text-decoration: underline !important;
    }

    /* Country info card — dark tile variant */
    .country-card {
        background: #272729;
        border-radius: 0;
        padding: 48px;
        margin: 24px 0;
        color: #ffffff;
    }
    .country-card h3 {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 40px;
        font-weight: 600;
        line-height: 1.10;
        letter-spacing: 0;
        color: #ffffff;
        margin: 8px 0 4px 0;
    }
    .country-card p {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 17px;
        font-weight: 400;
        letter-spacing: -0.374px;
        color: #cccccc;
        margin: 0;
    }

    /* Scenario / spread card */
    .insight-card {
        background: #f5f5f7;
        border-radius: 18px;
        padding: 20px 24px;
        margin: 16px 0;
        border: none;
    }
    .insight-card h4 {
        font-family: "SF Pro Display", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 21px;
        font-weight: 600;
        letter-spacing: 0.231px;
        color: #1d1d1f;
        margin: 0 0 6px 0;
    }
    .insight-card p {
        font-family: "SF Pro Text", system-ui, -apple-system, "Inter", sans-serif;
        font-size: 17px;
        font-weight: 400;
        letter-spacing: -0.374px;
        color: #7a7a7a;
        margin: 0;
    }

    /* Divider */
    hr {
        border: none !important;
        border-top: 1px solid #e0e0e0 !important;
        margin: 32px 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data Loading ────────────────────────────────────────────────────
@st.cache_data
def load_lender_data():
    """Load lender dataset from CSV."""
    csv_path = Path(__file__).parent / "data" / "loans.csv"
    df = pd.read_csv(csv_path)
    return df


@st.cache_data
def load_country_data():
    """Load country reference data."""
    json_path = Path(__file__).parent / "data" / "countries.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Sidebar Navigation ─────────────────────────────────────────────
st.sidebar.markdown(
    """
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">
            <svg width="28" height="28" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Graduation cap -->
                <path d="M13 5L2 10.5L13 16L24 10.5L13 5Z" fill="white" opacity="0.95"/>
                <path d="M7 13v5c0 2 2.686 4 6 4s6-2 6-4v-5L13 16 7 13Z" fill="white" opacity="0.7"/>
                <line x1="22" y1="10.5" x2="22" y2="17" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
                <circle cx="22" cy="17.5" r="1.5" fill="white" opacity="0.8"/>
            </svg>
        </div>
        <div class="sidebar-logo-text">
            <h2>Find Ed</h2>
            <p>Your education Journey, funded from A to Z</p>
        </div>
    </div>
    <div class="sidebar-nav-label">Navigation</div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "💰 Education Cost Estimator",
        "🏦 Loan Comparison",
        "📊 Detailed Analysis",
        "🔄 Scenario Simulator",
        "📈 Sensitivity Analysis",
        "🌍 International Education",
        "📰 Destination Updates",
        "ℹ️ About & Sources",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown(
    """
    <div style="margin: 20px; padding: 14px 16px; background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;
                font-size: 11px; letter-spacing: 0.1px;
                color: #5a5a6e; line-height: 1.6; margin-top: 16px;">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style="margin-right:5px;vertical-align:middle;">
            <circle cx="6" cy="6" r="5" stroke="#5a5a6e" stroke-width="1.2"/>
            <path d="M6 5v4M6 3.5v.5" stroke="#5a5a6e" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        Manually curated dataset from public sources. Always verify with the lender.
    </div>
    """,
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    # Hero section
    st.markdown('<p class="hero-title">Compare Education Loans<br/>with Clarity</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "A transparent decision-support platform that helps students and parents "
        "understand the true cost of education loans — beyond just the interest rate."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Quick EMI calculator
    st.markdown('<div class="section-header">Quick EMI Calculator</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        quick_principal = st.number_input(
            "Loan Amount (₹)", min_value=10000, max_value=100000000,
            value=1000000, step=50000, key="home_principal",
            help="The total amount you want to borrow.",
        )
    with col2:
        quick_rate = st.number_input(
            "Interest Rate (%)", min_value=0.1, max_value=30.0,
            value=9.0, step=0.25, key="home_rate",
            help="Annual interest rate offered by the lender.",
        )
    with col3:
        quick_tenure = st.number_input(
            "Tenure (Years)", min_value=1, max_value=30,
            value=10, step=1, key="home_tenure",
            help="Number of years to repay the loan.",
        )

    result = calculate_emi(quick_principal, quick_rate, quick_tenure)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Monthly EMI</div>'
            f'<div class="metric-value">₹{result["emi"]:,.0f}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Total Interest</div>'
            f'<div class="metric-value">₹{result["total_interest"]:,.0f}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Total Repayment</div>'
            f'<div class="metric-value">₹{result["total_payment"]:,.0f}</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">Interest / Principal</div>'
            f'<div class="metric-value">{result["interest_to_principal_ratio"]:.1%}</div></div>',
            unsafe_allow_html=True,
        )

    explain_emi()

    # Feature overview
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">What This Platform Offers</div>', unsafe_allow_html=True)

    features = [
        ("🏦", "Multi-Lender Comparison", "Compare EMI, interest, and total cost across 8+ lenders side-by-side."),
        ("📊", "Amortization Schedule", "Month-by-month breakdown of how each EMI splits between interest and principal."),
        ("⏸️", "Moratorium Simulator", "Understand how the study/grace period affects your total borrowing cost."),
        ("💰", "True Cost Analysis", "See the complete financial outflow including fees, not just the interest rate."),
        ("🔄", "Scenario Analysis", "Compare different loan configurations to find what works for your budget."),
        ("📈", "Sensitivity Analysis", "Visualize how rate and tenure changes affect your repayment."),
        ("🌍", "International Education", "Currency conversion and exchange-rate impact for studying abroad."),
        ("📰", "Destination Updates", "Relevant education, visa, and work-permit information by country."),
    ]

    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(features):
                icon, title, desc = features[i + j]
                with col:
                    st.markdown(
                        f"""
                        <div class="feature-card">
                            <span style="font-size: 1.3rem;">{icon}</span>
                            <h4>{title}</h4>
                            <p>{desc}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# ════════════════════════════════════════════════════════════════════
# PAGE: EDUCATION COST ESTIMATOR
# ════════════════════════════════════════════════════════════════════
elif page == "💰 Education Cost Estimator":
    st.markdown('<p class="hero-title">Education Cost Estimator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "Estimate your total education expenses and determine how much financing you need."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-header">Annual Expenses</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            tuition = st.number_input("Tuition Fee (₹/year)", min_value=0, value=200000, step=10000)
            hostel = st.number_input("Hostel / Accommodation (₹/year)", min_value=0, value=80000, step=5000)
            books = st.number_input("Books & Materials (₹/year)", min_value=0, value=15000, step=1000)
        with c2:
            living = st.number_input("Living Expenses (₹/year)", min_value=0, value=60000, step=5000)
            travel = st.number_input("Travel (₹ total)", min_value=0, value=20000, step=5000)
            other = st.number_input("Other Expenses (₹/year)", min_value=0, value=10000, step=1000)

        st.markdown('<div class="section-header">📅 Course Duration & Funds</div>', unsafe_allow_html=True)

        c3, c4, c5 = st.columns(3)
        with c3:
            num_years = st.number_input("Course Duration (years)", min_value=1, max_value=7, value=4)
        with c4:
            scholarship = st.number_input("Scholarship (₹ total)", min_value=0, value=0, step=10000)
        with c5:
            family_contribution = st.number_input("Family Contribution (₹)", min_value=0, value=200000, step=10000)

    # Calculate
    cost_result = estimate_education_cost(
        tuition=tuition, hostel=hostel, books=books,
        travel=travel, living=living, other=other,
        num_years=num_years, scholarship=scholarship,
        family_contribution=family_contribution,
    )

    with col_right:
        st.markdown('<div class="section-header">Summary</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Annual Education Cost</div>
                <div class="metric-value">₹{cost_result['annual_breakdown']['Annual Total']:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Education Cost ({num_years} years)</div>
                <div class="metric-value">₹{cost_result['total_education_cost']:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Available Funds</div>
                <div class="metric-value" style="color: #0066cc;">₹{cost_result['available_funds']:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="metric-card" style="border: 2px solid #0066cc;">
                <div class="metric-label">Estimated Financing Required</div>
                <div class="metric-value">₹{cost_result['financing_required']:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Breakdown table
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Detailed Breakdown</div>', unsafe_allow_html=True)

    breakdown_data = {
        "Category": list(cost_result["annual_breakdown"].keys())[:-1] + ["Travel (Total)"],
        "Annual (₹)": [f"₹{v:,.0f}" for v in list(cost_result["annual_breakdown"].values())[:-1]] + [f"₹{travel:,.0f}"],
        f"Total ({num_years} yrs) (₹)": [
            f"₹{v * num_years:,.0f}" for v in list(cost_result["annual_breakdown"].values())[:-1]
        ] + [f"₹{travel:,.0f}"],
    }
    st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True, hide_index=True)

    st.info(
        f"💡 **Next step:** Use the financing requirement of **₹{cost_result['financing_required']:,.0f}** "
        f"in the **Loan Comparison** page to find suitable loan options."
    )


# ════════════════════════════════════════════════════════════════════
# PAGE: LOAN COMPARISON
# ════════════════════════════════════════════════════════════════════
elif page == "🏦 Loan Comparison":
    st.markdown('<p class="hero-title">Loan Comparison</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "Compare education loans across multiple lenders — see how different rates "
        "affect your EMI, total interest, and total repayment."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Load data
    lender_df = load_lender_data()

    # User inputs
    st.markdown('<div class="section-header">Your Loan Requirement</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        loan_amount = st.number_input(
            "Loan Amount (₹)", min_value=10000, max_value=100000000,
            value=1000000, step=50000, key="compare_principal",
        )
    with c2:
        loan_tenure = st.number_input(
            "Repayment Tenure (Years)", min_value=1, max_value=30,
            value=10, step=1, key="compare_tenure",
        )

    rate_type = st.radio(
        "Calculate using:", ["Minimum rate", "Maximum rate", "Average rate"],
        horizontal=True,
        help="Lenders offer a range of rates. Choose which to use for comparison.",
    )

    # Calculate for all lenders
    lenders_list = []
    results_list = []

    for _, row in lender_df.iterrows():
        lender_dict = row.to_dict()

        if rate_type == "Minimum rate":
            use_rate = row["interest_rate_min"]
        elif rate_type == "Maximum rate":
            use_rate = row["interest_rate_max"]
        else:
            use_rate = (row["interest_rate_min"] + row["interest_rate_max"]) / 2

        emi_result = calculate_emi(loan_amount, use_rate, loan_tenure)
        lenders_list.append(lender_dict)
        results_list.append(emi_result)

    # Comparison table
    st.markdown('<div class="section-header">Comparison Results</div>', unsafe_allow_html=True)

    comparison_df = build_lender_comparison_df(lenders_list, results_list)
    render_comparison_table(comparison_df)

    # Visual chart
    st.plotly_chart(plot_emi_comparison(comparison_df), use_container_width=True)

    # Lender cards
    st.markdown('<div class="section-header">Lender Details</div>', unsafe_allow_html=True)

    for i in range(0, len(lenders_list), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(lenders_list):
                with col:
                    render_loan_card(lenders_list[idx], results_list[idx])
                    render_source_badge(lenders_list[idx])

    st.markdown(
        '<div class="disclaimer">'
        "📋 This comparison is based on a curated dataset. Actual rates depend on your credit profile, "
        "collateral, and the lender's current offers. Always verify directly with the lender."
        "</div>",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════
# PAGE: DETAILED ANALYSIS
# ════════════════════════════════════════════════════════════════════
elif page == "📊 Detailed Analysis":
    st.markdown('<p class="hero-title">Detailed Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "Deep dive into EMI breakdown, amortization, moratorium impact, and total cost."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Inputs
    c1, c2, c3 = st.columns(3)
    with c1:
        d_principal = st.number_input(
            "Loan Amount (₹)", min_value=10000, max_value=100000000,
            value=1000000, step=50000, key="detail_principal",
        )
    with c2:
        d_rate = st.number_input(
            "Interest Rate (%)", min_value=0.1, max_value=30.0,
            value=9.0, step=0.25, key="detail_rate",
        )
    with c3:
        d_tenure = st.number_input(
            "Tenure (Years)", min_value=1, max_value=30,
            value=10, step=1, key="detail_tenure",
        )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📐 EMI Breakdown", "📊 Amortization Schedule",
        "⏸️ Moratorium Simulator", "💰 Total Cost Analysis",
    ])

    # ── Tab 1: EMI Breakdown ────────────────────────────────────────
    with tab1:
        emi_result = calculate_emi(d_principal, d_rate, d_tenure)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Monthly EMI", f"₹{emi_result['emi']:,.0f}")
        with c2:
            st.metric("Total Interest", f"₹{emi_result['total_interest']:,.0f}")
        with c3:
            st.metric("Total Repayment", f"₹{emi_result['total_payment']:,.0f}")

        st.markdown("<br/>", unsafe_allow_html=True)

        # Cost pie chart
        cost_components = {
            "Principal": d_principal,
            "Interest": emi_result["total_interest"],
        }
        st.plotly_chart(plot_cost_breakdown(cost_components), use_container_width=True)

        explain_emi()

    # ── Tab 2: Amortization ─────────────────────────────────────────
    with tab2:
        schedule = generate_amortization_schedule(d_principal, d_rate, d_tenure)

        # Charts
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                plot_amortization_breakdown(schedule), use_container_width=True,
            )
        with c2:
            st.plotly_chart(
                plot_principal_decline(schedule), use_container_width=True,
            )

        # Yearly summary
        st.markdown('<div class="section-header">Yearly Summary</div>', unsafe_allow_html=True)
        yearly = get_yearly_summary(schedule)
        yearly_display = yearly.copy()
        for col in ["total_emi", "total_interest", "total_principal", "closing_principal"]:
            yearly_display[col] = yearly_display[col].apply(lambda x: f"₹{x:,.0f}")
        yearly_display.columns = ["Year", "Total EMI", "Total Interest", "Total Principal", "Balance"]
        st.dataframe(yearly_display, use_container_width=True, hide_index=True)

        # Full schedule (collapsed)
        with st.expander("📋 View Full Monthly Schedule"):
            schedule_display = schedule.copy()
            for col in ["opening_principal", "emi", "interest_component", "principal_component", "closing_principal"]:
                schedule_display[col] = schedule_display[col].apply(lambda x: f"₹{x:,.0f}")
            schedule_display.columns = [
                "Month", "Opening Balance", "EMI", "Interest", "Principal", "Closing Balance"
            ]
            st.dataframe(schedule_display, use_container_width=True, hide_index=True, height=400)

        explain_amortization()

    # ── Tab 3: Moratorium ───────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Moratorium Configuration</div>', unsafe_allow_html=True)

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            course_months = st.number_input(
                "Course Duration (months)", min_value=0, max_value=84,
                value=48, step=6, key="mora_course",
                help="How long is your course?",
            )
        with mc2:
            grace_months = st.number_input(
                "Grace Period (months)", min_value=0, max_value=24,
                value=6, step=3, key="mora_grace",
                help="Post-course grace period before EMI starts.",
            )
        with mc3:
            interest_treatment = st.selectbox(
                "Interest During Moratorium",
                ["capitalized", "paid_during"],
                format_func=lambda x: "Interest Capitalized (added to principal)" if x == "capitalized"
                                      else "Interest Paid Monthly During Moratorium",
                key="mora_treatment",
            )

        if course_months + grace_months > 0:
            mora_result = calculate_moratorium_impact(
                d_principal, d_rate, course_months, grace_months,
                d_tenure, interest_treatment,
            )

            # Timeline
            st.plotly_chart(
                plot_moratorium_timeline(mora_result["timeline"]),
                use_container_width=True,
            )

            # Metrics
            st.markdown('<div class="section-header">Moratorium Impact</div>', unsafe_allow_html=True)

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric(
                    "EMI Without Moratorium",
                    f"₹{mora_result['emi_without_moratorium']:,.0f}",
                )
            with mc2:
                st.metric(
                    "EMI With Moratorium",
                    f"₹{mora_result['emi_with_moratorium']:,.0f}",
                    delta=f"₹{mora_result['emi_increase']:,.0f}" if mora_result['emi_increase'] > 0 else None,
                    delta_color="inverse",
                )
            with mc3:
                st.metric(
                    "Additional Cost",
                    f"₹{mora_result['additional_cost_due_to_moratorium']:,.0f}",
                )

            # Detail breakdown
            detail_col1, detail_col2 = st.columns(2)
            with detail_col1:
                st.markdown("**Before Moratorium:**")
                st.write(f"- Original Principal: ₹{d_principal:,.0f}")
                st.write(f"- EMI: ₹{mora_result['emi_without_moratorium']:,.0f}")
                st.write(f"- Total Repayment: ₹{mora_result['total_cost_without_moratorium']:,.0f}")

            with detail_col2:
                st.markdown("**After Moratorium:**")
                st.write(f"- Effective Principal: ₹{mora_result['effective_principal_at_repayment']:,.0f}")
                if mora_result['principal_increase'] > 0:
                    st.write(f"- Principal Increase: ₹{mora_result['principal_increase']:,.0f}")
                st.write(f"- Moratorium Interest: ₹{mora_result['total_moratorium_interest']:,.0f}")
                st.write(f"- EMI: ₹{mora_result['emi_with_moratorium']:,.0f}")
                st.write(f"- Total Cost: ₹{mora_result['total_cost_with_moratorium']:,.0f}")

            if interest_treatment == "capitalized":
                st.warning(
                    "⚠️ With interest capitalization, the accrued interest is added to your principal. "
                    f"Your effective principal increases from ₹{d_principal:,.0f} to "
                    f"₹{mora_result['effective_principal_at_repayment']:,.0f}, resulting in higher EMIs."
                )

        else:
            st.info("Set a course duration or grace period above to see moratorium impact.")

        explain_moratorium()

    # ── Tab 4: Total Cost ───────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">Total Cost Configuration</div>', unsafe_allow_html=True)

        tc1, tc2 = st.columns(2)
        with tc1:
            proc_fee_pct = st.number_input(
                "Processing Fee (%)", min_value=0.0, max_value=5.0,
                value=0.0, step=0.25, key="tc_proc_pct",
                help="Enter 0 if not known.",
            )
        with tc2:
            doc_charges = st.number_input(
                "Documentation Charges (₹)", min_value=0, value=0, step=500,
                key="tc_doc",
            )

        other_charges = {}
        if doc_charges > 0:
            other_charges["Documentation Charges"] = doc_charges

        tc_result = calculate_total_cost(
            d_principal, d_rate, d_tenure,
            processing_fee_pct=proc_fee_pct if proc_fee_pct > 0 else None,
            other_charges=other_charges if other_charges else None,
        )

        # Summary metrics
        tc_m1, tc_m2, tc_m3 = st.columns(3)
        with tc_m1:
            st.metric("Total EMI Payments", f"₹{tc_result['total_emi_payments']:,.0f}")
        with tc_m2:
            st.metric("Processing Fee", f"₹{tc_result['processing_fee']:,.0f}" if tc_result['processing_fee_status'] == 'included' else "Not Available")
        with tc_m3:
            st.metric("Total Known Cost", f"₹{tc_result['total_known_cost']:,.0f}")

        # Cost breakdown chart
        st.plotly_chart(
            plot_cost_breakdown(tc_result["cost_components"]),
            use_container_width=True,
        )

        # Disclaimer
        st.markdown(
            f'<div class="disclaimer">⚠️ {tc_result["disclaimer"]}</div>',
            unsafe_allow_html=True,
        )

        explain_total_cost()


# ════════════════════════════════════════════════════════════════════
# PAGE: SCENARIO SIMULATOR
# ════════════════════════════════════════════════════════════════════
elif page == "🔄 Scenario Simulator":
    st.markdown('<p class="hero-title">Scenario Simulator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "Compare different loan configurations to understand how principal, rate, and "
        "tenure affect your repayment."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    num_scenarios = st.slider("Number of Scenarios", min_value=2, max_value=4, value=3)

    scenarios = []
    cols = st.columns(num_scenarios)

    for i, col in enumerate(cols):
        with col:
            st.markdown(f"### Scenario {chr(65 + i)}")
            p = st.number_input(
                f"Principal (₹)", min_value=10000, value=1000000,
                step=50000, key=f"sc_p_{i}",
            )
            r = st.number_input(
                f"Rate (%)", min_value=0.1, value=9.0 + i * 0.5,
                step=0.25, key=f"sc_r_{i}",
            )
            t = st.number_input(
                f"Tenure (yrs)", min_value=1, value=max(1, 10 - i * 3),
                step=1, key=f"sc_t_{i}",
            )
            scenarios.append({
                "name": f"Scenario {chr(65 + i)}",
                "principal": p,
                "annual_rate": r,
                "tenure_years": t,
            })

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Comparison Results</div>', unsafe_allow_html=True)

    scenario_df = compare_scenarios(scenarios)
    render_scenario_table(scenario_df)

    # Chart
    st.plotly_chart(plot_scenario_comparison(scenario_df), use_container_width=True)

    # Spreads
    spreads = find_scenario_differences(scenario_df)
    if spreads["interest_spread"] > 0:
        st.markdown(
            f"""
            <div class="insight-card">
                <h4>Key Differences Across Scenarios</h4>
                <p>EMI spread: ₹{spreads['emi_spread']:,.0f}/month &nbsp;&middot;&nbsp;
                    Interest spread: ₹{spreads['interest_spread']:,.0f} &nbsp;&middot;&nbsp;
                    Repayment spread: ₹{spreads['repayment_spread']:,.0f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════
# PAGE: SENSITIVITY ANALYSIS
# ════════════════════════════════════════════════════════════════════
elif page == "📈 Sensitivity Analysis":
    st.markdown('<p class="hero-title">Sensitivity Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "Visualize how changes in interest rate or tenure affect your loan outcome. "
        "This shows numerical tradeoffs, not recommendations."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    # Common inputs
    sc1, sc2 = st.columns(2)
    with sc1:
        s_principal = st.number_input(
            "Loan Amount (₹)", min_value=10000, max_value=100000000,
            value=1000000, step=50000, key="sens_principal",
        )
    with sc2:
        s_base_rate = st.number_input(
            "Base Interest Rate (%)", min_value=0.1, max_value=30.0,
            value=9.0, step=0.25, key="sens_rate",
        )

    tab_rate, tab_tenure = st.tabs(["📊 Interest Rate Sensitivity", "📅 Tenure Sensitivity"])

    with tab_rate:
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            s_tenure = st.number_input(
                "Fixed Tenure (Years)", min_value=1, max_value=30,
                value=10, step=1, key="sens_tenure_fixed",
            )
        with rc2:
            rate_min = st.number_input("Min Rate (%)", value=7.0, step=0.5, key="s_rate_min")
        with rc3:
            rate_max = st.number_input("Max Rate (%)", value=14.0, step=0.5, key="s_rate_max")

        rate_df = rate_sensitivity(s_principal, s_tenure, rate_min, rate_max, 0.5)
        st.plotly_chart(plot_rate_sensitivity(rate_df), use_container_width=True)

        st.dataframe(
            rate_df.style.format({
                "Monthly EMI (₹)": "₹{:,.0f}",
                "Total Interest (₹)": "₹{:,.0f}",
                "Total Repayment (₹)": "₹{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with tab_tenure:
        st.markdown("Select tenures to compare:")
        tenure_options = st.multiselect(
            "Tenure Options (years)",
            options=[1, 2, 3, 5, 7, 10, 12, 15, 20],
            default=[3, 5, 7, 10, 15],
            key="sens_tenure_opts",
        )

        if tenure_options:
            tenure_df = tenure_sensitivity(s_principal, s_base_rate, sorted(tenure_options))
            st.plotly_chart(plot_tenure_sensitivity(tenure_df), use_container_width=True)

            st.dataframe(
                tenure_df.style.format({
                    "Monthly EMI (₹)": "₹{:,.0f}",
                    "Total Interest (₹)": "₹{:,.0f}",
                    "Total Repayment (₹)": "₹{:,.0f}",
                    "Interest Saved vs Max": "₹{:,.0f}",
                }),
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "⚖️ *A shorter tenure means higher monthly payments but significantly less "
                "total interest. A longer tenure eases monthly burden but costs more overall. "
                "This is a personal tradeoff based on your monthly budget.*"
            )

    explain_sensitivity()


# ════════════════════════════════════════════════════════════════════
# PAGE: INTERNATIONAL EDUCATION
# ════════════════════════════════════════════════════════════════════
elif page == "🌍 International Education":
    st.markdown('<p class="hero-title">International Education</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "Plan your international education financing with currency conversion "
        "and exchange-rate impact analysis."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    countries = load_country_data()
    country_names = [c for c in countries.keys() if c != "India"]

    selected_country = st.selectbox(
        "🌍 Target Country",
        country_names,
        key="intl_country",
    )

    country_info = countries[selected_country]

    # Country info card
    st.markdown(
        f"""
        <div class="country-card">
            <span style="font-size: 2.5rem; line-height: 1;">{country_info['flag_emoji']}</span>
            <h3>{selected_country}</h3>
            <p>{country_info['currency_code']} ({country_info['currency_symbol']}) &nbsp;&middot;&nbsp; {country_info['avg_tuition_range']}</p>
            <p style="margin-top: 6px; font-size: 14px; letter-spacing: -0.224px; color: #7a7a7a;">
                {', '.join(country_info['popular_courses'])}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_convert, tab_sensitivity_curr = st.tabs(["💱 Currency Converter", "📊 Exchange Rate Sensitivity"])

    with tab_convert:
        cc1, cc2 = st.columns(2)
        with cc1:
            foreign_amount = st.number_input(
                f"Amount in {country_info['currency_code']}",
                min_value=0.0, value=30000.0, step=1000.0,
                key="intl_amount",
            )
        with cc2:
            exchange_rate = st.number_input(
                f"Exchange Rate ({country_info['currency_code']} → INR)",
                min_value=0.01, value=float(country_info['default_exchange_rate_to_inr']),
                step=0.5, key="intl_rate",
                help="You can edit this to use a current rate.",
            )

        conv_result = convert_currency(
            foreign_amount, exchange_rate,
            from_symbol=country_info['currency_symbol'],
            to_symbol="₹",
        )

        st.markdown(
            f"""
            <div class="metric-card" style="margin-top: 16px;">
                <div class="metric-label">{conv_result['display']}</div>
                <div class="metric-value">₹{conv_result['converted_amount']:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="disclaimer">'
            "💱 Exchange rates are user-editable defaults for illustration. "
            "They are not predictions. Always verify current rates from your bank."
            "</div>",
            unsafe_allow_html=True,
        )

        explain_currency()

    with tab_sensitivity_curr:
        var_pct = st.slider(
            "Variation Range (±%)", min_value=2, max_value=25, value=10, key="curr_var",
        )

        sens_data = currency_sensitivity(
            foreign_amount, exchange_rate,
            variation_pct=var_pct, steps=5,
            from_symbol=country_info['currency_symbol'],
            to_symbol="₹",
        )

        st.plotly_chart(plot_currency_sensitivity(sens_data), use_container_width=True)

        # Table
        sens_table = pd.DataFrame(sens_data)
        sens_table_display = sens_table[["rate_change_pct", "exchange_rate", "from_display", "to_display"]].copy()
        sens_table_display.columns = ["Rate Change (%)", "Exchange Rate", "Foreign Amount", "INR Equivalent"]
        st.dataframe(sens_table_display, use_container_width=True, hide_index=True)

        st.caption(
            "📊 *This chart shows how potential exchange-rate movements could affect "
            "the INR cost of your education. These are illustrative scenarios, "
            "not predictions of future rates.*"
        )


# ════════════════════════════════════════════════════════════════════
# PAGE: DESTINATION UPDATES
# ════════════════════════════════════════════════════════════════════
elif page == "📰 Destination Updates":
    st.markdown('<p class="hero-title">Destination Updates</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">'
        "Relevant education, visa, and work-permit updates for popular study destinations."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)

    fc1, fc2 = st.columns(2)
    with fc1:
        available_countries = get_available_countries()
        filter_country = st.selectbox(
            "🌍 Country", ["All"] + available_countries, key="updates_country",
        )
    with fc2:
        available_categories = get_available_categories()
        filter_category = st.selectbox(
            "📂 Category", ["All"] + available_categories, key="updates_category",
        )

    render_updates(
        country=filter_country if filter_country != "All" else None,
        category=filter_category if filter_category != "All" else None,
    )


# ════════════════════════════════════════════════════════════════════
# PAGE: ABOUT & SOURCES
# ════════════════════════════════════════════════════════════════════
elif page == "ℹ️ About & Sources":
    st.markdown('<p class="hero-title">About This Platform</p>', unsafe_allow_html=True)

    st.markdown(
        """
        ### 🎯 Purpose

        This is a **transparent education-financing decision-support platform** designed
        to help students and parents understand the true cost of education loans.

        We are **not** simply an EMI calculator. This platform brings together:
        - EMI calculation with full mathematical transparency
        - Multi-lender comparison across documented attributes
        - Repayment schedule visualization
        - Moratorium period impact analysis
        - Total cost estimation including applicable charges
        - Scenario and sensitivity analysis
        - International education cost planning
        - Relevant destination updates

        ### 🔬 Methodology

        This project follows a structured research methodology:

        1. **Problem Identification** → Evidence from credible sources
        2. **Literature Review** → Academic papers, existing platforms
        3. **Research Gap** → What existing solutions don't provide
        4. **Mathematical Model** → Standard reducing-balance EMI formula
        5. **System Architecture** → Modular calculation + presentation layers
        6. **Prototype Development** → Working Streamlit application
        7. **Validation** → Unit tests + cross-validation with known calculators

        ### 🎯 SDG Alignment

        - **SDG 4 — Quality Education**: Supporting informed access to education
          financing for higher/tertiary education.
        - **SDG 10 — Reduced Inequalities**: Improving access to understandable
          financial information for education planning.
        """
    )

    # Data sources table
    st.markdown('<div class="section-header">Data Sources</div>', unsafe_allow_html=True)

    lender_df = load_lender_data()
    source_table = lender_df[["lender_name", "source_url", "last_verified", "notes"]].copy()
    source_table.columns = ["Lender", "Source URL", "Last Verified", "Notes"]
    st.dataframe(source_table, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="disclaimer">
            📋 <strong>Data Disclaimer:</strong> This prototype uses a manually curated and dated
            dataset collected from publicly available official sources. Interest rates, fees, and
            terms are subject to change. Always verify directly with the lender before making
            financial decisions. Where information was not available from the source, it is marked
            as "Not Available" rather than assumed to be zero.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### 🏗️ Technology Stack

        | Component | Technology |
        |-----------|-----------|
        | Frontend | Streamlit 1.35.0 |
        | Language | Python 3.12 |
        | Visualization | Plotly 5.22 |
        | Data | CSV / JSON (curated dataset) |
        | Calculations | Pure Python (tested) |

        ### 📈 PML Roadmap

        | Phase | PML | Status |
        |-------|-----|--------|
        | Problem Research & Architecture | PML 1–3 | ✅ Current |
        | Real Data + User Testing | PML 4–5 | 🔜 Planned |
        | Live MVP + Partnerships | PML 6–9 | 📋 Future |

        ### 👥 Team

        Built by university students as part of a Project Expo competition.

        ---
        *This platform is a research prototype. It provides information for
        educational purposes and is not financial advice.*
        """
    )
