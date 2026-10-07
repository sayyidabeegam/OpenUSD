# Chapter 11 — Primvars

> **Exam domain:** Data Modeling (13%) and Visualization (8%) · **Objectives:** 5.1, 8.1
> **Study day:** 4 · **Est. time:** 80 min
> **Prerequisites:** Chapters 5, 9, 6

## Learning goals

- Explain what a **primvar** is and add one to a mesh (Obj 5.1 / 8.1).
- Use `UsdGeom.PrimvarsAPI`.
- Choose **interpolation**: constant, uniform, varying, vertex, faceVarying.
- Author **indexed** primvars and `elementSize`.
- Predict **inheritance** of primvars down namespace.
- Use `primvars:displayColor` and `displayOpacity`.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Primvar | A geometric primitive variable: extra data on a gprim, often for shading |
| Interpolation | How one primvar array maps onto vertices / faces / the whole prim |
| Indexed primvar | Values plus an index array (like a palette) |
| `elementSize` | How many array entries make one logical element |
| Inheritance | A primvar on an ancestor applies to descendants unless overridden |

---

## 11.1 What a primvar is

### 1. What is it?

A **primvar** is data attached to a geometric prim, stored as an attribute in the `primvars:` namespace (and optional sibling `indices` attributes).

### 2. Why do we need it?

Meshes need more than points: UVs, colors, IDs, custom shading data. Obj 5.1 / 8.1: add a primvar to a mesh. Obj 8.4: a shader reads a primvar for diffuse color (Ch 40).

### 3. Beginner explanation

Points say where the corners are. Primvars say what else each corner (or face, or the whole object) carries: color, UV, `st`, `id`.

Where the analogy breaks: a primvar can live on an **ancestor Xform** and still affect the child mesh (inheritance).

### 4. Technical explanation

- Attribute name: `primvars:<name>`.
- API class: `UsdGeom.Primvar` wrapping the attribute; factory: `UsdGeom.PrimvarsAPI`.
- `displayColor` / `displayOpacity` are built-in primvars on Gprims.
- Roles matter: `color3f[]`, `texCoord2f[]` (Ch 9).

### 5. Mental model

`primvars:foo` = extra channel named foo on this geometry (or inherited).

### 6. Simple example

A whole mesh is red: one `color3f` with interpolation `constant`.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    color3f[] primvars:displayColor = [(1, 0, 0)] (
        interpolation = "constant"
    )
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf, Gf

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Body")
api = UsdGeom.PrimvarsAPI(mesh)
pv = api.CreatePrimvar(
    "displayColor",
    Sdf.ValueTypeNames.Color3fArray,
    UsdGeom.Tokens.constant,
)
pv.Set([Gf.Vec3f(1, 0, 0)])
print("attr:", pv.GetAttr().GetName())
print("interpolation:", pv.GetInterpolation())
print("HasPrimvar:", api.HasPrimvar("displayColor"))
```

**Expected output**

```text
attr: primvars:displayColor
interpolation: constant
HasPrimvar: True
```

### 9. Real-world use case

Lookdev paints `primvars:st` UVs in one layer; lighting never touches `points`.

### 10. Common mistakes

> [!MISTAKE] Creating `displayColor` without the `primvars:` prefix. Hydra looks for the primvar namespace.

### 11. Exam traps

> [!TRAP] "Primvars are relationships." They are attributes (plus optional index attributes).

### 12. Practice questions

**DM-019** · Obj 5.1 · Difficulty: Easy · Type: Single choice

The USD name of a primvar `foo` is:

A. `foo`  
B. `primvars:foo`  
C. `rel foo`  
D. `kind:foo`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Primvar = `primvars:` attribute (+ optional indices).
> - Obj 5.1 / 8.1 = add one to a mesh via PrimvarsAPI or USDA.

---

## 11.2 UsdGeom.PrimvarsAPI

### 1. What is it?

**PrimvarsAPI** is the schema API for creating, finding, and inheriting primvars.

### 2. Why do we need it?

Direct `CreateAttribute("primvars:x", ...)` works, but you will forget interpolation metadata and indices. Use the API.

### 3. Beginner explanation

PrimvarsAPI is the toolbox labeled "channels on this mesh."

### 4. Technical explanation

Verified on USD 26.08:

- `CreatePrimvar(name, typeName, interpolation)`
- `GetPrimvar(name)`, `HasPrimvar(name)`, `GetPrimvars()`
- `FindPrimvarWithInheritance(name)`, `FindPrimvarsWithInheritance()` — not `FindPrimvar` (that name does not exist).
- `UsdGeom.Primvar`: `GetInterpolation`, `SetInterpolation`, `GetElementSize`, `SetIndices`, `IsIndexed`, `GetAttr`.

`GetPrimvars()` on a Mesh also lists schema primvars such as `primvars:displayOpacity` even if you never created them.

### 5. Mental model

Create / Get = local. Find…WithInheritance = walk ancestors.

### 6. Simple example

Lookdev tool: `api.CreatePrimvar("st", TexCoord2fArray, vertex)`.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    texCoord2f[] primvars:st = [(0, 0), (1, 0), (0, 1)] (
        interpolation = "vertex"
    )
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
api = UsdGeom.PrimvarsAPI(UsdGeom.Mesh.Define(stage, "/Body"))
api.CreatePrimvar("st", Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.vertex)
print("Has st:", api.HasPrimvar("st"))
print("names:", [p.GetName() for p in api.GetPrimvars()])
```

**Expected output**

```text
Has st: True
names: ['primvars:displayColor', 'primvars:displayOpacity', 'primvars:st']
```

### 9. Real-world use case

A validator requires `st` with interpolation vertex or faceVarying before shading.

### 10. Common mistakes

> [!MISTAKE] Calling `FindPrimvar` — it is `GetPrimvar` locally and `FindPrimvarWithInheritance` for ancestors.

### 11. Exam traps

> [!TRAP] "CreatePrimvar replaces Mesh typeName." No; it is an API on the existing prim.

### 12. Practice questions

**DM-020** · Obj 5.1 · Difficulty: Easy · Type: Single choice

Which class is the supported way to add a primvar in Python?

A. `UsdGeom.PrimvarsAPI`  
B. `UsdLux.ShadowAPI`  
C. `Sdf.LayerOffset`  
D. `Kind.Registry`  

**Answer:** A.

### 13. Exam takeaways

> [!KEY]
> - `PrimvarsAPI.CreatePrimvar` / `GetPrimvar` / `FindPrimvarWithInheritance`.

---

## 11.3 Interpolation

### 1. What is it?

**Interpolation** says how the primvar array maps onto the mesh: `constant`, `uniform`, `varying`, `vertex`, `faceVarying`.

### 2. Why do we need it?

Wrong interpolation = wrong colors / UVs (Obj 5.5 unexpected visuals). PreviewSurface reading a primvar (Obj 8.4) needs the interpolation the shader expects.

### 3. Beginner explanation

- **constant** — one value for the whole prim.
- **uniform** — one value per face.
- **vertex** — one value per point (indexed by `faceVertexIndices`).
- **faceVarying** — one value per face-corner (so UVs can seam).
- **varying** — like vertex for subdivision / interpolatable data (smooth across the surface).

Where the analogy breaks: `varying` vs `vertex` is subtle on a plain polygonal mesh; faceVarying vs vertex is the UV-seam question.

### 4. Technical explanation

Tokens: `UsdGeom.Tokens.constant` (and uniform, varying, vertex, faceVarying).

Lengths (triangle mesh, V vertices, F faces, C corners = sum of faceVertexCounts):

| Interpolation | Typical array length |
|---------------|----------------------|
| constant | 1 (or elementSize) |
| uniform | F |
| vertex / varying | V |
| faceVarying | C (e.g. 3F for all tris) |

Authored in USDA in the attribute's metadata block: `interpolation = "vertex"`.

### 5. Mental model

constant = object. uniform = face. vertex = point. faceVarying = corner.

### 6. Simple example

Hard-edged vertex colors that differ on a shared point must be **faceVarying**, not vertex.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Tri"
{
    int[] faceVertexCounts = [3]
    int[] faceVertexIndices = [0, 1, 2]
    point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    color3f[] primvars:displayColor = [(1, 0, 0), (0, 1, 0), (0, 0, 1)] (
        interpolation = "vertex"
    )
}
```

### 8. Python example

```python
from pxr import UsdGeom

print(
    UsdGeom.Tokens.constant,
    UsdGeom.Tokens.uniform,
    UsdGeom.Tokens.varying,
    UsdGeom.Tokens.vertex,
    UsdGeom.Tokens.faceVarying,
)
```

**Expected output**

```text
constant uniform varying vertex faceVarying
```

### 9. Real-world use case

UDIM UVs are faceVarying (or vertex if welded). Face colors for IDs are uniform.

### 10. Common mistakes

> [!MISTAKE] vertex-length array with faceVarying interpolation (or the reverse). Length must match the interpolation.

### 11. Exam traps

> [!TRAP] "constant means one float per vertex." Constant is **one** value for the prim.

### 12. Practice questions

**DM-021** · Obj 5.1 · Difficulty: Medium · Type: Single choice

Per-face IDs on a mesh of 10 faces should use interpolation:

A. constant  
B. uniform  
C. vertex  
D. faceVarying always  

**VIS-PRE-002** · Obj 8.1 · Difficulty: Medium · Type: Single choice

UVs that need seams (different UV at the same vertex) need:

A. constant  
B. vertex only  
C. faceVarying  
D. kind = component  

**Answers**

**DM-021 — Answer: B.** One value per face.

**VIS-PRE-002 — Answer: C.**

### 13. Exam takeaways

> [!KEY]
> - Five interpolations. Match array length to topology.
> - Seams → faceVarying. Whole object → constant. Per face → uniform.

---

## 11.4 Indexed primvars

### 1. What is it?

An **indexed primvar** stores a **values** array plus an **indices** array, like a palette.

### 2. Why do we need it?

A million corners sharing 8 colors: store 8 colors and a million small ints, not a million colors.

### 3. Beginner explanation

Paint-by-number: the palette is the values; the numbers on the canvas are the indices.

### 4. Technical explanation

- `pv.SetIndices(Vt.IntArray([...]))` → `IsIndexed()` True.
- USDA: `primvars:foo:indices = [0, 1, 0, 1]` beside `primvars:foo`.
- Indices follow the interpolation (they replace the "long" array). Values are the unique set (× elementSize).

### 5. Mental model

values[indices[i]] is the data for element i.

### 6. Simple example

Values `[(1,0,0), (0,1,0)]`, indices `[0,1,0,1]` — red, green, red, green.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    color3f[] primvars:displayColor = [(1, 0, 0), (0, 1, 0)] (
        interpolation = "vertex"
    )
    int[] primvars:displayColor:indices = [0, 1, 0, 1]
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf, Vt

stage = Usd.Stage.CreateInMemory()
api = UsdGeom.PrimvarsAPI(UsdGeom.Mesh.Define(stage, "/Body"))
pv = api.CreatePrimvar("id", Sdf.ValueTypeNames.IntArray, UsdGeom.Tokens.vertex)
pv.Set([10, 20])
pv.SetIndices(Vt.IntArray([0, 1, 0, 1]))
print("indexed:", pv.IsIndexed())
print("indices:", list(pv.GetIndices()))
print("values:", list(pv.Get()))
```

**Expected output**

```text
indexed: True
indices: [0, 1, 0, 1]
values: [10, 20]
```

### 9. Real-world use case

Packed USD from DCC often indexes UVs and colors. Flattening (Ch 34) may expand them.

### 10. Common mistakes

> [!MISTAKE] Index out of range of the values array — some renderers skip the primvar silently (unexpected visuals, Obj 5.5).

### 11. Exam traps

> [!TRAP] "Indexed means interpolation = vertex." Indexing is independent of interpolation.

### 12. Practice questions

**DM-022** · Difficulty: Medium · Type: Single choice

`primvars:displayColor:indices` holds:

A. RGB floats  
B. Integers into the primvar's values array  
C. Layer offsets  
D. Kinds  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Indexed = palette + indices. Interpolation still applies to the indices.

---

## 11.5 elementSize

### 1. What is it?

**elementSize** is how many array entries make **one** interpolated element. Default **1**.

### 2. Why do we need it?

A primvar of 3 floats per vertex stored as `float[]` with `elementSize = 3` instead of `float3[]`. Some DCC dumps use this.

### 3. Beginner explanation

If each vertex wants a 3-tuple but the array is flat floats, elementSize=3 groups them.

Where the analogy breaks: prefer a vector type (`float3[]`, `color3f[]`) when you can. elementSize is the escape hatch.

### 4. Technical explanation

- `pv.GetElementSize()` / `SetElementSize(n)`.
- USDA metadata: `elementSize = 3`.
- Length rules multiply: vertex interpolation needs `V * elementSize` scalars.

### 5. Mental model

logical_length = array_length / elementSize.

### 6. Simple example

`float[] primvars:foo` length 9, elementSize 3, vertex on a 3-point mesh.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    float[] primvars:foo = [1, 0, 0, 0, 1, 0, 0, 0, 1] (
        interpolation = "vertex"
        elementSize = 3
    )
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
pv = UsdGeom.PrimvarsAPI(UsdGeom.Mesh.Define(stage, "/Body")).CreatePrimvar(
    "foo", Sdf.ValueTypeNames.FloatArray, UsdGeom.Tokens.vertex
)
print("default elementSize:", pv.GetElementSize())
pv.SetElementSize(3)
print("after:", pv.GetElementSize())
```

**Expected output**

```text
default elementSize: 1
after: 3
```

### 9. Real-world use case

An old importer stored normals as flat floats with elementSize 3. A modern importer uses `normal3f[]`.

### 10. Common mistakes

> [!MISTAKE] elementSize 3 on `color3f[]` (already 3-vectors) — you just tripled the meaning. Use 1 with vector types.

### 11. Exam traps

> [!TRAP] "elementSize is the number of faces." No.

### 12. Practice questions

**DM-023** · Difficulty: Medium · Type: Single choice

Default `elementSize` is:

A. 0  
B. 1  
C. 3  
D. The vertex count  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Default elementSize is 1. Prefer vector types over packing with elementSize.

---

## 11.6 Primvar inheritance

### 1. What is it?

A primvar authored on an **ancestor** applies to **descendants** that do not override it.

### 2. Why do we need it?

Set `displayColor` once on `/Char` and every mesh under it tints, unless a mesh has its own primvar.

### 3. Beginner explanation

A team color on the jersey folder, not on every stitch.

Where the analogy breaks: inheritance is **namespace**, not composition-arc inherits (Ch 19). Different word, related idea.

### 4. Technical explanation

- `FindPrimvarsWithInheritance()` / `FindPrimvarWithInheritance("displayColor")`.
- Verified: primvar on `/X`, child mesh `/X/C` finds `[(0, 1, 0)]`.
- Local opinion on the child wins for that name.

### 5. Mental model

Walk up parents until you find that primvar name.

### 6. Simple example

Assembly tints all referenced components green; one component overrides to blue.

### 7. USDA example

```usda
#usda 1.0

def Xform "Char"
{
    color3f[] primvars:displayColor = [(0, 1, 0)] (
        interpolation = "constant"
    )
    def Mesh "Body"
    {
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
parent = UsdGeom.Xform.Define(stage, "/X")
child = UsdGeom.Mesh.Define(stage, "/X/C")
UsdGeom.PrimvarsAPI(parent).CreatePrimvar(
    "displayColor", Sdf.ValueTypeNames.Color3fArray, UsdGeom.Tokens.constant
).Set([(0, 1, 0)])
found = UsdGeom.PrimvarsAPI(child).FindPrimvarWithInheritance("displayColor")
print("inherited:", found.Get())
print("names:", [p.GetName() for p in UsdGeom.PrimvarsAPI(child).FindPrimvarsWithInheritance()])
```

**Expected output**

```text
inherited: [(0, 1, 0)]
names: ['primvars:displayColor']
```

### 9. Real-world use case

A shot overlay sets `primvars:displayColor` on `/World/Hero` to mark the character in dailies without editing the asset.

### 10. Common mistakes

> [!MISTAKE] Expecting inheritance to jump *out* of a reference to the referencing prim's siblings. It walks **ancestors of this prim** on the composed stage.

### 11. Exam traps

> [!TRAP] Mixing primvar inheritance with the **inherits** composition arc. Different mechanisms.

### 12. Practice questions

**DM-024** · Obj 8.1 · Difficulty: Medium · Type: Single choice

A constant `displayColor` on `/Char` with no opinion on `/Char/Geo`:

A. Does not affect `/Char/Geo`  
B. Can be found on `/Char/Geo` via inheritance  
C. Changes `/Char`'s typeName to Mesh  
D. Is illegal  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Primvars inherit down the namespace until overridden.
> - Use Find*WithInheritance, not only GetPrimvar.

---

## 11.7 displayColor and displayOpacity

### 1. What is it?

**displayColor** and **displayOpacity** are the standard preview primvars on Gprims. usdview and many GL delegates draw them without a full material.

### 2. Why do we need it?

Fast visualization and debugging. Obj 8.1 often uses displayColor as the primvar you add. Obj 8.4 then connects a *shader* to a primvar (which might still be displayColor).

### 3. Beginner explanation

The cheap crayon color on the mesh. Materials are the real paint (Ch 40).

### 4. Technical explanation

- Names: `primvars:displayColor` (`color3f[]`), `primvars:displayOpacity` (`float[]`).
- Schema-provided: `GetPrimvars()` lists them on Mesh even before you Set.
- Interpolation is yours to author (constant for a solid tint is common).

### 5. Mental model

displayColor = viewport crayon. UsdPreviewSurface = lookdev.

### 6. Simple example

Block out a set in gray constant displayColor; later bind materials.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    color3f[] primvars:displayColor = [(0.8, 0.8, 0.8)] (
        interpolation = "constant"
    )
    float[] primvars:displayOpacity = [1] (
        interpolation = "constant"
    )
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf, Gf

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Body")
api = UsdGeom.PrimvarsAPI(mesh)
color = api.CreatePrimvar(
    "displayColor", Sdf.ValueTypeNames.Color3fArray, UsdGeom.Tokens.constant
)
color.Set([Gf.Vec3f(0.8, 0.8, 0.8)])
print(api.GetPrimvar("displayColor").Get())
print("opacity exists:", api.HasPrimvar("displayOpacity"))
```

**Expected output**

```text
[(0.8, 0.8, 0.8)]
opacity exists: True
```

### 9. Real-world use case

Instance-proxy color edits (Obj 2.2) often set displayColor on the instance proxy without breaking instancing (Ch 24).

### 10. Common mistakes

> [!MISTAKE] Assuming displayColor is a UsdPreviewSurface. It is a primvar. Binding a material is separate (Ch 40).

### 11. Exam traps

> [!TRAP] "To color a mesh you must write a new schema." displayColor already exists.

### 12. Practice questions

**VIS-PRE-003** · Obj 8.1 · Difficulty: Easy · Type: Single choice

The standard viewport color primvar is:

A. `kind`  
B. `primvars:displayColor`  
C. `inputs:file`  
D. `subLayers`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - displayColor / displayOpacity = built-in preview primvars.
> - Adding them to a mesh satisfies Obj 5.1 / 8.1.

---

## Chapter lab(s)

Lab 12 (primvars: interpolation and indexed). Lab 34 uses a primvar-driven PreviewSurface.

## USDA reading exercise

**USDA-12.** A mesh has 2 faces, 4 vertices, each face a quad (8 corners). What length is `faceVarying` `st` without indexing?

**Answer:** 8.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Add a primvar to a mesh | PrimvarsAPI + interpolation |
| UV seams | faceVarying |
| Per-face IDs | uniform |
| Palette | indexed primvar |
| Color on the group, not the mesh | inheritance |

### Chapter questions

**Q1.** Namespace of primvars?  
**Q2.** Five interpolations?  
**Q3.** Obj 5.1 in one sentence?  
**Q4.** Get vs FindWithInheritance?  
**Q5.** Default elementSize?  
**Q6.** displayColor type?  
**Q7.** Indices type?  
**Q8.** Is primvar inheritance the inherits arc?

**Answers**

1. `primvars:`. 2. constant, uniform, varying, vertex, faceVarying. 3. Add a primvar to a mesh. 4. Local vs ancestor walk. 5. 1. 6. `color3f[]`. 7. `int[]`. 8. No.

## Further reading

- UsdGeomPrimvar detailed description — OpenUSD API  
- Rendering user guide: working with primvars  
- Interpolation of geometric primitive variables  
