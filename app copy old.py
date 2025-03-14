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

# Dictionary mapping stocks to their logo file paths
logo_paths = {
    "AAPL": "/mnt/data/AAPL.png",
    "MSFT": "/mnt/data/MSFT.png",
    "GOOG": "/mnt/data/GOOG.png",
    "AMZN": "/mnt/data/AMZN.png",
    "NVDA": "/mnt/data/NVDA.png",
    "META": "/mnt/data/META.png",
    "TSLA": "/mnt/data/TSLA.png",
}

# Display company logo instead of emoji
col1, col2 = st.columns([1, 6])  # Layout columns for logo and title
with col1:
    if selected_stock in logo_paths and os.path.exists(logo_paths[selected_stock]):
        st.image(logo_paths[selected_stock], width=80)
    else:
        st.warning(f"⚠️ Logo not found for {selected_stock}")

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
    logging.info("Successfully fetched stock data")
except Exception as e:
    logging.error(f"Error fetching data: {e}")
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

# Ensure data is not empty
if share_prices_df.empty:
    logging.warning("No stock data available")
    st.error("❌ No stock data available. Please try another stock or check back later.")
    st.stop()

# Convert date column to datetime format
share_prices_df["date"] = pd.to_datetime(share_prices_df["date"])

# Display only the last 10 rows
st.subheader(f"📊 API Live Data for {selected_stock} (Latest 10 Closing Data)")
share_prices_df["date"] = share_prices_df["date"].dt.date  # Converts to date format
st.dataframe(share_prices_df.set_index("date").tail(10))

# Load the trained XGBoost model
try:
    model = xgb.Booster()
    model.load_model("mag7_final_model.json")
    logging.info("Model successfully loaded")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    st.error(f"❌ Error loading model: {e}")
    st.stop()

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
