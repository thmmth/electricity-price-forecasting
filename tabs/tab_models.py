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

# === MODEL ANALYSIS (NEW) ===
MODEL_ANALYSIS = {
    "LassoCV": "LassoCV achieves the best overall performance among the tested models, with a validation MAE of 9.87 €/MWh and an almost identical test MAE of 7.95 €/MWh. Both validation and test R² values remain strong at 0.76, showing excellent consistency and generalisation capability. The predictions align very closely with the true PUN series, capturing both medium-term dynamics and local variations with high accuracy. Unlike boosting models, LassoCV does not excessively smooth the series and manages to follow short-term volatility more effectively. These results highlight the strength of regularised linear models when the dataset contains informative lagged and correlated features.",
    "RidgeCV": "RidgeCV performs strongly, with validation metrics of MAE 9.90 €/MWh and R² of 0.75, and solid generalization on the test set (MAE 8.83 €/MWh, R² 0.67). The predictions closely follow the true PUN dynamics, successfully capturing medium-term patterns and maintaining good stability. Compared to LassoCV, RidgeCV is slightly less accurate on the test set, but still provides reliable forecasts. Its L2 regularisation helps to control variance and handle collinearity among features, making it a robust linear baseline for electricity price prediction.",
    "SVR": "SVR achieves good overall performance, with a validation MAE of 10.81 €/MWh and R² of 0.72, and further improvement on the test set (MAE 9.40 €/MWh, R² 0.68). The predictions follow the true PUN series reasonably well, capturing medium-term variations and maintaining stable generalisation. However, the model tends to smooth out extreme price movements, which limits its ability to reproduce sharp spikes and volatility. Despite this limitation, SVR provides a strong non-linear baseline and performs better than ensemble tree methods such as RandomForest and XGBRegressor.",
    "CatBoostRegressor": "CatBoostRegressor demonstrates consistent performance across validation and test sets, with MAE around 10 €/MWh and RMSE close to 13 €/MWh. The R² values (0.73 on validation and 0.65 on test) indicate that the model captures a substantial portion of the variance in the PUN. However, the prediction line is smoother than the true series, suggesting that CatBoost tends to underfit short-term volatility and local peaks. Overall, it provides stable forecasts and follows the general upward and downward trends well, but struggles with sharp fluctuations that characterize electricity prices.",
    "RandomForestRegressor": "RandomForestRegressor shows weaker performance compared to other models, with validation metrics of MAE 15.23 €/MWh and R² of 0.49, and only modest improvement on the test set (MAE 12.65 €/MWh, R² 0.50). The predictions capture the general level of the PUN but fail to reproduce the volatility and local spikes, resulting in overly smoothed forecasts. This indicates limited ability to generalize the complex dynamics of electricity prices, likely due to the model's tendency to average out extreme values. Overall, RandomForest underperforms in this context and appears less suitable than linear or boosting approaches for accurate PUN forecasting.",
    "XGBRegressor": "XGBRegressor delivers moderate results, with validation metrics of MAE 11.55 €/MWh and R² of 0.67, and slightly weaker performance on the test set (MAE 10.54 €/MWh, R² 0.61). The model captures the overall direction of the PUN series but tends to produce smoother forecasts that underestimate sharp fluctuations and short-term volatility. While XGBoost is generally strong for tabular data, in this context it struggles to match the accuracy of linear models such as LassoCV and RidgeCV. Nevertheless, it provides a stable baseline and follows the broader market trends reliably.",
    "LGBMRegressor": "LGBMRegressor delivers solid results, with a validation MAE of 12.50 €/MWh and a test MAE reduced to 9.69 €/MWh. The R² improves from 0.62 on validation to 0.66 on test, indicating better generalization on unseen data. The predictions track the overall dynamics of the PUN series closely, capturing medium-term fluctuations and broader trends. However, similar to CatBoost, the model tends to smooth out short-term volatility and does not fully reproduce sudden spikes. Despite this limitation, LightGBM provides competitive performance and demonstrates robustness across different phases of the dataset."
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
        st.subheader("📝 Highlights")
        st.write("Among the different model families, **linear models** (LassoCV and RidgeCV) achieved the strongest results.\nLassoCV obtained the lowest test MAE (7.95 €/MWh) and the highest R² (0.757), followed closely by RidgeCV (MAE 8.83 €/MWh, R² 0.667).\nThe **SVR** model also performed well, with an R² of 0.684, confirming its ability to capture non-linear patterns while maintaining good generalisation.\n\nIn contrast, **ensemble tree methods** showed mixed outcomes. Boosting models such as CatBoost and LGBM delivered competitive results (R² around 0.65–0.66), but did not surpass the simpler linear approaches. XGBRegressor lagged slightly behind with R² = 0.610.\nThe **RandomForestRegressor** was the weakest performer, with the lowest R² on the test set (0.496), indicating limited ability to generalize in this task.\n\nOverall, the results suggest that **regularised linear models provide the best predictive accuracy** for this dataset, while non-linear and ensemble methods may require additional tuning or feature engineering to match their performance.")

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

        # === ANALYSIS (NEW, AFTER IMAGE) ===
        st.subheader("🔎 Analysis")
        st.markdown(MODEL_ANALYSIS.get(selected_model, "to be added"))
