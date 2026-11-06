/* ---------- scenes ---------- */
const S = {};
const hookScenes = {
 A: [BG.night, `${STARS(40, 700)}${MOON(860, 360, 70)}${GLOW(540, 1050, 380, C.red, 0.18)}
   <path d="M-100 1320 L1180 1320 L1180 2000 L-100 2000 Z" fill="#26224e"/><path d="M-100 1420 L1180 1420" stroke="#ffd23f" stroke-width="10" stroke-dasharray="70 60" opacity="0.6"/>
   ${CAR("hA-car", 520, 1300, 2.6, true)}${SMOKE("hA-smoke", 180, 1060, 1.5)}${HAZARD("hA-haz", 900, 1200, 0.9)}
   ${PHONEBOX("hA-phone", 540, 760, 0.95, STORY(), "hid")}`],
 B: [BG.day, `${STARS(26)}${GLOW(540, 820, 420, C.gold, 0.2)}${IOU("hB-iou", 540, 830, 1.15)}${STAMP("hB-void", 540, 760, "VOID", 1.4)}`],
 C: [BG.day, `${STARS(26)}${GLOW(330, 900, 300, C.cyan, 0.2)}${GROUND(1310)}
   ${YOU(330, 1310, 1.75, { id: "hC-you", face: "neutral" })}${YOU(330, 1310, 1.75, { id: "hC-yousad", face: "sad", pose: "shrug", cls: "hid" })}
   ${HIM(760, 1310, 1.75, { id: "hC-him", face: "happy" })}
   <g id="hC-ghost" class="hid" transform="translate(760 1310) scale(1.75)"><g class="in"><path d="M-70 -150 L-70 -330 Q-70 -340 -40 -340 L40 -340 Q70 -340 70 -330 L70 -150 Z M-44 0 L-44 -170 M44 0 L44 -170" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="14 12" opacity="0.7"/><circle cx="0" cy="-405" r="64" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="14 12" opacity="0.7"/></g></g>`],
};
S.hk = hookScenes[VERSION];
S.r1 = [BG.warm, `${STARS(30)}${GLOW(540, 820, 460, C.gold, 0.28)}${GROUND(1310, "#2a1d5a")}
  ${YOU(390, 1310, 1.75, { id: "r1-you", face: "happy", pose: "hold" })}${HIM(700, 1310, 1.75, { id: "r1-him", face: "joy", pose: "wave" })}
  ${HEART("r1-h1", 540, 420, 1.1)}`];
S.r2 = [BG.warm, `${STARS(24)}
  <g id="r2-c1" class="hid"><g class="in"><rect x="120" y="290" width="840" height="300" rx="40" fill="#2b2068" stroke="${C.cyan}" stroke-width="6"/>${BOX(380, 530, 1.25)}${BOX(540, 530, 1.25)}${BOX(460, 395, 1.1)}${TXT(780, 480, "×2", 120, C.gold)}</g></g>
  <g id="r2-c2" class="hid"><g class="in"><rect x="120" y="640" width="840" height="300" rx="40" fill="#1a1846" stroke="${C.cyan}" stroke-width="6"/>${MOON(260, 730, 46)}${CAR("", 440, 890, 1.0, false)}${CLOCK(780, 790, 95)}${TXT(780, 925, "5:00", 52, C.gold)}</g></g>
  <g id="r2-c3" class="hid"><g class="in"><rect x="120" y="990" width="840" height="300" rx="40" fill="#2b2068" stroke="${C.cyan}" stroke-width="6"/>${CASE(540, 1190, 1.2)}</g></g>`];
S.r3 = [BG.warm, `${STARS(30)}${GLOW(540, 800, 520, C.gold, 0.35)}${GROUND(1310, "#2a1d5a")}
  ${YOU(470, 1310, 1.8, { id: "r3-you", face: "happy", pose: "hugL" })}${HIM(640, 1310, 1.8, { id: "r3-him", face: "joy", pose: "hugR" })}
  ${HEART("r3-h1", 330, 520, 0.8)}${HEART("r3-h2", 770, 450, 1.0)}${HEART("r3-h3", 560, 330, 1.3)}`];
S.f1 = [BG.dark, `${STARS(20, 600)}${GLOW(540, 1000, 380, C.red, 0.16)}${GROUND(1320, "#141130")}
  ${CAR("f1-car", 470, 1320, 2.2, true, "#9a6a4a")}${SMOKE("f1-smoke", 200, 1080, 1.3)}
  ${PHONEBOX("f1-phone", 560, 720, 0.85, CHAT(), "hid")}`];
S.f2 = [BG.dark, `${GLOW(540, 800, 460, C.purple, 0.3)}${PHONEBOX("f2-phone", 540, 820, 1.2, STORY())}`];
S.f3 = [BG.dark, `${GROUND(1310, "#100e26")}<g id="f3-rain">${Array.from({ length: 38 }, () => { const x = rnd() * 1180 - 50, y = rnd() * 1500 + 150; return `<path d="M${x.toFixed(0)} ${y.toFixed(0)} l-14 46" stroke="#8a8fd5" stroke-width="4" opacity="0.45" stroke-linecap="round"/>`; }).join("")}</g>
  ${GLOW(540, 900, 260, "#4f5cff", 0.18)}${YOU(540, 1310, 2.05, { id: "f3-you", face: "sad", pose: "down" })}`];
S.g1 = [BG.holy, `${RAYS("g1-rays", 540, 560, 18, 1300)}${GLOW(540, 600, 360, C.gold, 0.45)}
  ${PERSON(540, 1330, 1.7, { id: "g1-pr", shirt: C.purple, pants: C.purple, robe: "#5a3fd6", hair: "#14102a", face: "fierce", pose: "preach" })}${PULPIT(540, 1330, 1.35)}
  ${TABLET("g2-tab", 540, 770, 1.15)}`];
S.m1 = [BG.day, `${STARS(26)}${GROUND(1310)}${GLOW(820, 760, 300, C.cyan, 0.3)}
  ${ARROWR("m1-back", 210, 760, 0.85, "#6a6890", "hid")}<g id="m1-backflip" transform="translate(210 760) scale(-1 1)"></g>${XMARK("m1-x", 210, 760, 1.2)}
  ${ARROWR("m1-fwd", 850, 760, 0.85, C.cyan, "hid")}${HIM(520, 1310, 1.75, { id: "m1-him", face: "smug", pose: "point" })}`];
S.m2 = [BG.day, `${STARS(24)}${GROUND(1310)}${GLOW(820, 900, 330, C.gold, 0.38)}
  <rect x="690" y="1150" width="260" height="160" rx="14" fill="#4a3a8c"/>${BOSS(820, 1150, 1.5, { id: "m2-boss", pose: "cross" })}
  ${YOU(190, 1310, 1.05, { id: "m2-you", face: "sad" })}
  <g id="m2-crowd">${[0, 1, 2, 3, 4].map(i => PERSON(330 + (i % 3) * 70, 1310 - (i > 2 ? 0 : 30), 0.62, { id: `m2-p${i}`, shirt: [C.teal, C.purple, C.red, "#ff8a3d", C.cyan][i] })).join("")}</g>`];
S.m3 = [BG.day, `${STARS(24)}${GLOW(540, 760, 420, C.purple, 0.25)}
  <path d="M540 700 L540 1290 M420 1300 L660 1300" stroke="#c9c3e9" stroke-width="26" stroke-linecap="round"/><path d="M500 700 L540 640 L580 700 Z" fill="#c9c3e9"/>
  <g id="m3-beam"><path d="M210 700 L870 700" stroke="#e9e5ff" stroke-width="22" stroke-linecap="round"/></g>
  <g id="m3-left"><g transform="translate(210 700)"><path d="M0 0 L-120 320 M0 0 L120 320" stroke="#c9c3e9" stroke-width="5"/><path d="M-150 320 Q0 380 150 320 Z" fill="#c9c3e9"/>
    <g id="m3-favs">${BOX(-60, 318, 0.75)}${CLOCK(55, 268, 46)}${CASE(10, 230, 0.5, false)}</g></g></g>
  <g id="m3-right"><g transform="translate(870 700)"><path d="M0 0 L-120 320 M0 0 L120 320" stroke="#c9c3e9" stroke-width="5"/><path d="M-150 320 Q0 380 150 320 Z" fill="#c9c3e9"/>
    ${GLOW(0, 160, 160, C.gold, 0.4)}${BOSS(0, 325, 0.62, { pose: "cross" })}</g></g>
  ${STAMP("m3-spent", 215, 880, "SPENT", 0.72, -12)}`];
S.o1 = [BG.day, `${STARS(26)}${GROUND(1310)}
  <g id="o1-pile" opacity="0.55">${BOX(160, 1300, 0.9)}${BOX(270, 1300, 0.9)}${CASE(215, 1200, 0.55, false)}</g>
  ${YOU(560, 1310, 1.8, { id: "o1-point", face: "neutral", pose: "point", flip: true })}
  ${YOU(470, 1310, 1.8, { id: "o1-show", face: "happy", pose: "hold", cls: "hid" })}${GLOW(760, 760, 300, C.cyan, 0.35)}${CHART("o1-chart", 760, 800, 1.0)}`];
S.o2 = [BG.warm, `${STARS(30)}${GROUND(1310, "#2a1d5a")}${GLOW(330, 900, 320, C.gold, 0.3)}
  ${YOU(330, 1310, 1.75, { id: "o2-you", face: "smug", pose: "cross" })}${CHIPS("o2-chips", 330, 1250, 1.0)}
  ${PHONEBOX("o2-phone", 790, 760, 0.6, `<rect width="352" height="692" fill="#1d1846"/>${AVATAR(176, 260, 90)}<text x="176" y="420" text-anchor="middle" font-family="Geist" font-weight="800" font-size="38" fill="#fff">him</text><text x="176" y="466" text-anchor="middle" font-family="Geist" font-weight="600" font-size="26" fill="#8a8fb5">calling...</text><circle cx="96" cy="600" r="44" fill="${C.red}"/><circle cx="256" cy="600" r="44" fill="#3ddc84"/>`, "hid")}
  ${RING("o2-ring", 790, 760, 0.95)}`];
S.e1 = [BG.day, `${STARS(24)}${GLOW(540, 820, 400, C.purple, 0.25)}${IOU("e1-iou", 540, 820, 1.05)}`];
S.e2 = [BG.day, `${STARS(30)}${GLOW(540, 900, 420, C.cyan, 0.3)}
  <g transform="translate(540 1000)"><path d="M-380 0 A380 380 0 0 1 380 0" fill="none" stroke="url(#dial)" stroke-width="70" stroke-linecap="round"/>
  ${Array.from({ length: 11 }, (_, i) => { const a = Math.PI * (1 - i / 10); return `<path d="M${300 * Math.cos(a)} ${-300 * Math.sin(a)} L${270 * Math.cos(a)} ${-270 * Math.sin(a)}" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity="0.8"/>`; }).join("")}
  <g id="e2-needle" transform="rotate(-80)"><path d="M-14 0 L0 -330 L14 0 Z" fill="#fff"/></g><circle r="40" fill="#fff"/><circle r="18" fill="${C.ink}"/></g>
  ${YOU(540, 1330, 0.68, { id: "e2-you", face: "smug", pose: "cross" })}`];

const ORDER = [["hk", "hk"], ["r1", "r1"], ["r2", "r2"], ["r3", "r3"], ["f1", "f1"], ["f2", "f2"], ["f3", "f3"], ["g1", "g1"], ["m1", "m1"], ["m2", "m2"], ["m3", "m3"], ["o1", "o1"], ["o2", "o2"], ["e1", "e1"], ["e2", "e2"]];
const HARD = ["r1", "f1", "f3", "g1", "e1"];
