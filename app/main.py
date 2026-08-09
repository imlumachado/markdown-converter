from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import download, upload
from app.config import (
    ADSENSE_CLIENT,
    ADSENSE_ENABLED,
    ADSENSE_SLOT,
    BASE_URL,
    GA_ID,
    MAX_CONCURRENT_JOBS,
    MAX_JOBS_PER_IP,
)
from app.middleware import CacheControlMiddleware, RateLimitMiddleware
from app.seo import ROBOTS_TXT, build_sitemap
from app.services.blog import get_article, load_articles
from app.services.concurrency import JobTracker
from app.services.legal import CONTACT_CONTENT, CONTACT_DESCRIPTION, CONTACT_TITLE, PRIVACY_CONTENT, PRIVACY_DESCRIPTION, PRIVACY_TITLE, TERMS_CONTENT, TERMS_DESCRIPTION, TERMS_TITLE

app = FastAPI(
    title="Markdown Converter",
    description="Conversor de DOCX, XLSX, PPTX e PDF para Markdown.",
    version="0.1.0",
)

app.state.job_tracker = JobTracker(MAX_CONCURRENT_JOBS, MAX_JOBS_PER_IP)

app.add_middleware(CacheControlMiddleware)
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
        context={
            "ga_id": GA_ID,
            "base_url": BASE_URL,
            "adsense_enabled": ADSENSE_ENABLED,
            "adsense_client": ADSENSE_CLIENT,
            "adsense_slot": ADSENSE_SLOT,
        },
    )


@app.get("/blog", response_class=HTMLResponse)
async def blog_list(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="blog.html",
        context={"ga_id": GA_ID, "base_url": BASE_URL, "articles": load_articles()},
    )


@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_article(request: Request, slug: str):
    article = get_article(slug)
    if article is None:
        return HTMLResponse("Artigo não encontrado", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="article.html",
        context={"ga_id": GA_ID, "base_url": BASE_URL, "article": article},
    )


def _page(request: Request, title: str, description: str, content: str, url: str):
    return templates.TemplateResponse(
        request=request,
        name="page.html",
        context={
            "ga_id": GA_ID,
            "base_url": BASE_URL,
            "page_title": title,
            "page_description": description,
            "page_url": url,
            "content": content,
        },
    )


@app.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return _page(request, PRIVACY_TITLE, PRIVACY_DESCRIPTION, PRIVACY_CONTENT, "/privacy")


@app.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return _page(request, TERMS_TITLE, TERMS_DESCRIPTION, TERMS_CONTENT, "/terms")


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return _page(request, CONTACT_TITLE, CONTACT_DESCRIPTION, CONTACT_CONTENT, "/contact")


@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots():
    return PlainTextResponse(ROBOTS_TXT.format(sitemap_url=f"{BASE_URL}/sitemap.xml"))


@app.get("/ads.txt", response_class=PlainTextResponse, include_in_schema=False)
async def ads():
    if not ADSENSE_CLIENT:
        return PlainTextResponse("# AdSense não configurado. Defina ADSENSE_CLIENT no ambiente.\n")
    publisher = ADSENSE_CLIENT.replace("ca-", "pub-") if not ADSENSE_CLIENT.startswith("pub-") else ADSENSE_CLIENT
    return PlainTextResponse(f"google.com, {publisher}, DIRECT, f08c47fec0942fa0\n")


@app.get("/sitemap.xml", response_class=Response, include_in_schema=False)
async def sitemap():
    return Response(content=build_sitemap(BASE_URL), media_type="application/xml")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
