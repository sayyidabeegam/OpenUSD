# Chapter 32 — Pipeline Architecture and Asset Management

> **Exam domain:** Pipeline Development (14%) · **Objectives:** 7.2 · **Study day:** 10 · **Est. time:** 100 min
> **Prerequisites:** Ch 15 (sublayers, edit targets), Ch 22 (workstreams, delivery), Ch 23 (asset structure, kinds)

Chapter 23 taught the *shape of one asset*. This chapter is the *studio around it*: how departments, folders, versions, and documents turn those assets into a working **pipeline**. Obj 7.2 is "document asset structure guidelines" — you must be able to draw, name, and explain the rules, not only author a chair.

## Learning goals

- Define a USD pipeline as people, folders, publish steps, and composition — not a single file.
- Choose a directory layout and naming scheme that stay stable when versions change.
- Version by **published folders**, not by renaming prims or stacking daily sublayers.
- Inventory an asset with `UsdUtils.ComputeAllDependencies` and contrast it with `ExtractExternalReferences`.
- Diagram layer stacks, asset trees, and ownership so another team can follow them.
- Split collaboration so each department owns one layer and downstream work is stronger.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Pipeline** | The agreed path from work-in-progress to published, reusable USD |
| **Work file** | A layer artists still edit; not what other shots should reference |
| **Publish** | Copy or write an **immutable** snapshot other assets may reference |
| **Pin** | A reference (or payload) that points at one published version |
| **Dependency** | A layer or file this layer needs (sublayer, reference, payload, texture) |
| **Unresolved path** | A dependency `ComputeAllDependencies` could not find on disk |
| **Asset identifier** | Stable name in `assetInfo` (for example `"chair"`), independent of version |
| **Guideline document** | The written rules and diagrams Obj 7.2 asks you to produce |

---

## 32.1 What a USD pipeline is

### 1. What is it?

A **USD pipeline** is the studio's contract for how 3D work is authored, published, referenced, and handed to the next department. The files are USD. The pipeline is the **rules plus the tools that enforce them**.

### 2. Why do we need it?

USD will compose whatever you give it. It will not stop two artists from saving the same layer, or a shot from pointing at an artist's desktop. Without a pipeline, composition still "works" — until a texture goes missing on the farm and nobody knows which chair version the shot meant.

### 3. Beginner explanation

Think of a restaurant. The recipes (USD layers) matter, but so do the stations (departments), the walk-in fridge labeled by date (published versions), and the ticket that says which plate is for table 12 (the shot file). A brilliant recipe with no ticket system is not a restaurant.

*Where the analogy breaks:* plates leave the kitchen once. A published chair stays on disk and is referenced by a thousand shots at once. Publishing is a snapshot, not a one-time serving.

### 4. Technical explanation

A small USD pipeline has five moving parts:

| Part | What it is | Typical USD tool |
|------|------------|------------------|
| **Workstreams** | One kind of work per layer | Sublayers inside an asset (Ch 22) |
| **Departments** | One team per shot layer | Shot sublayer stack, edit targets (Ch 15) |
| **Publish** | Immutable copy other people may use | Copy to a versioned folder; never edit in place |
| **Consume** | Scenes reference published assets | `references` / `payload` with relative paths |
| **Check** | Catch missing files and broken metadata | `ComputeAllDependencies`, UsdValidation (Ch 30) |

USD does **not** provide: file locking, a database of versions, or a GUI called "the pipeline." Those are studio tools. The exam tests whether you can *design* the USD side so those tools have something sensible to call.

Two composition facts that drive the design (already proven in Part III):

- **One writer per layer.** Two saves to the same file overwrite each other.
- **Downstream is stronger.** Later departments sit higher in `subLayers` so they can fix without asking earlier departments to republish.

The shot's **root layer** is often thin: stage metadata (`defaultPrim`, `upAxis`, `metersPerUnit`) plus the `subLayers` list. Nobody "owns" the root as a dump of opinions.

### 5. Mental model

```text
  artist work folders          publish          consume
  --------------------         -------          -------
  assets/chair/work/    --->   assets/chair/v002/   <---  shots/.../layout.usda
  shots/seq010/shot020/work     (immutable)              references that path

  shot.usda (thin root)
    subLayers, strongest first:
      lighting.usda     lighting artist  (edit target)
      anim.usda         animator
      layout.usda       layout           (places references)
```

### 6. Simple example

Layout publishes `assets/chair/v002/chair.usda`. The shot's `layout.usda` references that file. Animation never opens the chair work file; it only authors an `over` on `/World/Chair_A` in `anim.usda`.

### 7. USDA example

*File: shot.usda* — thin root. Department files are listed strongest first.

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 1
    upAxis = "Y"
    subLayers = [
        @./lighting.usda@,
        @./anim.usda@,
        @./layout.usda@
    ]
)

def Xform "World"
{
}
```

- `subLayers` — first listed is strongest (lighting can override anim).
- `./` — paths are anchored to this file, so the shot folder can move as a unit.
- `World` — the shot's namespace root; assets are referenced *under* it in `layout.usda`, not in this file.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom
import os

shot = Usd.Stage.CreateNew("shot.usda")
UsdGeom.Xform.Define(shot, "/World")
shot.SetDefaultPrim(shot.GetPrimAtPath("/World"))
shot.SetMetadata("metersPerUnit", 1)
UsdGeom.SetStageUpAxis(shot, UsdGeom.Tokens.y)
for name in ("lighting.usda", "anim.usda", "layout.usda"):
    Sdf.Layer.CreateNew(name).Save()
shot.GetRootLayer().subLayerPaths = [
    "./lighting.usda", "./anim.usda", "./layout.usda"]
shot.GetRootLayer().Save()

stage = Usd.Stage.Open("shot.usda")
print("root:", os.path.basename(stage.GetRootLayer().identifier))
print("stack:")
for layer in stage.GetLayerStack():
    if layer.anonymous:
        print("  session (anonymous, not saved)")
    else:
        print(" ", os.path.basename(layer.identifier))
print("subLayerPaths:", list(stage.GetRootLayer().subLayerPaths))
```

**Expected output**

```text
root: shot.usda
stack:
  session (anonymous, not saved)
  shot.usda
  lighting.usda
  anim.usda
  layout.usda
subLayerPaths: ['./lighting.usda', './anim.usda', './layout.usda']
```

`GetLayerStack()` always starts with the **session layer** (anonymous, strongest, not a file). Then the root, then sublayers in list order. That order *is* the pipeline's strength order.

### 9. Real-world use case

A digital-twin factory: CAD publishes `cell/v014/cell.usda`. Simulation references that version. Lighting for a marketing still is a stronger sublayer on a *shot* that also references `cell/v014`. CAD can publish `v015` the next day without silently changing yesterday's still, because the still is **pinned**.

### 10. Common mistakes

> [!MISTAKE] Calling "the USD file" the pipeline. One layer is data. The pipeline is work files, publish, pins, and checks.

> [!MISTAKE] Putting layout references in the shot root. Then every department's save rewrites the same file. Fix: references live in `layout.usda`; the root only lists sublayers.

> [!MISTAKE] Using the session layer as a publish destination. It is never saved with the stage (Ch 3).

### 11. Exam traps

> [!TRAP] "USD includes a version database." It does not. Versioning is folders + pins (and optionally a resolver, Ch 33).

> [!TRAP] "First sublayer is weakest." First listed is **strongest** (Ch 3, Ch 15).

> [!TRAP] Forgetting the session layer is in `GetLayerStack()`. The first identifier is often anonymous, not `shot.usda`.

### 12. Practice questions

**Q32.1-1.** Select two parts of a USD pipeline that USD itself does *not* provide.
A. Composition of sublayers
B. File locking so two artists cannot save the same layer
C. A central version database
D. `defaultPrim` on a published entry layer

**Q32.1-2.** In the example, which layer should contain `prepend references = @../../../assets/chair/v002/chair.usda@`?
A. `shot.usda` (the root)
B. `layout.usda`
C. The session layer
D. `chair.usda` itself

**Answers**

- **Q32.1-1: B and C.** Composition and `defaultPrim` are USD. Locking and a version DB are studio infrastructure.
- **Q32.1-2: B.** Layout owns placement. The root stays thin.

### 13. Exam takeaways

> [!KEY]
> - A pipeline is work → publish → pin → check, with one writer per layer.
> - Downstream departments sit higher in `subLayers` (stronger).
> - The shot root is metadata + the sublayer list, not a dumping ground.
> - Obj 7.2: you must be able to **document** that structure, not only build it.

---

## 32.2 Directory structures and naming conventions

### 1. What is it?

A **directory structure** is where files live on disk. A **naming convention** is how files, prims, and `assetInfo` identifiers are spelled. Together they are the part of the guideline document that a new hire can follow without asking.

### 2. Why do we need it?

Relative asset paths (`@./tex/wood.png@`) only work if everyone puts textures in the same place relative to the layer. Scripts that glob `*/chair.usda` only work if every asset uses that name. Inconsistent folders become unresolved paths (Section 32.4).

### 3. Beginner explanation

A library that shelves books by color instead of by call number still has books. Nobody can find the same book twice. USD folders are the call numbers. Prim names are the titles on the spine.

*Where the analogy breaks:* one USD "book" is a *folder* of layers plus textures, not one file. The entry layer is the card in the catalog; the payload is the pages in the stacks (Ch 23).

### 4. Technical explanation

A layout that scales from one chair to a feature film:

```text
show/
  assets/
    chair/
      work/                 artists edit here (not referenced by shots)
      v001/                 published, immutable
      v002/
        chair.usda          entry layer (what others reference)
        payload/            heavy layers, often USDC
        tex/                textures belonging to this version
  shots/
    seq010/
      shot020/
        shot.usda           thin root
        layout.usda
        anim.usda
        lighting.usda
```

Rules that belong in the guideline document:

| Rule | Why |
|------|-----|
| One published asset = one version folder | The pin is a directory, not a filename trick |
| Entry file named after the asset (`chair.usda`) | Tools can find it without a database |
| Relative paths only (`./`, `../`) | The tree can be copied or localized (Ch 22) |
| Prim names are stable (`Chair`, not `Chair_v002`) | References keep working; `GetModelNameFromRootLayer` stays `Chair` |
| `assetInfo["identifier"]` is the dictionary name (`chair`) | Resolvers and catalogs key off this, not the folder (Ch 12, Ch 33) |
| Files use valid identifiers where they become prims | `Tf.MakeValidIdentifier` / `Sdf.Path.IsValidIdentifier` (Ch 28) |
| Do not key behavior off names | Use `kind`, schemas, or properties (Ch 23) |

`UsdUtils.GetModelNameFromRootLayer(layer)` returns the layer's `defaultPrim` if set, otherwise the name of the (first) root prim. Keep `defaultPrim` equal to the public prim name, and never bake a version into that name.

> [!EXAM TIP] NVIDIA's four principles (legible, modular, performant, navigable) still apply to folders. Clear names are **legibility**. A version folder you can swap is **modularity**.

### 5. Mental model

```text
  identifier "chair"     <-- stays the same forever
  prim /Chair            <-- stays the same forever
  file  .../v002/chair.usda   <-- version lives HERE
  shot  references that file        <-- pin
```

### 6. Simple example

Wrong: `Hero_v003.usda` whose `defaultPrim` is `Hero_v003`. A shot that referenced `Hero_v002` cannot switch versions without renaming the prim in every downstream layer.

Right: `assets/hero/v003/hero.usda` with `defaultPrim = "Hero"`. The shot retargets the asset path only.

### 7. USDA example

*File: assets/chair/v002/chair.usda*

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "Chair" (
    kind = "component"
    assetInfo = {
        string identifier = "chair"
        string name = "DiningChair"
    }
)
{
    asset tex = @./tex/wood.png@
}
```

- `defaultPrim = "Chair"` — what `GetModelNameFromRootLayer` returns.
- `identifier = "chair"` — catalog key; not `chair_v002`.
- `@./tex/wood.png@` — texture lives *with this version*, not in a shared mutable dump.

### 8. Python example

```python
from pxr import Sdf, UsdUtils
import os

os.makedirs("assets/chair/v001", exist_ok=True)
open("assets/chair/v001/chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    kind = "component"
    assetInfo = {
        string identifier = "chair"
    }
)
{
    asset tex = @./wood.png@
}
""")
open("assets/chair/v001/wood.png", "wb").write(b"x")

layer = Sdf.Layer.FindOrOpen("assets/chair/v001/chair.usda")
print("model name:", UsdUtils.GetModelNameFromRootLayer(layer))
print("identifier:",
      layer.GetPrimAtPath("/Chair").assetInfo["identifier"])
tex = layer.GetAttributeAtPath("/Chair.tex").default
print("tex path:", tex.path)
print("relative:", not os.path.isabs(tex.path))
```

**Expected output**

```text
model name: Chair
identifier: chair
tex path: ./wood.png
relative: True
```

### 9. Real-world use case

A games studio keeps source under `content/props/barrel/` and published cooked USD under `cooked/props/barrel/v012/`. Engine imports pin `cooked/.../v012`. Artists never reference `content/` from a level file, so a half-saved work file cannot ship.

### 10. Common mistakes

> [!MISTAKE] Absolute paths (`@/mnt/show/assets/chair/wood.png@`). The shot dies when the mount changes. Fix: `./` relative to the layer.

> [!MISTAKE] Sharing one `tex/` folder across versions. Publishing v002 then overwrites v001's textures. Fix: textures live inside the version folder.

> [!MISTAKE] Matching file names to user login (`jdoe_chair.usda`) as the published entry. The identifier and entry name belong to the **asset**, not the artist.

### 11. Exam traps

> [!TRAP] "`GetModelNameFromRootLayer` reads `assetInfo['name']`." It uses `defaultPrim` (else a root prim name). `assetInfo` is separate.

> [!TRAP] "Prim names must include the version so you can tell them apart in usdview." That breaks every pin. Use layer comments, `assetInfo`, or the folder name.

> [!TRAP] "`.usd` in the folder name is required." The convention is the *entry file* often uses `.usd` so encoding can switch (Ch 23, Ch 31); the folder is still `chair/v002/`.

### 12. Practice questions

**Q32.2-1.** `GetModelNameFromRootLayer` on a layer with `defaultPrim = "Lamp"` and a prim `def Xform "Fixture"` returns:
A. `Fixture`
B. `Lamp`
C. the file stem
D. `assetInfo['identifier']`

**Q32.2-2.** Select two directory rules that keep pins stable.
A. Put the version in the folder path, not the prim name
B. Store textures inside that version folder
C. Rename `/Chair` to `/Chair_v002` on each publish
D. Use absolute `/mnt/show/...` asset paths so every machine agrees

**Answers**

- **Q32.2-1: B.** `defaultPrim` wins. Review: step 4.
- **Q32.2-2: A and B.** C breaks consumers; D breaks the moment the disk layout changes.

### 13. Exam takeaways

> [!KEY]
> - Version lives in the **folder**; prim name and `identifier` stay stable.
> - `GetModelNameFromRootLayer` → `defaultPrim` (else root prim name).
> - Relative `./` paths; textures travel with the version.
> - Write these rules down — that writing *is* Obj 7.2.

---

## 32.3 Versioning and publishing

### 1. What is it?

**Publishing** writes an immutable snapshot of an asset into a versioned location. **Versioning** is how you name those snapshots and how consumers **pin** one of them. Layer stacks are not a version-control system.

### 2. Why do we need it?

If shots reference a work file, yesterday's lighting render and today's modeling WIP become the same path. If you add `chair_monday.usda` as a new sublayer every day, the stack grows forever and composition slows (Ch 23: do not grow layer stacks as history).

### 3. Beginner explanation

A bakery puts each day's bread on a dated shelf. Tuesday's sandwich ticket says "use Tuesday's loaf," not "use whatever is on the counter." Publishing is taking the loaf *off* the counter and putting it on the dated shelf. The counter can keep changing.

*Where the analogy breaks:* git (or Perforce) may still version the work files. USD publish is an additional, **pipeline-visible** snapshot that other USD files pin. Source control history is not a composition arc.

### 4. Technical explanation

Three layers of "version" people confuse:

| Mechanism | What it versions | Use it for |
|-----------|------------------|------------|
| Git / Perforce / etc. | Bytes of work files | Artist history, diffs of USDA |
| Published folder `v001`, `v002` | Immutable USD + textures | What shots pin |
| Layer stack | Strength of opinions | Departments, not history |

Publish checklist (document this):

1. Work is done in `.../work/` (or a user sandbox).
2. A publisher copies or exports into `.../vNNN/` (new folder, never overwrite `vNNN` that shots already pin).
3. Run validation (Ch 30) and `ComputeAllDependencies` (Section 32.4); fail if unresolved.
4. Shots that *should* upgrade retarget their reference; others stay pinned.

Retargeting is an asset-path change on the consuming prim:

```{.python .norun}
prim.GetReferences().ClearReferences()
prim.GetReferences().AddReference("./assets/chair/v002/chair.usda")
```

The prim path (`/Set/C`) and the asset's internal `/Chair` name do not change. That is why you never put `v002` in the prim name.

> [!VERSION] Verified on USD 26.08. USD still has no built-in "current version" pointer. Some studios add a `.../chair/default` symlink or an Ar resolver (Ch 33) that maps `chair` → `v002`. The pin is then the identifier plus resolver context, not a raw folder. Teach the folder pin first; it is what the files themselves show.

### 5. Mental model

```text
  work/chair.usda  --publish-->  v001/chair.usda  <-- shot A (stays)
                           \-->  v002/chair.usda  <-- shot B (upgraded)

  NOT:  shot.usda sublayers v001, then v002, then v003  (that is not versioning)
```

### 6. Simple example

Shot A shipped with chair v001. Modeling publishes v002 with a taller seat (`custom double height = 1.2`). Shot A still opens v001 until layout retargets. Shot B, started after the publish, pins v002 from the start.

### 7. USDA example

*File: set.usda* (consumer, pinned to v001)

```usda
#usda 1.0
(
    defaultPrim = "Set"
)

def Xform "Set"
{
    def "C" (
        prepend references = @./assets/chair/v001/chair.usda@
    )
    {
    }
}
```

The version is in the **asset path**. The prim is still `"C"`. Inside the asset, `defaultPrim` is still `"Chair"`.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdUtils
import os


def write(path, text):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


write("assets/chair/v001/chair.usda", """#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    kind = "component"
)
{
}
""")
write("assets/chair/v002/chair.usda", """#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    kind = "component"
)
{
    custom double height = 1.2
}
""")
write("set.usda", """#usda 1.0
(
    defaultPrim = "Set"
)
def Xform "Set"
{
    def "C" (
        prepend references = @./assets/chair/v001/chair.usda@
    )
    {
    }
}
""")

stage = Usd.Stage.Open("set.usda")
prim = stage.GetPrimAtPath("/Set/C")
print("v001 has height:", prim.HasAttribute("height"))
print("v001 kind:", Usd.ModelAPI(prim).GetKind())
print("model name v001:", UsdUtils.GetModelNameFromRootLayer(
    Sdf.Layer.FindOrOpen("assets/chair/v001/chair.usda")))

prim.GetReferences().ClearReferences()
prim.GetReferences().AddReference("./assets/chair/v002/chair.usda")
stage.Save()

stage2 = Usd.Stage.Open("set.usda")
prim2 = stage2.GetPrimAtPath("/Set/C")
print("v002 height:", prim2.GetAttribute("height").Get())
print("model name v002:", UsdUtils.GetModelNameFromRootLayer(
    Sdf.Layer.FindOrOpen("assets/chair/v002/chair.usda")))
print("prim name still:", prim2.GetName())
```

**Expected output**

```text
v001 has height: False
v001 kind: component
model name v001: Chair
v002 height: 1.2
model name v002: Chair
prim name still: C
```

The consuming prim stayed `C`. The asset's model name stayed `Chair`. Only the **path** of the reference changed.

### 9. Real-world use case

A film shot is locked for lighting. Modeling must still publish v018 of a hero prop for another sequence. Lighting's pin on v017 does not move. A producer later asks to "pick up v018 in shot 120"; layout retargets that one shot and lighting re-renders it.

### 10. Common mistakes

> [!MISTAKE] Overwriting `v002/` in place because "it's the same version number." Anyone already pinning `v002` silently changes. Fix: new number, or a policy that `v002` is frozen once any shot pins it.

> [!MISTAKE] Using sublayers as history (`monday.usda`, `tuesday.usda`). Every layer costs composition time. Fix: source control for history; one current published layer per workstream.

> [!MISTAKE] Referencing `assets/chair/work/chair.usda` from a shot "just for now." That path will still be there on the farm.

### 11. Exam traps

> [!TRAP] "Add a stronger sublayer to upgrade an asset." A sublayer of the *shot* cannot replace which file a *reference* points at. You change the reference (or use a resolver).

> [!TRAP] "`ClearReferences` deletes the prim." It removes the arc. The `def "C"` spec remains; you then `AddReference` the new path.

> [!TRAP] "Published USDC cannot be pinned because it isn't text." Encoding is independent of publish. Pin the entry layer, whatever its encoding (Ch 31).

### 12. Practice questions

**Q32.3-1.** A shot must keep last week's chair while a new chair is published. Best mechanism?
A. Mute the new chair layer
B. Leave the shot's reference pointing at `.../v017/chair.usda`
C. Add `v018` as a weaker sublayer of the shot
D. Rename `/Chair` to `/Chair_old`

**Q32.3-2.** After `ClearReferences()` then `AddReference("./assets/chair/v002/chair.usda")` on `/Set/C`, what stays the same?
A. The composed `height` value
B. The consuming prim's path `/Set/C` and the asset `defaultPrim`
C. The asset path stored on the reference
D. Which textures are on disk under `v001/`

**Answers**

- **Q32.3-1: B.** Pins are paths. Muting and extra sublayers do not redirect a reference.
- **Q32.3-2: B.** Path and `defaultPrim` are the stable names; height and the stored asset path change.

### 13. Exam takeaways

> [!KEY]
> - Publish = new immutable folder; shots pin that folder.
> - Do not use layer stacks as version history.
> - Retarget the asset path; keep prim names and `defaultPrim` stable.
> - Never let shots reference work files.

---

## 32.4 Dependencies (`UsdUtils.ComputeAllDependencies`)

### 1. What is it?

A **dependency** is any other file a layer needs in order to compose or render: sublayers, references, payloads, clips, and asset-valued attributes (textures). `UsdUtils.ComputeAllDependencies` walks that graph from one starting file and returns everything it can find — plus a list of what it cannot.

### 2. Why do we need it?

A publisher that copies `chair.usda` but forgets `tex/wood.png` produces a package that opens and then renders black. Inventory the graph **before** you copy, flatten, or zip (Ch 22, Ch 31).

### 3. Beginner explanation

Before you email a spreadsheet that says `=VLOOKUP` into another workbook, you attach that workbook too. `ComputeAllDependencies` is "list every workbook and image this spreadsheet pulls in, and list the `#REF!` links."

*Where the analogy breaks:* USD follows composition arcs **recursively** (a shot's layout file's chair's payload's texture). Spreadsheet attach-dialogs often stay one hop.

### 4. Technical explanation

Verified on USD 26.08:

```text
UsdUtils.ComputeAllDependencies(assetPath)
    -> (layers, assets, unresolved)
```

`assetPath` may be a string or an `Sdf.AssetPath`. Both work.

| Return slot | Type | Contains |
|-------------|------|----------|
| `layers` | `list` of `Sdf.Layer` | Every USD layer opened while walking |
| `assets` | `list` of `str` | Non-layer files that resolved (textures, …) |
| `unresolved` | `list` of `str` | Paths that did not resolve; often **absolute** |

The walk follows sublayers, references, **and payloads** (payloads are still dependencies even if a stage might later unload them). Missing files produce Tf warnings on stderr and appear in `unresolved`. The call still returns; it does not raise.

A related one-layer helper:

```text
UsdUtils.ExtractExternalReferences(filePath)
    -> (sublayers, referencesAndAssets, payloads)
```

Differences that exam answers mix up:

| | `ExtractExternalReferences` | `ComputeAllDependencies` |
|--|-----------------------------|--------------------------|
| Scope | **One** file, authored strings | **Recursive**, resolved files |
| Assets | Texture paths sit in the **second** list with references | Separate `assets` list |
| Missing | Still listed as authored `@./gone.jpg@` | Listed in `unresolved` (often absolutized) |
| Recurses into sublayers? | No | Yes |

`UsdUtils.LocalizeAsset` and `CreateNewUsdzPackage` (Ch 22, Ch 31) use this same inventory internally. This section is the inventory; those chapters are the copy/zip.

> [!VERSION] `UsdUtils.LocalizeAsset` exists since 24.03. `ComputeAllDependencies` is older. On 26.08 both are present.

### 5. Mental model

```text
  ExtractExternalReferences(file)     ComputeAllDependencies(file)
  -------------------------------     ----------------------------
  what THIS file writes               the whole snowball
  three authored-path buckets         layers | assets | missing
```

### 6. Simple example

`asset.usda` payloads `payload.usda`, references `seat.usda`, has `@./tex/wood.png@` (exists) and `@./gone.jpg@` (missing). Compute: three layers, one asset `wood.png`, one unresolved `gone.jpg`. Extract on `asset.usda` alone: empty sublayers, refs+assets `./seat.usda` + textures, payloads `./payload.usda`.

### 7. USDA example

*File: asset.usda*

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    kind = "component"
    prepend payload = @./payload.usda@
)
{
    asset tex = @./tex/wood.png@
    asset missing = @./gone.jpg@
    def "Seat" (
        prepend references = @./seat.usda@
    )
    {
    }
}
```

Three different dependency *kinds* on one prim: payload, asset attributes, child reference. `ExtractExternalReferences` puts them in different buckets; `ComputeAllDependencies` flattens them into layers vs assets vs missing.

### 8. Python example

Stderr will show a "Failed to resolve" warning for `gone.jpg`. That is expected. The checker compares stdout only.

```python
from pxr import UsdUtils
import os

os.makedirs("tex", exist_ok=True)
open("tex/wood.png", "wb").write(b"PNG")
open("seat.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Seat"
)
def Cube "Seat" {}
""")
open("payload.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Extra"
)
def Sphere "Extra" {}
""")
open("asset.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    kind = "component"
    prepend payload = @./payload.usda@
)
{
    asset tex = @./tex/wood.png@
    asset missing = @./gone.jpg@
    def "Seat" (prepend references = @./seat.usda@) {}
}
""")

layers, assets, unresolved = UsdUtils.ComputeAllDependencies("asset.usda")
print("layers:", sorted(os.path.basename(l.realPath) for l in layers))
print("assets:", sorted(os.path.basename(a) for a in assets))
print("unresolved:", sorted(os.path.basename(u) for u in unresolved))

subs, refs, pays = UsdUtils.ExtractExternalReferences("asset.usda")
print("extract sublayers:", subs)
print("extract refs+assets:", sorted(refs))
print("extract payloads:", pays)
```

**Expected output**

```text
layers: ['asset.usda', 'payload.usda', 'seat.usda']
assets: ['wood.png']
unresolved: ['gone.jpg']
extract sublayers: []
extract refs+assets: ['./gone.jpg', './seat.usda', './tex/wood.png']
extract payloads: ['./payload.usda']
```

Read the extract line twice: `./gone.jpg` and `./tex/wood.png` sit next to `./seat.usda`. The second bucket is **not** "references only."

### 9. Real-world use case

A CI job runs `ComputeAllDependencies` on every published entry layer. If `unresolved` is non-empty, the publish is rejected. A second job compares the `assets` list to the files actually copied into `vNNN/` so a texture cannot be "forgotten" on a network share.

### 10. Common mistakes

> [!MISTAKE] Treating `ExtractExternalReferences` as a complete ship list. It does not walk into `layout.usda` to find the chair. Fix: `ComputeAllDependencies` on the shot or the asset entry.

> [!MISTAKE] Assuming `unresolved` paths look like the authored `@./gone.jpg@`. They are often absolutized. Compare with `os.path.basename` or normalize before matching.

> [!MISTAKE] Ignoring stderr warnings because the function returned a tuple. Unresolved items are a failed publish, not a footnote.

### 11. Exam traps

> [!TRAP] "`ComputeAllDependencies` returns a dict `{layers: ...}`." It returns a **3-tuple**.

> [!TRAP] "Payloads are omitted because they might be unloaded." They are still dependencies. Compute includes them; extract puts them in the **third** list.

> [!TRAP] "The second extract list is only USD references." Asset-valued attributes land there too.

### 12. Practice questions

**Q32.4-1.** `ComputeAllDependencies("shot.usda")` returns `(L, A, U)`. What is `U`?
A. Payload asset paths, even if the files exist
B. Paths the walker could not resolve
C. The session layer
D. Sublayer identifiers in authored order

**Q32.4-2.** Select two true statements.
A. `ExtractExternalReferences` recurses into every sublayer
B. Texture paths appear in extract's second list
C. `ComputeAllDependencies` follows payloads
D. Missing files raise `Tf.ErrorException` and abort the call

**Answers**

- **Q32.4-1: B.** Third slot = unresolved.
- **Q32.4-2: B and C.** Extract is one file; missing files warn and list, they do not abort.

### 13. Exam takeaways

> [!KEY]
> - `ComputeAllDependencies` → `(layers, assets, unresolved)`; recursive.
> - `ExtractExternalReferences` → `(sublayers, refs+assets, payloads)`; one file.
> - Payloads count. Textures are assets (compute) or mixed into refs (extract).
> - A non-empty `unresolved` list fails a publish.

---

## 32.5 Diagramming and documenting asset structure

### 1. What is it?

**Documenting** asset structure (Obj 7.2) means producing diagrams and short written rules another person can follow: folder tree, layer stack, prim tree with kinds, and an ownership table. The document is part of the pipeline, not a slide you make after the exam.

### 2. Why do we need it?

A perfect on-disk layout that exists only in one TD's head cannot be validated, onboarded, or examined. NVIDIA's objective uses the verb **document**. The exam will show a diagram or a USDA snippet and ask whether it matches the guidelines (Ch 23's ASWF/NVIDIA rules plus this chapter's folders and pins).

### 3. Beginner explanation

A fire-escape plan on the wall is not the building. You still need it so a guest can get out. Asset-structure diagrams are the fire-escape plan for chairs, shots, and departments.

*Where the analogy breaks:* the diagram must match the **files**, or CI will disagree with the wiki. Generate trees from the stage when you can (step 8).

### 4. Technical explanation

Four diagrams belong in every guideline pack:

**A. Folder tree** (Section 32.2) — where versions and textures live.

**B. Layer-stack strip** — strongest at the top, one owner per box:

```text
  session (not saved)
  shot.usda              supervisor / metadata
  lighting.usda          lighting
  anim.usda              animation
  layout.usda            layout (references published assets)
```

**C. Asset composition** — entry → payload → workstream layers (Ch 23):

```text
  chair.usda  (text entry: defaultPrim, kind, assetInfo, payload)
       payload --> contents.usdc
                      subLayers: geo.usdc , mtl.usdc
```

**D. Model hierarchy** — kinds only, so navigability is visible:

```text
  Room          assembly
    Furniture   group
      Chair     component
        Seat    (no kind; inside component)
```

Plus a **table of ownership** (who may author which properties). Geometry owns `points`; surfacing owns bindings; nobody else writes those names. Overlap is a silent LIVERPS fight (Ch 21).

Minimum written rules to print next to the diagrams (from Ch 23, restated as a checklist):

- Published roots are `component` or `assembly`, never `group`.
- Loft `kind`, `assetInfo`, variant set names above the payload.
- Reference published entries; payload heavy content.
- Relative paths; one writer per layer; downstream stronger.

### 5. Mental model

```text
  guideline document
    1. pictures (folders, stacks, kinds)
    2. tables  (owners, pins, names)
    3. checks  (ComputeAllDependencies, validators)
```

If it is not in those three, it is folklore.

### 6. Simple example

A one-page PDF titled "Chair v002" with: folder tree, the entry USDA's metadata block, a kind tree, and "layout references `assets/chair/v002/chair.usda`; do not reference `work/`."

### 7. USDA example

The model-hierarchy diagram in step 4 is this layer:

```usda
#usda 1.0
(
    defaultPrim = "Room"
)

def Xform "Room" (
    kind = "assembly"
)
{
    def Xform "Furniture" (
        kind = "group"
    )
    {
        def Xform "Chair" (
            kind = "component"
        )
        {
            def Cube "Seat"
            {
            }
        }
    }
}
```

A reviewer can check the diagram against `kind` metadata without opening usdview.

### 8. Python example

```python
from pxr import Usd, UsdGeom


stage = Usd.Stage.CreateInMemory()
room = UsdGeom.Xform.Define(stage, "/Room")
Usd.ModelAPI(room.GetPrim()).SetKind("assembly")
furn = UsdGeom.Xform.Define(stage, "/Room/Furniture")
Usd.ModelAPI(furn.GetPrim()).SetKind("group")
chair = UsdGeom.Xform.Define(stage, "/Room/Furniture/Chair")
Usd.ModelAPI(chair.GetPrim()).SetKind("component")
UsdGeom.Cube.Define(stage, "/Room/Furniture/Chair/Seat")


def tree(prim, indent=0):
    kind = Usd.ModelAPI(prim).GetKind() or "-"
    print("  " * indent + prim.GetName() + "  kind=" + kind)
    for child in prim.GetChildren():
        tree(child, indent + 1)


tree(stage.GetPrimAtPath("/Room"))
```

**Expected output**

```text
Room  kind=assembly
  Furniture  kind=group
    Chair  kind=component
      Seat  kind=-
```

This printout *is* diagram D. Keep it in the publish log next to the folder tree.

### 9. Real-world use case

An AEC firm hands contractors a two-page "USD package spec": folder names, required `assetInfo` keys, the layer-stack order for a building, and a screenshot of the kind tree. Incoming files are rejected when `ComputeAllDependencies` or the kind tree disagrees with the spec.

### 10. Common mistakes

> [!MISTAKE] Documenting only prims and skipping folders. Pins live in paths (Section 32.3).

> [!MISTAKE] Drawing a layer stack with layout on top "because layout comes first in the schedule." Time-order of work and strength-order of layers are different. Downstream (lighting) is stronger.

> [!MISTAKE] A wiki diagram that still shows `kind = component` under another component. The files must match ASWF (Ch 23): that child should be `subcomponent`.

### 11. Exam traps

> [!TRAP] Obj 7.2 is satisfied by "we use USD." The objective is **guidelines**: names, folders, kinds, ownership, pins.

> [!TRAP] A diagram that puts `group` on a published root. ASWF: published roots are `component` or `assembly`.

> [!TRAP] "Seat kind=- means the cube is invalid." No kind on a gprim inside a component is normal.

### 12. Practice questions

**Q32.5-1.** Select two items Obj 7.2 expects you to document.
A. Folder layout and pin paths
B. Which department owns which layer
C. The C++ source of `Sdf.Layer`
D. NVIDIA's exam passing score

**Q32.5-2.** In a layer-stack diagram, lighting is drawn above animation. That means:
A. Lighting works earlier in the schedule
B. Lighting's opinions are stronger
C. Animation files are payloads of lighting
D. Lighting cannot override translates

**Answers**

- **Q32.5-1: A and B.** Guidelines are structure and ownership, not USD internals or exam logistics.
- **Q32.5-2: B.** Higher in the list = stronger. Schedule order is the opposite story.

### 13. Exam takeaways

> [!KEY]
> - Obj 7.2 = write diagrams + ownership rules that match the files.
> - Four pictures: folders, layer stack, asset payload, kind tree.
> - Generate the kind tree from the stage so the wiki cannot drift.
> - Strength order ≠ production schedule order.

---

## 32.6 Collaboration across departments

### 1. What is it?

**Collaboration** in a USD pipeline means each department writes to **its own layer**, through an **edit target**, and hands off by **publishing** — not by emailing a merged file. The composed shot is the stack; the people never share a save button.

### 2. Why do we need it?

USD has no merge tool for two writers of one crate file. Parallel work is parallel **files**. Chapters 15 and 22 taught the mechanics. Here you connect them to publish and to the guideline document.

### 3. Beginner explanation

A newspaper: reporters file separate stories (layers). The night editor's page is a stronger sheet that can still override a headline. Nobody types into someone else's story file.

*Where the analogy breaks:* USD overrides are per property, not per article. Animation can set translate on `/World/Prop` while layout still owns the reference that put `Prop` there.

### 4. Technical explanation

Handoff pattern that belongs in the guidelines:

| Moment | Who | Where they write | What they publish |
|--------|-----|------------------|-------------------|
| Place assets | Layout | `layout.usda` | References to **published** asset versions |
| Move them | Animation | `anim.usda` | `over` opinions (xforms, time samples) |
| Light | Lighting | `lighting.usda` | Lights, stronger xform fixes if needed |
| Lock a version | Pipeline | new `vNNN/` of an **asset** | Immutable folder; shots retarget if asked |

Rules:

- **Edit target = department layer.** `stage.SetEditTarget(Usd.EditTarget(anim_layer))` so `AddTranslateOp` cannot accidentally hit `layout.usda`.
- **`def` once, `over` elsewhere.** Layout `def`s `/World/Prop`. Animation authors `over "Prop"` in its file (Ch 20).
- **Assets are referenced, not sublayered, into the shot.** Sublayers merge namespaces at the same paths; a chair asset should appear under `/World/Chair_A`, which is a reference (Ch 16 vs Ch 15).
- **Mute to review.** `MuteLayer` on `anim.usda` answers "what did animation change?" without deleting files (Ch 15).
- **Do not publish another department's layer.** Animation's publish is `anim.usda` (or a shot-level package), not a new chair `vNNN` unless modeling actually changed the chair.

Inspect **who won** with `GetPropertyStack()` (Ch 22): the strongest spec's layer should be the department you expect.

### 5. Mental model

```text
  layout.usda     def /World/Prop + reference to published chair
  anim.usda       over /World/Prop { translate }
  lighting.usda   over /World/Prop { ... optional fixes }

  Save buttons: three files.  Composed result: one stage.
```

### 6. Simple example

Layout defines `/World/Prop`. Animation's edit target is `anim.usda`. After both save, `xformOp:translate`'s property stack lists `anim.usda` first. Layout still has the `def`.

### 7. USDA example

*File: anim.usda* (what animation publishes for the shot)

```usda
#usda 1.0

over "World"
{
    over "Prop"
    {
        double3 xformOp:translate = (3, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
}
```

No `def`, no reference, no texture path. Animation does not take ownership of placement or the asset pin.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom
import os

layout = Sdf.Layer.CreateNew("layout.usda")
anim = Sdf.Layer.CreateNew("anim.usda")
shot = Usd.Stage.CreateNew("shot.usda")
UsdGeom.Xform.Define(shot, "/World")
shot.GetRootLayer().subLayerPaths = ["./anim.usda", "./layout.usda"]

shot.SetEditTarget(Usd.EditTarget(layout))
UsdGeom.Xform.Define(shot, "/World/Prop")

shot.SetEditTarget(Usd.EditTarget(anim))
UsdGeom.Xform.Get(shot, "/World/Prop").AddTranslateOp().Set((3, 0, 0))

shot.GetRootLayer().Save()
layout.Save()
anim.Save()

attr = shot.GetPrimAtPath("/World/Prop").GetAttribute(
    "xformOp:translate")
print("translate stack:",
      [os.path.basename(s.layer.identifier)
       for s in attr.GetPropertyStack()])
print("layout defines Prop?",
      layout.GetPrimAtPath("/World/Prop").specifier == Sdf.SpecifierDef)
print("anim is over?",
      anim.GetPrimAtPath("/World/Prop").specifier == Sdf.SpecifierOver)
print(anim.ExportToString())
```

**Expected output**

```text
translate stack: ['anim.usda']
layout defines Prop? True
anim is over? True
#usda 1.0

over "World"
{
    over "Prop"
    {
        double3 xformOp:translate = (3, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
}


```

Animation's file is only overs. The stack for translate has a single spec, in `anim.usda`. Layout still owns the `def`.

### 9. Real-world use case

A live-events team builds a stage: scenic layout pins published set pieces; animation publishes a 90-second `anim.usda` of LED-wall xforms; lighting publishes last. When the director asks "show me the empty set," the operator mutes `anim.usda`. No file is rewritten.

### 10. Common mistakes

> [!MISTAKE] Leaving the edit target on the session layer (the default in some tools) and wondering why Save does not keep the animation. Fix: set the department layer before authoring.

> [!MISTAKE] Animation adding a second reference to the chair "to be safe." Now two arcs fight. Fix: only layout holds the pin; animation overs the instance.

> [!MISTAKE] Lighting editing `chair/v002/geo.usdc` to hide a bolt. That mutates a published asset for every shot. Fix: an `over` in `lighting.usda` or a shot-specific stronger layer.

### 11. Exam traps

> [!TRAP] "Collaboration means `Flatten` at the end of each day." Flattening destroys arcs (Ch 22). Daily handoff is **saving each department layer**.

> [!TRAP] "Stronger department must `def` the prim." Stronger files usually `over`. The first owner `def`s.

> [!TRAP] `GetPropertyStack` empty means the attribute has no value. It can also mean you queried a prim that does not exist, or a name that was never authored (fallback vs authored — Ch 5).

### 12. Practice questions

**Q32.6-1.** Animation must move a prop that layout referenced. Where does the translate opinion go?
A. The published `chair/v002/chair.usda`
B. `anim.usda` as an `over`
C. The session layer, then flatten into the chair
D. A new sublayer of the chair asset named `anim.usda`

**Q32.6-2.** Select two actions that keep departments from overwriting each other.
A. One edit target per department layer
B. Everyone saves `shot.usda` (the root) so there is a single source of truth
C. Mute a department layer to review its contribution
D. Put all departments in one USDC for faster load

**Answers**

- **Q32.6-1: B.** Shot-level `over` in the animation layer. Never edit the published asset for a shot move.
- **Q32.6-2: A and C.** B and D put everyone back on one file.

### 13. Exam takeaways

> [!KEY]
> - One department, one layer, one edit target; `def` once, `over` downstream.
> - Shots reference published assets; they do not sublayer them.
> - Handoff is saving (and publishing) layers, not flattening daily.
> - `GetPropertyStack` names the department that won a property.

---

## Chapter lab(s)

- **Lab 22** (Chapter 23) builds a component and an assembly — the asset side of these guidelines.
- **Lab 28** (Chapter 31) runs `ComputeAllDependencies`, localize, and USDZ — the publish-inventory side.
- **Lab 37** (capstone) is a miniature pipeline: work → publish → pin → validate.

## USDA reading exercises

**Exercise 32-A.** A shot root lists `subLayers = [@./anim.usda@, @./layout.usda@]`. Layout references `@../../../assets/lamp/work/lamp.usda@`. Name two guideline violations.

**Exercise 32-B.** `ExtractExternalReferences("shot.usda")` returns `(['./anim.usda', './layout.usda'], [], [])`. Does that prove the shot has no textures? What call would you run instead?

**Answers**

- **32-A.** (1) The shot pins a **work** file, not a published version folder. (2) If lighting exists, it is missing from the stack — and even without lighting, work-file pins are the serious break. (Relative `./` on department layers is fine.)
- **32-B.** No. Extract does not recurse, so textures on the lamp never appear. Run `ComputeAllDependencies("shot.usda")` and inspect `assets` and `unresolved`.

## Chapter review

**Summary**

- A USD pipeline is work → publish → pin → check, with one writer per layer.
- Version lives in **folders**; prim names and `assetInfo` identifiers stay stable.
- `GetModelNameFromRootLayer` reads `defaultPrim`.
- `ComputeAllDependencies` → `(layers, assets, unresolved)` (recursive).
- `ExtractExternalReferences` → `(sublayers, refs+assets, payloads)` (one file).
- Obj 7.2 is **documentation**: folders, stacks, kinds, ownership.
- Downstream departments are stronger; they `over`, they do not edit published assets.
- Layer stacks are not version control; git is not a composition arc.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| "document asset structure" | Obj 7.2: diagrams + naming + pins + owners |
| `Hero_v003` as `defaultPrim` | Version in the wrong place |
| `ComputeAllDependencies` three items | layers, assets, unresolved |
| extract's second list includes `.png` | refs **and** asset attributes |
| shot references `.../work/` | unpublished pin |
| two artists, one `.usdc` | missing department layers |
| daily `monday.usda` sublayer | stacks used as history |
| lighting below layout in the list | strength order inverted |

**Review questions**

**R32-1** (Obj 7.2) Which statement belongs in an asset-structure guideline document?
A. "USD will lock the file when an artist has it open."
B. "Published roots use `component` or `assembly`; version is a folder; shots pin that folder."
C. "All departments write the shot root so Save is centralized."
D. "Put `v003` in the prim name so usdview labels stay unique."

**R32-2** (Obj 7.2) `UsdUtils.GetModelNameFromRootLayer(layer)` returns `"Hero_v003"`. What probably went wrong?
A. The layer has no `defaultPrim` and the root prim was named with a version
B. `ComputeAllDependencies` failed
C. The identifier in `assetInfo` is `"hero"`
D. The file is USDC

**R32-3** (Obj 7.2) Select two correct facts about `ComputeAllDependencies`.
A. It returns a 3-tuple `(layers, assets, unresolved)`
B. It follows payloads
C. It never lists textures
D. It raises if any path is missing

**R32-4** (Obj 7.2) `ExtractExternalReferences("shot.usda")` does not list `chair.usda`, but the composed shot shows a chair. Why?
A. References are illegal on sublayers
B. Extract does not recurse; the reference is in `layout.usda`
C. The chair is only in the session layer
D. `chair.usda` is USDC so extract ignores it

**R32-5** (Obj 7.2) Best pin for a locked lighting shot?
A. `assets/chair/work/chair.usda`
B. `assets/chair/v017/chair.usda`
C. A sublayer of every historical `v001`…`v017`
D. `/Chair_v017` as the prim name, any folder

**R32-6** (Obj 7.2) In `GetLayerStack()` of an opened shot, what is first?
A. The weakest sublayer
B. The anonymous session layer
C. `layout.usda`
D. The published chair entry

**R32-7** (Obj 7.2) Select two collaboration rules.
A. Animation authors `over` in `anim.usda` via that layer's edit target
B. Lighting may overwrite `v017/geo.usdc` to hide a bolt for one shot
C. Layout holds the asset reference
D. Daily `Flatten` is the handoff

**R32-8** (Obj 7.2) A texture `@./tex/wood.png@` exists. Where does `ComputeAllDependencies` put it?
A. `layers`
B. `assets`
C. `unresolved`
D. It is omitted because it is not USD

**R32-9** (Obj 7.2) Why are relative `./` paths part of the guideline?
A. Crate files forbid absolute paths
B. The tree can move, localize, or package without rewriting mounts
C. `defaultPrim` requires them
D. ExtractExternalReferences cannot see absolute paths

**R32-10** (Obj 7.2) Lighting is drawn *below* layout on a stack diagram labeled "strongest at top." The diagram claims lighting can override layout translates. The claim is:
A. True, because lighting works later
B. False; below means weaker
C. True, because payloads are always weaker than sublayers
D. True only if lighting uses `def` instead of `over`

**R32-11** (Obj 7.2) `assetInfo['identifier'] = "chair"` should change when?
A. Every publish (`chair_v002`, then `chair_v003`)
B. Almost never; it is the catalog key
C. Whenever `defaultPrim` changes to match the folder
D. Only for USDZ delivery

**R32-12** (Obj 7.2) Which pair is the right split?
A. Version control (git) = history of work files; publish folders = what shots pin
B. Version control = composition arcs; publish = `MuteLayer`
C. Both are `subLayers` lists
D. Publish folders replace the need for `kind`

**Review answers**

- **R32-1: B.** That sentence is a guideline. A is false (USD has no lock). C and D violate one-writer and stable names. Review: §32.1–32.3, §32.5.
- **R32-2: A.** The helper reads `defaultPrim` or the root prim name. Review: §32.2.
- **R32-3: A and B.** Textures go in `assets`; missing paths list, they do not raise. Review: §32.4.
- **R32-4: B.** One-file extract. Review: §32.4.
- **R32-5: B.** Immutable version folder. Review: §32.3.
- **R32-6: B.** Session is strongest and first. Review: §32.1.
- **R32-7: A and C.** Do not mutate published assets; do not flatten as handoff. Review: §32.6.
- **R32-8: B.** Non-layer resolved files. Review: §32.4.
- **R32-9: B.** Portability of the pin. Review: §32.2.
- **R32-10: B.** First listed / higher drawn = stronger. Review: §32.1, §32.5.
- **R32-11: B.** Identifier is stable; version is the folder. Review: §32.2.
- **R32-12: A.** Two different jobs. Review: §32.3.

## Further reading

- [S16] NVIDIA — *Principles of Scalable Asset Structure in OpenUSD*. https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
- [S17] ASWF USD Working Group — *Guidelines for Structuring USD Assets*. https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md
- [S06] OpenUSD API — `UsdUtils.ComputeAllDependencies`, `ExtractExternalReferences`, `GetModelNameFromRootLayer`, `LocalizeAsset`. https://openusd.org/release/api/usd_utils_page_front.html
- [S04] OpenUSD Glossary — Asset, Layer, Composition. https://openusd.org/release/glossary.html
