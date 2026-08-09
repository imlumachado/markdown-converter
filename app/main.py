from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import download, upload
from app.middleware import RateLimitMiddleware

app = FastAPI(
    title="Markdown Converter",
    description="Conversor de DOCX, XLSX, PPTX e PDF para Markdown.",
    version="0.1.0",
)

app.add_middleware(RateLimitMiddleware, max_requests=10, window_seconds=60)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(upload.router)
app.include_router(download.router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}
