from __future__ import annotations

import zipfile
from pathlib import Path

OXML_MARKERS: dict[str, str] = {
    "word/document.xml": "docx",
    "xl/workbook.xml": "xlsx",
    "ppt/presentation.xml": "pptx",
}

ODF_MARKERS: dict[str, str] = {
    "application/vnd.oasis.opendocument.text": "odt",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
    "application/vnd.oasis.opendocument.presentation": "odp",
}

# OLE2 Compound File: .doc/.xls/.ppt compartilham o mesmo magic bytes
OLE2_HEADER = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

# Marcadores internos (directory entries) usados para distinguir os formatos OLE2
OLE2_MARKERS: dict[str, str] = {
    "WordDocument": "doc",
    "Workbook": "xls",
    "PowerPoint Document": "ppt",
}


def sniff_format(path: Path) -> str | None:
    """Identifica o formato real pelo conteúdo (magic bytes), não pela extensão."""
    with path.open("rb") as f:
        header = f.read(8)

    if header.startswith(b"%PDF-"):
        return "pdf"
    if header.startswith(b"PK\x03\x04"):
        return _sniff_zip(path)
    if header.startswith(OLE2_HEADER):
        return _sniff_ole2(path)
    return None


def _sniff_zip(path: Path) -> str | None:
    """Distingue docx/xlsx/pptx e odt/ods/odp pelo conteúdo do pacote ZIP."""
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            if "mimetype" in names:
                mime = zf.read("mimetype").decode("utf-8", errors="replace")
                if mime in ODF_MARKERS:
                    return ODF_MARKERS[mime]
            for marker, fmt in OXML_MARKERS.items():
                if marker in names:
                    return fmt
    except (zipfile.BadZipFile, OSError, KeyError):
        return None
    return None


def _sniff_ole2(path: Path) -> str | None:
    """Distingue doc/xls/ppt pelo marcador interno do Compound File (OLE2)."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    for marker, fmt in OLE2_MARKERS.items():
        if marker.encode("utf-16le") in data:
            return fmt
    return None
