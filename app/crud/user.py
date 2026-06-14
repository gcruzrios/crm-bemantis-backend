from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from app.core.config import settings


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        count = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
        if count >= settings.MAX_ACTIVE_USERS:
            raise HTTPException(400, f"Límite de {settings.MAX_ACTIVE_USERS} usuarios activos alcanzado")

        db_obj = User(
            name=obj_in.name,
            email=obj_in.email,
            hashed_pw=hash_password(obj_in.password),
            role=obj_in.role,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def deactivate(self, db: AsyncSession, *, user: User) -> User:
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def authenticate(self, db: AsyncSession, email: str, password: str) -> User | None:
        from app.core.security import verify_password
        user = await self.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_pw):
            return None
        return user


crud_user = CRUDUser(User)
