# Chapter 1 — What Is OpenUSD?

> **Exam domain:** Foundations for every domain · **Objectives:** none directly (prepares all of them)
> **Study day:** 1 · **Est. time:** 60 min
> **Prerequisites:** Front matter F5 (you can run a Python script)

## Learning goals

- Explain in one sentence what OpenUSD is, and what it is not.
- Distinguish **scene description**, **file format**, and **runtime library**.
- Name where OpenUSD is used and why those industries adopted it.
- Map the main OpenUSD software modules (Tf, Gf, Vt, Ar, Sdf, Pcp, Usd, schema domains, Hydra) to what each does.
- Import `pxr` modules and print the installed USD version.

## Key terms

| Term | One-line definition |
|------|---------------------|
| OpenUSD / USD | An open-source system for describing, composing, and exchanging 3D scenes |
| Scene description | The data model: objects (prims) with properties, stored in layers |
| Layer | One document of scene description (often one file) |
| Stage | The composed scene you work with at runtime |
| Composition | The process of combining layers into one stage by fixed strength rules |
| `pxr` | The Python package that contains all OpenUSD modules |

---

## 1.1 Scene description vs. file format vs. runtime

### 1. What is it?

**OpenUSD** (Open Universal Scene Description) is an open-source system for describing 3D scenes, combining contributions from many files and people, and handing that scene to tools and renderers. People often shorten it to **USD**.

### 2. Why do we need it?

A 3D project uses many tools: a modeler, an animation package, a lighting tool, a game engine, a CAD program, a renderer. Each tool historically had its own scene format. Moving data between them meant lossy exports, duplicated files, and broken work whenever someone upstream changed something.

### 3. Beginner explanation

Think of a shared recipe book in a large restaurant kitchen. The original recipe stays untouched. The pastry chef clips a note on top saying "use less sugar". The head chef clips another saying "serve on a blue plate". Anyone reading the recipe sees the original plus all the notes, combined in a known order.

USD works the same way: the original data stays intact, and later contributions are **layered on top**.

Where the analogy breaks: in USD the "notes" follow strict, predictable rules about which note wins when two disagree. Learning those rules (Part III, Composition) is the largest single part of the exam.

### 4. Technical explanation

USD is three things that are easy to confuse. Exam questions often mix them.

| Part | What it is | Example |
|------|-----------|---------|
| **Scene description** | A data model: prims (scene objects) with properties, arranged in a hierarchy, stored in layers | "There is a sphere at `/World/Ball` with radius 2" |
| **File formats** | Ways to save a layer to disk | `.usda` (text), `.usdc` (binary crate), `.usd` (either), `.usdz` (zip package) |
| **Runtime libraries** | C++ libraries with Python bindings that read, compose, edit, and serve scene data | `pxr.Usd`, `pxr.Sdf`, `pxr.UsdGeom` |

The most important runtime idea is **composition**: USD reads several layers and combines them into one **composed** scene according to fixed strength rules. Applications see the composed result unless they ask for the authored details.

> [!NOTE] "USD" and "OpenUSD" refer to the same technology. The open-source project is called OpenUSD. The libraries, file extensions, and Python package (`pxr`) still say "usd". This book uses **OpenUSD** for the project and **USD** in running text.

### 5. Mental model

```text
  files on disk          runtime                     what you see
.usda / .usdc / .usdz --> compose layers --> one Stage --> tools / renderer
     (layers)            (Pcp + Usd)         (prims)
```

USD = a shared scene, built from stacked layers, combined by fixed rules, readable by every tool.

### 6. Simple example

A furniture company has a chair model. Design owns `chair_geo.usda` (the shape). Marketing wants a red version for a catalogue. Instead of copying the file, they create a small layer that says only "the chair's color is red" and stack it on top. If design improves the shape tomorrow, the red catalogue version picks up the new shape automatically.

### 7. USDA example

`.usda` is USD's human-readable text format. This complete layer describes one sphere:

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 2
    }
}
```

How to read it:

- `#usda 1.0` is required. It marks the file as USDA text.
- `def` means "define a new prim here".
- `Xform` and `Sphere` are **types** (schemas). An Xform is a transform group; a Sphere is a geometric sphere.
- `"World"` and `"Ball"` are **names**. Names join into a **prim path**: `/World/Ball`.
- `double radius = 2` is an **attribute** on the sphere.

You do not need to memorize every schema yet. You do need to recognize this as scene description, not "just a 3D file format".

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
world = UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.GetRadiusAttr().Set(2.0)
print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 2
    }
}
```

> [!NOTE] `stage.GetRootLayer().ExportToString()` prints what that layer authored. `stage.ExportToString()` prints a flattened composed view and may add a generated `doc` line. You will use both views in Chapter 8.

### 9. Real-world use case

A visual-effects shot is not one file. Layout publishes a camera and set. Animation publishes character poses. Lighting publishes lights. USD lets each department publish its own layer. The lighting department sees the composed shot without copying the animation files.

### 10. Common mistakes

> [!MISTAKE] Treating USD as "just another file format like OBJ or FBX". OBJ holds one mesh. USD holds a whole composed scene, with many files contributing opinions.

> [!MISTAKE] Thinking "if I don't see it in this `.usda` file, it isn't in the scene". A prim can come from a referenced file that this layer only points to. Chapter 16.

### 11. Exam traps

> [!TRAP] A question that says "USD is a file format" as the *complete* answer. USD **includes** file formats, but the important part is the scene description and the composition runtime.

> [!TRAP] Mixing up "layer" (a document of opinions) with "stage" (the composed result). Chapter 2 and Chapter 3 separate them.

### 12. Practice questions

**FUN-001** · Difficulty: Easy · Type: Single choice

What is the most complete description of OpenUSD?

A. A binary mesh format similar to Alembic  
B. A system for scene description, file formats, and a runtime that composes layers  
C. A renderer that draws USD files  
D. A Python-only library with no C++ core  

**FUN-002** · Difficulty: Easy · Type: Single choice

You open `shot.usda` and do not see the character's mesh in that file. The character still appears on the stage. What is the most likely explanation?

A. USD automatically invents geometry that is missing from files  
B. Another layer contributing to the stage (for example a reference) defines the mesh  
C. USDA files cannot store meshes, only transforms  
D. The mesh exists only in usdview's cache  

**Answers**

**FUN-001 — Answer: B.** A is too small. C is Hydra/usdview, not USD itself. D is false: the core is C++ with Python bindings.

**FUN-002 — Answer: B.** Composition pulls in other layers. A is invented. C is false (meshes are first-class). D mixes up the viewer with the data.

### 13. Exam takeaways

> [!KEY]
> - OpenUSD = scene description + file formats + composition runtime.
> - A `.usda` file is one **layer**, not automatically the whole scene.
> - Composition is the feature that makes USD different from "just an interchange file".

---

## 1.2 History: Pixar, open source, AOUSD

### 1. What is it?

USD started at **Pixar Animation Studios** as an internal scene-description system. Pixar open-sourced it in **2016**. In **2023**, companies formed the **Alliance for OpenUSD (AOUSD)** to evolve the specification in the open.

### 2. Why do we need it?

Knowing the history helps you read docs. Older material says "Pixar USD". Current material says "OpenUSD". The technology is the same line of work. AOUSD is why the exam talks about a *standard*, not a single vendor's tool.

### 3. Beginner explanation

A studio built a tool that solved their movie-pipeline problems so well that they published it, and other companies joined a group to keep it from fragmenting into twenty incompatible dialects.

Where the analogy breaks: OpenUSD is not "finished". Releases still add features (relocates, UsdValidation, splines). This book is verified against **USD 26.08**.

### 4. Technical explanation

- **Pixar** still leads much of the open-source implementation (the GitHub repository `PixarAnimationStudios/OpenUSD`).
- The Python package on PyPI is **`usd-core`**. Version 26.8 is OpenUSD release 26.08.
- **AOUSD** publishes specifications (for example UsdPreviewSurface, USDZ) so implementations can interoperate.
- NVIDIA's certification tests the **OpenUSD developer** skill set (Python/C++ APIs, composition, pipelines), not a single DCC's menus.

### 5. Mental model

```text
Pixar films  -->  open source (2016)  -->  AOUSD (2023)  -->  many industries
```

### 6. Simple example

If two applications both say they "support OpenUSD", they should agree on what a Mesh, a Material, and a reference mean. That agreement is the point of a standard.

### 7. USDA example

There is no unique "history" syntax. The layer header you already saw is part of the spec:

```usda
#usda 1.0
(
    defaultPrim = "World"
    upAxis = "Y"
    metersPerUnit = 0.01
)

def Xform "World"
{
}
```

Those three metadata fields (`defaultPrim`, `upAxis`, `metersPerUnit`) exist because the spec needs a shared meaning for "which prim is the asset", "which way is up", and "how big is one unit".

### 8. Python example

```python
from pxr import Usd
print("USD version:", Usd.GetVersion())
```

**Expected output**

```text
USD version: (0, 26, 8)
```

The tuple is `(0, major, minor)`: 26.08. The leading `0` is a historical major-version slot.

### 9. Real-world use case

A car maker, a game studio, and a VFX house can all sit on the AOUSD working groups and argue for schema changes. That is why you will see domains such as UsdPhysics and UsdLux in the same runtime as film-oriented UsdGeom.

### 10. Common mistakes

> [!MISTAKE] Assuming "NVIDIA USD" is a different scene description. NVIDIA contributes tools, training, and Omniverse applications. The scene description you study for NCP-OUSD is OpenUSD.

> [!MISTAKE] Pinning your career knowledge to one USD version without reading VERSION notes. APIs do get renamed (Chapter 24: `GetMaster` became `GetPrototype`).

### 11. Exam traps

> [!TRAP] "Pixar stopped USD when they open-sourced it." They did not. The implementation continues.

> [!TRAP] Treating AOUSD as a replacement for the runtime. AOUSD governs the standard; you still call Pixar's (and others') libraries.

### 12. Practice questions

**FUN-003** · Difficulty: Easy · Type: Single choice

What is AOUSD?

A. A rival file format to USD  
B. An industry alliance that steers the OpenUSD standard  
C. NVIDIA's proprietary fork of USD  
D. A Python module inside `pxr`  

**Answer:** B. A and C are false. D: there is no `pxr.AOUSD` module.

### 13. Exam takeaways

> [!KEY]
> - Open-sourced by Pixar in 2016; AOUSD formed in 2023.
> - This book and its labs are verified on USD **26.08**.
> - The exam is about OpenUSD development, not one vendor's GUI.

---

## 1.3 Where OpenUSD is used

### 1. What is it?

OpenUSD is used anywhere many 3D tools and teams must share a scene: film and VFX, games, manufacturing and digital twins, architecture/engineering/construction (AEC), robotics, and virtual production.

### 2. Why do we need it?

The exam's job description spans those industries. Pipeline questions are written in industry-neutral language ("DCC", "asset", "assembly") so they apply to a factory digital twin as much as to a feature film.

### 3. Beginner explanation

If more than one program needs to look at the same 3D world, and more than one person needs to edit that world without overwriting each other, USD is a candidate.

Where the analogy breaks: a single artist exporting one statue to a 3D printer does not need composition. USD still helps as an interchange format, but its real power shows up at pipeline scale.

### 4. Technical explanation

Typical patterns:

| Industry | What USD holds | Why composition matters |
|----------|----------------|-------------------------|
| Film / VFX | Shots: cameras, characters, sets, lights, FX | Departments publish layers; lighting does not copy animation |
| Games | Packed environments, instanced props | Native and point instancing keep memory down (Part IV) |
| Manufacturing | Product variants, CAD-derived meshes | Variants select trim levels without duplicating geometry |
| AEC | Buildings, coordinated trades | References assemble a site from many consultants' models |
| Robotics / simulation | Robots, sensors, environments | One stage feeds both visualization and physics |

### 5. Mental model

Same data model; different **assets** and **pipelines**. A "shot" and a "factory cell" are both composed stages.

### 6. Simple example

A robot-arm manufacturer publishes one component asset per arm model. A systems integrator references twenty arms into a cell assembly and overrides each arm's pose in a stronger layer. The original arm files stay untouched.

### 7. USDA example

A tiny "cell" that references an arm (the arm file would exist beside this layer in a real project):

```usda
#usda 1.0
(
    defaultPrim = "Cell"
)

def Xform "Cell" (
    kind = "assembly"
)
{
    def Xform "Arm_01" (
        prepend references = @./arm.usda@
    )
    {
        double3 xformOp:translate = (100, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
}
```

You will author references for real in Chapter 16. For now, notice the idea: the cell **points at** the arm rather than embedding it.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Kind

stage = Usd.Stage.CreateInMemory()
cell = UsdGeom.Xform.Define(stage, "/Cell")
Usd.ModelAPI(cell.GetPrim()).SetKind(Kind.Tokens.assembly)
arm = UsdGeom.Xform.Define(stage, "/Cell/Arm_01")
print("cell kind:", Usd.ModelAPI(cell.GetPrim()).GetKind())
print("paths:", [str(p.GetPath()) for p in stage.Traverse()])
```

**Expected output**

```text
cell kind: assembly
paths: ['/Cell', '/Cell/Arm_01']
```

### 9. Real-world use case

Virtual production on a LED stage consumes a USD scene in real time: cameras, set pieces, and lights. Layout can still replace a referenced building overnight without the playback operator copying files by hand.

### 10. Common mistakes

> [!MISTAKE] Assuming USD is "only for movies". The exam's data-exchange and pipeline domains are industry-neutral.

> [!MISTAKE] Copying assets between departments "to be safe". Copies go stale. Layers and references are the USD way.

### 11. Exam traps

> [!TRAP] A scenario set in manufacturing. The composition rules are the same as in VFX. Do not invent a second set of rules.

### 12. Practice questions

**FUN-004** · Difficulty: Easy · Type: Single choice

A factory digital twin and a VFX shot both use OpenUSD. What do they share?

A. The same renderer  
B. The same scene description, composition rules, and schemas (plus any domain schemas they need)  
C. The same file must be named `shot.usda`  
D. They cannot share anything; USD is film-only  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - USD is used across film, games, manufacturing, AEC, robotics, and virtual production.
> - The exam talks about assets, assemblies, DCCs, and pipelines — not one industry's jargon.

---

## 1.4 The OpenUSD software stack

### 1. What is it?

OpenUSD is a **stack of libraries**, not one module. Each library has a job. You import the ones you need from `pxr`.

### 2. Why do we need it?

Exam questions name these libraries (`Sdf`, `Pcp`, `UsdGeom`, `Ar`, `Tf`). You must know which layer of the stack a problem lives on: "is this a path-resolution issue (`Ar`), an authored-spec issue (`Sdf`), or a composed-value issue (`Usd`)?"

### 3. Beginner explanation

Think of a newspaper:

- **Tf / Gf / Vt** are the printing press and the paper (utilities, math, arrays).
- **Ar** is the mail room (finding files from paths).
- **Sdf** is the stack of original manuscripts (what was actually written).
- **Pcp** is the editor who combines manuscripts by house rules (composition).
- **Usd** is the newspaper you read (the composed scene).
- **UsdGeom / UsdShade / UsdLux / …** are the sections (sports, business) — **schemas** for kinds of data.
- **Hydra** is the newsstand display (imaging).

Where the analogy breaks: you often write through `Usd` and it authors into `Sdf`. You do not usually call `Pcp` directly.

### 4. Technical explanation

Bottom to top:

| Module | Role | You will use it for |
|--------|------|---------------------|
| **Tf** | Foundation: errors, tokens, debug flags, plugins wiring | Diagnostics, `TfDebug` (Ch 43) |
| **Gf** | Graphics-friendly math: vectors, matrices, quaternions | `Gf.Vec3f`, `Gf.Matrix4d` (Ch 9) |
| **Vt** | Value types and arrays | `Vt.Vec3fArray` for mesh points (Ch 9) |
| **Ar** | Asset resolution | Turning `@./chair.usda@` into a real file (Ch 33) |
| **Sdf** | Scene Description Foundations: layers, specs, paths, value types | Authoring and inspecting **what was written** (Ch 3, 8) |
| **Pcp** | PrimCache Population: composition engine | Why a prim exists and which opinions won (Ch 21–22). Rarely called directly |
| **Usd** | Composed scene graph: Stage, Prim, Attribute, Relationship | Everyday authoring and querying (Ch 2–5) |
| **Kind** | Model-kind registry | `component`, `assembly`, `group` (Ch 6) |
| **Plug** | Plugin registry | Custom schemas and file formats (Ch 36) |
| **UsdGeom / UsdShade / UsdLux / UsdPhysics / UsdSkel** | **Schema domains** — typed APIs on top of Usd | Meshes, materials, lights, physics, skeletons |
| **UsdUtils** | Pipeline helpers | Flatten, USDZ, diagnostics, dependencies |
| **UsdValidation** | Validation framework (current) | Replaces the old ComplianceChecker (Ch 30) |
| **Hydra** | Imaging architecture (render delegates, scene indices) | usdview, renderers (Ch 41). Not in `usd-core` |

> [!VERSION] Verified on USD 26.08. `UsdUtils.ComplianceChecker` is **gone**. Use `pxr.UsdValidation`. `Trace` (profiling) and `Ts` (splines) also ship in this build.

### 5. Mental model

```text
Hydra (imaging)          <-- not in usd-core
-------------------------
UsdGeom UsdShade UsdLux  <-- schemas (typed opinions)
Usd                      <-- composed prims / attributes
Pcp                      <-- composition (LIVERPS)
Sdf                      <-- layers and specs
Ar                       <-- find the files
Tf  Gf  Vt               <-- utilities, math, arrays
```

### 6. Simple example

"Why is this prim's radius 5?"

- Ask **Usd** for the composed value: `attr.Get()`.
- Ask **Sdf** which layer authored 5: look at the attribute spec.
- Ask **Pcp** (through `Usd.PrimCompositionQuery`) which composition arc brought that layer in.

### 7. USDA example

You do not import modules in USDA. You *see* which stack level a construct belongs to:

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 0.01
    upAxis = "Y"
)

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 2
        rel material:binding = </World/Looks/Red>
    }
}
```

- The file itself is an **Sdf** layer.
- `def Sphere` is a **UsdGeom** schema.
- `rel material:binding` is a **UsdShade** relationship (once `MaterialBindingAPI` is applied; Ch 40).
- Opening this file creates a **Usd** stage.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom, Gf, Vt, Ar, Kind, Tf

print("Usd", Usd.GetVersion())
print("Sdf.Path", Sdf.Path("/World/Ball"))
print("Gf.Vec3f", Gf.Vec3f(1, 2, 3))
print("Vt.IntArray", Vt.IntArray([1, 2, 3]))
print("Ar default resolver:", type(Ar.GetResolver()).__name__)
print("Kind component is a model:", Kind.Registry.IsA("component", "model"))
print("Tf.Debug present:", hasattr(Tf, "Debug"))
print("UsdGeom.Sphere:", UsdGeom.Sphere)
```

**Expected output**

```text
Usd (0, 26, 8)
Sdf.Path /World/Ball
Gf.Vec3f (1, 2, 3)
Vt.IntArray [1, 2, 3]
Ar default resolver: Resolver
Kind component is a model: True
Tf.Debug present: True
UsdGeom.Sphere: <class 'pxr.UsdGeom.Sphere'>
```

### 9. Real-world use case

A pipeline TD debugs a missing texture. The path string lives on an Sdf attribute. Ar fails to resolve it because the studio resolver does not search that folder. That is an **Ar** problem, not a Mesh schema problem. Choosing the right layer of the stack saves hours.

### 10. Common mistakes

> [!MISTAKE] Importing only `Usd` and then wondering why `Gf.Vec3f` is missing. Import each module you use: `from pxr import Usd, Gf`.

> [!MISTAKE] Calling Hydra APIs in `usd-core`. Imaging is not in this pip package. Teach and test Hydra conceptually (Ch 41).

### 11. Exam traps

> [!TRAP] "Pcp is where you author a sphere." You author with Usd/Sdf. Pcp *composes*.

> [!TRAP] "Sdf and Usd are two names for the same API." They are two views of the data (Ch 8).

### 12. Practice questions

**FUN-005** · Difficulty: Easy · Type: Single choice

Which module is the composition engine?

A. Gf  
B. UsdGeom  
C. Pcp  
D. UsdLux  

**FUN-006** · Difficulty: Medium · Type: Single choice

A texture path on a material does not resolve on the farm. Which library is the first place to look?

A. Gf  
B. Ar  
C. UsdSkel  
D. Vt  

**Answers**

**FUN-005 — Answer: C.** Gf is math. UsdGeom is geometry schemas. UsdLux is lights.

**FUN-006 — Answer: B.** Asset resolution is Ar.

### 13. Exam takeaways

> [!KEY]
> - Remember the stack: Tf/Gf/Vt → Ar → Sdf → Pcp → Usd → schema domains → Hydra.
> - Sdf = authored. Usd = composed. Pcp = the rules in between.
> - Schema domains (UsdGeom, UsdShade, UsdLux) are how you talk about meshes, materials, and lights.

---

## 1.5 The `pxr` Python package

### 1. What is it?

**`pxr`** is the Python package that wraps OpenUSD. Every script in this book starts with `from pxr import ...`.

### 2. Why do we need it?

The exam is a development exam. You must be fluent in the Python API names and how they map from the C++ docs.

### 3. Beginner explanation

`pxr` is a namespace (the letters come from PiXaR). Inside it are modules that match the stack in §1.4.

Where the analogy breaks: not every C++ library has a Python module in `usd-core`. Imaging (`UsdImaging`) is absent here.

### 4. Technical explanation

Verified on this book's environment (`usd-core` 26.8). Modules present include:

`Ar`, `Gf`, `Kind`, `Pcp`, `Plug`, `Sdf`, `Sdr`, `Tf`, `Trace`, `Ts`, `Usd`, `UsdGeom`, `UsdHydra`, `UsdLod`, `UsdLux`, `UsdMedia`, `UsdPhysics`, `UsdProc`, `UsdProfiles`, `UsdRender`, `UsdRi`, `UsdSemantics`, `UsdShade`, `UsdShaders`, `UsdSkel`, `UsdUI`, `UsdUtils`, `UsdValidation`, `UsdVol`, `Vt`, `Work`.

Naming map (C++ → Python), repeated from F2 because you will live in it:

| C++ | Python |
|-----|--------|
| `UsdStage::Open` | `Usd.Stage.Open` |
| `UsdPrim` | `Usd.Prim` |
| `SdfLayer` | `Sdf.Layer` |
| `SdfPath` | `Sdf.Path` |
| `UsdGeomMesh` | `UsdGeom.Mesh` |
| `GfVec3f` | `Gf.Vec3f` |
| `VtArray<int>` | `Vt.IntArray` |

Nested classes become attributes of the module: `Usd.Stage`, `Usd.Prim`, `Usd.Attribute`.

### 5. Mental model

`from pxr import Usd, Sdf, UsdGeom` is the default starter import for most labs.

### 6. Simple example

Wrong: `import usd`. Right: `from pxr import Usd`.

### 7. USDA example

USDA is not Python. Keep them straight: USDA is the text form of a **layer**. Python is how you **create and query** stages.

```usda
#usda 1.0
def Xform "World" {}
```

### 8. Python example

```python
import pkgutil
import pxr
from pxr import Usd

names = sorted(m.name for m in pkgutil.iter_modules(pxr.__path__))
print("version", Usd.GetVersion())
print("has UsdValidation", "UsdValidation" in names)
print("has UsdImaging", "UsdImaging" in names)
print("has UsdMtlx", "UsdMtlx" in names)
```

**Expected output**

```text
version (0, 26, 8)
has UsdValidation True
has UsdImaging False
has UsdMtlx False
```

### 9. Real-world use case

A studio's CI runs `usd-core` in a slim container to validate and convert assets. Artists use a full build with usdview. Both speak the same `pxr` API for the modules they share.

### 10. Common mistakes

> [!MISTAKE] `pip install usd` or `import usd`. The package is `usd-core`; the import is `pxr`.

> [!MISTAKE] Mixing two Pythons: `pip install` with system Python, then running scripts with `.venv`. Always `python -m pip` inside the venv (F5).

### 11. Exam traps

> [!TRAP] C++ snippet `UsdGeomXformable` vs Python `UsdGeom.Xformable`. Same type, different punctuation.

### 12. Practice questions

**FUN-007** · Difficulty: Easy · Type: Single choice

Which import is correct?

A. `import usd`  
B. `from pxr import Usd`  
C. `from nvidia import usd`  
D. `import OpenUSD`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Import from `pxr`. Package name on pip: `usd-core`.
> - C++ `UsdFooBar` → Python `Usd.FooBar` or `UsdGeom.FooBar`.
> - `usd-core` has no usdview and no `UsdImaging`.

---

## Chapter lab(s)

**Lab 01** (install and verify) and **Lab 02** (first stage) live in `python-labs/` and are written in Phase 11. Until then, run the Python examples in this chapter and in F5. That is enough for Day 1.

## USDA reading exercise

**USDA-01.** Read this layer. What is the prim path of the sphere, and what is its radius?

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 2
    }
}
```

**Answer:** Path `/World/Ball`. Radius `2` (a double). The Xform `/World` has no extra attributes.

## Chapter review

### Summary

- OpenUSD is scene description + formats + a composition runtime, not "just a file".
- Layers are documents of opinions; a stage is the composed result (Ch 2–3).
- Industries share the same rules.
- Know the stack: Tf/Gf/Vt, Ar, Sdf, Pcp, Usd, schemas, Hydra.
- Python lives in `pxr`; this book uses USD 26.08.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| "USD is a file format" as a complete answer | Incomplete — also scene description + runtime |
| A prim not in the file you opened | Composition pulled it from another layer |
| `Pcp` in a question | Composition engine, not authoring API |
| `from usd import` | Wrong; `from pxr import Usd` |
| Hydra / usdview in a `usd-core` lab | Not in this pip package; answer conceptually |

### Chapter questions

**Q1.** Name the three parts of OpenUSD (not just "a file format").  
**Q2.** What Python package do you import?  
**Q3.** Which module resolves asset paths?  
**Q4.** Which module stores authored layer specs?  
**Q5.** Which module is the composed scene graph?  
**Q6.** Who open-sourced USD, and in roughly which year?  
**Q7.** What does AOUSD stand for?  
**Q8.** True or false: `usd-core` includes usdview.  
**Q9.** `Usd.GetVersion()` returned `(0, 26, 8)`. What release is that?  
**Q10.** Why can a factory digital twin and a VFX shot use the same composition rules?

**Answers**

1. Scene description, file formats, runtime (composition) libraries.  
2. `pxr`.  
3. `Ar`.  
4. `Sdf`.  
5. `Usd`.  
6. Pixar, 2016.  
7. Alliance for OpenUSD.  
8. False.  
9. OpenUSD 26.08.  
10. Both are composed stages of layers; the data model does not care about the industry.

## Further reading

- [S03] OpenUSD documentation home: https://openusd.org/release/index.html  
- [S04] OpenUSD Glossary: https://openusd.org/release/glossary.html  
- [S14] NVIDIA Learn OpenUSD: https://docs.nvidia.com/learn-openusd/latest/index.html  
- [S18] Alliance for OpenUSD: https://aousd.org  
