from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.deps import get_db, get_current_user, require_vendedor
from app.crud.deal import crud_deal
from app.schemas.deal import DealCreate, DealUpdate, DealStageUpdate, DealRead
from app.core.enums import DealStage

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("/", response_model=list[DealRead])
async def list_deals(
    skip: int = 0,
    limit: int = 20,
    stage: Optional[DealStage] = None,
    owner_id: Optional[str] = None,
    company_id: Optional[str] = None,
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    return await crud_deal.get_multi(
        db, skip=skip, limit=limit, stage=stage, owner_id=owner_id,
        company_id=company_id, q=q
    )


@router.post("/", response_model=DealRead, status_code=201)
async def create_deal(
    body: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_vendedor),
):
    return await crud_deal.create(db, obj_in=body, owner_id=str(current_user.id))


@router.get("/{deal_id}", response_model=DealRead)
async def get_deal(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    deal = await crud_deal.get(db, deal_id)
    if not deal:
        raise HTTPException(404, "Negocio no encontrado")
    return deal


@router.patch("/{deal_id}", response_model=DealRead)
async def update_deal(
    deal_id: str,
    body: DealUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    deal = await crud_deal.get(db, deal_id)
    if not deal:
        raise HTTPException(404, "Negocio no encontrado")
    return await crud_deal.update(db, db_obj=deal, obj_in=body)


@router.patch("/{deal_id}/stage", response_model=DealRead)
async def update_deal_stage(
    deal_id: str,
    body: DealStageUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    deal = await crud_deal.get(db, deal_id)
    if not deal:
        raise HTTPException(404, "Negocio no encontrado")
    return await crud_deal.update(db, db_obj=deal, obj_in=body)


@router.delete("/{deal_id}", status_code=204)
async def delete_deal(
    deal_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    deal = await crud_deal.get(db, deal_id)
    if not deal:
        raise HTTPException(404, "Negocio no encontrado")
    await crud_deal.remove(db, id=deal_id)
