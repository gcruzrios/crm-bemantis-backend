from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user, require_admin, require_vendedor
from app.crud.service import crud_service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceRead

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=list[ServiceRead])
async def list_services(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    return await crud_service.get_active(db)


@router.post("/", response_model=ServiceRead, status_code=201)
async def create_service(
    body: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await crud_service.create(db, obj_in=body)


@router.patch("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: str,
    body: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    service = await crud_service.get(db, service_id)
    if not service:
        raise HTTPException(404, "Servicio no encontrado")
    return await crud_service.update(db, db_obj=service, obj_in=body)


@router.delete("/{service_id}", response_model=ServiceRead)
async def deactivate_service(
    service_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    service = await crud_service.get(db, service_id)
    if not service:
        raise HTTPException(404, "Servicio no encontrado")
    return await crud_service.deactivate(db, service=service)
