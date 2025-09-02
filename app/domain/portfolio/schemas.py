from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any, Union


class FetcherCoinGeckoCryptoSchema(BaseModel):
    symbol: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    market_cap: Optional[float] = None
    price_change_percentage_1h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    volume_24h: Optional[float] = None
    circulating_supply: Optional[float] = None
    icon: Optional[str] = None
    market_cap_rank: Optional[int] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
