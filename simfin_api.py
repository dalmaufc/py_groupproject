import pandas as pd
import requests

API_KEY = "b7f5ad1b-6cd9-4f19-983b-cfddaad8df9c"  # Replace with your actual API key

def get_latest_stock_data(ticker, date):
    """
    Fetches real-time stock data from the SimFin API.
    Processes and returns features needed for prediction.
    """
    try:
        # Fetch share prices
        url_prices = f"https://simfin.com/api/v2/companies/prices?ticker={ticker}&api-key={API_KEY}"
        prices_data = requests.get(url_prices).json()
        
        # Fetch financial statements
        url_income = f"https://simfin.com/api/v2/companies/statements?statement=income&ticker={ticker}&api-key={API_KEY}"
        income_data = requests.get(url_income).json()
        
        # Convert to DataFrame
        df_prices = pd.DataFrame(prices_data)
        df_income = pd.DataFrame(income_data)

        # Process financial ratios
        df_prices["date"] = pd.to_datetime(df_prices["date"])
        df_income["date"] = pd.to_datetime(df_income["date"])

        # Merge datasets
        df = df_prices.merge(df_income, on=["date"], how="left")
        
        # Compute P/E ratio
        df["p_e_ratio"] = df["close"] / (df["net_income"] / df["shares_outstanding"])
        
        # Compute 50-day SMA
        df["sma_50"] = df["close"].rolling(window=50, min_periods=1).mean()

        # Filter for the selected date
        latest_data = df[df["date"] == date].copy()

        return latest_data

    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if an error occurs