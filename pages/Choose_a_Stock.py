import streamlit as st
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from simfin_api import SimFinAPI
from datetime import datetime, timedelta
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log', filemode='a')

# Set the Streamlit page configuration first!
st.set_page_config(page_title="Stock Market Live Analysis", layout="wide")

# API Key input at the top of the sidebar
st.sidebar.title("🔑 Enter your SimFin API Key")
api_key = st.sidebar.text_input("API Key", type="password")

# Store API key in session state
if api_key:
    st.session_state["SIMFIN_API_KEY"] = api_key
elif "SIMFIN_API_KEY" in st.session_state:
    api_key = st.session_state["SIMFIN_API_KEY"]
else:
    st.sidebar.warning("⚠️ Please enter your SimFin API key to proceed.")
    st.stop()  # Stop execution until user provides the API key

# Initialize SimFin API
logging.info("Initializing SimFin API")
api = SimFinAPI(api_key=api_key)

# Sidebar stock selection (below API key input)
st.sidebar.title("📊 Select a Stock")
stocks = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA']
selected_stock = st.sidebar.radio("Choose a stock:", stocks)
logging.info(f"Selected stock: {selected_stock}")

# Get company logo dynamically from GitHub
logo_url = api.get_company_logo(selected_stock)

# Display logo alongside page title
col1, col2 = st.columns([1, 6])  # Adjust column width for layout
with col1:
    try:
        st.image(logo_url, width=80)
    except Exception as e:
        st.warning(f"⚠️ Could not load logo for {selected_stock}")

with col2:
    st.title(f"Live Trading - {selected_stock}")

# Set time range
start_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
logging.info(f"Start date: {start_date}")

# Adjust end_date based on the weekday
today = datetime.today()
weekday = today.weekday()
if weekday == 0:  # Monday → Use last Friday's data
    end_date = (today - timedelta(days=3)).strftime("%Y-%m-%d")
elif weekday == 6:  # Sunday → Use last Friday's data
    end_date = (today - timedelta(days=2)).strftime("%Y-%m-%d")
else:  # Normal case: Use yesterday's data
    end_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
logging.info(f"End date: {end_date}")

# Fetch stock price data
st.write(f"📡 Fetching {selected_stock} stock data from SimFin API... Please wait.")
try:
    share_prices_df = api.get_share_prices(selected_stock, start_date, end_date)
    income_df = api.get_income_statement(selected_stock, start_date, end_date)
    balance_sheet_df = api.get_balance_sheet(selected_stock, start_date, end_date)
    shares_outstanding_df = api.get_shares_outstanding(selected_stock, start_date, end_date)
    logging.info("Successfully fetched stock data")
except Exception as e:
    logging.error(f"Error fetching data: {e}")
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

# Ensure data is not empty
if share_prices_df.empty or income_df.empty or balance_sheet_df.empty or shares_outstanding_df.empty:
    logging.warning("No stock data available")
    st.error("❌ No stock data available. Please try another stock or check back later.")
    st.stop()

# Convert date columns to datetime format
def convert_to_datetime(df, column):
    try:
        df[column] = pd.to_datetime(df[column])
    except Exception as e:
        logging.warning(f"Date conversion error: {e}")
        st.warning(f"⚠️ Date conversion error: {e}")
convert_to_datetime(share_prices_df, "date")
convert_to_datetime(income_df, "date")
convert_to_datetime(balance_sheet_df, "date")
convert_to_datetime(shares_outstanding_df, "date")

# Merge datasets
try:
    merged_df = share_prices_df.merge(income_df, on=["ticker", "date"], how="left")
    merged_df = merged_df.merge(balance_sheet_df, on=["ticker", "date"], how="left")
    merged_df = merged_df.merge(shares_outstanding_df, on=["ticker", "date"], how="left")
    logging.info("Successfully merged datasets")
except Exception as e:
    logging.error(f"Error merging data: {e}")
    st.error(f"❌ Error merging data: {e}")
    st.stop()

# Sort and forward-fill missing values
merged_df = merged_df.sort_values(by=["ticker", "date"], ascending=[True, True])
merged_df.ffill(inplace=True)

# Compute P/E ratio
try:
    merged_df["market_capitalization"] = merged_df["close"] * merged_df["shares_outstanding"]
    merged_df["p_e_ratio"] = merged_df["market_capitalization"] / merged_df["net_income"]
    merged_df["sma_50"] = merged_df.groupby("ticker")["close"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())
    logging.info("Successfully computed financial metrics")
except KeyError as e:
    logging.error(f"Missing necessary columns for calculations: {e}")
    st.error(f"❌ Missing necessary columns for calculations: {e}")
    st.stop()

# Add next day's close price as a target variable
merged_df["next_close"] = merged_df.groupby("ticker")["close"].shift(-1)

# Drop rows with missing values in critical columns
merged_df.dropna(subset=["close", "p_e_ratio", "sma_50"], inplace=True)

# Drop the fiscal_period column if it exists
if "fiscal_period" in merged_df.columns:
    merged_df = merged_df.drop(columns=["fiscal_period"])

# Drop the fiscal_year column if it exists
if "fiscal_year" in merged_df.columns:
    merged_df = merged_df.drop(columns=["fiscal_year"])

show_merged_df = merged_df

# Display only the last 10 rows
st.subheader(f"📊 API Live Data for {selected_stock} (Latest 10 Closing Data)")
show_merged_df["date"] = show_merged_df["date"].dt.date  # Converts to date format
st.dataframe(show_merged_df.set_index("date").tail(10))

# Load the trained XGBoost model
try:
    model = xgb.Booster()
    model.load_model("mag7_final_model.json")
    logging.info("Model successfully loaded")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    st.error(f"❌ Error loading model: {e}")
    st.stop()

# Convert 'date' column to datetime explicitly
merged_df["date"] = pd.to_datetime(merged_df["date"])

# Ensure yesterday's date is in correct format
yesterday_date = pd.to_datetime(end_date).date()

# Filter for yesterday's data
yesterday_df = merged_df[merged_df["date"] == pd.to_datetime(yesterday_date)][["ticker", "close", "p_e_ratio", "sma_50"]]

if not yesterday_df.empty:
    try:
        dmatrix = xgb.DMatrix(yesterday_df[["close", "p_e_ratio", "sma_50"]])
        prediction = model.predict(dmatrix)[0]
        prediction_label = "📈 Buy" if prediction > 0.5 else "📉 Sell"
        yesterday_df["Prediction"] = prediction_label
        logging.info(f"Prediction generated for next closing price: {prediction_label}")
        
        # Display predictions
        st.subheader("📊 Prediction for Next Closing Price Movement")
        st.write(f"🔮 **{prediction_label}** signal for {selected_stock}")
        st.dataframe(yesterday_df)
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        st.error(f"❌ Prediction error: {e}")

# Plot Closing Price Trend
st.subheader(f"📈 Closing Price Trend for {selected_stock} (Last Year)")
plt.figure(figsize=(10, 5))
plt.plot(share_prices_df["date"], share_prices_df["close"], label="Closing Price", color="blue")
plt.xlabel("Date")
plt.ylabel("Closing Price (USD)")
plt.title(f"{selected_stock} Closing Price Over the Last Year")
plt.legend()
st.pyplot(plt)

logging.info("Successfully plotted closing price trend")
