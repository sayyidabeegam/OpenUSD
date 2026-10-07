# Chapter 5 — Properties: Attributes, Relationships, Metadata

> **Exam domain:** Data Modeling (13%) · **Objectives:** 5.3, 5.4
> **Study day:** 2 · **Est. time:** 90 min
> **Prerequisites:** Chapter 4

## Learning goals

- Retrieve a prim's properties (Obj 5.4).
- Author **attributes** (value, type, variability).
- Author **relationships** and list their targets.
- Read and write **metadata** on prims, properties, and layers (Obj 5.3 intro).
- Recognize property **namespaces** (`primvars:`, `xformOp:`, `inputs:`).

## Key terms

| Term | One-line definition |
|------|---------------------|
| Property | Either an attribute or a relationship on a prim |
| Attribute | A typed value (possibly time-sampled) |
| Relationship | A pointer to other prims or properties (targets) |
| Metadata | Named data that is not a property (on layer, prim, or property) |
| Variability | `varying` (can have time samples) vs `uniform` (one value) |
| Namespace | The prefix before `:` in a property name |

---

## 5.1 Properties

### 1. What is it?

A **property** is either an **attribute** or a **relationship**. Both live on a prim and have a name.

### 2. Why do we need it?

Obj 5.4: you must retrieve "the properties of a prim" — not only attributes, not only relationships.

### 3. Beginner explanation

If a prim is a form, properties are the fields. Some fields hold numbers (attributes). Some fields hold arrows to other forms (relationships).

### 4. Technical explanation

- `prim.GetPropertyNames()`, `GetProperties()`, `GetAttributes()`, `GetRelationships()`.
- `prim.GetProperty("points")` returns a `Usd.Attribute` or `Usd.Relationship` subclass of `Usd.Property`.
- `isinstance(prop, Usd.Attribute)` / `Usd.Relationship`.
- Schema properties appear even before you author values (`HasAuthoredValue()` may be False).

### 5. Mental model

```text
Usd.Property
   ├── Usd.Attribute     (values)
   └── Usd.Relationship  (targets)
```

### 6. Simple example

A Mesh prim already *has* a `points` attribute from its schema. Until you set it, it has no authored value.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    rel material:binding = </Looks/Red>
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Body")
prim = mesh.GetPrim()
names = prim.GetPropertyNames()
print("has points:", "points" in names)
print("has proxyPrim rel:", "proxyPrim" in names)
print("attribute count:", len(prim.GetAttributes()))
print("relationship count:", len(prim.GetRelationships()))
prop = prim.GetProperty("points")
print("points is Attribute:", isinstance(prop, Usd.Attribute))
print("points HasAuthoredValue:", mesh.GetPointsAttr().HasAuthoredValue())
```

**Expected output**

```text
has points: True
has proxyPrim rel: True
attribute count: 24
relationship count: 1
points is Attribute: True
points HasAuthoredValue: False
```

### 9. Real-world use case

A generic inspector panel lists `GetPropertyNames()` and then branches: if attribute, show value; if relationship, show targets.

### 10. Common mistakes

> [!MISTAKE] Using only `GetAttributes()` when the question says "properties". You will miss relationships.

### 11. Exam traps

> [!TRAP] "Metadata is a property." Metadata is a separate channel (section 5.4).

### 12. Practice questions

**DM-PRE-001** · Difficulty: Easy · Type: Single choice

Which call lists both attributes and relationships?

A. `GetAttributes()` only  
B. `GetPropertyNames()` / `GetProperties()`  
C. `GetChildren()`  
D. `GetLayerStack()`  

**Answer:** B. Obj 5.4.

### 13. Exam takeaways

> [!KEY]
> - Property = attribute or relationship.
> - Schema properties exist before you author values.

---

## 5.2 Attributes

### 1. What is it?

An **attribute** holds a typed value: a float, a `point3f[]`, a token, and so on. It may have a **default** value and/or **time samples** (Ch 10).

### 2. Why do we need it?

Almost all numeric and string scene data is attributes: radius, points, visibility, shader inputs.

### 3. Beginner explanation

An attribute is a labeled cell with a type. `double radius = 2` means "a double named radius whose default is 2".

### 4. Technical explanation

- `attr.Get()` / `Set(value)` for the default (or at a time code, Ch 10).
- `GetTypeName()` returns an `Sdf.ValueTypeName` (`double`, `point3f[]`, …).
- `GetVariability()`: `Sdf.VariabilityVarying` or `Sdf.VariabilityUniform`.
- `IsCustom()`: True for properties you created that are not from a schema.
- `CreateAttribute(name, Sdf.ValueTypeNames.Float)` on a prim.
- Uniform attributes cannot (meaningfully) time-sample; they are "one value for all time".

### 5. Mental model

Attribute = typed value slot. Default vs time samples = Ch 10.

### 6. Simple example

`double radius = 2` on a Sphere is a schema attribute, not custom.

### 7. USDA example

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 2
    custom bool extraFlag = 1
    uniform token purpose = "default"
}
```

`custom` marks a non-schema attribute. `uniform` marks variability.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
ball = UsdGeom.Sphere.Define(stage, "/Ball")
radius = ball.GetRadiusAttr()
print("type:", radius.GetTypeName())
print("variability:", radius.GetVariability())
print("custom:", radius.IsCustom(), "HasAuthoredValue:", radius.HasAuthoredValue())
radius.Set(2.0)
print("value:", radius.Get())
flag = ball.GetPrim().CreateAttribute("extraFlag", Sdf.ValueTypeNames.Bool)
flag.Set(True)
print("extraFlag custom:", flag.IsCustom(), "value:", flag.Get())
```

**Expected output**

```text
type: double
variability: Sdf.VariabilityVarying
custom: False HasAuthoredValue: False
value: 2.0
extraFlag custom: True value: True
```

### 9. Real-world use case

Choosing `float` vs `double` vs `float3` vs `color3f` is Obj 5.2 (Ch 9). Wrong types break shaders and extents.

### 10. Common mistakes

> [!MISTAKE] Calling `Get()` without `Set()` and assuming you always get a useful default. Some schema attributes have fallbacks (`radius` does); others return `None` until authored (`points`).

### 11. Exam traps

> [!TRAP] "All attributes are custom." Schema attributes are not custom.

### 12. Practice questions

**DM-PRE-002** · Difficulty: Medium · Type: Single choice

Before anyone calls `Set` on a Sphere's `radius`, `HasAuthoredValue()` is:

A. True, because schemas always author defaults into the layer  
B. False, until someone authors a value  
C. An error  
D. True only on the session layer  

**Answer:** B. (The composed `Get()` may still return the schema fallback.)

### 13. Exam takeaways

> [!KEY]
> - Attributes are typed; variability is uniform or varying.
> - `HasAuthoredValue` ≠ "Get returned a number".

---

## 5.3 Relationships

### 1. What is it?

A **relationship** stores **targets**: paths to other prims or properties. It does not store a numeric value.

### 2. Why do we need it?

Material bindings, proxy prims, connections, collections — anything that *points* uses a relationship.

### 3. Beginner explanation

A sticky arrow from this prim to that prim.

Where the analogy breaks: a relationship can have **several** targets, and list-editing (prepend/append/delete, Ch 14) applies.

### 4. Technical explanation

- `prim.CreateRelationship("look:material")`
- `rel.AddTarget(path)`, `SetTargets(list)`, `GetTargets()`.
- USDA: `rel material:binding = </Looks/Red>`
- Targets are `Sdf.Path`s. They may be invalid (broken bindings) — USD will still store them.
- `MaterialBindingAPI` must be **applied** before official material binding (Ch 40). You can still create a raw relationship here to learn the type.

### 5. Mental model

Attribute = value. Relationship = list of paths.

### 6. Simple example

`proxyPrim` on imageable prims points at a lighter proxy.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    rel proxyPrim = </BodyProxy>
}

def Mesh "BodyProxy"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
body = UsdGeom.Mesh.Define(stage, "/Body")
proxy = UsdGeom.Mesh.Define(stage, "/BodyProxy")
rel = body.GetPrim().CreateRelationship("look:dest")
rel.AddTarget(proxy.GetPath())
print("is Relationship:", isinstance(rel, Usd.Relationship))
print("targets:", [str(t) for t in rel.GetTargets()])
print("namespace:", rel.GetNamespace(), "baseName:", rel.GetBaseName())
```

**Expected output**

```text
is Relationship: True
targets: ['/BodyProxy']
namespace: look baseName: dest
```

### 9. Real-world use case

A broken `material:binding` that points outside `defaultPrim` is a classic export error (data exchange). The relationship exists; the target is just not part of the asset.

### 10. Common mistakes

> [!MISTAKE] Setting a relationship with `Set(1.0)` like an attribute. Use targets.

### 11. Exam traps

> [!TRAP] "Relationships store the material's color." They store **paths**. Colors live on shader attributes.

### 12. Practice questions

**DM-PRE-003** · Difficulty: Easy · Type: Single choice

A relationship's composed data is:

A. A float  
B. One or more `Sdf.Path` targets  
C. A layer identifier only  
D. A time code  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Relationships point. Attributes value.
> - Always inspect targets when a binding "does nothing".

---

## 5.4 Metadata

### 1. What is it?

**Metadata** is named data on a layer, prim, or property that is **not** a property. Examples: `kind`, `documentation`, `active`, `instanceable`, `defaultPrim`, `hidden`, `customData`.

### 2. Why do we need it?

Obj 5.3 / 7.6: pipelines store non-schema info (shot codes, asset IDs) without pretending it is geometry.

### 3. Beginner explanation

Properties are columns in the table. Metadata is the sticky note on the table, the folder, or the whole file.

Where the analogy breaks: some things that *look* like properties in USDA (`active = false` in parentheses) are metadata.

### 4. Technical explanation

- Prim metadata sits in parentheses in USDA: `def Xform "W" ( kind = "component" )`.
- Layer metadata sits in the header block.
- `prim.GetMetadata("kind")`, `SetMetadata("documentation", "...")`.
- **Registered** metadata has a known name and type. **Custom** extra dictionaries: `customData` and `assetInfo`.
- `SetCustomDataByKey("shot", "s001")` / `GetCustomData()`.
- `Usd.ModelAPI(prim).SetKind(...)` is the kind-aware API (Ch 6).

> [!VERSION] Schema prims may already contain documentation inside `customData` (`userDocBrief`). Merging your keys keeps those entries. Verified on USD 26.08 for `UsdGeom.Mesh`.

### 5. Mental model

Header / parentheses = metadata. Body with `type name = value` = properties.

### 6. Simple example

`kind = "component"` does not render. It tells asset tools "this is a publishable asset".

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    doc = "Hero chair v12"
)

def Xform "Chair" (
    kind = "component"
    customData = {
        string shot = "s001"
    }
)
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Kind

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
prim.SetMetadata("documentation", "Hero chair")
Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
prim.SetCustomDataByKey("shot", "s001")
print("documentation:", prim.GetMetadata("documentation"))
print("kind:", Usd.ModelAPI(prim).GetKind())
print("shot key:", prim.GetCustomDataByKey("shot"))
print("IsModel:", prim.IsModel())
```

**Expected output**

```text
documentation: Hero chair
kind: component
shot key: s001
IsModel: True
```

### 9. Real-world use case

A publisher writes `assetInfo` (identifier, version) so a resolver and a database can find the asset (Ch 12, 33).

### 10. Common mistakes

> [!MISTAKE] Creating an attribute named `kind` instead of setting kind metadata. Tools looking at `ModelAPI` will not see it.

### 11. Exam traps

> [!TRAP] "customData is a relationship." It is a metadata dictionary.

### 12. Practice questions

**DM-PRE-004** · Difficulty: Medium · Type: Single choice

How should you tag a prim as a component model?

A. `CreateAttribute("kind", ...)` with value `"component"`  
B. Kind / ModelAPI metadata: `Usd.ModelAPI(prim).SetKind("component")`  
C. A relationship named `kind`  
D. Rename the prim to `component`  

**Answer:** B. Obj 5.3 / 3.3.

### 13. Exam takeaways

> [!KEY]
> - Metadata ≠ properties. Look in USDA parentheses and headers.
> - `customData` / `assetInfo` are the usual extension dictionaries.

---

## 5.5 Property namespaces

### 1. What is it?

A **namespace** is the prefix of a property name before a colon: `primvars:displayColor`, `xformOp:translate`, `inputs:intensity`, `material:binding`.

### 2. Why do we need it?

Namespaces group properties, prevent collisions, and tell APIs which properties they own. Obj 5.1 (primvars) and visualization domains depend on this.

### 3. Beginner explanation

Like `primvars.` folders inside the prim, but the folder name is part of the property name.

Where the analogy breaks: the colon is the official separator. Nested namespaces exist (`primvars:ri:interpolation` in some pipelines).

### 4. Technical explanation

- `prop.GetName()` → full name. `GetNamespace()` → prefix. `GetBaseName()` → last piece.
- `primvars:` — geometric primitive variables (Ch 11).
- `xformOp:` — transform ops; order lives in `xformOpOrder` (Ch 39). Note: `xformOpOrder` itself has an **empty** namespace.
- `inputs:` / `outputs:` — shader and light connectable attributes (UsdLux `inputs:intensity` since USD 21.02).
- `material:binding` — relationship namespace `material`, base name `binding`.

### 5. Mental model

`namespace:baseName` — always split on the last colon for the base name; `GetNamespace()` returns the rest.

### 6. Simple example

`primvars:displayColor` is not a mysterious second color system; it is a primvar named `displayColor`.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    color3f[] primvars:displayColor = [(1, 0, 0)]
    float3 xformOp:translate = (0, 10, 0)
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Body")
color = mesh.GetPrim().GetProperty("primvars:displayColor")
order = mesh.GetPrim().GetProperty("xformOpOrder")
print("displayColor name:", color.GetName())
print("displayColor namespace:", color.GetNamespace(), "base:", color.GetBaseName())
print("xformOpOrder namespace empty:", order.GetNamespace() == "")
print("xformOpOrder base:", order.GetBaseName())
```

**Expected output**

```text
displayColor name: primvars:displayColor
displayColor namespace: primvars base: displayColor
xformOpOrder namespace empty: True
xformOpOrder base: xformOpOrder
```

### 9. Real-world use case

UsdLux lights use `inputs:intensity` so the intensity can be connected in a shading graph. Old files used a bare `intensity` attribute (VERSION note, Ch 41).

### 10. Common mistakes

> [!MISTAKE] Creating `displayColor` without the `primvars:` prefix and wondering why Hydra ignores it.

### 11. Exam traps

> [!TRAP] "xformOpOrder is namespaced `xformOp`." Its name is literally `xformOpOrder` with no colon.

### 12. Practice questions

**DM-PRE-005** · Difficulty: Medium · Type: Single choice

`primvars:displayColor` has namespace and base name:

A. namespace `displayColor`, base `primvars`  
B. namespace `primvars`, base `displayColor`  
C. no namespace  
D. namespace `primvars:display`, base `Color`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Colons are namespaces. `GetNamespace()` / `GetBaseName()`.
> - Remember `primvars:`, `xformOp:`, `inputs:`, `material:`.
> - `xformOpOrder` has no namespace.

---

## Chapter lab(s)

Labs 06–08 (attributes, relationships, metadata) map here.

## USDA reading exercise

**USDA-06.** How many properties are authored on `Body`, and which is a relationship?

```usda
#usda 1.0
def Mesh "Body" {
    point3f[] points = [(0, 0, 0)]
    rel material:binding = </Looks/Red>
}
```

**Answer:** Two authored properties in the layer: `points` (attribute) and `material:binding` (relationship). The schema still *has* many other unauthored properties.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| "Retrieve properties" | Attributes **and** relationships |
| Parentheses in USDA | Metadata |
| `rel` keyword | Relationship / targets |
| A colon in a property name | Namespace |

### Chapter questions

**Q1.** Two kinds of properties?  
**Q2.** `HasAuthoredValue` vs schema fallback?  
**Q3.** How do you add a relationship target in Python?  
**Q4.** Where does `kind` live?  
**Q5.** Namespace of `primvars:displayColor`?  
**Q6.** Is `xformOpOrder` in namespace `xformOp`?  
**Q7.** Obj 5.4 in one sentence?  
**Q8.** Why `customData` instead of random extra attributes (sometimes)?

**Answers**

1. Attribute, relationship. 2. Authored means written in a layer; Get may still fallback. 3. `AddTarget` / `SetTargets`. 4. Prim metadata (ModelAPI). 5. `primvars`. 6. No. 7. Get a prim's attributes and relationships (and know metadata is separate). 8. Keep pipeline keys out of the geometry schema; tools know to look in `customData`.

## Further reading

- Tutorial: Inspecting and Authoring Properties — OpenUSD tutorials  
- `UsdProperty::GetNamespace` (study guide API list)  
