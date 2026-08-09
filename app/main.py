from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import download, upload
from app.config import BASE_URL, GA_ID
from app.middleware import RateLimitMiddleware
from app.seo import ROBOTS_TXT, build_sitemap

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
        context={"ga_id": GA_ID},
    )


@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots():
    return PlainTextResponse(ROBOTS_TXT.format(sitemap_url=f"{BASE_URL}/sitemap.xml"))


@app.get("/sitemap.xml", response_class=Response, include_in_schema=False)
async def sitemap():
    return Response(content=build_sitemap(BASE_URL), media_type="application/xml")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
