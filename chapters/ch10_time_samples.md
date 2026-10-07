# Chapter 10 — Time Samples and Animation Data

> **Exam domain:** Data Modeling (13%) and Composition · **Objectives:** 1.4, 5.2
> **Study day:** 3 · **Est. time:** 90 min
> **Prerequisites:** Chapters 2, 5, 9

## Learning goals

- Distinguish a **default value** from **time samples**.
- Query with `Usd.TimeCode` and `Usd.TimeCode.Default()`.
- Read and set stage time metadata (`timeCodesPerSecond`, frame range).
- Predict **held** vs **linear** interpolation.
- Explain **layer offsets** well enough for Obj 1.4 (same clip, different times).
- Know what **value clips** and **splines** are, without treating them as the exam's main animation encoding.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Default value | The attribute value at `TimeCode.Default()` — not a frame |
| Time sample | A value authored at a numeric time code |
| TimeCode | USD's time type (`Usd.TimeCode`) |
| Interpolation | How values between samples are computed: linear (default) or held |
| Layer offset | `offset` and `scale` that remap a layer's time into the referencing/sublayering stage |
| Value clips | Metadata that streams animation from a sequence of files |
| Spline | Newer curve encoding on attributes (USD 24.03+; not the exam's core) |

---

## 10.1 Default value vs. time samples

### 1. What is it?

An attribute can hold a **default** (one value, "unvarying in time") and/or **time samples** (a dictionary of time → value).

### 2. Why do we need it?

Static assets use defaults. Animation uses samples. Mixing them wrongly is a classic "why doesn't my pose move?" bug.

### 3. Beginner explanation

Default = the still photograph. Time samples = the flip-book. If you ask "what does this look like as a still?" you get the photo. If you ask "what about frame 10?" you get the flip-book.

Where the analogy breaks: numeric time queries **do not use the default**. The default is only for `Default()` time. Frames before the first sample use the **first sample**, not the default. Verified on USD 26.08.

### 4. Technical explanation

- USDA default: `double radius = 2`
- USDA samples: `double radius.timeSamples = { 1: 1, 11: 5, }`
- `attr.Set(2.0)` authors the default. `attr.Set(5.0, 10)` authors a sample at time 10.
- `attr.Get()` with no time = `Get(Usd.TimeCode.Default())`.
- If there is **no authored default**, `Get()` returns the schema **fallback** (Sphere radius → `1.0`) or `None` (no fallback, e.g. a translate op).
- `GetNumTimeSamples()`, `GetTimeSamples()`.

### 5. Mental model

```text
Get(Default)  -->  authored default, else schema fallback, else None
Get(frame)    -->  time samples only (ignore default)
```

### 6. Simple example

Radius default 1, sample at 10 of 5: `Get()` is 1; `Get(10)` is 5; `Get(1)` is 5 (first sample, because 1 is before 10).

### 7. USDA example

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 1
    double radius.timeSamples = {
        10: 5,
        20: 9,
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
ball = UsdGeom.Sphere.Define(stage, "/Ball")
radius = ball.GetRadiusAttr()
radius.Set(1.0)
radius.Set(5.0, 10)
radius.Set(9.0, 20)
print("samples:", radius.GetTimeSamples())
print("Get() / Default:", radius.Get(), radius.Get(Usd.TimeCode.Default()))
print("Get(0):", radius.Get(0))
print("Get(10):", radius.Get(10))
print("Get(15):", radius.Get(15))
print("Get(20):", radius.Get(20))
print("Get(100):", radius.Get(100))
```

**Expected output**

```text
samples: [10.0, 20.0]
Get() / Default: 1.0 1.0
Get(0): 5.0
Get(10): 5.0
Get(15): 7.0
Get(20): 9.0
Get(100): 9.0
```

`Get(15)` is 7 because the stage default interpolation is **linear**.

### 9. Real-world use case

A character's rest pose is the default. Shot animation is samples. Tools that forget to pass a time code show the rest pose even though curves exist.

### 10. Common mistakes

> [!MISTAKE] Calling `Get()` in a playback loop and wondering why the value never changes. Pass the frame: `Get(timecode)`.

> [!MISTAKE] Expecting the default to fill times before the first sample. It does not.

### 11. Exam traps

> [!TRAP] "Default is frame 0." Default is a **special time**, not zero. `Usd.TimeCode.Default()` prints `DEFAULT`.

### 12. Practice questions

**DM-013** · Obj 5.2 · Difficulty: Medium · Type: Single choice

An attribute has default 2 and a sample at time 10 of 8. What does `Get(0)` return (linear interpolation, no other samples)?

A. 2  
B. 8  
C. 0  
D. None  

**Answer:** B. Numeric times use samples; time 0 is before the first sample, so the first sample (8) is used.

### 13. Exam takeaways

> [!KEY]
> - Default ≠ frame 0.
> - `Get()` without a time is Default time.
> - Playback must pass a numeric TimeCode.

---

## 10.2 Usd.TimeCode and Default()

### 1. What is it?

`Usd.TimeCode` is USD's time value. Two special values: **Default** and **EarliestTime**.

### 2. Why do we need it?

Every animated `Get`/`Set`/`Compute` takes a TimeCode. Mixing "frame 1" with Default is how extents and bounds go stale (Obj 5.6, Ch 13).

### 3. Beginner explanation

A TimeCode is a bookmark in the shot's timeline — unless it is Default, which means "the still / non-animated value."

### 4. Technical explanation

- `Usd.TimeCode(10)` — numeric.
- `Usd.TimeCode.Default()` — the default-value time. `IsDefault()` is True.
- `Usd.TimeCode.EarliestTime()` — lower than any numeric time; used when resolving "the first opinion in time."
- Many APIs accept a raw float/`int` as time; it is converted to a TimeCode.
- `TimeCode` is **not** a Python `float` (`float(Usd.TimeCode(1))` TypeErrors). Use `.GetValue()` if you need the number.

### 5. Mental model

```text
EARLIEST  ...  1  2  3 ...  N     and separately: DEFAULT
```

### 6. Simple example

`bboxCache = UsdGeom.BBoxCache(Usd.TimeCode(101), ...)` computes bounds at the shot frame, not at Default.

### 7. USDA example

TimeCodes appear as keys in `.timeSamples` blocks (they are just numbers in the file):

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius.timeSamples = {
        1001: 1,
        1100: 2,
    }
}
```

### 8. Python example

```python
from pxr import Usd

d = Usd.TimeCode.Default()
t = Usd.TimeCode(1001)
print("Default:", d, "IsDefault:", d.IsDefault())
print("numeric:", t, "IsDefault:", t.IsDefault(), "GetValue:", t.GetValue())
print("Earliest:", Usd.TimeCode.EarliestTime())
```

**Expected output**

```text
Default: DEFAULT IsDefault: True
numeric: 1001 IsDefault: False GetValue: 1001.0
Earliest: EARLIEST
```

### 9. Real-world use case

Shot start 1001, end 1100. All animation APIs in that show pass 1001–1100, never Default, during playback.

### 10. Common mistakes

> [!MISTAKE] `float(timeCode)` — use `timeCode.GetValue()`.

### 11. Exam traps

> [!TRAP] "EarliestTime is frame 0." It is a sentinel, weaker/earlier than any number.

### 12. Practice questions

**DM-014** · Difficulty: Easy · Type: Single choice

`Usd.TimeCode.Default()` means:

A. Frame 0  
B. The special default-value time, not a frame  
C. 24 fps  
D. The session layer  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Default is a sentinel. Numeric TimeCodes are frames (in whatever unit `timeCodesPerSecond` defines).

---

## 10.3 Stage time metadata

### 1. What is it?

The root layer stores `timeCodesPerSecond`, `framesPerSecond`, `startTimeCode`, `endTimeCode`.

### 2. Why do we need it?

So every tool agrees how to map TimeCodes to seconds and which range the shot covers.

### 3. Beginner explanation

The slate on the film can: 24 fps, frames 1001–1100.

### 4. Technical explanation

Verified defaults on a new stage in USD 26.08: **tps = 24, fps = 24, start = 0, end = 0**.

- `timeCodesPerSecond` converts TimeCodes to seconds: `seconds = timeCode / tps`.
- `framesPerSecond` is a hint for UIs; it can differ from tps in some pipelines (not common).
- These fields do **not** by themselves play animation. They label the stage.

### 5. Mental model

Header metadata = intended playback; samples = actual motion.

### 6. Simple example

A 48 fps capture might set tps=48. Layer offsets (next) still work in TimeCodes, not seconds.

### 7. USDA example

```usda
#usda 1.0
(
    startTimeCode = 1001
    endTimeCode = 1100
    timeCodesPerSecond = 24
    framesPerSecond = 24
)

def Xform "World"
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
print("defaults tps/fps/start/end:",
      stage.GetTimeCodesPerSecond(),
      stage.GetFramesPerSecond(),
      stage.GetStartTimeCode(),
      stage.GetEndTimeCode())
stage.SetTimeCodesPerSecond(24)
stage.SetFramesPerSecond(24)
stage.SetStartTimeCode(1001)
stage.SetEndTimeCode(1100)
UsdGeom.Xform.Define(stage, "/World")
print("range:", stage.GetStartTimeCode(), stage.GetEndTimeCode())
```

**Expected output**

```text
defaults tps/fps/start/end: 24.0 24.0 0.0 0.0
range: 1001.0 1100.0
```

### 9. Real-world use case

A conform tool refuses to publish a shot whose last animation sample is past `endTimeCode` — pipeline policy, not a USD error.

### 10. Common mistakes

> [!MISTAKE] Setting only fps and assuming samples are resampled. USD does not resample because you changed metadata.

### 11. Exam traps

> [!TRAP] "startTimeCode defaults to 1001." It defaults to 0 on a new stage.

### 12. Practice questions

**DM-015** · Difficulty: Easy · Type: Single choice

Changing `timeCodesPerSecond` from 24 to 48:

A. Automatically doubles all sample times  
B. Relabels how TimeCodes map to seconds; samples stay at the same TimeCodes  
C. Deletes animation  
D. Converts USDC to USDA  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Defaults: 24 tps / 24 fps / start 0 / end 0.
> - Metadata labels time; it does not rewrite samples.

---

## 10.4 Interpolation: held vs linear

### 1. What is it?

**Interpolation** fills in values *between* samples. A stage has one interpolation type: **linear** (default) or **held**.

### 2. Why do we need it?

Stepped animation (visibility, integer IDs, held poses) vs smooth motion. Obj 5.2-adjacent: the *type* of the attribute also matters (you do not linearly interpolate tokens).

### 3. Beginner explanation

Linear = draw a straight line between keys. Held = keep the previous key until the next one.

Where the analogy breaks: after the last sample, both modes keep the last value. Before the first sample, both use the first sample.

### 4. Technical explanation

- `stage.GetInterpolationType()` / `SetInterpolationType`.
- Tokens: `Usd.InterpolationTypeLinear`, `Usd.InterpolationTypeHeld`.
- Verified: samples at 1→(0,0,0) and 11→(10,0,0). Time 6 linear → (5,0,0). Time 6 held → (0,0,0). Time 20 (after last) → (10,0,0).
- This is **stage-level**, not per-attribute, in the core API.

### 5. Mental model

```text
1: 0 -------- 11: 10 ===== 20

linear t=6:  5
held   t=6:  0
both   t=20: 10
```

### 6. Simple example

Visibility should be held. Translation of a camera is usually linear (or a spline, §10.7).

### 7. USDA example

Interpolation is **not** stored in the layer. It is a runtime stage setting. The samples themselves are:

```usda
#usda 1.0

def Xform "Ball"
{
    double3 xformOp:translate.timeSamples = {
        1: (0, 0, 0),
        11: (10, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, Gf

stage = Usd.Stage.CreateInMemory()
xf = UsdGeom.Xform.Define(stage, "/Ball")
attr = xf.AddTranslateOp().GetAttr()
attr.Set(Gf.Vec3d(0, 0, 0), 1)
attr.Set(Gf.Vec3d(10, 0, 0), 11)
print("default interp:", stage.GetInterpolationType())
print("linear t=6:", attr.Get(6))
stage.SetInterpolationType(Usd.InterpolationTypeHeld)
print("held t=6:", attr.Get(6))
print("t=20:", attr.Get(20))
```

**Expected output**

```text
default interp: Usd.InterpolationTypeLinear
linear t=6: (5, 0, 0)
held t=6: (0, 0, 0)
t=20: (10, 0, 0)
```

### 9. Real-world use case

A layout pop-through (object teleports) is authored as held keys. If a tool forces linear, you see a slide nobody wanted.

### 10. Common mistakes

> [!MISTAKE] Authoring two samples on a `token` attribute and expecting a "blend." Tokens do not blend; you get held-like behavior.

### 11. Exam traps

> [!TRAP] "Held uses the *next* key." It uses the **previous** (the sample at or before the time).

### 12. Practice questions

**DM-016** · Difficulty: Medium · Type: Single choice

Samples at 0=0 and 10=10. Held interpolation at t=4 is:

A. 4  
B. 0  
C. 10  
D. 5  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Stage default interpolation is linear.
> - Held = previous sample. After last / before first = edge samples.

---

## 10.5 Layer offsets (Obj 1.4)

### 1. What is it?

A **layer offset** remaps time when a layer is brought in by a **reference** or **sublayer**: `composedTime = sourceTime * scale + offset`.

### 2. Why do we need it?

Obj 1.4: several characters reuse **the same animation layer** starting at different shot times. You do not copy the clip.

### 3. Beginner explanation

The dance is stored from 1–11. Hero A starts that dance at shot 1 (`offset = 0`). Hero B starts it at shot 11 (`offset = 10`). Same file, two clocks.

Where the analogy breaks: offset is in **TimeCodes**, not seconds. `scale` can speed up or reverse (negative scale).

### 4. Technical explanation

- Python: `Sdf.LayerOffset(offset=10, scale=1)` (scale 1 is the default; USDA may omit it).
- `prim.GetReferences().AddReference(id, primPath=..., layerOffset=off)`
- USDA: `prepend references = @anim.usda@ (offset = 10)`
- Verified: source samples at 1 and 11 with offset 10 compose as samples at **11 and 21**. At composed time 11 you see the source's time-1 value.

Works on sublayers too (`subLayers` entries can carry offsets — Ch 15).

### 5. Mental model

```text
source:     1 -------- 11
offset 10:           11 -------- 21
```

### 6. Simple example

Two walkers, one clip, offsets 0 and 48.

### 7. USDA example

*File: anim.usda*

```usda
#usda 1.0
(
    defaultPrim = "Ball"
)

def Xform "Ball"
{
    double3 xformOp:translate.timeSamples = {
        1: (0, 0, 0),
        11: (10, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
```

*File: shot.usda*

```usda
#usda 1.0

def Xform "HeroA" (
    prepend references = @./anim.usda@
)
{
}

def Xform "HeroB" (
    prepend references = @./anim.usda@ (
        offset = 10
    )
)
{
}
```

HeroB's translation samples sit 10 TimeCodes later than HeroA's.

### 8. Python example

```python
from pxr import Usd, Sdf

anim = Sdf.Layer.CreateAnonymous("anim.usda")
anim.ImportFromString(
    '#usda 1.0\n'
    '(\n'
    '    defaultPrim = "Ball"\n'
    ')\n'
    'def Xform "Ball" {\n'
    '    double3 xformOp:translate.timeSamples = {\n'
    '        1: (0, 0, 0),\n'
    '        11: (10, 0, 0),\n'
    '    }\n'
    '    uniform token[] xformOpOrder = ["xformOp:translate"]\n'
    '}\n'
)
root = Sdf.Layer.CreateAnonymous("shot.usda")
root.ImportFromString('#usda 1.0\ndef Xform "HeroB" {}\n')
stage = Usd.Stage.Open(root)
hero = stage.GetPrimAtPath("/HeroB")
hero.GetReferences().AddReference(
    anim.identifier,
    primPath=Sdf.Path("/Ball"),
    layerOffset=Sdf.LayerOffset(offset=10),
)
attr = hero.GetAttribute("xformOp:translate")
print("composed samples:", attr.GetTimeSamples())
print("t=11:", attr.Get(11))
print("t=21:", attr.Get(21))
```

**Expected output**

```text
composed samples: [11.0, 21.0]
t=11: (0, 0, 0)
t=21: (10, 0, 0)
```

### 9. Real-world use case

Crowd shots instance one walk cycle with many offsets so the crowd does not march in lockstep (Ch 24–25).

### 10. Common mistakes

> [!MISTAKE] Offsetting in seconds (`offset = 10` meaning 10 seconds at 24 fps). USD's offset is in TimeCodes: 10 frames if tps=24, not 10 seconds.

### 11. Exam traps

> [!TRAP] "Layer offset changes the file on disk." It remaps time **on that arc** only. `anim.usda` still has samples at 1 and 11.

### 12. Practice questions

**COMP-PRE-006** · Obj 1.4 · Difficulty: Medium · Type: Single choice

A clip has a sample at time 1. You reference it with `offset = 10`. Where does that sample appear on the stage?

A. Time 1  
B. Time 10  
C. Time 11  
D. It is deleted  

**Answer:** C. `1 * 1 + 10 = 11`.

### 13. Exam takeaways

> [!KEY]
> - `composed = source * scale + offset`.
> - Obj 1.4 = reuse one animation at different offsets; do not copy the clip.

---

## 10.6 Value clips (overview)

### 1. What is it?

**Value clips** stream animation from a **sequence of files** (often one file per frame or chunk) instead of packing every sample into one layer.

### 2. Why do we need it?

Caches that would make a single USDC enormous. The study guide lists value clips in the composition reading list.

### 3. Beginner explanation

Instead of one 200,000-sample file, you have `cache.1001.usdc`, `cache.1002.usdc`, … and metadata that says which file is active at which time.

Where the analogy breaks: clips are **not** payloads. Payloads load topology. Clips stitch **values** over time.

### 4. Technical explanation

- API: `Usd.ClipsAPI(prim)`.
- Metadata on the prim: clip asset paths, clip times, active times, optional template (`clipTemplateAssetPath`, stride, start, end).
- `GenerateClipManifest` builds a manifest of which attributes are in the clips.
- Clips contribute as a value-resolution source (Ch 21). Strength vs local opinions is a composition topic.

You will not author a full clip set in this chapter's lab. Know the name, the API class, and why pipelines use them.

### 5. Mental model

Clips = a playlist of cache files mapped onto the timeline.

### 6. Simple example

FX sim dumped per frame as USD; the character prim points at the playlist.

### 7. USDA example

Template-style metadata (shape only; paths are illustrative):

```usda
#usda 1.0

def Xform "Sim" (
    clips = {
        dictionary default = {
            string templateAssetPath = "./caches/sim.###.usdc"
            double templateStartTime = 1001
            double templateEndTime = 1100
            double templateStride = 1
        }
    }
)
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/Sim").GetPrim()
clips = Usd.ClipsAPI(prim)
print("schema:", type(clips).__name__)
print("has GetClipAssetPaths:", hasattr(clips, "GetClipAssetPaths"))
print("has GetClipTemplateAssetPath:", hasattr(clips, "GetClipTemplateAssetPath"))
```

**Expected output**

```text
schema: ClipsAPI
has GetClipAssetPaths: True
has GetClipTemplateAssetPath: True
```

### 9. Real-world use case

A 1500-frame ocean sim: one crate per frame, one set of clip metadata on `/World/Ocean`.

### 10. Common mistakes

> [!MISTAKE] Putting clip files behind a payload and expecting clip metadata on an unloaded prim to still stream. Working-set (Ch 17) and clips interact; keep the clip metadata on a loaded prim.

### 11. Exam traps

> [!TRAP] "Value clips are the same as time samples in one layer." Clips *feed* values; they are a different encoding and file layout.

### 12. Practice questions

**DM-017** · Difficulty: Medium · Type: Single choice

Value clips are primarily for:

A. Changing upAxis  
B. Streaming animation from many cache files over time  
C. Creating USDA from USDC  
D. Kind metadata  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Clips = playlist of cache layers over time (`Usd.ClipsAPI`).
> - Time samples in one layer remain the basic encoding you must master.

---

## 10.7 Splines (version note)

### 1. What is it?

**Splines** store a curve (tangents, interpolation segments) on an attribute instead of (or in addition to) dense samples. Python module `Ts`; `Usd.Attribute.GetSpline` exists in USD 26.08.

### 2. Why do we need it?

The study guide lists the spline proposal. You should recognize the feature and the VERSION story, not design a spline editor for the exam.

### 3. Beginner explanation

Samples = a polyline through keys. Splines = Bezier/Hermite-style animation curves.

### 4. Technical explanation

> [!VERSION] Splines (Ts) appeared 24.03; attribute value resolution gained spline support later (25.05+); `GetSpline`/`SetSpline` APIs 25.08; clips+splines 26.08. This book is verified on **26.08**, where `GetSpline` exists. **Time samples remain the encoding to master for NCP-OUSD.**

### 5. Mental model

If the question says "timeSamples dictionary," think samples. If it says "spline/tangents/Ts," think the newer curve object.

### 6. Simple example

A DCC may export Bezier camera motion as a spline in a 26.x pipeline, or bake it to samples for compatibility.

### 7. USDA example

You will meet `.timeSamples` far more often. A spline-backed attribute is still an ordinary typed attribute; the spline is extra encoded data (not required to paste a full spline USDA here).

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius.timeSamples = {
        1: 1,
        10: 2,
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
attr = UsdGeom.Sphere.Define(stage, "/Ball").GetRadiusAttr()
print("GetSpline exists:", hasattr(attr, "GetSpline"))
print("HasSpline:", attr.HasSpline())
```

**Expected output**

```text
GetSpline exists: True
HasSpline: False
```

### 9. Real-world use case

A studio on USD 23.x cannot read spline-authored files from a 26.x vendor. Bake samples for interchange.

### 10. Common mistakes

> [!MISTAKE] Assuming every USD file with animation has splines. Most caches are samples or clips.

### 11. Exam traps

> [!TRAP] A question that shows `.timeSamples` — the answer is samples, not splines.

### 12. Practice questions

**DM-018** · Difficulty: Easy · Type: Single choice

For the NCP-OUSD exam's core animation encoding, you should be fluent in:

A. Only Hydra scene indexes  
B. Attribute time samples (and layer offsets / clips at overview level)  
C. Only Alembic Ogawa  
D. Only USDZ  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Splines exist in 26.08 (`GetSpline`). Samples are still the foundation.
> - Mark spline interchange as version-sensitive.

---

## Chapter lab(s)

Lab 10 (time samples, interpolation, time codes) and Lab 14 (time-offset references) belong here.

## USDA reading exercise

**USDA-11.** Clip samples at 1 and 11. Reference with `offset = 5`. At composed time 6, which source time is sampled? What composed sample times do you expect?

**Answer:** Source time `6 - 5 = 1`. Composed samples at 6 and 16.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Get() never animates | You queried Default time |
| Default vs frame 0 | Different things |
| Two heroes, one walk file | Layer offset (Obj 1.4) |
| Held vs linear at mid-frame | Previous key vs lerp |
| Huge per-frame caches | Value clips |

### Chapter questions

**Q1.** What time does `attr.Get()` use?  
**Q2.** Numeric query before the first sample uses what?  
**Q3.** Default interpolation type?  
**Q4.** Held at a time between keys uses which key?  
**Q5.** Formula for layer offset?  
**Q6.** Obj 1.4 in one sentence?  
**Q7.** `TimeCode.Default().IsDefault()`?  
**Q8.** Do clips replace the need to understand samples?

**Answers**

1. Default time. 2. The first sample. 3. Linear. 4. The previous sample. 5. `scale * source + offset`. 6. Reuse one animation at different time offsets. 7. True. 8. No — clips feed values; samples are still core.

## Further reading

- Tutorial: Transformations, Time-Sampled Animation, and Layer Offsets  
- Glossary: TimeCode, Layer Offset, Value Clips  
- `UsdStage::SetInterpolationType()`  
- Spline animation in USD (proposal / changelog) — VERSION  
