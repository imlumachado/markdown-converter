from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import markdown as md

BLOG_DIR = Path("content/blog")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.S)
_MD = md.Markdown(extensions=["tables", "fenced_code", "nl2br"])


@dataclass(frozen=True)
class Article:
    slug: str
    title: str
    description: str
    date: str
    category: str
    body: str
    html: str = field(compare=False)

    @property
    def url(self) -> str:
        return f"/blog/{self.slug}"


def _parse(text: str) -> Article:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("Artigo sem frontmatter (--- title/description/date/category ---)")

    raw, body = match.groups()
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip()
    for key in ("title", "description", "date", "category"):
        if key not in meta:
            raise ValueError(f"Frontmatter sem campo obrigatório: {key}")

    html = _MD.reset().convert(body)
    return Article(
        slug=meta["slug"] if "slug" in meta else "",
        title=meta["title"],
        description=meta["description"],
        date=meta["date"],
        category=meta["category"],
        body=body,
        html=html,
    )


def load_articles() -> list[Article]:
    """Carrega todos os artigos, ordenados por data (mais recente primeiro)."""
    articles: list[Article] = []
    if not BLOG_DIR.is_dir():
        return articles
    for path in sorted(BLOG_DIR.glob("*.md")):
        try:
            article = _parse(path.read_text(encoding="utf-8"))
            article = Article(
                slug=article.slug or path.stem,
                title=article.title,
                description=article.description,
                date=article.date,
                category=article.category,
                body=article.body,
                html=article.html,
            )
            articles.append(article)
        except (ValueError, OSError):
            continue
    return sorted(articles, key=lambda a: a.date, reverse=True)


def get_article(slug: str) -> Article | None:
    for article in load_articles():
        if article.slug == slug:
            return article
    return None
