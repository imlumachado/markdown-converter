from __future__ import annotations

import json
import os
from pathlib import Path

import pymupdf

from app.converters.base import BaseConverter, ConversionResult

OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "por").strip() or "por"
OCR_DPI: int = int(os.getenv("OCR_DPI", "200"))


class PdfConverter(BaseConverter):
    """Converte documentos PDF para Markdown usando PyMuPDF.

    PyMuPDF é muito mais rápido que pdfplumber (motor do MarkItDown)
    para extração de texto em PDFs grandes. Páginas digitalizadas
    (sem camada de texto) são tratadas com OCR via Tesseract.
    """

    def convert(self, source: Path, output_dir: Path) -> ConversionResult:
        doc = pymupdf.open(source)
        chunks: list[str] = []
        ocr_pages = 0
        total_pages = len(doc)
        progress_file = os.getenv("CONVERSION_PROGRESS_FILE")
        try:
            for index, page in enumerate(doc):
                _write_progress(progress_file, index + 1, total_pages)
                if _looks_like_table(page):
                    table = _extract_tables(page)
                    if table:
                        chunks.append(table)
                text = page.get_text("text")
                if text.strip():
                    chunks.append(text.strip())
                else:
                    ocr_text = _ocr_page(page)
                    if ocr_text:
                        chunks.append(ocr_text)
                        ocr_pages += 1
        finally:
            doc.close()

        warnings: list[str] = []
        if ocr_pages:
            warnings.append(
                f"{ocr_pages} página(s) digitalizada(s) processada(s) via OCR "
                f"(idioma '{OCR_LANGUAGE}'). A precisão pode variar."
            )

        return ConversionResult(markdown="\n\n".join(chunks).strip(), warnings=warnings)


def _write_progress(progress_file: str | None, current: int, total: int) -> None:
    """Escreve o andamento da conversão em um arquivo JSON (usado pelo polling)."""
    if not progress_file:
        return
    try:
        payload = {"current": current, "total": total, "percent": round(current / total * 100) if total else 0}
        Path(progress_file).write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        pass


def _ocr_page(page: pymupdf.Page) -> str:
    """Extrai texto de uma página digitalizada usando OCR (Tesseract)."""
    try:
        textpage = page.get_textpage_ocr(
            language=OCR_LANGUAGE,
            full=True,
            dpi=OCR_DPI,
        )
        return (textpage.extractText() or "").strip()
    except RuntimeError:
        # Tesseract não instalado ou idioma indisponível
        return ""


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
