(function () {
  const fmt = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 2 });
  const pct = function (n) {
    return n == null ? "\u2014" : ((n > 0 ? "+" : "") + fmt.format(n) + "%");
  };
  const num = function (n, d) {
    return n == null ? "\u2014" : n.toLocaleString("vi-VN", { maximumFractionDigits: d == null ? 2 : d });
  };
  const cls = function (n) {
    return n > 0 ? "up" : n < 0 ? "dn" : "";
  };
  let REPORT = null;
  const SOURCES = {};
  const charts = {};
  const newsPage = { global: 0, vn: 0 };
  const PAGE = 8;

  function srcLink(id) {
    const s = SOURCES[id];
    if (!s) return "";
    return '<a href="' + s.url + '" target="_blank" rel="noopener noreferrer">' + s.name + "</a>";
  }

  function boot() {
    const date = document.body.getAttribute("data-date");
    const path = date ? "./data/" + date + "/report.json" : "./data/index.json";
    const srcPath = date ? "./data/" + date + "/sources.json" : null;
    const reportP = window.__REPORT__
      ? Promise.resolve(window.__REPORT__)
      : fetch(path).then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status + " " + path);
          return r.json();
        });
    const sourcesP = window.__SOURCES__
      ? Promise.resolve(window.__SOURCES__)
      : srcPath
        ? fetch(srcPath)
            .then(function (r) {
              return r.ok ? r.json() : { sources: [] };
            })
            .catch(function () {
              return { sources: [] };
            })
        : Promise.resolve({ sources: [] });
    Promise.all([reportP, sourcesP])
      .then(function (pair) {
        const rep = pair[0];
        const src = pair[1];
        if (rep && rep.reports && !rep.snapshot) {
          document.getElementById("app").innerHTML = renderHub(rep);
          return;
        }
        REPORT = rep;
        (src.sources || []).forEach(function (s) {
          SOURCES[s.id] = s;
        });
        renderDash();
      })
      .catch(function (e) {
        document.getElementById("app").innerHTML =
          '<div class="err">Không tải được dữ liệu (' + e.message + ").</div>";
      });
  }

  function renderHub(cat) {
    const rows = (cat.reports || [])
      .map(function (r) {
        const href = "./" + (r.path || "");
        return (
          '<li class="hub-row"><a href="' +
          href +
          '">' +
          r.date +
          " \u2014 " +
          (r.title || "") +
          '</a> <span class="badge ' +
          (r.status || "") +
          '">' +
          (r.status || "") +
          "</span></li>"
        );
      })
      .join("");
    return (
      '<header class="hdr"><h1>DP Stock \u2014 Bản tin thị trường</h1></header><div class="pb" style="padding:16px"><ul class="news">' +
      rows +
      "</ul></div>"
    );
  }

  function sessionLabel(s) {
    if (s === "closed") return "đã đóng cửa";
    if (s === "intraday") return "phiên đang chạy";
    return "ngoài giờ";
  }

  function renderDash() {
    const r = REPORT;
    const sess = r.marketSession || (r.coverage && r.coverage.session) || "closed";
    document.getElementById("app").innerHTML =
      '<header class="hdr"><h1>Bản tin thị trường</h1><div class="meta"><span>' +
      (r.timezone || "") +
      "</span><span>" +
      (r.generatedAt || "") +
      '</span><span class="badge ' +
      sess +
      '">' +
      sessionLabel(sess) +
      '</span></div><button id="themeBtn" type="button">Giao diện</button></header>' +
      '<div class="ticker" id="ticker"></div><div class="grid">' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-globe"></i> Tin thế giới</div><div class="pb"><ul class="news" id="gNews"></ul></div><div class="pager" id="gPager"></div></section>' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-chart-line"></i> Biểu đồ<div class="tabs" id="chartTabs"><button data-tab="vnindex" class="on">VN-Index</button><button data-tab="world">Thế giới</button><button data-tab="crypto">Crypto</button></div></div><div class="pb" id="chartPane"></div></section>' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-flag"></i> Vĩ mô Việt Nam</div><div class="macros" id="macros"></div><div class="pb"><ul class="news" id="vNews"></ul></div><div class="pager" id="vPager"></div></section>' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-building"></i> Doanh nghiệp &amp; triển vọng</div><div class="pb" id="rightPane"></div></section>' +
      '</div><footer class="foot" id="foot"></footer>';
    renderTicker();
    renderNews("globalNews", "gNews", "gPager", "global");
    renderNews("vietnamNews", "vNews", "vPager", "vn");
    renderMacros();
    renderRight();
    renderChart("vnindex");
    renderFoot();
    document.getElementById("themeBtn").onclick = function () {
      const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("brief-theme", next);
    };
    document.getElementById("chartTabs").onclick = function (e) {
      const b = e.target.closest("button");
      if (!b) return;
      document.querySelectorAll("#chartTabs button").forEach(function (x) {
        x.classList.toggle("on", x === b);
      });
      renderChart(b.dataset.tab);
    };
  }

  function renderTicker() {
    const q = (REPORT.snapshot && REPORT.snapshot.quotes) || [];
    document.getElementById("ticker").innerHTML = q
      .map(function (x) {
        return (
          '<div class="tq"><span class="s">' +
          x.symbol +
          '</span><span class="p">' +
          num(x.price) +
          '</span><span class="' +
          cls(x.changePct) +
          '">' +
          pct(x.changePct) +
          "</span></div>"
        );
      })
      .join("");
  }

  function renderNews(key, listId, pagerId, which) {
    const items = REPORT[key] || [];
    const size = (REPORT.ui && REPORT.ui.pageSizeNews) || PAGE;
    const page = newsPage[which];
    const slice = items.slice(page * size, page * size + size);
    document.getElementById(listId).innerHTML = slice
      .map(function (n) {
        const img = (n.image && n.image.url) || "https://picsum.photos/seed/mkt/144/96";
        const impact = (n.impact && n.impact.text) || "";
        return (
          "<li><img src=\"" +
          img +
          '" alt=""><div><div class="when">' +
          String(n.date || "").replace("T", " ").slice(0, 16) +
          " \u00b7 " +
          srcLink(n.sourceId) +
          "</div><h3>" +
          n.title +
          "</h3><div>" +
          (n.summary || "") +
          '</div><div class="impact">' +
          impact +
          "</div></div></li>"
        );
      })
      .join("");
    const pages = Math.max(1, Math.ceil(items.length / size));
    document.getElementById(pagerId).innerHTML =
      '<button type="button" data-d="-1">Trước</button><span>Trang ' +
      (page + 1) +
      "/" +
      pages +
      " (" +
      items.length +
      ' tin)</span><button type="button" data-d="1">Sau</button>';
    document.getElementById(pagerId).onclick = function (e) {
      const b = e.target.closest("button");
      if (!b) return;
      newsPage[which] = Math.min(pages - 1, Math.max(0, page + Number(b.getAttribute("data-d"))));
      renderNews(key, listId, pagerId, which);
    };
  }

  function renderMacros() {
    const m = REPORT.vietnamMacro || [];
    document.getElementById("macros").innerHTML = m
      .map(function (x) {
        return (
          '<div class="mac"><b>' +
          (x.nameVi || x.name || "") +
          "</b>" +
          (x.value != null ? num(x.value) : "\u2014") +
          " " +
          (x.unit || "") +
          "</div>"
        );
      })
      .join("");
  }

  function renderRight() {
    const cos = (REPORT.companies || [])
      .map(function (c) {
        const chg = c.metrics && c.metrics.changePct;
        const impact = (c.impact && c.impact.text) || c.summary || "";
        return (
          '<div class="co"><div class="tk ' +
          cls(chg) +
          '">' +
          c.ticker +
          "<div>" +
          pct(chg) +
          "</div></div><div><b>" +
          c.headline +
          '</b><div class="impact">' +
          impact +
          "</div>" +
          srcLink(c.sourceId) +
          "</div></div>"
        );
      })
      .join("");
    const o = REPORT.outlook || {};
    function block(title, arr, mapFn) {
      return (
        '<div class="out"><div class="k">' +
        title +
        "</div>" +
        ((arr || []).map(mapFn).join("") || "<div>\u2014</div>") +
        "</div>"
      );
    }
    document.getElementById("rightPane").innerHTML =
      cos +
      block("Theo dõi", o.watchpoints, function (w) {
        return "<div>\u2022 " + w.text + (w.impact && w.impact.text ? " \u2014 " + w.impact.text : "") + "</div>";
      }) +
      block("Mốc kỹ thuật", o.levels, function (l) {
        return (
          "<div>" +
          l.symbol +
          " " +
          (l.kind === "support" ? "hỗ trợ" : l.kind === "resistance" ? "kháng cự" : l.kind) +
          " " +
          num(l.price) +
          " \u2014 " +
          (l.note || "") +
          "</div>"
        );
      }) +
      block("Sự kiện", o.events, function (e) {
        return (
          "<div>" +
          String(e.when || "").slice(0, 10) +
          " \u00b7 " +
          e.title +
          (e.impact && e.impact.text ? " \u2014 " + e.impact.text : "") +
          "</div>"
        );
      });
  }

  function seriesById(id) {
    const s = REPORT.series || {};
    if (s[id]) return s[id];
    return Object.values(s).find(function (x) {
      return x && x.id === id;
    });
  }

  function lineData(ser) {
    const pts = (ser && ser.points) || [];
    return {
      labels: pts.map(function (p) {
        return String(p.t || "").slice(5, 10);
      }),
      values: pts.map(function (p) {
        return p.v;
      }),
    };
  }

  function renderChart(tab) {
    const pane = document.getElementById("chartPane");
    if (tab === "vnindex") {
      const eq = REPORT.equityMarket || {};
      const idx = (eq.relatedIndices || [])
        .map(function (x) {
          return (
            '<div class="qrow"><span>' +
            x.symbol +
            '</span><span class="' +
            cls(x.changePct) +
            '">' +
            num(x.price) +
            " " +
            pct(x.changePct) +
            "</span></div>"
          );
        })
        .join("");
      pane.innerHTML =
        '<div class="chart-wrap"><div class="chart-main"><div class="stats">' +
        '<div class="stat"><b>VN-Index</b>' +
        num(eq.index && eq.index.latest && eq.index.latest.price) +
        "</div>" +
        '<div class="stat"><b>+/\u2212</b><span class="' +
        cls(eq.index && eq.index.latest && eq.index.latest.changePct) +
        '">' +
        pct(eq.index && eq.index.latest && eq.index.latest.changePct) +
        "</span></div>" +
        '<div class="stat"><b>KLGD (tr.cp)</b>' +
        num(((eq.liquidity && eq.liquidity.hose && eq.liquidity.hose.volumeShares) || 0) / 1e6) +
        "</div>" +
        '<div class="stat"><b>GTGD (tỷ)</b>' +
        num(eq.liquidity && eq.liquidity.hose && eq.liquidity.hose.valueVndBn) +
        "</div>" +
        '<div class="stat"><b>NN ròng (tỷ)</b><span class="' +
        cls(eq.foreign && eq.foreign.netValueVndBn) +
        '">' +
        num(eq.foreign && eq.foreign.netValueVndBn) +
        "</span></div>" +
        "<div class=\"stat\"><b>Tự doanh</b>" +
        (eq.proprietary && eq.proprietary.netValueVndBn != null
          ? num(eq.proprietary.netValueVndBn)
          : (eq.proprietary && eq.proprietary.note) || "\u2014") +
        "</div>" +
        '<div class="stat"><b>Cá nhân</b>' +
        (eq.retail && eq.retail.netValueVndBn != null
          ? num(eq.retail.netValueVndBn)
          : (eq.retail && eq.retail.note) || "\u2014") +
        "</div>" +
        '</div><canvas id="c1"></canvas><canvas id="c2" height="90"></canvas></div><div class="qlist">' +
        idx +
        "</div></div>";
      drawLine("c1", seriesById("vnindex"), "VN-Index");
      drawBars("c2");
    } else if (tab === "world") {
      const quotes = (REPORT.worldMarkets && REPORT.worldMarkets.quotes) || [];
      pane.innerHTML =
        '<div class="chart-wrap"><div class="chart-main"><canvas id="c1"></canvas></div><div class="qlist" id="wq">' +
        quotes
          .map(function (x) {
            return (
              '<div class="qrow" data-sym="' +
              x.symbol +
              '"><span>' +
              (x.nameVi || x.symbol) +
              '</span><span class="' +
              cls(x.changePct) +
              '">' +
              num(x.price) +
              " " +
              pct(x.changePct) +
              "</span></div>"
            );
          })
          .join("") +
        "</div></div>";
      const map = { DJI: "dji", NDX: "ndx", SPX: "spx", DXY: "dxy", NKY: "nky", HSI: "hsi" };
      drawLine("c1", seriesById("dji"), "Dow Jones");
      pane.querySelector("#wq").onclick = function (e) {
        const row = e.target.closest(".qrow");
        if (!row) return;
        drawLine("c1", seriesById(map[row.getAttribute("data-sym")] || "dji"), row.getAttribute("data-sym"));
      };
    } else {
      const quotes = (REPORT.cryptoMarkets && REPORT.cryptoMarkets.quotes) || [];
      pane.innerHTML =
        '<div class="chart-wrap"><div class="chart-main"><canvas id="c1"></canvas></div><div class="qlist">' +
        quotes
          .map(function (x) {
            return (
              '<div class="qrow"><span>' +
              x.symbol +
              '</span><span class="' +
              cls(x.changePct) +
              '">' +
              num(x.price) +
              " " +
              pct(x.changePct) +
              "</span></div>"
            );
          })
          .join("") +
        "</div></div>";
      drawLine("c1", seriesById("btcUsd"), "Bitcoin");
    }
  }

  function destroyChart(id) {
    if (charts[id]) {
      charts[id].destroy();
      delete charts[id];
    }
  }

  function drawLine(canvasId, ser, label) {
    destroyChart(canvasId);
    const d = lineData(ser);
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === "undefined") return;
    const extra = ser && ser.interpolation === "anchored" ? " (nội suy)" : "";
    charts[canvasId] = new Chart(ctx, {
      type: "line",
      data: {
        labels: d.labels,
        datasets: [
          {
            label: label + extra,
            data: d.values,
            borderColor: "#10b981",
            backgroundColor: "rgba(16,185,129,.12)",
            fill: true,
            tension: 0.25,
            pointRadius: 0,
            borderWidth: 1.6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#8b97a8", maxTicksLimit: 8 }, grid: { color: "#1c2430" } },
          y: { ticks: { color: "#8b97a8" }, grid: { color: "#1c2430" } },
        },
      },
    });
  }

  function drawBars(canvasId) {
    destroyChart(canvasId);
    const v = REPORT.series && REPORT.series.vnindexVolume5d;
    const f = REPORT.series && REPORT.series.foreignNet5dVndBn;
    const ctx = document.getElementById(canvasId);
    if (!ctx || !v || typeof Chart === "undefined") return;
    charts[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels: v.labels,
        datasets: [
          { label: "GTGD (nghìn tỷ)", data: v.valueVndTn, backgroundColor: "#3b82f6", yAxisID: "y" },
          {
            label: "NN ròng (tỷ)",
            data: (f && f.values) || [],
            type: "line",
            borderColor: "#f59e0b",
            yAxisID: "y1",
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: "#8b97a8", boxWidth: 10 } } },
        scales: {
          y: { position: "left", ticks: { color: "#8b97a8" }, grid: { color: "#1c2430" } },
          y1: { position: "right", ticks: { color: "#8b97a8" }, grid: { display: false } },
        },
      },
    });
  }

  function renderFoot() {
    const links = Object.keys(SOURCES)
      .map(function (id) {
        const s = SOURCES[id];
        return '<a href="' + s.url + '" target="_blank" rel="noopener noreferrer">' + s.name + "</a>";
      })
      .join(" \u00b7 ");
    document.getElementById("foot").innerHTML = (REPORT.disclaimer || "") + (links ? " \u00b7 " + links : "");
  }

  document.documentElement.setAttribute("data-theme", localStorage.getItem("brief-theme") || "dark");
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
