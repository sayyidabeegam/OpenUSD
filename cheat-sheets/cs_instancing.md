# Cheat sheet — Instancing decisions

**USD 26.08** · Obj 1.2, 1.10, 2.1–2.5 · Ch 24–26 · `GetPrototype()` — **`GetMaster` does not exist**.

## Which style?

| | None | Native (`instanceable`) | PointInstancer |
|--|------|-------------------------|----------------|
| Count | 1–tens | tens–~10k | thousands–millions |
| Prims / copy | Whole subtree | 1 instance prim; subtree in prototype | **0** (arrays) |
| Path to a copy | Yes | Instance root yes; descendants are **proxies** | **No** |
| Per-copy edits | Anything | Root: xform, vis, variants, inherited primvars, root bind | Arrays / masks only |
| Unique internals | Yes | De-instance that one, or different variant → new prototype | Different proto index |

```text
 unique internals? yes → NONE (or de-instance that copy)
 need a prim path / variant per copy? yes → NATIVE
 huge count, transform + primvar only → POINT INSTANCER
 instance the ASSET, not each leaf mesh
```

Native prototype can contain a PointInstancer; PI prototypes can be native instances.

## Native instancing (Ch 24)

| Task | Fact (26.08) |
|------|----------------|
| Enable | `instanceable = true` / `SetInstanceable(True)` |
| Live instance? | `IsInstance()` (flag `IsInstanceable()` is only the authored intent) |
| Prototype | `prim.GetPrototype()` → `/__Prototype_N` (not saved in the layer) |
| `Traverse()` | Lists the instance root; **skips** proxy descendants |
| `GetPrimAtPath("/I/Body")` | Valid **proxy**; `IsInstanceProxy()` True |
| Nested `over "Seat"` | **Ignored** — new child not on the prototype |
| `OverridePrim("/I/Body")` | **Raises** |
| Tint one copy | Primvar / inherit / variant on the **instance root** |
| Tint all copies | Edit the prototype source (or shared class) |
| Remove a property on one | Instance-root block/delete, or `SetInstanceable(False)` |
| De-instance | `SetInstanceable(False)` → Body defined, not a proxy |

Different variant selections → **more prototypes** (`len(stage.GetPrototypes())`).

Broken model chain: un-kinded parent + child `kind = component` → `GetKind()` component, `IsComponent()` **False**.

## PointInstancer (Ch 25)

| Field | Role |
|-------|------|
| `prototypes` rel | List of proto prims (list-op!) |
| `protoIndices` | int per instance |
| `positions` / `orientations` / `scales` | Per-instance xform |
| `invisibleIds` | Hide by **id**; `GetInstanceCount()` **does not shrink** |

`PointInstancer` is **Boundable, not Gprim**.

Adding a proto: use **explicit** `ListPosition`.  
`FrontOfPrependList` → new proto is index **0** (all old `0`s retarget).  
`BackOfAppendList` → append; index 0 safe.  
Default `AddTarget` on 26.08 was **not** front-prepend — **measure**, don’t guess.

## Draw modes & working set (Ch 26, 44)

| Tool | Use |
|------|-----|
| Payload | Deferred heavy geo; `LoadNone` skips payloads, **not** references |
| Local `over` of a payload child | Child **exists** even while unloaded |
| `OpenMasked` | Population mask (`StagePopulationMask`) |
| ModelAPI drawMode | `cards` / `bounds` / … on **models** (valid hierarchy) |
| `extentsHint` | Cached model box per purpose |

## Exam traps

- Proxy edits. Nested overs. `GetMaster`.  
- PI `AddTarget` shifting proto 0. Hiding via deleting `protoIndices` instead of `invisibleIds`.  
- Instancing every bolt as a native prim (use PI). Instancing a hero that needs unique internals (don’t).
