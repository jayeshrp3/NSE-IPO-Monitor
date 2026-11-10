"""IPO JSON API."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_ipo_service
from app.schemas.ipo import IPOCreate, IPOResponse, IPOUpdate
from app.services.ipo_service import IPOService

router = APIRouter(prefix="/api/ipos", tags=["ipos"])
ServiceDependency = Annotated[IPOService, Depends(get_ipo_service)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=IPOResponse)
def create_ipo(payload: IPOCreate, service: ServiceDependency) -> IPOResponse:
    return IPOResponse.model_validate(service.create(payload.model_dump()))


@router.get("", response_model=list[IPOResponse])
def list_ipos(
    service: ServiceDependency,
    company_name: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    sort: str = Query(default="opening_date"),
    order: str = Query(default="asc"),
) -> list[IPOResponse]:
    records = service.list(
        company_name=company_name,
        status=status_filter,
        sort=sort,
        order=order,
    )
    return [IPOResponse.model_validate(record) for record in records]


@router.get("/{ipo_id}", response_model=IPOResponse)
def get_ipo(ipo_id: int, service: ServiceDependency) -> IPOResponse:
    result = service.get(ipo_id)
    if result is None:
        raise HTTPException(status_code=404, detail="IPO record not found.")
    return IPOResponse.model_validate(result)


@router.put("/{ipo_id}", response_model=IPOResponse)
def update_ipo(ipo_id: int, payload: IPOUpdate, service: ServiceDependency) -> IPOResponse:
    result = service.update(ipo_id, payload.model_dump(), payload.model_fields_set)
    if result is None:
        raise HTTPException(status_code=404, detail="IPO record not found.")
    return IPOResponse.model_validate(result)


@router.delete("/{ipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ipo(ipo_id: int, service: ServiceDependency) -> Response:
    if not service.delete(ipo_id):
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="IPO record not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
