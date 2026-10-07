#!/usr/bin/env python3
"""Parse every ```usda block in the given Markdown files (or .usda files) with Sdf.

Blocks tagged .norun or .fragment are skipped. Requires usd-core (pxr).

Usage: python check_usda_blocks.py chapters/ch17_*.md chapters/usda/*.usda
Exit code: 0 if all parsed blocks are valid, 1 otherwise.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mdblocks import parse_blocks  # noqa: E402

try:
    from pxr import Sdf, Tf
except ImportError:
    sys.exit("pxr not found: install usd-core (see technical-accuracy.md)")


def check(text, where):
    if not text.lstrip().startswith("#usda"):
        print(f"FAIL {where}: missing '#usda 1.0' header (tag fragments .norun)")
        return False
    layer = Sdf.Layer.CreateAnonymous(".usda")
    try:
        ok = layer.ImportFromString(text)
    except Tf.ErrorException as exc:
        print(f"FAIL {where}\n{exc}\n")
        return False
    if not ok:
        print(f"FAIL {where}: Sdf could not parse the layer")
    return ok


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    checked = skipped = failed = 0
    for path in sys.argv[1:]:
        if path.endswith(".usda"):
            checked += 1
            with open(path, encoding="utf-8") as f:
                failed += not check(f.read(), path)
            continue
        for block in parse_blocks(path):
            if block.lang != "usda":
                continue
            if block.norun:
                skipped += 1
                continue
            checked += 1
            failed += not check(block.code, f"{path}:{block.start_line}")
    print(f"usda blocks: checked={checked} skipped={skipped} failed={failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
