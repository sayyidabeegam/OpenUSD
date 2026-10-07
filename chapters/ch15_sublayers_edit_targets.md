# Chapter 15 — Sublayers, Layer Stacks, and Edit Targets

> **Exam domain:** Composition (23%) · **Objectives:** 1.3, 1.5 (also 1.1) · **Study day:** 5 · **Est. time:** 110 min
> **Prerequisites:** Ch 3 (Layers), Ch 10 (Time Samples), Ch 14 (Composition Fundamentals)

Chapter 3 introduced sublayers and the session layer. Chapter 14 showed that the local layer stack is the "L" in LIVERPS, the strongest source of opinions. This chapter covers how to control that stack: its order, its timing, where your edits go, how to switch layers off temporarily, and how teams share one scene without overwriting each other.

## Learning goals

- Predict the strength order of a layer stack with nested sublayers and a session layer.
- Apply a layer offset (`offset`, `scale`) to a sublayer and compute the stage time of a time sample.
- Direct edits to a chosen layer or variant with `Usd.EditTarget`, `SetEditTarget`, and `Usd.EditContext`.
- Mute and unmute layers to isolate problems, and explain what muting does not do.
- Design a sublayer-based layering strategy for several departments working on one shot (Obj 1.5).
- Compare sublayers with references and payloads for a given use case (Obj 1.3).

## Key terms

| Term | One-line definition |
|------|---------------------|
| Sublayer | A layer listed in another layer's `subLayers` metadata; its opinions join the same layer stack |
| Layer stack | A root layer plus all its sublayers, recursively, in strength order |
| Session layer | An in-memory layer that is stronger than the root layer and is not saved by `stage.Save()` |
| Layer offset | A time mapping (`offset`, `scale`) applied to a sublayer or reference: stage time = layer time × scale + offset |
| `Sdf.LayerOffset` | The Python class that stores a layer offset |
| Edit target | The layer (and optional path mapping) that receives new edits made through the `Usd` API |
| `Usd.EditContext` | A `with` block that sets an edit target temporarily and restores the previous one |
| Variant edit target | An edit target that writes inside a chosen variant of a variant set |
| Layer muting | Temporarily removing a layer from composition on one stage, without editing any file |
| Department layer | A sublayer owned by one team (layout, animation, lighting) in a shared shot |

---

## 15.1 Sublayer ordering

### 1. What is it?

A layer's `subLayers` metadata is an **ordered list** of other layers. The layer that lists them and all its sublayers form a **layer stack**. In that stack, the order is the strength order: the layer itself first, then its sublayers from first to last, with each sublayer's own sublayers inserted right after it.

### 2. Why do we need it?

Sublayers let many people contribute to the **same namespace** (the same prim paths) from separate files. A shot file can stack a layout layer, an animation layer, and a lighting layer. Their order decides who wins when two of them author the same attribute. Getting the order wrong is one of the most common reasons an edit "doesn't show up" (Obj 1.8).

### 3. Beginner explanation

This is the **transparent sheets on a projector** analogy from Chapter 3: the top sheet wins. The `subLayers` list is read from the top sheet down. If one of those sheets has its own little pile of sheets clipped to it, that pile goes right under it, before the next sheet in the list.

*Where the analogy breaks:* a sheet that is silent about a field lets weaker sheets "show through" for that field only. Also, the session layer is a sheet that sits above the root layer but is never saved to disk.

### 4. Technical explanation

- Strength order of a stage's local layer stack: **session layer** (and its sublayers) → **root layer** → root's `subLayers[0]` and its sublayers (depth-first) → `subLayers[1]` → … (verified on USD 26.08).
- `stage.GetLayerStack(includeSessionLayers=True)` returns the layers in that order. `stage.GetRootLayer().subLayerPaths` is the editable list of the root's direct sublayers.
- `subLayers` is a plain ordered list, not a list op: there is no `prepend subLayers`. To change order, edit the list (`layer.subLayerPaths = [...]`, `.insert(0, path)`, `.append(path)`, `.remove(path)`). The stage recomposes immediately.
- A layer can appear in a stack only once. Sublayer paths are resolved relative to the layer that lists them (anchored paths, Chapter 33).
- All layers in one layer stack share one namespace: `/World/Car` in every sublayer is the same prim. That is the key difference from a reference, which grafts another file's prim to a new path (Chapter 16).

**Sublayers vs. references vs. payloads (Obj 1.3)**

| Question | Sublayer | Reference | Payload |
|----------|----------|-----------|---------|
| Strength position | L (strongest, local) | R | P (below R) |
| Namespace | Same paths as the root | Target prim is mapped to the referencing prim's path | Same as reference |
| Granularity | Whole layer | One prim (subtree) | One prim (subtree) |
| Can be unloaded? | No (but can be muted) | No | Yes (`stage.Unload`, Chapter 17) |
| Typical use | Department/work layers in a shot | Reusing an asset many times | Heavy geometry you may not need |

### 5. Mental model

```text
 shot.usda            subLayers = [a, b, d];  b.usda: subLayers = [c]

 STRONGEST  [shot-session] -> [shot] -> [a] -> [b] -> [c] -> [d]  WEAKEST
                                                 \____/
                                         b's own sublayer comes
                                         right after b, before d
```

### 6. Simple example

| Layer (strongest first) | `/Ball.radius` |
|-------------------------|----------------|
| `shot.usda` (root) | — |
| `a.usda` | 1 |
| `b.usda` | 2 |
| `c.usda` (sublayer of `b`) | 3 |
| `d.usda` | 4 |
| **Composed** | **1** |

Reorder the root's list to `[d, a, b]` and the composed radius becomes 4.

### 7. USDA example

*File: shot.usda*

```usda
#usda 1.0
(
    subLayers = [
        @a.usda@,
        @b.usda@,
        @d.usda@
    ]
)
```

- `subLayers = [...]` — layer metadata at the top of the file. The first entry, `a.usda`, is the strongest sublayer.
- `@...@` — asset-path syntax. Relative paths are resolved next to `shot.usda`.
- The root has no prims of its own; it only assembles the stack. Its own opinions, if any, would beat all sublayers.

### 8. Python example

```python
from pxr import Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("c.usda", '#usda 1.0\ndef Sphere "Ball"\n{\n    double radius = 3\n}\n')
write("b.usda", """#usda 1.0
(
    subLayers = [@c.usda@]
)
over "Ball"
{
    double radius = 2
}
""")
write("a.usda", '#usda 1.0\nover "Ball"\n{\n    double radius = 1\n}\n')
write("d.usda", '#usda 1.0\nover "Ball"\n{\n    double radius = 4\n}\n')
write("shot.usda", "#usda 1.0\n(\n    subLayers = [@a.usda@, @b.usda@, @d.usda@]\n)\n")

stage = Usd.Stage.Open("shot.usda")
print("layer stack:", [l.GetDisplayName() for l in stage.GetLayerStack()])
radius = stage.GetPrimAtPath("/Ball").GetAttribute("radius")
print("radius:", radius.Get())
print("opinions:", [s.layer.GetDisplayName() for s in radius.GetPropertyStack()])

stage.GetRootLayer().subLayerPaths = ["d.usda", "a.usda", "b.usda"]
print("after reorder:", radius.Get())

stage.SetEditTarget(stage.GetSessionLayer())
radius.Set(9.0)
print("after session edit:", radius.Get())
print("opinions:", [s.layer.GetDisplayName() for s in radius.GetPropertyStack()])
```

**Expected output**

```text
layer stack: ['shot-session.usda', 'shot.usda', 'a.usda', 'b.usda', 'c.usda', 'd.usda']
radius: 1.0
opinions: ['a.usda', 'b.usda', 'c.usda', 'd.usda']
after reorder: 4.0
after session edit: 9.0
opinions: ['shot-session.usda', 'd.usda', 'a.usda', 'b.usda', 'c.usda']
```

`c.usda` sits between `b.usda` and `d.usda`: nested sublayers are depth-first. The session layer beats everything.

### 9. Real-world use case

A visual-effects shot file typically contains only `subLayers`: `shot_fx.usda`, `shot_lighting.usda`, `shot_anim.usda`, `shot_layout.usda`, and a sequence-wide layer at the bottom. Sequence-level fixes in the bottom layer reach every shot of the sequence, and any shot can still override them in its own, stronger layers. Architecture firms use the same pattern: a base building layer, then a stronger "design option" layer, then a stronger "review markup" layer.

### 10. Common mistakes

> [!MISTAKE] Assuming the last sublayer in the list is the strongest ("the last one written wins"). The **first** entry is the strongest.

> [!MISTAKE] Writing `prepend subLayers = [...]`. That does not parse; `subLayers` is a plain list. Edit the list order instead.

> [!MISTAKE] Using a sublayer to bring in one asset at a new location. Sublayers cannot move prims to a new path; use a reference (Chapter 16).

### 11. Exam traps

> [!TRAP] Nested sublayers: a question may show `b.usda` with its own `subLayers`. Its children rank right after `b`, **before** the next entry of the parent's list.

> [!TRAP] The root layer's own opinions beat all of its sublayers. Only the session layer is stronger than the root.

> [!TRAP] "Sublayers can be unloaded like payloads" — false. Sublayers can be muted (15.4), but loading and unloading is a payload feature.

### 12. Practice questions

**Q15.1-1** `root.usda` has `subLayers = [@x.usda@, @y.usda@]`, and `x.usda` has `subLayers = [@z.usda@]`. What is the strength order, strongest first (ignore the session layer)?
A. root, x, y, z B. root, x, z, y C. z, x, y, root D. y, x, z, root

**Q15.1-2** Which **two** statements describe sublayers correctly? (Select two.)
A. All layers in one layer stack share the same prim namespace.
B. A sublayer can be loaded and unloaded with `stage.Load()`.
C. Sublayer opinions are local opinions, the "L" in LIVERPS.
D. A sublayer must contain a `defaultPrim`.

**Answers**

- **Q15.1-1: B.** Depth-first: `z` comes right after its parent `x`, before `y`.
- **Q15.1-2: A and C.** Loading is for payloads; `defaultPrim` matters for references, not sublayers.

### 13. Exam takeaways

> [!KEY]
> - Order: session → root → `subLayers[0]` (+ its sublayers, depth-first) → `subLayers[1]` → …
> - First entry of `subLayers` = strongest sublayer. The root's own opinions beat all sublayers.
> - `subLayers` is a plain list (edit `subLayerPaths`); no `prepend`/`append` keywords.
> - Sublayers share one namespace; references graft a prim to a new path; payloads can be unloaded.

---

## 15.2 Layer offsets on sublayers

### 1. What is it?

A **layer offset** shifts and/or scales the time of everything in a sublayer. It has two numbers: `offset` (a shift in time codes) and `scale` (a speed factor). The rule is **stage time = layer time × scale + offset**. In Python it is an `Sdf.LayerOffset`.

### 2. Why do we need it?

An animation layer may have been authored starting at frame 0, but the shot starts at frame 1001. Or a layer must play twice as slowly. Without offsets you would have to rewrite every time sample in the file. With an offset, the file stays untouched and the stage maps its times.

### 3. Beginner explanation

Imagine a song file and a playlist. The playlist entry can say "start this song 20 seconds in" and "play it at half speed". The song itself is not edited; only the playlist entry changes how it plays.

*Where the analogy breaks:* the offset does not crop anything. Samples before the shifted start still exist (USD holds the first sample's value before it). And default values (non-time-sampled values) have no time, so offsets do not affect them.

### 4. Technical explanation

- USDA syntax: `subLayers = [@anim.usda@ (offset = 20; scale = 2)]`. Either field may be left out (defaults `offset = 0`, `scale = 1`).
- Python: `layer.subLayerOffsets` is a list of `Sdf.LayerOffset`, parallel to `layer.subLayerPaths`. Assign an element to change it: `layer.subLayerOffsets[0] = Sdf.LayerOffset(20, 2)`. The stage recomposes immediately.
- `Sdf.LayerOffset(offset, scale)` maps a time: `offset_obj * layer_time` returns the stage time. `GetInverse()` maps back. `IsIdentity()` is true for (0, 1).
- **Nested offsets compose.** If `top.usda` sublayers `mid.usda` with offset 5, and `mid.usda` sublayers `anim.usda` with offset 10, a sample at time 0 in `anim.usda` appears at time 15. `Sdf.LayerOffset` objects can be multiplied: `A * B` means "apply B, then A".
- **timeCodesPerSecond (TCPS) mismatch.** If a sublayer's `timeCodesPerSecond` differs from the root's, USD adds a scale automatically. A 24-TCPS layer under a 48-TCPS root has its sample at time 24 appear at time 48 (verified on USD 26.08).
- `attr.GetTimeSamples()` on the stage reports times already mapped to stage time.
- Offsets also exist on references and payloads (Chapter 16, Obj 1.4) and appear in value resolution (Chapter 21).

### 5. Mental model

```text
 anim.usda (layer time)      0 -------------- 10
                             |                 |
      x scale (2)            0 -------------------------------- 20
      + offset (20)                            20 ------------------------- 40
 stage time                                    20 ------------------------- 40

 stage = layer * scale + offset          layer = (stage - offset) / scale
```

### 6. Simple example

`anim.usda` has `tx` = 0 at time 0 and 100 at time 10. Sublayered with `(offset = 20; scale = 2)`, the stage sees samples at times 20 and 40. At stage time 30 (layer time 5) the linear interpolation gives 50.

### 7. USDA example

*File: shot.usda*

```usda
#usda 1.0
(
    endTimeCode = 40
    startTimeCode = 0
    subLayers = [
        @anim.usda@ (offset = 20; scale = 2)
    ]
)
```

- `@anim.usda@ (offset = 20; scale = 2)` — the layer offset is written in parentheses right after the asset path, with fields separated by `;`.
- `startTimeCode` / `endTimeCode` — the stage's playback range (Chapter 10). They are not changed by the offset; you set them to cover the shifted animation.

### 8. Python example

```python
from pxr import Sdf, Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("anim.usda", """#usda 1.0
def "Ball"
{
    double tx.timeSamples = {
        0: 0,
        10: 100,
    }
}
""")
write("shot.usda", """#usda 1.0
(
    subLayers = [@anim.usda@ (offset = 20; scale = 2)]
)
""")

stage = Usd.Stage.Open("shot.usda")
tx = stage.GetPrimAtPath("/Ball").GetAttribute("tx")
print("stage samples:", tx.GetTimeSamples())
for t in (10, 20, 30, 40):
    print(f"tx at stage time {t}: {tx.Get(t)}")

off = stage.GetRootLayer().subLayerOffsets[0]
print("offset, scale:", off.offset, off.scale)
print("layer 10 -> stage", off * 10.0)
print("stage 30 -> layer", off.GetInverse() * 30.0)

stage.GetRootLayer().subLayerOffsets[0] = Sdf.LayerOffset(offset=100)
print("new offset samples:", tx.GetTimeSamples())

write("mid.usda", "#usda 1.0\n(\n    subLayers = [@anim.usda@ (offset = 10)]\n)\n")
write("top.usda", "#usda 1.0\n(\n    subLayers = [@mid.usda@ (offset = 5)]\n)\n")
nested = Usd.Stage.Open("top.usda")
print("nested:", nested.GetPrimAtPath("/Ball").GetAttribute("tx").GetTimeSamples())
combined = Sdf.LayerOffset(5) * Sdf.LayerOffset(10)
print("A * B :", combined.offset, combined.scale)
```

**Expected output**

```text
stage samples: [20.0, 40.0]
tx at stage time 10: 0.0
tx at stage time 20: 0.0
tx at stage time 30: 50.0
tx at stage time 40: 100.0
offset, scale: 20.0 2.0
layer 10 -> stage 40.0
stage 30 -> layer 5.0
new offset samples: [100.0, 110.0]
nested: [15.0, 25.0]
A * B : 15.0 1.0
```

Before the first sample (stage time 10), USD holds the first sample's value, 0.0.

### 9. Real-world use case

A crowd shot reuses one walk-cycle layer for a background group, shifted so it starts at frame 1001. A sports broadcast digital twin plays a recorded motion layer at half speed for a replay (`scale = 2`). An animation authored at 24 time codes per second can be sublayered into a 48-per-second project, and USD rescales the timing automatically.

### 10. Common mistakes

> [!MISTAKE] Computing the inverse: "offset 20 means a sample at stage 20 came from layer 20". No: layer time = (stage time − offset) / scale. Stage 20 is layer 0.

> [!MISTAKE] Expecting an offset to change a default value. Defaults have no time; only time samples (and other time-based data such as value clips) move.

> [!MISTAKE] Forgetting to extend `endTimeCode` after shifting animation later. The samples are there, but playback stops before them.

### 11. Exam traps

> [!TRAP] Order of operations: scale first, then offset. With `(offset = 20; scale = 2)`, layer time 10 maps to 40, not 60.

> [!TRAP] Nested sublayer offsets add up (and scales multiply). A question with two levels of offsets wants the combined mapping.

> [!TRAP] Different `timeCodesPerSecond` values between root and sublayer are not an error. USD scales the sublayer's times automatically.

### 12. Practice questions

**Q15.2-1** A sublayer is listed as `@walk.usda@ (offset = 1000)`. `walk.usda` has a sample at time 1. At what stage time does it appear?
A. 1 B. 1000 C. 1001 D. 999

**Q15.2-2** A sublayer offset is `(offset = 10; scale = 0.5)`. A stage time of 20 corresponds to which layer time?
A. 5 B. 15 C. 20 D. 40

**Q15.2-3** Which Python attribute stores the offsets of a layer's sublayers?
A. `Sdf.Layer.subLayerOffsets` B. `Usd.Stage.GetLayerOffsets()` C. `Sdf.Layer.timeCodesPerSecond` D. `Usd.Attribute.GetTimeOffset()`

**Answers**

- **Q15.2-1: C.** 1 × 1 + 1000 = 1001.
- **Q15.2-2: C.** Layer time = (20 − 10) / 0.5 = 20.
- **Q15.2-3: A.** It is a list of `Sdf.LayerOffset`, parallel to `subLayerPaths`. The other names are not real APIs.

### 13. Exam takeaways

> [!KEY]
> - Stage time = layer time × scale + offset; inverse: (stage − offset) / scale.
> - USDA: `@file.usda@ (offset = N; scale = S)`; Python: `layer.subLayerOffsets[i] = Sdf.LayerOffset(N, S)`.
> - Nested offsets compose; different `timeCodesPerSecond` values add an automatic scale.
> - Offsets move time samples, never default values.

---

## 15.3 Edit targets (`Usd.EditTarget`, `SetEditTarget`)

### 1. What is it?

The **edit target** is the place where the `Usd` API writes your edits. When you call `attr.Set(...)` or `stage.DefinePrim(...)`, the change goes into the edit target's layer. By default the edit target is the stage's **root layer**. You change it with `stage.SetEditTarget(...)` or temporarily with `Usd.EditContext`.

### 2. Why do we need it?

The `Usd` API shows a composed view, but every edit must land in exactly one layer. If you are the lighter, your edits must go into `lighting.usda`, not into the shot's root layer or the layout layer. Edit targets let you work with the convenient composed API while choosing precisely which file receives the change. Without them, all edits pile into the root layer (Obj 1.1, Obj 1.5).

### 3. Beginner explanation

You are looking at the projector image made of many sheets, holding a marker. The edit target is the answer to "which sheet am I drawing on right now?". You see the combined picture, but your ink only goes onto the sheet you picked.

*Where the analogy breaks:* drawing on a lower sheet does not guarantee the new drawing is visible. If a stronger sheet already has an opinion for that field, your edit is stored but loses.

### 4. Technical explanation

- `stage.GetEditTarget()` returns a `Usd.EditTarget`. `edit_target.GetLayer()` is the receiving layer.
- `stage.SetEditTarget(layer)` accepts an `Sdf.Layer` or a `Usd.EditTarget`. The layer must be in the stage's **local layer stack** (session layer, root layer, or one of their sublayers). Otherwise USD raises `Tf.ErrorException` ("…is not in the local LayerStack…"). A muted layer is not in the layer stack, so it cannot be a target.
- `with Usd.EditContext(stage, target):` sets the target for the block, then restores the previous one, even if an exception occurs. Prefer it to calling `SetEditTarget` twice.
- **Time mapping.** `stage.GetEditTargetForLocalLayer(layer)` builds a target that includes the sublayer's layer offset, so `attr.Set(value, stage_time)` stores the sample at the matching **layer** time. A bare `Usd.EditTarget(layer)` has no offset mapping and stores the stage time unchanged (verified on USD 26.08).
- **Variant edit targets.** `variant_set.GetVariantEditTarget()` returns a target that writes inside the currently selected variant; `variant_set.GetVariantEditContext()` is the `with`-block form (Chapter 18). Select the variant first with `SetVariantSelection`.
- You cannot target a layer that arrives only through a reference or payload from this stage. To edit an asset, open the asset itself (`Usd.Stage.Open("asset.usda")` or `Sdf.Layer.FindOrOpen`) and edit it there.
- Reading is never affected by the edit target: `Get()` always returns the composed value.

### 5. Mental model

```text
          composed view (read)   <---   all layers
                 |
   attr.Set(v) --+--> EDIT TARGET --> exactly one layer (or one variant in it)
                        |
           must be in the local layer stack:
           [session] [root] [sublayer] [sublayer] ...   (not muted)
```

### 6. Simple example

The shot sublayers `anim.usda` with `(offset = 20; scale = 2)`. You set the edit target with `GetEditTargetForLocalLayer(anim)` and call `tx.Set(1.0, 30)`. The file `anim.usda` gets a sample at time 5, because (30 − 20) / 2 = 5. With `Usd.EditTarget(anim)` instead, the sample is stored at time 30.

### 7. USDA example

*File: chair.usda* (after authoring through a variant edit target)

```usda
#usda 1.0

def "Chair" (
    variants = {
        string color = "red"
    }
    prepend variantSets = "color"
)
{
    variantSet "color" = {
        "blue" {
        }
        "red" {
            custom string paint = "red!"
        }
    }
}
```

- `prepend variantSets = "color"` and `variants = {...}` — written by `AddVariantSet` and `SetVariantSelection`.
- `custom string paint = "red!"` sits **inside** `"red" { }` because the edit target was the variant, not the prim itself.

### 8. Python example

```python
from pxr import Sdf, Tf, Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("anim.usda", '#usda 1.0\ndef "Ball"\n{\n}\n')
write("shot.usda", """#usda 1.0
(
    subLayers = [@anim.usda@ (offset = 20; scale = 2)]
)
""")

stage = Usd.Stage.Open("shot.usda")
anim = Sdf.Layer.Find("anim.usda")
print("default target:", stage.GetEditTarget().GetLayer().GetDisplayName())

stage.SetEditTarget(stage.GetEditTargetForLocalLayer(anim))
tx = stage.GetPrimAtPath("/Ball").CreateAttribute("tx", Sdf.ValueTypeNames.Double)
tx.Set(1.0, 30)
stage.SetEditTarget(Usd.EditTarget(anim))
tx.Set(2.0, 30)
print("anim.usda samples:", anim.GetAttributeAtPath("/Ball.tx").GetInfo("timeSamples"))

stage.SetEditTarget(stage.GetRootLayer())
with Usd.EditContext(stage, stage.GetSessionLayer()):
    stage.GetPrimAtPath("/Ball").SetMetadata("comment", "try bigger")
print("restored target:", stage.GetEditTarget().GetLayer().GetDisplayName())
print("in session layer:", stage.GetSessionLayer().GetPrimAtPath("/Ball").comment)

try:
    stage.SetEditTarget(Sdf.Layer.CreateAnonymous("elsewhere"))
except Tf.ErrorException as err:
    print("error, not in local stack:", "not in the local LayerStack" in str(err))

chair = Usd.Stage.CreateInMemory()
prim = chair.DefinePrim("/Chair")
color = prim.GetVariantSets().AddVariantSet("color")
color.AddVariant("red")
color.AddVariant("blue")
color.SetVariantSelection("red")
with color.GetVariantEditContext():
    prim.CreateAttribute("paint", Sdf.ValueTypeNames.String).Set("red!")
spec = chair.GetRootLayer().GetObjectAtPath("/Chair{color=red}.paint")
print("variant spec:", spec.path, spec.default)
```

**Expected output**

```text
default target: shot.usda
anim.usda samples: {5.0: 1.0, 30.0: 2.0}
restored target: shot.usda
in session layer: try bigger
error, not in local stack: True
variant spec: /Chair{color=red}.paint red!
```

The first `Set` went through the offset mapping (stored at layer time 5). The second used a bare edit target (stored at 30). The `Usd.EditContext` block restored the root layer as the target afterwards.

### 9. Real-world use case

A layout tool opens the shot, sets the edit target to `layout.usda`, and moves props; a lighting tool opens the same shot with the target on `lighting.usda`. Asset tools use variant edit targets to author each look variant (`red`, `blue`) inside one asset file. Review tools use the session layer as the edit target, so reviewers can try changes without touching saved files.

### 10. Common mistakes

> [!MISTAKE] Forgetting to set the edit target, so every edit lands in the root (shot) layer. Use `with Usd.EditContext(stage, layer):` around each department's edits.

> [!MISTAKE] Authoring into a weaker layer and expecting the value to change on screen. The edit is stored, but a stronger opinion still wins. Check `attr.GetPropertyStack()`.

> [!MISTAKE] Using `Usd.EditTarget(layer)` for animation in an offset sublayer. Samples end up at the wrong time. Use `stage.GetEditTargetForLocalLayer(layer)`.

> [!MISTAKE] Authoring in a variant without selecting it first. The variant edit target writes into the **selected** variant; call `SetVariantSelection` first.

### 11. Exam traps

> [!TRAP] The default edit target is the **root layer**, not the session layer and not the strongest sublayer.

> [!TRAP] "Set the edit target to the referenced asset's layer" — not possible from the referencing stage; only local layer stack layers are valid targets.

> [!TRAP] The edit target changes where writes go, never what reads return. A question claiming `Get()` reads only from the edit target is wrong.

### 12. Practice questions

**Q15.3-1** Which code puts the edit into `fx.usda` and then restores the previous target automatically?
A. `stage.GetRootLayer().subLayerPaths.append("fx.usda")`
B. `with Usd.EditContext(stage, fx_layer): attr.Set(1.0)`
C. `stage.MuteLayer(fx_layer.identifier)`
D. `fx_layer.Save()`

**Q15.3-2** A stage's root layer sublayers `a.usda`. You call `stage.SetEditTarget(other_layer)` where `other_layer` is only referenced by a prim. What happens?
A. Edits go into `other_layer`.
B. A `Tf.ErrorException` is raised; the target is unchanged.
C. `other_layer` is added as a sublayer.
D. Edits go into the session layer.

**Q15.3-3** Which **two** calls produce valid edit targets? (Select two.)
A. `stage.GetEditTargetForLocalLayer(sublayer)`
B. `variant_set.GetVariantEditTarget()`
C. `stage.GetUsedLayers()`
D. `Sdf.LayerOffset(10)`

**Answers**

- **Q15.3-1: B.** `Usd.EditContext` sets and restores the target.
- **Q15.3-2: B.** Only layers in the local layer stack are allowed.
- **Q15.3-3: A and B.** `GetUsedLayers` returns layers, not targets; `Sdf.LayerOffset` is a time mapping.

### 13. Exam takeaways

> [!KEY]
> - Edit target = where `Usd` API writes go. Default = root layer.
> - `stage.SetEditTarget(layer)` / `with Usd.EditContext(stage, layer):` — layer must be in the local layer stack.
> - `GetEditTargetForLocalLayer` maps time through sublayer offsets; bare `Usd.EditTarget(layer)` does not.
> - `GetVariantEditContext()` writes inside the selected variant.
> - Editing a weaker layer stores the opinion but may not change the composed value.

---

## 15.4 Layer muting (`MuteLayer`)

### 1. What is it?

**Muting** a layer tells one stage to compose as if that layer did not exist. You call `stage.MuteLayer(layer_identifier)`. Nothing in any file changes, and you can bring it back with `stage.UnmuteLayer(...)`.

### 2. Why do we need it?

Debugging: "Is the lighting layer causing this?" Mute it and look. Performance: mute a heavy layer you do not need for your current task. Review: compare a scene with and without one department's work. All of this without editing `subLayers` in a file that others share.

### 3. Beginner explanation

On the projector, muting is like lifting one sheet off for a moment. The sheet still exists on your desk, unchanged. Put it back and the picture returns.

*Where the analogy breaks:* lifting a sheet affects only your projector. Another stage that opens the same files is not affected, and the mute is not saved anywhere.

### 4. Technical explanation

- `stage.MuteLayer(identifier)`, `stage.UnmuteLayer(identifier)`, `stage.IsLayerMuted(identifier)`, `stage.GetMutedLayers()`, and `stage.MuteAndUnmuteLayers(mute_list, unmute_list)` (one recomposition for many changes). They take layer **identifiers** (strings), for example `layer.identifier`.
- Muting works on any layer the stage uses: sublayers, and also layers reached through references or payloads. Muting a referenced asset's layer produces a composition warning ("…was muted for reference…") and the reference contributes nothing.
- The **root layer cannot be muted** (USD raises an error: "Cannot mute cache's root layer").
- A muted layer is removed from `stage.GetLayerStack()`, but `root.subLayerPaths` still lists it: muting is stage state, not file data.
- A muted layer cannot be the edit target (it is no longer in the local layer stack).
- After muting, USD may release the muted layer. Keep the identifier string, not an old `Sdf.Layer` Python object, to unmute it later.
- If the muted layer held the only `def` of a prim, the prim may remain as an undefined `over` from other layers (`prim.IsDefined()` is `False`) or disappear entirely.
- Muting is per stage and is not saved. To make the change permanent, edit `subLayers` instead.

### 5. Mental model

```text
 files (unchanged):  shot.usda  subLayers = [fx.usda, model.usda]

 stage A (fx muted):   [shot] ......... [model]      radius = 1
 stage B (normal):     [shot] [fx]      [model]      radius = 5

 mute = per stage, in memory, reversible, never saved
```

### 6. Simple example

`fx.usda` sets `radius = 5`; `model.usda` defines the ball with `radius = 1`. With both, radius is 5. Mute `fx.usda`: radius is 1. Unmute: 5 again. Opening the shot on a second stage gives 5 even while the first stage has it muted.

### 7. USDA example

*File: fx.usda*

```usda
#usda 1.0

over "Ball"
{
    double radius = 5
}
```

- This is the layer we will mute. It only holds an `over`, so muting it removes its opinion and nothing else.
- Note that the file has no "muted" flag: muting can only be requested on a stage, never authored in USDA.

### 8. Python example

```python
from pxr import Sdf, Tf, Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("model.usda", '#usda 1.0\ndef Sphere "Ball"\n{\n    double radius = 1\n}\n')
write("fx.usda", '#usda 1.0\nover "Ball"\n{\n    double radius = 5\n}\n')
write("shot.usda", "#usda 1.0\n(\n    subLayers = [@fx.usda@, @model.usda@]\n)\n")

stage = Usd.Stage.Open("shot.usda")
radius = stage.GetPrimAtPath("/Ball").GetAttribute("radius")
fx_id = Sdf.Layer.Find("fx.usda").identifier
print("before mute:", radius.Get())

stage.MuteLayer(fx_id)
print("muted:", radius.Get(), stage.IsLayerMuted(fx_id))
print("muted layers:", [p.split("/")[-1] for p in stage.GetMutedLayers()])
print("layer stack:", [l.GetDisplayName() for l in stage.GetLayerStack(False)])
print("file still lists:", list(stage.GetRootLayer().subLayerPaths))

other = Usd.Stage.Open("shot.usda")
print("second stage:", other.GetPrimAtPath("/Ball").GetAttribute("radius").Get())

stage.UnmuteLayer(fx_id)
print("unmuted:", radius.Get())

try:
    stage.MuteLayer(stage.GetRootLayer().identifier)
except Tf.ErrorException as err:
    print("mute root fails:", "Cannot mute" in str(err))

stage.MuteLayer(Sdf.Layer.Find("model.usda").identifier)
ball = stage.GetPrimAtPath("/Ball")
print("model muted -> defined:", ball.IsDefined(), "type:", repr(ball.GetTypeName()))
```

**Expected output**

```text
before mute: 5.0
muted: 1.0 True
muted layers: ['fx.usda']
layer stack: ['shot.usda', 'model.usda']
file still lists: ['fx.usda', 'model.usda']
second stage: 5.0
unmuted: 5.0
mute root fails: True
model muted -> defined: False type: ''
```

The second stage shares the same layers but not the mute. With `model.usda` muted, `/Ball` exists only as an `over` from `fx.usda`: it is not defined and has no type.

### 9. Real-world use case

A lighter's scene renders slowly. They mute the `fx.usda` layer to check whether the effects are responsible, without editing the shared shot file. A supervisor in review mutes the latest animation layer to compare with the previous layout. In a factory digital twin, an engineer mutes a "proposed changes" layer to see the current factory floor.

### 10. Common mistakes

> [!MISTAKE] Expecting `stage.Save()` to remember the mute. Muting is not stored in any layer. Remove the sublayer from `subLayers` to make it permanent.

> [!MISTAKE] Passing an `Sdf.Layer` object to `MuteLayer`. It takes the identifier string: `stage.MuteLayer(layer.identifier)`.

> [!MISTAKE] Keeping an old `Sdf.Layer` Python handle for a muted layer and using it later. It may have expired; look the layer up again by identifier after unmuting.

### 11. Exam traps

> [!TRAP] "Muting deletes the layer's opinions from disk" — false. Muting is in memory, per stage, reversible.

> [!TRAP] You cannot mute the root layer. A question offering "mute the root layer to test without it" is offering an impossible action.

> [!TRAP] Muting vs. deactivating: muting removes a whole **layer**; `prim.SetActive(False)` removes one **prim** subtree and is an authored opinion that is saved (Chapter 4).

### 12. Practice questions

**Q15.4-1** Which **two** statements about `stage.MuteLayer()` are true? (Select two.)
A. It affects only the stage on which it is called.
B. It writes `muted = true` into the layer's metadata.
C. It can mute a layer that arrives through a reference.
D. It can mute the stage's root layer.

**Q15.4-2** After `stage.MuteLayer(id)` on a sublayer, what does `stage.GetRootLayer().subLayerPaths` show?
A. The muted path is removed.
B. The muted path is still listed.
C. The muted path is replaced by `None`.
D. The list is empty.

**Answers**

- **Q15.4-1: A and C.** Muting is per stage and can target any used layer except the root; nothing is written to files.
- **Q15.4-2: B.** The file data is unchanged; only the stage's composition ignores the layer.

### 13. Exam takeaways

> [!KEY]
> - `MuteLayer`, `UnmuteLayer`, `IsLayerMuted`, `GetMutedLayers`, `MuteAndUnmuteLayers` take identifiers.
> - Per stage, in memory, reversible, never saved; files are untouched.
> - The root layer cannot be muted; a muted layer cannot be the edit target.
> - Great for debugging "which layer causes this?" (Obj 1.8, Chapter 42).

---

## 15.5 Multi-user layering strategies

### 1. What is it?

A **layering strategy** is a plan for which layers exist in a shared scene, who owns each one, and in what order they are stacked. The usual building block is a **department layer**: a sublayer owned by one team, edited only by that team through its edit target.

### 2. Why do we need it?

USD has no built-in file locking or merging. If two artists edit and save the same layer, one overwrites the other. A layering strategy avoids this by giving each workstream its own file, and it makes strength intentional: the team that should win a conflict sits higher in the stack (Obj 1.5).

### 3. Beginner explanation

Think of a group project where every student writes on their own transparent sheet, and the teacher stacks the sheets in an agreed order. Nobody erases anyone else's work, and the order says whose drawing wins where they overlap.

*Where the analogy breaks:* in real productions the "order" is a pipeline decision, and some teams also need to edit assets (through references), not only the shot. Layering is one tool; asset structure (Chapter 23) is the other.

### 4. Technical explanation

Common patterns (conventions, not rules enforced by USD):

| Pattern | How it works | Why |
|---------|--------------|-----|
| Department sublayers | `shot.usda` sublayers `lighting`, `fx`, `anim`, `layout` | One writer per file; clear ownership |
| Downstream is stronger | Later pipeline steps are higher in the list | Lighting can adjust what animation left; not the other way |
| Shared base at the bottom | `sequence.usda` or `set.usda` sublayered last | Fixes reach every shot; shots can override |
| Thin root layer | Root holds only `subLayers` (and stage metadata) | Nobody needs to write the root |
| Session layer for personal tweaks | Reviewer or artist edits not meant to be saved | Never pollutes shared files |
| Per-user work layer (optional) | A temporary strongest sublayer per artist, merged later | Try changes without blocking others |

Rules of thumb:

- Each tool sets its edit target to its department's layer before writing (15.3).
- Assets (characters, props) come in through **references or payloads**, not sublayers, so they can be reused and placed at any path (Chapter 16, 17). Shot-wide changes to many prims belong in **sublayers**. This is the core of Obj 1.3.
- `stage.Save()` saves every dirty layer in the local layer stack except the session layer. A careful tool saves only its own layer with `layer.Save()`.
- usdview's Layer Stack view, `stage.GetLayerStack()`, and `attr.GetPropertyStack()` show which department's layer holds the winning opinion. For splitting a monolithic asset into workstreams, see Chapter 22 (Obj 1.11).

### 5. Mental model

```text
 shot.usda (thin root: subLayers only)
   |
   +-- shot_lighting.usda   owner: lighting   STRONGEST (downstream)
   +-- shot_anim.usda       owner: animation
   +-- shot_layout.usda     owner: layout
   +-- sequence.usda        owner: sequence   WEAKEST (shared base)
         |
         `-- assets arrive by references/payloads, not sublayers
```

### 6. Simple example

Layout places `/Car` at x = 0 in `shot_layout.usda`. Animation authors `x = 5` in `shot_anim.usda`. Lighting adds a lamp in `shot_lighting.usda`. Each department saves only its own file. The composed car is at x = 5, because the animation layer is stronger than layout.

### 7. USDA example

*File: shot.usda*

```usda
#usda 1.0
(
    defaultPrim = "World"
    endTimeCode = 1100
    metersPerUnit = 0.01
    startTimeCode = 1001
    subLayers = [
        @shot_lighting.usda@,
        @shot_anim.usda@,
        @shot_layout.usda@,
        @sequence.usda@
    ]
    upAxis = "Y"
)
```

- A thin root: only stage metadata and the ordered department layers.
- `shot_lighting.usda` is first (strongest); `sequence.usda` is last (weakest, shared).
- Stage metadata such as `upAxis` and `metersPerUnit` is read from the root layer (Chapter 2), so it lives here, not in department layers.

### 8. Python example

Three departments author into their own layers through edit contexts; then we save and check what each file contains.

```python
from pxr import Sdf, Usd, UsdGeom


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


depts = ["shot_lighting.usda", "shot_anim.usda", "shot_layout.usda"]
for name in depts:
    write(name, "#usda 1.0\n")
paths = ", ".join(f"@{name}@" for name in depts)
write("shot.usda", f"#usda 1.0\n(\n    subLayers = [{paths}]\n)\n")

stage = Usd.Stage.Open("shot.usda")
layer = {name: Sdf.Layer.Find(name) for name in depts}

with Usd.EditContext(stage, layer["shot_layout.usda"]):
    car = UsdGeom.Xform.Define(stage, "/World/Car")
    car.AddTranslateOp().Set((0.0, 0.0, 0.0))
with Usd.EditContext(stage, layer["shot_anim.usda"]):
    op = car.GetPrim().GetAttribute("xformOp:translate")
    op.Set((5.0, 0.0, 0.0))
with Usd.EditContext(stage, layer["shot_lighting.usda"]):
    stage.DefinePrim("/World/Lamp", "SphereLight")
with Usd.EditContext(stage, stage.GetSessionLayer()):
    stage.GetPrimAtPath("/World/Lamp").SetMetadata("comment", "reviewer note")


def dirty_layers():
    return [l.GetDisplayName() for l in stage.GetLayerStack() if l.dirty]


print("dirty before save:", len(dirty_layers()), "layers")
stage.Save()
print("dirty after save :", dirty_layers())
print("car translate:", op.Get())
print("opinions:", [s.layer.GetDisplayName() for s in op.GetPropertyStack()])
for name in depts:
    paths = []
    layer[name].Traverse("/", paths.append)
    print(name, "holds", sorted(str(p) for p in paths if p.IsPrimPath()))
```

**Expected output**

```text
dirty before save: 4 layers
dirty after save : ['shot-session.usda']
car translate: (5, 0, 0)
opinions: ['shot_anim.usda', 'shot_layout.usda']
shot_lighting.usda holds ['/World', '/World/Lamp']
shot_anim.usda holds ['/World', '/World/Car']
shot_layout.usda holds ['/World', '/World/Car']
```

`stage.Save()` wrote the three department layers and left the session layer (with the reviewer note) unsaved. Each department file holds only the prims it touched; the `over`s for `/World` were created automatically so the edits have a parent path.

### 9. Real-world use case

Feature-animation studios run shots this way: layout, animation, character effects, effects, and lighting each publish one layer per shot, and the shot file stacks them in pipeline order. Game studios split a level into terrain, gameplay, audio, and lighting layers so designers and artists can work at the same time. In AEC, the structural, mechanical, and electrical teams each own a layer over a shared base model, and a coordination layer on top records agreed changes.

### 10. Common mistakes

> [!MISTAKE] Letting every tool write into the root shot layer. Merges become impossible. Keep the root thin and set the edit target per department.

> [!MISTAKE] Sublayering a character asset into a shot. The character is then fixed at its authored paths and cannot be placed twice. Reference it instead.

> [!MISTAKE] Putting an upstream department above a downstream one, so the lighter's tweaks are overridden by animation. Order the stack in pipeline order: downstream stronger.

> [!MISTAKE] Calling `stage.Save()` from a department tool and accidentally saving another department's half-finished edits. Save only your own layer with `layer.Save()`.

### 11. Exam traps

> [!TRAP] "USD locks a layer while someone edits it" — false. Avoiding conflicts is the job of the layering strategy (one writer per layer).

> [!TRAP] A multi-user question that offers "use variants for each department" is offering the wrong tool. Variants are alternatives for one asset (Chapter 18); departments need separate layers.

> [!TRAP] Sublayers vs. references: shot-wide work on shared paths → sublayers; reusable assets placed at new paths → references; heavy data you may defer → payloads.

### 12. Practice questions

**Q15.5-1** Four departments must edit the same shot at the same time without overwriting each other. What is the most appropriate structure?
A. One shared shot layer that everyone saves in turn
B. A shot root layer that sublayers one layer per department, each department editing only its own layer
C. A variant set with one variant per department
D. A payload per department that is unloaded while others work

**Q15.5-2** In a shot whose sublayers are `[lighting, anim, layout]`, the layout artist edits a car position that animation also authored, and sees no change. Which **two** explanations or fixes are correct? (Select two.)
A. The animation layer is stronger, so its opinion wins.
B. Layout should mute the root layer.
C. Animation (the stronger, downstream department) should remove or update its opinion.
D. Layout should save its layer twice.

**Answers**

- **Q15.5-1: B.** Separate department sublayers give one writer per file and an explicit strength order.
- **Q15.5-2: A and C.** The stronger layer's opinion hides layout's edit. The root layer cannot be muted, and saving twice changes nothing.

### 13. Exam takeaways

> [!KEY]
> - One writer per layer: department sublayers under a thin shot root.
> - Downstream departments are stronger; shared bases are weakest.
> - Each tool sets its edit target to its own layer; reviewers use the session layer.
> - Assets come in by reference/payload; shot-wide edits go in sublayers (Obj 1.3, 1.5).
> - `stage.Save()` saves dirty local layers except the session layer.

---

## Chapter lab(s)

- **Lab 05 — Build a sublayer stack and see who wins** (Chapters 3, 15; Obj 1.1). You build a three-layer stack with a nested sublayer, predict each composed value, then reorder and mute layers to check your predictions.
- **Lab 19 — Edit targets: author into layers and variants** (Chapter 15; Obj 1.1, 1.5). You write department edits through `Usd.EditContext`, author a look variant through a variant edit target, and use `GetEditTargetForLocalLayer` on an offset animation layer.

## USDA reading exercises

**Exercise 15-A.** Consider these files.

*File: shot.usda*

```usda
#usda 1.0
(
    subLayers = [
        @fix.usda@,
        @base.usda@ (offset = 100)
    ]
)
```

*File: base.usda*

```usda
#usda 1.0
(
    subLayers = [@older.usda@]
)

def Sphere "Ball"
{
    double radius.timeSamples = {
        0: 1,
        10: 2,
    }
}
```

*File: fix.usda*

```usda
#usda 1.0

over "Ball"
{
    color3f[] primvars:displayColor = [(1, 0, 0)]
}
```

`older.usda` contains `over "Ball" { double radius = 7 }`.

1. List the local layer stack, strongest first (without the session layer).
2. At which stage times does `/Ball.radius` have time samples?
3. What does `/Ball.radius` return at stage time 105?

**Exercise 15-B.** In the same scene, the stage's edit target is the root layer and a script calls `stage.MuteLayer(<identifier of fix.usda>)`, then `stage.Save()`. Is `fix.usda` still listed in `shot.usda` when the file is opened again? What color does `/Ball` show in a new stage?

## Chapter review

### Summary

- Layer stack order: session → root → `subLayers[0]` (with its own sublayers, depth-first) → `subLayers[1]` → …
- The first sublayer listed is the strongest; the root's own opinions beat all sublayers.
- `subLayers` is a plain list; edit `layer.subLayerPaths` to reorder. There is no `prepend subLayers`.
- Layer offsets: stage time = layer time × scale + offset; nested offsets compose; different `timeCodesPerSecond` values add an automatic scale.
- The edit target (default: root layer) decides where `Usd` API writes go; it must be in the local layer stack.
- `GetEditTargetForLocalLayer` maps time through sublayer offsets; a bare `Usd.EditTarget(layer)` does not.
- `Usd.EditContext` sets a target temporarily; `GetVariantEditContext()` writes inside the selected variant.
- Muting is per stage, in memory, reversible, never saved; the root layer cannot be muted.
- Multi-user strategy: one department per sublayer, downstream stronger, thin root, session layer for personal tweaks.
- Sublayers for shot-wide shared namespace; references for reusable assets; payloads for deferrable heavy data (Obj 1.3).

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| A nested `subLayers` inside a sublayer | Depth-first: its children rank right after it |
| `@file@ (offset = N; scale = S)` | Stage = layer × S + N |
| "Edits land in the wrong file" | Edit target; use `Usd.EditContext` |
| "Samples at the wrong time after Set" | Use `GetEditTargetForLocalLayer` for offset sublayers |
| "Test the scene without one layer" | `stage.MuteLayer(identifier)` (not the root) |
| "Many artists, one shot" | Department sublayers, one writer each, downstream stronger |
| "Try a change without saving" | Session layer as edit target |
| "Reuse an asset at several paths" | Reference, not sublayer |

### Review questions

**15-R1** · Obj 1.3 · Single choice
A team wants to place the same tree asset 40 times at different paths in a forest. Which arc is most appropriate?
A. Sublayers B. References C. Layer muting D. Specializes from the root layer

**15-R2** · Obj 1.1 · USDA reading
`root.usda` has `subLayers = [@p.usda@, @q.usda@]`, and `q.usda` has `subLayers = [@r.usda@]`. `p.usda` sets nothing on `/Lamp.inputs:intensity`; `q.usda` sets 20; `r.usda` sets 50; `root.usda` sets nothing. What is the composed intensity?
A. 50 B. 20 C. 70 D. The schema fallback

**15-R3** · Single choice
A sublayer is listed as `@anim.usda@ (offset = 24; scale = 0.5)`. A sample in `anim.usda` is at time 48. At what stage time does it appear?
A. 24 B. 48 C. 72 D. 120

**15-R4** · Obj 1.1 · Select two.
A script must write an override into `shot_fx.usda`, a sublayer of the open stage. Which **two** approaches work?
A. `stage.SetEditTarget(fx_layer)` and then `attr.Set(v)`
B. `with Usd.EditContext(stage, fx_layer): attr.Set(v)`
C. `stage.MuteLayer(fx_layer.identifier)` and then `attr.Set(v)`
D. `attr.Set(v)` with no other change

**15-R5** · Single choice
What is the default edit target of a newly opened stage?
A. The session layer B. The strongest sublayer C. The root layer D. None; you must set one

**15-R6** · Single choice
`anim.usda` is sublayered with `offset = 10`. You call `stage.SetEditTarget(Usd.EditTarget(anim))` and then `attr.Set(1.0, 30)`. At what time is the sample stored in `anim.usda`?
A. 20 B. 30 C. 40 D. 3

**15-R7** · Select two.
Which **two** statements about layer muting are correct?
A. A muted layer can still be the edit target.
B. Muting is not saved by `stage.Save()`.
C. The root layer cannot be muted.
D. Muting removes the layer from the file's `subLayers` list.

**15-R8** · Obj 1.5 · Single choice
In a shot, the lighting department's tweaks keep being hidden by animation's opinions. The sublayer list is `[layout, anim, lighting]`. What is the best structural fix?
A. Reorder to `[lighting, anim, layout]` so downstream departments are stronger.
B. Ask lighting to author into the session layer.
C. Mute the animation layer permanently.
D. Move lighting into a payload.

**15-R9** · Python reading
What does this print?

```{.python .norun}
off = Sdf.LayerOffset(offset=10, scale=2)
print(off * 5.0, off.GetInverse() * 30.0)
```

A. `20.0 10.0` B. `15.0 40.0` C. `20.0 20.0` D. `30.0 10.0`

**15-R10** · Obj 1.5 · Single choice
A reviewer wants to try a brighter light during a review without saving anything to shared files. Where should the edit go?
A. The root layer B. The lighting department layer C. The session layer D. The asset file of the light

**15-R11** · Obj 1.3 · Select two.
Which **two** are true of sublayers but not of references?
A. They share the root's prim namespace (same paths).
B. They are the strongest arc in LIVERPS (local).
C. They can target one specific prim in the other file.
D. They require `defaultPrim` in the target file.

**15-R12** · Single choice
A script runs `stage.SetEditTarget(asset_layer)` where `asset_layer` is reached only through a reference on `/World/Chair`. What happens?
A. Edits are written into the asset file.
B. A `Tf.ErrorException` is raised because the layer is not in the local layer stack.
C. The reference is converted to a sublayer.
D. Edits are silently discarded.

> The code in 15-R9 is a fragment (it omits the import), so it is not run automatically.

### Answers

**Exercise 15-A — Answer.**
1. `shot.usda`, `fix.usda`, `base.usda`, `older.usda` (`older.usda` is `base.usda`'s sublayer, so it comes right after it).
2. The offset applies to the `base.usda` entry, so its samples at 0 and 10 appear at stage times **100 and 110**.
3. **1.5**: stage time 105 is layer time 5, halfway between the samples 1 and 2. The default `radius = 7` in `older.usda` is weaker, and `base.usda` has time samples, so they win. (Time samples vs. defaults across layers is covered in Chapter 21.) Verified by composing the files on USD 26.08.

**Exercise 15-B — Answer.** Yes, `fix.usda` is still listed: muting never edits files, and `stage.Save()` only saves dirty layers. A new stage opens without the mute, so `/Ball` shows the red `displayColor` from `fix.usda` again.

- **15-R1: B.** References graft one asset to many paths. Sublayers share one namespace and cannot place copies. Review: §15.1, Chapter 16.
- **15-R2: B.** Order is root, p, q, r. `p` and `root` are silent, so `q` (20) wins over `r` (50). Values are not added. Review: §15.1.
- **15-R3: B.** 48 × 0.5 + 24 = 48. Review: §15.2.
- **15-R4: A and B.** Both set the edit target to the fx layer. A muted layer cannot be targeted; with no change, the edit goes into the root layer. Review: §15.3.
- **15-R5: C.** The root layer. Review: §15.3.
- **15-R6: B.** A bare `Usd.EditTarget(layer)` has no time mapping, so the sample is stored at 30. `GetEditTargetForLocalLayer` would have stored it at 20. Review: §15.3.
- **15-R7: B and C.** Muting is stage state only; muted layers leave the layer stack and cannot be targets. Review: §15.4.
- **15-R8: A.** The first sublayer is strongest, so downstream lighting should be listed first. The session layer is not saved; permanent muting and payloads do not fix ordering. Review: §15.5.
- **15-R9: A.** 5 × 2 + 10 = 20; (30 − 10) / 2 = 10. Review: §15.2.
- **15-R10: C.** The session layer is stronger than the root layer and is not saved by `stage.Save()`. Review: §15.5.
- **15-R11: A and B.** References can target one prim, and `defaultPrim` matters for references without a prim path. Review: §15.1.
- **15-R12: B.** Only layers in the local layer stack are valid edit targets. Review: §15.3.

## Further reading

- [S04] OpenUSD Glossary — entries "Sublayers", "Layer Stack", "Layer Offset", "EditTarget", "Session Layer". https://openusd.org/release/glossary.html
- [S05] OpenUSD tutorials — "Transformations, Time-sampled Animation, and Layer Offsets". https://openusd.org/release/tut_usd_tutorials.html
- [S06] OpenUSD API reference — `UsdStage` (`SetEditTarget`, `MuteLayer`, `GetEditTargetForLocalLayer`), `UsdEditTarget`, `UsdEditContext`, `SdfLayerOffset`. https://openusd.org/release/api/index.html
- [S08] USD FAQ — "What's the difference between sublayers and references?". https://openusd.org/release/usdfaq.html
- [S14] NVIDIA Learn OpenUSD — "Composition Basics" (layers and sublayers). https://docs.nvidia.com/learn-openusd/latest/index.html
