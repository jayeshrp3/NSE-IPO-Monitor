from fastapi import APIRouter, HTTPException, Request

from app.schemas.extraction import AnalysisRequest, AnalysisResponse, ApiError
from app.services.extraction import (
    analyze_output,
    build_prompt,
    has_unsupported_language,
)
from app.services.ollama_client import (
    OllamaInvalidResponse,
    OllamaTimeout,
    OllamaUnavailable,
)

router = APIRouter()


async def analyze_text(text: str, client=None) -> AnalysisResponse:
    if client is None:
        raise RuntimeError("Ollama client is not configured")

    if has_unsupported_language(text):
        from app.services.extraction import unsupported_language_response

        return unsupported_language_response()

    try:
        raw = await client.generate(build_prompt(text))
        return analyze_output(raw, text)

    except OllamaTimeout as exc:
        raise HTTPException(
            status_code=504,
            detail=ApiError(
                code="inference_timeout",
                message=str(exc),
            ).model_dump(),
        ) from exc

    except OllamaUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail=ApiError(
                code="ollama_unavailable",
                message=str(exc),
            ).model_dump(),
        ) from exc

    except (OllamaInvalidResponse, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=ApiError(
                code="invalid_model_output",
                message="Local model output could not be validated.",
            ).model_dump(),
        ) from exc


@router.post(
    "/api/v1/analyze",
    response_model=AnalysisResponse,
    responses={
        422: {"model": ApiError},
        502: {"model": ApiError},
        503: {"model": ApiError},
        504: {"model": ApiError},
    },
)
async def analyze(request: AnalysisRequest, http_request: Request):
    if len(request.announcement_text) > 50_000:
        raise HTTPException(
            status_code=422,
            detail=ApiError(
                code="input_too_large",
                message="Announcement text exceeds the 50,000-character limit.",
            ).model_dump(),
        )

    return await analyze_text(
        request.announcement_text,
        http_request.app.state.ollama_client,
    )
