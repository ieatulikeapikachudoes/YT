"""mix.py <short_dir> <V> <music_file> [build_at_line] [build_at_track_s] [volume]
Mixes an existing music file under proj-<V>/assets/voice.wav -> mix.wav. Music ducks under the voice.
Lines the track up so its big build (at build_at_track_s in the track) lands on the start of build_at_line.
Local only: no music generation here (Venice is off until Simon turns it back on)."""
import json, subprocess, sys
D, V, M = sys.argv[1], sys.argv[2], sys.argv[3]
line = sys.argv[4] if len(sys.argv) > 4 else None; at = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0; vol = float(sys.argv[6]) if len(sys.argv) > 6 else 0.30
P = f"{D}/proj-{V}/assets"; t = json.load(open(f"{P}/timing.json")); T = {l["key"]: l["start"] for l in t["lines"]}; dur = t["total"]
tlen = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", M], capture_output=True, text=True).stdout)
off = max(0.0, at - T[line]) if line else 0.0
if tlen - off < dur: print(f"warning: track has {tlen - off:.1f}s left after offset, video is {dur:.1f}s; the end will be voice only")
fc = (f"[1:a]atrim={off:.3f}:{off + dur:.3f},asetpts=N/SR/TB,aresample=24000,volume={vol},afade=t=in:d=0.4,afade=t=out:st={dur - 0.6:.3f}:d=0.6[m];"
      "[0:a]asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=350[md];"
      "[v][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[out]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{P}/voice.wav", "-i", M, "-filter_complex", fc, "-map", "[out]", f"{P}/mix.wav"], check=True)
print(f"{V}: music offset {off:.2f}s, volume {vol} -> {P}/mix.wav")
