from __future__ import annotations

"""Worker isolado de conversão.

Executado em subprocesso com timeout para isolar falhas e limitar
CPU/memória da API:

    python -m app.services.convert_worker <arquivo> <arquivo_saida_json>
"""

import importlib
import json
import sys
from pathlib import Path

from app.converters.base import BaseConverter
from app.services.detector import detect_format
from app.services.libreoffice import LEGACY_TARGETS, convert_to_modern

CONVERTER_MODULES: dict[str, str] = {
    "docx": "app.converters.docx",
    "xlsx": "app.converters.xlsx",
    "pptx": "app.converters.pptx",
    "pdf": "app.converters.pdf",
}

CLASS_BY_FORMAT: dict[str, str] = {
    "docx": "DocxConverter",
    "xlsx": "XlsxConverter",
    "pptx": "PptxConverter",
    "pdf": "PdfConverter",
}


def _get_converter(fmt: str) -> BaseConverter | None:
    """Carrega apenas o conversor do formato, evitando imports pesados."""
    module_name = CONVERTER_MODULES.get(fmt)
    if module_name is None:
        return None
    module = importlib.import_module(module_name)
    return getattr(module, CLASS_BY_FORMAT[fmt])()


def main() -> int:
    if len(sys.argv) != 3:
        print("Uso: python -m app.services.convert_worker <arquivo> <saida_json>", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    fmt = detect_format(source.name)

    # Formatos legados/OpenDocument são convertidos para o moderno via LibreOffice
    convert_source = source
    if fmt in LEGACY_TARGETS:
        try:
            convert_source = convert_to_modern(source, source.parent / "legacy", fmt)
            fmt = LEGACY_TARGETS[fmt]
        except Exception as exc:
            print(f"LibreOffice indisponível para '{source.name}': {exc}", file=sys.stderr)
            return 4

    converter = _get_converter(fmt)
    if converter is None:
        print(f"Conversor não suportado: {fmt}", file=sys.stderr)
        return 3

    try:
        result = converter.convert(convert_source, convert_source.parent / "output")
    except Exception as exc:
        print(f"Falha na conversão: {exc}", file=sys.stderr)
        return 1

    output.write_text(
        json.dumps(
            {
                "markdown": result.markdown,
                "title": result.title,
                "images": result.images,
                "warnings": result.warnings,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
