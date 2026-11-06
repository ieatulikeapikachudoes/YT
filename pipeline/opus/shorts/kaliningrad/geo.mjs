// Baltic theatre: Poland, Kaliningrad, Lithuania, Belarus. Writes geo.json for template.html.
import fs from "fs";
import * as topo from "topojson-client";
import { geoConicConformal, geoPath } from "d3-geo";
const world = JSON.parse(fs.readFileSync("../../node_modules/world-atlas/countries-50m.json"));
const all = topo.feature(world, world.objects.countries).features;
const byId = id => all.find(f => +f.id === id);
const proj = geoConicConformal().parallels([50, 58]).rotate([-22, 0]);
// fit the frame to the theatre: Germany/Denmark to Belarus, Slovakia to Estonia
proj.fitExtent([[40, 540], [1040, 1440]], { type: "MultiPoint", coordinates: [[13.5, 48.5], [30.5, 48.5], [30.5, 60], [13.5, 60]] });
const path = geoPath(proj);
const P = ll => proj(ll).map(v => +v.toFixed(1));
const line = pts => "M" + pts.map(P).map(p => p.join(" ")).join(" L");
const out = { countries: {}, cities: {}, lines: {} };
const keep = new Set([616, 440, 428, 233, 112, 643, 276, 752, 246, 208, 804, 203, 703, 578, 348, 40, 498, 642, 528, 56, 756, 380, 705, 191, 807, 100, 688]);
for (const f of all) if (keep.has(+f.id)) { const d = path(f); if (d) out.countries[f.id] = { name: f.properties.name, d }; }
// Kaliningrad: the polygon of the Russia multipolygon that sits between Poland and Lithuania
const ru = byId(643);
const polys = ru.geometry.type === "MultiPolygon" ? ru.geometry.coordinates : [ru.geometry.coordinates];
const kal = polys.find(pg => { const [x, y] = pg[0][0]; return x > 19 && x < 23.5 && y > 54 && y < 55.5; });
out.kal = path({ type: "Polygon", coordinates: kal });
out.pl = path(byId(616)); out.lt = path(byId(440)); out.lv = path(byId(428)); out.ee = path(byId(233)); out.by = path(byId(112));
const C = { warsaw: [21.01, 52.23], kalcity: [20.51, 54.71], sepopol: [21.01, 54.27], suwalki: [22.93, 54.11], vilnius: [25.28, 54.69], minsk: [27.56, 53.9],
  grodno: [23.83, 53.68], riga: [24.1, 56.95], tallinn: [24.75, 59.44], olsztyn: [20.48, 53.78], bialystok: [23.16, 53.13], gotland: [18.5, 57.5], berlin: [13.4, 52.52],
  kalcenter: [21.3, 54.75], bycenter: [27.0, 53.3], gapmid: [23.2, 54.2], baltmid: [25.5, 57.3], moscowdir: [30.5, 55.8], stockholm: [18.07, 59.33] };
for (const [k, ll] of Object.entries(C)) out.cities[k] = P(ll);
// the Poland-Lithuania border, Kaliningrad tripoint to Belarus tripoint (approximate)
out.lines.gap = line([[22.79, 54.36], [22.95, 54.41], [23.1, 54.3], [23.28, 54.25], [23.47, 54.17], [23.5, 54.05], [23.52, 53.95]]);
// two pincers that would close it (hypothetical, for the "close it" beat)
out.lines.pincerN = line([[21.8, 54.6], [22.5, 54.45], [23.0, 54.3]]);
out.lines.pincerS = line([[24.6, 53.75], [23.9, 54.0], [23.35, 54.2]]);
// the land link: Warsaw up through the gap to Riga and Tallinn
out.lines.border = line([[20.55, 54.36], [20.8, 54.37], [21.05, 54.345], [21.3, 54.33], [21.5, 54.32]]);
out.lines.link = line([[21.01, 52.23], [22.0, 53.2], [22.93, 54.11], [23.4, 54.6], [24.5, 55.6], [24.1, 56.95], [24.75, 59.44]]);
fs.writeFileSync("geo.json", JSON.stringify(out));
console.log(out.cities, Object.keys(out.countries).length, "kal", !!kal);
