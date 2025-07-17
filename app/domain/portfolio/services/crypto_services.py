from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.models import Crypto, CryptoHistoricalPrice
from app.domain.portfolio.fetchers.crypto_fetchers import CoinGeckoCryptoFetcher, BinanaceCryptoFetcher
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.schemas import FetcherCoinGeckoCryptoSchema


class CoinGeckoCryptoService:
    def __init__(self, fetcher: CoinGeckoCryptoFetcher, repository: CryptoRepository):
        self.fetcher = fetcher
        self.repository = repository

    def fetch_and_save_crypto_data(self):
        crypto_data = self.fetcher.fetch_data()
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
        

    def fetch_and_save_historical_cryptos_data(self):
        symbols = self._get_all_crypto_symbol()[0:5]
        for symbol in symbols:
            historical_data = self.fetcher.fetch_historical_crypto_data(symbol)
            if not historical_data:
            continue  # Skip if no data

            for data_point in historical_data:
            validated_data = CryptoHistoricalPrice(**data_point)
            self.repository.save_historical_price(symbol, validated_data)

        def _get_all_crypto_symbol(self) -> List[str]:
        return self.repository.get_all_crypto_symbols()
