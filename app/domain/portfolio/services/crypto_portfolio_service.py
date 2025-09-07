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

        return self.repository.delete_watched_crypto_from_portfolio(watched_crypto)

    def delete_all_watched_cryptos_from_portfolio(self, portfolio_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
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
                if t.crypto_id == crypto_id and t.transaction_type == "buy"
            )
            total_sold = sum(
                t.amount
                for t in transactions
                if t.crypto_id == crypto_id and t.transaction_type == "sell"
            )
            current_amount = total_bought - total_sold

            if transaction_data["amount"] > current_amount:
                raise BadRequestError(
                    "Nie można sprzedać więcej niż posiadasz w portfelu"
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

            if transaction_data["amount"] > current_amount:
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

    def delete_all_transactions_in_portfolio(self, portfolio_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        if not self.repository.delete_all_transactions_in_crypto_portfolio(
            portfolio_id
        ):
            raise NotFoundError("Brak transakcji w tym portfelu")

        return True
