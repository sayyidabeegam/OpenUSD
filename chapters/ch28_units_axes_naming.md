# Chapter 28 — Units, Axes, and Naming

> **Exam domain:** Data Exchange (15%) · **Objectives:** 4.7 (supports 4.1, 7.1) · **Study day:** 9 · **Est. time:** 75 min
> **Prerequisites:** Ch 2 (stage metadata), Ch 4 (prim paths), Ch 16 (references), Ch 27 (extract → transform → validate); xformOps are introduced in Ch 13 and taught fully in Ch 39

## Learning goals

- Read and write a stage's linear unit with `UsdGeom.SetStageMetersPerUnit` / `GetStageMetersPerUnit` and the `UsdGeom.LinearUnits` constants.
- Read and write a stage's up axis with `UsdGeom.SetStageUpAxis` / `GetStageUpAxis`.
- Explain why USD does not convert units or axes when composing, and add the corrective transform yourself.
- Turn arbitrary source names into valid, unique prim names with `Tf.MakeValidIdentifier`.
- Explain mesh `orientation` (`rightHanded` / `leftHanded`) and convert data from a left-handed source.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Linear unit** | The real-world length of one scene unit |
| **`metersPerUnit`** | Layer metadata on the root layer: how many meters one scene unit represents |
| **`UsdGeom.LinearUnits`** | Named constants for common `metersPerUnit` values (`centimeters` = 0.01, ...) |
| **`upAxis`** | Layer metadata on the root layer: which axis points "up", `"Y"` or `"Z"` |
| **Fallback** | The value USD reports when nothing is authored |
| **Corrective transform** | A scale or rotation you add where an asset is referenced, to match the consuming stage |
| **Identifier** | A name that is legal as a prim name or property-name part |
| **Handedness** | Whether a coordinate system (or a face's winding) follows the right-hand or left-hand rule |
| **Winding order** | The order in which a face lists its vertices; it decides which side is the front |
| **`orientation`** | A `Gprim` attribute that says how to read winding order: `rightHanded` (fallback) or `leftHanded` |

## 28.1 `metersPerUnit` and `UsdGeom.LinearUnits`

### 1. What is it?

**`metersPerUnit`** is stage metadata that says how long one scene unit is, in meters. `UsdGeom.LinearUnits` gives names to common values, such as `UsdGeom.LinearUnits.centimeters` (0.01).

### 2. Why do we need it?

A point at `(0, 100, 0)` is meaningless until you know the unit. In centimeters it is 1 m up; in meters it is 100 m up. Without declared units, an importer has to guess, and a guess is how a chair ends up the size of a building.

### 3. Beginner explanation

It is the scale bar printed on a map: "1 cm = 1 km". The map is the same drawing either way; the scale bar tells you how to read it.

Where the analogy breaks: a map reader converts automatically in their head. USD never converts for you (section 28.3). It only records the scale bar.

### 4. Technical explanation

- `metersPerUnit` is a `double` in the root layer's metadata block. Only the stage's **root layer** (and session layer) counts. Values in sublayers or referenced layers are ignored for the stage.
- Read it with `UsdGeom.GetStageMetersPerUnit(stage)`. If unauthored, it returns the **fallback 0.01** (centimeters). Use `UsdGeom.StageHasAuthoredMetersPerUnit(stage)` to tell "authored 0.01" from "nothing authored".
- Write it with `UsdGeom.SetStageMetersPerUnit(stage, value)`.
- Compare with `UsdGeom.LinearUnitsAre(a, b)`, which uses a small tolerance, instead of `==` on floats.
- `UsdGeom.LinearUnits` constants: `nanometers` 1e-9, `micrometers` 1e-6, `millimeters` 0.001, `centimeters` 0.01, `decimeters` 0.1, `meters` 1.0, `kilometers` 1000, `lightYears`, `inches` 0.0254, `feet` 0.3048, `yards` 0.9144, `miles` 1609.344.
- Converting a length from stage A to stage B: `value_B = value_A * mpu_A / mpu_B`.

> [!VERSION] Verified on USD 26.08: an unauthored stage reports `metersPerUnit` 0.01, and a `metersPerUnit` authored only in a sublayer is not seen by `GetStageMetersPerUnit`.

### 5. Mental model

```text
  root layer metadata          every length in the stage
  +--------------------+       +------------------------+
  | metersPerUnit = mpu|  -->  | meters = value * mpu   |
  +--------------------+       +------------------------+
   (nothing authored -> mpu = 0.01, centimeters)
```

### 6. Simple example

| `metersPerUnit` | A cube with `size = 2` is… |
|-----------------|----------------------------|
| 0.01 | 2 cm |
| 1.0 | 2 m |
| 0.0254 | 2 inches (5.08 cm) |

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Bolt"
    metersPerUnit = 0.001
    upAxis = "Z"
)

def Cylinder "Bolt"
{
    double height = 40
    double radius = 4
}
```

- `metersPerUnit = 0.001` means millimeters: the bolt is 40 mm long and 4 mm in radius.
- The metadata lives in the layer's header block, not on any prim.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
print("authored:", UsdGeom.StageHasAuthoredMetersPerUnit(stage))
print("fallback mpu:", UsdGeom.GetStageMetersPerUnit(stage))

UsdGeom.SetStageMetersPerUnit(stage, UsdGeom.LinearUnits.millimeters)
mpu = UsdGeom.GetStageMetersPerUnit(stage)
print("authored:", UsdGeom.StageHasAuthoredMetersPerUnit(stage), "mpu:", mpu)
print("is mm:", UsdGeom.LinearUnitsAre(mpu, UsdGeom.LinearUnits.millimeters))
print(stage.GetRootLayer().ExportToString().strip())

def convert(value, from_mpu, to_mpu):
    return value * from_mpu / to_mpu

print("250 mm in cm:", convert(250, mpu, UsdGeom.LinearUnits.centimeters))
print("6 ft in m:", round(convert(6, UsdGeom.LinearUnits.feet, 1.0), 4))
```

**Expected output**
```text
authored: False
fallback mpu: 0.01
authored: True mpu: 0.001
is mm: True
#usda 1.0
(
    metersPerUnit = 0.001
)
250 mm in cm: 25.0
6 ft in m: 1.8288
```

### 9. Real-world use case

A manufacturing digital twin combines CAD parts in millimeters with a factory building in meters. Every part file declares `metersPerUnit = 0.001`, the factory stage declares `1`, and the assembly tool reads both values to compute the scale for each referenced part.

### 10. Common mistakes

> [!MISTAKE] Not authoring `metersPerUnit` and assuming the reader will "know". The fallback is centimeters, which is wrong for most CAD and game data. Fix: always author it explicitly.

> [!MISTAKE] Comparing units with `==` (`mpu == 0.01`). Floats from different tools differ slightly. Fix: `UsdGeom.LinearUnitsAre(mpu, UsdGeom.LinearUnits.centimeters)`.

### 11. Exam traps

> [!TRAP] "The default `metersPerUnit` is 1 (meters)." No. The fallback when nothing is authored is 0.01 (centimeters).

> [!TRAP] `metersPerUnit` is layer metadata, not a prim attribute. An answer that sets it with `prim.CreateAttribute("metersPerUnit", ...)` is wrong.

### 12. Practice questions

**Q1.** A stage has no `metersPerUnit` authored. What does `UsdGeom.GetStageMetersPerUnit(stage)` return? A. 1.0. B. 0.01. C. 0.0. D. It raises an error.

**Q2.** A part from a stage with `metersPerUnit = 0.001` measures 500 units. How many units is that in a stage with `metersPerUnit = 0.01`?

**Q3.** Which call distinguishes "explicitly centimeters" from "nothing authored"?

**Answers**

**A1: B.** 0.01 is the fallback. No error is raised.

**A2:** 500 × 0.001 / 0.01 = **50** units (0.5 m).

**A3:** `UsdGeom.StageHasAuthoredMetersPerUnit(stage)`.

### 13. Exam takeaways

> [!KEY]
> - `metersPerUnit` = meters per scene unit, on the root layer; fallback 0.01.
> - `UsdGeom.SetStageMetersPerUnit` / `GetStageMetersPerUnit` / `StageHasAuthoredMetersPerUnit`.
> - Use `UsdGeom.LinearUnits.*` constants and `LinearUnitsAre` to compare.
> - Convert: `value_B = value_A * mpu_A / mpu_B`.

## 28.2 `upAxis`

### 1. What is it?

**`upAxis`** is stage metadata that says which axis points up: `"Y"` or `"Z"`.

### 2. Why do we need it?

Different tools disagree. Maya and most game engines are Y-up; Blender, 3ds Max, Unreal, and most CAD tools are Z-up. If an importer reads Z-up data as Y-up, the model lies on its back.

### 3. Beginner explanation

It is the "this side up" arrow printed on a shipping box. The contents are the same; the arrow tells you how to stand the box.

Where the analogy breaks: USD prints the arrow but never turns the box for you. Whoever combines data must rotate it.

### 4. Technical explanation

- Write with `UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)` or `UsdGeom.Tokens.z`. Any other value (for example `"X"`) raises `Tf.ErrorException`.
- Read with `UsdGeom.GetStageUpAxis(stage)`. If unauthored, it returns the fallback from `UsdGeom.GetFallbackUpAxis()`, which is `"Y"` in a default installation.
- Like `metersPerUnit`, only the root layer's value counts.
- To bring Z-up content into a Y-up stage, rotate −90° around X (`xformOp:rotateX = -90`). To bring Y-up content into a Z-up stage, rotate +90° around X.
- `upAxis` is a declaration for tools (cameras, viewers, importers). It does not move any geometry.

### 5. Mental model

```text
   Y-up                      Z-up
    Y                         Z
    |                         |
    +---- X                   +---- X
   /                         /
  Z  (toward viewer)        -Y  (toward viewer)

  Z-up -> Y-up: rotateX(-90)  maps (0,0,1) to (0,1,0)
```

### 6. Simple example

A tree modeled Z-up has its trunk along +Z. In a Y-up stage, without correction, the trunk points toward the camera. Adding `rotateX = -90` on the referencing prim stands it up along +Y.

### 7. USDA example

```usda
#usda 1.0
(
    upAxis = "Z"
)

def Xform "Tree"
{
    def Cylinder "Trunk"
    {
        uniform token axis = "Z"
        double height = 5
    }
}
```

- `upAxis = "Z"` declares the stage Z-up.
- The `Cylinder`'s own `axis` attribute is unrelated: it only says which way that cylinder's height runs. Stage `upAxis` never changes it.

### 8. Python example

```python
from pxr import Gf, Tf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
print("fallback:", UsdGeom.GetStageUpAxis(stage), UsdGeom.GetFallbackUpAxis())
UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
print("authored:", UsdGeom.GetStageUpAxis(stage))
try:
    UsdGeom.SetStageUpAxis(stage, "X")
except Tf.ErrorException:
    print("'X' rejected, still:", UsdGeom.GetStageUpAxis(stage))

z_to_y = Gf.Matrix4d().SetRotate(Gf.Rotation(Gf.Vec3d(1, 0, 0), -90))
up = z_to_y.TransformDir(Gf.Vec3d(0, 0, 1))
print("Z-up 'up' after rotateX(-90):", tuple(round(c, 6) + 0.0 for c in up))
```

**Expected output**
```text
fallback: Y Y
authored: Z
'X' rejected, still: Z
Z-up 'up' after rotateX(-90): (0.0, 1.0, 0.0)
```

The `+ 0.0` turns a possible `-0.0` into `0.0` so the printout is tidy.

### 9. Real-world use case

A game studio's level editor is Y-up, while its environment artists model in a Z-up DCC. The exporter authors `upAxis = "Z"` honestly, and the level-assembly script adds `rotateX = -90` on every Z-up asset it references, based on reading each asset's `upAxis`.

### 10. Common mistakes

> [!MISTAKE] Changing `upAxis` on an existing asset to "fix" it in a viewer. The geometry does not move; you just made the declaration lie. Fix: leave the declaration truthful and rotate where the asset is consumed.

> [!MISTAKE] Passing `"x"` or `"X"` for an X-up source. USD supports only Y and Z. Fix: rotate X-up data into Y or Z during the transform stage.

### 11. Exam traps

> [!TRAP] "`SetStageUpAxis` rotates the geometry." No. It writes metadata only.

> [!TRAP] Confusing stage `upAxis` with a `Cylinder`/`Capsule`/`Cone` prim's `axis` attribute. They are separate.

### 12. Practice questions

**Q1.** Which values can `UsdGeom.SetStageUpAxis` accept? A. X, Y, Z. B. Y, Z. C. Y only. D. Any token.

**Q2.** What rotation brings Z-up content upright in a Y-up stage? A. rotateX −90. B. rotateY 90. C. rotateZ 90. D. scale (1, −1, 1).

**Answers**

**A1: B.** Anything else raises an error.

**A2: A.** rotateX(−90) maps +Z to +Y.

### 13. Exam takeaways

> [!KEY]
> - `upAxis` is `"Y"` or `"Z"` only; fallback `"Y"`.
> - `UsdGeom.SetStageUpAxis` / `GetStageUpAxis` / `GetFallbackUpAxis`.
> - It is a declaration; it moves nothing.
> - Z-up → Y-up: `rotateX = -90`.

## 28.3 USD does not auto-convert units (why)

### 1. What is it?

When you reference, payload, or sublayer a file whose `metersPerUnit` or `upAxis` differs from your stage's, USD composes the values **unchanged**. No scale or rotation is added.

### 2. Why do we need it?

You need to know this because it is a classic source of "the asset is 100× too big" bugs. The consumer of an asset is responsible for adding a **corrective transform**.

### 3. Beginner explanation

Two recipes, one in grams and one in ounces, are stapled into one cookbook. The stapler does not rewrite the numbers. The cook has to notice and convert.

Where the analogy breaks: in USD you fix it once, with one scale on the referencing prim, and every number below it is converted by the transform hierarchy.

### 4. Technical explanation

Why USD does not convert:

- **Stage metrics are root-layer metadata.** Composition arcs bring in prims and their opinions, not another layer's stage-level metadata. The referenced file's `metersPerUnit` is simply not part of the composed stage.
- **No single right place.** A conversion could go on the referencing prim, on each child, or into the points. USD will not guess and silently change authored data.
- **Predictability and speed.** Composed values are exactly what was authored, which keeps value resolution fast and debuggable.

What you do instead (part of the transform stage of Chapter 27):

1. Read the asset's units and axis: open the asset (`Usd.Stage.Open`) and call `GetStageMetersPerUnit` / `GetStageUpAxis`.
2. Compute the scale factor: `asset_mpu / stage_mpu`. Meters into a centimeter stage: `1 / 0.01 = 100`.
3. Add xformOps on the **referencing prim**: a uniform `xformOp:scale` and, if the axes differ, `xformOp:rotateX` (−90 for Z-up into Y-up).
4. Validate: a pipeline check (Chapter 30) can compare each referenced asset's metrics with the stage's.

### 5. Mental model

```text
  shot.usda  (cm, Y-up)                chair.usda  (m, Z-up)
  /World/Chair  --references-->        /Chair        (Xform, no ops)
     scale = 100      <-- you add this   /Chair/Geom  Cube size = 1
     rotateX = -90    <-- and this
  USD itself adds NOTHING. Values arrive as authored: size = 1.
```

### 6. Simple example

`chair_m.usda` (meters) has a cube with `size = 1` (1 m). Referenced into `shot.usda` (centimeters), the composed `size` is still `1`, which the shot reads as 1 cm. With `scale = 100` on `/World/Chair`, the world-space size is 100 cm.

### 7. USDA example

*File: shot.usda* (the corrected consumer; it references the chair asset)

```usda
#usda 1.0
(
    metersPerUnit = 0.01
    upAxis = "Y"
)

def Xform "World"
{
    def "Chair" (
        prepend references = @chair_m.usda@
    )
    {
        float xformOp:rotateX = -90
        float3 xformOp:scale = (100, 100, 100)
        uniform token[] xformOpOrder = ["xformOp:rotateX", "xformOp:scale"]
    }
}
```

- `def "Chair"` has no type, so the prim takes whatever type the asset's root has (here `Xform`). A local type such as `def Xform` would be a stronger opinion and would replace a `Cube` or `Mesh` root type.
- The reference brings `/Chair` and its child `Geom` from `chair_m.usda` with their values untouched.
- `xformOp:scale = 100` converts meters to centimeters; `rotateX = -90` converts Z-up to Y-up.
- The corrective ops live on the referencing prim, so the asset file stays untouched and reusable.

### 8. Python example

This script writes a meters, Z-up asset, references it into a centimeters, Y-up stage, shows that nothing is converted, then adds the corrective ops.

```python
from pxr import Usd, UsdGeom

asset = Usd.Stage.CreateNew("chair_m.usda")
UsdGeom.SetStageMetersPerUnit(asset, UsdGeom.LinearUnits.meters)
UsdGeom.SetStageUpAxis(asset, UsdGeom.Tokens.z)
root = UsdGeom.Xform.Define(asset, "/Chair")
cube = UsdGeom.Cube.Define(asset, "/Chair/Geom")
cube.GetSizeAttr().Set(1.0)
cube.AddTranslateOp().Set((0, 0, 0.5))      # sits on the ground, Z-up
asset.SetDefaultPrim(root.GetPrim())
asset.Save()

shot = Usd.Stage.CreateInMemory()
UsdGeom.SetStageMetersPerUnit(shot, UsdGeom.LinearUnits.centimeters)
UsdGeom.SetStageUpAxis(shot, UsdGeom.Tokens.y)
UsdGeom.Xform.Define(shot, "/World")
prim = shot.DefinePrim("/World/Chair")       # typeless: type comes from asset
prim.GetReferences().AddReference("chair_m.usda")
chair = UsdGeom.Xformable(prim)

def world_range(stage, path):
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"])
    r = cache.ComputeWorldBound(stage.GetPrimAtPath(path)).ComputeAlignedRange()
    fix = lambda v: tuple(round(c, 3) + 0.0 for c in v)
    return fix(r.GetMin()), fix(r.GetMax())

geom = UsdGeom.Cube(shot.GetPrimAtPath("/World/Chair/Geom"))
print("composed size:", geom.GetSizeAttr().Get())
print("before:", world_range(shot, "/World/Chair"))

src = Usd.Stage.Open("chair_m.usda")
factor = UsdGeom.GetStageMetersPerUnit(src) / UsdGeom.GetStageMetersPerUnit(shot)
if UsdGeom.GetStageUpAxis(src) != UsdGeom.GetStageUpAxis(shot):
    chair.AddRotateXOp().Set(-90.0)
chair.AddScaleOp().Set((factor, factor, factor))
print("factor:", factor)
print("after: ", world_range(shot, "/World/Chair"))
```

**Expected output**
```text
composed size: 1.0
before: ((-0.5, -0.5, 0.0), (0.5, 0.5, 1.0))
factor: 100.0
after:  ((-50.0, 0.0, -50.0), (50.0, 100.0, 50.0))
```

Before correction, the chair is 1 unit (1 cm) tall along Z. After, it is 100 cm tall along +Y, standing on the ground.

> [!VERSION] Verified on USD 26.08: referencing a `metersPerUnit = 1`, `upAxis = "Z"` asset into a `0.01`, `"Y"` stage leaves all values unchanged and emits no warning.

### 9. Real-world use case

A VFX studio's sets are in centimeters, Y-up. It licenses a vehicle library authored in meters, Z-up. Its set-dressing tool reads each library asset's metrics when referencing it and authors a `scale` and `rotateX` on the reference prim. A validator flags any reference to a mismatched asset that lacks the correction.

### 10. Common mistakes

> [!MISTAKE] Fixing units by editing the asset's points. Every other consumer that already corrected for meters now gets the wrong size. Fix: correct on the referencing prim.

> [!MISTAKE] Adding corrective ops on a referencing prim whose asset root already has its own `xformOpOrder`. Your local `xformOpOrder` is a stronger opinion and replaces the asset's whole list, so the asset's own ops (for example its translate) stop applying. Verified on USD 26.08. Fix: keep asset roots free of xformOps (put them on children, as in the example), or put the correction on a parent "wrapper" Xform above the referencing prim.

> [!MISTAKE] Creating the referencing prim with `UsdGeom.Xform.Define` when the asset's root is a `Cube` or `Mesh`. The local `Xform` type is stronger than the referenced type, so the geometry disappears (empty bounds). Fix: use a typeless `stage.DefinePrim(path)` and wrap it with `UsdGeom.Xformable` to add the corrective ops.

> [!MISTAKE] Reading the asset's units from the composed stage. The composed stage reports its own root layer's metrics, not the asset's. Fix: open the asset file separately and read its metrics.

### 11. Exam traps

> [!TRAP] "USD automatically rescales references whose `metersPerUnit` differs." False. Values compose exactly as authored.

> [!TRAP] Inverted factor. Meters into centimeters is ×100 (`asset_mpu / stage_mpu = 1 / 0.01`), not ×0.01.

### 12. Practice questions

**Q1.** An asset in inches (`metersPerUnit = 0.0254`) is referenced into a meters stage. What uniform scale corrects it? A. 0.0254. B. 39.37. C. 2.54. D. 1 (USD converts automatically).

**Q2.** Select two. Why does USD not convert units during composition? A. Stage metrics are root-layer metadata that arcs do not carry. B. USD does not support units. C. There is no single correct place to apply a conversion. D. Conversion is done by `Tf.MakeValidIdentifier`.

**Answers**

**A1: A.** Factor = 0.0254 / 1.0 = 0.0254. B is the inverse.

**A2: A and C.** USD does support declaring units (B is false), and D is unrelated.

### 13. Exam takeaways

> [!KEY]
> - References, payloads, and sublayers never convert units or axes.
> - Corrective scale = `asset_mpu / stage_mpu`; Z-up into Y-up = `rotateX -90`.
> - Put corrections on the referencing prim; never edit the asset.
> - Read the asset's metrics by opening the asset itself.

## 28.4 Valid prim names (`Tf.MakeValidIdentifier`)

### 1. What is it?

Prim names must be valid **identifiers**. `Tf.MakeValidIdentifier(name)` turns any string into a valid ASCII identifier by replacing illegal characters with `_`.

### 2. Why do we need it?

Source formats allow names like `"Door - Left (2)"` or `"1st floor"`. USD rejects these as prim names, so an exporter that passes them straight through crashes or produces invalid paths.

### 3. Beginner explanation

It is like a filing clerk who renames folders to fit the filing system's rules: no spaces, no punctuation, don't start with a number.

Where the analogy breaks: the clerk might rename two different folders to the same name. `Tf.MakeValidIdentifier` can do that too, so you must de-duplicate yourself.

### 4. Technical explanation

- **ASCII rule:** first character a letter or `_`, then letters, digits, or `_`. `Tf.IsValidIdentifier(name)` checks exactly this.
- **UTF-8 rule (USD 24.03 and later):** prim names may use Unicode letters (first character from the Unicode XID_Start class or `_`, then XID_Continue characters). `Sdf.Path.IsValidIdentifier("café")` is `True`. Digits, spaces, `-`, and `.` are still not allowed where ASCII forbids them.
- **`Tf.MakeValidIdentifier`** produces ASCII only. It replaces each invalid byte with `_`, so `"café"` becomes `"caf__"` (é is two bytes in UTF-8), and a leading digit becomes `_`. An empty string becomes `"_"`.
- **Collisions:** `"my chair"`, `"my-chair"`, and `"my.chair"` all become `"my_chair"`. An exporter must add suffixes to keep sibling names unique, and should store the original name (for example in `customData` or `displayName` metadata) for the round trip.
- **Property names** follow the same rule per part, with `:` separating namespaces (`primvars:st`). Check with `Sdf.Path.IsValidNamespacedIdentifier`.
- Defining a prim with an invalid name (`stage.DefinePrim("/my chair")`) raises `Tf.ErrorException`.

> [!VERSION] Verified on USD 26.08. UTF-8 prim and property names have been allowed since USD 24.03. `Tf.IsValidIdentifier` and `Tf.MakeValidIdentifier` remain ASCII-only; `Sdf.Path.IsValidIdentifier` applies the UTF-8 rule. Older USD versions reject all non-ASCII names.

### 5. Mental model

```text
 "1st floor"  -> MakeValidIdentifier -> "_st_floor"
 "my-chair"   ->                     -> "my_chair"  \  collision!
 "my chair"   ->                     -> "my_chair"  /  add _1, _2 ...
 "café"       ->                     -> "caf__"     (ASCII only)
```

### 6. Simple example

| Source name | Valid as is? (`Sdf.Path.IsValidIdentifier`) | `Tf.MakeValidIdentifier` |
|-------------|---------------------------------------------|--------------------------|
| `Chair_01` | yes | `Chair_01` |
| `my chair` | no | `my_chair` |
| `1st_floor` | no | `_st_floor` |
| `café` | yes (UTF-8, 24.03+) | `caf__` |

### 7. USDA example

```usda
#usda 1.0

def Xform "Building"
{
    def Xform "_st_floor" (
        customData = {
            string sourceName = "1st floor"
        }
    )
    {
    }

    def Xform "café"
    {
    }
}
```

- `_st_floor` is the sanitized name; `customData` keeps the original for round trips and UIs.
- `café` is a legal UTF-8 prim name in USD 24.03 and later.

### 8. Python example

```python
from pxr import Sdf, Tf, Usd

for name in ["Chair_01", "my chair", "1st_floor", "door-left", "café", ""]:
    print(repr(name), Sdf.Path.IsValidIdentifier(name),
          Tf.IsValidIdentifier(name), repr(Tf.MakeValidIdentifier(name)))

def unique_names(raw_names):
    used, result = set(), []
    for raw in raw_names:
        base = name = Tf.MakeValidIdentifier(raw)
        i = 1
        while name in used:
            name, i = f"{base}_{i}", i + 1
        used.add(name)
        result.append(name)
    return result

print(unique_names(["my chair", "my-chair", "my.chair"]))

stage = Usd.Stage.CreateInMemory()
print(stage.DefinePrim("/café").GetName())
try:
    stage.DefinePrim("/my chair")
except Tf.ErrorException:
    print("'/my chair' rejected")
```

**Expected output**
```text
'Chair_01' True True 'Chair_01'
'my chair' False False 'my_chair'
'1st_floor' False False '_st_floor'
'door-left' False False 'door_left'
'café' True False 'caf__'
'' False False '_'
['my_chair', 'my_chair_1', 'my_chair_2']
café
'/my chair' rejected
```

The invalid path also prints a warning to standard error; only standard output is shown here.

### 9. Real-world use case

An architecture (AEC) exporter reads BIM element names such as `"Wall - Exterior (Type 2)"`. It sanitizes them with `Tf.MakeValidIdentifier`, de-duplicates siblings, and stores the original name and the BIM element ID in `customData`, so a round trip back to the BIM tool can match elements by ID, not by name.

### 10. Common mistakes

> [!MISTAKE] Sanitizing without de-duplicating. Two source objects get the same prim path, and the second silently merges into the first. Fix: add suffixes and track used names per parent.

> [!MISTAKE] Using `Tf.IsValidIdentifier` to reject UTF-8 names in a 24.03+ pipeline. It is ASCII-only. Fix: use `Sdf.Path.IsValidIdentifier` if you want to allow UTF-8, or sanitize deliberately if downstream tools need ASCII.

### 11. Exam traps

> [!TRAP] "`Tf.MakeValidIdentifier` guarantees unique names." No. It only makes names legal.

> [!TRAP] "Prim names must be ASCII." Outdated since USD 24.03; UTF-8 names are valid. Older tools in a pipeline may still reject them.

### 12. Practice questions

**Q1.** What does `Tf.MakeValidIdentifier("2nd-floor")` return? A. `2nd_floor`. B. `_nd_floor`. C. `nd_floor`. D. It raises an error.

**Q2.** Select two. Which are valid prim names in USD 26.08? A. `Lamp_02`. B. `lamp 02`. C. `Lampe_für_Tisch`. D. `02_lamp`.

**Answers**

**A1: B.** The leading digit and the `-` each become `_`.

**A2: A and C.** `C` is a valid UTF-8 identifier (24.03+). Spaces and leading digits are invalid.

### 13. Exam takeaways

> [!KEY]
> - Identifier: letter or `_` first, then letters, digits, `_`; UTF-8 letters allowed since 24.03.
> - `Tf.MakeValidIdentifier` makes an ASCII-legal name; it does not make it unique.
> - `Sdf.Path.IsValidIdentifier` = UTF-8-aware check; `Tf.IsValidIdentifier` = ASCII-only check.
> - Keep the original name in `customData` for round trips.

## 28.5 Coordinate-system handedness

### 1. What is it?

**Handedness** says whether a coordinate system follows the right-hand rule or the left-hand rule. USD uses a right-handed coordinate system. On meshes, the `orientation` attribute (`rightHanded` or `leftHanded`) says how to read each face's **winding order**, which decides which side of the face is the front.

### 2. Why do we need it?

Some sources are left-handed (Unity is left-handed Y-up, Unreal is left-handed Z-up, and many CAD tools vary). Bringing their data in without conversion mirrors the model, and faces may point inward, so back-face culling hides them or lighting looks inverted.

### 3. Beginner explanation

Curl the fingers of your right hand in the order a face lists its corners; your thumb points out of the front. That is `rightHanded`. Do the same with your left hand and the thumb points the other way: `leftHanded`.

Where the analogy breaks: USD's whole coordinate system is always right-handed. `orientation` changes only how a mesh's winding is read, not the axes.

### 4. Technical explanation

- `orientation` is a `uniform token` on `UsdGeom.Gprim` (so on `Mesh` and other gprims). Fallback: `rightHanded`.
- With `rightHanded`, a face whose vertices go counterclockwise when viewed from the front faces you. With `leftHanded`, the front is the other side. Normal direction and back-face culling follow from this.
- Setting `orientation = "leftHanded"` gives the same visual result as reversing every face's vertex order.
- **Converting a left-handed source** (a coordinate-system change): mirror one axis (for example negate Z on points and normals), which flips winding, then either reverse each face's vertex order or set `orientation = "leftHanded"`. Reversing is friendlier to tools that ignore `orientation`.
- A transform with a negative determinant (an odd number of negative scale components) mirrors geometry and also flips the apparent facing direction in world space.

### 5. Mental model

```text
   v2                         v2
   |\    0,1,2 counterclock-  |\    same face read leftHanded,
   | \   wise, rightHanded:   | \   or indices 0,2,1:
   |  \  front faces +Z       |  \  front faces -Z
   v0--v1                     v0--v1
```

### 6. Simple example

Triangle points `(0,0,0)`, `(1,0,0)`, `(0,1,0)`, indices `[0, 1, 2]`. Right-handed: normal `(0, 0, 1)`. Left-handed, or indices `[0, 2, 1]`: normal `(0, 0, -1)`.

### 7. USDA example

```usda
#usda 1.0

def Mesh "FromLeftHandedTool"
{
    int[] faceVertexCounts = [3]
    int[] faceVertexIndices = [0, 1, 2]
    uniform token orientation = "leftHanded"
    point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
}
```

- `orientation = "leftHanded"` tells renderers to read the winding the other way, so this triangle faces −Z.
- Leaving it out means `rightHanded`, and the triangle would face +Z.

### 8. Python example

USD has no "compute face normal" helper, so this computes it with the right-hand rule (`Gf.Cross`) and applies `orientation`.

```python
from pxr import Gf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Tri")
pts = [Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 1, 0)]
mesh.CreatePointsAttr(pts)
mesh.CreateFaceVertexCountsAttr([3])
mesh.CreateFaceVertexIndicesAttr([0, 1, 2])

def face_normal(points, idx, orientation):
    a, b, c = (points[i] for i in idx)
    n = Gf.Cross(b - a, c - a).GetNormalized()
    n = n if orientation == UsdGeom.Tokens.rightHanded else -n
    return tuple(round(x, 3) + 0.0 for x in n)

orient = mesh.GetOrientationAttr()
print("fallback:", orient.Get(), face_normal(pts, [0, 1, 2], orient.Get()))
orient.Set(UsdGeom.Tokens.leftHanded)
print("leftHanded:", face_normal(pts, [0, 1, 2], orient.Get()))
print("reversed winding, rightHanded:", face_normal(pts, [0, 2, 1], "rightHanded"))

# Import from a left-handed tool: mirror Z, then reverse winding.
src = [Gf.Vec3f(0, 0, 0), Gf.Vec3f(1, 0, 0), Gf.Vec3f(0, 0, 1)]
mirrored = [Gf.Vec3f(p[0], p[1], -p[2]) for p in src]
print("mirrored + reversed:", face_normal(mirrored, [0, 2, 1], "rightHanded"))
```

**Expected output**
```text
fallback: rightHanded (0.0, 0.0, 1.0)
leftHanded: (0.0, 0.0, -1.0)
reversed winding, rightHanded: (0.0, 0.0, -1.0)
mirrored + reversed: (0.0, -1.0, 0.0)
```

In the source tool's left-handed space, that triangle faced −Y. After mirroring Z and reversing winding, it still faces −Y in USD: the facing direction survived the conversion.

### 9. Real-world use case

A robotics company simulates in USD but receives environment meshes from a left-handed game engine. Its importer mirrors Z, reverses face winding, and authors `upAxis` and `metersPerUnit`, so collision normals in the physics simulation point outward.

### 10. Common mistakes

> [!MISTAKE] Mirroring points from a left-handed source but not fixing the winding. All faces now point inward. Fix: reverse vertex order per face, or set `orientation = "leftHanded"`.

> [!MISTAKE] Flipping normals to fix inside-out shading while leaving winding wrong. Culling still hides the faces. Fix: correct the winding (or `orientation`) first, then recompute normals.

### 11. Exam traps

> [!TRAP] "USD supports left-handed coordinate systems via `orientation`." No. USD's coordinate system is right-handed; `orientation` only says how to read a gprim's face winding.

> [!TRAP] The fallback for `orientation` is `rightHanded`, not unset or `leftHanded`.

### 12. Practice questions

**Q1.** A triangle with indices `[0, 1, 2]` and `orientation = "leftHanded"` looks the same as which right-handed triangle? A. `[0, 1, 2]`. B. `[1, 2, 0]`. C. `[0, 2, 1]`. D. `[2, 0, 1]`.

**Q2.** Select two. Correct steps when importing from a left-handed tool: A. Negate one axis of points and normals. B. Set `upAxis = "X"`. C. Reverse each face's winding (or set `leftHanded`). D. Rename prims with `Tf.MakeValidIdentifier`.

**Answers**

**A1: C.** Swapping two indices reverses the winding. B and D are rotations of the same order.

**A2: A and C.** `"X"` is not a valid `upAxis`, and renaming is unrelated to handedness.

### 13. Exam takeaways

> [!KEY]
> - USD's coordinate system is right-handed.
> - `orientation` on gprims: `rightHanded` (fallback) or `leftHanded`; it controls which side is front.
> - `leftHanded` = reversed winding.
> - Left-handed source: mirror one axis, then fix winding.

## Chapter lab(s)

**Lab 26 — Units and up-axis handling** (★★☆, Obj 4.7). You build assets in different units and axes, reference them into one stage, confirm that USD changes nothing, and write a helper that adds the corrective `scale` and `rotateX` on each reference. The lab ends with a check that every referenced asset's world bounds match its real-world size.

## USDA reading exercise(s)

**Exercise 28-A.** `lamp.usda` is referenced into `room.usda`. What is the lamp's world-space height in `room.usda` units, and how tall is it in meters?

*File: lamp.usda*

```usda
#usda 1.0
(
    defaultPrim = "Lamp"
    metersPerUnit = 1
    upAxis = "Y"
)

def Cube "Lamp"
{
    double size = 0.5
}
```

*File: room.usda*

```usda
#usda 1.0
(
    metersPerUnit = 0.01
    upAxis = "Y"
)

def Xform "Room"
{
    def "Lamp" (
        prepend references = @lamp.usda@
    )
    {
    }
}
```

**Exercise 28-B.** Which of these prim names fail in USD 26.08: `Wall_A`, `wall A`, `Wänd`, `3D_Text`?

## Chapter review

### Summary

- `metersPerUnit` and `upAxis` are root-layer metadata; fallbacks are 0.01 and `"Y"`.
- Use `UsdGeom.SetStageMetersPerUnit`/`GetStageMetersPerUnit`, `UsdGeom.LinearUnits`, `LinearUnitsAre`.
- `upAxis` accepts only `"Y"` or `"Z"`; it is a declaration and moves nothing.
- Composition never converts units or axes; the consumer adds `scale = asset_mpu / stage_mpu` and `rotateX` on the referencing prim.
- Metrics in sublayers and referenced layers are ignored by the stage.
- `Tf.MakeValidIdentifier` makes ASCII-legal names; de-duplicate yourself; keep the original name.
- UTF-8 prim names are legal since USD 24.03 (`Sdf.Path.IsValidIdentifier`).
- USD is right-handed; gprim `orientation` (`rightHanded` fallback) decides the front side of faces.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Referenced asset 100× too big or small | Unit mismatch; add `scale = asset_mpu / stage_mpu` on the reference prim |
| Asset lying on its back | Z-up vs Y-up; `rotateX ∓90` |
| `GetStageMetersPerUnit` returns 0.01 unexpectedly | Nothing authored on the root layer (fallback) |
| `SetStageUpAxis(stage, "X")` | Error: only Y or Z |
| Name with spaces, dashes, leading digit | `Tf.MakeValidIdentifier` + de-duplication |
| Non-ASCII name rejected by `Tf.IsValidIdentifier` | ASCII-only check; `Sdf.Path.IsValidIdentifier` allows UTF-8 (24.03+) |
| Faces inside out after import | Winding / `orientation`; mirror + reverse for left-handed sources |

### Review questions

**DE-R28-01** · Obj 4.7 · Single choice
What does `UsdGeom.GetStageMetersPerUnit` return for a new stage with no metadata?
A. 1.0 B. 0.01 C. 0.001 D. 0.0

**DE-R28-02** · Obj 4.7 · Single choice
A meters asset is referenced into a millimeter stage. What uniform scale corrects it on the referencing prim?
A. 0.001 B. 1 C. 100 D. 1000

**DE-R28-03** · Obj 4.7 · Select two.
Which statements about composition and units are true?
A. References preserve authored values exactly.
B. USD rescales payloads automatically.
C. Only the root layer's `metersPerUnit` affects `GetStageMetersPerUnit`.
D. A sublayer's `upAxis` overrides the root layer's.

**DE-R28-04** · Obj 4.7 · Single choice
What happens when you call `UsdGeom.SetStageUpAxis(stage, "X")` in USD 26.08?
A. The stage becomes X-up.
B. A `Tf.ErrorException` is raised and the value is not changed.
C. The value is silently changed to `"Y"`.
D. The geometry is rotated.

**DE-R28-05** · Obj 4.7 · Single choice
What does this print?

```{.python .norun}
from pxr import Tf
print(Tf.MakeValidIdentifier("Door Left-2"))
```

A. `Door Left-2` B. `DoorLeft2` C. `Door_Left_2` D. `_oor_Left_2`

**DE-R28-06** · Obj 4.7 · Single choice
An exporter sanitizes `"Pipe A"` and `"Pipe-A"` and writes both under the same parent. What goes wrong?
A. Nothing; `MakeValidIdentifier` adds suffixes.
B. Both map to `Pipe_A`, so the second merges into the first.
C. USD rejects the layer on save.
D. The prims become instances.

**DE-R28-07** · Obj 4.7 · Single choice
Which check accepts the prim name `Tür` in USD 26.08?
A. `Tf.IsValidIdentifier`
B. `Sdf.Path.IsValidIdentifier`
C. Both
D. Neither

**DE-R28-08** · Obj 4.7 · USDA reading
A mesh has `uniform token orientation = "leftHanded"` and indices `[0, 1, 2]` with points `(0,0,0)`, `(1,0,0)`, `(0,1,0)`. Which way does the front face point?
A. +Z B. −Z C. +X D. +Y

**DE-R28-09** · Obj 4.7 · Select two.
Which fixes correct a Z-up, meters asset referenced into a Y-up, centimeters stage?
A. `xformOp:rotateX = -90` on the referencing prim
B. Change the asset's `upAxis` to `"Y"`
C. `xformOp:scale = (100, 100, 100)` on the referencing prim
D. `UsdGeom.SetStageMetersPerUnit(stage, 1.0)` on the asset

**DE-R28-10** · Obj 4.7 · Single choice
What is the value of `UsdGeom.LinearUnits.inches`?
A. 0.0254 B. 2.54 C. 0.3048 D. 25.4

### Answers

**Exercise 28-A.** The composed `size` is `0.5` (unchanged by the reference), so the lamp is **0.5 room units** tall, which `room.usda` reads as 0.5 cm. It was meant to be 0.5 m. A `scale = 100` on `/Room/Lamp` fixes it (50 units = 50 cm = 0.5 m). Verified by composing the files on USD 26.08.

**Exercise 28-B.** `wall A` (space) and `3D_Text` (leading digit) fail. `Wall_A` is ASCII-valid; `Wänd` is a valid UTF-8 name (24.03+).

**DE-R28-01 — B.** Unauthored → fallback 0.01 (centimeters). Review: §28.1.

**DE-R28-02 — D.** `asset_mpu / stage_mpu = 1 / 0.001 = 1000`. A is the inverse. Review: §28.3.

**DE-R28-03 — A, C.** USD never rescales (B false), and sublayer metrics are ignored (D false). Review: §28.1, §28.3.

**DE-R28-04 — B.** Only `"Y"` and `"Z"` are allowed; the call raises and nothing changes. Metadata never rotates geometry. Review: §28.2.

**DE-R28-05 — C.** Space and dash each become `_`. Letters and digits are kept. Review: §28.4.

**DE-R28-06 — B.** `MakeValidIdentifier` does not ensure uniqueness; same path means one prim receives both sets of opinions. Review: §28.4.

**DE-R28-07 — B.** `Sdf.Path.IsValidIdentifier` applies the UTF-8 rule; `Tf.IsValidIdentifier` is ASCII-only. Review: §28.4.

**DE-R28-08 — B.** Counterclockwise in XY would face +Z when right-handed; `leftHanded` flips it to −Z. Review: §28.5.

**DE-R28-09 — A, C.** Corrections go on the consumer's referencing prim. B and D change the asset's declarations without moving data, and other consumers break. Review: §28.3.

**DE-R28-10 — A.** One inch is 0.0254 m. C is feet. Review: §28.1.

## Further reading

- [S06] OpenUSD API Reference — UsdGeom stage metrics (`UsdGeomLinearUnits`, `UsdGeomGetStageUpAxis`). https://openusd.org/release/api/index.html
- [S04] OpenUSD Glossary. https://openusd.org/release/glossary.html
- [S12] OpenUSD CHANGELOG (UTF-8 identifiers, 24.03). https://github.com/PixarAnimationStudios/OpenUSD
- [S14] NVIDIA Learn OpenUSD — Developing Data Exchange Pipelines. https://docs.nvidia.com/learn-openusd/latest/index.html
