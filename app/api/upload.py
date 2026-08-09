from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.converters.docx import DocxConverter
from app.converters.pdf import PdfConverter
from app.converters.pptx import PptxConverter
from app.converters.xlsx import XlsxConverter
from app.services.cleanup import cleanup_expired, cleanup_job
from app.services.detector import detect_format
from app.services.storage import create_job_dir, sanitize_filename
from app.services.validator import validate_extension, validate_size

router = APIRouter(prefix="/api", tags=["conversion"])

CONVERTERS: dict[str, object] = {
    "docx": DocxConverter(),
    "xlsx": XlsxConverter(),
    "pptx": PptxConverter(),
    "pdf": PdfConverter(),
}


@router.post("/convert")
async def convert(file: UploadFile = File(...)):
    try:
        validate_extension(file.filename or "")
        validate_size(file.size)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    fmt = detect_format(file.filename)
    converter = CONVERTERS.get(fmt)
    if converter is None:
        raise HTTPException(status_code=400, detail=f"Formato '{fmt}' ainda não é suportado.")

    cleanup_expired()

    job_dir, task_id = create_job_dir()
    source = job_dir / f"{task_id}{Path(file.filename).suffix.lower()}"
    content = await file.read()
    source.write_bytes(content)

    try:
        result = converter.convert(source, job_dir / "output")
    except Exception as exc:
        cleanup_job(job_dir)
        raise HTTPException(status_code=500, detail="Falha ao converter o arquivo.") from exc

    md_name = f"{Path(sanitize_filename(file.filename)).stem}.md"
    (job_dir / md_name).write_text(result.markdown, encoding="utf-8")

    return {
        "task_id": task_id,
        "filename": md_name,
        "markdown": result.markdown,
        "download_url": f"/api/download/{task_id}",
        "images": result.images,
        "warnings": result.warnings,
    }
