import requests
import pandas as pd
from simfin_api import SimFinAPI

# Initialize SimFin API (Replace with your valid API key)
api = SimFinAPI(api_key="b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c")  

# Define parameters
ticker = "AAPL"
start_date = "2024-01-01"
end_date = "2024-12-31"

# Fetch stock price data
print("🔍 Testing Share Prices API...")
share_prices_df = api.get_share_prices(ticker, start_date, end_date)
print(share_prices_df.head())

# Fetch income statement data
print("🔍 Testing Income Statement API...")
income_df = api.get_income_statement(ticker, start_date, end_date)
print(income_df.head())

# Fetch balance sheet data
print("🔍 Testing Balance Sheet API...")
balance_df = api.get_balance_sheet(ticker, start_date, end_date)
print(balance_df.head())

# Save results for further inspection
print("🔍 Testing Shares Outstanding API...")
shares_outstanding_df = api.get_shares_outstanding(ticker, start_date, end_date)
print(shares_outstanding_df.head())