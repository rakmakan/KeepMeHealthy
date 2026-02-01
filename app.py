from __future__ import annotations

import logging
from typing import List

import pandas as pd
import streamlit as st

from client import get_client
from models import RecommendationItem
from settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Healthy Grocery Picks", page_icon="🥗", layout="wide")


@st.cache_data(show_spinner=False, ttl=600)
def fetch_items_cached(food_item: str) -> List[RecommendationItem]:
    client = get_client()
    return client.fetch_recommendations(food_item)


def render_table(items: List[RecommendationItem]) -> None:
    rows = []
    for item in items:
        for brand in item.brand:
            rows.append(
                {
                    "Brand": brand,
                    "Item": item.item_name,
                    "Relevance": item.relevant,
                    "Source": str(item.url) if item.url else "",
                }
            )
    if not rows:
        st.info("No recommendations returned.")
        return

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_details(items: List[RecommendationItem]) -> None:
    for item in items:
        with st.expander(f"{item.item_name} — sources"):
            if item.url:
                st.markdown(f"[Source link]({item.url})")
            if item.summary:
                st.write(item.summary)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Pros**")
                for pro in item.pros:
                    st.markdown(f"- {pro}")
            with col2:
                st.markdown("**Cons**")
                for con in item.cons:
                    st.markdown(f"- {con}")


def main() -> None:
    settings = get_settings()

    if not settings.workflow_api_key:
        st.error("WORKFLOW_API_KEY is not set. Add it to .env or .streamlit/secrets.toml.")
        st.stop()

    st.title("Healthy Grocery Picks")
    st.caption("Nutritionist-style suggestions for what to buy in Montreal, Canada.")

    common_items = [
        "peanut butter",
        "almond milk",
        "greek yogurt",
        "whole grain bread",
        "brown rice",
        "oats",
        "protein powder",
    ]

    with st.sidebar:
        st.subheader("How it works")
        st.write(
            "Enter a food item and we'll query the workflow API for healthier brand suggestions, "
            "then display pros/cons and source links."
        )
        st.write("Results are cached for 10 minutes per food item.")

    with st.form("food-form", clear_on_submit=False):
        col_input, col_select = st.columns([2, 1])
        with col_input:
            food_item = st.text_input("Food item", placeholder="e.g., peanut butter")
        with col_select:
            preset = st.selectbox("Quick pick", options=[""] + common_items)
        submitted = st.form_submit_button("Get recommendations")

    if not submitted:
        st.stop()

    chosen_item = food_item.strip() if food_item.strip() else preset
    if not chosen_item:
        st.warning("Please type a food item or pick one from the list.")
        st.stop()

    st.info(f"Looking up healthier options for **{chosen_item}** ...")
    try:
        with st.spinner("Calling workflow..."):
            items = fetch_items_cached(chosen_item)
    except Exception as exc:  # broad: we want to surface any failure to the user
        logger.exception("Failed to fetch recommendations")
        st.error(f"Could not fetch recommendations: {exc}")
        st.stop()

    st.success(f"Found {len(items)} result sets.")
    render_table(items)
    render_details(items)


if __name__ == "__main__":
    main()
