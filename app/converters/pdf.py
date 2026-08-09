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
                if _looks_like_table(page):
                    table = _extract_tables(page)
                    if table:
                        chunks.append(table)
                text = page.get_text("text")
                if text.strip():
                    chunks.append(text.strip())
        finally:
            doc.close()

        return ConversionResult(markdown="\n\n".join(chunks).strip())


def _looks_like_table(page: pymupdf.Page, max_words: int = 400) -> bool:
    """Heurística barata para evitar `find_tables()` em páginas de prosa.

    Páginas de texto denso tornam o `find_tables()` (análise de layout O(n²))
    muito lento em PDFs grandes. Só rodamos a extração de tabelas quando as
    palavras da página estão alinhadas em 2+ colunas consistentes.
    """
    words = page.get_text("words")
    if not words or len(words) > max_words:
        return False

    rows: dict[int, list[object]] = {}
    for word in words:
        key = round(word[3] / 8)  # y1/8 agrupa linhas próximas
        rows.setdefault(key, []).append(word)

    column_rows = 0
    for ws in rows.values():
        x0s = sorted({round(w[0]) for w in ws})
        cols = 1
        for i in range(1, len(x0s)):
            if x0s[i] - x0s[i - 1] > 50:
                cols += 1
        if cols >= 2:
            column_rows += 1

    return bool(rows) and column_rows / len(rows) >= 0.5


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
