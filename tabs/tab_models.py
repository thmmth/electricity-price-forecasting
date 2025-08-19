import streamlit as st
import pandas as pd
import sqlite3
import os

# === DATABASE PATH ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "data.db")

# === MODEL DESCRIPTIONS PLACEHOLDER ===
MODEL_DESCRIPTIONS = {
    "LassoCV": "LassoCV is a linear regression model that uses L1 regularisation and automatically selects the optimal regularisation parameter (alpha) through cross-validation. By applying L1 penalty, it encourages sparsity in the coefficients, meaning some coefficients can be shrunk to exactly zero, which makes it useful for feature selection when dealing with datasets that contain many irrelevant or correlated features.\n\nSource: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LassoCV.html",
    "RidgeCV": "RidgeCV is a linear regression model that uses L2 regularisation and automatically selects the optimal regularisation parameter (alpha) through cross-validation. Unlike Lasso, Ridge does not set coefficients exactly to zero but instead shrinks them continuously, which helps to reduce model variance and handle multicollinearity among features.\n\nSource: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RidgeCV.html",
    "SVR": "SVR (Support Vector Regression) is a regression algorithm based on Support Vector Machines (SVM). It attempts to fit the best line within a certain margin of tolerance (epsilon), while using kernel functions to capture linear and non-linear relationships in the data. SVR is particularly effective in high-dimensional spaces and when the number of features exceeds the number of samples.\n\nSource: https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVR.html",
    "CatBoostRegressor": "CatBoostRegressor is a gradient boosting algorithm developed by Yandex that is particularly efficient with categorical features. It uses ordered boosting and target statistics to reduce overfitting and improve accuracy. CatBoost is designed to handle categorical variables natively without extensive preprocessing and often delivers strong performance with minimal hyperparameter tuning.\n\nSource: https://catboost.ai/en/docs/concepts/python-reference_catboostregressor",
    "RandomForestRegressor": "RandomForestRegressor is an ensemble learning method that builds multiple decision trees and combines their predictions by averaging. It reduces overfitting compared to individual decision trees and improves predictive accuracy. Random forests handle both numerical and categorical features, are robust to noise, and provide feature importance estimates.\n\nSource: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html",
    "XGBRegressor": "XGBRegressor is an implementation of gradient boosting optimized for speed and performance, developed as part of the XGBoost library. It builds an ensemble of decision trees sequentially, where each new tree corrects the errors of the previous ones. XGBoost incorporates regularisation, parallelization, and advanced optimization techniques, making it highly efficient and widely used in machine learning competitions.\n\nSource: https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor",
    "LGBMRegressor": "LGBMRegressor is a gradient boosting framework developed by Microsoft as part of the LightGBM library. It is optimized for speed and memory efficiency, using techniques such as histogram-based algorithms and leaf-wise tree growth. LightGBM can handle large-scale datasets with high dimensionality and supports both numerical and categorical features natively, making it a popular choice for regression and classification tasks.\n\nSource: https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.LGBMRegressor.html"
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

        # Create a copy to avoid changing the cached DataFrame
        df_display = df_results.drop(columns=["image_path"]).copy()

        # Format columns with €/MWh
        for col in ["val_mae", "val_rmse", "test_mae", "test_rmse"]:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f} €/MWh")

        # Round R² values
        for col in ["val_r2", "test_r2"]:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.3f}")

        # Display formatted table
        st.dataframe(df_display.sort_values(by="model_name"), use_container_width=True)

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

