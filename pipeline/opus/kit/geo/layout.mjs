// layout.mjs <proj dir>: opens the built page, seeks to the end of every line, and reports layout problems as JSON.
// Checks: text off screen, labels/cards overlapping, labels in the caption band or bottom app zone, too many labels, things off screen, WT misses.
import puppeteer from "puppeteer-core"; import path from "path";
const dir = path.resolve(process.argv[2]);
const b = await puppeteer.launch({ executablePath: process.env.HYPERFRAMES_BROWSER_PATH || "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell", args: ["--no-sandbox", "--allow-file-access-from-files"] });
const p = await b.newPage(); await p.setViewport({ width: 1080, height: 1920 });
const errs = []; p.on("console", m => { if (m.type() === "error") errs.push(m.text()); }); p.on("pageerror", e => errs.push("JS ERROR " + e.message));
await p.goto("file://" + dir + "/index.html", { waitUntil: "load" }); await p.evaluate(() => document.fonts.ready);
const out = await p.evaluate(() => {
  const tl = window.__timelines.main, T = window.__T, keys = Object.keys(T).filter(k => k !== "end"), issues = [];
  const vis = el => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentNode) o *= +getComputedStyle(e).opacity; return o > 0.6; };
  const name = el => (el.querySelector(".k")?.textContent ? `card "${el.querySelector(".k").textContent}"` : el.querySelector("text") ? `label "${el.querySelector("text").textContent}"` : el.id);
  keys.forEach((k, i) => {
    const t = (i + 1 < keys.length ? T[keys[i + 1]] : T.end) - 0.3; tl.seek(t);
    const boxes = [];
    const tt = document.getElementById("title"); if (vis(tt)) boxes.push({ n: "title", r: tt.querySelector("span").getBoundingClientRect(), kind: "text" });
    document.querySelectorAll(".card").forEach(c => { if (vis(c)) boxes.push({ n: name(c), r: c.querySelector(".box").getBoundingClientRect(), kind: "text" }); });
    document.querySelectorAll(".lab").forEach(l => { if (vis(l)) boxes.push({ n: name(l), r: l.querySelector("text").getBoundingClientRect(), kind: "text" }); });
    document.querySelectorAll("#cam .ann:not(.lab)").forEach(g => { if (!vis(g)) return; const r = g.getBoundingClientRect(); if (r.width + r.height < 2) return;
      const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2; if (cx < 0 || cx > 1080 || cy < 60 || cy > 1600) issues.push({ key: k, msg: `a ${g.id} element (marker/arrow/line) is off screen: move the camera focus or drop it` }); });
    // subject size: everything drawn on the map this line (shapes, markers, arrows, lines, labels) should span at least a quarter of the frame height
    let y0 = 1e9, y1 = -1e9, x0 = 1e9, x1 = -1e9;
    document.querySelectorAll("#cam .ann, #cam .shape").forEach(g => { if (!vis(g)) return; const r = g.getBoundingClientRect(); if (r.width + r.height < 2) return;
      y0 = Math.min(y0, Math.max(r.top, 0)); y1 = Math.max(y1, Math.min(r.bottom, 1340)); x0 = Math.min(x0, Math.max(r.left, 0)); x1 = Math.max(x1, Math.min(r.right, 1080)); });
    if (y1 < y0 || (y1 - y0 < 480 && x1 - x0 < 540)) issues.push({ key: k, msg: `the map subject is small (${y1 < y0 ? "nothing" : Math.round(y1 - y0) + "px tall, " + Math.round(x1 - x0) + "px wide"}); zoom the camera in on it, or add a highlight/line/marker cluster so the picture fills the middle of the screen` });
    const labels = boxes.filter(x => x.n.startsWith("label")).length; if (labels > 3) issues.push({ key: k, msg: `${labels} labels on screen at once; keep it to 2 or 3` });
    boxes.forEach(x => { const r = x.r;
      if (r.left < 30 || r.right > 1050) issues.push({ key: k, msg: `${x.n} runs off the ${r.left < 30 ? "left" : "right"} edge: shorten it, use side left/right, or move the camera` });
      if (r.top < 100) issues.push({ key: k, msg: `${x.n} is cut off at the top` });
      if (x.n.startsWith("label") && r.bottom > 1350) issues.push({ key: k, msg: `${x.n} sits in the caption area at the bottom: pick a target higher up or a different camera focus` }); });
    for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) { const A = boxes[a].r, B = boxes[c].r;
      const ix = Math.max(0, Math.min(A.right, B.right) - Math.max(A.left, B.left)), iy = Math.max(0, Math.min(A.bottom, B.bottom) - Math.max(A.top, B.top));
      const sm = Math.min(A.width * A.height, B.width * B.height) || 1; if (ix * iy / sm > 0.15) issues.push({ key: k, msg: `${boxes[a].n} overlaps ${boxes[c].n}` }); }
  });
  return issues;
});
errs.filter(e => /WT miss|JS ERROR/.test(e)).forEach(e => out.push({ key: "?", msg: e }));
console.log(JSON.stringify(out)); await b.close();
