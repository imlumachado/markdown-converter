from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

# Formatos legados/OpenDocument convertidos para o formato moderno correspondente
LEGACY_TARGETS: dict[str, str] = {
    "doc": "docx",
    "xls": "xlsx",
    "ppt": "pptx",
    "odt": "docx",
    "ods": "xlsx",
    "odp": "pptx",
}

SOFFICE_PATH = os.getenv(
    "SOFFICE_PATH",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
)

MODERN_MIME_BY_EXT: dict[str, str] = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


class LibreOfficeUnavailableError(RuntimeError):
    """LibreOffice não foi encontrado no ambiente."""


def _find_soffice() -> str:
    """Localiza o binário do LibreOffice (env, PATH ou caminhos padrão)."""
    candidates = [SOFFICE_PATH]
    found = shutil.which("soffice")
    if found:
        candidates.append(found)
    candidates += [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise LibreOfficeUnavailableError(
        "LibreOffice não encontrado. Instale o LibreOffice ou defina SOFFICE_PATH."
    )


def convert_to_modern(source: Path, out_dir: Path, fmt: str) -> Path:
    """Converte um formato legado para o moderno equivalente via LibreOffice headless.

    Ex.: .doc -> .docx, .xls -> .xlsx, .ppt -> .pptx, .odt -> .docx.
    Retorna o caminho do arquivo convertido.
    """
    target = LEGACY_TARGETS[fmt]
    soffice = _find_soffice()
    out_dir.mkdir(parents=True, exist_ok=True)

    proc = subprocess.run(
        [soffice, "--headless", "--convert-to", target, "--outdir", str(out_dir), str(source)],
        capture_output=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise LibreOfficeUnavailableError(
            f"Falha ao converter '{source.name}' com o LibreOffice: "
            f"{proc.stderr.decode(errors='replace').strip()[:300]}"
        )

    converted = out_dir / f"{source.stem}.{target}"
    if not converted.exists():
        raise LibreOfficeUnavailableError(
            f"LibreOffice não gerou o arquivo de saída para '{source.name}'."
        )
    return converted
