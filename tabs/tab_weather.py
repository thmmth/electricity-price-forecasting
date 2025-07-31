import streamlit as st
import pandas as pd
import sqlite3
import os

# === DATABASE CONNECTION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "data.db")

# === LOAD WEATHER DATA ===
@st.cache_data
def load_weather():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM weather_data", conn, parse_dates=["time"])

# === CONVERT TO CSV ===
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# === MAIN TAB ===
def render():
    st.header("🌦️ Weather Data")

    df_weather = load_weather()
    df_weather["time"] = df_weather["time"].dt.date

    cities = sorted(df_weather["city"].unique().tolist())
    selected_city = st.selectbox("🏙️ Select a city:", cities)

    min_date = df_weather["time"].min()
    max_date = df_weather["time"].max()

    date_input = st.date_input(
        "🗓️ Select date range:",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
        key="weather_date"
    )

    if isinstance(date_input, tuple) and len(date_input) == 2:
        start_date, end_date = date_input
    else:
        st.warning("Please select both start and end dates.")
        return

    filtered = df_weather[
        (df_weather["city"] == selected_city) &
        (df_weather["time"] >= start_date) &
        (df_weather["time"] <= end_date)
    ]

    # === SUMMARY STATISTICS ===
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Avg Temp", f"{filtered['tavg'].mean():.1f} °C")
    col2.metric("Min Temp", f"{filtered['tmin'].min():.1f} °C")
    col3.metric("Max Temp", f"{filtered['tmax'].max():.1f} °C")
    col4.metric("Precipitation", f"{filtered['prcp'].mean():.1f} mm")
    col5.metric("Wind Speed", f"{filtered['wspd'].mean():.1f} km/h")

    # === CHARTS ===
    st.subheader(f"🌡️ Daily Avg Temperature - {selected_city.title()}")
    st.line_chart(filtered.set_index("time")["tavg"])

    st.subheader(f"🌧️ Daily Precipitation - {selected_city.title()}")
    st.line_chart(filtered.set_index("time")["prcp"])

    st.subheader(f"💨 Daily Wind Speed - {selected_city.title()}")
    st.line_chart(filtered.set_index("time")["wspd"])

    # === TABLE ===
    st.subheader("📋 Data")
    weather_cols = ["time", "tavg", "tmin", "tmax", "prcp", "wspd"]
    st.dataframe(filtered[weather_cols], use_container_width=True)

    # === CSV DOWNLOAD ===
    st.subheader("📥 Download Data")
    csv = convert_df_to_csv(filtered[weather_cols])
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"weather_data_{selected_city.lower()}.csv",
        mime="text/csv",
        icon="⬇️"
    )

    # === FOOTER ATTRIBUTION ===
    st.markdown(
        "<p style='font-size:0.8em; text-align:center; color:gray;'>Powered by Meteostat API</p>",
        unsafe_allow_html=True
    )