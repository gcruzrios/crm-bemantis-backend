from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from app.core.deps import get_db, get_current_user
from app.models.deal import Deal
from app.models.quote import Quote
from app.core.enums import DealStage, QuoteStatus

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def summary(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    pipeline_total = await db.scalar(
        select(func.coalesce(func.sum(Deal.estimated_value), 0)).where(
            Deal.stage.notin_([DealStage.ganado, DealStage.perdido])
        )
    )

    closed_deals = await db.scalar(
        select(func.count(Deal.id)).where(
            Deal.stage.in_([DealStage.ganado, DealStage.perdido])
        )
    )
    won_deals = await db.scalar(
        select(func.count(Deal.id)).where(Deal.stage == DealStage.ganado)
    )
    close_rate = round((won_deals / closed_deals * 100), 1) if closed_deals else 0.0

    stages_result = await db.execute(
        select(Deal.stage, func.count(Deal.id).label("count"))
        .group_by(Deal.stage)
    )
    deals_by_stage = {row.stage: row.count for row in stages_result}

    return {
        "pipeline_total": float(pipeline_total or 0),
        "close_rate_pct": close_rate,
        "won_deals": won_deals,
        "lost_deals": closed_deals - won_deals if closed_deals else 0,
        "deals_by_stage": deals_by_stage,
    }


@router.get("/pipeline")
async def pipeline(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(
            Deal.stage,
            func.count(Deal.id).label("count"),
            func.coalesce(func.sum(Deal.estimated_value), 0).label("total_value"),
        ).group_by(Deal.stage)
    )
    return [
        {"stage": row.stage, "count": row.count, "total_value": float(row.total_value)}
        for row in result
    ]


@router.get("/activities/pending")
async def pending_activities(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.crud.activity import crud_activity
    from app.schemas.activity import ActivityRead
    activities = await crud_activity.get_pending(db, owner_id=str(current_user.id))
    return [ActivityRead.model_validate(a) for a in activities]


@router.get("/quotes/recent")
async def recent_quotes(
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    from app.schemas.quote import QuoteRead
    result = await db.execute(
        select(Quote)
        .options(selectinload(Quote.items))
        .order_by(Quote.created_at.desc())
        .limit(10)
    )
    quotes = result.scalars().all()
    return [QuoteRead.model_validate(q) for q in quotes]
