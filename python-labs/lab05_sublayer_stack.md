# Lab 05 — Build a sublayer stack and see who wins

**Domain / objectives:** Composition 1.1 · **Chapter:** 3, 15 · **Time:** 25 min · **Difficulty:** ★☆☆

## Goal
Author a root with two sublayers, predict the composed `radius`, then **mute** the winner to confirm which file was contributing.

## Background
`subLayers` on the root are weaker than the root itself but ordered **first-listed = stronger** among themselves (Ch 15). Muting (`MuteLayer`) pulls a layer out of composition without deleting the file — a debugging tool (Ch 42.1). Use **multiline** USDA; `def Sphere "Ball" { double radius = 1 }` on one line fails to parse.

## Steps
1. `b.usda` is listed first, so it beats `a.usda`. Radius **2**.
2. Mute `b` → radius **1** from `a`.
3. The root file itself authors nothing on `radius`.

## Full script (identical to `lab05_sublayer_stack.py`)

```python
"""Lab 05 — Build a sublayer stack and see who wins."""
import os
import tempfile
from pxr import Usd

os.chdir(tempfile.mkdtemp())
open("a.usda", "w").write("""#usda 1.0
def Sphere "Ball"
{
    double radius = 1
}
""")
open("b.usda", "w").write("""#usda 1.0
over "Ball"
{
    double radius = 2
}
""")
open("root.usda", "w").write("""#usda 1.0
(
    subLayers = [
        @./b.usda@,
        @./a.usda@
    ]
)
""")
stage = Usd.Stage.Open("root.usda")
print("stack:")
for lyr in stage.GetLayerStack(includeSessionLayers=False):
    print(" ", lyr.GetDisplayName())
radius = stage.GetPrimAtPath("/Ball").GetAttribute("radius")
print("radius:", radius.Get())
stage.MuteLayer(os.path.abspath("b.usda"))
print("muted radius:", radius.Get())
```

**Expected output**
```text
stack:
  root.usda
  b.usda
  a.usda
radius: 2.0
muted radius: 1.0
```

## Check your understanding
1. Why does `b` beat `a`?
2. Does the root beat `b` if it also authored radius 4?
3. Does muting delete `b.usda`?

**Answers**
1. It is **first-listed**, so stronger among sublayers.
2. **Yes.** Root is stronger than every sublayer.
3. **No.** Mute is per-stage; the file stays on disk.

## Stretch challenge
Unmute `b` and print radius again. Solution: `stage.UnmuteLayer(os.path.abspath("b.usda"))` then `Get()` → `2.0`.
