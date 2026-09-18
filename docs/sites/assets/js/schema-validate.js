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
  global.ReportSchema = { validateReport };
})(window);
