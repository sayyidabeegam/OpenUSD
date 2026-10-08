# Lab 13 — `defaultPrim`, explicit paths, `UnresolvedPrimPath`, internal refs

**Domain / objectives:** Composition 1.3 · **Chapter:** 16 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Reference four ways: **`defaultPrim`**, a file **with no `defaultPrim`**, an **explicit prim path**, and an **internal reference**. Prove that `AddReference` returning `True` is not composition success.

## Background
A reference without `<prim path>` uses the target layer's **`defaultPrim`** (Ch 16). USD does **not** guess the first root prim. Missing or wrong `defaultPrim` → **`Pcp.ErrorType_UnresolvedPrimPath`**. The referencing prim stays; it just receives nothing. **`AddInternalReference`** targets a prim path on this stage (no asset path). Sibling prims in the referenced file (here `/Skip`) are **not** brought in.

A warning is also printed on stderr for `/B`. Expected output below is **stdout only**.

## Steps
1. `/A` via `defaultPrim` is a `Cube` of size `2.0`. `AddReference` is `True`.
2. `/B` has no `defaultPrim`: type `''`, size `None`, still `authored: True`.
3. `/C` names `/Only` and gets size `1.0`. `/Skip` is **not** on the stage.
4. `/D` internally references `/_Tmpl` and becomes a `Sphere` of radius `4.0`.
5. `GetCompositionErrors()` reports `UnresolvedPrimPath` at `/B`.

## Full script (identical to `lab13_references.py`)

```python
"""Lab 13 — defaultPrim, explicit paths, UnresolvedPrimPath, internal refs."""
import os
import tempfile
from pxr import Sdf, Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
open("box.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Box"
)
def Cube "Box"
{
    double size = 2
}
""")
open("nodefault.usda", "w").write("""#usda 1.0
def Cube "Box"
{
    double size = 9
}
""")
open("explicit.usda", "w").write("""#usda 1.0
def Cube "Skip"
{
    double size = 99
}
def Cube "Only"
{
    double size = 1
}
""")
stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/_Tmpl").GetRadiusAttr().Set(4)
a = stage.DefinePrim("/A")
print("A authored:", a.GetReferences().AddReference("box.usda"))
b = stage.DefinePrim("/B")
print("B authored:", b.GetReferences().AddReference("nodefault.usda"))
c = stage.DefinePrim("/C")
print("C authored:", c.GetReferences().AddReference(
    "explicit.usda", Sdf.Path("/Only")
))
d = stage.DefinePrim("/D")
print("D authored:", d.GetReferences().AddInternalReference("/_Tmpl"))
print("A type/size:", a.GetTypeName(), a.GetAttribute("size").Get())
print("B type/size:", repr(b.GetTypeName()), b.GetAttribute("size").Get())
print("C type/size:", c.GetTypeName(), c.GetAttribute("size").Get())
print("Skip on stage?:", bool(stage.GetPrimAtPath("/Skip")))
print("D type/radius:", d.GetTypeName(), d.GetAttribute("radius").Get())
for err in sorted(stage.GetCompositionErrors(),
                  key=lambda e: str(e.rootSite.path)):
    print("error at", err.rootSite.path, "->", err.errorType)
```

**Expected output**
```text
A authored: True
B authored: True
C authored: True
D authored: True
A type/size: Cube 2.0
B type/size: '' None
C type/size: Cube 1.0
Skip on stage?: False
D type/radius: Sphere 4.0
error at /B -> Pcp.ErrorType_UnresolvedPrimPath
```

## Check your understanding
1. Does `AddReference` return `False` when `defaultPrim` is missing?
2. Without `defaultPrim` and without a prim path, what does USD pick?
3. Why is `/Skip` not on the stage?

**Answers**
1. **No.** It returns `True` (authoring succeeded). Check `GetCompositionErrors()`.
2. **Nothing.** USD never guesses the first root prim.
3. The reference targeted `/Only` only. Siblings of the target prim are not composed in.

## Stretch challenge
Set `layer.defaultPrim = "Box"` on `nodefault.usda` and re-check `/B`. Solution: type becomes `Cube`, size `9.0`, and the error list is empty (Ch 16.2).
