# Chapter 34 — Exporter Hooks, Flattening, and Change Processing

> **Exam domain:** Pipeline Development (14%), also Composition (23%) and Debugging (11%) · **Objectives:** 1.9, 6.1 · **Study day:** 10 · **Est. time:** 95 min
> **Prerequisites:** Ch 8 (Usd vs Sdf, ChangeBlock intro), Ch 22 (delivery: flatten / localize), Ch 29 (exporter hooks first look), Ch 32–33 (publish, Ar)

Chapter 29 called a **hook** after writing prims. Chapter 22 showed **Flatten**, **FlattenLayerStack**, and **LocalizeAsset** for delivery (Obj 1.9). This chapter is the pipeline version: hooks that *fix* structure, the flatten **decision**, stripping proprietary dependencies, **notices** so a DCC can stay live, and `Sdf.ChangeBlock` as the Obj 6.1 bottleneck tool with proof.

## Learning goals

- Write exporter hooks that enforce `defaultPrim`, `kind`, and other pipeline rules (and *apply* the fix).
- Choose `Usd.Stage.Flatten`, `UsdUtils.FlattenLayerStack`, or a plain layer `Export` for a delivery.
- Remove studio-only metadata and rewrite leaked absolute asset paths (`ModifyAssetPaths`).
- Register `Usd.Notice.ObjectsChanged` and revoke the listener.
- Use `Sdf.ChangeBlock` so many Sdf edits fire **one** notice (Obj 6.1).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Exporter hook** | A function the exporter runs after write, before Save, to enforce structure |
| **Flatten** | Bake the *composed stage* into one layer; arcs and unselected variants go away |
| **FlattenLayerStack** | Merge only the root **sublayers** into one layer; references stay |
| **Export (one layer)** | Write that layer's specs only; no composition |
| **Proprietary dependency** | A path, plugin, or `customData` key an outside party must not receive |
| **Notice** | A callback USD sends when the stage or a layer changes (`Tf.Notice`) |
| **Resync** | A notice that the prim index at a path must be rebuilt |
| **Change block** | Batches edits so listeners run once when the block ends |

---

## 34.1 Exporter hooks to enforce pipeline structure

### 1. What is it?

An **exporter hook** is a function you call at a fixed point in export — after prims exist, before `Save()` — that **checks and repairs** pipeline structure: `defaultPrim`, `kind`, relative asset paths, extents (Ch 13), naming (Ch 28). Chapter 29 introduced the idea. Here the hook is a **list of structural guarantees** the publisher will not skip.

### 2. Why do we need it?

Artists and DCC exporters forget metadata. A chair without `defaultPrim` cannot be referenced by path-less `@chair.usda@` (Ch 16). A publish without `kind` disappears from model traversal (Ch 23). Hooks make the rules one function every exporter calls (Obj 1.9 starts with a well-formed internal asset).

### 3. Beginner explanation

A hotel checkout checklist: key returned, minibar billed, door locked. The guest already packed. The checklist does not pack the suitcase; it refuses to let you leave until the room matches the house rules.

*Where the analogy breaks:* a hook may **repair** (set `defaultPrim` when there is exactly one root) instead of only refusing. Document which checks auto-fix and which fail the publish.

### 4. Technical explanation

A pipeline hook has a stable signature, for example `hook(stage) -> list[str]` of fixes applied (and a separate validator from Chapter 30 that *reports* remaining errors).

Typical structural fixes:

| Rule | Repair if safe | Else fail |
|------|----------------|-----------|
| `defaultPrim` | One root prim → `SetDefaultPrim` | Zero or many roots |
| `kind` on the default prim | Missing → `component` or studio default | Already wrong |
| Stage metrics | Missing `upAxis` / `metersPerUnit` → studio defaults | Mismatch with referenced assets (Ch 28) |
| Asset paths | Rewrite `/mnt/show/...` to `./...` if the file is inside the asset | Path outside the tree |

Hooks run on the **edit target / root layer** you are about to publish, not on the session layer.

Call order (repeat of Ch 29, now pipeline-complete): extract → transform → write → **hooks** → validate → Save. Notices (Section 34.4) are for *live* DCC sync; batch converters just call the list.

### 5. Mental model

```text
  write prims
      |
      v
  hooks:  defaultPrim? kind? metrics? relative paths?
      |
      v
  validate (Ch 30) then Save / publish (Ch 32)
```

### 6. Simple example

DCC export creates `/Chair` and nothing else, with no metadata. The hook sets `defaultPrim = Chair` and `kind = component`. Save then produces a referenceable entry layer.

### 7. USDA example

*After* the hook, the published layer's metadata block looks like this:

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "Chair" (
    kind = "component"
)
{
}
```

That block is what other shots pin (Ch 32). The hook's job is to make sure it exists even when the DCC GUI never showed a "defaultPrim" field.

### 8. Python example

```python
from pxr import Usd, UsdGeom


def pipeline_hooks(stage):
    fixes = []
    if not stage.HasDefaultPrim():
        roots = stage.GetPseudoRoot().GetChildren()
        if len(roots) == 1:
            stage.SetDefaultPrim(roots[0])
            fixes.append("defaultPrim")
    prim = stage.GetDefaultPrim()
    if prim and not Usd.ModelAPI(prim).GetKind():
        Usd.ModelAPI(prim).SetKind("component")
        fixes.append("kind")
    return fixes


stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/Chair")
print("before defaultPrim", stage.HasDefaultPrim())
print("before kind", bool(Usd.ModelAPI(
    stage.GetPrimAtPath("/Chair")).GetKind()))
print("fixes", pipeline_hooks(stage))
print("after defaultPrim", stage.GetDefaultPrim().GetName())
print("after kind", Usd.ModelAPI(stage.GetDefaultPrim()).GetKind())
print("fallback meters", stage.GetMetadata("metersPerUnit"))
print("fallback upAxis", UsdGeom.GetStageUpAxis(stage))
```

**Expected output**

```text
before defaultPrim False
before kind False
fixes ['defaultPrim', 'kind']
after defaultPrim Chair
after kind component
fallback meters 0.01
fallback upAxis Y
```

A fresh stage already has **fallback** `metersPerUnit = 0.01` and `upAxis = Y` (Ch 2, Ch 28). `GetMetadata` is therefore not `None`. A metrics hook must check **authored** metadata (`HasAuthoredMetadata`) before overwriting studio units. After this hook, the entry is at least pin-ready (`defaultPrim` + `kind`).

### 9. Real-world use case

Four DCCs (CAD, Maya, Blender, a custom tool) each `import studio_export_hooks` and run `pipeline_hooks(stage)` before Save. When the studio adds "identifier in `assetInfo`," one function changes; every exporter inherits it.

### 10. Common mistakes

> [!MISTAKE] Running hooks on the session layer. Nothing is saved. Fix: edit target = the layer you will publish.

> [!MISTAKE] Auto-setting `kind = component` on an assembly root. The hook must know the asset class. Fail instead of guessing when the type is ambiguous.

> [!MISTAKE] Skipping validation after a hook "because we just fixed it." Hooks can miss unresolved textures (Ch 33).

### 11. Exam traps

> [!TRAP] "Hooks are `Tf.Notice` listeners." They can be ordinary functions. Notices are Section 34.4, for live updates.

> [!TRAP] "`HasDefaultPrim()` is True on a fresh `CreateInMemory` stage." It is False until you set one.

> [!TRAP] Setting `defaultPrim` when two roots exist. A hook that picks the first prim silently is a pipeline bug.

### 12. Practice questions

**Q34.1-1.** Where in extract → transform → write → hooks → validate → Save do structural repairs belong?
A. Extract
B. Hooks
C. After Save, in git
D. Inside `Flatten` only

**Q34.1-2.** Select two safe auto-fixes for a hook.
A. `SetDefaultPrim` when there is exactly one root
B. `SetKind("component")` when kind is missing **and** the asset type is known to be a component
C. Delete every extra root prim to force a single `defaultPrim`
D. Replace all payloads with references so usdview is simpler

**Answers**

- **Q34.1-1: B.** Hooks repair; validate then Save.
- **Q34.1-2: A and B.** C destroys data; D changes composition on purpose and is not a metadata hook.

### 13. Exam takeaways

> [!KEY]
> - Hooks enforce pipeline structure after write, before Save.
> - Safe repairs: one-root `defaultPrim`, known `kind`, studio metrics.
> - Same hook list for every exporter; validate afterwards.
> - Hooks are functions; notices are a different tool.

---

## 34.2 `Flatten` vs `FlattenLayerStack` vs layer export

### 1. What is it?

Three ways to "write one file" that are **not** interchangeable. **Export** writes one layer's specs. **`FlattenLayerStack`** merges the root layer's **sublayers**. **`Flatten`** bakes the composed **stage** (Obj 1.9).

### 2. Why do we need it?

Sending `entry.usda` to a client who does not have your sublayers or your `ref.usda` gives them an incomplete scene. Sending a full Flatten may drop variants they still need. Picking the wrong tool is the usual delivery bug.

### 3. Beginner explanation

Export is photocopying **one** notebook page. FlattenLayerStack is taping the department pages of *this* binder into one sheet, while keeping "see also book X" footnotes (references). Flatten is rewriting the whole story as if there were never footnotes.

*Where the analogy breaks:* Flatten also turns `@./tex/t.png@` into an **absolute** path on *your* disk (Ch 22). You must rewrite paths before the client opens it.

### 4. Technical explanation

Verified on USD 26.08:

| Tool | Input | Arcs | Sublayers | Asset paths |
|------|-------|------|-----------|-------------|
| `root.Export` / `ExportToString` | One layer | Unchanged | Listed, not merged | Authored |
| `UsdUtils.FlattenLayerStack(stage)` | Root layer stack | References / payloads **kept** | Merged away (`subLayerPaths` empty) | Often **absolutized** |
| `stage.Flatten()` | Whole composed stage | Baked away | Baked away | Often **absolutized** |

Facts:

- Flatten of a referenced `Cube` child produces a local `Cube` spec with **no** `references =` (`typeName` is `Cube`).
- FlattenLayerStack of the same child **keeps** `prepend references`. The spec's own `typeName` may be **empty**; the Cube type still comes from the referenced file.
- Neither tool strips `customData` (Section 34.3).
- `usdcat --flatten` is the CLI for Flatten; not installed with `usd-core`.

> [!VERSION] Same APIs on 26.08 as in Chapter 22. This chapter is the **choice** table; Chapter 22 has the localize/USDZ package path.

### 5. Mental model

```text
  need the composed picture, no arcs     -> Flatten
  need one file of THIS stack, keep refs -> FlattenLayerStack
  need exactly what this layer authored  -> Export
```

### 6. Simple example

`entry.usda` sublayers `geo.usda` (a texture) and defines `/L/Bolt` as a reference to `ref.usda`. Export of entry has no texture attribute. FlattenLayerStack has the texture and still references Bolt. Flatten has the texture and a local Cube named Bolt.

### 7. USDA example

*File: entry.usda*

```usda
#usda 1.0
(
    defaultPrim = "L"
    subLayers = [
        @./geo.usda@
    ]
)

def Xform "L"
{
    def "Bolt" (
        prepend references = @./ref.usda@
    )
    {
    }
}
```

The texture lives in `geo.usda` as `over "L" { asset tex = @./tex/t.png@ }`. Flatten tools pull it up; Export of `entry.usda` does not.

### 8. Python example

```python
from pxr import Usd, UsdUtils
import os

os.makedirs("tex", exist_ok=True)
open("tex/t.png", "wb").write(b"x")
open("geo.usda", "w").write("""#usda 1.0
over "L"
{
    asset tex = @./tex/t.png@
}
""")
open("ref.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Bolt"
)
def Cube "Bolt" {}
""")
open("entry.usda", "w").write("""#usda 1.0
(
    defaultPrim = "L"
    subLayers = [@./geo.usda@]
)
def Xform "L"
{
    def "Bolt" (prepend references = @./ref.usda@) {}
}
""")

stage = Usd.Stage.Open("entry.usda")
root = stage.GetRootLayer()
print("Export has tex:", root.GetAttributeAtPath("/L.tex") is not None)
print("Export has subLayers:", bool(list(root.subLayerPaths)))

flat = stage.Flatten()
bolt = flat.GetPrimAtPath("/L/Bolt")
print("Flatten Bolt type:", bolt.typeName)
print("Flatten Bolt has ref:",
      bool(bolt.referenceList.prependedItems))
print("Flatten tex abs:",
      os.path.isabs(flat.GetAttributeAtPath("/L.tex").default.path))

ls = UsdUtils.FlattenLayerStack(stage)
bolt2 = ls.GetPrimAtPath("/L/Bolt")
print("FLS Bolt type:", bolt2.typeName or "-")
print("FLS Bolt has ref:",
      bool(bolt2.referenceList.prependedItems))
print("FLS subLayers empty:", list(ls.subLayerPaths) == [])
print("FLS tex abs:",
      os.path.isabs(ls.GetAttributeAtPath("/L.tex").default.path))
```

**Expected output**

```text
Export has tex: False
Export has subLayers: True
Flatten Bolt type: Cube
Flatten Bolt has ref: False
Flatten tex abs: True
FLS Bolt type: -
FLS Bolt has ref: True
FLS subLayers empty: True
FLS tex abs: True
```

Export missed the texture (it lives on a sublayer). Flatten baked the Cube. FlattenLayerStack kept the reference and still leaked an absolute texture path.

### 9. Real-world use case

A client can open USD but cannot reach your asset resolver. You FlattenLayerStack the entry (one file of your workstreams), then `ModifyAssetPaths` (next section), then `LocalizeAsset` so `ref.usda` and `t.png` travel in the folder. You do **not** Flatten if they still need to swap the Bolt asset later.

### 10. Common mistakes

> [!MISTAKE] Emailing `entry.usda` Export and wondering why the texture is gone. Fix: FlattenLayerStack or send the sublayers.

> [!MISTAKE] Flattening to "simplify" a shot that must keep variants. Unselected variants disappear.

> [!MISTAKE] Shipping Flatten output with `/home/you/.../tex/t.png`. Rewrite paths.

### 11. Exam traps

> [!TRAP] "`FlattenLayerStack` removes references." It removes **sublayers**. References stay.

> [!TRAP] "`Flatten` and `Export` are the same if the stage has one layer." Export still will not compose references *into* that layer.

> [!TRAP] "Absolute paths in Flatten mean the client can find the files." They point at *your* disk.

### 12. Practice questions

**Q34.2-1.** You must deliver one layer that still references the vendor Bolt file. Which tool?
A. `stage.Flatten()`
B. `UsdUtils.FlattenLayerStack(stage)`
C. `root.Export("out.usda")` of an entry that sublayers geo and never inlined Bolt
D. `Sdf.ChangeBlock`

**Q34.2-2.** Select two true results of `stage.Flatten()` in the example.
A. `/L/Bolt` is a `Cube` with no reference list
B. `tex` becomes an absolute path
C. `subLayers` remain on the result
D. `ref.usda` is still required to open Bolt

**Answers**

- **Q34.2-1: B.** Keeps references, merges sublayers. C still needs geo.usda on disk and does not by itself package Bolt.
- **Q34.2-2: A and B.** Arcs and sublayers are gone; Bolt is baked.

### 13. Exam takeaways

> [!KEY]
> - Export = one layer. FlattenLayerStack = merge sublayers, keep refs. Flatten = bake the stage.
> - Both flatten flavors absolutize asset paths.
> - Obj 1.9: pick the tool from what the *receiver* can open and override.

---

## 34.3 Removing proprietary dependencies

### 1. What is it?

**Proprietary dependencies** are files, URI schemes, plugins, and metadata an outside party should not receive: `/studio/rigs/...` references, `customData` owner names, internal `asset` attributes, resolver identifiers they cannot load. Removing them is the rest of Obj 1.9 after you pick a flatten tool.

### 2. Why do we need it?

Flatten and FlattenLayerStack **keep** `customData` and they **leak absolute paths**. A client with your `owner = "jdoe"` field and `@/mnt/show/tex/t.png@` has a broken, confidential package.

### 3. Beginner explanation

Before you send a cake recipe, you white-out "Mom's secret shelf in *our* pantry" and write "1 tsp vanilla" instead. You also take your name off the card.

*Where the analogy breaks:* USD will not white-out for you. `LocalizeAsset`'s `processingFunc` (Ch 22) can drop arcs; `ModifyAssetPaths` rewrites strings; `ClearCustomDataByKey` is manual.

### 4. Technical explanation

Three complementary cleanups (26.08):

| Job | API |
|-----|-----|
| Rewrite every asset path on a layer | `UsdUtils.ModifyAssetPaths(layer, fn)` — `fn` takes the authored path, returns the new string |
| Drop internal refs while copying a tree | `UsdUtils.LocalizeAsset(..., processingFunc)` returning empty `UsdUtils.DependencyInfo()` (Ch 22) |
| Strip private metadata | `prim.ClearCustomDataByKey("owner")`, `prim.ClearAssetInfo()`, `RemoveProperty` |

`ModifyAssetPaths` is the smallest tool for the flatten leak: after FlattenLayerStack, map absolute texture paths back to `./tex/t.png` if you will ship that relative file beside the layer.

Do not leave `@s3://...@` in a package for a client with no URI resolver (Ch 33).

### 5. Mental model

```text
  flatten or localize
       |
       +-- ModifyAssetPaths   (no /mnt, no s3 unless they have the plugin)
       +-- drop internal arcs (processingFunc / ClearReferences)
       +-- clear customData / assetInfo secrets
       +-- reopen and ComputeAllDependencies  (unresolved == [])
```

### 6. Simple example

FlattenLayerStack wrote `@/tmp/.../tex/t.png@`. `ModifyAssetPaths(layer, lambda p: "./tex/t.png")` makes the attribute portable. `ClearCustomDataByKey("owner")` removes the artist name.

### 7. USDA example

*Before cleanup* (what FlattenLayerStack emitted in spirit):

```usda
#usda 1.0
(
    defaultPrim = "L"
)

def Xform "L" (
    customData = {
        string owner = "jdoe"
    }
)
{
    asset tex = @/tmp/show/tex/t.png@
}
```

Both the `owner` key and the `/tmp/...` path must not ship.

### 8. Python example

```python
from pxr import Sdf, Usd, UsdUtils


layer = Sdf.Layer.CreateAnonymous(".usda")
layer.ImportFromString("""#usda 1.0
(
    defaultPrim = "L"
)
def Xform "L" (
    customData = { string owner = "jdoe" }
)
{
    asset tex = @/mnt/show/tex/t.png@
}
""")

print("before tex:", layer.GetAttributeAtPath("/L.tex").default)
print("before owner:", dict(layer.GetPrimAtPath("/L").customData))

UsdUtils.ModifyAssetPaths(layer, lambda p: "./tex/t.png")
stage = Usd.Stage.Open(layer)
stage.GetPrimAtPath("/L").ClearCustomDataByKey("owner")
print("after tex:", layer.GetAttributeAtPath("/L.tex").default)
print("after owner:", dict(layer.GetPrimAtPath("/L").customData))
```

**Expected output**

```text
before tex: @/mnt/show/tex/t.png@
before owner: {'owner': 'jdoe'}
after tex: @./tex/t.png@
after owner: {}
```

`ClearCustomDataByKey` is a **Usd.Prim** method (Ch 22). Sdf `PrimSpec` has `customData` you can assign; it does not have `ClearCustomDataKey`.

### 9. Real-world use case

A vendor delivery: FlattenLayerStack the internal entry, `processingFunc` drops `@/studio/...@`, `ModifyAssetPaths` forces `./`, `customData` wiped, then `CreateNewUsdzPackage` (Ch 31). The vendor opens the USDZ on a laptop with no studio resolver.

### 10. Common mistakes

> [!MISTAKE] Flattening and calling it "sanitized." Secrets in `customData` survived.

> [!MISTAKE] `ModifyAssetPaths` that returns `""` for every path. You just deleted every texture link. Return a real relative path or handle that file in `processingFunc`.

> [!MISTAKE] Cleaning the in-memory Flatten layer and forgetting to `Export` it. The original `entry.usda` is unchanged.

### 11. Exam traps

> [!TRAP] "`LocalizeAsset` strips `customData`." It copies files; metadata stays (Ch 22).

> [!TRAP] "Absolute paths are required in Flatten output." They are a side effect you are expected to fix.

### 12. Practice questions

**Q34.3-1.** After FlattenLayerStack, textures are `@/home/td/show/tex/a.png@`. Best next step for a client folder that will contain `tex/a.png`?
A. `UsdUtils.ModifyAssetPaths(layer, fn)` returning `./tex/a.png`
B. `Sdf.ChangeBlock`
C. `SetKind("component")`
D. `MuteLayer` of the texture

**Q34.3-2.** Select two items that survive Flatten and must be removed by hand or `processingFunc`.
A. `customData` artist names
B. Internal `@/studio/rigs/...@` references (FlattenLayerStack)
C. Unselected variant specs (they already died in Flatten)
D. The session layer

**Answers**

- **Q34.3-1: A.** Rewrite the leaked absolute path.
- **Q34.3-2: A and B.** Flatten already dropped unselected variants; the session layer is not saved.

### 13. Exam takeaways

> [!KEY]
> - Flatten is not a confidentiality tool.
> - `ModifyAssetPaths` fixes leaked absolute paths.
> - Clear `customData` / internal arcs yourself (or via `processingFunc`).
> - Re-open and inventory (`ComputeAllDependencies`) before you ship.

---

## 34.4 Change notifications (`Tf.Notice`, `Usd.Notice`)

### 1. What is it?

A **notice** is USD's callback: something changed, here is what. `Tf.Notice.Register(Usd.Notice.ObjectsChanged, callback, stage)` runs your function on that stage. Live DCC exporters and UIs use this instead of polling `Traverse()` every frame.

### 2. Why do we need it?

A DCC that re-exports the whole stage on every translate is slow and fights the user. A listener that hears `/World/Prop.xformOp:translate` can write **only** that opinion into `anim.usda`. Pipeline round-trips (Ch 35) sit on this.

### 3. Beginner explanation

A doorbell, not a security camera you stare at. USD rings `ObjectsChanged` when prims or properties change. You look through the peephole (`GetResyncedPaths`, `GetChangedInfoOnlyPaths`) and decide whether to open the door (update the DCC, dirty a hook).

*Where the analogy breaks:* one user action can ring **more than once** (creating an attribute then setting it). Batch with ChangeBlock (Section 34.5) so you get one ring.

### 4. Technical explanation

Verified on USD 26.08. Notice types on `Usd.Notice`:

| Type | When |
|------|------|
| `ObjectsChanged` | Prims/properties authored or resynced |
| `StageContentsChanged` | Broader "the stage changed" |
| `StageEditTargetChanged` | `SetEditTarget` |
| `LayerMutingChanged` | `MuteLayer` / unmute |
| `StageNotice` | Base type |

`ObjectsChanged` payload:

- `GetResyncedPaths()` — prim index rebuilt (new prim, type change, composition change).
- `GetChangedInfoOnlyPaths()` — value/metadata change, no resync.

Register:

```{.python .norun}
listener = Tf.Notice.Register(
    Usd.Notice.ObjectsChanged, callback, stage)
# callback(notice, sender)
listener.Revoke()
```

The callback is `fn(notice, sender)`. `sender` is the stage you passed. **Revoke on the listener object** (`listener.Revoke()`). There is no `Tf.Notice.Revoke(key)` on 26.08.

Creating `/W` resynced `['/W']`. Creating and setting attribute `a` produced **two** notices in a probe: one resync of `/W.a`, one info-only `/W.a`. Do not assume one Python call equals one notice.

### 5. Mental model

```text
  Td.Notice.Register(ObjectsChanged, fn, stage)
        ^
        |  DefinePrim  -> resync paths
        |  Set value   -> info-only (sometimes plus resync on create)
        |
  fn reads paths, updates DCC or flags "run hooks"
  listener.Revoke()  when the tool closes
```

### 6. Simple example

A USD outliner in a DCC registers `ObjectsChanged`. On resync of `/W`, it adds a row. On info-only `/W.a`, it refreshes that cell only.

### 7. USDA example

Notices are runtime. This is the layer the listener is watching; nothing in USDA registers a callback.

```usda
#usda 1.0

def Xform "W"
{
    double a = 1
}
```

### 8. Python example

```python
from pxr import Tf, Usd, Sdf, UsdGeom

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
print("n after set", len(hits))
for h in hits:
    print(" resync", h[0], "info", h[1])

print("types:", sorted(
    n for n in dir(Usd.Notice) if n[0].isupper()))
listener.Revoke()
```

**Expected output**

```text
after define [(['/W'], [])]
n after set 2
 resync ['/W.a'] info []
 resync [] info ['/W.a']
types: ['LayerMutingChanged', 'ObjectsChanged', 'StageContentsChanged', 'StageEditTargetChanged', 'StageNotice']
```

Define = one resync. CreateAttribute + Set = two notices. Revoke so the listener does not outlive the tool.

### 9. Real-world use case

A DCC "USD layer" mode registers `ObjectsChanged` on the opened shot. Translating a prop writes into the animation edit target. The listener marks that layer dirty in the UI. Closing the scene calls `listener.Revoke()` so a deleted stage is not pinged.

### 10. Common mistakes

> [!MISTAKE] `Tf.Notice.Revoke(listener)` — that API is not on `Tf.Notice` in 26.08. Call `listener.Revoke()`.

> [!MISTAKE] Doing heavy work (full flatten, full validate) in the callback. You will hitch. Set a dirty flag; run hooks on idle.

> [!MISTAKE] Registering globally when you meant one stage. Pass the stage as the third argument.

### 11. Exam traps

> [!TRAP] "One `Set()` is one notice." Attribute create + set was two.

> [!TRAP] "`GetChangedInfoOnlyPaths` includes new prims." New prims are **resync** paths.

> [!TRAP] Notices persist after the stage is destroyed if you forget `Revoke`.

### 12. Practice questions

**Q34.4-1.** How do you stop listening?
A. `Tf.Notice.Revoke(listener)`
B. `listener.Revoke()`
C. `stage.MuteLayer`
D. `Sdf.ChangeBlock`

**Q34.4-2.** Select two `Usd.Notice` types.
A. `ObjectsChanged`
B. `LayerMutingChanged`
C. `LIVERPSChanged`
D. `FlattenNotice`

**Answers**

- **Q34.4-1: B.** The object returned by `Register` has `Revoke`.
- **Q34.4-2: A and B.** There is no LIVERPS notice.

### 13. Exam takeaways

> [!KEY]
> - `Tf.Notice.Register(Usd.Notice.ObjectsChanged, fn, stage)`.
> - Resync vs info-only paths; one call can send two notices.
> - `listener.Revoke()` — not `Tf.Notice.Revoke`.
> - Use notices for live DCC; use hooks for batch export.

---

## 34.5 `Sdf.ChangeBlock` for performance

### 1. What is it?

`Sdf.ChangeBlock` is a context manager that **holds** scene-description notices until the block ends, then delivers **one** combined update. Obj 6.1: identify when that removes a bottleneck.

### 2. Why do we need it?

Each Sdf spec you create can resync the stage and ping every `ObjectsChanged` listener (Section 34.4). A thousand spheres without a block means a thousand UI refreshes. With a block, the outliner updates once.

### 3. Beginner explanation

A change block is "pause email notifications while I file 200 messages, then send one digest."

*Where the analogy breaks:* nested blocks are reference-counted; the digest goes out when the **outermost** `with` exits. And `Usd.Stage.DefinePrim` / some schema `Define` calls may **fail inside** a block because the stage has not resynced the parent yet. Author **Sdf specs** inside the block (Ch 8).

### 4. Technical explanation

Verified on USD 26.08:

```text
with Sdf.ChangeBlock():
    Sdf.PrimSpec(parent_spec, "S0", Sdf.SpecifierDef, "Sphere")
    ...
# one ObjectsChanged with all new paths
```

Probe: three `Sdf.PrimSpec` children **inside** a block → **1** notice listing `/W/S0`, `/W/S1`, `/W/S2`. The same three **outside** → **3** notices.

Obj 6.1 answer: ChangeBlock helps when **many small Sdf (or Usd) edits** would each trigger indexing and listeners. It does **not** make `Save()` or disk fsync faster. It does **not** skip LIVERPS; it delays *notification* of composition.

`UsdGeom.Sphere.Define(stage, "/W/S0")` inside a ChangeBlock **raised** `Failed to define UsdPrim` in a 26.08 probe even though `/W` already existed. Prefer Sdf authoring inside the block; let the stage catch up at the end.

### 5. Mental model

```text
  without:  edit -> notice -> edit -> notice -> edit -> notice
  with:     [ edit edit edit ] -> one notice
```

### 6. Simple example

A procedural city exporter writes 10,000 building Xforms. Wrap the Sdf loop in `ChangeBlock`. The DCC outliner (registered in Section 34.4) redraws once.

### 7. USDA example

ChangeBlock does not appear in USDA. The result after the block is ordinary specs:

```usda
#usda 1.0

def Xform "W"
{
    def Sphere "S0" {}
    def Sphere "S1" {}
    def Sphere "S2" {}
}
```

### 8. Python example

```python
from pxr import Tf, Usd, Sdf, UsdGeom

hits = []


def on_changed(notice, sender):
    hits.append([str(p) for p in notice.GetResyncedPaths()])


stage = Usd.Stage.CreateInMemory()
layer = stage.GetRootLayer()
UsdGeom.Xform.Define(stage, "/W")
parent = layer.GetPrimAtPath("/W")

listener = Tf.Notice.Register(
    Usd.Notice.ObjectsChanged, on_changed, stage)
hits.clear()

with Sdf.ChangeBlock():
    for i in range(3):
        Sdf.PrimSpec(parent, f"S{i}", Sdf.SpecifierDef, "Sphere")
print("inside block notices", len(hits), hits)

hits.clear()
for i in range(3, 6):
    Sdf.PrimSpec(parent, f"S{i}", Sdf.SpecifierDef, "Sphere")
print("outside block notices", len(hits), hits)
listener.Revoke()
```

**Expected output**

```text
inside block notices 1 [['/W/S0', '/W/S1', '/W/S2']]
outside block notices 3 [['/W/S3'], ['/W/S4'], ['/W/S5']]
```

That 1-versus-3 count *is* Obj 6.1. The bottleneck is "too many notices / resyncs," not "USD cannot write spheres."

### 9. Real-world use case

A CAD tessellator used to call `UsdGeom.Mesh.Define` per part while a Hydra view listened to `ObjectsChanged`. The view froze. Moving the inner loop to `Sdf.PrimSpec` + `ChangeBlock` dropped export from minutes to seconds; the view refreshed once (Ch 8's micro-benchmark, Ch 44 continues the story).

### 10. Common mistakes

> [!MISTAKE] Wrapping `DefinePrim` of new children inside ChangeBlock and catching unexplained failures. Fix: author `Sdf.PrimSpec` in the block.

> [!MISTAKE] Believing ChangeBlock writes USDC faster. It batches **notices**, not I/O.

> [!MISTAKE] Leaving a ChangeBlock open across user interaction. The UI sees a stale stage until the `with` ends.

### 11. Exam traps

> [!TRAP] "ChangeBlock skips composition / LIVERPS." It delays **notification**.

> [!TRAP] "Always use ChangeBlock." One `Set()` does not need it. Obj 6.1 is *when*: many edits, live listeners.

> [!TRAP] Counting Python loop iterations instead of notices. The exam cares that listeners ran once.

### 12. Practice questions

**Q34.5-1.** Three `Sdf.PrimSpec` calls inside one `Sdf.ChangeBlock` typically produce how many `ObjectsChanged` notices?
A. 0
B. 1
C. 3
D. One per attribute on each prim

**Q34.5-2.** Select two true statements (Obj 6.1).
A. ChangeBlock helps when many small edits would each resync listeners
B. ChangeBlock is the right tool to speed up `layer.Save()` to a slow NAS
C. `UsdGeom.Sphere.Define` inside a block may fail; prefer Sdf specs
D. ChangeBlock removes the need for exporter hooks

**Answers**

- **Q34.5-1: B.** One combined resync. Proven in step 8.
- **Q34.5-2: A and C.** Save/I/O and hooks are different problems.

### 13. Exam takeaways

> [!KEY]
> - Obj 6.1: ChangeBlock = many edits, one notice / one resync.
> - Author **Sdf** inside the block; schema `Define` may fail until flush.
> - It is not a disk optimization and not a substitute for hooks.
> - Nested blocks flush on the outermost exit.

---

## Chapter lab(s)

**Lab 30** (notices and change blocks) is this chapter: register `ObjectsChanged`, prove 1-vs-N notices with `ChangeBlock`, run a flatten + `ModifyAssetPaths` delivery. Lab 28 covers localize/USDZ. Lab 25/29 cover the exporter that should call `pipeline_hooks`.

## USDA reading exercises

**Exercise 34-A.** A delivery layer still contains `prepend references = @./bolt.usda@` and `asset tex = @/home/td/tex/a.png@`. Which flatten tool was probably used, and what two cleanups remain?

**Exercise 34-B.** An exporter calls `UsdGeom.Sphere.Define` 500 times inside `with Sdf.ChangeBlock():` and raises `Failed to define UsdPrim`. What should it do instead?

**Answers**

- **34-A.** `FlattenLayerStack` (references survived). Still need `ModifyAssetPaths` to a relative texture and to ship `bolt.usda` (or Flatten / localize it).
- **34-B.** Author `Sdf.PrimSpec` (and attribute specs) inside the block; let Usd see the prims after the block ends. Or Define outside a block.

## Chapter review

**Summary**

- Hooks repair structure (`defaultPrim`, `kind`, metrics) before Save.
- Export vs FlattenLayerStack vs Flatten: one layer / merge sublayers keep refs / bake stage.
- Both flatten tools leak absolute asset paths; `ModifyAssetPaths` and `customData` cleanup are part of Obj 1.9.
- `Tf.Notice.Register(ObjectsChanged, fn, stage)`; `listener.Revoke()`.
- ChangeBlock: 3 Sdf edits → 1 notice (Obj 6.1); do not DefinePrim inside blindly.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| Missing `defaultPrim` on export | Hook did not run |
| Client missing texture, file was a sublayer | They got Export, not FlattenLayerStack |
| Client still needs to retarget Bolt | Do not Flatten; FlattenLayerStack + send Bolt |
| `@/mnt/show/...@` in a package | `ModifyAssetPaths` |
| `owner = "jdoe"` after Flatten | Strip `customData` |
| UI hitches every prim | ChangeBlock + Sdf |
| `Failed to define UsdPrim` in a block | Use Sdf specs |
| `Tf.Notice.Revoke` | Wrong; `listener.Revoke()` |

**Review questions**

**R34-1** (Obj 1.9) Best description of `stage.Flatten()`?
A. Merge sublayers, keep references
B. Bake the composed stage into one layer; arcs go away
C. Write only the root layer's specs
D. Zip a USDZ

**R34-2** (Obj 1.9) Select two FlattenLayerStack results from this chapter's example.
A. `/L/Bolt` still has a reference
B. `tex` is typically an absolute path
C. `subLayers` remain pointing at `geo.usda`
D. `customData` is automatically cleared

**R34-3** (Obj 1.9) `UsdUtils.ModifyAssetPaths` is for:
A. Muting layers
B. Rewriting asset-path strings on a layer
C. Registering notices
D. Setting `kind`

**R34-4** (Obj 6.1) Three Sdf specs inside one ChangeBlock produced how many `ObjectsChanged` notices here?
A. 1
B. 3
C. 0
D. 6

**R34-5** (Obj 6.1) Select two reasons ChangeBlock is the right diagnosis.
A. A live listener redraws on every notice
B. You are creating thousands of specs in a loop
C. `Save()` to NFS is slow
D. LIVERPS is in the wrong order

**R34-6** (Obj 1.9) A hook should set `defaultPrim` when:
A. Always, picking `GetPseudoRoot()`
B. There is exactly one root prim and none is set
C. After Flatten only
D. Never; only artists may set it

**R34-7** (Obj 6.1) How do you unregister a notice listener on 26.08?
A. `listener.Revoke()`
B. `Tf.Notice.Revoke(listener)`
C. `stage.Close()`
D. Delete the callback function

**R34-8** (Obj 1.9) Export of `entry.usda` did not include `tex`. Why?
A. `tex` was authored on a **sublayer**
B. Asset attributes cannot export
C. Flatten is required to store `asset` types
D. `defaultPrim` was missing

**R34-9** (Obj 1.9) Select two proprietary items to strip before a client package.
A. `customData` owner
B. Internal `/studio/` references
C. `defaultPrim`
D. `kind = component`

**R34-10** (Obj 6.1) `UsdGeom.Sphere.Define` inside `Sdf.ChangeBlock` in a 26.08 probe:
A. Is always the recommended pattern
B. May raise `Failed to define UsdPrim`; use `Sdf.PrimSpec` instead
C. Skips LIVERPS
D. Writes USDC directly

**R34-11** (Obj 1.9) After Flatten, a referenced Cube child is:
A. Still a reference
B. A local typed spec with no reference list
C. Deleted
D. Moved to the session layer

**R34-12** (Obj 6.1) `GetResyncedPaths()` vs `GetChangedInfoOnlyPaths()`:
A. Resync = prim index rebuilt; info-only = value/metadata without resync
B. They are aliases
C. Info-only is only for sublayers
D. Resync paths are always empty inside ChangeBlock

**Review answers**

- **R34-1: B.** Review: §34.2.
- **R34-2: A and B.** Sublayers merge away; metadata stays. Review: §34.2–34.3.
- **R34-3: B.** Review: §34.3.
- **R34-4: A.** Review: §34.5.
- **R34-5: A and B.** Review: §34.5.
- **R34-6: B.** Review: §34.1.
- **R34-7: A.** Review: §34.4.
- **R34-8: A.** Review: §34.2.
- **R34-9: A and B.** Keep identifier metadata the client needs. Review: §34.3.
- **R34-10: B.** Review: §34.5.
- **R34-11: B.** Review: §34.2.
- **R34-12: A.** Review: §34.4.

## Further reading

- [S06] OpenUSD API — `UsdStage::Flatten`, `UsdUtilsFlattenLayerStack`, `UsdNotice`, `SdfChangeBlock`. https://openusd.org/release/api/index.html
- [S04] OpenUSD Glossary — Flatten, Layer stack. https://openusd.org/release/glossary.html
- Chapter 22 (localize / USDZ delivery), Chapter 8 (ChangeBlock intro), Chapter 29 (exporter shape).
