from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from app.models.quote import Quote


async def generate_quote_number(db: AsyncSession) -> str:
    year = datetime.now().year
    result = await db.execute(
        select(func.count(Quote.id)).where(
            extract("year", Quote.created_at) == year
        )
    )
    count = (result.scalar() or 0) + 1
    return f"COT-{year}-{count:03d}"
