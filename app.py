import streamlit as st
import pandas as pd
import xgboost as xgb
from simfin_api import SimFinAPI  # Import your API wrapper
from datetime import datetime, timedelta
import os

# Initialize SimFin API
api = SimFinAPI(api_key="b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c")  # Replace with your actual key

# Load the trained XGBoost classification model
model = xgb.XGBClassifier()
model.load_model("mag7_final_model.json")

# Define end date as yesterday
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

# Define CSV save path in the GitHub repository
csv_filename = "merged_debug_output.csv"
csv_save_path = os.path.join("/mnt/data", csv_filename)

# Streamlit UI
st.title("📈 AAPL Stock Movement Prediction App")

# Fetch the latest AAPL stock data dynamically
st.write("📡 Fetching AAPL stock data from SimFin API... Please wait.")

# Fetch data from API
prices_df = api.get_share_prices("AAPL", "2024-01-01", yesterday)
income_df = api.get_income_statement("AAPL", "2024-01-01", yesterday)
balance_df = api.get_balance_sheet("AAPL", "2024-01-01", yesterday)

# Ensure date columns are in datetime format
prices_df["date"] = pd.to_datetime(prices_df["date"])
income_df["date"] = pd.to_datetime(income_df["date"])
balance_df["date"] = pd.to_datetime(balance_df["date"])

# Merge datasets using a left join on ticker and date
merged_df = prices_df.merge(income_df, on=["ticker", "date"], how="left")
merged_df = merged_df.merge(balance_df, on=["ticker", "date"], how="left")

# Ensure ticker column exists before sorting
if "ticker" in merged_df.columns:
    merged_df = merged_df.sort_values(by=["ticker", "date"], ascending=[True, True])
else:
    merged_df = merged_df.sort_values(by=["date"], ascending=[True])

# Forward-fill missing values for financial data
merged_df = merged_df.ffill()

# Compute P/E ratio (Price-to-Earnings Ratio)
merged_df["earnings_per_share"] = merged_df["net_income"] / merged_df["share_capital"]
merged_df["p_e_ratio"] = merged_df["close"] / merged_df["earnings_per_share"]

# Compute 50-day Simple Moving Average (SMA)
merged_df["sma_50"] = merged_df.groupby("ticker")["close"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())

# Save merged dataset to GitHub repository path
merged_df.to_csv(csv_save_path, index=False)
st.write(f"✅ Data saved to {csv_filename} for further use.")

# Select date (default to today)
selected_date = st.date_input("Select a date:")

# Select required features
features = ["close", "p_e_ratio", "sma_50"]
latest_data = merged_df[merged_df["date"] == selected_date]

# Ensure valid data is available
if not latest_data.empty and all(col in latest_data.columns for col in features):
    X_latest = latest_data[features]

    # Make prediction
    predicted_movement = model.predict(X_latest)[0]
    prediction_label = "📈 Price Will Go UP" if predicted_movement == 1 else "📉 Price Will Go DOWN"

    # Display results
    st.subheader(f"📊 Prediction for AAPL on {selected_date}")
    st.metric(label="Market Movement Prediction", value=prediction_label)

    # Show actual market data for reference
    st.write("📌 Latest Market Data:")
    st.dataframe(latest_data[["date", "close", "p_e_ratio", "sma_50"]])
else:
    st.warning("⚠️ No valid data found for the selected date.")
