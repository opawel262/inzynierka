from typing import List, Dict, Any
from fastapi import HTTPException, status
from app.domain.portfolio.models import Crypto, CryptoHistoricalPrice

from app.domain.portfolio.repositories.crypto_repository import CryptoRepository



class CryptoService:
    def __init__(self, repository: CryptoRepository):
        self.repository = repository
        
    
    def search(self) -> List[Crypto]: 