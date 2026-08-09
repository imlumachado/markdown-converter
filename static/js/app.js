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
        setProgress(0.05, "Enviado. Iniciando conversão...");
        const data = JSON.parse(xhr.responseText);
        pollStatus(data.status_url);
      } else {
        let detail = "Não foi possível enviar o arquivo.";
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

  function pollStatus(statusUrl) {
    const poll = function () {
      fetch(statusUrl)
        .then(function (response) {
          if (!response.ok) throw new Error("status");
          return response.json();
        })
        .then(function (data) {
          if (data.status === "processing") {
            const p = data.progress;
            if (p && p.total) {
              setProgress(p.current / p.total, "Convertendo página " + p.current + " de " + p.total + "...");
            } else {
              setProgress(0.2, "Convertendo... PDF digitalizado pode levar mais tempo.");
            }
            setTimeout(poll, 1500);
          } else if (data.status === "done") {
            downloadUrl = data.download_url;
            renderResult(data.markdown, data.warnings);
          } else {
            progressWrap.hidden = true;
            showError(data.detail || "Não foi possível converter o arquivo.");
          }
        })
        .catch(function () {
          progressWrap.hidden = true;
          showError("Erro ao consultar o status da conversão.");
        });
    };
    poll();
  }

  function renderResult(markdown, warnings) {
    progressWrap.hidden = true;
    if (window.marked) {
      preview.innerHTML = marked.parse(markdown);
    } else {
      preview.textContent = markdown;
    }
    if (warnings && warnings.length) {
      const box = document.createElement("div");
      box.className = "warning-box";
      box.textContent = warnings.join(" ");
      resultBox.insertBefore(box, resultBox.firstChild);
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
