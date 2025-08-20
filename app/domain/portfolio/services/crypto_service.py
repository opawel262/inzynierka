from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.models import Crypto, CryptoHistoricalPrice

from app.domain.portfolio.repositories.crypto_repository import CryptoRepository


class CryptoService:
    def __init__(self, repository: CryptoRepository):
        self.repository = repository

    def search_cryptos(self, search: str | None) -> List[Crypto]:
        if search:
            search = search.lower()
            cryptos = self.repository.get_crypto_by_name_or_symbol_alike(
                name_or_symbol=search
            )
        else:
            cryptos = self.repository.get_all_cryptos()
        return cryptos
