import streamlit as st
import pandas as pd
import xgboost as xgb
from simfin_api import SimFinAPI  # Import your API wrapper
from datetime import datetime, timedelta
import os

# Initialize SimFin API (Replace with your valid API key)
api = SimFinAPI(api_key="b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c")

# Define parameters
stocks = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA']
start_date = "2024-01-01"
end_date = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")  # Always set to yesterday

# Load the trained XGBoost model
model = xgb.Booster()
model.load_model("mag7_final_model.json")

# Streamlit UI
st.title("📈 Stock Movement Prediction App")

# Fetch data for each stock
df_list = []
for ticker in stocks:
    st.write(f"📡 Fetching {ticker} stock data from SimFin API... Please wait.")
    
    # Fetch stock price data
    share_prices_df = api.get_share_prices(ticker, start_date, end_date)
    
    # Fetch financial data
    income_df = api.get_income_statement(ticker, start_date, end_date)
    balance_sheet_df = api.get_balance_sheet(ticker, start_date, end_date)
    
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
    
    df_list.append(yesterday_df)

# Combine results for all stocks
final_df = pd.concat(df_list, ignore_index=True)

# Display predictions
st.write("📊 Stock Predictions for Yesterday:")
st.dataframe(final_df)

