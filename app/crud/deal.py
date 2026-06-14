from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.crud.base import CRUDBase
from app.models.deal import Deal
from app.schemas.deal import DealCreate, DealUpdate
from app.core.enums import DealStage


class CRUDDeal(CRUDBase[Deal, DealCreate, DealUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: DealCreate, owner_id: str) -> Deal:
        db_obj = Deal(**obj_in.model_dump(), owner_id=owner_id)
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
        stage: DealStage | None = None,
        owner_id: str | None = None,
        company_id: str | None = None,
        q: str | None = None,
    ) -> list[Deal]:
        stmt = select(Deal)
        if stage:
            stmt = stmt.where(Deal.stage == stage)
        if owner_id:
            stmt = stmt.where(Deal.owner_id == owner_id)
        if company_id:
            stmt = stmt.where(Deal.company_id == company_id)
        if q:
            stmt = stmt.where(Deal.title.ilike(f"%{q}%"))
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


crud_deal = CRUDDeal(Deal)
