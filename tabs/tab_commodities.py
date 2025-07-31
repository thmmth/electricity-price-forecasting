import streamlit as st
import pandas as pd
import sqlite3
import os

# === DATABASE PATH ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "data.db")

# === STATIC DESCRIPTIONS FOR COMMODITIES ===
COMMODITY_DESCRIPTIONS = {
    "brent": "Brent Crude oil is a major benchmark price for purchases of oil worldwide. While Brent Crude oil is sourced from the North Sea the oil production coming from Europe, Africa and the Middle East flowing West tends to be priced relative to this oil.",
    "ttf_gas": "Dutch TTF Gas is a leading European benchmark price as the volumes traded represent more than 14 times the amount of gas used by the Netherlands for domestic purposes. Contracts are for physical delivery through the transfer of rights in respect of Natural Gas at the Title Transfer Facility (TTF) Virtual Trading Point, operated by Gasunie Transport Services (GTS), the transmission system operator in the Netherlands. Delivery is made equally each hour throughout the delivery period from 06:00 (CET) on the first day of the month until 06:00 (CET) on the first day of the next month. Futures are available for trading in the Intercontinental Exchange Inc. (ICE).",
    "crude_oil": "Crude oil futures are the benchmark for oil prices in the United States and serve as a reference point for global oil pricing. Crude oil is classified as light and sweet where light refers to its low density and sweet indicates its low sulfur content. The delivery point for crude oil futures is Cushing Hub in Oklahoma. Each futures contract represents 1,000 barrels of crude oil.",
    "coal": "Coal futures are available for trading in the Intercontinental Exchange and on the New York Mercantile Exchange. The standard GC Newcastle contact listed on ICE weights 1,000 metric tonnes. Coal is the major fuel used for generating electricity worldwide. The biggest producer and consumer of coal is China. Other big producers include: United States, India, Australia, Indonesia, Russia, South Africa, Germany and Poland. The biggest exporters of coal are: Indonesia, Australia, Russia, United States, Colombia, South Africa and Kazakhstan.",
    "gasoline": "Gasoline is the largest single volume refined product sold in the United States accounting for almost half of national oil consumption. The NYMEX Division New York harbor unleaded gasoline futures contract and reformulated gasoline blendstock for oxygen blending (RBOB) futures contract trade in units of 42,000 gallons (1,000 barrels). They are based on delivery at petroleum products terminals in the harbor, the major East Coast trading center for imports and domestic shipments from refineries in the New York harbor area or from the Gulf Coast refining centers.",
}

# === LOAD DATA ===
@st.cache_data
def load_commodities():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM commodity_prices", conn, parse_dates=["date"])

# === CSV EXPORT FUNCTION ===
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# === MAIN FUNCTION ===
def render():
    st.header("💰 Commodity Prices")

    df_comm = load_commodities()
    df_comm["date"] = df_comm["date"].dt.date

    # === COMMODITY SELECTION ===
    options = ["overview"] + sorted(df_comm["commodity"].unique().tolist())
    selected_commodity = st.selectbox("🛢️ Select a commodity:", options)

    if selected_commodity == "overview":
        filtered = df_comm.copy()
    else:
        filtered = df_comm[df_comm["commodity"] == selected_commodity]

    # === DATE FILTER ===
    min_date = filtered["date"].min()
    max_date = filtered["date"].max()
    date_range = st.date_input("📅 Filter by date:",
                               [min_date, max_date],
                               min_value=min_date,
                               max_value=max_date,
                               key="commodities_date")

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[(filtered["date"] >= start_date) & (filtered["date"] <= end_date)]

        # === SHOW DESCRIPTION IF APPLICABLE ===
        if selected_commodity != "overview" and selected_commodity in COMMODITY_DESCRIPTIONS:
            st.markdown(f"**About {selected_commodity}:** {COMMODITY_DESCRIPTIONS[selected_commodity]}")

        # === SHOW STATS IF SINGLE COMMODITY ===
        if selected_commodity != "overview":
            st.subheader("📊 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Mean", f"{filtered['price'].mean():.2f} {filtered['unit'].iloc[0]}")
            col2.metric("Min", f"{filtered['price'].min():.2f} {filtered['unit'].iloc[0]}")
            col3.metric("Max", f"{filtered['price'].max():.2f} {filtered['unit'].iloc[0]}")
            col4.metric("Std Dev", f"{filtered['price'].std():.2f}")

        # === CHART ===
        st.subheader("📈 Price Trends")
        if selected_commodity == "overview":
            chart_data = filtered.pivot(index="date", columns="commodity", values="price")
            st.line_chart(chart_data)
        else:
            st.line_chart(filtered.set_index("date")["price"])

        # === TABLE ===
        st.subheader("📋 Data")
        columns_to_show = ["commodity", "date", "price", "unit"]
        st.dataframe(filtered[columns_to_show].sort_values(by=["commodity", "date"]),
                     use_container_width=True)

        # === DOWNLOAD ===
        st.subheader("📥 Download Data")
        csv = convert_df_to_csv(filtered[columns_to_show])
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{selected_commodity.lower().replace(' ', '_')}_data.csv",
            mime="text/csv",
            icon="⬇️"
        )

        # === FOOTER ATTRIBUTION ===
        st.markdown(
            "<p style='font-size:0.8em; text-align:center; color:gray;'>Powered by Tradefeeds API</p>",
            unsafe_allow_html=True
        )
    else:
        st.warning("Please select both a start and end date.")
