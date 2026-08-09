from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.services.cleanup import cleanup_job
from app.services.storage import TEMP_ROOT

router = APIRouter(prefix="/api", tags=["download"])


@router.get("/download/{task_id}")
async def download(task_id: str, background_tasks: BackgroundTasks):
    """Serve o arquivo .md gerado e exclui a conversão após o download."""
    job_dir = TEMP_ROOT / task_id
    if not job_dir.is_dir():
        raise HTTPException(status_code=404, detail="Conversão expirada ou não encontrada.")

    md_files = list(job_dir.glob("*.md"))
    if not md_files:
        cleanup_job(job_dir)
        raise HTTPException(status_code=404, detail="Arquivo Markdown não encontrado.")

    md_path: Path = md_files[0]
    background_tasks.add_task(cleanup_job, job_dir)
    return FileResponse(
        md_path,
        media_type="text/markdown",
        filename=md_path.name,
    )
