# Chapter 21 — LIVERPS and Value Resolution

> **Exam domain:** Composition (23%) · **Objectives:** 1.1, 1.6, 1.8 · **Study day:** 7 · **Est. time:** 150 min
> **Prerequisites:** Ch 10 (time samples, layer offsets), Ch 14–20 (every composition arc)

This is the chapter that turns the arcs you already know into a **prediction skill**. You will recite LIVERPS, split strength into "inside a stack" versus "across arcs," resolve defaults, time samples, clips, and fallbacks, and work ten puzzles the way the exam likes them: given USDA, what is the composed value, and why?

## Learning goals

- Recite LIVERPS in strength order and name what each letter does (Obj 1.6).
- Change which opinion wins by moving it in the stack or across arcs (Obj 1.1).
- Resolve an attribute: time samples, clips, default, schema fallback, then weaker sites.
- Apply a layer offset: `stageTime = offset + scale × sourceTime`.
- Explain how value clips feed samples, and how an authored default hides them.
- Predict ten mixed-arc compositions and name the winning letter.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **LIVERPS** | Strength order of arcs: Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes |
| **Local (L)** | Opinions from the stage's layer stack (session, root, sublayers) |
| **Value resolution** | Picking the composed value of one field at one time |
| **`Usd.ResolveInfo`** | Result of `attr.GetResolveInfo(time)`: which encoding won |
| **Schema fallback** | A schema's built-in default, used only when nothing authored a value |
| **Property stack** | Attribute specs that contribute, strongest first (`GetPropertyStack`) |
| **Layer offset** | `(offset, scale)` remapping source time into stage time |
| **Value clips** | Prim metadata that streams samples from a sequence of files |
| **Winning site** | The composition node (arc + layer stack + path) that supplied the value |

---

## 21.1 LIVERPS spelled out

### 1. What is it?

**LIVERPS** is the strength order of composition arcs. When two arcs both have an opinion about the same field, the earlier letter wins.

### 2. Why do we need it?

A prim can inherit a class, select a variant, relocate a child, reference an asset, load a payload, and specialize a fallback — at once. Without a published order, every DCC would compose a different scene. The exam's largest domain is this order (Obj 1.6).

### 3. Beginner explanation

Read the word as a **queue at a service desk**. Local opinions are at the front. Specializes are at the back. USD asks the queue from the front: the first person who has an answer for this field wins. People who are silent about this field are skipped.

*Where the analogy breaks:* the queue is rebuilt **per prim** and the question is asked **per field**. Also, following a reference starts a *new* queue inside that asset (nested LIVERPS).

### 4. Technical explanation

| Letter | Name | Typical authoring | Stronger than |
|--------|------|-------------------|---------------|
| **L** | Local | Session, root, `subLayers`; nested `over` | I V E R P S |
| **I** | Inherits | `prepend inherits = </_Class>` | V E R P S |
| **V** | VariantSets | `variantSet "lod" = { "high" { … } }` | E R P S |
| **E** | rElocates | Layer metadata `relocates = { </old>: </new> }` | R P S |
| **R** | References | `prepend references = @asset@` | P S |
| **P** | Payloads | `prepend payload = @heavy@` | S |
| **S** | Specializes | `prepend specializes = </_Defaults>` | (nothing) |

- **Local** is not "this one file." It is the whole **layer stack** of the current node: session layer, root, sublayers in order (Chapter 15).
- Relocates do not usually fight a number against a reference; they **move** the referenced prim. Local opinions at the *destination* are still L and beat the moved content (Chapter 20).
- Arcs **nest**. A referenced asset has its own sublayers, inherits, and payloads. USD walks LIVERPS at the referencing site, then walks LIVERPS again inside the referenced layer stack.
- List-editing of arc lists (`prepend` / `append`) changes strength **among arcs of the same letter**, not across letters. Two references: the first prepended is stronger. A reference never beats a local `over` by being prepended.

> [!VERSION] Verified on USD 26.08. The OpenUSD glossary uses **LIVERPS**. Older talks and some NVIDIA study material say **LIVRPS**, which is the same order without relocates. If a question omits E, keep L I V R P S.

> [!EXAM TIP] Composition is 23% of the exam. A question that lists two arcs and two numbers is almost always asking "which letter is earlier?"

### 5. Mental model

```text
 STRONGEST                                                 WEAKEST
  L            I            V            E            R        P        S
 local       inherits    variants    relocates   references payloads specializes
 stack       classes     switches    rename      catalog    lazy      defaults
```

### 6. Simple example

A prim references an asset (`radius = 1`) and inherits a class (`radius = 3`). Composed radius is **3** (I before R). Add a local `radius = 8` and it becomes **8** (L before I).

### 7. USDA example

```usda
#usda 1.0

class Sphere "_Class"
{
    double radius = 3
}

def Sphere "_Defaults"
{
    double radius = 7
}

def "Ball" (
    prepend inherits = </_Class>
    prepend specializes = </_Defaults>
    prepend references = @./asset.usda@
)
{
    double radius = 8
}
```

Line notes: `asset.usda` (not shown) has `radius = 1`. Local 8 wins. Remove the local line and the class's 3 wins. Remove the inherit and the reference's 1 wins. The specializes 7 never wins while any stronger arc has `radius`.

### 8. Python example

```python
from pxr import Usd

with open("asset.usda", "w") as f:
    f.write("""#usda 1.0
(
    defaultPrim = "X"
)
def Sphere "X"
{
    double radius = 1
}
""")
with open("scene.usda", "w") as f:
    f.write("""#usda 1.0
class Sphere "_Class"
{
    double radius = 3
}
def Sphere "_Defaults"
{
    double radius = 7
}
def "Ball" (
    prepend inherits = </_Class>
    prepend specializes = </_Defaults>
    prepend references = @./asset.usda@
)
{
    double radius = 8
}
""")

stage = Usd.Stage.Open("scene.usda")
ball = stage.GetPrimAtPath("/Ball")
print("radius =", ball.GetAttribute("radius").Get())
for arc in Usd.PrimCompositionQuery(ball).GetCompositionArcs():
    print(str(arc.GetArcType()))
```

**Expected output**

```text
radius = 8.0
Pcp.ArcTypeRoot
Pcp.ArcTypeInherit
Pcp.ArcTypeReference
Pcp.ArcTypeSpecialize
```

The query lists contributing arcs in strength order. Root is Local. Variant and relocate arcs are absent here. Radius 8 is the local default on that root node.

### 9. Real-world use case

A film shot: layout's sublayers are L, a `_class_Hero` inherit tints every hero instance (I), an `outfit` variant picks a costume (V), a rig relocate shortens joint paths (E), each hero references `hero.usda` (R), heavy facial shapes sit in a payload (P), and `_HeroFallback` specializes give shader defaults that any of the above may override (S).

### 10. Common mistakes

> [!MISTAKE] Reciting "references then payloads then variants." Variants (V) are stronger than references (R).

> [!MISTAKE] Treating inherits and specializes as the same because both point at a class-like prim. I is near the top; S is last.

### 11. Exam traps

> [!TRAP] "Payloads are weaker than references" is a **strength** statement. It is not about loading. Unloaded payloads contribute nothing; loaded ones still lose to references on the same field.

> [!TRAP] A local empty `over "Ball" {}` does not beat a referenced radius. Local wins only when it **authors that field**.

### 12. Practice questions

**COMP-021a** · Obj 1.6 · Difficulty: Easy · Type: Single choice
Which list is strongest-first?

A. References, Payloads, Local
B. Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes
C. Inherits, Local, Variants
D. Specializes, Payloads, References

**COMP-021b** · Obj 1.6 · Difficulty: Medium · Type: Single choice
A prim has a referenced `radius = 1` and a specializes `radius = 7`. No other opinions. What is composed `radius`?

A. 7
B. 1
C. 8
D. The schema fallback 1, ignoring both

**Answers**

**COMP-021a — B.** LIVERPS. Review: §21.1.

**COMP-021b — B.** R before S. Review: §21.1.

### 13. Exam takeaways

> [!KEY]
> - LIVERPS: Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes.
> - Older spelling LIVRPS omits E; the rest is unchanged.
> - Same-letter lists use prepend/append; letters do not jump the queue.
> - Nested: each referenced asset has its own LIVERPS walk.

---

## 21.2 Strength within a layer stack vs. across arcs

### 1. What is it?

Strength is a **two-step** rank. First USD ranks layers **inside** the current layer stack. Then it ranks that whole stack against other stacks brought in by arcs.

### 2. Why do we need it?

Obj 1.1 is "change the strength of an opinion." You need to know whether to reorder sublayers or to change the arc. Reordering sublayers will not beat a stronger *letter*. Authoring locally will.

### 3. Beginner explanation

A layer stack is a **pile of transparent sheets** (Chapter 3). Arcs are **links to other piles**. USD looks at your pile from the top sheet down (session → root → first sublayer → …). If your pile is silent, it follows a link to another pile, in LIVERPS order, and looks through that pile the same way.

*Where the analogy breaks:* a link can itself have a pile (the referenced file's sublayers). You never flatten the piles unless you call `Flatten`.

### 4. Technical explanation

**Step A — inside one stack** (all of this is letter L for the stage's root node):

1. Session layer (and its sublayers)
2. Root layer
3. `subLayers[0]` and *its* sublayers, depth-first
4. `subLayers[1]` …

**Step B — across arcs:** L, then I, then V, then E, then R, then P, then S. Each of those nodes has its own stack; Step A runs there too.

**How to make an opinion win (Obj 1.1):**

| Goal | Move |
|------|------|
| Beat another department on this shot | Author in a stronger sublayer, or reorder `subLayers` |
| Beat the asset without editing it | Author locally (L) on the composed path |
| Beat a reference with a shared edit | Put the value on an inherited class (I) |
| Beat a payload | Author a reference opinion, or a local opinion |
| See who currently wins | `attr.GetPropertyStack()` (specs, strongest first) and `attr.GetResolveInfo()` |

`GetPropertyStack()` lists `Sdf.AttributeSpec` objects. Silent layers do not appear. The first spec that actually has the encoding you asked for is the winner for that time.

### 5. Mental model

```text
  ask L stack first:  [session] -> [root] -> [sub0] -> [sub1]
                         |           |
                      radius=5    radius=1     --> 5 wins, stop
                      (if session silent, try root, then sublayers)
  if L is silent about this field, ask I, then V, then E, then R, then P, then S
```

### 6. Simple example

Root authors `radius = 1`. Session authors `radius = 5`. Composed value is 5. The asset is not involved. Property stack: session spec first, then root spec.

### 7. USDA example

*File: ball.usda* (root)

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 1
}
```

The session layer is not a file on disk. Python in step 8 authors `radius = 5` there. USDA of the session would look like `over "Ball" { double radius = 5 }`.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateNew("ball.usda")
sph = UsdGeom.Sphere.Define(stage, "/Ball")
sph.GetRadiusAttr().Set(1.0)
stage.SetEditTarget(stage.GetSessionLayer())
sph.GetRadiusAttr().Set(5.0)
attr = stage.GetPrimAtPath("/Ball").GetAttribute("radius")
print("composed radius =", attr.Get())
print("property stack (strongest first):")
for spec in attr.GetPropertyStack():
    print(" ", spec.layer.GetDisplayName(), "default =", spec.default)
ri = attr.GetResolveInfo()
print("ResolveInfo source:", ri.GetSource())
print("node arcType:", ri.GetNode().arcType)
```

**Expected output**

```text
composed radius = 5.0
property stack (strongest first):
  ball-session.usda default = 5.0
  ball.usda default = 1.0
ResolveInfo source: Usd.ResolveInfoSourceDefault
node arcType: Pcp.ArcTypeRoot
```

Both specs are on the **root** (local) node. The session spec is stronger inside that stack. `GetSource()` says the winning encoding is a default value, not time samples.

### 9. Real-world use case

Lighting needs a brighter practical. They do not reorder layout's sublayers (that would reshuffle the whole shot). They author in `shot_lgt.usda`, listed before `shot_lay.usda`, or they author in the session layer for a temporary look. Both are Step A. If the value lives inside the referenced fixture asset, Step A is not enough unless they `over` the fixture locally (Step B: add an L opinion).

### 10. Common mistakes

> [!MISTAKE] Reordering sublayers of the *shot* to override a value that lives only inside a *referenced* asset. Sublayers of the shot are L at the shot's paths. The asset's internal layers sit on the R node. Add a local `over`, or edit the asset.

> [!MISTAKE] Reading `GetPropertyStack()` as "every layer in the stage." Only specs that contribute to **this** property are listed.

### 11. Exam traps

> [!TRAP] "Session layer is an arc." It is the strongest sheet of the **local** stack, not a LIVERPS letter.

> [!TRAP] "First-listed sublayer is weakest." First-listed is strongest (Chapter 15).

### 12. Practice questions

**COMP-021c** · Obj 1.1 · Difficulty: Medium · Type: Single choice
`radius` is authored only inside a referenced asset. Which change makes a new value win **without** editing the asset?

A. Swap two sublayers that do not mention `/Ball`
B. Author `over "Ball" { double radius = 2 }` in the shot
C. Convert the reference to a payload
D. Change `metersPerUnit`

**COMP-021d** · Obj 1.1 · Difficulty: Easy · Type: Single choice
Session has `radius = 5`, root has `radius = 1`. Who wins?

A. Root, because it `def`'d the sphere
B. Session
C. Schema fallback
D. Neither; USD errors

**Answers**

**COMP-021c — B.** That is a local opinion (L), stronger than R. A and D do not author the field. C makes the asset *weaker* (P), but then nothing else has `radius` unless you still author locally. Review: §21.2.

**COMP-021d — B.** Session is the top of the local stack. Review: §21.2.

### 13. Exam takeaways

> [!KEY]
> - Two steps: rank the stack, then rank the arc.
> - Session → root → first sublayer is all Local.
> - `GetPropertyStack()` is strongest-first specs for one property.
> - To beat an asset, author locally; reordering unrelated sublayers will not.

---

## 21.3 Value resolution: defaults, time samples, fallbacks

### 1. What is it?

**Value resolution** is how USD answers `attr.Get(time)` after composition has ranked the specs. It chooses among time samples, value clips, a default, a schema fallback, or "no value."

### 2. Why do we need it?

Two specs can both "win" composition and still disagree about *time*: one has a still default, the other a flip-book of samples. The exam mixes this with LIVERPS (Obj 1.8: "I set a default, why does frame 0 ignore it?").

### 3. Beginner explanation

Composition picks the **ladder**. Value resolution picks which **writing on that ladder's rungs** counts at this moment. A still photograph (default) is used when you ask for the default time, or when nobody shot a flip-book. A flip-book (samples) is used when you ask for a frame number.

*Where the analogy breaks:* if a flip-book exists, asking for a frame **never** falls back to the photograph on that same spec (Chapter 10). Frames before the first sample use the **first sample**, not the default.

### 4. Technical explanation

Verified on USD 26.08. `attr.GetResolveInfo(time).GetSource()` returns one of:

| Source | Meaning |
|--------|---------|
| `ResolveInfoSourceTimeSamples` | Authored samples (interpolated if needed) |
| `ResolveInfoSourceValueClips` | Samples streamed from clips (21.5) |
| `ResolveInfoSourceSpline` | Spline curve (overview only; Ch 10) |
| `ResolveInfoSourceDefault` | Attribute default (`TimeCode.Default()` or no samples) |
| `ResolveInfoSourceFallback` | Schema built-in (Sphere `radius` is 1) |
| `ResolveInfoSourceNone` | No value |

Rules that bite on the exam:

- `Get()` with no time uses the default if one is authored; otherwise it can still return a fallback.
- `Get(numeric)` **ignores the default on a spec that has samples**. Pre-first-sample → first sample. After last sample → last sample. Between samples → linear interpolation unless you `stage.SetInterpolationType(Usd.InterpolationTypeHeld)`.
- Schema fallback is **not an opinion**. It is used only when no contributing spec authored a value. `HasAuthoredValue()` is False; `HasValue()` is True.
- A **value block** (`double radius = None`) is an opinion of "no value" that hides weaker opinions. `Get()` returns `None`.
- Composition strength still comes first. A local default beats referenced samples, because the local spec is a stronger site and it *does* have a value (the default) at numeric times when that spec has no samples of its own.

### 5. Mental model

```text
  for this field, at this time:
    1. walk specs in strength order (stack, then LIVERPS)
    2. on the strongest spec that has a value encoding:
         samples (or clips/spline) if asking at a numeric time
         else default
    3. if nobody authored anything: schema fallback
```

### 6. Simple example

Sphere with fallback only: `Get()` is 1, source `Fallback`. Set default 3: `Get()` is 3, source `Default`. Add a sample 8 at time 10: `Get(Default())` is 3, `Get(0)` is 8 (first sample), `Get(10)` is 8.

### 7. USDA example

```usda
#usda 1.0

def Sphere "HasSamples"
{
    double radius = 2
    double radius.timeSamples = {
        10: 8
    }
}
```

Line notes: both encodings live on one spec. `Get(Usd.TimeCode.Default())` reads `= 2`. Any numeric `Get` reads the sample dictionary.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
empty = UsdGeom.Sphere.Define(stage, "/HasFallback").GetRadiusAttr()
authored = UsdGeom.Sphere.Define(stage, "/HasDefault").GetRadiusAttr()
authored.Set(3.0)
sampled = UsdGeom.Sphere.Define(stage, "/HasSamples").GetRadiusAttr()
sampled.Set(2.0)
sampled.Set(8.0, 10)
print("fallback Get() =", empty.Get(), empty.GetResolveInfo().GetSource())
print("default Get() =", authored.Get(),
      authored.GetResolveInfo().GetSource())
print("samples Default() =", sampled.Get(Usd.TimeCode.Default()),
      sampled.GetResolveInfo(Usd.TimeCode.Default()).GetSource())
print("samples Get(0) =", sampled.Get(0),
      sampled.GetResolveInfo(0).GetSource())
print("samples Get(10) =", sampled.Get(10),
      sampled.GetResolveInfo(10).GetSource())
```

**Expected output**

```text
fallback Get() = 1.0 Usd.ResolveInfoSourceFallback
default Get() = 3.0 Usd.ResolveInfoSourceDefault
samples Default() = 2.0 Usd.ResolveInfoSourceDefault
samples Get(0) = 8.0 Usd.ResolveInfoSourceTimeSamples
samples Get(10) = 8.0 Usd.ResolveInfoSourceTimeSamples
```

`Get(0)` is 8, not 2: numeric queries do not use the default once samples exist.

### 9. Real-world use case

A robot's rest pose is the default. Animation caches write samples. A lighter who keys `radius` (or `xformOp:translate`) as a **default** on a shot overlay wonders why the playback still uses the cache: they asked for frames, so samples on a weaker layer can still lose to a *stronger* default, but a default on the *same* spec as the samples is ignored at those frames. Check `GetResolveInfo(frame).GetSource()` before arguing about LIVERPS.

### 10. Common mistakes

> [!MISTAKE] Assuming `Get(0)` returns the default. If samples exist, you get the first sample (or interpolated value).

> [!MISTAKE] Calling schema fallback an "opinion." `HasAuthoredValue()` is False. You cannot "override the fallback" by reordering sublayers if nobody authored the field — you must author it.

### 11. Exam traps

> [!TRAP] "Defaults always lose to samples, even from a weaker layer." Strength first. A local default beats referenced samples.

> [!TRAP] Sphere `radius` is 1 because "someone authored 1." It is often the fallback. Check `GetResolveInfo().GetSource()`.

### 12. Practice questions

**COMP-021e** · Obj 1.8 · Difficulty: Medium · Type: Single choice
An attribute has default 2 and one sample `{10: 8}`. Interpolation is linear. What is `Get(0)`?

A. 2
B. 8
C. 0
D. 5

**COMP-021f** · Obj 1.8 · Difficulty: Easy · Type: Single choice
`UsdGeom.Sphere.Define` then `GetRadiusAttr().Get()` with nothing else authored. Source is:

A. `ResolveInfoSourceDefault`
B. `ResolveInfoSourceFallback`
C. `ResolveInfoSourceNone`
D. `ResolveInfoSourceTimeSamples`

**Answers**

**COMP-021e — B.** Pre-first-sample uses the first sample. Review: §21.3, Ch 10.

**COMP-021f — B.** Schema fallback; `HasAuthoredValue()` is False. Review: §21.3.

### 13. Exam takeaways

> [!KEY]
> - Strength first, then encoding (samples / clips / default / fallback).
> - Numeric `Get` ignores the default when samples exist on the winning spec.
> - Fallback is not an opinion.
> - `GetResolveInfo(time).GetSource()` names the encoding.

---

## 21.4 Layer offsets in resolution

### 1. What is it?

A **layer offset** remaps time on a sublayer or a reference (or payload): each source time sample is read as if it happened at a different stage time.

### 2. Why do we need it?

Obj 1.4: the same animation, played later or faster, without copying samples. Value resolution must use the **remapped** times, or your hold and your mix will disagree with usdview.

### 3. Beginner explanation

The clip was filmed with its own clapboard. The shot's clapboard is different. Offset is "start this clip later." Scale is "play it faster or slower."

*Where the analogy breaks:* USD does not resample onto integer frames unless you ask. Linear interpolation still runs in **stage** time after the mapping.

### 4. Technical explanation

```text
stageTime = offset + scale × sourceTime
sourceTime = (stageTime − offset) / scale
```

- USDA, on a reference: `@anim.usda@ (offset = 5; scale = 1)`
- USDA, on a sublayer: `subLayers = [@anim.usda@ (offset = 2; scale = 0.5)]`
- Python: `Sdf.LayerOffset(offset, scale)` on `AddReference`, or `layer.subLayerOffsets` (parallel to `subLayerPaths`).
- Defaults (non-time) are **not** moved. Offsets only affect time samples (and clips/splines).
- Before the first remapped sample, `Get(t)` uses the first sample's **value** (same pre-first rule as Chapter 10).
- `scale = 0.5` plays the source at **half speed** in stage time (source 10 occupies 5 stage units after the offset).

### 5. Mental model

```text
  source samples:  t=0 -> 0    t=10 -> 10
  offset=2, scale=0.5

  appear on stage: t=2 -> 0    t=7 -> 10
  stage t=4  -> source t=4  -> value 4  (linear)
```

### 6. Simple example

Sublayer `anim.usda` with samples 0→0 and 10→10, listed as `@anim.usda@ (offset = 2; scale = 0.5)`. `Get(2)` is 0, `Get(7)` is 10, `Get(4)` is 4.

### 7. USDA example

*File: anim.usda*

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius.timeSamples = {
        0: 0,
        10: 10
    }
}
```

*File: shot.usda*

```usda
#usda 1.0
(
    subLayers = [
        @./anim.usda@ (offset = 2; scale = 0.5)
    ]
)
```

Line notes: the offset is on the **sublayer entry**, not on the prim. Semicolon separates `offset` and `scale` inside those parentheses.

### 8. Python example

```python
from pxr import Usd

def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("anim.usda", """#usda 1.0
def Sphere "Ball"
{
    double radius.timeSamples = {
        0: 0,
        10: 10
    }
}
""")
write("shot.usda", """#usda 1.0
(
    subLayers = [
        @./anim.usda@ (offset = 2; scale = 0.5)
    ]
)
""")

stage = Usd.Stage.Open("shot.usda")
attr = stage.GetPrimAtPath("/Ball").GetAttribute("radius")
print("subLayerOffsets =", stage.GetRootLayer().subLayerOffsets)
for t in (0, 2, 4, 7):
    print(f"Get({t}) =", attr.Get(t))
```

**Expected output**

```text
subLayerOffsets = [Sdf.LayerOffset(2, 0.5)]
Get(0) = 0.0
Get(2) = 0.0
Get(4) = 4.0
Get(7) = 10.0
```

`Get(0)` is still 0: time 0 is before the first remapped sample (which sits at 2), so USD holds the first sample's value.

### 9. Real-world use case

A factory-line digital twin reuses `robot_cycle.usda` at three stations. Station B's reference uses `offset = 24` so the cycle starts one second later (at 24 fps). Same samples, different stage times (Obj 1.4, Lab 14).

### 10. Common mistakes

> [!MISTAKE] Using `stageTime = sourceTime + offset` and forgetting `scale`. The full formula multiplies first.

> [!MISTAKE] Expecting `scale = 2` to mean "twice as long." `scale = 2` maps source 1 to a +2 stage step: the clip plays **faster** (twice the speed) if you think in "stage seconds per source second."

### 11. Exam traps

> [!TRAP] Offsets on sublayers versus references look different in USDA but use the same `Sdf.LayerOffset` math.

> [!TRAP] "Offset moves the default pose." Defaults are unvarying; only samples move.

### 12. Practice questions

**COMP-021g** · Obj 1.4 · Difficulty: Medium · Type: Single choice
A reference has `(offset = 5; scale = 1)`. The asset's sample at source 0 is `radius = 1`. At which stage time does that sample appear?

A. −5
B. 0
C. 5
D. 1

**COMP-021h** · Obj 1.4 · Difficulty: Medium · Type: Single choice
`Sdf.LayerOffset(2, 0.5)` on samples at 0 and 10. What is `Get(7)` (linear)?

A. 0
B. 5
C. 10
D. 7

**Answers**

**COMP-021g — C.** `5 + 1 × 0 = 5`. Review: §21.4.

**COMP-021h — C.** Source time at stage 7 is `(7 − 2) / 0.5 = 10`, the last sample. Review: §21.4.

### 13. Exam takeaways

> [!KEY]
> - `stageTime = offset + scale × sourceTime`.
> - Same struct on sublayers and on references.
> - Defaults do not shift; samples do.
> - Pre-first remapped sample still uses the first sample's value.

---

## 21.5 Value clips in resolution

### 1. What is it?

**Value clips** are prim metadata that tell USD to pull time samples from a **sequence of other files** instead of storing every sample on the prim. Resolution can then report `ResolveInfoSourceValueClips`.

### 2. Why do we need it?

A 10 000-frame cache in one layer is slow to open and huge to version. Clips keep each chunk (or each frame) in its own file and activate them over time. Chapter 10 introduced the idea; this section is how they lose or win during `Get(time)`.

### 3. Beginner explanation

Think of a **shelf of tape reels**. Each reel is a small USD file with a few samples. A card on the shelf (`clips` metadata) says which reel is in the machine at each shot time.

*Where the analogy breaks:* clips are not a LIVERPS letter. They are a **value encoding** on whatever site already won composition. An authored **default** on that same prim hides the reels.

### 4. Technical explanation

Verified on USD 26.08:

- Author with `Usd.ClipsAPI(prim)`: `SetClipAssetPaths`, `SetClipPrimPath`, `SetClipActive`, `SetClipTimes`. USDA stores a `clips` dictionary on the prim.
- `active` pairs `(stageTime, clipIndex)` pick which clip file is current. `times` pairs map stage time to time-inside-the-clip.
- `Get(time)` interpolates across clip boundaries when interpolation is linear (clip1 value 1 at t=0, clip2 value 5 at t=10 → t=5 is 3).
- **An authored default on that attribute blocks clips** at every time, including numeric times. `GetResolveInfo` then says `Default`. Local time samples also beat clips.
- Clips are metadata, not an arc. Strength of the *prim site* still follows LIVERPS. A local default (L) hides clips on that prim; removing the default lets clips show through.

> [!VERSION] Splines: Ts library 24.03 (not yet used by USD attributes); `UsdAttribute` resolution / `ResolveInfoSourceSpline` 25.05; Get/SetSpline APIs 25.08. The exam's core encodings remain samples, defaults, and clips-at-overview.

### 5. Mental model

```text
  Get(t) encodings on the winning spec, strongest first:
    authored time samples  >  clips  >  default  >  schema fallback

  (numeric t ignores default when samples exist; default still hides clips)
```

### 6. Simple example

Two clip files, `radius` 1 and 5. Active switches at 0 and 10. `Get(0)=1`, `Get(10)=5`, `Get(5)=3`. Set `radius = 9` on the prim and `Get(5)` becomes 9.

### 7. USDA example

```usda
#usda 1.0

def Sphere "Ball" (
    clips = {
        dictionary default = {
            double2[] active = [(0, 0), (10, 1)]
            asset[] assetPaths = [@./clip1.usda@, @./clip2.usda@]
            string primPath = "/Ball"
            double2[] times = [(0, 0), (10, 0)]
        }
    }
)
{
}
```

Line notes: `primPath` is the path **inside each clip file**. `assetPaths` is the ordered reel list. Keep the attribute itself empty if you want the clips to win.

### 8. Python example

```python
from pxr import Usd, UsdGeom

def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("clip1.usda", """#usda 1.0
def Sphere "Ball"
{
    double radius.timeSamples = {
        0: 1
    }
}
""")
write("clip2.usda", """#usda 1.0
def Sphere "Ball"
{
    double radius.timeSamples = {
        0: 5
    }
}
""")

stage = Usd.Stage.CreateNew("clips.usda")
ball = UsdGeom.Sphere.Define(stage, "/Ball")
api = Usd.ClipsAPI(ball)
api.SetClipAssetPaths(["./clip1.usda", "./clip2.usda"])
api.SetClipPrimPath("/Ball")
api.SetClipActive([(0.0, 0.0), (10.0, 1.0)])
api.SetClipTimes([(0.0, 0.0), (10.0, 0.0)])
attr = ball.GetRadiusAttr()
for t in (0, 5, 10):
    print(f"clip Get({t}) =", attr.Get(t),
          attr.GetResolveInfo(t).GetSource())
attr.Set(9.0)
print("after default 9, Get(5) =", attr.Get(5),
      attr.GetResolveInfo(5).GetSource())
```

**Expected output**

```text
clip Get(0) = 1.0 Usd.ResolveInfoSourceValueClips
clip Get(5) = 3.0 Usd.ResolveInfoSourceValueClips
clip Get(10) = 5.0 Usd.ResolveInfoSourceValueClips
after default 9, Get(5) = 9.0 Usd.ResolveInfoSourceDefault
```

### 9. Real-world use case

A VFX cache department publishes `hero_sim.####.usd` as clips on `/Hero`. Lighting never authors a default `xformOp:translate` on that prim; if they did, the whole sim would freeze at the default pose.

### 10. Common mistakes

> [!MISTAKE] Defining the prim with `double radius = 1` "so it has a rest pose" **and** attaching clips. The rest pose hides the clips. Leave the attribute unauthored, or author samples.

> [!MISTAKE] Thinking clips are weaker than payloads. Clips are not an arc.

### 11. Exam traps

> [!TRAP] "`Get(5)` with clips interpolates unless a default exists." A default on that attribute stops clip resolution entirely.

> [!TRAP] "Clips are the C in LIVERPS." There is no C. Encodings ≠ arcs.

### 12. Practice questions

**COMP-021i** · Obj 1.8 · Difficulty: Medium · Type: Single choice
A prim has clips that would give `radius = 3` at t=5, and also `double radius = 9`. What is `Get(5)`?

A. 3, source ValueClips
B. 9, source Default
C. 6 (average)
D. Schema fallback 1

**COMP-021j** · Obj 1.6 · Difficulty: Easy · Type: Single choice
Value clips are:

A. The C arc in LIVERPS
B. A value encoding that streams samples from other files
C. A kind of payload
D. Stronger than local opinions

**Answers**

**COMP-021i — B.** Authored default hides clips. Review: §21.5.

**COMP-021j — B.** Review: §21.5.

### 13. Exam takeaways

> [!KEY]
> - Clips stream samples; `GetResolveInfo` can say `ValueClips`.
> - They are an encoding, not a LIVERPS letter.
> - Authored defaults (and local samples) hide clips.
> - Leave clip-driven attributes unauthored on the prim.

---

## 21.6 Ten worked LIVERPS puzzles

### 1. What is it?

Ten small compositions. For each one you predict the composed value, then check it. This is the exam format: USDA in, number out, letter as the reason.

### 2. Why do we need it?

Isolated chapters make each arc look easy. The exam stacks them. Working the set until the letter comes to mind before the number is the study method for Days 6–7.

### 3. Beginner explanation

Each puzzle is a **who-speaks-loudest** contest. Write the letters that are present, drop the ones that are silent about the field, and keep the earliest letter's number.

*Where the analogy breaks:* P6's payload still contributes `extra`, which the reference never mentioned. Weaker arcs can fill fields the stronger arc left blank.

### 4. Technical explanation

Use this checklist on every puzzle:

1. Which arcs are present? Write L I V E R P S and cross out missing ones.
2. Which of those authored **this field**?
3. Earliest remaining letter wins.
4. If the winner has samples or clips, apply Chapter 10 / 21.3–21.5 at the requested time.
5. If you authored at a relocation **source**, that opinion does not count (Chapter 20).

### 5. Mental model

```text
  present:  L  I  V  E  R  P  S
  has field:    I        R
  winner: I
```

### 6. Simple example

The table below is the answer key. Step 8 produces it from files.

| # | Contest | Winner | Value |
|---|---------|--------|-------|
| P1 | Local 2 vs reference 1 | L | 2 |
| P2 | Sublayer first-listed 5 vs second 9 | L (order) | 5 |
| P3 | Inherit 3 vs reference 1 | I | 3 |
| P4 | Local 8 vs inherit 3 | L | 8 |
| P5 | Variant 10 vs reference 1 | V | 10 |
| P6 | Reference 1 vs payload 9; payload `extra` | R for radius; P for extra | 1 and 1 |
| P7 | Specialize 7 vs reference 1 | R | 1 |
| P8 | Dest `over` 4 on a relocated arm | L at dest | 4 |
| P9 | Default 2, sample `{10: 8}`, `Get(0)` | samples | 8 |
| P10 | Reference offset 5, samples 0→1 and 10→11 | offset math | t=5 → 1, t=10 → 6, t=15 → 11 |

### 7. USDA example

*P1 — local beats reference*

```usda
#usda 1.0

def "Ball" (
    prepend references = @./asset.usda@
)
{
    double radius = 2
}
```

*P7 — reference beats specializes*

```usda
#usda 1.0

def Sphere "_D"
{
    double radius = 7
}

def "Ball" (
    prepend specializes = </_D>
    prepend references = @./asset.usda@
)
{
}
```

`asset.usda` defines `Sphere "X"` with `radius = 1` and `defaultPrim = "X"`. P1 composes to 2. P7 composes to 1.

### 8. Python example

```python
from pxr import Usd, UsdGeom

def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("asset.usda", """#usda 1.0
(
    defaultPrim = "X"
)
def Sphere "X"
{
    double radius = 1
}
""")
write("pay.usda", """#usda 1.0
(
    defaultPrim = "X"
)
def Sphere "X"
{
    double radius = 9
    double extra = 1
}
""")
write("s1.usda", """#usda 1.0
over "Ball"
{
    double radius = 5
}
""")
write("s2.usda", """#usda 1.0
def Sphere "Ball"
{
    double radius = 9
}
""")
write("robot.usda", """#usda 1.0
(
    defaultPrim = "Robot"
)
def Xform "Robot"
{
    def Xform "Rig"
    {
        def Sphere "Arm"
        {
            double radius = 1
        }
    }
}
""")
write("anim.usda", """#usda 1.0
(
    defaultPrim = "Ball"
)
def Sphere "Ball"
{
    double radius.timeSamples = {
        0: 1,
        10: 11
    }
}
""")

write("p1.usda", """#usda 1.0
def "Ball" (
    prepend references = @./asset.usda@
)
{
    double radius = 2
}
""")
st = Usd.Stage.Open("p1.usda")
print("P1 L>R", st.GetPrimAtPath("/Ball").GetAttribute("radius").Get())

write("p2.usda", """#usda 1.0
(
    subLayers = [@./s1.usda@, @./s2.usda@]
)
""")
st = Usd.Stage.Open("p2.usda")
print("P2 sublayer-first",
      st.GetPrimAtPath("/Ball").GetAttribute("radius").Get())

write("p3.usda", """#usda 1.0
class Sphere "_C"
{
    double radius = 3
}
def "Ball" (
    prepend inherits = </_C>
    prepend references = @./asset.usda@
)
{
}
""")
st = Usd.Stage.Open("p3.usda")
print("P3 I>R", st.GetPrimAtPath("/Ball").GetAttribute("radius").Get())

write("p4.usda", """#usda 1.0
class Sphere "_C"
{
    double radius = 3
}
def Sphere "Ball" (
    prepend inherits = </_C>
)
{
    double radius = 8
}
""")
st = Usd.Stage.Open("p4.usda")
print("P4 L>I", st.GetPrimAtPath("/Ball").GetAttribute("radius").Get())

write("p5.usda", """#usda 1.0
def "Ball" (
    prepend references = @./asset.usda@
    prepend variantSets = "size"
    variants = {
        string size = "big"
    }
)
{
    variantSet "size" = {
        "big" {
            double radius = 10
        }
        "small" {
            double radius = 0.2
        }
    }
}
""")
st = Usd.Stage.Open("p5.usda")
print("P5 V>R", st.GetPrimAtPath("/Ball").GetAttribute("radius").Get())

write("p6.usda", """#usda 1.0
def "Ball" (
    prepend references = @./asset.usda@
    prepend payload = @./pay.usda@
)
{
}
""")
st = Usd.Stage.Open("p6.usda")
b = st.GetPrimAtPath("/Ball")
print("P6 R>P", b.GetAttribute("radius").Get(),
      "extra", b.GetAttribute("extra").Get())

write("p7.usda", """#usda 1.0
def Sphere "_D"
{
    double radius = 7
}
def "Ball" (
    prepend specializes = </_D>
    prepend references = @./asset.usda@
)
{
}
""")
st = Usd.Stage.Open("p7.usda")
print("P7 R>S", st.GetPrimAtPath("/Ball").GetAttribute("radius").Get())

write("p8.usda", """#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)
def Xform "Bot" (
    prepend references = @./robot.usda@
)
{
    over "Arm"
    {
        double radius = 4
    }
}
""")
st = Usd.Stage.Open("p8.usda")
print("P8 L-at-dest>E",
      st.GetPrimAtPath("/Bot/Arm").GetAttribute("radius").Get())

st = Usd.Stage.CreateInMemory()
a = UsdGeom.Sphere.Define(st, "/S").GetRadiusAttr()
a.Set(2.0)
a.Set(8.0, 10)
print("P9 Default", a.Get(Usd.TimeCode.Default()),
      "Get(0)", a.Get(0),
      a.GetResolveInfo(0).GetSource())

write("p10.usda", """#usda 1.0
def "Ball" (
    prepend references = @./anim.usda@ (
        offset = 5
        scale = 1
    )
)
{
}
""")
st = Usd.Stage.Open("p10.usda")
a = st.GetPrimAtPath("/Ball").GetAttribute("radius")
print("P10 t=5", a.Get(5), "t=10", a.Get(10), "t=15", a.Get(15))
```

**Expected output**

```text
P1 L>R 2.0
P2 sublayer-first 5.0
P3 I>R 3.0
P4 L>I 8.0
P5 V>R 10.0
P6 R>P 1.0 extra 1.0
P7 R>S 1.0
P8 L-at-dest>E 4.0
P9 Default 2.0 Get(0) 8.0 Usd.ResolveInfoSourceTimeSamples
P10 t=5 1.0 t=10 6.0 t=15 11.0
```

P10 check: source 0 appears at stage 5 (value 1). Source 10 appears at stage 15 (value 11). Stage 10 → source 5 → linear halfway from 1 to 11 = 6.

### 9. Real-world use case

A lead lighting TD debugs a "wrong roughness" ticket by walking this table: is it a local light-tweak (L), a class broadcast (I), an outfit variant (V), a referenced material (R), or a specialized fallback (S)? Naming the letter tells them which file to open.

### 10. Common mistakes

> [!MISTAKE] Adding the two radii. Composition does not sum. One winner.

> [!MISTAKE] In P6, concluding the payload is unused because radius came from the reference. `extra` still comes from the payload.

### 11. Exam traps

> [!TRAP] P7 looks like "class-like prim, so 7." Specializes is the weakest letter.

> [!TRAP] P9 looks like LIVERPS. It is value resolution on one spec: numeric time ignores the default.

### 12. Practice questions

**COMP-021k** · Obj 1.6 · Difficulty: Hard · Type: Single choice
A prim inherits `radius = 3`, references `radius = 1`, and specializes `radius = 7`. No local opinion. Composed radius?

A. 3
B. 1
C. 7
D. 11

**COMP-021l** · Obj 1.8 · Difficulty: Medium · Type: Select two.
Which statements about P6 (reference radius 1, payload radius 9 and extra 1) are true?

A. Composed `radius` is 1
B. Composed `radius` is 9
C. Composed `extra` is 1
D. Unloading the payload changes `radius`

**Answers**

**COMP-021k — A.** I before R before S. Review: §21.1, P3/P7.

**COMP-021l — A and C.** R wins `radius`; `extra` only exists on P. Unloading drops `extra` but not the referenced `radius`. Review: P6, Ch 17.

### 13. Exam takeaways

> [!KEY]
> - Cross out silent letters; the earliest remaining letter wins.
> - Weaker arcs may still fill other fields.
> - Relocate puzzles: author at the destination (L).
> - Not every "wrong value" is LIVERPS; check samples vs default vs offset vs clips.

---

## Chapter lab(s)

Lab 20 (LIVERPS laboratory) is the practice set for this chapter: predict, then run. Lab 14 drills layer offsets. Lab 21 prints stacks and `PrimCompositionQuery`.

## USDA reading exercises

**Exercise 21-A.** `asset.usda` has `radius = 1`. The shot is:

```usda
#usda 1.0

class Sphere "_C"
{
    double radius = 3
}

def "Ball" (
    prepend inherits = </_C>
    prepend references = @./asset.usda@
)
{
}
```

What is `/Ball.radius`, and which letter won?

**Exercise 21-B.** Same asset. A reference uses `(offset = 5; scale = 1)`. Samples in the asset are `{0: 1, 10: 11}`. What is `Get(10)`?

**Answers**

**21-A.** `3`, letter **I**. Verified as P3.

**21-B.** `6`. Source time = 10 − 5 = 5, halfway from 1 to 11. Verified as P10.

---

## Chapter review

### Summary

- LIVERPS is strongest-to-weakest: Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes.
- Strength is two steps: rank the layer stack, then rank the arc. Nested assets repeat the walk.
- Change strength (Obj 1.1) by authoring in a stronger site, reordering sublayers, or changing the arc — not by a priority number.
- Value resolution: samples/clips/spline, then default, then schema fallback. Numeric `Get` ignores the default when samples exist.
- Layer offset: `stageTime = offset + scale × sourceTime`.
- Clips are an encoding. An authored default hides them.
- Ten puzzles: L>R, sublayer order, I>R, L>I, V>R, R>P, R>S, L-at-relocate-dest, samples vs default, offset math.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Two arcs, two numbers | Earliest LIVERPS letter |
| "Change who wins" | Stronger layer, reorder sublayers, or stronger arc (Obj 1.1) |
| `GetPropertyStack()` | Strongest-first specs for one property |
| `GetResolveInfo().GetSource()` | Encoding: samples / clips / default / fallback |
| `Get(0)` ≠ default | Samples exist; pre-first uses first sample |
| Sphere radius 1, nothing authored | Fallback, not an opinion |
| `(offset = a; scale = b)` | stage = a + b × source |
| Clips plus `double x = 9` | Default hides clips |
| LIVRPS in a question | Same order, no relocates |
| Payload and reference both set `x` | Reference wins; other payload fields may still show |

### Review questions

**R21-01** · Obj 1.6 · Single choice
The E in LIVERPS stands for:
A. Edits · B. rElocates · C. Extents · D. Export

**R21-02** · Obj 1.6 · Single choice
Which pair is in the correct strength order (stronger first)?
A. Payloads, References · B. Specializes, Inherits
C. VariantSets, References · D. References, Local

**R21-03** · Obj 1.1 · Single choice
The only `radius` opinion lives in a referenced asset. Fastest way to override it in the shot?
A. Mute the root layer
B. Local `over` of `radius` on the referencing prim
C. Change `defaultPrim`
D. Convert USDA to USDC

**R21-04** · Obj 1.1 · Single choice
`subLayers = [@a.usda@, @b.usda@]`. `a` has radius 5, `b` has 9. Composed radius?
A. 9 · B. 5 · C. 14 · D. fallback 1

**R21-05** · Obj 1.8 · Single choice
Default 2, samples `{10: 8}`. `Get(Usd.TimeCode.Default())` is:
A. 8 · B. 2 · C. 5 · D. None

**R21-06** · Obj 1.8 · Single choice
Same attribute. `Get(0)` is:
A. 2 · B. 8 · C. 0 · D. fallback 1

**R21-07** · Obj 1.4 · Single choice
Reference offset 5, scale 1, source sample at 0 equals 1. `Get(5)` is:
A. 1 · B. 5 · C. no value · D. 0

**R21-08** · Obj 1.6 · Select two.
A prim references `radius = 1` and payloads `radius = 9` plus `extra = 1`. Which are true?
A. `radius` is 1
B. `radius` is 9
C. `extra` is 1
D. Specializes would beat the reference

**R21-09** · Obj 1.8 · Single choice
Clips would give 3 at t=5. The prim also authors `double radius = 9`. `Get(5)` is:
A. 3 · B. 9 · C. 6 · D. 1

**R21-10** · Obj 1.6 · Single choice
Inherit 3, specialize 7, no other opinions. Composed radius?
A. 3 · B. 7 · C. 10 · D. fallback

**R21-11** · Obj 1.8 · Single choice
You relocated `/Bot/Rig/Arm` to `/Bot/Arm` and keyed `/Bot/Rig/Arm.radius`. Why is the value unchanged?
A. References beat local
B. The opinion is at the relocation source, so it is ignored
C. Radius is a schema fallback and cannot be authored
D. Relocates are weaker than payloads

**R21-12** · Obj 1.1 · Single choice
`GetResolveInfo().GetNode().arcType` is `Pcp.ArcTypeRoot` and the session spec is first in `GetPropertyStack()`. Who won?
A. A reference
B. Local stack (session over root)
C. Specializes
D. Value clips as an arc

### Review answers

**R21-01 — B.** rElocates. Review: §21.1.

**R21-02 — C.** V before R. Review: §21.1.

**R21-03 — B.** Add an L opinion. Review: §21.2.

**R21-04 — B.** First-listed sublayer is stronger. Review: §21.2, P2.

**R21-05 — B.** Default time reads the default. Review: §21.3.

**R21-06 — B.** Pre-first sample. Review: §21.3, P9.

**R21-07 — A.** Source 0 maps to stage 5. Review: §21.4, P10.

**R21-08 — A and C.** R wins `radius`; `extra` from P. Review: P6.

**R21-09 — B.** Default hides clips. Review: §21.5.

**R21-10 — A.** I before S. Review: §21.1.

**R21-11 — B.** Chapter 20 + P8. Review: §21.6.

**R21-12 — B.** Root node = local; session is strongest in that stack. Review: §21.2.

## Further reading

- [S04] OpenUSD Glossary — "LIVERPS Strength Ordering", "Value Resolution", "Layer Offset", "Value Clips": https://openusd.org/release/glossary.html
- [S06] OpenUSD API — `UsdAttribute::GetResolveInfo`, `UsdClipsAPI`, `SdfLayerOffset`: https://openusd.org/release/api/index.html
- [S14] NVIDIA Learn OpenUSD — Composition and LIVERPS: https://docs.nvidia.com/learn-openusd/latest/index.html
- [S11] Maximizing USD Performance — clips and payloads: https://openusd.org/release/maxperf.html
