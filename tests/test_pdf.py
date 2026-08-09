from __future__ import annotations

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


def test_convert_pdf(tmp_path: Path) -> None:
    source = tmp_path / "relatorio.pdf"
    _make_pdf(source)

    result = PdfConverter().convert(source, tmp_path / "output")

    assert result.markdown
    assert "Relatório de Vendas" in result.markdown
    assert "Análise do trimestre" in result.markdown
