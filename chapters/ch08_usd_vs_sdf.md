# Chapter 8 — Usd vs. Sdf: Two Ways to See Data

> **Exam domain:** Data Modeling (13%) · **Objectives:** 5.4, 6.1
> **Study day:** 3 · **Est. time:** 80 min
> **Prerequisites:** Chapters 2–5

## Learning goals

- Contrast the **composed view** (`Usd`) with the **authored view** (`Sdf`).
- Inspect `PrimSpec`, `AttributeSpec`, and `RelationshipSpec`.
- Use `Sdf.Path` operations when talking to Sdf APIs.
- Author with Sdf for speed.
- Know when `Sdf.ChangeBlock` removes composition-notification overhead (Obj 6.1).

## Key terms

| Term | One-line definition |
|------|---------------------|
| Composed view | What `Usd.Stage` / `Usd.Prim` return after composition |
| Authored view | What this *one layer* actually contains (`Sdf`) |
| Spec | An Sdf object for a prim, attribute, or relationship in one layer |
| Change block | Batches Sdf edits so USD recomposes once (Obj 6.1) |

---

## 8.1 Composed view vs authored view

### 1. What is it?

**Usd** answers "what is true on the stage after composition?" **Sdf** answers "what did this layer write?"

### 2. Why do we need it?

Debugging (Obj 1.8, 6.2) is almost always "the composed value is X; which layer authored it?" You cannot answer that with `attr.Get()` alone.

### 3. Beginner explanation

Usd is the finished newspaper. Sdf is one reporter's notebook.

Where the analogy breaks: you often *write* through Usd, which then fills in an Sdf spec on the edit-target layer.

### 4. Technical explanation

| Question | API |
|----------|-----|
| Composed radius? | `UsdGeom.Sphere(prim).GetRadiusAttr().Get()` |
| Did *this* layer author radius? | `layer.GetAttributeAtPath("/Ball.radius")` or `primSpec.attributes.get("radius")` |
| Which specs contribute? | `prim.GetPrimStack()`, `attr.GetPropertyStack()` (Ch 22) |

`stage.GetPrimAtPath` may return a valid composed prim even when the **root layer** has only an `over` — the `def` lives in a sublayer or reference.

### 5. Mental model

```text
Usd.Prim / Usd.Attribute   -->  composed
Sdf.PrimSpec / AttributeSpec --> one layer
```

### 6. Simple example

Session says radius=99. Root says 1. `Get()` → 99. Root's AttributeSpec.default → 1.

### 7. USDA example

*Root layer (no radius):*

```usda
#usda 1.0
(
    subLayers = [
        @geo.usda@
    ]
)
```

*geo.usda:*

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 2
}
```

Usd: radius 2. Sdf on the root: no `/Ball` spec at all.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom

weak = Sdf.Layer.CreateAnonymous("geo.usda")
root = Sdf.Layer.CreateAnonymous("root.usda")
weak.ImportFromString(
    '#usda 1.0\n'
    'def Sphere "Ball" {\n'
    '    double radius = 2\n'
    '}\n'
)
root.subLayerPaths = [weak.identifier]
stage = Usd.Stage.Open(root)
prim = stage.GetPrimAtPath("/Ball")
print("composed radius:", prim.GetAttribute("radius").Get())
print("root has /Ball spec:", bool(root.GetPrimAtPath("/Ball")))
print("weak has /Ball spec:", bool(weak.GetPrimAtPath("/Ball")))
print("weak default:", weak.GetAttributeAtPath("/Ball.radius").default)
```

**Expected output**

```text
composed radius: 2.0
root has /Ball spec: False
weak has /Ball spec: True
weak default: 2.0
```

### 9. Real-world use case

A lighting TD sees a red tint on a hero. Composed `displayColor` is red. Sdf on the lighting layer has no such opinion — the color comes from a referenced look file.

### 10. Common mistakes

> [!MISTAKE] Calling `rootLayer.ExportToString()` and concluding a prim "does not exist" because the root is empty. Open the composed stage.

### 11. Exam traps

> [!TRAP] "Usd and Sdf are two names for the same API." Different questions, different objects.

### 12. Practice questions

**DM-001** · Obj 5.4 · Difficulty: Medium · Type: Single choice

`attr.Get()` returns the value from:

A. The root layer only  
B. The composed stage after strength is applied  
C. Always the session layer  
D. Disk mtime of the files  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Usd = composed. Sdf = this layer.
> - Empty root ≠ empty stage.

---

## 8.2 Specs: PrimSpec, AttributeSpec, RelationshipSpec

### 1. What is it?

A **spec** is the Sdf object for one prim or property **in one layer**.

### 2. Why do we need it?

Authoring at Sdf speed, and debugging "is this opinion even in this file?"

### 3. Beginner explanation

If the layer is a document, a spec is one paragraph: one prim or one property as written there.

### 4. Technical explanation

- `Sdf.PrimSpec`, `Sdf.AttributeSpec`, `Sdf.RelationshipSpec`.
- `layer.GetPrimAtPath("/World/Ball")` → PrimSpec or None.
- `primSpec.attributes["radius"].default`
- `prim.GetPrimStack()` → list of PrimSpecs, strongest first.
- Specifiers, typeName, nameChildren live on PrimSpec.

### 5. Mental model

Stage prim → stack of PrimSpecs (one per contributing layer).

### 6. Simple example

`GetPrimStack()` on `/Ball` with a session override: two specs (session over, then def).

### 7. USDA example

The spec for `radius` is this line inside this file only:

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 2
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/Ball").GetRadiusAttr().Set(2.0)
prim = stage.GetPrimAtPath("/Ball")
specs = prim.GetPrimStack()
print("stack count:", len(specs), "type:", type(specs[0]).__name__)
spec = specs[0]
print("typeName:", spec.typeName, "specifier:", spec.specifier)
print("radius default:", spec.attributes["radius"].default)
```

**Expected output**

```text
stack count: 1 type: PrimSpec
typeName: Sphere specifier: Sdf.SpecifierDef
radius default: 2.0
```

### 9. Real-world use case

A "strip unpublished opinions" tool walks specs on the working layer and clears properties not on the allow-list.

### 10. Common mistakes

> [!MISTAKE] Holding a PrimSpec after the layer is reloaded — specs are layer objects; reload invalidates them.

### 11. Exam traps

> [!TRAP] `GetPrimAtPath` on a **layer** vs a **stage**. Layer: spec or None. Stage: Usd.Prim (maybe invalid).

### 12. Practice questions

**DM-002** · Difficulty: Medium · Type: Single choice

`stage.GetPrimAtPath("/A")` vs `layer.GetPrimAtPath("/A")` return:

A. The same Python type  
B. `Usd.Prim` vs `Sdf.PrimSpec` (or None)  
C. Both always None  
D. Both `Sdf.Path`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Specs are per-layer. `GetPrimStack` lists them.
> - Layer GetPrimAtPath ≠ Stage GetPrimAtPath.

---

## 8.3 Sdf.Path operations

### 1. What is it?

`Sdf.Path` is the shared address type for Usd and Sdf. Sdf APIs often *require* it.

### 2. Why do we need it?

String paths work in many Usd APIs. Sdf is pickier. Property paths must use `.`.

### 3. Beginner explanation

Same addresses as Chapter 4, now used to index a layer like a dictionary.

### 4. Technical explanation

- `Sdf.Path("/Ball.radius")` for `GetAttributeAtPath`.
- `path.IsPrimPath()`, `IsPropertyPath()`, `AppendProperty`, `GetParentPath`.
- Relative paths exist (`../Other`) — more important with references (Ch 16).

### 5. Mental model

Path in, spec out.

### 6. Simple example

`layer.GetAttributeAtPath("/Ball.radius")` — note the dot.

### 7. USDA example

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 2
}
```

The attribute path is `/Ball.radius`.

### 8. Python example

```python
from pxr import Sdf

p = Sdf.Path("/World/Ball")
a = p.AppendProperty("radius")
print(a.IsPropertyPath(), a.GetPrimPath(), a.name)
print("join child:", Sdf.Path("/World").AppendChild("Ball"))
```

**Expected output**

```text
True /World/Ball radius
join child: /World/Ball
```

### 9. Real-world use case

A binding validator collects relationship targets as `Sdf.Path`s and checks each `IsPrimPath()`.

### 10. Common mistakes

> [!MISTAKE] `GetAttributeAtPath("/Ball/radius")` — slash is a child prim, not an attribute.

### 11. Exam traps

> [!TRAP] Mixing `Sdf.Path("/World")` with the string `"World"` for `defaultPrim`. defaultPrim is a **name**.

### 12. Practice questions

**DM-003** · Difficulty: Easy · Type: Single choice

The Sdf path for attribute `points` on `/Geo/Mesh` is:

A. `/Geo/Mesh/points`  
B. `/Geo/Mesh.points`  
C. `points:/Geo/Mesh`  
D. `@/Geo/Mesh@`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Property paths use a dot. Sdf lookups use `Sdf.Path`.

---

## 8.4 Authoring with Sdf for speed

### 1. What is it?

Creating PrimSpecs / AttributeSpecs directly on a layer instead of `UsdGeom.Xform.Define` in a loop.

### 2. Why do we need it?

Massive procedural scenes: USD must recompose on each Usd edit unless you batch. Sdf authoring plus a change block is the usual fast path (Obj 6.1).

### 3. Beginner explanation

Usd.Define is "type this in the UI". Sdf specs are "write the database rows, then refresh once".

### 4. Technical explanation

- `Sdf.PrimSpec(layer, name, specifier, typeName)` for a **root** prim.
- Nested: `Sdf.PrimSpec(parentSpec, name, specifier, typeName)`.
- Then `Sdf.AttributeSpec(primSpec, "radius", Sdf.ValueTypeNames.Double)` and set `.default`.
- After Sdf edits, the stage sees them; with ChangeBlock, notification is deferred.

Verified: 200 Xforms via `UsdGeom.Xform.Define` vs `Sdf.PrimSpec` + `ChangeBlock` — Sdf path was several times faster in this environment (micro-benchmark, not a promise of a specific ratio).

### 5. Mental model

Loop in Sdf → one composition update.

### 6. Simple example

A point-cloud importer creates 50,000 parent Xforms: use Sdf.

### 7. USDA example

The result still looks like ordinary USDA:

```usda
#usda 1.0

def Xform "Y0" {}
def Xform "Y1" {}
```

### 8. Python example

```python
from pxr import Usd, Sdf

stage = Usd.Stage.CreateInMemory()
layer = stage.GetRootLayer()
with Sdf.ChangeBlock():
    for i in range(3):
        Sdf.PrimSpec(layer, f"Y{i}", Sdf.SpecifierDef, "Xform")
print([str(p.GetPath()) for p in stage.Traverse()])
```

**Expected output**

```text
['/Y0', '/Y1', '/Y2']
```

### 9. Real-world use case

DCC exporters that previously took minutes drop to seconds after moving the inner loop to Sdf + ChangeBlock (Obj 6.1).

### 10. Common mistakes

> [!MISTAKE] Mixing Usd.Define and Sdf edits on the same prims without understanding edit targets — you can double-author or miss the layer you meant.

### 11. Exam traps

> [!TRAP] "Sdf authoring skips composition rules." It authors into a layer; composition still applies when you query Usd.

### 12. Practice questions

**DBG-PRE-001** · Obj 6.1 · Difficulty: Medium · Type: Single choice

Creating 100,000 prims with Usd.Define in a tight loop is slow mainly because:

A. USDA cannot store that many prims  
B. Each edit can trigger composition/notification work  
C. Python cannot loop to 100,000  
D. Kind metadata is mandatory  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Heavy procedural authoring: Sdf specs + ChangeBlock.
> - Query still through Usd when you need composed values.

---

## 8.5 Sdf.ChangeBlock (intro)

### 1. What is it?

`Sdf.ChangeBlock` is a context manager (and C++ RAII object) that **batches** scene-description changes so listeners (the stage) update once.

### 2. Why do we need it?

Obj 6.1: identify when ChangeBlocks alleviate bottlenecks. Answer: **many small Sdf/Usd edits** that would otherwise each cause indexing work.

### 3. Beginner explanation

Instead of ringing the doorbell for every grocery bag, carry all the bags in, then ring once.

Where the analogy breaks: nested ChangeBlocks are reference-counted; the flush happens when the outermost block ends.

### 4. Technical explanation

```{.python .norun}
with Sdf.ChangeBlock():
    # many spec edits
    pass
```

- Use around Sdf authoring loops and some Usd loops.
- Do not do slow I/O or user interaction inside the block while the stage is "stale".
- Notices (`Usd.Notice`, Ch 34) fire after the block.

### 5. Mental model

ChangeBlock = pause notifications; resume and catch up at the end.

### 6. Simple example

See §8.4's loop.

### 7. USDA example

ChangeBlock does not appear in USDA. It is runtime only.

```usda
#usda 1.0
def Xform "Hint" {}
```

### 8. Python example

```python
from pxr import Usd, Sdf

stage = Usd.Stage.CreateInMemory()
layer = stage.GetRootLayer()
with Sdf.ChangeBlock():
    Sdf.PrimSpec(layer, "A", Sdf.SpecifierDef, "Xform")
    Sdf.PrimSpec(layer, "B", Sdf.SpecifierDef, "Xform")
print("after block:", [str(p.GetName()) for p in stage.Traverse()])
```

**Expected output**

```text
after block: ['A', 'B']
```

### 9. Real-world use case

A variant switcher that writes hundreds of overs: wrap in ChangeBlock or the UI freezes (Ch 44).

### 10. Common mistakes

> [!MISTAKE] Querying the stage in the middle of a huge block and assuming it already shows every spec. Wait until the block exits for a consistent view.

### 11. Exam traps

> [!TRAP] "ChangeBlock makes disk writes faster." It batches **in-memory composition notifications**, not fsync.

### 12. Practice questions

**DBG-PRE-002** · Obj 6.1 · Difficulty: Medium · Type: Single choice

When is `Sdf.ChangeBlock` the right tool?

A. Once, around opening a stage  
B. Around a burst of many scene-description edits  
C. Instead of USDC  
D. To compress USDZ  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - ChangeBlock = batch edits, one update (Obj 6.1).
> - It does not change composition strength rules.

---

## Chapter lab(s)

Lab 09 (Sdf specs & ChangeBlock) matches this chapter.

## USDA reading exercise

**USDA-09.** Root has no prims, only `subLayers = [@geo.usda@]`. `geo.usda` defs `/Ball`. Does `root.GetPrimAtPath("/Ball")` succeed? Does `stage.GetPrimAtPath("/Ball").IsValid()`?

**Answer:** Root Sdf lookup fails (None/false). Stage prim is valid.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Get() vs layer text disagree | Composed vs authored |
| Slow Define loop | ChangeBlock + Sdf |
| GetPrimAtPath | Which object — stage or layer? |

### Chapter questions

**Q1.** Usd vs Sdf in one sentence each?  
**Q2.** What does GetPrimStack return?  
**Q3.** Attribute path punctuation?  
**Q4.** Obj 6.1 in one sentence?  
**Q5.** Does ChangeBlock skip LIVERPS?  
**Q6.** Why can the root layer look empty?

**Answers**

1. Usd composed; Sdf authored-in-this-layer. 2. PrimSpecs, strongest first. 3. Dot. 4. Batch edits to avoid per-edit composition cost. 5. No. 6. Opinions live in sublayers/references.

## Further reading

- Sdf: Scene Description Foundations — OpenUSD API  
- `SdfChangeBlock` (study guide API list)  
- Tutorial: Inspecting and Authoring Properties  
