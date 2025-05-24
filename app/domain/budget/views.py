from sqladmin import ModelView
from .models import Budget, BudgetTransaction, Category


class BudgetAdminView(ModelView, model=Budget):
    column_list = "__all__"


class BudgetTransactionAdminView(ModelView, model=BudgetTransaction):
    column_list = "__all__"


class CategoryAdminView(ModelView, model=Category):
    column_list = "__all__"
