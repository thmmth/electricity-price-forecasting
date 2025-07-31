import streamlit as st
import pandas as pd
import sqlite3
import os

# === DATABASE PATH ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "data.db")

# === LOAD DATA FROM DATABASE ===
@st.cache_data
def load_pun():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM pun_prices", conn, parse_dates=["date"])

# === CONVERT DATAFRAME TO CSV ===
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# === MAIN TAB FUNCTION ===
def render():
    st.header("💡 PUN Index GME")

    st.markdown(
        "The **PUN Index GME** is the reference index for the Italian electricity market. It represents the reference price of electricity traded on the MGP and is calculated by the GME according to Article 13 of Legislative Decree 210/21 and its amendments, following the procedures set out in Article 1, paragraph 2 of Ministerial Decree MASE April 18, 2024."
    )

    # Load and preprocess data
    df_pun = load_pun()
    df_pun["date"] = df_pun["date"].dt.date

    # === DATE FILTER ===
    min_date = df_pun["date"].min()
    max_date = df_pun["date"].max()

    date_range = st.date_input(
        "📅 Select date range:",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range

        filtered_pun = df_pun[
            (df_pun["date"] >= start_date) & (df_pun["date"] <= end_date)
        ]

        # === SUMMARY STATISTICS ===
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean", f"{filtered_pun['price'].mean():.2f} €/MWh")
        col2.metric("Min", f"{filtered_pun['price'].min():.2f} €/MWh")
        col3.metric("Max", f"{filtered_pun['price'].max():.2f} €/MWh")
        col4.metric("Std Dev", f"{filtered_pun['price'].std():.2f}")

        # === PLOT PRICE TREND ===
        st.subheader("📈 Daily PUN Price")
        st.line_chart(filtered_pun.set_index("date")["price"])

        # === DISPLAY TABLE ===
        st.subheader("📋 Data")
        st.dataframe(filtered_pun, use_container_width=True)

        # === DOWNLOAD SECTION ===
        st.subheader("📥 Download Data")
        csv = convert_df_to_csv(filtered_pun)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="pun_filtered_data.csv",
            mime="text/csv",
            icon="⬇️"
        )

        # === FOOTER ATTRIBUTION ===
        st.markdown(
            "<p style='font-size:0.8em; text-align:center; color:gray;'>Source: Gestore dei Mercati Energetici (GME)</p>",
            unsafe_allow_html=True
        )
    else:
        st.warning("Please select both a start and end date.")
