from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.deps import get_db, get_current_user, require_vendedor
from app.crud.quote import crud_quote
from app.schemas.quote import QuoteCreate, QuoteUpdate, QuoteStatusUpdate, QuoteRead
from app.core.enums import QuoteStatus
from app.utils.quote_pdf import generate_pdf_bytes

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/", response_model=list[QuoteRead])
async def list_quotes(
    skip: int = 0,
    limit: int = 20,
    deal_id: Optional[str] = None,
    status: Optional[QuoteStatus] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    return await crud_quote.get_multi(db, skip=skip, limit=limit, deal_id=deal_id, status=status)


@router.post("/", response_model=QuoteRead, status_code=201)
async def create_quote(
    body: QuoteCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    return await crud_quote.create(db, obj_in=body)


@router.get("/{quote_id}", response_model=QuoteRead)
async def get_quote(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    quote = await crud_quote.get(db, quote_id)
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")
    return quote


@router.patch("/{quote_id}", response_model=QuoteRead)
async def update_quote(
    quote_id: str,
    body: QuoteUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    quote = await crud_quote.get(db, quote_id)
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")
    return await crud_quote.update_with_items(db, db_obj=quote, obj_in=body)


@router.post("/{quote_id}/send", response_model=QuoteRead)
async def send_quote(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    quote = await crud_quote.get(db, quote_id)
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")
    if quote.status != QuoteStatus.borrador:
        raise HTTPException(400, "La cotización ya fue enviada")
    return await crud_quote.mark_sent(db, db_obj=quote)


@router.patch("/{quote_id}/status", response_model=QuoteRead)
async def update_quote_status(
    quote_id: str,
    body: QuoteStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    quote = await crud_quote.get(db, quote_id)
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")
    return await crud_quote.update(db, db_obj=quote, obj_in=body)


@router.get("/{quote_id}/pdf")
async def download_pdf(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    quote = await crud_quote.get(db, quote_id)
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")
    pdf_bytes = generate_pdf_bytes(quote)
    filename = f"{quote.quote_number or quote_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{quote_id}", status_code=204)
async def delete_quote(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    quote = await crud_quote.get(db, quote_id)
    if not quote:
        raise HTTPException(404, "Cotización no encontrada")
    if quote.status != QuoteStatus.borrador:
        raise HTTPException(400, "Solo se pueden eliminar cotizaciones en borrador")
    await crud_quote.remove(db, id=quote_id)
