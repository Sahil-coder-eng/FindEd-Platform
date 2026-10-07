"""
Loan Card Component
===================
Renders styled loan information cards for individual lenders and
side-by-side comparisons.
"""

import streamlit as st


def render_loan_card(lender: dict, calculated: dict = None):
    """
    Render a styled card for a single lender.

    Parameters
    ----------
    lender : dict
        Lender data from the dataset.
    calculated : dict, optional
        Calculated EMI results for this lender.
    """
    with st.container():
        st.markdown(
            f"""
            <div style="
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 18px;
                padding: 24px;
                margin-bottom: 16px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                    <h3 style="margin: 0; color: #1d1d1f; font-family: 'SF Pro Display', system-ui, -apple-system, Inter, sans-serif; font-size: 17px; font-weight: 600; letter-spacing: -0.374px;">🏦 {lender.get('lender_name', 'Unknown')}</h3>
                    <span style="
                        background: rgba(0, 102, 204, 0.08);
                        color: #0066cc;
                        padding: 3px 10px;
                        border-radius: 9999px;
                        font-size: 12px;
                        font-weight: 600;
                        letter-spacing: -0.12px;
                        white-space: nowrap;
                    ">{lender.get('loan_type', '')}</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 4px;">
                    <div>
                        <span style="color: #7a7a7a; font-size: 12px; letter-spacing: -0.12px;">Interest Rate</span><br/>
                        <span style="color: #1d1d1f; font-size: 17px; font-weight: 600; letter-spacing: -0.374px;">{lender.get('interest_rate_min', 'N/A')}% &ndash; {lender.get('interest_rate_max', 'N/A')}%</span>
                    </div>
                    <div>
                        <span style="color: #7a7a7a; font-size: 12px; letter-spacing: -0.12px;">Max Loan</span><br/>
                        <span style="color: #1d1d1f; font-size: 17px; font-weight: 600; letter-spacing: -0.374px;">{_format_amount(lender.get('max_loan_amount', 'Not Available'))}</span>
                    </div>
                    <div>
                        <span style="color: #7a7a7a; font-size: 12px; letter-spacing: -0.12px;">Processing Fee</span><br/>
                        <span style="color: #1d1d1f; font-size: 17px; font-weight: 600; letter-spacing: -0.374px;">{lender.get('processing_fee', 'Not Available')}</span>
                    </div>
                    <div>
                        <span style="color: #7a7a7a; font-size: 12px; letter-spacing: -0.12px;">Moratorium</span><br/>
                        <span style="color: #1d1d1f; font-size: 17px; font-weight: 600; letter-spacing: -0.374px;">{lender.get('moratorium_months', 'N/A')} months</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if calculated:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Monthly EMI", f"₹{calculated['emi']:,.0f}")
            with c2:
                st.metric("Total Interest", f"₹{calculated['total_interest']:,.0f}")
            with c3:
                st.metric("Total Repayment", f"₹{calculated['total_payment']:,.0f}")


def render_comparison_cards(lenders: list, results: list):
    """
    Render multiple lender cards in columns for comparison.

    Parameters
    ----------
    lenders : list[dict]
        List of lender data dictionaries.
    results : list[dict]
        List of corresponding calculated results.
    """
    # Display in rows of 3
    for i in range(0, len(lenders), 3):
        cols = st.columns(min(3, len(lenders) - i))
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(lenders):
                with col:
                    render_loan_card(lenders[idx], results[idx] if idx < len(results) else None)


def render_source_badge(lender: dict):
    """
    Render a small source-transparency badge for a lender.
    """
    source_url = lender.get("source_url", "Not Available")
    last_verified = lender.get("last_verified", "Unknown")

    st.markdown(
        f"""
        <div style="
            background: #f5f5f7;
            border: none;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 12px;
            font-family: 'SF Pro Text', system-ui, -apple-system, Inter, sans-serif;
            letter-spacing: -0.12px;
            color: #7a7a7a;
            margin-top: 6px;
            margin-bottom: 16px;
        ">
            Source: <a href="{source_url}" target="_blank" style="color: #0066cc; text-decoration: none;">{source_url}</a>&nbsp;&nbsp;·&nbsp;&nbsp;Verified: {last_verified}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_amount(value):
    """Format amount in Indian notation or return as-is if not numeric."""
    if isinstance(value, str) and value.lower() in ("not available", "na", "n/a"):
        return value
    try:
        num = float(value)
        if num >= 10000000:
            return f"₹{num / 10000000:.1f} Cr"
        elif num >= 100000:
            return f"₹{num / 100000:.1f} L"
        else:
            return f"₹{num:,.0f}"
    except (ValueError, TypeError):
        return str(value)
