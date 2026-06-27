from fastapi import FastAPI

from database import Base, engine
import models

app = FastAPI(title="Simple Uptime Monitoring Service")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
