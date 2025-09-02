from pydantic import BaseModel
from app.domain.portfolio.schemas.base_schemas import AssetHistoricalPriceSchema


class StockHistoricalPriceSchema(AssetHistoricalPriceSchema):
    pass
