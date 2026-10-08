# Lab 34 — PreviewSurface and `MaterialBindingAPI`

**Domain / objectives:** Visualization 8.2, 8.3 · **Chapter:** 40 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Author a **Material** with a child **Shader** whose `info:id` is **`UsdPreviewSurface`**, connect `outputs:surface`, and prove **`Bind` without `Apply` writes the relationship but `HasAPI` stays False**. Then `Apply` + `Bind` and compute the bound material.

## Background
`UsdPreviewSurface` is an **`info:id` string**, not a prim type (Ch 40). Hydra draws a Shader connected to the Material terminal. **`MaterialBindingAPI.Apply(prim)` then `.Bind(material)`** is required. Skipping Apply still writes `rel material:binding` and Bind can succeed, but validators fail `HasAPI`. `ComputeSurfaceSource()` returns a **tuple** (length 3 on 26.08), not a single shader.

> [!VERSION] Verified on USD 26.08. Bind without Apply writes the rel; `HasAPI` is False until Apply.

## Steps
1. Bind without Apply: `HasAPI` False, `has rel` True.
2. After Apply: `HasAPI` True; bound path `/Looks/Paint`.
3. Shader id `UsdPreviewSurface`. Surface source tuple length 3.

## Full script (identical to `lab34_preview_binding.py`)

```python
"""Lab 34 — PreviewSurface, Apply then Bind, ComputeSurfaceSource."""
from pxr import Sdf, Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/World/Board")
UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
    "displayColor", Sdf.ValueTypeNames.Color3fArray,
    UsdGeom.Tokens.constant
).Set([(0.2, 0.5, 0.9)])
mat = UsdShade.Material.Define(stage, "/Looks/Paint")
ps = UsdShade.Shader.Define(stage, "/Looks/Paint/Preview")
ps.CreateIdAttr("UsdPreviewSurface")
ps.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((1, 0, 0))
ps.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat.CreateSurfaceOutput().ConnectToSource(ps.GetOutput("surface"))
UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(mat)
print("HasAPI without Apply:",
      mesh.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
print("has rel:", mesh.GetPrim().HasRelationship("material:binding"))
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
print("HasAPI after Apply:",
      mesh.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
bound = UsdShade.MaterialBindingAPI(mesh.GetPrim()).ComputeBoundMaterial()[0]
print("bound:", bound.GetPath())
print("shader id:", ps.GetIdAttr().Get())
print("surface source len:", len(mat.ComputeSurfaceSource()))
```

**Expected output**
```text
HasAPI without Apply: False
has rel: True
HasAPI after Apply: True
bound: /Looks/Paint
shader id: UsdPreviewSurface
surface source len: 3
```

## Check your understanding
1. Where is `info:id = "UsdPreviewSurface"` authored?
2. Is Bind-without-Apply a no-op?
3. What does `ComputeSurfaceSource()` return?

**Answers**
1. On the **Shader** child, not on the Material prim.
2. **No.** It still writes `material:binding`. `HasAPI` stays False until **Apply**.
3. A **tuple** (length 3 here), not a single shader object.

## Stretch challenge
Connect `UsdPrimvarReader_float3` (`varname = displayColor`) to `inputs:diffuseColor`. Solution: Obj 8.4 — PreviewSurface does not read mesh primvars by itself (Ch 40.5).
