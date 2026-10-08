# Cheat sheet — USDA syntax

**USD 26.08** · Obj 4.3, 7.3 · Ch 7, 14–20 · Always **multiline** `{` `}` — one-line `{ double r = 1 }` **does not parse**.

## File skeleton

```usda
#usda 1.0
(
    defaultPrim = "World"
    upAxis = "Z"
    metersPerUnit = 0.01
    subLayers = [
        @./layout.usda@,
        @./anim.usda@
    ]
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)

def Xform "World" (
    kind = "component"
)
{
    def Sphere "Ball"
    {
        double radius = 1
        color3f[] primvars:displayColor = [(1, 0, 0)]
        rel material:binding = </Looks/Paint>
    }
}
```

First line **must** be `#usda 1.0`. Layer metadata lives in the top `( ... )`.  
`defaultPrim` is layer metadata, not a prim field.

## Specifiers

| Keyword | Defines? | In `Traverse`? | Typical use |
|---------|----------|----------------|-------------|
| `def` | Yes (type may be `''`) | Yes | Create a prim |
| `over` | **No** alone | Only if something else defines | Overlay opinions |
| `class` | Abstract | Usually skipped in world Traverse | Inherit/specialize source |

Typeless `def "Dock"` → `IsDefined()` True, type `''`.  
`over "Jetty"` with no defining spec → `IsDefined()` **False**, `bool(prim)` **True** (not null).  
Missing path → `bool`/`IsValid` False; `IsDefined()` **raises**.

## Composition arcs (on the prim’s `( ... )`)

```usda.fragment
def "Hero" (
    prepend references = @./asset.usda@
    prepend payload = @./heavy.usda@
    prepend inherits = </_Look>
    prepend specializes = </_Defaults>
    instanceable = true
    prepend variantSets = "lod"
    variants = {
        string lod = "high"
    }
)
{
}
```

- Payload keyword is **`payload`**, not `payloads`. Python: `GetPayloads()`.  
- `@file@` uses the target’s `defaultPrim` unless you write `@file@</Prim>`.  
- No `defaultPrim` and no prim path → `UnresolvedPrimPath` (`<defaultPrim>`).  
- Missing file → `InvalidAssetPath`.

## Variants

```usda.fragment
variantSet "fit" = {
    "tight" {
        double binWidth = 1
    }
    "loose" {
        double binWidth = 8
    }
}
```

No selection → custom attr `Get()` is `None` (not composed).  
`GetVariantSets().GetNames()` → set names.  
`GetVariantSet("fit").GetVariantNames()` → `"tight"`, `"loose"`.  
Empty `GetVariantEditContext()` authors **local**, not inside a variant.

## List editing (same field, one spec)

| USDA | Effect |
|------|--------|
| `prepend references = @a@` | Front (stronger) |
| `append references = @b@` | Back (weaker) |
| `delete references = @a@` | Drop `a` from **weaker** layers |
| `references = [@a@, @b@]` | Explicit list (replaces) |

Same-spec `delete` + `prepend` of the **same** item does **not** remove it. Delete from a **stronger** layer.

`subLayers` first item is strongest. Time offset: `@anim.usda@ (offset = 10; scale = 2)`.

## Properties

| Kind | USDA | Python |
|------|------|--------|
| Attribute | `double radius = 1` | `CreateAttribute` / schema getter |
| Time samples | `double r.timeSamples = { 0: 1, 10: 5 }` | `attr.Set(v, time)` |
| Relationship | `rel material:binding = </Mat>` | `CreateRelationship` |
| Metadata | `customData = { string id = "x" }` | `SetCustomDataByKey` |
| API schema | `prepend apiSchemas = ["MaterialBindingAPI"]` | `MaterialBindingAPI.Apply` |
| Block | (authored none) | `attr.Block()` |

Namespaces: `primvars:`, `xformOp:`, `inputs:` (UsdLux intensity is `inputs:intensity`).

## Paths and assets

| Syntax | Meaning |
|--------|---------|
| `</World/Ball>` | Absolute prim path |
| `.radius` | Property on the current prim |
| `@./chair.usda@` | Layer-relative asset (composition anchors to **this layer**) |
| `@chair.usda@` | Context-dependent; may need a resolver context |

## Traps

- One-line `{ double x = 1 }` parse error — always break braces.  
- `CreateNew("x.usd")` is crate (`PXR-USDC`); formatId still `usd`.  
- USDA copied to `.usd` still **opens as text**; formatId stays `usd`.  
- `rel material:binding` without `apiSchemas` → HasAPI **False**, rel **True**.  
- Nested `over "Seat"` under `instanceable` is **ignored**.  
- Relocates are **layer** metadata; keys must be **composed** paths.
