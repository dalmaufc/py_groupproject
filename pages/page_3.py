import streamlit as st
import pandas as pd
import xgboost as xgb
from simfin_api import SimFinAPI  # Import your API wrapper
from datetime import datetime, timedelta
import os

# Initialize SimFin API (Replace with your valid API key)
api = SimFinAPI(api_key="b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c")

# Define parameters
stocks = ['GOOG']
start_date = "2024-01-01"
end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")  # Always set to yesterday

# Load the trained XGBoost model
model = xgb.Booster()
model.load_model("mag7_final_model.json")

# Streamlit UI
st.set_page_config(page_title="Stock Movement Prediction", layout="wide")
st.sidebar.title("📊 Select a Stock")
selected_stock = st.sidebar.radio("Choose a stock:", stocks)

# Fetch data for the selected stock
st.title(f"📈 {selected_stock} Stock Movement Prediction")
st.write(f"📡 Fetching {selected_stock} stock data from SimFin API... Please wait.")

# Fetch stock price data
share_prices_df = api.get_share_prices(selected_stock, start_date, end_date)

# Fetch financial data
income_df = api.get_income_statement(selected_stock, start_date, end_date)
balance_sheet_df = api.get_balance_sheet(selected_stock, start_date, end_date)

# Convert date columns to datetime format
share_prices_df["date"] = pd.to_datetime(share_prices_df["date"])
income_df["date"] = pd.to_datetime(income_df["date"])
balance_sheet_df["date"] = pd.to_datetime(balance_sheet_df["date"])

# Merge datasets
merged_df = share_prices_df.merge(income_df, on=["ticker", "date"], how="left")
merged_df = merged_df.merge(balance_sheet_df, on=["ticker", "date"], how="left")

# Sort and forward-fill missing values
merged_df = merged_df.sort_values(by=["ticker", "date"], ascending=[True, True])
merged_df.ffill(inplace=True)

# Compute P/E ratio
merged_df["earnings_per_share"] = merged_df["net_income"] / merged_df["share_capital"]
merged_df["p_e_ratio"] = merged_df["close"] / merged_df["earnings_per_share"]

# Compute 50-day SMA
merged_df["sma_50"] = merged_df.groupby("ticker")["close"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())

# Add next day's close price as a target variable
merged_df["next_close"] = merged_df.groupby("ticker")["close"].shift(-1)

# Drop rows where critical features contain NaN values
merged_df = merged_df.dropna(subset=["close", "p_e_ratio", "sma_50"])

# Create a second DataFrame for yesterday's data
yesterday_date = pd.to_datetime(end_date)
yesterday_df = merged_df[merged_df["date"] == yesterday_date][["ticker", "close", "p_e_ratio", "sma_50"]]

if not yesterday_df.empty:
    # Make a prediction using the model
    dmatrix = xgb.DMatrix(yesterday_df[["close", "p_e_ratio", "sma_50"]])
    prediction = model.predict(dmatrix)[0]
    
    # Determine if the price is expected to go up or down
    prediction_label = "📈 Up" if prediction > 0.5 else "📉 Down"
    yesterday_df["Prediction"] = prediction_label
    
    # Display results
    st.write("📊 Data for Yesterday:")
    st.dataframe(yesterday_df)
    st.subheader("📊 Prediction for Today's Close Price Movement")
    st.write(f"🔮 The model predicts: **{prediction_label}**")
else:
    st.warning("⚠️ No data available for yesterday.")