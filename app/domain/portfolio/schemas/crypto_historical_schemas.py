from pydantic import BaseModel
from app.domain.portfolio.schemas.base_schemas import AssetHistoricalPriceSchema


class CryptoHistoricalPriceSchema(AssetHistoricalPriceSchema):
    pass
