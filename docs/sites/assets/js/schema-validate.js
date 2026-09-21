(function (global) {
  function isIso(s) { return typeof s === "string" && s.includes("T"); }
  function validateReport(d) {
    const errors = [];
    if (!d || d.schemaVersion !== "1.0.0") errors.push("schemaVersion");
    if (!d.id || !d.generatedAt) errors.push("id/generatedAt");
    if (!Array.isArray(d.snapshot && d.snapshot.quotes)) errors.push("snapshot.quotes");
    if (!Array.isArray(d.globalNews)) errors.push("globalNews");
    if (!Array.isArray(d.vietnamMacro) || d.vietnamMacro.length < 1) errors.push("vietnamMacro");
    if (!d.equityMarket || !d.equityMarket.index) errors.push("equityMarket.index");
    if (!d.series) errors.push("series");
    if (d.generatedAt && !isIso(d.generatedAt)) errors.push("generatedAt not ISO");
    return { ok: errors.length === 0, errors };
  }
  function validateWeekFile(w) {
    const errors = [];
    if (!w || w.schemaVersion !== "2.0.0") errors.push("schemaVersion");
    if (!w.yearMonth) errors.push("yearMonth");
    if (!w.week || !w.week.id || w.week.isoWeek == null) errors.push("week");
    if (!Array.isArray(w.days)) errors.push("days");
    (w.days || []).forEach(function (day, i) {
      if (!day || !day.date) errors.push("days[" + i + "].date");
      if (!day || !day.report) errors.push("days[" + i + "].report");
      if (!day || !day.sources) errors.push("days[" + i + "].sources");
    });
    return { ok: errors.length === 0, errors };
  }
  function validateCatalog(c) {
    const errors = [];
    if (!c || c.schemaVersion !== "2.0.0") errors.push("schemaVersion");
    if (c && c.layout !== "monthly-weekly") errors.push("layout");
    if (!Array.isArray(c && c.reports)) errors.push("reports");
    (c && c.reports || []).forEach(function (r, i) {
      if (!r.date || !r.weekPath || !r.path) errors.push("reports[" + i + "]");
    });
    return { ok: errors.length === 0, errors };
  }
  global.ReportSchema = { validateReport: validateReport, validateWeekFile: validateWeekFile, validateCatalog: validateCatalog };
})(typeof window !== "undefined" ? window : globalThis);
