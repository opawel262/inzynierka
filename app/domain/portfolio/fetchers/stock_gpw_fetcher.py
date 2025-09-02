import yfinance as yf
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import pytz

import math


class GPWStockFetcher:
    def __init__(
        self,
        tickers: List[str] = [],
        timezone: pytz.timezone = pytz.timezone("Europe/Warsaw"),
    ):
        self.tickers = [ticker + ".WA" for ticker in tickers]
        self.timezone = timezone
        self._data_history: Dict[str, Any] = None

    def historical_data_from_last_fetch(self) -> dict:
        """
        Returns historical stock data as a `dict` object.

        The historical data is internally populated by the `fetch_stock_data_by_ticker`
        method, which must be called beforehand. If this method has not been called,
        the returned data may be outdated or empty.

        """
        if self._data_history is None or not self._data_history:
            raise ValueError(
                "Historical data is not available. Please call `fetch_stock_data_by_ticker` first."
            )
        return self._data_history

    def fetch_stock_data_by_ticker(self, ticker: str) -> Dict[str, Any]:

        try:
            spolka = yf.Ticker(ticker)
            info = spolka.info
            now = datetime.now(self.timezone)

            hist_for_day = spolka.history(period="1d", interval="1h")
            one_hour_ago = now - timedelta(hours=1)
            price_1h_ago = self._get_close_near_time(hist_for_day, one_hour_ago)
            hist_for_day = [
                {
                    "date": row.name,
                    "open_price": round(float(row["Open"]), 2),
                    "close_price": round(float(row["Close"]), 2),
                    "high_price": round(float(row["High"]), 2),
                    "low_price": round(float(row["Low"]), 2),
                    "volume": int(row["Volume"]),
                    "interval": "1h",
                    "period": "1d",
                }
                for _, row in hist_for_day.iterrows()
            ]

            hist_for_7_days = spolka.history(period="7d", interval="4h")

            one_day_ago = now - timedelta(days=1)
            price_24h_ago = self._get_close_near_time(hist_for_7_days, one_day_ago)
            hist_for_7_days = [
                {
                    "date": row.name,  # index to Datetime
                    "open_price": round(float(row["Open"]), 2),
                    "close_price": round(float(row["Close"]), 2),
                    "high_price": round(float(row["High"]), 2),
                    "low_price": round(float(row["Low"]), 2),
                    "volume": int(row["Volume"]),
                    "interval": "4h",
                    "period": "1w",
                }
                for _, row in hist_for_7_days.iterrows()
            ]

            hist_for_month = spolka.history(period="1mo", interval="1d")

            seven_days_ago = now - timedelta(days=7)
            price_7d_ago = self._get_close_near_time(hist_for_month, seven_days_ago)
            price_30d_ago = self.get_first_close_or_none(hist_for_month)
            hist_for_month = [
                {
                    "date": row.name,  # index to Datetime
                    "open_price": round(float(row["Open"]), 2),
                    "close_price": round(float(row["Close"]), 2),
                    "high_price": round(float(row["High"]), 2),
                    "low_price": round(float(row["Low"]), 2),
                    "volume": int(row["Volume"]),
                    "interval": "1d",
                    "period": "1m",
                }
                for _, row in hist_for_month.iterrows()
            ]

            hist_for_year = spolka.history(period="1y", interval="1wk")
            price_1y_ago = self.get_first_close_or_none(hist_for_year)
            hist_for_year = [
                {
                    "date": row.name,  # index to Datetime
                    "open_price": round(float(row["Open"]), 2),
                    "close_price": round(float(row["Close"]), 2),
                    "high_price": round(float(row["High"]), 2),
                    "low_price": round(float(row["Low"]), 2),
                    "volume": int(row["Volume"]),
                    "interval": "1w",
                    "period": "1y",
                }
                for _, row in hist_for_year.iterrows()
            ]

            hist_for_max = spolka.history(period="max", interval="1mo")
            price_max_ago = self.get_first_close_or_none(hist_for_max)
            hist_for_max = [
                {
                    "date": row.name,  # index to Datetime
                    "open_price": round(float(row["Open"]), 2),
                    "close_price": round(float(row["Close"]), 2),
                    "high_price": round(float(row["High"]), 2),
                    "low_price": round(float(row["Low"]), 2),
                    "volume": int(row["Volume"]),
                    "interval": "1mo",
                    "period": "max",
                }
                for _, row in hist_for_max.iterrows()
            ]
            price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            symbol = info.get("symbol")
            name = info.get("shortName")
            sector = info.get("sector")
            volume_24h = info.get("volume") or info.get("regularMarketVolume")
            market_cap = info.get("marketCap")
            market_state = info.get("marketState")
            description = info.get("longBusinessSummary")
            debt_to_equity = info.get("debtToEquity")
            trailing_annual_dividend_yield = info.get("trailingAnnualDividendYield")
            return_on_equity = info.get("returnOnEquity")
            free_cashflow = info.get("freeCashflow")
            payout_ratio = info.get("payoutRatio")
            price_to_book = info.get("priceToBook")
            price_to_sales = info.get("priceToSalesTrailing12Months")
            eps_trailing_twelve_months = info.get("epsTrailingTwelveMonths")
            beta = info.get("beta")
            pe_ratio = info.get("forwardPE") or info.get("trailingPE")
            if pe_ratio is not None and math.isinf(float(pe_ratio)):
                pe_ratio = None
            average_volume_10d = info.get("averageVolume10days")
            employees = info.get("fullTimeEmployees")
            circulating_supply = info.get("sharesOutstanding")
            price_change_percentage_1h = (
                self._calculate_change(price, price_1h_ago)
                if price_1h_ago is not None
                else 0
            )
            price_change_percentage_24h = (
                self._calculate_change(price, price_24h_ago)
                if price_24h_ago is not None
                else 0
            )
            price_change_percentage_7d = (
                self._calculate_change(price, price_7d_ago)
                if price_7d_ago is not None
                else 0
            )
            price_change_percentage_30d = (
                self._calculate_change(price, price_30d_ago)
                if price_30d_ago is not None
                else 0
            )
            price_change_percentage_1y = (
                self._calculate_change(price, price_1y_ago)
                if price_1y_ago is not None
                else 0
            )
            price_change_percentage_max = (
                self._calculate_change(price, price_max_ago)
                if price_max_ago is not None
                else 0
            )

            self._data_history = (
                hist_for_day
                + hist_for_7_days
                + hist_for_month
                + hist_for_year
                + hist_for_max
            )
            return {
                "symbol": symbol,
                "name": name,
                "sector": sector,
                "price": price,
                "currency": "PLN",
                "volume_24h": volume_24h,
                "market_cap": market_cap,
                "market_state": market_state,
                "description": description,
                "debt_to_equity": debt_to_equity,
                "trailing_annual_dividend_yield": trailing_annual_dividend_yield,
                "return_on_equity": return_on_equity,
                "free_cashflow": free_cashflow,
                "payout_ratio": payout_ratio,
                "price_to_book": price_to_book,
                "price_to_sales": price_to_sales,
                "eps_trailing_twelve_months": eps_trailing_twelve_months,
                "beta": beta,
                "pe_ratio": pe_ratio,
                "average_volume_10d": average_volume_10d,
                "employees": employees,
                "price_change_percentage_1h": price_change_percentage_1h,
                "price_change_percentage_24h": price_change_percentage_24h,
                "price_change_percentage_7d": price_change_percentage_7d,
                "price_change_percentage_30d": price_change_percentage_30d,
                "price_change_percentage_1y": price_change_percentage_1y,
                "price_change_percentage_max": price_change_percentage_max,
                "circulating_supply": circulating_supply,
            }

        except Exception as e:
            raise e

    @staticmethod
    def _calculate_change(
        current: Optional[float], previous: Optional[float]
    ) -> Optional[float]:
        if current is not None and previous:
            val = round((current - previous) / previous * 100, 2)
            return float(val)
        return None

    @staticmethod
    def _get_close_near_time(hist_df: pd.DataFrame, target_time: datetime):
        if hist_df.empty:
            return None

        hist_df = hist_df.copy()
        hist_df.index = pd.to_datetime(hist_df.index)

        df_filtered = hist_df[hist_df.index <= target_time]

        if not df_filtered.empty:
            return df_filtered.iloc[-1]["Open"]
        else:
            return None

    @staticmethod
    def get_first_close_or_none(df):
        if df is not None and not df.empty:
            return float(df.iloc[0]["Open"])
        return None
