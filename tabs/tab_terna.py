import streamlit as st
import pandas as pd
import sqlite3
import os

# === DATABASE PATH ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "data.db")

# === LOAD FORECAST DATA ===
@st.cache_data
def load_forecast():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM load_forecast", conn, parse_dates=["date"])

# === CONVERT TO CSV ===
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# === MAIN TAB RENDER FUNCTION ===
def render():
    st.header("🌀 Load Forecast")

    df = load_forecast()
    df["date"] = df["date"].dt.date

    # === ZONE SELECTION ===
    zone_options = sorted(df["zone"].unique().tolist())
    normalized_zones = [z.lower() for z in zone_options]

    if "italy" in normalized_zones:
        default_index = normalized_zones.index("italy")
    else:
        default_index = 0

    selected_zone = st.selectbox("🏞️ Select a zone:", zone_options, index=default_index)

    # === DATE FILTER ===
    min_date = df["date"].min()
    max_date = df["date"].max()
    date_range = st.date_input(
        "🗓️ Select date range:",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
        key="load_forecast_date"
    )

    if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
        st.warning("Please select both a start and end date.")
        return

    start_date, end_date = date_range

    # === FILTER DATA ===
    filtered = df[
        (df["zone"] == selected_zone) &
        (df["date"] >= start_date) &
        (df["date"] <= end_date)
    ]

    # === STATISTICS ===
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mean", f"{filtered['load_mw'].mean():,.0f} MW")
    col2.metric("Min", f"{filtered['load_mw'].min():,.0f} MW")
    col3.metric("Max", f"{filtered['load_mw'].max():,.0f} MW")
    col4.metric("Std Dev", f"{filtered['load_mw'].std():,.0f}")

    # === LINE CHART ===
    st.subheader("📈 Load Forecast Trend")
    st.line_chart(filtered.set_index("date")["load_mw"])

    # === TABLE VIEW ===
    st.subheader("📋 Data")
    st.dataframe(filtered.sort_values(by=["zone", "date"]), use_container_width=True)

    # === DOWNLOAD CSV ===
    st.subheader("📥 Download Data")
    csv = convert_df_to_csv(filtered)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"load_forecast_{selected_zone.lower().replace(' ', '_')}.csv",
        mime="text/csv",
        icon="⬇️"
    )

    # === ATTRIBUTION ===
    st.markdown(
        "<p style='font-size:0.8em; text-align:center; color:gray;'>Source: Terna Download Center</p>",
        unsafe_allow_html=True
    )
