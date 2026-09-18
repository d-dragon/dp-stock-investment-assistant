(function () {
  const $ = (sel, root) => (root || document).querySelector(sel);
  const fmt = (n, d = 2) =>
    n == null || Number.isNaN(Number(n))
      ? "—"
      : Number(n).toLocaleString("vi-VN", { maximumFractionDigits: d, minimumFractionDigits: 0 });
  const pct = (n) => (n == null ? "—" : (n > 0 ? "+" : "") + fmt(n, 2) + "%");
  const cls = (n) => (n == null ? "" : n >= 0 ? "pos" : "neg");

  function sourceMap(sourcesDoc) {
    const map = {};
    (sourcesDoc && sourcesDoc.sources || []).forEach((s) => { map[s.id] = s; });
    return map;
  }
  function sourceLink(map, id) {
    const s = map[id];
    if (!s) return "";
    return `<a href="${s.url}" target="_blank" rel="noopener noreferrer">${s.name}</a>`;
  }

  function renderTicker(quotes) {
    const bits = quotes.map((q) => {
      const sign = q.changePct >= 0 ? "pos" : "neg";
      return `<span>${q.name} <b class="${sign}">${fmt(q.price)} ${pct(q.changePct)}</b></span>`;
    });
    return bits.concat(bits).join("");
  }

  function renderKpis(quotes) {
    return quotes.map((q) => `
      <div class="card pad">
        <div class="muted">${q.name}</div>
        <div class="kpi-val">${q.currency === "USD" && q.unit !== "point" ? "$" : ""}${fmt(q.price)}</div>
        <div class="${cls(q.changePct)}">${pct(q.changePct)} · ${q.session || ""}</div>
      </div>`).join("");
  }

  function renderNews(items, smap) {
    return items.map((n) => `
      <article class="card">
        <img src="${(n.image && n.image.url) || "https://picsum.photos/seed/finance/800/400"}" alt="${(n.image && n.image.alt) || n.title}" />
        <div class="pad">
          <div class="pill">${n.region || ""} · ${n.category || ""}</div>
          <h3>${n.title}</h3>
          <p class="muted">${n.summary || ""}</p>
          ${sourceLink(smap, n.sourceId)}
        </div>
      </article>`).join("");
  }

  function renderMacro(items, smap) {
    return items.map((m) => `
      <article class="card pad">
        <div class="pill"><i class="fa-solid ${m.icon || "fa-chart-pie"}"></i> ${m.indicator}</div>
        <h3>${m.name}</h3>
        <div class="kpi-val">${fmt(m.value)}${m.unit === "percent" ? "%" : ""}</div>
        <p class="muted">${m.commentary || ""}</p>
        ${sourceLink(smap, m.sourceId)}
      </article>`).join("");
  }

  function renderCompanies(items, smap) {
    return items.map((c) => `
      <article class="card pad">
        <div class="pill">${c.ticker || ""} · ${c.theme || ""}</div>
        <h3>${c.headline}</h3>
        <p class="muted">${c.summary || ""}</p>
        ${sourceLink(smap, c.sourceId)}
      </article>`).join("");
  }

  function lineChart(canvasId, points, color) {
    const el = document.getElementById(canvasId);
    if (!el || !window.Chart || !points || !points.length) return;
    new Chart(el, {
      type: "line",
      data: {
        labels: points.map((p) => p.t.slice(5)),
        datasets: [{ data: points.map((p) => p.v), borderColor: color, backgroundColor: color + "33", fill: true, tension: 0.35, pointRadius: 2 }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#93a4bd", maxTicksLimit: 8 }, grid: { color: "rgba(148,163,184,.12)" } },
          y: { ticks: { color: "#93a4bd" }, grid: { color: "rgba(148,163,184,.12)" } }
        }
      }
    });
  }

  function barChart(canvasId, labels, datasets) {
    const el = document.getElementById(canvasId);
    if (!el || !window.Chart) return;
    new Chart(el, {
      type: "bar",
      data: { labels: labels.map((d) => d.slice(5)), datasets },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: "#93a4bd" } } },
        scales: {
          x: { ticks: { color: "#93a4bd" }, grid: { display: false } },
          y: { ticks: { color: "#93a4bd" }, grid: { color: "rgba(148,163,184,.12)" } }
        }
      }
    });
  }

  function bind(report, sources) {
    const smap = sourceMap(sources);
    const quotes = (report.snapshot && report.snapshot.quotes) || [];
    $("#ticker").innerHTML = renderTicker(quotes);
    $("#kpis").innerHTML = renderKpis(quotes);
    const dateLabel = (report.id || "").replace("daily-brief-", "");
    $("#title").textContent = "BÁO CÁO KINH TẾ - TÀI CHÍNH NGÀY " + dateLabel.split("-").reverse().join("/");
    $("#meta").textContent = `Tạo lúc ${report.generatedAt} · VN ${report.marketSession && report.marketSession.vn} · US ${report.marketSession && report.marketSession.us}`;
    $("#globalNews").innerHTML = renderNews(report.globalNews || [], smap);
    $("#vietnamMacro").innerHTML = renderMacro(report.vietnamMacro || [], smap);
    $("#companies").innerHTML = renderCompanies(report.companies || [], smap);
    const eq = report.equityMarket || {};
    const idx = eq.index || {};
    $("#eqSummary").innerHTML = `
      <div class="card pad"><div class="muted">Đóng cửa trước</div><div class="kpi-val">${fmt((idx.priorClose || {}).price)}</div><div class="${cls((idx.priorClose || {}).changePct)}">${pct((idx.priorClose || {}).changePct)}</div></div>
      <div class="card pad"><div class="muted">Mới nhất</div><div class="kpi-val">${fmt((idx.latest || {}).price)}</div><div class="${cls((idx.latest || {}).changePct)}">${pct((idx.latest || {}).changePct)} · ${(idx.latest || {}).session || ""}</div></div>
      <div class="card pad"><div class="muted">KL/GT HOSE phiên trước</div><div class="kpi-val">${fmt(((eq.liquidity || {}).hose || {}).valueVndBn)} tỷ</div><div class="muted">${fmt((((eq.liquidity || {}).hose || {}).volumeShares || 0) / 1e6)} tr CP</div></div>
      <div class="card pad"><div class="muted">NN ròng phiên trước</div><div class="kpi-val ${cls(((eq.foreign || {}).netValueVndBn))}">${fmt((eq.foreign || {}).netValueVndBn)} tỷ</div></div>`;
    const watch = ((report.outlook || {}).watchpoints || []).map((w) => `<li><b>${w.title}</b> — ${w.detail}</li>`).join("");
    $("#outlook").innerHTML = `<ul>${watch}</ul><p class="muted">${report.disclaimer || ""}</p>`;
    $("#sources").innerHTML = (sources.sources || []).map((s) => `<a href="${s.url}" target="_blank" rel="noopener noreferrer">${s.name}</a>`).join("");
    const s = report.series || {};
    lineChart("oilChart", (s.wtiUsd || {}).points, "#f59e0b");
    lineChart("goldChart", (s.goldUsdOz || {}).points, "#eab308");
    lineChart("btcChart", (s.btcUsd || {}).points, "#f97316");
    lineChart("djiChart", (s.dji || {}).points, "#3b82f6");
    if (s.vnindexVolume5d) {
      barChart("volChart", s.vnindexVolume5d.labels, [
        { label: "KL triệu CP", data: s.vnindexVolume5d.volumeMillionShares, backgroundColor: "#3b82f6" },
        { label: "GT nghìn tỷ", data: s.vnindexVolume5d.valueVndTn, backgroundColor: "#10b981" }
      ]);
    }
    if (s.foreignNet5dVndBn) {
      barChart("foreignChart", s.foreignNet5dVndBn.labels, [{
        label: "NN ròng tỷ đồng",
        data: s.foreignNet5dVndBn.values,
        backgroundColor: s.foreignNet5dVndBn.values.map((v) => v >= 0 ? "#10b981" : "#ef4444")
      }]);
    }
  }

  async function loadJson(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(url + " " + res.status);
    return res.json();
  }

  async function boot() {
    const date = document.body.dataset.reportDate;
    let report = window.__REPORT__;
    let sources = window.__SOURCES__;
    try {
      if (!report) report = await loadJson(`./data/${date}/report.json`);
      if (!sources) sources = await loadJson(`./data/${date}/sources.json`);
    } catch (e) {
      if (!report) {
        $("#app").innerHTML = `<div class="error">Không tải được JSON (${e.message}). Mở qua GitHub Pages, không dùng file://.</div>`;
        return;
      }
    }
    if (window.ReportSchema) {
      const v = window.ReportSchema.validateReport(report);
      if (!v.ok) console.warn("schema", v.errors);
    }
    bind(report, sources || { sources: [] });
  }

  window.toggleTheme = function () {
    const next = document.body.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.body.setAttribute("data-theme", next);
    localStorage.setItem("brief-theme", next);
  };

  document.addEventListener("DOMContentLoaded", function () {
    const saved = localStorage.getItem("brief-theme");
    if (saved) document.body.setAttribute("data-theme", saved);
    boot();
  });
})();
