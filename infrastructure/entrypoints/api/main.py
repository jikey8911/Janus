import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.api_v1.endpoints import status
from app.api.api_v1.endpoints import telegram_webhook

app = FastAPI(title="Project Janus API", version="2.0.0")

# Montar archivos estáticos del frontend
frontend_path = "/home/ubuntu/Janus/frontend/dist/public"
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=f"{frontend_path}/assets"), name="static")

app.include_router(status.router, prefix="/api/v1")
app.include_router(telegram_webhook.router, prefix="/api/v1")

@app.get("/")
async def serve_frontend():
    index_path = "/home/ubuntu/Janus/frontend/dist/public/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Project Janus API. Frontend not found."}

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Esto permite que React Router maneje las rutas
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        return {"detail": "Not Found"}
    
    index_path = "/home/ubuntu/Janus/frontend/dist/public/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not Found"}
