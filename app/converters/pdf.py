from __future__ import annotations

from pathlib import Path

from app.converters.base import BaseConverter, ConversionResult
from app.services.markdown import convert_with_markitdown


class PdfConverter(BaseConverter):
    """Converte documentos PDF para Markdown."""

    def convert(self, source: Path, output_dir: Path) -> ConversionResult:
        return convert_with_markitdown(source, output_dir)
