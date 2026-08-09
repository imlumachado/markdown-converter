(function () {
  "use strict";

  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const progressWrap = document.getElementById("progress-wrap");
  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  const errorBox = document.getElementById("error-box");
  const resultBox = document.getElementById("result-box");
  const preview = document.getElementById("preview");
  const downloadBtn = document.getElementById("download-btn");
  const newConversionBtn = document.getElementById("new-conversion-btn");

  let downloadUrl = null;

  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    progressWrap.hidden = true;
  }

  function hideError() {
    errorBox.hidden = true;
  }

  function setProgress(percent, text) {
    progressBar.style.width = Math.round(percent * 100) + "%";
    if (text) progressText.textContent = text;
  }

  function resetTool() {
    hideError();
    resultBox.hidden = true;
    progressWrap.hidden = true;
    progressBar.style.width = "0";
    downloadUrl = null;
    fileInput.value = "";
  }

  function upload(file) {
    resetTool();
    hideError();
    progressWrap.hidden = false;
    setProgress(0, "Enviando arquivo...");

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/convert");

    xhr.upload.onprogress = function (e) {
      if (e.lengthComputable) {
        setProgress(e.loaded / e.total, "Enviando arquivo...");
      }
    };

    xhr.onload = function () {
      if (xhr.status === 200) {
        setProgress(1, "Convertendo...");
        const data = JSON.parse(xhr.responseText);
        downloadUrl = data.download_url;
        renderResult(data.markdown);
      } else {
        let detail = "Não foi possível converter o arquivo.";
        try {
          const data = JSON.parse(xhr.responseText);
          if (data.detail) detail = data.detail;
        } catch (_) {
          /* ignore */
        }
        progressWrap.hidden = true;
        showError(detail);
      }
    };

    xhr.onerror = function () {
      progressWrap.hidden = true;
      showError("Erro de conexão. Tente novamente.");
    };

    xhr.onabort = function () {
      progressWrap.hidden = true;
      showError("Envio cancelado.");
    };

    xhr.send(formData);
  }

  function renderResult(markdown) {
    progressWrap.hidden = true;
    if (window.marked) {
      preview.innerHTML = marked.parse(markdown);
    } else {
      preview.textContent = markdown;
    }
    resultBox.hidden = false;
  }

  dropZone.addEventListener("click", function () {
    fileInput.click();
  });

  dropZone.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput.click();
    }
  });

  dropZone.addEventListener("dragover", function (e) {
    e.preventDefault();
    dropZone.classList.add("dragging");
  });

  dropZone.addEventListener("dragleave", function () {
    dropZone.classList.remove("dragging");
  });

  dropZone.addEventListener("drop", function (e) {
    e.preventDefault();
    dropZone.classList.remove("dragging");
    const file = e.dataTransfer.files[0];
    if (file) upload(file);
  });

  fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];
    if (file) upload(file);
  });

  downloadBtn.addEventListener("click", function () {
    if (downloadUrl) window.location.href = downloadUrl;
  });

  newConversionBtn.addEventListener("click", resetTool);
})();
