"""
Education Cost Estimator & Currency Converter
==============================================
Helps students estimate total education expenses and the resulting
financing requirement after accounting for scholarships and family
contributions.

Also provides currency conversion for international education,
allowing foreign expenses to be converted to INR.
"""


def estimate_education_cost(
    tuition: float = 0.0,
    hostel: float = 0.0,
    books: float = 0.0,
    travel: float = 0.0,
    living: float = 0.0,
    other: float = 0.0,
    num_years: int = 1,
    scholarship: float = 0.0,
    family_contribution: float = 0.0,
) -> dict:
    """
    Estimate total education cost and financing requirement.

    All amounts are per year unless otherwise specified.
    Scholarship and family contribution are total amounts.

    Parameters
    ----------
    tuition : float
        Annual tuition fee.
    hostel : float
        Annual hostel/accommodation cost.
    books : float
        Annual books and materials cost.
    travel : float
        Total travel cost (one-time or annual × years).
    living : float
        Annual living expenses.
    other : float
        Annual other expenses.
    num_years : int
        Number of years of study.
    scholarship : float
        Total scholarship amount (not per year).
    family_contribution : float
        Total family contribution.

    Returns
    -------
    dict
        Cost breakdown and financing requirement.
    """
    annual_cost = tuition + hostel + books + living + other
    total_recurring = annual_cost * num_years
    total_travel = travel  # assumed total, not per year
    total_cost = total_recurring + total_travel

    available_funds = scholarship + family_contribution
    financing_required = max(0, total_cost - available_funds)

    return {
        "annual_breakdown": {
            "Tuition": tuition,
            "Hostel / Accommodation": hostel,
            "Books & Materials": books,
            "Living Expenses": living,
            "Other Expenses": other,
            "Annual Total": annual_cost,
        },
        "total_breakdown": {
            "Recurring Costs (× years)": total_recurring,
            "Travel": total_travel,
            "Total Education Cost": total_cost,
            "Scholarship": scholarship,
            "Family Contribution": family_contribution,
            "Available Funds": available_funds,
        },
        "num_years": num_years,
        "total_education_cost": round(total_cost, 2),
        "available_funds": round(available_funds, 2),
        "financing_required": round(financing_required, 2),
    }


def convert_currency(
    amount: float,
    exchange_rate: float,
    from_symbol: str = "$",
    to_symbol: str = "₹",
) -> dict:
    """
    Convert an amount using a given exchange rate.

    Parameters
    ----------
    amount : float
        Amount in foreign currency.
    exchange_rate : float
        Units of target currency per unit of source currency.
    from_symbol : str
        Source currency symbol.
    to_symbol : str
        Target currency symbol.

    Returns
    -------
    dict
        Conversion result.
    """
    converted = round(amount * exchange_rate, 2)
    return {
        "original_amount": amount,
        "exchange_rate": exchange_rate,
        "converted_amount": converted,
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "display": f"{from_symbol}{amount:,.2f} × {exchange_rate} = {to_symbol}{converted:,.2f}",
    }


def currency_sensitivity(
    amount: float,
    base_rate: float,
    variation_pct: float = 10.0,
    steps: int = 5,
    from_symbol: str = "$",
    to_symbol: str = "₹",
) -> list[dict]:
    """
    Show how exchange-rate fluctuations affect the INR cost.

    Parameters
    ----------
    amount : float
        Amount in foreign currency.
    base_rate : float
        Base exchange rate.
    variation_pct : float
        Percentage variation to simulate (±).
    steps : int
        Number of steps on each side of the base rate.
    from_symbol : str
        Source currency symbol.
    to_symbol : str
        Target currency symbol.

    Returns
    -------
    list[dict]
        List of conversion results at different rates.
    """
    results = []
    step_size = variation_pct / steps

    for i in range(-steps, steps + 1):
        pct_change = i * step_size
        rate = round(base_rate * (1 + pct_change / 100), 2)
        converted = round(amount * rate, 2)
        results.append(
            {
                "rate_change_pct": round(pct_change, 1),
                "exchange_rate": rate,
                "converted_amount": converted,
                "from_display": f"{from_symbol}{amount:,.2f}",
                "to_display": f"{to_symbol}{converted:,.2f}",
            }
        )

    return results
