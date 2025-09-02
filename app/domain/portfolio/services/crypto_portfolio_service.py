from app.domain.portfolio.repositories.crypto_portfolio_repository import (
    CryptoPortfolioRepository,
)


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
        return self.repository.update_crypto_portfolio(portfolio_id, update_data)

    def delete_all_portfolios(self):
        return self.repository.delete_all_crypto_portfolios(self.user_id)
