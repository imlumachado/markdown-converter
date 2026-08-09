from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

import streamlit as st

from app.converters.base import ConversionResult
from app.converters.docx import DocxConverter
from app.converters.pdf import PdfConverter
from app.converters.pptx import PptxConverter
from app.converters.xlsx import XlsxConverter
from app.services.detector import FORMAT_BY_EXTENSION, detect_format
from app.services.validator import validate_extension, validate_size

CONVERTERS: dict[str, object] = {
    "docx": DocxConverter(),
    "xlsx": XlsxConverter(),
    "pptx": PptxConverter(),
    "pdf": PdfConverter(),
}


def convert_upload(uploaded) -> ConversionResult:
    fmt = detect_format(uploaded.name)
    converter = CONVERTERS.get(fmt)
    if converter is None:
        st.warning(
            f"O conversor para '{fmt}' ainda está em desenvolvimento. "
            "Neste momento são aceitos apenas arquivos .docx, .xlsx, .pptx e .pdf."
        )
        st.stop()

    with tempfile.TemporaryDirectory(prefix="mdconv-") as tmp:
        tmp_dir = Path(tmp)
        source = tmp_dir / f"{uuid.uuid4().hex}{Path(uploaded.name).suffix}"
        source.write_bytes(uploaded.getvalue())
        return converter.convert(source, tmp_dir / "output")


def main() -> None:
    st.set_page_config(
        page_title="Conversor de Arquivos para Markdown",
        page_icon=":page_facing_up:",
        layout="centered",
    )

    st.title("Conversor de Arquivos para Markdown")
    st.caption(
        "Converta DOCX, XLSX, PPTX e PDF para Markdown. "
        "Os arquivos são processados temporariamente e excluídos após a conversão."
    )

    uploaded = st.file_uploader(
        "Escolha um arquivo ou arraste-o aqui",
        type=sorted({ext.lstrip(".") for ext in FORMAT_BY_EXTENSION}),
    )

    if uploaded is None:
        st.info("Envie um arquivo para começar.")
        return

    try:
        validate_extension(uploaded.name)
        validate_size(uploaded.size)
    except ValueError as exc:
        st.error(str(exc))
        return

    with st.spinner("Convertendo..."):
        result = convert_upload(uploaded)

    st.success("Conversão concluída!")

    with st.expander("Preview", expanded=True):
        st.markdown(result.markdown)

    st.download_button(
        label="Baixar .md",
        data=result.markdown,
        file_name=f"{Path(uploaded.name).stem}.md",
        mime="text/markdown",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
