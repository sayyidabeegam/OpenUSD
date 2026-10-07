# Chapter 23 — Asset Structure and Model Hierarchy

> **Exam domain:** Content Aggregation (10%), also Pipeline Development (14%) · **Objectives:** 2.4, 7.2 · **Study day:** 8 · **Est. time:** 90 min
> **Prerequisites:** Ch 6 (schemas and model kinds), Ch 15 (sublayers), Ch 16 (references), Ch 17 (payloads), Ch 18 (variant sets), Ch 19 (inherits and classes)

Part III taught you *how* composition arcs work. This part teaches you how to *organize* real content with them. **Content aggregation** means assembling many reusable assets into larger scenes (a room from chairs, a city from buildings) in a way that stays fast and easy to manage. This chapter is about the shape of a single asset and the "map" that lets tools find assets inside a huge scene. Chapter 24 then shows how to make thousands of copies of an asset cheaply.

## Learning goals

- Explain the four principles of scalable asset structure: legibility, modularity, performance, navigability.
- Build an asset interface: a small entry layer that payloads binary content layers.
- Apply kinds (`component`, `group`, `assembly`, `subcomponent`) so that the model hierarchy is valid, and predict `IsModel()`, `IsGroup()`, `IsComponent()`.
- Design modular components that are referenced into assemblies and edited through classes.
- Document an asset structure using the ASWF guidelines (`geo`/`mtl` scopes, class per asset, no `group` kind on published roots).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Asset** | A named, versioned, structured container of files (USD layers, textures, …) meant to be reused. |
| **Entry layer** (asset interface layer) | The root layer of an asset: the file other scenes reference or open. |
| **Entry point prim** | The prim inside the entry layer that others reference, usually the `defaultPrim`. |
| **Lofting** | Copying cheap, important data (kind, variant sets, inherits, `extentsHint`) up into the entry layer, above the payload. |
| **Kind** | Prim metadata (a token) that labels a prim's role: `component`, `group`, `assembly`, `subcomponent`. |
| **Model** | A prim whose kind is `model` or derived from it, *and* which sits in a valid model hierarchy. |
| **Model hierarchy** | The tree of model prims from the root down to the component level; a quick "map" of the scene. |
| **Component** | A complete, leaf-level asset (a chair, a house). The model hierarchy stops here. |
| **Assembly** | A published asset that aggregates other components or assemblies (a room, a city). |
| **Group** | A kind for organizing prims *inside* an assembly so the model hierarchy stays valid. |
| **Subcomponent** | A marker for an important prim *inside* a component (a door, a lid). Not a model. |
| **Scope** | A prim type (`UsdGeom.Scope`) used only to organize children; it has no transform. |
| **ASWF guidelines** | Community asset-structure recommendations from the ASWF USD Working Group. |

---

## 23.1 Principles of scalable asset structure

### 1. What is it?

**Asset structure** is the set of rules for how an asset is split into files, prims, and names. NVIDIA's whitepaper *Principles of Scalable Asset Structure in OpenUSD* says a scalable structure should be **legible**, **modular**, **performant**, and **navigable**.

### 2. Why do we need it?

Without agreed rules, every artist and tool invents its own layout. Scripts break, scenes become slow, and nobody can find the prim they need. A structure lets many people and processes work in parallel on the same asset and lets large scenes stay manageable.

### 3. Beginner explanation

Think of a well-run warehouse. Every box has a clear **label** (legible). Boxes are standard sizes so they stack and ship anywhere (modular). Heavy pallets stay in the back until needed (performant). Aisles are numbered so anyone can find item 4-B-12 (navigable).

*Where the analogy breaks:* a warehouse box is physical and in one place. A USD asset is many layers composed together, and the same asset can appear in thousands of scenes at once.

### 4. Technical explanation

The four principles, as questions you ask about every design decision:

| Principle | Question to ask | Typical USD tools |
|-----------|-----------------|-------------------|
| **Legibility** | Do prim, property, and file names say what they are? | Naming conventions, `Tf.IsValidIdentifier`, `assetInfo`, `displayName` |
| **Modularity** | Can parts be improved and reused independently? | Separate layers per workstream, `defaultPrim`, references, anchored paths (`./`) |
| **Performance** | Does the structure keep reading and writing fast? | Payloads, USDC for heavy data, instancing, small entry layers |
| **Navigability** | Can people and tools find things by inspection? | Partition scopes (`geo`, `mtl`), model hierarchy (kinds), relationships, collections |

Further rules from the same source:

- **Workstreams become layers.** Geometry and materials are often separate layers so one can be republished without touching the other.
- **Partition the hierarchy** with `Scope` prims. `Scope` has no transform, so it cannot move its children by accident.
- **Naming signals intent.** Capitalized names often mean "public, safe to override"; a leading `_` means "internal". Names beginning with `__` are reserved by OpenUSD (for example the prototype prims `/__Prototype_1` you meet in Chapter 24).
- **Do not key logic off names.** A mesh must not render differently because of its name. Use kinds, schemas, or properties instead.
- **Do not grow layer stacks forever** (for example one sublayer per day). Every layer costs time to resolve and open. Layer stacks are not a version-control system.

### 5. Mental model

```text
+-----------------------------------------------------------+
|                 SCALABLE ASSET STRUCTURE                  |
+--------------+--------------+--------------+--------------+
|  LEGIBLE     |  MODULAR     |  PERFORMANT  |  NAVIGABLE   |
|  names say   |  parts are   |  heavy data  |  you can     |
|  what it is  |  reusable    |  loads late  |  find it     |
+--------------+--------------+--------------+--------------+
```

### 6. Simple example

| Bad | Better | Principle |
|-----|--------|-----------|
| Prim `/Mesh_017` | `/LargeCardboardBox/geo/box` | Legibility |
| One 2 GB file with geometry, shading, rig | `geo.usdc`, `mtl.usdc`, entry layer | Modularity |
| Opening the city loads every building | Buildings behind payloads | Performance |
| Materials mixed in with meshes | `geo` and `mtl` scopes | Navigability |

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "LargeCardboardBox"
    metersPerUnit = 0.01
    upAxis = "Y"
)

def Xform "LargeCardboardBox" (
    kind = "component"
)
{
    def Scope "geo"
    {
        def Mesh "box"
        {
        }
    }

    def Scope "mtl"
    {
    }
}
```

- `defaultPrim` names the entry point, so others can reference the file without a prim path (Chapter 16).
- `metersPerUnit` and `upAxis` make units explicit (Chapter 28).
- The name `LargeCardboardBox` is legible; `kind = "component"` makes it navigable; `geo` and `mtl` partition the contents.

### 8. Python example

A tiny "principles audit" that checks a few measurable rules.

```python
from pxr import Usd, Sdf, Tf

stage = Usd.Stage.CreateInMemory()
stage.GetRootLayer().ImportFromString("""#usda 1.0
(
    defaultPrim = "LargeCardboardBox"
    metersPerUnit = 0.01
    upAxis = "Y"
)

def Xform "LargeCardboardBox" (
    kind = "component"
)
{
    def Scope "geo"
    {
        def Mesh "box"
        {
        }
    }

    def Scope "mtl"
    {
    }
}
""")

root = stage.GetDefaultPrim()
checks = {
    "legible: root name is a valid identifier": Tf.IsValidIdentifier(root.GetName()),
    "modular: defaultPrim is set": stage.HasDefaultPrim(),
    "navigable: root has a kind": bool(Usd.ModelAPI(root).GetKind()),
    "navigable: geo and mtl scopes exist": all(
        root.GetChild(n).GetTypeName() == "Scope" for n in ("geo", "mtl")
    ),
}
for name, ok in checks.items():
    print("PASS" if ok else "FAIL", name)
```

**Expected output**

```text
PASS legible: root name is a valid identifier
PASS modular: defaultPrim is set
PASS navigable: root has a kind
PASS navigable: geo and mtl scopes exist
```

### 9. Real-world use case

A robotics company publishes thousands of warehouse props for synthetic-data simulation. Each prop follows the same structure, so one script can scatter, validate, and render any of them. When a texture is fixed in `mtl.usdc`, the geometry file is untouched, so storage deduplication keeps working and only one small file is re-sent to the render farm.

### 10. Common mistakes

> [!MISTAKE] Encoding meaning only in names (e.g. "anything called `*_proxy` is hidden"). **Fix:** use real data: `purpose`, `kind`, or a custom property. Names are hints for humans.

> [!MISTAKE] Adding a new sublayer for every revision (`asset_2026_10_01.usd`, `asset_2026_10_02.usd`, …). **Fix:** use a versioning system or asset resolver for versions; keep layer stacks short.

> [!MISTAKE] Grouping children under `Xform` "folders". **Fix:** use `Scope` for pure organization; it has no transform to change by accident.

### 11. Exam traps

> [!TRAP] The four principles are **legibility, modularity, performance, navigability**. Look-alike distractors such as "portability" or "flexibility" are not the named four.

> [!TRAP] "There is one correct asset structure for all pipelines." False. Both NVIDIA and the ASWF stress that structure depends on the clients and collaborators; the principles guide the choice.

### 12. Practice questions

**Q23.1-1** Which change most directly improves *navigability*?
A. Saving the geometry layer as USDC
B. Putting meshes under a `geo` scope and materials under a `mtl` scope
C. Renaming the asset from `Asset01` to `ArmChair`
D. Putting the geometry behind a payload

**Q23.1-2** Why is `Scope` preferred over `Xform` for organizational prims? (Select one.)
A. `Scope` prims are invisible to renderers.
B. `Scope` has no transform, so it cannot move its children accidentally.
C. `Scope` prims cannot have children.
D. `Scope` is required by the model hierarchy.

**Answers**

- **Q23.1-1: B.** Partition scopes help people and tools find prims. A is performance, C is legibility, D is performance.
- **Q23.1-2: B.** `Scope` is an imageable prim with no xform ops. It *can* have children, and kinds do not require it.

### 13. Exam takeaways

> [!KEY]
> - Scalable = **legible, modular, performant, navigable**.
> - Workstreams (geometry, materials, …) become separate layers.
> - Partition with `Scope` prims; `_name` = internal, `__name` = reserved by USD.
> - Never make behavior depend on prim names.

---

## 23.2 Asset interfaces (entry layer, geo/mtl/payload layers)

### 1. What is it?

An **asset interface** is the public "front door" of an asset: a small **entry layer** with one **entry point prim** that others reference. The heavy content sits behind a **payload** in separate content layers (typically geometry and materials).

### 2. Why do we need it?

If a scene had to open every heavy file just to learn an asset's name, kind, or variants, opening a city would take minutes. The interface keeps that cheap information on top, so a stage can be opened *unloaded* and still show what each asset is and what options it offers.

### 3. Beginner explanation

Think of a product box in a shop. The **label** on the outside (name, size, colors available) is the entry layer. The **contents** inside the sealed box are the payload. You can browse a whole shelf of labels without opening a single box.

*Where the analogy breaks:* in USD you can "open the box" (load the payload) and "close it" again at any time, per prim, without losing your edits (Chapter 17).

### 4. Technical explanation

NVIDIA's recommended starting point is: **a referenceable text entry layer → containing a payload → to binary sublayers**.

- **Entry layer** (`Chair.usda` or `Chair.usd`): sets `defaultPrim`, and on the entry prim authors `kind`, `assetInfo`, `inherits` to a class, the *names* of variant sets with default selections, and optionally `extentsHint` via `UsdGeom.ModelAPI`. This is called **lofting** the cheap fields above the payload.
- **Payload layer** (`payload/contents.usd`): its job is to sublayer the content layers, e.g. `mtl.usdc` over `geo.usdc`. Keeping this middle layer lets you mute one content layer; a payload's *target* is treated as a root layer and cannot be muted.
- **Content layers** (`geo.usdc`, `mtl.usdc`): heavy data in binary **Crate** format (USDC), which reads only what composition needs.
- **Anchored paths** (`./payload/contents.usd`) are resolved relative to the layer that contains them, so the asset folder can be moved as a whole.
- This is the **reference-payload pattern**: users *reference* the asset; the payload is internal. They never need to know whether a payload exists.

Why text for the entry layer and binary for the content? Text (USDA) is easy to read and diff, but is always read fully into memory. That is fine for a tiny entry layer. Heavy layers should be USDC. Using the `.usd` extension lets you switch between text and binary later without breaking anyone's reference paths (Chapter 31).

### 5. Mental model

```text
  scene.usda                       (someone else's scene)
      |  references
      v
  Chair.usda  [entry layer, text]  kind, assetInfo, inherits,
      |                            variant set names, extentsHint
      |  payload  (can stay unloaded)
      v
  payload/contents.usda            subLayers = [mtl, geo]
      |                \
      v                 v
  payload/mtl.usdc   payload/geo.usdc     [binary content]
```

### 6. Simple example

```text
Chair/
    Chair.usda            entry layer (small, text)
    payload/
        contents.usda     sublayers the two below
        mtl.usdc          materials (binary)
        geo.usdc          geometry  (binary)
```

### 7. USDA example

*File: Chair/Chair.usda* (the entry layer)

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    kind = "component"
    assetInfo = {
        string name = "Chair"
    }
    prepend payload = @./payload/contents.usda@
)
{
}
```

*File: Chair/payload/contents.usda* (the payload layer)

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    subLayers = [
        @./mtl.usdc@,
        @./geo.usdc@
    ]
)
```

- The entry prim carries the cheap, important data. `assetInfo` advertises the asset name.
- `contents.usda` has no prims of its own; it only stacks the content layers. `mtl.usdc` is listed first, so it is stronger: materials may override geometry (for example by adding bindings).
- The content layers are binary, so they are not shown here; Section 23.5 shows what goes in them.

### 8. Python example

Build the whole asset on disk, open it **unloaded**, then load it.

```python
import os
from pxr import Usd, Sdf, UsdGeom

os.makedirs("Chair/payload", exist_ok=True)

# 1. Binary content layers (USDC): geometry and materials.
geo = Sdf.Layer.CreateNew("Chair/payload/geo.usdc")
geo_stage = Usd.Stage.Open(geo)
geo_stage.SetDefaultPrim(geo_stage.DefinePrim("/Chair", "Xform"))
UsdGeom.Scope.Define(geo_stage, "/Chair/geo")
UsdGeom.Cube.Define(geo_stage, "/Chair/geo/seat")
geo.Save()

mtl = Sdf.Layer.CreateNew("Chair/payload/mtl.usdc")
mtl_stage = Usd.Stage.Open(mtl)
mtl_stage.SetDefaultPrim(mtl_stage.OverridePrim("/Chair"))
UsdGeom.Scope.Define(mtl_stage, "/Chair/mtl")
mtl.Save()

# 2. The payload layer just sublayers the content layers.
contents = Sdf.Layer.CreateNew("Chair/payload/contents.usda")
contents.subLayerPaths.append("./mtl.usdc")
contents.subLayerPaths.append("./geo.usdc")
contents.defaultPrim = "Chair"
contents.Save()

# 3. The interface layer: small, text, lofted metadata + payload.
iface = Sdf.Layer.CreateNew("Chair/Chair.usda")
iface.ImportFromString("""#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    kind = "component"
    assetInfo = {
        string name = "Chair"
    }
    prepend payload = @./payload/contents.usda@
)
{
}
""")
iface.Save()

stage = Usd.Stage.Open("Chair/Chair.usda", Usd.Stage.LoadNone)
chair = stage.GetPrimAtPath("/Chair")
print("unloaded kind:", Usd.ModelAPI(chair).GetKind())
print("unloaded children:", [c.GetName() for c in chair.GetChildren()])
stage.Load("/Chair")
print("loaded children:", [c.GetName() for c in chair.GetChildren()])
names = sorted(os.path.basename(l.identifier) for l in stage.GetUsedLayers())
print("used layers:", [n for n in names if not n.startswith("anon")])
```

**Expected output**

```text
unloaded kind: component
unloaded children: []
loaded children: ['geo', 'mtl']
used layers: ['Chair.usda', 'contents.usda', 'geo.usdc', 'mtl.usdc']
```

Notice that the kind is readable *before* loading: it was lofted into the entry layer.

### 9. Real-world use case

A film studio opens a 20,000-asset city set with `Usd.Stage.LoadNone`. Layout artists see every building's name, kind, variant sets, and bounding box (from `extentsHint`), and load only the three buildings in camera. In manufacturing, a factory digital twin does the same with machines: engineers browse the line unloaded and load one robot cell to inspect it.

### 10. Common mistakes

> [!MISTAKE] Putting variant set *definitions* only inside the payload. When the payload is unloaded, users cannot see or set the variants. **Fix:** loft the variant set names and default selections onto the entry prim (empty variants are fine; the payload supplies the opinions).

> [!MISTAKE] Using absolute file paths inside the asset (`/mnt/proj/chair/geo.usdc`). **Fix:** use anchored relative paths (`./payload/geo.usdc`) so the folder can be moved or delivered.

> [!MISTAKE] Making the entry layer itself heavy (meshes in the text file). **Fix:** keep it tiny; heavy data goes in USDC behind the payload.

### 11. Exam traps

> [!TRAP] "Payloads are always better than references for assets." Not exactly: the recommended pattern is that users **reference** the entry layer and the asset **payloads** its own contents internally (reference-payload pattern).

> [!TRAP] The sublayer order in `contents.usda` matters: the **first** listed sublayer is the **strongest** (Chapter 15).

### 12. Practice questions

**Q23.2-1** A stage is opened with `Usd.Stage.LoadNone`. Which data on an asset's entry prim is still available? (Select two.)
A. `kind` authored on the entry prim
B. Meshes defined in `geo.usdc` behind the payload
C. Variant set names authored on the entry prim
D. Material bindings authored in `mtl.usdc`

**Q23.2-2** Why does the NVIDIA pattern place a `contents` layer between the payload arc and the `geo`/`mtl` layers?
A. Payloads can only target text files.
B. It lets you mute an individual content layer; the payload's target layer itself cannot be muted.
C. It makes the geometry load before the materials.
D. It is required for the asset to be instanceable.

**Answers**

- **Q23.2-1: A and C.** Both are lofted into the entry layer. B and D live behind the payload.
- **Q23.2-2: B.** Payload and reference targets are root layers of their own layer stacks; muting them causes a composition error. Sublayers of `contents` can be muted.

### 13. Exam takeaways

> [!KEY]
> - Default structure: **text entry layer → payload → binary sublayers** (`mtl`, `geo`).
> - Users **reference** the asset; the asset **payloads** its contents (reference-payload pattern).
> - **Loft** kind, `assetInfo`, inherits, variant set names, `extentsHint` above the payload.
> - Use anchored `./` paths and the `.usd` extension for flexibility.

---

## 23.3 Model hierarchy and kinds in practice

### 1. What is it?

The **model hierarchy** is a simplified, high-level view of a scene made from prims that carry **kind** metadata. Chapter 6 introduced the kinds. Here you learn the rule that makes a kind "count": a prim is a **model** only if its kind is a model kind *and* every ancestor is a `group` or `assembly` (or a kind derived from them).

### 2. Why do we need it?

A city scene may hold millions of prims. A tool that wants "all assets" should not visit every mesh and shader. The model hierarchy lets it stop at the **component** level, which is far fewer prims.

### 3. Beginner explanation

Think of a postal address: Country → City → Street → House. The post office does not care about the rooms inside a house. The address is the model hierarchy; the house is the component; the rooms are ordinary prims beneath it. If a house is listed with no street ("House 7, somewhere"), the post office cannot find it: a component without a valid chain of groups above it is not a model.

*Where the analogy breaks:* a real address is checked by people; in USD the rule is enforced automatically by `Usd` when it computes `IsModel()`.

### 4. Technical explanation

Built-in kinds (from `Kind.Registry.GetAllKinds()`): `model`, `group`, `assembly`, `component`, `subcomponent`. Their "is-a" relations:

```text
model  (abstract base; do not author it directly)
 |-- group
 |    '-- assembly
 '-- component
subcomponent   (NOT a model kind)
```

Rules, verified on USD 26.08:

1. A prim is a **model** (`prim.IsModel()`) if its kind is-a `model` *and* its parent is a **group** (or it is a root prim, whose parent is the pseudo-root).
2. A prim is a **group** (`prim.IsGroup()`) if it is a model and its kind is-a `group` (`group` or `assembly`).
3. `prim.IsComponent()` is true only for a *valid model* whose kind is-a `component`.
4. A component's descendants are **outside** the model hierarchy. A `component` inside a `component` is not a model. Use `subcomponent` for important inner prims.
5. A prim with no kind breaks the chain: any `component` below it is not a model.

APIs:

- `Usd.ModelAPI(prim).GetKind()` / `SetKind("component")` read and write the `kind` metadata. `prim.GetMetadata("kind")` works too.
- `Usd.ModelAPI(prim).IsKind("component")` checks the kind *and* the hierarchy by default (`Usd.ModelAPI.KindValidationModelHierarchy`). Pass `Usd.ModelAPI.KindValidationNone` to check only the token.
- `Kind.Registry.IsA("assembly", "group")` compares kind tokens (`True`).
- Traversal predicate `Usd.PrimIsModel` (and `Usd.PrimIsGroup`) prunes traversal: children of a non-matching prim are skipped. There is no `PrimIsComponent` predicate; filter with `prim.IsComponent()`.

> [!NOTE] Custom kinds (for example `a_location` derived from `assembly`) are registered through plugin info and checked with `Kind.Registry`. Chapter 38 covers them. NVIDIA's whitepaper recommends using custom kinds sparingly.

### 5. Mental model

```text
/City            assembly   model, group
  /Block_A       group      model, group
    /House_1     component  model, component   <-- model hierarchy stops here
      /Door      subcomponent  (marker only, not a model)
  /props         (no kind)  breaks the chain
    /Bench       component  NOT a model
```

### 6. Simple example

| Prim | Kind | Parent valid group? | `IsModel()` |
|------|------|---------------------|-------------|
| `/Kitchen` | assembly | root | True |
| `/Kitchen/Props` | group | yes | True |
| `/Kitchen/Props/Kettle` | component | yes | True |
| `/Kitchen/Clutter` | none | — | False |
| `/Kitchen/Clutter/Mug` | component | **no** | **False** |

### 7. USDA example

```usda
#usda 1.0

def Xform "Kitchen" (
    kind = "assembly"
)
{
    def Xform "Props" (
        kind = "group"
    )
    {
        def Xform "Kettle" (
            kind = "component"
        )
        {
            def Xform "Lid" (
                kind = "subcomponent"
            )
            {
            }
        }
    }

    def Xform "Clutter"
    {
        def Xform "Mug" (
            kind = "component"
        )
        {
        }
    }
}
```

- `Kitchen` → `Props` → `Kettle` is a valid chain: assembly → group → component.
- `Clutter` has no kind, so `Mug` is *not* a model even though it says `component`.
- `Lid` is a subcomponent: a useful label, but outside the model hierarchy.

### 8. Python example

```python
from pxr import Usd

stage = Usd.Stage.CreateInMemory()
stage.GetRootLayer().ImportFromString("""#usda 1.0

def Xform "Kitchen" (
    kind = "assembly"
)
{
    def Xform "Props" (
        kind = "group"
    )
    {
        def Xform "Kettle" (
            kind = "component"
        )
        {
            def Xform "Lid" (
                kind = "subcomponent"
            )
            {
            }
        }
    }

    def Xform "Clutter"
    {
        def Xform "Mug" (
            kind = "component"
        )
        {
        }
    }
}
""")

print(f"{'path':28} {'kind':13} model group component")
for prim in stage.Traverse():
    kind = Usd.ModelAPI(prim).GetKind() or "-"
    print(f"{str(prim.GetPath()):28} {kind:13} {prim.IsModel()!s:5} "
          f"{prim.IsGroup()!s:5} {prim.IsComponent()}")

print("model traversal:")
for prim in stage.Traverse(Usd.PrimIsModel):
    print(" ", prim.GetPath())
```

**Expected output**

```text
path                         kind          model group component
/Kitchen                     assembly      True  True  False
/Kitchen/Props               group         True  True  False
/Kitchen/Props/Kettle        component     True  False True
/Kitchen/Props/Kettle/Lid    subcomponent  False False False
/Kitchen/Clutter             -             False False False
/Kitchen/Clutter/Mug         component     False False False
model traversal:
  /Kitchen
  /Kitchen/Props
  /Kitchen/Props/Kettle
```

The `Usd.PrimIsModel` traversal never even visits `Clutter`'s children, which is exactly the pruning that makes the model hierarchy fast.

> [!VERSION] Verified on USD 26.08: a `component` whose parent has no kind returns `False` for `IsModel()` and `IsComponent()`; a `component` at the root of the stage returns `True`.

### 9. Real-world use case

A lighting tool lists "every asset in the shot" by traversing with `Usd.PrimIsModel` and keeping components. On a 5-million-prim set it visits a few thousand prims instead of millions. In AEC (architecture, engineering, construction), a building is an assembly, each floor a group, and each furniture item a component, so a facilities app can count chairs per floor instantly.

### 10. Common mistakes

> [!MISTAKE] Referencing a component under an organizational prim with no kind (`/World/Props/Chair` where `World` and `Props` have no kind). **Fix:** tag the ancestors `assembly`/`group`.

> [!MISTAKE] Referencing a component asset *inside* another component and leaving its kind as `component`. **Fix:** override the inner one to `subcomponent`, or restructure as an assembly ("package").

> [!MISTAKE] Tagging individual meshes as `component`. This makes the hierarchy deep and slow, the opposite of its purpose. **Fix:** components are whole products (a chair, a house).

### 11. Exam traps

> [!TRAP] `subcomponent` is **not** a model kind. `prim.IsModel()` is `False` for a subcomponent prim.

> [!TRAP] `assembly` is a kind of `group`. `IsGroup()` is `True` for assemblies. A `component` is a model but **not** a group.

> [!TRAP] Kind alone is not enough: `GetKind()` can return `"component"` while `IsComponent()` returns `False` because the ancestor chain is broken.

### 12. Practice questions

**Q23.3-1** `/World` (no kind) → `/World/Tree` (kind `component`). What does `/World/Tree.IsModel()` return?
A. True, because the kind is `component`
B. False, because `World` is not a group
C. True, because root-level prims are always models
D. It raises an error

**Q23.3-2** Which statements are true? (Select two.)
A. `Kind.Registry.IsA("assembly", "group")` is `True`.
B. A `subcomponent` prim is part of the model hierarchy.
C. `Usd.ModelAPI(prim).IsKind("component")` checks the model hierarchy by default.
D. Components may contain other valid component models.

**Answers**

- **Q23.3-1: B.** `/World/Tree` is not a root prim; its parent `World` has no group kind, so the chain is broken.
- **Q23.3-2: A and C.** Assembly derives from group; `IsKind` uses `KindValidationModelHierarchy` by default. Subcomponents are outside the hierarchy, and a component inside a component is not a model.

### 13. Exam takeaways

> [!KEY]
> - Model = model kind **+** every ancestor is group/assembly (or the prim is at the root).
> - `assembly` is-a `group`; `component` is-a `model`; `subcomponent` is **not** a model.
> - The hierarchy **stops at components**; use `subcomponent` inside.
> - Traverse with `Usd.PrimIsModel` to visit only the model hierarchy.

---

## 23.4 Modular, reusable components

### 1. What is it?

A **modular component** is a self-contained asset (geometry, materials, and its own class) that is published once and **referenced** many times into assemblies, with every use editable through the asset's **class** prim.

### 2. Why do we need it?

If each room copied the chair's data, fixing the chair would mean editing every room. With references, you fix the chair file once and every scene sees the fix. Classes let an assembly change all chairs (or one chair) without touching the source file.

### 3. Beginner explanation

A **reference** is like linking a reusable part from a catalog (Chapter 16). A **class** is like a style sheet every copy follows, even after later edits (Chapter 19). Change the catalog part and every product that links it updates. Change the style sheet and every copy changes its look.

*Where the analogy breaks:* the "catalog" is composed live. There is no copy step at all; the chair data exists only once on disk.

### 4. Technical explanation

What makes a component modular:

- **Self-contained:** everything it needs lives under its root prim, apart from shared material libraries. Relationship targets (like `material:binding`) **must point inside the referenced prim**. A target outside the reference's scope is ignored, with the warning "refers to a path outside the scope of the reference" (verified on USD 26.08).
- **One entry point:** the root prim is `defaultPrim`, is transformable (`Xform`), and has `kind = "component"`.
- **Inherits a class:** the entry prim inherits `/_class_/<AssetName>`. Because the class path is *outside* the referenced prim, it maps to the same path in the **referencing** stage. This is how an assembly can author `/_class_/Chair` and reach every chair (implied inherits, Chapter 19.5).
- **Public interface:** variant sets and primvars on the entry prim are the "knobs" downstream users may set. Prims and properties with a `_` prefix are internal.
- **Assemblies** reference components (and other assemblies), tag organizing prims `group`, and position each reference with transforms on the referencing prim.

### 5. Mental model

```text
          Chair.usda  (published once)
         /     |      \
   reference reference reference
       |       |        |
 /Room/Chair_0  Chair_1  Chair_2        <- assembly
       \       |        /
        inherit /_class_/Chair           <- one edit, all chairs
```

### 6. Simple example

| Want | Edit where | Affects |
|------|-----------|---------|
| Fix the seat shape for everyone | `Chair.usda` (source) | Every scene, every chair |
| Smaller seats in this room only | `/_class_/Chair` in the room | All chairs in this room |
| One chair different | `/Room/Chair_2/...` | Only that chair |

### 7. USDA example

*File: Chair.usda*

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

class "_class_"
{
    class "Chair"
    {
    }
}

def Xform "Chair" (
    kind = "component"
    prepend inherits = </_class_/Chair>
)
{
    def Scope "geo"
    {
        def Cube "seat"
        {
            double size = 1
        }
    }
}
```

*File: Room.usda*

```usda
#usda 1.0

over "_class_"
{
    over "Chair"
    {
        over "geo"
        {
            over "seat"
            {
                double size = 0.5
            }
        }
    }
}

def Xform "Room" (
    kind = "assembly"
)
{
    def "Chair_0" (
        prepend references = @./Chair.usda@
    )
    {
    }
}
```

- The class is empty in the source. It contributes nothing until someone writes to it.
- `Room.usda` writes `size = 0.5` into `/_class_/Chair`. Every chair in the room inherits it. Inherits (I) are stronger than references (R) in LIVERPS, so the class beats the source's `size = 1`.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom

CHAIR = """#usda 1.0
(
    defaultPrim = "Chair"
)

class "_class_"
{
    class "Chair"
    {
    }
}

def Xform "Chair" (
    kind = "component"
    prepend inherits = </_class_/Chair>
)
{
    def Scope "geo"
    {
        def Cube "seat"
        {
            double size = 1
        }
    }
}
"""
with open("Chair.usda", "w") as f:
    f.write(CHAIR)

stage = Usd.Stage.CreateInMemory()
room = stage.DefinePrim("/Room", "Xform")
Usd.ModelAPI(room).SetKind("assembly")
for i in range(3):
    chair = stage.DefinePrim(f"/Room/Chair_{i}", "Xform")
    chair.GetReferences().AddReference("./Chair.usda")
    UsdGeom.XformCommonAPI(chair).SetTranslate((i * 2.0, 0, 0))

# One edit in the assembly's class reaches every chair.
over = stage.OverridePrim("/_class_/Chair/geo/seat")
over.CreateAttribute("size", Sdf.ValueTypeNames.Double).Set(0.5)
stage.GetPrimAtPath("/Room/Chair_2/geo/seat").GetAttribute("size").Set(2.0)

for i in range(3):
    seat = stage.GetPrimAtPath(f"/Room/Chair_{i}/geo/seat")
    print(f"Chair_{i} seat size:", seat.GetAttribute("size").Get())
```

**Expected output**

```text
Chair_0 seat size: 0.5
Chair_1 seat size: 0.5
Chair_2 seat size: 2.0
```

`Chair_2`'s own local opinion (L) beats the class (I), so it keeps `2.0`.

### 9. Real-world use case

A game studio publishes one `StreetLamp` component and references it 400 times into a city assembly. When art direction wants warmer lamps at night, a lighting artist edits `/_class_/StreetLamp` in the night-time layer only. Daytime scenes are unaffected, and the source asset is untouched.

### 10. Common mistakes

> [!MISTAKE] Binding a component's mesh to a material outside the component (e.g. `/Looks/Wood`). After referencing, the binding target is ignored. **Fix:** keep materials under the asset root (`/Chair/mtl/...`) or reference a library material *into* the asset.

> [!MISTAKE] Editing the source asset to fix a problem that exists only in one scene. **Fix:** edit the class or the referencing prim in that scene's layer.

### 11. Exam traps

> [!TRAP] A class prim (`class` specifier) is **abstract**: it is not traversed by default and is not rendered. Its only job is to be inherited.

> [!TRAP] "Changing the class affects only instanceable copies." False: class edits affect every prim that inherits it, instanced or not (Chapter 24).

### 12. Practice questions

**Q23.4-1** A component asset binds `/Lamp/geo/bulb` to `</Library/Glow>`, a prim outside `/Lamp`. The asset is referenced at `/Street/Lamp_1`. What does the composed binding target?
A. `/Library/Glow`
B. `/Street/Library/Glow`
C. Nothing; the target is outside the reference scope and is ignored
D. `/Street/Lamp_1/Library/Glow`

**Q23.4-2** Why does an asset's entry prim inherit from `/_class_/<Asset>` even if the class is empty?
A. Inherits are required for references to work.
B. It gives downstream scenes a place to broadcast edits to every copy of the asset.
C. It makes the asset load faster.
D. It sets the asset's kind.

**Answers**

- **Q23.4-1: C.** Targets must be inside the referenced prim's namespace; others are dropped with a warning.
- **Q23.4-2: B.** The empty class is a "hook"; any layer can later author opinions there.

### 13. Exam takeaways

> [!KEY]
> - Component = self-contained, `defaultPrim`, `Xform` root, `kind = "component"`, inherits a class.
> - Relationship targets must stay **inside** the asset root.
> - Edit the **source** to fix everywhere, the **class** to change all copies in a scene, the **prim** to change one.

---

## 23.5 ASWF asset structure guidelines

### 1. What is it?

The **ASWF guidelines** (*Guidelines for Structuring USD Assets*, from the Academy Software Foundation USD Working Group) are community recommendations for a "minimum viable" USD asset: what a component, assembly, and group are, and how to lay out scopes, classes, files, and folders.

### 2. Why do we need it?

Objective 7.2 asks you to *document* asset structure guidelines. Shared vocabulary lets artists, tools, and studios talk about assets the same way. You can adopt the ASWF rules as a starting point instead of inventing your own.

### 3. Beginner explanation

Think of building codes for houses. They do not design your house, but they say "every bedroom needs a window" and "stairs need a rail". The ASWF guidelines are the building code for USD assets.

*Where the analogy breaks:* building codes are law; the ASWF guidelines are recommendations. Studios adapt them.

### 4. Technical explanation

**Component** (the basic published asset):

- `kind = "component"` on an `Xform` root prim that is the root layer's `defaultPrim`.
- Geometry behind a **payload**, so it can be deferred.
- Self-contained (shared material libraries are the usual exception).
- Inherits from at least one **class** prim.
- At least two `Scope`s: **`geo`** (visible geometry) and **`mtl`** (materials and shaders). Optional: purpose scopes under `geo` (`proxy`, `render`), and scopes such as `fx` or `lgt`.
- Set `purpose` on the scopes, not on every gprim.
- Variant sets live on the **root prim** so they are settable when unloaded or instanced. Start with one geometry and one material variant set.

**Assembly:**

- `kind = "assembly"`; references components or other assemblies.
- Intermediate organizing prims use `kind = "group"`.
- Usually **no payload of its own**: the components already have payloads, and nested payloads add overhead.
- Referenced components are often made **instanceable** (Chapter 24) or used as PointInstancer prototypes (Chapter 25).
- Assembly-level materials go in its own `mtl` scope; new geometry created by the assembly goes behind a payload with `component` kind.

**Group:** used *only* to keep the model hierarchy valid inside assemblies. **Do not put `group` kind on the root of a published asset.**

**Files:** a folder named after the asset, a root file named after the asset (`campfire.usd`), plus `payload.usd`, `geo.usd`, `mtl.usd`. The `.usd` extension is recommended for the root so it can switch between text and binary without breaking references. Extra data goes in subfolders (`maps`, `vdb`, …).

> [!NOTE] The ASWF examples name the class root `__class__`. The NVIDIA whitepaper notes that names starting with a double underscore are reserved for OpenUSD's own use, so this book uses `_class_`. Either way, the structure is the same.

### 5. Mental model

```text
COMPONENT                         ASSEMBLY
/apple        (Xform) component   /appleBowl     (Xform) assembly
    /geo      (Scope)                 /apples    (Xform) group
        /proxy (purpose=proxy)           /apple1 -> ref apple component
        /render(purpose=render)          /apple2 -> ref apple component
    /mtl      (Scope)                 /bowl      -> ref bowl component
/_class_                              /mtl       (Scope) optional
    /apple    (class) <- inherited  /_class_/appleBowl (class)
```

### 6. Simple example

Checklist for documenting a structure (Objective 7.2):

| Item | ASWF recommendation |
|------|---------------------|
| Root prim | `Xform`, `defaultPrim`, kind `component` or `assembly` |
| Organizing prims | `Scope` inside components; `group` kind inside assemblies |
| Scopes | `geo`, `mtl` (plus `fx`, `lgt`, … as needed) |
| Class | Root inherits one class |
| Payload | Components yes; assemblies usually no |
| Variants | On the root prim |
| Files | `<asset>/<asset>.usd`, `payload.usd`, `geo.usd`, `mtl.usd` |

### 7. USDA example

*File: apple.usda* (ASWF-style component entry layer)

```usda
#usda 1.0
(
    defaultPrim = "apple"
    upAxis = "Y"
)

class "_class_"
{
    class "apple"
    {
    }
}

def Xform "apple" (
    kind = "component"
    assetInfo = {
        string name = "apple"
    }
    prepend inherits = </_class_/apple>
    prepend payload = @./payload.usd@
)
{
}
```

- Root is an `Xform` with `component` kind and is the `defaultPrim`.
- The root inherits its class and payloads the content.
- The `geo` and `mtl` scopes come from the payload's layers.

### 8. Python example

A small checker that documents and enforces some ASWF rules. Here it catches a published asset whose root was wrongly tagged `group`.

```python
from pxr import Usd

stage = Usd.Stage.CreateInMemory()
stage.GetRootLayer().ImportFromString("""#usda 1.0
(
    defaultPrim = "AppleBowl"
)

class "_class_"
{
    class "AppleBowl"
    {
    }
}

def Xform "AppleBowl" (
    kind = "group"
)
{
    def Xform "apples"
    {
        def Xform "apple1" (
            kind = "component"
        )
        {
        }
    }
}
""")


def aswf_report(stage):
    problems = []
    root = stage.GetDefaultPrim()
    kind = Usd.ModelAPI(root).GetKind()
    if kind not in ("component", "assembly"):
        problems.append(f"root kind is '{kind}', expected component/assembly")
    if not root.GetInherits().GetAllDirectInherits():
        problems.append("root does not inherit from a class")
    for prim in stage.Traverse():
        if Usd.ModelAPI(prim).GetKind() == "component" and not prim.IsModel():
            problems.append(f"{prim.GetPath()} breaks the model hierarchy")
    if kind == "component":
        for scope in ("geo", "mtl"):
            if not root.GetChild(scope):
                problems.append(f"missing '{scope}' scope")
    return problems


for p in aswf_report(stage):
    print("-", p)
```

**Expected output**

```text
- root kind is 'group', expected component/assembly
- root does not inherit from a class
- /AppleBowl/apples/apple1 breaks the model hierarchy
```

The fix is: tag the root `assembly`, tag `apples` as `group`, and add `prepend inherits = </_class_/AppleBowl>`. Chapter 30 shows how to turn checks like this into real `UsdValidation` validators.

### 9. Real-world use case

A studio writes a one-page "asset spec" for vendors based on the ASWF layout. Every delivery is run through a checker like the one above before ingestion. Because vendor assets match the in-house layout, they drop straight into assemblies and instancing works without manual fixes.

### 10. Common mistakes

> [!MISTAKE] Publishing an asset root with `kind = "group"`. **Fix:** published roots are `component` or `assembly`; `group` is only for organizing inside assemblies.

> [!MISTAKE] Putting payloads on assemblies *and* components (nested payloads). **Fix:** payloads on components; assemblies reference them directly.

> [!MISTAKE] Defining variant sets deep inside the asset. **Fix:** put them on the root prim so users can select them even when the asset is instanced or unloaded.

### 11. Exam traps

> [!TRAP] ASWF scope names are **`geo`** and **`mtl`**. NVIDIA's whitepaper examples use `Geometry` and `Materials`. The *idea* (separate geometry and material scopes) is what matters; don't pick an answer just because of the spelling.

> [!TRAP] "Assemblies should payload their components." ASWF says assemblies usually do **not** need payloads because the components already have them.

### 12. Practice questions

**Q23.5-1** According to the ASWF guidelines, where should the `group` kind be used?
A. On the root prim of every published asset
B. On intermediate prims inside assemblies, to keep the model hierarchy valid
C. On the `geo` and `mtl` scopes of a component
D. On subcomponents

**Q23.5-2** Which are ASWF recommendations for a basic component? (Select two.)
A. Inherit from at least one class prim
B. Put every mesh in its own payload
C. Keep geometry behind a payload
D. Use `kind = "group"` on the root prim

**Answers**

- **Q23.5-1: B.** Groups exist only to organize assemblies and keep the hierarchy valid.
- **Q23.5-2: A and C.** One payload for the component's geometry, not one per mesh; `group` is never the published root kind.

### 13. Exam takeaways

> [!KEY]
> - Component: `Xform` root, `component` kind, `defaultPrim`, payload, class, `geo` + `mtl` scopes.
> - Assembly: `assembly` kind, `group` for intermediate prims, references components, usually no payload.
> - Never `group` on a published root. Variants on the root prim.
> - Use `.usd` for the root file; folder named after the asset.

---

## Chapter lab(s)

**Lab 22 — Build a component asset and an assembly** (`python-labs/lab22_*.md`, Obj 2.4, 7.2). You build an ASWF-style component on disk (entry layer, payload, `geo`/`mtl` USDC layers, class), reference it several times into an assembly with `group` organizers, verify the model hierarchy with `IsModel()`/`IsComponent()`, and open the assembly unloaded to confirm lofted data is visible.

## USDA reading exercises

**Exercise 23-A.** Which prims are valid models? Which are components?

```usda
#usda 1.0

def Xform "City" (
    kind = "assembly"
)
{
    def Xform "Block_A" (
        kind = "group"
    )
    {
        def Xform "House_1" (
            kind = "component"
        )
        {
            def Xform "Mailbox" (
                kind = "component"
            )
            {
            }
        }
    }

    def Scope "props"
    {
        def Xform "Bench" (
            kind = "component"
        )
        {
        }
    }
}
```

**Exercise 23-B.** An asset's entry layer contains `kind`, `assetInfo`, and `prepend payload = @./payload/contents.usd@`, while variant sets are defined only in `payload/geo.usdc`. A layout artist opens the scene with `Usd.Stage.LoadNone`. What can the artist see, what can't they see, and how would you fix it?

**Answers**

- **23-A.** Models: `/City`, `/City/Block_A`, `/City/Block_A/House_1`. Only `House_1` is a component. `Mailbox` is a component inside a component, so it is not a model (it should be `subcomponent`). `Bench` is not a model because its parent `props` has no kind. *(Verified by composing in USD 26.08: `IsModel()` is `False` for `Mailbox`, `props`, and `Bench`.)*
- **23-B.** They see the entry prim's kind and `assetInfo` (lofted), but no variant sets and no children, because those live behind the unloaded payload. Fix: loft the variant set names and default selections onto the entry prim in the entry layer.

## Chapter review

**Summary**

- Scalable asset structure is **legible, modular, performant, navigable** (NVIDIA whitepaper).
- Model workstreams as layers; partition prims with `Scope`; `_` = internal, `__` = reserved.
- Recommended start: **text entry layer → payload → binary sublayers**; users reference, the asset payloads (reference-payload pattern).
- **Loft** kind, `assetInfo`, inherits, variant set names, and `extentsHint` above the payload.
- Kinds: `assembly` is-a `group` is-a `model`; `component` is-a `model`; `subcomponent` is not a model.
- A prim is a model only if every ancestor is a group/assembly; the hierarchy stops at components.
- `Usd.PrimIsModel` traversal prunes to the model hierarchy.
- Components are self-contained; relationship targets outside the asset root are ignored after referencing.
- ASWF: `geo`/`mtl` scopes, class per asset, payload on components, `group` only inside assemblies, never on published roots.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| "component not showing in model traversal" | An ancestor lacks `group`/`assembly` kind |
| `kind = "component"` under another component | Should be `subcomponent` |
| "see variants while unloaded" | Loft variant sets onto the entry prim |
| "which kind for a published root?" | `component` or `assembly`, never `group` |
| "binding target dropped after reference" | Target was outside the referenced prim |
| "fix everywhere vs this scene only" | Source asset vs class in the scene layer |
| "entry layer format" | Small text layer; heavy data in USDC; `.usd` extension |
| "legible / modular / performant / navigable" | NVIDIA's four principles |

**Review questions**

**R23-1** (Obj 2.4) Which kind should an intermediate organizing prim between an assembly and its components have?
A. `component`
B. `subcomponent`
C. `group`
D. `model`

**R23-2** (Obj 2.4) Given `/Set` (assembly) → `/Set/Table` (component) → `/Set/Table/Drawer` (component), which is true?
A. Both `Table` and `Drawer` are components.
B. `Table` is a component; `Drawer` is not a model.
C. Neither is a model because `Set` is an assembly.
D. `Drawer` is a component; `Table` becomes a group.

**R23-3** (Obj 7.2) Which describes NVIDIA's suggested starting asset structure?
A. A binary entry layer that sublayers text geometry layers
B. A referenceable text entry layer containing a payload to binary sublayers
C. A single USDZ file per asset
D. One layer per prim, combined with references

**R23-4** (Obj 7.2) Select two items that should be lofted into an asset's entry layer.
A. Mesh `points`
B. Variant set names and default selections
C. Texture files
D. `kind` and `assetInfo`

**R23-5** (Obj 2.4) What does this print?

```{.python .norun}
print(Usd.ModelAPI(stage.GetPrimAtPath("/Shelf/Lid")).GetKind(),
      stage.GetPrimAtPath("/Shelf/Lid").IsModel())
# /Shelf is kind "component", /Shelf/Lid is kind "subcomponent"
```

A. `subcomponent True`
B. `subcomponent False`
C. `component False`
D. ` False`

**R23-6** (Obj 7.2) According to the ASWF guidelines, which statement is correct?
A. Assemblies should always add their own payload around referenced components.
B. Published asset roots should use the `group` kind.
C. A component should have at least `geo` and `mtl` scopes.
D. Purpose should be set on every individual mesh.

**R23-7** (Obj 2.4) A tool must list all component models in a huge stage as fast as possible. Best approach?
A. `stage.Traverse()` and check `GetKind() == "component"`
B. `stage.Traverse(Usd.PrimIsModel)` and keep prims where `IsComponent()` is true
C. `stage.Traverse(Usd.TraverseInstanceProxies())`
D. Search prim names for "component"

**R23-8** (Obj 7.2) Why is `.usd` recommended for the entry layer's extension?
A. `.usd` files load faster than `.usdc`.
B. It lets the file switch between text and binary without changing references to it.
C. Only `.usd` files may contain payloads.
D. `.usd` is required for `defaultPrim`.

**R23-9** (Obj 2.4) Select two true statements about `Usd.ModelAPI(prim).IsKind("component")`.
A. By default it also checks the model hierarchy.
B. It returns `True` for `assembly` prims.
C. With `Usd.ModelAPI.KindValidationNone` it checks only the kind token.
D. It changes the prim's kind.

**R23-10** (Obj 7.2) Which principle is served by naming a prim `LargeCardboardBox` instead of `Mesh_017`?
A. Performance
B. Modularity
C. Legibility
D. Navigability through the model hierarchy

**R23-11** (Obj 2.4) A component's mesh binds a material at `/Looks/Steel`, outside the component's root. After the component is referenced into an assembly, what happens?
A. The binding is remapped to `/Assembly/Looks/Steel`.
B. The binding target is ignored, with a warning.
C. The stage fails to open.
D. The material is copied into the assembly.

**R23-12** (Obj 7.2) Where should variant sets live, according to ASWF, and why?
A. On the `geo` scope, so they are near the geometry
B. On the root prim, so they can be set even when the asset is instanced or unloaded
C. In a separate variant layer referenced by every mesh
D. In the class prim only

**Review answers**

- **R23-1: C.** `group` keeps the chain valid. `model` is abstract and should not be authored. Review: §23.3.
- **R23-2: B.** The hierarchy stops at `Table`; a component inside a component is not a model. Review: §23.3.
- **R23-3: B.** Text interface layer → payload → binary sublayers. Review: §23.2.
- **R23-4: B and D.** Cheap, important fields are lofted; heavy data (points, textures) stays behind the payload. Review: §23.2.
- **R23-5: B.** `GetKind` returns the token; subcomponent is not a model kind. Review: §23.3.
- **R23-6: C.** A and B are the opposite of ASWF advice; D: set purpose on scopes. Review: §23.5.
- **R23-7: B.** The `PrimIsModel` predicate prunes below components; A visits every prim and ignores the hierarchy rule. Review: §23.3.
- **R23-8: B.** The extension does not fix the encoding; references keep working after a format switch. Review: §23.2.
- **R23-9: A and C.** It is a query only; assemblies are not components. Review: §23.3.
- **R23-10: C.** Clear names are legibility. Review: §23.1.
- **R23-11: B.** Out-of-scope targets are dropped ("refers to a path outside the scope of the reference"). Review: §23.4.
- **R23-12: B.** Root-level variant sets remain accessible on instance roots and unloaded prims. Review: §23.5.

## Further reading

- [S16] NVIDIA — *Principles of Scalable Asset Structure in OpenUSD*. https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
- [S17] ASWF USD Working Group — *Guidelines for Structuring USD Assets*. https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md
- [S14] NVIDIA Learn OpenUSD — *Understanding Model Kinds*; *Asset Structure Principles and Content Aggregation*. https://docs.nvidia.com/learn-openusd/latest/index.html
- [S04] OpenUSD Glossary — Kind, Model Hierarchy, Assembly, Component. https://openusd.org/release/glossary.html
- [S06] OpenUSD API — `UsdModelAPI`, `KindRegistry`. https://openusd.org/release/api/index.html
