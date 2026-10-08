# Question Bank — Fundamentals (FUN)

**Original practice questions.** Not actual NVIDIA exam content. Not blueprint-weighted; they cover Part I (Ch 1–7) so a complete beginner can sit the domain banks. Verified against **USD 26.08** (`usd-core` 26.8).

Target: 30. This file holds **FUN-001–FUN-030** (domain complete).

Work the stems first. Answers are at the end.

---

**FUN-001** · Foundations · Difficulty: Easy · Type: Single choice

OpenUSD is best described as:

A. Only a file extension `.usd`
B. A **scene description** system (composition, schemas, APIs) that *includes* file formats
C. A renderer that replaced Hydra
D. A Pixar-only closed format

---

**FUN-002** · Foundations · Difficulty: Easy · Type: Single choice

Python imports live in which package?

A. `usd`
B. `pxr` (`from pxr import Usd`)
C. `openusd`
D. `nvidia`

---

**FUN-003** · Foundations · Difficulty: Medium · Type: Single choice

Stack order: Tf, Gf, Vt, Ar, Sdf, Pcp, Usd. Which layer is **scene composition** of opinions?

A. Tf
B. Sdf
C. **Pcp**
D. Hydra

---

**FUN-004** · Foundations · Difficulty: Easy · Type: Single choice

A **stage** is:

A. One USDA file on disk only
B. The live **composed** scene (`Usd.Stage`) built from layers and arcs
C. A Hydra render delegate
D. `plugInfo.json`

---

**FUN-005** · Foundations · Difficulty: Easy · Type: Single choice

`Usd.GetVersion()` on this book’s environment?

A. `(26, 8, 0)`
B. `(0, 26, 8)`
C. `(24, 11)`
D. `"usd-core"`

---

**FUN-006** · Foundations · Difficulty: Easy · Type: Multiple select
Select two.

usd-core 26.8 **does** include / **does not** include:

A. Does: `Usd`, `UsdGeom`, `UsdShade`, `UsdLux` Python modules
B. Does not: `usdcat` / `usdview` on PATH
C. Does: Hydra `UsdImaging` in the wheel
D. Does: `UsdMtlx`

---

**FUN-007** · Foundations · Difficulty: Medium · Type: Single choice

`CreateInMemory()` vs `CreateNew("a.usda")`?

A. Both always write disk immediately
B. In-memory has no path until Export/Save-as; CreateNew makes a **file-backed** root layer
C. CreateNew cannot save
D. In-memory cannot Define prims

---

**FUN-008** · Foundations · Difficulty: Easy · Type: Single choice

Fresh `CreateInMemory` `upAxis` and `metersPerUnit` fallbacks?

A. Z and 1.0
B. **Y and 0.01**
C. None and None
D. Y and 1.0

---

**FUN-009** · Foundations · Difficulty: Easy · Type: Single choice

Python stand-in for `usdcat` on usd-core?

A. There is none
B. `stage.GetRootLayer().ExportToString()` / `Export`
C. `print(stage)`
D. `GetMaster()`

---

**FUN-010** · Foundations · Difficulty: Medium · Type: Single choice

A **layer** (`Sdf.Layer`) vs the stage?

A. Identical objects
B. A layer is one **opinion container** (file or anonymous); the stage **composes** many layers
C. Layers cannot hold prims
D. Only USDC is a layer

---

**FUN-011** · Foundations · Difficulty: Medium · Type: Single choice

Session layer vs root layer: composed `radius` 9 vs 1, then `Save()` the root. Root file contains?

A. 9
B. **1** — session is not written into the root
C. Both averaged
D. Save fails

---

**FUN-012** · Foundations · Difficulty: Medium · Type: Single choice

`subLayers = [@b.usda@, @a.usda@]` with b radius 5 and a radius 9. Composed?

A. 9 (last listed)
B. **5** (first listed is stronger)
C. 7
D. None

---

**FUN-013** · Foundations · Difficulty: Easy · Type: Single choice

A **prim** is:

A. Only a mesh
B. A **namespace object** on the stage (Xform, Sphere, typeless, …)
C. An attribute
D. A layer offset

---

**FUN-014** · Foundations · Difficulty: Easy · Type: Single choice

Specifiers `def`, `over`, `class` mean:

A. The same
B. **Define** / **overlay** (does not by itself define) / **abstract** class
C. File formats
D. Kinds

---

**FUN-015** · Foundations · Difficulty: Medium · Type: Single choice

Opened alone, `over "Hero" { int hp = 10 }` — `Traverse()`?

A. Lists `/Hero`
B. **Empty** — `over` alone is not defined
C. Raises
D. Lists a Cube

---

**FUN-016** · Foundations · Difficulty: Easy · Type: Single choice

Attribute vs relationship?

A. Both store `double` values
B. Attributes store **typed values**; relationships store **prim/property targets**
C. Relationships are only for materials
D. Attributes cannot have defaults

---

**FUN-017** · Foundations · Difficulty: Easy · Type: Single choice

`primvars:`, `xformOp:`, `inputs:` are:

A. Composition arcs
B. **Property namespaces**
C. File extensions
D. Kinds

---

**FUN-018** · Foundations · Difficulty: Easy · Type: Single choice

Five built-in model kinds?

A. `door, window, wall, roof, floor`
B. **`model, group, assembly, component, subcomponent`**
C. `Mesh, Xform, Camera, Light, Material`
D. `usda, usdc, usd, usdz, abc`

---

**FUN-019** · Foundations · Difficulty: Medium · Type: Single choice

Typed schema vs API schema?

A. No difference
B. Typed is **IsA** (Cube); API is **applied** (`MaterialBindingAPI.Apply`)
C. API replaces kinds
D. Typed schemas cannot have attributes

---

**FUN-020** · Foundations · Difficulty: Easy · Type: Single choice

`.usda` vs `.usdc` vs `.usd` vs `.usdz`?

A. All crate binary
B. Text / crate binary / **either** (detect magic) / **zip package**
C. All require Hydra
D. `.usd` is always text

---

**FUN-021** · Foundations · Difficulty: Medium · Type: Single choice

`CreateNew("scene.usd")` magic and `formatId`?

A. `#usda`, `usda`
B. **`PXR-USDC`, `usd`**
C. `PXR-USDC`, `usdc`
D. `PK`, `usdz`

---

**FUN-022** · Foundations · Difficulty: Easy · Type: Single choice

USDA files must start with:

A. `<?xml`
B. **`#usda 1.0`**
C. `PXR-USDC`
D. `{`

---

**FUN-023** · Foundations · Difficulty: Medium · Type: Single choice

`GetPrimAtPath("/NoSuch")` — `bool(prim)`?

A. True
B. **False** (invalid handle; `GetPrimAtPath` does not raise)
C. Raises KeyError
D. Defines the prim

---

**FUN-024** · Foundations · Difficulty: Easy · Type: Single choice

`defaultPrim` is stored on:

A. Each attribute
B. **The layer** (stage metadata)
C. Hydra
D. `Kind.Registry`

---

**FUN-025** · Foundations · Difficulty: Medium · Type: Single choice

Anonymous layer (`CreateAnonymous`) in the local stack?

A. Always the root
B. A layer **without a file path**; not automatically in the stack until you sublayer/set it
C. The same as session
D. Cannot hold prims

---

**FUN-026** · Foundations · Difficulty: Easy · Type: Single choice

`Traverse()` vs `GetPrimAtPath`?

A. Identical
B. Traverse **walks defined prims** (skipping some overs/class/instance proxies); GetPrimAtPath is a **direct lookup**
C. GetPrimAtPath walks Hydra
D. Traverse cannot see Spheres

---

**FUN-027** · Foundations · Difficulty: Medium · Type: Multiple select
Select two.

Opinions (first look, Ch 3):

A. Strongest opinion for a scalar field **wins** (no averaging)
B. First listed sublayer is stronger than later ones
C. Weaker layers delete stronger files
D. Session is weaker than the root

---

**FUN-028** · Foundations · Difficulty: Easy · Type: Single choice

Pixar opened USD; the alliance for open standards is often abbreviated:

A. NVIDIA-only
B. **AOUSD** (Alliance for OpenUSD)
C. glTF
D. USDZ Inc.

---

**FUN-029** · Foundations · Difficulty: Medium · Type: Single choice

Hydra’s role in the stack?

A. Composition of layers
B. **Imaging / render-delegate** architecture (not in usd-core)
C. Asset resolution
D. Kind registry

---

**FUN-030** · Foundations · Difficulty: Easy · Type: Single choice

`UsdGeom.Sphere.Define(stage, "/World/Ball")` then `GetRadiusAttr().Set(2)` — lab 02 USDA shows:

A. `float radius = 2.0`
B. **`double radius = 2`** (USDA may drop `.0`)
C. `int radius = 2`
D. Radius cannot be authored

---

## Answers

**FUN-001 — Answer: B.** Scene description, not “just a file.” Review: §1.1.

**FUN-002 — Answer: B.** `pxr`. Review: §1.5.

**FUN-003 — Answer: C.** Pcp = prim cache population / composition. Review: §1.4.

**FUN-004 — Answer: B.** Stage = composed view. Review: §2.1.

**FUN-005 — Answer: B.** `(0, 26, 8)`. Review: lab 01.

**FUN-006 — Answer: A, B.** Schema modules yes; CLI/Hydra/Mtlx no. Review: lab 01, F5.

**FUN-007 — Answer: B.** File-backed vs memory. Review: §2.2.

**FUN-008 — Answer: B.** Y, 0.01. Review: lab 08, §28.

**FUN-009 — Answer: B.** ExportToString. Review: F5, lab 02.

**FUN-010 — Answer: B.** Layer vs stage. Review: §3.1.

**FUN-011 — Answer: B.** Session not in root Save. Review: lab 04.

**FUN-012 — Answer: B.** First listed wins. Review: lab 05.

**FUN-013 — Answer: B.** Prim = namespace object. Review: §4.1.

**FUN-014 — Answer: B.** def/over/class. Review: §4.3.

**FUN-015 — Answer: B.** over alone not defined. Review: §20.1.

**FUN-016 — Answer: B.** Value vs targets. Review: §5.2–5.3.

**FUN-017 — Answer: B.** Namespaces. Review: §5.5.

**FUN-018 — Answer: B.** Five kinds. Review: §6.5, lab 32.

**FUN-019 — Answer: B.** IsA vs Apply. Review: §6.2–6.3.

**FUN-020 — Answer: B.** Four encodings. Review: §7.1–7.4.

**FUN-021 — Answer: B.** Crate magic, formatId usd. Review: §31.3.

**FUN-022 — Answer: B.** `#usda 1.0`. Review: §7.5.

**FUN-023 — Answer: B.** Invalid handle. Review: §4.2.

**FUN-024 — Answer: B.** Layer metadata. Review: §2.4.

**FUN-025 — Answer: B.** Anonymous not auto-stacked. Review: §3.5, lab 19.

**FUN-026 — Answer: B.** Walk vs lookup. Review: §2.3.

**FUN-027 — Answer: A, B.** Strongest wins; first sublayer. Session is strongest local. Review: §3.6.

**FUN-028 — Answer: B.** AOUSD. Review: §1.2.

**FUN-029 — Answer: B.** Imaging. Review: §1.4, §41.

**FUN-030 — Answer: B.** double radius = 2. Review: lab 02.

---

*Fundamentals domain complete: FUN-001–FUN-030 (target 30). Question bank exam+FUN total 430.*
