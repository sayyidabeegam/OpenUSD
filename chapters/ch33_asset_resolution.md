# Chapter 33 — Asset Resolution

> **Exam domain:** Pipeline Development (14%), also Customizing USD (6%) and Debugging (11%) · **Objectives:** 3.5, 6.3, 7.5, 7.7 · **Study day:** 10 · **Est. time:** 90 min
> **Prerequisites:** Ch 9.8 (asset values), Ch 16 (anchored references), Ch 32 (pins, `ComputeAllDependencies`)

An **asset path** is a string USD must turn into a real file (or package member). **Ar** (Asset Resolution) is the library that does that turn. Obj 7.7 is "validate asset paths are formatted correctly." Obj 3.5 / 7.5 are "integrate a custom resolver." Obj 6.3 is "resolve issues related to asset management" — the debugging face of the same facts.

## Learning goals

- Distinguish authored asset paths (`Sdf.AssetPath`, USDA `@…@`) from **resolved** filesystem paths.
- Anchor a relative path to the layer that wrote it (`CreateIdentifier`, `Sdf.Layer.ComputeAbsolutePath`).
- Use `Ar.DefaultResolverContext` and `Ar.ResolverContextBinder` / `Usd.Stage.Open(..., pathResolverContext=)` for search paths.
- Validate format and resolvability (Obj 7.7) without calling `Resolve` on a bare `./` path from the wrong working directory.
- Explain how a custom `ArResolver` plugin is installed and selected (Obj 3.5 / 7.5) without inventing APIs.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Asset path** | Authored string naming a dependency (`Sdf.AssetPath`, USDA `@./tex.png@`) |
| **Resolved path** | What Ar turned that string into (`Ar.ResolvedPath`); empty if missing |
| **Ar** | USD's asset-resolution library (`pxr.Ar`) |
| **Resolver** | The plugin that implements Resolve (`Ar.GetResolver()`) |
| **Default resolver** | Filesystem resolver shipped with USD (`Ar.DefaultResolver`) |
| **Anchor** | Interpret `./` / `../` relative to the **layer file**, not your shell cwd |
| **Search path** | Directories the default resolver tries for **context-dependent** paths |
| **Context-dependent path** | A path that uses the resolver context (no `./`, not absolute) |
| **Resolver context** | Per-stage (or bound) extra info, e.g. search directories |
| **URI scheme** | Prefix such as `s3:`; needs a resolver that registered that scheme |

---

## 33.1 Asset paths and Ar

### 1. What is it?

An **asset path** is a value whose job is to name another file. **Ar** is the USD library that **resolves** that name to bytes on disk (or inside a package). `pxr.Ar` sits under Sdf, Pcp, and Usd: composition cannot open a reference until Ar succeeds.

### 2. Why do we need it?

`@./tex/wood.png@` is not a Python path and not a prim path. If you treat it as either, textures go missing and references fail with `Pcp.ErrorInvalidAssetPath` (Obj 6.3).

### 3. Beginner explanation

A library catalog card says "Shelf B-12, *Wood Chair*." The card is the **asset path**. Walking to the shelf and picking up the book is **resolution**. Ar is the librarian. A custom resolver (Section 33.5) is a librarian who also understands warehouse codes such as `s3://…`.

*Where the analogy breaks:* the card can be relative to *which catalog you opened* (the layer), not relative to where you are standing (the process cwd). That surprise is Section 33.2.

### 4. Technical explanation

Verified on USD 26.08:

| Piece | Type / API | Role |
|-------|------------|------|
| Authored value | `Sdf.AssetPath`, USDA `@path@` | Stored on attributes, references, payloads, sublayers |
| Resolver singleton | `Ar.GetResolver()` | Process-wide resolver object |
| Underlying plugin | `Ar.GetUnderlyingResolver()` | Usually `DefaultResolver` in `usd-core` |
| Success / failure | `Ar.ResolvedPath` | `bool(resolved)` is `False` when empty |
| Package member | `pkg.usdz[foo.usda]` | `Ar.IsPackageRelativePath`, `JoinPackageRelativePath` |

`Sdf.AssetPath` fields (26.08):

| Field | Meaning |
|-------|---------|
| `path` / `authoredPath` | What was written |
| `resolvedPath` | Filled after composition **Get()** if Ar found the file |
| `evaluatedPath` | Used with asset-path expressions; empty in simple cases |

USDA uses `@…@` for asset paths and `</…>` for **prim** paths. Mixing them is an exam favorite.

`Ar.GetRegisteredURISchemes()` is **empty** with stock `usd-core` (filesystem only). `s3://` is not understood until a URI resolver plugin is loaded.

> [!VERSION] Verified on USD 26.08. Older snippets call `resolver.AnchorRelativePath`. That method is **not** on `Ar.Resolver` in 26.08. Use `CreateIdentifier` with an anchor, or `Sdf.Layer.ComputeAbsolutePath`.

### 5. Mental model

```text
  USDA  @./tex/wood.png@     authored asset path
           |
           v
  Ar.GetResolver().Resolve(...)     (needs a correct identifier)
           |
           v
  Ar.ResolvedPath("/abs/.../wood.png")   or   Ar.ResolvedPath()  (empty)
```

### 6. Simple example

`asset tex = @./tex/wood.png@` on `/Chair`. After `Usd.Stage.Open` of that layer, `attr.Get().resolvedPath` is the absolute file. `attr.Get().path` is still `./tex/wood.png`.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair"
{
    asset tex = @./tex/wood.png@
}
```

- `@./tex/wood.png@` — asset path (file).
- `</Chair>` would be a prim path, not a file. Do not write `asset tex = </Chair>`.

### 8. Python example

```python
from pxr import Ar, Sdf, Usd
import os

os.makedirs("tex", exist_ok=True)
open("tex/wood.png", "wb").write(b"PNG")

stage = Usd.Stage.CreateNew("chair.usda")
prim = stage.DefinePrim("/Chair")
stage.SetDefaultPrim(prim)
attr = prim.CreateAttribute("tex", Sdf.ValueTypeNames.Asset)
attr.Set(Sdf.AssetPath("./tex/wood.png"))
stage.Save()

ap = attr.Get()
print("Get:", ap)
print("type:", type(ap).__name__)
print("path:", ap.path)
print("resolved nonempty:", bool(ap.resolvedPath))
print("resolver:", type(Ar.GetResolver()).__name__)
print("underlying:", type(Ar.GetUnderlyingResolver()).__name__)
print("URI schemes:", Ar.GetRegisteredURISchemes())
print("empty ResolvedPath bool:", bool(Ar.GetResolver().Resolve("nope.png")))
print("package?", Ar.IsPackageRelativePath("a.usdz[b.usda]"))
print("join:", Ar.JoinPackageRelativePath("a.usdz", "b.usda"))
```

**Expected output**

```text
Get: @./tex/wood.png@
type: AssetPath
path: ./tex/wood.png
resolved nonempty: True
resolver: Resolver
underlying: DefaultResolver
URI schemes: []
empty ResolvedPath bool: False
package? True
join: a.usdz[b.usda]
```

`GetResolver()` returns the facade type `Resolver`. The plugin doing filesystem work is `DefaultResolver`.

### 9. Real-world use case

A shot references `@./sets/kitchen.usda@` and a shader points at `@./tex/tile.png@`. usdview opens because Ar resolved both. A farm machine without the `tex/` folder still opens the USDA (the layer parses) but `resolvedPath` is empty and the render is black — an **asset management** bug (Obj 6.3), not a Mesh bug.

### 10. Common mistakes

> [!MISTAKE] Storing a texture as `string` instead of `asset`. Strings do not resolve. Fix: `Sdf.ValueTypeNames.Asset`.

> [!MISTAKE] Writing `asset tex = </tex/wood.png>`. Angle brackets are prim paths.

> [!MISTAKE] Assuming `s3://bucket/x.png` works with `usd-core` out of the box. `GetRegisteredURISchemes()` is `[]`. You need a URI resolver plugin (Section 33.5).

### 11. Exam traps

> [!TRAP] "`Ar.GetResolver()` returns `DefaultResolver`." It returns `Resolver`. Ask `GetUnderlyingResolver()` for the plugin class.

> [!TRAP] "`resolvedPath` is always filled on `Sdf.AssetPath('./x.png')` you just constructed." Only composition **Get()** (or the two-argument constructor) fills it.

> [!TRAP] Calling `AnchorRelativePath` in 26.08. The method is gone from `Ar.Resolver`.

### 12. Practice questions

**Q33.1-1.** USDA `@./a.png@` is:
A. A prim path
B. An asset path
C. A resolved filesystem path
D. A URI scheme registered by default

**Q33.1-2.** Select two true statements on USD 26.08 `usd-core`.
A. `bool(Ar.GetResolver().Resolve("missing"))` is `False`
B. `Ar.GetRegisteredURISchemes()` is empty
C. `Ar.GetResolver()` is a `DefaultResolver` instance
D. `AnchorRelativePath` is the supported anchoring API

**Answers**

- **Q33.1-1: B.** `@…@` marks an asset path. The resolved file is a different object.
- **Q33.1-2: A and B.** The facade is `Resolver`; `AnchorRelativePath` is gone.

### 13. Exam takeaways

> [!KEY]
> - `@…@` = asset path; `</…>` = prim path; `Ar.ResolvedPath` = lookup result.
> - `bool(empty_resolved)` is `False`; that is how you test "missing."
> - Stock `usd-core` has no URI schemes; filesystem `DefaultResolver` only.
> - Do not call `AnchorRelativePath` on 26.08.

---

## 33.2 `Ar.GetResolver()`, resolve, and anchoring

### 1. What is it?

**Resolve** asks the resolver for a `ResolvedPath`. **Anchoring** means a relative asset path is interpreted against the **layer that authored it**, not against the process current working directory.

### 2. Why do we need it?

`Ar.GetResolver().Resolve("./tex/wood.png")` from a script whose cwd is the show root returns empty, even though the texture sits next to `assets/chair.usda`. Composition still finds it, because Pcp **anchors first**. If you copy the naive `Resolve` into a validator, you fail good files (Obj 7.7 / 6.3).

### 3. Beginner explanation

A note in a cookbook says "see the sauce recipe in `./sauces/pesto.md`." `./` means "the folder this cookbook lives in," not "whatever kitchen you are standing in." Anchoring opens the cookbook's folder first, then walks `sauces/pesto.md`.

*Where the analogy breaks:* if the path has **no** `./` (`pesto.md` or `sauces/pesto.md`), the default resolver may instead walk a **search path** (Section 33.3). That is a different rule, not "also the cookbook folder" in Python `Resolve`.

### 4. Technical explanation

Verified on USD 26.08:

**1. Naive `Resolve` uses cwd / search path, not the layer.**

```text
Ar.GetResolver().Resolve("./tex/wood.png")
```

This looks for `tex/wood.png` under the process cwd. If your script ran in `show/` and the layer lives in `show/assets/`, the result is empty.

**2. Anchor, then resolve.** Two equivalent tools:

| API | What it does |
|-----|----------------|
| `layer.ComputeAbsolutePath("./tex/wood.png")` | Join the path to the layer's directory; returns a string (even if the file is missing) |
| `resolver.CreateIdentifier("./tex/wood.png", Ar.ResolvedPath(layer.realPath))` | Build the identifier Ar expects, anchored at that layer | then `Resolve(identifier)` |

`ComputeAbsolutePath` does **not** check existence. `Resolve` on that absolute string does.

**3. Composition already anchored.** After `Usd.Stage.Open("assets/chair.usda")`, `attr.Get().resolvedPath` is filled when the file exists. Prefer that field in validators that already have a stage.

**4. `CreateIdentifier("./tex/wood.png")` with no anchor** strips `./` and yields `tex/wood.png`, which is then **context-dependent** (search path), not layer-relative. Always pass the anchor `ResolvedPath` when you mean "relative to this layer."

**5. `GetExtension(path)`** returns the suffix without the dot (`usda`, `PNG`). Case follows the string you passed.

### 5. Mental model

```text
  WRONG:  Resolve(authored "./tex/wood.png")     <- cwd
  RIGHT:  ComputeAbsolutePath -> Resolve(abs)
  RIGHT:  CreateIdentifier(path, ResolvedPath(layer.realPath)) -> Resolve
  RIGHT:  stage Get() -> asset.resolvedPath
```

### 6. Simple example

Layer `assets/chair.usda` authors `@./tex/wood.png@`. File exists at `assets/tex/wood.png`. From cwd `show/`: naive Resolve is false; anchored Resolve is true; composed `Get().resolvedPath` is nonempty.

### 7. USDA example

*File: assets/chair.usda*

```usda
#usda 1.0

def Xform "Chair"
{
    asset tex = @./tex/wood.png@
}
```

The `./` is the signal: "anchor me to this file's directory."

### 8. Python example

```python
from pxr import Ar, Sdf, Usd
import os

os.makedirs("assets/tex", exist_ok=True)
open("assets/tex/wood.png", "wb").write(b"PNG")
open("assets/chair.usda", "w").write("""#usda 1.0
def Xform "Chair"
{
    asset tex = @./tex/wood.png@
}
""")

r = Ar.GetResolver()
print("naive Resolve ./tex/wood.png:",
      bool(r.Resolve("./tex/wood.png")))

layer = Sdf.Layer.FindOrOpen("assets/chair.usda")
abs_path = layer.ComputeAbsolutePath("./tex/wood.png")
print("ComputeAbsolutePath is file:", os.path.isfile(abs_path))
print("Resolve abs:", bool(r.Resolve(abs_path)))

ident = r.CreateIdentifier(
    "./tex/wood.png", Ar.ResolvedPath(layer.realPath))
print("CreateIdentifier then Resolve:", bool(r.Resolve(ident)))
print("GetExtension:", r.GetExtension(ident))

no_anchor = r.CreateIdentifier("./tex/wood.png")
print("CreateIdentifier no anchor:", no_anchor)

stage = Usd.Stage.Open("assets/chair.usda")
ap = stage.GetPrimAtPath("/Chair").GetAttribute("tex").Get()
print("composed resolved nonempty:", bool(ap.resolvedPath))
```

**Expected output**

```text
naive Resolve ./tex/wood.png: False
ComputeAbsolutePath is file: True
Resolve abs: True
CreateIdentifier then Resolve: True
GetExtension: png
CreateIdentifier no anchor: tex/wood.png
composed resolved nonempty: True
```

The first line is the bug. The next lines are the fix. The last line is what a stage-based validator should read.

### 9. Real-world use case

A CI validator ran `Resolve(attr.Get().path)` from the repo root and failed every asset. Switching to `bool(attr.Get().resolvedPath)` (after `Stage.Open` of the entry layer) matched usdview: good files pass, missing textures fail.

### 10. Common mistakes

> [!MISTAKE] Validating with `os.path.exists(ap.path)` on `./tex/wood.png`. That is cwd-relative in Python too. Fix: `ComputeAbsolutePath` or `resolvedPath`.

> [!MISTAKE] `CreateIdentifier("./x.png")` without the anchor `ResolvedPath`. You just converted an anchored path into a search-path path.

> [!MISTAKE] Treating `ComputeAbsolutePath` as "the file exists." It always concatenates. Then `Resolve` or `os.path.isfile`.

### 11. Exam traps

> [!TRAP] "Relative paths resolve from the process cwd, as in Python `open`." For **composed** USD they resolve from the **layer**. For raw `Ar.Resolve` they do not — unless you anchored.

> [!TRAP] "`resolvedPath` on Get() is cwd-based." It is composition-based (anchored).

> [!TRAP] `CreateIdentifier` with a `s3://` URL on the default resolver. 26.08 collapsed `s3://bucket/x` to `s3:/bucket/x` in a probe. URI paths need a URI resolver, not the default filesystem identifier logic.

### 12. Practice questions

**Q33.2-1.** A layer at `assets/chair.usda` authors `@./tex/wood.png@`. Your script's cwd is the show root. `Ar.GetResolver().Resolve("./tex/wood.png")` returns empty. The file is on disk. What is wrong?
A. USDA forbids `./`
B. Resolve was not anchored to the layer
C. The texture must be USDC
D. `GetResolver()` is the wrong module; use Sdf

**Q33.2-2.** Select two correct ways to test that the texture exists.
A. `bool(stage.GetPrimAtPath("/Chair").GetAttribute("tex").Get().resolvedPath)`
B. `os.path.isfile(layer.ComputeAbsolutePath("./tex/wood.png"))`
C. `os.path.exists("./tex/wood.png")` from the show root
D. `CreateIdentifier("./tex/wood.png")` with no second argument, then `Resolve`

**Answers**

- **Q33.2-1: B.** Anchor with `CreateIdentifier` + layer `ResolvedPath`, or `ComputeAbsolutePath`.
- **Q33.2-2: A and B.** C is cwd. D strips `./` and uses search paths.

### 13. Exam takeaways

> [!KEY]
> - Raw `Resolve("./…")` is cwd-relative. Composition is layer-relative.
> - Anchor with `CreateIdentifier(path, ResolvedPath(layer.realPath))` or `ComputeAbsolutePath`.
> - Prefer `Get().resolvedPath` when you already opened the stage.
> - `CreateIdentifier` without an anchor drops `./` and changes the meaning.

---

## 33.3 Resolver contexts and search paths

### 1. What is it?

A **resolver context** is extra data the resolver uses for this lookup (or this stage). For `DefaultResolver`, that data is a **search path**: a list of directories to try for **context-dependent** asset paths. You bind it with `Ar.ResolverContextBinder` or pass it to `Usd.Stage.Open(..., pathResolverContext=)`.

### 2. Why do we need it?

Studios want to write `@chair.usda@` (no `./`) and have Ar find the published chair via a configured list of asset roots — the same idea as Chapter 32's pin, but looked up by **name** instead of a long relative path. Without a context, `@chair.usda@` only succeeds if that file sits in the cwd (or next to the layer, when composition anchors it as a file-relative identifier).

### 3. Beginner explanation

Search path is `PATH` for assets. `chair.usda` is like the command `python`: the shell walks `PATH`. `./chair.usda` is like `./python`: only the current folder (here: the layer's folder), never `PATH`.

*Where the analogy breaks:* USD search paths do **not** override a file already in cwd for some lookups, and they never apply to paths that `IsContextDependentPath` says are false (`./`, `../`, absolute).

### 4. Technical explanation

Verified on USD 26.08:

**Context-dependent or not** (`resolver.IsContextDependentPath(s)`):

| Path | Context-dependent? | Meaning |
|------|--------------------|---------|
| `chair.usda` | True | Walk search path (and cwd rules) |
| `tex/wood.png` | True | Same |
| `./chair.usda` | False | Anchored; not a search |
| `/abs/chair.usda` | False | Absolute filesystem |

**Build and bind a context:**

```{.python .norun}
ctx = Ar.DefaultResolverContext(["/show/assets"])
rc = Ar.ResolverContext(ctx)
with Ar.ResolverContextBinder(rc):
    Ar.GetResolver().Resolve("chair.usda")
# or:
Usd.Stage.Open("shot.usda", pathResolverContext=rc)
```

`DefaultResolverContext(["searchA"])` stores **absolute** directories (`GetSearchPath()`). Relative inputs are expanded.

`resolver.GetCurrentContext()` inside the binder is non-empty; after the `with` it is empty again. `Usd.Stage.Open(..., pathResolverContext=)` **stores** the context on the stage (`stage.GetPathResolverContext()`), so later resolves for that stage keep using it.

**`SetDefaultSearchPath`** on `Ar.DefaultResolver` is process-global. Prefer a per-stage context so tests and tools do not leak search paths.

A shot that writes `@chair.usda@` (no `./`) **fails** to open the reference without a search path if `chair.usda` is not next to the shot. The local `def "C"` still exists; `GetCompositionErrors()` contains `ErrorInvalidAssetPath` (Obj 6.3). The same shot **succeeds** when opened with `DefaultResolverContext` pointing at the assets folder.

### 5. Mental model

```text
  @./chair.usda@     -> layer folder only     (pin by relative path, Ch 32)
  @chair.usda@       -> search path / context (pin by lookup)
  @/mnt/show/...@    -> absolute; brittle
```

### 6. Simple example

`searchA/tex/wood.png` exists. Unbound `Resolve("tex/wood.png")` is empty. Bound to `DefaultResolverContext(["searchA"])`, Resolve finds `searchA/tex/wood.png`. `Resolve("./tex/wood.png")` stays empty — `./` is not a search.

### 7. USDA example

*File: shot.usda* — lookup-style reference, not a relative pin.

```usda
#usda 1.0

def Xform "W"
{
    def "C" (
        prepend references = @chair.usda@
    )
    {
    }
}
```

This is legal USDA. It is not a complete pipeline pin until a resolver context (or a `./` path) says **which** `chair.usda`.

### 8. Python example

```python
from pxr import Ar, Usd
import os

os.makedirs("searchA/tex", exist_ok=True)
open("searchA/tex/wood.png", "wb").write(b"A")
os.makedirs("assets", exist_ok=True)
open("assets/chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" {}
""")
open("shot.usda", "w").write("""#usda 1.0
def Xform "W"
{
    def "C" (
        prepend references = @chair.usda@
    )
    {
    }
}
""")

r = Ar.GetResolver()
print("unbound tex/wood.png:", bool(r.Resolve("tex/wood.png")))
print("dependent tex/wood.png:", r.IsContextDependentPath("tex/wood.png"))
print("dependent ./tex/wood.png:", r.IsContextDependentPath("./tex/wood.png"))

ctx = Ar.DefaultResolverContext([os.path.abspath("searchA")])
with Ar.ResolverContextBinder(Ar.ResolverContext(ctx)):
    rp = r.Resolve("tex/wood.png")
    print("bound tex/wood.png:", bool(rp), os.path.relpath(str(rp)))
    print("bound ./tex/wood.png:", bool(r.Resolve("./tex/wood.png")))

print("after unbind:", bool(r.Resolve("tex/wood.png")))

rc_assets = Ar.ResolverContext(
    Ar.DefaultResolverContext([os.path.abspath("assets")]))
ok = Usd.Stage.Open("shot.usda", pathResolverContext=rc_assets)
bad = Usd.Stage.Open("shot.usda")
print("with context errors:", len(ok.GetCompositionErrors()),
      "type:", ok.GetPrimAtPath("/W/C").GetTypeName())
print("no context errors:", len(bad.GetCompositionErrors()),
      "err:", type(bad.GetCompositionErrors()[0]).__name__)
```

**Expected output**

```text
unbound tex/wood.png: False
dependent tex/wood.png: True
dependent ./tex/wood.png: False
bound tex/wood.png: True searchA/tex/wood.png
bound ./tex/wood.png: False
after unbind: False
with context errors: 0 type: Xform
no context errors: 1 err: ErrorInvalidAssetPath
```

Search paths find `tex/wood.png`. They do **not** find `./tex/wood.png`. The shot's `@chair.usda@` needs the assets directory in the **stage** context.

### 9. Real-world use case

A factory digital twin configures every `Usd.Stage.Open` with `DefaultResolverContext([os.environ["SHOW_ASSETS"]])`. Artists write `@robot.usda@`. IT moves the asset root between sites; shots do not change. Chapter 32's folder pins (`@../../../assets/robot/v014/robot.usda@`) are the other school: no search path, explicit relative path. Both are valid; mixing them without documenting which one you use is how Obj 6.3 bugs start.

### 10. Common mistakes

> [!MISTAKE] Expecting `@./chair.usda@` to use the search path. `./` disables it.

> [!MISTAKE] Setting `SetDefaultSearchPath` in a library and forgetting to clear it. Later tests resolve the wrong chair. Fix: `ResolverContextBinder` or `pathResolverContext`.

> [!MISTAKE] Assuming a failed reference deletes the prim. The local `def "C"` remains; check `GetCompositionErrors()`.

### 11. Exam traps

> [!TRAP] "Search path applies to every relative path." Only **context-dependent** paths.

> [!TRAP] "Open with a context mutates the process resolver forever." The binder is scoped; the stage argument sticks to **that stage**.

> [!TRAP] Printing `GetLayerStack()[0]` to debug a missing reference. The session layer is first (Ch 32). Look at composition errors and `resolvedPath`.

### 12. Practice questions

**Q33.3-1.** Which path is context-dependent for `DefaultResolver`?
A. `./chair.usda`
B. `/mnt/show/chair.usda`
C. `chair.usda`
D. `../chair.usda`

**Q33.3-2.** Select two effects of `Usd.Stage.Open("shot.usda", pathResolverContext=rc)` when `rc` lists the assets folder and the shot references `@chair.usda@`.
A. `GetCompositionErrors()` is empty if `chair.usda` is in that folder
B. `/W/C` becomes `Xform` from the asset's `defaultPrim`
C. `./chair.usda` in another attribute also uses the search path
D. `Ar.GetResolver().GetCurrentContext()` stays set after Open returns, for the whole process

**Answers**

- **Q33.3-1: C.** No `./`, not absolute.
- **Q33.3-2: A and B.** `./` stays anchored; stage context is per stage, not a process bind.

### 13. Exam takeaways

> [!KEY]
> - Context-dependent = no `./` and not absolute; those paths use search paths.
> - `DefaultResolverContext` + `ResolverContextBinder` or `pathResolverContext`.
> - Failed lookup: prim may still exist; errors are `ErrorInvalidAssetPath`.
> - Document whether the pipeline uses `./` pins or search-path names (Obj 7.2 + 7.5).

---

## 33.4 Validating asset paths

### 1. What is it?

**Validating an asset path** (Obj 7.7) means checking two things: the string is **formatted** so Ar can understand it, and it **resolves** to a real resource (or is reported as unresolved). Format without resolvability is a style check; resolvability without format still fails on the farm.

### 2. Why do we need it?

A publish that ships `chair.usda` and forgets `tex/wood.png` is the bug Chapter 32 already inventoried with `ComputeAllDependencies`. Obj 7.7 adds the **per-path** rules: slashes, empty values, `./` vs search-path style, no Windows backslashes, no fake URI schemes.

### 3. Beginner explanation

A postal validator checks that the address has a street and a zip (format) and that the house exists (resolve). `@./tex/wood.png@` is the address. `resolvedPath` or `ComputeAllDependencies`'s `unresolved` list is "the house exists."

*Where the analogy breaks:* an empty `Sdf.AssetPath` is a blank envelope. It parses as a value but must fail validation.

### 4. Technical explanation

A practical checklist (document it next to Chapter 32's guidelines):

| Check | Pass | Fail |
|-------|------|------|
| Non-empty | `ap.path` is not `""` | `Sdf.AssetPath()` |
| Slashes | Forward `/` only | `tex\wood.png` (Resolve was `False` on 26.08 Linux) |
| Scheme | Empty or a **registered** URI scheme | `s3://…` with `GetRegisteredURISchemes() == []` |
| Anchored relative | Starts with `./` or `../` when it is a pin | Bare `chair.usda` if the pipeline forbids search-path names |
| Exists | `bool(ap.resolvedPath)` after Open, or `bool(Resolve(ComputeAbsolutePath(...)))`, or not in `ComputeAllDependencies` unresolved | Empty `ResolvedPath` |

**Do not** call `Resolve(ap.path)` on a `./` string from a random cwd — Section 33.2.

**Package paths:** `a.usdz[b.usda]` is formatted correctly when `Ar.IsPackageRelativePath` is true. Existence then means the package opens and the inner member exists (`UsdUtils.ExtractUsdzPackage` or `Stage.Open` on the `.usdz`, Ch 31).

`ComputeAllDependencies` remains the recursive **ship list**. Per-attribute `resolvedPath` is the **local** check you can print next to a prim in a DCC.

### 5. Mental model

```text
  format  -->  can Ar even parse this string?
  resolve -->  does the file (or package member) exist *from this layer*?
  graph   -->  ComputeAllDependencies unresolved == []
```

All three belong in a publisher.

### 6. Simple example

`/Chair.tex` is `@./tex/wood.png@` and the file exists → pass. `/Chair.missing` is `@./nope.png@` → format pass, resolve fail. `/Chair.win` is `@tex\wood.png@` → format fail.

### 7. USDA example

```usda
#usda 1.0

def Xform "Chair"
{
    asset tex = @./tex/wood.png@
    asset missing = @./nope.png@
}
```

Both paths are well-formed USDA. Only `tex` should pass a resolvability check.

### 8. Python example

```python
from pxr import Ar, Sdf, Usd, UsdUtils
import os

os.makedirs("tex", exist_ok=True)
open("tex/wood.png", "wb").write(b"PNG")
open("chair.usda", "w").write("""#usda 1.0
def Xform "Chair"
{
    asset tex = @./tex/wood.png@
    asset missing = @./nope.png@
}
""")

stage = Usd.Stage.Open("chair.usda")
layer = stage.GetRootLayer()
r = Ar.GetResolver()


def format_ok(ap):
    p = ap.path
    if not p or "\\" in p:
        return False
    if "://" in p:
        scheme = p.split(":", 1)[0]
        return scheme in Ar.GetRegisteredURISchemes()
    return True


def exists_for_layer(ap):
    if ap.resolvedPath:
        return True
    abs_path = layer.ComputeAbsolutePath(ap.path)
    return bool(r.Resolve(abs_path))


for name in ("tex", "missing"):
    ap = stage.GetPrimAtPath("/Chair").GetAttribute(name).Get()
    print(name, "format", format_ok(ap), "exists", exists_for_layer(ap))

print("backslash format", format_ok(Sdf.AssetPath("tex\\wood.png")))
print("empty format", format_ok(Sdf.AssetPath()))
print("URI format", format_ok(Sdf.AssetPath("s3://bucket/x.png")))

layers, assets, unresolved = UsdUtils.ComputeAllDependencies("chair.usda")
print("unresolved names:", sorted(os.path.basename(u) for u in unresolved))
print("assets names:", sorted(os.path.basename(a) for a in assets))
```

**Expected output**

```text
tex format True exists True
missing format True exists False
backslash format False
empty format False
URI format False
unresolved names: ['nope.png']
assets names: ['wood.png']
```

`s3://` fails format here because no URI scheme is registered — which is the honest `usd-core` result.

### 9. Real-world use case

A DCC export hook (Ch 29, Ch 34) runs this pair of checks on every `asset` attribute plus `ComputeAllDependencies` on the root layer. The export button stays red until `unresolved` is empty. Lighting never discovers a missing UDIM on the farm.

### 10. Common mistakes

> [!MISTAKE] Checking only `format_ok` (syntax). `@./nope.png@` is pretty and still broken.

> [!MISTAKE] Checking only `os.path.isfile` on authored strings. You skipped Ar (packages, URI plugins, search paths).

> [!MISTAKE] Treating a URI as valid because it contains `://`. Validity is **registered scheme** + that plugin's resolve.

### 11. Exam traps

> [!TRAP] "Obj 7.7 is `ComputeAllDependencies`." That API inventories. 7.7 is **format + resolve** of the path strings themselves. Use both.

> [!TRAP] "Backslashes are fine if Python `open` on Windows accepts them." USD asset paths use `/`.

> [!TRAP] Empty `resolvedPath` after `Sdf.AssetPath("./x.png")` **construction** means the file is missing. No — you never composed. Open the stage first.

### 12. Practice questions

**Q33.4-1.** Which check matches Obj 7.7 most closely?
A. Confirm `kind` is `component`
B. Confirm each asset string is well-formed and resolves
C. Confirm `upAxis` is `Y`
D. Confirm the file extension is `.usdc`

**Q33.4-2.** Select two failures a validator should report for `@s3://bucket/wood.png@` on stock `usd-core` 26.08.
A. No registered URI scheme named `s3`
B. `GetRegisteredURISchemes()` is empty
C. USDA cannot spell `@…@` with a colon
D. `kind` metadata is required on every asset attribute

**Answers**

- **Q33.4-1: B.** Format + resolvability. The others are other objectives.
- **Q33.4-2: A and B.** Colons are legal in asset paths; `kind` is unrelated.

### 13. Exam takeaways

> [!KEY]
> - Obj 7.7 = format (non-empty, `/`, registered scheme) + resolve (anchored).
> - Never `Resolve("./…")` from a random cwd.
> - Pair per-attribute checks with `ComputeAllDependencies` unresolved.
> - URI schemes are invalid until a plugin registers them.

---

## 33.5 Custom resolvers (overview)

### 1. What is it?

A **custom resolver** is an Ar plugin that replaces (or sits beside) `DefaultResolver` so asset paths can mean something other than "a file on this disk": a URI (`s3://`), a database id (`chair?v=17`), or a studio alias (`chair` → today's published folder). Obj 3.5 and 7.5: **integrate** one — load it, select it, pass a context into `Stage.Open`.

### 2. Why do we need it?

Chapter 32's relative pins work until you have ten sites, two clouds, and identifiers that should not encode folder layout. The default resolver cannot talk to S3 or a production database. A plugin can.

### 3. Beginner explanation

The default librarian only walks the building's shelves (filesystem). A custom librarian also calls the warehouse and understands catalog numbers. You still hand them the same card (`@chair@`). You **install** the new librarian (plugin path) and **introduce** them (`SetPreferredResolver` / URI scheme) so every department uses the same one.

*Where the analogy breaks:* you rarely write that librarian in Python with `usd-core`. Production resolvers are **C++** `ArResolver` subclasses loaded from `plugInfo.json`. This section is the integration map, not a compiler tutorial (`usd-core` has no `usdGenSchema` / plugin build — Ch 35, Ch 36).

### 4. Technical explanation

**What you install (conceptual):**

1. A shared library implementing `ArResolver` (or a URI-scheme resolver).
2. A `plugInfo.json` that registers the type with base `ArResolver` (plugin system: Chapter 36).
3. The directory of that `plugInfo.json` on `PXR_PLUGINPATH_NAME`.

Illustrative `plugInfo.json` (not loaded by this book's `usd-core`; do not expect it to change `GetUnderlyingResolver()`):

```text
{
  "Plugins": [
    {
      "Type": "resource",
      "Name": "StudioResolver",
      "Info": {
        "Types": {
          "StudioResolver": {
            "bases": ["ArResolver"]
          }
        }
      }
    }
  ]
}
```

**What you call from Python once the plugin exists:**

| Step | API |
|------|-----|
| See filesystem plugin today | `type(Ar.GetUnderlyingResolver()).__name__` → `DefaultResolver` |
| URI schemes the process knows | `Ar.GetRegisteredURISchemes()` |
| Prefer a named resolver | `Ar.SetPreferredResolver("StudioResolver")` |
| Per-stage search / studio context | `Usd.Stage.Open(path, pathResolverContext=rc)` |
| Bind for a block of Resolve calls | `with Ar.ResolverContextBinder(rc):` |

`SetPreferredResolver("NoSuchResolver")` on 26.08 **did not switch** the underlying type; it stayed `DefaultResolver`. Integrating a resolver means the plugin must actually load. Typo names fail closed.

**URI vs search-path custom resolvers:**

| Style | Authored path | Typical plugin |
|-------|---------------|----------------|
| Search / identifier | `@chair@` or `@chair.usda@` | Replaces default lookup |
| URI | `@s3://bucket/chair.usda@` | Registers scheme `s3` |

Obj 7.5 in a pipeline document: "We load `StudioResolver` via `PXR_PLUGINPATH_NAME`; shots Open with a context that names the show; artists write `@identifier@`, never `/mnt/...`."

Custom resolvers are completed as a plugin topic in Chapter 38. Here you only need the Ar-facing contract: **same `Resolve` / `CreateIdentifier` / context APIs**, different backing store.

### 5. Mental model

```text
  usd-core today:   GetUnderlyingResolver() == DefaultResolver
                    GetRegisteredURISchemes() == []

  studio install:   PXR_PLUGINPATH_NAME -> plugInfo.json -> StudioResolver
                    Stage.Open(..., pathResolverContext=studioContext)

  Python still calls Ar.GetResolver().Resolve(...)  -- the facade does not change
```

### 6. Simple example

IT ships `StudioResolver.so` + `plugInfo.json`. A shot opener always passes a context that includes `show=film24`. Artists author `@chair@`. The plugin returns `/prod/film24/assets/chair/v022/chair.usda`. Validators still check `bool(resolvedPath)` (Section 33.4); they do not parse the identifier.

### 7. USDA example

The authored layer does not mention the plugin. That is the point: USDA stays `@chair@` or `@s3://…@`.

```usda
#usda 1.0

def Xform "W"
{
    def "C" (
        prepend references = @chair@
    )
    {
    }
}
```

Without the studio resolver and context, this is an `ErrorInvalidAssetPath`. With them, it is a pin.

### 8. Python example

This block shows the **stock** process — what you measure before a plugin is on the path — plus the integration calls that exist even when the plugin does not.

```python
from pxr import Ar

print("underlying:", type(Ar.GetUnderlyingResolver()).__name__)
print("schemes:", Ar.GetRegisteredURISchemes())
print("has SetPreferredResolver:", hasattr(Ar, "SetPreferredResolver"))
print("has DefaultResolverContext:", hasattr(Ar, "DefaultResolverContext"))
print("has Binder:", hasattr(Ar, "ResolverContextBinder"))

Ar.SetPreferredResolver("NoSuchResolver")
print("after missing name:", type(Ar.GetUnderlyingResolver()).__name__)
```

**Expected output**

```text
underlying: DefaultResolver
schemes: []
has SetPreferredResolver: True
has DefaultResolverContext: True
has Binder: True
after missing name: DefaultResolver
```

The APIs exist. A fake type name does not install a resolver. That is the integration lesson: **plugin load first**, then prefer, then Open with a context.

### 9. Real-world use case

A cloud renderer has no `/mnt/show`. The studio resolver maps `@chair@` to an object-store URL, `OpenAsset` streams bytes, and `CreateIdentifierForNewAsset` writes publishes back. Farm and artist's laptop run the **same** plugin so identifiers match (Obj 6.3: "it worked on my machine" is an Ar context mismatch until then).

### 10. Common mistakes

> [!MISTAKE] Subclassing `Ar.Resolver` in a notebook and expecting USD to use it. The process loads C++ plugins from `plugInfo.json`.

> [!MISTAKE] Setting `PXR_PLUGINPATH_NAME` after the first `Ar.GetResolver()` call and assuming types refresh. Load plugins before opening stages (Ch 36).

> [!MISTAKE] Shipping shots that still contain `/mnt/show/...` after adopting a resolver. Old absolute pins bypass the plugin.

### 11. Exam traps

> [!TRAP] "Custom resolvers are written in USDA." They are plugins. USDA only stores the **identifiers** the plugin understands.

> [!TRAP] "`SetPreferredResolver` always raises on a bad name." On 26.08 it left `DefaultResolver` in place.

> [!TRAP] Obj 7.5 is satisfied by calling `Resolve`. Integrating means plugin + context + documented identifier style.

### 12. Practice questions

**Q33.5-1.** What must be true before `SetPreferredResolver("StudioResolver")` can change lookups?
A. The name is mentioned in `defaultPrim`
B. A plugin registering that type loaded via `plugInfo.json` / `PXR_PLUGINPATH_NAME`
C. The shot uses `.usdc`
D. `GetRegisteredURISchemes()` already contains `studio`

**Q33.5-2.** Select two integration steps that belong to Obj 3.5 / 7.5.
A. Put the resolver's plugin directory on `PXR_PLUGINPATH_NAME`
B. Pass a studio `ResolverContext` into `Usd.Stage.Open`
C. Rename every prim to match the asset identifier
D. Replace `Sdf.AssetPath` with `string` so Ar is skipped

**Answers**

- **Q33.5-1: B.** Prefer only works on a loaded type. URI schemes are a different plugin style.
- **Q33.5-2: A and B.** Identifiers stay asset paths; prim names stay prim names (Ch 32).

### 13. Exam takeaways

> [!KEY]
> - Custom resolvers are **plugins** (`ArResolver` + `plugInfo.json` + `PXR_PLUGINPATH_NAME`).
> - Python keeps calling `Ar.GetResolver()`; the underlying type changes after a real load.
> - Integrate = load plugin, prefer it, Open with a context, document identifier style.
> - `usd-core` here: `DefaultResolver`, no URI schemes — know what "before" looks like.

---

## Chapter lab(s)

**Lab 29** (asset resolution) is this chapter's lab: anchor vs naive Resolve, a search-path `Stage.Open`, and a format/exists validator. Lab 28's `ComputeAllDependencies` list is the recursive half of Obj 7.7.

## USDA reading exercises

**Exercise 33-A.** A shader in `assets/lamp/lamp.usda` has `asset inputs:file = @./tex/metal.png@`. A validator in the show root runs `Ar.GetResolver().Resolve("./tex/metal.png")` and fails. usdview shows the texture. Why, and what should the validator call?

**Exercise 33-B.** `shot.usda` contains `prepend references = @chair.usda@` (no `./`). Opening the shot with no context yields `ErrorInvalidAssetPath`. Opening with `DefaultResolverContext([os.path.abspath("assets")])` succeeds. What kind of path is `@chair.usda@`, and what would `@./chair.usda@` have done instead?

**Answers**

- **33-A.** Naive Resolve is cwd-relative. The file lives next to the **layer**. Use `Get().resolvedPath` after opening that layer, or `Resolve(layer.ComputeAbsolutePath("./tex/metal.png"))`.
- **33-B.** `@chair.usda@` is **context-dependent** (search path). `@./chair.usda@` is anchored to the shot folder and would **not** use `assets/` even with that context; it would look for `shot-folder/chair.usda`.

## Chapter review

**Summary**

- Ar turns authored `@…@` into `ResolvedPath`; empty is missing (`bool` is False).
- Stock `usd-core`: `GetUnderlyingResolver()` is `DefaultResolver`; URI schemes `[]`.
- Anchor `./` to the layer (`CreateIdentifier` + `ResolvedPath(layer.realPath)`, or `ComputeAbsolutePath`).
- Context-dependent paths (`chair.usda`) use `DefaultResolverContext` / `pathResolverContext`.
- Obj 7.7: format (`/`, non-empty, registered scheme) and anchored resolve.
- Obj 3.5 / 7.5: load a plugin, prefer it, Open with a context — not a Python subclass in a notebook.
- Obj 6.3: missing refs are `ErrorInvalidAssetPath`; the local prim may still exist.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| `ErrorInvalidAssetPath` | Ar did not find the identifier (cwd vs layer vs search path) |
| `Resolve("./x")` False, usdview OK | Missing anchor |
| `@chair.usda@` vs `@./chair.usda@` | Search path vs layer pin |
| `s3://` on usd-core | No URI plugin |
| `AnchorRelativePath` | Removed from `Ar.Resolver` in 26.08 |
| `SetPreferredResolver` no effect | Plugin did not load |
| `resolvedPath` empty on a fresh `AssetPath()` | You never composed |

**Review questions**

**R33-1** (Obj 7.7) Best first test that a composed texture attribute found a file?
A. `bool(attr.Get().resolvedPath)`
B. `os.path.exists(attr.Get().path)` from the repo root
C. `attr.GetTypeName() == "string"`
D. `Ar.GetRegisteredURISchemes()`

**R33-2** (Obj 6.3) `Stage.Open("shot.usda")` leaves `/W/C` but `GetCompositionErrors()` lists `ErrorInvalidAssetPath` for `@chair.usda@`. What happened?
A. The spec `def "C"` exists locally; the reference did not resolve
B. The prim was deleted
C. `chair.usda` is USDC so Ar ignores it
D. The session layer swallowed the reference

**R33-3** (Obj 7.5) Select two identifiers that use a search-path context on `DefaultResolver`.
A. `chair.usda`
B. `./chair.usda`
C. `tex/wood.png`
D. `/abs/chair.usda`

**R33-4** (Obj 7.7) Why is `tex\\wood.png` a format failure in this book's validator?
A. USDA cannot store asset attributes
B. Asset paths should use forward slashes; Resolve was `False` with backslashes
C. Backslashes are reserved for package paths
D. `DefaultResolver` treats `\\` as a URI scheme

**R33-5** (Obj 3.5) Custom resolvers are shipped as:
A. A `class` prim in the shot
B. An Ar plugin (`plugInfo.json` + library) on `PXR_PLUGINPATH_NAME`
C. A variant named `resolver`
D. A USDA `#resolver` directive

**R33-6** (Obj 7.7) `CreateIdentifier("./tex/wood.png")` with **no** anchor returns:
A. `./tex/wood.png` unchanged
B. `tex/wood.png` (now context-dependent)
C. An `Ar.ResolvedPath` to the texture
D. A URI scheme `tex`

**R33-7** (Obj 7.5) `Usd.Stage.Open(path, pathResolverContext=rc)` is used to:
A. Mute sublayers
B. Give **that stage** a search path / studio context
C. Convert USDA to USDC
D. Register a URI scheme named `rc`

**R33-8** (Obj 6.3) Select two correct debugging moves for a missing texture.
A. Print `attr.Get().path` and `attr.Get().resolvedPath`
B. Compare naive `Resolve(path)` from cwd with `ComputeAbsolutePath`
C. Set `kind = component` on the shader
D. Flatten the stage so Ar is no longer needed

**R33-9** (Obj 7.7) `Ar.GetRegisteredURISchemes()` is `[]`. `@s3://bucket/a.png@` should:
A. Pass format because it has `://`
B. Fail format / resolve until a URI resolver plugin loads
C. Be rewritten automatically to a filesystem path
D. Be treated as `./s3://bucket/a.png`

**R33-10** (Obj 3.5) `SetPreferredResolver("NoSuchResolver")` on 26.08 `usd-core`:
A. Raises `Tf.ErrorException`
B. Leaves `DefaultResolver` as the underlying resolver
C. Registers URI scheme `nosuch`
D. Deletes `plugInfo.json`

**R33-11** (Obj 7.7) `layer.ComputeAbsolutePath("./nope.png")` when the file is missing:
A. Raises
B. Returns an absolute string anyway; `Resolve` of that string is empty
C. Returns `Ar.ResolvedPath()`
D. Creates the file

**R33-12** (Obj 7.5) Select two statements that belong in a pipeline guideline after adopting a studio resolver.
A. Artists author identifiers the plugin understands, not `/mnt/show/...`
B. Every `Stage.Open` in tools passes the studio `pathResolverContext`
C. Asset attributes must change to `string`
D. `AnchorRelativePath` is required in every validator

**Review answers**

- **R33-1: A.** Composed `resolvedPath` is already anchored. Review: §33.2, §33.4.
- **R33-2: A.** Local def survives; the arc failed. Review: §33.3.
- **R33-3: A and C.** `./` and absolute are not context-dependent. Review: §33.3.
- **R33-4: B.** Forward slashes. Review: §33.4.
- **R33-5: B.** Plugin integration. Review: §33.5.
- **R33-6: B.** Strips `./`. Review: §33.2.
- **R33-7: B.** Per-stage context. Review: §33.3.
- **R33-8: A and B.** Kind and flatten do not fix lookup. Review: §33.2, §33.4.
- **R33-9: B.** No schemes registered. Review: §33.1, §33.5.
- **R33-10: B.** Fail closed. Review: §33.5.
- **R33-11: B.** Join ≠ exist. Review: §33.2.
- **R33-12: A and B.** Keep `asset` type; `AnchorRelativePath` is gone. Review: §33.5.

## Further reading

- [S06] OpenUSD API — `ArResolver`, `ArDefaultResolver`, `ArResolverContext`. https://openusd.org/release/api/ar_page_front.html
- [S04] OpenUSD Glossary — Asset, Asset Resolution. https://openusd.org/release/glossary.html
- [S02] OpenUSD User Guide — Advanced features: asset resolution. https://openusd.org/release/user_guides.html
- Chapter 36 (plugins / `PXR_PLUGINPATH_NAME`) and Chapter 38 (custom resolvers in depth) continue Obj 3.5.
