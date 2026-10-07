"""Shared Markdown fenced-code-block parsing for the verification scripts."""

import re
from dataclasses import dataclass

FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})\s*(?P<info>.*)$")
EXPECTED_RE = re.compile(r"^\s*(\*\*)?expected output:?(\*\*)?\s*$", re.IGNORECASE)


@dataclass
class Block:
    lang: str
    classes: set
    code: str
    start_line: int
    text_before: str

    @property
    def norun(self):
        return "norun" in self.classes or "fragment" in self.classes


def _parse_info(info):
    """Return (lang, classes) from '```python' or '```{.python .norun}'."""
    info = info.strip()
    if info.startswith("{") and info.endswith("}"):
        classes = {tok[1:] for tok in info[1:-1].split() if tok.startswith(".")}
        lang = next(iter(sorted(c for c in classes if c in KNOWN_LANGS)), "")
        return lang, classes
    lang = info.split()[0] if info else ""
    return lang, set()


KNOWN_LANGS = {"python", "usda", "bash", "text", "cpp", "json", "dot"}


def parse_blocks(path):
    blocks = []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    i = 0
    prose = []
    while i < len(lines):
        m = FENCE_RE.match(lines[i])
        if not m:
            prose.append(lines[i])
            i += 1
            continue
        fence = m.group("fence")
        lang, classes = _parse_info(m.group("info"))
        start = i + 1
        body = []
        i += 1
        while i < len(lines) and not lines[i].startswith(fence):
            body.append(lines[i])
            i += 1
        i += 1
        blocks.append(Block(lang, classes, "\n".join(body) + "\n", start, "\n".join(prose)))
        prose = []
    return blocks


def expected_output_for(blocks, index):
    """Return the text block that directly follows blocks[index] as its expected output."""
    if index + 1 >= len(blocks):
        return None
    nxt = blocks[index + 1]
    if nxt.lang != "text":
        return None
    between = [ln for ln in nxt.text_before.splitlines() if ln.strip()]
    if len(between) == 1 and EXPECTED_RE.match(between[0]):
        return nxt.code
    return None
