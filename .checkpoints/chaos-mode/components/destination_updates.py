"""
Destination Updates Component
=============================
Renders education-related destination updates from the static dataset.
Clearly marked as sample data for prototype demonstration.
"""

import json
import streamlit as st
from pathlib import Path


def load_updates() -> list:
    """Load destination updates from the JSON file."""
    updates_path = Path(__file__).parent.parent / "data" / "destination_updates.json"
    try:
        with open(updates_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("updates", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def render_updates(country: str = None, category: str = None):
    """
    Render filtered destination updates as styled cards.

    Parameters
    ----------
    country : str, optional
        Filter by country name.
    category : str, optional
        Filter by category (e.g., "Visa / Immigration", "Education", "Student Work").
    """
    updates = load_updates()

    # Disclaimer banner
    st.markdown(
        """
        <div style="
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.35);
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 24px;
            font-size: 0.88rem;
            line-height: 1.5;
            color: #92400e;
        ">
            ⚠️ <strong style="color: #78350f;">Prototype Sample Data</strong> — These updates are illustrative entries
            for demonstration purposes. In a production system, these would be sourced from
            official government and education portals via RSS/API integration. Always verify
            information from official sources before making decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter
    if country:
        updates = [u for u in updates if u.get("country", "").lower() == country.lower()]
    if category:
        updates = [u for u in updates if u.get("category", "").lower() == category.lower()]

    if not updates:
        st.info("No updates found for the selected filters.")
        return

    # Render cards
    for update in updates:
        _render_update_card(update)


def _render_update_card(update: dict):
    """Render a single update card matching the Apple dark tile specification."""
    cat = update.get("category", "General")

    st.markdown(
        f"""
        <div class="destination-update-card" style="
            background: #272729 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 18px !important;
            padding: 24px 28px !important;
            margin-bottom: 16px !important;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="
                    background: rgba(41, 151, 255, 0.12) !important;
                    color: #2997ff !important;
                    border: 1px solid rgba(41, 151, 255, 0.28) !important;
                    padding: 3px 12px !important;
                    border-radius: 9999px !important;
                    font-size: 12px !important;
                    font-weight: 600 !important;
                    letter-spacing: -0.12px !important;
                ">{cat}</span>
                <span class="destination-update-meta" style="color: #86868b !important; font-size: 13px !important; font-weight: 400 !important; letter-spacing: -0.12px !important;">
                    {update.get('country', '')} &nbsp;&middot;&nbsp; {update.get('date', '')}
                </span>
            </div>
            <div class="destination-update-headline" style="
                color: #ffffff !important;
                font-family: 'SF Pro Display', system-ui, -apple-system, 'Inter', sans-serif !important;
                font-size: 20px !important;
                font-weight: 600 !important;
                line-height: 1.3 !important;
                letter-spacing: -0.374px !important;
                margin: 0 0 10px 0 !important;
            ">
                {update.get('headline', '')}
            </div>
            <div class="destination-update-body" style="
                color: #e0e0e0 !important;
                font-family: 'SF Pro Text', system-ui, -apple-system, 'Inter', sans-serif !important;
                font-size: 16px !important;
                font-weight: 400 !important;
                line-height: 1.55 !important;
                letter-spacing: -0.224px !important;
                margin: 0 0 16px 0 !important;
            ">
                {update.get('explanation', '')}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                <span class="destination-update-source" style="color: #86868b !important; font-size: 13px !important;">
                    Source: <strong style="color: #cccccc !important; font-weight: 500;">{update.get('source_name', 'Unknown')}</strong>
                </span>
                <a class="destination-update-link" href="{update.get('source_url', '#')}" target="_blank"
                   style="
                       color: #2997ff !important;
                       font-size: 14px !important;
                       font-weight: 500 !important;
                       letter-spacing: -0.12px !important;
                       text-decoration: none !important;
                   ">
                    View Original Source &rarr;
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_available_countries() -> list:
    """Get list of unique countries from updates."""
    updates = load_updates()
    return sorted(set(u.get("country", "") for u in updates if u.get("country")))


def get_available_categories() -> list:
    """Get list of unique categories from updates."""
    updates = load_updates()
    return sorted(set(u.get("category", "") for u in updates if u.get("category")))
