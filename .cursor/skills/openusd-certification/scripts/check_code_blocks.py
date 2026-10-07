#!/usr/bin/env python3
"""Run every ```python block in the given Markdown files.

Each block runs in its own temporary directory with the current interpreter.
If a block is followed by '**Expected output:**' and a ```text block, stdout is
compared (whitespace-normalized). Blocks tagged .norun or .fragment are skipped.

Usage: python check_code_blocks.py chapters/ch17_*.md [--timeout 60]
Exit code: 0 if all ran blocks pass, 1 otherwise.
"""

import argparse
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdblocks import expected_output_for, parse_blocks  # noqa: E402


def normalize(text):
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    ran = skipped = failed = mismatched = 0
    for path in args.files:
        blocks = parse_blocks(path)
        for idx, block in enumerate(blocks):
            if block.lang != "python":
                continue
            where = f"{path}:{block.start_line}"
            if block.norun:
                skipped += 1
                continue
            ran += 1
            with tempfile.TemporaryDirectory() as tmp:
                script = os.path.join(tmp, "block.py")
                with open(script, "w", encoding="utf-8") as f:
                    f.write(block.code)
                try:
                    proc = subprocess.run(
                        [sys.executable, script], cwd=tmp, capture_output=True,
                        text=True, timeout=args.timeout,
                    )
                except subprocess.TimeoutExpired:
                    failed += 1
                    print(f"FAIL (timeout) {where}")
                    continue
            if proc.returncode != 0:
                failed += 1
                print(f"FAIL {where}\n{proc.stderr.strip()}\n")
                continue
            expected = expected_output_for(blocks, idx)
            if expected is not None and normalize(proc.stdout) != normalize(expected):
                mismatched += 1
                print(f"MISMATCH {where}\n--- expected\n{normalize(expected)}\n"
                      f"--- actual\n{normalize(proc.stdout)}\n")

    print(f"python blocks: ran={ran} skipped={skipped} failed={failed} "
          f"output_mismatch={mismatched}")
    sys.exit(1 if failed or mismatched else 0)


if __name__ == "__main__":
    main()
