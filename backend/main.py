from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Nexus Core API",
    description="The intelligence layer for Nexus SaaS",
    version="1.0.0"
)

class HealthCheck(BaseModel):
    status: str = "OK"
    system: str = "Nexus Core"
    version: str = "1.0.0"

@app.get("/", response_model=HealthCheck)
async def root():
    """
    Health Check Endpoint.
    Used to verify if the brain is online.
    """
    return HealthCheck()

@app.get("/api/v1/status")
async def status():
    return {"status": "operational", "mode": "MVP"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
