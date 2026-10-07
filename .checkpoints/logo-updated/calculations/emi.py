"""
EMI Calculation Engine
======================
Implements the standard reducing-balance EMI formula used by Indian banks
and financial institutions for education loans.

Formula:
    EMI = P × r × (1+r)^n / ((1+r)^n − 1)

Where:
    P = Principal loan amount
    r = Monthly interest rate (annual rate / 12 / 100)
    n = Total number of monthly payments (tenure in years × 12)
"""


def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> dict:
    """
    Calculate EMI, total payment, and total interest for a loan.

    Parameters
    ----------
    principal : float
        Loan principal amount in currency units (e.g., INR).
    annual_rate : float
        Annual interest rate as a percentage (e.g., 8.5 for 8.5%).
    tenure_years : int
        Loan repayment tenure in years.

    Returns
    -------
    dict
        {
            'principal': float,
            'annual_rate': float,
            'tenure_years': int,
            'tenure_months': int,
            'monthly_rate': float,
            'emi': float,
            'total_payment': float,
            'total_interest': float,
            'interest_to_principal_ratio': float,
        }

    Raises
    ------
    ValueError
        If principal <= 0, annual_rate < 0, or tenure_years <= 0.
    """
    # ── Input validation ────────────────────────────────────────────
    if principal <= 0:
        raise ValueError("Principal must be greater than zero.")
    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")
    if tenure_years <= 0:
        raise ValueError("Tenure must be at least 1 year.")

    n = int(tenure_years * 12)  # total monthly payments

    # ── Special case: 0% interest ───────────────────────────────────
    if annual_rate == 0:
        emi = principal / n
        return {
            "principal": principal,
            "annual_rate": 0.0,
            "tenure_years": tenure_years,
            "tenure_months": n,
            "monthly_rate": 0.0,
            "emi": round(emi, 2),
            "total_payment": round(principal, 2),
            "total_interest": 0.0,
            "interest_to_principal_ratio": 0.0,
        }

    # ── Standard reducing-balance EMI formula ───────────────────────
    r = annual_rate / 12 / 100  # monthly interest rate
    power = (1 + r) ** n
    emi = principal * r * power / (power - 1)

    total_payment = emi * n
    total_interest = total_payment - principal
    ratio = total_interest / principal

    return {
        "principal": principal,
        "annual_rate": annual_rate,
        "tenure_years": tenure_years,
        "tenure_months": n,
        "monthly_rate": round(r, 8),
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "interest_to_principal_ratio": round(ratio, 4),
    }


def calculate_emi_amount(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Lightweight helper — returns only the EMI amount.

    Parameters
    ----------
    principal : float
        Loan principal.
    annual_rate : float
        Annual interest rate as percentage.
    tenure_months : int
        Number of monthly payments.

    Returns
    -------
    float
        Monthly EMI amount.
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0
    if annual_rate == 0:
        return round(principal / tenure_months, 2)

    r = annual_rate / 12 / 100
    power = (1 + r) ** tenure_months
    emi = principal * r * power / (power - 1)
    return round(emi, 2)
