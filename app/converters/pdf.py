from __future__ import annotations

import json
import os
from pathlib import Path

import pymupdf

from app.converters.base import BaseConverter, ConversionResult

OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "por").strip() or "por"
OCR_LANGUAGE_FALLBACK: str = os.getenv("OCR_LANGUAGE_FALLBACK", "eng").strip() or "eng"
OCR_DPI: int = int(os.getenv("OCR_DPI", "200"))
OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").strip().lower() in ("1", "true", "yes", "on")


class PdfConverter(BaseConverter):
    """Converte documentos PDF para Markdown usando PyMuPDF.

    PyMuPDF é muito mais rápido que pdfplumber (motor do MarkItDown)
    para extração de texto em PDFs grandes. Páginas digitalizadas
    (sem camada de texto) são tratadas com OCR via Tesseract.
    """

    def convert(self, source: Path, output_dir: Path) -> ConversionResult:
        doc = pymupdf.open(source)
        chunks: list[str] = []
        ocr_pages: list[tuple[int, str]] = []
        total_pages = len(doc)
        progress_file = os.getenv("CONVERSION_PROGRESS_FILE")
        try:
            for index, page in enumerate(doc):
                page_no = index + 1
                _write_progress(progress_file, page_no, total_pages)
                if _looks_like_table(page):
                    table = _extract_tables(page)
                    if table:
                        chunks.append(table)

                text = page.get_text("text")
                if text.strip():
                    if _has_images(page):
                        # Camada parcial: extrai o texto digital e faz OCR apenas
                        # das regiões com imagens (o PyMuPDF mescla ambos).
                        merged, lang = _ocr_page(page, full=False)
                        if merged:
                            chunks.append(merged)
                            ocr_pages.append((page_no, lang))
                        else:
                            chunks.append(text.strip())
                    else:
                        chunks.append(text.strip())
                else:
                    ocr_text, lang = _ocr_page(page, full=True)
                    if ocr_text:
                        chunks.append(ocr_text)
                        ocr_pages.append((page_no, lang))
        finally:
            doc.close()

        warnings: list[str] = []
        if ocr_pages:
            pages = sorted(p_no for p_no, _ in ocr_pages)
            langs = "+".join(dict.fromkeys(lang for _, lang in ocr_pages))
            warnings.append(
                f"{len(pages)} página(s) processada(s) via OCR "
                f"(página(s) {_fmt_pages(pages)}, idioma '{langs or OCR_LANGUAGE}'). "
                "A precisão pode variar."
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


def _ocr_page(page: pymupdf.Page, full: bool = True) -> tuple[str, str]:
    """Extrai texto de uma página usando OCR (Tesseract), com fallback de idioma.

    Retorna o texto OCR e o idioma efetivamente usado ("" se não houver Tesseract
    nem idioma disponível).
    """
    if not OCR_ENABLED:
        return "", ""
    last_error: RuntimeError | None = None
    for lang in _ocr_languages():
        try:
            textpage = page.get_textpage_ocr(
                language=lang,
                full=full,
                dpi=OCR_DPI,
            )
            text = (textpage.extractText() or "").strip()
            if text:
                return text, lang
        except RuntimeError as exc:
            last_error = exc
    if last_error is not None:
        # Tesseract não instalado ou idioma indisponível
        return "", ""
    return "", ""


def _ocr_languages() -> list[str]:
    """Lista de idiomas a tentar, sem duplicatas, na ordem de preferência."""
    langs: list[str] = []
    for lang in (OCR_LANGUAGE, OCR_LANGUAGE_FALLBACK):
        if lang and lang not in langs:
            langs.append(lang)
    return langs or ["eng"]


def _has_images(page: pymupdf.Page) -> bool:
    """Indica se a página contém imagens embutidas (candidatas a OCR parcial)."""
    return bool(page.get_images(full=True))


def _fmt_pages(pages: list[int]) -> str:
    """Formata números de página compactando intervalos (ex.: '2, 5-7')."""
    if not pages:
        return ""
    parts: list[str] = []
    start = prev = pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
            continue
        parts.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = p
    parts.append(str(start) if start == prev else f"{start}-{prev}")
    return ", ".join(parts)


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
