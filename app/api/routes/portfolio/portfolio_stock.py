from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.utils import limiter
from app.core.config import settings


router = APIRouter(
    prefix="/portfolio/stocks",
    tags=["Portfolio Management - Stocks"],
)
