# Cheat sheet — LIVERPS & value resolution

**USD 26.08** (`usd-core` 26.8) · Obj 1.1, 1.6, 1.8 · Ch 14–22 · Day 7

Older spelling **LIVRPS** is the same order **without relocates**.

## Strength (strongest → weakest)

| | Arc | Author | Beats |
|--|-----|--------|-------|
| **L** | Local | Session, root, `subLayers`, nested `over` | I V E R P S |
| **I** | Inherits | `prepend inherits = </_Class>` | V E R P S |
| **V** | VariantSets | `variantSet "lod" = { "hi" { } }` | E R P S |
| **E** | rElocates | Layer metadata `relocates = { </old>: </new> }` | R P S |
| **R** | References | `prepend references = @asset@` | P S |
| **P** | Payloads | `prepend payload = @heavy@` (keyword is singular) | S |
| **S** | Specializes | `prepend specializes = </_Defaults>` | — |

```text
L  →  I  →  V  →  E  →  R  →  P  →  S
stack  class  switch  rename  catalog lazy  defaults
```

## Two-step rank (Obj 1.1)

**A. Inside one stack** (this *is* Local at the root node):  
session → root → `subLayers[0]` (and its children) → `subLayers[1]` …  
**First listed sublayer is strongest** (not last-wins).

**B. Across arcs:** if the current stack is silent on this *field*, walk LIVERPS.

Each referenced/payloaded asset has its **own** nested LIVERPS walk.

Same-letter lists: `prepend` stronger than `append`. Letters never jump the queue.

## Verified 26.08 outcomes

| Situation | Winner |
|-----------|--------|
| Inherit `7` vs referenced `2` | **7** (I > R) |
| Specialize `7` vs referenced `2` | **2** (R > S) |
| Local `3` vs selected variant `11` | **3** (L > V) |
| Inherit `8` vs selected variant `2` | **8** (I > V) |
| Local `2` in a **weaker** sublayer vs inherit `8` | **2** (L still beats I) |
| Session `9` vs root `1` | **9** |
| Mute strongest sublayer (`6`); weaker has `15` | **15**; muted layer **drops** from `GetLayerStack` |
| Stronger **default** vs weaker time samples | Default; `GetTimeSamples()` → `[]` |
| Samples only; `Get()` (no time) | **`None`** (not the first sample) |
| Relocate dest `over` vs source-path `over` | **Destination**; source ignored |
| Relocate keys that are not composed paths | **Ignored**; sibling `over` is not a move |
| Shot `variants = { size = "lg" }` vs asset `sm` | Shot selection (local) |

## Value resolution order (one field, one time)

1. Authored **time sample** (or clip sample) at/near that time  
2. Else authored **default**  
3. Else **schema fallback** (Cube `size` → `2.0` even with no variant)  
4. Else **nothing** (`Get()` → `None`; custom attrs are not valid)

`GetPropertyStack()` / `GetPrimStack()`: contributing specs, **strongest first**.  
Silent layers do not appear. Weaker specs still list for debugging.

## Time, offsets, interpolation

`composedTime = offset + scale × layerTime`  
`Sdf.LayerOffset(offset, scale)` on a reference or `subLayerOffsets`.

| Call | Result (26.08) |
|------|----------------|
| Samples 0 and 10; **linear** `Get(4)` | `(4,0,0)` |
| Same; **held** `Get(4)` | `(0,0,0)` (holds previous) |
| `Get(99)` past last sample, linear *or* held | **last sample** (no extrapolate) |
| `GetEditTargetForLocalLayer` + sublayer `offset=10`; `Set(..., 20)` | Stored at **t=10** |
| Bare `Usd.EditTarget(layer)`; `Set(..., 20)` | Stored at **t=20** |

## Debug “why doesn’t this opinion show?”

1. `GetPropertyStack` / `GetResolveInfo` / `Usd.PrimCompositionQuery`  
2. Muted layer? Wrong **edit target**?  
3. Stronger **letter** (inherit hiding a variant; reference hiding a specialize)?  
4. Stronger **local** in a stronger sublayer?  
5. Empty variant selection → opinions not composed (Cube `size` still shows fallback `2`)?  
6. Relocate source path mismatch? Instance proxy (`OverridePrim` raises)?  
7. `LoadNone` skipped a **payload** (references still load)?

**Make it win:** author **local** on the composed path, or move the layer up the stack — do not expect specializes or variants to beat inherits.
