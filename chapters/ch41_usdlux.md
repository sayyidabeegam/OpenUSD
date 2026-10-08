# Chapter 41 — UsdLux and Rendering

> **Exam domain:** Visualization (8%) · **Objectives:** 8.x (UsdLux / Hydra) · **Study day:** 11 · **Est. time:** 80 min
> **Prerequisites:** Ch 6 (schema domains), Ch 13 / 39 (Xformable, purpose, cameras), Ch 40 (UsdShade `inputs:` namespace)

Geometry (Chapter 39) and materials (Chapter 40) still need **light**. **UsdLux** is the schema domain for lights. Typed prims such as `DistantLight` and `RectLight` carry **`LightAPI`** automatically. Optional **`ShadowAPI`** and **`ShapingAPI`** add shadows and spot cones. This chapter also sketches **Hydra**, render delegates, and usdview — concepts you must recognize even though `usd-core` cannot draw a pixel.

Official numbered objectives stop at 8.4 (primvars and PreviewSurface). UsdLux and Hydra appear in the study-guide reading list and in Visualization questions that name light types, `inputs:intensity`, and usdview. Treat them as exam material.

## Learning goals

- Define the six common light types and predict intensity fallbacks (Distant vs local).
- Explain built-in `LightAPI` versus applied `ShadowAPI` / `ShapingAPI`.
- Author `inputs:intensity`, `inputs:exposure`, `inputs:color`, and color temperature.
- Describe Hydra, render delegates, and usdview, and know what `usd-core` cannot do.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **UsdLux** | Schema domain for lights, light filters, and light linking. |
| **LightAPI** | Applied API (built into typed lights) that owns `inputs:intensity`, `exposure`, `color`, … |
| **DistantLight** | Infinite parallel rays (the sun); default intensity **50000**. |
| **Sphere / Rect / Disk / Cylinder** | Local area lights with size attributes. |
| **DomeLight** | Image-based environment light (`inputs:texture:file`). |
| **ShadowAPI** | Applied API for shadow on/off, color, distance, falloff. |
| **ShapingAPI** | Applied API for spot cones (`shaping:cone:angle`) and IES focus. |
| **Exposure** | Power-of-two scale: rendered intensity ∝ `intensity × 2^exposure`. |
| **Color temperature** | Kelvin blackbody tint, used only when `enableColorTemperature` is true. |
| **Hydra** | USD's imaging framework: scene → render delegate → pixels. |
| **Render delegate** | A Hydra backend (Storm, RenderMan, Arnold, …). |
| **usdview** | The reference USD viewer (not shipped in `usd-core`). |

---

## 41.1 Light types (Distant, Sphere, Rect, Disk, Cylinder, Dome)

### 1. What is it?
UsdLux provides **typed light prims**. The six you must recognize: **DistantLight** (sun), **SphereLight**, **RectLight**, **DiskLight**, **CylinderLight**, and **DomeLight** (environment / HDRI). Each `Define`s like a Mesh: `UsdLux.RectLight.Define(stage, "/Lights/Key")`.

### 2. Why do we need it?
A PreviewSurface with roughness 0.1 still looks flat without a light. Exporters that drop lights produce "grey clay" in usdview even when materials are perfect. Shared light types are how DCCs exchange a key / fill / rim / dome.

### 3. Beginner explanation
Think of a film set. The **sun** through a window is Distant (parallel rays, very far). A **softbox** is Rect. A **bare bulb** is Sphere. A **snooted circular light** is Disk. A **fluorescent tube** is Cylinder. The **painted cyclorama / HDRI ball** is Dome.

*Where the analogy breaks:* USD lights do not consume watts from a generator. Intensity is a schema number; each render delegate maps it to its own photometric units.

### 4. Technical explanation
- All six are **Xformable** and **Imageable** (Chapter 39): they take xformOps, `visibility`, and `purpose`. They emit along local **−Z**, like cameras.
- **`LightAPI` is built in.** `HasAPI(UsdLux.LightAPI)` is True after `Define` even though USDA shows no `apiSchemas`. Built-in companions: `CollectionAPI:lightLink` and `CollectionAPI:shadowLink` (`includeRoot` fallback True = affect everything).
- **Boundable vs not.** Sphere, Rect, Disk, Cylinder (and Portal) are `BoundableLightBase` — they have size and an extent. Distant and Dome are `NonboundableLightBase` — infinite / environmental, no mesh-like extent.
- **Intensity fallbacks (verified 26.08):** DistantLight **50000**; every local type and Dome **1**. Distant also has `inputs:angle` (angular diameter in degrees, fallback **~0.53**, the real sun).
- Size fallbacks: Sphere / Disk `inputs:radius` **0.5**; Rect `inputs:width` / `height` **1**; Cylinder `inputs:length` **1**, `radius` **0.5**. Sphere has `treatAsPoint`; Cylinder has `treatAsLine` (both fallback False).
- Dome: `inputs:texture:file` (asset), `inputs:texture:format` (`automatic`, `latlong`, `angular`, `mirroredBall`). **`DomeLight_1`** adds `poleAxis` (fallback `scene`) so the HDRI follows stage `upAxis`. Prefer `_1` in new files; this book shows `DomeLight` because it is the name you will still see.
- **MeshLightAPI** applied to a Mesh turns geometry into a light (replaces the older `GeometryLight` typed prim). PortalLight is a window that admits dome light.

> [!VERSION] Verified on USD 26.08. Light attributes live in the **`inputs:`** namespace (`inputs:intensity`) since USD 21.02 so they can connect in a shading graph. Old files used bare `intensity`. Always author `inputs:`.

### 5. Mental model

```text
sun / directional     DistantLight     intensity fallback 50000   non-boundable
point-like / bulb     SphereLight      radius 0.5                 boundable
softbox               RectLight        width × height             boundable
circular / snoot      DiskLight        radius                     boundable
tube                  CylinderLight    length × radius            boundable
HDRI / sky            DomeLight        texture:file               non-boundable
```

### 6. Simple example
`/Lights/Distant` with no authored intensity still reports `Get() == 50000`. `/Lights/Sphere` reports `1`. That difference is a favorite exam trap.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Lights"
    upAxis = "Y"
)

def Xform "Lights"
{
    def DistantLight "Sun"
    {
        float inputs:intensity = 50000
        float inputs:angle = 0.53
        float xformOp:rotateX = -90
        uniform token[] xformOpOrder = ["xformOp:rotateX"]
    }

    def RectLight "Key"
    {
        float inputs:width = 2
        float inputs:height = 1
        float inputs:intensity = 8
        double3 xformOp:translate = (2, 3, 4)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }

    def DomeLight "Sky"
    {
        asset inputs:texture:file = @./sky.hdr@
        token inputs:texture:format = "latlong"
    }
}
```

- Empty `def DistantLight "Sun" {}` would still *behave* at intensity 50000; authoring the value makes the intent readable.
- `rotateX = -90` on a Y-up stage aims the Distant −Z axis downward (sun from above). Same convention as cameras (Chapter 39.7).

### 8. Python example

```python
from pxr import Usd, UsdLux

stage = Usd.Stage.CreateInMemory()
makers = [
    ("/Lights/Distant", UsdLux.DistantLight),
    ("/Lights/Sphere", UsdLux.SphereLight),
    ("/Lights/Rect", UsdLux.RectLight),
    ("/Lights/Disk", UsdLux.DiskLight),
    ("/Lights/Cylinder", UsdLux.CylinderLight),
    ("/Lights/Dome", UsdLux.DomeLight),
]
for path, cls in makers:
    prim = cls.Define(stage, path).GetPrim()
    api = UsdLux.LightAPI(prim)
    print(f"{prim.GetName()} {prim.GetTypeName()} "
          f"I={api.GetIntensityAttr().Get()} "
          f"boundable={prim.IsA(UsdLux.BoundableLightBase)}")
sun = UsdLux.DistantLight(stage.GetPrimAtPath("/Lights/Distant"))
print("sun angle:", round(sun.GetAngleAttr().Get(), 2))
print("sphere radius:",
      UsdLux.SphereLight(stage.GetPrimAtPath("/Lights/Sphere"))
      .GetRadiusAttr().Get())
print("rect size:",
      UsdLux.RectLight(stage.GetPrimAtPath("/Lights/Rect"))
      .GetWidthAttr().Get(),
      UsdLux.RectLight(stage.GetPrimAtPath("/Lights/Rect"))
      .GetHeightAttr().Get())
print("applied on Distant:",
      list(stage.GetPrimAtPath("/Lights/Distant").GetAppliedSchemas()))
```

**Expected output**
```text
Distant DistantLight I=50000.0 boundable=False
Sphere SphereLight I=1.0 boundable=True
Rect RectLight I=1.0 boundable=True
Disk DiskLight I=1.0 boundable=True
Cylinder CylinderLight I=1.0 boundable=True
Dome DomeLight I=1.0 boundable=False
sun angle: 0.53
sphere radius: 0.5
rect size: 1.0 1.0
applied on Distant: ['LightAPI', 'CollectionAPI:lightLink', 'CollectionAPI:shadowLink']
```

USDA for that Distant prim is still `def DistantLight "Distant" {}` — the applied schemas are **built in**, not authored.

### 9. Real-world use case
A product-shot USD ships `RectLight "Key"` and `"Fill"` plus `DomeLight "Studio"` with a lat-long HDRI. The manufacturing digital twin uses one `DistantLight` for the sun (intensity left at the 50000 fallback) and a `DomeLight` for sky. Games often import only the Dome as IBL and ignore local UsdLux, which is why the mapping table in Chapter 27 mentioned `KHR_lights_punctual`.

### 10. Common mistakes
> [!MISTAKE] Setting Distant `inputs:intensity = 1` because "that's the default for lights." You just made the sun 50 000× dimmer than the schema fallback. Use ~50000 or compensate with exposure.

> [!MISTAKE] Importing lights from `UsdGeom`. There is no `UsdGeom.DistantLight`. `from pxr import UsdLux`.

> [!MISTAKE] Forgetting xformOps. A RectLight at the origin, emitting −Z, may light the back of the set. Place it like a camera.

### 11. Exam traps
> [!TRAP] "All lights default intensity 1." DistantLight is **50000**.

> [!TRAP] USDA shows no `apiSchemas` on a DistantLight, so `HasAPI(LightAPI)` is False. It is **True** (built-in).

> [!TRAP] DomeLight `texture:file` is a Shader `UsdUVTexture`. No: it is an **attribute on the DomeLight** (`asset inputs:texture:file`).

### 12. Practice questions
1. Which light type is not boundable, besides Dome?
2. Unauthored Distant `inputs:intensity`. What does `Get()` return?
3. Which attribute aims a DistantLight at the set?

**Answers**
1. **DistantLight** (`NonboundableLightBase`).
2. **50000.0**
3. **xformOps** (typically a rotate so local −Z points toward the subject), same as a camera.

### 13. Exam takeaways
> [!KEY]
> - Six types: Distant, Sphere, Rect, Disk, Cylinder, Dome. Domain = **UsdLux**.
> - Distant fallback intensity **50000**; others **1**. Distant `angle` ≈ 0.53°.
> - Typed lights already have LightAPI + lightLink/shadowLink collections.
> - Emit along local −Z; place with xformOps. `inputs:` namespace since 21.02.

---

## 41.2 `LightAPI`, `ShadowAPI`, `ShapingAPI`

### 1. What is it?
**LightAPI** is the common applied schema on every UsdLux light: intensity, exposure, color, normalize, diffuse/specular weights, color temperature. **ShadowAPI** and **ShapingAPI** are *optional* applied APIs. Shadow controls whether the light casts shadows. Shaping turns a Disk/Rect/Sphere into a **spot** (`shaping:cone:angle`) or applies an IES profile.

### 2. Why do we need it?
Not every light needs a cone or a shadow toggle. Keeping those properties off the typed schema means a Distant sun is a short prim, and a theatrical spot is the same DiskLight plus two applied APIs. That is the same Apply pattern as `MaterialBindingAPI` (Chapter 40) — with one twist: LightAPI is already there.

### 3. Beginner explanation
LightAPI is the dimmer and gel that every lamp ships with. ShadowAPI is the optional barn-door / flag kit ("this lamp casts a shadow"). ShapingAPI is the snoot or cookie that squeezes the beam into a cone.

*Where the analogy breaks:* applying ShapingAPI does not change the prim **type**. It is still a DiskLight. Validators look at `apiSchemas`, not at a `SpotLight` type (USD has none).

### 4. Technical explanation
- **LightAPI** attributes (all `inputs:`): `intensity`, `exposure`, `color`, `enableColorTemperature`, `colorTemperature`, `normalize`, `diffuse`, `specular`. Also `light:shaderId` and `light:materialSyncMode` (advanced).
- Typed `Define` already applies LightAPI. Calling `LightAPI.Apply` again is legal but redundant; it authors `prepend apiSchemas = ["LightAPI"]` that was already built in.
- **ShadowAPI.Apply(prim)** then set `inputs:shadow:enable` (fallback **True**), `inputs:shadow:color` (fallback black), plus distance / falloff / falloffGamma. Until you Apply, `HasAPI(ShadowAPI)` is False even though the light may still cast shadows in a renderer using its own defaults.
- **ShapingAPI.Apply(prim)** then `inputs:shaping:cone:angle` (fallback **90**, i.e. a hemisphere), `inputs:shaping:cone:softness`, `inputs:shaping:focus`, `inputs:shaping:focusTint`, IES file / angle scale. A 30° cone is a spot.
- **MeshLightAPI.Apply(mesh)** makes a Mesh emit; it brings LightAPI (and the link collections) with it. USDA shows `prepend apiSchemas = ["MeshLightAPI"]` only — LightAPI is built into that API.
- **Light linking:** `CollectionAPI:lightLink` / `shadowLink` on the light. `includeRoot` True means "all geometry." Exclude paths to keep a light off a character. `LightListAPI` on a model caches a list of lights for the renderer.
- **LightFilter** is a typed prim for extra filters (barn doors, blockers) in the Lux family; know the name, do not memorize every filter.

> [!VERSION] Verified on USD 26.08. Contrast with Chapter 40: `MaterialBindingAPI` is **not** built into Mesh — you must `Apply`. `LightAPI` **is** built into `DistantLight` / `RectLight` / … You must `Apply` only ShadowAPI, ShapingAPI, and MeshLightAPI.

### 5. Mental model

```text
DiskLight "Spot"
  built-in:  LightAPI, CollectionAPI:lightLink, CollectionAPI:shadowLink
  authored:  prepend apiSchemas = ["ShadowAPI", "ShapingAPI"]
             inputs:shadow:enable
             inputs:shaping:cone:angle = 30
```

Type = DiskLight. Behavior = spot, because of applied APIs.

### 6. Simple example
Define `/Lights/Spot` as DiskLight. HasAPI LightAPI True, HasAPI ShadowAPI False. Apply Shadow + Shaping, set cone 30. USDA shows those two APIs in `apiSchemas`, not LightAPI.

### 7. USDA example

```usda
#usda 1.0

def DiskLight "Spot" (
    prepend apiSchemas = ["ShadowAPI", "ShapingAPI"]
)
{
    float inputs:intensity = 20
    bool inputs:shadow:enable = 1
    float inputs:shaping:cone:angle = 30
    float inputs:shaping:cone:softness = 0.2
    double3 xformOp:translate = (0, 3, 0)
    float xformOp:rotateX = -90
    uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateX"]
}
```

- `apiSchemas` lists **only** the extra APIs you applied.
- Cone angle 30 + rotateX −90 = a spotlight from above on a Y-up stage.

### 8. Python example

```python
from pxr import Usd, UsdLux

stage = Usd.Stage.CreateInMemory()
spot = UsdLux.DiskLight.Define(stage, "/Lights/Spot")
print("HasAPI LightAPI:", spot.GetPrim().HasAPI(UsdLux.LightAPI))
print("HasAPI Shadow before:",
      spot.GetPrim().HasAPI(UsdLux.ShadowAPI))
UsdLux.ShadowAPI.Apply(spot.GetPrim())
UsdLux.ShapingAPI.Apply(spot.GetPrim())
sh = UsdLux.ShadowAPI(spot.GetPrim())
sg = UsdLux.ShapingAPI(spot.GetPrim())
print("HasAPI Shadow:", spot.GetPrim().HasAPI(UsdLux.ShadowAPI))
print("HasAPI Shaping:", spot.GetPrim().HasAPI(UsdLux.ShapingAPI))
print("shadow enable fallback:", sh.GetShadowEnableAttr().Get())
print("cone angle fallback:", sg.GetShapingConeAngleAttr().Get())
sh.GetShadowEnableAttr().Set(True)
sg.GetShapingConeAngleAttr().Set(30.0)
sg.GetShapingConeSoftnessAttr().Set(0.2)
print("applied:", list(spot.GetPrim().GetAppliedSchemas()))
for line in stage.GetRootLayer().ExportToString().splitlines():
    if "apiSchemas" in line or "shadow" in line or "shaping" in line:
        print(line.strip())
```

**Expected output**
```text
HasAPI LightAPI: True
HasAPI Shadow before: False
HasAPI Shadow: True
HasAPI Shaping: True
shadow enable fallback: True
cone angle fallback: 90.0
applied: ['LightAPI', 'CollectionAPI:lightLink', 'CollectionAPI:shadowLink', 'ShadowAPI', 'ShapingAPI']
prepend apiSchemas = ["ShadowAPI", "ShapingAPI"]
bool inputs:shadow:enable = 1
float inputs:shaping:cone:angle = 30
float inputs:shaping:cone:softness = 0.2
```

`GetAppliedSchemas()` lists built-ins first; USDA `apiSchemas` lists only what you Applied.

### 9. Real-world use case
A stage play USD uses DiskLights with ShapingAPI cones parented to moving Xforms (follow spots). ShadowAPI stays enabled for the key, disabled on fill (`inputs:shadow:enable = 0`) so fill does not double the character's shadow. Light-link collections exclude the theatrical curtain so the key does not light the drape.

### 10. Common mistakes
> [!MISTAKE] Searching for `UsdLux.SpotLight`. There is none. Disk/Rect/Sphere + **ShapingAPI** is a spot.

> [!MISTAKE] Assuming ShadowAPI is built in because shadows appear in Storm. `HasAPI(ShadowAPI)` is False until `Apply`. Author it when you need an explicit off switch.

> [!MISTAKE] Applying LightAPI on every Mesh "to be safe." That does not make a mesh a light. Use **MeshLightAPI** (or a typed light prim).

### 11. Exam traps
> [!TRAP] "You must `LightAPI.Apply` before setting intensity, like MaterialBindingAPI." Intensity works without that `Apply` on typed lights; LightAPI is built in.

> [!TRAP] Cone fallback 30°. It is **90** (hemisphere). 30 is a value *you* author for a spot.

> [!TRAP] `bool inputs:shadow:enable = 1` in USDA is False because it is not `true`. In USDA, `1` is true for bools.

### 12. Practice questions
1. Name the two applied APIs that turn a DiskLight into a shadow-casting spot.
2. Does `def DistantLight "Sun" {}` have `HasAPI(LightAPI)` True?
3. Which API do you Apply to a Mesh to make it emit light?

**Answers**
1. **ShapingAPI** (cone) and **ShadowAPI** (shadows).
2. **Yes** — built-in, even with empty braces.
3. **`UsdLux.MeshLightAPI`.**

### 13. Exam takeaways
> [!KEY]
> - LightAPI is built into typed lights; ShadowAPI and ShapingAPI are opt-in `Apply`.
> - No SpotLight type: ShapingAPI cone on Disk/Rect/Sphere.
> - USDA `apiSchemas` shows extras; `GetAppliedSchemas()` also lists built-ins.
> - MeshLightAPI on a Mesh; lightLink/shadowLink collections for linking.

---

## 41.3 Intensity, exposure, color temperature

### 1. What is it?
Every LightAPI light has **intensity** (linear brightness), **exposure** (photographic stops, a power of two), **color** (an RGB gel), and optional **color temperature** in Kelvin. Rendered brightness scales as **`intensity × 2^exposure`**. Temperature applies only when **`enableColorTemperature`** is true.

### 2. Why do we need it?
Lighting TDs think in stops ("plus one stop") while TDs debugging a converter think in a single float. Exposure lets the artist add a stop without rewriting intensity. Color temperature matches real lamps (2700 K tungsten, 6500 K daylight) without picking RGB by eye.

### 3. Beginner explanation
Intensity is the dimmer's linear scale. Exposure is the camera's ISO/stop knob: each +1 doubles the light (`2^exposure`). Color is a gel taped on the lamp. Color temperature is "set the gel from a Kelvin chart," but the lamp ignores the chart until you flip **enableColorTemperature**.

*Where the analogy breaks:* USD does not guarantee nits or lumens. `normalize` (fallback False) asks the renderer to keep brightness independent of the light's area; delegates differ. Always check the delegate's UsdLux notes.

### 4. Technical explanation
- `inputs:intensity` (float). Fallback **1** on local lights / Dome, **50000** on Distant (§41.1).
- `inputs:exposure` (float, fallback **0**). Formula used by UsdLux: **final ∝ intensity × 2^exposure**. Exposure 2 with intensity 3 → scale 3 × 4 = 12.
- `inputs:color` (color3f, fallback white `(1, 1, 1)`).
- `inputs:enableColorTemperature` (bool, fallback **False**). `inputs:colorTemperature` (float, fallback **6500**, daylight). When enabled, the renderer tints using a blackbody curve. Python helper: `UsdLux.BlackbodyTemperatureAsRgb(kelvin)` → `Gf.Vec3f` (verified: 2700 K ≈ `(1.9353, 0.8036, 0.1917)`).
- `inputs:normalize` (bool, fallback False): when True, intensity is per-area so scaling a RectLight up does not make it brighter.
- `inputs:diffuse` / `inputs:specular` (float, fallback 1): weights for those lobes. Set specular 0 for a fill that should not sparkle in the eye.
- These are connectable **inputs** (same `inputs:` idea as UsdShade). A stronger layer can override them; a shader could theoretically connect to them.

### 5. Mental model

```text
emitted ~  color  ×  intensity  ×  2^exposure  ×  (blackbody if enableColorTemperature)

  2700 K tungsten     enableColorTemperature = true
  6500 K daylight     fallback temperature (ignored until enable is true)
```

### 6. Simple example
Sphere bulb: intensity 3, exposure 2, color (1, 0.9, 0.8), enableColorTemperature true, 2700 K. USDA authors all five `inputs:`.

### 7. USDA example

```usda
#usda 1.0

def SphereLight "Bulb"
{
    color3f inputs:color = (1, 0.9, 0.8)
    float inputs:colorTemperature = 2700
    bool inputs:enableColorTemperature = 1
    float inputs:exposure = 2
    float inputs:intensity = 3
    bool inputs:normalize = 0
    float inputs:radius = 0.5
}
```

- Without `enableColorTemperature = 1`, the 2700 value is authored but unused.
- `exposure = 2` is two stops up (×4), not "plus 2 intensity."

### 8. Python example

```python
from pxr import Usd, UsdLux

stage = Usd.Stage.CreateInMemory()
bulb = UsdLux.SphereLight.Define(stage, "/Lights/Bulb")
api = UsdLux.LightAPI(bulb.GetPrim())
api.GetIntensityAttr().Set(3.0)
api.GetExposureAttr().Set(2.0)
api.GetColorAttr().Set((1.0, 0.9, 0.8))
api.GetEnableColorTemperatureAttr().Set(True)
api.GetColorTemperatureAttr().Set(2700.0)
rgb = UsdLux.BlackbodyTemperatureAsRgb(2700)
print("intensity:", api.GetIntensityAttr().Get())
print("exposure:", api.GetExposureAttr().Get())
print("2**exposure:", 2 ** api.GetExposureAttr().Get())
print("color:", api.GetColorAttr().Get())
print("enableColorTemperature:",
      api.GetEnableColorTemperatureAttr().Get())
print("colorTemperature:", api.GetColorTemperatureAttr().Get())
print("2700K rgb:", tuple(round(c, 4) for c in rgb))
print("normalize fallback:", api.GetNormalizeAttr().Get())
for line in stage.GetRootLayer().ExportToString().splitlines():
    if "inputs:" in line:
        print(line.strip())
```

**Expected output**
```text
intensity: 3.0
exposure: 2.0
2**exposure: 4.0
color: (1, 0.9, 0.8)
enableColorTemperature: True
colorTemperature: 2700.0
2700K rgb: (1.9353, 0.8036, 0.1917)
normalize fallback: False
color3f inputs:color = (1, 0.9, 0.8)
float inputs:colorTemperature = 2700
bool inputs:enableColorTemperature = 1
float inputs:exposure = 2
float inputs:intensity = 3
```

The USDA dump matches §7 (plus the unauthored radius fallback, which is not written).

### 9. Real-world use case
A practical tungsten lamp on a film set is a SphereLight at 2700 K with `enableColorTemperature` on. The gaffer adds one stop in the shot layer by setting `inputs:exposure = 1` rather than multiplying intensity, so the published asset's intensity stays a round number. Daylight plates keep 6500 K and usually leave enable off, relying on `inputs:color` from the HDRI dome instead.

### 10. Common mistakes
> [!MISTAKE] Authoring `colorTemperature = 2700` and leaving `enableColorTemperature` false. The light stays white (or whatever `inputs:color` is). Flip the bool.

> [!MISTAKE] Treating exposure as additive intensity (`intensity + exposure`). It is **stops**: `2^exposure`.

> [!MISTAKE] Using `BlackbodyTemperatureAsRgb` as the authored `inputs:color` *and* enabling temperature, double-tinting. Pick one: Kelvin+enable, or a gel RGB.

### 11. Exam traps
> [!TRAP] Fallback color temperature 2700 K. It is **6500**. 2700 is a value you author for tungsten.

> [!TRAP] "Color temperature replaces intensity." It tints; intensity/exposure still scale brightness.

> [!TRAP] `inputs:intensity` vs old `intensity`. Exam USDA that shows bare `intensity` is pre-21.02; the current name is `inputs:intensity`.

### 12. Practice questions
1. Intensity 2, exposure 3. By what factor does exposure scale the light?
2. When does `inputs:colorTemperature` affect the render?
3. What Python helper converts 2700 K to RGB?

**Answers**
1. **×8** (`2^3`). Combined scale 2 × 8 = 16.
2. Only when **`enableColorTemperature` is true**.
3. **`UsdLux.BlackbodyTemperatureAsRgb(2700)`.**

### 13. Exam takeaways
> [!KEY]
> - Brightness ∝ `intensity × 2^exposure`. Exposure 0 is a no-op.
> - Distant intensity fallback 50000; local 1; exposure fallback 0.
> - Color temperature is ignored until `enableColorTemperature` is true (fallback temp 6500).
> - `inputs:` names; `normalize` keeps intensity per-area when True.

---

## 41.4 Hydra, render delegates, usdview (concepts)

### 1. What is it?
**Hydra** is OpenUSD's imaging architecture: it takes a composed stage and asks a **render delegate** to produce pixels. **usdview** is the reference application that hosts Hydra. A **render delegate** is a plug-in backend — Storm (OpenGL rasterizer), RenderMan, Arnold, Cycles, and others. **`UsdRender.Settings`** is the schema for render settings (resolution, products) stored *in* the stage.

### 2. Why do we need it?
Authoring PreviewSurface and UsdLux is pointless if you cannot name the thing that *draws* them. Exam questions say "in usdview" or "the Storm delegate" or "Hydra." You must know the pipeline even when your pip package cannot open a window.

### 3. Beginner explanation
Think of a mixing desk (the stage) plugged into different speakers. Hydra is the amp rack. Storm is the cheap rehearsal speaker (fast, GL). RenderMan is the concert PA (slow, beautiful). usdview is the room where you pick which speaker is plugged in. Switching delegates does not rewrite the USD; it changes who interprets materials and lights.

*Where the analogy breaks:* some delegates ignore parts of UsdLux or PreviewSurface, or only read `purpose = render`. The file is the same; the picture is not.

### 4. Technical explanation
- **Pipeline:** composed `Usd.Stage` → Hydra **scene index** (Chapter 38: the modern imaging filter graph) → **render delegate** → framebuffer or EXR. Older path: Hydra primary adapter / UsdImaging hydra plugin. `usd-core` 26.8 ships **neither** `UsdImaging` nor `Hd`.
- **Storm** (`HdStorm`) is the default raster delegate in usdview: good for layout, purpose, PreviewSurface, simple UsdLux. It is not a production path tracer.
- **usdview** features you will see named: viewport, **Metal/GL**, **purpose** filters (proxy / render / guide, Chapter 39.6), **Lights** on/off, Hydra renderer dropdown, Layer Stack / Composition tabs (Chapter 22). Command: `usdview shot.usda` (not runnable here).
- **Material purpose** (Chapter 40.6 `preview` / `full`) is how usdview's preview pass picks PreviewSurface while a film delegate may bind `full`.
- **`UsdRender.Settings`**, `RenderProduct`, `RenderVar`: describe cameras, resolution, and AOVs inside USD so `usdrecord` / batch renderers do not need a side-car XML. Present in `usd-core`.
- **usdrecord** renders frames through Hydra from the command line. Same limitation: not in `usd-core`.
- Changing a light's intensity is a stage edit; Hydra notices via the same change pipeline as Chapter 34 (`ObjectsChanged`). You do not restart usdview to see a new intensity.

> [!VERSION] Verified on USD 26.08. `from pxr import UsdImaging` and `from pxr import Hd` raise `ImportError` in this book's `.venv`. Teach Hydra as concepts; keep examples that *run* limited to schema authoring and `UsdRender.Settings`.

### 5. Mental model

```text
.usda / .usdc
    → Usd.Stage (composition, LIVERPS)
        → Hydra scene index
            → render delegate   Storm | Prman | Arnold | …
                → pixels in usdview / usdrecord / DCC viewport
```

No delegate, no picture. The stage does not know about pixels.

### 6. Simple example
`usdview set.usda` opens Storm, draws meshes with PreviewSurface, uses UsdLux Distant + Dome. Switching the Hydra dropdown to a RenderMan delegate still reads the same prims; shadows and Dome importance sampling change.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def Mesh "Ground" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {
        rel material:binding = </Looks/Clay>
    }

    def DistantLight "Sun"
    {
        float inputs:intensity = 50000
    }
}

def Scope "Looks"
{
    def Material "Clay" {}
}

def Scope "Render"
{
    def RenderSettings "Settings"
    {
    }
}
```

- Geometry, a light, a (stub) material bind, and a RenderSettings prim: the four prims a Hydra app looks for.
- `RenderSettings` is authored data; it does not draw by itself.

### 8. Python example
This block checks what `usd-core` actually imports and authors a `RenderSettings` prim.

```python
print("UsdImaging imported:", end=" ")
try:
    from pxr import UsdImaging
    print(True)
except ImportError:
    print(False)
print("Hd imported:", end=" ")
try:
    from pxr import Hd
    print(True)
except ImportError:
    print(False)

from pxr import Usd, UsdRender

stage = Usd.Stage.CreateInMemory()
settings = UsdRender.Settings.Define(stage, "/Render/Settings")
print("render settings:", settings.GetPrim().GetTypeName())
```

**Expected output**
```text
UsdImaging imported: False
Hd imported: False
render settings: RenderSettings
```

Usdview itself is a command-line tool, not a Python import. Mark it `.norun` when you quote it:

```{.python .norun}
# Not in usd-core; requires a full OpenUSD / NVIDIA inventory build.
# usdview shot.usda
# usdrecord --camera /Shot/Cam --frames 1001:1100 shot.usda out.#.exr
```

### 9. Real-world use case
A layout artist in usdview / Storm places RectLights and checks proxy purpose. Lighting opens the same USD in a DCC with the RenderMan delegate, which reads `purpose = render` meshes, `material:binding:full`, and DomeLight importance samples. Batch `usdrecord` uses `RenderSettings` for resolution. Nobody converts the file between those apps.

### 10. Common mistakes
> [!MISTAKE] Expecting `pip install usd-core` to provide usdview. It does not (Chapter F5). On Windows and Linux, NVIDIA's OpenUSD prebuilts include usdview; otherwise build with imaging.

> [!MISTAKE] Assuming Storm matches the beauty render. Storm is a raster preview. Lookdev sign-off needs the production delegate.

> [!MISTAKE] Putting renderer-specific attributes only on `RenderSettings` and omitting UsdLux. Delegates still need the light prims.

### 11. Exam traps
> [!TRAP] "Hydra is a renderer." Hydra is the **framework**; Storm / Prman / Arnold are **delegates**.

> [!TRAP] Mixing Imageable `purpose` (`proxy`/`render`/`guide`) with material-binding purpose (`preview`/`full`). Both affect usdview; they are different schemas (Ch 39.6 vs Ch 40.6).

> [!TRAP] `UsdImaging` is part of `usd-core` because UsdGeom is. Geom is data; imaging is the optional view plugin.

### 12. Practice questions
1. What is Storm in one sentence?
2. Does `usd-core` 26.8 import `UsdImaging`?
3. Which schema stores resolution / products in the stage?

**Answers**
1. Hydra's **OpenGL raster render delegate**, usdview's default preview backend.
2. **No** (`ImportError`).
3. **`UsdRender.Settings`** (type `RenderSettings`).

### 13. Exam takeaways
> [!KEY]
> - Hydra = imaging framework; a **render delegate** draws pixels.
> - usdview hosts Hydra (Storm by default); not shipped in `usd-core`.
> - Imageable purpose and material purpose both affect what you see; they are not the same.
> - `UsdRender.Settings` is authorable in `usd-core`; `UsdImaging` / `Hd` are not.

---

## Chapter lab(s)

**Lab 35 — Lights with UsdLux** (★★☆, Obj 8.x). You define a Distant sun (leave or author intensity 50000), a Rect key with xformOps, a Disk spot with ShapingAPI + ShadowAPI, and a Dome with `texture:file`. You set exposure vs intensity and enable 2700 K on a Sphere practical. Stretch: MeshLightAPI on a panel, lightLink exclude.

## USDA reading exercise(s)

**Exercise 41-A.** A set is nearly black in usdview despite a sun prim. Why, given this USDA?

```usda
#usda 1.0

def DistantLight "Sun"
{
    float inputs:intensity = 1
    float inputs:exposure = 0
}
```

**Exercise 41-B.** Is `/Lights/Spot` a spot, and does it have LightAPI?

```usda
#usda 1.0

def DiskLight "Spot" (
    prepend apiSchemas = ["ShapingAPI"]
)
{
    float inputs:shaping:cone:angle = 25
}
```

**Exercise 41-C.** Will this bulb render as tungsten orange?

```usda
#usda 1.0

def SphereLight "Practical"
{
    float inputs:colorTemperature = 2700
    float inputs:intensity = 5
}
```

## Chapter review

### Summary
- UsdLux typed lights: Distant, Sphere, Rect, Disk, Cylinder, Dome. Emit −Z. Distant intensity fallback 50000; others 1.
- LightAPI is built in; Apply ShadowAPI / ShapingAPI / MeshLightAPI when you need them. No SpotLight type.
- Brightness ∝ intensity × 2^exposure. Color temperature needs `enableColorTemperature`.
- Hydra delegates draw; usdview/Storm/UsdImaging are not in `usd-core`. `UsdRender.Settings` is.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Dim sun, `inputs:intensity = 1` | Distant fallback is 50000 |
| `SpotLight` as a prim type | Does not exist; ShapingAPI on Disk/Rect |
| Empty `def DistantLight "Sun" {}` | Still HasAPI LightAPI; intensity 50000 |
| `prepend apiSchemas = ["ShadowAPI"]` | Extra API; LightAPI is built-in already |
| `colorTemperature` but still white | `enableColorTemperature` is false |
| `exposure = 2` | ×4, not +2 |
| `inputs:intensity` vs `intensity` | Post-21.02 namespace |
| usdview / Storm / Hydra | Framework vs delegate vs app; not in usd-core |
| `purpose = proxy` vs `material:binding:preview` | Imageable vs material purpose |
| Mesh that emits | `MeshLightAPI`, not LightAPI alone |

### Review questions

**Q41.1** · Obj 8.x · Easy · Single choice
Which module defines `RectLight`?
A. UsdGeom · B. UsdShade · C. UsdLux · D. UsdRender

**Q41.2** · Obj 8.x · Easy · Single choice
Unauthored DistantLight intensity `Get()` returns:
A. 1.0 · B. 0.0 · C. 50000.0 · D. None

**Q41.3** · Obj 8.x · Medium · Select two.
Which lights are *not* `BoundableLightBase`?
A. DistantLight · B. RectLight · C. DomeLight · D. SphereLight

**Q41.4** · Obj 8.x · Medium · Single choice
How do you author a spotlight in UsdLux?
A. `UsdLux.SpotLight.Define` · B. Disk/Rect/Sphere + `ShapingAPI` cone · C. `UsdGeom.Cone` + LightAPI · D. DomeLight with `angle`

**Q41.5** · Obj 8.x · Medium · Single choice
`def DistantLight "Sun" {}` — `HasAPI(UsdLux.LightAPI)` is:
A. False until `LightAPI.Apply` · B. True (built-in) · C. True only if intensity is authored · D. An error

**Q41.6** · Obj 8.x · Easy · Single choice
Intensity 1, exposure 2. Relative brightness vs intensity 1 exposure 0:
A. Same · B. ×2 · C. ×4 · D. +2

**Q41.7** · Obj 8.x · Medium · Single choice
`inputs:colorTemperature = 2700` with no other temperature attrs. Effect?
A. Tungsten tint · B. None; enable is false · C. Replaces intensity with 2700 · D. Blackbody is multiplied twice

**Q41.8** · Obj 8.x · Easy · Single choice
UsdLux attributes such as intensity are named:
A. `intensity` · B. `inputs:intensity` · C. `light:intensity` · D. `outputs:intensity`

**Q41.9** · Obj 8.x · Medium · Select two.
Which imports fail on `usd-core` 26.8?
A. `from pxr import UsdLux` · B. `from pxr import UsdImaging` · C. `from pxr import Hd` · D. `from pxr import UsdRender`

**Q41.10** · Obj 8.x · Medium · Single choice
Storm is:
A. A path tracer · B. Hydra's GL raster render delegate · C. A UsdShade shader id · D. A file format

**Q41.11** · Obj 8.x · Easy · Single choice
Lights emit in which local direction (same as cameras)?
A. +Y · B. +Z · C. −Z · D. −X

**Q41.12** · Obj 8.x · Medium · USDA reading
What is the cone angle of `/Lights/Key`?

```usda
#usda 1.0

def RectLight "Key"
{
    float inputs:intensity = 10
}
```

A. 90 · B. 30 · C. Unauthored; no ShapingAPI, so not a cone light · D. 0.53

### Answers

**Q41.1 — C.** UsdLux is the light domain. Review: §41.1.

**Q41.2 — C.** Distant fallback is 50000. Review: §41.1, §41.3.

**Q41.3 — A, C.** Distant and Dome are `NonboundableLightBase`. Review: §41.1.

**Q41.4 — B.** There is no SpotLight type. Review: §41.2.

**Q41.5 — B.** Built-in applied schema. Review: §41.1–41.2.

**Q41.6 — C.** `2^2 = 4`. Review: §41.3.

**Q41.7 — B.** `enableColorTemperature` fallback is False. Review: §41.3.

**Q41.8 — B.** Since 21.02. Review: §41.1, §41.3.

**Q41.9 — B, C.** UsdLux and UsdRender import; imaging / Hd do not. Review: §41.4.

**Q41.10 — B.** usdview's default delegate. Review: §41.4.

**Q41.11 — C.** Local −Z. Review: §41.1.

**Q41.12 — C.** No ShapingAPI, so no cone. 90 is the *fallback if* ShapingAPI is applied; 0.53 is Distant `angle`. Review: §41.2.

### USDA exercise answers

**41-A — Intensity 1 on a DistantLight is ~50 000× below the schema fallback.** Storm/usdview will look almost unlit next to a default sun. Author ~50000 or raise exposure (~15–16 stops to compensate — not practical). The prim type is correct; the number is wrong.

**41-B — Yes it is a spot (cone 25 via ShapingAPI), and yes it has LightAPI.** LightAPI is built into DiskLight; USDA does not list it. ShadowAPI is not applied.

**41-C — No.** `enableColorTemperature` is missing (fallback false), so 2700 K is unused. The bulb is white at intensity 5. Add `bool inputs:enableColorTemperature = 1`.

## Further reading

- [S06] OpenUSD API — UsdLuxLightAPI, UsdLuxShadowAPI, UsdLuxShapingAPI, typed lights, UsdRenderSettings: https://openusd.org/release/api/usd_lux_page_front.html
- [S04] OpenUSD Glossary (Hydra, render delegate): https://openusd.org/release/glossary.html
- [S14] NVIDIA Learn OpenUSD — lighting and usdview: https://docs.nvidia.com/learn-openusd/latest/index.html
- Chapter 39.6–39.7 (purpose, cameras / −Z), Chapter 40.6 (material purpose), Chapter 38 (scene indices)
