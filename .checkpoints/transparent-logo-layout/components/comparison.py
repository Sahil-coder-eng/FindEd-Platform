"""
Comparison Table Component
==========================
Renders styled comparison tables for lenders and scenarios.
"""

import streamlit as st
import pandas as pd


def render_comparison_table(comparison_df: pd.DataFrame):
    """
    Render a styled comparison table.

    Parameters
    ----------
    comparison_df : pd.DataFrame
        DataFrame with lender comparison data.
    """
    # Format currency columns
    currency_cols = [
        col for col in comparison_df.columns
        if "(₹)" in col
    ]

    styled_df = comparison_df.copy()
    for col in currency_cols:
        styled_df[col] = styled_df[col].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lender": st.column_config.TextColumn("🏦 Lender", width="medium"),
            "Interest Rate (%)": st.column_config.TextColumn("📊 Rate (%)", width="small"),
            "Monthly EMI (₹)": st.column_config.TextColumn("💰 EMI/month", width="medium"),
            "Total Interest (₹)": st.column_config.TextColumn("📈 Total Interest", width="medium"),
            "Total Repayment (₹)": st.column_config.TextColumn("💳 Total Repayment", width="medium"),
        },
    )


def render_scenario_table(scenario_df: pd.DataFrame):
    """
    Render a scenario comparison table with highlights.

    Parameters
    ----------
    scenario_df : pd.DataFrame
        Output of compare_scenarios().
    """
    styled_df = scenario_df.copy()

    # Format currency columns
    for col in styled_df.columns:
        if "(₹)" in col:
            styled_df[col] = styled_df[col].apply(lambda x: f"₹{x:,.0f}")

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
    )

    # Show key insights
    if len(scenario_df) >= 2:
        min_emi_idx = scenario_df["Monthly EMI (₹)"].idxmin()
        min_interest_idx = scenario_df["Total Interest (₹)"].idxmin()

        col1, col2 = st.columns(2)
        with col1:
            st.info(
                f"📉 **Lowest EMI**: {scenario_df.loc[min_emi_idx, 'Scenario']} "
                f"at ₹{scenario_df.loc[min_emi_idx, 'Monthly EMI (₹)']:,.0f}/month"
            )
        with col2:
            st.info(
                f"💡 **Lowest Total Interest**: {scenario_df.loc[min_interest_idx, 'Scenario']} "
                f"at ₹{scenario_df.loc[min_interest_idx, 'Total Interest (₹)']:,.0f}"
            )

        if min_emi_idx != min_interest_idx:
            st.caption(
                "⚖️ *Note: The option with the lowest EMI is not the same as the one with the "
                "lowest total interest. A longer tenure reduces monthly payments but increases "
                "the total amount paid. This is a personal tradeoff, not a universal recommendation.*"
            )


def build_lender_comparison_df(lenders: list, results: list) -> pd.DataFrame:
    """
    Build a unified comparison DataFrame from lenders and their calculated results.

    Parameters
    ----------
    lenders : list[dict]
        Lender data from dataset.
    results : list[dict]
        Calculated EMI results for each lender.

    Returns
    -------
    pd.DataFrame
    """
    rows = []
    for lender, result in zip(lenders, results):
        rows.append({
            "Lender": lender.get("lender_name", "Unknown"),
            "Interest Rate (%)": f"{lender.get('interest_rate_min', 'N/A')}–{lender.get('interest_rate_max', 'N/A')}",
            "Monthly EMI (₹)": result["emi"],
            "Total Interest (₹)": result["total_interest"],
            "Total Repayment (₹)": result["total_payment"],
            "Processing Fee": lender.get("processing_fee", "Not Available"),
            "Moratorium (months)": lender.get("moratorium_months", "N/A"),
        })
    return pd.DataFrame(rows)
