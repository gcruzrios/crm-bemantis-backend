from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password


async def init_db(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.role == "admin"))
    if result.scalars().first():
        return

    admin = User(
        name="Administrador",
        email="admin@bemantis.com",
        hashed_pw=hash_password("Admin1234!"),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    await db.commit()
