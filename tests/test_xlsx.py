from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from app.converters.xlsx import XlsxConverter


def _make_xlsx(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Vendas"
    ws.append(["Produto", "Quantidade", "Preço"])
    ws.append(["Caneta", 12, 2.5])
    ws.append(["Caderno", 5, 15.0])
    wb.save(str(path))


def test_convert_xlsx(tmp_path: Path) -> None:
    source = tmp_path / "planilha.xlsx"
    _make_xlsx(source)

    result = XlsxConverter().convert(source, tmp_path / "output")

    assert result.markdown
    assert "Vendas" in result.markdown
    assert "Produto" in result.markdown
    assert "Caneta" in result.markdown
    assert "Caderno" in result.markdown
