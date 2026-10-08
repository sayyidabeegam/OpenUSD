# Lab 25 — JSON/OBJ → USD converter

**Domain / objectives:** Data Exchange 4.5, 4.7, 4.8 · **Chapter:** 29 · **Time:** 35 min · **Difficulty:** ★★★

## Goal
Convert a JSON crate (centimeters, a space in the name) into a **meters, Y-up, `kind=component`** Mesh with **extent** and a custom `factory:partId`. Parse a tiny OBJ and prove face indices are **0-based**.

## Background
A converter's transform stage maps DCC records onto USD schemas (Ch 27–29). **`Tf.MakeValidIdentifier`** turns `"Crate Box"` into `Crate_Box`. Scale source units into meters (`cm → ×0.01`) and author **`metersPerUnit = 1`**. Always **`ComputeExtentFromPlugins` then `Set`**. OBJ `f 1 2 3` is 1-based — subtract 1. Custom namespaced attributes (`factory:partId`) carry data that has no USD schema (Obj 4.5). Set `subdivisionScheme = none` for tessellated CAD.

## Steps
1. `defaultPrim` is `Crate_Box`; kind `component`; up/units `Y 1.0`.
2. Point `[100,0,0]` cm became `(1.0, 0.0, 0.0)` meters.
3. Extent matches the scaled quad; `partId` is `CR-7`.
4. OBJ object `Tiny`, 3 points, first face `[0, 1, 2]` (not `1 2 3`).

## Full script (identical to `lab25_json_obj_converter.py`)

```python
"""Lab 25 — JSON/OBJ records to a meters Y-up Mesh component."""
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

## Check your understanding
1. Why is `points[1]` `(1,0,0)` if the JSON said `[100,0,0]`?
2. What does `f 1 2 3` become, and why?
3. Does `ComputeExtentFromPlugins` write `extent` for you?

**Answers**
1. Source units were **cm**; the converter scales by **0.01** into meters.
2. **`[0, 1, 2]`**. OBJ vertex indices are 1-based; USD is 0-based.
3. **No.** It returns an array. You `CreateExtentAttr` / `Set`.

## Stretch challenge
Wire `parse_obj` into `json_to_usd` by building a `src` dict from `n, pts, faces` with `"units": "m"`. Solution: you get `/Tiny/Geo` with three points and `faceVertexCounts = [3]`.
