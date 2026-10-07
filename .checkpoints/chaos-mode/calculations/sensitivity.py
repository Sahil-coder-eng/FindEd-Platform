"""
Sensitivity Analysis Engine
============================
Demonstrates how changes in a single variable (interest rate or tenure)
affect loan outcomes while holding other variables constant.

This is NOT a recommendation engine — it shows numerical tradeoffs so
users can make informed decisions.

Interest Rate Sensitivity:
    Vary rate while keeping principal and tenure fixed.
    → Shows how rate changes affect EMI, total interest, total repayment.

Tenure Sensitivity:
    Vary tenure while keeping principal and rate fixed.
    → Shows the tradeoff: shorter tenure = higher EMI but less total interest.
"""

import pandas as pd
from calculations.emi import calculate_emi


def rate_sensitivity(
    principal: float,
    tenure_years: int,
    rate_min: float = 7.0,
    rate_max: float = 14.0,
    rate_step: float = 0.5,
) -> pd.DataFrame:
    """
    Analyze how different interest rates affect loan outcomes.

    Parameters
    ----------
    principal : float
        Loan principal.
    tenure_years : int
        Fixed tenure in years.
    rate_min : float
        Minimum interest rate to simulate.
    rate_max : float
        Maximum interest rate to simulate.
    rate_step : float
        Step size between rates.

    Returns
    -------
    pd.DataFrame
        Columns: rate, emi, total_interest, total_payment
    """
    results = []
    rate = rate_min
    while rate <= rate_max + 0.001:  # small epsilon for float comparison
        emi_result = calculate_emi(principal, rate, tenure_years)
        results.append(
            {
                "Interest Rate (%)": round(rate, 2),
                "Monthly EMI (₹)": emi_result["emi"],
                "Total Interest (₹)": emi_result["total_interest"],
                "Total Repayment (₹)": emi_result["total_payment"],
            }
        )
        rate += rate_step

    return pd.DataFrame(results)


def tenure_sensitivity(
    principal: float,
    annual_rate: float,
    tenure_options: list[int] = None,
) -> pd.DataFrame:
    """
    Analyze how different tenures affect loan outcomes.

    Parameters
    ----------
    principal : float
        Loan principal.
    annual_rate : float
        Fixed annual interest rate.
    tenure_options : list[int], optional
        List of tenures (years) to compare. Defaults to common options.

    Returns
    -------
    pd.DataFrame
        Columns: tenure_years, emi, total_interest, total_payment
    """
    if tenure_options is None:
        tenure_options = [3, 5, 7, 10, 12, 15]

    results = []
    for years in tenure_options:
        emi_result = calculate_emi(principal, annual_rate, years)
        results.append(
            {
                "Tenure (Years)": years,
                "Monthly EMI (₹)": emi_result["emi"],
                "Total Interest (₹)": emi_result["total_interest"],
                "Total Repayment (₹)": emi_result["total_payment"],
                "Interest Saved vs Max": 0.0,  # filled below
            }
        )

    df = pd.DataFrame(results)
    if not df.empty:
        max_interest = df["Total Interest (₹)"].max()
        df["Interest Saved vs Max"] = round(max_interest - df["Total Interest (₹)"], 2)

    return df
