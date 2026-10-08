# Cheat sheet — Python API (usd-core 26.8)

`Usd.GetVersion()` → `(0, 26, 8)`. Package: `from pxr import Usd`.  
**Gone / missing here:** CLI (`usdcat`, `usdchecker`, `usdzip`), `UsdImaging`, `Hd`, `UsdMtlx`, `usdGenSchema`, `GetMaster`, `Kind.Registry.Register`, `AnchorRelativePath`, `UsdUtils.ComplianceChecker`.

## `Usd` — stage and prims

| Task | Call |
|------|------|
| New / open | `Stage.CreateInMemory()`, `CreateNew(path)`, `Open(path)` |
| Mask | **`OpenMasked(path, StagePopulationMask([...]))`** — not `Open(..., mask=)` |
| Load rules | `Open(path, Stage.LoadNone)` — **refs still load**; payloads deferred |
| Units | `CreateInMemory` → upAxis **Y**, mpu **0.01** |
| Set units | `UsdGeom.SetStageUpAxis(s, UsdGeom.Tokens.z)` · `SetStageMetersPerUnit(s, 1)` |
| Traverse | `stage.Traverse()`; missing path: `bool(prim)` False; `IsDefined()` **raises** |
| Prototype | `prim.GetPrototype()` (**not** `GetMaster`) |
| Edit target | `SetEditTarget(layer)`; `GetEditTargetForLocalLayer(layer)` maps offsets |
| Scoped edit | `with Usd.EditContext(stage, layer):` |
| Mute | `MuteLayer(identifier)` — layer **omitted** from `GetLayerStack` |
| Stacks | `prim.GetPrimStack()`, `attr.GetPropertyStack()` (strongest first) |
| Query | `Usd.PrimCompositionQuery(prim)` |

Anonymous layer **not** in the local stack → `SetEditTarget` raises `Tf.ErrorException`.

## `Sdf` — layers and specs

| Task | Call |
|------|------|
| Open / export | `Layer.FindOrOpen`, `Export`, `ExportToString` (always USDA text) |
| Relocates | `layer.relocates` (layer metadata) |
| Offset | `Sdf.LayerOffset(offset, scale)` → `offset + scale * layerTime` |
| Batch | `with Sdf.ChangeBlock():` — coalesces notices (**6 → 1** in lab 09) |
| New child in block | `DefinePrim` of a **new** path can raise `Tf.ErrorException` |
| Types | `Sdf.ValueTypeNames.Float`, `Color3fArray`, `Asset` |

## `UsdGeom`

| Task | Call |
|------|------|
| Define | `Xform.Define`, `Mesh.Define`, `Cube.Define`, `Sphere.Define` |
| Extent | `Boundable.ComputeExtentFromPlugins(mesh, time)` then `extent.Set` |
| Primvars | `PrimvarsAPI(prim).CreatePrimvar` / `FindPrimvarWithInheritance` |
| Visibility | `GetVisibilityAttr().Get()` may be `inherited`; use `ComputeVisibility()` |
| Tokens | `UsdGeom.Tokens.z` (**no** `Tokens.Z`) |
| Xform | `AddTranslateOp()` authors `xformOpOrder` |
| Imageable | `purpose` fallback `default`; viewer masks hide `proxy`/`guide` |
| PI | `PointInstancer` is **Boundable, not Gprim** |
| Subset | `UsdGeom.Subset.Define` |

Mesh `subdivisionScheme` fallback: **`catmullClark`**. Sphere `radius` fallback `1`; Cube `size` fallback `2`.

## `UsdShade` / `UsdLux`

| Task | Call |
|------|------|
| Bind | `MaterialBindingAPI.Apply(prim)` **then** `.Bind(material)` |
| USDA rel only | HasAPI **False**, `HasRelationship` True |
| Surface | `material.ComputeSurfaceSource()` → tuple **len 3** |
| displayColor | `UsdPrimvarReader_float3`, `inputs:varname = displayColor` |
| UV | `UsdPrimvarReader_float2` (`st`) → `UsdUVTexture` |
| Distant intensity | fallback **50000**; SphereLight **1**; name `inputs:intensity` |
| Brightness | `intensity * 2**exposure` |
| LightAPI | built-in on typed lights (`HasAPI` True) |
| ShadowAPI / ShapingAPI | **Apply** required |
| Kelvin | enable fallback **False**; temp fallback **6500** |

No `UsdMtlx` in this wheel.

## `Gf` `Vt` `Tf` `Kind`

| Module | Use |
|--------|-----|
| `Gf` | `Gf.Vec3d`, `Gf.Vec3f`, `Gf.Matrix4d`, `Gf.Camera` |
| `Vt` | `Vt.Vec3fArray`, `Vt.IntArray` (attribute arrays) |
| `Tf` | `MakeValidIdentifier("2ball")` → `_ball`; `"Pier-Dock"` → `Pier_Dock` |
| `Tf.Notice` | `Register(Usd.Notice.ObjectsChanged, cb, stage)`; `listener.Revoke()` |
| `Kind.Registry` | `GetAllKinds`, `IsA`, `IsComponent`, … — **no `Register`** |

Kinds: model → group → assembly / component; subcomponent.  
Un-kinded parent → child `GetKind()` may be `component` but `IsComponent()` **False**.  
Assembly: `IsGroup()` True, `IsComponent()` False.

## `Ar` `UsdUtils` `UsdValidation`

| Task | Call |
|------|------|
| Facade | `Ar.GetResolver()` → type **`Resolver`** |
| Plugin | `Ar.GetUnderlyingResolver()` → **`DefaultResolver`** |
| Cwd trap | `Resolve("./tex.png")` uses **cwd**; composition **anchors to the layer** |
| Layer path | `layer.ComputeAbsolutePath("./tex.png")` |
| Extract (one file) | `ExtractExternalReferences` → `(sublayers, refs+assets, payloads)` |
| Closure | `ComputeAllDependencies` → `(layers, assets, unresolved)` |
| Flatten | `stage.Flatten()` **bakes refs**; `FlattenLayerStack` **keeps refs**, drops sublayers |
| USDZ | `CreateNewUsdzPackage` — ZIP **`STORED` (0)** |
| Model name | `GetModelNameFromRootLayer` — `defaultPrim`, else **first root prim**, else `''` |
| Coalesce | `CoalescingDiagnosticDelegate` **before** `Open` |
| Validate | `from pxr import UsdValidation` — not `ComplianceChecker` |
| Localize | `UsdUtils.LocalizeAsset` |

`PXR_PLUGINPATH_NAME` plus `Plug.Registry.RegisterPlugins(path)`.

## Notices / perf (Ch 43–44)

DefinePrim → **resync** paths. Attribute `Set` → **changed-info-only**.  
`Trace` Collector works. `Tf.MallocTag.GetTotalBytes()` often **0** on this wheel.
