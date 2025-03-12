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
        """Handles API requests with rate limiting and error handling."""
        self._respect_rate_limit()
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Ensure the response is in expected format
            if not isinstance(data, list):
                raise ValueError(f"Unexpected response format: {data}")

            return data  # Return raw JSON

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            print("Error: Connection issue. Please check your internet connection.")
        except requests.exceptions.Timeout:
            print("Error: Request timed out. Try again later.")
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
        except ValueError as e:
            print(f"Data Format Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
        
        return []

    def _extract_columns(self, data, expected_columns):
        """Helper function to extract required column indices from API response."""
        if not data or "columns" not in data[0]:
            print("Error: Missing column information in API response.")
            return {}

        columns = data[0]["columns"]
        try:
            indices = {col: columns.index(col) for col in expected_columns}
        except ValueError as e:
            print(f"Error: Missing expected column in API response. {e}")
            return {}

        return indices

    def get_share_prices(self, ticker, start_date, end_date):
        """Fetches daily share prices for a ticker using the v3 API."""
        url = f"{self.base_url}companies/prices/compact"
        params = {"ticker": ticker.upper(), "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        indices = self._extract_columns(data, ["Date", "Last Closing Price"])
        if not indices:
            return pd.DataFrame(columns=['date', 'ticker', 'close'])

        processed_data = [
            {
                "date": pd.to_datetime(row[indices["Date"]], errors='coerce'),
                "ticker": ticker.upper(),
                "close": pd.to_numeric(row[indices["Last Closing Price"]], errors='coerce')
            }
            for row in data[0].get("data", []) if len(row) > max(indices.values())
        ]

        df = pd.DataFrame(processed_data).dropna()
        return df.sort_values(by="date", ascending=True)

    def get_income_statement(self, ticker, start_date, end_date):
        """Fetches the income statement data for a ticker."""
        url = f"{self.base_url}companies/statements/compact"
        params = {"ticker": ticker.upper(), "statements": "PL", "period": "Q1,Q2,Q3,Q4", "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not data or "statements" not in data[0] or not data[0]["statements"]:
            print(f"No income data for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame(columns=['ticker', 'date', 'fiscal_period', 'fiscal_year', 'revenue', 'net_income'])

        statements = data[0]["statements"][0]
        indices = self._extract_columns([statements], ["Fiscal Period", "Fiscal Year", "Report Date", "Revenue", "Net Income"])
        if not indices:
            return pd.DataFrame(columns=['ticker', 'date', 'fiscal_period', 'fiscal_year', 'revenue', 'net_income'])

        processed_data = [
            {
                "ticker": ticker.upper(),
                "date": pd.to_datetime(row[indices["Report Date"]], errors='coerce'),
                "fiscal_period": row[indices["Fiscal Period"]],
                "fiscal_year": row[indices["Fiscal Year"]],
                "revenue": pd.to_numeric(row[indices["Revenue"]], errors='coerce'),
                "net_income": pd.to_numeric(row[indices["Net Income"]], errors='coerce')
            }
            for row in statements.get("data", []) if len(row) > max(indices.values())
        ]

        df = pd.DataFrame(processed_data).dropna()
        return df.sort_values(by="date", ascending=True)

    def get_balance_sheet(self, ticker, start_date, end_date):
        """Fetches balance sheet data for a ticker."""
        url = f"{self.base_url}companies/statements/compact"
        params = {"ticker": ticker.upper(), "statements": "BS", "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not data or "statements" not in data[0] or not data[0]["statements"]:
            print(f"No balance sheet data for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame(columns=['ticker', 'date', 'totalLiabilities', 'totalEquity', 'share_capital'])

        statements = data[0]["statements"][0]
        indices = self._extract_columns([statements], ["Report Date", "Total Liabilities", "Total Equity", "Share Capital & Additional Paid-In Capital"])
        if not indices:
            return pd.DataFrame(columns=['ticker', 'date', 'totalLiabilities', 'totalEquity', 'share_capital'])

        processed_data = [
            {
                "date": pd.to_datetime(row[indices["Report Date"]], errors='coerce'),
                "ticker": ticker.upper(),
                "totalLiabilities": pd.to_numeric(row[indices["Total Liabilities"]], errors='coerce'),
                "totalEquity": pd.to_numeric(row[indices["Total Equity"]], errors='coerce'),
                "share_capital": pd.to_numeric(row[indices["Share Capital & Additional Paid-In Capital"]], errors='coerce')
            }
            for row in statements.get("data", []) if len(row) > max(indices.values())
        ]

        df = pd.DataFrame(processed_data).dropna()
        return df.sort_values(by="date", ascending=True)

    def get_shares_outstanding(self, ticker, start_date, end_date):
        """Fetches common shares outstanding for a ticker."""
        url = f"{self.base_url}companies/common-shares-outstanding"
        params = {"ticker": ticker.upper(), "start": start_date, "end": end_date}
        data = self._make_request(url, params)

        if not data or not isinstance(data, list):
            print(f"No shares outstanding data for {ticker} between {start_date} and {end_date}")
            return pd.DataFrame(columns=['date', 'ticker', 'shares_outstanding'])

        processed_data = [
            {"date": pd.to_datetime(entry.get("endDate"), errors='coerce'), "ticker": ticker.upper(), "shares_outstanding": pd.to_numeric(entry.get("value"), errors='coerce')}
            for entry in data if entry.get("endDate") and entry.get("value") is not None
        ]

        df = pd.DataFrame(processed_data).dropna()
        return df.sort_values(by="date", ascending=True)
