from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, require_admin
from app.crud.user import crud_user
from app.schemas.user import UserCreate, UserUpdate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await crud_user.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    if await crud_user.get_by_email(db, body.email):
        raise HTTPException(400, "El correo ya está registrado")
    return await crud_user.create(db, obj_in=body)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    user = await crud_user.get(db, user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    user = await crud_user.get(db, user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    return await crud_user.update(db, db_obj=user, obj_in=body)


@router.delete("/{user_id}", response_model=UserRead)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    user = await crud_user.get(db, user_id)
    if not user:
        raise HTTPException(404, "Usuario no encontrado")
    return await crud_user.deactivate(db, user=user)
