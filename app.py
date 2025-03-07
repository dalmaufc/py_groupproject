import streamlit as st
import pandas as pd
import xgboost as xgb
from simfin_api import SimFinAPI  # Import your API wrapper
from datetime import datetime, timedelta
import os

# Initialize SimFin API
api = SimFinAPI(api_key="b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c")  # Replace with your actual key

# Define end date as yesterday
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

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

# Display the dataset for verification
st.write("📌 Processed Dataset Preview:")
st.dataframe(merged_df.head(20))


st.write(f"📊 Stock Prices Data: {prices_df.shape}")
st.write(f"📊 Income Statement Data: {income_df.shape}")
st.write(f"📊 Balance Sheet Data: {balance_df.shape}")




st.write(f"📊 Merged Dataset Shape: {merged_df.shape}")
st.write("📆 Available Dates in Merged Data:", merged_df["date"].dropna().unique())



st.write(f"📊 Earliest Date: {merged_df['date'].min()}")
st.write(f"📊 Latest Date: {merged_df['date'].max()}")