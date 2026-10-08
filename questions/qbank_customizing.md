# Question Bank — Customizing USD (CUST)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 3.1–3.8 (Customizing USD, 6%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 24 questions. This file holds **CUST-001–CUST-026** (domain complete; two extra Obj 3.8 items added in the Phase 15 audit).

Work the stems first. Answers and explanations are grouped at the end.

---

**CUST-001** · Obj 3.1 · Difficulty: Easy · Type: Single choice

A studio `.so` plugin built against USD 24.11 is copied onto a DCC that embeds 26.08. Likely result?

A. Perfect load; ABI is frozen
B. Load failure / missing types — **rebuild against the DCC’s USD**
C. USD recompiles it at Open
D. Only USDA plugins fail

---

**CUST-002** · Obj 3.1 · Difficulty: Medium · Type: Multiple select
Select two.

To load a studio plugin (Obj 3.1):

A. `plugInfo.json` in a directory on `PXR_PLUGINPATH_NAME`
B. Set the path **before** USD initializes when the host allows
C. `Kind.Registry.Register("plugin")`
D. `pip install` a wheel built for a different `_GLIBCXX`

---

**CUST-003** · Obj 3.1 · Difficulty: Easy · Type: Single choice

`Plug.Registry` is used to:

A. Flatten stages
B. Discover loaded plugins (`GetAllPlugins`, typed registries)
C. Author primvars
D. Replace Ar

---

**CUST-004** · Obj 3.2 · Difficulty: Medium · Type: Single choice

Why build OpenUSD from source (`build_usd.py` / CMake) instead of usd-core (Obj 3.2)?

A. usd-core cannot author layers
B. Need imaging, MaterialX, CLI (`usdview`, `usdcat`, `usdGenSchema`), or custom deps
C. Source builds forbid Python
D. Crate files require a source build

---

**CUST-005** · Obj 3.2 · Difficulty: Easy · Type: Single choice

`Usd.GetVersion()` on this book’s wheel?

A. `(0, 24, 11)`
B. `(0, 26, 8)`
C. `(26, 8, 0)`
D. `None`

---

**CUST-006** · Obj 3.3 · Difficulty: Easy · Type: Single choice

`hasattr(Kind.Registry, "Register")` on 26.08 Python?

A. True
B. **False** — custom kinds are **`plugInfo.json`**, not a Python Register call
C. True after `from pxr import Kind`
D. Register lives on `Usd.ModelAPI`

---

**CUST-007** · Obj 3.3 · Difficulty: Medium · Type: Single choice

`SetKind("door")` on a prim that was `component`. `GetKind()` and `IsComponent()`?

A. `door`, True
B. **`door`, False** — unregistered kind is stored but is not a model/component
C. Raises
D. Kind resets to `component`

---

**CUST-008** · Obj 3.3 · Difficulty: Medium · Type: Multiple select
Select two.

Built-in kind tree (verified):

A. `assembly` is-a `group` is-a `model`
B. `component` is-a `model` but **not** a group
C. `subcomponent` is-a `model`
D. `HasKind("door")` is True on stock usd-core

---

**CUST-009** · Obj 3.3 · Difficulty: Easy · Type: Single choice

When is a **custom kind** appropriate?

A. For every unique mesh name
B. When the studio needs a new **model taxonomy** the five built-ins cannot express, declared in plugin metadata
C. Instead of `component` for all furniture
D. To hide instance proxies

---

**CUST-010** · Obj 3.4 · Difficulty: Easy · Type: Single choice

`shutil.which("usdGenSchema")` on usd-core?

A. A path
B. **`None`**
C. `usdcat`
D. Raises

---

**CUST-011** · Obj 3.4 · Difficulty: Medium · Type: Single choice

`Sdf.Layer.ImportFromString` of `schema.usda` defining `class "Door"`. `FindConcretePrimDefinition("Door")`?

A. Door’s definition
B. **`None` — parse ≠ register**
C. Cube’s definition
D. Raises

---

**CUST-012** · Obj 3.4 · Difficulty: Medium · Type: Single choice

Codeless schema (`skipCodeGeneration = 1`) still needs:

A. Nothing but the parsed USDA in memory
B. Generated schema.usda + **`plugInfo.json` loaded as a plugin**; it only skips C++ wrappers
C. Hydra SceneIndex
D. `GetMaster()`

---

**CUST-013** · Obj 3.4 · Difficulty: Medium · Type: Multiple select
Select two.

Typed vs applied API schemas:

A. Concrete typed (`UsdTyped` / `IsA("Cube")`) — Cube is concrete, size fallback 2
B. Applied API (`MaterialBindingAPI`) — `IsAppliedAPISchema` True; must **Apply**
C. All APIs are IsA types
D. Door is registered on usd-core

---

**CUST-014** · Obj 3.6 · Difficulty: Medium · Type: Single choice

Nonstandard CAD `factory:partId` vs a `Door` schema (Obj 3.6 / 4.5)?

A. Always schema first
B. One-off field → namespaced **attribute**; shared typed prim across DCCs → **schema**
C. customData cannot hold strings
D. Schemas cannot be used on import

---

**CUST-015** · Obj 3.5 · Difficulty: Easy · Type: Single choice

`Ar.GetResolver()` vs `GetUnderlyingResolver()` on usd-core?

A. Both DefaultResolver
B. Facade **Resolver**; underlying **DefaultResolver**
C. Both None
D. Underlying is StudioResolver after pip install usd-core

---

**CUST-016** · Obj 3.5 · Difficulty: Medium · Type: Single choice

Custom resolver integration (Obj 3.5)?

A. `AnchorRelativePath` registers it
B. `ArResolver` C++ (or wrapped) plugin + `plugInfo.json` + `PXR_PLUGINPATH_NAME` + Open with a context
C. `SetEditTarget` to the resolver
D. Python `Kind.Registry.Register("ar")`

---

**CUST-017** · Obj 3.8 · Difficulty: Medium · Type: Single choice

An AssetResolver that **generates in-memory primitives** (Obj 3.8) is conceptually:

A. `DefaultResolver` finding PNG files
B. A resolver `Resolve`/`OpenAsset` that returns **generated** bytes/layers (procedural URI), not only disk files
C. `UsdGeom.Mesh.Define` in usdview
D. FlattenLayerStack

---

**CUST-018** · Obj 3.7 · Difficulty: Medium · Type: Single choice

Hydra **SceneIndex** plugin (Obj 3.7) vs usd-core:

A. Fully implemented in the pip wheel (`import pxr.Hd` works)
B. **Imaging/Hd absent** from usd-core — SceneIndex is a Hydra 2.0 filter/source of **render prims**; you need a full/imaging build
C. SceneIndex replaces Sdf
D. SceneIndex is `Kind.Registry`

---

**CUST-019** · Obj 3.7 · Difficulty: Easy · Type: Single choice

SceneIndex plugins generate:

A. USDA comments
B. **Hydra prims / scene index entries** for the render delegate (not a substitute for authoring USD on disk unless that is your design)
C. Git commits
D. `customData` only

---

**CUST-020** · Obj 3.1 · Difficulty: Medium · Type: Single choice

`PXR_PLUGINPATH_NAME` pointing at plugins **instead of** the DCC’s USD plugin dir so `usdGeom` disappears. Debug?

A. Expected
B. Prepending a path that **hides** the default plugins — include **both** the USD prefix and the studio dir
C. MuteLayer
D. Need `LoadNone`

---

**CUST-021** · Obj 3.6 · Difficulty: Medium · Type: Single choice

`schema.usda` `class "Door" (inherits = </Typed>)` means Door is:

A. An applied API
B. A **typed/IsA** schema (concrete or abstract depending on metadata)
C. A file format plugin
D. A resolver

---

**CUST-022** · Obj 3.4 · Difficulty: Easy · Type: Single choice

`over "GLOBAL"` customData `libraryName` in schema.usda is:

A. Ignored
B. The schema **library** name `usdGenSchema` / plugins use
C. The defaultPrim
D. A kind

---

**CUST-023** · Obj 3.5 · Difficulty: Medium · Type: Multiple select
Select two.

`AnchorRelativePath` on Ar.Resolver in 26.08:

A. Exists and is required
B. **Gone** — use `CreateIdentifier` + `ResolvedPath` or `ComputeAbsolutePath`
C. Custom resolvers still implement **their** resolve/anchor rules in C++
D. Python Register on Kind replaces Ar

---

**CUST-024** · Obj 3.2 · Difficulty: Medium · Type: Single choice

CMake flag conceptually enabling MaterialX in a source build?

A. `PXR_BUILD_MATERIALX_PLUGIN` (book’s table) — not present in usd-core
B. `USD_CORE_ONLY=1` on pip
C. `Kind.Registry.Register("mtlx")`
D. `stage.Flatten()`

---

**CUST-025** · Obj 3.8 · Difficulty: Medium · Type: Single choice

A candidate says Obj 3.8 is just `Usd.Stage.CreateInMemory()`. What is wrong?

A. Nothing — `CreateInMemory` is the procedural resolver API
B. `CreateInMemory` makes an **empty stage in this process**; Obj 3.8 is an **AssetResolver** (or Hydra procedural) that **generates bytes/prims from an identifier**
C. `CreateInMemory` was removed in 26.08
D. You must call `CreateInMemory` inside `Kind.Registry.Register`

---

**CUST-026** · Obj 3.8 · Difficulty: Medium · Type: Multiple select
Select two.

Legal designs for “generate in-memory renderable primitives” from an identifier:

A. Custom `ArResolver.OpenAsset` returns a memory buffer of USDA/USDC that Sdf then parses
B. A Hydra scene-index / procedural emits render prims for a URI such as `@proc:box@`
C. `Kind.Registry.Register("proc")` in Python on usd-core 26.8
D. `stage.Flatten()` on any referenced file

---

## Answers

**CUST-001 — Answer: B.** ABI/version match. Review: §35.2.

**CUST-002 — Answer: A, B.** plugInfo + early path. Review: §36.2.

**CUST-003 — Answer: B.** Plug.Registry. Review: §36.2.

**CUST-004 — Answer: B.** Full stack vs wheel. Review: §35.1.

**CUST-005 — Answer: B.** Verified `(0, 26, 8)`. Review: lab 01, §35.

**CUST-006 — Answer: B.** No Python Register. Review: lab 32.

**CUST-007 — Answer: B.** GetKind door, IsComponent False. Review: lab 32.

**CUST-008 — Answer: A, B.** Tree facts; door not registered; subcomponent not model. Review: lab 32.

**CUST-009 — Answer: B.** Taxonomy plugin. Review: §38, §3.3.

**CUST-010 — Answer: B.** usdGenSchema missing. Review: lab 31.

**CUST-011 — Answer: B.** Parse ≠ register. Review: lab 31.

**CUST-012 — Answer: B.** Still a plugin. Review: §37.3.

**CUST-013 — Answer: A, B.** Cube vs MaterialBindingAPI. Review: lab 31.

**CUST-014 — Answer: B.** Attribute vs schema. Review: §29.4, §37.5.

**CUST-015 — Answer: B.** Facade vs plugin. Review: lab 29.

**CUST-016 — Answer: B.** Resolver plugin. Review: §33.5.

**CUST-017 — Answer: B.** Procedural OpenAsset. Review: §38.

**CUST-018 — Answer: B.** No Hd on usd-core. Review: §38, §41.

**CUST-019 — Answer: B.** Hydra prims. Review: §38.

**CUST-020 — Answer: B.** Don’t hide default plugins. Review: §35.2, §36.2.

**CUST-021 — Answer: B.** Typed inherit. Review: §37.4.

**CUST-022 — Answer: B.** libraryName. Review: lab 31.

**CUST-023 — Answer: B, C.** API gone; C++ resolver still anchors. Review: §33.2.

**CUST-024 — Answer: A.** CMake MaterialX plugin. Review: §35.1.

**CUST-025 — Answer: B.** `CreateInMemory` is an empty in-process stage, not a resolver. Review: §38.4.

**CUST-026 — Answer: A, B.** Resolver memory buffer or Hydra procedural; not Kind.Register or Flatten. Review: §38.4–38.5.

---

*Customizing USD domain complete: CUST-001–CUST-026 (target 24; +2 Obj 3.8 audit fill).*
