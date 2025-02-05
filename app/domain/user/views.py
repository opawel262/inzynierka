from sqladmin import ModelView
from .models import User


class UserAdminView(ModelView, model=User):
    column_list = "__all__"
