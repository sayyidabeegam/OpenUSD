# Chapter 2 — The Stage

> **Exam domain:** Data Modeling (13%) and foundations · **Objectives:** 5.4 (retrieve properties — you need a stage first)
> **Study day:** 1 · **Est. time:** 75 min
> **Prerequisites:** Chapter 1, F5

## Learning goals

- Explain what a **stage** is and how it differs from a layer.
- Create, open, save, and export stages with `CreateInMemory`, `CreateNew`, `Open`, `Save`, and `Export`.
- Traverse prims with `Traverse` and look up a prim with `GetPrimAtPath`.
- Read and set stage metadata: `defaultPrim`, `upAxis`, `metersPerUnit`, time codes.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Stage | The runtime composed scene (`Usd.Stage`) |
| Root layer | The layer you opened or created; the stage's main document |
| Session layer | An anonymous scratch layer, stronger than the root, not saved with the file |
| Traversal | Walking the prim hierarchy on the stage |
| `defaultPrim` | Metadata naming the prim used when this layer is referenced without a prim path |
| `upAxis` | Which axis is "up" in this stage (`Y` or `Z`) |
| `metersPerUnit` | How many meters one scene unit represents |

---

## 2.1 What a stage is

### 1. What is it?

A **stage** is the live, composed 3D scene you work with in code. In Python it is a `Usd.Stage`.

### 2. Why do we need it?

A layer is a document. A renderer, a validator, and your scripts need one combined view of every contributing document. That view is the stage.

### 3. Beginner explanation

If layers are transparent sheets, the stage is what you see on the projector after all the sheets are stacked.

Where the analogy breaks: the stage is not a screenshot. It is a live query API. Changing an opinion on a layer updates what the stage returns.

### 4. Technical explanation

- `Usd.Stage.Open(path)` composes the layer at `path` (and everything it depends on) into a stage.
- Every stage has a **root layer** (`GetRootLayer()`) and a **session layer** (`GetSessionLayer()`).
- The session layer is strongest and anonymous. Edits you put there vanish when the process ends unless you export them yourself.
- `GetLayerStack()` lists the layers that currently contribute, **session layer first** (strongest), then the root, then sublayers in order.

### 5. Mental model

```text
session layer  (scratch, strongest, not the file on disk)
root layer     (the file you opened)
sublayer 0
sublayer 1     (weaker as you go down)
        \________ compose ________/  -->  Usd.Stage
```

### 6. Simple example

You open `shot.usda`. That file lists two sublayers, `anim.usda` and `lgt.usda`. You receive one `Usd.Stage`. Asking for `/World/Hero.xformOp:translate` returns the composed translation, not "the value in shot.usda only".

### 7. USDA example

A stage is not stored as "a stage". You store layers. This layer is enough to open as a stage:

```usda
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
print("root is anonymous:", stage.GetRootLayer().anonymous)
print("session is anonymous:", stage.GetSessionLayer().anonymous)
print("prims on empty stage:", [str(p.GetPath()) for p in stage.Traverse()])
UsdGeom.Xform.Define(stage, "/World")
print("after Define:", [str(p.GetPath()) for p in stage.Traverse()])
```

**Expected output**

```text
root is anonymous: True
session is anonymous: True
prims on empty stage: []
after Define: ['/World']
```

### 9. Real-world use case

usdview opens a stage, not "just a file". Its Layer Stack panel lists the same layers `GetLayerStack()` would return.

### 10. Common mistakes

> [!MISTAKE] Calling the `.usda` file "the stage". The file is a layer. Opening it produces a stage.

> [!MISTAKE] Editing the session layer and wondering why the file on disk did not change. Session edits are not the root layer.

### 11. Exam traps

> [!TRAP] "The stage is the root layer." No. The stage *has* a root layer, plus a session layer, plus everything composition pulls in.

### 12. Practice questions

**FUN-008** · Difficulty: Easy · Type: Single choice

What is a `Usd.Stage`?

A. A ZIP package of textures  
B. The runtime composed scene built from a root layer and its dependencies  
C. Another name for `Sdf.Path`  
D. A Hydra render delegate  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Stage = composed runtime scene. Layer = document of opinions.
> - Every stage has a root layer and a session layer.
> - The session layer is strongest and is not your saved file.

---

## 2.2 Creating, opening, saving

### 1. What is it?

The common constructors and savers on `Usd.Stage`: `CreateInMemory`, `CreateNew`, `Open`, `Save`, `Export`.

### 2. Why do we need it?

You cannot query or author anything without first having a stage. Choosing the wrong constructor loses files or fails in notebooks.

### 3. Beginner explanation

- **CreateInMemory** — scratch paper. Nothing hits disk until you export.
- **CreateNew** — start a new file.
- **Open** — open an existing file (and compose it).
- **Save** — write the layers that are dirty back to their files.
- **Export** — write the *composed* result to a new file (flatten-like; details in Ch 34).

Where the analogy breaks: `Save` saves **layers**, not "the stage as one magic blob". If the root has sublayers, those files save separately.

### 4. Technical explanation

| Method | Use |
|--------|-----|
| `Usd.Stage.CreateInMemory()` | Tests, examples, scratch. Root and session are anonymous layers |
| `Usd.Stage.CreateNew("path.usda")` | New identifier on disk. In a **new** Python process, if the file already exists, this starts an **empty** layer and `Save()` will replace the file |
| `Usd.Stage.Open("path.usda")` | Compose an existing layer |
| `stage.GetRootLayer().Save()` | Write the root layer |
| `stage.Save()` | Save all dirty saveable layers |
| `stage.Export("out.usda")` / `stage.ExportToString()` | Dump the composed scene |

> [!MISTAKE] In the **same** Python session, `CreateNew` on an identifier that is already open raises `A layer already exists with identifier…`. Restart the interpreter, or `Open` the existing layer. In a **fresh** session, `CreateNew` on an existing **file** does not error — it starts empty and can overwrite on Save. Use `Open` to edit existing files.

`Open` can take `Usd.Stage.InitialLoadSet` to start with payloads loaded or unloaded (Ch 17).

### 5. Mental model

CreateInMemory = RAM. CreateNew = new file. Open = existing file. Save = write layers. Export = snapshot of the composed stage.

### 6. Simple example

Lab scripts in this book almost always `CreateInMemory()` so they do not leave files behind. Pipeline tools almost always `Open` a published asset.

### 7. USDA example

After `CreateNew("hello.usda")` and defining `/World`, the file looks like:

```usda
#usda 1.0

def Xform "World"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateNew("ch02_hello.usda")
UsdGeom.Xform.Define(stage, "/World")
stage.GetRootLayer().Save()

opened = Usd.Stage.Open("ch02_hello.usda")
print("opened prims:", [str(p.GetPath()) for p in opened.Traverse()])
print("identifier ends with:", opened.GetRootLayer().identifier.split("/")[-1])
print(opened.GetRootLayer().ExportToString())
```

**Expected output**

```text
opened prims: ['/World']
identifier ends with: ch02_hello.usda
#usda 1.0

def Xform "World"
{
}

```

### 9. Real-world use case

A publisher tool `Open`s the working layer, authors `assetInfo`, then `Save`s. A delivery tool `Open`s the same asset and `Export`s a flattened package for a vendor who cannot resolve your internal references (Ch 34).

### 10. Common mistakes

> [!MISTAKE] Using `CreateNew` every time you run a script on the same path. You wipe previous content when you Save.

> [!MISTAKE] Forgetting `Save()`. In-memory and even CreateNew stages do not write until you save or export.

### 11. Exam traps

> [!TRAP] "Export and Save are the same." Save writes authored layers. Export writes the composed result to a new location.

### 12. Practice questions

**FUN-009** · Difficulty: Medium · Type: Single choice

You want to edit `chair.usda` without wiping it. Which call?

A. `Usd.Stage.CreateNew("chair.usda")`  
B. `Usd.Stage.Open("chair.usda")`  
C. `Usd.Stage.CreateInMemory("chair.usda")` then hope  
D. `Sdf.Path("/chair.usda")`  

**Answer:** B. A can overwrite. C is a new anonymous stage (the string is only a label). D is a path, not a stage.

### 13. Exam takeaways

> [!KEY]
> - `Open` to edit. `CreateNew` for a new file. `CreateInMemory` for tests.
> - `Save` ≠ `Export`.
> - `CreateNew` in a fresh process can silently replace an existing file on Save.

---

## 2.3 Stage traversal

### 1. What is it?

**Traversal** walks the prims on the stage. `GetPrimAtPath` jumps to one prim.

### 2. Why do we need it?

Obj 5.4 (retrieve properties of a prim) starts with finding the prim. Validators, converters, and debug tools all traverse.

### 3. Beginner explanation

The stage is a tree. Traversal is walking the tree from the root down.

Where the analogy breaks: inactive prims are skipped by `Traverse()` but still exist. Use `TraverseAll()` when you need them (see Ch 4).

### 4. Technical explanation

- `stage.Traverse()` yields `Usd.Prim` in depth-first, namespace order, skipping inactive and (by default) abstract prims.
- `stage.GetPrimAtPath("/World/Ball")` returns a `Usd.Prim`. If nothing is there, you still get a handle; **check `IsValid()`**.
- `stage.GetPseudoRoot()` is the hidden `/` prim that parents every root prim.

### 5. Mental model

```text
/              (pseudo-root, you rarely author it)
└── World
    └── Ball
```

`Traverse()` visits `/World` then `/World/Ball`.

### 6. Simple example

"Print every prim type on this asset" is a ten-line traverse.

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 2
    }
    def Cube "Box"
    {
    }
}
```

Traversal order: `/World`, `/World/Ball`, `/World/Box`.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/World")
UsdGeom.Sphere.Define(stage, "/World/Ball")
UsdGeom.Cube.Define(stage, "/World/Box")

print("Traverse:")
for prim in stage.Traverse():
    print(f"  {prim.GetPath()} type={prim.GetTypeName()}")

ball = stage.GetPrimAtPath("/World/Ball")
missing = stage.GetPrimAtPath("/Nope")
print("Ball valid:", ball.IsValid(), "name:", ball.GetName())
print("Nope valid:", missing.IsValid())
```

**Expected output**

```text
Traverse:
  /World type=Xform
  /World/Ball type=Sphere
  /World/Box type=Cube
Ball valid: True name: Ball
Nope valid: False
```

### 9. Real-world use case

A converter traverses the stage, and for every `UsdGeom.Mesh` prim exports a glTF mesh (Ch 27). Skipping `IsValid()` checks is how importers crash on empty paths.

### 10. Common mistakes

> [!MISTAKE] Using the result of `GetPrimAtPath` without `IsValid()`. Invalid prims look like objects; they just do not represent anything on the stage.

> [!MISTAKE] Expecting `Traverse()` to visit inactive prims. It will not. Ch 4.

### 11. Exam traps

> [!TRAP] "GetPrimAtPath raises if the prim is missing." It does not. It returns an invalid prim.

### 12. Practice questions

**FUN-010** · Difficulty: Easy · Type: Single choice

`stage.GetPrimAtPath("/Does/Not/Exist").IsValid()` returns:

A. True  
B. False  
C. It raises KeyError  
D. None  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - `Traverse()` walks defined, active prims in namespace order.
> - Always `IsValid()` after `GetPrimAtPath`.

---

## 2.4 Stage metadata

### 1. What is it?

**Stage metadata** is data about the whole scene, stored on the **root layer**: `defaultPrim`, `upAxis`, `metersPerUnit`, `timeCodesPerSecond`, `startTimeCode`, `endTimeCode`, and others.

### 2. Why do we need it?

Without `defaultPrim`, referencing this file without a prim path fails. Without agreed `upAxis` and `metersPerUnit`, a chair from one DCC appears on its side or 100× too small in another (Obj 4.7, Ch 28). Time metadata tells animation tools the intended frame range.

### 3. Beginner explanation

Metadata is the label on the moving box: which way is up, how big is a unit, which object inside is "the thing", and which frames the shot covers.

Where the analogy breaks: USD does **not** automatically rescale a referenced file to match the stage's units. That is a famous exam fact (Ch 28).

### 4. Technical explanation

Verified defaults on USD 26.08 for a new in-memory stage:

| Field | Default | API |
|-------|---------|-----|
| `upAxis` | `Y` | `UsdGeom.GetStageUpAxis` / `SetStageUpAxis` |
| `metersPerUnit` | `0.01` (centimetres) | `UsdGeom.GetStageMetersPerUnit` / `SetStageMetersPerUnit` |
| `timeCodesPerSecond` | `24.0` | `stage.GetTimeCodesPerSecond()` / `SetTimeCodesPerSecond` |
| `framesPerSecond` | `24.0` | `GetFramesPerSecond` / `SetFramesPerSecond` |
| `startTimeCode` / `endTimeCode` | `0.0` / `0.0` | `GetStartTimeCode` / `SetStartTimeCode` (same for end) |
| `defaultPrim` | unset | `stage.SetDefaultPrim(prim)` / `GetDefaultPrim` |

`UsdGeom.LinearUnits.meters` is `1.0`; `UsdGeom.LinearUnits.centimeters` is `0.01`.

Tokens: `UsdGeom.Tokens.y`, `UsdGeom.Tokens.z` (and `x`).

### 5. Mental model

Stage metadata lives in the USDA header, inside the first parentheses after `#usda 1.0`.

### 6. Simple example

A camera-tracking department works Z-up in metres. They set `upAxis = "Z"` and `metersPerUnit = 1`. A DCC that defaults to Y-up centimetres must be taught to write those fields or the shot will not match.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "World"
    metersPerUnit = 0.01
    upAxis = "Z"
    timeCodesPerSecond = 24
    startTimeCode = 1001
    endTimeCode = 1100
)

def Xform "World"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
print("default upAxis:", UsdGeom.GetStageUpAxis(stage))
print("default metersPerUnit:", UsdGeom.GetStageMetersPerUnit(stage))
print("default tps/fps:", stage.GetTimeCodesPerSecond(), stage.GetFramesPerSecond())

UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.LinearUnits.meters)
world = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(world.GetPrim())
stage.SetStartTimeCode(1001)
stage.SetEndTimeCode(1100)

print("upAxis:", UsdGeom.GetStageUpAxis(stage))
print("metersPerUnit:", UsdGeom.GetStageMetersPerUnit(stage))
print("defaultPrim:", stage.GetDefaultPrim().GetName())
print("range:", stage.GetStartTimeCode(), stage.GetEndTimeCode())
print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
default upAxis: Y
default metersPerUnit: 0.01
default tps/fps: 24.0 24.0
upAxis: Z
metersPerUnit: 1.0
defaultPrim: World
range: 1001.0 1100.0
#usda 1.0
(
    defaultPrim = "World"
    endTimeCode = 1100
    metersPerUnit = 1
    startTimeCode = 1001
    upAxis = "Z"
)

def Xform "World"
{
}

```

### 9. Real-world use case

A data-exchange validator fails an export that has no `defaultPrim`, because downstream `references = @asset.usda@` (no prim path) cannot pick an entry point (Ch 16, Obj 4.6).

### 10. Common mistakes

> [!MISTAKE] Assuming USD converts units when you reference a metres file into a centimetres stage. It does not. The geometry numbers stay as authored (Ch 28).

> [!MISTAKE] Setting `upAxis` as an attribute on `/World`. It is **stage/layer metadata**, not a prim property.

### 11. Exam traps

> [!TRAP] Default `metersPerUnit` is `0.01` in this runtime, not `1`. Do not memorize "USD is always metres".

> [!TRAP] `defaultPrim` value in USDA is the **prim name** (`"World"`), not the path `"/World"`.

### 12. Practice questions

**FUN-011** · Difficulty: Medium · Type: Single choice

What is `defaultPrim` for?

A. The material used when none is bound  
B. The prim used as the target when this layer is referenced without a prim path  
C. The first prim `Traverse()` visits, always `/`  
D. The session layer's name  

**FUN-012** · Difficulty: Medium · Type: Single choice

A layer with `metersPerUnit = 1.0` is referenced into a stage with `metersPerUnit = 0.01`. What does USD do at compose time?

A. Scales the referenced geometry ×100 automatically  
B. Scales the referenced geometry ×0.01 automatically  
C. Leaves the numbers as authored; no automatic unit conversion  
D. Refuses to compose  

**Answers**

**FUN-011 — Answer: B.** Obj-adjacent to 1.x / defaultPrim docs.

**FUN-012 — Answer: C.** Automatic conversion is a common wrong answer. Full treatment in Ch 28. NVIDIA's study-guide sample on this topic is **not** reproduced here; this question is original.

### 13. Exam takeaways

> [!KEY]
> - Always author `defaultPrim`, `upAxis`, and `metersPerUnit` on publishable assets.
> - Defaults on USD 26.08: upAxis Y, metersPerUnit 0.01, 24 fps.
> - USD does not auto-convert units across references.

---

## Chapter lab(s)

Day 1 labs 02–03 (first stage; open and traverse) correspond to this chapter. Until Phase 11 writes the lab files, run this chapter's Python examples in your venv.

## USDA reading exercise

**USDA-02.** From the layer in §2.4's USDA example: what is the default prim name, which way is up, and what is the first intended time code?

**Answer:** `World`, Z-up, 1001.

## Chapter review

### Summary

- A stage is the composed runtime scene.
- CreateInMemory / CreateNew / Open / Save / Export do different jobs.
- Traverse and GetPrimAtPath are how you find prims; check IsValid.
- Stage metadata lives in the layer header.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| "Stage vs layer" | Stage = composed; layer = document |
| Missing prim after GetPrimAtPath | Call IsValid() |
| Asset referenced with no prim path | defaultPrim |
| Object 100× too small after reference | metersPerUnit, no auto-convert |
| Edits disappeared after restart | You authored on the session layer |

### Chapter questions

**Q1.** Name the two layers every stage always has.  
**Q2.** Which `GetLayerStack` entry is strongest by default?  
**Q3.** `CreateNew` vs `Open` — which edits an existing file safely?  
**Q4.** What does `Traverse()` skip that `TraverseAll()` still visits (preview of Ch 4)?  
**Q5.** Default `upAxis` and `metersPerUnit` on USD 26.08?  
**Q6.** Does `GetPrimAtPath` raise on a missing path?  
**Q7.** Save vs Export in one sentence each.  
**Q8.** Why set `defaultPrim` on an asset you will reference?

**Answers**

1. Root layer and session layer.  
2. The session layer (first in the stack).  
3. Open.  
4. Inactive (and abstract) prims.  
5. Y and 0.01.  
6. No; invalid prim.  
7. Save writes authored layers; Export writes a composed snapshot.  
8. So references without a prim path have an entry point.

## Further reading

- OpenUSD API: `UsdStage` — https://openusd.org/release/api/class_usd_stage.html  
- Tutorial: Traversing a Stage — https://openusd.org/release/tut_traversing_stage.html  
- Encoding stage `upAxis` and linear units (API docs linked from the study guide)
