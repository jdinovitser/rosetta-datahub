#!/usr/bin/env python3
"""
Remove silence/dead space from video, denoise audio, output trimmed result.
Does NOT alter speech speed — only removes silent gaps.
"""
import subprocess, json, re, os, sys, math, shutil

INPUT  = "/home/runner/workspace/video_edit/input.mp4"
OUTPUT = "/home/runner/workspace/video_edit/output_trimmed.mp4"
TMP    = "/home/runner/workspace/video_edit/tmp_segments"
TARGET = 180.0  # 3 minutes

SILENCE_THRESH    = "-35dB"   # medium — catches pauses without clipping words
SILENCE_MIN_DUR   = 0.5       # gaps shorter than this are kept
PADDING           = 0.12      # seconds to keep on each side of a cut (avoids clipping)

os.makedirs(TMP, exist_ok=True)

# ── 1. Get total duration ──────────────────────────────────────────────────────
probe = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", INPUT],
    capture_output=True, text=True, check=True
)
total_dur = float(json.loads(probe.stdout)["format"]["duration"])
print(f"Input duration: {total_dur:.2f}s  ({total_dur/60:.2f} min)")

# ── 2. Detect silence ──────────────────────────────────────────────────────────
print(f"\nDetecting silence ({SILENCE_THRESH}, min {SILENCE_MIN_DUR}s) ...")
result = subprocess.run(
    ["ffmpeg", "-i", INPUT,
     "-af", f"silencedetect=noise={SILENCE_THRESH}:d={SILENCE_MIN_DUR}",
     "-f", "null", "-"],
    capture_output=True, text=True
)
stderr = result.stderr

# Parse silence_start / silence_end pairs
starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", stderr)]
ends   = [float(m) for m in re.findall(r"silence_end: ([\d.]+)",   stderr)]

print(f"  Found {len(starts)} silent gaps")
for s, e in zip(starts, ends):
    print(f"    {s:.2f}s – {e:.2f}s  ({e-s:.2f}s)")

# ── 3. Build list of speaking segments ────────────────────────────────────────
speaking = []
cursor = 0.0
for s, e in zip(starts, ends):
    seg_start = cursor
    seg_end   = max(cursor, s + PADDING)
    if seg_end - seg_start > 0.05:
        speaking.append((seg_start, seg_end))
    cursor = max(cursor, e - PADDING)

# final tail
if cursor < total_dur - 0.05:
    speaking.append((cursor, total_dur))

total_speech = sum(e - s for s, e in speaking)
print(f"\nSpeaking segments: {len(speaking)}")
print(f"Total speech time: {total_speech:.2f}s  ({total_speech/60:.2f} min)")
print(f"Silence removed:   {total_dur - total_speech:.2f}s")

# ── 4. If we need to cut more, extend silence threshold ───────────────────────
if total_speech > TARGET + 2:
    print(f"\n⚠ Still {total_speech - TARGET:.1f}s over target after silence removal.")
    print("  Re-running with aggressive settings (-30dB, 0.3s) ...")

    SILENCE_THRESH = "-30dB"
    SILENCE_MIN_DUR = 0.3

    result = subprocess.run(
        ["ffmpeg", "-i", INPUT,
         "-af", f"silencedetect=noise={SILENCE_THRESH}:d={SILENCE_MIN_DUR}",
         "-f", "null", "-"],
        capture_output=True, text=True
    )
    stderr = result.stderr
    starts = [float(m) for m in re.findall(r"silence_start: ([\d.]+)", stderr)]
    ends   = [float(m) for m in re.findall(r"silence_end: ([\d.]+)",   stderr)]

    speaking = []
    cursor = 0.0
    for s, e in zip(starts, ends):
        seg_start = cursor
        seg_end   = max(cursor, s + PADDING)
        if seg_end - seg_start > 0.05:
            speaking.append((seg_start, seg_end))
        cursor = max(cursor, e - PADDING)
    if cursor < total_dur - 0.05:
        speaking.append((cursor, total_dur))

    total_speech = sum(e - s for s, e in speaking)
    print(f"  After aggressive: {total_speech:.2f}s  ({total_speech/60:.2f} min)")
    print(f"  Silence removed:  {total_dur - total_speech:.2f}s")

# ── 5. Extract each speaking segment ──────────────────────────────────────────
print(f"\nExtracting {len(speaking)} segments ...")
segment_files = []
for i, (seg_start, seg_end) in enumerate(speaking):
    dur = seg_end - seg_start
    seg_path = os.path.join(TMP, f"seg_{i:04d}.mp4")
    subprocess.run(
        ["ffmpeg", "-y",
         "-ss", str(seg_start), "-to", str(seg_end),
         "-i", INPUT,
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k",
         "-avoid_negative_ts", "make_zero",
         seg_path],
        capture_output=True, check=True
    )
    segment_files.append(seg_path)
    if i % 10 == 0:
        print(f"  Extracted {i+1}/{len(speaking)} ...", flush=True)

print(f"  All {len(segment_files)} segments extracted.")

# ── 6. Write concat list ───────────────────────────────────────────────────────
concat_list = os.path.join(TMP, "concat.txt")
with open(concat_list, "w") as f:
    for p in segment_files:
        f.write(f"file '{p}'\n")

# ── 7. Concatenate + denoise audio ────────────────────────────────────────────
print("\nConcatenating and denoising ...")
subprocess.run(
    ["ffmpeg", "-y",
     "-f", "concat", "-safe", "0", "-i", concat_list,
     # audio: FFT-based denoiser (no external model needed) + gentle high-pass
     "-vf", "setpts=PTS",             # keep video timestamps clean
     "-af", "afftdn=nf=-25,highpass=f=80",
     "-c:v", "libx264", "-preset", "slow", "-crf", "18",
     "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart",
     OUTPUT],
    check=True
)

# ── 8. Report ──────────────────────────────────────────────────────────────────
probe2 = subprocess.run(
    ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", OUTPUT],
    capture_output=True, text=True, check=True
)
final_dur = float(json.loads(probe2.stdout)["format"]["duration"])
size_mb   = os.path.getsize(OUTPUT) / 1024 / 1024

print(f"\n{'='*50}")
print(f"✅  Done!")
print(f"   Input:  {total_dur:.1f}s  ({total_dur/60:.2f} min)")
print(f"   Output: {final_dur:.1f}s  ({final_dur/60:.2f} min)")
print(f"   Removed {total_dur - final_dur:.1f}s of silence/noise")
print(f"   File:   {OUTPUT}  ({size_mb:.1f} MB)")
print(f"{'='*50}")

# Clean up tmp
shutil.rmtree(TMP, ignore_errors=True)
