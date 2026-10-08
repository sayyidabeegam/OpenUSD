# Lab 28 — Dependencies, Flatten vs FlattenLayerStack, USDZ

**Domain / objectives:** Pipeline 7.2 · Data Exchange 4.3 · Composition 1.9 · **Chapter:** 31, 32, 34 · **Time:** 35 min · **Difficulty:** ★★★

## Goal
Inventory an entry with **`ComputeAllDependencies`** (3-tuple), contrast **Export / Flatten / FlattenLayerStack**, then pack a USDZ whose zip method is **STORE (0)** — the `usdzip` stand-in on usd-core.

## Background
`ComputeAllDependencies(path)` returns **`(layers, assets, unresolved)`** and walks recursively (Ch 32). `ExtractExternalReferences` is one-file only. **Export** writes one layer (the texture lives on a sublayer, so Export misses it). **`FlattenLayerStack`** merges sublayers and **keeps references**. **`Flatten`** bakes the composed stage (Bolt becomes a local Cube; no ref). Both flatten tools often **absolutize** asset paths. `CreateNewUsdzPackage` is the Python `usdzip`; USDZ files are **uncompressed** zip members (`compress_type == 0`). A warning on stderr for `gone.jpg` is expected.

## Steps
1. Layers: `entry`, `geo`, `ref`. Assets: `wood.png`. Unresolved: `gone.jpg`.
2. Export of the root has **no** `tex`. Flatten Bolt type `Cube`, no ref. FLS Bolt type empty, **has** ref, subLayers empty.
3. USDZ succeeds; contents `root.usda` then `tex.png`; both stored (0).

## Full script (identical to `lab28_deps_flatten_usdz.py`)

```python
"""Lab 28 — ComputeAllDependencies, Flatten vs FLS, USDZ STORE."""
import os
import tempfile
import zipfile
from pxr import Sdf, Usd, UsdGeom, UsdUtils

os.chdir(tempfile.mkdtemp())
os.makedirs("tex", exist_ok=True)
open("tex/wood.png", "wb").write(b"PNG")
open("geo.usda", "w").write("""#usda 1.0
over "L"
{
    asset tex = @./tex/wood.png@
}
""")
open("ref.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Bolt"
)
def Cube "Bolt"
{
}
""")
open("entry.usda", "w").write("""#usda 1.0
(
    defaultPrim = "L"
    subLayers = [
        @./geo.usda@
    ]
)
def Xform "L"
{
    asset missing = @./gone.jpg@
    def "Bolt" (
        prepend references = @./ref.usda@
    )
    {
    }
}
""")
layers, assets, unresolved = UsdUtils.ComputeAllDependencies("entry.usda")
print("layers:", sorted(os.path.basename(l.realPath) for l in layers))
print("assets:", sorted(os.path.basename(a) for a in assets))
print("unresolved:", sorted(os.path.basename(u) for u in unresolved))

stage = Usd.Stage.Open("entry.usda")
root = stage.GetRootLayer()
print("Export has tex:", root.GetAttributeAtPath("/L.tex") is not None)
flat = stage.Flatten()
bolt = flat.GetPrimAtPath("/L/Bolt")
print("Flatten Bolt type:", bolt.typeName)
print("Flatten Bolt has ref:", bool(bolt.referenceList.prependedItems))
ls = UsdUtils.FlattenLayerStack(stage)
bolt2 = ls.GetPrimAtPath("/L/Bolt")
print("FLS Bolt type:", bolt2.typeName or "-")
print("FLS Bolt has ref:", bool(bolt2.referenceList.prependedItems))
print("FLS subLayers empty:", list(ls.subLayerPaths) == [])

pkg = Usd.Stage.CreateNew("root.usda")
UsdGeom.Xform.Define(pkg, "/Asset")
pkg.SetDefaultPrim(pkg.GetPrimAtPath("/Asset"))
open("tex.png", "wb").write(
    bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"\x00" * 8)
pkg.GetPrimAtPath("/Asset").CreateAttribute(
    "tex", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath("./tex.png"))
pkg.GetRootLayer().Save()
print("usdz:", UsdUtils.CreateNewUsdzPackage("root.usda", "out.usdz"))
print("contents:", zipfile.ZipFile("out.usdz").namelist())
print("compress:",
      [i.compress_type for i in zipfile.ZipFile("out.usdz").infolist()])
```

**Expected output**
```text
layers: ['entry.usda', 'geo.usda', 'ref.usda']
assets: ['wood.png']
unresolved: ['gone.jpg']
Export has tex: False
Flatten Bolt type: Cube
Flatten Bolt has ref: False
FLS Bolt type: -
FLS Bolt has ref: True
FLS subLayers empty: True
usdz: True
contents: ['root.usda', 'tex.png']
compress: [0, 0]
```

## Check your understanding
1. What three lists does `ComputeAllDependencies` return?
2. Does FlattenLayerStack remove references?
3. Why is `compress: [0, 0]` the exam fact?

**Answers**
1. **`(layers, assets, unresolved)`** — a 3-tuple, not a dict.
2. **No.** It removes **sublayers**. References stay. Flatten bakes them away.
3. USDZ members are **stored**, not deflated, so USD can mmap them.

## Stretch challenge
`UsdUtils.CreateNewARKitUsdzPackage("root.usda", "arkit.usdz")` and print the first zip name. Solution: `root.usdc` (crate), not USDA (Ch 31).
