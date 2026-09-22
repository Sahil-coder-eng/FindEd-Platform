"""
Scenario Comparison Engine
==========================
Allows users to define multiple hypothetical loan scenarios and compare
them side-by-side. Each scenario specifies principal, interest rate,
and tenure — the engine calculates all derived metrics for comparison.

This demonstrates that both interest rate AND tenure affect total
borrowing cost, not just the interest rate alone.
"""

import pandas as pd
from calculations.emi import calculate_emi


def compare_scenarios(scenarios: list[dict]) -> pd.DataFrame:
    """
    Compare multiple loan scenarios side-by-side.

    Parameters
    ----------
    scenarios : list[dict]
        Each dict must contain:
            - 'name': str (e.g., "Scenario A")
            - 'principal': float
            - 'annual_rate': float
            - 'tenure_years': int

    Returns
    -------
    pd.DataFrame
        Comparison table with all calculated metrics.
    """
    results = []

    for sc in scenarios:
        emi_result = calculate_emi(
            sc["principal"], sc["annual_rate"], sc["tenure_years"]
        )
        results.append(
            {
                "Scenario": sc.get("name", "Unnamed"),
                "Principal (₹)": sc["principal"],
                "Interest Rate (%)": sc["annual_rate"],
                "Tenure (Years)": sc["tenure_years"],
                "Monthly EMI (₹)": emi_result["emi"],
                "Total Interest (₹)": emi_result["total_interest"],
                "Total Repayment (₹)": emi_result["total_payment"],
                "Interest / Principal": emi_result["interest_to_principal_ratio"],
            }
        )

    return pd.DataFrame(results)


def find_scenario_differences(comparison_df: pd.DataFrame) -> dict:
    """
    Calculate the spread (max − min) for key metrics across scenarios.

    Parameters
    ----------
    comparison_df : pd.DataFrame
        Output of compare_scenarios().

    Returns
    -------
    dict
        Spread values for EMI, total interest, and total repayment.
    """
    if comparison_df.empty or len(comparison_df) < 2:
        return {
            "emi_spread": 0,
            "interest_spread": 0,
            "repayment_spread": 0,
        }

    return {
        "emi_spread": round(
            comparison_df["Monthly EMI (₹)"].max()
            - comparison_df["Monthly EMI (₹)"].min(), 2
        ),
        "interest_spread": round(
            comparison_df["Total Interest (₹)"].max()
            - comparison_df["Total Interest (₹)"].min(), 2
        ),
        "repayment_spread": round(
            comparison_df["Total Repayment (₹)"].max()
            - comparison_df["Total Repayment (₹)"].min(), 2
        ),
    }
