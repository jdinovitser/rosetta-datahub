#!/usr/bin/env python3
"""
Validate or regenerate examples/input-manifest.json.

Usage
-----
  python scripts/validate_manifest.py           # validate (default)
  python scripts/validate_manifest.py --check   # same as default
  python scripts/validate_manifest.py --regen   # recompute checksums and update manifest

Exit codes
----------
  0  All checksums and file sizes match (or manifest was regenerated successfully).
  1  One or more checksums or file sizes do not match.
  2  Manifest file not found, or a listed source file is missing.

How it works
------------
  --check  For each file listed in the manifest, computes its SHA-256 and byte
           size from disk and compares against the recorded values.  Any
           mismatch prints a FAIL line and exits 1.  Run this in CI to catch
           unintentional changes to bundled input files.

  --regen  Recomputes sha256 and file_size_bytes for each listed file and
           writes the updated values back into the manifest, preserving all
           other provenance metadata (source_url, license, fields_used_by_rosetta,
           etc.).  Also updates the generated_at timestamp.  Commit both the
           changed source file and the updated manifest together.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
_MANIFEST_PATH = _REPO_ROOT / "examples" / "input-manifest.json"

RESET  = "\033[0m"
GREEN  = "\033[32m"
RED    = "\033[31m"
YELLOW = "\033[33m"
BOLD   = "\033[1m"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_manifest() -> dict:
    if not _MANIFEST_PATH.exists():
        print(f"{RED}ERROR{RESET} manifest not found: {_MANIFEST_PATH}")
        sys.exit(2)
    return json.loads(_MANIFEST_PATH.read_text())


def _check(manifest: dict) -> int:
    """Validate checksums and file sizes. Returns exit code (0 or 1)."""
    files = manifest.get("files", [])
    if not files:
        print(f"{YELLOW}WARN{RESET}  manifest contains no file entries")
        return 0

    failures = 0
    col_w = max(len(e["relative_path"]) for e in files) + 2

    print(f"\n{'File':<{col_w}} {'SHA-256':>10}  {'Size':>8}  Status")
    print("─" * (col_w + 35))

    for entry in files:
        rel = entry["relative_path"]
        path = _REPO_ROOT / rel

        if not path.exists():
            print(f"{rel:<{col_w}} {'':>10}  {'':>8}  {RED}MISSING{RESET}")
            failures += 1
            continue

        actual_sha  = _sha256(path)
        actual_size = path.stat().st_size

        sha_ok  = actual_sha  == entry.get("sha256", "")
        size_ok = actual_size == entry.get("file_size_bytes", -1)

        if sha_ok and size_ok:
            tag = f"{GREEN}PASS{RESET}"
        else:
            tag = f"{RED}FAIL{RESET}"
            failures += 1
            if not sha_ok:
                print(f"  {RED}sha256 mismatch for {rel}{RESET}")
                print(f"    expected: {entry.get('sha256','(none)')}")
                print(f"    actual:   {actual_sha}")
            if not size_ok:
                print(f"  {RED}size mismatch for {rel}{RESET}")
                print(f"    expected: {entry.get('file_size_bytes','(none)')} bytes")
                print(f"    actual:   {actual_size} bytes")

        short_sha = actual_sha[:12] + "…"
        size_str  = f"{actual_size:,}"
        print(f"{rel:<{col_w}} {short_sha:>13}  {size_str:>12}  {tag}")

    print()
    if failures:
        print(f"{RED}{BOLD}VALIDATION FAILED{RESET} — {failures} file(s) do not match the manifest.")
        print(f"  If the change is intentional, run:  python scripts/validate_manifest.py --regen")
        return 1
    print(f"{GREEN}{BOLD}VALIDATION PASSED{RESET} — all {len(files)} file(s) match the manifest.")
    return 0


def _regen(manifest: dict) -> int:
    """Recompute sha256 + file_size_bytes for each entry and write back."""
    files = manifest.get("files", [])
    updated = 0
    missing = 0

    for entry in files:
        rel  = entry["relative_path"]
        path = _REPO_ROOT / rel

        if not path.exists():
            print(f"{RED}MISSING{RESET}  {rel} — skipping (provenance metadata preserved)")
            missing += 1
            continue

        new_sha  = _sha256(path)
        new_size = path.stat().st_size

        changed = (new_sha  != entry.get("sha256")  or
                   new_size != entry.get("file_size_bytes"))

        entry["sha256"]           = new_sha
        entry["file_size_bytes"]  = new_size

        if changed:
            print(f"{YELLOW}UPDATED{RESET}  {rel}")
            print(f"         sha256: {new_sha}")
            print(f"         size:   {new_size:,} bytes")
            updated += 1
        else:
            print(f"{GREEN}UNCHANGED{RESET} {rel}")

    manifest["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    _MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nManifest written to {_MANIFEST_PATH.relative_to(_REPO_ROOT)}")
    if missing:
        print(f"{YELLOW}WARN{RESET}  {missing} file(s) were missing and not updated.")
    print(f"  {updated} checksum(s) updated.")
    return 0 if missing == 0 else 2


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_true",
        help="Validate checksums and sizes (default behaviour).",
    )
    group.add_argument(
        "--regen",
        action="store_true",
        help="Recompute checksums and update the manifest in-place.",
    )
    args = parser.parse_args()

    manifest = _load_manifest()

    if args.regen:
        sys.exit(_regen(manifest))
    else:
        sys.exit(_check(manifest))


if __name__ == "__main__":
    main()
