# ADR-0002: MarkItDown como motor de conversão

- **Status:** Aceita
- **Data:** 2026-08-09

## Contexto

Converter DOCX, XLSX, PPTX e PDF para Markdown preservando estrutura é o principal desafio técnico. Desenvolver parsers do zero é inviável e arriscado.

## Decisão

- Usar **MarkItDown** (microsoft/markitdown) como motor principal de conversão.
- Complementar com bibliotecas especializadas quando a qualidade exigir:
  - python-docx (DOCX)
  - openpyxl (XLSX)
  - python-pptx (PPTX)
  - PyMuPDF / pdfplumber (PDF)
- O produto pode ter diferencial na experiência, segurança e SEO — não necessariamente no parser.

## Consequências

- Menor tempo de desenvolvimento e menor risco.
- Qualidade da conversão limitada ao que MarkItDown/bibliotecas entregam por padrão.
- Conversores específicos podem ser melhorados incrementalmente em `app/converters/`.
