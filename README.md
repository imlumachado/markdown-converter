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

- **Render:** Blueprint detecta o `render.yaml` (deploy automático por push).
- **VPS/Docker:** `docker compose up -d --build` (ou `docker build` + `docker run`).
- Configure `BASE_URL` e `GA_ID` (variáveis de ambiente).

## Fases

| Fase | Descrição | Status |
|---|---|---|
| 0 | Fundação (estrutura, git, ambiente, ADRs) | Concluída |
| 1 | Motor via Streamlit | Concluída (4 formatos) |
| 2 | Produto HTML/CSS/JS + FastAPI | Concluída |
| 3 | Segurança e confiabilidade | Concluída |
| 4 | Publicação | Em andamento (preparação de deploy pronta) |
| 3 | Segurança e confiabilidade | Pendente |
| 4 | Publicação | Pendente |
| 5 | SEO e conteúdo | Pendente |
| 6 | Monetização (AdSense) | Pendente |
| 7 | Escalabilidade | Pendente |
