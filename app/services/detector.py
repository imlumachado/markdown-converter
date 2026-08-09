from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS: set[str] = {
    ".docx",
    ".xlsx",
    ".pptx",
    ".pdf",
    ".doc",
    ".xls",
    ".ppt",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".xml",
    ".ipynb",
    ".md",
    ".markdown",
    ".txt",
    ".jpg",
    ".jpeg",
    ".png",
    ".mp3",
    ".wav",
}

FORMAT_BY_EXTENSION: dict[str, str] = {
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".pptx": "pptx",
    ".pdf": "pdf",
    ".doc": "doc",
    ".xls": "xls",
    ".ppt": "ppt",
    ".html": "html",
    ".htm": "html",
    ".csv": "csv",
    ".json": "json",
    ".xml": "xml",
    ".ipynb": "ipynb",
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "plaintext",
    ".jpg": "jpg",
    ".jpeg": "jpeg",
    ".png": "png",
    ".mp3": "mp3",
    ".wav": "wav",
}


class UnsupportedFormatError(ValueError):
    """Erro quando a extensão do arquivo não é suportada."""


def detect_format(filename: str) -> str:
    """Detecta o formato a partir da extensão do arquivo."""
    ext = Path(filename).suffix.lower()
    if ext not in FORMAT_BY_EXTENSION:
        raise UnsupportedFormatError(
            f"Formato não suportado: '{ext or '(sem extensão)'}'. "
            f"Formatos aceitos: {', '.join(sorted(FORMAT_BY_EXTENSION))}"
        )
    return FORMAT_BY_EXTENSION[ext]
