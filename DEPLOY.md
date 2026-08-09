# Deploy

## Pré-requisitos

- Repositório no GitHub com este projeto.
- Variáveis de ambiente (veja `.env.example`):
  - `BASE_URL` — URL pública (ex.: `https://markdown-converter.com`)
  - `GA_ID` — Measurement ID do Google Analytics 4 (opcional)

## Opção 1 — Render (mais simples)

1. Crie uma conta em https://render.com.
2. Vá em **New > Blueprint** e conecte o repositório.
3. O Render detecta o `render.yaml` automaticamente.
4. Configure `GA_ID` como variável (value or from env) no painel.
5. Deploy é automático a cada push.

Ajuste o valor de `BASE_URL` no `render.yaml` para o seu domínio final.

## Opção 2 — Docker em VPS (mais controle)

```bash
# Na máquina
cp .env.example .env        # edite os valores
docker compose up -d --build
```

Ou sem compose:

```bash
docker build -t markdown-converter .
docker run -d --name markdown-converter \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  markdown-converter
```

Para HTTPS, coloque um reverse proxy (Caddy ou Nginx) na frente na porta 443 apontando para `127.0.0.1:8000`.

## Opção 3 — Railway / Fly.io

- **Railway:** New Project > Deploy from GitHub. Defina `BASE_URL` e `GA_ID` como variáveis.
- **Fly.io:**
  ```bash
  fly launch
  fly secrets set BASE_URL=https://seu-dominio.com GA_ID=G-XXXXXX
  fly deploy
  ```

## Validação pós-deploy

- `https://SEU-DOMINIO/api/health` → `{"status":"ok"}`
- `https://SEU-DOMINIO/robots.txt` e `https://SEU-DOMINIO/sitemap.xml` respondendo.
- Converter um arquivo real de ponta a ponta.
- Enviar o sitemap no Google Search Console.
