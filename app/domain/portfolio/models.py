from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
from app.domain.model_base import Base


# Portfolio for user to store investments
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    owner = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.timezone("UTC", func.now()))
    updated_at = Column(DateTime, server_default=func.timezone("UTC", func.now()), onupdate=func.timezone("UTC", func.now()))

    # Relationships
    owner = relationship("User", back_populates="portfolios")
    portfolio_transactions = relationship("PortfolioTransaction", back_populates="portfolio", cascade="all, delete-orphan")
    
class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(String, nullable=False)  # "buy" or "sell"
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)  
    price_per_unit = Column(Float, nullable=False)  
    transaction_date = Column(DateTime, default=datetime.utcnow)  

    portfolio = relationship("Portfolio", back_populates="portfolio_transactions")
    asset = relationship("Asset", back_populates="transactions")
    

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    symbol = Column(String, nullable=False)  # Symbol for stock or crypto (e.g., CDR.WA, BTC)
    icon = Column(String, nullable=True)  # Optiunalll
    asset_type = Column(String, nullable=False)  # "stock" or "crypto"

    transactions = relationship("AssetTransaction", back_populates="asset")


class AssetHistoricalPrice(Base):
    __tablename__ = "asset_historical_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    
    date = Column(DateTime, nullable=False)  # np. timestamp lub data w UTC
    open_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)

    # Relacje
    asset = relationship("Asset", back_populates="historical_prices")
