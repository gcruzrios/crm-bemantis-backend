from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.crud.base import CRUDBase
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityUpdate
from app.core.enums import ActivityType


class CRUDActivity(CRUDBase[Activity, ActivityCreate, ActivityUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: ActivityCreate, owner_id: str) -> Activity:
        db_obj = Activity(**obj_in.model_dump(), owner_id=owner_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def complete(self, db: AsyncSession, *, db_obj: Activity) -> Activity:
        db_obj.completed_at = datetime.now(timezone.utc)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        deal_id: str | None = None,
        owner_id: str | None = None,
        type: ActivityType | None = None,
    ) -> list[Activity]:
        stmt = select(Activity)
        if deal_id:
            stmt = stmt.where(Activity.deal_id == deal_id)
        if owner_id:
            stmt = stmt.where(Activity.owner_id == owner_id)
        if type:
            stmt = stmt.where(Activity.type == type)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_pending(self, db: AsyncSession, *, owner_id: str) -> list[Activity]:
        result = await db.execute(
            select(Activity)
            .where(Activity.owner_id == owner_id, Activity.completed_at.is_(None))
            .order_by(Activity.due_date.asc())
            .limit(20)
        )
        return list(result.scalars().all())


crud_activity = CRUDActivity(Activity)
