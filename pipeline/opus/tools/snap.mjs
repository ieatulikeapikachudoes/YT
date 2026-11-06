// snap.mjs page.html outdir t1,t2,... : seeks the timeline and screenshots each time; prints console errors
import puppeteer from "puppeteer-core"; import fs from "fs";
const [page, out, ts] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
const b = await puppeteer.launch({ executablePath: "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell", args: ["--no-sandbox", "--allow-file-access-from-files"], protocolTimeout: 120000 });
const p = await b.newPage(); const errs = []; p.on("console", m => { if (m.type() === "error") errs.push(m.text()); }); p.on("pageerror", e => errs.push(String(e)));
await p.setViewport({ width: 1080, height: 1920 }); await p.goto("file://" + page, { waitUntil: "domcontentloaded" }); await new Promise(r => setTimeout(r, 800));
for (const t of ts.split(",")) { await p.evaluate(t => { window.__timelines.main.seek(+t); }, t); await new Promise(r => setTimeout(r, 60)); await p.screenshot({ path: `${out}/${(+t).toFixed(2).padStart(6, "0")}.jpg`, type: "jpeg", quality: 80 }); }
console.log(JSON.stringify(errs)); await b.close();
