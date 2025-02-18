from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class CreateToken(BaseModel):
    email: EmailStr
    password: str


class AccessToken(BaseModel):
    access_token: str
