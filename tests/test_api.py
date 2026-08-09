from __future__ import annotations

from pathlib import Path

from docx import Document
from fastapi.testclient import TestClient

from app.main import app
from app.services.storage import TEMP_ROOT

client = TestClient(app)


def _make_docx(path: Path) -> None:
    doc = Document()
    doc.add_heading("API Teste", level=1)
    doc.add_paragraph("Conteúdo da API.")
    doc.save(str(path))


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Conversor de Arquivos para Markdown" in response.text


def test_convert_and_download(tmp_path: Path) -> None:
    source = tmp_path / "api.docx"
    _make_docx(source)

    with source.open("rb") as f:
        response = client.post(
            "/api/convert",
            files={"file": ("api.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"].endswith(".md")
    assert "# API Teste" in data["markdown"]
    assert data["download_url"] == f"/api/download/{data['task_id']}"

    job_dir = TEMP_ROOT / data["task_id"]
    assert job_dir.is_dir()

    download = client.get(f"/api/download/{data['task_id']}")
    assert download.status_code == 200
    assert b"API Teste" in download.content

    assert not job_dir.is_dir(), "Diretório temporário deve ser excluído após o download"


def test_convert_unknown_task() -> None:
    response = client.get("/api/download/inexistente")
    assert response.status_code == 404


def test_reject_bad_extension() -> None:
    response = client.post(
        "/api/convert",
        files={"file": ("malware.exe", b"x", "application/octet-stream")},
    )
    assert response.status_code == 400


def test_reject_empty_file() -> None:
    response = client.post(
        "/api/convert",
        files={"file": ("vazio.docx", b"", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert response.status_code == 400
