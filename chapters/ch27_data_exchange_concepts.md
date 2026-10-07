# Chapter 27 — Data Exchange Concepts

> **Exam domain:** Data Exchange (15%) · **Objectives:** 4.1, 4.2, 4.4 (also 7.1) · **Study day:** 9 · **Est. time:** 100 min
> **Prerequisites:** Ch 2 (stage metadata), Ch 5 (properties), Ch 11 (primvars), Ch 12 (metadata), Ch 13 (extents); Ch 40 (UsdShade) is previewed here and taught fully later

## Learning goals

- Explain the difference between importing, exporting, and converting, and name the three ways foreign data reaches USD.
- Describe the extraction → transformation → validation pipeline and what happens in each stage.
- Write a conceptual data mapping document using a reusable template table.
- Map USD geometry and `UsdPreviewSurface` materials to glTF, and list what glTF cannot carry.
- Map UsdShade concepts to MaterialX concepts.
- Design a round-trip pipeline that does not silently lose data.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Data exchange** | Moving scene data between USD and another tool or file format |
| **DCC** | "Digital content creation" application, such as Maya, Houdini, Blender, or a CAD tool |
| **Export** | Writing data from a tool's own format into USD |
| **Import** | Reading USD into a tool's own in-memory format |
| **Conversion** | Translating one file into another file, usually by a standalone script, with no DCC open |
| **Translator** | General name for an exporter, importer, or converter |
| **Fidelity** | How much of the original meaning survives the translation |
| **Lossy / lossless** | A translation that drops or changes information / one that keeps everything |
| **Data model** | The set of concepts a format can express (meshes, materials, layers, ...) |
| **Data mapping document** | A table that says, for every source concept, what it becomes in the target and what is lost |
| **Round trip** | USD → DCC → USD (or the reverse) with no unintended changes |
| **glTF** | Khronos "GL Transmission Format" 2.0: a compact JSON + binary format for real-time 3D delivery |
| **MaterialX** | An open standard (ASWF) for describing material and shading networks |
| **File format plugin** | A plugin (`SdfFileFormat`) that lets USD open a non-USD file directly as a layer |

## 27.1 Import, export, conversion

### 1. What is it?

**Data exchange** is moving scene data between USD and something else. **Export** writes a tool's data into USD. **Import** reads USD into a tool. **Conversion** translates a file into another file with a standalone program.

### 2. Why do we need it?

Every tool has its own **data model**: Maya thinks in nodes, a game engine thinks in GPU buffers, a CAD tool thinks in exact curved surfaces. Without a common format, every pair of tools needs its own translator. USD is designed to be the common hub, but data still has to be translated into and out of it.

### 3. Beginner explanation

Picture an international conference with one shared language. Each delegate needs one interpreter to and from the shared language, not one interpreter per other delegate. USD is the shared language, and each tool's exporter and importer is its interpreter.

Where the analogy breaks: human languages can describe almost anything. 3D formats cannot. If glTF has no word for "variant set", the interpreter has no way to say it, so the information is dropped. That is **loss**.

### 4. Technical explanation

Foreign data reaches USD in three ways:

1. **DCC exporter / importer.** Code inside the DCC walks the DCC's scene and calls the `Usd`/`Sdf` API to write layers (export), or opens a `Usd.Stage` and builds DCC objects (import). Examples: the Maya USD plug-in, Houdini Solaris, Blender's built-in USD import/export.
2. **Standalone converter.** A script reads file A and writes file B, for example OBJ → USDA or USD → glTF. Chapter 29 writes one.
3. **File format plugin.** A C++ plugin derived from `SdfFileFormat` teaches `Sdf.Layer.FindOrOpen` to read a foreign extension directly, so `Usd.Stage.Open("model.abc")` works. Alembic (`usdAbc`) and MaterialX (`usdMtlx`) plugins ship with full USD builds, but not with `usd-core`. Chapter 38 covers writing one.

Directions are named from the DCC's point of view: you "export to USD" and "import from USD". Converting "USD to glTF" is an export from USD's point of view.

**Fidelity** is measured, not assumed. A good translator reports what it could not carry, rather than dropping it silently.

### 5. Mental model

```text
        point-to-point                     hub (USD)
   Maya ---- Houdini                Maya       Houdini
    | \      / |                       \       /
    |   \  /   |                      [  USD  ]
    |   /  \   |                       /   |   \
  Blender -- Engine              Blender  glTF  Engine
  N tools: N*(N-1) translators   N tools: about 2*N translators
```

### 6. Simple example

| Situation | Kind | Who does it |
|-----------|------|-------------|
| An artist clicks "File → Export USD" in a DCC | Export | DCC exporter |
| A web team turns `chair.usd` into `chair.gltf` on a build server | Conversion | Standalone script |
| `Usd.Stage.Open("chair.abc")` works in a full USD build | Neither: direct read | File format plugin |

### 7. USDA example

A converted file should record where it came from. Layer-level `customLayerData` is a free-form dictionary for this.

```usda
#usda 1.0
(
    customLayerData = {
        string sourceFile = "chair.obj"
        string translator = "obj2usd 1.2"
    }
    defaultPrim = "Chair"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "Chair" (
    kind = "component"
)
{
    def Mesh "Geom"
    {
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    }
}
```

- `customLayerData` holds provenance: the source file and the translator version. USD does not interpret it.
- `metersPerUnit` and `upAxis` record the converter's unit and axis decisions (Chapter 28).
- `defaultPrim` lets other files reference this one without a prim path (Chapter 16).

### 8. Python example

`usd-core` knows only USD's own formats. This script lists them, shows that `.obj` has no reader, and converts USDA to USDC with `Sdf.Layer.Export`, the Python equivalent of `usdcat -o`.

```python
from pxr import Sdf, Usd, UsdGeom

print("formats:", sorted(Sdf.FileFormat.FindAllFileFormatExtensions()))
print("obj reader:", Sdf.FileFormat.FindByExtension("obj"))

stage = Usd.Stage.CreateNew("chair.usda")
UsdGeom.Cube.Define(stage, "/Chair")
stage.GetRootLayer().customLayerData = {"sourceFile": "chair.obj"}
stage.Save()

layer = Sdf.Layer.FindOrOpen("chair.usda")
layer.Export("chair.usdc")
crate = Sdf.Layer.FindOrOpen("chair.usdc")
print("usdc format:", crate.GetFileFormat().formatId)
print("provenance kept:", crate.customLayerData)
```

**Expected output**
```text
formats: ['usd', 'usda', 'usdc', 'usdz']
obj reader: None
usdc format: usdc
provenance kept: {'sourceFile': 'chair.obj'}
```

USD-to-USD conversion (USDA ↔ USDC) is lossless. Conversion to a different data model, such as OBJ or glTF, is where loss happens.

### 9. Real-world use case

A furniture retailer receives CAD files from manufacturers. A conversion service tessellates the exact curved surfaces into meshes, writes USD for the internal pipeline, and later converts USD to glTF and USDZ for the website and mobile AR viewers. Each hop is a translator with its own loss report.

### 10. Common mistakes

> [!MISTAKE] Assuming `Usd.Stage.Open("model.obj")` works because "USD reads everything". It works only if a file format plugin for that extension is installed. In `usd-core` it fails. Fix: write a converter (Chapter 29) or install the plugin.

> [!MISTAKE] Writing a converted file with no provenance. Months later nobody knows which source or translator version produced it. Fix: record both in `customLayerData`.

### 11. Exam traps

> [!TRAP] "Converting USDA to USDC loses data." False. Both encode the same USD data model; only size, speed, and readability differ (Chapter 31).

> [!TRAP] Watch the direction words. "Exporter to USD" writes USD; "importer" reads USD into a DCC. A question about writing a USD file from a DCC is about an exporter.

### 12. Practice questions

**Q1.** A team wants `Usd.Stage.Open("scan.ply")` to work in every tool without a conversion step. What do they need? A. A custom schema. B. An `SdfFileFormat` plugin for `.ply`. C. A `customLayerData` entry. D. A variant set.

**Q2.** Which translation is lossless? A. USD → glTF. B. USDA → USDC. C. USD → OBJ. D. CAD surfaces → USD mesh.

**Q3.** Why does a hub format reduce translator count?

**Answers**

**A1: B.** A file format plugin lets `Sdf` read the extension directly as a layer. Schemas and metadata do not add readers.

**A2: B.** USDA and USDC store the same data model. The others drop features or approximate geometry.

**A3:** Each tool needs translators only to and from the hub (about 2·N), not one to every other tool (N·(N−1)).

### 13. Exam takeaways

> [!KEY]
> - Export writes USD from a tool; import reads USD into a tool; conversion is file-to-file.
> - Three routes into USD: DCC plugin, standalone converter, `SdfFileFormat` plugin.
> - `usd-core` reads only `usd`, `usda`, `usdc`, `usdz`.
> - USDA ↔ USDC is lossless; changing data model is where loss happens.

## 27.2 Extraction → transformation → validation

### 1. What is it?

The standard three-stage shape of every data exchange pipeline: **extract** data from the source, **transform** it into the target's data model and conventions, then **validate** the result before anyone uses it.

### 2. Why do we need it?

Mixing reading, fixing, and writing in one tangled loop makes bugs hard to find and fidelity impossible to measure. Separate stages give you clear places to test, log, and report loss. Without validation, broken files reach downstream departments and fail there, far from the cause.

### 3. Beginner explanation

Think of a factory that imports raw fruit and ships jam. First you unload the trucks (extract). Then you wash, cut, and cook (transform). Finally quality control checks every jar before shipping (validate). Nobody cooks on the loading dock.

Where the analogy breaks: in software, "quality control" can send data back to the transform stage automatically, and the three stages may run in milliseconds inside one script.

### 4. Technical explanation

| Stage | Input → output | Typical work |
|-------|----------------|--------------|
| **Extraction** | Source file or DCC scene → neutral records | Parse the file, walk the DCC scene, read only what the mapping document lists |
| **Transformation** | Neutral records → USD-shaped data | Rename (`Tf.MakeValidIdentifier`, Chapter 28), convert units and axes, triangulate or keep polygons, choose value types (Chapter 9), compute `extent` (Chapter 13), map materials |
| **Load / write** | USD-shaped data → layer on disk | Author prims with `Usd`/`Sdf`, set `defaultPrim`, `upAxis`, `metersPerUnit`, save as USDA or USDC |
| **Validation** | Layer → list of problems | `pxr.UsdValidation` validators plus your own checks (Chapter 30) |

Some texts call this ETL (extract, transform, load) with validation added. Keep the neutral records simple (Python dicts or small classes) so you can unit-test each stage separately.

Validation in USD 26.08 uses `pxr.UsdValidation`. For example, the validator `usdGeomValidators:StageMetadataChecker` reports a stage that lacks `upAxis` or `metersPerUnit`.

> [!VERSION] Verified on USD 26.08. Older material validates with `UsdUtils.ComplianceChecker`, which was removed entirely in 26.08. Use `pxr.UsdValidation` (Chapter 30).

### 5. Mental model

```text
 source --> [ EXTRACT ] --> records --> [ TRANSFORM ] --> USD data
                                                            |
                                                            v
                      report <-- [ VALIDATE ] <-- layer <-- [ WRITE ]
                         |
                 errors? +--> fix the transform, run again
```

### 6. Simple example

A JSON file says a table is `120` units wide, units `"cm"`, up axis `"Z"`, name `"Table Top"`. Extraction reads those four facts. Transformation produces width `1.2` (meters), name `Table_Top`, `upAxis = "Z"`. Validation confirms the stage declares `upAxis` and `metersPerUnit`.

### 7. USDA example

This is the output of the transform and write stages for the example above.

```usda
#usda 1.0
(
    defaultPrim = "Furniture"
    metersPerUnit = 1
    upAxis = "Z"
)

def Xform "Furniture"
{
    def Cube "Table_Top"
    {
        double size = 1.2
        double3 xformOp:translate = (0, 0, 0.75)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
}
```

- The name `Table Top` became `Table_Top`, because spaces are not allowed in prim names.
- `120` cm became `1.2` and `75` cm became `0.75`, because the target declares `metersPerUnit = 1`.

### 8. Python example

A complete, tiny pipeline with one function per stage.

```python
from pxr import Tf, Usd, UsdGeom, UsdValidation

SOURCE = {"units": "cm", "up": "Z", "objects": [
    {"name": "Table Top", "size": 120.0, "pos": [0, 0, 75]},
    {"name": "1st Leg", "size": 5.0, "pos": [50, 30, 37.5]}]}
TO_METERS = {"cm": 0.01, "mm": 0.001, "m": 1.0}

def extract(src):
    return src["objects"], src["units"], src["up"]

def transform(objects, units, up):
    k = TO_METERS[units]
    return up, [{"name": Tf.MakeValidIdentifier(o["name"]),
                 "size": o["size"] * k,
                 "pos": [round(c * k, 4) for c in o["pos"]]} for o in objects]

def write(up, records):
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageUpAxis(stage, up)
    UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.LinearUnits.meters)
    root = UsdGeom.Xform.Define(stage, "/Furniture")
    stage.SetDefaultPrim(root.GetPrim())
    for r in records:
        cube = UsdGeom.Cube.Define(stage, root.GetPath().AppendChild(r["name"]))
        cube.GetSizeAttr().Set(r["size"])
        cube.AddTranslateOp().Set(tuple(r["pos"]))
    return stage

def validate(stage):
    reg = UsdValidation.ValidationRegistry()
    v = reg.GetOrLoadValidatorByName("usdGeomValidators:StageMetadataChecker")
    problems = [e.GetName() for e in v.Validate(stage)]
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Cube) and UsdGeom.Cube(prim).GetSizeAttr().Get() <= 0:
            problems.append(f"non-positive size on {prim.GetPath()}")
    return problems

up, records = transform(*extract(SOURCE))
for r in records:
    print(r)
stage = write(up, records)
print("validation problems:", validate(stage))
```

**Expected output**
```text
{'name': 'Table_Top', 'size': 1.2, 'pos': [0.0, 0.0, 0.75]}
{'name': '_st_Leg', 'size': 0.05, 'pos': [0.5, 0.3, 0.375]}
validation problems: []
```

Notice `1st Leg` became `_st_Leg`: a prim name cannot start with a digit, so `Tf.MakeValidIdentifier` replaced the `1` with `_`. Chapter 28 covers naming in depth.

### 9. Real-world use case

A digital-twin team receives nightly factory-layout exports from a CAD system. The extraction stage reads the CAD export, the transformation stage converts millimeters to meters and sanitizes part names, and the validation stage blocks the publish if any part lacks an extent or the stage lacks units. Failures are emailed to the CAD team with the offending part names.

### 10. Common mistakes

> [!MISTAKE] Converting units inside the extraction code "while you are there". Later nobody can tell whether the records are in source or target units. Fix: extraction keeps source values; only the transformation stage converts.

> [!MISTAKE] Skipping validation because "the exporter is tested". New source data breaks old assumptions. Fix: validate every run, automatically.

### 11. Exam traps

> [!TRAP] Validation comes after writing USD, not before extraction. The order is extract → transform → (write) → validate.

> [!TRAP] An answer that suggests `UsdUtils.ComplianceChecker` for a current pipeline is outdated. In 26.08 it no longer exists; the current API is `UsdValidation`.

### 12. Practice questions

**Q1.** In which stage should centimeters be converted to meters? A. Extraction. B. Transformation. C. Validation. D. Any stage, as long as it happens once.

**Q2.** Which validator reports a stage with no `upAxis`? A. `usdGeomValidators:StageMetadataChecker`. B. `usdShadeValidators:MaterialBindingApiAppliedValidator`. C. `usdUtilsValidators:FileExtensionValidator`. D. `usdGeomValidators:SubsetFamilies`.

**Q3.** Name two benefits of separating the stages.

**Answers**

**A1: B.** Transformation is where the source data model and conventions are mapped to the target's. D works but makes the code hard to test and reason about.

**A2: A.** It checks that stages declare `upAxis` and `metersPerUnit`. The others check binding, file extensions, and subsets.

**A3:** Each stage can be tested on its own, and loss can be logged at one clear place (the transform).

### 13. Exam takeaways

> [!KEY]
> - Extract (read source) → transform (rename, units, axes, types, extents, materials) → write → validate.
> - Validate every run with `pxr.UsdValidation` plus your own checks.
> - Keep extracted records in source units; convert only in the transform stage.
> - Validation is covered in full in Chapter 30.

## 27.3 Conceptual data mapping documents (with template)

### 1. What is it?

A **conceptual data mapping document** is a table that lists every concept in a source data model, what it becomes in the target data model, how it is transformed, and what is lost.

### 2. Why do we need it?

Translators are written by one person and maintained by others. Without a written mapping, nobody can answer "where did my smoothing groups go?" or "is this loss a bug or a design decision?". The mapping is also the specification you test the translator against.

### 3. Beginner explanation

It is a bilingual dictionary for two data models. For each word in language A it gives the word in language B, plus notes like "no exact equivalent; closest is…".

Where the analogy breaks: a dictionary maps words, but a data mapping also maps structure (one source object can become several prims, or several source objects can merge into one prim) and units.

### 4. Technical explanation

Use this reusable template. One row per source concept.

| Source concept | Source type / units | USD target | USD value type | Transformation rule | Fidelity / loss | Round-trips? |
|----------------|---------------------|------------|----------------|---------------------|-----------------|--------------|
| (name in source) | (type, units, space) | (prim type, property, or metadata) | (e.g. `point3f[]`) | (formula, rename, split) | lossless / lossy / dropped + why | yes / no / partial |

Add a header above the table:

- **Source and target versions** (for example "OBJ (Wavefront) → USD 26.08, `UsdGeom`/`UsdShade`").
- **Global conventions**: units, up axis, handedness, naming rule, default prim.
- **Out of scope**: concepts deliberately not translated.

Here is a filled-in example for OBJ → USD.

| Source concept | Source type / units | USD target | USD value type | Transformation rule | Fidelity / loss | Round-trips? |
|----------------|---------------------|------------|----------------|---------------------|-----------------|--------------|
| `o` object name | string | `Mesh` prim name | prim name | `Tf.MakeValidIdentifier`, de-duplicate | lossy for invalid characters | partial |
| `v` vertex | 3 floats, file units | `points` | `point3f[]` | scale by units factor | lossless | yes |
| `f` face | 1-based indices | `faceVertexCounts`, `faceVertexIndices` | `int[]` | subtract 1 | lossless | yes |
| `vt` UV | 2 floats | `primvars:st` (faceVarying, indexed) | `texCoord2f[]` | per face corner | lossless | yes |
| `vn` normal | 3 floats | `normals` or `primvars:normals` (faceVarying) | `normal3f[]` | per face corner | lossless | yes |
| `usemtl` | material name | `Material` + `GeomSubset` binding | relationship | one subset per material | lossless | yes |
| `s` smoothing group | int or off | none | — | dropped; normals carry shading | dropped | no |
| `l` polyline | indices | `BasisCurves` (linear) | `int[]` | optional | dropped in v1 | no |

The same template works for USD → glTF and UsdShade ↔ MaterialX (section 27.4).

### 5. Mental model

```text
  +-------------+  rule  +-------------+
  | source item | -----> | USD item    |   each row = one arrow
  +-------------+        +-------------+   rows with no arrow = LOSS
         |                                 (write them down!)
         +--> (nothing)  "dropped: why"
```

### 6. Simple example

Row: "OBJ `v` (3 floats, centimeters) → `Mesh.points` (`point3f[]`), multiply by 0.01, lossless, round-trips." Anyone reading this row knows the target property, the type, the formula, and the fidelity.

### 7. USDA example

The USD side of the OBJ mapping above: a single quad with one material subset.

```usda
#usda 1.0
(
    defaultPrim = "Crate"
    metersPerUnit = 1
    upAxis = "Y"
)

def Mesh "Crate"
{
    int[] faceVertexCounts = [4]
    int[] faceVertexIndices = [0, 1, 2, 3]
    point3f[] points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    texCoord2f[] primvars:st = [(0, 0), (1, 0), (1, 1), (0, 1)] (
        interpolation = "faceVarying"
    )
    int[] primvars:st:indices = [0, 1, 2, 3]

    def GeomSubset "wood"
    {
        uniform token elementType = "face"
        uniform token familyName = "materialBind"
        int[] indices = [0]
    }
}
```

- `faceVertexIndices` are 0-based: the "subtract 1" rule from the `f` row.
- `primvars:st` with `primvars:st:indices` is the indexed, faceVarying target of the `vt` row (Chapter 11).
- The `GeomSubset` with `familyName = "materialBind"` is the target of the `usemtl` row.

### 8. Python example

Keep the mapping as data in the translator. The same table can then print the document and report unmapped source concepts, so the document never drifts from the code.

```python
MAPPING = {
    "o": ("Mesh prim name", "token", "MakeValidIdentifier", "partial"),
    "v": ("points", "point3f[]", "scale to meters", "yes"),
    "f": ("faceVertexCounts/Indices", "int[]", "1-based -> 0-based", "yes"),
    "vt": ("primvars:st", "texCoord2f[]", "faceVarying, indexed", "yes"),
    "vn": ("normals", "normal3f[]", "faceVarying", "yes"),
    "usemtl": ("GeomSubset + Material", "rel", "subset per material", "yes"),
}
OBJ_TEXT = """o Crate
v 0 0 0
v 1 0 0
v 1 1 0
vt 0 0
s 1
usemtl wood
f 1/1 2/1 3/1
l 1 2
"""

print("| OBJ | USD target | Type | Rule | Round-trips |")
print("|-----|------------|------|------|-------------|")
for key, (target, vtype, rule, rt) in MAPPING.items():
    print(f"| {key} | {target} | {vtype} | {rule} | {rt} |")

seen = sorted({line.split()[0] for line in OBJ_TEXT.splitlines() if line})
print("unmapped (loss):", [k for k in seen if k not in MAPPING])
```

**Expected output**
```text
| OBJ | USD target | Type | Rule | Round-trips |
|-----|------------|------|------|-------------|
| o | Mesh prim name | token | MakeValidIdentifier | partial |
| v | points | point3f[] | scale to meters | yes |
| f | faceVertexCounts/Indices | int[] | 1-based -> 0-based | yes |
| vt | primvars:st | texCoord2f[] | faceVarying, indexed | yes |
| vn | normals | normal3f[] | faceVarying | yes |
| usemtl | GeomSubset + Material | rel | subset per material | yes |
unmapped (loss): ['l', 's']
```

### 9. Real-world use case

An automotive company exchanges materials between a CAD visualization tool, a MaterialX-based renderer, and USD. Its mapping document has one row per material parameter, with value ranges and color spaces, and is reviewed by both the CAD and rendering teams before any translator code changes.

### 10. Common mistakes

> [!MISTAKE] Listing only what maps. The rows that do not map are the most important ones. Fix: every source concept gets a row, even if the target column says "dropped".

> [!MISTAKE] Leaving out units and spaces ("color" without saying linear or sRGB, "position" without saying meters). Fix: a "Source type / units" column on every row.

### 11. Exam traps

> [!TRAP] A mapping document is conceptual: it describes concepts and rules, not code. An answer that says "the mapping document is the converter script" is wrong, even though code can be generated from it.

> [!TRAP] "Every source concept must have a USD target." No. Dropping is allowed, but must be documented and justified.

### 12. Practice questions

**Q1.** Which column best records "OBJ smoothing groups are not translated; vertex normals carry the shading"? A. USD value type. B. Fidelity / loss. C. Source type / units. D. USD target.

**Q2.** Select two. Which belong in a mapping document's header? A. Source and target versions. B. The translator's full source code. C. Global unit and axis conventions. D. A screenshot of the DCC UI.

**Answers**

**A1: B.** Loss and its reason belong in the fidelity column.

**A2: A and C.** Versions and global conventions apply to every row. Source code and screenshots are not conceptual mapping content.

### 13. Exam takeaways

> [!KEY]
> - One row per source concept: target, type, rule, fidelity, round-trip.
> - Document dropped concepts and why.
> - Always state units, spaces, versions, and conventions.
> - Keep the mapping as data so code and document agree.

## 27.4 Mapping USD to glTF and MaterialX

### 1. What is it?

Applying the mapping-document idea to two common partners: **glTF 2.0**, a delivery format for real-time and web viewers, and **MaterialX**, an interchange standard for shading networks.

### 2. Why do we need it?

Objective 4.1 asks you to convert USD to formats such as glTF "with fidelity". That means knowing which USD concepts have a glTF equivalent, which need transformation, and which are lost, and then checking the result. Objective 4.2 uses MaterialX as its example of a data model you map to USD.

### 3. Beginner explanation

USD is a full workshop: layers, composition, variants, any custom attribute. glTF is a shipping box: one flattened, triangulated, ready-to-display result. You can pack the finished product, but not the workshop.

Where the analogy breaks: glTF can hold some "workshop" items through extensions and `extras`, so loss is not absolute. You choose what to pack.

### 4. Technical explanation

**glTF basics.** A `.gltf` file is JSON plus binary buffers (or one `.glb` file). It has `scenes` → `nodes` (a transform as translation/rotation/scale or matrix) → `meshes` → `primitives`. A primitive has vertex `attributes` (`POSITION`, `NORMAL`, `TEXCOORD_0`, `COLOR_0`, ...), optional `indices`, and one `material`. Data lives in `buffers`, sliced by `bufferViews`, typed by `accessors`. The `POSITION` accessor must have `min` and `max`. glTF uses meters, +Y up, a right-handed system, and counterclockwise front faces.

**USD → glTF mapping.**

| USD concept | glTF concept | Rule / loss |
|-------------|--------------|-------------|
| Composed stage | One `scene` | Compose first; layers, references, variants are not kept (only the current selections, flattened) |
| `Xform` + xformOps | `node` TRS or `matrix` | Bake `xformOpOrder` into one matrix or TRS |
| `Mesh` points / counts / indices | `POSITION` + `indices` | Triangulate polygons; glTF has no quads or n-gons |
| `faceVarying` primvars and normals | Per-vertex attributes | Split vertices so each corner has one value |
| `primvars:st` | `TEXCOORD_0` | Flip v: `v_gltf = 1 - v_usd` (glTF UV origin is top-left) |
| `primvars:displayColor` | `COLOR_0` | Expand constant/uniform to per-vertex |
| `GeomSubset` (materialBind) | Several primitives | One primitive per material |
| `metersPerUnit`, `upAxis = "Z"` | (fixed: meters, Y-up) | Scale by `metersPerUnit`; rotate Z-up to Y-up |
| `subdivisionScheme` | — | Lost; export the base cage or a refined mesh |
| `purpose`, `kind`, `customData` | — or `extras` | Lost unless written into `extras` |
| Custom attributes | `extras`, or attribute `_NAME` | glTF requires custom vertex attribute names to start with `_` |
| Time-sampled xforms | `animations` (channels + samplers) | Time in seconds = timeCode / `timeCodesPerSecond`; only TRS and morph weights animate in core glTF |
| Native instancing / PointInstancer | Several nodes reusing one mesh | `EXT_mesh_gpu_instancing` extension for many copies |
| UsdLux lights | `KHR_lights_punctual` | Only point, spot, directional |

**UsdPreviewSurface → glTF `pbrMetallicRoughness`.**

| UsdPreviewSurface input | glTF material field | Note |
|-------------------------|---------------------|------|
| `diffuseColor` | `baseColorFactor` RGB / `baseColorTexture` | |
| `opacity` | `baseColorFactor` alpha | Set `alphaMode` to `BLEND` |
| `opacityThreshold` | `alphaCutoff` | With `alphaMode` `MASK` |
| `metallic`, `roughness` | `metallicFactor`, `roughnessFactor` | One texture: roughness in G, metallic in B |
| `emissiveColor` | `emissiveFactor` / `emissiveTexture` | |
| `normal` | `normalTexture` | |
| `occlusion` | `occlusionTexture` | |
| `useSpecularWorkflow = 1` | no core field | Extension `KHR_materials_specular`, or convert |
| `clearcoat`, `ior` | no core field | `KHR_materials_clearcoat`, `KHR_materials_ior` |
| Gprim `doubleSided` | material `doubleSided` | Moves from geometry to material |

**UsdShade ↔ MaterialX.** MaterialX describes a material as a graph of typed nodes, each defined by a **nodedef** (for example `ND_standard_surface_surfaceshader`).

| MaterialX concept | UsdShade concept |
|-------------------|------------------|
| `surfacematerial` node | `UsdShade.Material` |
| `nodegraph` | `UsdShade.NodeGraph` |
| node (e.g. `standard_surface`, `image`) | `UsdShade.Shader` with `info:id` = nodedef name |
| `input` / `output` | `inputs:` / `outputs:` attributes |
| connection (`nodename=`, `nodegraph=`) | `connectToSource` on the input |
| shader for the MaterialX render context | `outputs:mtlx:surface` on the Material |
| `look` + `materialassign` | material binding (`MaterialBindingAPI`), often per variant |
| `UsdPreviewSurface` nodedef in MaterialX | Same node name in both: the safe common subset |

In a full USD build the `usdMtlx` file format plugin reads `.mtlx` files as USD layers. It is not in `usd-core`, so the mapping is taught conceptually here.

> [!VERSION] Verified on USD 26.08 with `usd-core`: `from pxr import UsdMtlx` fails, and no glTF reader is registered. Full USD builds can include `UsdMtlx`; glTF import/export usually comes from DCCs or separate tools.

### 5. Mental model

```text
  USD (rich)                         glTF (delivery)
  layers/variants  --compose+flatten-->  one scene
  polygons         --triangulate------>  triangles
  faceVarying      --split vertices--->  per-vertex
  any units/axis   --scale/rotate----->  meters, +Y up
  custom data      --extras or LOST--->  extras
```

### 6. Simple example

A USD quad (one 4-sided face) with `diffuseColor = (0.8, 0.2, 0.1)` becomes a glTF primitive with 4 positions, 6 indices (two triangles), and a material with `baseColorFactor = [0.8, 0.2, 0.1, 1.0]`.

### 7. USDA example

The source asset for the Python example below.

```usda
#usda 1.0
(
    defaultPrim = "Tile"
    metersPerUnit = 1
    upAxis = "Y"
)

def Mesh "Tile" (
    prepend apiSchemas = ["MaterialBindingAPI"]
)
{
    int[] faceVertexCounts = [4]
    int[] faceVertexIndices = [0, 1, 2, 3]
    rel material:binding = </Tile/Mat>
    point3f[] points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    custom int studio:tileId = 7

    def Material "Mat"
    {
        token outputs:surface.connect = </Tile/Mat/PBR.outputs:surface>

        def Shader "PBR"
        {
            uniform token info:id = "UsdPreviewSurface"
            color3f inputs:diffuseColor = (0.8, 0.2, 0.1)
            float inputs:metallic = 0
            float inputs:roughness = 0.4
            token outputs:surface
        }
    }
}
```

- The 4-vertex face must become 2 triangles in glTF.
- `inputs:diffuseColor`, `inputs:metallic`, `inputs:roughness` map to the `pbrMetallicRoughness` fields.
- `studio:tileId` has no glTF home, so the exporter writes it to `extras`.

### 8. Python example

No glTF library is installed, so this exporter uses only the Python standard library. It triangulates, packs a binary buffer, maps the material, writes `tile.gltf`, then reads the file back and checks fidelity.

```python
import base64, json, struct
from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.LinearUnits.meters)
mesh = UsdGeom.Mesh.Define(stage, "/Tile")
mesh.CreatePointsAttr([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
mesh.CreateFaceVertexCountsAttr([4])
mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
mesh.GetPrim().CreateAttribute("studio:tileId", Sdf.ValueTypeNames.Int).Set(7)
mat = UsdShade.Material.Define(stage, "/Tile/Mat")
pbr = UsdShade.Shader.Define(stage, "/Tile/Mat/PBR")
pbr.CreateIdAttr("UsdPreviewSurface")
pbr.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
pbr.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
pbr.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
mat.CreateSurfaceOutput().ConnectToSource(pbr.ConnectableAPI(), "surface")
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)

# --- transform: units, triangulation, material lookup ---
assert UsdGeom.GetStageUpAxis(stage) == "Y"          # glTF is +Y up
k = UsdGeom.GetStageMetersPerUnit(stage)            # glTF is meters
pts = [Gf.Vec3f(p) * k for p in mesh.GetPointsAttr().Get()]
tris, start = [], 0
idx = mesh.GetFaceVertexIndicesAttr().Get()
for n in mesh.GetFaceVertexCountsAttr().Get():      # fan triangulation
    for i in range(1, n - 1):
        tris += [idx[start], idx[start + i], idx[start + i + 1]]
    start += n
bound, _ = UsdShade.MaterialBindingAPI(mesh.GetPrim()).ComputeBoundMaterial()
surf = bound.ComputeSurfaceSource()[0]
get = lambda name: surf.GetInput(name).Get()
r4 = lambda xs: [round(float(x), 4) for x in xs]

# --- write glTF JSON + base64 buffer ---
pos = b"".join(struct.pack("<3f", *p) for p in pts)
ind = struct.pack(f"<{len(tris)}H", *tris)
blob = pos + ind
gltf = {
    "asset": {"version": "2.0", "generator": "ch27-sketch"},
    "scene": 0, "scenes": [{"nodes": [0]}],
    "nodes": [{"name": "Tile", "mesh": 0,
               "extras": {"studio:tileId": mesh.GetPrim()
                          .GetAttribute("studio:tileId").Get()}}],
    "meshes": [{"primitives": [{"attributes": {"POSITION": 0},
                                "indices": 1, "material": 0}]}],
    "materials": [{"name": bound.GetPrim().GetName(), "pbrMetallicRoughness": {
        "baseColorFactor": r4(get("diffuseColor")) + [1.0],
        "metallicFactor": r4([get("metallic")])[0],
        "roughnessFactor": r4([get("roughness")])[0]}}],
    "buffers": [{"byteLength": len(blob), "uri":
                 "data:application/octet-stream;base64,"
                 + base64.b64encode(blob).decode()}],
    "bufferViews": [
        {"buffer": 0, "byteOffset": 0, "byteLength": len(pos), "target": 34962},
        {"buffer": 0, "byteOffset": len(pos), "byteLength": len(ind),
         "target": 34963}],
    "accessors": [
        {"bufferView": 0, "componentType": 5126, "count": len(pts),
         "type": "VEC3", "min": r4(min(p[a] for p in pts) for a in range(3)),
         "max": r4(max(p[a] for p in pts) for a in range(3))},
        {"bufferView": 1, "componentType": 5123, "count": len(tris),
         "type": "SCALAR"}],
}
with open("tile.gltf", "w") as f:
    json.dump(gltf, f, indent=1)

# --- fidelity check: read the file back and compare with USD ---
back = json.load(open("tile.gltf"))
raw = base64.b64decode(back["buffers"][0]["uri"].split(",")[1])
n_pts = back["accessors"][0]["count"]
xyz = struct.unpack(f"<{3 * n_pts}f", raw[:12 * n_pts])
ext = UsdGeom.PointBased.ComputeExtent(mesh.GetPointsAttr().Get())
print("triangles:", back["accessors"][1]["count"] // 3)
print("points match:", [tuple(Gf.Vec3f(xyz[i:i + 3])) for i in range(0, 12, 3)]
      == [tuple(p) for p in pts])
print("bounds match extent:", back["accessors"][0]["min"] == r4(ext[0]),
      back["accessors"][0]["max"] == r4(ext[1]))
print("material:", back["materials"][0])
print("extras:", back["nodes"][0]["extras"])
```

**Expected output**
```text
triangles: 2
points match: True
bounds match extent: True True
material: {'name': 'Mat', 'pbrMetallicRoughness': {'baseColorFactor': [0.8, 0.2, 0.1, 1.0], 'metallicFactor': 0.0, 'roughnessFactor': 0.4}}
extras: {'studio:tileId': 7}
```

The fidelity check compares counts, positions, and bounds against USD, which is what "ensure fidelity" means in practice. Production converters also render both files and compare images.

### 9. Real-world use case

An e-commerce site authors products in USD with a `color` variant set. Its build server exports one glTF per variant selection (`chair_red.glb`, `chair_blue.glb`), because glTF cannot hold variants. Each export runs a fidelity check on triangle counts and bounds, and a turntable render comparison.

### 10. Common mistakes

> [!MISTAKE] Exporting a Z-up, centimeter USD stage to glTF without conversion. The model appears 100× too large and lying on its back. Fix: scale by `metersPerUnit` and rotate Z-up to Y-up during transformation.

> [!MISTAKE] Copying `primvars:st` straight into `TEXCOORD_0`. Textures appear upside down. Fix: `v_gltf = 1 - v_usd`.

> [!MISTAKE] Exporting faceVarying normals as if they were per-vertex. Shading breaks at hard edges. Fix: split vertices so each corner has its own normal.

### 11. Exam traps

> [!TRAP] "glTF supports variants and layers, so a USD → glTF export is lossless." Core glTF has no layers, references, or variant sets. You export one composed, flattened result per variant choice.

> [!TRAP] glTF puts metallic and roughness in one texture (roughness in G, metallic in B). UsdPreviewSurface has separate inputs. A converter must pack or split channels.

> [!TRAP] MaterialX's `nodedef` name maps to the UsdShade Shader's `info:id`, not to the prim name.

### 12. Practice questions

**Q1.** A USD mesh has 3 quads and 1 triangle. How many triangles does its glTF primitive need? A. 4. B. 7. C. 10. D. 12.

**Q2.** Select two. Which USD data is lost in a core glTF 2.0 export unless written to `extras` or an extension? A. `points`. B. `customData`. C. Variant sets other than the current selection. D. Material `roughness`.

**Q3.** In a UsdShade network that came from MaterialX, where does the nodedef name `ND_standard_surface_surfaceshader` appear?

**Answers**

**A1: B.** Each quad is 2 triangles (6), plus 1 triangle: 7.

**A2: B and C.** Points and roughness have direct glTF fields. `customData` has no field, and glTF holds only one composed result.

**A3:** As the `info:id` value of the `UsdShade.Shader` prim.

### 13. Exam takeaways

> [!KEY]
> - glTF: meters, +Y up, right-handed, triangles, per-vertex attributes, one material per primitive.
> - USD → glTF: compose and flatten, triangulate, split faceVarying data, flip v, convert units and axis.
> - Lost unless you use `extras` or extensions: layers, variants, custom data, subdivision, most animated attributes.
> - UsdPreviewSurface maps closely to glTF `pbrMetallicRoughness`.
> - MaterialX node → `UsdShade.Shader` with `info:id` = nodedef; nodegraph → `NodeGraph`.

## 27.5 Round-trip pipelines with a DCC

### 1. What is it?

A **round trip** takes USD into a DCC, lets an artist edit it, and brings the result back to USD with only the intended changes.

### 2. Why do we need it?

Real assets move between departments many times. If each trip drops custom data, renames prims, or flattens composition, the asset degrades a little more each time, and downstream overrides that target the old prim paths stop working.

### 3. Beginner explanation

Lending your annotated notebook to a friend who only copies the parts they understand into a fresh notebook. You get back their fixes, but your margin notes are gone. A better friend writes their fixes on sticky notes and hands back your original notebook with the notes on top.

Where the analogy breaks: in USD the "sticky notes" are an override layer, and composition applies them automatically and precisely, attribute by attribute.

### 4. Technical explanation

Typical round-trip losses:

- **Unknown data dropped.** The importer ignores attributes and metadata it does not understand.
- **Composition flattened.** References, payloads, and variants become plain local data.
- **Identity changed.** Prims are renamed or re-parented, so paths change.
- **Topology changed.** Meshes are retriangulated or point order is changed, which breaks primvars and downstream overrides.
- **Conventions changed.** Units, up axis, or interpolation are altered.

Strategies, best first:

1. **Sparse override export.** The DCC writes only what the artist changed, as `over` opinions in a new layer that sits above the original (by sublayer or as a stronger layer in the shot). The original asset is never rewritten. This is how USD-native DCCs such as Houdini Solaris and the Maya USD plug-in can work.
2. **Preserve what you cannot interpret.** The importer stores unknown attributes and metadata, and the exporter writes them back unchanged.
3. **Stable identity.** Keep the USD prim path as the DCC object's identity; never rename on import.
4. **Automated diff test.** Import, export with no edits, and compare: the result must equal the input (Chapter 30 for validation, Chapter 35 for DCC integration).

### 5. Mental model

```text
 Strategy A: full rewrite           Strategy B: sparse override layer
 chair.usda --import--> DCC         chair_edits.usda   (over: only the edit)
                 |                        | subLayers
 chair.usda <--export-- (rewritten)  chair.usda         (untouched original)
 unknown data LOST                   unknown data KEPT
```

### 6. Simple example

The asset has `size = 2`, a gray `displayColor`, and `customData` with an asset ID. The DCC understands only size and color. The artist changes the color to red. Strategy A writes a new file with size and red color, and the asset ID is gone. Strategy B writes a layer that contains only the red color; the asset ID survives in the original underneath.

### 7. USDA example

The override layer written by strategy B.

*File: chair_edits.usda*

```usda
#usda 1.0
(
    subLayers = [
        @chair.usda@
    ]
)

over "Chair"
{
    color3f[] primvars:displayColor = [(0.8, 0.1, 0.1)]
}
```

- `subLayers` puts the original under this layer, so the original's opinions still apply where this layer is silent.
- `over` adds an opinion without defining the prim; the type and everything else come from `chair.usda`.

### 8. Python example

Both strategies side by side, then a check of what survived.

```python
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateNew("chair.usda")
cube = UsdGeom.Cube.Define(stage, "/Chair")
cube.GetSizeAttr().Set(2.0)
cube.GetDisplayColorAttr().Set([(0.5, 0.5, 0.5)])
cube.GetPrim().SetCustomDataByKey("assetId", "CH-001")
stage.SetDefaultPrim(cube.GetPrim())
stage.Save()

# Import: the "DCC" keeps only what it understands, then the artist edits.
dcc = {"size": cube.GetSizeAttr().Get(),
       "color": tuple(cube.GetDisplayColorAttr().Get()[0])}
dcc["color"] = (0.8, 0.1, 0.1)

# Strategy A: rewrite the whole asset from the DCC's data.
full = Usd.Stage.CreateNew("chair_full.usda")
c = UsdGeom.Cube.Define(full, "/Chair")
c.GetSizeAttr().Set(dcc["size"])
c.GetDisplayColorAttr().Set([dcc["color"]])
full.Save()

# Strategy B: write only changed values into an override layer.
edits = Sdf.Layer.CreateNew("chair_edits.usda")
edits.subLayerPaths.append("chair.usda")
over_stage = Usd.Stage.Open(edits)
chair = UsdGeom.Cube(over_stage.GetPrimAtPath("/Chair"))
if tuple(chair.GetDisplayColorAttr().Get()[0]) != dcc["color"]:
    chair.GetDisplayColorAttr().Set([dcc["color"]])
if chair.GetSizeAttr().Get() != dcc["size"]:
    chair.GetSizeAttr().Set(dcc["size"])
edits.Save()

for name in ["chair_full.usda", "chair_edits.usda"]:
    result = Usd.Stage.Open(name)
    prim = result.GetPrimAtPath("/Chair")
    color = UsdGeom.Cube(prim).GetDisplayColorAttr().Get()[0]
    print(name, "color:", color, "assetId:", prim.GetCustomDataByKey("assetId"))
specs = []
edits.Traverse("/", lambda path: specs.append(str(path)))
print("specs in edits layer:", sorted(specs))
original = Sdf.Layer.FindOrOpen("chair.usda")
print("original color spec:",
      original.GetAttributeAtPath("/Chair.primvars:displayColor").default)
```

**Expected output**
```text
chair_full.usda color: (0.8, 0.1, 0.1) assetId: None
chair_edits.usda color: (0.8, 0.1, 0.1) assetId: CH-001
specs in edits layer: ['/', '/Chair', '/Chair.primvars:displayColor']
original color spec: [(0.5, 0.5, 0.5)]
```

Strategy B carried the edit and kept the asset ID. Strategy A lost it silently. The edits layer holds only the pseudo-root `/`, an `over` for `/Chair`, and the one changed attribute. The original file still says gray.

> [!NOTE] The script reads `GetCustomDataByKey("assetId")` rather than `GetCustomData()`. On USD 26.08, `GetCustomData()` on a typed prim such as `Cube` also returns a `userDocBrief` entry that comes from the schema definition, not from your layers.

### 9. Real-world use case

In a film pipeline, layout artists open the shot in a DCC, nudge a few props, and publish. The publish writes a `layout.usda` layer with only `over` opinions for the moved props' `xformOp:translate`. The set-dressing layer and every asset file below stay untouched, and other departments' layers keep composing on top.

### 10. Common mistakes

> [!MISTAKE] Testing a round trip only with your own simple test file. Real assets have custom attributes, variants, and references. Fix: run the "import, export unchanged, diff" test on real published assets.

> [!MISTAKE] Renaming prims on import to match DCC naming rules. Every downstream override that targets the old path stops applying. Fix: keep the USD path as the identity, and use display names in the DCC if needed.

### 11. Exam traps

> [!TRAP] "The safest round trip re-exports the entire asset." Usually wrong. Writing sparse overrides into a new layer is safer, because the original stays untouched and unknown data survives.

> [!TRAP] An override layer uses `over`, not `def`. With `def`, the layer would also be able to define a prim that does not exist below, hiding a path typo.

### 12. Practice questions

**Q1.** After a round trip, an asset's `customData` is empty. Which design most likely caused it? A. Sparse override export. B. Full rewrite from DCC data. C. Using USDC instead of USDA. D. Setting `defaultPrim`.

**Q2.** Select two. Which practices protect round-trip fidelity? A. Keep the USD prim path as object identity. B. Retriangulate all meshes on import. C. Write only edits into an override layer. D. Convert all files to glTF between steps.

**Answers**

**A1: B.** The DCC did not import `customData`, so a full rewrite could not write it back. Sparse export leaves the original intact.

**A2: A and C.** Retriangulating changes topology, and glTF drops USD-only data.

### 13. Exam takeaways

> [!KEY]
> - Round trip = USD → DCC → USD with only intended changes.
> - Best practice: export sparse `over` opinions into a new layer; never rewrite the original.
> - Preserve unknown data, keep prim paths stable, avoid topology changes.
> - Prove fidelity with an automated "import, export unchanged, diff" test.

## Chapter lab(s)

This chapter has no dedicated lab. Practice its ideas in **Lab 25 — Write a JSON/OBJ → USD converter** (Chapter 29), which follows the extract → transform → validate structure, and **Lab 37 — Capstone: a small multi-asset pipeline end to end**, which includes an export and validation step. Lab 27 (Write an asset validator, Chapter 30) completes the validation stage.

## USDA reading exercise(s)

**Exercise 27-A.** A converter produced this layer. Name two things a glTF export of it must change, and one thing it will lose.

```usda
#usda 1.0
(
    metersPerUnit = 0.01
    upAxis = "Z"
)

def Mesh "Panel" (
    customData = {
        string partNumber = "P-77"
    }
)
{
    int[] faceVertexCounts = [4]
    int[] faceVertexIndices = [0, 1, 2, 3]
    point3f[] points = [(0, 0, 0), (100, 0, 0), (100, 0, 100), (0, 0, 100)]
    uniform token subdivisionScheme = "catmullClark"
}
```

**Exercise 27-B.** In the two files below, what is the composed `size` of `/Chair`, and which file did the round trip write?

*File: chair.usda*

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Cube "Chair"
{
    double size = 2
}
```

*File: chair_edits.usda*

```usda
#usda 1.0
(
    subLayers = [
        @chair.usda@
    ]
)

over "Chair"
{
    double size = 2.5
}
```

## Chapter review

### Summary

- Data exchange = export (tool → USD), import (USD → tool), conversion (file → file).
- Foreign data reaches USD through DCC plugins, standalone converters, or `SdfFileFormat` plugins; `usd-core` reads only USD formats.
- Every translator follows extract → transform → write → validate.
- A mapping document has one row per source concept, including dropped ones, with units and rules.
- glTF is meters, +Y up, triangles, per-vertex attributes; USD composition and custom data do not survive without `extras`.
- UsdPreviewSurface maps closely to glTF PBR; MaterialX nodes map to `UsdShade.Shader` with `info:id` = nodedef.
- Fidelity is proved by checks (counts, bounds, values, renders), not assumed.
- Safe round trips write sparse `over` opinions into a new layer and keep prim paths stable.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| "convert USD to glTF with fidelity" | Flatten, triangulate, split faceVarying, flip v, meters/Y-up, then check counts and bounds |
| "document the mapping to MaterialX" | Template table: concept, type, target, rule, loss; Shader `info:id` = nodedef |
| "data lost after round trip" | Full rewrite dropped unknown data; use sparse override layer |
| "open .obj/.abc directly with Usd.Stage.Open" | Needs an `SdfFileFormat` plugin |
| "stage has no upAxis" in a pipeline check | `usdGeomValidators:StageMetadataChecker` (UsdValidation) |
| "custom attribute in glTF" | `extras`, or vertex attribute named `_NAME` |
| "USDA → USDC loses data?" | No; same data model |

### Review questions

**DE-R27-01** · Obj 4.1 · Single choice
A USD stage has `metersPerUnit = 0.01` and `upAxis = "Z"`. What must a glTF exporter do to its point positions?
A. Nothing; glTF reads `metersPerUnit`.
B. Multiply by 0.01 and rotate from Z-up to Y-up.
C. Multiply by 100 and keep Z-up.
D. Only flip the winding order.

**DE-R27-02** · Obj 4.1 · Select two.
Which steps are required to export a USD mesh with faceVarying UVs to core glTF?
A. Split vertices so each corner has a single UV.
B. Convert the mesh to a `BasisCurves`.
C. Flip the v coordinate.
D. Store UVs in `extras`.

**DE-R27-03** · Obj 4.2 · Single choice
In a USD ↔ MaterialX mapping document, a MaterialX `nodegraph` maps to:
A. `UsdShade.Material`.
B. `UsdShade.NodeGraph`.
C. A `GeomSubset`.
D. A variant set.

**DE-R27-04** · Obj 4.2 · Single choice
Which mapping-document column records "OBJ `l` polylines are dropped in version 1"?
A. USD value type.
B. Transformation rule.
C. Fidelity / loss.
D. Source type / units.

**DE-R27-05** · Obj 4.4 · Single choice
A DCC re-exports a whole asset after an artist edits one color. Downstream, a variant set and a custom attribute are missing. What is the best fix?
A. Export as USDC instead of USDA.
B. Export only the changed color as an `over` in a layer above the original.
C. Add `defaultPrim` to the exported file.
D. Run `Tf.MakeValidIdentifier` on every prim name.

**DE-R27-06** · Obj 4.1 · Single choice
What does this print?

```{.python .norun}
counts = [4, 4, 3]
print(sum(n - 2 for n in counts))
```

A. 3 B. 5 C. 8 D. 11

**DE-R27-07** · Obj 4.4 · USDA reading
In Exercise 27-B, a teammate deletes `chair_edits.usda`. What is the composed `size` when opening `chair.usda`?
A. 2 B. 2.5 C. 1 (the Cube fallback) D. The prim no longer exists.

**DE-R27-08** · Obj 4.1 · Select two.
Which UsdPreviewSurface inputs map directly to core glTF `pbrMetallicRoughness` fields?
A. `roughness`
B. `clearcoat`
C. `diffuseColor`
D. `ior`

**DE-R27-09** · Obj 4.1 · Single choice
In the pipeline order extract → transform → write → validate, where does `Tf.MakeValidIdentifier` belong?
A. Extract. B. Transform. C. Write. D. Validate.

**DE-R27-10** · Obj 4.1 · Single choice
Why is a `.usda` → `.usdc` conversion not a fidelity risk?
A. USDC compresses only textures.
B. Both encode the same USD data model.
C. USDC stores only the composed result.
D. USDA cannot store time samples.

### Answers

**Exercise 27-A.** Must change: scale points by 0.01 (glTF is meters) and rotate Z-up to Y-up; triangulate the quad into 2 triangles. Lost: `subdivisionScheme = "catmullClark"` (glTF has no subdivision) and `customData` (unless written to `extras`).

**Exercise 27-B.** `size = 2.5`. `chair_edits.usda` is the round-trip output; its `over` is stronger than the sublayered original. Verified by composing the two files.

**DE-R27-01 — B.** glTF has fixed conventions (meters, +Y up); the exporter must convert. A is wrong: glTF has no `metersPerUnit`. Review: §27.4, Chapter 28.

**DE-R27-02 — A, C.** glTF attributes are per-vertex, and its UV origin is top-left. Curves and `extras` are not how UVs are carried. Review: §27.4.

**DE-R27-03 — B.** `nodegraph` ↔ `UsdShade.NodeGraph`; `surfacematerial` ↔ `Material`. Review: §27.4.

**DE-R27-04 — C.** Dropped concepts and their reason go in the fidelity column. Review: §27.3.

**DE-R27-05 — B.** A sparse override keeps the original (with its variants and custom data) untouched. Formats, default prim, and names do not restore lost data. Review: §27.5.

**DE-R27-06 — B.** A polygon with n vertices fan-triangulates into n − 2 triangles: 2 + 2 + 1 = 5. D (11) is the vertex count, not the triangle count. Review: §27.4.

**DE-R27-07 — A.** `chair.usda` alone authors `size = 2`. Review: §27.5.

**DE-R27-08 — A, C.** `roughness` → `roughnessFactor`, `diffuseColor` → `baseColorFactor`. `clearcoat` and `ior` need extensions. Review: §27.4.

**DE-R27-09 — B.** Renaming to the target's naming rules is a transformation. Review: §27.2.

**DE-R27-10 — B.** USDA and USDC are two encodings of the same data. Review: §27.1, Chapter 31.

## Further reading

- [S14] NVIDIA Learn OpenUSD — Developing Data Exchange Pipelines. https://docs.nvidia.com/learn-openusd/latest/index.html
- [S06] OpenUSD API Reference — UsdShade, UsdGeom, SdfFileFormat. https://openusd.org/release/api/index.html
- [S10] UsdPreviewSurface specification. https://openusd.org/release/spec_usdpreviewsurface.html
- [S07] USD Toolset (usdcat). https://openusd.org/release/toolset.html
- [S08] USD FAQ. https://openusd.org/release/usdfaq.html
- Khronos glTF 2.0 specification. https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- MaterialX specification. https://materialx.org
