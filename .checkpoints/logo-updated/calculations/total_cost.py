"""
Total Cost Calculator
=====================
Aggregates ALL known costs of a loan beyond just EMI payments.

Total Financial Outflow = Total EMI Payments + Processing Fee + Other Known Charges

Where a charge is not available, it is flagged as "Not Available" rather
than assumed to be zero. This ensures transparency — the user knows
what is and isn't included in the cost estimate.
"""

from calculations.emi import calculate_emi


def calculate_total_cost(
    principal: float,
    annual_rate: float,
    tenure_years: int,
    processing_fee_pct: float = None,
    processing_fee_flat: float = None,
    other_charges: dict = None,
) -> dict:
    """
    Calculate the total financial outflow for a loan.

    Parameters
    ----------
    principal : float
        Loan principal amount.
    annual_rate : float
        Annual interest rate as percentage.
    tenure_years : int
        Repayment tenure in years.
    processing_fee_pct : float, optional
        Processing fee as a percentage of principal (e.g., 1.0 for 1%).
    processing_fee_flat : float, optional
        Processing fee as a flat amount.
    other_charges : dict, optional
        Dictionary of {charge_name: amount_or_None}.
        None values are flagged as "Not Available".

    Returns
    -------
    dict
        Comprehensive cost breakdown.
    """
    emi_result = calculate_emi(principal, annual_rate, tenure_years)

    # ── Processing fee ──────────────────────────────────────────────
    if processing_fee_pct is not None and processing_fee_pct > 0:
        proc_fee = round(principal * processing_fee_pct / 100, 2)
        proc_fee_status = "included"
        proc_fee_note = f"{processing_fee_pct}% of principal"
    elif processing_fee_flat is not None and processing_fee_flat > 0:
        proc_fee = round(processing_fee_flat, 2)
        proc_fee_status = "included"
        proc_fee_note = "Flat fee"
    else:
        proc_fee = 0.0
        proc_fee_status = "not_available"
        proc_fee_note = "Not available in collected source"

    # ── Other charges ───────────────────────────────────────────────
    known_charges = {}
    unavailable_charges = []
    total_other = 0.0

    if other_charges:
        for name, amount in other_charges.items():
            if amount is not None and amount > 0:
                known_charges[name] = round(amount, 2)
                total_other += amount
            else:
                unavailable_charges.append(name)

    # ── Total cost ──────────────────────────────────────────────────
    total_known_cost = round(
        emi_result["total_payment"] + proc_fee + total_other, 2
    )

    return {
        "emi": emi_result["emi"],
        "total_emi_payments": emi_result["total_payment"],
        "total_interest": emi_result["total_interest"],
        "processing_fee": proc_fee,
        "processing_fee_status": proc_fee_status,
        "processing_fee_note": proc_fee_note,
        "known_charges": known_charges,
        "unavailable_charges": unavailable_charges,
        "total_other_charges": round(total_other, 2),
        "total_known_cost": total_known_cost,
        "cost_above_principal": round(total_known_cost - principal, 2),
        "cost_components": {
            "Principal Repayment": principal,
            "Interest": emi_result["total_interest"],
            "Processing Fee": proc_fee if proc_fee_status == "included" else 0,
            "Other Charges": round(total_other, 2),
        },
        "disclaimer": (
            "This total includes only charges for which data was available. "
            "Actual costs may include additional fees not captured here."
            + (
                f" Unavailable: {', '.join(unavailable_charges)}."
                if unavailable_charges
                else ""
            )
        ),
    }
