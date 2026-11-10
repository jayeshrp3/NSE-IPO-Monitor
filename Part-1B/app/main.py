import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router
from app.schemas.extraction import ApiError
from app.services.ollama_client import OllamaClient

ROOT = Path(__file__).parent


def create_app(ollama_client=None) -> FastAPI:
    application = FastAPI(title="IPO Announcement Assistant", version="1.0.0")
    application.state.ollama_client = ollama_client or OllamaClient(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        timeout=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120")),
    )
    application.include_router(router)
    application.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
    templates = Jinja2Templates(directory=ROOT / "templates")

    @application.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        return templates.TemplateResponse(request, "index.html")

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc):
        del exc
        try:
            payload = await request.json()
        except ValueError:
            payload = {}
        text = payload.get("announcement_text") if isinstance(payload, dict) else None
        too_large = isinstance(text, str) and len(text) > 50_000
        error = ApiError(
            code="input_too_large" if too_large else "invalid_request",
            message=(
                "Announcement text exceeds the 50,000-character limit."
                if too_large
                else "Request must contain non-blank announcement text."
            ),
        )
        return JSONResponse(
            status_code=422,
            content=error.model_dump(),
        )

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        del request
        detail = exc.detail
        if isinstance(detail, dict) and {"code", "message"} <= detail.keys():
            return JSONResponse(status_code=exc.status_code, content=detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiError(
                code="invalid_request", message="The request could not be completed."
            ).model_dump(),
        )

    return application


app = create_app()
