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
        print(transaction_data)
        transaction_data["portfolio_id"] = portfolio_id
        return self.repository.create_transaction_in_crypto_portfolio(transaction_data)

    def get_transaction_in_portfolio(self, portfolio_id: str, transaction_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=False
        )

        transaction = self.repository.get_transaction_in_crypto_portfolio_by_id(
            portfolio_id, transaction_id
        )

        return transaction

    def get_transactions_in_portfolio(self, portfolio_id: str):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=False
        )

        transactions = self.repository.get_all_transactions_in_crypto_portfolio(
            portfolio_id
        )

        return transactions

    def update_transaction_in_portfolio(
        self, portfolio_id: str, transaction_id: str, update_data: dict
    ):
        crypto_portfolio = self.get_portfolio_by_id(
            portfolio_id, validate_permission_to_edit=True
        )

        transaction = self.repository.get_transaction_in_crypto_portfolio_by_id(
            portfolio_id, transaction_id
        )
        if not transaction:
            raise NotFoundError("Nie znaleziono transakcji")

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
