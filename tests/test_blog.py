from __future__ import annotations

import app.services.blog as blog


def _article_text(slug: str, title: str, date: str) -> str:
    return (
        "---\n"
        f"title: {title}\n"
        "description: Descrição de teste para o artigo.\n"
        f"date: {date}\n"
        "category: Tutoriais\n"
        f"slug: {slug}\n"
        "---\n\n"
        f"# {title}\n\nCorpo do artigo."
    )


def test_parse_frontmatter(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(blog, "BLOG_DIR", tmp_path)
    (tmp_path / "teste.md").write_text(
        _article_text("artigo-teste", "Artigo Teste", "2026-01-01"),
        encoding="utf-8",
    )

    articles = blog.load_articles()
    assert len(articles) == 1
    article = articles[0]
    assert article.slug == "artigo-teste"
    assert article.title == "Artigo Teste"
    assert article.url == "/blog/artigo-teste"
    assert "<h1>" in article.html


def test_articles_sorted_by_date_desc(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(blog, "BLOG_DIR", tmp_path)
    (tmp_path / "antigo.md").write_text(
        _article_text("antigo", "Artigo Antigo", "2025-01-01"),
        encoding="utf-8",
    )
    (tmp_path / "novo.md").write_text(
        _article_text("novo", "Artigo Novo", "2026-01-01"),
        encoding="utf-8",
    )

    articles = blog.load_articles()
    assert [a.slug for a in articles] == ["novo", "antigo"]


def test_slug_falls_back_to_filename(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(blog, "BLOG_DIR", tmp_path)
    (tmp_path / "sem-slug.md").write_text(
        "---\n"
        "title: Sem Slug\n"
        "description: Desc.\n"
        "date: 2026-01-01\n"
        "category: Tutoriais\n"
        "---\n\n"
        "Corpo.",
        encoding="utf-8",
    )

    articles = blog.load_articles()
    assert articles[0].slug == "sem-slug"


def test_invalid_article_is_skipped(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(blog, "BLOG_DIR", tmp_path)
    (tmp_path / "quebrado.md").write_text("sem frontmatter aqui", encoding="utf-8")
    (tmp_path / "ok.md").write_text(
        _article_text("ok", "OK", "2026-01-01"),
        encoding="utf-8",
    )

    assert len(blog.load_articles()) == 1


def test_get_article(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(blog, "BLOG_DIR", tmp_path)
    (tmp_path / "um.md").write_text(
        _article_text("um", "Um", "2026-01-01"),
        encoding="utf-8",
    )

    assert blog.get_article("um") is not None
    assert blog.get_article("nao-existe") is None
