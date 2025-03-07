import streamlit as st
import pandas as pd
import xgboost as xgb
from simfin_api import get_latest_stock_data  # Import the API function

# Load the trained model
model = xgb.XGBRegressor()
model.load_model("mag7_final_model.json")

# Streamlit UI
st.title("📈 AAPL Stock Price Prediction App")

# Select date (default to today's date)
selected_date = st.date_input("Select a date:")

# Fetch the latest stock data dynamically
st.write("Fetching the latest AAPL stock data from SimFin API... Please wait.")
latest_data = get_latest_stock_data("AAPL", selected_date)

if not latest_data.empty:
    # Features used for prediction
    features = ["close", "p_e_ratio", "sma_50"]
    X_latest = latest_data[features]

    # Make prediction for next close price
    predicted_next_close = model.predict(X_latest)[0]

    # Display the results
    st.subheader(f"📊 Prediction for AAPL on {selected_date}")
    st.metric(label="📈 Predicted Next Close Price", value=f"${predicted_next_close:.2f}")

    # Show actual market data for reference
    st.write("📌 Latest Market Data:")
    st.dataframe(latest_data[["date", "close", "p_e_ratio", "sma_50"]])
else:
    st.warning("⚠️ No valid data found for the selected date.")