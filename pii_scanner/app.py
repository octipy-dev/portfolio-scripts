#!/usr/bin/env python3
import re
import os
import argparse
from pathlib import Path

# Requires tqdm: pip install tqdm
from tqdm import tqdm

# ——— Define your regex patterns here ———
PATTERNS = {
    "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "AWS Secret Key": re.compile(r"(?i)aws(.{0,20})?(secret|access)(.{0,20})?[0-9a-zA-Z/+]{40}"),
    "Generic API Key":  re.compile(r"(?i)api[_-]?key(.{0,10})?[:=]\s*[0-9a-zA-Z\-]{16,}"),
    "Password in Code": re.compile(r"(?i)password(.{0,20})?[:=]\s*['\"].*?['\"]")
}

def scan_file(path: Path):
    results = []
    text = path.read_text(errors="ignore")
    for name, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            line_no = text[:m.start()].count("\n") + 1
            snippet = m.group(0)
            results.append((name, line_no, snippet.strip()))
    return results


def main():
    parser = argparse.ArgumentParser(
        description=" Scan a directory for hard‑coded secrets (API keys, passwords…)."
    )
    parser.add_argument(
        "-d", "--dir", type=Path, default=Path.cwd(),
        help="Directory to scan (defaults to current folder)"
    )
    args = parser.parse_args()

    # Gather all files to scan, skipping common noise folders
    file_list = []
    for root, _, files in os.walk(args.dir):
        # skip node_modules, .venv, and other unwanted folders
        if any(skip in root for skip in ("node_modules", ".venv", "__pycache__")):
            continue
        for fname in files:
            file_list.append(Path(root) / fname)

    print(f"\nScanning {args.dir.resolve()} for secrets…\n")

    # Display progress bar over files, in green
    for filepath in tqdm(file_list, desc="Scanning files", unit="file", colour="green"):
        try:
            findings = scan_file(filepath)
            if findings:
                print(f"\n⚠️  {filepath.relative_to(args.dir)}")
                for kind, ln, snip in findings:
                    print(f"   • {kind} @ line {ln}: {snip}")
        except Exception:
            # skip unreadable/binary files
            continue

    print("\n Scan complete.\n")

if __name__ == "__main__":
    main()

