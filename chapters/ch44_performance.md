# Chapter 44 — Performance: Load and Render Times

> **Exam domain:** Debugging & Troubleshooting (11%) · **Objectives:** 6.1, 6.4 · **Study day:** 12 · **Est. time:** 90 min
> **Prerequisites:** Ch 17 (payloads), Ch 24–26 (instancing), Ch 31 (USDA/USDC), Ch 34 (ChangeBlock, notices), Ch 39 (extent, purpose), Ch 42–43 (measure before you guess)

A "slow USD" ticket is usually one of five things: **too much I/O** (ASCII USDA, no payloads), **too many prims in memory** (no instancing, no mask), **too many notices** (edits outside a ChangeBlock), **too much to draw** (no purpose/extent/drawMode), or **recomposing the world** on every keystroke. Obj 6.1 is ChangeBlock and batched edits. Obj 6.4 is the visual side of speed (culling, purpose, extents). This chapter is the checklist you run after Chapter 42 found that the *data* is correct.

Do not optimize from folklore. Trace (Chapter 43) times a step; then pick the knob below that matches the step.

## Learning goals

- Name the usual load-time vs render-time costs and which file/stage APIs address each.
- Open with `LoadNone`, `Load`, `FindLoadable`, and `OpenMasked`.
- Explain why native instancing cuts memory and why `Traverse()` looks "too small."
- Batch edits in `Sdf.ChangeBlock` and count `ObjectsChanged` notices (Obj 6.1).
- Author extent, purpose, and `model:drawMode` so Hydra can skip work (Obj 6.4).
- Walk a performance checklist without flattening first.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **USDC / crate** | Binary USD; faster and smaller than USDA for big geometry. |
| **Payload** | A lazy reference; unloaded until `Load`. |
| **Load rules** | Which payloads are in memory (`LoadAll` / `LoadNone` / per-path). |
| **Population mask** | Which *prim paths* exist on the stage at all (`OpenMasked`). |
| **Native instancing** | Many instance roots share one prototype in memory. |
| **ChangeBlock** | Batches scene description edits so notices fire once (Obj 6.1). |
| **Extent** | Axis-aligned box Hydra uses to cull. |
| **Purpose** | `default` / `render` / `proxy` / `guide` — what a renderer includes. |
| **Draw mode** | Model-level Hydra shortcut: `bounds`, `cards`, `origin`, … |

---

## 44.1 What makes stages slow

### 1. What is it?
**Load time** is opening layers, composing prims, and resolving assets. **Edit time** is how long a `Set` takes (notices, recomp). **Render time** is how long Hydra spends on the composed result. A slow *session* can be any mix; the fix is different for each.

### 2. Why do we need it?
People "optimize" by flattening (which *increases* memory) or by converting to USDA (which *increases* parse time). Naming the bucket first is Obj 6.1/6.4 hygiene.

### 3. Beginner explanation
Opening a warehouse (load), rearranging boxes (edit), photographing the floor (render). A crate (USDC) is a packed pallet — faster to fork-lift than a pile of labelled sticky notes (USDA). Payloads are rooms you do not unlock. Instancing is one chair prototype stamped a thousand times.

*Where the analogy breaks:* flattening is photocopying every room into one giant hall. It can make *render* of a one-file delivery simpler and still make *load* of the working scene worse. Flatten is a publish tool (Chapter 34), not a speed ritual.

### 4. Technical explanation
Typical costs (what to measure with Trace):

| Bucket | Cost | First knobs |
|--------|------|-------------|
| Parse / I/O | USDA text parse, many tiny files | USDC; fewer layers; `usdcat --flatten` only at deliver |
| Composition | Huge prim indexes, many arcs | Payloads, masks, simpler graphs (Ch 22) |
| Memory | Duplicate meshes | Instancing, payloads, masks |
| Notices / Python | Thousands of `ObjectsChanged` | `Sdf.ChangeBlock` (Obj 6.1) |
| Asset resolve | Thousands of `Resolve` | Package / USDZ; search-path hygiene (Ch 33) |
| Draw | Every mesh, every frame | `purpose`, `extent`, draw modes, vis |

- `Sdf.FileFormat.FindByExtension("usda").formatId` is `usda`; `"usdc"` is `usdc`. The `"usd"` id is a wrapper: `CreateNew("x.usd")` still has formatId `usd`, but `GetUnderlyingFormatForLayer` is **`usdc`** and the file starts with magic `PXR-USDC` (Chapter 31).
- Session layer + many sublayers is fine; **hundreds of sublayers** that each delta one prim is not (composition cost).
- `GetUsedLayers()` size is a cheap "how many files did I actually open?" probe.

### 5. Mental model

```text
LOAD     parse USDC/USDA → compose (Pcp) → resolve assets
EDIT     author spec → notices → maybe recompose
DRAW     traverse imageable prims → cull extent/purpose → shade

Ask which bar is long (Trace) before turning a knob.
```

### 6. Simple example
A 20 MB USDA mesh file takes longer to `Stage.Open` than the same data as USDC. The composed prim count is identical. Switching format fixes **load**, not **draw**.

### 7. USDA example

A working-scene pattern that stays fast to open: payloads for heavy geo, USDA only for the shot list.

```usda
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def "City" (
        prepend payload = @./city.usdc@
    )
    {
    }

    def Camera "ShotCam"
    {
    }
}
```

- The shot file is tiny USDA (diffable). The city is crate, behind a payload.

### 8. Python example

```python
from pxr import Sdf

print("usda id:", Sdf.FileFormat.FindByExtension("usda").formatId)
print("usdc id:", Sdf.FileFormat.FindByExtension("usdc").formatId)
print("usd id:", Sdf.FileFormat.FindByExtension("usd").formatId)
layer = Sdf.Layer.CreateNew("tmp.usd")
print("CreateNew .usd formatId:", layer.GetFileFormat().formatId)
usd_fmt = Sdf.FileFormat.FindByExtension("usd")
print("underlying:", usd_fmt.GetUnderlyingFormatForLayer(layer))
layer.Save()
with open("tmp.usd", "rb") as fh:
    print("magic:", fh.read(8))
```

**Expected output**
```text
usda id: usda
usdc id: usdc
usd id: usd
CreateNew .usd formatId: usd
underlying: usdc
magic: b'PXR-USDC'
```

`.usd` without a format hint is **crate** on disk (magic `PXR-USDC`). The format *id* stays `usd`; ask `GetUnderlyingFormatForLayer` or read the bytes. That is a load-time win and a diff-time loss — pick on purpose (Chapter 31).

### 9. Real-world use case
A games exporter wrote every prop as USDA "so we can git diff." Opening a level took 40 s. Switching published geometry to USDC (keeping shot layers USDA) cut open to 6 s. Git still diffs the shot; geometry diffs happen in DCC, not in text.

### 10. Common mistakes
> [!MISTAKE] Flattening the working scene to "make it faster." You pay composition *once* at flatten, then carry a giant file forever.

> [!MISTAKE] Measuring `ExportToString` time and calling it load time. That is ASCII serialize, the opposite direction.

> [!MISTAKE] Optimizing draw when Trace says `Sdf.Layer.Open` is 90% of the hitch.

### 11. Exam traps
> [!TRAP] USDA is always faster because it is smaller to think about. Binary crate is faster to **parse**.

> [!TRAP] `.usd` means USDA. Default **crate** (`PXR-USDC`); formatId is still the wrapper `usd`.

> [!TRAP] "More sublayers always slower than one file." A few workstream sublayers are the design (Ch 22). Hundreds of tiny deltas are the smell.

### 12. Practice questions
1. Which format parses faster for large meshes, USDA or USDC?
2. What formatId does `FindByExtension("usd")` return, and what is on disk after `CreateNew("x.usd")`?
3. Flattening a working scene primarily helps which *delivery* case?

**Answers**
1. **USDC.**
2. **Id `usd`; on disk crate (`usdc` / `PXR-USDC`).**
3. **A single-file package for a consumer who will not compose the original graph.**

### 13. Exam takeaways
> [!KEY]
> - Split load / edit / draw before changing files.
> - USDC for heavy geometry; USDA for small authored shots.
> - `.usd` wraps crate (`formatId` `usd`, underlying `usdc`).
> - Trace the slow bar; then pick the matching section below.

---

## 44.2 USDC, payloads, masks, load rules

### 1. What is it?
Three *stage population* knobs: **payloads** (lazy arcs), **load rules** (`LoadAll` / `LoadNone` / `Load(path)`), and **population masks** (`OpenMasked`) that omit prims entirely. USDC is the file-format partner: payload targets should be crate.

### 2. Why do we need it?
Opening a city to edit one shop should not compose every brick. `LoadNone` keeps payload *roots* so you can pick which to load. A mask is stricter: prims outside the mask **do not exist** on that stage.

### 3. Beginner explanation
Payloads are locked rooms; load rules are which keys you brought; a population mask is a floor plan that omits whole wings from the building. References are open doors — they always load (Chapter 42.2).

*Where the analogy breaks:* `FindLoadable()` lists payload paths, not references. Masking `/World/A` also drops `/World/B` *and* referenced `/World/C`.

### 4. Technical explanation
- `Usd.Stage.Open(path)` defaults to **`LoadAll`**. `Open(path, Usd.Stage.LoadNone)` leaves payloads unloaded; **references still compose** (verified).
- `stage.FindLoadable()` → payload prim paths (`/World/A`, `/World/B`). `stage.Load("/World/A")` / `Unload` / `LoadAndUnload`.
- `stage.GetLoadRules()` → `Usd.StageLoadRules`. `GetEffectiveRuleForPath` after an explicit `Load` is **`AllRule`**. Other rules: `NoneRule`, `OnlyRule`, `LoadWithDescendants` / `WithoutDescendants`.
- **`Usd.Stage.OpenMasked(path, mask)`** with `Usd.StagePopulationMask()` + `mask.Add("/World/A")`. TraverseAll is `/World`, `/World/A`, and descendants. `/World/B` is **invalid**. This is not unload — the prims were never populated.
- Payload targets as **USDC** give you lazy *and* fast parse when you do load them.
- Masks are for tools (a sim that only needs `/World/Chars`). Load rules are for interactive working sets (usdview load/unload).

> [!VERSION] Verified on USD 26.08. `Open(path, mask)` is not a valid overload; use **`OpenMasked`**. `Open(path, Usd.Stage.LoadNone)` is valid.

### 5. Mental model

```text
LoadNone     A,B exist, unloaded     C (reference) fully there
Load(A)      A populated             B still unloaded
OpenMasked{A}  only /World/A tree    B and C are not on the stage
```

### 6. Simple example
Shot with payloads A, B and reference C. `LoadNone`: A/B unloaded, C has `/Hi`. `FindLoadable` = A, B. `Load(A)` brings `/World/A/Hi`. `OpenMasked` `{/World/A}`: B invalid, C invalid.

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    def "A" (
        prepend payload = @./geo.usdc@
    )
    {
    }

    def "B" (
        prepend payload = @./geo.usdc@
    )
    {
    }

    def "C" (
        prepend references = @./geo.usdc@
    )
    {
    }
}
```

- Same target file; payload vs reference decides *when* it costs memory.

### 8. Python example

```python
from pxr import Usd

open("geo.usda", "w").write("""#usda 1.0
(
    defaultPrim = "P"
)
def Xform "P"
{
    def Mesh "Hi"
    {
    }
    def Mesh "Lo"
    {
    }
}
""")
open("shot.usda", "w").write("""#usda 1.0
def Xform "World"
{
    def "A" (
        prepend payload = @./geo.usda@
    )
    {
    }
    def "B" (
        prepend payload = @./geo.usda@
    )
    {
    }
    def "C" (
        prepend references = @./geo.usda@
    )
    {
    }
}
""")

stn = Usd.Stage.Open("shot.usda", Usd.Stage.LoadNone)
print("LoadNone traverseAll:",
      [str(p.GetPath()) for p in stn.TraverseAll()])
print("FindLoadable:", sorted(str(p) for p in stn.FindLoadable()))
stn.Load("/World/A")
print("after Load A/Hi:", stn.GetPrimAtPath("/World/A/Hi").IsValid(),
      "B loaded:", stn.GetPrimAtPath("/World/B").IsLoaded())
print("rule A:", stn.GetLoadRules().GetEffectiveRuleForPath("/World/A"))

mask = Usd.StagePopulationMask()
mask.Add("/World/A")
stm = Usd.Stage.OpenMasked("shot.usda", mask)
print("masked traverseAll:",
      [str(p.GetPath()) for p in stm.TraverseAll()])
print("masked B valid:", stm.GetPrimAtPath("/World/B").IsValid())
```

**Expected output**
```text
LoadNone traverseAll: ['/World', '/World/A', '/World/B', '/World/C', '/World/C/Hi', '/World/C/Lo']
FindLoadable: ['/World/A', '/World/B']
after Load A/Hi: True B loaded: False
rule A: Usd.StageLoadRules.AllRule
masked traverseAll: ['/World', '/World/A', '/World/A/Hi', '/World/A/Lo']
masked B valid: False
```

C's children appear under `LoadNone` because C is a **reference**. Masking `/World/A` drops B *and* C.

### 9. Real-world use case
A layout DCC opens the shot with `LoadNone`, then loads only `/World/Set/Building_12` when the artist selects it. A crowd sim uses `OpenMasked` on `/World/Agents` so character caches never even compose the set.

### 10. Common mistakes
> [!MISTAKE] Using references for hero buildings you wanted lazy. Switch those arcs to **payloads**.

> [!MISTAKE] `Open(path, mask)` — that overload does not exist. **`OpenMasked`**.

> [!MISTAKE] Expecting `FindLoadable()` to list referenced prims. It lists **payloads**.

### 11. Exam traps
> [!TRAP] `LoadNone` unloads references. It does not.

> [!TRAP] Masked-out prims are unloaded payloads. They are **not on the stage** (`IsValid` False).

> [!TRAP] `Load("/World/A")` loads B too. It does not; rules are per path (with descendant policy).

### 12. Practice questions
1. `LoadNone`: is a referenced prim's geometry composed?
2. Which API opens a stage that omits prims not in a path set?
3. `FindLoadable()` returns what kind of path?

**Answers**
1. **Yes.**
2. **`Usd.Stage.OpenMasked`.**
3. **Payload (loadable) prim paths.**

### 13. Exam takeaways
> [!KEY]
> - Payloads + `LoadNone` / `Load` = working set. References always compose.
> - `OpenMasked` + `StagePopulationMask` omits prims entirely.
> - `FindLoadable` = payload paths. `GetLoadRules` for the policy.
> - Put heavy payload targets in USDC.

---

## 44.3 Instancing for memory and speed

### 1. What is it?
**Native scenegraph instancing** (`instanceable = true` on a referencing prim) stores descendant specs **once** on a **prototype**. A thousand chairs share `/__Prototype_1`. Draw and memory scale with unique prototypes, not with instance count (Chapter 24).

### 2. Why do we need it?
Duplicating a 50k-face mesh 2 000 times without instancing is the classic "stage is 12 GB and usdview crawls" bug. Point instancers (Chapter 25) are the next step for tens of thousands of cheap copies.

### 3. Beginner explanation
A rubber stamp vs 2 000 carved copies. The stamp is the prototype. `Traverse()` visits stamp handles, not every carved groove — that is why the list looks short, not why the chairs are missing (Chapter 42.2).

*Where the analogy breaks:* instance *roots* can still have local overs (translate each chair). Overs **below** the root are ignored. That is a correctness constraint, not a perf bug.

### 4. Technical explanation
- Author `instanceable = true` on the prim that **references** (or inherits) the shared asset. `prim.IsInstance()` True; descendants `IsInstanceProxy()` True.
- `prim.GetPrototype().GetPath()` → `/__Prototype_1` (name assigned by the stage). `GetMaster` does not exist (26.08).
- `Traverse()`: instance roots yes, interior proxies no. Hydra still *draws* the proxies.
- Cost: unique prototypes × size. 2 000 identical refs → ~1 prototype. 2 000 slightly different meshes (unique local topology) → no sharing.
- PointInstancer: one prototype relationship + per-instance arrays (`positions`, `scales`, …). Even cheaper when you do not need a prim per copy.
- Instancing does not replace payloads. Instance a payload root: many stamps, still lazy.

> [!VERSION] Verified on USD 26.08: `GetPrototype()`, not `GetMaster()`.

### 5. Mental model

```text
/World/A  instanceable  ──┐
/World/B  instanceable  ──┼── /__Prototype_1 /S
Traverse: /Proto /Proto/S /World /World/A /World/B
          (no /World/A/S)
GetPrimAtPath(/World/A/S) still valid (proxy)
```

### 6. Simple example
Two instanceable refs of `/Proto`. Traverse has five prims, not seven. Prototype path `/__Prototype_1`.

### 7. USDA example

```usda
#usda 1.0

def Xform "Proto"
{
    def Sphere "S"
    {
    }
}

def Xform "World"
{
    def "A" (
        instanceable = true
        prepend references = </Proto>
    )
    {
    }

    def "B" (
        instanceable = true
        prepend references = </Proto>
    )
    {
    }
}
```

### 8. Python example

```python
from pxr import Usd

open("inst.usda", "w").write("""#usda 1.0
def Xform "Proto"
{
    def Sphere "S"
    {
    }
}
def Xform "World"
{
    def "A" (
        instanceable = true
        prepend references = </Proto>
    )
    {
    }
    def "B" (
        instanceable = true
        prepend references = </Proto>
    )
    {
    }
}
""")
si = Usd.Stage.Open("inst.usda")
print("traverse:", [str(p.GetPath()) for p in si.Traverse()])
print("A instance:", si.GetPrimAtPath("/World/A").IsInstance())
print("A/S proxy:", si.GetPrimAtPath("/World/A/S").IsInstanceProxy())
print("prototype:",
      si.GetPrimAtPath("/World/A").GetPrototype().GetPath())
```

**Expected output**
```text
traverse: ['/Proto', '/Proto/S', '/World', '/World/A', '/World/B']
A instance: True
A/S proxy: True
prototype: /__Prototype_1
```

Five traverse hits, two drawn spheres. That is the memory win.

### 9. Real-world use case
A stadium of identical seats: one `seat.usdc` payload, instanceable refs per row, or one PointInstancer for the bowl. Layout still translates instance roots. Lighting binds on the prototype (or uses collection binds) rather than 40 000 unique materials.

### 10. Common mistakes
> [!MISTAKE] Setting `instanceable` on the prototype asset's *root in its own file* only, and referencing without `instanceable` on the *shot prim*. The shot prim must be instanceable.

> [!MISTAKE] Unique `displayColor` local on every proxy child. That de-instances or is ignored. Color at the instance root / primvar on the prototype.

> [!MISTAKE] Counting `Traverse()` length as "draw prims." Proxies are drawn, not traversed.

### 11. Exam traps
> [!TRAP] `GetMaster()`. **`GetPrototype()`.**

> [!TRAP] Instancing is a payload. Different knobs; they compose.

> [!TRAP] PointInstancer *is* native instancing. Related, different schema (Ch 25).

### 12. Practice questions
1. Which method returns `/__Prototype_1`?
2. Does `Traverse()` yield `/World/A/S` for an instanceable `A`?
3. Where must `instanceable = true` be authored for the shot copies?

**Answers**
1. **`GetPrototype()`** on the instance root.
2. **No.** `GetPrimAtPath` still works; `IsInstanceProxy` True.
3. On the **referencing (instance root) prims**, not only inside the asset file.

### 13. Exam takeaways
> [!KEY]
> - Native instancing: one prototype, many roots; `GetPrototype` not `GetMaster`.
> - `Traverse` skips proxies; Hydra does not.
> - Instanceable flag belongs on the copies.
> - PointInstancer when you do not need a prim per copy.

---

## 44.4 `Sdf.ChangeBlock` and batched edits

### 1. What is it?
**`Sdf.ChangeBlock`** is a context manager that **holds USD notices** until the block exits. A hundred `Set`s inside one block send **one** `ObjectsChanged` instead of hundreds. That is Obj 6.1.

### 2. Why do we need it?
Every notice can trigger Hydra sync, Python listeners, and recomposition. An importer that sets 50 000 points one attribute at a time without a block stutters for minutes; the same writes in a block finish in a beat (Chapter 34).

### 3. Beginner explanation
A change block is "hold your applause until the end of the scene." USD still writes every spec immediately into the layer; it just does not *announce* each one.

*Where the analogy breaks:* `Usd.DefinePrim` of a **child that needs a live parent** can fail inside a block (Chapter 34). Author with `Sdf.PrimSpec` or Define parents *before* the block. Attribute `Set`s on existing prims are the happy path.

### 4. Technical explanation
- `with Sdf.ChangeBlock():` … edits …  Notices (`Usd.Notice.ObjectsChanged`) flush on exit.
- Verified pattern: three `CreateAttribute`+`Set` pairs **without** a block → **6** notices; the same **with** a block → **1**.
- Register: `key = Tf.Notice.Register(Usd.Notice.ObjectsChanged, callback, stage)` and **`key.Revoke()`** (not `Tf.Notice.Revoke`).
- Nested blocks coalesce to the outermost exit.
- ChangeBlock is **not** a transaction: no automatic undo. Failed Python in the block still leaves specs; notices still fire on exit.
- Combine with USDC writes: author in-memory, one `Export`. Do not `Export` per prim.

> [!VERSION] Verified on USD 26.08. `listener.Revoke()` / `key.Revoke()`; `DefinePrim` of new children inside a block may fail — use Sdf specs.

### 5. Mental model

```text
without block:  Set  Set  Set     →  notice notice notice
with block:     Set  Set  Set     →  ........ notice
```

### 6. Simple example
Six attribute creates/sets → 6 notices. Wrap in `ChangeBlock` → 1.

### 7. USDA example

USDA is the *result*, not the block. After a blocked author of three ints:

```usda
#usda 1.0

def Xform "W"
{
    int a = 1
    int b = 2
    int c = 3
}
```

The block never appears in the file.

### 8. Python example

```python
from pxr import Tf, Usd, Sdf, UsdGeom


class Counter:
    def __init__(self):
        self.n = 0

    def __call__(self, notice, sender):
        self.n += 1


stage = Usd.Stage.CreateInMemory()
key_holder = []
lis = Counter()
key = Tf.Notice.Register(Usd.Notice.ObjectsChanged, lis, stage)
prim = UsdGeom.Xform.Define(stage, "/W").GetPrim()
lis.n = 0
prim.CreateAttribute("a", Sdf.ValueTypeNames.Int).Set(1)
prim.CreateAttribute("b", Sdf.ValueTypeNames.Int).Set(2)
prim.CreateAttribute("c", Sdf.ValueTypeNames.Int).Set(3)
print("without block:", lis.n)
lis.n = 0
with Sdf.ChangeBlock():
    prim.CreateAttribute("d", Sdf.ValueTypeNames.Int).Set(4)
    prim.CreateAttribute("e", Sdf.ValueTypeNames.Int).Set(5)
    prim.CreateAttribute("f", Sdf.ValueTypeNames.Int).Set(6)
print("with block:", lis.n)
key.Revoke()
```

**Expected output**
```text
without block: 6
with block: 1
```

Obj 6.1 in two numbers.

### 9. Real-world use case
An Alembic→USD converter used to set each of 200 000 `points` time samples without a block; usdview's listener hung the DCC. Wrapping the sample loop in `ChangeBlock` dropped the hitch to one refresh.

### 10. Common mistakes
> [!MISTAKE] Defining new child prims with `Usd.DefinePrim` inside the block. Prefer `Sdf.PrimSpec` on the target layer.

> [!MISTAKE] Forgetting `key.Revoke()`. Listeners leak; later tests count extra notices.

> [!MISTAKE] Nested `Export` inside the block. Flush the block first, then write the file.

### 11. Exam traps
> [!TRAP] ChangeBlock delays *writes* to the layer. It delays **notices**; specs are already in the layer.

> [!TRAP] `Tf.Notice.Revoke(key)`. Call **`key.Revoke()`**.

> [!TRAP] One `Set` always one notice. Not inside a block; also some `Set`s send two (Ch 34).

### 12. Practice questions
1. What does ChangeBlock batch?
2. How do you unregister an `ObjectsChanged` listener?
3. Why might `DefinePrim` inside a block fail?

**Answers**
1. **Notices** (e.g. `ObjectsChanged`), not the specs themselves.
2. **`key.Revoke()`.**
3. **The parent may not be visible to Usd until the block ends** — use Sdf specs or define parents outside.

### 13. Exam takeaways
> [!KEY]
> - Obj 6.1: `with Sdf.ChangeBlock():` around bulk edits.
> - Verified: 6 notices → 1 for three create+set pairs.
> - `key.Revoke()`; avoid `Usd.DefinePrim` of new children inside the block.
> - Specs write immediately; applause waits.

---

## 44.5 Render-time factors (extent, purpose, draw modes)

### 1. What is it?
Hydra's cheap rejections: **extent** (frustum cull), **purpose** (do not even consider guide/proxy in a beauty pass), **visibility**, and **model draw modes** (`bounds` / `cards` / `origin`) that replace a component's full mesh with a box or camera-facing cards. Obj 6.4 includes these as causes of both *wrong* pictures and *slow* pictures.

### 2. Why do we need it?
A correct 12-million-face set that is all `purpose = default` with empty extents forces Storm to bound and shade everything. Authoring extents and a proxy purpose is often faster than instancing.

### 3. Beginner explanation
Extent is the moving-box on a truck so the dock can skip opening it. Purpose is a sticker: `proxy` for the lobby snapshot, `render` for the catalog, `guide` for riggers. Draw mode `cards` is a cardboard cut-out of the truck when you only need the silhouette.

*Where the analogy breaks:* unauthored extent is not "infinite." Many delegates compute a box (slow) or skip culling (also slow). Unauthored `subdivisionScheme` is a *look* bug (melted CAD) that also costs tessellation.

### 4. Technical explanation
- **Extent:** `UsdGeom.Boundable` `extent` (`float3[]` min/max). `HasAuthoredValue()` False means every consumer may recompute. Keep it in sync when you edit `points` (Ch 13). `UsdGeom.ModelAPI.GetExtentsHint` / `SetExtentsHint` stores a *model-level* hint for draw modes.
- **Purpose:** `Imageable.ComputePurpose()`. Beauty: include `default`+`render`. Layout: often `proxy`. Guides hidden in both. Inherited (Ch 39.6, 42.6).
- **Visibility:** `invisible` prunes descendants. Prefer purpose for "this is a stand-in," visibility for animated hide.
- **Draw modes** (`UsdGeom.ModelAPI` on a model kind): `model:drawMode` fallback **`inherited`**. Values: `default` (full geo), `bounds`, `origin`, `cards`. `model:applyDrawMode` True to actually switch. `ComputeModelDrawMode()` resolves inheritance. Cards use `model:cardTextureXPos` etc.
- Apply `ModelAPI` (or rely on built-in for some schemas) on **component** models (`kind = component`).
- Lights: too many unbound shadow-casting DiskLights (Ch 41) is a render-time cost; `inputs:shadow:enable = 0` on fills.

> [!VERSION] Verified on USD 26.08. `GetModelDrawModeAttr().Get()` unauthored → **`inherited`**. `CreateModelDrawModeAttr("cards")` + `CreateModelApplyDrawModeAttr(True)` → `ComputeModelDrawMode()` **`cards`**.

### 5. Mental model

```text
per gprim:   extent?  purpose?  visibility?
per model:   drawMode bounds/cards/origin   applyDrawMode
Hydra: skip → cheap bounds → cards → full mesh
```

### 6. Simple example
Component `/Asset` with ModelAPI, `drawMode = cards`, `applyDrawMode = true`. ComputeModelDrawMode returns `cards`. Unauthored draw mode is `inherited`.

### 7. USDA example

```usda
#usda 1.0

def Xform "Asset" (
    kind = "component"
    prepend apiSchemas = ["GeomModelAPI"]
)
{
    uniform token model:drawMode = "cards"
    uniform bool model:applyDrawMode = 1
    float3[] extentsHint = [(-1, 0, -1), (1, 2, 1)]

    def Mesh "Hi"
    {
        uniform token purpose = "render"
        float3[] extent = [(-1, 0, -1), (1, 2, 1)]
    }

    def Mesh "Lo"
    {
        uniform token purpose = "proxy"
        float3[] extent = [(-1, 0, -1), (1, 2, 1)]
    }
}
```

- Layout cameras that include `proxy` draw `Lo` (or cards). Beauty uses `Hi`.
- `GeomModelAPI` is the schema name in USDA for `UsdGeom.ModelAPI`.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
xf = UsdGeom.Xform.Define(stage, "/Asset")
xf.GetPrim().SetMetadata("kind", "component")
api = UsdGeom.ModelAPI.Apply(xf.GetPrim())
print("fallback drawMode:", api.GetModelDrawModeAttr().Get())
api.CreateModelDrawModeAttr("cards")
api.CreateModelApplyDrawModeAttr(True)
print("mode:", api.GetModelDrawModeAttr().Get())
print("apply:", api.GetModelApplyDrawModeAttr().Get())
print("ComputeModelDrawMode:", api.ComputeModelDrawMode())
print("HasAPI:", xf.GetPrim().HasAPI(UsdGeom.ModelAPI))
```

**Expected output**
```text
fallback drawMode: inherited
mode: cards
apply: True
ComputeModelDrawMode: cards
HasAPI: True
```

### 9. Real-world use case
A city layout set ships `proxy` box meshes plus `render` hi meshes, extents on both, and component drawMode `cards` for helicopter shots. Storm stays interactive; the beauty delegate never sees the boxes.

### 10. Common mistakes
> [!MISTAKE] Setting `drawMode` without `applyDrawMode`. Hydra keeps drawing full geo.

> [!MISTAKE] Stale extent after a points edit. Culls wrong (objects pop) — Obj 6.4.

> [!MISTAKE] Putting `purpose = render` on the only mesh, then wondering why layout cameras that exclude render are empty.

### 11. Exam traps
> [!TRAP] Unauthored `model:drawMode` is `default`. It is **`inherited`**.

> [!TRAP] Draw mode is a Mesh attribute. It is **ModelAPI** on the model root.

> [!TRAP] Imageable purpose vs material purpose vs draw mode — three switches (Ch 39, 40, this section).

### 12. Practice questions
1. Unauthored `GetModelDrawModeAttr().Get()`?
2. Which boolean makes `cards` actually apply?
3. Why author `extent` for performance?

**Answers**
1. **`inherited`.**
2. **`model:applyDrawMode` (True).**
3. **So Hydra can frustum-cull without reading all points.**

### 13. Exam takeaways
> [!KEY]
> - Obj 6.4 speed: extent, purpose, visibility, draw modes.
> - ModelAPI `drawMode` fallback `inherited`; set `applyDrawMode`.
> - Proxy/render pairs beat sending hi meshes to layout.
> - Stale extent is both a wrong picture and a slow picture.

---

## 44.6 Maximizing USD performance checklist

### 1. What is it?
A **fixed order** of performance questions, parallel to Chapter 42.7's correctness procedure. You measure (Trace / MallocTag / prim counts), then walk the list. Pixar's "Maximizing USD Performance" essay is the spirit; the items below are the APIs this book verified.

### 2. Why do we need it?
Random instancing of a 12-prim shot wastes time. The checklist stops you from applying §44.3 when §44.2 was the bug (you referenced instead of payloaded).

### 3. Beginner explanation
Same medic order as 42.7, but the vital signs are **time and bytes**: how many files, how many loaded payloads, how many notices per edit, how many imageable prims Hydra will visit.

*Where the analogy breaks:* a scene can be correct *and* slow. Chapter 42 passing does not skip this list.

### 4. Technical explanation

**Checklist (stop when the measured bar drops):**

1. **Measure.** `Trace.Collector` around `Stage.Open`, around your edit loop, around export. `MallocTag` on a tagged build. `len(list(stage.Traverse()))` vs `TraverseAll`.
2. **Format.** Heavy layers USDC; shot/work USDA. `.usd` is crate unless you say otherwise.
3. **Working set.** Payloads for heavy roots; `LoadNone` + `Load` / `FindLoadable`. Masks for tools that only need a subtree (`OpenMasked`).
4. **Instancing / PointInstancer.** Shared geometry gets `instanceable` copies or a PointInstancer.
5. **Edit batching.** `Sdf.ChangeBlock` around importer loops (Obj 6.1). Revoke listeners.
6. **Assets.** `ComputeAllDependencies` unresolved empty; avoid cwd-relative resolves in inner loops (Ch 33).
7. **Draw.** Extents authored; purpose split; ModelAPI draw modes for layout; lights' shadow flags; `subdivisionScheme = none` on CAD (also Obj 6.4 correctness).
8. **Do not flatten the working scene.** Flatten/USDZ at *publish* (Ch 31, 34).

usdview's **Memory** / **Hydra** debug (not in `usd-core`) visualizes 3–4 and 7. Python above is the exam-safe stand-in.

### 5. Mental model

```text
Trace which bar
  Open slow  →  USDC, payloads, masks, fewer layers
  Edit slow  →  ChangeBlock, fewer listeners
  Draw slow  →  extent, purpose, instance, drawMode
  RAM high   →  instance, payloads, masks (MallocTag if tagged)
```

### 6. Simple example
`LoadNone` shot: TraverseAll lists payload roots + referenced geo; `FindLoadable` is the working-set menu. That one print tells you whether anyone used payloads.

### 7. USDA example

A "fast by construction" shot:

```usda
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def "Set" (
        prepend payload = @./set.usdc@
    )
    {
    }

    def "Hero" (
        instanceable = true
        prepend payload = @./hero.usdc@
    )
    {
    }
}
```

- Crate payloads, instanceable hero, tiny USDA shot.

### 8. Python example

```python
from pxr import Usd, Sdf

open("geo.usda", "w").write("""#usda 1.0
(
    defaultPrim = "P"
)
def Xform "P"
{
    def Mesh "Hi"
    {
    }
}
""")
open("shot.usda", "w").write("""#usda 1.0
def Xform "World"
{
    def "Set" (
        prepend payload = @./geo.usda@
    )
    {
    }
    def "Hero" (
        instanceable = true
        prepend payload = @./geo.usda@
    )
    {
    }
}
""")
st = Usd.Stage.Open("shot.usda", Usd.Stage.LoadNone)
print("format usd default:",
      Sdf.FileFormat.FindByExtension("usd").formatId)
print("traverseAll:", [str(p.GetPath()) for p in st.TraverseAll()])
print("loadable:", sorted(str(p) for p in st.FindLoadable()))
print("Hero instanceable:",
      st.GetPrimAtPath("/World/Hero").GetMetadata("instanceable"))
print("Set loaded:", st.GetPrimAtPath("/World/Set").IsLoaded())
```

**Expected output**
```text
format usd default: usd
traverseAll: ['/World', '/World/Set', '/World/Hero']
loadable: ['/World/Hero', '/World/Set']
Hero instanceable: True
Set loaded: False
```

Both heavy prims are payloads and unloaded; Hero is ready to instance when loaded. That is a passing score on steps 2–4 before anyone hits Render.

### 9. Real-world use case
A studio wiki page titled "Maximizing USD Performance" is this checklist plus two commands: `TF_DEBUG=USD_CHANGES` for surprise recomposes, and Trace around Open. New shows copy the shot template in §7 rather than debating crate vs USDA on Slack.

### 10. Common mistakes
> [!MISTAKE] Instancing first on a scene whose Open is 90% USDA parse. Format/payloads first.

> [!MISTAKE] Population-masking the artist's working stage so they cannot see the set. Masks are for **tools**; load rules are for **people**.

> [!MISTAKE] Publishing flattened crates *and* expecting payloads to still be lazy. Flatten already pulled them in.

### 11. Exam traps
> [!TRAP] The performance essay's first item is flatten. For a **working** scene it is near the last.

> [!TRAP] `LoadNone` as a render optimization for beauty. Beauty must `Load` (or `LoadAll`) the payloads it needs; masks/purpose then cut draw.

> [!TRAP] ChangeBlock speeds `Stage.Open`. It speeds **edits**, not open.

### 12. Practice questions
1. Open is slow, Traverse count is small. Which knobs first?
2. Open is fine, dragging a slider stutters. Which knob?
3. Should a layout artist use `OpenMasked` omitting the set?

**Answers**
1. **USDC + payloads** (I/O / compose), not draw modes.
2. **`Sdf.ChangeBlock`** (and fewer listeners) — edit bar.
3. **No** — they need to see the set; use load rules / purpose / draw modes.

### 13. Exam takeaways
> [!KEY]
> - Measure (Trace) → format → payloads/mask → instance → ChangeBlock → draw.
> - Working set = load rules; tools = masks; publish = flatten/USDZ.
> - Obj 6.1 is ChangeBlock; Obj 6.4 is extent/purpose/draw/subdivision.
> - Do not flatten to "go faster" while still authoring.

---

## Chapter lab(s)

**Lab 30 — Change notices and change-block performance** (★★☆, Obj 6.1, Ch 34 and 44). You count `ObjectsChanged` with and without `Sdf.ChangeBlock`.

**Lab 23 — Native instancing** and **Lab 15 — payloads / load rules** cover §44.3 and §44.2. There is no separate "perf" lab; the checklist is the exercise.

## USDA reading exercise(s)

**Exercise 44-A.** A DCC opens this shot with `LoadNone` to be fast. The artist cannot see `/World/Hall/Wall`. Why, and is the arc type the problem?

```usda
#usda 1.0

def Xform "World"
{
    def "Hall" (
        prepend references = @./hall.usdc@
    )
    {
    }
}
```

**Exercise 44-B.** An importer sets `points` 10 000 times. usdview freezes until it finishes. Which Obj 6.1 tool, and what must wrap the loop?

**Exercise 44-C.** Layout is slow; beauty is fine. Hi meshes have `purpose = default`, no proxy, no extents, `model:drawMode` unauthored. Name three authors that would speed layout without changing beauty.

## Chapter review

### Summary
- Load vs edit vs draw. USDC for heavy data; USDA for small shots; `.usd` defaults crate.
- Payloads + `LoadNone`/`Load`/`FindLoadable`; `OpenMasked` omits prims; references always load.
- Instancing: `GetPrototype`, Traverse skips proxies.
- ChangeBlock: 6 notices → 1 for three create+set pairs (Obj 6.1).
- Draw: extent, purpose, ModelAPI `cards`/`bounds` + `applyDrawMode` (Obj 6.4).
- Checklist: measure, then format, working set, instance, batch, assets, draw; flatten at publish.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Open slow, tiny prim count | USDA parse / too many files |
| `.usd` | Wrapper id `usd`; disk magic **PXR-USDC** |
| `LoadNone` still heavy | You used **references** |
| `FindLoadable` empty | No payloads |
| `Open(path, mask)` TypeError | **`OpenMasked`** |
| Masked prim `IsValid` False | Not unloaded — **absent** |
| RAM huge, many identical refs | Missing `instanceable` |
| `GetMaster` | **`GetPrototype`** |
| Edit hitch, Open fine | ChangeBlock / notices |
| Layout slow, beauty OK | purpose / drawMode / extents |
| `drawMode` ignored | Forgot `applyDrawMode` |
| Flatten to go faster | Publish tool, not a working-set tool |

### Review questions

**Q44.1** · Obj 6.1 · Easy · Single choice
`CreateNew("shot.usd")` writes crate bytes. `FindByExtension("usd").formatId` is still:
A. `usda` · B. `usdc` · C. `usd` · D. `None`

**Q44.2** · Obj 6.1 · Easy · Single choice
`Stage.Open(path, Usd.Stage.LoadNone)` still fully composes:
A. Payloads · B. References · C. Nothing · D. Only the session layer

**Q44.3** · Obj 6.1 · Medium · Single choice
Which call opens a stage that *omits* prims not under `/World/A`?
A. `Open(path, LoadNone)` then `Unload` · B. `OpenMasked(path, mask)` with `mask.Add("/World/A")` · C. `Open(path, mask)` · D. `MuteLayer`

**Q44.4** · Obj 6.1 · Easy · Single choice
`FindLoadable()` lists:
A. Every prim · B. Payload paths · C. Referenced paths · D. Muted layers

**Q44.5** · Obj 6.1 · Medium · Single choice
Native instance prototype accessor in 26.08:
A. `GetMaster()` · B. `GetPrototype()` · C. `GetInstance()` · D. `GetProxy()`

**Q44.6** · Obj 6.1 · Medium · Single choice
Three `CreateAttribute`+`Set` pairs: notices without vs with `ChangeBlock` (this book's measurement):
A. 3 and 3 · B. 6 and 1 · C. 1 and 1 · D. 6 and 6

**Q44.7** · Obj 6.1 · Easy · Single choice
Unregister an `ObjectsChanged` listener with:
A. `Tf.Notice.Revoke(key)` · B. `key.Revoke()` · C. `del key` · D. `stage.Unsubscribe(key)`

**Q44.8** · Obj 6.4 · Easy · Single choice
Unauthored `model:drawMode` `Get()` is:
A. `default` · B. `cards` · C. `inherited` · D. `None`

**Q44.9** · Obj 6.4 · Medium · Select two.
Layout-only speedups that should not change beauty:
A. `purpose = proxy` stand-in meshes · B. Deleting render meshes from the asset · C. `model:drawMode = cards` with `applyDrawMode` · D. Flattening the lighting layer into geometry

**Q44.10** · Obj 6.4 · Easy · Single choice
Hydra frustum culling wants authored:
A. `kind` · B. `extent` · C. `info:id` · D. `defaultPrim`

**Q44.11** · Obj 6.1 · Medium · Single choice
ChangeBlock speeds up:
A. `Stage.Open` of USDA · B. Bulk **edits** (fewer notices) · C. Texture resolve · D. Variant selection fallbacks

**Q44.12** · Obj 6.1 · Medium · Single choice
A working-scene performance checklist puts flatten:
A. First · B. Instead of USDC · C. At **publish**, not while authoring · D. Never in any pipeline

### Answers

**Q44.1 — C.** The wrapper id is `usd`; `GetUnderlyingFormatForLayer` is `usdc` and the magic is `PXR-USDC`. Review: §44.1.

**Q44.2 — B.** Review: §44.2 / §42.2.

**Q44.3 — B.** `Open(path, mask)` is not an overload. Review: §44.2.

**Q44.4 — B.** Review: §44.2.

**Q44.5 — B.** Review: §44.3.

**Q44.6 — B.** Review: §44.4.

**Q44.7 — B.** Review: §44.4 / Ch 34.

**Q44.8 — C.** Review: §44.5.

**Q44.9 — A, C.** Deleting hi meshes changes beauty; flatten is unrelated. Review: §44.5–44.6.

**Q44.10 — B.** Review: §44.5.

**Q44.11 — B.** Review: §44.4.

**Q44.12 — C.** Review: §44.6.

### USDA exercise answers

**44-A — `Hall` is a *reference*, so `LoadNone` still composes `hall.usdc`.** The artist should see `Wall` if the asset has `defaultPrim` (or an explicit prim path). If they wanted laziness, the arc should be a **payload**. The format `.usdc` is fine.

**44-B — `with Sdf.ChangeBlock():` around the loop** (Obj 6.1). Optionally revoke extra listeners. ChangeBlock delays notices, not the `points` writes.

**44-C — (1) `purpose = proxy` (or a sibling proxy mesh), (2) authored `extent`, (3) ModelAPI `drawMode` `bounds` or `cards` with `applyDrawMode`.** Do not delete hi meshes; beauty still needs them at `purpose = render` / default.

## Further reading

- [S06] OpenUSD API — UsdStage load rules, OpenMasked, StagePopulationMask, SdfChangeBlock, UsdGeomModelAPI: https://openusd.org/release/api/index.html
- [S04] OpenUSD user docs — "Maximizing USD Performance" (study-guide reading list)
- [S14] NVIDIA Learn OpenUSD — performance: https://docs.nvidia.com/learn-openusd/latest/index.html
- Chapters 17, 24–26, 31, 34, 39, 42–43
