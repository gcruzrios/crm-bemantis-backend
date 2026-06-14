from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.deps import get_db, get_current_user, require_vendedor
from app.crud.contact import crud_contact
from app.schemas.contact import ContactCreate, ContactUpdate, ContactRead

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=list[ContactRead])
async def list_contacts(
    skip: int = 0,
    limit: int = 20,
    company_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    return await crud_contact.get_multi(db, skip=skip, limit=limit, company_id=company_id)


@router.post("/", response_model=ContactRead, status_code=201)
async def create_contact(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    return await crud_contact.create(db, obj_in=body)


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    contact = await crud_contact.get(db, contact_id)
    if not contact:
        raise HTTPException(404, "Contacto no encontrado")
    return contact


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: str,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    contact = await crud_contact.get(db, contact_id)
    if not contact:
        raise HTTPException(404, "Contacto no encontrado")
    return await crud_contact.update(db, db_obj=contact, obj_in=body)


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(
    contact_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    contact = await crud_contact.get(db, contact_id)
    if not contact:
        raise HTTPException(404, "Contacto no encontrado")
    await crud_contact.remove(db, id=contact_id)
