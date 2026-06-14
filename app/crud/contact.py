from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class CRUDContact(CRUDBase[Contact, ContactCreate, ContactUpdate]):
    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        company_id: str | None = None,
    ) -> list[Contact]:
        stmt = select(Contact)
        if company_id:
            stmt = stmt.where(Contact.company_id == company_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


crud_contact = CRUDContact(Contact)
