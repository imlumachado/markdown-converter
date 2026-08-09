from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.cleanup import cleanup_expired, cleanup_job
from app.services.detector import detect_format
from app.services.storage import create_job_dir, sanitize_filename
from app.services.validator import (
    MAX_FILE_SIZE,
    validate_content,
    validate_extension,
)

router = APIRouter(prefix="/api", tags=["conversion"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONVERSION_TIMEOUT_SECONDS = 120
CHUNK_SIZE = 1024 * 1024  # 1 MB

SUPPORTED_FORMATS = frozenset({"docx", "xlsx", "pptx", "pdf"})


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


async def _run_conversion(source: Path) -> dict:
    """Executa a conversão em subprocesso isolado com timeout, sem bloquear o event loop."""
    result_json = source.parent / "result.json"

    async def _convert() -> tuple[str, str]:
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "app.services.convert_worker",
            str(source),
            str(result_json),
            cwd=PROJECT_ROOT,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode(errors="replace"), stderr.decode(errors="replace")

    try:
        await asyncio.wait_for(_convert(), timeout=CONVERSION_TIMEOUT_SECONDS)
    except asyncio.TimeoutError as exc:
        raise HTTPException(status_code=408, detail="Tempo limite de conversão excedido.") from exc

    if not result_json.exists():
        raise HTTPException(status_code=500, detail="Falha ao converter o arquivo.")

    return json.loads(result_json.read_text(encoding="utf-8"))


@router.post("/convert")
async def convert(file: UploadFile = File(...)):
    try:
        validate_extension(file.filename or "")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

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
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        data = await _run_conversion(source)
    except HTTPException:
        cleanup_job(job_dir)
        raise

    md_name = f"{Path(sanitize_filename(file.filename)).stem}.md"
    (job_dir / md_name).write_text(data["markdown"], encoding="utf-8")

    return {
        "task_id": task_id,
        "filename": md_name,
        "markdown": data["markdown"],
        "download_url": f"/api/download/{task_id}",
        "images": data["images"],
        "warnings": data["warnings"],
    }
