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

# Debugging: Check if file exists
def check_file_exists(file_path):
    return os.path.exists(file_path)

# Display company logo instead of emoji
col1, col2 = st.columns([1, 6])  # Layout columns for logo and title
with col1:
    logo_path = logo_paths.get(selected_stock, "")
    if check_file_exists(logo_path):
        st.image(logo_path, width=80)
    else:
        st.warning(f"⚠️ Logo not found for {selected_stock} at {logo_path}")

with col2:
    st.title(f"Live Trading - {selected_stock}")

