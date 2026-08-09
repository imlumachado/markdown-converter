from __future__ import annotations

from pathlib import Path

from app.converters.base import BaseConverter, ConversionResult
from app.services.markdown import convert_with_markitdown


class PptxConverter(BaseConverter):
    """Converte apresentações PowerPoint (.pptx) para Markdown."""

    def convert(self, source: Path, output_dir: Path) -> ConversionResult:
        return convert_with_markitdown(source, output_dir)
