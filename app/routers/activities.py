from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.deps import get_db, get_current_user, require_vendedor
from app.crud.activity import crud_activity
from app.schemas.activity import ActivityCreate, ActivityUpdate, ActivityRead
from app.core.enums import ActivityType

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=list[ActivityRead])
async def list_activities(
    skip: int = 0,
    limit: int = 20,
    deal_id: Optional[str] = None,
    owner_id: Optional[str] = None,
    type: Optional[ActivityType] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    return await crud_activity.get_multi(
        db, skip=skip, limit=limit, deal_id=deal_id, owner_id=owner_id, type=type
    )


@router.post("/", response_model=ActivityRead, status_code=201)
async def create_activity(
    body: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_vendedor),
):
    return await crud_activity.create(db, obj_in=body, owner_id=str(current_user.id))


@router.patch("/{activity_id}", response_model=ActivityRead)
async def update_activity(
    activity_id: str,
    body: ActivityUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    activity = await crud_activity.get(db, activity_id)
    if not activity:
        raise HTTPException(404, "Actividad no encontrada")
    return await crud_activity.update(db, db_obj=activity, obj_in=body)


@router.patch("/{activity_id}/complete", response_model=ActivityRead)
async def complete_activity(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    activity = await crud_activity.get(db, activity_id)
    if not activity:
        raise HTTPException(404, "Actividad no encontrada")
    if activity.completed_at:
        raise HTTPException(400, "La actividad ya fue completada")
    return await crud_activity.complete(db, db_obj=activity)


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_vendedor),
):
    activity = await crud_activity.get(db, activity_id)
    if not activity:
        raise HTTPException(404, "Actividad no encontrada")
    await crud_activity.remove(db, id=activity_id)
