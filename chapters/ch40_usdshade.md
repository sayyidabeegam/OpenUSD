# Chapter 40 — UsdShade: Materials and Shaders

> **Exam domain:** Visualization (8%) · **Objectives:** 8.2, 8.3, 8.4 · **Study day:** 11 · **Est. time:** 110 min
> **Prerequisites:** Ch 5 (properties), Ch 6 (schemas / API schemas), Ch 11 (primvars), Ch 29 (exporter PreviewSurface sketch), Ch 39 (meshes, GeomSubset)

A mesh without a material is a grey shape. **UsdShade** is the schema domain that describes *what it looks like*: a **Material** prim, the **Shader** nodes inside it, the connections between their inputs and outputs, and the **binding** that assigns that material to geometry. This chapter is the whole Visualization domain's material half: assign PreviewSurface (Obj 8.2), bind it to a mesh (Obj 8.3), and drive diffuse color from a primvar (Obj 8.4).

Chapter 29 showed a one-shader bind as part of an exporter. Here you learn the network, the purposes, the strength, and the public knobs you expose for downstream overrides.

## Learning goals

- Author a `Material` with nested `Shader` and `NodeGraph` prims, and explain why a Material *is* a NodeGraph.
- Connect shader outputs to inputs, including the Material's `outputs:surface` terminal.
- Build a `UsdPreviewSurface` shader with the inputs Hydra preview renderers understand.
- Wire `UsdUVTexture` and `UsdPrimvarReader_float2` so a texture follows mesh UVs.
- Build the Obj 8.4 network: `UsdPrimvarReader_float3` reading `displayColor` into `diffuseColor`.
- Apply `MaterialBindingAPI`, bind with purpose and strength, and resolve the bound material.
- Expose Material interface inputs so a shot layer can recolor an asset without editing the shader graph.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Material** | A `UsdShade.Material` prim: the container you bind to geometry. |
| **Shader** | A `UsdShade.Shader` prim: one node in the graph, identified by `info:id`. |
| **NodeGraph** | A container for connected shaders; Material derives from it. |
| **`info:id`** | Uniform token on a Shader naming the implementation (`UsdPreviewSurface`, `UsdUVTexture`, …). |
| **Connectable** | A prim whose inputs and outputs can be wired (`ConnectableAPI`). |
| **Connection** | An attribute with `.connect` targeting another input or output. |
| **UsdPreviewSurface** | The standard interchange shader id for preview / lookdev. |
| **Binding** | The relationship from geometry to a Material (`material:binding`). |
| **`MaterialBindingAPI`** | Applied API schema that makes a prim a legal binding target. |
| **Purpose** | Which binding to use: all-purpose `''`, `preview`, or `full`. |
| **`bindMaterialAs`** | Strength metadata: `strongerThanDescendants` or `weakerThanDescendants`. |
| **Interface input** | A Material-level input that shaders connect *to*, so shots can override one knob. |

---

## 40.1 `Material`, `Shader`, `NodeGraph`

### 1. What is it?
**UsdShade** describes shading as a small scene graph of its own. A **Material** is the named look you bind to geometry. A **Shader** is one node in that look (a preview surface, a texture, a primvar reader). A **NodeGraph** groups nodes. A Material *is* a NodeGraph, so it can own inputs, outputs, and child shaders.

### 2. Why do we need it?
Geometry (Chapter 39) answers "where is the surface?" Shading answers "how does it respond to light?" Without a Material, every DCC invents its own look encoding and interchange dies. UsdShade is the shared encoding.

### 3. Beginner explanation
Think of a recipe card in a binder. The **Material** is the card you pull ("Wood"). The **Shader** nodes are the steps on the card ("mix brown paint", "read the grain photo"). A **NodeGraph** is a sub-recipe you reuse ("make wood grain") that is not itself the card you hand the cook.

*Where the analogy breaks:* the Material card *is* also a sub-recipe (it *is* a NodeGraph). You do not keep a separate empty binder for the card.

### 4. Technical explanation
- Concrete typed schemas: `UsdShade.Material`, `UsdShade.Shader`, `UsdShade.NodeGraph`. Define with `UsdShade.Material.Define(stage, path)` (same pattern as `UsdGeom.Mesh.Define`).
- **Material IsA NodeGraph is True.** Shader is *not* a NodeGraph. NodeGraph is *not* a Material. Verified on USD 26.08.
- A Shader's implementation is **not** its prim type. The prim type is always `Shader`. The implementation is the uniform token **`info:id`**, set with `shader.CreateIdAttr("UsdPreviewSurface")`.
- Conventional layout: `/Looks/<MaterialName>/<ShaderName>`. `/Looks` is often a `Scope` (no transform). The Material is what you bind; the shaders stay *inside* it so the look ships as one prim tree.
- Shaders and materials are connectable (`UsdShade.ConnectableAPI`). That is how §40.2 wires them.
- **MaterialX** (`UsdMtlx`) is a separate plugin. `usd-core` 26.8 does not ship it. The exam's interchange shader is PreviewSurface, not MaterialX.

> [!VERSION] Verified on USD 26.08 (`usd-core` 26.8). `UsdMtlx` is absent. Do not write `from pxr import UsdMtlx` in runnable examples.

### 5. Mental model

```text
Scope "Looks"
 └── Material "Wood"          <- this is what you BIND (also a NodeGraph)
      ├── Shader "Preview"    info:id = UsdPreviewSurface
      ├── Shader "DiffuseTex" info:id = UsdUVTexture
      └── NodeGraph "Utility"  <- nested graph, not bindable by itself
```

Bind **Wood**, never the Preview shader.

### 6. Simple example
Three prims: `/Looks/Wood` (Material), `/Looks/Wood/Preview` (Shader), `/Looks/Wood/Utility` (NodeGraph). Types: Material, Shader, NodeGraph. Wood IsA NodeGraph.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Looks"
)

def Scope "Looks"
{
    def Material "Wood"
    {
        def Shader "Preview"
        {
            uniform token info:id = "UsdPreviewSurface"
        }

        def NodeGraph "Utility"
        {
        }
    }
}
```

- `def Material "Wood"` is the bind target.
- `info:id` lives on the **Shader**, not on the Material.
- `Utility` is a nested graph; nothing binds to it.

### 8. Python example

```python
from pxr import Usd, UsdShade

stage = Usd.Stage.CreateInMemory()
mat = UsdShade.Material.Define(stage, "/Looks/Wood")
shader = UsdShade.Shader.Define(stage, "/Looks/Wood/Preview")
graph = UsdShade.NodeGraph.Define(stage, "/Looks/Wood/Utility")

print("Material type:", mat.GetPrim().GetTypeName())
print("Shader type:", shader.GetPrim().GetTypeName())
print("NodeGraph type:", graph.GetPrim().GetTypeName())
print("Material IsA NodeGraph:", mat.GetPrim().IsA(UsdShade.NodeGraph))
print("Shader IsA NodeGraph:", shader.GetPrim().IsA(UsdShade.NodeGraph))
print("NodeGraph IsA Material:", graph.GetPrim().IsA(UsdShade.Material))
```

**Expected output**
```text
Material type: Material
Shader type: Shader
NodeGraph type: NodeGraph
Material IsA NodeGraph: True
Shader IsA NodeGraph: False
NodeGraph IsA Material: False
```

The IsA line is the fact to memorize: Material is a NodeGraph; the reverse is false.

### 9. Real-world use case
A furniture catalog publishes each wood species as `/Looks/Oak`, `/Looks/Walnut`, each a Material with a PreviewSurface child. A set-dressing USD references the catalog and binds `/Looks/Oak` onto table meshes. Artists never bind the Preview shader; if they did, a later extra texture node inside the Material would be skipped.

### 10. Common mistakes
> [!MISTAKE] Putting `info:id = "UsdPreviewSurface"` on the Material prim. Hydra looks for a *Shader* with that id, connected to `outputs:surface`. Fix: author a child Shader.

> [!MISTAKE] Binding `/Looks/Wood/Preview` instead of `/Looks/Wood`. The relationship can point at a Shader, but binding APIs and validators expect a **Material**.

> [!MISTAKE] Treating NodeGraph as a Material. `IsA(UsdShade.Material)` on a NodeGraph is False; you cannot bind it as a look.

### 11. Exam traps
> [!TRAP] "`UsdPreviewSurface` is a prim type." It is an `info:id` **value**. The prim type is `Shader`.

> [!TRAP] "A Material is not connectable; only Shaders are." Material IsA NodeGraph, so it has inputs and outputs. That is how §40.2 and §40.7 work.

> [!TRAP] Questions that offer `UsdMtlx` as the only way to preview. PreviewSurface is the required interchange path; MaterialX is optional and missing from `usd-core`.

### 12. Practice questions
1. A USDA file has `def Material "Paint" { uniform token info:id = "UsdPreviewSurface" }` and no Shader child. What is wrong?
2. `mat.GetPrim().IsA(UsdShade.NodeGraph)` for a Material. What does it print?
3. What prim type do you `Define` for a UsdUVTexture node?

**Answers**
1. `info:id` belongs on a **Shader** child. The Material is the container; without a connected Shader, there is no surface implementation.
2. **True.** Material derives from NodeGraph.
3. **Shader** (`UsdShade.Shader.Define`), with `CreateIdAttr("UsdUVTexture")`. There is no `UsdUVTexture` prim type.

### 13. Exam takeaways
> [!KEY]
> - Bind a **Material**. Put **Shader** children inside it. `info:id` names the shader implementation.
> - Material IsA NodeGraph (True); Shader IsA NodeGraph (False).
> - `UsdPreviewSurface` is an id string, not a schema type.
> - `usd-core` has no UsdMtlx; PreviewSurface is the runnable interchange shader.

---

## 40.2 Inputs, outputs, connections

### 1. What is it?
A shader node has **inputs** (values it consumes) and **outputs** (values it produces). A **connection** wires one output (or a NodeGraph/Material interface input) to another input. USDA writes this as `inputs:foo.connect = </Path.outputs:bar>`.

### 2. Why do we need it?
A PreviewSurface that always uses a constant brown cannot show a wood photo or a per-face paint color. Connections are how you build a **network**: reader → texture → surface, and surface → the Material terminal that Hydra actually draws.

### 3. Beginner explanation
Think of patch cables on a small analog synth. Each module has jacks in (inputs) and jacks out (outputs). A cable from Texture's `rgb` into Preview's `diffuseColor` is a connection. The Material's `outputs:surface` is the speaker output: if that cable is unplugged, you hear (see) nothing.

*Where the analogy breaks:* USD will let you author a constant *and* a cable on the same input. The cable wins for shading; the constant remains in the file (see the Python example).

### 4. Technical explanation
- Create with `shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)` and `shader.CreateOutput("surface", Sdf.ValueTypeNames.Token)`. Property names in USDA are `inputs:diffuseColor` and `outputs:surface`.
- Connect: `dest.ConnectToSource(sourceOutput)` or `dest.ConnectToSource(connectableAPI, "surface")`. Query: `HasConnectedSource()`, `GetConnectedSources()` → `(list of ConnectionSourceInfo, invalidPaths)`.
- The Material terminal Hydra preview uses is **`outputs:surface`**, created with `material.CreateSurfaceOutput()`. Also: `CreateDisplacementOutput()` → `outputs:displacement`, `CreateVolumeOutput()` → `outputs:volume`. A render-context suffix is allowed: `CreateSurfaceOutput("ri")` → `outputs:ri:surface`.
- `material.ComputeSurfaceSource()` returns `(shader, outputName, attributeType)` for the connected surface shader. Unpacking is required; it is a tuple, not a Shader.
- A connected input can still hold an authored **value**. `Get()` returns the value; `HasConnectedSource()` is True. Renderers follow the connection.
- Connections compose like other attributes: a stronger layer can reconnect or disconnect.

### 5. Mental model

```text
Material.outputs:surface  <── connect ──  Shader.outputs:surface
                                              │
                              inputs:diffuseColor  (value and/or connect)
```

If `outputs:surface` on the Material is not connected, the look has no surface terminal.

### 6. Simple example
Shader Preview has `inputs:diffuseColor = (0.6, 0.4, 0.2)` and `outputs:surface`. Material Wood connects its `outputs:surface` to Preview's `outputs:surface`. ComputeSurfaceSource → `/Looks/Wood/Preview`.

### 7. USDA example

```usda
#usda 1.0

def Material "Wood"
{
    token outputs:surface.connect = </Wood/Preview.outputs:surface>

    def Shader "Preview"
    {
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor = (0.6, 0.4, 0.2)
        token outputs:surface
    }
}
```

- `.connect` is authored on the **destination**.
- The target path is prim + `.outputs:surface` (or `.inputs:name` for interface inputs in §40.7).
- `outputs:surface` on the Shader can be declared with no value; the connection only needs the name to exist.

### 8. Python example

```python
from pxr import Usd, UsdShade, Sdf

stage = Usd.Stage.CreateInMemory()
mat = UsdShade.Material.Define(stage, "/Looks/Wood")
ps = UsdShade.Shader.Define(stage, "/Looks/Wood/Preview")
ps.CreateIdAttr("UsdPreviewSurface")
diff = ps.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
diff.Set((0.6, 0.4, 0.2))
surf = ps.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat_out = mat.CreateSurfaceOutput()
mat_out.ConnectToSource(surf)

print("shader id:", ps.GetIdAttr().Get())
print("has connect:", mat_out.HasConnectedSource())
shader, name, _ = mat.ComputeSurfaceSource()
print("surface source:", shader.GetPath(), name)
cs, invalid = mat_out.GetConnectedSources()
print("connected count:", len(cs), "invalid:", invalid)
for line in stage.GetRootLayer().ExportToString().splitlines():
    if "connect" in line or "diffuseColor" in line:
        print(line.strip())
r = UsdShade.Shader.Define(stage, "/Looks/Wood/Reader")
r.CreateOutput("result", Sdf.ValueTypeNames.Float3)
diff.ConnectToSource(r.GetOutput("result"))
print("after connect Get():", diff.Get())
print("HasConnectedSource:", diff.HasConnectedSource())
```

**Expected output**
```text
shader id: UsdPreviewSurface
has connect: True
surface source: /Looks/Wood/Preview surface
connected count: 1 invalid: []
token outputs:surface.connect = </Looks/Wood/Preview.outputs:surface>
color3f inputs:diffuseColor = (0.6, 0.4, 0.2)
after connect Get(): (0.6, 0.4, 0.2)
HasConnectedSource: True
```

After the extra connect, USDA would also show `inputs:diffuseColor.connect`. `Get()` still returns the leftover `(0.6, 0.4, 0.2)`.

### 9. Real-world use case
A lookdev artist in usdview (or any Hydra viewport) sees brown wood because `outputs:surface` is connected. A lighting TD then reconnects `diffuseColor` to a texture in a stronger shot layer without replacing the Material prim: composition edits the `.connect` target (Chapter 15 edit targets).

### 10. Common mistakes
> [!MISTAKE] Calling `ComputeSurfaceSource()` and treating the return as a Shader. It is a **tuple** `(shader, name, type)`. Unpacking, then `shader.GetPath()`.

> [!MISTAKE] Connecting the Shader *to* the Material terminal but never creating `outputs:surface` on the Shader. `ConnectToSource` needs a real output.

> [!MISTAKE] Reading `Get()` on a connected input and assuming there is no connection. Leftover values are common after a DCC connect.

### 11. Exam traps
> [!TRAP] USDA shows both `inputs:diffuseColor = (1, 0, 0)` *and* `.connect`. The connection is what the renderer uses; the value is leftover.

> [!TRAP] "Connect the Material's surface output to the *input* of the Shader." The Material terminal connects to the Shader's **output** `surface`.

> [!TRAP] `outputs:ri:surface` is a RenderMan-context terminal. `CreateSurfaceOutput()` with no argument is the universal `outputs:surface` that PreviewSurface uses.

### 12. Practice questions
1. In USDA, which attribute carries the cable: the source or the destination?
2. `ComputeSurfaceSource()` returns what kind of object?
3. A shader input has an authored value and a `.connect`. Which drives shading?

**Answers**
1. The **destination** (`inputs:foo.connect` or `outputs:surface.connect` on the Material).
2. A **tuple** `(UsdShade.Shader, outputName, AttributeType)`, not a single Shader.
3. The **connection**. `Get()` may still return the leftover value.

### 13. Exam takeaways
> [!KEY]
> - Inputs are `inputs:<name>`, outputs `outputs:<name>`; `.connect` is authored on the destination.
> - Material `outputs:surface` must connect to a Shader `outputs:surface`.
> - `ComputeSurfaceSource()` → unpack a tuple.
> - Authored value + connect can coexist; the connect wins for shading.

---

## 40.3 `UsdPreviewSurface`

### 1. What is it?
**UsdPreviewSurface** is the standard, DCC-neutral shader implementation for preview and interchange. You author it as a Shader whose `info:id` is the string `"UsdPreviewSurface"`, then set physically based inputs such as `diffuseColor`, `metallic`, `roughness`, and `opacity`.

### 2. Why do we need it?
Maya's Standard Surface, Blender's Principled BSDF, and glTF's pbrMetallicRoughness all describe "a painted surface," but their node graphs do not travel. PreviewSurface is the common dialect so usdview, Storm, and other Hydra delegates can draw *something correct enough* everywhere. Obj 8.2 is exactly this: assign PreviewSurface materials for asset visualization.

### 3. Beginner explanation
Think of a restaurant's "house salad" that every location must be able to make from a short ingredient list. PreviewSurface is that house salad: not every garnish from the Michelin kitchen, but lettuce, dressing, salt — `diffuseColor`, `roughness`, `metallic`, `opacity` — so any cook (renderer) can plate it.

*Where the analogy breaks:* production renderers (RenderMan, Arnold, MaterialX graphs) often live *beside* PreviewSurface, connected to `outputs:full` or a render-context terminal. Preview is the interchange plate, not the à-la-carte menu.

### 4. Technical explanation
- Author: `UsdShade.Shader.Define` → `CreateIdAttr("UsdPreviewSurface")` → `CreateInput` / `CreateOutput("surface", Token)` → connect to the Material's `CreateSurfaceOutput()`.
- Common inputs (types you will author in this book):
  - `diffuseColor` — `color3f` (the "paint" color; Obj 8.4 often replaces this with a connection)
  - `emissiveColor` — `color3f`
  - `metallic` — `float` (0 dielectric, 1 metal)
  - `roughness` — `float` (0 mirror, 1 chalk)
  - `opacity` — `float` (1 opaque)
  - `opacityThreshold` — `float` (cutout)
  - `ior` — `float`
  - `normal` — `normal3f` (usually connected to a texture's rgb)
  - `displacement` — `float`
  - `occlusion` — `float`
  - `useSpecularWorkflow` — `int` (0 = metallic workflow, 1 = specular)
- Outputs used in preview: `surface` (token). Displacement/volume terminals exist on the Material for other networks.
- PreviewSurface does **not** read mesh primvars by itself. To use UVs or `displayColor` you insert reader/texture shaders (§40.4, §40.5).
- Hydra Storm / usdview consume this network. `usd-core` has no Hydra; you author and inspect the graph in Python, you do not rasterize it here.

> [!NOTE] glTF's metallic-roughness maps onto PreviewSurface (`metallic`, `roughness`, `diffuseColor` ← baseColor). That mapping is why exporters in Chapter 29 wrote this shader.

### 5. Mental model

```text
Material
 └── Shader info:id = "UsdPreviewSurface"
      inputs:  diffuseColor, metallic, roughness, opacity, ...
      outputs: surface  ──connect──►  Material.outputs:surface
```

If `info:id` is missing or misspelled, the renderer has no implementation to run.

### 6. Simple example
A red plastic: `diffuseColor (0.8, 0.1, 0.1)`, `metallic 0`, `roughness 0.5`, `opacity 1`. That is enough for Obj 8.2 visualization.

### 7. USDA example

```usda
#usda 1.0

def Material "Paint"
{
    token outputs:surface.connect = </Paint/Preview.outputs:surface>

    def Shader "Preview"
    {
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor = (0.8, 0.1, 0.1)
        float inputs:metallic = 0
        float inputs:roughness = 0.5
        float inputs:opacity = 1
        token outputs:surface
    }
}
```

- Four inputs plus `info:id` and the surface terminal: a complete preview look.
- `metallic = 0` and `opacity = 1` are often left unauthored (fallbacks exist in the spec); authoring them makes the intent obvious for exam reading.

### 8. Python example

```python
from pxr import Usd, UsdShade, Sdf

stage = Usd.Stage.CreateInMemory()
mat = UsdShade.Material.Define(stage, "/Looks/Paint")
sh = UsdShade.Shader.Define(stage, "/Looks/Paint/Preview")
sh.CreateIdAttr("UsdPreviewSurface")
sh.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
    (0.8, 0.1, 0.1))
sh.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
sh.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
sh.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(1.0)
sh.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat.CreateSurfaceOutput().ConnectToSource(
    sh.ConnectableAPI(), "surface")
print("id:", sh.GetIdAttr().Get())
for name in ("diffuseColor", "metallic", "roughness", "opacity"):
    i = sh.GetInput(name)
    print(name, i.GetTypeName(), i.Get())
```

**Expected output**
```text
id: UsdPreviewSurface
diffuseColor color3f (0.8, 0.1, 0.1)
metallic float 0.0
roughness float 0.5
opacity float 1.0
```

`ConnectToSource(sh.ConnectableAPI(), "surface")` is the overload that names the output as a string; §40.2 used the Output object. Both work.

### 9. Real-world use case
A CAD exporter (Chapter 29) cannot ship SolidWorks appearances. It writes one PreviewSurface per unique color/metal pair so Storm and usdview show the assembly in roughly the right colors during design review. The high-end Arnold network, if any, lives in a sibling render-context output the CAD tool never writes.

### 10. Common mistakes
> [!MISTAKE] Setting `info:id` to `"PreviewSurface"` or `"previewSurface"`. The id is exactly **`UsdPreviewSurface`**.

> [!MISTAKE] Filling `diffuseColor` and forgetting to connect `outputs:surface` to the Material. usdview shows default grey; the shader is an orphan.

> [!MISTAKE] Using `float3` for `diffuseColor`. The interchange type is **`color3f`**. Connections from a `float3` texture `rgb` still work in practice, but author the Preview input as `color3f`.

### 11. Exam traps
> [!TRAP] Options that put PreviewSurface inputs on the Material prim. Inputs on the Material are *interface* knobs (§40.7), not the shader implementation.

> [!TRAP] "Metallic workflow means you must omit `diffuseColor`." You still author `diffuseColor` (base color); `metallic` blends dielectric vs metal.

> [!TRAP] Obj 8.2 vs 8.4: assigning PreviewSurface with a constant `diffuseColor` satisfies 8.2. Reading color from a primvar is a *different* objective (8.4) and needs a reader node.

### 12. Practice questions
1. Which property identifies a Shader as PreviewSurface?
2. Name four PreviewSurface inputs you would set for a red plastic.
3. Does PreviewSurface automatically read `primvars:displayColor` from the mesh?

**Answers**
1. `uniform token info:id = "UsdPreviewSurface"` on the **Shader**.
2. `diffuseColor`, `metallic` (0), `roughness`, `opacity` (and the `surface` output).
3. **No.** You must connect a `UsdPrimvarReader_float3` (§40.5) or a texture (§40.4).

### 13. Exam takeaways
> [!KEY]
> - Obj 8.2 = Shader `info:id = UsdPreviewSurface` under a Material, surface output connected.
> - Core inputs: `diffuseColor`, `metallic`, `roughness`, `opacity`.
> - PreviewSurface does not magically see mesh primvars; wire readers/textures.
> - Exact id string: `UsdPreviewSurface`.

---

## 40.4 Textures: `UsdUVTexture`, `UsdPrimvarReader_float2`

### 1. What is it?
**UsdUVTexture** is a Shader that samples an image file. **UsdPrimvarReader_float2** is a Shader that reads a 2-float primvar (almost always **`st`**, the UV coordinates) from the bound geometry and feeds it to the texture's `st` input.

### 2. Why do we need it?
A constant `diffuseColor` paints the whole mesh one color. Real assets have wood grain, logos, and rust. Those live in image files, and the image must stick to the surface using UVs stored as a primvar (Chapter 11).

### 3. Beginner explanation
Think of wrapping patterned paper around a gift box. The **photo** is the texture file (`inputs:file`). The **crease pattern** telling you which part of the paper hits which face is the UV primvar `st`. The **reader** is the person looking up the crease pattern; the **UVTexture** is the person laying the photo down.

*Where the analogy breaks:* the reader does not copy the primvar into the Material. It samples it *on the geometry being shaded*, so one Material can wrap many meshes that each have their own `st`.

### 4. Technical explanation
- `UsdPrimvarReader_float2`: `CreateIdAttr("UsdPrimvarReader_float2")`. Input **`varname`** is a token naming the primvar **without** the `primvars:` prefix (`"st"`, not `"primvars:st"`). Output `result` is `float2`.
- `UsdUVTexture`: `CreateIdAttr("UsdUVTexture")`. Inputs: `file` (`asset`, e.g. `./wood.png`), `st` (`float2`, connected from the reader). Outputs: `rgb` (`float3`), plus `r`, `g`, `b`, `a`. Connect `rgb` to PreviewSurface `diffuseColor`.
- Other UVTexture inputs you will see in USDA: `wrapS` / `wrapT` (`repeat`, `clamp`, `mirror`), `fallback`, `scale`, `bias`.
- Asset paths follow Chapter 33: `./wood.png` is layer-relative when written as an asset-valued input. Naive `Ar.GetResolver().Resolve("./wood.png")` is still cwd; the composed stage uses the layer as anchor.
- `usd-core` will author the graph; it will not open the PNG. Missing files are an asset-resolution problem, not a UsdShade schema error.

> [!VERSION] Verified on USD 26.08. There is no Python class `UsdShade.UVTexture`; it is a Shader id, like PreviewSurface.

### 5. Mental model

```text
Mesh primvars:st  ──(at shade time)──►  PrimvarReader_float2
                                              outputs:result
                                                    │
                                                    ▼
File wood.png  ──►  UsdUVTexture.inputs:file     inputs:st
                         outputs:rgb  ──►  PreviewSurface.inputs:diffuseColor
                                                outputs:surface ──► Material
```

### 6. Simple example
`varname = "st"` → UVTexture `file = @./wood.png@` → `rgb` into `diffuseColor`. Three shaders, one Material.

### 7. USDA example

```usda
#usda 1.0

def Material "Wood"
{
    token outputs:surface.connect = </Wood/Preview.outputs:surface>

    def Shader "StReader"
    {
        uniform token info:id = "UsdPrimvarReader_float2"
        token inputs:varname = "st"
        float2 outputs:result
    }

    def Shader "DiffuseTex"
    {
        uniform token info:id = "UsdUVTexture"
        asset inputs:file = @./wood.png@
        float2 inputs:st.connect = </Wood/StReader.outputs:result>
        float3 outputs:rgb
    }

    def Shader "Preview"
    {
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor.connect = </Wood/DiffuseTex.outputs:rgb>
        token outputs:surface
    }
}
```

- Reader id is `UsdPrimvarReader_float2` (the `2` matches UV's two floats).
- `varname` is `"st"`, matching `primvars:st` on the mesh.
- Texture `file` uses asset syntax `@./wood.png@`.

### 8. Python example

```python
from pxr import Usd, UsdShade, Sdf

stage = Usd.Stage.CreateInMemory()
mat = UsdShade.Material.Define(stage, "/Looks/Wood")
reader = UsdShade.Shader.Define(stage, "/Looks/Wood/StReader")
reader.CreateIdAttr("UsdPrimvarReader_float2")
reader.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
reader.CreateOutput("result", Sdf.ValueTypeNames.Float2)

tex = UsdShade.Shader.Define(stage, "/Looks/Wood/DiffuseTex")
tex.CreateIdAttr("UsdUVTexture")
tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("./wood.png")
tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(
    reader.GetOutput("result"))
tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)

ps = UsdShade.Shader.Define(stage, "/Looks/Wood/Preview")
ps.CreateIdAttr("UsdPreviewSurface")
ps.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
    tex.GetOutput("rgb"))
ps.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat.CreateSurfaceOutput().ConnectToSource(ps.GetOutput("surface"))

print("reader id:", reader.GetIdAttr().Get())
print("tex id:", tex.GetIdAttr().Get())
print("st connected:", tex.GetInput("st").HasConnectedSource())
print("file:", tex.GetInput("file").Get())
for line in stage.GetRootLayer().ExportToString().splitlines():
    if any(k in line for k in ("varname", "file", "connect")):
        print(line.strip())
```

**Expected output**
```text
reader id: UsdPrimvarReader_float2
tex id: UsdUVTexture
st connected: True
file: @./wood.png@
token outputs:surface.connect = </Looks/Wood/Preview.outputs:surface>
token inputs:varname = "st"
asset inputs:file = @./wood.png@
float2 inputs:st.connect = </Looks/Wood/StReader.outputs:result>
color3f inputs:diffuseColor.connect = </Looks/Wood/DiffuseTex.outputs:rgb>
```

`Get()` on an asset input prints the USDA `@path@` form.

### 9. Real-world use case
A games exporter writes one 2K albedo PNG next to `wood.usda` and this three-node graph. The engine's USD importer either samples the same PreviewSurface in the editor or reads `inputs:file` to feed its own sampler. Variant sets (Chapter 18) can swap `file` between `wood_2k.png` and `wood_512.png` without rebuilding the graph.

### 10. Common mistakes
> [!MISTAKE] `varname = "primvars:st"`. The reader wants the primvar **name** `st`. The `primvars:` prefix is the attribute namespace on the mesh, not the varname.

> [!MISTAKE] Using `UsdPrimvarReader_float3` for UVs. UVs are two floats; the id must be `UsdPrimvarReader_float2`.

> [!MISTAKE] Connecting the texture `file` input to the reader. `file` is the image; `st` is the UV. Mix them up and the texture has no coordinates (or tries to open a path named after a float2).

### 11. Exam traps
> [!TRAP] USDA with `varname = "UVMap"` while the mesh authors `primvars:st`. The names must match.

> [!TRAP] "UsdUVTexture is a typed schema you `Apply`." It is a Shader **id**, like PreviewSurface.

> [!TRAP] A question that omits the reader and sets `inputs:st = (0, 0)` on the texture. That samples one texel for the whole mesh.

### 12. Practice questions
1. Which Shader id samples an image file?
2. What `varname` reads typical USD UVs?
3. Which texture output connects to PreviewSurface `diffuseColor`?

**Answers**
1. **`UsdUVTexture`.**
2. **`"st"`** (the primvar name; mesh attribute `primvars:st`).
3. **`outputs:rgb`.**

### 13. Exam takeaways
> [!KEY]
> - Texture network: `UsdPrimvarReader_float2` (`varname=st`) → `UsdUVTexture` (`file`, `st`) → Preview `diffuseColor`.
> - `varname` has no `primvars:` prefix.
> - Both nodes are Shaders with `info:id`; there is no UVTexture prim type.
> - `inputs:file` is an `asset` (`@./wood.png@`).

---

## 40.5 Reading diffuse color from a primvar

### 1. What is it?
Objective **8.4** asks you to create a UsdPreviewSurface network whose **diffuse color comes from a primvar** on the mesh — usually **`displayColor`**. The extra node is **`UsdPrimvarReader_float3`**: it reads three floats (a color) and connects to `inputs:diffuseColor`.

### 2. Why do we need it?
Point clouds, CAD faces, and debug visualizations often carry a color per point or per mesh already (`primvars:displayColor`, Chapter 11 / 39). Baking that into a constant on the shader would freeze the color. A reader keeps one Material and lets each mesh (or each vertex) supply its own color.

### 3. Beginner explanation
Think of a paint-by-numbers kit that already printed the numbers on the canvas. The Material is "use the printed number as the paint color." The reader is the instruction "look at the `displayColor` box on this mesh." Different canvases, same instruction card.

*Where the analogy breaks:* interpolation matters. A `constant` primvar paints the whole prim one color; `vertex` interpolates; `faceVarying` follows corners. The reader does not change interpolation — the primvar does (Chapter 11).

### 4. Technical explanation
- Mesh side: author `primvars:displayColor` as `color3f[]`. Helpers: `UsdGeom.Mesh.CreateDisplayColorPrimvar(interpolation)` or `UsdGeom.PrimvarsAPI(mesh).CreatePrimvar("displayColor", ...)`. The primvar **name** is `displayColor`.
- Shader side: Shader id **`UsdPrimvarReader_float3`** (three floats, not two). `inputs:varname = "displayColor"`. Output `result` (`float3`) connects to PreviewSurface `inputs:diffuseColor`.
- Then bind the Material to the mesh (§40.6). The reader samples the primvar **on the geometry being shaded**, so one Material can serve many colored meshes.
- `displayOpacity` is the usual companion (`float` / `UsdPrimvarReader_float` into `opacity`). Obj 8.4 names diffuse color specifically.
- This is **not** the texture path. If the exam stem says "reads diffuse color from a primvar," look for PrimvarReader_float3, not UsdUVTexture.

> [!EXAM TIP] Obj 8.4 is a named, testable network. Memorize: Mesh `primvars:displayColor` + Shader `UsdPrimvarReader_float3` + `varname = displayColor` + connect to Preview `diffuseColor` + bind.

### 5. Mental model

```text
Mesh
  primvars:displayColor = [(0.2, 0.5, 0.9)]
  rel material:binding → Material "FromPrimvar"
                              │
                   Shader ColorReader
                     id = UsdPrimvarReader_float3
                     varname = "displayColor"
                     result ──► Preview.diffuseColor
```

### 6. Simple example
One mesh, constant blue-ish displayColor, one Material, two shaders (reader + Preview), binding applied. ComputeBoundMaterial → that Material. Reader varname → `displayColor`.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def Mesh "Board" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {
        rel material:binding = </Looks/FromPrimvar>
        color3f[] primvars:displayColor = [(0.2, 0.5, 0.9)] (
            interpolation = "constant"
        )
    }
}

def Scope "Looks"
{
    def Material "FromPrimvar"
    {
        token outputs:surface.connect = </Looks/FromPrimvar/Preview.outputs:surface>

        def Shader "ColorReader"
        {
            uniform token info:id = "UsdPrimvarReader_float3"
            token inputs:varname = "displayColor"
            float3 outputs:result
        }

        def Shader "Preview"
        {
            uniform token info:id = "UsdPreviewSurface"
            color3f inputs:diffuseColor.connect = </Looks/FromPrimvar/ColorReader.outputs:result>
            token outputs:surface
        }
    }
}
```

- `varname` matches the primvar name, not `primvars:displayColor`.
- Binding and the applied API schema are on the **mesh** (§40.6).

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Vt

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/World/Board")
UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
    "displayColor", Sdf.ValueTypeNames.Color3fArray,
    UsdGeom.Tokens.constant
).Set(Vt.Vec3fArray([Gf.Vec3f(0.2, 0.5, 0.9)]))

mat = UsdShade.Material.Define(stage, "/Looks/FromPrimvar")
reader = UsdShade.Shader.Define(stage, "/Looks/FromPrimvar/ColorReader")
reader.CreateIdAttr("UsdPrimvarReader_float3")
reader.CreateInput("varname", Sdf.ValueTypeNames.Token).Set(
    "displayColor")
reader.CreateOutput("result", Sdf.ValueTypeNames.Float3)
ps = UsdShade.Shader.Define(stage, "/Looks/FromPrimvar/Preview")
ps.CreateIdAttr("UsdPreviewSurface")
ps.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
    reader.GetOutput("result"))
ps.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat.CreateSurfaceOutput().ConnectToSource(ps.GetOutput("surface"))
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
bound = UsdShade.MaterialBindingAPI(mesh.GetPrim()).ComputeBoundMaterial()[0]
print("reader id:", reader.GetIdAttr().Get())
print("varname:", reader.GetInput("varname").Get())
print("diffuse connected:", ps.GetInput("diffuseColor").HasConnectedSource())
print("bound:", bound.GetPath())
print("primvar:", UsdGeom.PrimvarsAPI(mesh).GetPrimvar("displayColor").Get())
```

**Expected output**
```text
reader id: UsdPrimvarReader_float3
varname: displayColor
diffuse connected: True
bound: /Looks/FromPrimvar
primvar: [(0.2, 0.5, 0.9)]
```

This block is the Obj 8.4 recipe in runnable form.

### 9. Real-world use case
A digital-twin importer colors each machine by status: running = green, fault = red, stored on the mesh as `displayColor` and updated every tick. One Material (`FromPrimvar`) is bound to every machine. Changing a primvar is cheaper than swapping materials, and usdview's default purpose still shows the colors.

### 10. Common mistakes
> [!MISTAKE] Using `UsdPrimvarReader_float2` for color. Color is three floats; UVs are two. Wrong id → wrong output type → failed connection.

> [!MISTAKE] `varname = "primvars:displayColor"`. Same trap as UVs: drop the namespace.

> [!MISTAKE] Setting Preview `diffuseColor` to a constant *and* forgetting the reader. That is Obj 8.2, not 8.4. The exam stem's "from a primvar" is the tell.

### 11. Exam traps
> [!TRAP] A mesh with `displayColor` authored as a **non-primvar** attribute `color3f displayColor`. Readers look up **primvars**. Use `primvars:displayColor` / `CreateDisplayColorPrimvar`.

> [!TRAP] Binding the ColorReader Shader instead of the Material.

> [!TRAP] Connecting the reader to `emissiveColor` and leaving `diffuseColor` black. Obj 8.4 says **diffuse**.

### 12. Practice questions
1. Which `info:id` reads a color primvar into PreviewSurface?
2. What exact `varname` matches `primvars:displayColor`?
3. Select two. What else must exist for Obj 8.4 to visualize?
   A. Material `outputs:surface` connected to Preview
   B. `MaterialBindingAPI.Apply` + `Bind` on the mesh
   C. `UsdUVTexture`
   D. `info:id` on the Material

**Answers**
1. **`UsdPrimvarReader_float3`.**
2. **`displayColor`.**
3. **A and B.** A texture is a different network; `info:id` is never on the Material.

### 13. Exam takeaways
> [!KEY]
> - Obj 8.4 = `UsdPrimvarReader_float3` + `varname=displayColor` → Preview `diffuseColor`.
> - Mesh authors `primvars:displayColor`; varname omits `primvars:`.
> - float3 = color, float2 = UVs. Do not swap the ids.
> - Still bind a Material (next section); the reader is not the bind target.

---

## 40.6 Material binding (`MaterialBindingAPI`, strength, purpose, collections)

### 1. What is it?
**Binding** assigns a Material to geometry. The relationship is `rel material:binding`. The applied API schema **`MaterialBindingAPI`** is what makes that relationship legal. Bindings have **purpose** (`''` / `preview` / `full`) and **strength** (`strongerThanDescendants` / `weakerThanDescendants`). You can also bind via **collections** and **GeomSubsets**.

### 2. Why do we need it?
A Material sitting under `/Looks` does nothing until geometry points at it. Without a standard relationship, every DCC would invent `rel myApp:shader`. `material:binding` is the contract. Obj 8.3 is this contract.

### 3. Beginner explanation
Think of a gallery label stuck on a sculpture: "this piece uses the Wood look." The sculpture is the mesh; the label is `material:binding`; the look is the Material. A **purpose** is a different label for different lighting ("preview" for the lobby snapshot, "full" for the catalog shoot). **Strength** says whether a child's label beats the parent's.

*Where the analogy breaks:* you can stick a label that says "none" (`rel material:binding = None`) and still inherit a parent's label. Unbinding *this* prim is not unbinding the ancestor.

### 4. Technical explanation
- **Always** `UsdShade.MaterialBindingAPI.Apply(prim)` then `.Bind(material)`. Skipping `Apply` still writes `rel material:binding` and `Bind` returns True, but `HasAPI(MaterialBindingAPI)` stays False and validators fail.
> [!VERSION] Verified on USD 26.08. Since USD 22.11, validators expect `MaterialBindingAPI` applied. Always `Apply`.
- Direct bind USDA: `rel material:binding = </Looks/Wood>`. Purpose-specific: `rel material:binding:preview` and `rel material:binding:full`. `GetMaterialPurposes()` returns `['', 'preview', 'full']`. The empty string is **all-purpose** (`UsdShade.Tokens.allPurpose`).
- Resolve: `api.ComputeBoundMaterial()` → `(Material, Relationship)`. Pass `UsdShade.Tokens.preview` to resolve the preview purpose (falls back to all-purpose if no preview bind exists).
- **Strength.** Fallback (unauthored) is `strongerThanDescendants`: a parent's bind beats a child's. Pass `bindingStrength=UsdShade.Tokens.weakerThanDescendants` to let children win. Strength is metadata **`bindMaterialAs`** on the relationship, authored only when you set a non-default.
- **UnbindDirectBinding()** authors `rel material:binding = None` (empty targets). `ComputeBoundMaterial` then returns an invalid Material *if nothing else binds* (parent/collection). It does not remove the applied API schema.
- **Collections.** `api.Bind(collectionAPI, material)` writes `rel material:binding:collection:<name>` with **two targets**: the collection, then the Material. Include paths on the collection name the bound prims.
- **GeomSubsets.** `api.CreateMaterialBindSubset(name, Vt.IntArray([...]))` creates a child `GeomSubset` with `familyName = "materialBind"` and parent `subsetFamily:materialBind:familyType = "nonOverlapping"`. Bind the subset prim the same way: Apply + Bind. Family name must be `materialBind` (Chapter 39.5).
- Bindings inherit down the prim tree until a stronger descendant bind wins.

### 5. Mental model

```text
purpose:    all-purpose ('')   preview   full
            material:binding   :preview  :full

strength:   strongerThanDescendants  → parent beats child
            weakerThanDescendants    → child beats parent

collection bind rel targets:  [ <prim.collection:name> , <Material> ]
```

### 6. Simple example
Mesh `/World/Board/Top` Apply + Bind Wood. ComputeBoundMaterial → `/Looks/Wood`, rel name `material:binding`. Bind WoodPreview with purpose `preview` and weaker strength → rel `material:binding:preview`. Parent Board weaker-binds Wood, child Inlay binds Inlay → child wins; flip parent to stronger → parent Wood wins.

### 7. USDA example

```usda
#usda 1.0

def Xform "World" (
    prepend apiSchemas = ["MaterialBindingAPI", "CollectionAPI:woodbits"]
)
{
    prepend rel collection:woodbits:includes = </World/Board>
    rel material:binding:collection:woodbits = [
        </World.collection:woodbits>,
        </Looks/Wood>,
    ]

    def Mesh "Board" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {
        rel material:binding = </Looks/Wood>
        rel material:binding:preview = </Looks/WoodPreview> (
            bindMaterialAs = "weakerThanDescendants"
        )
    }
}

def Scope "Looks"
{
    def Material "Wood" {}
    def Material "WoodPreview" {}
}
```

- Direct bind has no `bindMaterialAs` → fallback stronger.
- Preview bind authors the metadata on the **relationship**.
- Collection rel has **two** targets, collection first.

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade, Vt

stage = Usd.Stage.CreateInMemory()
board = UsdGeom.Xform.Define(stage, "/World/Board")
top = UsdGeom.Mesh.Define(stage, "/World/Board/Top")
inlay = UsdGeom.Mesh.Define(stage, "/World/Board/Inlay")
loose = UsdGeom.Mesh.Define(stage, "/World/Loose")

wood = UsdShade.Material.Define(stage, "/Looks/Wood")
inlay_mat = UsdShade.Material.Define(stage, "/Looks/Inlay")
preview = UsdShade.Material.Define(stage, "/Looks/WoodPreview")

print("HasAPI before:", top.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
top_api = UsdShade.MaterialBindingAPI.Apply(top.GetPrim())
print("HasAPI after Apply:",
      top.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
top_api.Bind(wood)
bound, rel = top_api.ComputeBoundMaterial()
print("direct bind:", bound.GetPath(), rel.GetName())

top_api.Bind(
    preview,
    bindingStrength=UsdShade.Tokens.weakerThanDescendants,
    materialPurpose=UsdShade.Tokens.preview,
)
print("purposes:", UsdShade.MaterialBindingAPI.GetMaterialPurposes())
pbound, prel = top_api.ComputeBoundMaterial(UsdShade.Tokens.preview)
print("preview bind:", pbound.GetPath(), prel.GetName())

board_api = UsdShade.MaterialBindingAPI.Apply(board.GetPrim())
inlay_api = UsdShade.MaterialBindingAPI.Apply(inlay.GetPrim())
inlay_api.Bind(inlay_mat)
board_api.Bind(
    wood, bindingStrength=UsdShade.Tokens.weakerThanDescendants)
print("inlay when parent weaker:",
      inlay_api.ComputeBoundMaterial()[0].GetPath())
board_api.Bind(
    wood, bindingStrength=UsdShade.Tokens.strongerThanDescendants)
print("inlay when parent stronger:",
      inlay_api.ComputeBoundMaterial()[0].GetPath())

loose_api = UsdShade.MaterialBindingAPI.Apply(loose.GetPrim())
loose_api.Bind(wood)
loose_api.UnbindDirectBinding()
ubound, _ = loose_api.ComputeBoundMaterial()
print("after UnbindDirectBinding valid:", bool(ubound))
print("unbound rel targets:",
      list(loose_api.GetDirectBindingRel().GetTargets()))

sub = top_api.CreateMaterialBindSubset("faces", Vt.IntArray([0, 1]))
print("subset family:", sub.GetFamilyNameAttr().Get())
```

**Expected output**
```text
HasAPI before: False
HasAPI after Apply: True
direct bind: /Looks/Wood material:binding
purposes: ['', 'preview', 'full']
preview bind: /Looks/WoodPreview material:binding:preview
inlay when parent weaker: /Looks/Inlay
inlay when parent stronger: /Looks/Wood
after UnbindDirectBinding valid: False
unbound rel targets: []
subset family: materialBind
```

Default `Bind(wood)` does not disturb the later preview-purpose bind: they are different relationships.

### 9. Real-world use case
A car body mesh binds a full-fidelity Material (`purpose=full`, paint flakes, clearcoat) and a cheap PreviewSurface (`purpose=preview`) for usdview. Body panels are GeomSubsets `paint` / `glass` / `chrome`, each with `familyName = materialBind` and its own bind. The assembly root binds a weaker "clay" Material so any unpainted child still has a look.

### 10. Common mistakes
> [!MISTAKE] `Bind` without `Apply`. The rel exists, `HasAPI` is False, UsdValidation fails. Fix: `Apply` first.

> [!MISTAKE] Expecting `UnbindDirectBinding` to clear inherited parent binds. It only authors `None` on **this** prim.

> [!MISTAKE] Creating a GeomSubset with empty `familyName` and binding it. Material families must be **`materialBind`**. Use `CreateMaterialBindSubset`.

### 11. Exam traps
> [!TRAP] "Parent bind always loses to the child." Only if the parent is `weakerThanDescendants`. Default / unauthored is **stronger**.

> [!TRAP] Collection binding relationship has one target, the Material. It has **two**: collection, then Material.

> [!TRAP] `GetMaterialPurposes()` includes `'all'`. The all-purpose token is the **empty string** `''`.

> [!TRAP] `purpose` on `UsdGeom.Imageable` (`proxy` / `render`) is a different concept from material-binding purpose (`preview` / `full`). Do not mix them (Chapter 39.6 vs this section).

### 12. Practice questions
1. What two Python calls make a legal mesh bind?
2. Parent binds Wood `strongerThanDescendants`, child binds Inlay. What does the child resolve to?
3. `GetMaterialPurposes()` prints what three strings?

**Answers**
1. **`MaterialBindingAPI.Apply(prim)` then `.Bind(material)`.**
2. **Wood.** Stronger parent wins.
3. **`''`, `'preview'`, `'full'`.** Empty string is all-purpose.

### 13. Exam takeaways
> [!KEY]
> - Obj 8.3: `Apply` then `Bind`; `ComputeBoundMaterial` to resolve.
> - Purposes: `''` (all), `preview`, `full`. Strength lives in `bindMaterialAs`.
> - Default strength is strongerThanDescendants (parent wins).
> - Collection bind rel = `[collection, material]`. Subsets use family `materialBind`.
> - `UnbindDirectBinding` → `rel = None`; inherited binds can remain.

---

## 40.7 Exposing material parameters for overrides

### 1. What is it?
A Material can publish **interface inputs** — public knobs such as `inputs:paint` — that internal shaders connect *to*. A shot or assembly layer then overrides `inputs:paint` on the Material without diving into PreviewSurface, textures, or connections.

### 2. Why do we need it?
If every lookdev edit retargets `/Looks/Paint/Preview.inputs:diffuseColor`, referencing assets (Chapter 16) and variant sets become brittle: rename the shader child and every override breaks. Interface inputs are the stable API of the look, the same idea as exposing one color on a MaterialX public node or a DCC "published parameter."

### 3. Beginner explanation
Think of a blender with a single "strength" dial on the outside. Inside, that dial's cable runs to the motor. You do not open the housing to change speed. The Material's `inputs:paint` is the dial; the Shader's `diffuseColor` is the motor, connected to the dial.

*Where the analogy breaks:* USD still lets you override the internal shader input in a stronger layer. The interface is a *convention for stability*, not a lock.

### 4. Technical explanation
- Create on the Material: `mat.CreateInput("paint", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))`. USDA: `color3f inputs:paint = (0.8, 0.2, 0.1)` on the **Material** prim.
- Connect the *shader* input to that interface: `shader.GetInput("diffuseColor").ConnectToSource(paintInput)`. USDA: `color3f inputs:diffuseColor.connect = </Looks/Paint.inputs:paint>`.
- Notice the reverse of §40.2's terminal: there, the Material **output** connected to a Shader **output**. Here, a Shader **input** connects to a Material **input**.
- `GetConnectedSources()` on the shader input reports `source.GetPath() == /Looks/Paint` and `sourceName == paint` (the connectable is the Material prim).
- Downstream: `over` the Material (or a reference to the asset) and `Set` the interface input. Internal connections stay. This is the composition-friendly override path (Chapters 16, 20).
- Name interface inputs for *artists* (`paint`, `wear`, `roughness`), not for the shader implementation (`diffuseColor`), so you can retarget the internal graph later.

### 5. Mental model

```text
Shot layer:   over Material "Paint" { inputs:paint = green }

Asset:        Material "Paint"
                inputs:paint = red          ← public knob
                outputs:surface.connect → Preview.outputs:surface
                Shader "Preview"
                  inputs:diffuseColor.connect → Material.inputs:paint
```

Override the knob, not the child shader.

### 6. Simple example
Material `/Looks/Paint` has `inputs:paint = (0.8, 0.2, 0.1)`. Preview `diffuseColor` connects to it. A shot `over` sets `inputs:paint = (0, 1, 0)`. The network is unchanged; the color is green.

### 7. USDA example

```usda
#usda 1.0

def Material "Paint"
{
    color3f inputs:paint = (0.8, 0.2, 0.1)
    token outputs:surface.connect = </Paint/Preview.outputs:surface>

    def Shader "Preview"
    {
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor.connect = </Paint.inputs:paint>
        token outputs:surface
    }
}
```

- Interface input sits on the Material, sibling to `outputs:surface`.
- Shader input `.connect` points at **`.inputs:paint`**, not at another shader.

### 8. Python example

```python
from pxr import Usd, UsdShade, Sdf

stage = Usd.Stage.CreateInMemory()
mat = UsdShade.Material.Define(stage, "/Looks/Paint")
sh = UsdShade.Shader.Define(stage, "/Looks/Paint/Preview")
sh.CreateIdAttr("UsdPreviewSurface")
paint = mat.CreateInput("paint", Sdf.ValueTypeNames.Color3f)
paint.Set((0.8, 0.2, 0.1))
diff = sh.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f)
diff.ConnectToSource(paint)
sh.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat.CreateSurfaceOutput().ConnectToSource(sh.GetOutput("surface"))

print("interface:", paint.GetFullName(), paint.Get())
print("shader connected:", diff.HasConnectedSource())
src, _ = diff.GetConnectedSources()
print("connected from:", src[0].source.GetPath(), src[0].sourceName)
for line in stage.GetRootLayer().ExportToString().splitlines():
    if "paint" in line or "diffuseColor" in line or "connect" in line:
        print(line.strip())
```

**Expected output**
```text
interface: inputs:paint (0.8, 0.2, 0.1)
shader connected: True
connected from: /Looks/Paint paint
color3f inputs:paint = (0.8, 0.2, 0.1)
token outputs:surface.connect = </Looks/Paint/Preview.outputs:surface>
color3f inputs:diffuseColor.connect = </Looks/Paint.inputs:paint>
```

`GetFullName()` includes the `inputs:` namespace; `sourceName` is just `paint`.

### 9. Real-world use case
A hero car publishes `inputs:paint`, `inputs:roughness`, and `inputs:flake`. The lookdev graph inside `/Looks/CarPaint` has eight shaders. Lighting publishes a shot layer with `over "CarPaint" { color3f inputs:paint = (0.02, 0.09, 0.28) }` for a night-blue livery. The internal graph can be rebuilt next week; the shot still only knows `paint`.

### 10. Common mistakes
> [!MISTAKE] Connecting the Material input *to* the Shader input (`paint.connect = </Paint/Preview.inputs:diffuseColor>`). The public knob would then *follow* the shader, which is the opposite of an override API. Shader input connects to the Material input.

> [!MISTAKE] Exposing twenty internal texture scale inputs. Publish the three the shot actually changes; keep the rest private.

> [!MISTAKE] Naming the interface `diffuseColor` and then switching the internal graph to a texture mix. Shots that overrode `diffuseColor` now fight the texture. Use a stable public name (`paint`).

### 11. Exam traps
> [!TRAP] USDA with `inputs:paint` on the Shader. That is just another shader input, not an interface. Interface inputs live on the **Material** (or NodeGraph).

> [!TRAP] "You must flatten the Material to override a color." An `over` on the interface input is enough (Chapter 20).

> [!TRAP] `ConnectToSource(paint)` reports source path `/Looks/Paint/Preview`. No: the connectable is the **Material** prim `/Looks/Paint`.

### 12. Practice questions
1. Where is `inputs:paint` authored in a well-designed look?
2. Write the USDA connection that lets Preview's `diffuseColor` follow that knob.
3. Why not override `/Looks/Paint/Preview.inputs:diffuseColor` from the shot?

**Answers**
1. On the **Material** prim (an interface input).
2. `color3f inputs:diffuseColor.connect = </Looks/Paint.inputs:paint>` on the Shader.
3. It is brittle: rename or replace the Preview child and the shot breaks. The interface name is the public API.

### 13. Exam takeaways
> [!KEY]
> - Material `CreateInput` = public knob; shader inputs connect *to* it.
> - USDA: `Shader.inputs:diffuseColor.connect = </Material.inputs:paint>`.
> - Override the interface in a stronger layer; leave the graph intact.
> - Name knobs for artists, not for the current shader child.

---

## Chapter lab(s)

**Lab 34 — UsdPreviewSurface + primvar-driven color + binding** (★★☆, Obj 8.2–8.4). You author a PreviewSurface Material, bind it with `MaterialBindingAPI`, add a `UsdPrimvarReader_float3` so `displayColor` drives `diffuseColor`, then expose `inputs:paint` as an interface override. Stretch: UVTexture + `st` reader, and a `materialBind` GeomSubset.

Chapter 29's exporter sketch is the warm-up; this lab is the complete network.

## USDA reading exercise(s)

**Exercise 40-A.** A lookdev USDA is supposed to show red plastic in usdview. Why is the mesh still grey?

```usda
#usda 1.0

def Mesh "Tile" (
    prepend apiSchemas = ["MaterialBindingAPI"]
)
{
    rel material:binding = </Looks/Paint>
}

def Scope "Looks"
{
    def Material "Paint"
    {
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor = (0.8, 0.1, 0.1)
        token outputs:surface
    }
}
```

**Exercise 40-B.** What Material does `/Set/Knob` resolve to for all-purpose binding, and why?

```usda
#usda 1.0

def Xform "Set" (
    prepend apiSchemas = ["MaterialBindingAPI"]
)
{
    rel material:binding = </Looks/Clay> (
        bindMaterialAs = "weakerThanDescendants"
    )

    def Mesh "Knob" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {
        rel material:binding = </Looks/Chrome>
    }
}

def Scope "Looks"
{
    def Material "Clay" {}
    def Material "Chrome" {}
}
```

**Exercise 40-C.** Does this network satisfy Obj 8.4 (diffuse from a primvar)? If not, what is wrong?

```usda
#usda 1.0

def Mesh "Flag"
{
    color3f[] primvars:displayColor = [(0, 1, 0)] (
        interpolation = "constant"
    )
}

def Material "FromPrimvar"
{
    token outputs:surface.connect = </FromPrimvar/Preview.outputs:surface>

    def Shader "ColorReader"
    {
        uniform token info:id = "UsdPrimvarReader_float2"
        token inputs:varname = "primvars:displayColor"
        float2 outputs:result
    }

    def Shader "Preview"
    {
        uniform token info:id = "UsdPreviewSurface"
        color3f inputs:diffuseColor.connect = </FromPrimvar/ColorReader.outputs:result>
        token outputs:surface
    }
}
```

## Chapter review

### Summary
- Bind **Materials**. Shaders live inside them; `info:id` names the implementation (`UsdPreviewSurface`, `UsdUVTexture`, `UsdPrimvarReader_float2` / `_float3`).
- Material IsA NodeGraph; connect `outputs:surface` to the surface shader.
- Obj 8.2: PreviewSurface with `diffuseColor` / `metallic` / `roughness` / `opacity`.
- Textures: reader `varname=st` → UVTexture `file` + `st` → `rgb` → `diffuseColor`.
- Obj 8.4: `UsdPrimvarReader_float3`, `varname=displayColor`, mesh `primvars:displayColor`.
- Obj 8.3: `MaterialBindingAPI.Apply` then `Bind`. Purposes `''` / `preview` / `full`. Default strength parent-wins.
- Interface inputs on the Material are the public override API.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `info:id` on a Material | Wrong place; belongs on a Shader |
| `UsdPreviewSurface` as a prim type | It is an id string on type `Shader` |
| Mesh grey in usdview, Material exists | Missing bind, missing `Apply`, or `outputs:surface` not connected |
| Obj 8.4 / "from a primvar" | `UsdPrimvarReader_float3` + `varname=displayColor` |
| `varname = "primvars:st"` | Drop the namespace; use `"st"` |
| `HasAPI(MaterialBindingAPI)` False | Forgot `Apply` (rel may still exist) |
| Parent bind vs child bind | Read `bindMaterialAs`; default is stronger (parent wins) |
| `material:binding:collection:X` | Two targets: collection, then Material |
| `familyName = "materialBind"` | Per-face materials via GeomSubset |
| `inputs:paint` on the Material | Interface knob; shaders connect to it |
| Value *and* `.connect` on one input | Connection wins for shading |
| `purpose = "proxy"` on the mesh | Imageable purpose (Ch 39), not material purpose |

### Review questions

**Q40.1** · Obj 8.2 · Easy · Single choice
Where is `uniform token info:id = "UsdPreviewSurface"` authored?
A. On the Material prim · B. On a Shader prim · C. On the bound Mesh · D. As layer metadata

**Q40.2** · Obj 8.2 · Easy · Single choice
`UsdShade.Material.Define(...).GetPrim().IsA(UsdShade.NodeGraph)` prints:
A. False · B. True · C. An error · D. None

**Q40.3** · Obj 8.2 · Medium · Single choice
`ComputeSurfaceSource()` returns:
A. A Shader · B. A Material · C. A tuple `(shader, name, type)` · D. A relationship

**Q40.4** · Obj 8.4 · Medium · Single choice
Which Shader `info:id` reads mesh `primvars:displayColor` into Preview `diffuseColor`?
A. `UsdPrimvarReader_float2` · B. `UsdUVTexture` · C. `UsdPrimvarReader_float3` · D. `UsdPreviewSurface`

**Q40.5** · Obj 8.4 · Medium · Single choice
The reader's `varname` for that primvar must be:
A. `primvars:displayColor` · B. `displayColor` · C. `diffuseColor` · D. `st`

**Q40.6** · Obj 8.3 · Easy · Select two.
A correct mesh bind includes:
A. `MaterialBindingAPI.Apply` · B. `.Bind(material)` · C. `info:id` on the mesh · D. `Kind.Register`

**Q40.7** · Obj 8.3 · Medium · Single choice
Parent bind is unauthored strength; child binds a different Material. Who wins?
A. Child · B. Parent · C. Neither; the mesh is grey · D. The stronger purpose

**Q40.8** · Obj 8.3 · Medium · Single choice
`GetMaterialPurposes()` includes which all-purpose token?
A. `"all"` · B. `"default"` · C. `""` · D. `"universal"`

**Q40.9** · Obj 8.3 · Medium · Select two.
A collection material bind relationship's targets are:
A. The collection path · B. The Material path · C. Every included mesh path · D. The Shader path

**Q40.10** · Obj 8.2 · Medium · USDA reading
What color does shading use for `diffuseColor`?

```usda
#usda 1.0

def Shader "Preview"
{
    uniform token info:id = "UsdPreviewSurface"
    color3f inputs:diffuseColor = (1, 0, 0)
    color3f inputs:diffuseColor.connect = </Paint/Reader.outputs:result>
}
```

A. Red `(1, 0, 0)` · B. The connected reader result · C. Average of both · D. Preview fallback grey

**Q40.11** · Obj 8.2 · Easy · Single choice
Typical UVTexture network uses which reader id and varname?
A. `UsdPrimvarReader_float3`, `st` · B. `UsdPrimvarReader_float2`, `st` · C. `UsdPrimvarReader_float2`, `primvars:st` · D. `UsdUVTexture`, `uv`

**Q40.12** · Obj 8.3 · Medium · Single choice
`UnbindDirectBinding()` on a mesh with no ancestor bind authors:
A. Removal of `MaterialBindingAPI` · B. `rel material:binding = None` · C. Deletion of the Material · D. `rel material:binding:preview = None` only

**Q40.13** · Obj 8.2 · Medium · Single choice
A shot should recolor an asset without editing `/Looks/Paint/Preview`. What should the asset have authored?
A. A variant set on the Shader · B. Material interface `inputs:paint` that Preview connects to · C. `displayColor` on every mesh · D. `bindMaterialAs` on the mesh

### Answers

**Q40.1 — B.** `info:id` identifies a Shader implementation. Review: §40.1, §40.3.

**Q40.2 — B.** Material derives from NodeGraph. Review: §40.1.

**Q40.3 — C.** Unpack the tuple; do not call `.GetPath()` on the return value itself. Review: §40.2.

**Q40.4 — C.** float3 = color. float2 is UVs; UVTexture is images; PreviewSurface is the lighting model. Review: §40.5.

**Q40.5 — B.** `varname` is the primvar name without `primvars:`. Review: §40.5.

**Q40.6 — A, B.** Apply then Bind. Meshes do not carry `info:id`. Review: §40.6.

**Q40.7 — B.** Unauthored / default strength is `strongerThanDescendants`. Review: §40.6.

**Q40.8 — C.** Empty string is all-purpose. Review: §40.6.

**Q40.9 — A, B.** Two targets, collection then Material; not the included prims and not a Shader. Review: §40.6.

**Q40.10 — B.** Connection wins; `(1, 0, 0)` is leftover. Review: §40.2.

**Q40.11 — B.** `UsdPrimvarReader_float2` + `varname=st`. Review: §40.4.

**Q40.12 — B.** The applied schema stays; the direct rel is authored `None`. Review: §40.6.

**Q40.13 — B.** Interface inputs are the public override API. Review: §40.7.

### USDA exercise answers

**40-A — The Material has no Shader, and `info:id` is on the Material.** Hydra runs a Shader with `info:id = UsdPreviewSurface` whose `outputs:surface` is connected to the Material terminal. Move `info:id` and `diffuseColor` onto a child Shader, declare `outputs:surface` there, and connect `token outputs:surface.connect = </Looks/Paint/Preview.outputs:surface>` on the Material. The bind and `Apply` are already correct.

**40-B — `/Looks/Chrome`.** The parent is explicitly `weakerThanDescendants`, so the child's direct bind wins. If `bindMaterialAs` were omitted, fallback stronger would have resolved to Clay.

**40-C — No.** Three problems: (1) reader id is `float2` but color needs `UsdPrimvarReader_float3`; (2) `varname` must be `displayColor`, not `primvars:displayColor`; (3) the mesh never binds the Material (`MaterialBindingAPI` + `rel material:binding`). Any one of these fails Obj 8.4.

## Further reading

- [S06] OpenUSD API — UsdShadeMaterial, UsdShadeShader, UsdShadeNodeGraph, UsdShadeMaterialBindingAPI, UsdShadeConnectableAPI: https://openusd.org/release/api/usd_shade_page_front.html
- [S06] UsdPreviewSurface specification: https://openusd.org/release/spec_usdpreviewsurface.html
- [S04] OpenUSD Glossary (Material, Shader, primvar): https://openusd.org/release/glossary.html
- [S14] NVIDIA Learn OpenUSD — materials and binding: https://docs.nvidia.com/learn-openusd/latest/index.html
- Chapter 11 (primvars), Chapter 29 (exporter PreviewSurface sketch), Chapter 39.5 (GeomSubset `materialBind`)
