from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile

from app.services.cleanup import cleanup_expired, cleanup_job
from app.services.concurrency import JobTracker
from app.services.detector import detect_format
from app.services.storage import create_job_dir, sanitize_filename
from app.services.validator import (
    MAX_FILE_SIZE,
    validate_content,
    validate_extension,
)

router = APIRouter(prefix="/api", tags=["conversion"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONVERSION_TIMEOUT_SECONDS = int(os.getenv("CONVERSION_TIMEOUT_SECONDS", "600"))
CHUNK_SIZE = 1024 * 1024  # 1 MB

SUPPORTED_FORMATS = frozenset({"docx", "xlsx", "pptx", "pdf", "doc", "xls", "ppt", "odt", "ods", "odp"})


async def _read_upload(file: UploadFile) -> bytes:
    """Lê o upload em blocos, recusando arquivos acima do limite."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_FILE_SIZE:
            limit_mb = MAX_FILE_SIZE // (1024 * 1024)
            raise HTTPException(status_code=413, detail=f"O arquivo excede o limite de {limit_mb} MB.")
        chunks.append(chunk)
    if total == 0:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")
    return b"".join(chunks)


def _write_status(job_dir: Path, payload: dict) -> None:
    """Persiste o status do job em um JSON que o endpoint de polling lê."""
    (job_dir / "status.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _read_status(job_dir: Path) -> dict:
    status_file = job_dir / "status.json"
    if status_file.exists():
        return json.loads(status_file.read_text(encoding="utf-8"))
    progress_file = job_dir / "progress.json"
    if progress_file.exists():
        return {"status": "processing"}
    return {"status": "processing"}


def _read_progress(job_dir: Path) -> dict | None:
    progress_file = job_dir / "progress.json"
    if not progress_file.exists():
        return None
    try:
        return json.loads(progress_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


async def _run_conversion(source: Path) -> dict:
    """Executa a conversão em subprocesso isolado, escrevendo progresso."""
    result_json = source.parent / "result.json"
    env = dict(os.environ)
    env["CONVERSION_PROGRESS_FILE"] = str(source.parent / "progress.json")

    def _convert() -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "app.services.convert_worker",
                str(source),
                str(result_json),
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            env=env,
            check=False,
        )

    try:
        proc = await asyncio.wait_for(asyncio.to_thread(_convert), timeout=CONVERSION_TIMEOUT_SECONDS)
    except TimeoutError as exc:
        raise HTTPException(status_code=408, detail="Tempo limite de conversão excedido.") from exc

    if proc.returncode != 0 or not result_json.exists():
        raise HTTPException(status_code=500, detail="Falha ao converter o arquivo.")

    return json.loads(result_json.read_text(encoding="utf-8"))


async def _convert_background(
    job_dir: Path,
    source: Path,
    md_name: str,
    client_ip: str,
    tracker: JobTracker,
) -> None:
    """Executa a conversão em segundo plano e atualiza o status do job."""
    try:
        data = await _run_conversion(source)
    except HTTPException as exc:
        _write_status(job_dir, {"status": "error", "detail": exc.detail})
        return
    except Exception:
        _write_status(job_dir, {"status": "error", "detail": "Falha ao converter o arquivo."})
        return
    finally:
        tracker.release(client_ip)

    (job_dir / md_name).write_text(data["markdown"], encoding="utf-8")

    _write_status(
        job_dir,
        {
            "status": "done",
            "filename": md_name,
            "markdown": data["markdown"],
            "download_url": f"/api/download/{job_dir.name}",
            "images": data["images"],
            "warnings": data["warnings"],
        },
    )


@router.post("/convert")
async def convert(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    request: Request = None,
):
    if background_tasks is None:
        background_tasks = BackgroundTasks()

    tracker: JobTracker = request.app.state.job_tracker
    client_ip = request.client.host if request.client else "unknown"
    if not tracker.try_acquire(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Servidor ocupado. Aguarde as conversões ativas terminarem e tente novamente.",
        )

    try:
        try:
            validate_extension(file.filename or "")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from None

        fmt = detect_format(file.filename)
        if fmt not in SUPPORTED_FORMATS:
            raise HTTPException(status_code=400, detail=f"Formato '{fmt}' ainda não é suportado.")

        content = await _read_upload(file)

        cleanup_expired()

        job_dir, task_id = create_job_dir()
        source = job_dir / f"{task_id}{Path(file.filename).suffix.lower()}"
        source.write_bytes(content)

        try:
            validate_content(source, fmt)
        except ValueError as exc:
            cleanup_job(job_dir)
            raise HTTPException(status_code=400, detail=str(exc)) from None

        _write_status(job_dir, {"status": "processing"})

        md_name = f"{Path(sanitize_filename(file.filename)).stem}.md"
        background_tasks.add_task(_convert_background, job_dir, source, md_name, client_ip, tracker)

        return {
            "task_id": task_id,
            "status": "processing",
            "filename": md_name,
            "status_url": f"/api/status/{task_id}",
            "download_url": f"/api/download/{task_id}",
        }
    except HTTPException:
        tracker.release(client_ip)
        raise


@router.get("/status/{task_id}")
async def status(task_id: str):
    job_dir = Path(__file__).resolve().parents[2] / "temp" / "conversions" / task_id
    if not job_dir.is_dir():
        raise HTTPException(status_code=404, detail="Conversão não encontrada.")

    payload = _read_status(job_dir)
    progress = _read_progress(job_dir)
    if progress is not None:
        payload["progress"] = progress
    return payload
