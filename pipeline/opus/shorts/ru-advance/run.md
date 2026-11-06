# run.md: ru-advance ("What If Russia Broke Through")
Order (Simon, Nov 2026): a short on what it would look like if Russia made battlefield progress; crisp geopolitical animation; ominous, scary music. Geo explainer, not a Gospel short, so the story-first / gospel-at-60% rules don't apply.

- RESEARCH: DeepState (19.25% held at start of 2026, 4,336 km² taken in 2025), Meduza June 2026 (Kramatorsk/Sloviansk anchor the Donbas defense; Kostiantynivka contested; Pokrovsk, Toretsk, Siversk taken), Nov 1 2026 digest (heaviest fighting Pokrovsk, Kostiantynivka, Lyman). Framed as a clearly labeled hypothetical; on-screen "HYPOTHETICAL SCENARIO" tag the whole time, chip switches TODAY / WHAT IF / TODAY.
- HOOKS: 5 written (hooks.md), hook judge picked "What if these two cities fell? The map of Europe would change."
- SCRIPT: S + STRANGER + S-PAIR. S-PAIR changes 1, 3, 4 applied; change 2 (name the captured towns aloud) skipped because the stranger lost interest on lists. 132 words.
- VOICE: Gemini 3.1 Flash, Charon, tempo 1.08, 56.49 s. Russian-sounding pronunciations fixed with phonetic "say" fields (Krah-ma-torsk, Slo-vyansk, Kos-tyan-tee-niv-ka, Za-po-rizh-zhya).
- MUSIC: ElevenLabs Music v2.5 via Venice, 59 s ominous score ($0.69). Mixed under the voice with sidechain ducking, music dipped before "Now imagine they fall", a sub boom on "fall" (19.6 s) and on the last word "line". Mean -16.9 dB.
- MAP: Natural Earth 50m borders (world-atlas), conic conformal projection, baked dark relief rasters; front line hand-drawn from DeepState/ISW (approximate). Hypothetical push drawn west of Kramatorsk/Sloviansk toward the Dnipro.
- BOARD r1: free check flagged STATIC 40.8-44.0 and 49-54 s; added the 603,500 KM² chip, Ukraine outline pulse, ≈19% chip and front pulse. PASS.
- BOARD judge r1: 6/10 FIX (weak hook, tiny labels, clipped Kramatorsk, flat chips). Applied: hook opens tight on the two cities with a red ring and big title then zooms out on "map of Europe"; towns flip red with X instead of tiny labels; labels 1.5 to 2.5x bigger; chips made the hero.
- BOARD judge r2: 7.5/10 FIX (clipped label, short west arrow, Dnipro label clutter, 30 km ruler needs the border named, s4 arrows at the right edge). All five applied. Max rounds reached, moving on.
- RENDER: first try was crawling (fullscreen feTurbulence grain recomputed every frame); swapped for a baked grain PNG.
- FINAL r1: check.py final PASS (56.5 s, mean -17.0 dB). Final judge picked cover 1 ("IF THESE 2 CITIES FALL / WHAT HAPPENS NEXT?"); flagged Zaporizhzhia label cut at the left edge, Kharkiv labels dropping out early, and a visible edge on the close-up relief image during zooms. All fixed; one re-render (crf 25 for a smaller phone file).
- OPEN: front line is hand-drawn and approximate; the hypothetical push is our own illustration, not a forecast.
