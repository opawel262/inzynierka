from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Float,
    Integer,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
from app.domain.model_base import Base
from datetime import datetime, timedelta


### BASE MODELS TO EXTEND ###
# Portfolio for user to store investments
class BasePortfolio(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    title = Column(String(64), nullable=False)
    description = Column(String(255), nullable=True)
    color = Column(String(20), nullable=False)
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, server_default=func.timezone("UTC", func.now()))
    updated_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )
    is_public = Column(Boolean, default=False, nullable=False)


class BaseAsset(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )
    market_cap = Column(BigInteger, nullable=True)
    market_cap_rank = Column(Integer, nullable=True)
    price_change_percentage_1h = Column(Float, nullable=True)
    price_change_percentage_24h = Column(Float, nullable=True)
    price_change_percentage_7d = Column(Float, nullable=True)
    price_change_percentage_30d = Column(Float, nullable=True)
    price_change_percentage_1y = Column(Float, nullable=True)
    price_change_percentage_max = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    circulating_supply = Column(Float, nullable=True)

    def __str__(self):
        return self.name


class BaseHistoricalPrice(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    low_price = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    interval = Column(String, nullable=False)
    period = Column(String, nullable=False)

    def __str__(self):
        return str(self.date)


class BaseTransaction(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    transaction_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)


### PORTFOLIOS ###
# Portfolio for user to store stock investments
class StockPortfolio(BasePortfolio):
    __tablename__ = "stock_portfolios"

    stock_transactions = relationship(
        "StockTransaction", back_populates="portfolio", cascade="all, delete-orphan"
    )
    owner = relationship("User", back_populates="stock_portfolios")
    watched_stocks = relationship(
        "WatchedStockInPortfolio",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )


# Portfolio for user to store crypto investments
class CryptoPortfolio(BasePortfolio):
    __tablename__ = "crypto_portfolios"

    crypto_transactions = relationship(
        "CryptoTransaction", back_populates="portfolio", cascade="all, delete-orphan"
    )
    owner = relationship("User", back_populates="crypto_portfolios")
    watched_cryptos = relationship(
        "WatchedCryptoInPortfolio",
        back_populates="portfolio",
        cascade="all, delete-orphan",
    )

    @property
    def total_watched_cryptos(self):
        return len(self.watched_cryptos)

    @property
    def total_transactions(self):
        return len(self.crypto_transactions)

    @property
    def total_investment(self):
        return sum(
            tx.amount * tx.price_per_unit
            for tx in self.crypto_transactions
            if tx.transaction_type.lower() == "buy"
        ) - sum(
            tx.amount * tx.price_per_unit
            for tx in self.crypto_transactions
            if tx.transaction_type.lower() == "sell"
        )

    @property
    def profit_loss(self):
        total_current_value = sum(
            tx.amount * tx.crypto.price for tx in self.crypto_transactions
        )
        return total_current_value - self.total_investment

    @property
    def profit_loss_percentage(self):
        if self.total_investment == 0:
            return 0
        return (self.profit_loss / self.total_investment) * 100

    @property
    def profit_loss_24h(self):
        total_24h_change = 0
        for tx in self.crypto_transactions:
            if tx.crypto and tx.crypto.price_change_percentage_24h is not None:
                total_24h_change += (
                    2
                    * (tx.crypto.price_change_percentage_24h / 100)
                    * (tx.amount * tx.price_per_unit)
                )
        return round(total_24h_change, 2)

    @property
    def percentage_profit_loss_24h(self):
        if self.total_investment == 0:
            return 0
        return round((self.profit_loss_24h / self.total_investment) * 100, 2)

    @property
    def current_value(self):
        return sum(
            tx.amount * tx.crypto.price
            for tx in self.crypto_transactions
            if tx.transaction_type == "buy"
        ) - sum(
            tx.amount * tx.crypto.price
            for tx in self.crypto_transactions
            if tx.transaction_type == "sell"
        )

    @property
    def cryptos_percentage_holdings(self):
        holdings = {}
        total_value = sum(
            tx.amount * tx.price_per_unit
            for tx in self.crypto_transactions
            if tx.transaction_type.lower() == "buy"
        ) - sum(
            tx.amount * tx.price_per_unit
            for tx in self.crypto_transactions
            if tx.transaction_type.lower() == "sell"
        )
        if total_value == 0:
            return holdings
        for tx in self.crypto_transactions:
            crypto_symbol = tx.crypto.symbol if tx.crypto else "Unknown"
            if crypto_symbol not in holdings:
                holdings[crypto_symbol] = 0
            if tx.transaction_type.lower() == "buy":
                holdings[crypto_symbol] += tx.amount * tx.price_per_unit
            elif tx.transaction_type.lower() == "sell":
                holdings[crypto_symbol] -= tx.amount * tx.price_per_unit
        sorted_holdings = sorted(holdings.items(), key=lambda x: x[1], reverse=True)
        result = {}
        other_sum = 0
        for idx, (symbol, value) in enumerate(sorted_holdings):
            percent = (value / total_value) * 100
            if idx < 6:
                result[symbol] = percent
            else:
                other_sum += percent
        if other_sum > 0:
            result["Other"] = other_sum
        return result

    @property
    def historical_value_7d(self):
        interval_hours = 6
        now = datetime.utcnow()
        start_time = now - timedelta(days=7)
        time_points = [
            start_time + timedelta(hours=i * interval_hours)
            for i in range(int(7 * 24 / interval_hours) + 1)
        ]

        # Prepare transactions grouped by crypto
        transactions_by_crypto = {}
        for tx in self.crypto_transactions:
            transactions_by_crypto.setdefault(tx.crypto_id, []).append(tx)

        # Prepare historical prices for each crypto
        historical_prices_by_crypto = {}
        for watched in self.watched_cryptos:
            crypto = watched.crypto
            prices = {
                price.date.replace(minute=0, second=0, microsecond=0): price.close_price
                for price in crypto.historical_prices
                if price.period == "7d" and price.date >= start_time
            }
            historical_prices_by_crypto[crypto.id] = prices

        result = []
        for point in time_points:
            total_value = 0
            for watched in self.watched_cryptos:
                crypto = watched.crypto
                # Find price at this time point, fallback to current price if not found
                price = historical_prices_by_crypto.get(crypto.id, {}).get(
                    point.replace(minute=0, second=0, microsecond=0), crypto.price
                )
                # Calculate holdings up to this time point
                holdings = 0
                for tx in transactions_by_crypto.get(crypto.id, []):
                    if tx.transaction_date <= point:
                        if tx.transaction_type.lower() == "buy":
                            holdings += tx.amount
                        elif tx.transaction_type.lower() == "sell":
                            holdings -= tx.amount
                total_value += holdings * price
            result.append({"date": point, "value": total_value})
        return result

    @property
    def historical_value_1m(self):
        interval_hours = 12
        now = datetime.utcnow()
        start_time = now - timedelta(days=30)
        time_points = [
            start_time + timedelta(hours=i * interval_hours)
            for i in range(int(30 * 24 / interval_hours) + 1)
        ]

        # Prepare transactions grouped by crypto
        transactions_by_crypto = {}
        for tx in self.crypto_transactions:
            transactions_by_crypto.setdefault(tx.crypto_id, []).append(tx)

        # Prepare historical prices for each crypto
        historical_prices_by_crypto = {}
        for watched in self.watched_cryptos:
            crypto = watched.crypto
            prices = {
                price.date.replace(minute=0, second=0, microsecond=0): price.close_price
                for price in crypto.historical_prices
                if price.period == "1m" and price.date >= start_time
            }
            historical_prices_by_crypto[crypto.id] = prices

        result = []
        for point in time_points:
            total_value = 0
            for watched in self.watched_cryptos:
                crypto = watched.crypto
                # Find price at this time point, fallback to current price if not found
                price = historical_prices_by_crypto.get(crypto.id, {}).get(
                    point.replace(minute=0, second=0, microsecond=0), crypto.price
                )
                # Calculate holdings up to this time point
                holdings = 0
                for tx in transactions_by_crypto.get(crypto.id, []):
                    if tx.transaction_date <= point:
                        if tx.transaction_type.lower() == "buy":
                            holdings += tx.amount
                        elif tx.transaction_type.lower() == "sell":
                            holdings -= tx.amount
                total_value += holdings * price
            result.append({"date": point, "value": total_value})
        return result

    @property
    def historical_value_1y(self):
        interval_days = 7
        now = datetime.utcnow()
        start_time = now - timedelta(days=365)
        time_points = [
            start_time + timedelta(days=i * interval_days)
            for i in range(int(365 / interval_days) + 1)
        ]

        # Prepare transactions grouped by crypto
        transactions_by_crypto = {}
        for tx in self.crypto_transactions:
            transactions_by_crypto.setdefault(tx.crypto_id, []).append(tx)

        # Prepare historical prices for each crypto
        historical_prices_by_crypto = {}
        for watched in self.watched_cryptos:
            crypto = watched.crypto
            prices = {
                price.date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ): price.close_price
                for price in crypto.historical_prices
                if price.period == "1y" and price.date >= start_time
            }
            historical_prices_by_crypto[crypto.id] = prices

        result = []
        for point in time_points:
            total_value = 0
            for watched in self.watched_cryptos:
                crypto = watched.crypto
                # Find price at this time point, fallback to current price if not found
                price = historical_prices_by_crypto.get(crypto.id, {}).get(
                    point.replace(hour=0, minute=0, second=0, microsecond=0),
                    crypto.price,
                )
                # Calculate holdings up to this time point
                holdings = 0
                for tx in transactions_by_crypto.get(crypto.id, []):
                    if tx.transaction_date <= point:
                        if tx.transaction_type.lower() == "buy":
                            holdings += tx.amount
                        elif tx.transaction_type.lower() == "sell":
                            holdings -= tx.amount
                total_value += holdings * price
            result.append({"date": point, "value": total_value})
        return result


### ASSETS ###
# Transaction for stock investments
class Stock(BaseAsset):
    __tablename__ = "stocks"
    beta = Column(Float, nullable=True)
    pe_ratio = Column(Float, nullable=True)
    eps_trailing_twelve_months = Column(Float, nullable=True)
    price_to_book = Column(Float, nullable=True)
    price_to_sales = Column(Float, nullable=True)
    payout_ratio = Column(Float, nullable=True)
    trailing_annual_dividend_yield = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    return_on_equity = Column(Float, nullable=True)
    free_cashflow = Column(Float, nullable=True)
    average_volume_10d = Column(Integer, nullable=True)
    employees = Column(Integer, nullable=True)
    market_state = Column(String, nullable=True)
    description = Column(String, nullable=True)
    sector = Column(String, nullable=True)

    transactions = relationship("StockTransaction", back_populates="stock")
    historical_prices = relationship("StockHistoricalPrice", back_populates="stock")
    watched_in_portfolios = relationship(
        "WatchedStockInPortfolio", back_populates="stock", cascade="all, delete-orphan"
    )


# Transaction for crypto investments
class Crypto(BaseAsset):
    __tablename__ = "cryptos"

    transactions = relationship("CryptoTransaction", back_populates="crypto")
    historical_prices = relationship("CryptoHistoricalPrice", back_populates="crypto")
    icon = Column(String, nullable=True)
    total_supply = Column(Float, nullable=True)
    max_supply = Column(Float, nullable=True)

    transactions = relationship("CryptoTransaction", back_populates="crypto")
    historical_prices = relationship("CryptoHistoricalPrice", back_populates="crypto")
    watched_in_portfolios = relationship(
        "WatchedCryptoInPortfolio",
        back_populates="crypto",
        cascade="all, delete-orphan",
    )


### TRANSACTIONS ###
# Transaction for stock investments
class StockTransaction(BaseTransaction):
    __tablename__ = "stock_transactions"

    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("stock_portfolios.id", ondelete="CASCADE"),
        nullable=False,
    )
    stock_id = Column(
        Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )

    portfolio = relationship("StockPortfolio", back_populates="stock_transactions")
    stock = relationship("Stock", back_populates="transactions")


# Transaction for crypto investments
class CryptoTransaction(BaseTransaction):
    __tablename__ = "crypto_transactions"

    portfolio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("crypto_portfolios.id", ondelete="CASCADE"),
        nullable=False,
    )
    crypto_id = Column(
        Integer, ForeignKey("cryptos.id", ondelete="CASCADE"), nullable=False
    )

    portfolio = relationship("CryptoPortfolio", back_populates="crypto_transactions")
    crypto = relationship("Crypto", back_populates="transactions")

    @property
    def profit_loss(self):
        current_value = self.amount * self.crypto.price
        invested_value = self.amount * self.price_per_unit
        if self.transaction_type.lower() == "sell":
            invested_value = -invested_value

        return current_value - invested_value

    @property
    def profit_loss_percentage(self):
        invested_value = self.amount * self.price_per_unit
        if invested_value == 0:
            return 0
        return (self.profit_loss / invested_value) * 100


### HISTORICAL PRICES ###
# Historical prices for stock investments
class StockHistoricalPrice(BaseHistoricalPrice):
    __tablename__ = "stock_historical_prices"

    stock_id = Column(
        Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False
    )
    stock = relationship("Stock", back_populates="historical_prices")


# Historical prices for crypto investments
class CryptoHistoricalPrice(BaseHistoricalPrice):
    __tablename__ = "crypto_historical_prices"

    crypto_id = Column(
        Integer, ForeignKey("cryptos.id", ondelete="CASCADE"), nullable=False
    )
    crypto = relationship("Crypto", back_populates="historical_prices")


#
class CurrencyPairRate(Base):
    __tablename__ = "currency_pair_rates"
    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3), index=True)
    quote_currency = Column(String(3), index=True)
    updated_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )
    rate = Column(Float, nullable=False)


class WatchedCryptoInPortfolio(Base):
    __tablename__ = "watched_cryptos_in_portfolio"
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(
        UUID(as_uuid=True), ForeignKey("crypto_portfolios.id", ondelete="CASCADE")
    )
    crypto_id = Column(Integer, ForeignKey("cryptos.id", ondelete="CASCADE"))

    portfolio = relationship("CryptoPortfolio", back_populates="watched_cryptos")
    crypto = relationship("Crypto", back_populates="watched_in_portfolios")

    @property
    def total_invested(self):
        return sum(
            tx.amount * tx.price_per_unit
            for tx in self.portfolio.crypto_transactions
            if tx.crypto_id == self.crypto_id and tx.transaction_type.lower() == "buy"
        ) - sum(
            tx.amount * tx.price_per_unit
            for tx in self.portfolio.crypto_transactions
            if tx.crypto_id == self.crypto_id and tx.transaction_type.lower() == "sell"
        )

    @property
    def avg_buy_price(self):
        total_amount = sum(
            tx.amount
            for tx in self.portfolio.crypto_transactions
            if tx.crypto_id == self.crypto_id and tx.transaction_type.lower() == "buy"
        )
        if total_amount == 0:
            return 0
        return self.total_invested / total_amount

    @property
    def holdings(self):
        return sum(
            tx.amount
            for tx in self.portfolio.crypto_transactions
            if tx.crypto_id == self.crypto_id and tx.transaction_type.lower() == "buy"
        ) - sum(
            tx.amount
            for tx in self.portfolio.crypto_transactions
            if tx.crypto_id == self.crypto_id and tx.transaction_type.lower() == "sell"
        )

    @property
    def profit_loss_24h(self):
        if self.crypto and self.crypto.price_change_percentage_24h is not None:
            return round(
                2
                * (self.crypto.price_change_percentage_24h / 100)
                * self.total_invested,
                2,
            )
        return 0

    @property
    def percentage_profit_loss_24h(self):
        if self.total_invested == 0:
            return 0
        return round((self.profit_loss_24h / self.total_invested) * 100, 2)

    @property
    def profit_loss(self):
        if self.crypto:
            current_value = self.holdings * self.crypto.price
            return current_value - self.total_invested
        return 0

    @property
    def profit_loss_percentage(self):
        if self.total_invested == 0:
            return 0
        return (self.profit_loss / self.total_invested) * 100

    @property
    def current_value(self):
        if self.crypto:
            return self.holdings * self.crypto.price
        return 0


class WatchedStockInPortfolio(Base):
    __tablename__ = "watched_stocks_in_portfolio"
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(
        UUID(as_uuid=True), ForeignKey("stock_portfolios.id", ondelete="CASCADE")
    )
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"))

    portfolio = relationship("StockPortfolio", back_populates="watched_stocks")
    stock = relationship("Stock", back_populates="watched_in_portfolios")
