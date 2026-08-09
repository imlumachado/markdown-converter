from __future__ import annotations

import shutil
import time
from pathlib import Path

from app.services.storage import TEMP_ROOT

JOB_TTL_SECONDS: int = 30 * 60  # 30 minutos


def cleanup_job(job_dir: Path) -> None:
    """Exclui o diretório de uma conversão."""
    shutil.rmtree(job_dir, ignore_errors=True)


def cleanup_expired(now: float | None = None, ttl: int = JOB_TTL_SECONDS) -> int:
    """Remove conversões órfãs mais antigas que o TTL. Retorna quantas foram removidas."""
    now = now if now is not None else time.time()
    count = 0
    if not TEMP_ROOT.exists():
        return 0
    for child in TEMP_ROOT.iterdir():
        try:
            if now - child.stat().st_mtime > ttl:
                shutil.rmtree(child, ignore_errors=True)
                count += 1
        except OSError:
            continue
    return count
