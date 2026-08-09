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

## Como rodar o protótipo (Fase 1)

```bash
.venv\Scripts\activate
streamlit run app/prototype.py
```

## Como rodar o produto (Fase 2)

```bash
.venv\Scripts\activate
uvicorn app.main:app --reload
```

Acesse http://localhost:8000

Testes:

```bash
.venv\Scripts\python.exe -m pytest tests -q
```

## Deploy

Veja o guia completo em [DEPLOY.md](DEPLOY.md). Resumo:

- **VPS/Docker:** `docker compose up -d --build` (ou `docker build` + `docker run`).
- Configure `BASE_URL` e `GA_ID` (variáveis de ambiente).

## Fases

| Fase | Descrição | Status |
|---|---|---|
| 0 | Fundação (estrutura, git, ambiente, ADRs) | Concluída |
| 1 | Motor via Streamlit | Concluída (4 formatos) |
| 2 | Produto HTML/CSS/JS + FastAPI | Concluída |
| 3 | Segurança e confiabilidade | Concluída |
| 4 | Publicação | Pausada (testes locais em andamento) |
| 5 | SEO e conteúdo | Em andamento (blog, sitemap dinâmico, rich snippets) |
| 6 | Monetização (AdSense) | Em andamento (páginas legais, banner cookies, ads.txt) |
| 7 | Escalabilidade | Em andamento (limite de concorrência, caching HTTP) |

## Novas funcionalidades

- **Formatos legados:** `.doc`, `.xls`, `.ppt`, `.odt`, `.ods` e `.odp` via
  LibreOffice headless (requer instalação; `SOFFICE_PATH`).
- **Copiar:** botão "Copiar" envia o Markdown para a área de transferência.
- **Histórico:** últimas 20 conversões salvas no navegador (localStorage).
- **Lote:** arraste vários arquivos e baixe tudo em um ZIP.
- **Exportar HTML:** gera página HTML a partir do Markdown.

## Conversão assíncrona e OCR

- **Fluxo assíncrono:** `POST /api/convert` retorna `task_id` e `status_url` na hora; o
  progresso é consultado em `GET /api/status/{task_id}` (polling pelo frontend).
- **OCR para PDFs digitalizados:** páginas sem camada de texto são processadas via
  Tesseract (`OCR_LANGUAGE`, padrão `por`). Requer o binário `tesseract` no ambiente
  (instalado no Dockerfile).
- **Fallback de idioma:** se `OCR_LANGUAGE` falhar (idioma não instalado), tenta
  `OCR_LANGUAGE_FALLBACK` (padrão `eng`) automaticamente.
- **Camada parcial:** páginas com texto e imagens fazem OCR apenas das regiões sem
  texto (via `full=False` do PyMuPDF), mesclando o texto digital com o OCR.
- **Aviso detalhado:** a conversão informa quais páginas passaram por OCR e o idioma
  usado (ex.: "página(s) 2, 5-7, idioma 'por'").
- Variáveis: `OCR_LANGUAGE`, `OCR_LANGUAGE_FALLBACK`, `OCR_DPI`, `OCR_ENABLED`,
  `CONVERSION_TIMEOUT_SECONDS` (veja `.env.example`).
