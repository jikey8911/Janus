from fastapi import FastAPI
from app.api.api_v1.endpoints import status

app = FastAPI(title="Project Janus API", version="1.0.0")

app.include_router(status.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Project Janus API. Visit /docs for documentation."}
