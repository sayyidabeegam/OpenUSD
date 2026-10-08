# Lab 22 — Component, assembly, group, and a broken model chain

**Domain / objectives:** Content Aggregation 2.4 · Pipeline 7.2 · **Chapter:** 23 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Publish a **component** chair, reference it under an **assembly → group** chain, then put another `component` under a prim with **no kind**. Prove `GetKind()` can say `"component"` while **`IsComponent()` is False**.

## Background
A prim is a **model** only if its kind is a model kind **and** every ancestor is `group` or `assembly` (or it is the stage root) (Ch 23). **`assembly` is-a `group`** (`Kind.Registry.IsA`). The hierarchy **stops at components**. `subcomponent` and ordinary geo (here `Seat`) are not models. A `component` under an un-kinded parent is **not** a model — the classic "chair missing from the asset list" bug. `Usd.PrimIsModel` traversal prunes non-models, so it never even visits `Clutter`'s children.

## Steps
1. `assembly is-a group: True`.
2. `/Kitchen` assembly: model+group. `/Kitchen/Props` group: model+group.
3. Referenced `/Kitchen/Props/Chair_0` is a valid **component** (`Xform`, kind `component`).
4. `/Kitchen/Clutter/Mug` has kind `component` but `IsModel`/`IsComponent` are **False**.
5. Model traversal lists only Kitchen, Props, Chair_0 — not Mug, not Seat.

## Full script (identical to `lab22_component_assembly.py`)

```python
"""Lab 22 — Component, assembly, group, and a broken model chain."""
import os
import tempfile
from pxr import Kind, Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
open("chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    kind = "component"
)
{
    def Cube "Seat"
    {
        double size = 1
    }
}
""")
stage = Usd.Stage.CreateInMemory()
kitchen = UsdGeom.Xform.Define(stage, "/Kitchen").GetPrim()
Usd.ModelAPI(kitchen).SetKind("assembly")
props = UsdGeom.Xform.Define(stage, "/Kitchen/Props").GetPrim()
Usd.ModelAPI(props).SetKind("group")
c0 = stage.DefinePrim("/Kitchen/Props/Chair_0")
c0.GetReferences().AddReference("chair.usda")
UsdGeom.Xform.Define(stage, "/Kitchen/Clutter")
mug = UsdGeom.Xform.Define(stage, "/Kitchen/Clutter/Mug").GetPrim()
Usd.ModelAPI(mug).SetKind("component")
print("assembly is-a group:", Kind.Registry.IsA("assembly", "group"))
print(f"{'path':28} {'kind':13} model group component")
for prim in stage.Traverse():
    kind = Usd.ModelAPI(prim).GetKind() or "-"
    print(f"{str(prim.GetPath()):28} {kind:13} {prim.IsModel()!s:5} "
          f"{prim.IsGroup()!s:5} {prim.IsComponent()}")
print("model traversal:")
for prim in stage.Traverse(Usd.PrimIsModel):
    print(" ", prim.GetPath())
print("Chair_0 type:", c0.GetTypeName(),
      "kind:", Usd.ModelAPI(c0).GetKind())
```

**Expected output**
```text
assembly is-a group: True
path                         kind          model group component
/Kitchen                     assembly      True  True  False
/Kitchen/Props               group         True  True  False
/Kitchen/Props/Chair_0       component     True  False True
/Kitchen/Props/Chair_0/Seat  -             False False False
/Kitchen/Clutter             -             False False False
/Kitchen/Clutter/Mug         component     False False False
model traversal:
  /Kitchen
  /Kitchen/Props
  /Kitchen/Props/Chair_0
Chair_0 type: Xform kind: component
```

## Check your understanding
1. Why is Mug not a model even though `GetKind()` is `component`?
2. Is `group` a legal kind for a **published root**?
3. Does `assembly` count as a group?

**Answers**
1. **`Clutter` has no kind**, so the ancestor chain is broken.
2. **No.** Published roots are `component` or `assembly`. `group` is only for organizers inside assemblies.
3. **Yes.** `Kind.Registry.IsA("assembly", "group")` is True, so `IsGroup()` is True.

## Stretch challenge
`Usd.ModelAPI(stage.GetPrimAtPath("/Kitchen/Clutter")).SetKind("group")` and reprint Mug. Solution: Mug becomes `IsModel`/`IsComponent` True — the chain is assembly → group → component.
