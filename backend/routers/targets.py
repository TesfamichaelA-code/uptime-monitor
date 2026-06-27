import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from deps import get_current_user
from models import Check, Target, User
from schemas import CheckOut, StatsOut, TargetCreate, TargetOut

router = APIRouter(prefix="/targets", tags=["targets"])


def validate_url(url: str) -> None:
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must start with http:// or https://",
        )


def empty_status() -> dict[str, bool | float | str | None]:
    return {"is_up": None, "last_latency_ms": None, "last_checked": None}


def parse_target_status(raw_status: str | None) -> dict[str, bool | float | str | None]:
    if raw_status is None:
        return empty_status()

    try:
        status_data = json.loads(raw_status)
    except json.JSONDecodeError:
        return empty_status()

    return {
        "is_up": status_data.get("is_up"),
        "last_latency_ms": status_data.get("last_latency_ms", status_data.get("latency_ms")),
        "last_checked": status_data.get("last_checked", status_data.get("checked_at")),
    }


def target_response(target: Target, status_data: dict[str, bool | float | str | None] | None = None) -> TargetOut:
    status_data = status_data or empty_status()
    return TargetOut(
        id=target.id,
        user_id=target.user_id,
        name=target.name,
        url=target.url,
        is_active=target.is_active,
        created_at=target.created_at,
        is_up=status_data["is_up"],
        last_latency_ms=status_data["last_latency_ms"],
        last_checked=status_data["last_checked"],
    )


def calculate_uptime_percent(up_count: int, total_count: int) -> float:
    if total_count == 0:
        return 0.0
    return float(up_count) / float(total_count) * 100.0


async def get_target_for_user(target_id: int, current_user: User, db: AsyncSession) -> Target:
    target = await db.get(Target, target_id)
    if target is None or not target.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
    if target.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return target


@router.post("", response_model=TargetOut, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_data: TargetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TargetOut:
    validate_url(target_data.url)

    target = Target(
        user_id=current_user.id,
        name=target_data.name,
        url=target_data.url,
    )
    db.add(target)
    await db.commit()
    await db.refresh(target)

    return target_response(target)


@router.get("", response_model=list[TargetOut])
async def list_targets(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TargetOut]:
    targets = (
        await db.scalars(
            select(Target)
            .where(Target.user_id == current_user.id, Target.is_active.is_(True))
            .order_by(Target.id)
        )
    ).all()

    responses: list[TargetOut] = []
    for target in targets:
        raw_status = await request.app.state.redis.get(f"status:{target.id}")
        responses.append(target_response(target, parse_target_status(raw_status)))

    return responses


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    target = await db.get(Target, target_id)
    if target is None or target.user_id != current_user.id or not target.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    target.is_active = False
    await db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{target_id}/stats", response_model=StatsOut)
async def get_target_stats(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StatsOut:
    target = await get_target_for_user(target_id, current_user, db)
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(hours=24)
    since_7d = now - timedelta(days=7)

    total_24h = await db.scalar(
        select(func.count()).where(Check.target_id == target.id, Check.checked_at >= since_24h)
    )
    up_24h = await db.scalar(
        select(func.count()).where(
            Check.target_id == target.id,
            Check.checked_at >= since_24h,
            Check.is_up.is_(True),
        )
    )
    total_7d = await db.scalar(
        select(func.count()).where(Check.target_id == target.id, Check.checked_at >= since_7d)
    )
    up_7d = await db.scalar(
        select(func.count()).where(
            Check.target_id == target.id,
            Check.checked_at >= since_7d,
            Check.is_up.is_(True),
        )
    )
    avg_latency_24h = await db.scalar(
        select(func.avg(Check.latency_ms)).where(
            Check.target_id == target.id,
            Check.checked_at >= since_24h,
            Check.latency_ms.is_not(None),
        )
    )

    total_24h_count = int(total_24h or 0)
    up_24h_count = int(up_24h or 0)
    total_7d_count = int(total_7d or 0)
    up_7d_count = int(up_7d or 0)

    return StatsOut(
        uptime_percent_24h=calculate_uptime_percent(up_24h_count, total_24h_count),
        avg_latency_24h=float(avg_latency_24h) if avg_latency_24h is not None else None,
        uptime_percent_7d=calculate_uptime_percent(up_7d_count, total_7d_count),
        total_checks=total_7d_count,
    )


@router.get("/{target_id}/history", response_model=list[CheckOut])
async def get_target_history(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CheckOut]:
    target = await get_target_for_user(target_id, current_user, db)
    checks = (
        await db.scalars(
            select(Check)
            .where(Check.target_id == target.id)
            .order_by(Check.checked_at.desc())
            .limit(100)
        )
    ).all()
    return list(checks)

