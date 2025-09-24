from app.domain.portfolio.repositories.crypto_portfolio_repository import (
    CryptoPortfolioRepository,
)
from app.core.exceptions import UnauthorizedError, NotFoundError, BadRequestError
from app.domain.portfolio.models import Crypto


class CryptoPortfolioService:

    def __init__(
        self, crypto_portfolio_repository: CryptoPortfolioRepository, user_id: str
    ):
        self.repository = crypto_portfolio_repository
        self.user_id = user_id

    def get_all_portfolios(self):
        return self.repository.get_all_crypto_portfolios(self.user_id)

    def create_portfolio(self, portfolio_data: dict):
        portfolio_data["owner_id"] = self.user_id
        return self.repository.create_crypto_portfolio(portfolio_data)

    def update_portfolio(self, portfolio_id: str, update_data: dict):
        # Get the existing portfolio and check ownership
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        # after validating, update the portfolio
        crypto_portfolio = self.repository.update_crypto_portfolio(
            crypto_portfolio, update_data
        )

        return crypto_portfolio

    def delete_portfolio(self, portfolio_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        self.repository.delete_crypto_portfolio_by_id(portfolio_id)
        return True

    def delete_all_portfolios(self):
        return self.repository.delete_all_crypto_portfolios(self.user_id)

    def get_portfolio_by_id(
        self, portfolio_id: str, validate_permission_to_edit: bool = False
    ):
        crypto_portfolio = self.repository.get_crypto_portfolio_by_id(portfolio_id)
        if not crypto_portfolio:
            raise NotFoundError("Nie znaleziono portfela")

        if validate_permission_to_edit:
            if str(crypto_portfolio.owner_id) != str(self.user_id):
                raise UnauthorizedError("Brak dostępu do portfela")

        if crypto_portfolio.is_public is False and str(
            crypto_portfolio.owner_id
        ) != str(self.user_id):
            raise UnauthorizedError("Brak dostępu do portfela")

        return crypto_portfolio

    def get_portfolios_holding_crypto(self, crypto: Crypto):
        portfolios = self.get_all_portfolios()
        portfolios_holding_crypto = []
        for portfolio in portfolios:
            in_portfolio = self.repository.get_watched_crypto_in_portfolio_by_id(
                portfolio.id, crypto.id
            )
            portfolios_holding_crypto.append(
                {
                    "id": portfolio.id,
                    "title": portfolio.title,
                    "color": portfolio.color,
                    "in_portfolio": in_portfolio is not None,
                }
            )

        return portfolios_holding_crypto

    def add_watched_crypto_to_portfolio(self, portfolio_id: str, crypto: Crypto):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )
        if self.repository.get_watched_crypto_in_portfolio_by_id(
            portfolio_id, crypto.id
        ):
            raise BadRequestError("Kryptowaluta jest już obserwowana w tym portfelu")

        return self.repository.add_watched_crypto_to_portfolio(portfolio_id, crypto)

    def delete_watched_crypto_from_portfolio(self, portfolio_id: str, crypto: Crypto):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        watched_crypto = self.repository.get_watched_crypto_in_portfolio_by_id(
            portfolio_id, crypto.id
        )
        if not watched_crypto:
            raise NotFoundError("Kryptowaluta nie jest obserwowana w tym portfelu")

        self.delete_all_transactions_in_portfolio(
            portfolio_id, crypto=crypto, avoid_non_found=True
        )

        return self.repository.delete_watched_crypto_from_portfolio(watched_crypto)

    def delete_all_watched_cryptos_from_portfolio(self, portfolio_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )
        for crypto in crypto_portfolio.watched_cryptos:
            self.delete_all_transactions_in_portfolio(
                portfolio_id, crypto=crypto.crypto, avoid_non_found=True
            )
        if not self.repository.delete_all_watched_cryptos_in_portfolio(portfolio_id):
            raise NotFoundError("Brak obserwowanych kryptowalut w tym portfelu")
        return True

    def create_transaction_in_portfolio(
        self, portfolio_id: str, transaction_data: dict
    ):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        if (
            transaction_data.get("crypto", None) is not None
            and len(crypto_portfolio.watched_cryptos) > 0
            and not any(
                wc.crypto_id == transaction_data["crypto"].id
                for wc in crypto_portfolio.watched_cryptos
            )
        ):
            raise BadRequestError("Kryptowaluta nie jest obserwowana w tym portfelu")

        if transaction_data["amount"] <= 0:
            raise BadRequestError("Ilość musi być większa od 0")
        if transaction_data["price_per_unit"] <= 0:
            raise BadRequestError("Cena za jednostkę musi być większa od 0")
        if transaction_data["transaction_type"] not in ["buy", "sell"]:
            raise BadRequestError(
                "Nieprawidłowy typ transakcji, musi być 'buy' lub 'sell'"
            )

        # Przypisz portfolio_id do danych transakcji
        transaction_data["portfolio_id"] = portfolio_id

        # Walidacja ilości przy sprzedaży
        if transaction_data["transaction_type"] == "sell":
            crypto_id = transaction_data.get("crypto").id
            if not crypto_id:
                raise BadRequestError("Brak identyfikatora kryptowaluty w transakcji")

            # Pobierz wszystkie transakcje dla tej kryptowaluty w portfelu
            transactions = crypto_portfolio.crypto_transactions
            total_bought = sum(
                t.amount
                for t in transactions
                if t.crypto_id == crypto_id
                and t.transaction_type == "buy"
                and t.transaction_date <= transaction_data["transaction_date"]
            )
            total_sold = sum(
                t.amount
                for t in transactions
                if t.crypto_id == crypto_id
                and t.transaction_type == "sell"
                and t.transaction_date <= transaction_data["transaction_date"]
            )
            current_amount = total_bought - total_sold

            if transaction_data["amount"] > current_amount:
                raise BadRequestError(
                    "Nie można sprzedać więcej niż posiadasz w portfelu w danym momencie czasu"
                )
        return self.repository.create_transaction_in_crypto_portfolio(transaction_data)

    def get_transaction_in_portfolio(self, portfolio_id: str, transaction_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=False
        )

        transaction = self.repository.get_transaction_in_crypto_portfolio_by_id(
            portfolio_id, transaction_id
        )

        return transaction

    def get_transactions_in_portfolio(self, portfolio_id: str, crypto: Crypto = None):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=False
        )
        if (
            crypto
            and len(crypto_portfolio.watched_cryptos) > 0
            and not any(
                crypto and wc.crypto_id == crypto.id
                for wc in crypto_portfolio.watched_cryptos
            )
        ):
            raise BadRequestError("Kryptowaluta nie jest obserwowana w tym portfelu")
        transactions = self.repository.get_all_transactions_in_crypto_portfolio(
            portfolio_id, crypto=crypto
        )

        return transactions

    def update_transaction_in_portfolio(
        self, portfolio_id: str, transaction_id: str, update_data: dict
    ):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        if (
            update_data.get("crypto", None) is not None
            and len(crypto_portfolio.watched_cryptos) > 0
            and not any(
                wc.crypto_id == update_data["crypto"].id
                for wc in crypto_portfolio.watched_cryptos
            )
        ):
            raise BadRequestError("Kryptowaluta nie jest obserwowana w tym portfelu")
        transaction = self.repository.get_transaction_in_crypto_portfolio_by_id(
            portfolio_id, transaction_id
        )
        if not transaction:
            raise NotFoundError("Nie znaleziono transakcji")
        if update_data.get("amount") is not None and update_data["amount"] <= 0:
            raise BadRequestError("Ilość musi być większa od 0")
        if (
            update_data.get("price_per_unit") is not None
            and update_data["price_per_unit"] <= 0
        ):
            raise BadRequestError("Cena za jednostkę musi być większa od 0")
        if update_data.get("transaction_type", None) is not None and update_data[
            "transaction_type"
        ] not in ["buy", "sell"]:
            raise BadRequestError(
                "Nieprawidłowy typ transakcji, musi być 'buy' lub 'sell'"
            )

        # Przypisz portfolio_id do danych transakcji
        update_data["portfolio_id"] = portfolio_id

        # Walidacja ilości przy sprzedaży
        if (
            update_data.get("transaction_type", None) is not None
            and update_data["transaction_type"] == "sell"
        ):
            crypto_id = update_data.get("crypto").id
            if not crypto_id:
                raise BadRequestError("Brak identyfikatora kryptowaluty w transakcji")

            # Pobierz wszystkie transakcje dla tej kryptowaluty w portfelu
            transactions = crypto_portfolio.crypto_transactions
            total_bought = sum(
                t.amount
                for t in transactions
                if t.crypto_id == crypto_id and t.transaction_type == "buy"
            )
            total_sold = sum(
                t.amount
                for t in transactions
                if t.crypto_id == crypto_id and t.transaction_type == "sell"
            )
            current_amount = total_bought - total_sold

            if update_data["amount"] > current_amount:
                raise BadRequestError(
                    "Nie można sprzedać więcej niż posiadasz w portfelu"
                )
        transaction = self.repository.update_transaction_in_crypto_portfolio(
            transaction, update_data
        )

        return transaction

    def delete_transaction_in_portfolio(self, portfolio_id: str, transaction_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        transaction = self.repository.get_transaction_in_crypto_portfolio_by_id(
            portfolio_id, transaction_id
        )
        if not transaction:
            raise NotFoundError("Nie znaleziono transakcji")

        self.repository.delete_transaction_in_crypto_portfolio(transaction)
        return True

    def delete_all_transactions_in_portfolio(
        self, portfolio_id: str, crypto: Crypto = None, avoid_non_found: bool = False
    ):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )
        if (
            crypto
            and len(crypto_portfolio.watched_cryptos) > 0
            and not any(
                crypto and wc.crypto_id == crypto.id
                for wc in crypto_portfolio.watched_cryptos
            )
        ):
            raise BadRequestError("Kryptowaluta nie jest obserwowana w tym portfelu")
        transactions = self.repository.get_all_transactions_in_crypto_portfolio(
            portfolio_id, crypto=crypto
        )
        if not avoid_non_found and len(transactions) == 0:
            raise NotFoundError("Brak transakcji w tym portfelu")

        self.repository.delete_all_transactions_in_crypto_portfolio(
            portfolio_id, crypto=crypto
        )

        return True

    def get_portfolios_summary(self):
        portfolios = self.repository.get_all_crypto_portfolios(self.user_id)
        portfolio_summary = {
            "total_investment": 0,
            "current_value": 0,
            "total_percentage_profit_loss_24h": 0,
            "total_profit_loss_24h": 0,
            "total_profit_loss_percentage": 0,
            "total_profit_loss": 0,
            "total_portfolios": 0,
            "total_transactions": 0,
            "holdings_percentage": {},
            "top_gainer_24h": {},
            "historical_value_7d": [],
            "historical_value_1m": [],
            "historical_value_1y": [],
        }
        watched_cryptos = set()
        for portfolio in portfolios:
            for watched_crypto in portfolio.watched_cryptos:
                if watched_crypto.holdings > 0:
                    watched_cryptos.add(watched_crypto)

            portfolio_summary["total_investment"] += portfolio.total_investment
            portfolio_summary["current_value"] += portfolio.current_value
            portfolio_summary["total_profit_loss_24h"] += portfolio.profit_loss_24h
            portfolio_summary["total_profit_loss"] += portfolio.profit_loss
            portfolio_summary["total_portfolios"] += 1
            portfolio_summary["total_transactions"] += len(
                portfolio.crypto_transactions
            )
            for key, value in portfolio.holdings_percentage.items():
                if key in portfolio_summary["holdings_percentage"]:
                    portfolio_summary["holdings_percentage"][key] += value
                else:
                    portfolio_summary["holdings_percentage"][key] = value

            # Calculate percentage holdings after accumulating all values
            total_crypto_value = sum(portfolio_summary["holdings_percentage"].values())
            if total_crypto_value > 0:
                for key in portfolio_summary["holdings_percentage"]:
                    portfolio_summary["holdings_percentage"][key] = (
                        portfolio_summary["holdings_percentage"][key]
                        / total_crypto_value
                        * 100
                    )
            holdings = portfolio_summary["holdings_percentage"]
            sorted_keys = sorted(holdings, key=lambda k: holdings[k], reverse=True)
            top_keys = sorted_keys[:5]
            other_keys = sorted_keys[5:]
            other_sum = sum(holdings[k] for k in other_keys)
            new_holdings = {
                k: round(holdings[k], 2) for k in top_keys if round(holdings[k], 2) > 0
            }
            if other_sum > 0:
                new_holdings["Other"] = round(other_sum, 2)
            portfolio_summary["holdings_percentage"] = new_holdings
            # Aggregate historical values for 7d, 1m, 1y
            for idx, historical_value_7 in enumerate(portfolio.historical_value_7d):
                if len(portfolio_summary["historical_value_7d"]) <= idx:
                    portfolio_summary["historical_value_7d"].append(
                        {
                            "date": historical_value_7["date"],
                            "value": round(historical_value_7["value"], 2),
                        }
                    )
                else:
                    portfolio_summary["historical_value_7d"][idx]["value"] += round(
                        historical_value_7["value"], 2
                    )

            for idx, historical_value_1m in enumerate(portfolio.historical_value_1m):
                if len(portfolio_summary["historical_value_1m"]) <= idx:
                    portfolio_summary["historical_value_1m"].append(
                        {
                            "date": historical_value_1m["date"],
                            "value": round(historical_value_1m["value"], 2),
                        }
                    )
                else:
                    portfolio_summary["historical_value_1m"][idx]["value"] += round(
                        historical_value_1m["value"], 2
                    )

            for idx, historical_value_1y in enumerate(portfolio.historical_value_1y):
                if len(portfolio_summary["historical_value_1y"]) <= idx:
                    portfolio_summary["historical_value_1y"].append(
                        {
                            "date": historical_value_1y["date"],
                            "value": round(historical_value_1y["value"], 2),
                        }
                    )
                else:
                    portfolio_summary["historical_value_1y"][idx]["value"] += round(
                        historical_value_1y["value"], 2
                    )
        if len(watched_cryptos) > 0:
            top_gainer_24h_crypto = max(
                watched_cryptos,
                key=lambda c: (
                    c.crypto.price_change_percentage_24h
                    if c.crypto.price_change_percentage_24h is not None
                    else 0
                ),
            )

            portfolio_summary["top_gainer_24h"] = {
                "crypto": {
                    "symbol": top_gainer_24h_crypto.crypto.symbol,
                    "icon": top_gainer_24h_crypto.crypto.icon,
                    "name": top_gainer_24h_crypto.crypto.name,
                    "price": top_gainer_24h_crypto.crypto.price,
                    "price_change_percentage_24h": top_gainer_24h_crypto.crypto.price_change_percentage_24h,
                },
                "percentage_profit_loss_24h": 0,
                "profit_loss_24h": 0,
                "profit_loss": 0,
                "profit_loss_percentage": 0,
                "current_value": 0,
                "total_invested": 0,
                "avg_buy_price": 0,
                "holdings": 0,
                "current_value": 0,
            }
            for c in watched_cryptos:
                if c.crypto.symbol == top_gainer_24h_crypto.crypto.symbol:
                    portfolio_summary["top_gainer_24h"][
                        "percentage_profit_loss_24h"
                    ] = round(c.percentage_profit_loss_24h, 2)
                    portfolio_summary["top_gainer_24h"]["profit_loss_24h"] += round(
                        c.profit_loss_24h, 2
                    )

                    portfolio_summary["top_gainer_24h"]["current_value"] += round(
                        c.current_value, 2
                    )
                    portfolio_summary["top_gainer_24h"]["total_invested"] += round(
                        c.total_invested, 2
                    )
                    portfolio_summary["top_gainer_24h"]["holdings"] += round(
                        c.holdings, 8
                    )

            # Normalize avg_buy_price for top_gainer_24h
            holdings = portfolio_summary["top_gainer_24h"]["holdings"]
            if holdings > 0:
                # Weighted average buy price
                avg_buy_price_sum = 0
                for c in watched_cryptos:
                    if (
                        c.crypto.symbol == top_gainer_24h_crypto.crypto.symbol
                        and c.holdings > 0
                    ):
                        avg_buy_price_sum += c.avg_buy_price * c.holdings
                portfolio_summary["top_gainer_24h"]["avg_buy_price"] = round(
                    avg_buy_price_sum / holdings, 2
                )
            else:
                portfolio_summary["top_gainer_24h"]["avg_buy_price"] = 0
            portfolio_summary["top_gainer_24h"]["profit_loss"] = round(
                portfolio_summary["top_gainer_24h"]["current_value"]
                - portfolio_summary["top_gainer_24h"]["total_invested"],
                2,
            )
            if (
                portfolio_summary["top_gainer_24h"]["total_invested"] > 0
                and portfolio_summary["top_gainer_24h"]["current_value"] > 0
            ):
                portfolio_summary["top_gainer_24h"]["profit_loss_percentage"] = round(
                    (
                        portfolio_summary["top_gainer_24h"]["profit_loss"]
                        / portfolio_summary["top_gainer_24h"]["total_invested"]
                    )
                    * 100,
                    2,
                )

        else:
            portfolio_summary["top_gainer_24h"] = None

        if portfolio_summary["current_value"] > 0:
            portfolio_summary["total_percentage_profit_loss_24h"] = round(
                (
                    portfolio_summary["total_profit_loss_24h"]
                    / portfolio_summary["current_value"]
                )
                * 100,
                2,
            )
            portfolio_summary["total_profit_loss_percentage"] = round(
                (
                    portfolio_summary["total_profit_loss"]
                    / portfolio_summary["current_value"]
                )
                * 100,
                2,
            )

        return portfolio_summary
