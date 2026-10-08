# Lab 04 — Root layer, session layer, export to string

**Domain / objectives:** Composition 1.3 · **Chapter:** 3 · **Time:** 20 min · **Difficulty:** ★☆☆

## Goal
See that the **session layer** is strongest, is the first `GetLayerStack` entry, and is *not* the default edit target. An override there wins while the root still holds the weaker value.

## Background
Every stage has a **root layer** (the document) and a **session layer** (anonymous scratch, strongest). Default `GetEditTarget()` is the root. `SetEditTarget(session)` makes subsequent `Set` calls write on the session layer. Reopening the file would lose those edits unless you export the session yourself (Ch 3, Ch 15, Ch 42.1).

## Steps
1. Run the script. Two layers: session first, then root.
2. After targeting the session, composed radius is `9`.
3. `root still has: 1.0` — Sdf on the root layer still sees the original default. The session won composition, it did not rewrite the file.

## Full script (identical to `lab04_root_session.py`)

```python
"""Lab 04 — Root layer, session layer, export to string."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
ball = UsdGeom.Sphere.Define(stage, "/Ball")
ball.GetRadiusAttr().Set(1.0)
stack = stage.GetLayerStack(includeSessionLayers=True)
print("n layers:", len(stack))
print("first is session:", stack[0] == stage.GetSessionLayer())
print("second is root:", stack[1] == stage.GetRootLayer())
print("edit target is root:",
      stage.GetEditTarget().GetLayer() == stage.GetRootLayer())
stage.SetEditTarget(stage.GetSessionLayer())
ball.GetRadiusAttr().Set(9.0)
print("radius:", ball.GetRadiusAttr().Get())
print("winning layer is session:",
      ball.GetRadiusAttr().GetPropertyStack()[0].layer
      == stage.GetSessionLayer())
print("root still has:",
      stage.GetRootLayer().GetAttributeAtPath("/Ball.radius").default)
```

**Expected output**
```text
n layers: 2
first is session: True
second is root: True
edit target is root: True
radius: 9.0
winning layer is session: True
root still has: 1.0
```

## Check your understanding
1. Is the session layer in `GetLayerStack(includeSessionLayers=False)`?
2. Why is the default edit target the root, not the session?
3. Would `Save()` on the root persist radius 9?

**Answers**
1. **No.** Pass `True` (and it is the default if you omit the flag — this lab passes it explicitly).
2. So ordinary `Set` calls go into the document you will save.
3. **No.** 9 lives on the session layer. The root still has 1.

## Stretch challenge
`print(stage.GetSessionLayer().ExportToString())` and find `double radius = 9`. Solution: the session layer USDA contains an `over "Ball"` (or a def) with radius 9.
