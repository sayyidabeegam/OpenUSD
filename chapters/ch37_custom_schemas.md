# Chapter 37 — Custom Schemas

> **Exam domain:** Customizing USD (6%), also Data Exchange (15%) · **Objectives:** 3.4, 3.6, 4.5 · **Study day:** 11 · **Est. time:** 85 min
> **Prerequisites:** Ch 6 (typed vs API schemas), Ch 29 (custom attributes), Ch 36 (`plugInfo.json`)

A **custom schema** is a contract *you* add: a new typed prim (`def Door`) or an API you `Apply` (`LabelAPI`). Obj 3.4 / 3.6 / 4.5 all ask when to use a schema instead of a one-off `custom` attribute, how `schema.usda` and `usdGenSchema` fit, and which **base class** to inherit. This book's `usd-core` has **no** `usdGenSchema`; you still must read `schema.usda` and use `Usd.SchemaRegistry` on the built-ins.

## Learning goals

- Decide when a custom schema is worth it versus a namespaced custom attribute.
- Read and write a minimal `schema.usda` (`class`, `inherits`, `GLOBAL`).
- Contrast **codeless** vs **codeful** output of `usdGenSchema`.
- Choose `UsdTyped` (IsA) vs `UsdAPISchemaBase` (Apply).
- Carry nonstandard DCC fields through a schema or a documented custom attribute (Obj 4.5).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **`schema.usda`** | The USDA source file `usdGenSchema` reads to generate code and `plugInfo.json` |
| **`usdGenSchema`** | Tool that compiles `schema.usda` into C++/Python wrappers and plugin metadata |
| **Codeless schema** | Schema used at runtime from generated USDA + `plugInfo.json`, **no** C++ types |
| **Codeful schema** | Schema that generates C++ classes you compile against a USD version |
| **`UsdTyped`** | Base for IsA / typed schemas (`def Cube`) |
| **`UsdAPISchemaBase`** | Base for API schemas you `Apply` |
| **`Usd.SchemaRegistry`** | Query concrete vs abstract vs applied vs multiple-apply |
| **`skipCodeGeneration`** | `customData` flag in `schema.usda` for a codeless type |

---

## 37.1 When to create a schema

### 1. What is it?

Creating a schema means publishing a **named contract** (typed prim or API) that many tools will honor. It is not the same as adding one `custom float studio:weight` on one chair.

### 2. Why do we need it?

Custom attributes are fast (Ch 29). They do not give you `Apply`, `HasAPI`, generated accessors, or `usdchecker`-style validators that know the field. When three DCCs and a farm all need `partId`, a schema stops the name from drifting (`part_id` vs `partId` vs `pn`).

### 3. Beginner explanation

A sticky note on one box is a custom attribute. A printed form every warehouse uses is a schema. Print the form when the sticky note is copied so often that people misspell it.

*Where the analogy breaks:* a schema still *stores* ordinary USD properties. You are not inventing a new file format (that is Ch 38). You are naming a bundle of properties and (for typed schemas) a type name.

### 4. Technical explanation

Use a **custom attribute** (or `customData`) when:

- One exporter, one shot, or a temporary experiment
- The name is already namespaced (`studio:cadId`) and documented
- You do not need `HasAPI` / generated `CreatePartIdAttr`

Use a **custom schema** when:

- Several tools must create, validate, and query the same fields (Obj 3.4, 3.6)
- You want `def Door` in USDA (typed / IsA) or `apiSchemas = ["LabelAPI"]` (API)
- You will write a validator that looks for that schema (Ch 30)
- Import/export of a DCC family should round-trip through `Apply` (Obj 4.5)

Cost: `schema.usda`, `usdGenSchema`, a plugin (Ch 36), and — if codeful — a rebuild against each USD version (Ch 35). That cost is why NVIDIA still expects you to *start* with custom attributes.

### 5. Mental model

```text
  one tool, one field     -->  custom studio:weight
  many tools, a bundle    -->  schema (API or typed)
  new encoding on disk    -->  file-format plugin (Ch 38), not a schema
```

### 6. Simple example

Factory CAD: first week, `custom string studio:partId`. Six months later every DCC and the MES need it → `LabelAPI` with `studio:partId`, `usdGenSchema`, plugin on `PXR_PLUGINPATH_NAME`.

### 7. USDA example

The *before* (no schema). Legal, portable, and what Ch 29 taught.

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    kind = "component"
)
{
    custom string studio:partId = "PN-42"
    custom float studio:weight = 4
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
attr = prim.CreateAttribute(
    "studio:partId", Sdf.ValueTypeNames.String, custom=True)
attr.Set("PN-42")
print("custom", attr.IsCustom())
print("value", attr.Get())
print("HasAPI LabelAPI", prim.HasAPI(Usd.APISchemaBase))
print("typeName", prim.GetTypeName())
```

**Expected output**

```text
custom True
value PN-42
HasAPI LabelAPI False
typeName Xform
```

`HasAPI(Usd.APISchemaBase)` is not a substitute for a real `LabelAPI`. The attribute works; nothing in the registry yet knows `LabelAPI`.

### 9. Real-world use case

A robotics team stored joint limits as `customData` for a year. When two engines needed the same limits, they moved to `UsdPhysics` (already a schema) plus a thin `StudioJointAPI` for extra fields. The customData leftovers are stripped on publish (Ch 34).

### 10. Common mistakes

> [!MISTAKE] Creating a typed schema `def Weight "W"` for a single float. An API or a custom attribute is enough.

> [!MISTAKE] A new schema for every DCC version. Namespace the attribute until the contract is stable.

> [!MISTAKE] Using a schema plugin as a file format. Schemas do not parse `.sldprt`.

### 11. Exam traps

> [!TRAP] "Obj 4.5 always requires `usdGenSchema` on the exam machine." You must *choose* schema vs custom attribute. `usd-core` does not ship the generator.

> [!TRAP] "Custom attributes are illegal in production." They are the right first step.

### 12. Practice questions

**Q37.1-1.** Four DCCs must set and validate the same `partId`. Best long-term choice?
A. Four different custom names
B. A documented API schema generated from `schema.usda`
C. Put `partId` in the prim's name
D. Store it only in `session` layer

**Q37.1-2.** Select two good uses of a *custom attribute* instead of a schema.
A. A one-week experiment in one exporter
B. A field only one internal tool reads
C. A new prim type `Door` used in every set
D. A single-apply API shared by Maya, Houdini, and the farm

**Answers**

- **Q37.1-1: B.** Shared contract → schema + plugin.
- **Q37.1-2: A and B.** C and D are schema territory.

### 13. Exam takeaways

> [!KEY]
> - Custom attribute first; schema when many tools share a bundle.
> - Schema ≠ file format ≠ resolver.
> - Obj 4.5 is the *choice*, not a requirement to run `usdGenSchema` in `usd-core`.

---

## 37.2 `schema.usda`

### 1. What is it?

**`schema.usda`** is an USDA file that *describes* schemas for code generation. It is not a shot. It uses `class` prims, `inherits`, and an `over "GLOBAL"` block with `libraryName` / `libraryPath`.

### 2. Why do we need it?

One text file is the source of truth for property names, fallbacks, and inheritance. `usdGenSchema` reads it so C++, Python, and `plugInfo.json` cannot drift.

### 3. Beginner explanation

`schema.usda` is the blank form template. `usdGenSchema` is the print shop. Shots are filled-in copies (`def Cube "Box"`). You do not hand the blank form to lighting as a set file.

*Where the analogy breaks:* `class Cube "Cube"` in the *official* `usdGeom/schema.usda` is the generator's class, not a LIVERPS `class` you inherit in a shot (Ch 19). Same USDA keyword; different pipeline role.

### 4. Technical explanation

Verified pattern (Pixar `usdGeom/schema.usda`, USD 26.08):

- Layer opens with `#usda 1.0` and often sublayers `usd/schema.usda` (for `Typed`, `Gprim`, …).
- `over "GLOBAL"` holds `customData.libraryName` and `libraryPath`.
- Each schema is a **`class`** prim: `class Cube "Cube" ( inherits = </Gprim> )`.
- Properties inside the class become schema attributes (`double size = 2.0`).
- `doc` metadata becomes C++ / Python documentation.
- Extra `customData` can set `implementsComputeExtent`, `apiSchemaType`, `skipCodeGeneration`.

A **minimal** file that still **parses** as USDA (this is teaching-sized, not a full Pixar library):

Typed schema class inherits `</Typed>` (the `UsdTyped` prim in `usd/schema.usda`). API schema class inherits `</APISchemaBase>`.

Parsing `schema.usda` with `Sdf` does **not** register the schema. Registration needs `usdGenSchema` output in a plugin (Section 37.3).

### 5. Mental model

```text
  schema.usda  --usdGenSchema-->  generatedSchema.usda
                                  plugInfo.json
                                  C++ (if codeful)
  shots use:  def Cube "Box"   or   apiSchemas = ["LabelAPI"]
```

### 6. Simple example

Studio `schema.usda` defines `class "Door"` with `bool sliding` and `float width`. After generation, artists write `def Door "Hall"` in sets.

### 7. USDA example

*File: schema.usda* (minimal, parses as USDA; not installed as a plugin here)

```usda
#usda 1.0

over "GLOBAL" (
    customData = {
        string libraryName = "studio"
        string libraryPath = "studio"
    }
)
{
}

class "Door" (
    inherits = </Typed>
    doc = "A studio door prim."
)
{
    bool sliding = 0
    float width = 0.9
}

class "LabelAPI" (
    inherits = </APISchemaBase>
    doc = "A single-apply API for a part label."
)
{
    string studio:partId = ""
}
```

- `GLOBAL` — library identity for the generator.
- `class "Door"` + `inherits = </Typed>` — IsA schema (Section 37.4).
- `class "LabelAPI"` + `</APISchemaBase>` — API schema.
- Fallbacks (`sliding = 0`, `width = 0.9`) become schema defaults, like Cube's `size = 2`.

### 8. Python example

```python
from pxr import Sdf

text = """#usda 1.0

over "GLOBAL" (
    customData = {
        string libraryName = "studio"
        string libraryPath = "studio"
    }
)
{
}

class "Door" (
    inherits = </Typed>
)
{
    bool sliding = 0
    float width = 0.9
}

class "LabelAPI" (
    inherits = </APISchemaBase>
)
{
    string studio:partId = ""
}
"""
layer = Sdf.Layer.CreateAnonymous(".usda")
print("parsed", layer.ImportFromString(text))
for spec in layer.rootPrims:
    inh = [str(p) for p in spec.inheritPathList.GetAddedOrExplicitItems()]
    print(spec.name, str(spec.specifier), "inherits", inh)
```

**Expected output**

```text
parsed True
GLOBAL Sdf.SpecifierOver inherits []
Door Sdf.SpecifierClass inherits ['/Typed']
LabelAPI Sdf.SpecifierClass inherits ['/APISchemaBase']
```

Sdf sees classes and inherits. The **SchemaRegistry** still does not know `Door` until this file is generated into a plugin.

### 9. Real-world use case

Pixar's own `usdGeom/schema.usda` is thousands of lines. `class Cube "Cube" ( inherits = </Gprim> )` with `double size = 2.0` is why `FindConcretePrimDefinition("Cube")` reports fallback size `2` (next sections).

### 10. Common mistakes

> [!MISTAKE] Referencing `schema.usda` from a shot as a sublayer. It is generator input, not scene data.

> [!MISTAKE] Using `def Door` in `schema.usda` instead of `class`. The generator looks for schema classes.

> [!MISTAKE] Forgetting `over "GLOBAL"` `libraryName`. `usdGenSchema` needs the library identity.

### 11. Exam traps

> [!TRAP] "`inherits = </Typed>` in schema.usda is the same as a shot `inherits` class for broadcast edits." Shot inherits are LIVERPS (Ch 19). Schema inherits are the **C++ / registry** base.

> [!TRAP] "If Sdf parses `schema.usda`, `def Door` works in usdview." Parse ≠ register.

### 12. Practice questions

**Q37.2-1.** In `schema.usda`, a new typed prim is authored as:
A. `def Xform "Door"`
B. `class "Door" ( inherits = </Typed> )`
C. `over "Door"`
D. `payload = @Door@`

**Q37.2-2.** Select two things `over "GLOBAL"` typically stores.
A. `libraryName`
B. `libraryPath`
C. `defaultPrim` of the shot
D. `metersPerUnit` of the factory floor

**Answers**

- **Q37.2-1: B.** Schema classes inherit `Typed` or `APISchemaBase`.
- **Q37.2-2: A and B.** GLOBAL is generator metadata, not a shot.

### 13. Exam takeaways

> [!KEY]
> - `schema.usda`: `GLOBAL` + `class` + `inherits` (`/Typed` or `/APISchemaBase`).
> - Sdf can parse it; the registry ignores it until `usdGenSchema` + plugin.
> - Do not sublayer `schema.usda` into shots.

---

## 37.3 `usdGenSchema`; codeful vs. codeless schemas

### 1. What is it?

**`usdGenSchema`** reads `schema.usda` and writes generated files: `generatedSchema.usda`, `plugInfo.json`, and (unless told not to) C++/Python wrappers. A **codeless** schema skips those wrappers (`skipCodeGeneration`) and is used from the generated USDA at runtime. A **codeful** schema compiles C++ classes (`UsdStudioDoor`) against a USD version.

### 2. Why do we need it?

Hand-writing `plugInfo.json` `Types` for every property is how names drift. The generator is the official bridge from `schema.usda` to the plugin system (Ch 36). Codeless lets you ship a schema **without** a C++ rebuild on every farm image; codeful gives typed Python/C++ APIs.

### 3. Beginner explanation

Codeless is a PDF form everyone fills in a viewer that already knows "PDF." Codeful is a native app compiled for that OS. Both came from the same InDesign file (`schema.usda`).

*Where the analogy breaks:* codeless schemas still need a USD that can load the plugin's `generatedSchema.usda`. They are not "just JSON."

### 4. Technical explanation

```{.bash .norun}
usdGenSchema schema.usda
```

Not installed with `usd-core` (`shutil.which` is `None` below). A full OpenUSD build provides it (Ch 35). Typical outputs:

| Output | Role |
|--------|------|
| `generatedSchema.usda` | Runtime schema definitions the plugin loads |
| `plugInfo.json` | `Info.Types` with `schemaKind`, `bases`, aliases |
| `door.cpp` / wrap files | Codeful only; compile with matching USD |
| Tokens header | Attribute name tokens |

**Codeless:** on the `class` (or library), `customData` includes `skipCodeGeneration = true` (token/bool per official docs). Tools talk to the prim through generic `Usd.Prim` / `CreateAttribute`, or a thin Python helper. Faster to ship; weaker compile-time API.

**Codeful:** generate + compile `UsdTyped` / `UsdAPISchemaBase` subclasses. `UsdStudio.Door.Define(stage, path)` looks like `UsdGeom.Cube.Define`. Must rebuild when USD's ABI changes (Obj 3.1, Ch 35).

Both still need `PXR_PLUGINPATH_NAME` / `RegisterPlugins`.

> [!VERSION] Verified: `usdGenSchema` is **not** on `PATH` in this `usd-core` 26.8 venv. Teach the command as `.norun`. Built-in schemas (`Cube`, `MaterialBindingAPI`) were generated by Pixar when *they* built USD.

### 5. Mental model

```text
  schema.usda
       |
       v
  usdGenSchema
       |
       +-- always: generatedSchema.usda + plugInfo.json
       +-- codeful: C++/Python classes  (compile)
       +-- codeless: skipCodeGeneration, no compile
```

### 6. Simple example

A small studio ships `LabelAPI` as **codeless** so every DCC Python can `Apply` via the generic API once the plugin path is set. The engine team later promotes it to **codeful** for C++ accessors.

### 7. USDA example

Codeless marker on the class (still ordinary USDA `customData`):

```usda
#usda 1.0

class "LabelAPI" (
    inherits = </APISchemaBase>
    customData = {
        token skipCodeGeneration = "true"
        token apiSchemaType = "singleApply"
    }
)
{
    string studio:partId = ""
}
```

`usdGenSchema` would emit plugin metadata instead of `labelAPI.cpp`.

### 8. Python example

```python
import shutil
from pxr import Usd, UsdGeom

print("usdGenSchema", shutil.which("usdGenSchema"))
sr = Usd.SchemaRegistry()
print("Cube registered",
      sr.FindConcretePrimDefinition("Cube") is not None)
print("Cube size fallback",
      sr.FindConcretePrimDefinition("Cube").GetAttributeFallbackValue("size"))
print("Door registered",
      sr.FindConcretePrimDefinition("Door") is not None)
```

**Expected output**

```text
usdGenSchema None
Cube registered True
Cube size fallback 2.0
Door registered False
```

Pixar's generated Cube is in the wheel. Your `Door` from Section 37.2 is **not**, because we never ran `usdGenSchema` or loaded a plugin.

### 9. Real-world use case

A games company checks `generatedSchema.usda` and `plugInfo.json` into git (codeless) so QA machines without a C++ toolchain still load `DestructibleAPI`. The runtime engine uses a **codeful** copy compiled into the game for speed.

### 10. Common mistakes

> [!MISTAKE] Editing `generatedSchema.usda` by hand and losing the edits on the next `usdGenSchema`. Edit `schema.usda`.

> [!MISTAKE] Shipping codeful `.so` built for 25.11 into 26.08 usdview (Ch 35).

> [!MISTAKE] Expecting `which usdGenSchema` to work after `pip install usd-core`.

### 11. Exam traps

> [!TRAP] "Codeless means no `plugInfo.json`." Codeless still needs the JSON and generated USDA.

> [!TRAP] "Codeful schemas do not need a plugin path." They still discover via `plugInfo.json`.

### 12. Practice questions

**Q37.3-1.** `usdGenSchema` in this book's venv:
A. Is on `PATH`
B. Is not installed; use a full USD build
C. Is `Usd.SchemaRegistry`
D. Is `usdcat`

**Q37.3-2.** Select two true statements.
A. Codeless skips C++ generation but still uses `plugInfo.json`
B. Codeful APIs must match the host USD ABI
C. Codeless schemas cannot define properties
D. `FindConcretePrimDefinition("Door")` works after only parsing `schema.usda` with Sdf

**Answers**

- **Q37.3-1: B.**
- **Q37.3-2: A and B.** Parse ≠ register; properties exist on the class in `schema.usda`.

### 13. Exam takeaways

> [!KEY]
> - `usdGenSchema` turns `schema.usda` into plugin files (+ C++ if codeful).
> - Codeless = no generated C++; still a plugin. Codeful = compile against USD.
> - This venv: generator absent; built-in Cube fallback `size` is `2.0`.

---

## 37.4 IsA (`UsdTyped`) vs. API (`UsdAPISchemaBase`) base classes

### 1. What is it?

When you author `schema.usda`, you pick a **base class**. **`UsdTyped`** (schema inherit `</Typed>`) makes an IsA type: `def Door`. **`UsdAPISchemaBase`** (inherit `</APISchemaBase>`) makes an API you **Apply** onto an existing typed prim. This is the exam's favorite custom-schema fork (Obj 3.4, 3.6).

### 2. Why do we need it?

Physics properties on a mesh should not force `def PhysicsMesh`. They **Apply** onto `Mesh` / `Cube` (`UsdPhysics.RigidBodyAPI`, Ch 35). A brand-new thing that *is* a door gets `def Door` from `UsdTyped`.

### 3. Beginner explanation

`UsdTyped` is a new species. `UsdAPISchemaBase` is a collar you buckle onto any animal. Collars compose (`RigidBodyAPI` + `CollisionAPI` + `MaterialBindingAPI` on one Cube). Species is one `typeName`.

*Where the analogy breaks:* abstract typed schemas (`Gprim`) are species that you never instantiate; they only exist so Cube/Sphere inherit them. `IsAbstract` is True, `IsConcrete` is False.

### 4. Technical explanation

`Usd.SchemaRegistry` queries (verified 26.08):

| Question | Cube | Gprim | GeomModelAPI | CollectionAPI | MaterialBindingAPI |
|----------|------|-------|--------------|---------------|--------------------|
| `IsTyped` | True | True | False | False | False |
| `IsConcrete` | True | False | False | False | False |
| `IsAbstract` | False | True | — | — | — |
| `IsAppliedAPISchema` | False | False | True | True | True |
| `IsMultipleApplyAPISchema` | False | False | False | True | False |
| `GetSchemaKind` | `ConcreteTyped` | abstract typed | `SingleApplyAPI` | `MultipleApplyAPI` | `SingleApplyAPI` |

Python:

- Typed: `UsdGeom.Cube.Define` → `prim.IsA(UsdGeom.Cube)`
- Single-apply API: `UsdShade.MaterialBindingAPI.Apply(prim)` → `HasAPI(...)` (must Apply; Ch 29)
- Multiple-apply: `Usd.CollectionAPI.Apply(prim, "include")` → `CollectionAPI:include`

**Rule of thumb for custom schemas:** extra fields on existing geometry → **API** (`UsdAPISchemaBase`). A new first-class object in the outliner → **typed** (`UsdTyped`). NVIDIA's physics-on-geometry example is the API fork.

`FindSchemaInfo(UsdGeom.Cube).kind` is `ConcreteTyped`; `.identifier` / `.family` are `Cube`.

### 5. Mental model

```text
  typeName:  one IsA (UsdTyped, concrete)
  apiSchemas: zero or more applied APIs (UsdAPISchemaBase)
```

### 6. Simple example

`Door` as typed: artists `def Door "Hall"`. `LabelAPI` as API: `def Mesh "Crate"` plus `LabelAPI.Apply`. Putting `partId` on a new `def PartIdPrim` would pollute the model hierarchy.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Crate" (
    prepend apiSchemas = ["MaterialBindingAPI"]
)
{
}

def Cube "Box"
{
    double size = 2
}
```

Mesh *is-a* Mesh (typed). `MaterialBindingAPI` is applied (API). Cube is concrete typed; you never `def Gprim`.

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade, Tf

sr = Usd.SchemaRegistry()
cube_t = UsdGeom.Cube
gprim_t = Tf.Type.FindByName("UsdGeomGprim")
print("Cube IsConcrete", sr.IsConcrete(cube_t),
      "IsTyped", sr.IsTyped(cube_t))
print("Gprim IsConcrete", sr.IsConcrete(gprim_t),
      "IsAbstract", sr.IsAbstract(gprim_t),
      "IsTyped", sr.IsTyped(gprim_t))
print("ModelAPI applied", sr.IsAppliedAPISchema(UsdGeom.ModelAPI),
      "multi", sr.IsMultipleApplyAPISchema(UsdGeom.ModelAPI))
print("Collection multi", sr.IsMultipleApplyAPISchema(Usd.CollectionAPI))
print("Binding applied",
      sr.IsAppliedAPISchema(UsdShade.MaterialBindingAPI))
info = sr.FindSchemaInfo(UsdGeom.Cube)
print("Cube kind", info.kind, "family", info.family)

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Mesh.Define(stage, "/M").GetPrim()
UsdShade.MaterialBindingAPI.Apply(prim)
print("IsA Mesh", prim.IsA(UsdGeom.Mesh),
      "IsA Cube", prim.IsA(UsdGeom.Cube))
print("HasAPI binding", prim.HasAPI(UsdShade.MaterialBindingAPI))
print("applied", list(prim.GetAppliedSchemas()))
```

**Expected output**

```text
Cube IsConcrete True IsTyped True
Gprim IsConcrete False IsAbstract True IsTyped True
ModelAPI applied True multi False
Collection multi True
Binding applied True
Cube kind ConcreteTyped family Cube
IsA Mesh True IsA Cube False
HasAPI binding True
applied ['MaterialBindingAPI']
```

### 9. Real-world use case

USD Physics: bodies stay `Cube`/`Mesh` (typed geom) plus `RigidBodyAPI` / `CollisionAPI` (applied). That is the pattern the exam wants copied for "add friction to existing meshes."

### 10. Common mistakes

> [!MISTAKE] Inheriting `UsdTyped` for "has a part id." You just forced a new type name on every labeled mesh.

> [!MISTAKE] Forgetting `Apply` on an API schema. `HasAPI` stays False (Ch 29, Ch 40).

> [!MISTAKE] `def Gprim "Thing"`. Gprim is abstract.

### 11. Exam traps

> [!TRAP] "`IsA` tests API schemas." `IsA` is typed inheritance. APIs use `HasAPI`.

> [!TRAP] "CollectionAPI is single-apply because it is an API." It is **multiple-apply**.

> [!TRAP] "Concrete means 'has C++ code'." Concrete means instantiable typed schema (`def Cube`). Codeless typed schemas can still be concrete.

### 12. Practice questions

**Q37.4-1.** Extra simulation flags on existing `Mesh` prims. Base class?
A. `UsdTyped`
B. `UsdAPISchemaBase`
C. `SdfFileFormat`
D. `ArResolver`

**Q37.4-2.** Select two true registry facts on 26.08.
A. Cube is concrete typed
B. Gprim is abstract typed
C. MaterialBindingAPI is multiple-apply
D. CollectionAPI is not an applied API

**Answers**

- **Q37.4-1: B.** Apply onto Mesh; do not replace the type.
- **Q37.4-2: A and B.** Binding is single-apply; Collection is applied *and* multiple-apply.

### 13. Exam takeaways

> [!KEY]
> - New species → `UsdTyped` / `def Door`. Extra collar → `UsdAPISchemaBase` / `Apply`.
> - `IsA` vs `HasAPI`; concrete vs abstract; single vs multiple apply.
> - Physics-on-geometry is the API pattern.

---

## 37.5 Schemas for nonstandard import/export data

### 1. What is it?

Obj 4.5 / 3.6: when a DCC has data USD does not model (CAD id, PLC tag, proprietary shader knob), you either **map it to a custom attribute** or **wrap it in a schema** so round-trips do not invent a new name each time.

### 2. Why do we need it?

Chapter 29 showed `studio:partId` as a custom attribute. That is correct until the importer must *find* every labeled part: then `HasAPI(LabelAPI)` is faster and safer than string-matching attribute names.

### 3. Beginner explanation

The factory stamp on a crate is either a Sharpie (`custom` attribute) or an official barcode format (schema). Shipping with a Sharpie works. A barcode reader in every warehouse wants the official format.

*Where the analogy breaks:* both still live on the same USD prim. The schema does not move the data to a side-car file.

### 4. Technical explanation

Exporter policy (document it, Ch 32):

| Data | Mechanism |
|------|-----------|
| One-off / unstable | `custom` namespaced attribute (`studio:…`) |
| Stable bundle, many tools | API schema `Apply` + generated properties |
| New outliner object | Typed schema |
| Whole other file type | File-format plugin (Ch 38), not a schema |

Round-trip test (Ch 35): after DCC import/export, `HasAPI` and the attribute `Get()` still match. Flatten must not be the default Save (Ch 34) or the API application can be baked in a way that loses the plugin dependency — still keep `apiSchemas` in the layer.

You can mix: `def Mesh` (built-in typed) + `LabelAPI` (custom API) + `custom float studio:debug` (ephemeral).

### 5. Mental model

```text
  DCC extra fields
       |
       +-- unstable --> custom studio:*
       +-- stable  --> Apply(LabelAPI) / def Door
       +-- file    --> converter or SdfFileFormat
```

### 6. Simple example

CAD `cadId` is stable → `LabelAPI.studio:partId`. A debug tessellation count that changes every export → `custom int studio:tessDebug`.

### 7. USDA example

Mesh (built-in typed) plus an applied built-in API, plus a custom attribute still waiting to become `LabelAPI`:

```usda
#usda 1.0

def Mesh "Crate" (
    prepend apiSchemas = ["MaterialBindingAPI"]
)
{
    custom string studio:partId = "PN-42"
}
```

After the studio ships `LabelAPI`, the same file grows `LabelAPI` in `apiSchemas` and `studio:partId` becomes a **schema** property (often no longer marked `custom`).

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade, Sdf

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Mesh.Define(stage, "/Crate").GetPrim()
UsdShade.MaterialBindingAPI.Apply(prim)
prim.CreateAttribute(
    "studio:partId", Sdf.ValueTypeNames.String, custom=True).Set("PN-42")

print("type", prim.GetTypeName())
print("applied", list(prim.GetAppliedSchemas()))
print("partId custom",
      prim.GetAttribute("studio:partId").IsCustom())
print("partId", prim.GetAttribute("studio:partId").Get())

# Simulate a DCC reopen from a layer string.
text = stage.GetRootLayer().ExportToString()
again = Usd.Stage.CreateInMemory()
again.GetRootLayer().ImportFromString(text)
p2 = again.GetPrimAtPath("/Crate")
print("reopen type", p2.GetTypeName())
print("reopen applied", list(p2.GetAppliedSchemas()))
print("reopen partId", p2.GetAttribute("studio:partId").Get())
```

**Expected output**

```text
type Mesh
applied ['MaterialBindingAPI']
partId custom True
partId PN-42
reopen type Mesh
reopen applied ['MaterialBindingAPI']
reopen partId PN-42
```

If a DCC drops unknown `custom` attributes or `apiSchemas`, this reopen test fails. That is the Obj 4.5 regression.

### 9. Real-world use case

A PLC exporter writes `studio:tag` on every motor. When the digital-twin standard froze, they generated `FactoryTagAPI` (codeless) and the exporter switched from `CreateAttribute` to `Apply` + schema property. Old files still open: the importer accepts *either* the custom attribute or the API until the cut-over date.

### 10. Common mistakes

> [!MISTAKE] Deleting unknown `custom` attributes on import "to keep the scene clean." You just broke the round-trip (Ch 29, Ch 35).

> [!MISTAKE] Putting CAD ids in prim names. Names are identifiers, not data (Ch 28, Ch 32).

> [!MISTAKE] A typed schema per CAD part instance. One Mesh + API per part, or a schema on the component root.

### 11. Exam traps

> [!TRAP] "Nonstandard data must be a new file format." Only if the *bytes* are not USD. Fields inside USD are attributes/schemas.

> [!TRAP] "`custom` keyword is required on schema properties." Generated schema properties are usually ordinary (non-custom) attributes.

### 12. Practice questions

**Q37.5-1.** A DCC has a stable `cadId` used by four tools and a one-off tessellation debug integer. Best split?
A. Both as typed schemas
B. `cadId` → API schema; debug → custom attribute
C. Both as file-format plugins
D. Put both in the prim path

**Q37.5-2.** Select two Obj 4.5 round-trip requirements.
A. Preserve `apiSchemas` you applied
B. Preserve namespaced custom attributes you do not understand
C. Flatten on every Save
D. Strip `custom` attributes so USDA is smaller

**Answers**

- **Q37.5-1: B.** Stable shared field vs ephemeral debug.
- **Q37.5-2: A and B.** Flatten/strip are how data dies.

### 13. Exam takeaways

> [!KEY]
> - Nonstandard *fields* → attribute or schema; nonstandard *files* → format plugin.
> - Round-trip: keep `apiSchemas` and unknown `studio:*` customs.
> - Promote custom attributes to an API when the contract freezes.

---

## Chapter lab(s)

**Lab 31** — Codeless custom schema: write `schema.usda` + `plugInfo.json` structure (even if this venv cannot run `usdGenSchema`), and round-trip a `studio:partId` attribute as in §37.5.

## USDA reading exercises

**Exercise 37-A.** A schema file contains `class "Bolt" ( inherits = </APISchemaBase> )` and someone authors `def Bolt "B"` in a shot. What went wrong?

**Exercise 37-B.** `FindConcretePrimDefinition("Door")` is `None` after `Sdf` parsed the `schema.usda` from §37.2. Why?

**Answers**

- **37-A.** `APISchemaBase` is for **Apply**, not `def Bolt`. Use `inherits = </Typed>` for a typed `def Bolt`, or `def Mesh` + `BoltAPI.Apply`.
- **37-B.** Parse ≠ register. Need `usdGenSchema` output loaded as a plugin.

## Chapter review

**Summary**

- Custom attribute first; schema when many tools share a bundle (Obj 3.4, 4.5).
- `schema.usda`: `GLOBAL`, `class`, `inherits` `/Typed` or `/APISchemaBase`.
- `usdGenSchema` is absent in `usd-core`; codeless vs codeful is still exam material.
- `UsdTyped` = IsA; `UsdAPISchemaBase` = Apply; Gprim is abstract; Collection is multiple-apply.
- Round-trip nonstandard data: keep APIs and `studio:*` customs.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| Physics on a Mesh | API schema, not a new type |
| `def Door` | `UsdTyped` / concrete |
| `apiSchemas = ["LabelAPI"]` | `UsdAPISchemaBase` + Apply |
| `usdGenSchema` on usd-core | Not installed |
| `schema.usda` sublayered in a shot | Wrong role |
| Cube `size` fallback 2 | `PrimDefinition` |
| One-off CAD debug field | custom attribute |

**Review questions**

**R37-1** (Obj 3.4) Extra friction on existing meshes. Inherit:
A. `UsdTyped`
B. `UsdAPISchemaBase`
C. `SdfFileFormat`
D. `UsdGeomGprim` as a `def Gprim`

**R37-2** (Obj 3.4) Select two `schema.usda` facts.
A. Typed schemas `inherits = </Typed>`
B. API schemas `inherits = </APISchemaBase>`
C. Shot `defaultPrim` belongs in `GLOBAL`
D. `def` is preferred over `class` for generator input

**R37-3** (Obj 3.6) Codeless schemas:
A. Need no `plugInfo.json`
B. Skip C++ generation; still load via a plugin
C. Cannot be applied
D. Are file formats

**R37-4** (Obj 4.5) Select two round-trip keepers.
A. `MaterialBindingAPI` in `apiSchemas`
B. `custom string studio:partId`
C. The session layer
D. Absolute `/mnt` texture paths you meant to strip

**R37-5** (Obj 3.4) `IsConcrete(Gprim)` is False because:
A. Gprim is an abstract typed schema
B. Gprim is multiple-apply
C. `usd-core` omitted geom
D. Gprim is an API

**R37-6** (Obj 3.4) `prim.IsA(UsdGeom.Cube)` vs `prim.HasAPI(UsdShade.MaterialBindingAPI)`:
A. They are aliases
B. `IsA` is typed; `HasAPI` is applied APIs
C. `HasAPI` is only for kinds
D. `IsA` tests `plugInfo.json` names

**R37-7** (Obj 3.6) `usdGenSchema` in this venv prints from `shutil.which`:
A. `/usr/bin/usdGenSchema`
B. `None`
C. `usdcat`
D. `True`

**R37-8** (Obj 4.5) Best first encoding for an experimental DCC knob?
A. Codeful typed schema rebuilt weekly
B. Namespaced `custom` attribute
C. New `.knob` file format plugin
D. Prim rename

**R37-9** (Obj 3.4) Select two true 26.08 registry facts.
A. CollectionAPI is multiple-apply
B. MaterialBindingAPI is applied (single)
C. Cube is abstract
D. ModelAPI is typed concrete

**R37-10** (Obj 3.6) Editing `generatedSchema.usda` instead of `schema.usda`:
A. Is the official workflow
B. Will be overwritten the next `usdGenSchema`
C. Registers Door without a plugin
D. Sets `skipCodeGeneration` automatically

**R37-11** (Obj 4.5) After promoting `studio:partId` to `LabelAPI`, old files with only the custom attribute:
A. Must be discarded
B. Can be accepted by an importer that reads either form during cut-over
C. Automatically gain `HasAPI`
D. Become `.usdz` only

**R37-12** (Obj 3.4) `FindSchemaInfo(UsdGeom.Cube).kind` is:
A. `ConcreteTyped`
B. `SingleApplyAPI`
C. `component`
D. `usdc`

**Review answers**

- **R37-1: B.** Review: §37.4.
- **R37-2: A and B.** Review: §37.2.
- **R37-3: B.** Review: §37.3.
- **R37-4: A and B.** Review: §37.5.
- **R37-5: A.** Review: §37.4.
- **R37-6: B.** Review: §37.4.
- **R37-7: B.** Review: §37.3.
- **R37-8: B.** Review: §37.1.
- **R37-9: A and B.** Review: §37.4.
- **R37-10: B.** Review: §37.3.
- **R37-11: B.** Review: §37.5.
- **R37-12: A.** Review: §37.4.

## Further reading

- [S06] OpenUSD API — `UsdSchemaRegistry`, `UsdTyped`, `UsdAPISchemaBase`. https://openusd.org/release/api/usd_page_front.html
- [S03] OpenUSD — Creating a USD schema / `usdGenSchema`. https://openusd.org/release/tut_generating_schemas.html
- Chapter 6 (schema kinds), Chapter 29 (custom attributes), Chapter 36 (plugins).
