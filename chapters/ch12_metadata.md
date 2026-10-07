# Chapter 12 — Metadata in Depth

> **Exam domain:** Data Modeling (13%) and Pipeline (14%) · **Objectives:** 5.3, 7.6
> **Study day:** 4 · **Est. time:** 60 min
> **Prerequisites:** Chapter 5

## Learning goals

- Distinguish **registered** metadata from **custom** dictionaries.
- Represent pipeline data in `customData` and `assetInfo` (Obj 5.3, 7.6).
- Use `documentation`, `hidden`, and `kind`.
- List the important **layer** metadata fields.
- Choose metadata vs attributes vs custom schemas.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Registered metadata | Built-in named fields (`kind`, `hidden`, `defaultPrim`, …) |
| `customData` | Dictionary for your keys; not interpreted by core USD |
| `assetInfo` | Dictionary intended for asset identity (identifier, version, …) |
| `hidden` | Metadata hint that UIs should hide this prim |
| Layer metadata | Header fields on the layer / stage |

---

## 12.1 Registered vs. custom metadata

### 1. What is it?

**Registered** metadata has a known name and type in USD. **Custom** extra data usually goes in the `customData` or `assetInfo` dictionaries.

### 2. Why do we need it?

Obj 5.3: represent custom metadata. If you invent a new top-level metadata field, many tools will ignore it unless you register it (advanced). Dictionaries always work.

### 3. Beginner explanation

Registered = printed fields on the government form. customData = the blank "notes" box.

### 4. Technical explanation

- Read/write: `prim.GetMetadata("kind")`, `SetMetadata("documentation", "...")`.
- `HasMetadata`, `HasAuthoredMetadata`.
- Unregistered names may fail or be ignored; use `customData` instead.
- Specifiers' parentheses in USDA hold prim metadata.

### 5. Mental model

Known name → registered API. Anything else → customData/assetInfo.

### 6. Simple example

`kind` is registered. `pipelineShot` is not — put it in customData.

### 7. USDA example

```usda
#usda 1.0

def Xform "Chair" (
    kind = "component"
    documentation = "Hero chair"
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
Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
prim.SetMetadata("documentation", "Hero chair")
print("kind:", prim.GetMetadata("kind"))
print("documentation:", prim.GetMetadata("documentation"))
print("HasAuthored kind:", prim.HasAuthoredMetadata("kind"))
```

**Expected output**

```text
kind: component
documentation: Hero chair
HasAuthored kind: True
```

### 9. Real-world use case

A studio schema might later *register* `studio:show`, but until then customData keeps exporters simple (Obj 7.6).

### 10. Common mistakes

> [!MISTAKE] Creating an attribute named `documentation` instead of metadata. Inspectors looking at metadata miss it.

### 11. Exam traps

> [!TRAP] "All metadata is customData." kind, hidden, instanceable, apiSchemas are registered.

### 12. Practice questions

**DM-025** · Obj 5.3 · Difficulty: Easy · Type: Single choice

`kind` should be stored as:

A. A custom float attribute  
B. Registered prim metadata (ModelAPI)  
C. A relationship  
D. A layer offset  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Registered names vs dictionaries.
> - Obj 5.3: put unknown keys in customData/assetInfo, not random attributes.

---

## 12.2 customData and assetInfo

### 1. What is it?

Two dictionary metadata fields: **customData** (general) and **assetInfo** (asset identity).

### 2. Why do we need it?

Obj 5.3 / 7.6. Resolvers, databases, and publishers look in `assetInfo`. Arbitrary pipeline notes go in `customData`.

### 3. Beginner explanation

assetInfo = the library card (ISBN, edition). customData = sticky notes.

Where the analogy breaks: USD does not enforce that split. Pipelines should.

### 4. Technical explanation

- `SetCustomDataByKey("shot", "s001")` / `GetCustomData()` / `GetCustomDataByKey`.
- `SetAssetInfoByKey("identifier", "chair")` / `GetAssetInfo()`.
- Nested dictionaries are allowed.
- Verified: schema prims may already contain `userDocBrief` inside customData. Read a **key**, do not assume the dict has only your keys.

### 5. Mental model

```text
assetInfo: identifier, name, version, payloadAssetDependencies, ...
customData: anything else
```

### 6. Simple example

Publisher writes `assetInfo.identifier = "props/chair"`. Shot tools never parse the file path for identity.

### 7. USDA example

```usda
#usda 1.0

def Xform "Chair" (
    kind = "component"
    assetInfo = {
        string identifier = "props/chair"
        string name = "chair"
    }
    customData = {
        string shot = "s001"
        string department = "model"
    }
)
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
prim.SetAssetInfoByKey("identifier", "props/chair")
prim.SetCustomDataByKey("shot", "s001")
print("assetInfo:", prim.GetAssetInfo())
print("shot:", prim.GetCustomDataByKey("shot"))
```

**Expected output**

```text
assetInfo: {'identifier': 'props/chair'}
shot: s001
```

### 9. Real-world use case

An asset resolver (Ch 33) keys off `assetInfo.identifier` rather than the current filename so moves on disk do not break identity.

### 10. Common mistakes

> [!MISTAKE] Dumping the entire dict and asserting equality in tests — schema `userDocBrief` will surprise you (Ch 5).

### 11. Exam traps

> [!TRAP] "assetInfo is a relationship to the USDZ." It is metadata on the prim.

### 12. Practice questions

**PIP-PRE-001** · Obj 7.6 · Difficulty: Medium · Type: Single choice

The usual place for an asset's stable identifier string is:

A. `assetInfo`  
B. `xformOpOrder`  
C. `metersPerUnit`  
D. A payload  

**Answer:** A.

### 13. Exam takeaways

> [!KEY]
> - assetInfo = identity. customData = other pipeline keys.
> - Read by key.

---

## 12.3 documentation, hidden, kind

### 1. What is it?

Three registered prim (or property) metadata fields you will see constantly.

### 2. Why do we need it?

documentation for humans; hidden for UIs; kind for the model hierarchy (Ch 6).

### 3. Beginner explanation

documentation = tooltip. hidden = do not show in the outliner. kind = what kind of *asset* this is.

### 4. Technical explanation

- `documentation` — string. Layer also has `doc` in the header (`stage` / layer documentation).
- `hidden` — bool. Hiding is **not** deactivating and **not** `visibility=invisible`.
- `kind` — via `Usd.ModelAPI`.

### 5. Mental model

hidden ≠ inactive ≠ invisible. Three different switches.

### 6. Simple example

A rig's utility bones: `hidden = true`, still active, still computed.

### 7. USDA example

```usda
#usda 1.0

def Xform "RigControls" (
    hidden = true
    documentation = "Do not show to lighting"
)
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/RigControls").GetPrim()
prim.SetMetadata("hidden", True)
prim.SetMetadata("documentation", "Do not show to lighting")
print("hidden:", prim.GetMetadata("hidden"))
print("IsActive:", prim.IsActive())
print("documentation:", prim.GetMetadata("documentation"))
```

**Expected output**

```text
hidden: True
IsActive: True
documentation: Do not show to lighting
```

### 9. Real-world use case

usdview can hide `hidden` prims in the hierarchy while they still contribute.

### 10. Common mistakes

> [!MISTAKE] Using `hidden` to skip expensive geometry. Use payloads, purpose, or deactivation (Ch 17, 39, 4).

### 11. Exam traps

> [!TRAP] "hidden prims are skipped by Traverse()." Traverse skips **inactive** and abstract, not hidden.

### 12. Practice questions

**DM-026** · Difficulty: Medium · Type: Single choice

`hidden = true` means:

A. The prim is inactive  
B. A UI hint; the prim can still be active and defined  
C. The prim's layer is muted  
D. visibility is invisible  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - hidden ≠ active ≠ visibility.
> - kind is ModelAPI metadata, not typeName.

---

## 12.4 Layer metadata

### 1. What is it?

The USDA header `( ... )` fields: `defaultPrim`, `upAxis`, `metersPerUnit`, time range, `subLayers`, `doc`, `startTimeCode`, …

### 2. Why do we need it?

Stage-wide contract. You already set these in Ch 2 and 10. This section is the checklist.

### 3. Beginner explanation

The cover of the book: title, units, which chapter is the start (`defaultPrim`), table of contents (`subLayers`).

### 4. Technical explanation

| Field | Why it matters |
|-------|----------------|
| `defaultPrim` | Referencing without a path (Ch 16) |
| `upAxis` | Y vs Z |
| `metersPerUnit` | No auto-convert |
| `timeCodesPerSecond` / `framesPerSecond` | Time mapping |
| `startTimeCode` / `endTimeCode` | Shot range |
| `subLayers` | Local stack (Ch 3) |
| `doc` | Layer documentation |

`stage.GetMetadata("upAxis")` reads authored stage/root metadata.

### 5. Mental model

Header = layer metadata. Parentheses on a prim = prim metadata.

### 6. Simple example

Every published component header should set defaultPrim, upAxis, metersPerUnit.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    doc = "Hero chair v12"
    metersPerUnit = 0.01
    upAxis = "Y"
    startTimeCode = 1
    endTimeCode = 1
)

def Xform "Chair"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
UsdGeom.SetStageMetersPerUnit(stage, 0.01)
world = UsdGeom.Xform.Define(stage, "/Chair")
stage.SetDefaultPrim(world.GetPrim())
print("defaultPrim:", stage.GetDefaultPrim().GetName())
print("upAxis:", UsdGeom.GetStageUpAxis(stage))
print("metersPerUnit:", UsdGeom.GetStageMetersPerUnit(stage))
```

**Expected output**

```text
defaultPrim: Chair
upAxis: Y
metersPerUnit: 0.01
```

### 9. Real-world use case

A publish linter fails assets missing `defaultPrim` (Obj 4.6).

### 10. Common mistakes

> [!MISTAKE] Setting `upAxis` as an attribute on `/World`.

### 11. Exam traps

> [!TRAP] `defaultPrim = "/Chair"` with a slash — it is a **name**, `"Chair"`.

### 12. Practice questions

**DM-027** · Difficulty: Easy · Type: Single choice

`defaultPrim` is:

A. A prim attribute  
B. Layer/stage metadata naming the entry prim  
C. A relationship  
D. A kind  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Publishable layers: defaultPrim, upAxis, metersPerUnit, and a sensible time range.

---

## 12.5 Representing pipeline metadata (Obj 5.3, 7.6)

### 1. What is it?

A decision guide: attribute vs metadata vs API schema vs custom typed schema.

### 2. Why do we need it?

The exam asks you to "represent custom metadata" and to know when a **schema** is the right upgrade (Obj 3.4, 3.6).

### 3. Beginner explanation

Start with customData. If many tools need typed fields, graduate to an API schema.

### 4. Technical explanation

| Need | Put it here |
|------|-------------|
| Shot name, notes, one-off flags | `customData` |
| Stable asset id / version | `assetInfo` |
| Kind / hidden / docs | registered metadata |
| Values a renderer must see | attributes / primvars |
| Shared typed fields on many prims | API schema (Ch 37) |
| A new kind of object | typed schema |

Do not store geometry in customData. Do not store the studio's asset id as `primvars:id` unless shading needs it.

### 5. Mental model

Visibility to renderer → property. Visibility to pipeline → metadata.

### 6. Simple example

`studio:task = "model"` → customData. `points` → attribute.

### 7. USDA example

```usda
#usda 1.0

def Xform "Chair" (
    kind = "component"
    assetInfo = {
        string identifier = "props/chair"
    }
    customData = {
        string department = "model"
        int version = 12
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
Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
prim.SetAssetInfoByKey("identifier", "props/chair")
prim.SetCustomDataByKey("department", "model")
prim.SetCustomDataByKey("version", 12)
print(prim.GetAssetInfo()["identifier"], prim.GetCustomDataByKey("department"), prim.GetCustomDataByKey("version"))
```

**Expected output**

```text
props/chair model 12
```

### 9. Real-world use case

A DCC exporter writes customData on the way out and a USD importer reads it back for round-trip (Obj 4.4) without polluting Mesh schemas.

### 10. Common mistakes

> [!MISTAKE] Encoding version in the prim **name** (`Chair_v12`). Names that churn break references. Use assetInfo + resolver (Ch 33).

### 11. Exam traps

> [!TRAP] "Custom metadata requires a C++ plugin." Dictionaries do not. Plugins are for *registered* new fields and schemas.

### 12. Practice questions

**PIP-PRE-002** · Obj 5.3 · Difficulty: Medium · Type: Single choice

A one-off "approvedBy" string on a publish should usually be:

A. A new typed Mesh subclass  
B. `customData`  
C. `faceVertexIndices`  
D. A Hydra scene index  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Pipeline strings → customData / assetInfo.
> - Geometry → attributes. Shared typed contracts → schemas.

---

## Chapter lab(s)

Lab 08 (metadata, customData, assetInfo, stage metadata).

## USDA reading exercise

**USDA-13.** Is `hidden = true` on a defined Mesh enough to remove it from `Traverse()`?

**Answer:** No. Traverse still visits it unless it is inactive or abstract.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Custom metadata | customData / assetInfo |
| Asset identity | assetInfo |
| hidden vs active vs visibility | three switches |
| defaultPrim | layer metadata, a name |

### Chapter questions

**Q1.** Obj 5.3 in one sentence?  
**Q2.** assetInfo vs customData?  
**Q3.** Does hidden skip Traverse?  
**Q4.** Where is defaultPrim stored?  
**Q5.** Why not Chair_v12 as a prim name?  
**Q6.** userDocBrief surprise?  
**Q7.** When to upgrade to an API schema?  
**Q8.** kind vs typeName?

**Answers**

1. Store non-schema info as metadata (usually dictionaries). 2. Identity vs other notes. 3. No. 4. Layer header. 5. Names that change break arcs. 6. Schema may already put keys in customData. 7. When many tools need the same typed fields. 8. Metadata vs schema type.

## Further reading

- Glossary: Metadata, Custom Data, Asset Info  
- ModelAPI / Kind  
