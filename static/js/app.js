(function () {
  "use strict";

  var dropZone = document.getElementById("drop-zone");
  var fileInput = document.getElementById("file-input");
  var progressWrap = document.getElementById("progress-wrap");
  var progressBar = document.getElementById("progress-bar");
  var progressText = document.getElementById("progress-text");
  var errorBox = document.getElementById("error-box");
  var resultBox = document.getElementById("result-box");
  var preview = document.getElementById("preview");
  var copyBtn = document.getElementById("copy-btn");
  var downloadBtn = document.getElementById("download-btn");
  var exportHtmlBtn = document.getElementById("export-html-btn");
  var newConversionBtn = document.getElementById("new-conversion-btn");
  var batchInfo = document.getElementById("batch-info");
  var historyList = document.getElementById("history-list");
  var clearHistoryBtn = document.getElementById("clear-history-btn");

  var HISTORY_KEY = "mdconverter-history";
  var HISTORY_LIMIT = 20;
  var downloadUrl = null;
  var currentMarkdown = "";
  var currentFilename = "";
  var filesQueue = [];

  /* ---------------- helpers ---------------- */

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
    batchInfo.hidden = true;
    progressBar.style.width = "0";
    downloadUrl = null;
    currentMarkdown = "";
    currentFilename = "";
    fileInput.value = "";
    filesQueue = [];
  }

  function baseName(filename) {
    return filename.replace(/\\/g, "/").split("/").pop() || filename;
  }

  function mdName(filename) {
    var base = baseName(filename);
    var dot = base.lastIndexOf(".");
    return (dot > 0 ? base.slice(0, dot) : base) + ".md";
  }

  /* ---------------- histórico (localStorage) ---------------- */

  function getHistory() {
    try {
      var raw = localStorage.getItem(HISTORY_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (_) {
      return [];
    }
  }

  function addToHistory(filename, markdown, timestamp) {
    var items = getHistory();
    items.unshift({
      filename: filename,
      markdown: markdown,
      date: timestamp || new Date().toISOString(),
    });
    if (items.length > HISTORY_LIMIT) items = items.slice(0, HISTORY_LIMIT);
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(items));
    } catch (_) {
      /* ignore */
    }
    renderHistory();
  }

  function renderHistory() {
    var items = getHistory();
    historyList.innerHTML = "";
    if (!items.length) {
      var empty = document.createElement("p");
      empty.className = "history-empty";
      empty.textContent = "Nenhuma conversão ainda.";
      historyList.appendChild(empty);
      return;
    }
    items.forEach(function (item) {
      var card = document.createElement("article");
      card.className = "history-item";

      var info = document.createElement("div");
      info.className = "history-info";

      var name = document.createElement("strong");
      name.textContent = item.filename;
      info.appendChild(name);

      var date = document.createElement("span");
      date.className = "history-date";
      date.textContent = new Date(item.date).toLocaleString("pt-BR");
      info.appendChild(date);

      card.appendChild(info);

      var actions = document.createElement("div");
      actions.className = "history-actions";

      var copy = document.createElement("button");
      copy.className = "btn btn-secondary btn-sm";
      copy.textContent = "Copiar";
      copy.addEventListener("click", function () {
        copyToClipboard(item.markdown);
      });
      actions.appendChild(copy);

      var download = document.createElement("button");
      download.className = "btn btn-secondary btn-sm";
      download.textContent = "Baixar";
      download.addEventListener("click", function () {
        downloadMarkdown(item.filename, item.markdown);
      });
      actions.appendChild(download);

      var remove = document.createElement("button");
      remove.className = "btn btn-secondary btn-sm";
      remove.textContent = "Remover";
      remove.addEventListener("click", function () {
        removeFromHistory(item.filename, item.date);
      });
      actions.appendChild(remove);

      card.appendChild(actions);
      historyList.appendChild(card);
    });
  }

  function removeFromHistory(filename, date) {
    var items = getHistory().filter(function (item) {
      return !(item.filename === filename && item.date === date);
    });
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(items));
    } catch (_) {
      /* ignore */
    }
    renderHistory();
  }

  clearHistoryBtn.addEventListener("click", function () {
    try {
      localStorage.removeItem(HISTORY_KEY);
    } catch (_) {
      /* ignore */
    }
    renderHistory();
  });

  /* ---------------- clipboard ---------------- */

  function copyToClipboard(text) {
    if (!text) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () {
        flashCopy("Copiado!");
      }, function () {
        fallbackCopy(text);
      });
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
      flashCopy("Copiado!");
    } catch (_) {
      flashCopy("Falha ao copiar");
    }
    document.body.removeChild(ta);
  }

  function flashCopy(message) {
    var original = copyBtn.textContent;
    copyBtn.textContent = message;
    copyBtn.disabled = true;
    setTimeout(function () {
      copyBtn.textContent = original;
      copyBtn.disabled = false;
    }, 1500);
  }

  copyBtn.addEventListener("click", function () {
    copyToClipboard(currentMarkdown);
  });

  /* ---------------- download ---------------- */

  function downloadMarkdown(filename, markdown) {
    var blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = mdName(filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function downloadHtml(filename, markdown) {
    var html = renderHtml(markdown);
    var blob = new Blob([html], { type: "text/html;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = (mdName(filename) || "conversao.md").replace(/\.md$/, "") + ".html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function renderHtml(markdown) {
    var body = window.marked ? marked.parse(markdown) : markdown.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    return "<!DOCTYPE html><html lang=\"pt-BR\"><head><meta charset=\"UTF-8\">" +
      "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">" +
      "<title>Conversão</title>" +
      "<style>body{font-family:system-ui,sans-serif;max-width:800px;margin:0 auto;padding:24px;line-height:1.6;color:#0f172a}" +
      "table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:6px 10px;text-align:left}" +
      "img{max-width:100%}pre{background:#f1f5f9;padding:12px;border-radius:8px;overflow:auto}</style>" +
      "</head><body>" + body + "</body></html>";
  }

  /* ---------------- conversão individual ---------------- */

  function upload(file, onDone) {
    hideError();
    progressWrap.hidden = false;
    setProgress(0, "Enviando " + baseName(file.name) + "...");

    var formData = new FormData();
    formData.append("file", file);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/convert");

    xhr.upload.onprogress = function (e) {
      if (e.lengthComputable) {
        setProgress(e.loaded / e.total, "Enviando " + baseName(file.name) + "...");
      }
    };

    xhr.onload = function () {
      if (xhr.status === 200) {
        var data = JSON.parse(xhr.responseText);
        pollStatus(data.status_url, file.name, onDone);
      } else {
        var detail = "Não foi possível enviar " + baseName(file.name) + ".";
        try {
          var parsed = JSON.parse(xhr.responseText);
          if (parsed.detail) detail = parsed.detail;
        } catch (_) { /* ignore */ }
        if (onDone) {
          onDone({ error: detail });
        } else {
          progressWrap.hidden = true;
          showError(detail);
        }
      }
    };

    xhr.onerror = function () {
      var msg = "Erro de conexão. Tente novamente.";
      if (onDone) { onDone({ error: msg }); } else { progressWrap.hidden = true; showError(msg); }
    };

    xhr.send(formData);
  }

  function pollStatus(statusUrl, filename, onDone) {
    var poll = function () {
      fetch(statusUrl)
        .then(function (response) {
          if (!response.ok) throw new Error("status");
          return response.json();
        })
        .then(function (data) {
          if (data.status === "processing") {
            var p = data.progress;
            if (p && p.total) {
              setProgress(p.current / p.total, "Convertendo " + baseName(filename) + " (" + p.current + "/" + p.total + ")...");
            } else {
              setProgress(0.2, "Convertendo " + baseName(filename) + "...");
            }
            setTimeout(poll, 1500);
          } else if (data.status === "done") {
            if (onDone) {
              onDone({ markdown: data.markdown, warnings: data.warnings, filename: filename });
            } else {
              renderResult(data.markdown, data.warnings, filename);
            }
          } else {
            var msg = data.detail || "Não foi possível converter o arquivo.";
            if (onDone) { onDone({ error: msg }); } else { progressWrap.hidden = true; showError(msg); }
          }
        })
        .catch(function () {
          var msg = "Erro ao consultar o status da conversão.";
          if (onDone) { onDone({ error: msg }); } else { progressWrap.hidden = true; showError(msg); }
        });
    };
    poll();
  }

  function renderResult(markdown, warnings, filename) {
    progressWrap.hidden = true;
    currentMarkdown = markdown;
    currentFilename = filename || "conversao.md";
    preview.innerHTML = window.marked ? marked.parse(markdown) : markdown;
    resultBox.hidden = false;

    var existing = resultBox.querySelector(".warning-box");
    if (existing) existing.remove();
    if (warnings && warnings.length) {
      var box = document.createElement("div");
      box.className = "warning-box";
      box.textContent = warnings.join(" ");
      resultBox.insertBefore(box, resultBox.firstChild);
    }
    addToHistory(currentFilename, markdown);
  }

  /* ---------------- conversão em lote ---------------- */

  function convertBatch(files) {
    if (!files || !files.length) return;
    resetTool();
    progressWrap.hidden = false;

    var results = [];
    var errors = [];
    var index = 0;

    function next() {
      if (index >= files.length) {
        finishBatch(results, errors);
        return;
      }
      var file = files[index];
      index += 1;
      upload(file, function (res) {
        if (res.error) {
          errors.push({ name: file.name, error: res.error });
        } else {
          results.push({ name: file.name, markdown: res.markdown });
        }
        next();
      });
    }
    next();
  }

  function finishBatch(results, errors) {
    progressWrap.hidden = true;
    if (results.length) {
      results.forEach(function (r) { addToHistory(r.name, r.markdown); });
      if (window.JSZip && results.length > 1) {
        downloadZip(results);
      } else if (results.length === 1) {
        renderResult(results[0].markdown, [], results[0].name);
      }
    }
    if (errors.length) {
      var summary = errors.map(function (e) { return e.name + ": " + e.error; }).join("\n");
      showError("Alguns arquivos falharam:\n" + summary);
    }
    if (!results.length && !errors.length) {
      showError("Nenhum arquivo processado.");
    }
  }

  function downloadZip(results) {
    var zip = new JSZip();
    results.forEach(function (r) {
      zip.file(mdName(r.name), r.markdown);
    });
    zip.generateAsync({ type: "blob" }).then(function (blob) {
      var url = URL.createObjectURL(blob);
      var a = document.createElement("a");
      a.href = url;
      a.download = "conversoes-markdown.zip";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
  }

  /* ---------------- eventos ---------------- */

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
    var files = Array.prototype.slice.call(e.dataTransfer.files);
    if (files.length > 1) {
      convertBatch(files);
    } else if (files.length === 1) {
      upload(files[0]);
    }
  });

  fileInput.addEventListener("change", function () {
    var files = Array.prototype.slice.call(fileInput.files);
    if (files.length > 1) {
      convertBatch(files);
    } else if (files.length === 1) {
      upload(files[0]);
    }
    fileInput.value = "";
  });

  downloadBtn.addEventListener("click", function () {
    if (downloadUrl) window.location.href = downloadUrl;
    else if (currentMarkdown) downloadMarkdown(currentFilename, currentMarkdown);
  });

  exportHtmlBtn.addEventListener("click", function () {
    if (currentMarkdown) downloadHtml(currentFilename, currentMarkdown);
  });

  newConversionBtn.addEventListener("click", resetTool);

  document.addEventListener("DOMContentLoaded", function () {
    renderHistory();
  });
})();
