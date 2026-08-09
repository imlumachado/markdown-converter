from __future__ import annotations

SITEMAP_PATHS: list[str] = ["/"]

ROBOTS_TXT = """User-agent: *
Allow: /

Sitemap: {sitemap_url}
"""


def build_sitemap(base_url: str, paths: list[str] | None = None) -> str:
    """Gera o sitemap.xml a partir de uma lista de caminhos."""
    paths = paths if paths is not None else SITEMAP_PATHS
    urls = "\n".join(f"  <url><loc>{base_url}{path}</loc></url>" for path in paths)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
