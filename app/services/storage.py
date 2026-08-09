from __future__ import annotations

import re
import uuid
from pathlib import Path

TEMP_ROOT: Path = Path(__file__).resolve().parents[2] / "temp" / "conversions"


def sanitize_filename(name: str) -> str:
    """Remove caracteres perigosos do nome do arquivo, preservando acentos."""
    name = Path(name).name
    name = re.sub(r"[^\w.\- ]+", "_", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name).strip("._")
    return name or "arquivo"


def create_job_dir() -> tuple[Path, str]:
    """Cria um diretório isolado para a conversão, identificado por UUID."""
    task_id = uuid.uuid4().hex
    job_dir = TEMP_ROOT / task_id
    job_dir.mkdir(parents=True, exist_ok=False)
    return job_dir, task_id
