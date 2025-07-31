import streamlit as st
import pandas as pd
import sqlite3
import os

# === DATABASE PATH ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "data.db")

# === MODEL DESCRIPTIONS PLACEHOLDER ===
MODEL_DESCRIPTIONS = {
    "LassoCV": "da inserire dopo",
    "RidgeCV": "da inserire dopo",
    "SVR": "da inserire dopo",
    "CatBoostRegressor": "da inserire dopo",
    "RandomForestRegressor": "da inserire dopo",
    "XGBRegressor": "da inserire dopo",
    "LGBMRegressor": "da inserire dopo"
}

# === LOAD MODEL RESULTS FROM DB ===
@st.cache_data
def load_model_results():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM model_results", conn)

# === MAIN FUNCTION ===
def render():
    st.header("🧠 Machine Learning Model Results")

    df_results = load_model_results()

    if df_results.empty:
        st.warning("No model results found in the database.")
        return

    model_names = sorted(df_results["model_name"].unique().tolist())
    options = ["overview"] + model_names

    selected_model = st.selectbox("📂 Select a model:", options)

    if selected_model == "overview":
        st.subheader("📋 All Model Results")
        st.dataframe(
            df_results.drop(columns=["image_path"]).sort_values(by="model_name"),
            use_container_width=True
        )
    else:
        model_data = df_results[df_results["model_name"] == selected_model].iloc[0]

        # === DESCRIPTION ===
        st.markdown(f"**About {selected_model}:** {MODEL_DESCRIPTIONS.get(selected_model, 'da inserire dopo')}")

        # === METRICS ===
        st.subheader("📊 Performance Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Val. MAE", f"{model_data['val_mae']:.2f} €/MWh")
        col2.metric("Val. RMSE", f"{model_data['val_rmse']:.2f} €/MWh")
        col3.metric("Val. R²", f"{model_data['val_r2']:.2f}")

        col4, col5, col6 = st.columns(3)
        col4.metric("Test MAE", f"{model_data['test_mae']:.2f} €/MWh")
        col5.metric("Test RMSE", f"{model_data['test_rmse']:.2f} €/MWh")
        col6.metric("Test R²", f"{model_data['test_r2']:.2f}")

        # === IMAGE ===
        st.subheader("📈 Prediction Plot")
        image_path = model_data["image_path"]
        if os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.error(f"Plot not found at: {image_path}")

