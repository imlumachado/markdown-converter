from __future__ import annotations

from pathlib import Path

from app.services.detector import SUPPORTED_EXTENSIONS
from app.services.magic import sniff_format

MAX_FILE_SIZE: int = 25 * 1024 * 1024  # 25 MB

# Formatos com validação de conteúdo por magic bytes
CONTENT_CHECKABLE: set[str] = {"docx", "xlsx", "pptx", "pdf", "doc", "xls", "ppt", "odt", "ods", "odp"}


class ValidationError(ValueError):
    """Erro de validação do arquivo enviado."""


def validate_extension(filename: str) -> None:
    """Valida a extensão do arquivo contra a lista de formatos suportados."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValidationError(
            f"Extensão '{ext or '(sem extensão)'}' não é suportada. "
            f"Formatos aceitos: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )


def validate_size(size: int) -> None:
    """Valida o tamanho do arquivo em bytes."""
    if size <= 0:
        raise ValidationError("O arquivo enviado está vazio.")
    if size > MAX_FILE_SIZE:
        limit_mb = MAX_FILE_SIZE // (1024 * 1024)
        raise ValidationError(f"O arquivo excede o limite de {limit_mb} MB.")


def validate_content(path: Path, expected_format: str) -> None:
    """Valida que o conteúdo real do arquivo corresponde ao formato esperado."""
    if expected_format not in CONTENT_CHECKABLE:
        return
    detected = sniff_format(path)
    if detected is None:
        raise ValidationError(
            "O conteúdo do arquivo não corresponde a um formato suportado."
        )
    if detected != expected_format:
        raise ValidationError(
            f"Extensão '.{expected_format}' não corresponde ao conteúdo real "
            f"do arquivo (detectado: .{detected})."
        )
