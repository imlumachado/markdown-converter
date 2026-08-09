# Etapas do Projeto — Markdown Converter

Backup consolidado do conteúdo criado até o momento. Cada etapa registra o que foi entregue.

## Etapa 0 — Fundação (concluída)

- Estrutura de diretórios (`app/`, `converters/`, `services/`, `api/`, `tests/`, `temp/`, `docs/`)
- Repositório Git inicializado
- Ambiente virtual + `requirements.txt` (markitdown, python-docx, openpyxl, python-pptx, PyMuPDF, Pillow, streamlit, fastapi, pytest)
- `.gitignore`, `README.md`
- ADRs: Streamlit→FastAPI, MarkItDown como motor, armazenamento temporário

## Etapa 1 — Motor de conversão (concluída)

- Interface `BaseConverter` / `ConversionResult`
- Conversores DOCX, XLSX, PPTX e PDF via MarkItDown
- `detector.py` (detecção por extensão) e `validator.py` (extensão/tamanho)
- Protótipo Streamlit (`app/prototype.py`): upload, preview, download
- Testes unitários por formato

## Etapa 2 — Produto HTML/CSS/JS + FastAPI (concluída)

- API FastAPI: `POST /api/convert` e `GET /api/download/{task_id}`
- `storage.py` (UUID, nomes sanitizados) e `cleanup.py` (TTL 30 min)
- Frontend: drag & drop, barra de progresso, preview markdown, download
- Exclusão automática do diretório temporário após o download
- Testes da API

## Etapa 3 — Segurança e confiabilidade (concluída)

- `magic.py`: validação de conteúdo por magic bytes (rejeita extensão mascarada)
- `convert_worker.py`: conversão isolada em subprocesso com timeout de 30s
- `middleware.py`: rate limiting por IP (10 req/min)
- Leitura do upload em blocos (413 acima do limite)
- Testes de segurança

## Etapa 4 — Publicação (pausada — testes locais em andamento)

- `config.py` (BASE_URL, GA_ID, PORT via env)
- `seo.py` + rotas `/robots.txt` e `/sitemap.xml`
- Google Analytics 4 (opcional via env)
- `Dockerfile`, `.dockerignore`, `docker-compose.yml`
- `.env.example`, `DEPLOY.md`

> Nota: a configuração do Render (`render.yaml`) foi removida por enquanto;
> o foco atual são os testes na máquina local.

## Etapa 5 — SEO e conteúdo (em andamento)

- **Blog de artigos:** conteúdo em Markdown (`content/blog/`), frontmatter
  (título, descrição, data, categoria), rotas `/blog` e `/blog/{slug}`.
- **SEO técnico:** `sitemap.xml` dinâmico com artigos + `<lastmod>`, `robots.txt`.
- **Rich snippets:** Open Graph/Twitter Cards + JSON-LD (`WebApplication`,
  `FAQPage` na home, `BreadcrumbList` nos artigos).
- **SEO on-page:** meta description, canônico e h1 por rota.
- 4 artigos iniciais publicados.

## Etapa 6 — Monetização (em andamento)

- **Páginas legais + contato:** `/privacy`, `/terms` e `/contact` (obrigatórias
  para aprovação no AdSense).
- **Injeção de anúncios:** slot responsivo via env (`ADSENSE_ENABLED`,
  `ADSENSE_CLIENT`, `ADSENSE_SLOT`); só carrega com consentimento de cookies.
- **Banner de cookies:** consentimento LGPD/GDPR em `localStorage`; anúncios
  personalizados só após "Aceitar todos".
- **ads.txt** servido dinamicamente com o publisher ID.

## Status dos testes

- 36 testes passando (`pytest tests -q` com Tesseract no PATH)

## Como restaurar

O backup completo do código está na pasta `projeto/` dentro desta pasta. Para restaurar, copie o conteúdo de `projeto/` para o local desejado e execute:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
