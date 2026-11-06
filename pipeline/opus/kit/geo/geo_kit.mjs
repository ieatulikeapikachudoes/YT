// geo_kit.mjs <shotlist.json> <out geo.json>
// Projects everything a shot list refers to. No model involved. Errors go into geo.json "errors" so the
// shot-list loop can send them back to DeepSeek.
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import * as topo from "topojson-client";
import { geoConicConformal, geoPath, geoCentroid, geoBounds } from "d3-geo";
const HERE = path.dirname(fileURLToPath(import.meta.url));
const SL = JSON.parse(fs.readFileSync(process.argv[2]));
const world = JSON.parse(fs.readFileSync(path.join(HERE, "../../node_modules/world-atlas/countries-50m.json")));
const all = topo.feature(world, world.objects.countries).features;
const ALIAS = { "usa": "United States of America", "united states": "United States of America", "us": "United States of America", "uk": "United Kingdom",
  "czech republic": "Czechia", "bosnia": "Bosnia and Herz.", "north macedonia": "Macedonia", "south korea": "South Korea", "dr congo": "Dem. Rep. Congo" };
const byName = n => { const k = (ALIAS[n.toLowerCase()] || n).toLowerCase(); return all.find(f => f.properties.name.toLowerCase() === k); };
const errors = [];
const places = SL.places || {};
const [w, s, e, n] = SL.region.bbox;
const proj = geoConicConformal().parallels([s + (n - s) / 4, n - (n - s) / 4]).rotate([-(w + e) / 2, 0]);
proj.fitExtent([[40, 540], [1040, 1440]], { type: "MultiPoint", coordinates: [[w, s], [e, s], [e, n], [w, n]] });
proj.clipExtent([[-1500, -800], [2600, 3000]]);  // clip in screen space so huge countries cannot wrap over the frame
const gp = geoPath(proj);
const P = ll => proj(ll).map(v => +v.toFixed(1));
const out = { base: [], shapes: {}, pts: {}, kmpx: 0, errors };
// base map: every country that lands near the frame
const near = f => { const [[x0, y0], [x1, y1]] = geoBounds(f); if (x1 - x0 > 300) return true; return x1 > w - 25 && x0 < e + 25 && y1 > s - 15 && y0 < n + 15; };
for (const f of all) { if (f.properties.name === "Antarctica" || !near(f)) continue; const d = gp(f); if (d) out.base.push(d); }
const cx = (w + e) / 2, cy = (s + n) / 2; const a = P([cx, cy]), b = P([cx, cy + 100 / 111.2]);
out.kmpx = +(Math.hypot(a[0] - b[0], a[1] - b[1]) / 100).toFixed(4);
for (const [k, ll] of Object.entries(places)) {
  if (!Array.isArray(ll) || ll.length !== 2) { errors.push(`place "${k}" needs [lon, lat]`); continue; }
  if (ll[0] < w - 3 || ll[0] > e + 3 || ll[1] < s - 3 || ll[1] > n + 3) errors.push(`place "${k}" ${JSON.stringify(ll)} is outside region.bbox; fix its coordinates or the bbox`);
  out.pts[k] = P(ll);
}
// a shape ref is "Country" or "Country@Place" (the piece of that country nearest the place)
function shape(ref) {
  if (out.shapes[ref]) return true;
  const [cn, near] = ref.split("@");
  const f = byName(cn.trim());
  if (!f) { const sug = all.map(x => x.properties.name).filter(x => x.toLowerCase().startsWith(cn.trim().slice(0, 3).toLowerCase())).slice(0, 5);
    errors.push(`unknown country "${cn}"${sug.length ? ` (did you mean: ${sug.join(", ")})` : ""}`); return false; }
  let g = f.geometry;
  if (near) {
    const ll = places[near.trim()]; if (!ll) { errors.push(`"${ref}": place "${near}" is not in places`); return false; }
    const polys = g.type === "MultiPolygon" ? g.coordinates : [g.coordinates];
    let best = null, bd = 1e9;
    for (const pg of polys) { const c = geoCentroid({ type: "Polygon", coordinates: pg }); const d = Math.hypot(c[0] - ll[0], c[1] - ll[1]); if (d < bd) { bd = d; best = pg; } }
    g = { type: "Polygon", coordinates: best };
  }
  const feat = { type: "Feature", geometry: g };
  out.shapes[ref] = gp(feat);
  // focus point: centroid of the part of the shape inside the bbox
  const bb = geoBounds(feat);
  const c = (bb[1][0] - bb[0][0] > 40) ? [Math.min(Math.max(geoCentroid(feat)[0], w), e), Math.min(Math.max(geoCentroid(feat)[1], s), n)] : geoCentroid(feat);
  out.pts[ref] = P(c);
  return true;
}
const ref = r => { if (typeof r !== "string") return; if (places[r]) return; shape(r); };
const refs = (act) => {
  const one = ["target", "place", "from", "center", "focus"];
  for (const k of one) if (act[k]) ref(act[k]);
  for (const k of ["to", "through"]) if (Array.isArray(act[k])) act[k].forEach(r => { if (!places[r]) errors.push(`"${r}" in ${act.do}.${k} must be a place (add it to places)`); });
  if (act.do === "highlight" && act.country) ref(act.near ? `${act.country}@${act.near}` : act.country);
  for (const k of ["place", "from", "center"]) if (act[k] && !places[act[k]]) errors.push(`"${act[k]}" in ${act.do}.${k} must be a place (add it to places)`);
};
for (const sh of SL.shots || []) { if (sh.camera && sh.camera.focus) ref(sh.camera.focus); (sh.actions || []).forEach(refs); }
fs.writeFileSync(process.argv[3], JSON.stringify(out));
console.log(JSON.stringify({ errors: errors.length, shapes: Object.keys(out.shapes).length, places: Object.keys(places).length }));
