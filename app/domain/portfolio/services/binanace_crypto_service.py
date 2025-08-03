from typing import List, Dict, Any
from app.domain.portfolio.fetchers.crypto_fetchers import BinanaceCryptoFetcher
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.schemas import FetcherHistoricalCryptoRecordSchema


class BinanaceCryptoService:
    def __init__(self, fetcher: BinanaceCryptoFetcher, repository: CryptoRepository):
        self.fetcher = fetcher
        self.repository = repository

    def fetch_and_save_historical_crypto_data(self):
        cryptos = self.repository.get_all_crypto()
        historical_data_list = []
        for crypto in cryptos:
            historical_data = self.fetcher.fetch_historical_crypto_data(crypto.symbol)
            historical_data_list.append(historical_data)
            if not historical_data:
                continue

            for data_point in historical_data:
                validated_data = FetcherHistoricalCryptoRecordSchema(
                    **data_point
                ).model_dump()

                if self.repository.get_crypto_historical_prices_by_symbol_period_date(
                    symbol=crypto.symbol,
                    period=validated_data["period"],
                    date=validated_data["date"],
                ):
                    continue
                self.repository.create_crypto_historical_price(crypto, validated_data)

        return historical_data_list
