import streamlit as st
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from simfin_api import SimFinAPI  # Import your API wrapper
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv('keys.env')

# Retrieve API key securely
api_key = os.getenv("SIMFIN_API_KEY")

# Initialize SimFin API
api = SimFinAPI(api_key=api_key)

# Define parameters
stocks = ['TSLA']
start_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")  # Set start date to one year ago
# Get today's date and determine the stock market's last available trading day
today = datetime.today()
weekday = today.weekday()  # Monday = 0, Sunday = 6


# Adjust end_date based on the weekday
if weekday == 0:  # Today is Monday → Use last Friday's data
    end_date = (today - timedelta(days=3)).strftime("%Y-%m-%d")
elif weekday == 6:  # Today is Sunday → Use last Friday's data
    end_date = (today - timedelta(days=2)).strftime("%Y-%m-%d")
else:  # Normal case: Use yesterday's data
    end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")

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


# Sort and forward-fill missing values
merged_df = merged_df.sort_values(by=["ticker", "date"], ascending=[True, True])
merged_df.ffill(inplace=True)

# Compute P/E ratio
merged_df["market_capitalization"] = merged_df["close"] * merged_df["shares_outstanding"]
merged_df["p_e_ratio"] = merged_df["market_capitalization"] / merged_df["net_income"]

# Compute 50-day SMA
merged_df["sma_50"] = merged_df.groupby("ticker")["close"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())

# Add next day's close price as a target variable
merged_df["next_close"] = merged_df.groupby("ticker")["close"].shift(-1)

# Drop rows where critical features contain NaN values
merged_df = merged_df.dropna(subset=["close", "p_e_ratio", "sma_50"])

# Drop the fiscal_period column if it exists
if "fiscal_period" in merged_df.columns:
    merged_df = merged_df.drop(columns=["fiscal_period"])

if not merged_df.empty:
    st.dataframe(merged_df)

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

# Plot Closing Price Trend
st.subheader(f"📈 Closing Price Trend for {selected_stock} (Last Year)")
plt.figure(figsize=(10, 5))
plt.plot(merged_df["date"], merged_df["close"], label="Closing Price", color="blue")
plt.xlabel("Date")
plt.ylabel("Closing Price (USD)")
plt.title(f"{selected_stock} Closing Price Over the Last Year")
plt.legend()
st.pyplot(plt)
