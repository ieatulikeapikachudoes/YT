import fs from "fs";
import * as topo from "topojson-client";
import { geoConicConformal, geoPath } from "d3-geo";
const world = JSON.parse(fs.readFileSync("node_modules/world-atlas/countries-50m.json"));
const all = topo.feature(world, world.objects.countries).features;
const byId = id => all.find(f => +f.id === id);
const UA = 804, RU = 643;
const proj = geoConicConformal().parallels([45, 52]).rotate([-32, 0]);
proj.fitExtent([[60, 640], [1020, 1320]], byId(UA));
const path = geoPath(proj);
const P = ll => proj(ll).map(v => +v.toFixed(1));
const line = pts => "M" + pts.map(P).map(p => p.join(" ")).join(" L");
const out = { countries: {}, cities: {}, lines: {} };
const keep = new Set([804, 643, 112, 616, 440, 428, 233, 498, 642, 348, 703, 276, 203, 40, 100, 792, 268, 246, 752, 578, 208, 528, 56, 250, 380, 705, 191, 688, 70, 807, 8, 300, 51, 31, 398, 860, 795, 4, 364, 368, 760, 422, 376, 400, 196]);
for (const f of all) if (keep.has(+f.id)) { const d = path(f); if (d) out.countries[f.id] = { name: f.properties.name, d }; }
// approximate line of contact, autumn 2026 (from captured / contested towns in the research), north to south
const FRONT = [[37.75, 50.45], [37.7, 49.95], [37.68, 49.7], [37.8, 49.35], [37.92, 49.05], [37.98, 48.92], [37.82, 48.78], [37.78, 48.62], [37.7, 48.51], [37.45, 48.43], [37.05, 48.36], [36.88, 48.2], [36.78, 48.02], [36.6, 47.86], [36.3, 47.7], [35.95, 47.6], [35.62, 47.52], [35.32, 47.46], [35.08, 47.55], [34.6, 47.5], [34.05, 47.25], [33.45, 46.8], [32.65, 46.62], [31.9, 46.52]];
const EAST = [[31.4, 46.2], [31.4, 43.8], [41, 43.8], [41, 51.2], [37.75, 51.2]];
// hypothetical: the Kramatorsk-Sloviansk belt falls and the line is pushed west
const HYPO = [[37.3, 50.42], [37.05, 49.75], [36.75, 49.25], [36.35, 48.75], [36.05, 48.35], [35.75, 47.95], [35.45, 47.62], [35.08, 47.55]];
const close = pts => line(pts) + " Z";
out.lines.front = line(FRONT);
out.lines.occupied = close([...FRONT, ...EAST]);
out.lines.hypoFront = line(HYPO);
out.lines.hypo = close([...HYPO, [34.6, 47.5], [34.05, 47.25], [33.45, 46.8], [32.65, 46.62], [31.9, 46.52], ...EAST.map(p => p)]);
out.lines.hypoBand = close([...HYPO, ...FRONT.slice(0, 19).reverse()]);
out.lines.dnipro = line([[30.62, 51.45], [30.52, 50.45], [31.1, 49.95], [32.06, 49.44], [33.42, 49.07], [34.12, 48.78], [34.61, 48.51], [35.05, 48.46], [35.18, 48.1], [35.14, 47.84], [34.85, 47.62], [34.4, 47.57], [33.9, 47.2], [33.37, 46.75], [32.62, 46.64], [31.9, 46.55]]);
for (const [k, ll] of Object.entries({ kramatorsk: [37.56, 48.72], sloviansk: [37.61, 48.85], kostiantynivka: [37.71, 48.53], druzhkivka: [37.53, 48.62], pokrovsk: [37.18, 48.28], toretsk: [37.85, 48.4], siversk: [38.1, 48.87],
  kharkiv: [36.23, 49.99], zaporizhzhia: [35.14, 47.84], dnipro: [35.05, 48.46], kyiv: [30.52, 50.45], warsaw: [21.01, 52.23], vilnius: [25.28, 54.69], riga: [24.1, 56.95], tallinn: [24.75, 59.44], moscow: [37.62, 55.75], chisinau: [28.86, 47.01], minsk: [27.56, 53.9],
  border_kh: [36.55, 50.25] })) out.cities[k] = P(ll);
out.ua = path(byId(UA));
fs.writeFileSync("geo.json", JSON.stringify(out));
console.log(out.cities, Object.keys(out.countries).length);
