import streamlit as st
import pandas as pd
import xgboost as xgb
from simfin_api import SimFinAPI  # Import your API wrapper
from datetime import datetime, timedelta
import os

import requests
import pandas as pd
from simfin_api import SimFinAPI

# Initialize SimFin API (Replace with your valid API key)
api = SimFinAPI(api_key="b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c")

# Define parameters
ticker = "AAPL"
start_date = "2024-01-01"
end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")  # Always set to yesterday

# Fetch stock price data
print("\n🔍 Testing Share Prices API...")
share_prices_df = api.get_share_prices(ticker, start_date, end_date)
print(share_prices_df.head())

# Fetch income statement data
print("\n🔍 Testing Income Statement API...")
income_df = api.get_income_statement(ticker, start_date, end_date)
print(income_df.head())

# Fetch balance sheet data
print("\n🔍 Testing Balance Sheet API...")
balance_sheet_df = api.get_balance_sheet(ticker, start_date, end_date)
print(balance_sheet_df.head())

# Convert date columns to datetime format for proper merging
share_prices_df["date"] = pd.to_datetime(share_prices_df["date"])
income_df["date"] = pd.to_datetime(income_df["date"])
balance_sheet_df["date"] = pd.to_datetime(balance_sheet_df["date"])

# Merge datasets using a left join on ticker and date
merged_df = share_prices_df.merge(income_df, on=["ticker", "date"], how="left")
merged_df = merged_df.merge(balance_sheet_df, on=["ticker", "date"], how="left")

# Sort by ticker and date (most recent to oldest)
merged_df = merged_df.sort_values(by=["ticker", "date"], ascending=[True, True])

# Forward-fill missing values for financial data
merged_df.ffill(inplace=True)

# Compute P/E ratio (Price-to-Earnings Ratio)
merged_df["earnings_per_share"] = merged_df["net_income"] / merged_df["share_capital"]
merged_df["p_e_ratio"] = merged_df["close"] / merged_df["earnings_per_share"]

# Compute 50-day Simple Moving Average (SMA)
merged_df["sma_50"] = merged_df.groupby("ticker")["close"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())

# Add next day's close price as a target variable
merged_df["next_close"] = merged_df.groupby("ticker")["close"].shift(-1)

# Drop rows where critical features contain NaN values
merged_df = merged_df.dropna(subset=["close", "p_e_ratio", "sma_50"])

# Display the dataset for verification
st.write("📌 Processed Dataset Preview:")
st.dataframe(merged_df.tail(20))


