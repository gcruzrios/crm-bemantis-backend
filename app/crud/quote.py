from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.models.quote import Quote
from app.models.quote_item import QuoteItem
from app.schemas.quote import QuoteCreate, QuoteUpdate
from app.utils.quote_number import generate_quote_number
from app.core.enums import QuoteStatus


def _with_items(stmt):
    return stmt.options(selectinload(Quote.items))


class CRUDQuote(CRUDBase[Quote, QuoteCreate, QuoteUpdate]):

    async def get(self, db: AsyncSession, id) -> Quote | None:
        result = await db.execute(_with_items(select(Quote).where(Quote.id == id)))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: QuoteCreate) -> Quote:
        items_data = obj_in.items
        quote_data = obj_in.model_dump(exclude={"items"})
        quote_data["quote_number"] = await generate_quote_number(db)

        subtotal = sum(Decimal(str(i.quantity)) * Decimal(str(i.unit_price)) for i in items_data)
        tax_rate = Decimal(str(quote_data.get("tax_rate", 13)))
        quote_data["subtotal"] = subtotal
        quote_data["total"] = subtotal * (1 + tax_rate / 100)

        db_quote = Quote(**quote_data)
        db.add(db_quote)
        await db.flush()

        for item in items_data:
            db.add(QuoteItem(quote_id=db_quote.id, **item.model_dump()))

        await db.commit()
        return await self.get(db, db_quote.id)

    async def update_with_items(self, db: AsyncSession, *, db_obj: Quote, obj_in: QuoteUpdate) -> Quote:
        data = obj_in.model_dump(exclude_unset=True, exclude={"items"})
        for field, value in data.items():
            setattr(db_obj, field, value)

        if obj_in.items is not None:
            await db.execute(
                QuoteItem.__table__.delete().where(QuoteItem.quote_id == db_obj.id)
            )
            items_data = obj_in.items
            for item in items_data:
                db.add(QuoteItem(quote_id=db_obj.id, **item.model_dump()))

            subtotal = sum(Decimal(str(i.quantity)) * Decimal(str(i.unit_price)) for i in items_data)
            tax_rate = Decimal(str(db_obj.tax_rate))
            db_obj.subtotal = subtotal
            db_obj.total = subtotal * (1 + tax_rate / 100)

        db.add(db_obj)
        await db.commit()
        return await self.get(db, db_obj.id)

    async def mark_sent(self, db: AsyncSession, *, db_obj: Quote) -> Quote:
        db_obj.status = QuoteStatus.enviada
        db_obj.sent_at = datetime.now(timezone.utc)
        db.add(db_obj)
        await db.commit()
        return await self.get(db, db_obj.id)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        deal_id: str | None = None,
        status: QuoteStatus | None = None,
    ) -> list[Quote]:
        stmt = _with_items(select(Quote))
        if deal_id:
            stmt = stmt.where(Quote.deal_id == deal_id)
        if status:
            stmt = stmt.where(Quote.status == status)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())


crud_quote = CRUDQuote(Quote)
