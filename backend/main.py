import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
import models
from monitor.worker import run_monitor_loop
from redis_client import redis_client
from routers.auth import router as auth_router
from routers.targets import router as targets_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.redis = redis_client
    await app.state.redis.ping()
    app.state.monitor_task = asyncio.create_task(run_monitor_loop(app))

    try:
        yield
    finally:
        app.state.monitor_task.cancel()
        try:
            await app.state.monitor_task
        except asyncio.CancelledError:
            pass
        await app.state.redis.aclose()


app = FastAPI(title="Simple Uptime Monitoring Service", lifespan=lifespan)
app.include_router(auth_router, prefix="/api")
app.include_router(targets_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
