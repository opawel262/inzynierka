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
    created_at = Column(DateTime, server_default=func.timezone("UTC", func.now()))
    updated_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )


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

    @property
    def total_watched(self):
        return len(self.watched_stocks)

    @property
    def total_transactions(self):
        return len(self.stock_transactions)

    @property
    def total_investment(self):
        return round(
            sum(
                tx.amount * tx.price_per_unit
                for tx in self.stock_transactions
                if tx.transaction_type.lower() == "buy"
            ),
            2,
        )

    @property
    def profit_loss(self):
        return round(
            sum([watched_stock.profit_loss for watched_stock in self.watched_stocks]),
            2,
        )

    @property
    def profit_loss_percentage(self):
        if self.current_value <= 0:
            return 0
        return round((self.profit_loss / self.current_value) * 100, 2)

    @property
    def profit_loss_24h(self):
        return round(
            sum(
                [watched_stock.profit_loss_24h for watched_stock in self.watched_stocks]
            ),
            2,
        )

    @property
    def percentage_profit_loss_24h(self):
        if self.current_value <= 0:
            return 0
        return round((self.profit_loss_24h / self.current_value) * 100, 2)

    @property
    def current_value(self):
        return round(
            sum(
                tx.amount * tx.stock.price
                for tx in self.stock_transactions
                if tx.transaction_type == "buy"
            )
            - sum(
                tx.amount * tx.stock.price
                for tx in self.stock_transactions
                if tx.transaction_type == "sell"
            ),
            2,
        )

    @property
    def holdings_percentage(self):
        # Use watched_stocks and their current_value
        values = {
            wc.stock.symbol: wc.current_value for wc in self.watched_stocks if wc.stock
        }
        total_value = sum(values.values())
        if total_value == 0:
            return {}

        sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
        result = {}
        other_sum = 0
        for idx, (symbol, value) in enumerate(sorted_values):
            percent = (value / total_value) * 100
            if idx < 6:
                if percent == 0:
                    continue
                result[symbol] = round(percent, 2)
            else:
                other_sum += percent
        if other_sum > 0:
            result["Other"] = round(other_sum, 2)
        return result

    @property
    def historical_value_7d(self):
        interval_hours = 12
        now = datetime.utcnow()
        start_time = now - timedelta(days=7)
        time_points = [
            start_time + timedelta(hours=i * interval_hours)
            for i in range(int(7 * 24 / interval_hours) + 1)
        ]
        results = []
        sorted_stock_transactions = sorted(
            self.stock_transactions, key=lambda tx: tx.transaction_date
        )

        for time_point in time_points:
            total_value = 0
            for transaction in sorted_stock_transactions:
                if transaction.transaction_date <= time_point:
                    price_at_time = None
                    if transaction.stock and transaction.stock.historical_prices:
                        for historical_price in transaction.stock.historical_prices:
                            if (
                                historical_price.period == "1w"
                                and historical_price.date <= time_point
                            ):
                                price_at_time = historical_price.close_price
                    # Jeśli nie znaleziono historycznej ceny, użyj aktualnej ceny
                    if price_at_time is None and transaction.stock:
                        price_at_time = transaction.stock.price
                    if price_at_time is not None:
                        if transaction.transaction_type.lower() == "buy":
                            total_value += transaction.amount * price_at_time
                        elif transaction.transaction_type.lower() == "sell":
                            total_value -= transaction.amount * price_at_time

            results.append({"date": time_point, "value": round(total_value, 2)})
        return results

    @property
    def historical_value_1m(self):
        interval_hours = 24
        now = datetime.utcnow()
        start_time = now - timedelta(days=30)
        time_points = [
            start_time + timedelta(hours=i * interval_hours)
            for i in range(int(30 * 24 / interval_hours) + 1)
        ]
        results = []
        sorted_stock_transactions = sorted(
            self.stock_transactions, key=lambda tx: tx.transaction_date
        )

        for time_point in time_points:
            total_value = 0
            for transaction in sorted_stock_transactions:
                if transaction.transaction_date <= time_point:
                    price_at_time = None
                    if transaction.stock and transaction.stock.historical_prices:
                        for historical_price in transaction.stock.historical_prices:
                            if (
                                historical_price.period == "1m"
                                and historical_price.date <= time_point
                            ):
                                price_at_time = historical_price.close_price
                    # Jeśli nie znaleziono historycznej ceny, użyj aktualnej ceny
                    if price_at_time is None and transaction.stock:
                        price_at_time = transaction.stock.price
                    if price_at_time is not None:
                        if transaction.transaction_type.lower() == "buy":
                            total_value += transaction.amount * price_at_time
                        elif transaction.transaction_type.lower() == "sell":
                            total_value -= transaction.amount * price_at_time

            results.append({"date": time_point, "value": round(total_value, 2)})
        return results

    @property
    def historical_value_1y(self):
        interval_days = 14
        now = datetime.utcnow()
        start_time = now - timedelta(days=365)
        time_points = [
            start_time + timedelta(days=i * interval_days)
            for i in range(int(365 / interval_days) + 1)
        ]

        results = []
        sorted_stock_transactions = sorted(
            self.stock_transactions, key=lambda tx: tx.transaction_date
        )

        for time_point in time_points:
            total_value = 0
            for transaction in sorted_stock_transactions:
                if transaction.transaction_date <= time_point:
                    price_at_time = None
                    if transaction.stock and transaction.stock.historical_prices:
                        for historical_price in transaction.stock.historical_prices:
                            if (
                                historical_price.period == "1y"
                                and historical_price.date <= time_point
                            ):
                                price_at_time = historical_price.close_price
                    # Jeśli nie znaleziono historycznej ceny, użyj aktualnej ceny
                    if price_at_time is None and transaction.stock:
                        price_at_time = transaction.stock.price
                    if price_at_time is not None:
                        if transaction.transaction_type.lower() == "buy":
                            total_value += transaction.amount * price_at_time
                        elif transaction.transaction_type.lower() == "sell":
                            total_value -= transaction.amount * price_at_time

            results.append({"date": time_point, "value": round(total_value, 2)})
        return results


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
    def total_watched(self):
        return len(self.watched_cryptos)

    @property
    def total_transactions(self):
        return len(self.crypto_transactions)

    @property
    def total_investment(self):
        return round(
            sum(
                tx.amount * tx.price_per_unit
                for tx in self.crypto_transactions
                if tx.transaction_type.lower() == "buy"
            ),
            2,
        )

    @property
    def profit_loss(self):
        return round(
            sum(
                [watched_crypto.profit_loss for watched_crypto in self.watched_cryptos]
            ),
            2,
        )

    @property
    def profit_loss_percentage(self):
        if self.current_value <= 0:
            return 0
        return round((self.profit_loss / self.current_value) * 100, 2)

    @property
    def profit_loss_24h(self):
        return round(
            sum(
                [
                    watched_crypto.profit_loss_24h
                    for watched_crypto in self.watched_cryptos
                ]
            ),
            2,
        )

    @property
    def percentage_profit_loss_24h(self):
        if self.current_value <= 0:
            return 0
        return round((self.profit_loss_24h / self.current_value) * 100, 2)

    @property
    def current_value(self):
        return round(
            sum(
                tx.amount * tx.crypto.price
                for tx in self.crypto_transactions
                if tx.transaction_type == "buy"
            )
            - sum(
                tx.amount * tx.crypto.price
                for tx in self.crypto_transactions
                if tx.transaction_type == "sell"
            ),
            2,
        )

    @property
    def holdings_percentage(self):
        # Use watched_cryptos and their current_value
        values = {
            wc.crypto.symbol: wc.current_value
            for wc in self.watched_cryptos
            if wc.crypto
        }
        total_value = sum(values.values())
        if total_value == 0:
            return {}

        sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
        result = {}
        other_sum = 0
        for idx, (symbol, value) in enumerate(sorted_values):
            percent = (value / total_value) * 100
            if idx < 6:
                if percent == 0:
                    continue
                result[symbol] = round(percent, 2)
            else:
                other_sum += percent
        if other_sum > 0:
            result["Other"] = round(other_sum, 2)
        return result

    @property
    def historical_value_7d(self):
        interval_hours = 12
        now = datetime.utcnow()
        start_time = now - timedelta(days=7)
        time_points = [
            start_time + timedelta(hours=i * interval_hours)
            for i in range(int(7 * 24 / interval_hours) + 1)
        ]
        results = []
        sorted_crypto_transactions = sorted(
            self.crypto_transactions, key=lambda tx: tx.transaction_date
        )

        for time_point in time_points:
            total_value = 0
            for transaction in sorted_crypto_transactions:
                if transaction.transaction_date <= time_point:
                    price_at_time = None
                    if transaction.crypto and transaction.crypto.historical_prices:
                        for historical_price in transaction.crypto.historical_prices:
                            if (
                                historical_price.period == "1w"
                                and historical_price.date <= time_point
                            ):
                                price_at_time = historical_price.close_price
                    # Jeśli nie znaleziono historycznej ceny, użyj aktualnej ceny
                    if price_at_time is None and transaction.crypto:
                        price_at_time = transaction.crypto.price
                    if price_at_time is not None:
                        if transaction.transaction_type.lower() == "buy":
                            total_value += transaction.amount * price_at_time
                        elif transaction.transaction_type.lower() == "sell":
                            total_value -= transaction.amount * price_at_time

            results.append({"date": time_point, "value": round(total_value, 2)})
        return results

    @property
    def historical_value_1m(self):
        interval_hours = 24
        now = datetime.utcnow()
        start_time = now - timedelta(days=30)
        time_points = [
            start_time + timedelta(hours=i * interval_hours)
            for i in range(int(30 * 24 / interval_hours) + 1)
        ]
        results = []
        sorted_crypto_transactions = sorted(
            self.crypto_transactions, key=lambda tx: tx.transaction_date
        )

        for time_point in time_points:
            total_value = 0
            for transaction in sorted_crypto_transactions:
                if transaction.transaction_date <= time_point:
                    price_at_time = None
                    if transaction.crypto and transaction.crypto.historical_prices:
                        for historical_price in transaction.crypto.historical_prices:
                            if (
                                historical_price.period == "1m"
                                and historical_price.date <= time_point
                            ):
                                price_at_time = historical_price.close_price
                    # Jeśli nie znaleziono historycznej ceny, użyj aktualnej ceny
                    if price_at_time is None and transaction.crypto:
                        price_at_time = transaction.crypto.price
                    if price_at_time is not None:
                        if transaction.transaction_type.lower() == "buy":
                            total_value += transaction.amount * price_at_time
                        elif transaction.transaction_type.lower() == "sell":
                            total_value -= transaction.amount * price_at_time

            results.append({"date": time_point, "value": round(total_value, 2)})
        return results

    @property
    def historical_value_1y(self):
        interval_days = 14
        now = datetime.utcnow()
        start_time = now - timedelta(days=365)
        time_points = [
            start_time + timedelta(days=i * interval_days)
            for i in range(int(365 / interval_days) + 1)
        ]

        results = []
        sorted_crypto_transactions = sorted(
            self.crypto_transactions, key=lambda tx: tx.transaction_date
        )

        for time_point in time_points:
            total_value = 0
            for transaction in sorted_crypto_transactions:
                if transaction.transaction_date <= time_point:
                    price_at_time = None
                    if transaction.crypto and transaction.crypto.historical_prices:
                        for historical_price in transaction.crypto.historical_prices:
                            if (
                                historical_price.period == "1y"
                                and historical_price.date <= time_point
                            ):
                                price_at_time = historical_price.close_price
                    # Jeśli nie znaleziono historycznej ceny, użyj aktualnej ceny
                    if price_at_time is None and transaction.crypto:
                        price_at_time = transaction.crypto.price
                    if price_at_time is not None:
                        if transaction.transaction_type.lower() == "buy":
                            total_value += transaction.amount * price_at_time
                        elif transaction.transaction_type.lower() == "sell":
                            total_value -= transaction.amount * price_at_time

            results.append({"date": time_point, "value": round(total_value, 2)})
        return results


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

    @property
    def profit_loss(self):
        if self.transaction_type.lower() == "sell":
            return None
        current_value = self.amount * self.stock.price
        invested_value = self.amount * self.price_per_unit
        return round(current_value - invested_value, 2)

    @property
    def profit_loss_percentage(self):
        if self.transaction_type.lower() == "sell":
            return None
        invested_value = self.amount * self.price_per_unit
        if invested_value == 0:
            return 0
        return round((self.profit_loss / invested_value) * 100, 2)


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
        if self.transaction_type.lower() == "sell":
            return None
        current_value = self.amount * self.crypto.price
        invested_value = self.amount * self.price_per_unit
        return round(current_value - invested_value, 2)

    @property
    def profit_loss_percentage(self):
        if self.transaction_type.lower() == "sell":
            return None
        invested_value = self.amount * self.price_per_unit
        if invested_value == 0:
            return 0
        return round((self.profit_loss / invested_value) * 100, 2)


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
        )

    @property
    def avg_buy_price(self):
        total_cost = sum(
            tx.amount * tx.price_per_unit
            for tx in self.portfolio.crypto_transactions
            if tx.crypto_id == self.crypto_id and tx.transaction_type.lower() == "buy"
        )
        total_proceeds = sum(
            tx.amount * tx.price_per_unit
            for tx in self.portfolio.crypto_transactions
            if tx.crypto_id == self.crypto_id and tx.transaction_type.lower() == "sell"
        )
        holdings = self.holdings
        if holdings == 0:
            return 0
        avg_net_cost = (total_cost - total_proceeds) / holdings
        return avg_net_cost

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
            # Calculate profit/loss for 24h based on holdings and price change
            return round(
                (self.crypto.price_change_percentage_24h / 100) * self.current_value,
                2,
            )
        return 0

    @property
    def percentage_profit_loss_24h(self):
        if self.total_invested == 0:
            return 0
        return round((self.profit_loss_24h / self.current_value) * 100, 2)

    @property
    def profit_loss(self):
        if self.crypto:
            total_bought = sum(
                tx.amount * tx.price_per_unit
                for tx in self.portfolio.crypto_transactions
                if tx.crypto_id == self.crypto_id
                and tx.transaction_type.lower() == "buy"
            )
            total_sold = sum(
                tx.amount * tx.price_per_unit
                for tx in self.portfolio.crypto_transactions
                if tx.crypto_id == self.crypto_id
                and tx.transaction_type.lower() == "sell"
            )
            profit = total_sold - total_bought + self.current_value
            return profit
        return 0

    @property
    def profit_loss_percentage(self):
        if self.total_invested == 0:
            return 0
        return round((self.profit_loss / self.current_value) * 100, 2)

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

    @property
    def total_invested(self):
        return sum(
            tx.amount * tx.price_per_unit
            for tx in self.portfolio.stock_transactions
            if tx.stock_id == self.stock_id and tx.transaction_type.lower() == "buy"
        )

    @property
    def avg_buy_price(self):
        total_cost = sum(
            tx.amount * tx.price_per_unit
            for tx in self.portfolio.stock_transactions
            if tx.stock_id == self.stock_id and tx.transaction_type.lower() == "buy"
        )
        total_proceeds = sum(
            tx.amount * tx.price_per_unit
            for tx in self.portfolio.stock_transactions
            if tx.stock_id == self.stock_id and tx.transaction_type.lower() == "sell"
        )
        holdings = self.holdings
        if holdings == 0:
            return 0
        avg_net_cost = (total_cost - total_proceeds) / holdings
        return avg_net_cost

    @property
    def holdings(self):
        return sum(
            tx.amount
            for tx in self.portfolio.stock_transactions
            if tx.stock_id == self.stock_id and tx.transaction_type.lower() == "buy"
        ) - sum(
            tx.amount
            for tx in self.portfolio.stock_transactions
            if tx.stock_id == self.stock_id and tx.transaction_type.lower() == "sell"
        )

    @property
    def profit_loss_24h(self):
        if self.stock and self.stock.price_change_percentage_24h is not None:
            # Calculate profit/loss for 24h based on holdings and price change
            return round(
                (self.stock.price_change_percentage_24h / 100) * self.current_value,
                2,
            )
        return 0

    @property
    def percentage_profit_loss_24h(self):
        if self.total_invested == 0:
            return 0
        return round((self.profit_loss_24h / self.current_value) * 100, 2)

    @property
    def profit_loss(self):
        if self.stock:
            total_bought = sum(
                tx.amount * tx.price_per_unit
                for tx in self.portfolio.stock_transactions
                if tx.stock_id == self.stock_id and tx.transaction_type.lower() == "buy"
            )
            total_sold = sum(
                tx.amount * tx.price_per_unit
                for tx in self.portfolio.stock_transactions
                if tx.stock_id == self.stock_id
                and tx.transaction_type.lower() == "sell"
            )
            profit = total_sold - total_bought + self.current_value
            return profit
        return 0

    @property
    def profit_loss_percentage(self):
        if self.total_invested == 0:
            return 0
        return round((self.profit_loss / self.current_value) * 100, 2)

    @property
    def current_value(self):
        if self.stock:
            return self.holdings * self.stock.price
        return 0
