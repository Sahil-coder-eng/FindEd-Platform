"""
Explainer Components
====================
"How is this calculated?" expandable sections for every major computation.
These serve dual purpose:
  1. Help users understand the financial math.
  2. Demonstrate methodology rigor to judges during Q&A.
"""

import streamlit as st


def explain_emi():
    """Expandable EMI formula explanation."""
    with st.expander("📐 How is EMI calculated?", expanded=False):
        st.markdown(
            """
            ### Reducing-Balance EMI Formula

            Education loans in India typically use the **reducing-balance method**
            (also called the diminishing-balance method). Under this method, interest
            is charged only on the **outstanding principal**, which decreases with
            every EMI payment.

            **Formula:**

            $$EMI = P \\times \\frac{r \\times (1+r)^n}{(1+r)^n - 1}$$

            **Where:**
            | Symbol | Meaning |
            |--------|---------|
            | **P** | Principal — the original loan amount |
            | **r** | Monthly interest rate = Annual Rate ÷ 12 ÷ 100 |
            | **n** | Total number of monthly payments = Tenure in years × 12 |
            | **EMI** | Equated Monthly Instalment — the fixed amount paid each month |

            **Example:**

            For a loan of ₹10,00,000 at 9% annual interest for 10 years:
            - P = 10,00,000
            - r = 9 / 12 / 100 = 0.0075
            - n = 10 × 12 = 120

            $$EMI = 10,00,000 \\times \\frac{0.0075 \\times (1.0075)^{120}}{(1.0075)^{120} - 1} = ₹12,668$$

            Each EMI consists of two parts:
            - **Interest component** = Outstanding Balance × Monthly Rate
            - **Principal component** = EMI − Interest Component

            As you keep paying EMIs, the outstanding balance reduces, so the interest
            component decreases and the principal component increases over time.
            """
        )


def explain_amortization():
    """Expandable amortization schedule explanation."""
    with st.expander("📊 How does the repayment schedule work?", expanded=False):
        st.markdown(
            """
            ### Amortization Schedule

            An amortization schedule shows the **month-by-month breakdown** of every
            EMI payment across the entire loan tenure.

            For each month, the schedule shows:

            | Column | Meaning |
            |--------|---------|
            | **Opening Principal** | Balance at the start of that month |
            | **EMI** | Fixed monthly payment |
            | **Interest Component** | Opening Principal × Monthly Rate |
            | **Principal Component** | EMI − Interest Component |
            | **Closing Principal** | Opening Principal − Principal Component |

            **Key insight:** In the early months, most of your EMI goes toward interest.
            As the principal reduces, more of your EMI goes toward actual repayment.
            This is why **prepayments early in the loan tenure save the most interest**.
            """
        )


def explain_moratorium():
    """Expandable moratorium explanation."""
    with st.expander("⏸️ What is a moratorium period?", expanded=False):
        st.markdown(
            """
            ### Moratorium (Grace Period)

            A **moratorium** is the period during and/or after your studies when you
            are **not required to pay regular EMIs**. However, interest typically
            continues to accrue during this period.

            The moratorium usually includes:
            1. **Course duration** — while you are studying
            2. **Grace period** — typically 6–12 months after course completion

            #### How is moratorium interest handled?

            Different lenders handle moratorium interest differently:

            **Option A — Interest Paid During Moratorium:**
            > You pay only the monthly interest during the moratorium. Your principal
            > stays the same, and your eventual EMI is calculated on the original
            > principal. This costs less in total.

            **Option B — Interest Capitalized:**
            > You don't pay anything during the moratorium. Interest accrues monthly
            > and is **added to your principal** (capitalized). When repayment starts,
            > your EMI is calculated on the **inflated principal**, resulting in higher
            > EMIs and more total interest.

            ⚠️ *The moratorium treatment varies by lender. Always confirm with your
            lender how interest is handled during the moratorium period.*
            """
        )


def explain_total_cost():
    """Expandable total cost explanation."""
    with st.expander("💰 How is total cost calculated?", expanded=False):
        st.markdown(
            """
            ### Total Financial Outflow

            The **advertised interest rate** does not tell the full story. The actual
            cost of a loan includes several components:

            | Component | Description |
            |-----------|-------------|
            | **Principal** | The amount you borrowed |
            | **Total Interest** | Cumulative interest over the entire tenure |
            | **Processing Fee** | One-time fee charged by the lender (if any) |
            | **Other Charges** | Insurance, documentation, etc. (if applicable) |

            **Total Cost = Total EMI Payments + Processing Fee + Other Known Charges**

            ⚠️ *Where a specific charge is not available in our dataset, it is marked
            as "Not Available" rather than assumed to be zero. This ensures you know
            exactly what is and isn't included in the estimate.*
            """
        )


def explain_sensitivity():
    """Expandable sensitivity analysis explanation."""
    with st.expander("📈 What does sensitivity analysis show?", expanded=False):
        st.markdown(
            """
            ### Sensitivity Analysis

            Sensitivity analysis shows **how changes in one variable affect the
            loan outcome**, while keeping other variables constant.

            **Interest Rate Sensitivity:**
            > Varies the interest rate and shows the impact on EMI and total interest.
            > Even small rate differences can significantly affect the total cost over
            > a long tenure.

            **Tenure Sensitivity:**
            > Varies the repayment tenure and shows the tradeoff:
            > - **Shorter tenure** → Higher EMI but less total interest
            > - **Longer tenure** → Lower EMI but more total interest

            ⚖️ *Neither option is universally "better". The right choice depends on
            your monthly budget and total cost tolerance.*
            """
        )


def explain_currency():
    """Expandable currency conversion explanation."""
    with st.expander("💱 How does the currency conversion work?", expanded=False):
        st.markdown(
            """
            ### Currency Conversion for International Education

            When planning to study abroad, your education expenses will be in the
            destination country's currency. To understand the INR equivalent:

            **INR Cost = Foreign Amount × Exchange Rate**

            *Example:* $30,000 × ₹83/USD = ₹24,90,000

            ⚠️ **Important:** Exchange rates fluctuate daily. The rates shown here
            are user-editable defaults and are **not predictions**. The currency
            sensitivity chart shows how rate changes could affect your INR cost,
            **not** what will actually happen.

            For actual transactions, always check current rates from your bank or
            an authorized dealer.
            """
        )
