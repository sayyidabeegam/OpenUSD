# Chapter 4 — Prims and Prim Paths

> **Exam domain:** Data Modeling (13%) · **Objectives:** 5.4
> **Study day:** 2 · **Est. time:** 80 min
> **Prerequisites:** Chapters 2–3

## Learning goals

- Explain what a **prim** is and how **prim paths** address them.
- Choose among specifiers **`def`**, **`over`**, and **`class`**.
- Distinguish typed and typeless prims.
- Activate and deactivate prims, and know what `Traverse()` hides.
- Read a namespace hierarchy.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Prim | A named object on the stage (`Usd.Prim`) |
| Prim path | The address of a prim, like `/World/Ball` (`Sdf.Path`) |
| Specifier | `def`, `over`, or `class` — how this layer introduces the prim |
| Typed prim | A prim with a schema type name (`Sphere`, `Xform`, `Mesh`, …) |
| Typeless prim | A `def` or `over` with no type name |
| Active | Whether the prim participates in default traversal and imaging |
| Namespace | The parent/child tree of prim paths |

---

## 4.1 Prims

### 1. What is it?

A **prim** (primitive) is a named container on the stage. Almost everything you care about — a group, a mesh, a camera, a material — is a prim.

### 2. Why do we need it?

Scenes need a unit of identity. Properties hang off prims. Composition arcs target prims. Paths point at prims.

### 3. Beginner explanation

If a stage is a company org chart, each named box is a prim.

Where the analogy breaks: two files can contribute to the *same* prim. `/World/Ball` is one prim on the stage, assembled from many layers.

### 4. Technical explanation

- `UsdGeom.Xform.Define(stage, "/World")` (and other `Define` methods) create a typed `def`.
- `stage.DefinePrim("/A")` creates a typeless `def`.
- `stage.DefinePrim("/B", "Xform")` creates a typed `def`.
- `prim.GetName()`, `GetPath()`, `GetTypeName()`, `GetPrimStack()` (debug, Ch 22).
- A prim handle can be invalid (`IsValid()`), defined or not (`IsDefined()`), abstract (`IsAbstract()`).

### 5. Mental model

Prim = named node. Path = its address. Type = optional schema.

### 6. Simple example

`/World` is an Xform prim. `/World/Ball` is a Sphere prim. `/World/Ball` cannot exist on the composed stage without some opinion on `/World`.

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
world = UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
prim = ball.GetPrim()
print("name:", prim.GetName())
print("path:", prim.GetPath())
print("type:", prim.GetTypeName())
print("valid:", prim.IsValid(), "defined:", prim.IsDefined())
print("parent:", prim.GetParent().GetName())
```

**Expected output**

```text
name: Ball
path: /World/Ball
type: Sphere
valid: True defined: True
parent: World
```

### 9. Real-world use case

A validator reports "missing prim `/World/Hero/Geo`". That path is the identity everyone in the pipeline shares, even if twenty layers contribute to it.

### 10. Common mistakes

> [!MISTAKE] Creating `/World/Ball` without ever defining `/World`. `Define` on a child will create parent specs as needed, but they may be typeless overs/defs you did not intend. Prefer to define parents explicitly.

### 11. Exam traps

> [!TRAP] "A prim is a mesh." Meshes are one type of prim. Materials, cameras, and empty groups are prims too.

### 12. Practice questions

**FUN-015** · Difficulty: Easy · Type: Single choice

A prim is:

A. Only a polygonal mesh  
B. A named scene object that can hold properties and children  
C. A texture file  
D. A Hydra render pass  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Prim = named node on the stage.
> - One composed prim, many contributing layers.

---

## 4.2 Prim paths

### 1. What is it?

A **prim path** is the prim's address in the namespace tree. In Python it is `Sdf.Path`. In USDA it looks like `/World/Ball`.

### 2. Why do we need it?

Every API that finds, binds, or references something uses a path. Wrong paths are the number-one authoring bug.

### 3. Beginner explanation

A path is like `/home/you/docs` on a filesystem, except the names are prims, not folders. The last name is this prim; everything before it is ancestors.

Where the analogy breaks: property paths exist too: `/World/Ball.radius` (a dot, not a slash).

### 4. Technical explanation

- Absolute prim path: `/World/Ball`. Always starts with `/`.
- Property path: `/World/Ball.radius`.
- `path.name` or `path.GetName()` — last element.
- `path.GetParentPath()`, `GetPrefixes()`, `AppendChild("Ball")`, `AppendProperty("radius")`.
- `IsPrimPath()`, `IsPropertyPath()`, `IsAbsolutePath()`.
- Pseudo-root path is `/`.

Invalid characters in names are a data-exchange topic (`Tf.MakeValidIdentifier`, Ch 28).

### 5. Mental model

```text
/World/Ball.radius
 \____/ \__/ \____/
 prims   name  property
```

### 6. Simple example

Relationship targets and material bindings are paths. If you bind `</Looks/Red>` but the material is `/World/Looks/Red`, the binding is broken (exam data-exchange trap in later chapters).

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        rel proxyPrim = </World/BallProxy>
    }
    def Cube "BallProxy"
    {
    }
}
```

`</World/BallProxy>` is a path in angle brackets — USDA's way of writing an `Sdf.Path` as a value.

### 8. Python example

```python
from pxr import Sdf

prim = Sdf.Path("/World/Ball")
prop = prim.AppendProperty("radius")
print("prim:", prim, "IsPrimPath:", prim.IsPrimPath())
print("prop:", prop, "IsPropertyPath:", prop.IsPropertyPath())
print("prop's prim path:", prop.GetPrimPath())
print("parent:", prim.GetParentPath())
print("prefixes:", [str(p) for p in prim.GetPrefixes()])
print("child:", Sdf.Path("/World").AppendChild("Ball"))
```

**Expected output**

```text
prim: /World/Ball IsPrimPath: True
prop: /World/Ball.radius IsPropertyPath: True
prop's prim path: /World/Ball
parent: /World
prefixes: ['/World', '/World/Ball']
child: /World/Ball
```

### 9. Real-world use case

A compositor's "pick this asset" tool stores `/World/Set/Building_12`, not "the twelfth building", so every department agrees.

### 10. Common mistakes

> [!MISTAKE] Writing `/World/Ball/radius` for an attribute. Attributes use a **dot**: `/World/Ball.radius`.

### 11. Exam traps

> [!TRAP] `defaultPrim` in the header is `"World"` (a name), not `"/World"` (a path).

### 12. Practice questions

**FUN-016** · Difficulty: Easy · Type: Single choice

The path of attribute `radius` on `/World/Ball` is:

A. `/World/Ball/radius`  
B. `/World/Ball.radius`  
C. `World.Ball.radius`  
D. `@radius@`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Prim paths use `/`. Property paths use `.` after the prim.
> - `Sdf.Path` is the type; always prefer it over raw strings in APIs that accept paths.

---

## 4.3 Specifiers: def, over, class

### 1. What is it?

A **specifier** is how a layer introduces a prim: **`def`** (define), **`over`** (overlay), **`class`** (abstract class prim).

### 2. Why do we need it?

Composition needs a way to add new objects (`def`), to add opinions on objects that already exist (`over`), and to store shared templates (`class`). The FAQ question "over vs typeless def" is on NVIDIA's reading list.

### 3. Beginner explanation

- `def` — "this object exists here."
- `over` — "if this object exists, here are extra notes." An `over` alone does **not** make a defined prim on the stage.
- `class` — "this is a template", skipped by default traversal (`IsAbstract()`).

Where the analogy breaks: a stronger `over` still wins **values** over a weaker `def`. Specifiers are about *existence in namespace*, not about value strength (Ch 3.6).

### 4. Technical explanation

Verified on USD 26.08:

| Specifier | USDA | Python | `IsDefined()` if nothing else defines it | In `Traverse()`? |
|----------|------|--------|------------------------------------------|------------------|
| `def` | `def Xform "W"` | `Define` / `DefinePrim` | True | Yes (if active) |
| `over` | `over "W"` | `OverridePrim` | **False** | No |
| `class` | `class "C"` | `CreateClassPrim` | True, and `IsAbstract()` True | **No** |

`OverridePrim("/C/D")` also authors `over "C"` for the parent.

### 5. Mental model

`def` plants a flag. `over` writes on a flag that should already be there. `class` plants a flag in the "templates" drawer.

### 6. Simple example

A shot layer should `over` the referenced character to set a pose, not `def` a second character at the same path (unless you really mean to define it locally).

### 7. USDA example

*File: defs.usda — a `def` and a `class` in one layer*

```usda
#usda 1.0

def Xform "World"
{
}

class "_class_Ball"
{
}
```

*File: overlay.usda — `over` belongs in a different layer; two specs for the same prim in one layer are illegal*

```usda
#usda 1.0

over "World"
{
}
```

### 8. Python example

```python
from pxr import Usd

stage = Usd.Stage.CreateInMemory()
defined = stage.DefinePrim("/A", "Xform")
overlay = stage.OverridePrim("/C/D")
klass = stage.CreateClassPrim("/_Class")
print("A specifier/defined/abstract:", defined.GetSpecifier(), defined.IsDefined(), defined.IsAbstract())
print("D specifier/defined:", overlay.GetSpecifier(), overlay.IsDefined())
print("C specifier/defined:", stage.GetPrimAtPath("/C").GetSpecifier(), stage.GetPrimAtPath("/C").IsDefined())
print("class specifier/defined/abstract:", klass.GetSpecifier(), klass.IsDefined(), klass.IsAbstract())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
print("TraverseAll:", [str(p.GetPath()) for p in stage.TraverseAll()])
```

**Expected output**

```text
A specifier/defined/abstract: Sdf.SpecifierDef True False
D specifier/defined: Sdf.SpecifierOver False
C specifier/defined: Sdf.SpecifierOver False
class specifier/defined/abstract: Sdf.SpecifierClass True True
Traverse: ['/A']
TraverseAll: ['/A', '/C', '/C/D', '/_Class']
```

### 9. Real-world use case

Inherits (Ch 19) point at `class` prims. The class holds default looks; instances `def` their own prims and inherit the class.

### 10. Common mistakes

> [!MISTAKE] Authoring only `over "Hero"` in a layer that is opened *by itself*. The prim is not defined; usdview looks empty. Someone must `def` it (often via a reference).

> [!MISTAKE] Using typeless `def "Hero"` as a "soft" overlay. A typeless `def` **does** define the prim. If you meant overlay, use `over`.

### 11. Exam traps

> [!TRAP] "over is weaker than def." Not for values. Strength is stack/arcs. Specifier is existence.

> [!TRAP] Expecting `class` prims in `Traverse()`. They are abstract.

### 12. Practice questions

**FUN-017** · Difficulty: Medium · Type: Single choice

A layer contains only `over "Ball" { double radius = 2 }`. You open that layer as a stage. What is true?

A. `/Ball` is defined and appears in `Traverse()`  
B. `/Ball` is not defined; `Traverse()` does not visit it  
C. USD errors because `over` is illegal at root  
D. `/Ball` becomes a class prim  

**FUN-018** · Difficulty: Medium · Type: Single choice

What is the specifier designed for shared, abstract templates?

A. `def`  
B. `over`  
C. `class`  
D. `payload`  

**Answers**

**FUN-017 — Answer: B.** Verified: `IsDefined()` is False; `Traverse()` skips it.

**FUN-018 — Answer: C.**

### 13. Exam takeaways

> [!KEY]
> - `def` defines. `over` overlays (not defined by itself). `class` is abstract.
> - Specifier ≠ value strength.
> - Prefer `over` in shot layers that override referenced assets.

---

## 4.4 Typed vs. typeless prims

### 1. What is it?

A **typed** prim has a schema type name (`Xform`, `Sphere`, `Mesh`). A **typeless** prim has an empty type name.

### 2. Why do we need it?

Schemas give you attributes and APIs (`GetRadiusAttr()`). Typeless prims are still valid grouping nodes or placeholders.

### 3. Beginner explanation

Typed = labeled box ("this is a Sphere"). Typeless = unlabeled box (you can still put things in it).

### 4. Technical explanation

- `GetTypeName()` returns `""` when typeless.
- `IsA(UsdGeom.Sphere)` is False for typeless.
- A typeless `def` still `IsDefined()`.
- You can set a type later (`prim.SetTypeName("Xform")`).
- Composition can provide the type from a weaker layer and opinions from a stronger typeless `over`.

### 5. Mental model

Type is just another opinion (a special one). It can come from a different layer than the properties.

### 6. Simple example

Root: `over "Ball" { double radius = 2 }`. Weaker sublayer: `def Sphere "Ball" {}`. Composed: a Sphere with radius 2.

### 7. USDA example

```usda
#usda 1.0

def "Group"
{
    def Sphere "Ball"
    {
    }
}
```

`Group` is typeless; `Ball` is typed.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
group = stage.DefinePrim("/Group")
ball = stage.DefinePrim("/Group/Ball", "Sphere")
print("Group type:", repr(group.GetTypeName()), "IsA Xform:", group.IsA(UsdGeom.Xform))
print("Ball type:", ball.GetTypeName(), "IsA Sphere:", ball.IsA(UsdGeom.Sphere))
```

**Expected output**

```text
Group type: '' IsA Xform: False
Ball type: Sphere IsA Sphere: True
```

### 9. Real-world use case

Some pipelines `def Xform` for every group so tools can transform them. Others leave scope-only groups as `Scope` or typeless. Be consistent (Ch 32).

### 10. Common mistakes

> [!MISTAKE] Calling `UsdGeom.Sphere(typelessPrim).GetRadiusAttr().Set(2)` and assuming it is a sphere. Check `IsA` (or Define through the schema class).

### 11. Exam traps

> [!TRAP] "Typeless prims are illegal." They are legal. The FAQ contrast is over vs *typeless def* — both exist, different existence rules.

### 12. Practice questions

**FUN-019** · Difficulty: Easy · Type: Single choice

`def "Group" {}` is:

A. Illegal USDA  
B. A defined, typeless prim  
C. An abstract class  
D. Automatically an Xform  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Type name is optional; schemas need it.
> - Typeless `def` still defines. Typeless `over` still does not.

---

## 4.5 Active and inactive prims

### 1. What is it?

A prim is **active** by default. **Deactivating** it (`active = false`) removes it from default traversal and typical imaging, without deleting authored data.

### 2. Why do we need it?

Hide a character from a shot, or prune a branch, without destroying the layers that define it. Unlike visibility (Ch 39), inactivity is a namespace-level switch.

### 3. Beginner explanation

Active = on the org chart. Inactive = still in the filing cabinet, not invited to the meeting.

Where the analogy breaks: children of an inactive prim are not visited by `Traverse()` even if they are themselves active.

### 4. Technical explanation

- `prim.IsActive()`, `prim.SetActive(False)`.
- USDA: `def Sphere "Ball" ( active = false ) { }`
- `Traverse()` skips inactive prims. `TraverseAll()` includes them.
- Deactivation is an opinion — a stronger layer can reactivate.

### 5. Mental model

Inactive = pruned from the working set. Data remains.

### 6. Simple example

Layout deactivates `/World/TempBlockout` in a stronger layer so lighting never sees it.

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball" (
        active = false
    )
    {
        double radius = 2
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
print("active:", ball.GetPrim().IsActive())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
ball.GetPrim().SetActive(False)
print("after inactive, Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
print("TraverseAll:", [str(p.GetPath()) for p in stage.TraverseAll()])
```

**Expected output**

```text
active: True
Traverse: ['/World', '/World/Ball']
after inactive, Traverse: ['/World']
TraverseAll: ['/World', '/World/Ball']
```

### 9. Real-world use case

A variant (Ch 18) might deactivate whole geometry branches for a low-LOD choice.

### 10. Common mistakes

> [!MISTAKE] Confusing `active = false` with `visibility = "invisible"`. Visibility is an imageable property; the prim still exists in traversal. Inactivity removes it from `Traverse()`.

### 11. Exam traps

> [!TRAP] "Deactivating deletes the prim from layers." It authors an opinion. Weaker defs remain.

### 12. Practice questions

**FUN-020** · Difficulty: Medium · Type: Single choice

You deactivate `/World/Ball`. `stage.Traverse()` will:

A. Still yield `/World/Ball`  
B. Skip `/World/Ball`  
C. Delete `Ball` from every layer  
D. Raise  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Default: active. `Traverse()` skips inactive; `TraverseAll()` does not.
> - Inactivity ≠ visibility ≠ deletion.

---

## 4.6 Namespace hierarchy

### 1. What is it?

**Namespace** is the tree formed by prim paths. Parents own children. Composition can add children from references under a parent prim.

### 2. Why do we need it?

Transform inheritance, primvar inheritance (Ch 11), material binding (Ch 40), and model hierarchy (Ch 6) all walk ancestors.

### 3. Beginner explanation

Folders in a file browser, but each folder is a prim that can also have properties.

Where the analogy breaks: a referenced asset brings its *internal* tree in under the referencing prim, possibly renaming the root via `defaultPrim`.

### 4. Technical explanation

- `prim.GetChildren()`, `GetParent()`, `GetAllChildren()`.
- Sibling order is the order they were authored (stable enough for tests if you define in order).
- Do not encode variant identity in path names if you can use variant sets (Ch 18); paths that churn break bindings.

### 5. Mental model

```text
/World          Xform
  /Lights       Xform or Scope
    /Key        DistantLight
  /Sets
    /Building
  /Chars
    /Hero
```

### 6. Simple example

Putting materials under `/World/Looks` and meshes under `/World/Geo` is a namespace convention, not a USD requirement — but pipelines depend on conventions (Ch 23).

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def Scope "Geo"
    {
        def Mesh "Body" {}
    }
    def Scope "Looks"
    {
        def Material "Default" {}
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/World")
UsdGeom.Scope.Define(stage, "/World/Geo")
UsdGeom.Mesh.Define(stage, "/World/Geo/Body")
UsdGeom.Scope.Define(stage, "/World/Looks")
UsdShade.Material.Define(stage, "/World/Looks/Default")
world = stage.GetPrimAtPath("/World")
print("children:", [c.GetName() for c in world.GetChildren()])
print("all paths:", [str(p.GetPath()) for p in stage.Traverse()])
```

**Expected output**

```text
children: ['Geo', 'Looks']
all paths: ['/World', '/World/Geo', '/World/Geo/Body', '/World/Looks', '/World/Looks/Default']
```

### 9. Real-world use case

ASWF-style assets put geometry under `geo` and materials under `mtl` (Ch 23). Bindings use paths inside that tree.

### 10. Common mistakes

> [!MISTAKE] Deeply nesting every gprim under extra empty groups "for organization" until model hierarchy becomes expensive (Ch 23, 26).

### 11. Exam traps

> [!TRAP] Assuming USD requires `/World` as the root name. It is a convention. `defaultPrim` is the real entry point.

### 12. Practice questions

**FUN-021** · Difficulty: Easy · Type: Single choice

`prim.GetChildren()` returns:

A. Attributes  
B. Direct child prims  
C. Every descendant  
D. Layers  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Namespace = path tree. Children, parents, ancestors.
> - Conventions (`/World`, `geo`, `mtl`) are pipeline design, not core syntax.
> - `defaultPrim` marks the asset's entry prim.

---

## Chapter lab(s)

Labs 06–07 start properties; prim/path practice is this chapter's examples plus USDA-05.

## USDA reading exercise

**USDA-05.** In this layer, which prims does `Traverse()` visit, and why is `_Class` missing?

```usda
#usda 1.0

def Xform "World" {}
class "_Class" {}
over "Ghost" {}
```

**Answer:** Only `/World`. `_Class` is abstract. `/Ghost` is an `over` and not defined.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `/A/B/C` vs `/A/B.c` | Prim path vs property path |
| Empty usdview on a shot overlay | You used `over` without a `def`/reference |
| Prim missing from Traverse | Inactive, abstract, or undefined |
| `def "Group"` | Typeless defined prim |

### Chapter questions

**Q1.** Python type for paths?  
**Q2.** Three specifiers?  
**Q3.** Does an `over` alone define a prim?  
**Q4.** Does `Traverse()` visit class prims?  
**Q5.** Attribute path punctuation?  
**Q6.** `SetActive(False)` vs deleting the spec?  
**Q7.** `GetPrimAtPath` on a missing path?  
**Q8.** Why define parents explicitly?

**Answers**

1. `Sdf.Path`. 2. def, over, class. 3. No. 4. No. 5. A dot. 6. Authors an opinion; data remains. 7. Invalid prim, no raise. 8. Avoid surprise typeless parent specs.

## Further reading

- Glossary: Prim, Path, Specifier, Active — https://openusd.org/release/glossary.html  
- FAQ: over vs typeless def — https://openusd.org/release/usdfaq.html  
