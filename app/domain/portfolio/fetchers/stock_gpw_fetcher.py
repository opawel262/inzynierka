import yfinance as yf
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import pytz
from app.domain.portfolio.schemas import (
    FetcherStockGPWSchema,
    FetcherHistoricalStockSchema,
)

tickers = [
    "06N",
    "08N",
    "11B",
    "1AT",
    "3RG",
    "4MS",
]


class GPWStockFetcher:
    def __init__(
        self,
        tickers: List[str] = tickers,
        timezone: pytz.timezone = pytz.timezone("Europe/Warsaw"),
    ):
        self.tickers = [ticker + ".WA" for ticker in tickers]
        self.timezone = timezone

    def fetch_stock_data_by_ticker(self, ticker: str) -> Dict[str, Any]:

        try:
            spolka = yf.Ticker(ticker)
            info = spolka.info
            now = datetime.now(self.timezone)

            hist_for_day = spolka.history(period="1d", interval="5m")
            one_hour_ago = now - timedelta(hours=1)
            price_1h_ago = self._get_close_near_time(hist_for_day, one_hour_ago)

            hist_for_day = {
                "open_price": hist_for_day["Open"].iloc[0],
                "close_price": hist_for_day["Close"].iloc[0],
                "high_price": hist_for_day["High"].iloc[0],
                "low_price": hist_for_day["Low"].iloc[0],
                "volume": hist_for_day["Volume"].iloc[0],
                "interval": "5m",
                "period": "1d",
            }

            hist_for_7_days = spolka.history(period="7d", interval="30m")

            one_day_ago = now - timedelta(days=1)
            price_24h_ago = self._get_close_near_time(hist_for_7_days, one_day_ago)

            hist_for_7_days = {
                "open_price": hist_for_7_days["Open"].iloc[0],
                "close_price": hist_for_7_days["Close"].iloc[0],
                "high_price": hist_for_7_days["High"].iloc[0],
                "low_price": hist_for_7_days["Low"].iloc[0],
                "volume": hist_for_7_days["Volume"].iloc[0],
                "interval": "30m",
                "period": "7d",
            }

            hist_for_month = spolka.history(period="1mo", interval="4h")

            seven_days_ago = now - timedelta(days=7)
            price_7d_ago = self._get_close_near_time(hist_for_month, seven_days_ago)

            hist_for_month = {
                "open_price": hist_for_month["Open"].iloc[0],
                "close_price": hist_for_month["Close"].iloc[0],
                "high_price": hist_for_month["High"].iloc[0],
                "low_price": hist_for_month["Low"].iloc[0],
                "volume": hist_for_month["Volume"].iloc[0],
                "interval": "4h",
                "period": "1mo",
            }

            hist_for_year = spolka.history(period="1y", interval="1d")
            hist_for_year = {
                "open_price": hist_for_year["Open"].iloc[0],
                "close_price": hist_for_year["Close"].iloc[0],
                "high_price": hist_for_year["High"].iloc[0],
                "low_price": hist_for_year["Low"].iloc[0],
                "volume": hist_for_year["Volume"].iloc[0],
                "interval": "1d",
                "period": "1y",
            }

            hist_for_max = spolka.history(period="max", interval="1wk")
            hist_for_max = {
                "open_price": hist_for_max["Open"].iloc[0],
                "close_price": hist_for_max["Close"].iloc[0],
                "high_price": hist_for_max["High"].iloc[0],
                "low_price": hist_for_max["Low"].iloc[0],
                "volume": hist_for_max["Volume"].iloc[0],
                "interval": "1wk",
                "period": "max",
            }

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            symbol = info.get("symbol")
            name = info.get("shortName")
            sector = info.get("sector")
            volume = info.get("volume") or info.get("regularMarketVolume")
            market_cap = info.get("marketCap")
            market_state = info.get("marketState")
            description = info.get("longBusinessSummary")
            debt_to_equity = (info.get("debtToEquity"),)
            trailing_annual_dividend_yield = (info.get("trailingAnnualDividendYield"),)
            return_on_equity = (info.get("returnOnEquity"),)
            free_cashflow = (info.get("freeCashflow"),)
            payout_ratio = (info.get("payoutRatio"),)
            price_to_book = (info.get("priceToBook"),)
            price_to_sales = (info.get("priceToSalesTrailing12Months"),)
            eps_trailing_twelve_months = (info.get("epsTrailingTwelveMonths"),)
            beta = (info.get("beta"),)
            pe_ratio = (info.get("trailingPE"),)
            average_volume_10d = (info.get("averageVolume10days"),)
            employees = (info.get("fullTimeEmployees"),)

            price_change_percentage_1h = self._calculate_change(
                current_price, price_1h_ago
            )
            price_change_percentage_24h = self._calculate_change(
                current_price, price_24h_ago
            )
            price_change_percentage_7d = self._calculate_change(
                current_price, price_7d_ago
            )
            self.data_history = {
                "1d": hist_for_day,
                "7d": hist_for_7_days,
                "1mo": hist_for_month,
                "1y": hist_for_year,
                "max": hist_for_max,
            }
            return {
                "symbol": symbol,
                "name": name,
                "sector": sector,
                "price": current_price,
                "currency": "PLN",
                "volume_24h": volume,
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
            return df_filtered.iloc[-1]["Close"]
        else:
            return None

    def print_summary(self, data: List[Dict[str, Optional[float]]]) -> None:
        for item in data:
            print(f"\nTicker: {item['ticker']}")
            print(f"Nazwa: {item['name']}")
            print(f"Sektor: {item['sector']}")
            print(f"Aktualna cena: {item['current_price']} PLN")
            print(f"Wolumen: {item['volume']}")
            print(f"Kapitalizacja rynkowa: {item['market_cap']} PLN")
            print(
                f"Cena 1h temu: {item['price_1h_ago']} PLN, zmiana: {item['change_1h']}%"
            )
            print(
                f"📅 Cena 24h temu: {item['price_24h_ago']} PLN, zmiana: {item['change_24h']}%"
            )
            print(
                f"Cena 7 dni temu: {item['price_7d_ago']} PLN, zmiana: {item['change_7d']}%"
            )
