# Chapter 14 — Composition Fundamentals

> **Exam domain:** Composition (23%) · **Objectives:** 1.1, 1.6 · **Study day:** 5 · **Est. time:** 120 min
> **Prerequisites:** Ch 3 (Layers), Ch 4 (Prims and Prim Paths), Ch 5 (Properties), Ch 8 (Usd vs. Sdf)

Part III starts here. Composition is the largest exam domain, and it also shows up inside the debugging, pipeline, and content-aggregation questions. This chapter gives you the vocabulary and the core rules. Chapters 15–22 then study each composition arc in depth.

## Learning goals

- Explain what composition does and why OpenUSD composes layers instead of merging them.
- Define an opinion and its strength, and name three ways to change which opinion wins (Obj 1.1).
- List the seven composition arcs and recite LIVERPS in strength order (Obj 1.6).
- Predict the result of list editing with `prepend`, `append`, `delete`, and explicit lists.
- Describe a layer stack, a prim index, and a prim stack, and inspect them from Python.
- Tell which fields are replaced by the strongest opinion and which fields combine.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Composition | Combining opinions from many layers, connected by arcs, into one stage view |
| Composition arc | A link that pulls opinions from another layer or another prim path into a prim |
| Opinion | One authored value for one field (attribute value, metadata) at one path in one layer |
| Strength | The rank of an opinion; the strongest opinion for a field usually wins |
| LIVERPS | Strength order of arcs: Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes |
| Layer stack | A root layer plus all its sublayers (recursively), in strength order |
| Local opinion | An opinion that comes from the stage's own layer stack (root, sublayers, session) |
| List op | A field that stores edits (`prepend`, `append`, `delete`) or an explicit list |
| List editing | Changing a weaker layer's list from a stronger layer without retyping it |
| Pcp | "Prim cache population", the OpenUSD library that computes composition |
| Prim index | Pcp's per-prim graph of nodes (sources of opinions), ordered by strength |
| Node / site | One source in the prim index; a site is a layer stack plus a prim path |
| Prim stack | The flat list of prim specs that contribute to a prim, strongest first |
| Flatten | Bake a composed stage into one layer with no arcs left |

---

## 14.1 What composition is

### 1. What is it?

**Composition** is the process that combines the contents of many layers into the single scene you see on a stage. Layers are connected by **composition arcs** (sublayers, references, variants, and others). OpenUSD follows those arcs, collects every **opinion** (authored value) about each prim, and decides which one wins.

### 2. Why do we need it?

Real scenes are built by many people and tools. A modeler publishes a chair. A set dresser places fifty chairs in a room. A lighter tweaks a lamp. If all of that lived in one file, people would overwrite each other, every copy of the chair would be duplicated data, and nobody could update the chair once and see it change everywhere. Composition lets each piece stay in its own file and be reused, while the stage shows the combined result.

### 3. Beginner explanation

Think of **transparent sheets on an overhead projector**. Each sheet (layer) has some drawings on it. You stack them. Where two sheets draw on the same spot, the top sheet wins. Where only one sheet draws, you see that drawing. A reference is like **linking a reusable part from a catalog**: instead of drawing the chair again, the sheet says "put catalog item *chair* here".

*Where the analogy breaks:* sheets on a projector only stack. Composition also has arcs that copy a whole subtree to a new path (references), switch between alternatives (variants), and share edits across many prims (inherits). The "top wins" rule also has exceptions: some fields, such as lists and dictionaries, combine instead of replacing.

### 4. Technical explanation

- Composition is computed by the **Pcp** library ("prim cache population"). The `Usd.Stage` asks Pcp to build a **prim index** for each prim. The prim index lists every source of opinions for that prim, in strength order (see 14.5).
- Composition happens **per prim and per field**. For each field (an attribute's default value, a metadata key such as `kind`, a relationship's targets) OpenUSD looks at the opinions in strength order. For most fields the strongest opinion wins. This step is called **value resolution** (Chapter 21).
- Composition is **non-destructive**. It never changes the source layers. If you edit a layer, the stage recomposes and shows the new result.
- The `Usd` API (`Usd.Stage`, `Usd.Prim`, `Usd.Attribute`) shows you the **composed** result. The `Sdf` API (`Sdf.Layer`, `Sdf.PrimSpec`) shows you **what one layer authored** (Chapter 8).
- `prim.GetPrimStack()` returns the `Sdf.PrimSpec` objects that contribute to a prim, strongest first. This is your first debugging tool for "where did this come from?".

### 5. Mental model

```text
  layers on disk              composition (Pcp)           what you see
 +-------------+                                    +--------------------+
 | room.usda   |---+                                |  Usd.Stage         |
 +-------------+   |      follow arcs, collect      |   /Room            |
 | dressing    |---+----> opinions per prim, -----> |   /Room/Chair      |
 +-------------+   |      order them by strength    |     color=walnut   |
 | chair.usda  |---+                                |     height=0.9     |
 +-------------+          (files never change)      +--------------------+
```

### 6. Simple example

| Layer | Opinion about `/Room/Chair.color` |
|-------|-----------------------------------|
| `dressing.usda` (sublayer of the room) | `"walnut"` |
| `chair.usda` (referenced asset) | `"oak"` |
| **Composed result** | `"walnut"`, because local opinions beat referenced ones |

The `height` attribute is only authored in `chair.usda`, so the stage shows the chair's own value `0.9`.

### 7. USDA example

*File: room.usda*

```usda
#usda 1.0
(
    subLayers = [@dressing.usda@]
)

def Xform "Room"
{
    def "Chair" (
        prepend references = @chair.usda@
    )
    {
    }
}
```

- `subLayers = [@dressing.usda@]` — adds a sublayer. Its opinions join this file's layer stack (Chapter 15).
- `def "Chair" (...)` — defines the prim `/Room/Chair` in this layer.
- `prepend references = @chair.usda@` — a reference arc. It pulls in the default prim of `chair.usda` (Chapter 16). `prepend` is a list-editing operation (14.4).
- The empty `{ }` body means this layer authors no values of its own on the chair.

### 8. Python example

The script writes three small files, opens the room, prints the composed values, lists the prim stack, and shows that `chair.usda` itself was not changed.

```python
from pxr import Sdf, Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("chair.usda", """#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair"
{
    string color = "oak"
    double height = 0.9
}
""")
write("dressing.usda", """#usda 1.0
over "Room"
{
    over "Chair"
    {
        string color = "walnut"
    }
}
""")
write("room.usda", """#usda 1.0
(
    subLayers = [@dressing.usda@]
)
def Xform "Room"
{
    def "Chair" (
        prepend references = @chair.usda@
    )
    {
    }
}
""")

stage = Usd.Stage.Open("room.usda")
chair = stage.GetPrimAtPath("/Room/Chair")
print("composed color :", chair.GetAttribute("color").Get())
print("composed height:", chair.GetAttribute("height").Get())
for spec in chair.GetPrimStack():
    print("prim spec in", spec.layer.GetDisplayName(), "at", spec.path)

chair_layer = Sdf.Layer.FindOrOpen("chair.usda")
print("chair.usda still says:",
      chair_layer.GetAttributeAtPath("/Chair.color").default)
```

**Expected output**

```text
composed color : walnut
composed height: 0.9
prim spec in room.usda at /Room/Chair
prim spec in dressing.usda at /Room/Chair
prim spec in chair.usda at /Chair
chair.usda still says: oak
```

Notice that the referenced spec lives at `/Chair` in its own file, but it contributes to `/Room/Chair` on the stage. Arcs can remap paths.

### 9. Real-world use case

In a film shot, the environment, the characters, the animation, and the lighting are separate files owned by separate departments. The shot file only contains arcs and a few overrides. When the modeling department republishes the chair, every shot that references it shows the new chair the next time it is opened. The same idea drives digital twins: a factory layout references one robot asset many times, and a fix to that asset reaches every station.

### 10. Common mistakes

> [!MISTAKE] Editing the asset file to fix one shot. The fix then leaks into every shot that uses the asset. Author the override in the shot's own layer (a stronger, local opinion) instead.

> [!MISTAKE] Reading a layer with `Sdf` and expecting composed values. `Sdf.Layer.GetAttributeAtPath(...).default` shows only what that one layer authored. Use `Usd.Stage` and `Usd.Attribute.Get()` for the composed answer.

> [!MISTAKE] Thinking the stage is "one big file". A stage is a live view over many layers. Saving the stage saves the edited layers, not a merged copy.

### 11. Exam traps

> [!TRAP] "Composition copies the referenced file into the scene" — false. Nothing is copied into your layer; opinions are read from the referenced layer at compose time.

> [!TRAP] "The last layer loaded wins" — there is no time order. Strength comes from the arc type and the position of the layer, never from when a file was opened or saved.

> [!TRAP] An answer that says composition happens "per file". It happens per prim (and value resolution per field). Two prims in the same file can have completely different sources.

### 12. Practice questions

**Q14.1-1** Which library in the OpenUSD stack computes composition?
A. `Sdf` B. `Pcp` C. `Gf` D. `Ar`

**Q14.1-2** A shot sublayers `dressing.usda` and references `chair.usda`. You change `chair.usda` and save it. What happens to `dressing.usda`?
A. It is rewritten with the new chair values.
B. Nothing; composition never changes source layers.
C. Its opinions are deleted because the asset changed.
D. It becomes muted.

**Q14.1-3** Which call returns the layers' prim specs that contribute to a prim, strongest first?
A. `stage.GetLayerStack()` B. `prim.GetPrimStack()` C. `layer.GetPrimAtPath()` D. `prim.GetChildren()`

**Answers**

- **Q14.1-1: B.** Pcp builds prim indexes. Sdf stores layer data, Gf is math, Ar resolves asset paths.
- **Q14.1-2: B.** Composition is non-destructive; only the stage's view changes.
- **Q14.1-3: B.** `GetPrimStack()` lists `Sdf.PrimSpec` objects. `GetLayerStack()` lists layers, not specs for one prim.

### 13. Exam takeaways

> [!KEY]
> - Composition = follow arcs, collect opinions per prim, rank them by strength.
> - It is computed by Pcp and is non-destructive: source layers never change.
> - `Usd` shows composed results; `Sdf` shows what one layer authored.
> - `prim.GetPrimStack()` answers "which layers contribute to this prim?".

---

## 14.2 Opinions and strength

### 1. What is it?

An **opinion** is one authored value for one field at one path in one layer, for example "`/Ball.radius` default is 2 in `fix.usda`". **Strength** is the rank of that opinion compared to other opinions about the same field. For most fields, the **strongest opinion wins**.

### 2. Why do we need it?

Several layers often say different things about the same attribute. USD needs a deterministic rule to pick one, so every application that opens the scene shows the same result. Strength lets a downstream department override an upstream one on purpose, without editing the upstream file.

### 3. Beginner explanation

Use the **ladder of opinions**: picture a ladder where each rung is one opinion. USD asks the top rung first. If that rung has an answer, the question is settled. If the rung is silent about this field, USD asks the next rung down.

*Where the analogy breaks:* the ladder is built separately for each field. A rung can be silent about `radius` but have an answer for `color`. Also, a few fields (lists, dictionaries) collect answers from several rungs instead of taking just the top one (14.4, 14.6).

### 4. Technical explanation

Strength is decided in two steps:

1. **Within one layer stack**, stronger layers come first: the session layer, then the root layer, then sublayers in listed order (Chapter 15).
2. **Across arcs**, the arc type decides: opinions in the local layer stack beat inherits, which beat variants, and so on down LIVERPS (14.3, Chapter 21). Arcs nest: inside a referenced asset, the same rules apply again to that asset's own arcs.

An opinion only exists where something is authored. An `over` with no attributes contributes no attribute opinions. A schema's fallback value (for example `radius = 1` for `UsdGeom.Sphere`) is **not** an opinion; it is used only when no layer has an opinion at all.

**Changing the strength of an opinion (Obj 1.1).** You cannot set a "priority number" on an opinion. To make a value win, you move it or restructure the arcs:

| Technique | How |
|-----------|-----|
| Author in a stronger layer | Put the override in the root layer, a stronger sublayer, or the session layer |
| Reorder sublayers | Change the order of `subLayers` (first is strongest) |
| Use a stronger arc | A local opinion beats a referenced one; an inherited class beats a reference |
| Reorder an arc list | `prepend` puts an arc first (strongest) in its list; `append` puts it last |
| Remove the competitor | Delete the stronger opinion (`attr.Clear()` / `ClearAtTime()`) or the arc providing it |

Introspection: `attr.GetPropertyStack()` returns the attribute specs that hold opinions, strongest first. `attr.GetResolveInfo()` tells you the source of the winning value (Chapter 21).

### 5. Mental model

```text
 ask strongest first ---------------------------------------->
 [session] -> [root] -> [sublayer 1] -> [sublayer 2] -> [arcs: I V E R P S]
     |           |            |              |
   silent      silent      radius=2       radius=1
                              ^
                      first answer wins: radius = 2
```

### 6. Simple example

`shot.usda` has `subLayers = [@fix.usda@, @model.usda@]`. `fix.usda` says radius 2, `model.usda` says radius 1. The composed radius is 2. Swap the order to `[@model.usda@, @fix.usda@]` and it becomes 1. Neither file changed.

### 7. USDA example

*File: fix.usda*

```usda
#usda 1.0

over "Ball"
{
    double radius = 2
}
```

- `over "Ball"` — "I have opinions about `/Ball`, but I am not defining it". The definition (`def Sphere "Ball"`) lives in a weaker layer.
- `double radius = 2` — one opinion: the default value of `radius`. This layer is silent about every other field of `/Ball`.

### 8. Python example

Three ways to change which opinion wins, without editing the opinions themselves.

```python
from pxr import Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("model.usda", '#usda 1.0\ndef Sphere "Ball"\n{\n    double radius = 1\n}\n')
write("fix.usda", '#usda 1.0\nover "Ball"\n{\n    double radius = 2\n}\n')
write("shot.usda", "#usda 1.0\n(\n    subLayers = [@fix.usda@, @model.usda@]\n)\n")

stage = Usd.Stage.Open("shot.usda")
radius = stage.GetPrimAtPath("/Ball").GetAttribute("radius")
stack = [spec.layer.GetDisplayName() for spec in radius.GetPropertyStack()]
print("1 start           :", radius.Get(), stack)

stage.GetRootLayer().subLayerPaths = ["model.usda", "fix.usda"]
print("2 reorder         :", radius.Get())

with Usd.EditContext(stage, stage.GetRootLayer()):
    radius.Set(3.0)
print("3 root layer      :", radius.Get())

with Usd.EditContext(stage, stage.GetSessionLayer()):
    radius.Set(4.0)
print("4 session layer   :", radius.Get())
stack = [spec.layer.GetDisplayName() for spec in radius.GetPropertyStack()]
print("  property stack  :", stack)
```

**Expected output**

```text
1 start           : 2.0 ['fix.usda', 'model.usda']
2 reorder         : 1.0
3 root layer      : 3.0
4 session layer   : 4.0
  property stack  : ['shot-session.usda', 'shot.usda', 'model.usda', 'fix.usda']
```

`Usd.EditContext` temporarily sets the **edit target**, the layer that receives new edits (Chapter 15). The session layer is an in-memory layer that is stronger than the root layer (Chapter 3).

### 9. Real-world use case

In games and film, a lighting artist needs a lamp brighter in one shot only. The lamp asset says `inputs:intensity = 10`. The lighter authors `inputs:intensity = 40` in the shot's lighting layer, which is stronger than the referenced asset. The asset stays untouched for all other shots. In AEC review sessions, a reviewer can hide a wall in the session layer without changing any saved file.

### 10. Common mistakes

> [!MISTAKE] Authoring an override into a layer that is weaker than the current winner, then wondering why nothing changed. Check `attr.GetPropertyStack()` first and author into a layer above the winning one.

> [!MISTAKE] Treating a schema fallback as an opinion. A sphere with no authored `radius` reports 1.0, but no layer says so. `attr.HasAuthoredValue()` is `False` in that case.

> [!MISTAKE] Expecting the most recently saved file to win. File timestamps play no role in strength.

### 11. Exam traps

> [!TRAP] "Change the strength of an opinion" questions want a structural answer: move the opinion to a stronger layer, reorder sublayers, or use a stronger arc. There is no per-opinion priority field.

> [!TRAP] A weaker layer that authors **more** attributes does not become stronger. Strength is per field: the weaker layer still wins for fields the stronger layer leaves silent.

> [!TRAP] Session-layer edits win over the root layer, but they are not saved with `stage.Save()` (`stage.Save()` skips the session layer; `stage.SaveSessionLayers()` exists for that).

### 12. Practice questions

**Q14.2-1** `shot.usda` sublayers `[@a.usda@, @b.usda@]`. Both set `/Car.speed`. Which **two** changes make the value from `b.usda` win? (Select two.)
A. Reorder to `[@b.usda@, @a.usda@]`.
B. Save `b.usda` after `a.usda`.
C. Remove the `speed` opinion from `a.usda`.
D. Make `b.usda` a binary `.usdc` file.

**Q14.2-2** A `Sphere` prim has no authored `radius` in any layer, and `Get()` returns 1.0. Where does 1.0 come from?
A. The root layer B. The session layer C. The schema's fallback value D. The weakest sublayer

**Answers**

- **Q14.2-1: A and C.** Reordering puts `b.usda` first (strongest); removing the competing opinion leaves `b.usda` as the only voice. Save order and file format do not affect strength.
- **Q14.2-2: C.** Fallbacks come from the schema definition and apply only when there is no opinion at all.

### 13. Exam takeaways

> [!KEY]
> - Opinion = one authored value for one field, at one path, in one layer.
> - Strongest opinion wins, decided per field: layer order inside a layer stack, then arc type (LIVERPS).
> - To change strength: move the opinion, reorder sublayers or arc lists, use a stronger arc, or remove the competitor.
> - Schema fallbacks are not opinions. `GetPropertyStack()` shows who has an opinion.

---

## 14.3 The seven arcs at a glance

### 1. What is it?

OpenUSD has seven **composition arcs**, the ways a prim can receive opinions from somewhere else: **sublayers**, **inherits**, **variant sets**, **relocates**, **references**, **payloads**, and **specializes**. Their strength order is remembered with the acronym **LIVERPS**.

### 2. Why do we need it?

Each arc solves a different problem: stacking work (sublayers), reusing assets (references), deferring heavy data (payloads), switching alternatives (variants), broadcasting shared edits (inherits), providing overridable defaults (specializes), and renaming or moving prims that came from somewhere else (relocates). Knowing the order lets you predict which arc wins when two of them disagree.

### 3. Beginner explanation

| Arc | Analogy (used across this book) |
|-----|---------------------------------|
| Sublayers | Transparent sheets on a projector; top sheet wins |
| Inherits | A style sheet every instance follows, even later edits |
| Variant sets | A switch with named positions |
| Relocates | A forwarding address: the prim now lives at a new path |
| References | Linking a reusable part from a catalog |
| Payloads | A reference you can choose not to load (a box in storage) |
| Specializes | A default that anything else can override |

*Where the analogy breaks:* the arcs are not independent tools. They nest (a referenced asset can contain variants that contain references), and the strength rules apply again at every level of nesting.

### 4. Technical explanation

**LIVERPS**, strongest to weakest:

| Letter | Arc | USDA keyword | Where it is authored | Chapter |
|--------|-----|--------------|----------------------|---------|
| L | **Local** opinions (the layer stack built by sublayers) | `subLayers` | layer metadata | 15 |
| I | Inherits | `inherits` | prim metadata | 19 |
| V | VariantSets | `variantSets`, `variants`, `variantSet` | prim metadata and body | 18 |
| E | rElocates | `relocates` | **layer** metadata | 20 |
| R | References | `references` | prim metadata | 16 |
| P | Payloads | `payload` | prim metadata | 17 |
| S | Specializes | `specializes` | prim metadata | 19 |

- "Local" is not a separate arc keyword. It means all opinions from the stage's own layer stack: the root layer, its sublayers, and the session layer. Sublayers are the arc that builds that stack.
- Inherits and specializes point at a prim path (often a `class` prim). References and payloads point at a layer (and optionally a prim path in it). Variants select one of several named bodies inside the same prim.
- **Relocates** are authored as layer metadata: `relocates = { </Old/Path>: </New/Path> }`. In Python you set them with `Sdf.Layer.relocates` (Chapter 20).
- `Usd.PrimCompositionQuery(prim).GetCompositionArcs()` lists the arcs on a prim in strength order. Each `Usd.CompositionArc` reports `GetArcType()` (a `Pcp.ArcType` value), `GetTargetLayer()`, and `GetTargetPrimPath()`.

> [!VERSION] Verified on USD 26.08. The OpenUSD glossary spells the acronym **LIVERPS** (Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes). Older books, talks, and the NVIDIA study material may say **LIVRPS**, which simply leaves out relocates; the relative order of the other six arcs is the same. Relocates authoring and composition arrived in the USD 24.x releases (Chapter 20).

> [!NOTE] The Python enum `Pcp.ArcType` lists its values as Root, Inherit, Relocate, Variant, Reference, Payload, Specialize. That enum order is not a strength chart; use LIVERPS.

### 5. Mental model

```text
 STRONGEST                                                   WEAKEST
    L --------> I --------> V --------> E --------> R --------> P --------> S
  local      inherits    variants   relocates   references  payloads  specializes
 (layer      (classes)   (switch)   (moved      (catalog    (lazy      (overridable
  stack)                             prims)      parts)      parts)     defaults)

 "LIVERPS": the closer to L, the louder the voice.
```

### 6. Simple example

A prim `/Bot` gets `team` from an inherited class, `scale` from its selected variant, `triangles` from a payload, and `paint` from a specialized default. If the class and the specialized prim both authored `paint`, the class (Inherits, I) would win over Specializes (S).

### 7. USDA example

*File: scene.usda* (one prim using every arc; `robot.usda`, `heavy.usda`, and `layout.usda` are separate files)

```usda
#usda 1.0
(
    subLayers = [@layout.usda@]
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)

class "_Base"
{
    string team = "blue"
}

def "_Defaults"
{
    string paint = "grey"
}

def Xform "Bot" (
    inherits = </_Base>
    specializes = </_Defaults>
    prepend references = @robot.usda@
    prepend payload = @heavy.usda@
    variantSets = "size"
    variants = {
        string size = "big"
    }
)
{
    variantSet "size" = {
        "big" {
            double scale = 2
        }
        "small" {
            double scale = 0.5
        }
    }
}
```

- `subLayers` (L) and `relocates` (E) are **layer** metadata in the parentheses at the top of the file.
- `inherits`, `specializes`, `references`, `payload`, `variantSets` are **prim** metadata in the parentheses after `def Xform "Bot"`.
- `variants = { string size = "big" }` is the variant **selection**; the `variantSet "size" = {...}` block holds the variant bodies.
- The relocate moves `Arm` (which arrives from `robot.usda` under `Rig`) to `/Bot/Arm`.

### 8. Python example

```python
from pxr import Pcp, Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("robot.usda", """#usda 1.0
(
    defaultPrim = "Robot"
)
def Xform "Robot"
{
    def Xform "Rig"
    {
        def Xform "Arm"
        {
            double length = 1
        }
    }
}
""")
write("heavy.usda", """#usda 1.0
(
    defaultPrim = "Geo"
)
def Xform "Geo"
{
    int triangles = 50000
}
""")
write("layout.usda", '#usda 1.0\nover "Bot"\n{\n    string fromLayout = "yes"\n}\n')
write("scene.usda", """#usda 1.0
(
    subLayers = [@layout.usda@]
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)
class "_Base"
{
    string team = "blue"
}
def "_Defaults"
{
    string paint = "grey"
}
def Xform "Bot" (
    inherits = </_Base>
    specializes = </_Defaults>
    prepend references = @robot.usda@
    prepend payload = @heavy.usda@
    variantSets = "size"
    variants = {
        string size = "big"
    }
)
{
    variantSet "size" = {
        "big" {
            double scale = 2
        }
        "small" {
            double scale = 0.5
        }
    }
}
""")

stage = Usd.Stage.Open("scene.usda")
bot = stage.GetPrimAtPath("/Bot")
for arc in Usd.PrimCompositionQuery(bot).GetCompositionArcs():
    print(f"{str(arc.GetArcType()):24}",
          arc.GetTargetLayer().GetDisplayName(), arc.GetTargetPrimPath())

for name in ["fromLayout", "team", "scale", "triangles", "paint"]:
    print(name, "=", bot.GetAttribute(name).Get())

print("children of /Bot:", bot.GetChildrenNames())
arm = stage.GetPrimAtPath("/Bot/Arm")
for arc in Usd.PrimCompositionQuery(arm).GetCompositionArcs():
    if arc.GetArcType() == Pcp.ArcTypeRelocate:
        print("/Bot/Arm is relocated from", arc.GetTargetPrimPath())
```

**Expected output**

```text
Pcp.ArcTypeRoot          scene.usda /Bot
Pcp.ArcTypeInherit       scene.usda /_Base
Pcp.ArcTypeVariant       scene.usda /Bot{size=big}
Pcp.ArcTypeReference     robot.usda /Robot
Pcp.ArcTypePayload       heavy.usda /Geo
Pcp.ArcTypeSpecialize    scene.usda /_Defaults
fromLayout = yes
team = blue
scale = 2.0
triangles = 50000
paint = grey
children of /Bot: ['Rig', 'Arm']
/Bot/Arm is relocated from /Bot/Rig/Arm
```

The query lists arcs in LIVERPS order. "Root" is the local layer stack (the L), which includes `layout.usda`. `Usd.Stage.Open` loads payloads by default, so `triangles` is visible (Chapter 17). The `Rig` prim stays, but `Arm` has moved out of it.

### 9. Real-world use case

A game studio's level file sublayers a layout layer (L), references a prop catalog (R), loads heavy terrain through payloads (P), offers `lod` variants (V), puts shared "team color" settings on a class that all enemy prims inherit (I), and uses specializes for material defaults that any asset may override (S). Relocates let a character pipeline rename a rig joint hierarchy coming from a referenced rig without editing the rig file.

### 10. Common mistakes

> [!MISTAKE] Writing `relocates` in a prim's metadata. Relocates are **layer** metadata, at the top of the file, mapping old paths to new paths.

> [!MISTAKE] Spelling the payload keyword `payloads` in USDA. The keyword is `payload` (for example `prepend payload = @heavy.usda@`), even though the arc is called "payloads" in prose and the Python API is `prim.GetPayloads()`.

> [!MISTAKE] Thinking "Local" means "this one file". Local means the whole local layer stack, including every sublayer and the session layer.

### 11. Exam traps

> [!TRAP] References are stronger than payloads, but that is a strength statement. It says nothing about loading: payloads can be unloaded, references cannot.

> [!TRAP] Inherits (I) is near the top and Specializes (S) is at the bottom, even though both point at a class-like prim. A question pairing them is testing exactly that.

> [!TRAP] "Variants are the weakest because they are inside the prim" — false. VariantSets (V) are stronger than references, payloads, and specializes.

### 12. Practice questions

**Q14.3-1** Which arc is authored as layer metadata, not prim metadata?
A. Inherits B. Payloads C. Relocates D. Specializes

**Q14.3-2** A prim gets `color` from a reference and a different `color` from its selected variant. Which wins?
A. The reference, because it is authored first.
B. The variant, because V is stronger than R.
C. Neither; USD reports a conflict error.
D. Whichever file is larger.

**Q14.3-3** Put these in strength order, strongest first: Payloads, Inherits, Specializes, References.
A. Inherits, References, Payloads, Specializes
B. References, Payloads, Inherits, Specializes
C. Inherits, Payloads, References, Specializes
D. Specializes, Inherits, References, Payloads

**Answers**

- **Q14.3-1: C.** `relocates = {...}` sits in the layer's metadata block.
- **Q14.3-2: B.** LIVERPS puts VariantSets above References. Conflicts are normal; strength resolves them.
- **Q14.3-3: A.** I, then R, then P, then S.

### 13. Exam takeaways

> [!KEY]
> - Seven arcs: sublayers, inherits, variant sets, relocates, references, payloads, specializes.
> - LIVERPS = Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes (strongest first). Older material says LIVRPS.
> - L = the local layer stack (root, sublayers, session), not one file.
> - Relocates and sublayers are layer metadata; the other arcs are prim metadata.
> - `Usd.PrimCompositionQuery` lists a prim's arcs in strength order.

---

## 14.4 List editing: `prepend`, `append`, `delete`, explicit

### 1. What is it?

Some fields hold a **list**, for example the list of references on a prim, its inherit paths, its applied API schemas, or a relationship's targets. These fields are stored as **list ops** (list operations). A stronger layer can **edit** a weaker layer's list (add to the front, add to the back, remove items) instead of replacing it. This is **list editing**.

### 2. Why do we need it?

Without list editing, a shot that wanted one extra reference on a prim would have to retype the full list from the asset. If the asset later added another reference, the shot's copy would silently hide it. List editing lets each layer say only what it changes, so upstream additions still flow through.

### 3. Beginner explanation

Think of a shared shopping list on the fridge. Instead of rewriting the whole list, each family member leaves a sticky note: "add milk at the top", "add bread at the bottom", "cross out sugar". Someone reading the list applies the notes from the most important person last, so their notes have the final say. If someone writes a brand-new list and says "ignore everything else", that is an **explicit** list.

*Where the analogy breaks:* in USD the order of the final list matters. For arcs, an item near the front of the list is **stronger** than an item near the back.

### 4. Technical explanation

A list op (`Sdf.ReferenceListOp`, `Sdf.PathListOp`, `Sdf.TokenListOp`, …) is either **explicit** or a set of **edits**:

| USDA form | Meaning |
|-----------|---------|
| `references = [@a@, @b@]` | **Explicit**: this is the whole list; ignore all weaker opinions |
| `prepend references = @c@` | Put `c` at the **front** of the list (strongest position) |
| `append references = @d@` | Put `d` at the **back** of the list (weakest position) |
| `delete references = @a@` | Remove `a` if a weaker layer added it |

Rules verified on USD 26.08:

- Edits are applied weakest layer first, strongest layer last, so the strongest layer has the final word.
- Within one layer's edits, `delete` is applied first, then `prepend`, then `append`.
- Prepending an item that is already in the list **moves** it to the front. Appending an existing item moves it to the back.
- Deleting an item that is not in the list does nothing (no error).
- An explicit list in a stronger layer discards all weaker opinions. An explicit list in a weaker layer is simply the starting list that stronger edits modify.
- One spec cannot be explicit and have edits at the same time. If a USDA prim writes both `references = ...` and `prepend references = ...`, the parser keeps only the last statement.
- `references = None` is an explicit **empty** list: it removes every weaker reference.

Python authoring: `prim.GetReferences().AddReference(...)` writes `prepend` by default (`position=Usd.ListPositionFrontOfPrependList`). Other positions are `Usd.ListPositionBackOfPrependList`, `Usd.ListPositionFrontOfAppendList`, `Usd.ListPositionBackOfAppendList`. `RemoveReference` writes a `delete` (or removes the item from an explicit list); `SetReferences([...])` writes an explicit list; `ClearReferences()` removes this layer's opinion. The same pattern exists on `GetInherits()`, `GetSpecializes()`, `GetPayloads()`, and relationships (`AddTarget`, `RemoveTarget`, `SetTargets`).

> [!NOTE] Older files may contain `add` and `reorder` list operations. They are legacy forms; new content should use `prepend`, `append`, `delete`, or an explicit list.

### 5. Mental model

```text
 weakest layer  :  prepend [a, b]                 -> list = [a, b]
 stronger layer :  delete [b]                     -> list = [a]
                   append [c]                     -> list = [a, c]
 strongest layer:  prepend [n]                    -> list = [n, a, c]
                                                      ^ front = strongest arc
 strongest layer:  explicit [x]  (instead)        -> list = [x]  (all else ignored)
```

### 6. Simple example

The asset layer says `prepend references = [@a.usda@, @b.usda@]`. The shot layer says `delete references = @b.usda@` and `append references = @c.usda@`. The composed reference list is `[a, c]`: `b` is gone, `c` joined at the back, and `a` is the strongest reference.

### 7. USDA example

*File: strong.usda*

```usda
#usda 1.0

over "Thing" (
    delete references = @b.usda@
    append references = @c.usda@
)
{
}
```

- `over "Thing"` — this layer edits `/Thing`, which is defined in a weaker layer.
- `delete references = @b.usda@` — removes the `b.usda` reference that a weaker layer added.
- `append references = @c.usda@` — adds `c.usda` at the back, the weakest position.
- Neither line restates `a.usda`; it survives because this layer does not mention it.

### 8. Python example

First, the pure list rules with `Sdf.TokenListOp` (no stage needed):

```python
from pxr import Sdf

start = ["M", "N"]

edits = Sdf.TokenListOp()
edits.deletedItems = ["M"]
edits.prependedItems = ["A"]
edits.appendedItems = ["Z"]
print("edits           :", edits.ApplyOperations(start))

move = Sdf.TokenListOp()
move.prependedItems = ["N"]
print("prepend existing:", move.ApplyOperations(start))

explicit = Sdf.TokenListOp.CreateExplicit(["X"])
print("explicit        :", explicit.ApplyOperations(start), explicit.isExplicit)

missing = Sdf.TokenListOp()
missing.deletedItems = ["Q"]
print("delete missing  :", missing.ApplyOperations(start))
```

**Expected output**

```text
edits           : ['A', 'N', 'Z']
prepend existing: ['N', 'M']
explicit        : ['X'] True
delete missing  : ['M', 'N']
```

Now the same idea with real references across two sublayers, plus what Python writes when you author list edits:

```python
from pxr import Sdf, Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


for src in ["a", "b", "c"]:
    write(f"{src}.usda", f"""#usda 1.0
(
    defaultPrim = "P"
)
def "P"
{{
    string src = "{src}"
}}
""")
write("weak.usda", """#usda 1.0
def "Thing" (
    prepend references = [@a.usda@, @b.usda@]
)
{
}
""")
write("strong.usda", """#usda 1.0
over "Thing" (
    delete references = @b.usda@
    append references = @c.usda@
)
{
}
""")
write("shot.usda", "#usda 1.0\n(\n    subLayers = [@strong.usda@, @weak.usda@]\n)\n")

stage = Usd.Stage.Open("shot.usda")
thing = stage.GetPrimAtPath("/Thing")
query = Usd.PrimCompositionQuery.GetDirectReferences(thing)
names = [arc.GetTargetLayer().GetDisplayName() for arc in query.GetCompositionArcs()]
print("composed references:", names)
print("src resolves to    :", thing.GetAttribute("src").Get())

mem = Usd.Stage.CreateInMemory()
x = mem.DefinePrim("/X")
x.GetReferences().AddReference("a.usda")
x.GetReferences().AddReference("c.usda", position=Usd.ListPositionBackOfAppendList)
ops = mem.GetRootLayer().GetPrimAtPath("/X").referenceList
print("authored prepend   :", [r.assetPath for r in ops.prependedItems])
print("authored append    :", [r.assetPath for r in ops.appendedItems])
```

**Expected output**

```text
composed references: ['a.usda', 'c.usda']
src resolves to    : a
authored prepend   : ['a.usda']
authored append    : ['c.usda']
```

`a.usda` is first in the composed list, so its `src` opinion beats `c.usda`'s. The last two lines read the raw list op stored in the in-memory layer: `AddReference` wrote a `prepend` by default and an `append` when asked.

> [!NOTE] `thing.GetMetadata("references")` returns only the **strongest layer's** list op (here the delete/append edits), not the composed list. To see the composed result, use `Usd.PrimCompositionQuery` (Chapter 22).

### 9. Real-world use case

A character asset applies `prepend apiSchemas = ["MaterialBindingAPI"]`. A shot adds a physics schema with its own `prepend apiSchemas = [...]`; both survive because list ops combine. In a factory digital twin, a station layer uses `delete references = @old_gripper.usda@` and `prepend references = @new_gripper.usda@` to swap a tool without retyping the robot's other references.

### 10. Common mistakes

> [!MISTAKE] Writing `references = @c.usda@` (explicit) when you meant "add one more". The explicit list wipes every weaker reference. Use `prepend` or `append`.

> [!MISTAKE] Using `append` for an override reference that must win. Appended items are the weakest. Use `prepend` when the new arc should be strongest.

> [!MISTAKE] Writing `prepend subLayers = [...]`. `subLayers` is a plain ordered list, not a list op; that line does not parse. Just edit the list (Chapter 15).

### 11. Exam traps

> [!TRAP] "`delete` errors if the item is missing" — false; it is silently ignored.

> [!TRAP] In an arc list, **front = strongest**. A question that asks which of two prepended references wins wants the one listed first in the strongest layer's edit.

> [!TRAP] `references = None` does not mean "no opinion". It is an explicit empty list that removes all weaker references.

### 12. Practice questions

**Q14.4-1** A weak layer has `prepend inherits = [</A>, </B>]`. A stronger layer has `delete inherits = </A>` and `prepend inherits = </C>`. What is the composed inherits list?
A. `[</C>, </B>]` B. `[</A>, </B>, </C>]` C. `[</C>]` D. `[</B>, </C>]`

**Q14.4-2** Which Python call writes `prepend references` by default?
A. `prim.GetReferences().SetReferences([ref])`
B. `prim.GetReferences().AddReference(ref)`
C. `prim.GetReferences().ClearReferences()`
D. `prim.SetMetadata("references", ref)`

**Q14.4-3** A stronger layer says `references = @x.usda@` and a weaker layer says `prepend references = @y.usda@`. How many references does the prim have?
A. 0 B. 1 C. 2 D. It is a composition error.

**Answers**

- **Q14.4-1: A.** Start `[A, B]`, delete `A` gives `[B]`, prepend `C` gives `[C, B]`.
- **Q14.4-2: B.** `AddReference` defaults to the front of the prepend list. `SetReferences` writes an explicit list.
- **Q14.4-3: B.** A stronger explicit list ignores weaker opinions, so only `x.usda` remains.

### 13. Exam takeaways

> [!KEY]
> - List ops: explicit (replace everything weaker) or edits (`prepend` front, `append` back, `delete` remove).
> - Edits apply weakest first, strongest last; front of an arc list = strongest arc.
> - Prepending an existing item moves it; deleting a missing item is a no-op.
> - `AddReference` → `prepend`; `SetReferences` → explicit; `subLayers` is not a list op.

---

## 14.5 Layer stacks and the prim index

### 1. What is it?

A **layer stack** is a root layer plus all its sublayers (recursively), in strength order. A stage's **local layer stack** also includes the session layer on top. The **prim index** is the graph Pcp builds for each prim: one **node** per source of opinions (the local layer stack, each inherited class, each variant, each reference…), ordered by strength. Flattening the prim index into a list of prim specs gives the **prim stack**.

### 2. Why do we need it?

These are the data structures behind every "why did this value win?" answer. The exam's debugging questions (Obj 1.8, Obj 6.2) expect you to reason about which layer stack and which node an opinion came from. Inspecting the prim index turns guessing into reading.

### 3. Beginner explanation

Picture a family tree of opinion sources. The prim itself is at the top. Under it hang its sources: "my local layers", "the class I inherit", "the asset I reference". Each source is itself a little stack of sheets (a layer stack). To answer a question, USD walks the tree in a fixed order (LIVERPS) and reads each stack of sheets top-down.

*Where the analogy breaks:* a family tree has one parent per person. A prim index can contain the same layer more than once (for example an inherited class in the same file as the prim), and sources can be implied across arcs (Chapter 19).

### 4. Technical explanation

- **Layer stack** (`Pcp.LayerStack`): root layer + sublayers, recursively depth-first. Each referenced or payloaded file brings **its own** layer stack (its root plus its sublayers). `stage.GetLayerStack()` returns the local one, session layers first.
- **Site**: a layer stack plus a prim path, for example "the layer stack of `robot.usda` at `/Robot`".
- **Node** (`Pcp.NodeRef`): one site in the prim index plus how it got there: `node.arcType`, `node.layerStack`, `node.path`, `node.children`, `node.parent`. The **root node** is the prim's own path in the local layer stack.
- **Prim index** (`Pcp.PrimIndex`, from `prim.GetPrimIndex()`): the tree of nodes. Strength order is a depth-first walk: a node, then its children in LIVERPS order. Each child's own children (for example the arcs inside a referenced asset) are visited before moving on to the next sibling.
- **Prim stack**: `prim.GetPrimStack()` (or `primIndex.primStack`) returns the `Sdf.PrimSpec` objects in that order. Value resolution walks the same order (Chapter 21).
- `primIndex.DumpToString()` prints a full debug dump. It contains memory addresses of anonymous layers, so this book walks the nodes itself to keep output stable.
- Composition **errors** (for example an unresolvable reference) are recorded on the prim index (`primIndex.localErrors`) and reported as warnings; the stage still opens (Chapter 43).

### 5. Mental model

```text
 prim index for /Bot                       prim stack (strongest first)
 ------------------------------            ----------------------------
 Root  [scene-session, scene] /Bot   -->   scene.usda          /Bot
  |-- Inherit  [scene...]  /_Base    -->   scene.usda          /_Base
  `-- Reference [robot, robot_geo]   -->   robot.usda          /Robot
               /Robot                -->   robot_geo.usda      /Robot
```

### 6. Simple example

`/Bot` in `scene.usda` inherits `/_Base` and references `robot.usda`. `robot.usda` sublayers `robot_geo.usda`. The prim index has three nodes (root, inherit, reference). The reference node's layer stack has two layers, so it contributes two prim specs.

### 7. USDA example

*File: robot.usda* (the referenced asset has its own layer stack)

```usda
#usda 1.0
(
    defaultPrim = "Robot"
    subLayers = [@robot_geo.usda@]
)

def Xform "Robot"
{
    string status = "published"
}
```

- `subLayers = [@robot_geo.usda@]` — `robot.usda` and `robot_geo.usda` form one layer stack. When `scene.usda` references `robot.usda`, that whole stack becomes one reference node.
- `defaultPrim = "Robot"` — the prim a reference uses when it names no prim path.

### 8. Python example

```python
from pxr import Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("robot_geo.usda", '#usda 1.0\nover "Robot"\n{\n    int faces = 12\n}\n')
write("robot.usda", """#usda 1.0
(
    defaultPrim = "Robot"
    subLayers = [@robot_geo.usda@]
)
def Xform "Robot"
{
    string status = "published"
}
""")
write("scene.usda", """#usda 1.0
class "_Base"
{
    string team = "blue"
}
def Xform "Bot" (
    inherits = </_Base>
    prepend references = @robot.usda@
)
{
}
""")

stage = Usd.Stage.Open("scene.usda")
print("local layer stack:", [l.GetDisplayName() for l in stage.GetLayerStack()])
bot = stage.GetPrimAtPath("/Bot")


def walk(node, depth=0):
    layers = [l.GetDisplayName() for l in node.layerStack.layers]
    arc = str(node.arcType).replace("Pcp.ArcType", "")
    print("  " * depth + f"{arc:9} {node.path} {layers}")
    for child in node.children:
        walk(child, depth + 1)


walk(bot.GetPrimIndex().rootNode)
for spec in bot.GetPrimStack():
    print("spec:", spec.layer.GetDisplayName(), spec.path)
```

**Expected output**

```text
local layer stack: ['scene-session.usda', 'scene.usda']
Root      /Bot ['scene-session.usda', 'scene.usda']
  Inherit   /_Base ['scene-session.usda', 'scene.usda']
  Reference /Robot ['robot.usda', 'robot_geo.usda']
spec: scene.usda /Bot
spec: scene.usda /_Base
spec: robot.usda /Robot
spec: robot_geo.usda /Robot
```

The session layer is part of every local-layer-stack node, but it has no specs here, so it is absent from the prim stack.

### 9. Real-world use case

A pipeline technical director (TD) debugging "the robot is the wrong color in shot 42" walks the prim index: is the winning opinion in the shot's local layer stack, in a class, in a variant, or deep inside the referenced asset's sublayers? Studio debugging tools and usdview's composition view display this same tree.

### 10. Common mistakes

> [!MISTAKE] Assuming `stage.GetLayerStack()` lists every layer in the scene. It lists only the **local** layer stack. Layers reached through references and payloads are listed by `stage.GetUsedLayers()`.

> [!MISTAKE] Printing `DumpToString()` in tests or docs and expecting stable output. It includes memory addresses; walk `rootNode` and its `children` instead.

> [!MISTAKE] Looking only at the referencing file when a value is wrong. The referenced asset's own sublayers are part of the reference node and may hold the winning opinion.

### 11. Exam traps

> [!TRAP] "A referenced file's sublayers are ignored" — false. A reference brings the target's whole layer stack.

> [!TRAP] Prim stack vs. layer stack: the layer stack is a list of **layers** for a stage or asset; the prim stack is a list of **prim specs** for one prim.

### 12. Practice questions

**Q14.5-1** `scene.usda` references `asset.usda`, which sublayers `asset_mtl.usda`. Which call on the scene's stage includes `asset_mtl.usda`?
A. `stage.GetLayerStack()` B. `stage.GetUsedLayers()` C. `stage.GetRootLayer().subLayerPaths` D. `stage.GetSessionLayer()`

**Q14.5-2** What is a "site" in Pcp terms?
A. A file path on disk B. A layer stack plus a prim path C. A variant selection D. A Hydra render target

**Answers**

- **Q14.5-1: B.** `GetUsedLayers()` returns every layer the stage uses. `GetLayerStack()` is only the local stack.
- **Q14.5-2: B.** Each prim index node represents one site.

### 13. Exam takeaways

> [!KEY]
> - Layer stack = root + sublayers (recursive); the local one also has the session layer on top.
> - Prim index = tree of nodes (sites) in LIVERPS order; prim stack = its prim specs, strongest first.
> - A reference or payload node carries the target's whole layer stack.
> - `prim.GetPrimIndex()`, `prim.GetPrimStack()`, `stage.GetLayerStack()`, `stage.GetUsedLayers()`.

---

## 14.6 Composition is not merging

### 1. What is it?

Composition does **not** merge files into one, and it does not blend values. Every layer stays separate. For each field, USD **picks** the strongest opinion. Only a few kinds of fields **combine** across layers: list ops (14.4), dictionaries such as `customData`, and the set of child prims and properties. Turning a composed stage into one merged layer is a separate, explicit step called **flattening**.

### 2. Why do we need it?

Because layers stay separate, you can change, swap, mute, or reorder any of them and the stage updates. A merged file would freeze everyone's work together and lose the information about who authored what. Knowing which fields are picked and which combine prevents surprises, such as an array that you expected to "add to" but that was replaced.

### 3. Beginner explanation

Back to the projector sheets: if the top sheet draws a red circle and the bottom sheet draws a blue circle in the same spot, you see red, not purple. Composition never mixes the two. A photocopy of the projected image would be "flattening": you get one sheet, but you can no longer lift off the top layer.

*Where the analogy breaks:* some fields behave like a list or a labeled form instead of a drawing. A dictionary (like `customData`) is combined key by key, so a stronger layer can change one key and keep the weaker layer's other keys.

### 4. Technical explanation

| Field kind | Across layers | Example |
|------------|---------------|---------|
| Attribute value (scalar **or array**) | Strongest wins; arrays are never concatenated | `int[] ids` |
| Most metadata (`kind`, `active`, `documentation`, …) | Strongest wins | `kind = "component"` |
| List ops (`references`, `inherits`, `apiSchemas`, relationship targets, …) | Edits combine (14.4) | `prepend apiSchemas` |
| Dictionaries (`customData`, `assetInfo`) | Combined key by key; strongest wins per key | `customData` |
| Child prims and properties | Union of names from all contributing specs | children of a prim |
| Specifier (`def`/`over`/`class`) | A stronger `over` never undoes a weaker `def` | `over "Box"` over `def "Box"` |

Flattening:

- `stage.Flatten()` returns a new anonymous `Sdf.Layer` with all composition baked in: no sublayers, references, variants, or classes remain, only resolved specs. It is used for delivery and debugging (Chapter 22, Chapter 34).
- `UsdUtils.FlattenLayerStack(stage)` flattens only the local layer stack and keeps other arcs (Chapter 34).
- `stage.Export("file.usda")` writes the flattened result to a file.

### 5. Mental model

```text
  COMPOSITION (live)                     FLATTEN (one-time bake)
  +--------+  +--------+                 +--------------------------+
  | strong |  |  weak  |    Flatten()    | one layer, values picked |
  | ids=[9]|  |ids=[1, |  ------------>  | ids=[9]  label="weak"    |
  |        |  | 2,3]   |                 | no arcs, no sublayers    |
  +--------+  +--------+                 +--------------------------+
  files stay separate; pick per field    history of "who said what" lost
```

### 6. Simple example

`weak.usda` sets `ids = [1, 2, 3]` and `label = "weak"`. `strong.usda` sets `ids = [9]`. The composed `ids` is `[9]`, not `[9, 1, 2, 3]`. The composed `label` is `"weak"`, because the strong layer is silent about it.

### 7. USDA example

*File: weak.usda*

```usda
#usda 1.0

def "Box" (
    customData = {
        string owner = "modeling"
        int version = 1
    }
    prepend apiSchemas = ["CollectionAPI:a"]
)
{
    int[] ids = [1, 2, 3]
    string label = "weak"
}
```

- `customData = {...}` — a dictionary. A stronger layer can override `version` alone and keep `owner`.
- `prepend apiSchemas = [...]` — a token list op; stronger layers can add more schemas.
- `int[] ids = [1, 2, 3]` — an array value; a stronger `ids` replaces it entirely.

### 8. Python example

```python
from pxr import Sdf, Usd


def write(name, text):
    with open(name, "w") as f:
        f.write(text)


write("weak.usda", """#usda 1.0
def "Box" (
    customData = {
        string owner = "modeling"
        int version = 1
    }
    prepend apiSchemas = ["CollectionAPI:a"]
)
{
    int[] ids = [1, 2, 3]
    string label = "weak"
}
""")
write("strong.usda", """#usda 1.0
over "Box" (
    customData = {
        int version = 7
    }
    prepend apiSchemas = ["CollectionAPI:b"]
)
{
    int[] ids = [9]
}
""")
write("shot.usda", "#usda 1.0\n(\n    subLayers = [@strong.usda@, @weak.usda@]\n)\n")

stage = Usd.Stage.Open("shot.usda")
box = stage.GetPrimAtPath("/Box")
print("ids        :", box.GetAttribute("ids").Get())
print("label      :", box.GetAttribute("label").Get())
print("customData :", sorted(box.GetCustomData().items()))
print("apiSchemas :", box.GetAppliedSchemas())

flat = stage.Flatten()
print("flat subLayers:", list(flat.subLayerPaths))
print("flat ids      :", flat.GetAttributeAtPath("/Box.ids").default)
weak = Sdf.Layer.FindOrOpen("weak.usda")
print("weak.usda ids :", weak.GetAttributeAtPath("/Box.ids").default)
```

**Expected output**

```text
ids        : [9]
label      : weak
customData : [('owner', 'modeling'), ('version', 7)]
apiSchemas : ['CollectionAPI:b', 'CollectionAPI:a']
flat subLayers: []
flat ids      : [9]
weak.usda ids : [1, 2, 3]
```

The array was replaced, the dictionary combined per key, and the list op combined. Flattening produced one layer with no sublayers, while `weak.usda` kept its own value.

### 9. Real-world use case

Studios keep composition live during production so departments can iterate, then flatten for delivery to a vendor or a game engine that should not depend on the studio's file structure (Obj 1.9, Chapter 22). Pipelines often write `customData` or `assetInfo` from several layers (for example the modeling department writes `owner`, the publishing tool writes `version`) and rely on the per-key combination.

### 10. Common mistakes

> [!MISTAKE] Authoring `points = [new points]` in a shot layer expecting to "add" points to a mesh. Arrays are replaced; author the full array.

> [!MISTAKE] Flattening a production scene to "fix" a composition problem. You lose the arcs that made it editable. Debug the composition instead (Chapter 22).

> [!MISTAKE] Overriding a whole `customData` dictionary to change one key, thinking you must restate all keys. You only need to author the keys you change.

### 11. Exam traps

> [!TRAP] "Composition merges the layers into the root layer" — false. Merging is what `Flatten()` does, on request, into a new layer.

> [!TRAP] A question showing two array opinions and offering a concatenated answer. Arrays never concatenate across layers.

> [!TRAP] A question asking which field kinds combine. Correct choices are list ops and dictionaries (and the set of children/properties), not attribute values.

### 12. Practice questions

**Q14.6-1** Weak layer: `customData = { string a = "1"  string b = "2" }`. Strong layer: `customData = { string b = "9" }`. What is the composed `customData`? 
A. `{b: "9"}` B. `{a: "1", b: "9"}` C. `{a: "1", b: "2"}` D. `{a: "1", b: ["2", "9"]}`

**Q14.6-2** Which **two** statements are true? (Select two.)
A. `stage.Flatten()` returns a layer with no composition arcs.
B. Composition writes resolved values back into the root layer.
C. A stronger `float[]` opinion replaces a weaker one completely.
D. Attribute values from all layers are averaged.

**Answers**

- **Q14.6-1: B.** Dictionaries combine key by key; the strong layer wins only for `b`.
- **Q14.6-2: A and C.** Composition never writes back to layers, and values are picked, never averaged.

### 13. Exam takeaways

> [!KEY]
> - Composition picks the strongest opinion per field; it never blends or concatenates values.
> - Combining fields: list ops, dictionaries (`customData`, `assetInfo`), and the set of children/properties.
> - Flattening (`stage.Flatten()`, `stage.Export()`) is an explicit bake into one layer; arcs are lost.
> - Source layers are never modified by composition.

---

## Chapter lab(s)

This chapter has no lab of its own. Practice it with **Lab 05 — Build a sublayer stack and see who wins** (Chapters 3 and 15): you build a three-layer stack, predict the winning opinion, then reorder layers and check your prediction. Later, **Lab 20 — LIVERPS laboratory: predict, then verify** (Chapter 21) combines every arc from 14.3 into one puzzle scene.

## USDA reading exercises

**Exercise 14-A.** `shot.usda` contains `subLayers = [@strong.usda@, @weak.usda@]`. Each of `base.usda`, `old.usda`, and `new.usda` has a default prim with `string src` set to its own name.

*File: weak.usda*

```usda
#usda 1.0

def "Lamp" (
    prepend references = [@base.usda@, @old.usda@]
)
{
}
```

*File: strong.usda*

```usda
#usda 1.0

over "Lamp" (
    delete references = @old.usda@
    prepend references = @new.usda@
)
{
}
```

What is the composed reference list on `/Lamp`, and what does `/Lamp.src` resolve to?

**Exercise 14-B.** `shot2.usda` contains `subLayers = [@s2.usda@, @w2.usda@]`.

*File: w2.usda*

```usda
#usda 1.0

def "Rock" (
    customData = {
        string a = "w"
        string b = "w"
    }
)
{
    float[] weights = [1, 2]
    float size = 3
}
```

*File: s2.usda*

```usda
#usda 1.0

over "Rock" (
    customData = {
        string b = "s"
    }
)
{
    float[] weights = [5]
}
```

What are the composed `weights`, `size`, and `customData` of `/Rock`? Is `/Rock` defined?

## Chapter review

### Summary

- Composition combines opinions from many layers, linked by arcs, into one stage view. Pcp computes it; source layers never change.
- An opinion is one authored value for one field in one layer. Strength decides the winner, per field.
- Change strength structurally: move the opinion to a stronger layer, reorder sublayers or arc lists, use a stronger arc, or remove the competitor (Obj 1.1).
- Seven arcs; LIVERPS order: Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes (Obj 1.6). Older material: LIVRPS.
- Relocates and sublayers are layer metadata; the other arcs are prim metadata.
- List ops: explicit lists replace weaker opinions; `prepend`/`append`/`delete` edit them. Front of an arc list is strongest.
- A layer stack is a root plus sublayers; each reference brings its target's whole layer stack.
- The prim index is a tree of nodes in strength order; the prim stack is its specs, strongest first.
- Values are picked, never blended. Only list ops, dictionaries, and child/property name sets combine.
- Flattening is an explicit bake into one layer; arcs are lost.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| "Which opinion wins?" | Walk LIVERPS, then layer order inside each layer stack |
| "Change the strength of an opinion" | Move it to a stronger layer, reorder, or use a stronger arc |
| `prepend` vs `append` on an arc | Prepend = front = strongest; append = back = weakest |
| `references = [...]` without a keyword | Explicit list: weaker reference opinions are discarded |
| `relocates = {...}` | Layer metadata; the E in LIVERPS, between variants and references |
| Two array values in two layers | Strongest array wins whole; no concatenation |
| `customData` in two layers | Combined per key |
| "Where did this value come from?" | `GetPropertyStack()`, `GetPrimStack()`, `PrimCompositionQuery` |
| "Merge the scene into one file" | `stage.Flatten()` / `stage.Export()`; arcs are lost |

### Review questions

**14-R1** · Obj 1.6 · Single choice
In LIVERPS, which letter stands for an arc that is authored in layer metadata and remaps prim paths?
A. L B. E C. R D. S

**14-R2** · Obj 1.6 · Select two.
Which **two** arcs are weaker than References?
A. Inherits B. Payloads C. Specializes D. VariantSets

**14-R3** · Obj 1.1 · Single choice
A shot sublayers `[@anim.usda@, @layout.usda@]`. Layout wants its `/Car.xformOp:translate` to win over animation in this shot only, without touching `anim.usda`. What should be done?
A. Re-save `layout.usda` so it is newer.
B. Reorder the shot's sublayers to `[@layout.usda@, @anim.usda@]`.
C. Convert `layout.usda` to `.usdc`.
D. Add `prepend` before the attribute in `layout.usda`.

**14-R4** · Obj 1.1 · USDA reading
A weaker layer has `prepend references = [@a.usda@, @b.usda@]`. A stronger layer has `append references = @a.usda@`. What is the composed list, strongest first?
A. `[a, b]` B. `[b, a]` C. `[a, b, a]` D. `[a]`

**14-R5** · Obj 1.6 · Single choice
A prim inherits `/_Class` (which sets `size = 2`) and specializes `/_Defaults` (which sets `size = 5`). Neither the prim's layer stack nor any other arc sets `size`. What is `size`?
A. 5 B. 2 C. 7 D. The schema fallback

**14-R6** · Single choice
What does `prim.GetPrimStack()` return?
A. Layers of the local layer stack
B. Prim specs that contribute to the prim, strongest first
C. Child prims in namespace order
D. The variant sets on the prim

**14-R7** · Select two.
Which **two** fields combine across layers instead of taking only the strongest opinion?
A. `customData`
B. `double radius`
C. `apiSchemas`
D. `kind`

**14-R8** · Obj 1.1 · Python reading
What does this print?

```{.python .norun}
op = Sdf.TokenListOp()
op.deletedItems = ["x"]
op.prependedItems = ["y"]
print(op.ApplyOperations(["x", "z"]))
```

A. `['y', 'z']` B. `['x', 'y', 'z']` C. `['z', 'y']` D. `['y', 'x', 'z']`

**14-R9** · Single choice
Which statement about composition is correct?
A. It writes the resolved values into the root layer when the stage opens.
B. It is recomputed when a contributing layer changes, and it never edits the layers.
C. It concatenates array attributes from all layers.
D. It only considers the root layer and its direct sublayers.

**14-R10** · Single choice
`scene.usda` references `asset.usda`, which sublayers `asset_shading.usda`. A wrong material comes from `asset_shading.usda`. In the prim index of the referencing prim, where does that opinion live?
A. In the root node, because sublayers are local
B. In the reference node, whose layer stack includes `asset_shading.usda`
C. Nowhere; sublayers of referenced files are ignored
D. In a specializes node

**14-R11** · Single choice
A stronger layer authors `inherits = None`. A weaker layer authored `prepend inherits = </_Base>`. What happens?
A. The prim still inherits `/_Base`.
B. The prim inherits nothing: `None` is an explicit empty list.
C. A parse error occurs.
D. `/_Base` becomes a specializes arc.

**14-R12** · Obj 1.6 · Single choice
Which pair is in the correct strength order (stronger first)?
A. Payloads, then References
B. Specializes, then Inherits
C. VariantSets, then References
D. References, then Local

> The code in 14-R8 is a fragment (it omits the import), so it is not run automatically.

### Answers

**Exercise 14-A — Answer.** The weak layer gives `[base, old]`. The strong layer deletes `old` (`[base]`) and prepends `new` (`[new, base]`). `new.usda` is the strongest reference, so `/Lamp.src` is `"new"`. Verified by composing the files: the composed reference list is `['new.usda', 'base.usda']` and `src` resolves to `new`.

**Exercise 14-B — Answer.** `weights = [5]` (the strong array replaces the weak one), `size = 3` (only the weak layer has an opinion), `customData = {a: "w", b: "s"}` (dictionaries combine per key). `/Rock` is defined: the strong layer only has an `over`, but the weak layer's `def` is the defining specifier. Verified by composing the files.

- **14-R1: B.** E = rElocates, authored as `relocates = {...}` layer metadata. Review: §14.3.
- **14-R2: B and C.** Payloads (P) and Specializes (S) come after References (R). Inherits and VariantSets are stronger. Review: §14.3.
- **14-R3: B.** Reordering sublayers in the shot changes strength for this shot only. Save time and file format do not affect strength; `prepend` is not an attribute keyword. Review: §14.2.
- **14-R4: B.** Appending an item that is already in the list moves it to the back: `[b, a]`. Review: §14.4.
- **14-R5: B.** Inherits (I) is stronger than Specializes (S). The values are not added. Review: §14.3.
- **14-R6: B.** The prim stack is a list of `Sdf.PrimSpec`s. Review: §14.5.
- **14-R7: A and C.** Dictionaries and list ops combine; `radius` and `kind` take the strongest opinion. Review: §14.6.
- **14-R8: A.** Delete `x` first (`['z']`), then prepend `y` (`['y', 'z']`). Review: §14.4.
- **14-R9: B.** Composition is live and non-destructive. Review: §14.1, §14.6.
- **14-R10: B.** A reference node carries the target's whole layer stack. Review: §14.5.
- **14-R11: B.** `None` authors an explicit empty list in the stronger layer. Review: §14.4.
- **14-R12: C.** V comes before R in LIVERPS. Review: §14.3.

## Further reading

- [S04] OpenUSD Glossary — entries "LIVERPS Strength Ordering", "List Editing", "Composition Arcs", "Prim Index", "Layer Stack". https://openusd.org/release/glossary.html
- [S14] NVIDIA Learn OpenUSD — "Composition Basics" and "Creating Composition Arcs". https://docs.nvidia.com/learn-openusd/latest/index.html
- [S05] OpenUSD tutorials — "Referencing Layers". https://openusd.org/release/tut_usd_tutorials.html
- [S06] OpenUSD API reference — `UsdPrimCompositionQuery`, `PcpPrimIndex`, `SdfListOp`. https://openusd.org/release/api/index.html
- [S08] USD FAQ — sublayers vs. references. https://openusd.org/release/usdfaq.html
