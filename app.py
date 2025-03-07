import streamlit as st
import pandas as pd
import xgboost as xgb
from simfin_api import SimFinAPI  # Import your API wrapper

# Initialize SimFin API
api = SimFinAPI(api_key="YOUR_SIMFIN_API_KEY")  # Replace with your actual key

# Load the trained XGBoost model
model = xgb.XGBRegressor()
model.load_model("mag7_final_model.json")

# Streamlit UI
st.title("📈 AAPL Stock Price Prediction App")

# Select date (default to today's date)
selected_date = st.date_input("Select a date:")

# Fetch the latest AAPL stock data dynamically
st.write("📡 Fetching AAPL stock data from SimFin API... Please wait.")

# Fetch data from API
prices_df = api.get_share_prices("AAPL", "2024-01-01", str(selected_date))
income_df = api.get_income_statement("AAPL", "2024-01-01", str(selected_date))
balance_df = api.get_balance_sheet("AAPL", "2024-01-01", str(selected_date))

# Merge datasets
if not prices_df.empty and not income_df.empty and not balance_df.empty:
    latest_data = prices_df.merge(income_df, on=["date", "ticker"], how="left")
    latest_data = latest_data.merge(balance_df, on=["date", "ticker"], how="left")

    # Feature engineering
    latest_data["p_e_ratio"] = latest_data["close"] / (latest_data["net_income"] / latest_data["share_capital"])
    latest_data["sma_50"] = latest_data["close"].rolling(window=50, min_periods=1).mean()

    # Select required features
    features = ["close", "p_e_ratio", "sma_50"]
    X_latest = latest_data[features].dropna()

    # Make prediction
    if not X_latest.empty:
        predicted_next_close = model.predict(X_latest)[0]

        # Display results
        st.subheader(f"📊 Prediction for AAPL on {selected_date}")
        st.metric(label="📈 Predicted Next Close Price", value=f"${predicted_next_close:.2f}")

        # Show actual market data for reference
        st.write("📌 Latest Market Data:")
        st.dataframe(latest_data[["date", "close", "p_e_ratio", "sma_50"]])
    else:
        st.warning("⚠️ Not enough data available for prediction.")
else:
    st.warning("⚠️ No valid data found for the selected date.")