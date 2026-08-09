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

CONVERTER_MODULES: dict[str, str] = {
    "docx": "app.converters.docx",
    "xlsx": "app.converters.xlsx",
    "pptx": "app.converters.pptx",
    "pdf": "app.converters.pdf",
}


def _get_converter(fmt: str) -> BaseConverter | None:
    """Carrega apenas o conversor do formato, evitando imports pesados."""
    module_name = CONVERTER_MODULES.get(fmt)
    if module_name is None:
        return None
    module = importlib.import_module(module_name)
    class_name = {
        "docx": "DocxConverter",
        "xlsx": "XlsxConverter",
        "pptx": "PptxConverter",
        "pdf": "PdfConverter",
    }[fmt]
    return getattr(module, class_name)()


def main() -> int:
    if len(sys.argv) != 3:
        print("Uso: python -m app.services.convert_worker <arquivo> <saida_json>", file=sys.stderr)
        return 2

    source = Path(sys.argv[1])
    output = Path(sys.argv[2])
    fmt = detect_format(source.name)

    converter = _get_converter(fmt)
    if converter is None:
        print(f"Conversor não suportado: {fmt}", file=sys.stderr)
        return 3

    try:
        result = converter.convert(source, source.parent / "output")
    except Exception as exc:  # noqa: BLE001 - erros vão para o subprocesso
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
