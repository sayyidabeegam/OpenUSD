# Cheat sheet — Debugging toolkit

**USD 26.08** · Obj 6.1–6.5 · Ch 8, 22, 33, 34, 42–44

Composition “errors” at `Open` are often **warnings**; the stage still opens. Catch **`Tf.ErrorException`**, not a bare `Exception`, for USD API/parse failures.

## Eight-step procedure (Obj 6.2)

1. `bool(prim)` / `IsValid()` — missing path is a **null** handle (`IsDefined()` **raises**).  
2. `IsDefined()`, specifier `def` vs `over` vs `class`.  
3. Load rules: `LoadNone` still loads **references**; payloads deferred. Local `over` of a payload child can exist while unloaded.  
4. `GetPrimStack()` / `GetPropertyStack()` — **strongest first**; `[0].layer` won.  
5. `GetResolveInfo()` — sample vs default vs fallback.  
6. `Usd.PrimCompositionQuery` — which arcs contributed.  
7. `stage.GetCompositionErrors()` / Pcp types (below).  
8. Mute, edit target, variant selection, relocates path, instance proxy.

## Asset vs prim path (Obj 6.3)

| Symptom | Type | Fix |
|---------|------|-----|
| File not found / unreadable | `InvalidAssetPath` | `@path@`, cwd vs **layer** anchor, resolver context |
| File opens; target prim missing | `UnresolvedPrimPath` | `defaultPrim` or `@file@</Prim>` |
| Variant name not in the set | Selection ignored | `GetVariantNames()`; opinions never apply |
| `Resolve("./tex.png")` empty; usdview shows it | Cwd vs layer | `layer.ComputeAbsolutePath` |

`ComputeAllDependencies` → `(layers, assets, unresolved)`.

## Visual (Obj 6.4 / 5.5)

| Picture | Check |
|---------|--------|
| Bounds wrong after `points` | `ComputeExtentFromPlugins` then `extent.Set` |
| Present in Traverse, missing in viewer | `purpose` vs viewer mask (`proxy`/`guide`) |
| Child gone | `GetVisibility` = `inherited`; `ComputeVisibility()` |
| Tiny / axis-flipped | `metersPerUnit` / `upAxis` (in-memory **Y**, **0.01**) |
| Subdivision surprise | Mesh fallback **`catmullClark`** |
| Material not showing | Apply `MaterialBindingAPI` then Bind; purpose/strength |
| One instance color | Instance **root**, not proxy (`OverridePrim` raises) |

## ChangeBlock & notices (Obj 6.1)

| Pattern | Result (26.08) |
|---------|----------------|
| 3× `CreateAttribute().Set()` | **6** `ObjectsChanged` notices (lab 09) |
| Same work in `Sdf.ChangeBlock` | **1** notice |
| `DefinePrim` of a **new** child inside a live block | Can raise `Tf.ErrorException` |
| `DefinePrim("/N")` | **Resync** `/N` |
| `attr.Set(...)` | **Changed-info-only** `/N.f` |

Anonymous layer not in the local stack → `SetEditTarget` raises.

## Diagnostics (Obj 6.5)

| Tool | Use |
|------|-----|
| `Tf.Status` / `Tf.Warn` | stderr; keep going |
| `Tf.RaiseCodingError` | `Tf.ErrorException` |
| `Tf.Debug` / `TF_DEBUG=` | e.g. `USD_CHANGES`, `PCP_PRIM_INDEX` |
| `UsdUtils.CoalescingDiagnosticDelegate` | Install **before** `Open` |
| `Usd.Trace.Collector` / Reporter | Timelines (works on this wheel) |
| `Tf.MallocTag.GetTotalBytes()` | Often **0** — tagging not in pip wheel |
| `GetCompositionErrors()` | Structured Pcp errors |

```text
stderr:  Status / Warn
Python:  raise Tf.ErrorException
Open:    composition failures → warnings + Pcp objects
```

## Instancing / LIVERPS traps

- `GetPrototype` not `GetMaster`. Nested `over` ignored.  
- Weaker-sublayer **local** still beats inherit. Inherit beats variant. Reference beats specialize.  
- Relocate keys must be **composed** paths.  
- Empty `GetVariantEditContext` authors **local**.
