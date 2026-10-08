# Lab 09 — Authoring with Sdf specs + `Sdf.ChangeBlock`

**Domain / objectives:** Debugging 6.1 · **Chapter:** 8 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Count `ObjectsChanged` notices for three Usd `CreateAttribute`+`Set` calls (**6** notices), then author two more attributes through **`Sdf.AttributeSpec`** inside **`Sdf.ChangeBlock`** (**1** notice). Revoke the listener.

## Background
`Usd` APIs compose as they write. `Sdf` APIs write the layer spec directly (Ch 8). `Sdf.ChangeBlock` **delays notices**, not the writes (Ch 34, Ch 44.4). Three create+set pairs without a block sent **6** notices in USD 26.08. `Usd.DefinePrim` of *new children* inside a block can fail — this lab only adds attributes on an existing prim, via Sdf, which is the safe pattern.

Unregister with **`key.Revoke()`**, not `Tf.Notice.Revoke`.

## Steps
1. Run the script. `without block: 6`.
2. `with block: 1` even though two attributes were authored.
3. `d via Usd: 4` — the stage sees the Sdf write after the block exits.

## Full script (identical to `lab09_sdf_changeblock.py`)

```python
"""Lab 09 — Authoring with Sdf specs + Sdf.ChangeBlock."""
from pxr import Sdf, Tf, Usd, UsdGeom


class Counter:
    def __init__(self):
        self.n = 0

    def __call__(self, notice, sender):
        self.n += 1


stage = Usd.Stage.CreateInMemory()
lis = Counter()
key = Tf.Notice.Register(Usd.Notice.ObjectsChanged, lis, stage)
prim = UsdGeom.Xform.Define(stage, "/W").GetPrim()
lis.n = 0
prim.CreateAttribute("a", Sdf.ValueTypeNames.Int).Set(1)
prim.CreateAttribute("b", Sdf.ValueTypeNames.Int).Set(2)
prim.CreateAttribute("c", Sdf.ValueTypeNames.Int).Set(3)
print("without block:", lis.n)
lis.n = 0
with Sdf.ChangeBlock():
    spec = stage.GetRootLayer().GetPrimAtPath("/W")
    Sdf.AttributeSpec(spec, "d", Sdf.ValueTypeNames.Int)
    spec.properties["d"].default = 4
    Sdf.AttributeSpec(spec, "e", Sdf.ValueTypeNames.Int)
    spec.properties["e"].default = 5
print("with block:", lis.n)
print("d via Usd:", prim.GetAttribute("d").Get())
print("spec typeName:", spec.typeName)
key.Revoke()
print("revoked")
```

**Expected output**
```text
without block: 6
with block: 1
d via Usd: 4
spec typeName: Xform
revoked
```

## Check your understanding
1. Does ChangeBlock delay the spec writes until `exit`?
2. How do you unregister the listener?
3. Why 6 notices for 3 attributes without a block?

**Answers**
1. **No.** Specs write immediately; **notices** wait.
2. **`key.Revoke()`.**
3. Each `CreateAttribute` and each `Set` can emit a notice (2×3 = 6).

## Stretch challenge
Move the `Sdf.AttributeSpec` lines *out* of the `with` block and compare the notice count. Solution: you will see more than 1 (typically 4 for two create+default pairs).
