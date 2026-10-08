# Chapter 38 — Kinds, Variant Fallbacks, File Formats, Resolvers, Scene Indices

> **Exam domain:** Customizing USD (6%) · **Objectives:** 3.3, 3.5, 3.7, 3.8 · **Study day:** 11 · **Est. time:** 80 min
> **Prerequisites:** Ch 6 / 23 (kinds), Ch 18 (variants), Ch 33 (Ar), Ch 36 (plugInfo), Ch 37 (schemas)

Chapter 36 named the four plugin jobs. This chapter fills the remaining **customizing** knobs: **custom kinds** (Obj 3.3), **variant fallbacks**, **file-format plugins**, **custom resolvers** (Obj 3.5, 3.8), and **Hydra scene indices** (Obj 3.7). `usd-core` can prove kinds, fallbacks, and file-format queries. C++ resolvers and scene indices stay conceptual, with verified Python around the edges.

## Learning goals

- Query the built-in kind tree with `Kind.Registry` and explain how a custom kind is *declared* (Obj 3.3).
- Set process-wide variant fallbacks and know they lose to authored selections.
- Identify a file-format plugin (`SdfFileFormat`, extensions, `IsPackage`).
- Restate how a custom `ArResolver` is integrated (Obj 3.5) and what Obj 3.8 adds.
- Describe a Hydra scene-index plugin at concept level (Obj 3.7).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Kind registry** | Catalog of kind tokens and their `baseKind` (`Kind.Registry`) |
| **Custom kind** | A studio token (e.g. `prop`) whose base is a built-in kind |
| **Variant fallback** | Default variant choice used when the prim has **no** authored selection |
| **File-format plugin** | `SdfFileFormat` subclass registered for an extension |
| **Package format** | A format that contains other files (USDZ); `IsPackage()` |
| **Scene index** | Hydra graph node that can generate or filter render prims |
| **Procedural resolver** | Resolver that can produce bytes / prims without a normal file (Obj 3.8) |

---

## 38.1 Custom model kinds (`Kind.Registry`)

### 1. What is it?

**Kinds** label a prim's role in the model hierarchy (`component`, `assembly`, `group`, `model`, `subcomponent`). A **custom kind** is an extra token you add to that catalog, always with a **base kind** so `IsA("prop", "component")` can still be true (Obj 3.3).

### 2. Why do we need it?

`component` is too coarse for a studio that wants to filter "only props" in a layout tool. A custom kind `prop` with `baseKind = component` keeps model-hierarchy rules (Ch 23) and gives tools a finer label.

### 3. Beginner explanation

Built-in kinds are the Linnaean ranks: animal / mammal / dog. A custom kind is "terrier": still a dog (`component`), just a studio nickname. Layout can say "select all terriers" without breaking `IsComponent()`.

*Where the analogy breaks:* you do **not** invent a rank *beside* `model` that is not based on `model`/`component`/`group` if you still want a valid model hierarchy. `subcomponent` is already "inside a component, not a model."

### 4. Technical explanation

Verified on USD 26.08:

| Call | Result here |
|------|-------------|
| `Kind.Registry.GetAllKinds()` | `assembly`, `component`, `group`, `model`, `subcomponent` |
| `GetBaseKind("component")` | `model` |
| `GetBaseKind("assembly")` | `group` |
| `GetBaseKind("group")` | `model` |
| `GetBaseKind("model")` | empty |
| `GetBaseKind("subcomponent")` | empty |
| `IsA("component", "model")` | True |
| `IsA("assembly", "model")` | True |
| `IsA("subcomponent", "model")` | **False** |
| `HasKind("door")` | False until a plugin declares it |

**There is no `Kind.Registry.Register` in this Python.** Custom kinds are declared in `plugInfo.json`:

```text
"Info": {
  "Kinds": {
    "prop": { "baseKind": "component" }
  }
}
```

A resource plugin registered at runtime in a 26.08 probe **did not** make `HasKind("prop")` True. Treat custom kinds as **startup** plugin data (often on the `kind` library's JSON), not as a live `Register` call.

Authoring still uses prim metadata: `Usd.ModelAPI(prim).SetKind("prop")` once the token exists. If the token is unknown, you can still *set the string*, but `IsA` / model queries will not treat it as a component.

### 5. Mental model

```text
  model
    component     <-- custom "prop" should base here
    group
      assembly
  subcomponent    (not a model; inside a component)
```

### 6. Simple example

Studio `plugInfo.json` adds `prop` → `baseKind: component`. Sets use `kind = "prop"` on furniture. `PrimIsModel` and `IsComponent()` still work because `IsA("prop", "component")` is designed to be True **after** the plugin loads.

### 7. USDA example

```usda
#usda 1.0

def Xform "Chair" (
    kind = "component"
)
{
    def Xform "Seat" (
        kind = "subcomponent"
    )
    {
    }
}
```

`Chair` is a model/component. `Seat` is not a model. A custom `prop` would replace `"component"` on `Chair` only after the kind plugin exists.

### 8. Python example

```python
from pxr import Kind

print("all", sorted(Kind.Registry.GetAllKinds()))
print("HasKind door", Kind.Registry.HasKind("door"))
print("base component", Kind.Registry.GetBaseKind("component"))
print("base assembly", Kind.Registry.GetBaseKind("assembly"))
print("base group", Kind.Registry.GetBaseKind("group"))
print("base model", repr(Kind.Registry.GetBaseKind("model")))
print("base subcomponent",
      repr(Kind.Registry.GetBaseKind("subcomponent")))
print("component IsA model", Kind.Registry.IsA("component", "model"))
print("assembly IsA model", Kind.Registry.IsA("assembly", "model"))
print("subcomponent IsA model",
      Kind.Registry.IsA("subcomponent", "model"))
print("component IsA group", Kind.Registry.IsA("component", "group"))
print("IsComponent component", Kind.Registry.IsComponent("component"))
print("IsModel assembly", Kind.Registry.IsModel("assembly"))
print("has Register", hasattr(Kind.Registry, "Register"))
```

**Expected output**

```text
all ['assembly', 'component', 'group', 'model', 'subcomponent']
HasKind door False
base component model
base assembly group
base group model
base model ''
base subcomponent ''
component IsA model True
assembly IsA model True
subcomponent IsA model False
component IsA group False
IsComponent component True
IsModel assembly True
has Register False
```

### 9. Real-world use case

A layout tool's "props only" filter uses `Kind.Registry.IsA(kind, "prop")` once `prop` is registered. Until IT ships the kind plugin, the same tool falls back to `IsComponent()` and over-selects characters.

### 10. Common mistakes

> [!MISTAKE] Inventing `kind = "hero"` with no `baseKind`. Model hierarchy tools ignore it. Fix: `baseKind` `component` or `assembly`.

> [!MISTAKE] `Kind.Registry.Register("prop")` in Python 26.08. The method **does not exist**. Use `plugInfo.json`.

> [!MISTAKE] `kind = "subcomponent"` on a published root. Published roots are `component` or `assembly` (Ch 23).

### 11. Exam traps

> [!TRAP] "`subcomponent` IsA `model`." False. The hierarchy **stops** at components.

> [!TRAP] "`assembly` bases on `component`." It bases on **`group`**, which bases on `model`.

> [!TRAP] "Custom kinds are schemas." Kinds are tokens in the kind registry, not `UsdTyped` classes.

### 12. Practice questions

**Q38.1-1.** `Kind.Registry.GetBaseKind("assembly")` is:
A. `component`
B. `group`
C. `subcomponent`
D. `assembly`

**Q38.1-2.** Select two true statements on 26.08 Python.
A. `HasKind("door")` is False until a plugin declares it
B. `Kind.Registry.Register` exists and is the official API
C. `IsA("subcomponent", "model")` is False
D. `GetAllKinds()` includes `prop` by default

**Answers**

- **Q38.1-1: B.** assembly → group → model.
- **Q38.1-2: A and C.** No `Register` in this Python; `prop` is not built-in.

### 13. Exam takeaways

> [!KEY]
> - Built-in tree: component→model, assembly→group→model, subcomponent not a model.
> - Custom kinds: `plugInfo.json` `Kinds` + `baseKind`; no Python `Register` here.
> - Obj 3.3: add a kind only when a tool must filter finer than component/assembly.

---

## 38.2 Variant fallback selections

### 1. What is it?

A **variant fallback** is a process-wide default: "if nobody authored a selection for variant set `lod`, pick `low`." You set it with `Usd.Stage.SetGlobalVariantFallbacks`. Plugins can also ship fallbacks in `plugInfo.json`. An **authored** `variants = { string lod = "high" }` always wins.

### 2. Why do we need it?

A games runtime wants every asset's `lod` set to `low` unless a shot pinned `high`. You should not edit a thousand entry layers. Fallbacks fill the gap when the selection is **missing** (Ch 18).

### 3. Beginner explanation

A thermostat schedule: "if nobody touched the dial, use 18 °C." If a guest set 22 °C, the schedule does not override them. Fallbacks are the schedule; authored `variants` are the dial.

*Where the analogy breaks:* fallbacks are **per process**, not per stage file. `SetGlobalVariantFallbacks` affects later `Stage.Open` calls in that process.

### 4. Technical explanation

Verified on USD 26.08:

```text
Usd.Stage.GetGlobalVariantFallbacks()  -> dict  (default {})
Usd.Stage.SetGlobalVariantFallbacks({"lod": ["low"]})
```

The value is a **list** of names (tried in order). With no authored selection, opening a layer that has `variantSet "lod" = { "high": Sphere, "low": Cube }` composed **Cube** and `GetVariantSelection("lod")` was `"low"`. With authored `variants = { string lod = "high" }` **and** fallback `low`, the child was still **Sphere**.

Without fallback *and* without authored selection, the variant set exists but **no child** `/A/G` composed.

`plugInfo.json` can declare plugin variant fallbacks (studio default `lod=low` for every DCC that loads the plugin). Python `SetGlobalVariantFallbacks` is the runtime equivalent for a player or test.

Reset to `{}` when the test ends so you do not leak defaults into the next Open in the same process.

### 5. Mental model

```text
  authored variants { lod = high }   -->  always wins
  else global / plugin fallback      -->  used
  else                               -->  no selection (children in variants missing)
```

### 6. Simple example

A batch renderer sets `SetGlobalVariantFallbacks({"lod": ["render"]})` then opens every shot. Artists who pinned `lod=proxy` in the shot keep proxy; everyone else gets render.

### 7. USDA example

*File: asset.usda* — **no** authored selection:

```usda
#usda 1.0

def Xform "A" (
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" {
            def Sphere "G"
            {
            }
        }
        "low" {
            def Cube "G"
            {
            }
        }
    }
}
```

Without a fallback, `/A/G` does not exist. With fallback `low`, `/A/G` is a Cube.

### 8. Python example

```python
from pxr import Usd

open("asset.usda", "w").write("""#usda 1.0
def Xform "A" (
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" {
            def Sphere "G" {}
        }
        "low" {
            def Cube "G" {}
        }
    }
}
""")
open("pinned.usda", "w").write("""#usda 1.0
def Xform "A" (
    variants = {
        string lod = "high"
    }
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" {
            def Sphere "G" {}
        }
        "low" {
            def Cube "G" {}
        }
    }
}
""")

Usd.Stage.SetGlobalVariantFallbacks({})
s = Usd.Stage.Open("asset.usda")
print("no fb child", bool(s.GetPrimAtPath("/A/G")))

Usd.Stage.SetGlobalVariantFallbacks({"lod": ["low"]})
s2 = Usd.Stage.Open("asset.usda")
print("fb type", s2.GetPrimAtPath("/A/G").GetTypeName())
print("fb sel",
      s2.GetPrimAtPath("/A").GetVariantSet("lod").GetVariantSelection())

s3 = Usd.Stage.Open("pinned.usda")
print("pinned type", s3.GetPrimAtPath("/A/G").GetTypeName())
Usd.Stage.SetGlobalVariantFallbacks({})
print("reset", Usd.Stage.GetGlobalVariantFallbacks())
```

**Expected output**

```text
no fb child False
fb type Cube
fb sel low
pinned type Sphere
reset {}
```

### 9. Real-world use case

usdview and a farm player load the same `prop` plugin that sets fallback `drawMode=cards` for huge sets. A lighting shot that authored `drawMode=default` still sees full geometry.

### 10. Common mistakes

> [!MISTAKE] Expecting fallbacks to override shot selections. Authored wins.

> [!MISTAKE] Setting fallbacks after `Stage.Open`. Open again (or open after the set).

> [!MISTAKE] `SetGlobalVariantFallbacks({"lod": "low"})` if the API wants a **list**. Use `["low"]`.

### 11. Exam traps

> [!TRAP] "Fallbacks are layer metadata." They are process (or plugin) defaults, not `defaultPrim`.

> [!TRAP] "Missing selection uses the first variant in the USDA file." Not guaranteed. Without fallback, the child may be **absent**.

### 12. Practice questions

**Q38.2-1.** Authored `lod=high` and fallback `["low"]`. Composed child?
A. Cube from `low`
B. Sphere from `high`
C. Both
D. Neither

**Q38.2-2.** Select two true statements.
A. No selection and no fallback → variant children may not compose
B. `SetGlobalVariantFallbacks` is per process
C. Fallbacks are stronger than `variants = { ... }`
D. Fallbacks require `usdGenSchema`

**Answers**

- **Q38.2-1: B.** Authored selection wins.
- **Q38.2-2: A and B.**

### 13. Exam takeaways

> [!KEY]
> - Fallbacks fill **missing** selections; authored `variants` win.
> - `SetGlobalVariantFallbacks({set: [names]})`; reset to `{}`.
> - No selection and no fallback can mean the variant's prims are gone.

---

## 38.3 File format plugins (`SdfFileFormat`)

### 1. What is it?

A **file-format plugin** teaches Sdf how to read (and maybe write) a file extension. Built-ins: `usda`, `usdc`, `usd`, `usdz`. A studio format (`.mygeo`, `.gltf` as USD) subclasses **`SdfFileFormat`** and lists `extensions` / `formatId` in `plugInfo.json` (Ch 36).

### 2. Why do we need it?

`Stage.Open("hero.abc")` only works if some plugin claimed `abc`. Otherwise you convert offline (Ch 27) instead of opening in place.

### 3. Beginner explanation

Windows "Open with…" for `.usda`. The format plugin is the app registered for that extension. USDZ is a **package** app: it also knows there are files *inside*.

*Where the analogy breaks:* `.usd` is one extension that may hold USDA *or* crate (Ch 31). The plugin still has `formatId` `usd`.

### 4. Technical explanation

Verified on USD 26.08:

| Query | Result |
|-------|--------|
| `Sdf.FileFormat.FindAllFileFormatExtensions()` | `usd`, `usda`, `usdc`, `usdz` |
| `FindByExtension("usda").formatId` | `usda` |
| `FindByExtension("usdz").IsPackage()` | True |
| `FindByExtension("usdz").SupportsWriting()` | **False** |
| `FindByExtension("usda").SupportsWriting()` | True |
| Owner plugin of `SdfUsdaFileFormat` | `sdf` |

`plugInfo.json` fields you already saw: `bases: ["SdfFileFormat"]`, `extensions`, `formatId`, `primary`. USDZ also sets `supportsWriting: false` in JSON — matching `SupportsWriting()`.

Obj 3.8 sometimes pairs a format with a **package resolver** (`ArPackageResolver`, as `Sdf_UsdzResolver` does for `.usdz`).

You cannot implement `SdfFileFormat` in this venv's pure Python. You *can* query the registry and know which `bases` to put in JSON.

### 5. Mental model

```text
  .usda  -->  SdfUsdaFileFormat   (text, writable)
  .usdc  -->  SdfUsdcFileFormat   (crate)
  .usd   -->  SdfUsdFileFormat    (either encoding)
  .usdz  -->  SdfUsdzFileFormat   (package, not writable as a layer)
  .mygeo -->  your SdfFileFormat plugin
```

### 6. Simple example

A CAD vendor registers `.sldprt` as a format plugin so `Stage.Open` tessellates on the fly. Pipelines that prefer a frozen mesh still run the Ch 29 converter instead.

### 7. USDA example

USDA is itself a format. Opening this file used `SdfUsdaFileFormat`:

```usda
#usda 1.0
(
    defaultPrim = "Box"
)

def Cube "Box"
{
    double size = 1
}
```

### 8. Python example

```python
from pxr import Sdf, Plug, Tf

print("extensions", sorted(Sdf.FileFormat.FindAllFileFormatExtensions()))
usda = Sdf.FileFormat.FindByExtension("usda")
usdz = Sdf.FileFormat.FindByExtension("usdz")
print("usda id", usda.formatId, "write", usda.SupportsWriting())
print("usdz id", usdz.formatId, "package", usdz.IsPackage(),
      "write", usdz.SupportsWriting())
print("abc", Sdf.FileFormat.FindByExtension("abc"))
t = Tf.Type.FindByName("SdfUsdaFileFormat")
print("usda plugin", Plug.Registry().GetPluginForType(t).name)
```

**Expected output**

```text
extensions ['usd', 'usda', 'usdc', 'usdz']
usda id usda write True
usdz id usdz package True write False
abc None
usda plugin sdf
```

### 9. Real-world use case

A VFX house opens `.abc` through a format plugin during layout, then publishes `.usdc` so lighting never depends on the Alembic plugin on the farm.

### 10. Common mistakes

> [!MISTAKE] Expecting `Stage.Save()` on a USDZ layer. `SupportsWriting` is False; rebuild the package (Ch 31).

> [!MISTAKE] Writing a resolver because you want a new extension. Extension → format plugin. Search path → resolver.

### 11. Exam traps

> [!TRAP] "USDZ is just crate with a different extension." It is a **package** format (`IsPackage` True).

> [!TRAP] "`FindByExtension('abc')` raises." It returns `None`.

### 12. Practice questions

**Q38.3-1.** `FindByExtension("usdz").IsPackage()` is:
A. False
B. True
C. An exception
D. `"usdc"`

**Q38.3-2.** Select two correct `bases` / jobs.
A. New `.mygeo` extension → `SdfFileFormat`
B. `@chair@` database lookup → `ArResolver`
C. New `.mygeo` extension → `UsdTyped`
D. USDZ write via `layer.Save()` because USDA writes

**Answers**

- **Q38.3-1: B.**
- **Q38.3-2: A and B.** USDZ `Save` is not supported on the format.

### 13. Exam takeaways

> [!KEY]
> - File-format plugin = `SdfFileFormat` + `extensions` / `formatId`.
> - Built-ins: four extensions; USDZ is a non-writable package.
> - `FindByExtension` returns `None` for unknown suffixes.

---

## 38.4 Custom asset resolvers (`ArResolver`)

### 1. What is it?

A **custom resolver** is an `ArResolver` plugin that changes how `@path@` becomes bytes (Obj 3.5). Obj 3.8 asks for a resolver that can **generate in-memory primitives** — a procedural lookup that does not need a file on disk.

### 2. Why do we need it?

Chapter 33 taught search paths and `DefaultResolver`. Studios still need `s3://`, database ids, or a resolver that *synthesizes* a cube when you open `@procedural:box@`.

### 3. Beginner explanation

The default librarian walks shelves. A custom librarian can phone a warehouse (Obj 3.5) or **print a new pamphlet on the spot** (Obj 3.8) when the card says `procedural:box`.

*Where the analogy breaks:* generating prims still has to look like a USD layer (or Hydra prims) to the rest of the stack. You do not `def Cube` from inside `Resolve` without a format/layer to parse.

### 4. Technical explanation

Integration recap (Ch 33, Ch 36), verified APIs still:

- `plugInfo.json`: `"bases": ["ArResolver"]` (or `ArPackageResolver` for packages)
- `PXR_PLUGINPATH_NAME` / `RegisterPlugins`
- `Ar.SetPreferredResolver("StudioResolver")` only after the type **loads** (fake names stay `DefaultResolver`)
- `Usd.Stage.Open(path, pathResolverContext=rc)`
- `GetRegisteredURISchemes()` is `[]` on this wheel until a URI plugin registers

Obj 3.8 (generate in-memory primitives): typical design is Resolve → `OpenAsset` returns a memory buffer of USDA/USDC that Sdf then parses, **or** a Hydra scene-index / procedural that emits render prims (Section 38.5). Both are C++ plugins. `usd-core` Python cannot subclass `Ar.Resolver` usefully.

Package relative paths (`a.usdz[b.usda]`) already use `ArPackageResolver` (`Sdf_UsdzResolver`).

### 5. Mental model

```text
  Obj 3.5  Resolve("chair") --> /prod/show/assets/chair/v022/chair.usda
  Obj 3.8  Resolve("procedural:box") --> in-memory USDA of a Cube
```

### 6. Simple example

`@s3://bucket/chair.usda@` needs a URI resolver (scheme `s3`). `@box@` that never touches disk needs Obj 3.8-style `OpenAsset` memory.

### 7. USDA example

The layer does not mention the plugin. Identifiers are just asset paths:

```usda
#usda 1.0

def "C" (
    prepend references = @chair@
)
{
}
```

Without the studio resolver and context, this is `ErrorInvalidAssetPath` (Ch 33).

### 8. Python example

```python
from pxr import Ar, Plug, Tf

print("underlying", type(Ar.GetUnderlyingResolver()).__name__)
print("schemes", Ar.GetRegisteredURISchemes())
t = Tf.Type.FindByName("ArDefaultResolver")
print("plugin", Plug.Registry().GetPluginForType(t).name)
print("package path",
      Ar.IsPackageRelativePath("a.usdz[b.usda]"))
Ar.SetPreferredResolver("NoSuchResolver")
print("after fake prefer", type(Ar.GetUnderlyingResolver()).__name__)
```

**Expected output**

```text
underlying DefaultResolver
schemes []
plugin ar
package path True
after fake prefer DefaultResolver
```

Same fail-closed behavior as Chapter 33: a name that did not load does not switch the resolver.

### 9. Real-world use case

A cloud renderer maps `@asset/chair@` to an object-store GET (Obj 3.5). A lookdev tool maps `@proc:uvgrid@` to an in-memory Mesh of a calibration grid (Obj 3.8) so artists never check a file in.

### 10. Common mistakes

> [!MISTAKE] Subclassing `Ar.Resolver` in a notebook. Load a C++ plugin (Ch 36).

> [!MISTAKE] Using a resolver to add `def Door`. That is a schema (Ch 37).

### 11. Exam traps

> [!TRAP] Obj 3.8 is `CreateInMemory()`. That API makes an empty stage, not a resolver that *generates* assets from an identifier.

> [!TRAP] Obj 3.5 is satisfied by `Resolve("./x")` from cwd. Integration means plugin + context + documented identifiers.

### 12. Practice questions

**Q38.4-1.** `@s3://bucket/a.usda@` on stock `usd-core`:
A. Works because `://` is enough
B. Fails until a URI resolver plugin registers `s3`
C. Is a prim path
D. Requires `kind = component`

**Q38.4-2.** Select two Obj 3.8 ideas.
A. `OpenAsset` returns a memory buffer of USDA
B. A scene index emits Hydra prims for `@proc:box@`
C. `Kind.Registry.Register`
D. `stage.Flatten()`

**Answers**

- **Q38.4-1: B.**
- **Q38.4-2: A and B.**

### 13. Exam takeaways

> [!KEY]
> - Custom resolvers: `ArResolver` + plugInfo + context (Obj 3.5).
> - Obj 3.8: identifier → in-memory layer or Hydra prims, still a plugin.
> - Fake `SetPreferredResolver` stays `DefaultResolver`.

---

## 38.5 Hydra scene index plugins (concepts)

### 1. What is it?

**Hydra** is USD's imaging architecture: a renderer-agnostic scene, then a **render delegate** (Storm, Karma, …). A **scene index** is a node in Hydra 2.0's scene graph that can filter, instance, or **generate** renderable prims. Obj 3.7: write a scene-index plugin that generates geometry as Hydra prims.

### 2. Why do we need it?

Some geometry should not live in USD layers at all: a procedural ocean, a CAD tessellation at render time, a point-cloud display. A scene index can create Hydra meshes when the renderer asks, without `def Mesh` in the USDA.

### 3. Beginner explanation

USD is the script. Hydra is the stage lighting and cameras of the *theatre*. A scene-index plugin is a technician who *builds extra scenery during the show* that was never in the script.

*Where the analogy breaks:* usdview *is* that theatre, and this wheel has **no** `UsdImaging`. You can register `usdHydra` schema types and still have no window. Obj 3.7 assumes a USD build with imaging (Ch 35).

### 4. Technical explanation

What this venv **can** prove:

- Plugin `usdHydra` is in `GetAllPlugins()` (shader discovery / Hydra API schemas).
- `import pxr.UsdImaging` fails on `usd-core`.

What a scene-index plugin **is** (exam-level, not runnable here):

- A C++ class implementing the Hydra scene-index API (filtering or generating `Hd` prims).
- Discovered via `plugInfo.json` like every other plugin (`bases` pointing at the scene-index type).
- Inserted into the imaging graph for usdview / a DCC viewport / a batch Hydra render.

Obj 3.7 vs 3.8: scene index generates **Hydra** prims (render). Procedural **resolver** generates **USD** bytes/layers (composition). You can use both: resolver provides a tiny overlay layer; scene index densifies it at render.

You do not author scene indices in USDA. You might author a typed prim the index *looks for* (`def DistantLight`, or a custom procedural schema).

> [!VERSION] `usd-core` 26.8: no Hydra runtime. Full `build_usd.py --usdview` (Ch 35) is required to *run* Obj 3.7.

### 5. Mental model

```text
  USD stage  -->  Hydra scene index chain  -->  render delegate
                     ^
                     |  your plugin can insert/generate prims here
```

### 6. Simple example

A "card" scene index turns unloaded payloads into bounding-box meshes for the viewport. The USDA still has payloads; Hydra never tessellates until you load (related to draw modes, Ch 26).

### 7. USDA example

The file the index might watch — still ordinary USD:

```usda
#usda 1.0

def Cube "ProxyCard"
{
    double size = 1
}
```

A generating index could *invent* this Cube at render without the layer existing. That is the point of Obj 3.7.

### 8. Python example

```python
from pxr import Plug

names = [p.name for p in Plug.Registry().GetAllPlugins()]
print("has usdHydra", "usdHydra" in names)
print("has usdGeom", "usdGeom" in names)
try:
    import pxr.UsdImaging  # noqa: F401
    print("UsdImaging", True)
except ModuleNotFoundError:
    print("UsdImaging", False)
```

**Expected output**

```text
has usdHydra True
has usdGeom True
UsdImaging False
```

The Hydra *schema plugin* is present. The imaging *module* is not. Obj 3.7 needs the latter in a real DCC/usdview.

### 9. Real-world use case

A digital-twin viewport uses a scene index to draw millions of instanced bolts from a table, while the USD layer only stores the table. The Hydra delegate never sees a million `def Cube` specs.

### 10. Common mistakes

> [!MISTAKE] Thinking `usdHydra` in `GetAllPlugins()` means usdview works. It does not on `usd-core`.

> [!MISTAKE] Implementing Obj 3.7 as `UsdGeom.Cube.Define` in a Python loop. That writes USD, not a Hydra scene index.

### 11. Exam traps

> [!TRAP] "Scene index = variant set." Unrelated. Variants are composition; scene indices are imaging.

> [!TRAP] Obj 3.7 is `plugInfo.json` for `usdGeom`. Geom schemas are not scene indices.

### 12. Practice questions

**Q38.5-1.** Obj 3.7 "generate renderable geometry as Hydra prims" is:
A. A scene-index plugin in a USD imaging build
B. `Kind.Registry`
C. `SetGlobalVariantFallbacks`
D. `Sdf.Layer.CreateAnonymous`

**Q38.5-2.** Select two true facts about this venv.
A. `usdHydra` appears in `GetAllPlugins()`
B. `UsdImaging` imports
C. `UsdImaging` does not import
D. Scene indices are authored as USDA `variantSet`

**Answers**

- **Q38.5-1: A.**
- **Q38.5-2: A and C.**

### 13. Exam takeaways

> [!KEY]
> - Scene index = Hydra 2.0 plugin that can generate/filter render prims (Obj 3.7).
> - Needs an imaging build; `usd-core` has `usdHydra` JSON but no `UsdImaging`.
> - Resolver (USD bytes) vs scene index (Hydra prims) — Obj 3.8 vs 3.7.

---

## Chapter lab(s)

**Lab 32** — Custom kinds & fallbacks: print the `Kind.Registry` table and a fallback vs authored-selection pair. Resolvers stay Lab 29; Hydra stays conceptual until you have usdview.

## USDA reading exercises

**Exercise 38-A.** A prim has `kind = "prop"` but `Kind.Registry.HasKind("prop")` is False. `IsComponent()`? What should IT ship?

**Exercise 38-B.** `variants` is not authored. Fallback is `lod=["low"]`. Variant set has `high` (Sphere) and `low` (Cube). What is `/A/G`?

**Answers**

- **38-A.** Unknown kind is just a string; it is **not** a component in the registry. Ship `plugInfo.json` `Kinds.prop.baseKind = component` at process start.
- **38-B.** A Cube named `G` (fallback applied).

## Chapter review

**Summary**

- Kinds: five built-ins; custom via `plugInfo` `Kinds` + `baseKind`; no Python `Register`.
- Fallbacks fill missing variant selections; authored wins; process-wide.
- File formats: `SdfFileFormat`; USDZ is a non-writable package.
- Resolvers: Obj 3.5 lookup, Obj 3.8 in-memory generation; still plugins.
- Scene indices: Obj 3.7 Hydra generation; not in `usd-core` imaging.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| `GetBaseKind("assembly")` | `group` |
| `subcomponent` IsA model | False |
| `Kind.Registry.Register` | Missing in 26.08 Python |
| Fallback vs `variants =` | Authored wins |
| `IsPackage` | USDZ |
| `SupportsWriting` False on usdz | Package via `CreateNewUsdzPackage` |
| Obj 3.7 | Hydra scene index, not `def Mesh` |
| Obj 3.8 | Resolver that synthesizes bytes/prims |

**Review questions**

**R38-1** (Obj 3.3) `GetBaseKind("component")` is:
A. `group`
B. `model`
C. `assembly`
D. `subcomponent`

**R38-2** (Obj 3.3) Select two true kind facts.
A. `IsA("assembly", "model")` is True
B. `IsA("subcomponent", "model")` is False
C. `HasKind("prop")` is True in stock usd-core
D. Python `Kind.Registry.Register` exists on 26.08

**R38-3** (Obj 3.3) Custom kind `prop` should declare:
A. `baseKind: component` in `plugInfo.json`
B. `inherits = </Typed>`
C. `formatId: prop`
D. `SdfFileFormat`

**R38-4** No authored selection, fallback `lod=["low"]`, variants high=Sphere low=Cube. `/A/G` is:
A. Sphere
B. Cube
C. Missing
D. Both

**R38-5** Select two fallback facts.
A. Authored `variants` beat fallbacks
B. `SetGlobalVariantFallbacks` is process-wide
C. Fallbacks are stronger than shot layers
D. Fallbacks require Hydra

**R38-6** (Obj 3.5) Custom path lookup plugin `bases`:
A. `ArResolver`
B. `UsdTyped`
C. `SdfFileFormat`
D. `UsdAPISchemaBase`

**R38-7** `FindByExtension("usdz")`:
A. `IsPackage` True, `SupportsWriting` False
B. Same as USDA
C. Raises
D. `formatId` `usda`

**R38-8** (Obj 3.7) Scene-index plugins generate:
A. Kind tokens
B. Hydra render prims
C. `plugInfo.json` Includes
D. `defaultPrim`

**R38-9** (Obj 3.8) Select two legal designs.
A. Resolver `OpenAsset` returns in-memory USDA
B. Scene index emits a mesh at render
C. `Kind.Registry.Register` in a notebook
D. `GetMajorVersion() == 26`

**R38-10** This venv:
A. `UsdImaging` imports; `usdHydra` missing
B. `usdHydra` present; `UsdImaging` missing
C. Both present
D. Both missing

**R38-11** Unknown extension `.abc`:
A. `FindByExtension` returns `None`
B. Raises `Tf.ErrorException`
C. Opens as USDA
D. Uses `DefaultResolver` to parse Alembic

**R38-12** (Obj 3.3) Published asset root `kind`:
A. `subcomponent`
B. `component` or `assembly` (custom kinds should still IsA those)
C. `model` authored as the token `model`
D. Empty so kinds stay flexible

**Review answers**

- **R38-1: B.** Review: §38.1.
- **R38-2: A and B.** Review: §38.1.
- **R38-3: A.** Review: §38.1.
- **R38-4: B.** Review: §38.2.
- **R38-5: A and B.** Review: §38.2.
- **R38-6: A.** Review: §38.4.
- **R38-7: A.** Review: §38.3.
- **R38-8: B.** Review: §38.5.
- **R38-9: A and B.** Review: §38.4–38.5.
- **R38-10: B.** Review: §38.5.
- **R38-11: A.** Review: §38.3.
- **R38-12: B.** Review: §38.1, Ch 23.

## Further reading

- [S06] OpenUSD API — `KindRegistry`, `UsdStage::SetGlobalVariantFallbacks`, `SdfFileFormat`, `ArResolver`, Hydra scene indices. https://openusd.org/release/api/index.html
- [S04] OpenUSD Glossary — Kind, Model Hierarchy, Hydra. https://openusd.org/release/glossary.html
- Chapter 23 (kinds in assets), Chapter 18 (variants), Chapter 33 (Ar), Chapter 36 (plugins).
