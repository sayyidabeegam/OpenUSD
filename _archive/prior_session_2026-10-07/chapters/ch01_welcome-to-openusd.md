# Chapter 1 — Welcome to OpenUSD {#ch01}

::: {.chapter-meta}
**Exam domain:** Foundations for all domains · **Objectives:** none directly (prepares every domain)
**Study day:** Day 1 · **Estimated time:** 45 min · **Prerequisites:** none
:::

## Learning goals

By the end of this chapter you can:

- explain in one sentence what OpenUSD is, and what it is not;
- distinguish *scene description*, *file format*, and *runtime library*;
- describe non-destructive layered editing and why studios depend on it;
- name the main OpenUSD software modules and what each is for;
- run your first tiny OpenUSD Python script (after Chapter 2's setup).

## 1.1 What is USD / OpenUSD?

### What is it?

**OpenUSD** (Open Universal Scene Description, often just **USD**) is an open-source system for describing, combining, and exchanging 3D scenes. It was created at Pixar Animation Studios and released as open source in 2016. Today it is developed in the open, and its standardization is guided by the **Alliance for OpenUSD (AOUSD)**, an industry group founded in 2023.

### Why do we need it?

A modern 3D project uses many tools: one for modeling, one for animation, one for lighting, a game engine, a CAD package, a renderer. Each tool historically had its own scene format. Moving data between them meant lossy exports, duplicated files, and broken work whenever someone upstream changed something.

USD gives all those tools **one shared way to describe a scene**, and a way for many people to contribute to the same scene **at the same time without overwriting each other**.

### Beginner explanation

Think of a shared recipe book in a large restaurant kitchen. The original recipe stays untouched. The pastry chef clips a note on top saying "use less sugar", and the head chef clips another saying "serve on a blue plate". Anyone reading the recipe sees the original plus all the notes, combined in a known order.

USD works the same way: the original data stays intact, and later contributions are *layered on top*.

*Where the analogy stops:* in USD, the "notes" follow strict, predictable rules about which note wins when two disagree. Learning those rules (Part III, Composition) is the biggest single part of the exam.

### Technical explanation

USD consists of three things that are easy to confuse:

| Part | What it is | Example |
|------|-----------|---------|
| **Scene description** | A data model: prims (scene objects) with properties, arranged in a hierarchy, stored in layers | "There is a sphere at `/World/Ball` with radius 2" |
| **File formats** | Ways to save layers to disk | `.usda` (text), `.usdc` (binary), `.usdz` (package) |
| **Runtime libraries** | C++ libraries with Python bindings that read, combine (*compose*), edit, and serve scene data to applications and renderers | `pxr.Usd`, `pxr.Sdf`, `pxr.UsdGeom` |

The most important runtime idea is **composition**: USD reads several layers and combines them into one *composed* scene according to fixed strength rules. Applications see only the composed result unless they ask for the details.

::: {.note}
"USD" and "OpenUSD" refer to the same technology. The official name for the open-source project is OpenUSD; the libraries, file extensions, and Python package (`pxr`) still use "usd". This book uses "OpenUSD" for the project and "USD" in running text.
:::

### Mental model

::: {.mental-model}
USD = a shared scene, built from stacked layers, combined by fixed rules, readable by every tool.
:::

### Simple example

A furniture company has a chair model. The design team owns `chair_geo.usda` (shape). The marketing team wants a red version for a catalogue. Instead of copying and editing the file, they create a small layer that says only "the chair's color is red" and stack it on top. The original file is never touched; if the designers improve the chair's shape tomorrow, the red catalogue version picks up the new shape automatically.

### USDA example

`.usda` is USD's human-readable text format. Here is a complete, valid layer describing one sphere:

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

- `#usda 1.0` — the header every text layer starts with.
- `def Xform "World"` — *define* a prim named `World` of type `Xform` (a transformable group).
- `def Sphere "Ball"` — define a child prim `Ball` of type `Sphere`. Its full path is `/World/Ball`.
- `double radius = 2` — an attribute named `radius`, of value type `double`, with value 2.

You will learn every part of this syntax in Chapters 3–6.

### Python example

This script builds the same scene in memory and prints the layer as USDA text. Run it after completing the setup in Chapter 2.

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.GetRadiusAttr().Set(2.0)

print(stage.GetRootLayer().ExportToString())
```

**Expected output:**

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

What happened:

1. `Usd.Stage.CreateInMemory()` created an empty **stage** (the composed scene) with one empty, unsaved **root layer**.
2. `UsdGeom.Xform.Define` and `UsdGeom.Sphere.Define` *authored* two prims into that root layer.
3. `GetRadiusAttr().Set(2.0)` authored a value for the sphere's `radius` attribute.
4. `ExportToString()` turned the layer into USDA text.

### Real-world use case

- **Film and animation:** hundreds of artists work on one shot. Layout, animation, effects, and lighting each write to their own layers; the shot is the composition of all of them.
- **Games and real-time:** engines import USD assets and scenes from many content tools.
- **Manufacturing and digital twins:** CAD data, factory layouts, and simulation results are aggregated into one live, navigable scene.
- **Architecture (AEC), robotics, and AR:** large scenes with millions of reused parts, robot descriptions, and `.usdz` packages viewed on phones.

### Common mistakes

- **"USD is just a file format."** It also defines a data model and a composition engine; the file formats are only one part.
- **"Editing a scene changes the original files."** Edits go to whichever layer you target; source layers can stay untouched.
- **"USD is a renderer."** USD describes scenes. Rendering is done by renderers that read USD, usually through Pixar's *Hydra* imaging framework (Chapter 54).

### Exam traps

::: {.exam-trap}
- Answers that describe USD as "a 3D file format like OBJ or FBX" miss composition and non-destructive layering, which are the core of the exam.
- USD does **not** silently merge conflicting edits by "last saved wins". Conflicts are resolved by **strength order** (Chapter 25).
:::

### Practice questions

See 1-Q1 and 1-Q2 at the end of the chapter.

### Exam takeaways

::: {.takeaways}
- OpenUSD = scene description + file formats + runtime libraries with a composition engine.
- Originated at Pixar; open-sourced in 2016; standardization guided by AOUSD (founded 2023).
- Many contributors edit one scene through separate layers, combined by fixed strength rules.
:::

## 1.2 Scene description, file format, and runtime

### What is it?

**Scene description** is data that *describes* a 3D scene (what objects exist, how they are arranged, what they look like) as opposed to pixels or render instructions.

### Why do we need it?

Separating "what the scene is" from "how it is stored" and "how it is drawn" lets each part improve independently. The same scene can be stored as text for debugging, as binary for speed, and drawn by any renderer.

### Beginner explanation

Sheet music describes a song; it is not the sound. The same sheet music can be printed on paper or stored as a PDF (file format) and played by any orchestra (renderer).

### Technical explanation

- Scene description is stored in **layers** (`Sdf.Layer`). A layer is the unit that is saved to a file.
- The **file format** of a layer is chosen by its extension, through USD's file format plugins. `.usda` and `.usdc` hold identical scene description in different encodings; Chapter 9 compares them.
- The **runtime** composes layers into a **stage** (`Usd.Stage`) that applications query. Renderers consume the stage, usually through Hydra.

### Mental model

::: {.mental-model}
Layer = stored data. Stage = composed view. Renderer = consumer of the stage.
:::

### Simple example

The text file `ball.usda` and the binary file `ball.usdc` can contain exactly the same sphere. Open either one and the stage looks identical to your code.

### USDA example

The USDA in Section 1.1 is scene description. Saved as `ball.usdc`, it would contain the same data in binary form, which you cannot read in a text editor but can print with the `usdcat` tool (Chapter 2).

### Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/Ball")
stage.GetRootLayer().Export("ball.usda")
stage.GetRootLayer().Export("ball.usdc")

for name in ("ball.usda", "ball.usdc"):
    s = Usd.Stage.Open(name)
    print(name, [str(p.GetPath()) for p in s.Traverse()])
```

**Expected output:**

```text
ball.usda ['/Ball']
ball.usdc ['/Ball']
```

Both files open to the same composed scene. `Export` chose the encoding from the file extension.

### Real-world use case

Pipelines publish heavy geometry as `.usdc` for speed and keep small top-level "assembly" files as `.usda` so humans can read and diff them in version control.

### Common mistakes

- Assuming a `.usd` file is always binary. `.usd` can hold either encoding (Chapter 9).
- Thinking the renderer reads files directly. It reads the *composed stage*.

### Exam traps

::: {.exam-trap}
USDA vs USDC is a storage choice, not a feature choice: both support the same scene description.
:::

### Practice questions

See 1-Q3.

### Exam takeaways

::: {.takeaways}
- Layers store; stages compose; renderers consume.
- File format is selected by extension; `.usda` and `.usdc` encode identical data.
:::

## 1.3 Non-destructive layered editing

### What is it?

**Non-destructive editing** means making changes in a separate, stronger layer instead of modifying the original data. The original stays intact; the composed result shows the change.

### Why do we need it?

- Many people can work in parallel without file conflicts.
- Any change can be removed simply by removing its layer.
- Upstream improvements flow downstream automatically.

### Beginner explanation

Transparent sheets on an overhead projector: the bottom sheet has the drawing; a sheet on top recolors one shape. What you see on the wall is the combination. Remove the top sheet and the original returns.

*Where the analogy stops:* a projector shows every sheet equally. In USD a stronger layer's opinion *replaces* a weaker one for the same property; it does not blend.

### Technical explanation

A value authored in a layer is called an **opinion**. When several layers hold opinions for the same property, the composed value comes from the **strongest** one. When layers are stacked with **sublayers**, earlier entries in the `subLayers` list are stronger. A prim specified with `over` adds opinions without defining a new prim. These rules are expanded in Chapters 17–25.

### Mental model

::: {.mental-model}
Stronger layer's opinion wins; weaker layers are never modified.
:::

```text
  shot.usda (root layer)
    subLayers:
      [0] edits.usda   radius = 2   <-- stronger (listed first)
      [1] base.usda    radius = 1   <-- weaker
  Composed result: /Ball.radius = 2
```

Figure 1.1 — A layer stack. Strongest layer at the top.

### Simple example

`base.usda` says the ball's radius is 1. `edits.usda` says 2. The shot layer lists `edits.usda` before `base.usda`, so the composed radius is 2, and `base.usda` still says 1.

### USDA example

The three layers, as they would appear on disk:

`base.usda`:

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 1
}
```

`edits.usda` (note `over`: it adds an opinion but does not define the prim):

```usda
#usda 1.0

over "Ball"
{
    double radius = 2
}
```

`shot.usda` (the root layer that stacks them):

```usda
#usda 1.0
(
    subLayers = [
        @./edits.usda@,
        @./base.usda@
    ]
)
```

### Python example

```python
from pxr import Sdf, Usd, UsdGeom

base = Sdf.Layer.CreateNew("base.usda")
base.ImportFromString('#usda 1.0\ndef Sphere "Ball"\n{\n    double radius = 1\n}\n')
base.Save()

edits = Sdf.Layer.CreateNew("edits.usda")
edits.ImportFromString('#usda 1.0\nover "Ball"\n{\n    double radius = 2\n}\n')
edits.Save()

shot = Sdf.Layer.CreateNew("shot.usda")
shot.subLayerPaths.append("./edits.usda")
shot.subLayerPaths.append("./base.usda")
shot.Save()

stage = Usd.Stage.Open("shot.usda")
ball = UsdGeom.Sphere(stage.GetPrimAtPath("/Ball"))
print("Composed radius:", ball.GetRadiusAttr().Get())
print("base.usda still says:", base.GetAttributeAtPath("/Ball.radius").default)
```

**Expected output:**

```text
Composed radius: 2.0
base.usda still says: 1.0
```

### Real-world use case

In a film shot, the animation department's layer moves a character, while the lighting department's layer adds lights. Both are sublayers of the shot. Neither department edits the other's file, and the character asset itself is untouched.

### Common mistakes

- Expecting the *last* sublayer in the list to win. In a `subLayers` list, the **first** entry is the strongest.
- Using `def` when you only mean to override. `def` defines the prim (and can give it a type); `over` only adds opinions. Chapter 4 explains when it matters.

### Exam traps

::: {.exam-trap}
- "The weaker layer's value is overwritten on disk" is false. Weaker layers are not modified.
- Sublayer order: first listed = strongest. Many distractors invert this.
:::

### Practice questions

See 1-Q4 and 1-Q5.

### Exam takeaways

::: {.takeaways}
- An authored value is an **opinion**; the strongest opinion wins.
- In `subLayers`, earlier = stronger.
- `over` adds opinions without defining a prim.
:::

## 1.4 Where OpenUSD is used

OpenUSD started in feature animation and visual effects, where huge, collaborative scenes are normal. It is now used across:

| Industry | Typical use |
|----------|-------------|
| Animation and VFX | Shot assembly, department layering, asset libraries, render handoff |
| Games and real-time | Asset interchange between content tools and engines |
| Manufacturing and digital twins | Aggregating CAD, factory layouts, and simulation data |
| Architecture, engineering, construction (AEC) | Coordinating models from many disciplines |
| Robotics and simulation | Robot and environment descriptions, physics (UsdPhysics) |
| AR and e-commerce | `.usdz` packages viewed on phones and the web |

Table 1.1 — OpenUSD use by industry.

::: {.exam-tip}
The NCP-OUSD exam is tool-neutral. Questions use USD concepts, USDA snippets, and the Python/C++ API, not any one application's interface.
:::

## 1.5 The OpenUSD module map

### What is it?

OpenUSD is split into libraries (modules). In Python they all live under the `pxr` package, for example `from pxr import Usd, Sdf`.

### Why do we need it?

Exam questions and API documentation name classes by module (`UsdStage`, `SdfLayer`, `GfVec3f`). Knowing what each module does tells you where to look and which class to use.

### Technical explanation

| Module | Full name | What it provides | Chapters |
|--------|-----------|------------------|----------|
| `Tf` | Tools Foundation | Tokens, diagnostics, notices, type system, debug flags | 36, 57 |
| `Gf` | Graphics Foundations | Math: vectors, matrices, quaternions, ranges, cameras | 11, 49 |
| `Vt` | Value Types | `VtArray` arrays and the type-erased `VtValue` | 11 |
| `Ar` | Asset Resolution | Turning asset paths like `@./chair.usda@` into real locations | 41 |
| `Sdf` | Scene Description Foundations | Layers, paths, specs, value type names, the text format | 10 |
| `Pcp` | PrimCache Population | The composition engine that applies the strength rules | 17, 27 |
| `Usd` | Universal Scene Description core | Stage, prim, attribute, relationship, composition arc editing | 3–7 |
| `Kind` | Kind | Model kinds (component, assembly, ...) | 8, 29 |
| `Plug` | Plugins | Plugin discovery and registration | 46 |
| `UsdGeom` | Geometry schemas | Xform, Mesh, Points, Camera, PointInstancer, primvars | 49–51 |
| `UsdShade` | Shading schemas | Material, Shader, material binding | 52 |
| `UsdLux` | Lighting schemas | Lights | 53 |
| `UsdUtils` | Utilities | Flattening, dependencies, packaging, diagnostics helpers | 42, 44 |
| `UsdValidation` | Validation framework | Validators for checking assets | 39 |
| Hydra (`Hd` and related) | Imaging framework | Feeds scenes to renderers | 54 |

Table 1.2 — Main OpenUSD modules.

### Mental model

::: {.mental-model}
Bottom to top: math and values (Gf, Vt, Tf) → files and paths (Ar, Sdf) → composition (Pcp) → scene API (Usd) → domain schemas (UsdGeom, UsdShade, UsdLux) → imaging (Hydra).
:::

### Simple example

To read a mesh's points: `Usd` opens the stage, `UsdGeom.Mesh` gives the `points` attribute, and the values come back as a `Vt.Vec3fArray` of `Gf.Vec3f`.

### Python example

```python
from pxr import Gf, Sdf, Usd, UsdGeom, Vt

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Tri")
mesh.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)]))

points = mesh.GetPointsAttr().Get()
print(type(points).__name__, len(points))
print(mesh.GetPath(), isinstance(mesh.GetPath(), Sdf.Path))
```

**Expected output:**

```text
Vec3fArray 3
/Tri True
```

### Real-world use case

Pipeline tools mostly use `Usd` plus the schema modules. Performance-critical exporters drop down to `Sdf` (Chapter 10). Studios customize `Ar` to plug in their asset management system (Chapter 41).

### Common mistakes

- Looking for Python classes under C++ names: C++ `UsdStage` is Python `Usd.Stage`; C++ `GfVec3f` is Python `Gf.Vec3f`.
- Confusing `Sdf` (individual layers) with `Usd` (the composed stage). Chapter 10 is devoted to this.

### Exam traps

::: {.exam-trap}
`Pcp` performs composition; `Sdf` only stores layer data. A question asking "which library computes the strongest opinion across layers" points at composition (Pcp, surfaced through Usd), not Sdf.
:::

### Practice questions

See 1-Q6.

### Exam takeaways

::: {.takeaways}
- Python modules live under `pxr`; C++ `UsdStage` = Python `Usd.Stage`.
- Sdf = layers and paths; Pcp = composition; Usd = composed scene API.
- Schema modules: UsdGeom (geometry), UsdShade (materials), UsdLux (lights).
:::

## Putting it together

A furniture retailer receives a chair asset from a manufacturer as `chair.usdc`. The retailer's web team creates `catalogue.usda`, which sublayers the chair and adds an `over` that changes the color. Their AR team packages the result as `.usdz` for phones. The manufacturer later sends an improved `chair.usdc`; the catalogue picks it up with no edits. One shared scene description, several layers, many tools.

## Chapter summary

- OpenUSD is a scene description system: a data model, file formats, and runtime libraries with a composition engine.
- Scenes are built from layers; the runtime composes them into a stage; renderers consume the stage.
- Non-destructive editing: stronger layers override weaker ones without modifying them. In `subLayers`, first = strongest.
- The `pxr` modules form a stack from math (Gf, Vt) through layers (Sdf), composition (Pcp), the scene API (Usd), to schemas and imaging.

## Practice questions

**1-Q1.** Which description of OpenUSD is most complete?

A. A binary 3D file format optimized for fast loading
B. A renderer for film-quality images
C. A scene description system with a data model, file formats, and a composition engine
D. A modeling application for creating 3D assets

**1-Q2.** A lighting artist changes a light's intensity in their own layer. What happens to the layout department's layer that also contains the light? (Select one.)

A. Its value is overwritten when the lighting layer is saved
B. It is unchanged; the composed scene shows the stronger opinion
C. USD averages the two values
D. USD reports a conflict error and refuses to open the stage

**1-Q3.** `asset.usda` and `asset.usdc` were exported from the same stage. Which statement is true?

A. Only the `.usda` file can contain composition arcs
B. They hold the same scene description in different encodings
C. The `.usdc` file must be converted before it can be opened on a stage
D. The `.usda` file loses time samples

**1-Q4.** A root layer has `subLayers = [@./a.usda@, @./b.usda@]`. Both sublayers author `radius` on `/Ball`: `a.usda` says 3, `b.usda` says 5. What is the composed radius?

A. 3
B. 5
C. 8
D. Undefined: USD reports an error

**1-Q5.** Which statements about non-destructive editing are true? (Select two.)

A. Removing an override layer restores the previous composed result
B. Weaker layers are rewritten to match stronger ones when saved
C. Upstream changes to a weaker layer still appear in the composed result where no stronger opinion exists
D. Only one layer may author a given property

**1-Q6.** Which OpenUSD library is responsible for turning an asset path such as `@./chair.usda@` into a concrete location?

A. Sdf
B. Ar
C. Gf
D. Vt

## Answers and explanations

**1-Q1 — C.** OpenUSD is more than a file format (A) and is not a renderer (B) or a modeling tool (D). Its defining features are the data model and composition.

**1-Q2 — B.** Edits go to the targeted layer only. Opinions are never averaged (C), conflicting opinions are normal and resolved by strength (D), and weaker layers are not modified (A).

**1-Q3 — B.** USDA and USDC are two encodings of the same data model; both support all features and open directly on a stage.

**1-Q4 — A.** The first entry in `subLayers` is the strongest, so `a.usda`'s value 3 wins. Values never add up (C), and differing opinions are not an error (D).

**1-Q5 — A, C.** Removing a stronger layer reveals the weaker opinions again (A). Weaker layers keep contributing wherever nothing stronger speaks (C). Weaker layers are never rewritten (B), and any number of layers may author the same property (D).

**1-Q6 — B.** Ar (Asset Resolution) resolves asset paths. Sdf stores layers and holds the asset path as data, but does not decide where it points.

## Labs for this chapter

- **Lab 01 — Hello Stage** (after Chapter 2 setup): create a stage, define prims, save as `.usda`.

## Sources for this chapter

[S-03] USD Terms and Concepts · [S-05] USD API Documentation · [S-13] OpenUSD repository · [S-20] Learn OpenUSD · [S-21] Learn OpenUSD — Setting the Stage · [S-43] AOUSD
