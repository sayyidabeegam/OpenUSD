# Chapter 29 — Writing Exporters, Converters, and Importers

> **Exam domain:** Data Exchange (15%) · **Objectives:** 4.5, 4.7, 4.8 · **Study day:** 9 · **Est. time:** 120 min
> **Prerequisites:** Ch 9 (types), Ch 10 (time samples), Ch 13 (extents), Ch 27 (extract → transform → validate), Ch 28 (units, names)

Chapter 27 taught the ideas. This chapter writes the code: a converter you can run, materials and animation, nonstandard data (Obj 4.5), how a DCC importer should walk a stage (Obj 4.8), and **exporter hooks** that enforce structure before you save (Obj 4.7). Lab 25 is the longer version of 29.2.

## Learning goals

- Structure an exporter as extract → transform → write → hook → validate.
- Convert a simple JSON (or OBJ) mesh to USD with units, names, `kind`, `extent`, and `defaultPrim` (Obj 4.7).
- Bind a `UsdPreviewSurface` with `MaterialBindingAPI`, and author animation as time samples.
- Carry nonstandard fields as namespaced custom attributes or `customData` until a schema exists (Obj 4.5).
- Design a DCC importer that reads the composed stage and round-trips extra data (Obj 4.8).
- Register post-write hooks that set `defaultPrim`, compute extents, and fail loudly.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Exporter** | Code in a DCC (or a script) that writes the DCC's scene into USD |
| **Converter** | A standalone program that reads file A and writes USD (or the reverse) |
| **Importer** | Code that reads USD and builds the DCC's own objects |
| **Hook** | A small function the exporter calls at a known moment (usually after write, before save) |
| **Neutral record** | A dict or struct that is neither DCC-native nor USD-native |
| **Custom attribute** | A property not declared by a schema; USDA writes the `custom` keyword |
| **Applied API schema** | A schema you `Apply` so a prim legally holds extra properties (e.g. `MaterialBindingAPI`) |
| **`UsdPreviewSurface`** | The standard preview material shader id for interchange |
| **Round trip** | Export then import (or the reverse) with no unintended loss |

---

## 29.1 Exporter structure

### 1. What is it?

An **exporter** is a program with five jobs in a fixed order: **extract** the source scene, **transform** it into USD-shaped records, **write** prims, run **hooks** that enforce pipeline rules, then **validate**.

### 2. Why do we need it?

A single 400-line "walk Maya and Set() everything" function cannot be tested, cannot report loss, and cannot be reused for a second DCC. Splitting the jobs lets you unit-test the math without opening Maya, and it gives the exam a vocabulary for Obj 4.7.

### 3. Beginner explanation

Think of a **shipping dock**. Extract is packing the warehouse inventory onto carts. Transform is labeling each carton in the customer's language (meters, legal names). Write is loading the truck (the layer). Hooks are the dock checklist (default prim? extents?). Validate is the weigh-station.

*Where the analogy breaks:* the dock can send a carton back to labeling. Validation errors should fix the transform, not get pasted over in the USDA by hand.

### 4. Technical explanation

| Step | Input | Output | Typical calls |
|------|-------|--------|----------------|
| Extract | DCC scene or file | Neutral records | DCC APIs, or `json.load` / an OBJ parser |
| Transform | Records + mapping doc | USD-shaped records | `Tf.MakeValidIdentifier`, unit scale, axis, triangulation policy |
| Write | USD-shaped records | `Usd.Stage` | `Define`, `Create*Attr`, `SetDefaultPrim` |
| Hook | Stage | Same stage, rules applied | `defaultPrim`, `kind`, `ComputeExtentFromPlugins`, strip secrets |
| Validate | Stage | Problem list | `pxr.UsdValidation` (Chapter 30) plus your checks |

Keep DCC imports inside **extract** only. Transform and write should run in a unit test with a fake list of records. That is how you prove Obj 4.7 without a license for the DCC.

Write through `Usd` for schema help (`UsdGeom.Mesh.Define`), or through `Sdf` plus `Sdf.ChangeBlock` when you author tens of thousands of prims (Chapters 8 and 34).

### 5. Mental model

```text
  DCC / file
      | extract
      v
  records  --transform-->  USD records  --write-->  stage
                                                      |
                                         hooks + validate
                                                      v
                                                   layer.usd
```

### 6. Simple example

A fake DCC has two nodes. Extract yields two dicts. Transform fixes names. Write makes two Cubes. A hook sets `defaultPrim` if you forgot it.

### 7. USDA example

What a well-structured exporter should always leave on disk: stage metadata, a `defaultPrim`, and a model `kind`.

```usda
#usda 1.0
(
    defaultPrim = "Set"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "Set" (
    kind = "assembly"
)
{
    def Cube "Box"
    {
        double size = 1
    }
}
```

### 8. Python example

```python
from pxr import Tf, Usd, UsdGeom

DCC_NODES = [
    {"name": "Box One", "size": 1.0},
    {"name": "2nd box", "size": 0.5},
]


def extract(nodes):
    return list(nodes)


def transform(records):
    return [{"name": Tf.MakeValidIdentifier(r["name"]),
             "size": r["size"]} for r in records]


def write(records):
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, "Y")
    UsdGeom.SetStageMetersPerUnit(stage, 1)
    root = UsdGeom.Xform.Define(stage, "/Set")
    root.GetPrim().SetMetadata("kind", "assembly")
    for r in records:
        cube = UsdGeom.Cube.Define(
            stage, root.GetPath().AppendChild(r["name"]))
        cube.GetSizeAttr().Set(r["size"])
    return stage


def hook_default_prim(stage):
    if not stage.GetDefaultPrim():
        stage.SetDefaultPrim(stage.GetPrimAtPath("/Set"))
    return str(stage.GetDefaultPrim().GetPath())


records = transform(extract(DCC_NODES))
stage = write(records)
print("children:", [c.GetName() for c in
                    stage.GetPrimAtPath("/Set").GetChildren()])
print("defaultPrim:", hook_default_prim(stage))
print("steps: extract -> transform -> write -> hook -> validate")
```

**Expected output**

```text
children: ['Box_One', '_nd_box']
defaultPrim: /Set
steps: extract -> transform -> write -> hook -> validate
```

`Tf.MakeValidIdentifier("2nd box")` becomes `_nd_box` (a leading digit is replaced; Chapter 28).

### 9. Real-world use case

A CAD exporter at a factory: extract walks the CAD assembly, transform converts millimeters to meters and names, write authors component Xforms, hooks stamp `kind = component` and extents, validate runs `StageMetadataChecker` on a build server overnight.

### 10. Common mistakes

> [!MISTAKE] Calling DCC APIs from `write()`. Tests then require the DCC. Keep DCC I/O in `extract`.

> [!MISTAKE] Saving before hooks. You ship files with no `defaultPrim`. Call hooks, then `Save()`.

### 11. Exam traps

> [!TRAP] "The exporter is the mapping document." The document is the spec; the exporter is the program (Chapter 27).

> [!TRAP] "Validate, then write." If you validate an empty stage you always pass. Write, hook, then validate.

### 12. Practice questions

**DE-029a** · Obj 4.7 · Difficulty: Easy · Type: Single choice
Which step should be free of DCC API calls so you can unit-test it?

A. Extract
B. Transform
C. The DCC "Export" menu item
D. Opening the DCC file

**DE-029b** · Obj 4.7 · Difficulty: Medium · Type: Single choice
A file is saved with no `defaultPrim`. Which step was skipped?

A. Extract
B. Transform of point units
C. A post-write hook (or the write itself forgot `SetDefaultPrim`)
D. glTF conversion

**Answers**

**DE-029a — B.** Transform works on records. Review: §29.1.

**DE-029b — C.** `defaultPrim` is authored at write/hook time. Review: §29.1, §29.6.

### 13. Exam takeaways

> [!KEY]
> - Five steps: extract, transform, write, hook, validate.
> - Keep DCC I/O in extract.
> - Hooks run after write, before save.
> - `MakeValidIdentifier` belongs in transform, not in a later cleanup by hand.

---

## 29.2 Converting a simple format (JSON/OBJ) to USD

### 1. What is it?

A **converter** reads a non-USD file and writes a USD layer. This section converts a tiny JSON mesh (and shows the same math for OBJ `v` / `f` lines) into a `Mesh` component.

### 2. Why do we need it?

Obj 4.7 is literally "write an exporter or converter to USD." The exam expects you to know the mesh fields (`points`, `faceVertexCounts`, `faceVertexIndices`), units, names, `kind`, `extent`, and `defaultPrim` — not a production OBJ parser.

### 3. Beginner explanation

JSON here is a **packing list**: name, units, points, faces. The converter is a clerk who rewrites the list in USD's form: meters, legal names, a Mesh prim, a bounding box.

*Where the analogy breaks:* OBJ face indices are **1-based**. USD's `faceVertexIndices` are **0-based**. Forgetting to subtract 1 is the classic converter bug.

### 4. Technical explanation

Minimum viable mesh converter (verified on USD 26.08):

1. Scale points by the source unit (`cm` → × 0.01 if the stage is meters).
2. `Tf.MakeValidIdentifier` on the object name.
3. `UsdGeom.SetStageUpAxis` / `SetStageMetersPerUnit`.
4. `UsdGeom.Mesh.Define`; set `points`, `faceVertexCounts`, `faceVertexIndices`.
5. `subdivisionScheme = none` for a hard-surface crate (so the mesh is not Catmull–Clark subdivided).
6. `ComputeExtentFromPlugins` then `CreateExtentAttr` (it does not author by itself, Chapter 13).
7. `SetDefaultPrim`, `kind = component`.
8. Carry extra source fields as custom attributes (29.4).

OBJ: `o` → prim name, `v` → `points`, `f` → faces (`int(token.split("/")[0]) - 1` to drop optional `vt`/`vn` and convert to 0-based). Ignore `l` (lines) and `s` (smoothing) unless your mapping document says otherwise (Chapter 27).

### 5. Mental model

```text
  JSON/OBJ                     USD
  name "Crate Box"     ->      /Crate_Box   (identifier)
  units cm, pt 100     ->      points in meters (1.0)
  faces [[0,1,2,3]]    ->      counts [4], indices [0,1,2,3]
  OBJ f 1 2 3          ->      indices [0,1,2]   (minus one)
```

### 6. Simple example

A 100 cm × 50 cm quad becomes a 1 m × 0.5 m Mesh named `/Crate_Box/Geo`. Point `(100, 0, 0)` in cm becomes `(1, 0, 0)` in meters.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Crate_Box"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "Crate_Box" (
    kind = "component"
)
{
    def Mesh "Geo"
    {
        float3[] extent = [(0, 0, 0), (1, 0.5, 0)]
        int[] faceVertexCounts = [4]
        int[] faceVertexIndices = [0, 1, 2, 3]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (1, 0.5, 0), (0, 0.5, 0)]
        uniform token subdivisionScheme = "none"
        custom string factory:partId = "CR-7"
    }
}
```

### 8. Python example

```python
from pxr import Gf, Sdf, Tf, Usd, UsdGeom

SRC = {
    "name": "Crate Box",
    "units": "cm",
    "up": "Y",
    "points": [[0, 0, 0], [100, 0, 0], [100, 50, 0], [0, 50, 0]],
    "faces": [[0, 1, 2, 3]],
    "partId": "CR-7",
}
TO_M = {"cm": 0.01, "m": 1.0, "mm": 0.001}


def json_to_usd(src):
    k = TO_M[src["units"]]
    name = Tf.MakeValidIdentifier(src["name"])
    points = [Gf.Vec3f(p[0] * k, p[1] * k, p[2] * k) for p in src["points"]]
    counts = [len(f) for f in src["faces"]]
    indices = [i for f in src["faces"] for i in f]
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, src["up"])
    UsdGeom.SetStageMetersPerUnit(stage, 1)
    root = UsdGeom.Xform.Define(stage, "/" + name)
    stage.SetDefaultPrim(root.GetPrim())
    root.GetPrim().SetMetadata("kind", "component")
    mesh = UsdGeom.Mesh.Define(stage, root.GetPath().AppendChild("Geo"))
    mesh.CreatePointsAttr(points)
    mesh.CreateFaceVertexCountsAttr(counts)
    mesh.CreateFaceVertexIndicesAttr(indices)
    mesh.CreateSubdivisionSchemeAttr("none")
    ext = UsdGeom.Boundable.ComputeExtentFromPlugins(
        mesh, Usd.TimeCode.Default())
    mesh.CreateExtentAttr(ext)
    mesh.GetPrim().CreateAttribute(
        "factory:partId", Sdf.ValueTypeNames.String).Set(src["partId"])
    return stage


stage = json_to_usd(SRC)
mesh = UsdGeom.Mesh(stage.GetPrimAtPath("/Crate_Box/Geo"))
print("defaultPrim:", stage.GetDefaultPrim().GetName())
print("kind:", stage.GetDefaultPrim().GetMetadata("kind"))
print("up/units:", UsdGeom.GetStageUpAxis(stage),
      UsdGeom.GetStageMetersPerUnit(stage))
print("points[1]:", tuple(mesh.GetPointsAttr().Get()[1]))
print("counts:", list(mesh.GetFaceVertexCountsAttr().Get()))
print("extent:", [tuple(v) for v in mesh.GetExtentAttr().Get()])
print("partId:", mesh.GetPrim().GetAttribute("factory:partId").Get())
print("name was:", SRC["name"], "->", Tf.MakeValidIdentifier(SRC["name"]))

OBJ = """o Tiny
v 0 0 0
v 1 0 0
v 0 1 0
f 1 2 3
"""


def parse_obj(text):
    name, pts, faces = "Mesh", [], []
    for line in text.splitlines():
        bits = line.split()
        if not bits:
            continue
        if bits[0] == "o":
            name = Tf.MakeValidIdentifier(bits[1])
        elif bits[0] == "v":
            pts.append(Gf.Vec3f(*map(float, bits[1:4])))
        elif bits[0] == "f":
            faces.append([int(b.split("/")[0]) - 1 for b in bits[1:]])
    return name, pts, faces


n, pts, faces = parse_obj(OBJ)
print("OBJ name:", n, "nPoints:", len(pts), "first face:", faces[0])
```

**Expected output**

```text
defaultPrim: Crate_Box
kind: component
up/units: Y 1.0
points[1]: (1.0, 0.0, 0.0)
counts: [4]
extent: [(0.0, 0.0, 0.0), (1.0, 0.5, 0.0)]
partId: CR-7
name was: Crate Box -> Crate_Box
OBJ name: Tiny nPoints: 3 first face: [0, 1, 2]
```

The OBJ face `f 1 2 3` became `[0, 1, 2]`. Lab 25 asks you to wire `parse_obj` into `json_to_usd`-style authoring.

### 9. Real-world use case

A catalog team publishes furniture as OBJ from a 1990s CAD tool. A nightly converter builds `chair_geo.usda` with meters, Y-up, `kind = component`, and extents so usdview framing works on day one.

### 10. Common mistakes

> [!MISTAKE] Leaving OBJ indices 1-based. Faces then point at the wrong vertices (or crash). Always subtract 1.

> [!MISTAKE] Forgetting `extent`. The mesh is valid but viewers frame nothing (Chapter 13).

### 11. Exam traps

> [!TRAP] "`ComputeExtentFromPlugins` writes the file." It returns an array. You `Set`.

> [!TRAP] "JSON converters do not need `metersPerUnit`." Every USD layer you publish should declare units and up axis (Chapter 28).

### 12. Practice questions

**DE-029c** · Obj 4.7 · Difficulty: Medium · Type: Single choice
OBJ line `f 1 2 3` should become `faceVertexIndices`:

A. `[1, 2, 3]`
B. `[0, 1, 2]`
C. `[3, 2, 1]`
D. `[(1, 2, 3)]`

**DE-029d** · Obj 4.7 · Difficulty: Easy · Type: Select two.
A JSON crate is authored in centimeters onto a meters stage. Point `(100, 0, 0)` should:

A. Stay `100`
B. Become `1` in `points`
C. Have `metersPerUnit = 1` (or 0.01 if you keep cm as scene units, declared)
D. Omit `extent`

**Answers**

**DE-029c — B.** OBJ is 1-based. Review: §29.2.

**DE-029d — B and C.** Scale **or** declare cm; do not leave units implicit. Review: §29.2, Ch 28.

### 13. Exam takeaways

> [!KEY]
> - Mesh trio: `points`, `faceVertexCounts`, `faceVertexIndices`.
> - OBJ faces minus one; JSON faces already 0-based.
> - Always: identifier, units, upAxis, defaultPrim, kind, extent.
> - Extra source fields: namespaced custom attributes.

---

## 29.3 Materials and animation mapping

### 1. What is it?

After geometry, a converter maps **materials** (usually to `UsdPreviewSurface`) and **animation** (to attribute time samples or xformOp samples).

### 2. Why do we need it?

A crate with no material and a robot with no motion fail interchange reviews. Obj 4.1/4.2 already mapped PreviewSurface to glTF; this section authors the USD side.

### 3. Beginner explanation

A material is a **paint recipe**. `UsdPreviewSurface` is the recipe card every DCC is supposed to understand. Animation is a **flip-book** of translates (or any attribute) at time codes, not a Maya animation curve node.

*Where the analogy breaks:* DCC curves have tangents. USD time samples are just values at times (splines exist, Chapter 10, but samples are the interchange core). You lose Bezier handles unless you store them as extra data (29.4).

### 4. Technical explanation

**Material (verified 26.08):**

1. `UsdShade.Material.Define(stage, path)`
2. `UsdShade.Shader.Define` with `CreateIdAttr("UsdPreviewSurface")`
3. `CreateInput("diffuseColor", Color3f)` (and roughness, metallic, opacity as needed)
4. `CreateOutput("surface")` on the shader; `material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")`
5. **`UsdShade.MaterialBindingAPI.Apply(meshPrim)` then `.Bind(material)`**. Skipping `Apply` still often binds, but validators require the applied schema.

> [!VERSION] Verified on USD 26.08. Since USD 22.11, validators expect `MaterialBindingAPI` to be applied before binding. Always `Apply`.

**Animation:**

- `xformable.AddTranslateOp().Set(value, time)` authors samples.
- Linear interpolation is the stage default (Chapter 10): samples at 1 and 11 yield the midpoint at time 6.
- Do not put the rest pose only as a default if the DCC also has a key at the start frame; pick one encoding and document it.

### 5. Mental model

```text
  /Prop/Looks/Paint          Material
       Preview               Shader id=UsdPreviewSurface
  /Prop/Geo  --Bind-->       Paint   (MaterialBindingAPI applied)

  translate.timeSamples { 1: (0,0,0), 11: (2,0,0) }
```

### 6. Simple example

A red PreviewSurface bound to a quad. The parent Xform moves from x=0 at time 1 to x=2 at time 11.

### 7. USDA example

```usda
#usda 1.0

def Xform "Prop"
{
    double3 xformOp:translate.timeSamples = {
        1: (0, 0, 0),
        11: (2, 0, 0)
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]

    def Mesh "Geo" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {
        rel material:binding = </Prop/Looks/Paint>
    }

    def "Looks"
    {
        def Material "Paint"
        {
            token outputs:surface.connect = </Prop/Looks/Paint/Preview.outputs:surface>
            def Shader "Preview"
            {
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.8, 0.1, 0.1)
                token outputs:surface
            }
        }
    }
}
```

### 8. Python example

```python
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

st = Usd.Stage.CreateInMemory()
UsdGeom.SetStageUpAxis(st, "Y")
UsdGeom.SetStageMetersPerUnit(st, 1)
root = UsdGeom.Xform.Define(st, "/Prop")
st.SetDefaultPrim(root.GetPrim())
mesh = UsdGeom.Mesh.Define(st, "/Prop/Geo")
mesh.CreatePointsAttr([Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0),
                       Gf.Vec3f(1, 1, 0), Gf.Vec3f(0, 1, 0)])
mesh.CreateFaceVertexCountsAttr([4])
mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
op = UsdGeom.Xformable(root).AddTranslateOp()
op.Set(Gf.Vec3d(0, 0, 0), 1)
op.Set(Gf.Vec3d(2, 0, 0), 11)
mat = UsdShade.Material.Define(st, "/Prop/Looks/Paint")
sh = UsdShade.Shader.Define(st, "/Prop/Looks/Paint/Preview")
sh.CreateIdAttr("UsdPreviewSurface")
sh.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
    (0.8, 0.1, 0.1))
sh.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat.CreateSurfaceOutput().ConnectToSource(sh.ConnectableAPI(), "surface")
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
bound = UsdShade.MaterialBindingAPI(mesh.GetPrim()).ComputeBoundMaterial()[0]
print("material:", bound.GetPath())
print("shader id:", sh.GetIdAttr().Get())
print("translate @1:", op.Get(1), "@11:", op.Get(11), "@6:", op.Get(6))
print("has MaterialBindingAPI:",
      mesh.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
```

**Expected output**

```text
material: /Prop/Looks/Paint
shader id: UsdPreviewSurface
translate @1: (0, 0, 0) @11: (2, 0, 0) @6: (1, 0, 0)
has MaterialBindingAPI: True
```

Time 6 is 1.0 because linear interpolation is the default.

### 9. Real-world use case

A game exporter writes PreviewSurface for the engine's debug view and also writes a custom `game:shaderId` (29.4) for the real engine shader. Animation of the root Xform is samples at 30 fps; blend-shape weights become `primvars` samples.

### 10. Common mistakes

> [!MISTAKE] Binding without `MaterialBindingAPI.Apply`. Looks fine in a quick test; `usdchecker` / UsdValidation fails.

> [!MISTAKE] Authoring animation only as a default translate, then wondering why the shot does not play. Playback queries numeric times.

### 11. Exam traps

> [!TRAP] "`info:id = UsdPreviewSurface` goes on the Material prim." It goes on the **Shader**.

> [!TRAP] "Connections use relationship `rel`." Shader connections are `outputs:surface.connect` on the Material.

### 12. Practice questions

**DE-029e** · Obj 4.7 · Difficulty: Medium · Type: Select two.
A correct PreviewSurface bind includes:

A. `Shader` with `info:id = UsdPreviewSurface`
B. `MaterialBindingAPI.Apply` then `Bind`
C. Putting `info:id` on the Mesh
D. Skipping the Material prim

**DE-029f** · Obj 4.7 · Difficulty: Easy · Type: Single choice
Translate samples at 1=(0,0,0) and 11=(2,0,0). `Get(6)` with linear interpolation is:

A. (0, 0, 0)
B. (1, 0, 0)
C. (2, 0, 0)
D. no value

**Answers**

**DE-029e — A and B.** Review: §29.3.

**DE-029f — B.** Midpoint. Review: §29.3, Ch 10.

### 13. Exam takeaways

> [!KEY]
> - PreviewSurface lives on a Shader under a Material.
> - Always `MaterialBindingAPI.Apply` before `Bind`.
> - Animation interchange = time samples.
> - Curve tangents are extra data, not USD samples.

---

## 29.4 Nonstandard data via custom attributes or schemas

### 1. What is it?

Source scenes have fields USD has no built-in schema for: a factory part number, a CAD document GUID, a proprietary flag. Obj 4.5 says to **use USD schemas** to carry them. Until you generate a schema (Chapter 37), you author **namespaced custom attributes** and/or `customData`, then graduate to an API schema.

### 2. Why do we need it?

If you drop those fields, the round trip fails and downstream tools guess. If you stuff them into random un-namespaced names, they collide with future schemas. A namespace (`factory:partId`) is the contract.

### 3. Beginner explanation

A custom attribute is a **sticky note** on the prim: "part id PN-42." A schema is a **printed form** with official boxes. Start with sticky notes in a named pad (`factory:`). When the factory standardizes, print the form (`usdGenSchema`, Chapter 37).

*Where the analogy breaks:* sticky notes still round-trip. They are real properties. They just have no generated C++/Python accessors and no validator until you register a schema.

### 4. Technical explanation

Verified on USD 26.08:

- `prim.CreateAttribute("factory:partId", Sdf.ValueTypeNames.String)` authors `custom string factory:partId`. `IsCustom()` is True. `GetNamespace()` is `"factory"`.
- `prim.SetCustomDataByKey("sourceApp", "AcmeCAD 12")` stores dictionary metadata, not a typed attribute. Good for provenance; bad for values you will animate or bind.
- **Applied API schemas** (like `MaterialBindingAPI`) are already "using a schema during import/export." That *is* Obj 4.5 for bindings.
- When several DCCs must share the same extra fields, write `schema.usda` and generate a codeless or codeful API schema (Chapter 37). The exporter then calls `FactoryAPI.Apply(prim).CreatePartIdAttr().Set(...)`.
- Do not invent a second `points` attribute. If a built-in schema already has the concept, use it.

Decision table:

| Need | Mechanism |
|------|-----------|
| One pipeline-local string | Namespaced custom attribute |
| Provenance blob | `customData` / `assetInfo` (Chapter 12) |
| Official interchange field | API or IsA schema (Chapter 37) |
| Material / collection / geom subset | Existing applied API schemas |

### 5. Mental model

```text
  CAD "PartNumber"  -->  custom factory:partId     (today)
                    -->  FactoryAPI.partId         (when the schema ships)

  CAD "native node id" --> customData["sourceApp"]  (not an attribute)
```

### 6. Simple example

`/Part` gets `factory:partId = "PN-42"` and `customData sourceApp = "AcmeCAD 12"`. `IsCustom()` is True. `HasAPI(MaterialBindingAPI)` is False until you apply it.

### 7. USDA example

```usda
#usda 1.0

def Xform "Part" (
    customData = {
        string sourceApp = "AcmeCAD 12"
    }
)
{
    custom string factory:partId = "PN-42"
}
```

Line notes: the `custom` keyword marks a non-schema attribute. `customData` is metadata, not a property you `GetAttribute`.

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/Part").GetPrim()
attr = prim.CreateAttribute("factory:partId", Sdf.ValueTypeNames.String)
attr.Set("PN-42")
prim.SetCustomDataByKey("sourceApp", "AcmeCAD 12")
print("IsCustom:", attr.IsCustom())
print("name:", attr.GetName(), "namespace:", attr.GetNamespace())
print("value:", attr.Get())
print("sourceApp:", prim.GetCustomDataByKey("sourceApp"))
print("HasAPI MaterialBindingAPI:",
      prim.HasAPI(UsdShade.MaterialBindingAPI))
```

**Expected output**

```text
IsCustom: True
name: factory:partId namespace: factory
value: PN-42
sourceApp: AcmeCAD 12
HasAPI MaterialBindingAPI: False
```

Xform also stores a schema `userDocBrief` inside `customData` if you dump the whole dict; read a key, do not print the whole bag.

### 9. Real-world use case

An automotive CAD exporter writes `vehicle:vin` as a custom string on the assembly root on day one. Six months later the studio publishes a `VehicleAPI` schema; the exporter switches to `VehicleAPI.Apply` and the same files remain readable because the attribute name was planned as `vehicle:vin`.

### 10. Common mistakes

> [!MISTAKE] `CreateAttribute("points", ...)` on a Mesh for a second point cloud. You collide with `UsdGeom.Mesh.points`. Use a namespace.

> [!MISTAKE] Putting the part number only in the prim name (`Bolt_PN42`). Names then cannot change without breaking references.

### 11. Exam traps

> [!TRAP] "Custom attributes are illegal in USD." They are legal; `custom` is the keyword.

> [!TRAP] "Obj 4.5 requires `usdGenSchema` on the exam machine." You must *know* when to use a schema versus a custom attribute. `usd-core` does not ship `usdGenSchema` (V-004).

### 12. Practice questions

**DE-029g** · Obj 4.5 · Difficulty: Medium · Type: Single choice
A CAD GUID must round-trip and might later become an official schema. Best authoring today?

A. `custom string factory:guid = "..."` (stable namespace)
B. Overwrite `prim.GetName()`
C. Store it in `points[0].x`
D. Drop it

**DE-029h** · Obj 4.5 · Difficulty: Easy · Type: Select two.
Which are "using a schema during import/export"?

A. `MaterialBindingAPI.Apply` then bind
B. `UsdGeom.Mesh.Define` for OBJ faces
C. A random untyped `def "Foo"` with no properties
D. Ignoring `upAxis`

**Answers**

**DE-029g — A.** Namespaced custom attribute, schema later. Review: §29.4.

**DE-029h — A and B.** Built-in and applied schemas both count. Review: §29.4, §29.3.

### 13. Exam takeaways

> [!KEY]
> - Namespace extra fields (`factory:`). `IsCustom()` will be True.
> - `customData` is metadata; attributes are for typed values.
> - Applied APIs (MaterialBindingAPI) already satisfy "use a schema."
> - Graduate sticky notes to `schema.usda` when several tools share them (Ch 37).

---

## 29.5 Importer design in a DCC

### 1. What is it?

An **importer** reads a USD stage and builds DCC-native objects (Maya nodes, Houdini SOPs, engine actors). Obj 4.8 is "write or extend a USD importer in a DCC." You will not open Maya here; you will design the walk and prove it by converting USD **back** into records.

### 2. Why do we need it?

Export without import is a one-way dump. A DCC that cannot round-trip custom attributes, time samples, or references will silently destroy the pipeline the next time an artist hits Save.

### 3. Beginner explanation

If the exporter is a clerk packing boxes, the importer is the clerk **unpacking** them onto the DCC's shelves. The shelf layout is the DCC data model. Some USD boxes (variants, payloads) have no shelf; you document the loss (Chapter 27) or store the box unopened (`customData`).

*Where the analogy breaks:* you usually unpack the **composed** stage (`Usd.Stage`), not each layer. Composition has already mixed opinions. A high-end importer may also read specs (`Sdf`) to round-trip layer structure; that is an extension, not the default.

### 4. Technical explanation

Design checklist for a DCC importer (Obj 4.8):

1. **Open** the stage (`Usd.Stage.Open`). Decide `LoadAll` vs `LoadNone` (Chapter 17).
2. **Walk** `Traverse()` for defined, active, non-abstract prims. Use `TraverseInstanceProxies()` only if the DCC needs unique nodes per instance (usually it should instance instead, Chapter 24).
3. **Map types:** `IsA(UsdGeom.Mesh)` → DCC mesh, `IsA(UsdGeom.Xform)` → group, `IsA(UsdShade.Material)` → DCC material, unknown → group + custom attrs.
4. **Read data at the right time:** `attr.Get(time)` for the DCC current frame; `GetTimeSamples()` to build curves.
5. **Materials:** `MaterialBindingAPI.ComputeBoundMaterial()`.
6. **Extra fields:** read namespaced custom attributes and `customData` back into DCC extra attributes so the next export restores them.
7. **References:** either create DCC instances / references, or flatten (lossy). Do not explode every reference into unique copies by accident.
8. **Report loss** (lights the DCC cannot draw, variants not represented, etc.).

Extending an existing importer usually means adding a type case ("when `IsA(MySchema)`, build this DCC node") or a post-hook that copies custom namespaces. You rarely rewrite the walker.

### 5. Mental model

```text
  stage.Traverse()
       |  IsA Mesh?  -->  DCC mesh + points/faces
       |  IsA Xform? -->  DCC group + xformOps at time
       |  Has factory:* --> DCC extra attributes
       |  unknown     --> group + dump properties to extras
```

### 6. Simple example

Open the crate stage from 29.2. The importer emits one record: path `/Crate_Box/Geo`, 4 points, `partId CR-7`, and the stage `upAxis`.

### 7. USDA example

The importer's *input* is the crate USDA from 29.2. No new syntax. What it must not drop: `factory:partId`, `upAxis`, `kind`.

### 8. Python example

```python
from pxr import Gf, Sdf, Tf, Usd, UsdGeom

SRC = {
    "name": "Crate Box", "units": "cm", "up": "Y",
    "points": [[0, 0, 0], [100, 0, 0], [100, 50, 0], [0, 50, 0]],
    "faces": [[0, 1, 2, 3]], "partId": "CR-7",
}
TO_M = {"cm": 0.01, "m": 1.0, "mm": 0.001}


def json_to_usd(src):
    k = TO_M[src["units"]]
    name = Tf.MakeValidIdentifier(src["name"])
    points = [Gf.Vec3f(p[0] * k, p[1] * k, p[2] * k) for p in src["points"]]
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, src["up"])
    UsdGeom.SetStageMetersPerUnit(stage, 1)
    root = UsdGeom.Xform.Define(stage, "/" + name)
    stage.SetDefaultPrim(root.GetPrim())
    mesh = UsdGeom.Mesh.Define(stage, root.GetPath().AppendChild("Geo"))
    mesh.CreatePointsAttr(points)
    mesh.CreateFaceVertexCountsAttr([len(f) for f in src["faces"]])
    mesh.CreateFaceVertexIndicesAttr([i for f in src["faces"] for i in f])
    mesh.GetPrim().CreateAttribute(
        "factory:partId", Sdf.ValueTypeNames.String).Set(src["partId"])
    return stage


def import_meshes(stage):
    records = []
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Mesh):
            mesh = UsdGeom.Mesh(prim)
            records.append({
                "path": str(prim.GetPath()),
                "nPoints": len(mesh.GetPointsAttr().Get()),
                "partId": prim.GetAttribute("factory:partId").Get(),
            })
    return records


st = json_to_usd(SRC)
print("imported meshes:", import_meshes(st))
print("upAxis:", UsdGeom.GetStageUpAxis(st))
```

**Expected output**

```text
imported meshes: [{'path': '/Crate_Box/Geo', 'nPoints': 4, 'partId': 'CR-7'}]
upAxis: Y
```

`partId` survived the round trip because the exporter stored it and the importer asked for it.

### 9. Real-world use case

A DCC vendor extends its USD importer with a `case` for `UsdLux.RectLight` that used to become an empty locator. After the extension, lights round-trip; the mapping document's "RectLight → dropped" row is updated to "RectLight → area light."

### 10. Common mistakes

> [!MISTAKE] Walking only the root layer (`Sdf`) and ignoring references. You import an empty assembly. Walk the composed stage unless you are a layer editor.

> [!MISTAKE] Turning every native instance into a unique DCC mesh. Memory explodes. Prefer DCC instancing from the prototype.

### 11. Exam traps

> [!TRAP] "Importers must flatten." Flattening is a choice. It loses composition (Chapter 22).

> [!TRAP] "Unknown prim types should error and abort." Better: create a group, copy extra properties, report a warning, continue.

### 12. Practice questions

**DE-029i** · Obj 4.8 · Difficulty: Medium · Type: Single choice
A DCC importer should read geometry from:

A. The composed `Usd.Stage` (then optionally inspect specs)
B. Only `GetRootLayer()` prim specs, never following references
C. Hydra only
D. The session layer only

**DE-029j** · Obj 4.8 · Difficulty: Medium · Type: Select two.
Extending an importer to support a studio schema usually means:

A. Adding an `IsA(StudioAPI)` / applied-API case in the type map
B. Copying `studio:*` attributes into DCC extras
C. Deleting `MaterialBindingAPI` handling
D. Forcing `LoadNone` always

**Answers**

**DE-029i — A.** Composition is the scene. Review: §29.5.

**DE-029j — A and B.** Review: §29.5, §29.4.

### 13. Exam takeaways

> [!KEY]
> - Importers walk the composed stage; map `IsA` types to DCC nodes.
> - Round-trip custom namespaces and `customData`.
> - Keep references/instances as shares, not unique copies, by default.
> - Extending = new type case + extras, not a rewrite.

---

## 29.6 Exporter hooks

### 1. What is it?

An **exporter hook** is a function the exporter calls at a fixed time — almost always after prims are written and before `Save()` — to enforce pipeline structure: `defaultPrim`, `kind`, extents, naming, stripping internal data.

### 2. Why do we need it?

Every exporter forgets something. Hooks make the rules **one list** that CAD, DCC, and the JSON converter all run. Chapter 34 returns to hooks in a full pipeline (notices, flatten). Here you write two hooks and see them fix a stage.

### 3. Beginner explanation

Hooks are the **pre-flight checklist**: doors closed, extents filled, default prim set. The plane (the file) does not taxi until the list is green.

*Where the analogy breaks:* a hook that *silently* drops unknown attributes is a data-loss bug, not a checklist. Hooks should author missing structure or **fail**, not invent geometry.

### 4. Technical explanation

Good hooks (verified pattern):

| Hook | Does | Fails when |
|------|------|------------|
| `hook_default_prim` | `SetDefaultPrim` to the first defined root if missing | No defined root prim |
| `hook_extents` | `ComputeExtentFromPlugins` + `Set` on every Boundable | Extent compute returns empty and the prim should be visible |
| `hook_kind` | Set `component` on asset roots that have no kind | Conflicting kind already authored (do not clobber; warn) |
| `hook_strip_internal` | Remove `debug:*` attributes | — (log how many you stripped) |

Properties of a hook:

- **Idempotent:** running twice does not change a good stage.
- **No DCC dependency:** it takes a `Usd.Stage`.
- **Ordered:** extents after meshes exist; `defaultPrim` after roots exist.
- Chapter 34 adds change notices (`Tf.Notice`) for live DCC exporters; a batch converter just calls the list.

### 5. Mental model

```text
  write()  -->  [defaultPrim] --> [extents] --> [kind] --> validate --> Save
```

### 6. Simple example

A stage with `/Crate/Geo` as a Mesh and **no** `defaultPrim`. `hook_default_prim` sets `/Crate`. `hook_extents` authors the triangle's extent.

### 7. USDA example

*After hooks, the layer has the missing structure. Before hooks, `/Crate` had no `defaultPrim` and the mesh had no `extent`.*

```usda
#usda 1.0
(
    defaultPrim = "Crate"
)

def "Crate"
{
    def Mesh "Geo"
    {
        float3[] extent = [(0, 0, 0), (1, 1, 0)]
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    }
}
```

### 8. Python example

```python
from pxr import Gf, Sdf, Usd, UsdGeom


def hook_default_prim(stage):
    if not stage.GetDefaultPrim():
        roots = [p for p in stage.GetPseudoRoot().GetChildren()
                 if p.GetSpecifier() == Sdf.SpecifierDef]
        if roots:
            stage.SetDefaultPrim(roots[0])
    return bool(stage.GetDefaultPrim())


def hook_extents(stage):
    n = 0
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Boundable):
            b = UsdGeom.Boundable(prim)
            ext = UsdGeom.Boundable.ComputeExtentFromPlugins(
                b, Usd.TimeCode.Default())
            if ext:
                b.CreateExtentAttr().Set(ext)
                n += 1
    return n


st = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(st, "/Crate/Geo")
mesh.CreatePointsAttr(
    [Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)])
mesh.CreateFaceVertexCountsAttr([3])
mesh.CreateFaceVertexIndicesAttr([0, 1, 2])
print("defaultPrim before:", bool(st.GetDefaultPrim()))
print("hook_default_prim:", hook_default_prim(st),
      "now:", st.GetDefaultPrim().GetPath())
print("extents authored:", hook_extents(st))
print("extent:", [tuple(v) for v in mesh.GetExtentAttr().Get()])
```

**Expected output**

```text
defaultPrim before: False
hook_default_prim: True now: /Crate
extents authored: 1
extent: [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)]
```

`Define("/Crate/Geo")` created a typeless `/Crate` parent; the hook picked that defined root.

### 9. Real-world use case

A studio's "USD export" button in four DCCs all `import studio_export_hooks` and run the same list. When the pipeline adds "every component must have `assetInfo['identifier']`", one hook update fixes all four exporters.

### 10. Common mistakes

> [!MISTAKE] A hook that overwrites an authored `kind` with `component`. Assemblies then become components. Warn, do not clobber.

> [!MISTAKE] Computing extents before points are set. The hook returns empty; you skip the prim. Order the hook list after geometry authoring.

### 11. Exam traps

> [!TRAP] "Hooks are Tf.Notice listeners." Notices are Chapter 34. A hook can be an ordinary function called from the exporter.

> [!TRAP] "Validation is a hook that deletes prims until usdchecker is quiet." Validation **reports**. Hooks **author structure**.

### 12. Practice questions

**DE-029k** · Obj 4.7 · Difficulty: Medium · Type: Single choice
When should `hook_extents` run?

A. Before extract
B. After mesh points/faces are authored, before save
C. Inside `Tf.MakeValidIdentifier`
D. Only in the DCC UI thread

**DE-029l** · Obj 4.7 · Difficulty: Easy · Type: Select two.
A healthy exporter hook is:

A. Idempotent
B. Independent of the DCC
C. Allowed to invent missing vertices
D. Required to flatten the stage

**Answers**

**DE-029k — B.** Review: §29.6.

**DE-029l — A and B.** Review: §29.6.

### 13. Exam takeaways

> [!KEY]
> - Hooks enforce structure after write, before save.
> - Typical: `defaultPrim`, extents, kind, strip internals.
> - Idempotent, DCC-free, no silent data invention.
> - Shared hook lists keep many exporters consistent (Ch 34 continues).

---

## Chapter lab(s)

Lab 25 (JSON/OBJ → USD converter) expands 29.2 into a file on disk with validation. Lab 26 covers units if your converter's scale is wrong. Lab 34 in Chapter 40 binds PreviewSurface more fully.

## USDA reading exercises

**Exercise 29-A.** An OBJ face line is `f 4/1/1 5/2/1 6/3/1`. What three integers go into `faceVertexIndices` for that face?

**Exercise 29-B.** A converter writes a Mesh but no `defaultPrim`, no `extent`, and binds a material without applying `MaterialBindingAPI`. Name the hook or call that fixes each of the three problems.

**Answers**

**29-A.** `4, 5, 6` minus one → `[3, 4, 5]`. The `/vt/vn` parts are ignored for this field.

**29-B.** `hook_default_prim` / `SetDefaultPrim`; `hook_extents` / `ComputeExtentFromPlugins` then `Set`; `MaterialBindingAPI.Apply` then `Bind`.

---

## Chapter review

### Summary

- Exporter = extract → transform → write → hook → validate. DCC I/O stays in extract.
- Converter (Obj 4.7): scale units, `MakeValidIdentifier`, Mesh fields, `kind`, `defaultPrim`, extent. OBJ faces are 1-based.
- Materials: Shader `UsdPreviewSurface` + `MaterialBindingAPI.Apply` + `Bind`. Animation: time samples.
- Nonstandard data (Obj 4.5): namespaced custom attributes, then a real schema (Ch 37). Applied APIs already count.
- Importer (Obj 4.8): walk the composed stage, map `IsA`, round-trip extras, do not flatten by default.
- Hooks: idempotent, DCC-free, after write; they author structure, they do not invent geometry.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Obj 4.7 | Write a converter: mesh + metadata + hooks |
| `f 1 2 3` | Indices `[0, 1, 2]` |
| No `defaultPrim` | Write step or `hook_default_prim` |
| Empty framing in usdview | Missing `extent` hook |
| `MaterialBindingAPI` | `Apply` then `Bind` |
| CAD GUID | `factory:guid` custom attr (Obj 4.5) |
| Obj 4.8 | Walk composed stage; extend by type case |
| "Exporter hook" | Function after write, before save |
| `ComputeExtentFromPlugins` | Returns values; you `Set` |

### Review questions

**R29-01** · Obj 4.7 · Single choice
The transform step of an exporter should:
A. Call Maya's mesh API
B. Convert records (units, names) with no DCC
C. Open usdview
D. Flatten the stage

**R29-02** · Obj 4.7 · Single choice
JSON point `(100,0,0)` in cm, stage in meters. Stored `points` value?
A. (100, 0, 0)
B. (1, 0, 0)
C. (0.1, 0, 0)
D. (10, 0, 0)

**R29-03** · Obj 4.7 · Single choice
`subdivisionScheme = none` on a crate mesh means:
A. The file is invalid
B. Do not Catmull–Clark subdivide
C. No faces
D. No extent

**R29-04** · Obj 4.7 · Select two.
Required Mesh topology attributes:
A. `points`
B. `faceVertexCounts` and `faceVertexIndices`
C. `clipTimes`
D. `info:id`

**R29-05** · Obj 4.7 · Single choice
PreviewSurface `info:id` is authored on:
A. The Mesh
B. The Shader
C. The stage metadata
D. `customData` only

**R29-06** · Obj 4.5 · Single choice
`CreateAttribute("factory:partId", String)` makes:
A. An illegal property
B. A custom namespaced attribute
C. A relationship
D. A variant

**R29-07** · Obj 4.5 · Single choice
`MaterialBindingAPI.Apply` during export is:
A. Optional decoration
B. Using a schema for interchange (Obj 4.5) and required by validators
C. Deprecated in 26.08
D. Only for payloads

**R29-08** · Obj 4.8 · Single choice
A DCC importer that ignores references and reads only the root layer will:
A. See the full composed assembly
B. Miss referenced geometry
C. Auto-load payloads as meshes
D. Convert glTF

**R29-09** · Obj 4.8 · Select two.
A round-trip importer should restore:
A. `factory:*` custom attributes
B. `upAxis` / `metersPerUnit`
C. `/__Prototype_1` as a saved prim
D. Session-layer mute state

**R29-10** · Obj 4.7 · Single choice
`hook_default_prim` found no defined root. It should:
A. Invent `/World`
B. Fail/report, not save a useless file
C. Set `defaultPrim` to `/__Prototype_1`
D. Mute the root layer

**R29-11** · Obj 4.7 · Single choice
Time samples at 1 and 11, `Get(6)` linear, values 0 and 2 on X:
A. 0
B. 1
C. 2
D. Default only

**R29-12** · Obj 4.5 · Single choice
When several DCCs must share the same extra fields officially:
A. Keep inventing new un-namespaced names
B. Publish an API/IsA schema (Chapter 37)
C. Put the fields in the prim path
D. Store them in `extent`

### Review answers

**R29-01 — B.** Review: §29.1.

**R29-02 — B.** × 0.01. Review: §29.2.

**R29-03 — B.** Review: §29.2.

**R29-04 — A and B.** Review: §29.2.

**R29-05 — B.** Review: §29.3.

**R29-06 — B.** Review: §29.4.

**R29-07 — B.** Review: §29.3, §29.4.

**R29-08 — B.** Review: §29.5.

**R29-09 — A and B.** Prototypes are runtime (C). Review: §29.5, Ch 24.

**R29-10 — B.** Review: §29.6.

**R29-11 — B.** Review: §29.3.

**R29-12 — B.** Review: §29.4, Ch 37.

## Further reading

- [S06] OpenUSD API — `UsdGeomMesh`, `UsdShadeMaterial`, `UsdShadeMaterialBindingAPI`: https://openusd.org/release/api/index.html
- [S14] NVIDIA Learn OpenUSD — data exchange modules: https://docs.nvidia.com/learn-openusd/latest/index.html
- [S08] USD FAQ — identifiers, upAxis, metersPerUnit: https://openusd.org/release/usdfaq.html
- [S16] Principles of Scalable Asset Structure — component `kind` on exported assets: https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
