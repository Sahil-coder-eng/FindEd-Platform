"""
Moratorium Impact Calculator
============================
Education loans typically have a moratorium (grace) period comprising:
  1. Course duration — while the student is studying.
  2. Post-course grace period — typically 6–12 months after course completion.

During this combined period, interest accrues on the principal but regular
EMI repayment has not yet started. The treatment of this accrued interest
varies by lender:

  Mode A — "paid_during":
      The borrower pays simple interest each month during the moratorium.
      The principal does not increase, and repayment EMI is based on the
      original principal.

  Mode B — "capitalized":
      Interest accrues and is added (capitalized) to the principal at the
      end of the moratorium. The repayment EMI is then calculated on the
      inflated principal.
"""

from calculations.emi import calculate_emi


def calculate_moratorium_impact(
    principal: float,
    annual_rate: float,
    course_months: int,
    moratorium_months: int,
    tenure_years: int,
    interest_treatment: str = "capitalized",
) -> dict:
    """
    Calculate the impact of a moratorium period on the loan.

    Parameters
    ----------
    principal : float
        Original loan principal.
    annual_rate : float
        Annual interest rate as a percentage.
    course_months : int
        Duration of the course in months.
    moratorium_months : int
        Additional grace period after course completion in months.
    tenure_years : int
        Repayment tenure in years (after moratorium ends).
    interest_treatment : str
        "paid_during" — interest is paid monthly during moratorium.
        "capitalized" — interest is added to principal at end of moratorium.

    Returns
    -------
    dict
        Comprehensive moratorium impact analysis.
    """
    if principal <= 0 or annual_rate < 0 or tenure_years <= 0:
        raise ValueError("Invalid input parameters.")

    total_moratorium_months = course_months + moratorium_months
    monthly_rate = annual_rate / 12 / 100

    # ── Calculate moratorium-period interest ─────────────────────────
    if interest_treatment == "paid_during":
        # Simple interest paid each month — principal stays the same
        monthly_interest_payment = round(principal * monthly_rate, 2)
        total_moratorium_interest = round(
            monthly_interest_payment * total_moratorium_months, 2
        )
        effective_principal = principal

    elif interest_treatment == "capitalized":
        # Compound interest added to principal month by month
        balance = principal
        total_moratorium_interest = 0.0
        for _ in range(total_moratorium_months):
            month_interest = balance * monthly_rate
            total_moratorium_interest += month_interest
            balance += month_interest  # capitalize
        total_moratorium_interest = round(total_moratorium_interest, 2)
        effective_principal = round(balance, 2)
        monthly_interest_payment = None  # not applicable

    else:
        raise ValueError(
            f"Unknown interest_treatment: '{interest_treatment}'. "
            "Use 'paid_during' or 'capitalized'."
        )

    # ── Calculate repayment EMI on effective principal ───────────────
    emi_result_without_moratorium = calculate_emi(principal, annual_rate, tenure_years)
    emi_result_with_moratorium = calculate_emi(effective_principal, annual_rate, tenure_years)

    # ── Total cost comparison ───────────────────────────────────────
    total_cost_without_moratorium = emi_result_without_moratorium["total_payment"]
    if interest_treatment == "paid_during":
        total_cost_with_moratorium = (
            emi_result_with_moratorium["total_payment"] + total_moratorium_interest
        )
    else:  # capitalized
        total_cost_with_moratorium = emi_result_with_moratorium["total_payment"]

    additional_cost = round(total_cost_with_moratorium - total_cost_without_moratorium, 2)

    # ── Timeline breakdown ──────────────────────────────────────────
    timeline = {
        "course_period": {
            "duration_months": course_months,
            "description": "Study period — no EMI payments",
        },
        "grace_period": {
            "duration_months": moratorium_months,
            "description": "Post-course grace period",
        },
        "total_moratorium": {
            "duration_months": total_moratorium_months,
            "description": "Total period before EMI repayment begins",
        },
        "repayment_period": {
            "duration_months": tenure_years * 12,
            "description": "Regular EMI repayment period",
        },
        "total_loan_duration": {
            "duration_months": total_moratorium_months + (tenure_years * 12),
            "description": "Total time from loan disbursement to final payment",
        },
    }

    return {
        "principal": principal,
        "annual_rate": annual_rate,
        "course_months": course_months,
        "moratorium_months": moratorium_months,
        "total_moratorium_months": total_moratorium_months,
        "interest_treatment": interest_treatment,
        "monthly_interest_payment": monthly_interest_payment,
        "total_moratorium_interest": total_moratorium_interest,
        "effective_principal_at_repayment": effective_principal,
        "principal_increase": round(effective_principal - principal, 2),
        "emi_without_moratorium": emi_result_without_moratorium["emi"],
        "emi_with_moratorium": emi_result_with_moratorium["emi"],
        "emi_increase": round(
            emi_result_with_moratorium["emi"] - emi_result_without_moratorium["emi"], 2
        ),
        "total_cost_without_moratorium": total_cost_without_moratorium,
        "total_cost_with_moratorium": round(total_cost_with_moratorium, 2),
        "additional_cost_due_to_moratorium": additional_cost,
        "timeline": timeline,
    }
