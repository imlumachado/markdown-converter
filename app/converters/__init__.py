from __future__ import annotations

from app.converters.base import BaseConverter, ConversionResult
from app.converters.docx import DocxConverter
from app.converters.pdf import PdfConverter
from app.converters.pptx import PptxConverter
from app.converters.xlsx import XlsxConverter

CONVERTERS: dict[str, BaseConverter] = {
    "docx": DocxConverter(),
    "xlsx": XlsxConverter(),
    "pptx": PptxConverter(),
    "pdf": PdfConverter(),
}

__all__ = [
    "CONVERTERS",
    "BaseConverter",
    "ConversionResult",
    "DocxConverter",
    "PdfConverter",
    "PptxConverter",
    "XlsxConverter",
]
