import requests
import pandas as pd
import time

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
        """Handles API requests with rate limiting and improved error handling."""
        self._respect_rate_limit()
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            try:
                return response.json()  # Return raw JSON if valid
            except ValueError:
                print("Error: Unable to parse JSON response.")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
    
    def _validate_response(self, data, required_keys):
        """Checks if the API response is valid and contains expected keys."""
        if not data or not isinstance(data, list) or len(data) == 0:
            return False
        if not all(key in data[0] for key in required_keys):
            print("Error: Unexpected API response format.")
            return False
        return True

    def get_share_prices(self, ticker, start_date, end_date):
        """Fetches daily share prices for a ticker using the v3 API."""
        url = f"{self.base_url}companies/prices/compact"
        params = {"ticker": ticker.upper(), "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not self._validate_response(data, ["columns", "data"]):
            return pd.DataFrame(columns=['date', 'ticker', 'close'])

        try:
            columns = data[0]["columns"]
            date_idx = columns.index("Date")
            close_idx = columns.index("Last Closing Price")

            processed_data = [
                {"date": pd.to_datetime(row[date_idx]), "ticker": ticker.upper(), "close": row[close_idx]}
                for row in data[0]["data"] if len(row) > close_idx
            ]
            return pd.DataFrame(processed_data).dropna().sort_values(by="date", ascending=True)
        except (ValueError, IndexError, KeyError):
            print("Error: Unable to extract expected share price data.")
            return pd.DataFrame(columns=['date', 'ticker', 'close'])

    def get_income_statement(self, ticker, start_date, end_date):
        """Fetches the income statement data for a ticker."""
        url = f"{self.base_url}companies/statements/compact"
        params = {"ticker": ticker.upper(), "statements": "PL", "period": "Q1,Q2,Q3,Q4", "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not self._validate_response(data, ["statements"]):
            return pd.DataFrame(columns=['ticker', 'date', 'fiscal_period', 'fiscal_year', 'revenue', 'net_income'])

        try:
            pl_statement = data[0]["statements"][0]
            columns = pl_statement["columns"]
            fiscal_period_idx = columns.index("Fiscal Period")
            fiscal_year_idx = columns.index("Fiscal Year")
            report_date_idx = columns.index("Report Date")
            revenue_idx = columns.index("Revenue")
            net_income_idx = columns.index("Net Income")

            processed_data = [
                {
                    "ticker": ticker.upper(),
                    "date": pd.to_datetime(row[report_date_idx], errors='coerce'),
                    "fiscal_period": row[fiscal_period_idx],
                    "fiscal_year": row[fiscal_year_idx],
                    "revenue": pd.to_numeric(row[revenue_idx], errors='coerce'),
                    "net_income": pd.to_numeric(row[net_income_idx], errors='coerce')
                }
                for row in pl_statement["data"] if len(row) > max(report_date_idx, revenue_idx, net_income_idx)
            ]
            return pd.DataFrame(processed_data).dropna().sort_values(by="date", ascending=True)
        except (ValueError, IndexError, KeyError):
            print("Error: Unable to extract expected income statement data.")
            return pd.DataFrame(columns=['ticker', 'date', 'fiscal_period', 'fiscal_year', 'revenue', 'net_income'])

    def get_shares_outstanding(self, ticker, start_date, end_date):
        """Fetches common shares outstanding for a ticker."""
        url = f"{self.base_url}companies/common-shares-outstanding"
        params = {"ticker": ticker.upper(), "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not data or not isinstance(data, list):
            print(f"No shares outstanding data for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame(columns=['date', 'ticker', 'shares_outstanding'])

        try:
            processed_data = [
                {"date": pd.to_datetime(entry["endDate"]), "ticker": ticker.upper(), "shares_outstanding": entry["value"]}
                for entry in data if "endDate" in entry and "value" in entry
            ]
            return pd.DataFrame(processed_data).dropna().sort_values(by="date", ascending=True)
        except (KeyError, TypeError):
            print("Error: Unexpected format in shares outstanding data.")
            return pd.DataFrame(columns=['date', 'ticker', 'shares_outstanding'])
