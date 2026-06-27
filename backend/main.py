from fastapi import FastAPI

app = FastAPI(title="Simple Uptime Monitoring Service")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
