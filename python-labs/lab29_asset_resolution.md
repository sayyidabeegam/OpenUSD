# Lab 29 — Asset resolution: anchor, search path, stage context

**Domain / objectives:** Pipeline 7.5, 7.7 · Debugging 6.3 · **Chapter:** 33 · **Time:** 30 min · **Difficulty:** ★★★

## Goal
Prove naive **`Resolve("./tex/wood.png")` is False** from the wrong cwd, that **anchoring** finds the file, that **search paths** only help **context-dependent** paths (no `./`), and that **`Stage.Open(..., pathResolverContext=)`** is how `@chair.usda@` resolves.

## Background
`Ar.GetResolver()` is the **Resolver** facade; **`GetUnderlyingResolver()`** is **DefaultResolver** on usd-core (Ch 33). **`AnchorRelativePath` is gone** in 26.08 — use `CreateIdentifier(path, ResolvedPath(layer.realPath))` or `ComputeAbsolutePath`. Composition anchors to the **layer**; raw `Resolve("./…")` uses cwd. `./` paths are **not** search-path lookups. `@chair.usda@` without `./` is context-dependent: Open without a context → `ErrorInvalidAssetPath`.

## Steps
1. Facade `Resolver`, plugin `DefaultResolver`, no `AnchorRelativePath`.
2. Naive `./tex/wood.png` False; absolute / CreateIdentifier True.
3. No-anchor CreateIdentifier strips to `tex/wood.png` (now search-path).
4. Bound search finds `tex/wood.png`, **not** `./tex/wood.png`. Unbind restores False.
5. Shot with context: 0 errors, type `Xform`. Without: 1 `ErrorInvalidAssetPath`.

## Full script (identical to `lab29_asset_resolution.py`)

```python
"""Lab 29 — Naive vs anchored Resolve, search path, Stage.Open context."""
import os
import tempfile
from pxr import Ar, Sdf, Usd

os.chdir(tempfile.mkdtemp())
os.makedirs("assets/tex", exist_ok=True)
open("assets/tex/wood.png", "wb").write(b"PNG")
open("assets/chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair"
{
    asset tex = @./tex/wood.png@
}
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
os.makedirs("searchA/tex", exist_ok=True)
open("searchA/tex/wood.png", "wb").write(b"A")

r = Ar.GetResolver()
print("resolver:", type(r).__name__)
print("underlying:", type(Ar.GetUnderlyingResolver()).__name__)
print("AnchorRelativePath:", hasattr(r, "AnchorRelativePath"))
print("naive ./tex/wood.png:", bool(r.Resolve("./tex/wood.png")))
layer = Sdf.Layer.FindOrOpen("assets/chair.usda")
abs_path = layer.ComputeAbsolutePath("./tex/wood.png")
print("Resolve abs:", bool(r.Resolve(abs_path)))
ident = r.CreateIdentifier(
    "./tex/wood.png", Ar.ResolvedPath(layer.realPath))
print("CreateIdentifier then Resolve:", bool(r.Resolve(ident)))
print("no-anchor ident:", r.CreateIdentifier("./tex/wood.png"))
print("dependent tex/wood.png:", r.IsContextDependentPath("tex/wood.png"))
print("dependent ./tex/wood.png:", r.IsContextDependentPath("./tex/wood.png"))
print("unbound tex/wood.png:", bool(r.Resolve("tex/wood.png")))
ctx = Ar.DefaultResolverContext([os.path.abspath("searchA")])
with Ar.ResolverContextBinder(Ar.ResolverContext(ctx)):
    print("bound tex/wood.png:", bool(r.Resolve("tex/wood.png")))
    print("bound ./tex/wood.png:", bool(r.Resolve("./tex/wood.png")))
print("after unbind:", bool(r.Resolve("tex/wood.png")))
rc = Ar.ResolverContext(
    Ar.DefaultResolverContext([os.path.abspath("assets")]))
ok = Usd.Stage.Open("shot.usda", pathResolverContext=rc)
bad = Usd.Stage.Open("shot.usda")
print("with ctx errors/type:", len(ok.GetCompositionErrors()),
      ok.GetPrimAtPath("/W/C").GetTypeName())
print("no ctx errors:", len(bad.GetCompositionErrors()),
      type(bad.GetCompositionErrors()[0]).__name__)
```

**Expected output**
```text
resolver: Resolver
underlying: DefaultResolver
AnchorRelativePath: False
naive ./tex/wood.png: False
Resolve abs: True
CreateIdentifier then Resolve: True
no-anchor ident: tex/wood.png
dependent tex/wood.png: True
dependent ./tex/wood.png: False
unbound tex/wood.png: False
bound tex/wood.png: True
bound ./tex/wood.png: False
after unbind: False
with ctx errors/type: 0 Xform
no ctx errors: 1 ErrorInvalidAssetPath
```

## Check your understanding
1. Does `GetResolver()` return `DefaultResolver`?
2. Why is naive `Resolve("./tex/wood.png")` False even though the PNG exists?
3. Do search paths apply to `@./tex/wood.png@`?

**Answers**
1. **No.** It returns **`Resolver`**. Ask **`GetUnderlyingResolver()`**.
2. Raw Resolve uses **cwd**, not the layer that authored `./`. Anchor first.
3. **No.** `./` is layer-relative, not context-dependent.

## Stretch challenge
Print `hasattr(Ar.Resolver, "AnchorRelativePath")`. Solution: **False** on USD 26.08 (Ch 33 VERSION).
