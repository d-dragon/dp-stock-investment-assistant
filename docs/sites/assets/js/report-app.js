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
  /** @type {Record<string, object>} in-memory cache of weekly JSON by weekPath */
  const weekCache = {};
  let catalogCache = null;

  function srcLink(id, overrideUrl) {
    const s = SOURCES[id];
    const url = overrideUrl || (s && s.url);
    if (!url) return (s && s.name) || "";
    const name = s ? s.name : (id || "Nguồn");
    return '<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + name + "</a>";
  }

  function resolveNewsUrl(n) {
    if (!n) return "";
    if (n.url && /^https?:\/\//i.test(n.url)) return n.url;
    if (n.id && /^https?:\/\//i.test(n.id)) return n.id;
    const s = SOURCES[n.sourceId];
    if (s && s.url) return s.url;
    return "";
  }

  function parseRoute() {
    const raw = (location.hash || "").replace(/^#\/?/, "").trim();
    if (!raw || raw === "latest" || raw === "years" || raw.indexOf("y/") === 0) {
      return { view: "latest", date: null };
    }
    const m = raw.match(/^(\d{4}-\d{2}-\d{2})$/);
    if (m) return { view: "day", date: m[1] };
    return { view: "latest", date: null };
  }

  function latestReportDate(cat) {
    const list = (cat.reports || []).slice().sort(function (a, b) {
      return b.date.localeCompare(a.date);
    });
    return list.length ? list[0].date : null;
  }

  function reportDates(cat) {
    const map = {};
    (cat.reports || []).forEach(function (r) {
      map[r.date] = r;
    });
    return map;
  }

  function fetchJson(path) {
    return fetch(path).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status + " " + path);
      return r.json();
    });
  }

  function loadCatalog() {
    if (catalogCache) return Promise.resolve(catalogCache);
    return fetchJson("./data/index.json").then(function (cat) {
      catalogCache = cat;
      return cat;
    });
  }

  function loadWeek(weekPath) {
    if (weekCache[weekPath]) return Promise.resolve(weekCache[weekPath]);
    return fetchJson("./data/" + weekPath).then(function (week) {
      weekCache[weekPath] = week;
      return week;
    });
  }

  function loadDayFile(dayPath) {
    return fetchJson("./data/" + dayPath).then(function (day) {
      if (day && day.report) return day;
      throw new Error("day file thiếu report: " + dayPath);
    });
  }

  function resolveDay(entry, date) {
    if (entry.dayPath) return loadDayFile(entry.dayPath);
    return loadWeek(entry.weekPath).then(function (week) {
      const day = (week.days || []).find(function (d) {
        return d.date === date;
      });
      if (!day) throw new Error("Không có ngày " + date + " trong " + entry.weekPath);
      if (day.dayPath) return loadDayFile(day.dayPath);
      if (day.report) return day;
      throw new Error("Không có payload ngày " + date + " trong " + entry.weekPath);
    });
  }

  function clearSources() {
    Object.keys(SOURCES).forEach(function (k) {
      delete SOURCES[k];
    });
  }

  function normalizeOutlook(raw) {
    if (raw && !Array.isArray(raw) && typeof raw === "object") {
      return {
        watchpoints: raw.watchpoints || [],
        levels: raw.levels || [],
        events: raw.events || []
      };
    }
    if (Array.isArray(raw)) {
      return {
        watchpoints: raw.map(function (x) {
          return { text: x.text || x.title || "", impact: x.impact || null };
        }),
        levels: [],
        events: raw
          .filter(function (x) { return x && (x.when || x.title); })
          .map(function (x) {
            return { when: x.when || "", title: x.title || x.text || "", impact: x.impact || null };
          })
      };
    }
    return { watchpoints: [], levels: [], events: [] };
  }

  function applyDayPayload(day) {
    REPORT = day.report || {};
    REPORT.outlook = normalizeOutlook(REPORT.outlook);
    if (!REPORT.series || typeof REPORT.series !== "object") REPORT.series = {};
    clearSources();
    const src = day.sources || {};
    (src.sources || []).forEach(function (s) {
      if (s && s.id) SOURCES[s.id] = s;
    });
    newsPage.global = 0;
    newsPage.vn = 0;
    Object.keys(charts).forEach(function (id) {
      if (charts[id]) {
        charts[id].destroy();
        delete charts[id];
      }
    });
    renderDash();
  }

  function showError(msg) {
    document.getElementById("app").innerHTML = '<div class="err">' + msg + "</div>";
  }

  function boot() {
    const route = parseRoute();
    loadCatalog()
      .then(function (cat) {
        window.__CATALOG__ = cat;
        let date = route.date;
        if (!date) {
          date = latestReportDate(cat);
          if (!date) throw new Error("Catalog trống");
          location.replace("#/" + date);
          return;
        }
        const entry = (cat.reports || []).find(function (r) {
          return r.date === date;
        });
        if (!entry || (!entry.weekPath && !entry.dayPath)) {
          throw new Error("Không có mục catalog cho " + date);
        }
        return resolveDay(entry, date).then(function (day) {
          if (!day || !day.report) {
            throw new Error("Không có payload ngày " + date);
          }
          window.__BRIEF_DATE__ = date;
          applyDayPayload(day);
        });
      })
      .catch(function (e) {
        showError("Không tải được (" + e.message + '). <a href="#/latest">Thử bản mới nhất</a>');
      });
  }

  function sessionLabel(s) {
    if (s === "closed") return "đã đóng cửa";
    if (s === "intraday") return "phiên đang chạy";
    return "ngoài giờ";
  }

  function bindDatePicker(activeDate) {
    const btn = document.getElementById("dateBtn");
    const pop = document.getElementById("calPop");
    const wrap = document.getElementById("datePicker");
    if (!btn || !pop || !wrap) return;
    let view = activeDate ? activeDate.slice(0, 7) : null;

    function close() {
      pop.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    }
    function open() {
      const cat = window.__CATALOG__;
      if (!cat) return;
      if (!view) {
        const latest = latestReportDate(cat);
        view = latest ? latest.slice(0, 7) : null;
      }
      pop.innerHTML = renderCalendar(cat, view, activeDate);
      pop.hidden = false;
      btn.setAttribute("aria-expanded", "true");
    }

    btn.onclick = function (e) {
      e.stopPropagation();
      if (pop.hidden) open();
      else close();
    };
    pop.onclick = function (e) {
      e.stopPropagation();
      const nav = e.target.closest("[data-nav]");
      if (nav) {
        view = nav.getAttribute("data-nav");
        pop.innerHTML = renderCalendar(window.__CATALOG__, view, activeDate);
        return;
      }
      const day = e.target.closest("button[data-date]");
      if (day) {
        const next = day.getAttribute("data-date");
        close();
        if (next && next !== activeDate) location.hash = "#/" + next;
      }
    };
    if (!window.__CAL_DOC_BOUND__) {
      window.__CAL_DOC_BOUND__ = true;
      document.addEventListener("click", function (e) {
        const el = document.getElementById("datePicker");
        const p = document.getElementById("calPop");
        if (el && p && !p.hidden && !el.contains(e.target)) {
          p.hidden = true;
          const b = document.getElementById("dateBtn");
          if (b) b.setAttribute("aria-expanded", "false");
        }
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
          const p = document.getElementById("calPop");
          const b = document.getElementById("dateBtn");
          if (p) p.hidden = true;
          if (b) b.setAttribute("aria-expanded", "false");
        }
      });
    }
  }

  function renderCalendar(cat, ym, activeDate) {
    const dates = reportDates(cat);
    const parts = (ym || activeDate || "").split("-");
    let y = parseInt(parts[0], 10);
    let m = parseInt(parts[1], 10);
    if (!y || !m) {
      const latest = latestReportDate(cat);
      y = parseInt(latest.slice(0, 4), 10);
      m = parseInt(latest.slice(5, 7), 10);
    }
    const first = new Date(y, m - 1, 1);
    const startPad = (first.getDay() + 6) % 7;
    const daysInMonth = new Date(y, m, 0).getDate();
    const prev = m === 1 ? y - 1 + "-12" : y + "-" + String(m - 1).padStart(2, "0");
    const next = m === 12 ? y + 1 + "-01" : y + "-" + String(m + 1).padStart(2, "0");
    const label = first.toLocaleString("vi-VN", { month: "long", year: "numeric" });
    let cells = "";
    for (let i = 0; i < startPad; i++) cells += '<span class="cal-cell empty"></span>';
    for (let day = 1; day <= daysInMonth; day++) {
      const ds = y + "-" + String(m).padStart(2, "0") + "-" + String(day).padStart(2, "0");
      const hit = dates[ds];
      if (hit) {
        const on = ds === activeDate ? " on" : "";
        cells +=
          '<button type="button" class="cal-cell has' +
          on +
          '" data-date="' +
          ds +
          '" title="' +
          (hit.title || ds) +
          '">' +
          day +
          "</button>";
      } else {
        cells += '<span class="cal-cell">' + day + "</span>";
      }
    }
    return (
      '<div class="cal-head"><button type="button" data-nav="' +
      prev +
      '" aria-label="Tháng trước">‹</button><strong>' +
      label +
      '</strong><button type="button" data-nav="' +
      next +
      '" aria-label="Tháng sau">›</button></div>' +
      '<div class="cal-dow"><span>T2</span><span>T3</span><span>T4</span><span>T5</span><span>T6</span><span>T7</span><span>CN</span></div>' +
      '<div class="cal-grid">' +
      cells +
      "</div>" +
      '<div class="cal-foot"><a href="#/latest">Mới nhất</a><span class="muted">Ngày có báo cáo được tô sáng</span></div>'
    );
  }

  function renderDash() {
    const r = REPORT;
    const sess = r.marketSession || (r.coverage && r.coverage.session) || "closed";
    const d = window.__BRIEF_DATE__ || "";
    document.getElementById("app").innerHTML =
      '<header class="hdr"><div class="hdr-left"><a class="nav-home" href="../index.html" title="Về trang docs"><i class="fa-solid fa-house"></i><span>Home</span></a><div class="hdr-titles"><h1>Bản tin thị trường</h1></div></div><div class="meta"><span>' +
      (r.timezone || "") +
      "</span><span>" +
      (r.generatedAt || "") +
      '</span><span class="badge ' +
      sess +
      '">' +
      sessionLabel(sess) +
      '</span></div>' +
      '<div class="date-picker" id="datePicker">' +
      '<button type="button" class="date-btn" id="dateBtn" aria-haspopup="dialog" aria-expanded="false" title="Chọn ngày">' +
      '<i class="fa-regular fa-calendar"></i> <span>' +
      d +
      "</span></button>" +
      '<div class="cal-pop" id="calPop" hidden role="dialog" aria-label="Chọn ngày báo cáo"></div></div>' +
      '<button id="themeBtn" type="button">Giao diện</button></header>' +
      '<div class="ticker" id="ticker"></div><div class="grid">' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-globe"></i> Tin thế giới</div><div class="pb"><ul class="news" id="gNews"></ul></div><div class="pager" id="gPager"></div></section>' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-chart-line"></i> Biểu đồ<div class="tabs" id="chartTabs"><button data-tab="vnindex" class="on">VN-Index</button><button data-tab="world">Thế giới</button><button data-tab="crypto">Crypto</button></div></div><div class="pb" id="chartPane"></div></section>' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-flag"></i> Vĩ mô Việt Nam</div><div class="macros" id="macros"></div><div class="pb"><ul class="news" id="vNews"></ul></div><div class="pager" id="vPager"></div></section>' +
      '<section class="pane"><div class="pt"><i class="fa-solid fa-building"></i> Doanh nghiệp & triển vọng</div><div class="pb" id="rightPane"></div></section>' +
      '</div><footer class="foot" id="foot"></footer>';
    renderTicker();
    renderNews("globalNews", "gNews", "gPager", "global");
    renderNews("vietnamNews", "vNews", "vPager", "vn");
    renderMacros();
    renderRight();
    renderChart("vnindex");
    renderFoot();
    bindDatePicker(d);
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
        const link = resolveNewsUrl(n);
        const titleHtml = link
          ? '<a href="' + link + '" target="_blank" rel="noopener noreferrer">' + n.title + "</a>"
          : n.title;
        const imgTag = '<img src="' + img + '" alt="">';
        const imgHtml = link
          ? '<a href="' + link + '" target="_blank" rel="noopener noreferrer" tabindex="-1">' + imgTag + "</a>"
          : imgTag;
        const sourceHtml = srcLink(n.sourceId, link || null);
        return (
          "<li>" +
          imgHtml +
          "<div><div class=\"when\">" +
          String(n.date || "").replace("T", " ").slice(0, 16) +
          " \u00b7 " +
          sourceHtml +
          "</div><h3>" +
          titleHtml +
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
  window.addEventListener("hashchange", boot);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
