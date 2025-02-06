from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any


class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, str]
    subject: str
    template_name: str


class ReponseDetailSchema(BaseModel):
    detail: str
