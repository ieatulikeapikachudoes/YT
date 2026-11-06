import fs from "fs"; import puppeteer from "puppeteer-core";
const g = JSON.parse(fs.readFileSync("geo.json"));
const land = Object.values(g.countries).map(c => c.d).join(" ");
const svg = (X0, Y0, W, H, K, oct) => `<svg xmlns="http://www.w3.org/2000/svg" width="${Math.round(W * K)}" height="${Math.round(H * K)}" viewBox="${X0} ${Y0} ${W} ${H}">
<defs><radialGradient id="sea" cx="0.55" cy="0.55" r="0.8"><stop offset="0" stop-color="#0b1c2e"/><stop offset="1" stop-color="#050b14"/></radialGradient>
<filter id="hill" x="0" y="0" width="1" height="1" filterUnits="objectBoundingBox"><feTurbulence type="fractalNoise" baseFrequency="${0.012 * 900 / W * (W > 1500 ? 1 : 3)}" numOctaves="${oct}" seed="7" result="n"/>
<feDiffuseLighting in="n" surfaceScale="7" lighting-color="#fff" diffuseConstant="1.0"><feDistantLight azimuth="315" elevation="40"/></feDiffuseLighting></filter>
<clipPath id="lc"><path d="${land}"/></clipPath><filter id="shore"><feGaussianBlur stdDeviation="${W / 300}"/></filter></defs>
<rect x="${X0}" y="${Y0}" width="${W}" height="${H}" fill="url(#sea)"/>
<path d="${land}" fill="none" stroke="#1d4a6e" stroke-width="${W / 160}" opacity="0.45" filter="url(#shore)"/>
<g clip-path="url(#lc)"><rect x="${X0}" y="${Y0}" width="${W}" height="${H}" fill="#1a1f27"/>
<rect x="${X0}" y="${Y0}" width="${W}" height="${H}" filter="url(#hill)" style="mix-blend-mode:multiply" opacity="0.55"/>
<rect x="${X0}" y="${Y0}" width="${W}" height="${H}" fill="#2b3340" opacity="0.35" style="mix-blend-mode:screen"/></g></svg>`;
const b = await puppeteer.launch({ executablePath: "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell", args: ["--no-sandbox"], protocolTimeout: 180000 });
async function shot(name, X0, Y0, W, H, K, oct) {
  const p = await b.newPage(); await p.setViewport({ width: Math.round(W * K), height: Math.round(H * K) });
  await p.setContent(`<html><body style="margin:0">${svg(X0, Y0, W, H, K, oct)}</body></html>`);
  await p.screenshot({ path: `proj-A/assets/${name}.jpg`, type: "jpeg", quality: 86 }); await p.close();
  return { X0, Y0, W, H };
}
const R = { wide: await shot("relief-wide", -1300, -700, 3500, 3000, 0.9, 6), near: await shot("relief-near", 600, 760, 460, 400, 6, 6) };
fs.writeFileSync("relief.json", JSON.stringify(R)); await b.close(); console.log(R);
