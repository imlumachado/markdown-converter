# ADR-0001: Streamlit para protótipo, FastAPI para o produto

- **Status:** Aceita
- **Data:** 2026-08-09

## Contexto

O projeto precisa de SEO, AdSense, URLs específicas por ferramenta, controle de HTML/metadados, performance mobile e posicionamento de anúncios.

## Decisão

- **Protótipo:** usar Streamlit para validar o motor de conversão rapidamente (1–3 dias).
- **Produto:** usar HTML/CSS/JS + FastAPI como arquitetura oficial.
- O motor Python desenvolvido no protótipo deve ser reaproveitado (sem reescrever parsers).

## Consequências

- O Streamlit nunca será tratado como arquitetura definitiva.
- A migração de interface faz parte do escopo do produto.
- A camada de conversão fica desacoplada da interface (módulos `app/converters/`).
