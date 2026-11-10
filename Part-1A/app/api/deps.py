"""FastAPI dependencies."""

from fastapi import Request

from app.db.repository import IPORepository
from app.services.ipo_service import IPOService


def get_ipo_service(request: Request) -> IPOService:
    settings = request.app.state.settings
    return IPOService(IPORepository(settings), settings)
