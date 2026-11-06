/* ---------- Law 46 Weak Ties: beats ---------- */
tl.set("#p1-heart, #o1-heart, #e1-h", { opacity: 0 }, 0);
tl.set("#cam-hk", { scale: 1.0 }, 0);
/* hook: hearts in the chat, then the gym guy and the offer */
tl.set("#hk-chat .gc-h", { opacity: 1 }, 0);
tl.fromTo("#hk-chat .gc-h", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.18, stagger: 0.12, immediateRender: false }, 0.05);
punch("#hk-chat", WT("hk", "hearts"), 1.05);
tl.to("#hk-chat .in", { x: -230, scale: 0.72, duration: 0.35, ease: "power2.inOut" }, WT("hk", "gym") - 0.25); fade("#hk-right", WT("hk", "gym") - 0.1, 0.2); pop("#hk-gym", WT("hk", "gym") - 0.1, 0.5);
pop("#hk-offer", WT("hk", "job") - 0.05, 0.3); tl.to("#hk-chat", { opacity: 0.45, duration: 0.3 }, WT("hk", "job"));
/* rewind to the crew */
rewind(T.r1, WT("r1", "you") - 0.05 - T.r1);
bob("#r1-b0", WT("r1", "crew"), 2.4, 12); bob("#r1-b2", WT("r1", "crew") + 0.2, 2.4, 12);
punch("#r1-you", WT("r1", "crew"), 1.06); punch("#r1-b1", WT("r1", "die"), 1.06); punch("#r1-you", WT("r1", "die"), 1.06);
/* laid off */
slam("#f1-stamp", WT("f1", "laid")); shake("#f1-you", WT("f1", "laid") + 0.2, 5);
tl.fromTo("#f1-box", { y: -30 }, { y: 0, duration: 0.3, ease: "bounce.out", immediateRender: false }, T.f1);
/* group chat: hearts, prayers, zero leads */
tl.set("#f2-chat .gc-h", { opacity: 0 }, T.f2 - 0.2);
tl.fromTo("#f2-chat .gc-h", { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.18, stagger: 0.18, immediateRender: false }, WT("f2", "hearts") - 0.1);
pop("#f2-zero", WT("f2", "zero") - 0.05, 0.4); shake("#f2-zero", WT("f2", "leads") + 0.15, 6);
/* months of applications */
tl.fromTo("#f3-papers .in", { scaleY: 0.12, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 1.0, ease: "power2.out", immediateRender: false }, WT("f3", "applications") - 0.3);
pop("#f3-cal", WT("f3", "months") - 0.1, 0.5); pop("#f3-200", WT("f3", "hundred") - 0.1, 0.4);
pop("#f3-x", WT("f3", "nothing")); tl.to("#f3-papers", { opacity: 0.5, duration: 0.3 }, WT("f3", "nothing"));
/* the gym guy sends a link */
bob("#t1-gym", T.t1, 1.4, 8);
pop("#t1-two", WT("t1", "twice") - 0.05, 0.4); hide("#t1-two", WT("t1", "sends") - 0.1);
fade("#t1-fly", WT("t1", "sends") - 0.05, 0.1); tl.fromTo("#t1-fly .in", { x: 0, y: 0, scale: 0.4 }, { x: 390, y: -280, scale: 1, duration: 0.5, ease: "power2.out", immediateRender: false }, WT("t1", "sends") - 0.05); hide("#t1-fly", WT("t1", "link") - 0.2, 0.15);
pop("#t1-phone", WT("t1", "link") - 0.25, 0.4); fade("#t1-msg", WT("t1", "link") - 0.05, 0.2); punch("#t1-phone", WT("t1", "link") + 0.2, 1.06);
tl.to("#t1-you .in", { y: -14, duration: 0.25, yoyo: true, repeat: 1 }, WT("t1", "link") + 0.3);
/* hired, more money */
slam("#t2-hired", WT("t2", "hired")); pop("#t2-badge", WT("t2", "hired") + 0.15, 0.4);
tl.fromTo("#t2-cash .in", { scaleY: 0.1, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.8, ease: "back.out(1.4)", immediateRender: false }, WT("t2", "money") - 0.2);
tl.set("#t2-cash", { opacity: 0 }, 0); tl.set("#t2-cash", { opacity: 1 }, WT("t2", "money") - 0.2);
bob("#t2-you", WT("t2", "more"), 1.6, 10);
/* the gospel, LAW 46 */
tl.fromTo("#g1-rays .in", { rotation: 0, scale: 0.4, transformOrigin: "0px 0px" }, { rotation: 18, scale: 1, duration: 1.0, ease: "power2.out", immediateRender: false }, WT("g1", "gospel") - 0.2);
tl.to("#g1-rays .in", { rotation: 40, duration: D("g1") + D("g2") + 0.5, ease: "none" }, WT("g1", "gospel") + 0.8);
punch("#g1-pr", WT("g1", "gospel"), 1.08);
tl.to("#g1-pr", { opacity: 0.35, duration: 0.2 }, WT("g2", "law") - 0.05);
slam("#g2-tab", WT("g2", "law") - 0.05); shake("#g2-tab", WT("g2", "law") + 0.2, 6); punch("#g2-tab", WT("g2", "ties"), 1.1);
fade("#law", T.m1 - 0.1, 0.25); tl.fromTo("#law", { scale: 1.6 }, { scale: 1, duration: 0.4, ease: "back.out(2)", immediateRender: false }, T.m1 - 0.1);
/* one closed world, the same jobs */
[1, 2, 3, 4].forEach(i => pop(`#m1-p${i}`, WT("m1", "people") + (i - 1) * 0.08, 0.4));
punch("#m1-world", WT("m1", "know"), 1.04);
pop("#m1-jobs", WT("m1", "same") + 0.6, 0.5); punch("#m1-jobs", WT("m1", "jobs"), 1.08);
/* a different world, doors */
fade("#m2-right", WT("m2", "different") - 0.1, 0.25); tl.fromTo("#m2-right .in", { scale: 0.6, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.4, ease: "back.out(1.8)", immediateRender: false }, WT("m2", "different") - 0.1);
tl.fromTo("#m2-bridge", { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.6, immediateRender: false }, WT("m2", "barely"));
bob("#m2-gym", WT("m2", "guy"), 1.5, 10);
["#m2-d1", "#m2-d2", "#m2-d3"].forEach((d, i) => tl.to(`${d} .in`, { scaleX: 0.08, transformOrigin: "0% 50%", duration: 0.35, ease: "power2.inOut" }, WT("m2", "doors") + i * 0.12));
/* the study: 282 workers, one in six saw them often */
pop("#p1-clip", T.p1 + 0.05, 0.6); punch("#p1-clip", WT("p1", "workers"), 1.05);
[0, 1, 2, 3, 4, 5].forEach(i => pop(`#p1-m${i}`, WT("p1", "contact") + i * 0.07, 0.4));
pop("#p1-one", WT("p1", "one") - 0.05, 0.4); pop("#p1-heart", WT("p1", "often") - 0.1, 0.4); punch("#p1-m0", WT("p1", "often"), 1.15);
/* LinkedIn: the people in between */
tl.fromTo("#p2-curve", { attr: { "stroke-dashoffset": 1 } }, { attr: { "stroke-dashoffset": 0 }, duration: 1.0, ease: "power1.inOut", immediateRender: false }, WT("p2", "tested"));
pop("#p2-lx", WT("p2", "distant")); tl.to("#p2-l", { opacity: 0.35, duration: 0.2 }, WT("p2", "distant"));
pop("#p2-rx", WT("p2", "best") + 0.25); tl.to("#p2-r", { opacity: 0.35, duration: 0.2 }, WT("p2", "best") + 0.25);
tl.set("#p2-rh", { opacity: 1 }, 0);
pop("#p2-star", WT("p2", "between") - 0.15, 0.3); fade("#p2-glow", WT("p2", "between") - 0.1, 0.25); punch("#p2-m", WT("p2", "between"), 1.25);
/* keep your boys, text the gym guy */
pop("#o1-heart", WT("o1", "keep") - 0.05, 0.4); punch("#o1-heart", WT("o1", "boys"), 1.15);
pop("#o1-msg", WT("o1", "text") - 0.05, 0.4); tl.fromTo("#o1-msg .in", { x: 60 }, { x: 0, duration: 0.3, immediateRender: false }, WT("o1", "text") - 0.05);
/* belonging vs mobility */
punch("#e1-l", WT("e1", "belonging") - 0.1, 1.08); pop("#e1-h", WT("e1", "belonging") - 0.1, 0.4);
punch("#e1-r", WT("e1", "mobility") - 0.1, 1.08); pop("#e1-arrow", WT("e1", "mobility") - 0.1, 0.4);
/* build both */
pop("#e2-you", T.e2, 0.6); punch("#e2-l", WT("e2", "both"), 1.12); punch("#e2-r", WT("e2", "both"), 1.12);
tl.to("#law", { scale: 1.25, duration: 0.15, yoyo: true, repeat: 1 }, WT("e2", "both"));
