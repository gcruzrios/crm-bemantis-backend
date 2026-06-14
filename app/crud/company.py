from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.crud.base import CRUDBase
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        q: str | None = None,
    ) -> list[Company]:
        stmt = select(Company)
        if q:
            stmt = stmt.where(
                or_(
                    Company.name.ilike(f"%{q}%"),
                    Company.industry.ilike(f"%{q}%"),
                    Company.city.ilike(f"%{q}%"),
                )
            )
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


crud_company = CRUDCompany(Company)
