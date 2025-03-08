import streamlit as st
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from simfin_api import SimFinAPI  # Import your API wrapper
from datetime import datetime, timedelta
import os

# Initialize SimFin API (Replace with your valid API key)
api = SimFinAPI(api_key="b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c")

# Define parameters
stocks = ['AAPL']
start_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")  # Set start date to one year ago
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
shares_outstanding_df = api.get_shares_outstanding(selected_stock, start_date, end_date)

# Convert date columns to datetime format
share_prices_df["date"] = pd.to_datetime(share_prices_df["date"])
income_df["date"] = pd.to_datetime(income_df["date"])
balance_sheet_df["date"] = pd.to_datetime(balance_sheet_df["date"])
shares_outstanding_df["date"] = pd.to_datetime(shares_outstanding_df["date"])

# Merge datasets
merged_df = share_prices_df.merge(income_df, on=["ticker", "date"], how="left")
merged_df = merged_df.merge(balance_sheet_df, on=["ticker", "date"], how="left")
merged_df = merged_df.merge(shares_outstanding_df, on=["ticker", "date"], how="left")

# Drop the fiscal_period column if it exists
if "fiscal_period" in merged_df.columns:
    merged_df = merged_df.drop(columns=["fiscal_period"])

# Sort and forward-fill missing values
merged_df = merged_df.sort_values(by=["ticker", "date"], ascending=[True, True])
merged_df.ffill(inplace=True)

# Compute P/E ratio
merged_df["market_capitalization"] = merged_df["close"] * merged_df["shares_outstanding"]
merged_df["p_e_ratio"] = merged_df["market_capitalization"] / merged_df["net_income"]

# Compute 50-day Simple Moving Average (SMA)
merged_df["sma_50"] = merged_df.groupby("ticker")["close"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())

# Add next day's close price as a target variable
merged_df["next_close"] = merged_df.groupby("ticker")["close"].shift(-1)

# Drop rows where critical features contain NaN values
merged_df = merged_df.dropna(subset=["close", "p_e_ratio", "sma_50"])
