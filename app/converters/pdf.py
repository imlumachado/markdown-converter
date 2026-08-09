from __future__ import annotations

from pathlib import Path

import pymupdf

from app.converters.base import BaseConverter, ConversionResult


class PdfConverter(BaseConverter):
    """Converte documentos PDF para Markdown usando PyMuPDF.

    PyMuPDF é muito mais rápido que pdfplumber (motor do MarkItDown)
    para extração de texto em PDFs grandes.
    """

    def convert(self, source: Path, output_dir: Path) -> ConversionResult:
        doc = pymupdf.open(source)
        chunks: list[str] = []
        try:
            for page in doc:
                table = _extract_tables(page)
                if table:
                    chunks.append(table)
                text = page.get_text("text")
                if text.strip():
                    chunks.append(text.strip())
        finally:
            doc.close()

        return ConversionResult(markdown="\n\n".join(chunks).strip())


def _extract_tables(page: pymupdf.Page) -> str:
    """Extrai tabelas da página em formato Markdown, se houver."""
    tables = page.find_tables()
    if not tables.tables:
        return ""
    out: list[str] = []
    for table in tables.tables:
        header, *rows = table.extract()
        if header is None:
            continue
        cols = len(header)
        out.append("| " + " | ".join(_cell(c) for c in header) + " |")
        out.append("| " + " | ".join("---" for _ in range(cols)) + " |")
        for row in rows:
            cells = [_cell(c) for c in row]
            if len(cells) < cols:
                cells += [""] * (cols - len(cells))
            out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def _cell(value: object) -> str:
    text = str(value) if value is not None else ""
    return text.replace("|", "\\|").strip()
