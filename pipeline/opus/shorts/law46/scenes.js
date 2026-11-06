/* ---------- Law 46 Weak Ties: local helpers ---------- */
const GYM = (x, y, s, o = {}) => PERSON(x, y, s, { shirt: "#ff8a3d", band: C.red, hair: "#3a2214", face: "happy", ...o });
const BRO = (x, y, s, col, o = {}) => PERSON(x, y, s, { shirt: col, hair: "#1a1430", ...o });
const CREWCOLS = [C.purple, "#ff5f8f", C.teal];
const GSTAMP = (id, x, y, t, s = 1, rot = -10) => `<g id="${id}" class="hid" transform="translate(${x} ${y}) rotate(${rot}) scale(${s})"><g class="in"><rect x="${-t.length * 34 - 30}" y="-62" width="${t.length * 68 + 60}" height="124" rx="16" fill="none" stroke="#3ddc84" stroke-width="14"/>${TXT(0, 34, t, 96, "#3ddc84", 900, 'letter-spacing="6"')}</g></g>`;
const PILL = (id, x, y, t, col = C.red, s = 1) => G(id, `<rect x="${-t.length * 17 - 34}" y="-44" width="${t.length * 34 + 68}" height="88" rx="44" fill="${col}"/>${TXT(0, 18, t, 52, "#fff", 900)}`, x, y, s, "hid");
const HEARTB = (x, y, mine = false) => `<g transform="translate(${x} ${y})"><rect x="0" y="-34" width="150" height="68" rx="30" fill="${mine ? C.cyan : "#3a3466"}"/><path transform="translate(75 -2) scale(0.42)" d="M0 40 C-70 -10 -60 -70 -20 -70 C-5 -70 0 -58 0 -50 C0 -58 5 -70 20 -70 C60 -70 70 -10 0 40 Z" fill="${C.red}"/></g>`;
const GROUPCHAT = () => `<rect width="352" height="692" fill="#120f2c"/><rect width="352" height="96" fill="#1d1846"/>
  ${[0, 1, 2].map(i => `<circle cx="${40 + i * 26}" cy="52" r="22" fill="${CREWCOLS[i]}" stroke="#1d1846" stroke-width="4"/>`).join("")}<text x="130" y="62" font-family="Geist" font-weight="800" font-size="28" fill="#fff">the boys</text>
  <g id="gc-mine"><rect x="96" y="130" width="236" height="74" rx="30" fill="${C.cyan}"/><text x="214" y="176" text-anchor="middle" font-family="Geist" font-weight="700" font-size="26" fill="#0e1530">got laid off today</text></g>
  <g class="gc-h">${HEARTB(20, 260)}</g><g class="gc-h">${HEARTB(20, 340)}</g><g class="gc-h">${HEARTB(20, 420)}</g>
  <g class="gc-h"><rect x="20" y="466" width="250" height="68" rx="30" fill="#3a3466"/><text x="145" y="510" text-anchor="middle" font-family="Geist" font-weight="700" font-size="26" fill="#fff">praying for u bro</text></g>
  <g class="gc-h">${HEARTB(20, 590)}</g>`;
const OFFER = () => `<rect width="352" height="692" fill="#0f2a22"/><circle cx="176" cy="250" r="96" fill="#3ddc84"/><path d="M128 250 L162 284 L226 214" fill="none" stroke="#fff" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="176" y="420" text-anchor="middle" font-family="Geist" font-weight="900" font-size="48" fill="#fff">OFFER</text><rect x="70" y="460" width="212" height="18" rx="9" fill="#2f6a55"/><rect x="100" y="496" width="152" height="18" rx="9" fill="#2f6a55"/>`;
const LINKSCREEN = () => `<rect width="352" height="692" fill="#120f2c"/><rect width="352" height="96" fill="#1d1846"/><circle cx="46" cy="52" r="26" fill="#ff8a3d"/><text x="84" y="62" font-family="Geist" font-weight="800" font-size="26" fill="#fff">gym guy</text>
  <g id="t1-msg" class="hid"><rect x="20" y="140" width="300" height="190" rx="28" fill="#3a3466"/><rect x="40" y="160" width="260" height="96" rx="14" fill="#2b2068"/><g transform="translate(170 208)"><rect x="-56" y="-18" width="62" height="36" rx="18" fill="none" stroke="${C.cyan}" stroke-width="9"/><rect x="-6" y="-18" width="62" height="36" rx="18" fill="none" stroke="${C.cyan}" stroke-width="9"/></g>
  <text x="40" y="300" font-family="Geist" font-weight="700" font-size="26" fill="#fff">they're hiring. apply</text></g>`;
const BUILDING = (x, y, s = 1) => `<g transform="translate(${x} ${y}) scale(${s})"><rect x="-150" y="-620" width="300" height="620" fill="#2a2466"/>${Array.from({ length: 24 }, (_, i) => `<rect x="${-120 + (i % 4) * 66}" y="${-590 + Math.floor(i / 4) * 96}" width="40" height="58" fill="${i % 5 ? "#3f3a8a" : "#ffd23f"}" opacity="0.8"/>`).join("")}</g>`;
const PAPERS = (id, x, y, n = 14) => `<g id="${id}" transform="translate(${x} ${y})"><g class="in">${Array.from({ length: n }, (_, i) => `<g transform="translate(${(i % 2 ? 8 : -8)} ${-i * 38})"><rect x="-150" y="-34" width="300" height="34" rx="4" fill="#fbf7ec" stroke="#c9c3d9" stroke-width="3"/><rect x="-120" y="-24" width="${120 + (i * 37) % 100}" height="8" rx="4" fill="#c9c3d9"/></g>`).join("")}</g></g>`;
const CAL = (id, x, y, n, s = 1) => G(id, `<rect x="-130" y="-150" width="260" height="290" rx="22" fill="#fbf7ec"/><rect x="-130" y="-150" width="260" height="70" rx="22" fill="${C.red}"/><rect x="-130" y="-100" width="260" height="20" fill="${C.red}"/>
  <circle cx="-70" cy="-150" r="12" fill="#888"/><circle cx="70" cy="-150" r="12" fill="#888"/>${TXT(0, 70, n, 130, "#0e1530")}${TXT(0, 125, "months", 38, "#6a6890", 800)}`, x, y, s);
const DUMBBELL = (x, y, s = 1, rot = 0) => `<g transform="translate(${x} ${y}) rotate(${rot}) scale(${s})"><rect x="-90" y="-10" width="180" height="20" rx="8" fill="#8a8fb5"/><rect x="-120" y="-44" width="34" height="88" rx="10" fill="#3a3466"/><rect x="86" y="-44" width="34" height="88" rx="10" fill="#3a3466"/><rect x="-146" y="-32" width="28" height="64" rx="10" fill="#4a4480"/><rect x="118" y="-32" width="28" height="64" rx="10" fill="#4a4480"/></g>`;
const CASH = (id, x, y, n = 8, s = 1) => G(id, Array.from({ length: n }, (_, i) => `<g transform="translate(${(i % 2 ? 6 : -6)} ${-i * 26})"><rect x="-110" y="-24" width="220" height="48" rx="6" fill="#3ddc84" stroke="#1f8a52" stroke-width="5"/><circle r="15" fill="#1f8a52"/></g>`).join(""), x, y, s);
const BADGE = (x, y) => `<g transform="translate(${x} ${y})"><path d="M-30 -120 L0 -40 L30 -120" fill="none" stroke="${C.red}" stroke-width="8"/><rect x="-40" y="-44" width="80" height="100" rx="10" fill="#fff"/><rect x="-26" y="-28" width="52" height="40" rx="6" fill="${C.cyan}"/><rect x="-26" y="22" width="52" height="8" rx="4" fill="#c9c3d9"/></g>`;
const WORLD = (id, x, y, r, col, inner = "", cls = "") => `<g id="${id}" class="${cls}" transform="translate(${x} ${y})"><g class="in"><circle r="${r}" fill="${col}" opacity="0.22"/><circle r="${r}" fill="none" stroke="${col}" stroke-width="8" opacity="0.8"/>${inner}</g></g>`;
const MINI = (x, y, col, s = 0.42, o = {}) => PERSON(x, y, s, { shirt: col, ...o });
const JOBCARD = (x, y, col = C.cyan) => `<g transform="translate(${x} ${y})"><rect x="-62" y="-46" width="124" height="92" rx="14" fill="#fbf7ec" stroke="${col}" stroke-width="7"/>${CASE(0, 34, 0.42, false)}</g>`;
const DOOR = (id, x, y, s = 1) => `<g id="${id}" transform="translate(${x} ${y}) scale(${s})"><rect x="-60" y="-170" width="120" height="170" rx="8" fill="#fff3b0"/><g class="in"><rect x="-60" y="-170" width="120" height="170" rx="8" fill="#8a5a2a"/><circle cx="36" cy="-80" r="9" fill="${C.gold}"/></g></g>`;
const MESH = (pts, col = "#c9c3e9") => { let s = ""; for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++) s += `<path d="M${pts[i][0]} ${pts[i][1]} L${pts[j][0]} ${pts[j][1]}" stroke="${col}" stroke-width="4" opacity="0.5"/>`; return s; };
const GHOST = (x, y, s = 1) => `<g transform="translate(${x} ${y}) scale(${s})"><path d="M-70 -150 L-70 -330 Q-70 -340 -40 -340 L40 -340 Q70 -340 70 -330 L70 -150 Z M-44 0 L-44 -170 M44 0 L44 -170" fill="none" stroke="#c9c3e9" stroke-width="7" stroke-dasharray="14 12"/><circle cx="0" cy="-405" r="64" fill="none" stroke="#c9c3e9" stroke-width="7" stroke-dasharray="14 12"/></g>`;
const STAR = (id, x, y, s = 1) => G(id, `<path d="M0 -80 L22 -26 L80 -24 L34 12 L50 70 L0 36 L-50 70 L-34 12 L-80 -24 L-22 -26 Z" fill="${C.gold}" stroke="#fff" stroke-width="7" stroke-linejoin="round"/>`, x, y, s, "hid");

/* ---------- scenes ---------- */
const S = {};
S.hk = [BG.day, `${STARS(26)}${GLOW(320, 760, 300, C.red, 0.18)}${GLOW(790, 900, 320, "#3ddc84", 0.0)}${GROUND(1310)}
  ${PHONEBOX("hk-chat", 540, 780, 1.1, GROUPCHAT())}
  <g id="hk-right" class="hid">${GLOW(720, 760, 320, "#3ddc84", 0.32)}${GYM(630, 1310, 1.4, { id: "hk-gym", pose: "wave" })}</g>
  ${PHONEBOX("hk-offer", 845, 555, 0.5, OFFER(), "hid")}`];
S.r1 = [BG.warm, `${STARS(30)}${GLOW(540, 820, 520, C.gold, 0.3)}${GROUND(1310, "#2a1d5a")}
  ${BRO(170, 1310, 1.3, CREWCOLS[0], { id: "r1-b0", face: "joy", pose: "up" })}${BRO(910, 1310, 1.3, CREWCOLS[2], { id: "r1-b2", face: "joy", pose: "up", cap: "#1a7a70" })}
  ${BRO(720, 1310, 1.4, CREWCOLS[1], { id: "r1-b1", face: "happy", pose: "hugR" })}${YOU(390, 1310, 1.45, { id: "r1-you", face: "joy", pose: "hugL" })}`];
S.f1 = [BG.dark, `${STARS(16, 500)}${BUILDING(820, 1310, 1.0)}${GROUND(1310, "#141130")}
  ${YOU(430, 1310, 1.7, { id: "f1-you", face: "sad", pose: "hold" })}<g id="f1-box">${BOX(430, 1060, 1.4)}</g>
  ${STAMP("f1-stamp", 540, 360, "LAID OFF", 0.95, -7)}`];
S.f2 = [BG.dark, `${GLOW(540, 800, 420, C.purple, 0.3)}${PHONEBOX("f2-chat", 540, 790, 1.12, GROUPCHAT())}${PILL("f2-zero", 540, 1290, "0 leads", C.red, 1.2)}`];
S.f3 = [BG.dark, `${STARS(14, 500)}${GROUND(1310, "#141130")}${GLOW(360, 900, 300, C.purple, 0.25)}
  ${PAPERS("f3-papers", 330, 1300, 16)}<g id="f3-200" class="hid"><g class="in">${TXT(330, 640, "200", 120, C.gold)}</g></g>${CAL("f3-cal", 790, 470, "3", 0.95)}
  ${YOU(790, 1310, 1.45, { id: "f3-you", face: "sad", pose: "down" })}${XMARK("f3-x", 360, 900, 2.2)}`];
S.t1 = [BG.day, `${STARS(20)}
  ${GROUND(1310)}${GLOW(280, 900, 300, "#ff8a3d", 0.22)}${GYM(280, 1310, 1.55, { id: "t1-gym", pose: "phone" })}
  ${YOU(800, 1310, 1.55, { id: "t1-you", face: "neutral", pose: "phone" })}
  <g id="t1-two" class="hid"><g class="in">${TXT(540, 640, "×2", 120, C.gold)}</g></g>
  ${PHONEBOX("t1-phone", 790, 420, 0.45, LINKSCREEN(), "hid")}<g id="t1-fly" class="hid" transform="translate(400 700)"><g class="in"><circle r="62" fill="${C.cyan}"/><g transform="scale(1.1)"><rect x="-44" y="-14" width="48" height="28" rx="14" fill="none" stroke="#0e1530" stroke-width="8"/><rect x="-4" y="-14" width="48" height="28" rx="14" fill="none" stroke="#0e1530" stroke-width="8"/></g></g></g>`];
S.t2 = [BG.warm, `${STARS(30)}${GLOW(470, 820, 480, "#3ddc84", 0.28)}${GROUND(1310, "#2a1d5a")}
  ${YOU(420, 1310, 1.7, { id: "t2-you", face: "joy", pose: "up", tie: C.navy })}<g id="t2-badge" class="hid">${BADGE(420, 1050)}</g>
  ${CASH("t2-cash", 790, 1290, 12, 1.0)}${GSTAMP("t2-hired", 560, 340, "HIRED", 1.05)}`];
S.g1 = [BG.holy, `${RAYS("g1-rays", 540, 560, 18, 1300)}${GLOW(540, 600, 360, C.gold, 0.45)}
  ${PERSON(540, 1330, 1.7, { id: "g1-pr", shirt: C.purple, pants: C.purple, robe: "#5a3fd6", hair: "#14102a", face: "fierce", pose: "preach" })}${PULPIT(540, 1330, 1.35)}
  ${TABLET("g2-tab", 540, 770, 1.15)}`];
const CREWPTS = [[540, 860], [380, 700], [700, 700], [380, 1020], [700, 1020]];
S.m1 = [BG.day, `${STARS(24)}${WORLD("m1-world", 540, 860, 380, C.purple, `${MESH(CREWPTS.map(([x, y]) => [x - 540, y - 860 - 90]))}`)}
  ${CREWPTS.map(([x, y], i) => i ? MINI(x, y, [C.purple, "#ff5f8f", C.teal, "#ffb13d"][i - 1], 0.45, { id: `m1-p${i}`, face: "happy" }) : MINI(x, y, C.cyan, 0.55, { id: "m1-you", face: "neutral" })).join("")}
  <g id="m1-jobs" class="hid"><g class="in">${JOBCARD(330, 420)}${JOBCARD(540, 380)}${JOBCARD(750, 420)}</g></g>`];
S.m2 = [BG.day, `${STARS(28)}
  ${WORLD("m2-left", 270, 900, 230, C.purple, `${MINI(0, 60, C.cyan, 0.4)}${MINI(-110, 0, C.purple, 0.32)}${MINI(110, 0, "#ff5f8f", 0.32)}`)}
  ${WORLD("m2-right", 720, 640, 210, C.gold, `${DOOR("m2-d1", -90, 80, 0.8)}${DOOR("m2-d2", 75, 40, 0.95)}${DOOR("m2-d3", 0, 190, 0.6)}`, "hid")}
  <path id="m2-bridge" d="M410 820 Q540 770 600 770" pathLength="1" fill="none" stroke="#ff8a3d" stroke-width="12" stroke-dasharray="1" stroke-dashoffset="1" stroke-linecap="round"/>
  ${GYM(560, 1330, 1.1, { id: "m2-gym", pose: "up" })}`];
S.p1 = [BG.day, `${STARS(20)}
  <g id="p1-clip"><g class="in"><rect x="300" y="300" width="480" height="300" rx="26" fill="#fbf7ec"/><rect x="460" y="280" width="160" height="50" rx="14" fill="#8a8fb5"/>${TXT(540, 460, "282", 130, "#0e1530")}${TXT(540, 540, "workers", 48, "#6a6890", 800)}</g></g>
  ${[0, 1, 2, 3, 4, 5].map(i => MINI(190 + i * 140, 1260, i ? "#8a8fb5" : C.red, 0.58, { id: `p1-m${i}`, face: i ? "neutral" : "happy" })).join("")}
  ${HEART("p1-heart", 190, 900, 0.85)}${PILL("p1-one", 540, 760, "1 in 6", C.gold, 1.3)}`];
S.p2 = [BG.day, `${STARS(18)}
  <path d="M130 1100 L880 1100 M130 1100 L130 420" stroke="#c9c3e9" stroke-width="8" stroke-linecap="round"/>
  <path id="p2-curve" d="M160 1080 C320 1080 380 520 510 520 C640 520 700 1080 860 1080" pathLength="1" fill="none" stroke="${C.cyan}" stroke-width="14" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/>
  <g id="p2-l">${GHOST(220, 1320, 0.5)}</g>${XMARK("p2-lx", 220, 1200, 0.9)}
  <g id="p2-r">${BRO(800, 1320, 0.5, "#ff5f8f", { face: "happy" })}</g>${HEART("p2-rh", 800, 1050, 0.6)}${XMARK("p2-rx", 800, 1200, 0.9)}
  <g id="p2-m">${GYM(510, 1320, 0.55, { face: "happy" })}</g>
  ${STAR("p2-star", 510, 520, 1.0)}${TXT(250, 1010, "distant", 64, "#c9c3e9", 900)}${TXT(770, 980, "close", 64, "#c9c3e9", 900)}<g id="p2-glow" class="hid">${GLOW(510, 1200, 140, C.gold, 0.5)}</g>`];
S.o1 = [BG.warm, `${STARS(26)}${GROUND(1310, "#2a1d5a")}${GLOW(290, 900, 280, "#ff5f8f", 0.25)}
  ${BRO(200, 1310, 0.95, CREWCOLS[0], { face: "happy" })}${BRO(390, 1310, 0.95, CREWCOLS[2], { face: "happy", cap: "#1a7a70" })}${HEART("o1-heart", 295, 620, 1.1)}
  <path d="M560 520 L560 1300" stroke="#fff" stroke-width="4" stroke-dasharray="12 14" opacity="0.4"/>
  ${YOU(770, 1310, 1.4, { id: "o1-you", face: "smug", pose: "phone" })}
  <g id="o1-msg" class="hid"><g class="in"><rect x="530" y="400" width="320" height="110" rx="40" fill="${C.cyan}"/><circle cx="600" cy="455" r="34" fill="#ff8a3d"/><circle cx="600" cy="448" r="18" fill="${C.skin}"/><path d="M580 438 L620 438" stroke="${C.red}" stroke-width="7"/>${TXT(720, 472, "yo!", 54, "#0e1530")}</g></g>`];
S.e1 = [BG.day, `${STARS(30)}
  ${WORLD("e1-l", 540, 590, 240, "#ff5f8f", `${MINI(-90, 130, C.purple, 0.4)}${MINI(90, 130, C.teal, 0.4)}${MINI(0, 160, C.cyan, 0.46)}${HEART("e1-h", 0, -110, 1.3)}`)}
  ${WORLD("e1-r", 540, 1090, 220, C.gold, `${MESH([[-150, 60], [-60, -120], [100, -140], [160, 40], [40, 130]], "#ffd23f")}${[[-150, 60], [-60, -120], [100, -140], [160, 40], [40, 130]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="24" fill="#ffd23f"/>`).join("")}`)}
  <g id="e1-arrow" class="hid" transform="translate(860 1090)"><g class="in"><path d="M0 90 L0 -80 M-60 -20 L0 -80 L60 -20" fill="none" stroke="${C.gold}" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/></g></g>`];
S.e2 = [BG.warm, `${STARS(34)}${GLOW(540, 860, 480, C.gold, 0.3)}${GROUND(1310, "#2a1d5a")}
  ${WORLD("e2-l", 290, 540, 150, "#ff5f8f", `${HEART("", 0, 10, 1.0)}`)}${WORLD("e2-r", 790, 540, 150, C.gold, `<path d="M0 70 L0 -60 M-55 -5 L0 -60 L55 -5" fill="none" stroke="${C.gold}" stroke-width="24" stroke-linecap="round" stroke-linejoin="round"/>`)}
  <path d="M360 680 Q430 760 470 820 M720 680 Q650 760 610 820" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-dasharray="4 18" opacity="0.8"/>
  ${YOU(540, 1310, 1.4, { id: "e2-you", face: "joy", pose: "up" })}`];
const ORDER = [["hk", "hk"], ["r1", "r1"], ["f1", "f1"], ["f2", "f2"], ["f3", "f3"], ["t1", "t1"], ["t2", "t2"], ["g1", "g1"], ["m1", "m1"], ["m2", "m2"], ["p1", "p1"], ["p2", "p2"], ["o1", "o1"], ["e1", "e1"], ["e2", "e2"]];
const HARD = ["r1", "f1", "g1", "p1", "e1"];
