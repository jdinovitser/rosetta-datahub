#!/usr/bin/env python3
"""
Clean silence-removal pass starting from the original input.
Parses silence events in order (never mismatches start/end).
End of video is always preserved in full.
"""
import subprocess, json, re, os, shutil, sys

INPUT  = "/home/runner/workspace/video_edit/input.mp4"
OUTPUT = "/home/runner/workspace/video_edit/final_3min.mp4"
TMP    = "/home/runner/workspace/video_edit/tmp3"
TARGET = 180.0

os.makedirs(TMP, exist_ok=True)

# ── helpers ───────────────────────────────────────────────────────────────────
def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
        capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])

def detect_silence(path, thresh, min_dur):
    """Returns list of (start, end) pairs in chronological order."""
    r = subprocess.run(
        ["ffmpeg", "-i", path,
         "-af", f"silencedetect=noise={thresh}:d={min_dur}",
         "-f", "null", "-"],
        capture_output=True, text=True)
    # Parse events in order so starts/ends are always correctly paired
    pairs, cur_start = [], None
    for line in r.stderr.splitlines():
        ms = re.search(r"silence_start: ([\d.]+)", line)
        me = re.search(r"silence_end: ([\d.]+)",   line)
        if ms:
            cur_start = float(ms.group(1))
        if me and cur_start is not None:
            pairs.append((cur_start, float(me.group(1))))
            cur_start = None
    return pairs

def build_speaking(silence_pairs, total_dur, pad=0.05):
    """Convert silence intervals → speaking intervals, keeping full end."""
    segs, cursor = [], 0.0
    for s, e in silence_pairs:
        seg_end = max(cursor, s + pad)
        if seg_end - cursor > 0.05:
            segs.append((cursor, seg_end))
        cursor = max(cursor, e - pad)
    if cursor < total_dur - 0.05:
        segs.append((cursor, total_dur))   # ← always keep to the very end
    return segs

def extract_segment(path, t0, t1, out):
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t0), "-to", str(t1), "-i", path,
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k",
         "-avoid_negative_ts", "make_zero", out],
        capture_output=True, check=True)

# ── 1. Probe original ─────────────────────────────────────────────────────────
total_dur = get_duration(INPUT)
print(f"Original: {total_dur:.2f}s ({total_dur/60:.2f} min)  →  target {TARGET}s")
print(f"Need to cut: {total_dur - TARGET:.1f}s\n")

# ── 2. Try progressively tighter silence detection until we hit target ────────
presets = [
    ("-35dB", 0.5, 0.05),   # light   — natural pauses
    ("-32dB", 0.3, 0.05),   # medium
    ("-28dB", 0.2, 0.03),   # tight
    ("-25dB", 0.15, 0.02),  # aggressive
]

chosen_segs = None
for thresh, min_dur, pad in presets:
    silence = detect_silence(INPUT, thresh, min_dur)
    segs    = build_speaking(silence, total_dur, pad)
    speech  = sum(e - s for s, e in segs)
    print(f"  {thresh} / {min_dur}s / pad={pad}s → {len(silence)} gaps, "
          f"speech={speech:.1f}s ({speech/60:.2f} min)")
    chosen_segs = segs
    chosen_speech = speech
    if speech <= TARGET + 1.0:   # within 1s of target is fine
        print(f"  ✓ Good enough at this preset.\n")
        break

print(f"\nUsing {len(chosen_segs)} speaking segments → {chosen_speech:.1f}s")

# ── 3. Extract segments ───────────────────────────────────────────────────────
print("Extracting segments ...")
seg_files = []
for i, (t0, t1) in enumerate(chosen_segs):
    p = os.path.join(TMP, f"s{i:04d}.mp4")
    extract_segment(INPUT, t0, t1, p)
    seg_files.append(p)
    if i % 20 == 0:
        print(f"  {i+1}/{len(chosen_segs)} ...", flush=True)
print("  Done.")

# ── 4. Concatenate + denoise ──────────────────────────────────────────────────
concat_list = os.path.join(TMP, "list.txt")
with open(concat_list, "w") as f:
    for p in seg_files:
        f.write(f"file '{p}'\n")

print("\nConcatenating + denoising ...")
subprocess.run(
    ["ffmpeg", "-y",
     "-f", "concat", "-safe", "0", "-i", concat_list,
     "-af", "afftdn=nf=-25,highpass=f=80",
     "-c:v", "libx264", "-preset", "slow", "-crf", "18",
     "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart",
     OUTPUT],
    check=True, capture_output=True)

# ── 5. Report ─────────────────────────────────────────────────────────────────
final = get_duration(OUTPUT)
size  = os.path.getsize(OUTPUT) / 1024 / 1024
m, s  = divmod(final, 60)
print(f"\n{'='*52}")
print(f"✅  Done!")
print(f"    Original : {total_dur:.1f}s  ({total_dur/60:.2f} min)")
print(f"    Output   : {final:.1f}s  ({int(m)}:{s:05.2f})")
print(f"    Removed  : {total_dur - final:.1f}s of silence/noise")
print(f"    File     : {OUTPUT}  ({size:.1f} MB)")
print(f"{'='*52}")

shutil.rmtree(TMP, ignore_errors=True)
