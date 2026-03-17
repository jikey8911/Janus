import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.api_v1.endpoints import status
from app.api.api_v1.endpoints import telegram_webhook

app = FastAPI(title="Project Janus API", version="2.0.0")

# Montar archivos estáticos del frontend
frontend_path = "/home/ubuntu/Janus/frontend/dist/public"
assets_path = f"{frontend_path}/assets"

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="static")

app.include_router(status.router, prefix="/api/v1")
app.include_router(telegram_webhook.router, prefix="/api/v1")

@app.get("/")
async def serve_frontend():
    index_path = "/home/ubuntu/Janus/frontend/dist/public/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "Welcome to Project Janus API. Frontend not found."}

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Permitir acceso a API, docs y archivos estáticos
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        return {"detail": "Not Found"}
    
    # Servir archivos estáticos si existen
    static_path = f"{frontend_path}/{full_path}"
    if os.path.exists(static_path) and os.path.isfile(static_path):
        return FileResponse(static_path)
    
    # Fallback a index.html para rutas de React Router
    index_path = "/home/ubuntu/Janus/frontend/dist/public/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"detail": "Not Found"}
