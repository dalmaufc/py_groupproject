import requests
import pandas as pd
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimFinAPI:
    """
    A simple API wrapper for SimFin v3, handling share prices, income statements, and balance sheets.
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://backend.simfin.com/api/v3/"
        self.headers = {
            "Authorization": f"{self.api_key}",
            "accept": "application/json"
        }
        self.rate_limit = 0.5  # Respect SimFin's API rate limit (2 requests/sec)

    def _respect_rate_limit(self):
        """Ensures requests comply with SimFin's rate limits."""
        time.sleep(self.rate_limit)

    def _make_request(self, url, params=None):
        """Handles API requests with rate limiting, error handling, and logging."""
        self._respect_rate_limit()
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            logging.error("Error: Network problem (e.g., DNS failure, refused connection). Check your connection.")
        except requests.exceptions.Timeout:
            logging.error("Error: Request timed out. Consider retrying later.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
        return []
    
    def get_share_prices(self, ticker, start_date, end_date):
        """Fetches daily share prices for a ticker using the v3 API."""
        url = f"{self.base_url}companies/prices/compact"
        params = {"ticker": ticker.upper(), "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not data:
            logging.warning(f"No price data for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame(columns=['date', 'ticker', 'close'])

        columns = data[0].get("columns", [])
        try:
            date_idx = columns.index("Date")
            close_idx = columns.index("Last Closing Price")
        except ValueError:
            logging.error("Error: Expected columns not found in API response.")
            return pd.DataFrame(columns=['date', 'ticker', 'close'])

        processed_data = [
            {"date": pd.to_datetime(row[date_idx]), "ticker": ticker.upper(), "close": row[close_idx]}
            for row in data[0].get("data", []) if len(row) > close_idx
        ]

        df = pd.DataFrame(processed_data).dropna()
        return df.sort_values(by="date", ascending=True)
    
    def get_income_statement(self, ticker, start_date, end_date):
        """Fetches the income statement data for a ticker."""
        url = f"{self.base_url}companies/statements/compact"
        params = {"ticker": ticker.upper(), "statements": "PL", "period": "Q1,Q2,Q3,Q4", "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not data:
            logging.warning(f"No income data for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame(columns=['ticker', 'date', 'fiscal_period', 'fiscal_year', 'revenue', 'net_income'])
        
        statements = data[0].get("statements", [])
        if not statements:
            logging.warning("No statement data found in API response.")
            return pd.DataFrame(columns=['ticker', 'date', 'fiscal_period', 'fiscal_year', 'revenue', 'net_income'])
        
        pl_statement = statements[0]
        columns = pl_statement.get("columns", [])
        try:
            fiscal_period_idx = columns.index("Fiscal Period")
            fiscal_year_idx = columns.index("Fiscal Year")
            report_date_idx = columns.index("Report Date")
            revenue_idx = columns.index("Revenue")
            net_income_idx = columns.index("Net Income")
        except ValueError:
            logging.error("Error: Expected columns not found in API response.")
            return pd.DataFrame(columns=['ticker', 'date', 'fiscal_period', 'fiscal_year', 'revenue', 'net_income'])

        processed_data = [
            {
                "ticker": ticker.upper(),
                "date": pd.to_datetime(row[report_date_idx], errors='coerce'),
                "fiscal_period": row[fiscal_period_idx],
                "fiscal_year": row[fiscal_year_idx],
                "revenue": pd.to_numeric(row[revenue_idx], errors='coerce'),
                "net_income": pd.to_numeric(row[net_income_idx], errors='coerce')
            }
            for row in pl_statement.get("data", []) if len(row) > max(report_date_idx, revenue_idx, net_income_idx)
        ]

        df = pd.DataFrame(processed_data).dropna()
        return df.sort_values(by="date", ascending=True)
    
    def get_balance_sheet(self, ticker, start_date, end_date):
        """Fetches balance sheet data for a ticker."""
        url = f"{self.base_url}companies/statements/compact"
        params = {"ticker": ticker.upper(), "statements": "BS", "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not data:
            logging.warning(f"No balance sheet data for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame(columns=['ticker', 'date', 'totalLiabilities', 'totalEquity', 'share_capital'])
        
        statements = data[0].get("statements", [])
        if not statements:
            logging.warning("No statement data found in API response.")
            return pd.DataFrame(columns=['ticker', 'date', 'totalLiabilities', 'totalEquity', 'share_capital'])
        
        bs_statement = statements[0]
        columns = bs_statement.get("columns", [])
        try:
            date_idx = columns.index("Report Date")
            liabilities_idx = columns.index("Total Liabilities")
            equity_idx = columns.index("Total Equity")
            share_capital_idx = columns.index("Share Capital & Additional Paid-In Capital")
        except ValueError:
            logging.error("Error: Expected columns not found in API response.")
            return pd.DataFrame(columns=['ticker', 'date', 'totalLiabilities', 'totalEquity', 'share_capital'])

        processed_data = [
            {
                "date": pd.to_datetime(row[date_idx], errors='coerce'),
                "ticker": ticker.upper(),
                "totalLiabilities": pd.to_numeric(row[liabilities_idx], errors='coerce'),
                "totalEquity": pd.to_numeric(row[equity_idx], errors='coerce'),
                "share_capital": pd.to_numeric(row[share_capital_idx], errors='coerce')
            }
            for row in bs_statement.get("data", []) if len(row) > max(date_idx, liabilities_idx, equity_idx, share_capital_idx)
        ]
        df = pd.DataFrame(processed_data).dropna()
        return df.sort_values(by="date", ascending=True)

