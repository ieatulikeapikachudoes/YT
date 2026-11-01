CAP_SANS = '.cap { font-family: "Geist", sans-serif; font-size: 58px; font-weight: 800; line-height: 1.16; letter-spacing: -0.02em; color: #fff; text-shadow: 0 3px 0 rgba(0,0,0,0.5), 0 0 22px rgba(0,0,0,0.95); }'
STYLES = {
 "flat": dict(C=dict(bgSolid="#120e2e", fg="#f6f4ff", ink="#0e1530", panel="#1d2a5a", muted="#8a8fb5", ground="#1a1446", skin="#f4c7a1", a1="#4fd8ff", a2="#ffd23f", a3="#ff3b5c", a4="#7b5cff", a5="#2fb5a6"),
   bg="radial-gradient(ellipse at 50% 40%, #4a3a8c 0%, #241c52 55%, #120e2e 100%)", font="Geist", dust=True,
   vig="radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.45) 100%)", cap=CAP_SANS,
   look="Kurzgesagt-like flat vector. Saturated accents on deep purple/blue gradients. Round friendly characters (PERSON), soft GLOWs, big simple shapes."),
 "mono": dict(C=dict(bgSolid="#111111", fg="#ffffff", ink="#111111", panel="#1e1e1e", muted="#8a8a8a", ground="#1a1a1a", skin="#d9d9d9", a1="#ffffff", a2="#bdbdbd", a3="#e5484d", a4="#5a5a5a", a5="#3a3a3a"),
   bg="linear-gradient(180deg, #2a2a2a 0%, #151515 55%, #0b0b0b 100%)", font="Geist", dust=True,
   vig="radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.6) 100%)", cap=CAP_SANS,
   look="Cinematic black, white and grey. ONE accent (a3 red) spent only on the thing that matters in each frame. Silhouettes, strong contrast, negative space."),
 "ink": dict(C=dict(bgSolid="#0a0a0a", fg="#f5f5f5", ink="#0a0a0a", panel="#161616", muted="#7a7a7a", ground="#141414", skin="#f5f5f5", a1="#f5f5f5", a2="#ffd23f", a3="#ff5a6a", a4="#9a9a9a", a5="#4fd8ff"),
   bg="#0a0a0a", font="Patrick", dust=False, vig="none",
   cap='.cap { font-family: "Patrick", cursive; font-size: 66px; line-height: 1.1; color: #fff; }',
   look="White hand-drawn line art on pure black (ThatGuy style). One recurring emotional narrator drawn with STICK (col fg, w 8). Minimal props, outlined not filled, yellow/red used rarely for emotion."),
 "paper": dict(C=dict(bgSolid="#f4efe4", fg="#1a1a1a", ink="#1a1a1a", panel="#ffffff", muted="#8c8579", ground="#e6dfd0", skin="#f4efe4", a1="#1a1a1a", a2="#9a8f7a", a3="#d62828", a4="#5c564b", a5="#c9bfa9"),
   bg="radial-gradient(ellipse at 50% 40%, #faf6ee 0%, #f1ebde 70%, #e8e0cf 100%)", font="Patrick", dust=False,
   vig="radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 65%, rgba(60,40,10,0.18) 100%)",
   cap='.cap { font-family: "Geist", sans-serif; font-size: 56px; font-weight: 800; line-height: 1.16; color: #1a1a1a; } .cap { padding: 0 } ',
   look="CGP Grey style: black ink stick figures (STICK) on warm off-white paper. Everyone in ink or muted grey-brown, ONE red (a3) for the single thing that matters. Clean, centred, lots of air."),
}
def js(name):
    import json
    s = STYLES[name]
    return f"const STYLE = {json.dumps(dict(bg=s['bg'], dust=s['dust'], vig=s['vig']))};\nconst C = {json.dumps(s['C'])};\nconst FONT = {{ label: {json.dumps(s['font'] + ', sans-serif')} }};"
