"""Scratch helper: run each runnable python block and write its real stdout into
the ```text block that follows '**Expected output**'. Prints outputs for review."""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".cursor", "skills",
                 "openusd-certification", "scripts")))
from mdblocks import parse_blocks, expected_output_for  # noqa: E402

path = sys.argv[1]
blocks = parse_blocks(path)
with open(path, encoding="utf-8") as f:
    lines = f.read().splitlines()

replacements = []
for idx, b in enumerate(blocks):
    if b.lang != "python" or b.norun:
        continue
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, "block.py")
        with open(script, "w") as f:
            f.write(b.code)
        proc = subprocess.run([sys.executable, script], cwd=tmp,
                              capture_output=True, text=True, timeout=120)
    print(f"===== line {b.start_line} rc={proc.returncode}")
    print(proc.stdout.rstrip())
    if proc.stderr.strip():
        print("--- stderr\n" + proc.stderr.rstrip())
    if expected_output_for(blocks, idx) is None:
        print("!!! no expected-output block")
        continue
    nxt = blocks[idx + 1]
    body_start = nxt.start_line
    n_old = len(nxt.code.splitlines()) if nxt.code.strip() else 0
    out = [ln.rstrip() for ln in proc.stdout.rstrip().splitlines()]
    replacements.append((body_start, body_start + n_old, out))

for start, end, new in sorted(replacements, reverse=True):
    lines[start:end] = new
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

for i, ln in enumerate(lines, 1):
    if len(ln) > 88:
        print(f"LONG LINE {i}: {len(ln)}")
