# Chapter 9 — Value Types

> **Exam domain:** Data Modeling (13%) · **Objectives:** 5.2
> **Study day:** 3 · **Est. time:** 90 min
> **Prerequisites:** Chapter 5

## Learning goals

- Choose `Sdf.ValueTypeNames` for attribute data (Obj 5.2).
- Distinguish tokens vs strings, roles (`point3f` vs `float3` vs `color3f`), arrays vs scalars.
- Use `Gf` and `Vt` types in Python.
- Author `asset` paths as `Sdf.AssetPath`.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Value type name | The USDA type tag (`double`, `color3f`, `point3f[]`) |
| Role | Extra meaning on a vector (`Point`, `Color`, `Normal`, `TexCoord`) |
| Token | An interned identifier string (`TfToken` / Python `str` with type `token`) |
| `Vt` array | USD's typed array (`Vt.Vec3fArray`, `Vt.IntArray`) |
| `Gf` | Graphics math: `Gf.Vec3f`, `Gf.Matrix4d`, `Gf.Quatf` |
| Asset path | A resolvable path value (`Sdf.AssetPath`, USDA `@./x.png@`) |

USD 26.08 exposes **111** names on `Sdf.ValueTypeNames`. You do not memorize all of them. You memorize the families and the roles.

---

## 9.1 Sdf.ValueTypeNames

### 1. What is it?

`Sdf.ValueTypeNames` is the catalog of legal attribute types.

### 2. Why do we need it?

`CreateAttribute` requires a type name. USDA declares it on every attribute.

### 3. Beginner explanation

It is the menu of types: pick `Float`, `Point3f`, `Color3fArray`, `Token`, `Asset`, `Matrix4d`, …

### 4. Technical explanation

Python: `Sdf.ValueTypeNames.Color3f`. USDA writes `color3f`. Arrays append `Array` in Python (`Point3fArray`) and `[]` in USDA (`point3f[]`).

`typeName.role` is nonempty for role types (`Point`, `Color`).

### 5. Mental model

Python enum-like catalog ↔ USDA type tag.

### 6. Simple example

Mesh points: `Sdf.ValueTypeNames.Point3fArray` / `point3f[]`. Display color: `Color3fArray` / `color3f[]`.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    point3f[] points = [(0, 0, 0)]
    color3f[] primvars:displayColor = [(1, 0, 0)]
    token purpose = "default"
}
```

### 8. Python example

```python
from pxr import Sdf

print("Point3f:", Sdf.ValueTypeNames.Point3f, "role:", Sdf.ValueTypeNames.Point3f.role)
print("Float3:", Sdf.ValueTypeNames.Float3, "role:", repr(Sdf.ValueTypeNames.Float3.role))
print("Color3f:", Sdf.ValueTypeNames.Color3f, "role:", Sdf.ValueTypeNames.Color3f.role)
print("Point3fArray:", Sdf.ValueTypeNames.Point3fArray)
```

**Expected output**

```text
Point3f: point3f role: Point
Float3: float3 role: '' 
Color3f: color3f role: Color
Point3fArray: point3f[]
```

### 9. Real-world use case

An importer maps glTF `COLOR_0` to `color3f[]` primvars, not `float3[]`, so Hydra treats them as color.

### 10. Common mistakes

> [!MISTAKE] Using `Float3` for mesh points. Points have role `Point` (`point3f`) so transforms treat them as positions.

### 11. Exam traps

> [!TRAP] "float3 and point3f are identical in meaning." Same storage, different **role**.

### 12. Practice questions

**DM-004** · Obj 5.2 · Difficulty: Medium · Type: Single choice

Mesh vertex positions should be stored as:

A. `float3[]`  
B. `point3f[]`  
C. `token[]`  
D. `asset[]`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Pick the type name (and role) that matches the meaning, not just the number of floats.

---

## 9.2 Scalars

### 1. What is it?

**Scalars** are single values: `bool`, `int`, `int64`, `float`, `double`, `half`, `string`, `token`, `uchar`, …

### 2. Why do we need it?

Radius is `double` on Sphere. Flags are `bool`. Counts are `int`.

### 3. Beginner explanation

One cell, one value.

### 4. Technical explanation

- Sphere `radius` is **double** (not float) — verified.
- `half` is 16-bit; rare in Python pipelines; more common in GPU-facing data.
- `string` vs `token`: next section.
- Bool in USDA: `1` / `0` or `true` / `false` depending on writer; Python uses True/False.

### 5. Mental model

If it is not an array (`[]`) and not a vector (`3f`), it is a scalar.

### 6. Simple example

`double radius = 2` · `bool doubleSided = 1`

### 7. USDA example

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 2
    bool doubleSided = 1
    custom int count = 4
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
ball = UsdGeom.Sphere.Define(stage, "/Ball")
print("radius type:", ball.GetRadiusAttr().GetTypeName())
ball.GetRadiusAttr().Set(2.5)
print("radius:", ball.GetRadiusAttr().Get())
flag = ball.GetPrim().CreateAttribute("count", Sdf.ValueTypeNames.Int)
flag.Set(4)
print("count:", flag.Get(), flag.GetTypeName())
```

**Expected output**

```text
radius type: double
radius: 2.5
count: 4 int
```

### 9. Real-world use case

Do not store a unique identifier that must survive as a human string in `token` if you need spaces and punctuation — use `string` (next section).

### 10. Common mistakes

> [!MISTAKE] Setting a float Python value on a `int` attribute and assuming it truncates silently in every version. Match types.

### 11. Exam traps

> [!TRAP] "All numeric USD attributes are float." Sphere radius is double; matrices are double; many shader inputs are float.

### 12. Practice questions

**DM-005** · Obj 5.2 · Difficulty: Easy · Type: Single choice

`UsdGeom.Sphere` radius is typed as:

A. float  
B. double  
C. int  
D. token  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Match the schema's scalar type. Radius is double.

---

## 9.3 Tokens vs strings

### 1. What is it?

A **token** is an interned identifier (`purpose = "render"`). A **string** is general text (`documentation`, file labels).

### 2. Why do we need it?

Tokens are compared by identity and used in enums (`purpose`, `visibility`, `interpolation`). Strings hold prose.

### 3. Beginner explanation

Token = keyword. String = sentence.

Where the analogy breaks: in Python, `Get()` on a token attribute still returns a Python `str`. The distinction is the **USD type**, not the Python class.

### 4. Technical explanation

- USDA: `token purpose = "default"` vs `string documentation = "Hero chair"`.
- Tokens should be short, stable vocabulary.
- `Vt.TokenArray` / `token[]` for lists (`xformOpOrder`).

### 5. Mental model

Closed vocabulary → token. Open text → string.

### 6. Simple example

`uniform token[] xformOpOrder = ["xformOp:translate"]`

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    uniform token[] xformOpOrder = ["xformOp:translate"]
    custom string note = "layout v3"
}
```

### 8. Python example

```python
from pxr import Usd, Sdf

stage = Usd.Stage.CreateInMemory()
prim = stage.DefinePrim("/P")
tok = prim.CreateAttribute("purposeCopy", Sdf.ValueTypeNames.Token)
tok.Set("render")
s = prim.CreateAttribute("note", Sdf.ValueTypeNames.String)
s.Set("layout v3")
print("token value:", tok.Get(), "pytype:", type(tok.Get()).__name__, "usd:", tok.GetTypeName())
print("string value:", s.Get(), "usd:", s.GetTypeName())
```

**Expected output**

```text
token value: render pytype: str usd: token
string value: layout v3 usd: string
```

### 9. Real-world use case

`purpose` tokens are `default`, `render`, `proxy`, `guide` (Ch 39). A free-form string would break filters.

### 10. Common mistakes

> [!MISTAKE] Storing asset paths in `string` when they must resolve — use `asset` (section 9.8).

### 11. Exam traps

> [!TRAP] "In Python tokens are a special class, so `==` fails against str." They come back as `str`. The USDA *type* still matters.

### 12. Practice questions

**DM-006** · Obj 5.2 · Difficulty: Medium · Type: Single choice

`xformOpOrder` is stored as:

A. `string`  
B. `token[]`  
C. `float[]`  
D. `asset[]`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - token = vocabulary. string = text. Python both look like str.

---

## 9.4 Vectors and roles

### 1. What is it?

**Vector types** (`float3`, `double3`, `half3`, …) plus **roles**: `point3f`, `normal3f`, `vector3f`, `color3f`, `texCoord2f`.

### 2. Why do we need it?

Obj 5.2 and visualization: points transform as positions, normals as normals, colors as colors. Wrong role → "unexpected visual results" (Obj 5.5).

### 3. Beginner explanation

Three floats are not enough information. *What they mean* is the role.

### 4. Technical explanation

Verified roles: `Point3f.role` is `Point`; `Color3f.role` is `Color`; `Float3.role` is empty.

| USDA | Meaning |
|------|---------|
| `point3f` | Position (affected by translate/scale/rotate as a point) |
| `vector3f` | Direction/displacement |
| `normal3f` | Surface normal (inverse-transpose) |
| `color3f` / `color4f` | Color (and optional alpha) |
| `texCoord2f` | UV |
| `float3` | Three floats, no role |

Arrays: `point3f[]` for mesh points.

### 5. Mental model

Role rides along with the three numbers.

### 6. Simple example

`points` is `point3f[]`. `normals` is `normal3f[]`. `primvars:displayColor` is `color3f[]`.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    normal3f[] normals = [(0, 1, 0), (0, 1, 0), (0, 1, 0)]
    color3f[] primvars:displayColor = [(1, 0, 0)]
    texCoord2f[] primvars:st = [(0, 0), (1, 0), (0, 1)]
}
```

### 8. Python example

```python
from pxr import Usd, Sdf, Gf

stage = Usd.Stage.CreateInMemory()
prim = stage.DefinePrim("/P")
c = prim.CreateAttribute("c", Sdf.ValueTypeNames.Color3f)
c.Set(Gf.Vec3f(1, 0, 0))
p = prim.CreateAttribute("p", Sdf.ValueTypeNames.Point3f)
p.Set(Gf.Vec3f(0, 10, 0))
print("color", c.Get(), c.GetTypeName())
print("point", p.Get(), p.GetTypeName())
print("roles", Sdf.ValueTypeNames.Color3f.role, Sdf.ValueTypeNames.Point3f.role)
```

**Expected output**

```text
color (1, 0, 0) color3f
point (0, 10, 0) point3f
roles Color Point
```

### 9. Real-world use case

A converter that copies normals into `point3f[]` will transform them like positions — lighting breaks (Obj 5.5 / 6.4).

### 10. Common mistakes

> [!MISTAKE] UVs as `float2[]` instead of `texCoord2f[]` — some renderers still work; PreviewSurface workflows expect texCoord roles (Ch 40).

### 11. Exam traps

> [!TRAP] "color3f is just float3." Role `Color` is the point of the type.

### 12. Practice questions

**DM-007** · Obj 5.2 · Difficulty: Medium · Type: Single choice

Vertex normals on a mesh should be:

A. `point3f[]`  
B. `normal3f[]`  
C. `token[]`  
D. `color3f[]`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Roles: Point, Normal, Color, TexCoord. Empty role = plain floatN.

---

## 9.5 Matrices and quaternions

### 1. What is it?

`matrix4d` (4×4 double matrix) and `quatf` / `quatd` / `quath` store transforms and orientations.

### 2. Why do we need it?

Xformable prims can use a transform matrix; PointInstancer uses quaternions for instance orientations (Ch 25).

### 3. Beginner explanation

A 4×4 matrix is "the whole pose in one blob". A quaternion is "rotation only, compact".

### 4. Technical explanation

- `Gf.Matrix4d`, `Gf.Quatf`.
- USDA: `matrix4d xformOp:transform = ( (1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1) )`
- Prefer xformOps (translate/rotate/scale) for editable pipelines (Ch 39); matrices appear in caches and instancers.

### 5. Mental model

Matrix = full linear pose. Quat = rotation.

### 6. Simple example

Identity matrix = no transform.

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    custom quatf spin = (1, 0, 0, 0)
}
```

### 8. Python example

```python
from pxr import Gf, Sdf, Usd

stage = Usd.Stage.CreateInMemory()
prim = stage.DefinePrim("/P")
m = prim.CreateAttribute("m", Sdf.ValueTypeNames.Matrix4d)
m.Set(Gf.Matrix4d(1.0))
q = prim.CreateAttribute("q", Sdf.ValueTypeNames.Quatf)
q.Set(Gf.Quatf(1, 0, 0, 0))
print("matrix[0][0]:", m.Get()[0][0])
print("quat:", q.Get())
```

**Expected output**

```text
matrix[0][0]: 1.0
quat: (1, 0, 0, 0)
```

### 9. Real-world use case

PointInstancer `orientations` is `quath[]` (half quats) for memory (Ch 25).

### 10. Common mistakes

> [!MISTAKE] Assuming row-vector vs column-vector conventions without checking `Gf.Matrix4d` docs. Be consistent inside one pipeline.

### 11. Exam traps

> [!TRAP] "matrix4d is 4 floats." It is 16 doubles.

### 12. Practice questions

**DM-008** · Difficulty: Easy · Type: Single choice

The common 4×4 transform type in USD is:

A. `float4`  
B. `matrix4d`  
C. `token`  
D. `color4f`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - `matrix4d` and `quat*` are first-class types. Prefer xformOps when humans will edit.

---

## 9.6 Arrays and Vt

### 1. What is it?

**Arrays** are homogeneous lists: `int[]`, `point3f[]`. In Python they are **`Vt` arrays**.

### 2. Why do we need it?

Meshes, curves, primvars, instancer prototype indices — almost all bulk geometry is arrays.

### 3. Beginner explanation

A column of values of one type.

### 4. Technical explanation

- `Vt.IntArray`, `Vt.Vec3fArray`, `Vt.TokenArray`, …
- `attr.Set([(0,0,0),(1,0,0)])` often converts to the right Vt array.
- Length must match the schema's rules (e.g. `faceVertexIndices` length = sum of `faceVertexCounts`).

### 5. Mental model

`[]` in USDA = Vt array in Python.

### 6. Simple example

Three corners of a triangle: `point3f[] points` length 3.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Tri"
{
    int[] faceVertexCounts = [3]
    int[] faceVertexIndices = [0, 1, 2]
    point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
}
```

### 8. Python example

```python
from pxr import Vt

pts = Vt.Vec3fArray([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
idx = Vt.IntArray([0, 1, 2])
print(pts)
print(list(idx), len(idx))
```

**Expected output**

```text
[(0, 0, 0), (1, 0, 0), (0, 1, 0)]
[0, 1, 2] 3
```

### 9. Real-world use case

NVIDIA's study-guide sample on `faceVertexIndices` length for 500 triangles (1500 indices) is **not copied** here. Original: 10 triangles need 30 indices if all are tris.

### 10. Common mistakes

> [!MISTAKE] Setting Python lists of lists with the wrong inner length (2 vs 3) for `Vec3fArray`.

### 11. Exam traps

> [!TRAP] "faceVertexIndices length equals vertex count." It equals **corners referenced**, not unique vertices.

### 12. Practice questions

**DM-009** · Obj 5.2 · Difficulty: Medium · Type: Single choice

A mesh of 4 triangular faces uses `faceVertexIndices` of length:

A. 4  
B. 8  
C. 12  
D. Number of unique vertices always  

**Answer:** C. 4 × 3.

### 13. Exam takeaways

> [!KEY]
> - Bulk data is `[]` / Vt arrays.
> - Index array length follows topology, not unique vertex count.

---

## 9.7 Gf math types

### 1. What is it?

**Gf** (Graphics Foundations) provides `Gf.Vec2f/3f/4f`, `Gf.Vec3d`, `Gf.Matrix4d`, `Gf.Quatf`, `Gf.Range3d`, …

### 2. Why do we need it?

Python attribute `Set`/`Get` for vectors and matrices uses Gf (and Vt for arrays of them).

### 3. Beginner explanation

Gf is the math kit. Vt is the array kit. Sdf names the type. Usd stores the value.

### 4. Technical explanation

`Gf.Vec3f(1, 2, 3)` prints `(1, 2, 3)`. Matrices are 4×4 doubles by default for xforms.

### 5. Mental model

Gf = one math object. Vt = many.

### 6. Simple example

`attr.Set(Gf.Vec3f(0, 10, 0))` for a point3f.

### 7. USDA example

```usda
#usda 1.0

def Xform "W"
{
    custom float3 v = (0, 10, 0)
}
```

### 8. Python example

```python
from pxr import Gf

v = Gf.Vec3f(1, 2, 3)
print(v, v[1])
print(Gf.Matrix4d(1.0)[3][3])
```

**Expected output**

```text
(1, 2, 3) 2.0
1.0
```

### 9. Real-world use case

Extent boxes use `Gf.Vec3f` min/max pairs in `float3[] extent` (Ch 13).

### 10. Common mistakes

> [!MISTAKE] Mixing `Vec3f` and `Vec3d` in the same attribute. Match the type name's precision (`3f` vs `3d`).

### 11. Exam traps

> [!TRAP] "Gf is only for cameras." It is used everywhere vectors exist.

### 12. Practice questions

**DM-010** · Difficulty: Easy · Type: Single choice

`Gf.Vec3f` is used as the Python value for:

A. Layers  
B. 3-float vectors such as color3f / float3 / (with Vt) array elements  
C. Tokens  
D. Kinds  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Gf = math objects. Pair them with the matching ValueTypeName.

---

## 9.8 Asset paths

### 1. What is it?

An **asset** value is a path USD will **resolve** (`Sdf.AssetPath`). USDA writes `@./tex.png@`.

### 2. Why do we need it?

Textures, referenced layers, audio — anything that lives in another file. Obj 7.7: validate asset paths.

### 3. Beginner explanation

Not just a string: a ticket the resolver can turn into a real file (Ch 33).

### 4. Technical explanation

- Type: `Sdf.ValueTypeNames.Asset` / `asset`.
- Python: `Sdf.AssetPath("./tex.png")`; prints `@./tex.png@`.
- Anchored paths (`./`, `../`) resolve relative to the layer.
- Search paths depend on `Ar` configuration.

### 5. Mental model

`@…@` = asset. `</…>` = prim path.

### 6. Simple example

`asset inputs:file = @./textures/albedo.png@` on a texture shader.

### 7. USDA example

```usda
#usda 1.0

def Shader "Tex"
{
    asset inputs:file = @./albedo.png@
}
```

### 8. Python example

```python
from pxr import Sdf, Usd

stage = Usd.Stage.CreateInMemory()
prim = stage.DefinePrim("/Tex")
attr = prim.CreateAttribute("file", Sdf.ValueTypeNames.Asset)
attr.Set(Sdf.AssetPath("./albedo.png"))
print(attr.Get(), type(attr.Get()).__name__, attr.GetTypeName())
```

**Expected output**

```text
@./albedo.png@ AssetPath asset
```

### 9. Real-world use case

A validator lists every `asset` attribute and checks `Ar.GetResolver().Resolve`.

### 10. Common mistakes

> [!MISTAKE] Windows backslashes in asset paths. Use forward slashes.

### 11. Exam traps

> [!TRAP] Confusing `@file@` (asset) with `</Prim>` (target path).

### 12. Practice questions

**DM-011** · Obj 5.2 · Difficulty: Easy · Type: Single choice

A texture filename on a shader should be stored as:

A. `token`  
B. `asset`  
C. `matrix4d`  
D. `bool`  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Asset paths: type `asset`, Python `Sdf.AssetPath`, USDA `@path@`.

---

## 9.9 Choosing the right type (Obj 5.2)

### 1. What is it?

A decision table for exam questions that ask "which type should you use?"

### 2. Why do we need it?

This *is* objective 5.2.

### 3. Beginner explanation

Ask: is it text, a keyword, a filename, a position, a color, a list, a pose?

### 4. Technical explanation

| If you mean… | Use |
|--------------|-----|
| Keyword / enum | `token` or `token[]` |
| Prose | `string` |
| File to resolve | `asset` |
| Position | `point3f` / `point3f[]` |
| Normal | `normal3f[]` |
| Color | `color3f` / `color3f[]` |
| UV | `texCoord2f[]` |
| Generic 3 floats | `float3` (no role) |
| Whole pose | `matrix4d` |
| Bulk topology | `int[]` |
| Sphere radius | `double` (schema) |

### 5. Mental model

Meaning first, then precision (`f` vs `d`), then array or not.

### 6. Simple example

Display color on a mesh: `color3f[] primvars:displayColor`, not `float[]`.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    point3f[] points = [(0, 0, 0)]
    color3f[] primvars:displayColor = [(0.8, 0.1, 0.1)]
    custom asset sourceFile = @./body.obj@
}
```

### 8. Python example

```python
from pxr import Sdf

choices = {
    "positions": str(Sdf.ValueTypeNames.Point3fArray),
    "color": str(Sdf.ValueTypeNames.Color3fArray),
    "filename": str(Sdf.ValueTypeNames.Asset),
    "purpose": str(Sdf.ValueTypeNames.Token),
}
print(choices)
```

**Expected output**

```text
{'positions': 'point3f[]', 'color': 'color3f[]', 'filename': 'asset', 'purpose': 'token'}
```

### 9. Real-world use case

Data mapping documents (Obj 4.2) include a table exactly like this between DCC types and USD types.

### 10. Common mistakes

> [!MISTAKE] One `float[]` dumping every channel. You lose roles, interpolation, and tooling.

### 11. Exam traps

> [!TRAP] Questions that offer both `float3[]` and `point3f[]` — pick the **role**.

### 12. Practice questions

**DM-012** · Obj 5.2 · Difficulty: Medium · Type: Select two.

Select two appropriate types:

A. Mesh points as `point3f[]`  
B. Mesh points as `token[]`  
C. Texture as `asset`  
D. Texture as `matrix4d`  

**Answer:** A and C.

### 13. Exam takeaways

> [!KEY]
> - Obj 5.2 = pick type **and role**.
> - asset vs token vs string vs point vs color is the usual four-way trap.

---

## Chapter lab(s)

Lab 06 (attributes and value types) maps here.

## USDA reading exercise

**USDA-10.** What is wrong with `float3[] points` on a Mesh if you care about transforms?

**Answer:** Missing Point role. Use `point3f[]`.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| float3 vs point3f | Role |
| token vs string vs asset | Keyword vs prose vs file |
| faceVertexIndices length | Corners, not unique verts |
| `@path@` | Asset |

### Chapter questions

**Q1.** Python catalog of types?  
**Q2.** Role of `color3f`?  
**Q3.** Sphere radius precision?  
**Q4.** `xformOpOrder` type?  
**Q5.** Texture type?  
**Q6.** 4 triangular faces → indices length?  
**Q7.** Gf vs Vt?  
**Q8.** Empty role on Float3 means?

**Answers**

1. `Sdf.ValueTypeNames`. 2. Color. 3. double. 4. `token[]`. 5. `asset`. 6. 12. 7. One math object vs array. 8. Three floats with no Point/Color/Normal meaning.

## Further reading

- Basic Datatypes for Scene Description Provided by Sdf — OpenUSD API  
- `Sdf.ValueTypeNames` in this book's USD 26.08 build (111 names)  
