# Cheat sheet — Primvars & interpolation

**USD 26.08** · Obj 5.1, 8.1, 8.4 · Ch 11, 40 · Namespace `primvars:<name>` (+ optional `primvars:<name>:indices`).

Factory: `UsdGeom.PrimvarsAPI`. Wrapper: `UsdGeom.Primvar`.  
Built-in on Gprims: `primvars:displayColor`, `displayOpacity`.

## Interpolation (array length)

Mesh: **V** vertices, **F** faces, **C** corners (`sum(faceVertexCounts)`).

| Token | Length | Maps to |
|-------|--------|---------|
| `constant` | 1 | Whole prim |
| `uniform` | F | One per **face** |
| `varying` | ~V | Surface-varying (smooth) |
| `vertex` | V | One per **point** |
| `faceVarying` | C | One per **face-corner** (seams) |

Tokens: `UsdGeom.Tokens.constant` / `uniform` / `varying` / `vertex` / `faceVarying`.

USDA:

```usda.fragment
color3f[] primvars:displayColor = [(1, 0, 0)] (
    interpolation = "constant"
)
```

| Need | Interpolation |
|------|----------------|
| Whole-object color | `constant` |
| Per-face ID | `uniform` |
| Shared vertex color | `vertex` |
| UV seams / hard corners | `faceVarying` |

**Lengths must match.** Vertex-length array + `faceVarying` is a visual bug (Obj 5.5).

One triangle: `faceVertexCounts` len **1**, `faceVertexIndices` len **3**.  
Two quads, 4 verts: vertex colors **4**; faceVarying `st` **8**.

## Indexed primvars

Values = palette; indices = which palette slot per element.

```{.python .norun}
pv.Set([(1, 0, 0), (0, 1, 0)])
pv.SetIndices([0, 1, 0, 1])
# IsIndexed() True — independent of interpolation
```

`elementSize`: entries per logical element (e.g. 3 floats packed).

## Inheritance

A primvar on an **ancestor Xform** applies to descendant meshes unless overridden.

```{.python .norun}
UsdGeom.PrimvarsAPI(child).FindPrimvarWithInheritance("displayColor")
# finds /Parent.primvars:displayColor — not child.GetAttribute("displayColor")
```

Instance **root** primvars can tint one native instance without de-instancing.  
Authoring on an instance-**proxy** descendant (`OverridePrim("/I/Mesh")`) **raises**.

## Shading (Obj 8.4)

| Want | Network |
|------|---------|
| Vertex `displayColor` → PreviewSurface | `UsdPrimvarReader_float3`, `inputs:varname = displayColor` |
| UV texture | `UsdPrimvarReader_float2` (`st`) → `UsdUVTexture` → `diffuseColor` |

Roles: `color3f[]` for color, `texCoord2f[]` for `st`, `float[]` for scalars.  
Do not store sRGB display color as anonymous `float3[]` if you mean a color role.

## Related visual bugs (Obj 5.5 / 5.6)

| Symptom | Check |
|---------|--------|
| Bounds wrong after moving points | `ComputeExtentFromPlugins` then `Set` `extent` |
| Hidden in viewer | `purpose` vs viewer mask (`proxy`/`guide`) |
| Child invisible | `Get()` is `inherited`; `ComputeVisibility()` walks parents |
| Subdivision surprise | Mesh fallback **`catmullClark`** |
| Tiny / sideways asset | Stage `metersPerUnit` / `upAxis` (in-memory: **Y**, **0.01**) |
