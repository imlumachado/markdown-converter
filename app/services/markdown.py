from __future__ import annotations

from pathlib import Path

from app.converters.base import ConversionResult


def convert_with_markitdown(source: Path, output_dir: Path) -> ConversionResult:
    """Converte `source` para Markdown usando MarkItDown como motor."""
    from markitdown import MarkItDown  # import tardio: evita custo fixo para PDFs

    md = MarkItDown()
    result = md.convert(source)
    return ConversionResult(
        markdown=result.text_content or "",
        title=result.title,
    )
