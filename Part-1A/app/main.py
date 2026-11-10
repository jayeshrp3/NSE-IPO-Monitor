"""FastAPI application setup."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes.ipos import router as ipo_api_router
from app.core.config import Settings
from app.core.errors import (
    DuplicateIPOError,
    IPODataError,
    IPOStorageError,
    ValidationError,
)
from app.db.connection import initialize_database
from app.web.routes import router as web_router

BASE_DIR = Path(__file__).resolve().parent.parent


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings.from_environment()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        initialize_database(app_settings)
        yield

    application = FastAPI(title="NSE IPO Deadline Tracker", lifespan=lifespan)
    application.state.settings = app_settings
    application.state.templates = Jinja2Templates(
        directory=str(BASE_DIR / "frontend" / "templates")
    )
    application.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "frontend" / "static")),
        name="static",
    )
    application.include_router(ipo_api_router)
    application.include_router(web_router)

    @application.exception_handler(ValidationError)
    async def validation_error_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @application.exception_handler(DuplicateIPOError)
    async def duplicate_error_handler(_: Request, exc: DuplicateIPOError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @application.exception_handler(IPODataError)
    async def data_error_handler(_: Request, exc: IPODataError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @application.exception_handler(IPOStorageError)
    async def storage_error_handler(_: Request, exc: IPOStorageError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @application.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Request validation failed.",
                "errors": [
                    {
                        "location": list(error["loc"]),
                        "message": error["msg"],
                        "type": error["type"],
                    }
                    for error in exc.errors()
                ],
            },
        )

    return application


app = create_app()
