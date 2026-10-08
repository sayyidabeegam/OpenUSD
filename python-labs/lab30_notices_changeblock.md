# Lab 30 — `ObjectsChanged`, ChangeBlock, and the DefinePrim trap

**Domain / objectives:** Debugging 6.1 · **Chapter:** 34, 44 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Split **resync** vs **info-only** notices, batch three `Sdf.PrimSpec` children into **one** `ObjectsChanged`, prove three outside the block, and catch **`UsdGeom.Sphere.Define` inside `ChangeBlock`**.

## Background
Lab 09 counted 6 vs 1 for attribute create+set. This lab names the **payload**: `GetResyncedPaths()` vs `GetChangedInfoOnlyPaths()` (Ch 34). CreateAttribute is a resync of `/W.a`; Set is info-only. `Sdf.ChangeBlock` **delays notices**, not writes. Author **Sdf specs** inside the block — `Define` of a **new child** raised `Tf.ErrorException` on USD 26.08. Unregister with **`listener.Revoke()`**.

## Steps
1. Define `/W` → one resync `['/W']`, empty info list.
2. CreateAttribute+Set → **2** notices: resync `/W.a`, then info `/W.a`.
3. Three `Sdf.PrimSpec` inside a block → **1** notice with all three paths.
4. Three more outside → **3** notices.
5. `Sphere.Define` inside a block → `Tf.ErrorException`. Then `Revoke`.

## Full script (identical to `lab30_notices_changeblock.py`)

```python
"""Lab 30 — ObjectsChanged resync vs info, ChangeBlock, DefinePrim trap."""
from pxr import Sdf, Tf, Usd, UsdGeom

hits = []


def on_changed(notice, sender):
    hits.append((
        [str(p) for p in notice.GetResyncedPaths()],
        [str(p) for p in notice.GetChangedInfoOnlyPaths()],
    ))


stage = Usd.Stage.CreateInMemory()
listener = Tf.Notice.Register(
    Usd.Notice.ObjectsChanged, on_changed, stage)
UsdGeom.Xform.Define(stage, "/W")
print("after define", hits)
hits.clear()
stage.GetPrimAtPath("/W").CreateAttribute(
    "a", Sdf.ValueTypeNames.Double).Set(1.0)
print("n after create+set", len(hits))
for h in hits:
    print(" resync", h[0], "info", h[1])
hits.clear()
parent = stage.GetRootLayer().GetPrimAtPath("/W")
with Sdf.ChangeBlock():
    for i in range(3):
        Sdf.PrimSpec(parent, f"S{i}", Sdf.SpecifierDef, "Sphere")
print("inside block", len(hits), [h[0] for h in hits])
hits.clear()
for i in range(3, 6):
    Sdf.PrimSpec(parent, f"S{i}", Sdf.SpecifierDef, "Sphere")
print("outside block", len(hits), [h[0] for h in hits])
try:
    with Sdf.ChangeBlock():
        UsdGeom.Sphere.Define(stage, "/W/Bad")
except Tf.ErrorException:
    print("Define inside block: Tf.ErrorException")
listener.Revoke()
print("revoked")
```

**Expected output**
```text
after define [(['/W'], [])]
n after create+set 2
 resync ['/W.a'] info []
 resync [] info ['/W.a']
inside block 1 [['/W/S0', '/W/S1', '/W/S2']]
outside block 3 [['/W/S3'], ['/W/S4'], ['/W/S5']]
Define inside block: Tf.ErrorException
revoked
```

## Check your understanding
1. Does ChangeBlock delay the spec writes until `exit`?
2. How do you unregister the listener?
3. Should a CAD exporter call `UsdGeom.Mesh.Define` 10,000 times inside a ChangeBlock?

**Answers**
1. **No.** Specs write immediately; **notices** wait.
2. **`listener.Revoke()`**, not `Tf.Notice.Revoke`.
3. **No.** Prefer **`Sdf.PrimSpec`** (or Define **outside** the block). New `Define` children can fail inside the block.

## Stretch challenge
Print `sorted(n for n in dir(Usd.Notice) if n[0].isupper())`. Solution includes `ObjectsChanged`, `LayerMutingChanged`, `StageContentsChanged`, `StageEditTargetChanged`, `StageNotice` (Ch 34.4).
