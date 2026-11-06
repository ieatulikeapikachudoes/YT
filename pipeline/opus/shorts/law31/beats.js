document.querySelectorAll("#fx .du").forEach((c, i) => { const d = 7 + (i % 5) * 1.6; tl.fromTo(c, { y: 0 }, { y: -420, duration: d, ease: "none", repeat: Math.floor(T.end / d), immediateRender: false }, 0); });
/* hook */
if (VERSION === "A") { shake("#hA-car", 0.05, 4); tl.fromTo("#hA-smoke .puff", { y: 0, opacity: 0.7 }, { y: -80, opacity: 0.25, duration: 1.6, stagger: 0.1, repeat: 1, yoyo: true, ease: "sine.inOut", immediateRender: false }, 0);
  pop("#hA-haz", WT("hk", "dead")); pop("#hA-phone", WT("hk", "courtside") - 0.1, 0.4); punch("#hA-phone", WT("hk", "boss"), 1.06); }
if (VERSION === "B") { slam("#hB-void", WT("hk", "nobody")); shake("#hB-iou", WT("hk", "nobody") + 0.22, 10); punch("#hB-void", E.hk - 0.75, 1.2); }
if (VERSION === "C") { tl.to("#hC-him", { opacity: 0, duration: 0.45 }, WT("hk", "vanish")); fade("#hC-ghost", WT("hk", "vanish"), 0.45); swap("#hC-you", "#hC-yousad", WT("hk", "need")); }
/* rewind flash */
rewind(T.r1, WT("r1", "you") - 0.05 - T.r1);
bob("#r1-him", WT("r1", "you"), D("r1")); pop("#r1-h1", WT("r1", "guy"));
/* favors */
pop("#r2-c1", WT("r2", "moves") - 0.1, 0.5); pop("#r2-c2", WT("r2", "airport") - 0.1, 0.5); pop("#r2-c3", WT("r2", "interview") - 0.1, 0.5); punch("#r2-c3", WT("r2", "hired"), 1.06);
/* hug */
["#r3-h1", "#r3-h2", "#r3-h3"].forEach((h, i) => { pop(h, WT("r3", i ? "owe" : "hugged") + i * 0.12); tl.to(`${h} .in`, { y: -40, duration: 1.6, ease: "sine.out" }, WT("r3", "owe") + i * 0.12); });
bob("#r3-him", WT("r3", "bro"), 1.4, 8);
/* car dies + text */
tl.fromTo("#f1-smoke .puff", { y: 0, opacity: 0.2 }, { y: -90, opacity: 0.8, duration: 1.0, stagger: 0.1, ease: "power1.out", immediateRender: false }, WT("f1", "dies")); shake("#f1-car", WT("f1", "dies"), 6);
pop("#f1-phone", WT("f1", "text") - 0.1, 0.5); tl.set("#f1-reply", { opacity: 1 }, WT("f1", "cant") - 0.05); tl.fromTo("#f1-reply", { y: 20 }, { y: 0, duration: 0.2, immediateRender: false }, WT("f1", "cant") - 0.05);
/* story */
punch("#f2-phone", WT("f2", "courtside"), 1.05); punch("#f2-phone", WT("f2", "boss"), 1.08);
/* alone */
tl.fromTo("#f3-rain", { y: -60 }, { y: 140, duration: D("f3") + 0.6, ease: "none", immediateRender: false }, T.f3); tl.fromTo("#cam-f3", { scale: 1 }, { scale: 1.16, duration: D("f3") + 0.5, ease: "power1.in", immediateRender: false }, T.f3);
/* gospel */
tl.fromTo("#g1-rays .in", { rotation: 0, scale: 0.4, transformOrigin: "0px 0px" }, { rotation: 18, scale: 1, duration: 1.0, ease: "power2.out", immediateRender: false }, WT("g1", "gospel") - 0.2);
tl.to("#g1-rays .in", { rotation: 40, duration: D("g1") + D("g2") + 0.5, ease: "none" }, WT("g1", "gospel") + 0.8);
punch("#g1-pr", WT("g1", "gospel"), 1.08);
tl.to("#g1-pr, #sc-g1 .cam svg > g:not(#g1-rays):not(#g2-tab)", { opacity: 0.35, duration: 0.2 }, WT("g2", "law") - 0.05);
slam("#g2-tab", WT("g2", "law") - 0.05); shake("#g2-tab", WT("g2", "law") + 0.2, 6); punch("#g2-tab", WT("g2", "meme"), 1.1);
fade("#law", T.m1 - 0.1, 0.25); tl.fromTo("#law", { scale: 1.6 }, { scale: 1, duration: 0.4, ease: "back.out(2)", immediateRender: false }, T.m1 - 0.1);
/* forward */
tl.set("#m1-back", { opacity: 1 }, T.m1); tl.set("#m1-back .in", { scaleX: -1, transformOrigin: "50% 50%" }, T.m1);
pop("#m1-x", WT("m1", "back")); tl.to("#m1-back", { opacity: 0.4, duration: 0.2 }, WT("m1", "back"));
pop("#m1-fwd", WT("m1", "forward") - 0.05, 0.4); tl.fromTo("#m1-fwd .in", { x: -40 }, { x: 20, duration: 0.6, ease: "power2.out", immediateRender: false }, WT("m1", "forward"));
/* crowd walks to the boss */
tl.fromTo("#m2-crowd", { x: 0 }, { x: 230, duration: D("m2") - 0.2, ease: "power1.inOut", immediateRender: false }, WT("m2", "show"));
pop("#m2-boss", WT("m2", "matters")); bob("#m2-crowd .in", WT("m2", "show"), D("m2"), 8);
/* scale */
tl.fromTo("#m3-beam", { rotation: 0, svgOrigin: "540 700" }, { rotation: 0, svgOrigin: "540 700", duration: 0.01 }, T.m3);
tl.to("#m3-beam", { rotation: 11, svgOrigin: "540 700", duration: 0.6, ease: "back.out(1.6)" }, WT("m3", "make"));
tl.to("#m3-left", { y: -63, duration: 0.6, ease: "back.out(1.6)" }, WT("m3", "make")); tl.to("#m3-right", { y: 63, duration: 0.6, ease: "back.out(1.6)" }, WT("m3", "make"));
tl.to("#m3-favs", { opacity: 0.45, duration: 0.3 }, WT("m3", "already")); slam("#m3-spent", WT("m3", "spent"));
/* stop pointing, show what's coming */
punch("#o1-point", WT("o1", "past"), 1.06); swap("#o1-point", "#o1-show", WT("o1", "show") - 0.05); tl.to("#o1-pile", { opacity: 0.15, duration: 0.3 }, WT("o1", "show"));
pop("#o1-chart", WT("o1", "show")); tl.fromTo("#o1-chart .bar", { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.5, stagger: 0.08, ease: "back.out(1.6)", immediateRender: false }, WT("o1", "coming") - 0.2);
/* betting + phone rings */
tl.set("#o2-chips", { opacity: 1 }, WT("o2", "betting")); tl.fromTo("#o2-chips .in", { x: 600, opacity: 0 }, { x: 0, opacity: 1, duration: 0.5, ease: "power3.out", immediateRender: false }, WT("o2", "betting"));
pop("#o2-phone", WT("o2", "phone") - 0.1, 0.5); tl.set("#o2-ring", { opacity: 0 }, 0); tl.fromTo("#o2-ring", { opacity: 0 }, { opacity: 1, duration: 0.12, yoyo: true, repeat: 7, immediateRender: false }, WT("o2", "rings"));
shake("#o2-phone", WT("o2", "rings"), 6);
/* ledger crumples */
tl.to("#e1-iou .in", { scale: 0.18, rotation: 160, duration: 0.55, ease: "power3.in", transformOrigin: "50% 50%" }, WT("e1", "owe")); tl.to("#e1-iou .in", { y: 900, duration: 0.6, ease: "power2.in" }, WT("e1", "owe") + 0.55);
/* calibrate gauge */
tl.fromTo("#e2-needle", { rotation: -80, svgOrigin: "0 0" }, { rotation: -40, svgOrigin: "0 0", duration: 0.4, ease: "power2.out", immediateRender: false }, T.e2);
tl.to("#e2-needle", { rotation: 78, svgOrigin: "0 0", duration: 0.9, ease: "back.out(1.8)" }, WT("e2", "will"));
punch("#e2-you", WT("e2", "do"), 1.2); tl.to("#law", { scale: 1.25, duration: 0.15, yoyo: true, repeat: 1 }, WT("e2", "do"));

