from __future__ import annotations

from datetime import UTC, datetime

from app.services.blog import load_articles

SITEMAP_PATHS: list[str] = ["/", "/blog"]

ROBOTS_TXT = """User-agent: *
Allow: /

Sitemap: {sitemap_url}
"""


def sitemap_entries(base_url: str) -> list[tuple[str, str]]:
    """Retorna pares (caminho, lastmod ISO) para o sitemap, incluindo os artigos."""
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    entries: list[tuple[str, str]] = [(path, today) for path in SITEMAP_PATHS]
    for article in load_articles():
        entries.append((article.url, article.date))
    return entries


def build_sitemap(base_url: str, paths: list[str] | None = None) -> str:
    """Gera o sitemap.xml. Se `paths` for informado, ignora o blog."""
    if paths is not None:  # noqa: SIM108
        entries = [(path, "") for path in paths]
    else:
        entries = sitemap_entries(base_url)
    urls = "\n".join(
        "  <url><loc>{base}{path}</loc>{lastmod}</url>".format(
            base=base_url,
            path=path,
            lastmod=f"\n    <lastmod>{lastmod}</lastmod>" if lastmod else "",
        )
        for path, lastmod in entries
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
