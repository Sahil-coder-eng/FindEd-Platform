"""
Repayment Schedule / Amortization Engine
=========================================
Generates a month-by-month amortization schedule showing how each EMI
payment is split between interest and principal repayment.

For each month:
    Interest Component  = Opening Principal × Monthly Rate
    Principal Component = EMI − Interest Component
    Closing Principal   = Opening Principal − Principal Component
"""

import pandas as pd
from calculations.emi import calculate_emi_amount


def generate_amortization_schedule(
    principal: float,
    annual_rate: float,
    tenure_years: int,
) -> pd.DataFrame:
    """
    Generate a complete month-by-month amortization schedule.

    Parameters
    ----------
    principal : float
        Loan principal amount.
    annual_rate : float
        Annual interest rate as a percentage.
    tenure_years : int
        Repayment tenure in years.

    Returns
    -------
    pd.DataFrame
        Columns: month, opening_principal, emi, interest_component,
                 principal_component, closing_principal
    """
    if principal <= 0 or tenure_years <= 0:
        return pd.DataFrame(
            columns=[
                "month", "opening_principal", "emi",
                "interest_component", "principal_component", "closing_principal",
            ]
        )

    n = int(tenure_years * 12)
    r = annual_rate / 12 / 100 if annual_rate > 0 else 0.0
    emi = calculate_emi_amount(principal, annual_rate, n)

    schedule = []
    balance = principal

    for month in range(1, n + 1):
        interest = round(balance * r, 2)
        # Last month adjustment: ensure balance goes to exactly zero
        if month == n:
            principal_part = round(balance, 2)
            emi_adjusted = principal_part + interest
        else:
            principal_part = round(emi - interest, 2)
            emi_adjusted = emi

        closing = round(balance - principal_part, 2)
        # Guard against tiny floating-point negatives
        if closing < 0:
            closing = 0.0

        schedule.append(
            {
                "month": month,
                "opening_principal": round(balance, 2),
                "emi": round(emi_adjusted, 2),
                "interest_component": interest,
                "principal_component": principal_part,
                "closing_principal": closing,
            }
        )
        balance = closing

    return pd.DataFrame(schedule)


def get_yearly_summary(schedule_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate the monthly schedule into a yearly summary.

    Parameters
    ----------
    schedule_df : pd.DataFrame
        The monthly amortization schedule.

    Returns
    -------
    pd.DataFrame
        Columns: year, total_emi, total_interest, total_principal,
                 closing_principal
    """
    if schedule_df.empty:
        return pd.DataFrame(
            columns=["year", "total_emi", "total_interest",
                      "total_principal", "closing_principal"]
        )

    df = schedule_df.copy()
    df["year"] = ((df["month"] - 1) // 12) + 1

    yearly = df.groupby("year").agg(
        total_emi=("emi", "sum"),
        total_interest=("interest_component", "sum"),
        total_principal=("principal_component", "sum"),
        closing_principal=("closing_principal", "last"),
    ).reset_index()

    for col in ["total_emi", "total_interest", "total_principal", "closing_principal"]:
        yearly[col] = yearly[col].round(2)

    return yearly
