from __future__ import annotations

import zipfile
from pathlib import Path

OXML_MARKERS: dict[str, str] = {
    "word/document.xml": "docx",
    "xl/workbook.xml": "xlsx",
    "ppt/presentation.xml": "pptx",
}


def sniff_format(path: Path) -> str | None:
    """Identifica o formato real pelo conteúdo (magic bytes), não pela extensão."""
    with path.open("rb") as f:
        header = f.read(8)

    if header.startswith(b"%PDF-"):
        return "pdf"
    if header.startswith(b"PK\x03\x04"):
        return _sniff_ooxml(path)
    return None


def _sniff_ooxml(path: Path) -> str | None:
    """Distingue docx/xlsx/pptx pelo conteúdo interno do pacote ZIP."""
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
    except zipfile.BadZipFile:
        return None
    for marker, fmt in OXML_MARKERS.items():
        if marker in names:
            return fmt
    return None
