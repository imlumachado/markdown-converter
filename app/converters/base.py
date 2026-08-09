from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConversionResult:
    """Resultado da conversão de um arquivo para Markdown."""

    markdown: str
    title: str | None = None
    images: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class BaseConverter(ABC):
    """Interface comum para todos os conversores de formato."""

    @abstractmethod
    def convert(self, source: Path, output_dir: Path) -> ConversionResult:
        """Converte `source` para Markdown.

        Imagens extraídas devem ser salvas em `output_dir` e referenciadas
        pelo nome do arquivo no markdown retornado.
        """
        raise NotImplementedError
