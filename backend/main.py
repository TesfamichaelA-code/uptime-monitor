from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
import models
from redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.redis = redis_client
    await app.state.redis.ping()

    try:
        yield
    finally:
        await app.state.redis.aclose()


app = FastAPI(title="Simple Uptime Monitoring Service", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
