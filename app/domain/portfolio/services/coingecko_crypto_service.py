from app.domain.portfolio.models import Crypto
from app.domain.portfolio.fetchers.crypto_fetchers import CoinGeckoCryptoFetcher
from app.domain.portfolio.repositories.crypto_repository import CryptoRepository
from app.domain.portfolio.schemas import FetcherCoinGeckoCryptoSchema


class CoinGeckoCryptoService:
    def __init__(self, fetcher: CoinGeckoCryptoFetcher, repository: CryptoRepository):
        self.fetcher = fetcher
        self.repository = repository

    def fetch_and_save_crypto_data(self):
        crypto_data = self.fetcher.fetch_crypto_data()
        if not crypto_data:
            raise Exception("No crypto data found")

        for data in crypto_data:
            validated_data = FetcherCoinGeckoCryptoSchema(**data).model_dump()

            crypto = self.repository.get_crypto_by_symbol(validated_data["symbol"])
            if crypto:
                self.repository.update_crypto(validated_data)
            else:
                self.repository.create_crypto(validated_data)

        return crypto_data
