# Cheat sheet — Schemas & kinds

**USD 26.08** · Obj 3.3, 3.4, 3.6, 4.5, 5.4 · Ch 6, 23, 37, 38

## Typed vs API

| | Typed (`UsdTyped`) | API (`UsdAPISchemaBase`) |
|--|--------------------|--------------------------|
| USDA | `def Cube "Box"` | `prepend apiSchemas = ["MaterialBindingAPI"]` |
| Python | `UsdGeom.Cube.Define` | `MaterialBindingAPI.Apply(prim)` then use the API |
| `typeName` | Changes (`Cube`) | Unchanged |
| `IsA` / `HasAPI` | `prim.IsA(UsdGeom.Cube)` | `prim.HasAPI(UsdShade.MaterialBindingAPI)` |
| Use | New prim type / Gprim | Properties on **existing** prims |

Physics properties on a Mesh → **API** (`UsdPhysics.CollisionAPI.Apply`), not a new typed Mesh.  
Verified: CollisionAPI Apply works on this wheel.

**Apply then Bind:** USDA `rel material:binding` without `apiSchemas` → HasAPI **False**, rel True.

Built-in vs applied lights: DistantLight **HasAPI LightAPI** already; **ShadowAPI** / **ShapingAPI** need Apply.  
Intensity name: `inputs:intensity`.

## Kind hierarchy (model TOC)

```text
model
  group
    assembly     (aggregates models — IsGroup True, IsComponent False)
    component    (publishable asset — IsComponent True if chain intact)
subcomponent     (inside a component — NOT a model)
```

`Kind.Registry.IsA("assembly", "group")` True.  
`IsA("subcomponent", "model")` **False**.

| Kind | Model? | Typical root |
|------|--------|----------------|
| `assembly` | yes | Shot / set |
| `component` | yes | Published asset (`Chair`) |
| `group` | yes | Organize *inside* assemblies — not the published root |
| `subcomponent` | **no** | Wheel, lid, seat |

**Broken chain:** un-kinded `/Clutter` + child `kind = component` → `GetKind()` is `component`, `IsComponent()` **False**.

`Kind.Registry.Register` **does not exist**. Custom kinds: kind plugin / `plugInfo.json` (Obj 3.3).  
Python: `GetAllKinds`, `IsA`, `IsComponent`, `IsAssembly`, `IsGroup`, `IsModel`, `HasKind`.

ASWF: published roots are usually **component** or **assembly**.

## Custom schemas (Obj 3.4 / 4.5)

| Path | When |
|------|------|
| `custom float studio:lod = 2` | One-off / exporter; **persists** without a plugin |
| API / typed schema | Many DCCs, fallbacks, docs, validation |

`schema.usda` is the source. `usdGenSchema` generates code + `plugInfo.json`.  
**Parse ≠ register.** `Sdf.Layer.FindOrOpen("schema.usda")` does not install types.  
`usdGenSchema` is **not** on PATH in usd-core.  
Codeless: `skipCodeGeneration` in `customData`; still needs a plugin on `PXR_PLUGINPATH_NAME`.  
Codeful: rebuild against the **same ABI** the process loaded (`Usd.GetVersion()` → `(0, 26, 8)` here).

Plugin jobs (Ch 36–38): schema, **kind**, **Ar resolver**, file format, Hydra SceneIndex.  
SceneIndex / `UsdImaging` / `Hd` / `UsdMtlx`: **not** in this wheel.

## ModelAPI extras

`UsdGeom.ModelAPI` draw modes (`cards`, `bounds`, …) and `extentsHint` apply to **models** with a valid hierarchy — not every gprim / shapeless `over`.
