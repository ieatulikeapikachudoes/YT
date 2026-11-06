import fs from "fs";
import * as topo from "topojson-client";
import { geoConicConformal, geoPath } from "d3-geo";
const world = JSON.parse(fs.readFileSync("node_modules/world-atlas/countries-50m.json"));
const all = topo.feature(world, world.objects.countries).features;
const byId = id => all.find(f => +f.id === id);
const proj = geoConicConformal().parallels([20, 34]).rotate([-50, 0]);
// fit the Gulf theatre (Red Sea to Pakistan, Yemen to the Caspian) into the frame
proj.fitExtent([[40, 520], [1040, 1420]], { type: "MultiPoint", coordinates: [[37, 13], [62, 13], [62, 38], [37, 38]] });
const path = geoPath(proj);
const P = ll => proj(ll).map(v => +v.toFixed(1));
const line = pts => "M" + pts.map(P).map(p => p.join(" ")).join(" L");
const out = { countries: {}, cities: {}, lines: {} };
const keep = new Set([364, 368, 682, 414, 48, 634, 784, 512, 887, 400, 760, 792, 376, 818, 4, 586, 795, 232, 262, 729, 231, 706, 422, 51, 31, 268, 196, 275, 860, 398, 356, 434, 728]);
for (const f of all) if (keep.has(+f.id)) { const d = path(f); if (d) out.countries[f.id] = { name: f.properties.name, d }; }
const C = { tehran: [51.39, 35.69], isfahan: [51.67, 32.65], bandarabbas: [56.27, 27.18], jask: [57.77, 25.64], bushehr: [50.84, 28.97], chabahar: [60.64, 25.29], qeshm: [55.89, 26.82],
  kharg: [50.31, 29.23], raslaffan: [51.53, 25.92], rastanura: [50.16, 26.64], abqaiq: [49.68, 25.94], yanbu: [38.06, 24.09], riyadh: [46.68, 24.71], doha: [51.53, 25.29], udeid: [51.32, 25.12],
  dubai: [55.27, 25.2], kuwait: [47.98, 29.37], bahrain: [50.58, 26.22], sanaa: [44.19, 15.37], aden: [45.03, 12.8], hodeidah: [42.95, 14.8], mandab: [43.33, 12.58], hormuz: [56.4, 26.45], muscat: [58.4, 23.6],
  cv1: [59.4, 24.7], blkA: [58.9, 22.4], blkB: [62.2, 25.4], cv2: [61.0, 22.2], cv3: [59.3, 20.6], baghdad: [44.36, 33.31] };
for (const [k, ll] of Object.entries(C)) out.cities[k] = P(ll);
// shipping lane through the strait and the Saudi East-West pipeline
out.lines.lane = line([[50.6, 28.6], [52.5, 27.0], [54.6, 26.4], [56.0, 26.55], [56.55, 26.35], [57.0, 25.6], [58.3, 24.6], [60.5, 23.2]]);
out.lines.pipeline = line([[49.68, 25.94], [47.6, 25.0], [45.0, 24.5], [42.0, 24.2], [38.06, 24.09]]);
out.ir = path(byId(364));
fs.writeFileSync("geo.json", JSON.stringify(out));
console.log(out.cities, Object.keys(out.countries).length);
