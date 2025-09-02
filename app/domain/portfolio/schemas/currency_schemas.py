from datetime import datetime
from pydantic import BaseModel


class CurrencyPairRateSchema(BaseModel):
    id: int
    base_currency: str
    quote_currency: str
    rate: float
    updated_at: datetime
