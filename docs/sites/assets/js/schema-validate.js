(function (global) {
  function isIso(s) {
    return typeof s === "string" && /\d{4}-\d{2}-\d{2}T/.test(s);
  }
  function isYmd(s) {
    return typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s);
  }
  function isNum(n) {
    return typeof n === "number" && isFinite(n);
  }
  function isNumOrNull(n) {
    return n == null || isNum(n);
  }

  var REPORT_KEYS = [
    "schemaVersion", "id", "type", "locale", "timezone", "generatedAt",
    "coverage", "marketSession", "disclaimer", "ui", "snapshot",
    "globalNews", "vietnamNews", "vietnamMacro", "equityMarket",
    "worldMarkets", "cryptoMarkets", "companies", "outlook", "series"
  ];
  var SERIES_IDS = [
    "vnindex", "dji", "ndx", "spx", "dxy", "nky", "hsi",
    "btcUsd", "vnindexVolume5d", "foreignNet5dVndBn"
  ];
  var IMPACT_DIR = { risk_on: 1, risk_off: 1, mixed: 1, neutral: 1 };

  function checkImpact(prefix, imp, errors) {
    if (!imp || typeof imp !== "object" || Array.isArray(imp)) {
      errors.push(prefix + ".impact");
      return;
    }
    if (!IMPACT_DIR[imp.direction]) errors.push(prefix + ".impact.direction");
    if (!imp.horizon) errors.push(prefix + ".impact.horizon");
    if (!Array.isArray(imp.assets) || !imp.assets.length) errors.push(prefix + ".impact.assets");
    if (typeof imp.text !== "string" || imp.text.length < 8) errors.push(prefix + ".impact.text");
  }

  function checkNews(name, arr, errors) {
    if (!Array.isArray(arr) || arr.length < 8) {
      errors.push(name + " length<8");
      return;
    }
    arr.forEach(function (n, i) {
      var p = name + "[" + i + "]";
      if (!n || !n.id || !n.title || !n.summary || !n.sourceId) errors.push(p + " fields");
      if (n && n.date && !isIso(n.date)) errors.push(p + ".date");
      if (n) checkImpact(p, n.impact, errors);
    });
  }

  function validateReport(d) {
    var errors = [];
    if (!d || d.schemaVersion !== "1.0.0") errors.push("schemaVersion");
    if (!d || d.type !== "daily_market_brief") errors.push("type");
    if (!d || d.locale !== "vi-VN") errors.push("locale");
    if (!d || d.timezone !== "Asia/Ho_Chi_Minh") errors.push("timezone");
    if (!d || !d.id || !d.generatedAt) errors.push("id/generatedAt");
    if (d && d.generatedAt && !isIso(d.generatedAt)) errors.push("generatedAt not ISO");
    REPORT_KEYS.forEach(function (k) {
      if (!d || d[k] == null) errors.push("missing." + k);
    });
    if (d && d.outlook && Array.isArray(d.outlook)) {
      errors.push("outlook must be object {watchpoints,levels,events}");
    }
    if (!Array.isArray(d && d.snapshot && d.snapshot.quotes) || d.snapshot.quotes.length < 10) {
      errors.push("snapshot.quotes");
    } else {
      d.snapshot.quotes.forEach(function (q, i) {
        if (!q || !q.symbol || !isNum(q.price) || !isNumOrNull(q.changePct)) {
          errors.push("snapshot.quotes[" + i + "]");
        }
      });
    }
    checkNews("globalNews", d && d.globalNews, errors);
    checkNews("vietnamNews", d && d.vietnamNews, errors);
    if (!Array.isArray(d && d.vietnamMacro) || d.vietnamMacro.length < 8) {
      errors.push("vietnamMacro length<8");
    }
    var eq = d && d.equityMarket;
    if (!eq || !eq.index || !eq.index.latest || !isNum(eq.index.latest.price)) {
      errors.push("equityMarket.index.latest");
    }
    if (!eq || !eq.liquidity || !eq.liquidity.hose) errors.push("equityMarket.liquidity.hose");
    if (!eq || !eq.foreign || !isNumOrNull(eq.foreign.netValueVndBn)) errors.push("equityMarket.foreign");
    if (!Array.isArray(d && d.companies) || d.companies.length < 5) errors.push("companies length<5");
    var o = d && d.outlook;
    if (!o || typeof o !== "object" || Array.isArray(o)) {
      errors.push("outlook");
    } else {
      if (!Array.isArray(o.watchpoints) || o.watchpoints.length < 2) errors.push("outlook.watchpoints");
      if (!Array.isArray(o.levels) || o.levels.length < 2) errors.push("outlook.levels");
      if (!Array.isArray(o.events) || o.events.length < 2) errors.push("outlook.events");
    }
    var s = d && d.series;
    if (!s || typeof s !== "object") {
      errors.push("series");
    } else {
      SERIES_IDS.forEach(function (id) {
        if (!s[id]) errors.push("series." + id);
      });
      ["vnindex", "dji", "btcUsd"].forEach(function (id) {
        if (s[id] && (!Array.isArray(s[id].points) || s[id].points.length < 2)) {
          errors.push("series." + id + ".points");
        }
      });
      if (s.vnindexVolume5d && !Array.isArray(s.vnindexVolume5d.labels)) {
        errors.push("series.vnindexVolume5d.labels");
      }
    }
    if (!Array.isArray(d && d.worldMarkets && d.worldMarkets.quotes) || d.worldMarkets.quotes.length < 6) {
      errors.push("worldMarkets.quotes");
    }
    if (!Array.isArray(d && d.cryptoMarkets && d.cryptoMarkets.quotes) || d.cryptoMarkets.quotes.length < 2) {
      errors.push("cryptoMarkets.quotes");
    }
    return { ok: errors.length === 0, errors: errors };
  }

  function validateWeekFile(w) {
    var errors = [];
    if (!w || w.schemaVersion !== "2.0.0") errors.push("schemaVersion");
    if (!w || !/^\d{4}-\d{2}$/.test(w.yearMonth || "")) errors.push("yearMonth");
    if (!w || !w.week || !w.week.id || w.week.isoWeek == null) errors.push("week");
    if (!Array.isArray(w && w.days) || !w.days.length) errors.push("days");
    var seen = {};
    (w && w.days || []).forEach(function (day, i) {
      if (!day || !isYmd(day.date)) errors.push("days[" + i + "].date");
      if (day && day.date) {
        if (seen[day.date]) errors.push("days[" + i + "] duplicate " + day.date);
        seen[day.date] = 1;
      }
      if (!day || !day.report) errors.push("days[" + i + "].report");
      else {
        var inner = validateReport(day.report);
        inner.errors.forEach(function (e) {
          errors.push("days[" + i + "].report." + e);
        });
      }
      if (!day || !day.sources || !Array.isArray(day.sources.sources) || day.sources.sources.length < 4) {
        errors.push("days[" + i + "].sources");
      }
    });
    return { ok: errors.length === 0, errors: errors };
  }

  function validateCatalog(c) {
    var errors = [];
    if (!c || c.schemaVersion !== "2.0.0") errors.push("schemaVersion");
    if (c && c.layout !== "monthly-weekly") errors.push("layout");
    if (!Array.isArray(c && c.reports) || !c.reports.length) errors.push("reports");
    (c && c.reports || []).forEach(function (r, i) {
      if (!r || !isYmd(r.date) || !r.weekPath || !r.path || !r.weekId) {
        errors.push("reports[" + i + "]");
      }
    });
    return { ok: errors.length === 0, errors: errors };
  }

  global.ReportSchema = {
    validateReport: validateReport,
    validateWeekFile: validateWeekFile,
    validateCatalog: validateCatalog,
    SERIES_IDS: SERIES_IDS,
    REPORT_KEYS: REPORT_KEYS
  };
})(typeof window !== "undefined" ? window : globalThis);
