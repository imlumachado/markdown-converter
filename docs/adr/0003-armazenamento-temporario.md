# ADR-0003: Armazenamento temporário e exclusão automática

- **Status:** Aceita
- **Data:** 2026-08-09

## Contexto

O produto promete: "Seus arquivos são processados temporariamente e excluídos após a conversão." Essa promessa exige garantia na arquitetura.

## Decisão

- Cada upload gera um diretório isolado: `/tmp/conversions/<uuid>/`.
- Nunca usar o nome original do arquivo como identificador interno (usar UUID).
- Excluir o diretório após o download (ou por limpeza agendada para órfãos).
- Não manter arquivos indefinidamente; definir TTL (ex.: 30 min).

## Consequências

- Privacidade garantida por projeto, não por convenção.
- Necessário serviço de limpeza (`app/services/cleanup.py`).
- Logs não devem conter conteúdo nem nomes originais.
