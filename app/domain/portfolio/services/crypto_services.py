from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.models import Crypto, CryptoHistoricalPrice
from app.domain.portfolio.fetchers.crypto_fetchers import (
    CoinGeckoCryptoFetcher,
    BinanaceCryptoFetcher,
)
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.schemas import (
    FetcherCoinGeckoCryptoSchema,
    FetcherHistoricalCryptoRecordSchema,
)


class CoinGeckoCryptoService:
    def __init__(self, fetcher: CoinGeckoCryptoFetcher, repository: CryptoRepository):
        self.fetcher = fetcher
        self.repository = repository

    def fetch_and_save_crypto_data(self):
        crypto_data = self.fetcher.fetch_crypto_data()
        if not crypto_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No crypto data found",
            )

        for data in crypto_data:
            validated_data = FetcherCoinGeckoCryptoSchema(**data).model_dump()

            crypto = self.repository.get_crypto_by_symbol(validated_data["symbol"])
            if crypto:
                self.repository.update_crypto(validated_data)
            else:
                self.repository.create_crypto(validated_data)

        return crypto_data


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
