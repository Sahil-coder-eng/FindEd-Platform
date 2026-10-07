"""
Chart Components
================
All Plotly chart functions used across the application.
Charts use the Apple design system — white canvas, near-black ink, Action Blue accent.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Shared chart theme — Apple Design System ───────────────────────
COLORS = {
    "primary": "#0066cc",       # Action Blue
    "secondary": "#34aadc",     # Sky accent
    "accent": "#ff6b00",        # Warm orange (replaces amber)
    "danger": "#ff3b30",        # iOS red
    "purple": "#5856d6",        # iOS purple
    "cyan": "#32ade6",          # iOS teal
    "bg": "#ffffff",            # canvas
    "card_bg": "#f5f5f7",       # canvas-parchment
    "text": "#1d1d1f",          # ink
    "muted": "#7a7a7a",         # ink-muted-48
    "hairline": "#e0e0e0",      # hairline
}

PALETTE = [
    COLORS["primary"], COLORS["secondary"], COLORS["accent"],
    COLORS["purple"], COLORS["cyan"], COLORS["danger"],
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color=COLORS["text"],
        family="SF Pro Text, SF Pro Display, system-ui, -apple-system, Inter, sans-serif",
        size=14,
    ),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
        font=dict(size=12, color=COLORS["muted"]),
    ),
    xaxis=dict(
        gridcolor=COLORS["hairline"],
        zerolinecolor=COLORS["hairline"],
        tickfont=dict(color=COLORS["muted"], size=12),
        linecolor=COLORS["hairline"],
    ),
    yaxis=dict(
        gridcolor=COLORS["hairline"],
        zerolinecolor=COLORS["hairline"],
        tickfont=dict(color=COLORS["muted"], size=12),
        linecolor=COLORS["hairline"],
    ),
)


def _apply_layout(fig, title: str = "", height: int = 450):
    """Apply consistent Apple theme to a figure."""
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(
                size=21,
                color=COLORS["text"],
                family="SF Pro Display, system-ui, -apple-system, Inter, sans-serif",
            ),
        ),
        height=height,
        **LAYOUT_DEFAULTS,
    )
    return fig



# ── EMI Comparison Bar Chart ───────────────────────────────────────

def plot_emi_comparison(comparison_df: pd.DataFrame):
    """Grouped bar chart comparing EMI, total interest, and total repayment."""
    fig = go.Figure()

    lenders = comparison_df["Lender"]
    fig.add_trace(go.Bar(
        name="Monthly EMI",
        x=lenders, y=comparison_df["Monthly EMI (₹)"],
        marker_color=COLORS["primary"],
        text=[f"₹{v:,.0f}" for v in comparison_df["Monthly EMI (₹)"]],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Total Interest",
        x=lenders, y=comparison_df["Total Interest (₹)"],
        marker_color=COLORS["accent"],
        text=[f"₹{v:,.0f}" for v in comparison_df["Total Interest (₹)"]],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Total Repayment",
        x=lenders, y=comparison_df["Total Repayment (₹)"],
        marker_color=COLORS["secondary"],
        text=[f"₹{v:,.0f}" for v in comparison_df["Total Repayment (₹)"]],
        textposition="outside",
    ))

    fig.update_layout(barmode="group")
    return _apply_layout(fig, "Loan Comparison Overview", 500)


# ── Amortization Charts ────────────────────────────────────────────

def plot_amortization_breakdown(schedule_df: pd.DataFrame):
    """Stacked area chart: interest vs principal component over time."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=schedule_df["month"],
        y=schedule_df["interest_component"],
        name="Interest Component",
        fill="tonexty",
        mode="lines",
        line=dict(width=0.5, color=COLORS["accent"]),
        fillcolor="rgba(245, 158, 11, 0.3)",
    ))
    fig.add_trace(go.Scatter(
        x=schedule_df["month"],
        y=schedule_df["principal_component"],
        name="Principal Component",
        fill="tonexty",
        mode="lines",
        line=dict(width=0.5, color=COLORS["primary"]),
        fillcolor="rgba(16, 185, 129, 0.3)",
    ))

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (₹)",
    )
    return _apply_layout(fig, "EMI Breakdown: Interest vs Principal Over Time")


def plot_principal_decline(schedule_df: pd.DataFrame):
    """Line chart of outstanding principal declining over time."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=schedule_df["month"],
        y=schedule_df["closing_principal"],
        name="Outstanding Principal",
        mode="lines",
        line=dict(width=3, color=COLORS["secondary"]),
        fill="tozeroy",
        fillcolor="rgba(59, 130, 246, 0.15)",
    ))

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Outstanding Principal (₹)",
    )
    return _apply_layout(fig, "Outstanding Loan Balance Over Time")


# ── Sensitivity Charts ─────────────────────────────────────────────

def plot_rate_sensitivity(sensitivity_df: pd.DataFrame):
    """Multi-line chart: EMI and total interest vs interest rate."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sensitivity_df["Interest Rate (%)"],
        y=sensitivity_df["Monthly EMI (₹)"],
        name="Monthly EMI",
        mode="lines+markers",
        line=dict(width=3, color=COLORS["primary"]),
        marker=dict(size=8),
        yaxis="y",
    ))

    fig.add_trace(go.Scatter(
        x=sensitivity_df["Interest Rate (%)"],
        y=sensitivity_df["Total Interest (₹)"],
        name="Total Interest",
        mode="lines+markers",
        line=dict(width=3, color=COLORS["accent"]),
        marker=dict(size=8),
        yaxis="y2",
    ))

    fig.update_layout(
        xaxis_title="Interest Rate (%)",
        yaxis=dict(title="Monthly EMI (₹)", side="left", gridcolor="rgba(148,163,184,0.1)"),
        yaxis2=dict(title="Total Interest (₹)", side="right", overlaying="y", gridcolor="rgba(148,163,184,0.1)"),
    )
    return _apply_layout(fig, "Interest Rate Sensitivity Analysis", 500)


def plot_tenure_sensitivity(sensitivity_df: pd.DataFrame):
    """Bar + line chart: EMI (bars) vs total interest (line) by tenure."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=sensitivity_df["Tenure (Years)"].astype(str) + " yrs",
        y=sensitivity_df["Monthly EMI (₹)"],
        name="Monthly EMI",
        marker_color=COLORS["primary"],
        text=[f"₹{v:,.0f}" for v in sensitivity_df["Monthly EMI (₹)"]],
        textposition="outside",
        yaxis="y",
    ))

    fig.add_trace(go.Scatter(
        x=sensitivity_df["Tenure (Years)"].astype(str) + " yrs",
        y=sensitivity_df["Total Interest (₹)"],
        name="Total Interest",
        mode="lines+markers",
        line=dict(width=3, color=COLORS["accent"]),
        marker=dict(size=10),
        yaxis="y2",
    ))

    fig.update_layout(
        xaxis_title="Tenure",
        yaxis=dict(title="Monthly EMI (₹)", side="left", gridcolor="rgba(148,163,184,0.1)"),
        yaxis2=dict(title="Total Interest (₹)", side="right", overlaying="y", gridcolor="rgba(148,163,184,0.1)"),
    )
    return _apply_layout(fig, "Tenure Sensitivity: EMI vs Total Interest Tradeoff", 500)


# ── Cost Breakdown Chart ───────────────────────────────────────────

def plot_cost_breakdown(cost_components: dict):
    """Donut chart of total cost components."""
    labels = []
    values = []
    for label, value in cost_components.items():
        if value > 0:
            labels.append(label)
            values.append(value)

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=PALETTE[:len(labels)]),
        textinfo="label+percent",
        textfont=dict(size=12, color=COLORS["text"]),
        hovertemplate="%{label}<br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))

    fig.add_annotation(
        text="Total<br>Cost",
        x=0.5, y=0.5,
        font=dict(size=14, color=COLORS["muted"]),
        showarrow=False,
    )

    return _apply_layout(fig, "Cost Breakdown", 450)


# ── Moratorium Timeline ────────────────────────────────────────────

def plot_moratorium_timeline(timeline: dict):
    """Horizontal timeline visualization of the loan lifecycle."""
    phases = [
        ("📚 Course Period", timeline["course_period"]["duration_months"], COLORS["secondary"]),
        ("⏸️ Grace Period", timeline["grace_period"]["duration_months"], COLORS["accent"]),
        ("💳 Repayment", timeline["repayment_period"]["duration_months"], COLORS["primary"]),
    ]

    fig = go.Figure()
    start = 0
    for name, duration, color in phases:
        if duration > 0:
            fig.add_trace(go.Bar(
                x=[duration],
                y=["Loan Timeline"],
                orientation="h",
                name=name,
                marker=dict(color=color, line=dict(width=0)),
                text=f"{name}<br>{duration} months",
                textposition="inside",
                textfont=dict(size=11, color="white"),
                base=start,
            ))
            start += duration

    fig.update_layout(
        barmode="stack",
        xaxis_title="Months",
        yaxis=dict(showticklabels=False),
        showlegend=True,
        height=200,
    )
    return _apply_layout(fig, "", 220)


# ── Scenario Comparison ────────────────────────────────────────────

def plot_scenario_comparison(scenario_df: pd.DataFrame):
    """Grouped bar chart for scenario comparison."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Monthly EMI",
        x=scenario_df["Scenario"],
        y=scenario_df["Monthly EMI (₹)"],
        marker_color=COLORS["primary"],
        text=[f"₹{v:,.0f}" for v in scenario_df["Monthly EMI (₹)"]],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Total Interest",
        x=scenario_df["Scenario"],
        y=scenario_df["Total Interest (₹)"],
        marker_color=COLORS["accent"],
        text=[f"₹{v:,.0f}" for v in scenario_df["Total Interest (₹)"]],
        textposition="outside",
    ))

    fig.update_layout(barmode="group")
    return _apply_layout(fig, "Scenario Comparison", 450)


# ── Currency Sensitivity ───────────────────────────────────────────

def plot_currency_sensitivity(sensitivity_data: list):
    """Line chart showing how exchange rate changes affect INR cost."""
    rates = [d["exchange_rate"] for d in sensitivity_data]
    amounts = [d["converted_amount"] for d in sensitivity_data]
    pct_changes = [d["rate_change_pct"] for d in sensitivity_data]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=rates,
        y=amounts,
        mode="lines+markers",
        line=dict(width=3, color=COLORS["cyan"]),
        marker=dict(size=8),
        text=[f"{p:+.1f}%" for p in pct_changes],
        hovertemplate="Rate: %{x:.2f}<br>INR Cost: ₹%{y:,.0f}<br>Change: %{text}<extra></extra>",
    ))

    # Highlight the base rate
    base_idx = len(sensitivity_data) // 2
    fig.add_vline(
        x=rates[base_idx],
        line_dash="dash",
        line_color=COLORS["muted"],
        annotation_text="Base Rate",
    )

    fig.update_layout(
        xaxis_title="Exchange Rate",
        yaxis_title="INR Cost (₹)",
    )
    return _apply_layout(fig, "Exchange Rate Sensitivity — Impact on INR Cost", 450)
