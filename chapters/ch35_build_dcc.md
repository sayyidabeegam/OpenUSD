# Chapter 35 — Build Configurations and DCC Integration

> **Exam domain:** Pipeline Development (14%), also Customizing USD (6%) · **Objectives:** 3.1, 3.2, 7.4, 7.8 · **Study day:** 10 · **Est. time:** 80 min
> **Prerequisites:** Ch 1 (the USD stack), Ch 27 / 29 (exchange and DCC importers), Ch 33 (resolvers), Ch 34 (hooks, notices)

This chapter is how USD **gets onto a machine** and **into a DCC**. Obj 3.1 / 3.2 are "build a plugin against a given USD" and "build USD from scratch." Obj 7.4 / 7.8 are round-trip pipelines and writing a DCC importer. `usd-core` in this book's venv is a **wheel**, not a source build — we teach the official build map, then run what 26.08 Python actually exposes (`Usd.GetVersion`, `UsdPhysics`).

## Learning goals

- Describe `build_usd.py` / CMake as the way you compile USD and optional components.
- Match a plugin's USD version to the DCC's USD version (Obj 3.1).
- Design a DCC round-trip that does not drop custom data, units, or payloads (Obj 7.4, 7.8).
- Apply `UsdPhysics` APIs (`RigidBodyAPI`, `CollisionAPI`, `PhysicsScene`, `kilogramsPerUnit`) in a pipeline.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **`build_usd.py`** | Pixar's Python wrapper around CMake that compiles OpenUSD |
| **Monolithic vs shared** | One fat library vs many `.so`/`.dll` plugins |
| **ABI** | Binary interface; plugins built against USD *N* must not load in USD *M* |
| **DCC** | Digital content creation app (Maya, Houdini, 3ds Max, Blender, CAD, …) |
| **Round-trip** | Export to USD and import back without silent data loss |
| **`UsdPhysics`** | Schema domain for rigid bodies, collisions, joints, mass |
| **`kilogramsPerUnit`** | Stage metadata: how many kilograms one USD mass unit is |

---

## 35.1 Building USD (`build_usd.py`, CMake options)

### 1. What is it?

**Building USD** means compiling the C++ libraries, Python bindings, plugins, and (optionally) tools such as `usdview` from the OpenUSD source. Pixar ships `build_scripts/build_usd.py`. Under it, **CMake** selects which domains and third-party libraries you get.

### 2. Why do we need it?

The `usd-core` wheel is enough to *author* layers. It does **not** include `usdview`, `usdcat`, Hydra imaging, MaterialX (`UsdMtlx`), or `usdGenSchema`. A studio that needs those — or a patched USD — builds from source (Obj 3.2). A plugin author must build **against the same tree** the DCC loads (Obj 3.1).

### 3. Beginner explanation

Buying a ready-made bicycle (`usd-core` / a DCC's bundled USD) vs welding your own frame from a kit (`build_usd.py`). The kit lets you add lights, a different wheel size, or a custom rack (Hydra, MaterialX, your resolver). You cannot bolt a rack built for a 2024 frame onto a 2026 bike without checking the mounts (ABI).

*Where the analogy breaks:* you do not rebuild USD to *use* it in this book. You rebuild when you need a component the wheel omitted, or when you ship a C++ plugin.

### 4. Technical explanation

Official flow (not runnable in this venv; commands are illustrative):

```{.bash .norun}
python build_scripts/build_usd.py /opt/usd \
    --python --usdview \
    --build-args USD,"-DPXR_BUILD_USD_PHYSICS=ON"
```

Typical CMake knobs (names you should recognize, not memorize every flag):

| Area | What it controls |
|------|------------------|
| `PXR_BUILD_USD_PHYSICS` | `UsdPhysics` schemas |
| `PXR_BUILD_IMAGING` / `PXR_BUILD_USD_IMAGING` | Hydra, `usdview` |
| `PXR_BUILD_MATERIALX_PLUGIN` | MaterialX file format / `UsdMtlx` |
| Python bindings | Whether `from pxr import Usd` works for that install |
| Monolithic (`PXR_BUILD_MONOLITHIC`) | One library vs many plugin libraries |

This book's **verified** install:

- Package: `usd-core` **26.8** → API `Usd.GetVersion() == (0, 26, 8)`
- Present: `UsdPhysics`, `UsdShade`, `UsdLux`, `UsdSkel`, `UsdValidation`, `Trace`
- Absent: `UsdImaging`, `UsdMtlx`, CLI tools (`usdcat`, `usdview`, `usdGenSchema`)

> [!VERSION] `Usd.GetVersion()` returns **`(0, 26, 8)`** for OpenUSD 26.08. The leading `0` is the historical major field. Do not write a check that compares `GetMajorVersion() == 26`.

`build_usd.py` also downloads or uses system TBB, Boost, OpenSubdiv, etc. Obj 3.2 "custom dependencies" means: you point CMake at *your* TBB/Python, not a mystery copy from another DCC.

### 5. Mental model

```text
  source  --build_usd.py / CMake-->  libusd, plugins, optional usdview
  usd-core wheel ----------------->  Python pxr.* only (this book)

  GetVersion()  (0, 26, 8)  ==  OpenUSD 26.08
```

### 6. Simple example

A farm image has no GUI. You build USD with imaging **off** and Python **on**. Artists' workstations build with `--usdview`. Both must still be 26.08 if they share plugin `.so` files.

### 7. USDA example

Build flags are not stored in USDA. Version metadata you *can* put on a layer for the pipeline:

```usda
#usda 1.0
(
    customLayerData = {
        string usdVersion = "26.08"
        string generator = "studio_export 4.2"
    }
)
```

`customLayerData` is layer metadata (Ch 12). It does not change `GetVersion()` of the running library.

### 8. Python example

```{.python .norun}
from pxr import UsdImaging  # ModuleNotFoundError on usd-core
```

That import is expected to **fail** on `usd-core`. The runnable check:

```python
from pxr import Usd, UsdPhysics
import pkgutil
import pxr

print("GetVersion", Usd.GetVersion())
print("major,minor,patch", Usd.GetMajorVersion(),
      Usd.GetMinorVersion(), Usd.GetPatchVersion())
mods = sorted(m.name for m in pkgutil.iter_modules(pxr.__path__))
print("has UsdPhysics", "UsdPhysics" in mods)
print("has UsdImaging", "UsdImaging" in mods)
print("has UsdMtlx", "UsdMtlx" in mods)
print("RigidBodyAPI", hasattr(UsdPhysics, "RigidBodyAPI"))
```

**Expected output**

```text
GetVersion (0, 26, 8)
major,minor,patch 0 26 8
has UsdPhysics True
has UsdImaging False
has UsdMtlx False
RigidBodyAPI True
```

### 9. Real-world use case

A studio's IT runs `build_usd.py` once per USD upgrade, with a locked TBB and Python 3.11 matching Maya's. The same prefix is used to compile the studio resolver (Ch 33) and schema plugin (Ch 37). DCC plugin builds take `-I/opt/usd/include` from that prefix — never from a second stray USD.

### 10. Common mistakes

> [!MISTAKE] Mixing `usd-core` from pip with a DCC's `pxr` on `PYTHONPATH`. Two USDs in one process. Fix: one prefix.

> [!MISTAKE] Reading `GetMajorVersion() == 26`. It is `0`; minor is `26`.

> [!MISTAKE] Assuming `usdview` appears after `pip install usd-core`. Use NVIDIA's Windows/Linux prebuilts (Chapter F5) or build with imaging.

### 11. Exam traps

> [!TRAP] "Obj 3.2 is `pip install`." Building from scratch is CMake/`build_usd.py` and *your* dependencies.

> [!TRAP] "`usd-core` includes Hydra." `UsdImaging` is missing here.

> [!TRAP] Version string `"26.8"` vs `"26.08"` vs tuple `(0, 26, 8)`. Know all three labels.

### 12. Practice questions

**Q35.1-1.** `Usd.GetVersion()` on this book's venv is:
A. `(26, 8, 0)`
B. `(0, 26, 8)`
C. `"26.08"`
D. `(26, 0, 8)`

**Q35.1-2.** Select two components **not** in `usd-core` 26.8.
A. `UsdPhysics`
B. `UsdImaging`
C. `UsdMtlx`
D. `UsdShade`

**Answers**

- **Q35.1-1: B.** Historical major `0`, minor `26`, patch `8`.
- **Q35.1-2: B and C.** Physics and Shade **are** present.

### 13. Exam takeaways

> [!KEY]
> - Source builds use `build_usd.py` / CMake; `usd-core` is a Python subset.
> - `GetVersion()` → `(0, 26, 8)` for OpenUSD 26.08.
> - Imaging, MaterialX, CLI tools, `usdGenSchema` need a full build.
> - Obj 3.2: you choose the third-party libraries CMake links.

---

## 35.2 Matching plugin builds to USD versions

### 1. What is it?

A **plugin** (resolver, schema, file format, Hydra delegate) is a shared library compiled against **one** USD ABI. **Matching** means the DCC, the farm, and the plugin were all built with that same USD version and the same C++ compiler/C++ standard (Obj 3.1).

### 2. Why do we need it?

Loading a 25.11 schema plugin into 26.08 usdview is a crash or a silent miss, not a friendly error. Pipelines die at "it worked in Maya."

### 3. Beginner explanation

A trailer hitch rated for one car year. The plugin is the trailer. USD is the car. Same-year hitch (headers + libusd) or the trailer falls off.

*Where the analogy breaks:* Python-only tools that use `usd-core` via `from pxr import Usd` are not C++ plugins. They still must not import a second `pxr`. Codeless schemas (Ch 37) are XML/USDA and are gentler, but C++ schema generated code is not.

### 4. Technical explanation

Checklist studios write next to Chapter 32's guidelines:

| Check | Why |
|-------|-----|
| Same `Usd.GetVersion()` in DCC and plugin host | ABI |
| Same build flavor (monolithic vs shared) | Link errors |
| `PXR_PLUGINPATH_NAME` points at **this** USD's plugin dir plus studio plugins | Wrong `plugInfo.json` = missing types |
| One `PYTHONPATH` / `PATH` / `LD_LIBRARY_PATH` prefix | Two libusd in one process |
| Rebuild plugins on every USD bump | Obj 3.1 "against a given version" |

`Plug.Registry().GetAllPlugins()` lists loaded plugin names (`usdPhysics`, `usdGeom`, …). A studio plugin that did not load will not appear. Set `PXR_PLUGINPATH_NAME` **before** the first `from pxr import …` in some hosts; in others the DCC loads USD first — then you append via that host's plugin path UI.

Python:

```{.python .norun}
# Conceptual: run inside the DCC's Python, not a second venv
from pxr import Usd
assert Usd.GetVersion() == (0, 26, 8)
```

Do not copy Maya's `pxr` into this book's `.venv`.

### 5. Mental model

```text
  Maya 26.08  <---- plugin.so built with 26.08 headers
  farm 26.08  <---- same .so
  usdview 25.11  --X--  that .so   (wrong year)
```

### 6. Simple example

IT ships `StudioResolver.so` in ` /opt/studio/usd/26.08/plugin `. Maya, the farm, and usdview all use `/opt/usd/26.08`. After upgrading to 26.11 they rebuild the resolver; they do not reuse the 26.08 `.so`.

### 7. USDA example

USDA cannot record ABI. A publish may still stamp the generator:

```usda
#usda 1.0
(
    customLayerData = {
        string usdVersion = "26.08"
        string pluginSet = "studio-36"
    }
)
```

The farm's opener refuses layers whose `usdVersion` is newer than the host.

### 8. Python example

```python
from pxr import Plug, Usd

print("version", Usd.GetVersion())
names = sorted(p.name for p in Plug.Registry().GetAllPlugins())
print("n plugins", len(names))
print("has usdPhysics", "usdPhysics" in names)
print("has usdGeom", "usdGeom" in names)
```

**Expected output**

```text
version (0, 26, 8)
n plugins 27
has usdPhysics True
has usdGeom True
```

If `usdPhysics` were missing here, either the wheel omitted it (it does not) or `PXR_PLUGINPATH_NAME` hid the default plugins. That is the matching debug for Obj 3.1.

### 9. Real-world use case

Houdini ships a USD. The studio also builds usdview. They **pin Houdini's USD** for Solaris plugins and a **separate** 26.08 prefix for standalone tools, and they never copy `.so` files between those two prefixes.

### 10. Common mistakes

> [!MISTAKE] Dropping a plugin into `PXR_PLUGINPATH_NAME` built with a different `_GLIBCXX` / MSVC. Load fails with an unreadable dynamic-linker error.

> [!MISTAKE] Using `LD_PRELOAD` to force one libusd over another. You now have two heaps. Don't.

### 11. Exam traps

> [!TRAP] "Any USD plugin loads in any USD because USDA is text." C++ plugins are binary.

> [!TRAP] "Codeless schemas need a matching ABI too." Codeless still need a USD that understands the schema file format; they do not ship a `.so` of generated accessors (Ch 37).

### 12. Practice questions

**Q35.2-1.** Obj 3.1 "build a plugin against a given version" means:
A. Recompile the plugin with that USD's headers and libraries
B. Rename `plugInfo.json` to the version number
C. Set `kind = component`
D. Flatten the plugin into the stage

**Q35.2-2.** Select two matching failures.
A. 25.11 `.so` in a 26.08 usdview
B. Two `libusd` on `LD_LIBRARY_PATH`
C. USDA `upAxis = Y`
D. `defaultPrim` missing

**Answers**

- **Q35.2-1: A.** Headers + libs of that build.
- **Q35.2-2: A and B.** C and D are data, not ABI.

### 13. Exam takeaways

> [!KEY]
> - One USD version per process; plugins rebuilt per bump.
> - `GetVersion()` in the DCC must match the plugin's build.
> - `PXR_PLUGINPATH_NAME` loads *this* tree's `plugInfo.json`.
> - Count `GetAllPlugins()` when a type "does not exist."

---

## 35.3 DCC round-trips (importer / exporter integration)

### 1. What is it?

A **round-trip** is export from a DCC to USD and import back (or USD → DCC → USD) so the scene is still the same in the ways the pipeline promised (Obj 7.4, 7.8). Chapter 27 gave the data-mapping document. Chapter 29 gave importer shape. Here you **wire** those into the DCC: same hooks, same resolver context, same version.

### 2. Why do we need it?

A DCC that drops payloads, secretly Flattens, or rewrites `@./tex.png@` to `@C:\Users\...@` on Save destroys the pipeline. Round-trip tests catch that before artists notice on the farm.

### 3. Beginner explanation

A bilingual meeting with a translator both ways. If the joke survives the return trip, the translator is good. If the punchline becomes a cube, you need a new importer.

*Where the analogy breaks:* some loss is **documented** (NURBS → tessellated mesh). Round-trip success is "nothing *undocumented* disappeared," not "CAD b-reps came back."

### 4. Technical explanation

Integration checklist (pin this next to Obj 7.4):

| Step | Implementation |
|------|----------------|
| Open | `Usd.Stage.Open(path, pathResolverContext=studio_ctx)` (Ch 33) |
| Edit target | Department layer, not session, not Flatten (Ch 15, Ch 32) |
| Export | extract → transform → write → **hooks** (Ch 34) → validate (Ch 30) → Save |
| Import | Read composed Usd; do not require every arc to become a native DCC node |
| Custom data | Preserve `custom` attributes and `customData` (Ch 29) |
| Units | Honor `metersPerUnit`, `upAxis`, `kilogramsPerUnit`; do not silently bake |
| Paths | Keep `./` pins; do not absolutize on Save (Ch 34 `ModifyAssetPaths`) |
| Notices | Optional live sync via `ObjectsChanged` (Ch 34) |

Round-trip **test** (automate in CI): write a tiny stage with a payload, a reference, a custom attribute, a texture `asset`, and physics APIs → DCC import → DCC export → compare `ComputeAllDependencies` and attribute `Get()` values.

Obj 7.8 (write/extend an importer): the importer is the DCC-side reader that applies this checklist, not a second exporter.

### 5. Mental model

```text
  DCC memory  --export/hooks-->  published USD  --import-->  DCC memory
                     ^                         |
                     +----- same resolver, version, mapping doc -----+
```

### 6. Simple example

Maya export writes `/Chair` with `custom float studio:weight = 4`. Maya import must recreate that attribute, not drop unknown names. A round-trip test asserts `Get() == 4`.

### 7. USDA example

The file the DCC must round-trip without flattening:

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "Chair" (
    kind = "component"
    prepend payload = @./payload.usdc@
)
{
    custom float studio:weight = 4
}
```

If the DCC Save comes back with no payload and inlined mesh points, the round-trip failed even if the chair still *looks* right.

### 8. Python example

A stand-in for "DCC Save then Open": Export and reopen must keep the custom attribute and the payload arc.

```python
from pxr import Usd, UsdGeom, Sdf

payload = Usd.Stage.CreateNew("payload.usda")
UsdGeom.Cube.Define(payload, "/Chair")
payload.SetDefaultPrim(payload.GetPrimAtPath("/Chair"))
payload.Save()

stage = Usd.Stage.CreateNew("chair.usda")
prim = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
stage.SetDefaultPrim(prim)
prim.GetPayloads().AddPayload("./payload.usda")
prim.CreateAttribute(
    "studio:weight", Sdf.ValueTypeNames.Float, custom=True).Set(4.0)
stage.Save()

again = Usd.Stage.Open("chair.usda")
p = again.GetPrimAtPath("/Chair")
items = again.GetRootLayer().GetPrimAtPath("/Chair").payloadList.prependedItems
print("weight", p.GetAttribute("studio:weight").Get())
print("payloads", [str(i.assetPath) for i in items])
print("HasAuthoredPayloads", p.HasAuthoredPayloads())
print("composed type", p.GetTypeName())
```

**Expected output**

```text
weight 4.0
payloads ['./payload.usda']
HasAuthoredPayloads True
composed type Xform
```

Local `Xform` is stronger than the payload's `Cube` type (LIVERPS), so the composed type stays `Xform`. The test that must not regress: **weight** and the **payload arc** survive a reopen. If a DCC Flattened, `HasAuthoredPayloads` would be False and `payloads` would be empty.

### 9. Real-world use case

A CAD round-trip: CAD → USD (tessellated mesh + `studio:cadId`) → CAD importer looks up `studio:cadId` and reattaches the parametric body. Without that custom attribute, CAD can only import a dumb mesh (Ch 29).

### 10. Common mistakes

> [!MISTAKE] Import that FlattenLayerStacks for "simplicity." You just deleted the pipeline.

> [!MISTAKE] Export from the DCC's current working file path using absolute Windows paths.

> [!MISTAKE] A different USD version in the DCC than on the farm (Section 35.2).

### 11. Exam traps

> [!TRAP] "Round-trip means the USDA text diffs empty." Binary crate, timestamp metadata, and `doc` comments will differ. Compare composed values and arcs.

> [!TRAP] Obj 7.8 is `Stage.Open`. An importer maps USD into **DCC nodes** (or a USD-native layer mode). Opening a stage is necessary but not sufficient.

### 12. Practice questions

**Q35.3-1.** A DCC Save of the chair example returns a layer with mesh `points` and no `payloads` metadata. What happened?
A. A correct payload load
B. The exporter Flattened (or inlined) instead of keeping the arc
C. `usd-core` cannot store payloads
D. `studio:weight` forced a flatten

**Q35.3-2.** Select two round-trip requirements.
A. Same resolver context on Open as the rest of the pipeline
B. Preserve custom attributes
C. Convert every reference into a sublayer
D. Drop `kind` so DCCs are free to rename prims

**Answers**

- **Q35.3-1: B.** Inlined geometry, lost arc.
- **Q35.3-2: A and B.**

### 13. Exam takeaways

> [!KEY]
> - Round-trip = mapping doc + hooks + same USD/resolver + tests on arcs and custom data.
> - Do not Flatten as a default Save.
> - Importer (Obj 7.8) maps USD into the DCC; it must not invent a second data model silently.
> - Compare composed values, not USDA bytes.

---

## 35.4 Physics and other domain schemas in pipelines

### 1. What is it?

**Domain schemas** beyond `UsdGeom` travel through the same pipeline: `UsdPhysics` (rigid bodies, collisions, scenes, mass), `UsdShade`, `UsdLux`, `UsdSkel`. A pipeline that only round-trips meshes will drop `apiSchemas = ["PhysicsRigidBodyAPI"]` and the simulation dies (Obj 7.4 applied to physics).

### 2. Why do we need it?

Games, robotics, and digital twins need mass and collision in the **same** asset the renderer uses. If export strips unknown APIs, you fork "render USD" and "physics USD" and they drift.

### 3. Beginner explanation

The chair's *look* is the mesh and material. The chair's *behavior* when you knock it is `RigidBodyAPI` + `CollisionAPI` + a `PhysicsScene` gravity. Both are USD prims/API schemas. The pipeline must Save both.

*Where the analogy breaks:* `UsdPhysics` does not run a solver. A DCC or engine reads the schemas and simulates. USD stores the **intent**.

### 4. Technical explanation

Verified on USD 26.08 (`usd-core` includes `UsdPhysics`):

| API | Role |
|-----|------|
| `UsdPhysics.RigidBodyAPI.Apply(prim)` | Marks a prim as a simulated body |
| `UsdPhysics.CollisionAPI.Apply(prim)` | Marks it as colliding |
| `UsdPhysics.MassAPI` | Mass / density |
| `UsdPhysics.Scene.Define(stage, path)` | Gravity and scene settings |
| `UsdPhysics.SetStageKilogramsPerUnit` | Mass analog of `metersPerUnit` |

Authored USDA uses `prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsCollisionAPI"]`. Exporters must **Apply** the API (same rule as `MaterialBindingAPI` in Ch 29). Listing the token by hand without Apply is fragile.

Defaults: `GetStageKilogramsPerUnit` returns **1.0** even when not authored; `StageHasAuthoredKilogramsPerUnit` tells you whether someone wrote it. Gravity on a new `PhysicsScene` starts unset-looking (`magnitude` was `-inf` until we authored it). **Always author gravity** if you care.

Other domains follow the same pipeline rule: if the DCC has no native node, store a custom attribute or keep the USD API schema — do not delete it on import (Ch 29 nonstandard data).

### 5. Mental model

```text
  Cube "Box"
     apiSchemas: PhysicsRigidBodyAPI + PhysicsCollisionAPI
  PhysicsScene
     gravityDirection / gravityMagnitude
  stage metadata
     metersPerUnit + kilogramsPerUnit
```

### 6. Simple example

A robotics cell: each link is a mesh with `RigidBodyAPI` + `CollisionAPI`; `/PhysicsScene` has Earth gravity; `kilogramsPerUnit = 1`. The engine reads those APIs; usdview still draws the mesh.

### 7. USDA example

```usda
#usda 1.0
(
    kilogramsPerUnit = 1
)

def Cube "Box" (
    prepend apiSchemas = ["PhysicsRigidBodyAPI", "PhysicsCollisionAPI"]
)
{
}

def PhysicsScene "PhysicsScene"
{
    vector3f physics:gravityDirection = (0, -1, 0)
    float physics:gravityMagnitude = 10
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdPhysics

stage = Usd.Stage.CreateInMemory()
box = UsdGeom.Cube.Define(stage, "/Box")
UsdPhysics.RigidBodyAPI.Apply(box.GetPrim())
UsdPhysics.CollisionAPI.Apply(box.GetPrim())
print("has RB", box.GetPrim().HasAPI(UsdPhysics.RigidBodyAPI))
print("has Col", box.GetPrim().HasAPI(UsdPhysics.CollisionAPI))

print("kg authored?", UsdPhysics.StageHasAuthoredKilogramsPerUnit(stage))
UsdPhysics.SetStageKilogramsPerUnit(stage, 1)
print("kg", UsdPhysics.GetStageKilogramsPerUnit(stage),
      "authored?", UsdPhysics.StageHasAuthoredKilogramsPerUnit(stage))

scene = UsdPhysics.Scene.Define(stage, "/PhysicsScene")
scene.CreateGravityDirectionAttr().Set((0, -1, 0))
scene.CreateGravityMagnitudeAttr().Set(10)
print("g dir", tuple(scene.GetGravityDirectionAttr().Get()))
print("g mag", scene.GetGravityMagnitudeAttr().Get())
print("apiSchemas",
      list(box.GetPrim().GetAppliedSchemas()))
```

**Expected output**

```text
has RB True
has Col True
kg authored? False
kg 1.0 authored? True
g dir (0.0, -1.0, 0.0)
g mag 10.0
apiSchemas ['PhysicsRigidBodyAPI', 'PhysicsCollisionAPI']
```

### 9. Real-world use case

A digital twin of a conveyor: USD carries kinematics (`UsdPhysics` joints) and the factory mesh. The PLC simulator subscribes to joint schemas; the marketing render ignores them. One published `cell/v014` serves both because the exporter **Apply**'d the APIs instead of putting mass in a side-car JSON.

### 10. Common mistakes

> [!MISTAKE] Import that strips `apiSchemas` it does not understand. Physics vanishes; the mesh still looks fine.

> [!MISTAKE] Assuming `GetStageKilogramsPerUnit` going `1.0` means someone authored it. Check `StageHasAuthoredKilogramsPerUnit`.

> [!MISTAKE] Forgetting `PhysicsScene` gravity. Bodies may not fall; that is data, not a solver bug.

### 11. Exam traps

> [!TRAP] "`UsdPhysics` is not in usd-core." It **is**, on 26.08. `UsdImaging` is not.

> [!TRAP] "Apply is optional if USDA lists `apiSchemas`." Use `Apply` in Python; validators and `HasAPI` expect the schema applied (same story as materials).

> [!TRAP] Mass uses `metersPerUnit`. Mass uses **`kilogramsPerUnit`**.

### 12. Practice questions

**Q35.4-1.** Which call marks a cube as a simulated body?
A. `UsdPhysics.RigidBodyAPI.Apply(prim)`
B. `kind = "component"`
C. `UsdGeom.Cube.Define` alone
D. `SetStageKilogramsPerUnit`

**Q35.4-2.** Select two pipeline rules for physics USD.
A. Round-trip must keep `apiSchemas`
B. Author `PhysicsScene` gravity if you need a world
C. Physics requires `UsdImaging`
D. `kilogramsPerUnit` is an alias of `metersPerUnit`

**Answers**

- **Q35.4-1: A.** Apply the API schema.
- **Q35.4-2: A and B.** Imaging is render; kg and meters are different metadata.

### 13. Exam takeaways

> [!KEY]
> - `UsdPhysics` ships in 26.08 `usd-core`; Apply `RigidBodyAPI` / `CollisionAPI`.
> - `kilogramsPerUnit` is authored separately from meters; fallback get is `1.0`.
> - Author gravity on `PhysicsScene`.
> - Domain schemas are first-class pipeline data, not optional extras to strip.

---

## Chapter lab(s)

No dedicated lab number beyond **Lab 37** (capstone pipeline) and **Lab 25/29** (exporter/importer). When you write those labs, include a `UsdPhysics` Apply and a round-trip assert on `studio:weight` plus payloads.

## USDA reading exercises

**Exercise 35-A.** A DCC plugin was compiled with USD 25.11 headers. usdview reports `GetVersion() == (0, 26, 8)`. The plugin's types do not appear in `GetAllPlugins()`. Why?

**Exercise 35-B.** `GetStageKilogramsPerUnit(stage)` prints `1.0` on a brand-new stage. Did someone author mass units?

**Answers**

- **35-A.** ABI / version mismatch (Obj 3.1). Rebuild the plugin against 26.08 and load it from that prefix's `PXR_PLUGINPATH_NAME`.
- **35-B.** No. Fallback is 1.0. Ask `StageHasAuthoredKilogramsPerUnit`.

## Chapter review

**Summary**

- Build USD with `build_usd.py` / CMake when you need imaging, MaterialX, tools, or custom deps (Obj 3.2).
- `GetVersion()` is `(0, 26, 8)` here — not major 26.
- Plugins match that ABI; one libusd per process (Obj 3.1).
- DCC round-trip: same resolver, hooks, custom data, no surprise Flatten (Obj 7.4 / 7.8).
- `UsdPhysics` APIs and `kilogramsPerUnit` travel with the asset.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| `GetMajorVersion() == 0` | Normal for 26.08 |
| `UsdImaging` import fails | `usd-core` wheel |
| Plugin types missing | Version / `PXR_PLUGINPATH_NAME` |
| Save inlined a payload | Flattened round-trip |
| Physics missing after DCC | `apiSchemas` stripped |
| `kg == 1.0` | Could be fallback |

**Review questions**

**R35-1** (Obj 3.2) `build_usd.py` is:
A. A pip wrapper for `usd-core`
B. The OpenUSD source-build entry that drives CMake
C. A Hydra delegate
D. A USDZ packer

**R35-2** (Obj 3.1) Select two requirements for a C++ resolver plugin.
A. Built against the host USD version
B. Discoverable via `plugInfo.json` / `PXR_PLUGINPATH_NAME`
C. Listed in `defaultPrim`
D. Flattened into every shot

**R35-3** (Obj 7.4) A round-trip test should fail if:
A. USDA whitespace changed
B. `payloads` prepend disappeared and meshes were inlined
C. Crate vs USDA encoding changed by policy
D. `doc` metadata was added by Flatten

**R35-4** (Obj 7.8) An importer's job is:
A. Only `Stage.Open`
B. Map USD into the DCC (or keep USD-native layers) without silent loss
C. Always FlattenLayerStack first
D. Delete unknown API schemas

**R35-5** (Obj 3.1) `Usd.GetVersion()` in this venv:
A. `(0, 26, 8)`
B. `(26, 8, 0)`
C. `(26, 0, 8)`
D. `(8, 26, 0)`

**R35-6** (Obj 7.4) Select two physics round-trip must-keeps.
A. `PhysicsRigidBodyAPI` on the body
B. Authored `PhysicsScene` gravity
C. `UsdImaging` plugin
D. `GetMaster()`

**R35-7** (Obj 3.2) `usd-core` 26.8 includes:
A. `UsdPhysics` and `UsdShade`, not `UsdImaging`
B. `usdview`
C. `usdGenSchema`
D. MaterialX `UsdMtlx`

**R35-8** (Obj 7.4) `StageHasAuthoredKilogramsPerUnit` is False and `GetStageKilogramsPerUnit` is 1.0. Meaning?
A. Someone authored 1.0
B. Fallback; mass units were not authored
C. Physics is disabled
D. `metersPerUnit` is 1.0

**R35-9** (Obj 7.8) Select two exporter/importer integration rules.
A. Open with the studio `pathResolverContext`
B. Run pipeline hooks before Save
C. Use the session layer as the published file
D. Absolutize all asset paths for portability

**R35-10** (Obj 3.1) `Plug.Registry().GetAllPlugins()` missing `usdPhysics` on a full USD build usually means:
A. The cube has no extent
B. Plugin search path / build omitted physics
C. `kind` is wrong
D. LIVERPS failed

**R35-11** (Obj 7.4) `RigidBodyAPI.Apply` authors:
A. `prepend apiSchemas = ["PhysicsRigidBodyAPI"]`
B. A new sublayer
C. A Hydra material
D. `defaultPrim`

**R35-12** (Obj 3.2) "Build USD with custom dependencies" means:
A. Edit USDA `subLayers`
B. Point CMake at your TBB/Python/OpenSubdiv instead of random copies
C. `pip install numpy`
D. `CreateNewUsdzPackage`

**Review answers**

- **R35-1: B.** Review: §35.1.
- **R35-2: A and B.** Review: §35.2.
- **R35-3: B.** Bytes and comments are allowed to change. Review: §35.3.
- **R35-4: B.** Review: §35.3.
- **R35-5: A.** Review: §35.1.
- **R35-6: A and B.** Review: §35.4.
- **R35-7: A.** Review: §35.1.
- **R35-8: B.** Review: §35.4.
- **R35-9: A and B.** Review: §35.3.
- **R35-10: B.** Review: §35.2.
- **R35-11: A.** Review: §35.4.
- **R35-12: B.** Review: §35.1.

## Further reading

- [S03] OpenUSD — Building USD (`build_usd.py`, CMake). https://openusd.org/release/dl_build.html
- [S06] OpenUSD API — `UsdPhysics`, `Usd.GetVersion`. https://openusd.org/release/api/usd_physics_page_front.html
- [S16] NVIDIA Learn OpenUSD — data exchange / DCC workflows. https://docs.nvidia.com/learn-openusd/latest/index.html
- Chapter 36 continues plugins (`plugInfo.json`). Chapter 37 covers `usdGenSchema` (not in `usd-core`).
