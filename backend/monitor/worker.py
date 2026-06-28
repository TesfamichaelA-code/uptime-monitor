import asyncio
import json
import time
from datetime import datetime

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alerting import notify_down, notify_recovery
from database import AsyncSessionLocal
from models import Check, Target, User


async def trigger_alert(
    db: AsyncSession,
    target: Target,
    is_up: bool,
    status_code: int,
    checked_at: datetime,
) -> None:
    owner = await db.get(User, target.user_id)
    if owner is None:
        return

    user_email = owner.notification_email or owner.email
    if is_up:
        await notify_recovery(target, user_email, status_code, checked_at)
    else:
        await notify_down(target, user_email, status_code, checked_at)


async def check_single_target(db: AsyncSession, redis, target: Target) -> None:
    start = time.time()
    is_up = False
    status_code = 0

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(target.url, allow_redirects=True) as response:
                status_code = response.status
                is_up = 200 <= response.status < 400
    except Exception:
        is_up = False
        status_code = 0

    latency_ms = round((time.time() - start) * 1000, 2)
    checked_at = datetime.utcnow()

    db.add(
        Check(
            target_id=target.id,
            status_code=status_code,
            latency_ms=latency_ms,
            is_up=is_up,
            checked_at=checked_at,
        )
    )
    await db.commit()

    prev_json = await redis.get(f"status:{target.id}")
    if prev_json is not None:
        try:
            prev = json.loads(prev_json)
            if prev["is_up"] != is_up:
                await trigger_alert(db, target, is_up, status_code, checked_at)
        except Exception as exc:
            print(f"alert failed for target {target.id}: {exc}", flush=True)

    await redis.set(
        f"status:{target.id}",
        json.dumps(
            {
                "is_up": is_up,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "checked_at": checked_at.isoformat(),
            }
        ),
    )


async def check_target_with_new_session(redis, target: Target) -> None:
    async with AsyncSessionLocal() as db:
        await check_single_target(db, redis, target)


async def run_monitor_loop(app) -> None:
    while True:
        try:
            redis = app.state.redis
            async with AsyncSessionLocal() as db:
                targets = (
                    await db.scalars(
                        select(Target).where(Target.is_active.is_(True)).order_by(Target.id)
                    )
                ).all()

            await asyncio.gather(
                *[check_target_with_new_session(redis, target) for target in targets]
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"monitor loop error: {exc}", flush=True)

        await asyncio.sleep(60)
