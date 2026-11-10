"""Server-rendered UI routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.api.deps import get_ipo_service
from app.core.errors import ValidationError
from app.services.ipo_service import IPOService

router = APIRouter(include_in_schema=False)
ServiceDependency = Annotated[IPOService, Depends(get_ipo_service)]


@router.get("/", response_class=HTMLResponse)
@router.get("/ipos", response_class=HTMLResponse)
def ipo_list(
    request: Request,
    service: ServiceDependency,
    company_name: str | None = None,
    status: str | None = None,
    sort: str = "opening_date",
    order: str = "asc",
) -> HTMLResponse:
    try:
        records = service.list(company_name=company_name, status=status, sort=sort, order=order)
        error = None
    except ValidationError as exc:
        records = []
        error = str(exc)
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="ipo_list.html",
        context={
            "records": records,
            "company_name": company_name or "",
            "selected_status": status or "",
            "sort": sort,
            "order": order,
            "error": error,
        },
    )


@router.get("/ipos/new", response_class=HTMLResponse)
def new_ipo(request: Request) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="ipo_form.html",
        context={"record": None, "page_title": "Add IPO"},
    )


@router.get("/ipos/{ipo_id}/edit", response_class=HTMLResponse)
def edit_ipo(
    request: Request,
    ipo_id: int,
    service: ServiceDependency,
) -> HTMLResponse:
    record = service.get(ipo_id)
    if record is None:
        raise HTTPException(status_code=404, detail="IPO record not found.")
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="ipo_form.html",
        context={"record": record, "page_title": "Edit IPO"},
    )


@router.get("/ipos/{ipo_id}", response_class=HTMLResponse)
def ipo_detail(
    request: Request,
    ipo_id: int,
    service: ServiceDependency,
) -> HTMLResponse:
    record = service.get(ipo_id)
    if record is None:
        raise HTTPException(status_code=404, detail="IPO record not found.")
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="ipo_detail.html",
        context={"record": record},
    )
