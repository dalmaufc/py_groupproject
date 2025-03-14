import streamlit as st
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from simfin_api import SimFinAPI
from datetime import datetime, timedelta
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

# **GitHub Repository Base URL for Logos**
GITHUB_BASE_URL = "https://raw.githubusercontent.com/dalmaufc/py_groupproject/tree/logos"

# Construct the URL for the selected stock's logo
logo_url = f"{GITHUB_BASE_URL}/{selected_stock}.png"

# Display company logo instead of emoji
col1, col2 = st.columns([1, 6])  # Layout columns for logo and title
with col1:
    try:
        st.image(logo_url, width=80)
    except Exception as e:
        st.warning(f"⚠️ Could not load logo for {selected_stock}")

with col2:
    st.title(f"Live Trading - {selected_stock}")

