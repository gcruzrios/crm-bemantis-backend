from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    async def get_active(self, db: AsyncSession) -> list[Service]:
        result = await db.execute(select(Service).where(Service.is_active == True))
        return list(result.scalars().all())

    async def deactivate(self, db: AsyncSession, *, service: Service) -> Service:
        service.is_active = False
        db.add(service)
        await db.commit()
        await db.refresh(service)
        return service


crud_service = CRUDService(Service)
