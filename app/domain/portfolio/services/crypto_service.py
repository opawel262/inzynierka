from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.models import Crypto, CryptoHistoricalPrice

from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from datetime import datetime, timedelta


class CryptoService:
    def __init__(self, repository: CryptoRepository):
        self.repository = repository

    def search_cryptos(self, search: str | None) -> List[Crypto]:
        if search:
            search = search.lower()
            cryptos = self.repository.get_cryptos_by_name_or_symbol_alike(
                name_or_symbol=search
            )
        else:
            cryptos = self.repository.get_all_cryptos()
        return cryptos

    def get_crypto_by_symbol(self, symbol: str) -> Crypto | None:
        return self.repository.get_crypto_by_symbol(symbol=symbol)

    def get_crypto_historical_by_symbol_period_data_from_last(
        self, symbol: str, period: str
    ) -> List[CryptoHistoricalPrice]:

        if (
            period == "1d"
        ):  # There is no option in endpoint for this but it can be changed it later
            from_date = datetime.now() - timedelta(days=1)
        elif period == "1h":
            from_date = datetime.now() - timedelta(hours=1)
        elif period == "1w":
            from_date = datetime.now() - timedelta(weeks=1)
        elif period == "1m":
            from_date = datetime.now() - timedelta(days=30)
        elif period == "1y":
            from_date = datetime.now() - timedelta(days=365)
        else:
            from_date = datetime.now() - timedelta(days=1)
        to_date = datetime.now()

        historical_prices = (
            self.repository.get_crypto_historical_prices_by_symbol_period_from_to_date(
                symbol=symbol,
                period=period,
                from_date=from_date,
                to_date=to_date,
            )
        )

        return historical_prices

    def get_crypto_historical_by_symbol_data_from_last_max(
        self, symbol: str
    ) -> List[CryptoHistoricalPrice]:
        historical_prices = (
            self.repository.get_crypto_historical_prices_by_symbol_period(
                symbol=symbol,
                period="max",
            )
        )

        return historical_prices

    def get_global_performance_data(self) -> Dict[str, Any]:
        cryptos = self.repository.get_all_cryptos()

        total_volume_24h = sum(c.volume_24h or 0 for c in cryptos)
        total_market_cap = sum(c.market_cap or 0 for c in cryptos)
        top_gainers_24h = self.repository.get_cryptos_biggest_gainers()
        top_losers_24h = self.repository.get_cryptos_biggest_losers()
        top_biggest_market_cap = self.repository.get_cryptos_biggest_market_cap()

        return {
            "total_volume_24h": total_volume_24h,
            "total_market_cap": total_market_cap,
            "top_gainers_24h": top_gainers_24h,
            "top_losers_24h": top_losers_24h,
            "top_market_cap_rank": top_biggest_market_cap,
        }
