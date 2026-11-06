import puppeteer from "puppeteer-core";
const b = await puppeteer.launch({ executablePath: "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell", args: ["--no-sandbox"], protocolTimeout: 60000 });
const p = await b.newPage(); await p.setViewport({ width: 1080, height: 1920 }); await p.goto("file://" + process.argv[2], { waitUntil: "domcontentloaded" }); await new Promise(r => setTimeout(r, 1200));
await p.screenshot({ path: process.argv[3], type: "jpeg", quality: 92 }); await b.close();
