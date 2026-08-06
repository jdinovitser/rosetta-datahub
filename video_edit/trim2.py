#!/usr/bin/env python3
"""
Second-pass silence removal on output_trimmed.mp4.
Removes micro-pauses from THROUGHOUT the video — end is fully preserved.
"""
import subprocess, json, re, os, shutil

INPUT  = "/home/runner/workspace/video_edit/output_trimmed.mp4"
OUTPUT = "/home/runner/workspace/video_edit/final_3min.mp4"
TMP    = "/home/runner/workspace/video_edit/tmp2"
TARGET = 180.0

os.makedirs(TMP, exist_ok=True)

# ── 1. Get duration ───────────────────────────────────────────────────────────
probe = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", INPUT],
    capture_output=True, text=True, check=True
)
total_dur = float(json.loads(probe.stdout)["format"]["duration"])
print(f"Input: {total_dur:.2f}s  ({total_dur/60:.2f} min)  →  target {TARGET}s")
need_to_cut = total_dur - TARGET
print(f"Need to remove: {need_to_cut:.2f}s from within the video\n")

# ── 2. Detect remaining silence ───────────────────────────────────────────────
result = subprocess.run(
    ["ffmpeg", "-i", INPUT,
     "-af", "silencedetect=noise=-28dB:d=0.2",
     "-f", "null", "-"],
    capture_output=True, text=True
)
starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", result.stderr)]
ends   = [float(m) for m in re.findall(r"silence_end: ([\d.]+)",   result.stderr)]

# Pair them up; ignore any trailing unpaired start (audio ends during silence)
pairs = list(zip(starts, ends))
total_silence = sum(e - s for s, e in pairs)
print(f"Found {len(pairs)} silent gaps totalling {total_silence:.2f}s")

# ── 3. Build speaking segments — keep a tiny 0.04s breath on each side ────────
PADDING = 0.04
speaking = []
cursor = 0.0
for s, e in pairs:
    seg_end = max(cursor, s + PADDING)
    if seg_end - cursor > 0.05:
        speaking.append((cursor, seg_end))
    cursor = max(cursor, e - PADDING)

# Always keep through the very end
if cursor < total_dur - 0.05:
    speaking.append((cursor, total_dur))

total_speech = sum(e - s for s, e in speaking)
print(f"Speech after removal: {total_speech:.2f}s  ({total_speech/60:.2f} min)")
print(f"Removed: {total_dur - total_speech:.2f}s  (target was {need_to_cut:.2f}s)\n")

# ── 4. Extract segments ───────────────────────────────────────────────────────
print(f"Extracting {len(speaking)} segments ...")
seg_files = []
for i, (t0, t1) in enumerate(speaking):
    p = os.path.join(TMP, f"s{i:04d}.mp4")
    subprocess.run(
        ["ffmpeg", "-y",
         "-ss", str(t0), "-to", str(t1),
         "-i", INPUT,
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k",
         "-avoid_negative_ts", "make_zero",
         p],
        capture_output=True, check=True
    )
    seg_files.append(p)
    if i % 20 == 0:
        print(f"  {i+1}/{len(speaking)} ...", flush=True)

print(f"  Done extracting.")

# ── 5. Concatenate + final quality encode ─────────────────────────────────────
concat_list = os.path.join(TMP, "list.txt")
with open(concat_list, "w") as f:
    for p in seg_files:
        f.write(f"file '{p}'\n")

print("\nConcatenating ...")
subprocess.run(
    ["ffmpeg", "-y",
     "-f", "concat", "-safe", "0", "-i", concat_list,
     "-c:v", "libx264", "-preset", "slow", "-crf", "18",
     "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart",
     OUTPUT],
    check=True, capture_output=True
)

# ── 6. Report ─────────────────────────────────────────────────────────────────
probe2 = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", OUTPUT],
    capture_output=True, text=True, check=True
)
final_dur = float(json.loads(probe2.stdout)["format"]["duration"])
size_mb   = os.path.getsize(OUTPUT) / 1024 / 1024
mins, secs = divmod(final_dur, 60)

print(f"\n{'='*50}")
print(f"✅  Done!")
print(f"   Input:  {total_dur:.1f}s  ({total_dur/60:.2f} min)")
print(f"   Output: {final_dur:.1f}s  ({int(mins)}:{secs:05.2f})")
print(f"   File:   {OUTPUT}  ({size_mb:.1f} MB)")
print(f"{'='*50}")

shutil.rmtree(TMP, ignore_errors=True)
