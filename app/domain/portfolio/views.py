from sqladmin import ModelView
from .models import (
    Stock,
    Crypto,
    StockTransaction,
    CryptoTransaction,
    StockPortfolio,
    CryptoPortfolio,
)


class StockAdminView(ModelView, model=Stock):
    column_list = "__all__"


class CryptoAdminView(ModelView, model=Crypto):
    column_list = "__all__"


class StockTransactionAdminView(ModelView, model=StockTransaction):
    column_list = "__all__"


class CryptoTransactionAdminView(ModelView, model=CryptoTransaction):
    column_list = "__all__"


class StockPortfolioAdminView(ModelView, model=StockPortfolio):
    column_list = "__all__"


class CryptoPortfolioAdminView(ModelView, model=CryptoPortfolio):
    column_list = "__all__"
