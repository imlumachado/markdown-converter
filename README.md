# Markdown Converter

Plataforma de conversão de arquivos (DOCX, XLSX, PPTX, PDF) para Markdown (.md).

## Estratégia

- **Protótipo:** Streamlit para validar rapidamente o motor de conversão.
- **Produto:** HTML/CSS/JS + FastAPI como arquitetura oficial (SEO, AdSense, controle total).
- **Motor:** MarkItDown + bibliotecas especializadas (python-docx, openpyxl, python-pptx, PyMuPDF).

## Estrutura

```
markdown-converter/
├── app/
│   ├── main.py            # Entrypoint (FastAPI / Streamlit)
│   ├── converters/        # Conversores por formato
│   ├── services/          # Validação, detecção, markdown, imagens, limpeza
│   ├── api/               # Rotas de upload e download
│   └── templates/         # HTML
├── static/                # CSS / JS
├── tests/                 # Testes unitários por formato
├── temp/                  # Arquivos temporários (excluídos após conversão)
└── docs/                  # ADRs e documentação
```

## Como começar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Fases

| Fase | Descrição | Status |
|---|---|---|
| 0 | Fundação (estrutura, git, ambiente, ADRs) | Em andamento |
| 1 | Motor via Streamlit | Pendente |
| 2 | Produto HTML/CSS/JS + FastAPI | Pendente |
| 3 | Segurança e confiabilidade | Pendente |
| 4 | Publicação | Pendente |
| 5 | SEO e conteúdo | Pendente |
| 6 | Monetização (AdSense) | Pendente |
| 7 | Escalabilidade | Pendente |
