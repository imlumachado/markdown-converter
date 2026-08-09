from __future__ import annotations

import os
import shutil
from pathlib import Path

import pymupdf

from app.converters.pdf import PdfConverter


def _make_pdf(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Relatório de Vendas")
    page.insert_text((72, 100), "Análise do trimestre")
    doc.save(str(path))
    doc.close()


def _make_scanned_pdf(path: Path) -> Path:
    """Cria um PDF digitalizado (página renderizada como imagem, sem texto)."""
    tmp = path.parent
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 100), "Livro digitalizado para teste de OCR", fontsize=18)
    pix = page.get_pixmap(dpi=150)
    img = tmp / "page.png"
    pix.save(img)
    doc.close()

    doc2 = pymupdf.open()
    page2 = doc2.new_page(width=612, height=792)
    page2.insert_image(page2.rect, filename=str(img))
    doc2.save(str(path))
    doc2.close()
    img.unlink(missing_ok=True)
    return path


def test_convert_pdf(tmp_path: Path) -> None:
    source = tmp_path / "relatorio.pdf"
    _make_pdf(source)

    result = PdfConverter().convert(source, tmp_path / "output")

    assert result.markdown
    assert "Relatório de Vendas" in result.markdown
    assert "Análise do trimestre" in result.markdown


def _has_tesseract() -> bool:
    """Verifica o Tesseract no PATH ou nos locais de instalação padrão."""
    if shutil.which("tesseract"):
        return True
    return any(
        Path(p).is_file()
        for p in (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        )
    )


def test_convert_scanned_pdf_uses_ocr(tmp_path: Path) -> None:
    if not _has_tesseract():
        import pytest

        pytest.skip("Tesseract não instalado no ambiente")

    source = _make_scanned_pdf(tmp_path / "livro.pdf")

    result = PdfConverter().convert(source, tmp_path / "output")

    assert "Livro digitalizado" in result.markdown
    assert result.warnings, "Deve haver aviso sobre páginas processadas via OCR"


def test_ocr_page_graceful_without_tesseract(monkeypatch) -> None:
    """Sem Tesseract, a extração OCR falha silenciosamente sem quebrar o fluxo."""
    import pymupdf as mupdf

    doc = mupdf.open()
    page = doc.new_page()

    import app.converters.pdf as pdf_module

    def _raise(*args, **kwargs):
        raise RuntimeError("No tessdata specified and Tesseract is not installed")

    monkeypatch.setattr(pdf_module, "OCR_LANGUAGE", "por")
    monkeypatch.setattr(page, "get_textpage_ocr", _raise)

    assert pdf_module._ocr_page(page) == ""
    doc.close()
