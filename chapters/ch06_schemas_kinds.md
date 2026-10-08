# Chapter 6 — Schemas and Model Kinds

> **Exam domain:** Customizing USD (6%) and Data Modeling · **Objectives:** 3.3, 3.4 (intro; custom schemas in Ch 37)
> **Study day:** 2 · **Est. time:** 75 min
> **Prerequisites:** Chapter 5

## Learning goals

- Explain what a **schema** is and why USD uses them.
- Distinguish **typed (IsA) schemas** from **API schemas**.
- Distinguish **single-apply** vs **multiple-apply** API schemas.
- Name the built-in schema domains you must know for the exam.
- Use **model kinds**: model, group, assembly, component, subcomponent.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Schema | A contract: prim type or API that defines properties and meaning |
| Typed / IsA schema | Gives the prim its type name (`Mesh`, `Sphere`); `prim.IsA(...)` |
| API schema | Extra bundle of properties applied onto a prim (`HasAPI`) |
| Single-apply | At most one application per prim (`MaterialBindingAPI`) |
| Multiple-apply | Named instances (`CollectionAPI:include`) |
| Kind | Extensible category for the **model hierarchy** (`component`, `assembly`, …) |

---

## 6.1 What a schema is

### 1. What is it?

A **schema** is a named contract that says "this prim has these properties and this meaning." `UsdGeom.Mesh` is a schema. So is `UsdShade.MaterialBindingAPI`.

### 2. Why do we need it?

Without schemas, every tool would invent its own `points` vs `P` vs `vertices`. Schemas are how OpenUSD stays a *standard* (Obj 3.4, 3.6).

### 3. Beginner explanation

A schema is a form template. "Mesh form" always has `points` and `faceVertexIndices`. Tools can fill the form without a meeting.

Where the analogy breaks: applying an API schema is like stapling a second form onto the first (material binding on a mesh).

### 4. Technical explanation

- Schemas are generated from a `schema.usda` (Ch 37) into C++/Python classes.
- **IsA / typed schemas** inherit `UsdTyped`. They set `typeName`.
- **API schemas** inherit `UsdAPISchemaBase`. They do not change `typeName`; they add `apiSchemas` metadata.
- Fallback values, doc strings, and property types all come from the schema.

### 5. Mental model

Type name = which IsA schema. `apiSchemas` list = extra API schemas.

### 6. Simple example

`def Mesh "Body"` means IsA schema `Mesh`. Adding `prepend apiSchemas = ["MaterialBindingAPI"]` applies the binding API.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body" (
    prepend apiSchemas = ["MaterialBindingAPI"]
)
{
    rel material:binding = </Looks/Red>
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Body")
prim = mesh.GetPrim()
print("typeName:", prim.GetTypeName())
print("IsA Mesh:", prim.IsA(UsdGeom.Mesh))
print("HasAPI before:", prim.HasAPI(UsdShade.MaterialBindingAPI))
UsdShade.MaterialBindingAPI.Apply(prim)
print("HasAPI after:", prim.HasAPI(UsdShade.MaterialBindingAPI))
print("applied:", prim.GetAppliedSchemas())
```

**Expected output**

```text
typeName: Mesh
IsA Mesh: True
HasAPI before: False
HasAPI after: True
applied: ['MaterialBindingAPI']
```

### 9. Real-world use case

A CAD importer can put extra bolts-and-threads data on an API schema instead of inventing a rival Mesh type (Obj 3.6).

### 10. Common mistakes

> [!MISTAKE] Authoring `rel material:binding` without applying `MaterialBindingAPI`. Validators and `ComputeBoundMaterial` expect the API applied (Ch 40).

### 11. Exam traps

> [!TRAP] "API schemas change the prim's typeName to MaterialBindingAPI." They do not. Type stays `Mesh`.

### 12. Practice questions

**CUST-PRE-001** · Difficulty: Easy · Type: Single choice

An API schema:

A. Replaces the prim's type name  
B. Adds a bundle of properties/behavior without changing typeName  
C. Is the same as a layer  
D. Can only live on class prims  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Schema = contract. IsA changes typeName; API schemas append to `apiSchemas`.

---

## 6.2 Typed (IsA) schemas

### 1. What is it?

A **typed schema** (IsA schema) is the prim's type: `Xform`, `Mesh`, `Camera`, `Material`. Query with `prim.IsA(UsdGeom.Mesh)`.

### 2. Why do we need it?

Traversal filters ("all meshes") and schema APIs (`UsdGeom.Mesh(prim).GetPointsAttr()`) depend on IsA, including **inherited** types (`Mesh` is a `Gprim` is a `Boundable` is an `Xformable` is `Imageable`).

### 3. Beginner explanation

IsA is the "this *is a* mesh" test, and it understands parent classes: a Mesh *is a* Gprim.

### 4. Technical explanation

Verified: `UsdGeom.Mesh` IsA `Gprim`, `Boundable`, `Xformable`, `Imageable`.

Python: `prim.IsA(UsdGeom.Gprim)`.

You cannot apply two typed schemas as the type name; a prim has one type (composition may still provide it from a weaker layer).

### 5. Mental model

```text
Imageable
  Xformable
    Boundable
      Gprim
        Mesh, Sphere, Cube, ...
    Camera (xformable, not a gprim)
  Scope (imageable, not xformable in the same way — see Ch 13)
```

(Exact inheritance is Ch 13. Remember Mesh → Gprim → Boundable for extents.)

### 6. Simple example

A bounding-box tool asks `IsA(UsdGeom.Boundable)` rather than listing every gprim type.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body" {}
def Sphere "Ball" {}
def Camera "ShotCam" {}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Body").GetPrim()
print("Mesh:", mesh.IsA(UsdGeom.Mesh))
print("Gprim:", mesh.IsA(UsdGeom.Gprim))
print("Boundable:", mesh.IsA(UsdGeom.Boundable))
print("Xformable:", mesh.IsA(UsdGeom.Xformable))
print("Imageable:", mesh.IsA(UsdGeom.Imageable))
print("Sphere?:", mesh.IsA(UsdGeom.Sphere))
```

**Expected output**

```text
Mesh: True
Gprim: True
Boundable: True
Xformable: True
Imageable: True
Sphere?: False
```

### 9. Real-world use case

Extent computation (Obj 5.6) only makes sense on Boundables (Ch 13).

### 10. Common mistakes

> [!MISTAKE] Wrapping `UsdGeom.Sphere(prim)` without `IsA` — silent nonsense on the wrong type.

### 11. Exam traps

> [!TRAP] "Camera is a Gprim." Cameras are Xformable/Imageable, not polygonal Gprims.

### 12. Practice questions

**DM-PRE-006** · Difficulty: Medium · Type: Single choice

`UsdGeom.Mesh` is a `UsdGeom.Gprim`. True or false?

A. True  
B. False — only Sphere is a Gprim  
C. True only after applying an API  
D. False — Mesh is only Imageable  

**Answer:** A.

### 13. Exam takeaways

> [!KEY]
> - `IsA` walks the typed-schema inheritance.
> - One type name per prim.

---

## 6.3 API schemas: single-apply vs multiple-apply

### 1. What is it?

**API schemas** add optional capabilities. **Single-apply**: one per prim (`MaterialBindingAPI`). **Multiple-apply**: many, each with an instance name (`CollectionAPI:include`).

### 2. Why do we need it?

Obj 3.4: custom APIs are how you extend prims. A typical “add physics-like properties to existing geometry” schema subclasses **`UsdAPISchemaBase`**, not `UsdTyped`.

### 3. Beginner explanation

Single-apply = one "Material Binding" stamp on the mesh. Multiple-apply = many named "Collection" stamps (`include`, `exclude`).

### 4. Technical explanation

- Apply: `UsdShade.MaterialBindingAPI.Apply(prim)` → `apiSchemas` includes `MaterialBindingAPI`.
- Multiple-apply: `Usd.CollectionAPI.Apply(prim, "include")` → `CollectionAPI:include`.
- Query: `prim.HasAPI(UsdShade.MaterialBindingAPI)`, `GetAppliedSchemas()`.
- Custom APIs you write later inherit `UsdAPISchemaBase` (Ch 37). Typed custom schemas inherit `UsdTyped`.

### 5. Mental model

```text
typeName: Mesh
apiSchemas: [MaterialBindingAPI, CollectionAPI:include]
```

### 6. Simple example

Collections for light linking use multiple-apply CollectionAPI with names per collection.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body" (
    prepend apiSchemas = ["MaterialBindingAPI", "CollectionAPI:include"]
)
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Mesh.Define(stage, "/Body").GetPrim()
UsdShade.MaterialBindingAPI.Apply(prim)
Usd.CollectionAPI.Apply(prim, "include")
print(prim.GetAppliedSchemas())
print("Has MaterialBindingAPI:", prim.HasAPI(UsdShade.MaterialBindingAPI))
```

**Expected output**

```text
['MaterialBindingAPI', 'CollectionAPI:include']
Has MaterialBindingAPI: True
```

### 9. Real-world use case

A studio's `StudioPublishAPI` (single-apply) adds `studio:assetId`. Multiple shots still share `Mesh`.

### 10. Common mistakes

> [!MISTAKE] Applying CollectionAPI without an instance name. Multiple-apply requires the name.

### 11. Exam traps

> [!TRAP] Custom *physics properties on existing geometry* → API schema (`UsdAPISchemaBase`), not a new typed Mesh subclass. (Original question; same idea as the study-guide sample, not a copy.)

### 12. Practice questions

**CUST-PRE-002** · Difficulty: Medium · Type: Single choice

You want to add studio tracking fields to many existing Mesh prims. The usual schema kind is:

A. A new typed schema replacing Mesh  
B. A single-apply API schema  
C. A new file format  
D. A Hydra scene index only  

**CUST-PRE-003** · Difficulty: Medium · Type: Single choice

`CollectionAPI:include` is:

A. A typed schema typeName  
B. A multiple-apply API instance named `include`  
C. A layer metadata field  
D. Invalid USDA  

**Answers**

**CUST-PRE-002 — Answer: B.** Obj 3.4 / 3.6.

**CUST-PRE-003 — Answer: B.**

### 13. Exam takeaways

> [!KEY]
> - Single-apply vs multiple-apply (named instances).
> - Extra properties on existing types → API schema.
> - New stand-alone prim types → typed / IsA schema.

---

## 6.4 Built-in schema domains

### 1. What is it?

**Schema domains** are modules of related schemas: **UsdGeom**, **UsdShade**, **UsdLux**, **UsdPhysics**, **UsdSkel**, plus others (`UsdMedia`, `UsdVol`, `UsdUI`, …).

### 2. Why do we need it?

Visualization (8%) tests UsdGeom, UsdShade, UsdLux. Physics appears in the study-guide reading list. You must know which domain to import.

### 3. Beginner explanation

Geom = shape and transform. Shade = materials. Lux = lights. Physics = simulation. Skel = skeletons / blend shapes.

### 4. Technical explanation

| Domain | Typical types | Exam |
|--------|---------------|------|
| UsdGeom | Xform, Scope, Mesh, Sphere, Camera, PointInstancer, PrimvarsAPI | Heavy (Ch 39, 25) |
| UsdShade | Material, Shader, NodeGraph, MaterialBindingAPI | Ch 40 |
| UsdLux | DistantLight, RectLight, DomeLight, LightAPI | Ch 41 |
| UsdPhysics | Rigid bodies, joints (overview) | Pipeline reading list |
| UsdSkel | Skeleton, BlendShape | Awareness |

`usd-core` 26.08 includes these Python modules (no UsdMtlx, no UsdImaging).

### 5. Mental model

Import the domain you mean: `from pxr import UsdGeom, UsdShade, UsdLux`.

### 6. Simple example

A light is not a Mesh. `UsdLux.DistantLight.Define(stage, "/Lights/Key")`.

### 7. USDA example

```usda
#usda 1.0

def DistantLight "Key"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade, UsdLux, UsdPhysics, UsdSkel

stage = Usd.Stage.CreateInMemory()
print("Mesh", UsdGeom.Mesh.Define(stage, "/M").GetPrim().GetTypeName())
print("Material", UsdShade.Material.Define(stage, "/Mat").GetPrim().GetTypeName())
print("DistantLight", UsdLux.DistantLight.Define(stage, "/L").GetPrim().GetTypeName())
print("modules", UsdPhysics is not None, UsdSkel is not None)
```

**Expected output**

```text
Mesh Mesh
Material Material
DistantLight DistantLight
modules True True
```

### 9. Real-world use case

A game exporter writes UsdGeom + UsdShade + a custom physics API, not a private "GameMesh" type, so usdview can still draw it.

### 10. Common mistakes

> [!MISTAKE] Putting lights under `UsdGeom` because they are "in the scene". Use UsdLux.

### 11. Exam traps

> [!TRAP] Visualization questions naming UsdGeom/UsdShade/UsdLux specifically — do not answer with Sdf layer APIs.

### 12. Practice questions

**VIS-PRE-001** · Difficulty: Easy · Type: Single choice

Lights in OpenUSD are primarily schemas in:

A. UsdGeom  
B. UsdLux  
C. UsdShade  
D. Kind  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Geom / Shade / Lux are the visualization trio.
> - Physics and Skel exist; know they are domains.

---

## 6.5 Model kinds

### 1. What is it?

**Kind** is metadata that places a prim in the **model hierarchy**: a shallow table of contents for the stage. Core kinds: `model`, `group`, `assembly`, `component`, plus `subcomponent` (not a model).

### 2. Why do we need it?

Obj 3.3: custom kinds when appropriate. Obj 2.4 / 7.2: asset structure. Traversal and instancing tools prune at **component** boundaries.

### 3. Beginner explanation

If the prim tree is every screw, the model hierarchy is the furniture: this is a *chair component*, this is a *room assembly*.

Where the analogy breaks: `subcomponent` is a kind for pieces **inside** a component (a lid, a wheel). It is **not** a model. Verified: `Kind.Registry.IsA("subcomponent", "model")` is False.

### 4. Technical explanation

Verified on USD 26.08 (`Kind.Tokens`): `model`, `group`, `assembly`, `component`, `subcomponent`.

| Kind | IsA group? | IsA model? | Role |
|------|------------|------------|------|
| model | | yes | Base category |
| group | yes | yes | Organizational model |
| assembly | yes (hence model) | yes | Aggregates other models |
| component | | yes | Leaf publishable asset ("the chair") |
| subcomponent | | **no** | Piece inside a component |

Python: `Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)`, `prim.IsModel()`, `prim.IsGroup()`, `Kind.Registry.IsA("component", "model")`.

Rule of thumb from asset-structure docs: keep the model hierarchy **shallow**. A Gprim tagged `component` is a smell (too deep).

### 5. Mental model

```text
assembly  (set / shot)
  group
    component  (chair)     <-- prune point
      subcomponent (seat)
      Mesh                 <-- not a model
```

### 6. Simple example

Publish `Chair` as `component`. The shot references many chairs into an `assembly` named `Set`.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    kind = "component"
)
{
    def Mesh "Seat" (
        kind = "subcomponent"
    )
    {
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Kind

stage = Usd.Stage.CreateInMemory()
chair = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
Usd.ModelAPI(chair).SetKind(Kind.Tokens.component)
seat = UsdGeom.Mesh.Define(stage, "/Chair/Seat").GetPrim()
Usd.ModelAPI(seat).SetKind(Kind.Tokens.subcomponent)
print("component is model:", Kind.Registry.IsA("component", "model"))
print("assembly is group:", Kind.Registry.IsA("assembly", "group"))
print("subcomponent is model:", Kind.Registry.IsA("subcomponent", "model"))
print("chair IsModel/IsGroup:", chair.IsModel(), chair.IsGroup())
print("seat IsModel:", seat.IsModel())
```

**Expected output**

```text
component is model: True
assembly is group: True
subcomponent is model: False
chair IsModel/IsGroup: True False
seat IsModel: False
```

### 9. Real-world use case

Payload unloading (Ch 17) often stops at component models so a shot can open as a "table of contents" in under a second (performance guide).

### 10. Common mistakes

> [!MISTAKE] Marking every Mesh a `component`. That deepens the model hierarchy and costs composition time.

> [!MISTAKE] Using `group` as the published asset's root kind. ASWF guidance: groups organize insides of assemblies; published roots are usually `component` or `assembly`.

### 11. Exam traps

> [!TRAP] "subcomponent is a model." It is a kind, but not in the model hierarchy.

> [!TRAP] Kind vs typeName: `kind = "component"` does not make `GetTypeName()` return `component`. Type stays `Xform`.

### 12. Practice questions

**CUST-PRE-004** · Difficulty: Medium · Type: Single choice

Which kind is **not** a model?

A. assembly  
B. component  
C. group  
D. subcomponent  

**CUST-PRE-005** · Difficulty: Medium · Type: Single choice

The usual kind for a publishable chair asset is:

A. subcomponent  
B. component  
C. Mesh  
D. session  

**Answers**

**CUST-PRE-004 — Answer: D.**

**CUST-PRE-005 — Answer: B.**

### 13. Exam takeaways

> [!KEY]
> - Kind is metadata for the model hierarchy, not the prim type.
> - component / assembly / group are models. subcomponent is not.
> - Keep the hierarchy shallow; components are the prune point.

---

## Chapter lab(s)

Lab 31–32 (schemas, kinds) come later. Run this chapter's scripts now.

## USDA reading exercise

**USDA-07.** What is `/Chair`'s typeName vs kind?

```usda
#usda 1.0
def Xform "Chair" ( kind = "component" ) {}
```

**Answer:** typeName `Xform`, kind `component`. Both can be true at once.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| IsA vs HasAPI | Typed schema vs API schema |
| `CollectionAPI:foo` | Multiple-apply instance `foo` |
| Physics fields on Mesh | API schema, not a new Mesh type |
| subcomponent | Inside a component, not a model |
| Kind vs type | Metadata vs typeName |

### Chapter questions

**Q1.** Two families of schemas?  
**Q2.** `IsA` vs `HasAPI`?  
**Q3.** Visualization domains?  
**Q4.** Five core kind tokens?  
**Q5.** Why not mark Gprims as component?  
**Q6.** Base class for a custom API schema (preview of Ch 37)?  
**Q7.** `GetAppliedSchemas()` after CollectionAPI named `include`?  
**Q8.** Does kind change typeName?

**Answers**

1. Typed/IsA and API. 2. Type inheritance vs applied APIs. 3. UsdGeom, UsdShade, UsdLux. 4. model, group, assembly, component, subcomponent. 5. Deep model hierarchy; prune point should be the asset. 6. `UsdAPISchemaBase`. 7. `CollectionAPI:include`. 8. No.

## Further reading

- Kind: Extensible Categorization — OpenUSD API  
- NVIDIA Learn OpenUSD: Understanding Model Kinds  
- ASWF asset structure guidelines (kinds) — https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md  
