from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.deps import get_db, get_current_user, require_vendedor
from app.crud.company import crud_company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyRead])
async def list_companies(
    skip: int = 0,
    limit: int = 20,
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    return await crud_company.get_multi(db, skip=skip, limit=limit, q=q)


@router.post("/", response_model=CompanyRead, status_code=201)
async def create_company(
    body: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    return await crud_company.create(db, obj_in=body)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    company = await crud_company.get(db, company_id)
    if not company:
        raise HTTPException(404, "Empresa no encontrada")
    return company


@router.patch("/{company_id}", response_model=CompanyRead)
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    company = await crud_company.get(db, company_id)
    if not company:
        raise HTTPException(404, "Empresa no encontrada")
    return await crud_company.update(db, db_obj=company, obj_in=body)


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    company = await crud_company.get(db, company_id)
    if not company:
        raise HTTPException(404, "Empresa no encontrada")
    await crud_company.remove(db, id=company_id)
