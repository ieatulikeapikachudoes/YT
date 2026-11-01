// node snap.js <index.html> <outdir> <t1,t2,...>  -> frames + errors.json
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const [file, out, ts] = process.argv.slice(2); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.setDefaultTimeout(30000); const kill = setTimeout(() => { console.log('snap timeout'); process.exit(3); }, 150000); const errs = []; p.on('pageerror', e => errs.push(String(e.message).slice(0, 300))); p.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|favicon/.test(m.text())) errs.push(m.text().slice(0, 300)); });
  await p.goto('file://' + file); await p.waitForTimeout(700);
  const missing = await p.evaluate(() => { try { return ORDER.filter(o => !S[o[0]]).map(o => o[0]); } catch (e) { return ['(page script did not run: ' + e.message + ')']; } }).catch(e => ['eval failed']);
  if (missing.length) errs.push('missing scenes: ' + missing.join(', '));
  const times = ts.split(',').map(Number);
  for (let i = 0; i < times.length; i++) { await p.evaluate(t => { window.__timelines.main.seek(t); return 1; }, times[i]).catch(e => errs.push('seek: ' + e.message));
    await p.screenshot({ path: `${out}/frame-${String(i).padStart(2, '0')}.png` }); }
  fs.writeFileSync(out + '/errors.json', JSON.stringify(errs)); clearTimeout(kill); await b.close(); })().catch(e => { require('fs').writeFileSync(process.argv[3] + '/errors.json', JSON.stringify(['snapshot crashed: ' + e.message])); process.exit(0); });
