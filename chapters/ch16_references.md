# Chapter 16 — References

> **Exam domain:** Composition (23%) · **Objectives:** 1.3, 1.4 · **Study day:** 5 · **Est. time:** 120 min
> **Prerequisites:** Ch 2 (stage, `defaultPrim`), Ch 3 (layers), Ch 4 (prim paths), Ch 10 (time samples), Ch 14 (composition, list editing), Ch 15 (sublayers, layer offsets on sublayers)

## Learning goals

- Author an external reference in USDA and in Python, and predict which prims and values it produces.
- Explain how `defaultPrim` lets you reference a file without naming a prim path, and what happens when it is missing.
- Use internal references to reuse a prim from the same layer stack.
- Place the same animation at different times and speeds with `Sdf.LayerOffset(offset, scale)`, and calculate the resulting times.
- Diagnose why a reference "does nothing", using `Usd.Stage.GetCompositionErrors()`.
- Compare references with sublayers and choose the right one for a task.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Reference** | A composition arc that brings a prim (and everything below it) from a layer into a prim on your stage. |
| **Referencing prim** | The prim on your stage that holds the reference (the destination). |
| **Target prim** | The prim inside the referenced layer that is brought in (the source). |
| **External reference** | A reference whose target lives in another file, named by an asset path such as `@chair.usda@`. |
| **Internal reference** | A reference whose target lives in the same layer stack; it has a prim path but no asset path. |
| **`defaultPrim`** | Layer metadata naming the prim that is used when a reference gives no prim path. |
| **Layer offset** | A pair (offset, scale) that shifts and stretches the time samples coming through an arc. |
| **Composition error** | A problem found while composing (missing file, missing prim, cycle). The stage still opens. |
| **Namespace mapping** | The renaming of paths from the target prim's location to the referencing prim's location. |
| **Anchoring** | Resolving a relative asset path from the folder of the layer that wrote it. |

---

## 16.1 External references

### 1. What is it?

An **external reference** tells a prim on your stage: "get your contents from that prim in that other file." The prim in your stage then shows the referenced prim's type, properties, and children, as if they were written there.

### 2. Why do we need it?

Real scenes reuse assets. A city has 500 identical street lamps; a film set has 40 copies of one chair. Without references you would copy the chair's data 40 times. A fix to the chair would then need 40 edits. With references, the chair lives in one file, and every copy follows it.

### 3. Beginner explanation

Think of **linking a reusable part from a catalog**. Your room design does not contain a drawing of the chair; it says "chair, catalog item 17, here." When the catalog item is improved, every room that links it gets the improvement. You can still write a local note on one copy ("this one is red"), and your note wins over the catalog.

Where the analogy breaks: a catalog link usually copies a whole product. A USD reference brings exactly **one prim and its subtree**, and it renames all of its paths to fit your scene.

### 4. Technical explanation

- A reference is stored as prim metadata named `references`. Each entry is an `Sdf.Reference(assetPath, primPath, layerOffset, customData)`.
- In Python you edit it through `Usd.References`, returned by `prim.GetReferences()`. `AddReference(assetPath, primPath)` adds one entry.
- `references` is a **list-edited** field (Chapter 14). `AddReference` writes `prepend` by default, so new references are added at the front of the list of prepended items. Earlier entries in the final list are **stronger**.
- The target prim's whole **layer stack** comes along: if `chair.usda` has sublayers, their opinions are included too.
- **Namespace mapping:** the target `/Chair` is mapped to the referencing prim, say `/Room/Chair_01`. So `/Chair/Seat` appears as `/Room/Chair_01/Seat`. Relationship targets inside `/Chair` are remapped the same way.
- **Strength:** references are the **R** in LIVERPS (Chapter 14). Local opinions on the referencing prim, from any layer of your stage's layer stack, are stronger than anything brought in by the reference. That is why overrides work.
- Layer metadata of the referenced file (`upAxis`, `metersPerUnit`, `defaultPrim`) does not become stage metadata. Only the stage's root layer and session layer set stage metadata.
- Relative asset paths are **anchored** to the layer that authored them, not to your current working folder.

### 5. Mental model

```text
 chair.usda                        room.usda (your stage)
 +------------------+              +-----------------------------+
 | /Chair  (Xform)  |  reference   | /Room                       |
 |   /Seat (Cube)   | ===========> |   /Chair_01  -> /Chair      |
 +------------------+     |        |     /Seat                   |
                          +======> |   /Chair_02  -> /Chair      |
                                   |     /Seat  (local override) |
                                   +-----------------------------+
 One source, many destinations. Local opinions beat the reference.
```

### 6. Simple example

| Step | What you write | What you see on the stage |
|------|----------------|---------------------------|
| 1 | `chair.usda` defines `/Chair/Seat` with `size = 1` | — |
| 2 | `room.usda`: `/Room/Chair_01` references `chair.usda` | `/Room/Chair_01/Seat`, size 1 |
| 3 | `room.usda`: `over` on `/Room/Chair_02/Seat`, size 2 | Chair_02's seat is size 2; Chair_01's stays 1 |

### 7. USDA example

*File: chair.usda*

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair"
{
    def Cube "Seat"
    {
        double size = 1
    }
}
```

*File: room.usda*

```usda
#usda 1.0

def "Room"
{
    def "Chair_01" (
        prepend references = @./chair.usda@</Chair>
    )
    {
    }

    def "Chair_02" (
        prepend references = @./chair.usda@</Chair>
    )
    {
        over "Seat"
        {
            double size = 2
        }
    }
}
```

Line-by-line notes:

- `defaultPrim = "Chair"` is layer metadata; Section 16.2 explains why it matters.
- `prepend references = @./chair.usda@</Chair>`: the asset path is between `@…@`, the target prim path between `<…>`.
- `Chair_01` and `Chair_02` have no type of their own. They become `Xform` because the referenced `/Chair` is an `Xform`.
- `over "Seat"` adds an opinion without defining a new prim; it is stronger than the reference, so `size` becomes 2 for `Chair_02` only.

### 8. Python example

```python
from pxr import Usd

CHAIR = """#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair"
{
    def Cube "Seat"
    {
        double size = 1
    }
}
"""
with open("chair.usda", "w") as f:
    f.write(CHAIR)

stage = Usd.Stage.CreateNew("room.usda")
for name in ["Chair_01", "Chair_02"]:
    prim = stage.DefinePrim(f"/Room/{name}")
    prim.GetReferences().AddReference("./chair.usda", "/Chair")

# A local opinion on one copy only.
seat2 = stage.GetPrimAtPath("/Room/Chair_02/Seat")
seat2.GetAttribute("size").Set(2.0)

for prim in stage.Traverse():
    print(prim.GetPath(), prim.GetTypeName())
for name in ["Chair_01", "Chair_02"]:
    seat = stage.GetPrimAtPath(f"/Room/{name}/Seat")
    print(name, "seat size =", seat.GetAttribute("size").Get())
stage.Save()
print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
/Room
/Room/Chair_01 Xform
/Room/Chair_01/Seat Cube
/Room/Chair_02 Xform
/Room/Chair_02/Seat Cube
Chair_01 seat size = 1.0
Chair_02 seat size = 2.0
#usda 1.0

def "Room"
{
    def "Chair_01" (
        prepend references = @./chair.usda@</Chair>
    )
    {
    }

    def "Chair_02" (
        prepend references = @./chair.usda@</Chair>
    )
    {
        over "Seat"
        {
            double size = 2
        }
    }
}
```

Notice that `Set(2.0)` on a referenced attribute did not touch `chair.usda`. USD wrote an `over` into the current edit target, the root layer (Chapter 15).

### 9. Real-world use case

In film set dressing, a "set" file references hundreds of prop assets (chairs, cups, books) by asset path. In a factory digital twin, each robot cell references the same robot asset; the robot vendor updates one file, and every cell follows. In AEC, a building model references a window family many times, and local overrides change only the frame color of some.

### 10. Common mistakes

> [!MISTAKE] Editing a referenced prim and expecting the source file to change. Edits go to the current edit target (usually your root layer) as `over` opinions. To change the asset itself, open `chair.usda` and edit it there.

> [!MISTAKE] Writing a prim path without a leading `/`, such as `AddReference("chair.usda", "Chair")`. This raises a `Tf.ErrorException` ("must be either empty or an absolute prim path"). Use `"/Chair"`.

> [!MISTAKE] Assuming the asset path is relative to the folder you run Python from. It is anchored to the folder of the layer that contains the reference.

### 11. Exam traps

> [!TRAP] "A reference copies the asset into the file." False. The reference stores only the link (`@chair.usda@</Chair>`). The data is composed at load time and stays in the source file.

> [!TRAP] "The referenced file's `upAxis` applies to the stage." False. Stage metadata comes from the root (and session) layer only. Unit or axis mismatches must be fixed by the pipeline (Chapter 28).

> [!TRAP] Two references on one prim: the one listed **first** is stronger, not the last one written.

### 12. Practice questions

**Q1.** A prim `/Set/Cup_03` references `@cup.usda@</Cup>`. The file `cup.usda` contains `/Cup/Handle`. What is the path of the handle on the stage?
A. `/Cup/Handle` · B. `/Set/Cup_03/Handle` · C. `/Set/Cup_03/Cup/Handle` · D. `/Set/Handle`

**Q2.** Your root layer has `over "Seat" { double size = 2 }` under a prim that references a chair whose seat has `size = 1`. What is the composed size, and why?

**Q3.** Select two. Which statements about external references are true?
A. They bring in the target prim's descendants.
B. They bring in the target prim's sibling prims.
C. Opinions in the referencing layer stack are stronger than opinions from the reference.
D. They change the stage's `metersPerUnit` to match the referenced file.

**Answers**

**Q1 — B.** The target `/Cup` is mapped onto `/Set/Cup_03`, so its child keeps its name under the new parent.
**Q2 — 2.** Local opinions (L) are stronger than referenced ones (R).
**Q3 — A, C.** Only the target subtree comes in (not siblings), and stage metadata is never taken from a referenced layer.

### 13. Exam takeaways

> [!KEY]
> - A reference = asset path + optional prim path + optional layer offset, stored as list-edited `references` metadata.
> - Only the target prim and its descendants come in, renamed to the referencing prim's path.
> - Local opinions beat referenced opinions; that is how per-copy overrides work.
> - `prim.GetReferences().AddReference(...)` writes `prepend references` into the edit target.

---

## 16.2 `defaultPrim` and references without prim paths

### 1. What is it?

A reference may leave out the prim path: `@chair.usda@`. USD then uses the referenced layer's **`defaultPrim`** metadata to decide which prim to bring in.

### 2. Why do we need it?

The person who uses an asset should not need to know how it is organised inside. With `defaultPrim`, the asset author says "this is my entry point", and every user writes only the file name. If the author later renames the root prim, they update `defaultPrim`, and no referencing file breaks.

### 3. Beginner explanation

A catalog item can contain many sheets: the product, a spare-parts list, notes. The catalog marks one sheet as **"the product"**. If you order item 17 without naming a sheet, you get the marked sheet.

Where the analogy breaks: if no sheet is marked, USD does not guess. You get nothing, plus an error.

### 4. Technical explanation

- `defaultPrim` is layer metadata: `defaultPrim = "Chair"` in the layer header.
- Python: `stage.SetDefaultPrim(prim)`, `stage.GetDefaultPrim()`, `stage.HasDefaultPrim()`, or on a layer `layer.defaultPrim = "Chair"`.
- A reference with an empty prim path (`Sdf.Path()` or simply omitted) targets the `defaultPrim` of the referenced layer.
- If the layer has **no** `defaultPrim`, or names a prim that does not exist, composition reports a **`Pcp.ErrorUnresolvedPrimPath`** error. The referencing prim remains, but receives nothing from the reference.
- `AddReference` still returns `True`: it only *authored* the reference. The failure appears when the stage composes.
- `defaultPrim` is also used by payloads (Chapter 17) and by tools that "open the asset's main prim".

> [!VERSION] Verified on USD 26.08: `defaultPrim` may also hold an absolute path such as `"/Asset/Geo"`, and `Sdf.Layer.GetDefaultPrimAsPath()` returns it as an `Sdf.Path`. Most documentation, asset guidelines, and exam material assume the classic form: the **name of a root prim**. Use that form.

### 5. Mental model

```text
 reference has a prim path?
        |
   yes  +----> use that path
        |
   no   +----> does the layer have defaultPrim?
                  |
             yes  +----> use /<defaultPrim>
                  |
             no   +----> ErrorUnresolvedPrimPath; reference contributes nothing
```

### 6. Simple example

| Referenced file | Reference written | Result |
|-----------------|-------------------|--------|
| `defaultPrim = "Lamp"`, defines `/Lamp` | `@lamp.usda@` | `/Lamp` comes in |
| no `defaultPrim`, defines `/Lamp` | `@lamp.usda@` | nothing comes in, composition error |
| no `defaultPrim`, defines `/Lamp` | `@lamp.usda@</Lamp>` | `/Lamp` comes in |

### 7. USDA example

*File: lamp.usda*

```usda
#usda 1.0
(
    defaultPrim = "Lamp"
)

def Xform "Lamp"
{
    def Cylinder "Pole"
    {
    }
}

def Scope "Notes"
{
}
```

*File: street.usda*

```usda
#usda 1.0

def "Street"
{
    def "Lamp_01" (
        prepend references = @./lamp.usda@
    )
    {
    }
}
```

Notes: `@./lamp.usda@` has no `<…>` part, so `/Lamp` (the `defaultPrim`) is used. `/Notes` is a sibling of `/Lamp` and is **not** brought in.

### 8. Python example

```python
from pxr import Sdf, Usd

WITH_DEFAULT = """#usda 1.0
(
    defaultPrim = "Lamp"
)
def Xform "Lamp"
{
    def Cylinder "Pole" {}
}
"""
NO_DEFAULT = """#usda 1.0
def Xform "Lamp"
{
    def Cylinder "Pole" {}
}
"""
for name, text in [("good.usda", WITH_DEFAULT), ("nodefault.usda", NO_DEFAULT)]:
    with open(name, "w") as f:
        f.write(text)

stage = Usd.Stage.CreateInMemory()
a = stage.DefinePrim("/Street/Lamp_A")
print("authored:", a.GetReferences().AddReference("good.usda"))
b = stage.DefinePrim("/Street/Lamp_B")
print("authored:", b.GetReferences().AddReference("nodefault.usda"))

for prim in (a, b):
    kids = [c.GetName() for c in prim.GetChildren()]
    print(prim.GetName(), repr(prim.GetTypeName()), kids)
for err in stage.GetCompositionErrors():
    print("error at", err.rootSite.path, "->", err.errorType)

# Fix the asset: give it a defaultPrim. The stage recomposes automatically.
layer = Sdf.Layer.FindOrOpen("nodefault.usda")
layer.defaultPrim = "Lamp"
print("after fix:", [c.GetName() for c in b.GetChildren()],
      "errors:", len(stage.GetCompositionErrors()))
```

**Expected output**

```text
authored: True
authored: True
Lamp_A 'Xform' ['Pole']
Lamp_B '' []
error at /Street/Lamp_B -> Pcp.ErrorType_UnresolvedPrimPath
after fix: ['Pole'] errors: 0
```

USD also prints a warning on the error stream (stderr), for example `Unresolved reference prim path @nodefault.usda@<defaultPrim>`. The expected output above shows only normal output.

### 9. Real-world use case

Asset structure guidelines (Chapter 23) require every published asset file to set `defaultPrim` to its root prim. Pipeline validators check this before publishing, because set dressers and layout tools always reference assets by file name only.

### 10. Common mistakes

> [!MISTAKE] Building an asset in Python and forgetting `stage.SetDefaultPrim(root)` before `Save()`. Every reference without a prim path to that file then fails. Fix: always set it when you create the root prim.

> [!MISTAKE] Setting `defaultPrim` to a name that does not exist (a typo, or a prim renamed later). The error is the same `UnresolvedPrimPath`, and the warning names the missing path, e.g. `@bad.usda@</Ghost>`.

### 11. Exam traps

> [!TRAP] "`AddReference` returns `False` when the file has no `defaultPrim`." False. It returns `True`; authoring succeeded. The problem is a composition error, visible through `stage.GetCompositionErrors()` and a warning.

> [!TRAP] "Without `defaultPrim`, USD uses the first root prim." False. USD never guesses.

### 12. Practice questions

**Q1.** `asset.usda` defines `/Car` and `/Truck` and has `defaultPrim = "Truck"`. A prim references `@asset.usda@`. What comes in?
A. Both · B. `/Car` · C. `/Truck` · D. Nothing

**Q2.** Select two. A prim references `@prop.usda@`, and nothing appears below it. Which are likely causes?
A. `prop.usda` has no `defaultPrim`.
B. `prop.usda`'s `defaultPrim` names a prim that does not exist.
C. The referencing prim is typeless.
D. The referencing layer has no `defaultPrim`.

**Answers**

**Q1 — C.** The empty prim path means "use `defaultPrim`", which is `Truck`.
**Q2 — A, B.** Both give `ErrorUnresolvedPrimPath`. The referencing prim's type and the *referencing* layer's metadata do not matter.

### 13. Exam takeaways

> [!KEY]
> - A reference without `<prim path>` uses the referenced layer's `defaultPrim`.
> - Missing or wrong `defaultPrim` → `Pcp.ErrorType_UnresolvedPrimPath`; the prim stays empty.
> - Authoring still succeeds (`AddReference` returns `True`); check `stage.GetCompositionErrors()`.
> - Always set `defaultPrim` on published assets.

---

## 16.3 Internal references

### 1. What is it?

An **internal reference** points to a prim in the **same layer stack** instead of another file. It has a prim path but no asset path: `references = </Templates/Crate>`.

### 2. Why do we need it?

Sometimes the thing you want to reuse lives in the same file: a template crate, a light rig, or a set of default attributes. Internal references let many prims share it without creating a separate asset file.

### 3. Beginner explanation

It is like a catalog link to **a page in the same binder**: "build this exactly like the crate on page 3." Edit page 3, and every crate built "like page 3" changes.

Where the analogy breaks: the page-3 crate is also a real prim in the scene. If you do not want it to show up, make it a `class` prim (abstract, Chapter 4) or keep it under a scope you deactivate.

### 4. Technical explanation

- Python: `prim.GetReferences().AddInternalReference("/Templates/Crate")`, optionally with an `Sdf.LayerOffset`.
- USDA: `prepend references = </Templates/Crate>` (no `@…@` part). `Sdf.Reference.IsInternal()` returns `True` for such entries.
- The target is composed from the **whole local layer stack** (root layer plus all sublayers), not only from the layer where the reference is written.
- Any prim path may be the target, not only root prims.
- It is still a reference arc: **R** in LIVERPS. Local opinions on the referencing prim win.
- A prim cannot reference itself or one of its own ancestors. That creates a cycle: `Pcp.ErrorType_ArcCycle`.
- Compared with inherits (Chapter 19): both reuse a template, but inherits are stronger (**I** in LIVERPS) and keep working when the whole asset is referenced elsewhere. Use internal references for "start from this", inherits for "always follow this class".

### 5. Mental model

```text
  one layer stack (root.usda + its sublayers)
  +-----------------------------------------+
  |  class "_Crate"  (template, abstract)   |
  |        ^               ^                |
  |        | </_Crate>     | </_Crate>      |
  |   def "Crate_A"    def "Crate_B"        |
  +-----------------------------------------+
  Same building, no asset path, still the R arc.
```

### 6. Simple example

| Prim | Authored | Composed `size` |
|------|----------|-----------------|
| `class "_Crate"` | `size = 1` | not traversed (abstract) |
| `Crate_A` | `references = </_Crate>` | 1 |
| `Crate_B` | `references = </_Crate>`, `size = 3` | 3 (local wins) |

### 7. USDA example

```usda
#usda 1.0

class Cube "_Crate"
{
    double size = 1
}

def "Warehouse"
{
    def "Crate_A" (
        prepend references = </_Crate>
    )
    {
    }

    def "Crate_B" (
        prepend references = </_Crate>
    )
    {
        double size = 3
    }
}
```

Notes: `class Cube "_Crate"` is an abstract template; default traversal skips it. `</_Crate>` has no asset path, so it is internal. `Crate_B` overrides `size` locally.

### 8. Python example

```python
from pxr import Sdf, Usd

stage = Usd.Stage.CreateInMemory()
tpl = stage.CreateClassPrim("/_Crate")
tpl.SetTypeName("Cube")
tpl.CreateAttribute("size", Sdf.ValueTypeNames.Double).Set(1.0)

for name in ["Crate_A", "Crate_B"]:
    crate = stage.DefinePrim(f"/Warehouse/{name}")
    crate.GetReferences().AddInternalReference("/_Crate")

b = stage.GetPrimAtPath("/Warehouse/Crate_B")
b.GetAttribute("size").Set(3.0)

def report(label):
    sizes = [stage.GetPrimAtPath(f"/Warehouse/{n}").GetAttribute("size").Get()
             for n in ["Crate_A", "Crate_B"]]
    print(label, sizes)

print([str(p.GetPath()) for p in stage.Traverse()])
report("before template edit:")
tpl.GetAttribute("size").Set(2.0)       # edit the template once
report("after template edit: ")

ref = b.GetMetadata("references").prependedItems[0]
print("internal?", ref.IsInternal(), "asset path:", repr(ref.assetPath))
```

**Expected output**

```text
['/Warehouse', '/Warehouse/Crate_A', '/Warehouse/Crate_B']
before template edit: [1.0, 3.0]
after template edit:  [2.0, 3.0]
internal? True asset path: ''
```

`Crate_A` followed the template edit. `Crate_B` kept its local value 3.0, because local beats reference.

### 9. Real-world use case

A game level file contains one `class` "pickup" template with a collision shape and score attribute; 200 pickups internally reference it. A lighting file keeps a template light rig and internally references it for each shot camera.

### 10. Common mistakes

> [!MISTAKE] Using a normal `def` prim as the template. It renders as an extra object at its own location. Use a `class` prim (abstract) for templates you do not want to see.

> [!MISTAKE] Referencing an ancestor, e.g. `/A/B` internally referencing `/A`. This is a cycle (`Pcp.ErrorType_ArcCycle`) and is ignored with a warning.

### 11. Exam traps

> [!TRAP] "Internal references only see opinions from the current layer." False. They see the whole local layer stack at the target path.

> [!TRAP] "An internal reference is an inherit." No. It is a reference (R, weaker than I). The USDA keyword `references` versus `inherits` tells them apart.

### 12. Practice questions

**Q1.** Which USDA line is an internal reference?
A. `prepend references = @./crate.usda@` · B. `prepend references = </_Crate>` · C. `prepend inherits = </_Crate>` · D. `subLayers = [@./crate.usda@]`

**Q2.** The template `/_Crate` has `size = 1` in a sublayer and `size = 2` in the root layer. `/Crate_A` internally references `/_Crate` and has no local `size`. What is `/Crate_A.size`?

**Answers**

**Q1 — B.** A prim path with no asset path. C is an inherit; A is external; D is a sublayer.
**Q2 — 2.** The internal reference composes `/_Crate` from the whole layer stack, where the root layer is stronger than its sublayer.

### 13. Exam takeaways

> [!KEY]
> - Internal reference = prim path only (`</Path>`), `AddInternalReference(path)`.
> - It composes the target from the whole local layer stack.
> - Still the R arc: local opinions win; weaker than inherits.
> - Do not reference your own ancestor (cycle error).

---

## 16.4 Reference layer offsets: reusing animation at different times

### 1. What is it?

A **layer offset** on a reference shifts and/or stretches the time samples that come through it. It has two numbers: **offset** (shift, in time codes) and **scale** (speed factor). In Python it is `Sdf.LayerOffset(offset, scale)`.

### 2. Why do we need it?

Objective 1.4 asks you to build a scene where several elements use the **same animation at different time offsets**: a crowd where people start walking at different frames, or three birds flapping out of sync. Without layer offsets you would need a separate copy of the animation for every start frame.

### 3. Beginner explanation

Think of a music track on a timeline in a video editor. You drop the same clip three times: one starts at second 0, one at second 10, and one is slowed to half speed. It is still the same clip file.

Where the analogy breaks: the offset only changes **time samples**. A default (non-animated) value is not affected.

### 4. Technical explanation

- Authoring: `AddReference(assetPath, primPath, Sdf.LayerOffset(offset, scale))`, or `AddReference(assetPath, Sdf.LayerOffset(...))` when you use `defaultPrim`. `AddInternalReference(path, Sdf.LayerOffset(...))` works too. Payloads accept layer offsets the same way.
- USDA: `@anim.usda@ (offset = 10; scale = 2)` after the reference.
- **The formula** (maps a time in the referenced layer to a time on the stage):

```text
  stageTime = offset + scale * layerTime
  layerTime = (stageTime - offset) / scale
```

- `Sdf.LayerOffset` defaults to `(0, 1)`, the identity. You can apply it as `lo * layerTime` and invert it with `lo.GetInverse()`.
- `scale` must be positive. A zero or negative scale gives `Pcp.ErrorType_InvalidReferenceOffset`, and USD uses no offset instead.
- **Nesting:** offsets multiply through chains of arcs. A reference with offset 10 to a file that references with offset 5 places layer time 0 at stage time 15.
- **Automatic scaling:** if the referenced layer's `timeCodesPerSecond` differs from the stage's, USD adds a scale. Verified: a 48-tcps layer referenced into a 24-tcps stage maps samples 0 and 48 to 0 and 24.
- Before the first sample and after the last, values are **held** (Chapter 10), so a shifted clip "waits" at its first pose.
- Sublayers take layer offsets too (Chapter 15). The math is the same.

### 5. Mental model

```text
 layer time:   0 -------- 10 -------- 20        (anim.usda: up and down)
 Ball_A (0,1): 0 -------- 10 -------- 20
 Ball_B (10,1):          10 -------- 20 -------- 30
 Ball_C (0,2): 0 -------------------- 20 ------------------- 40

 stageTime = offset + scale * layerTime
```

### 6. Simple example

The animation peaks at layer time 10. Where is the peak on the stage?

| Layer offset | Calculation | Peak at stage time |
|--------------|-------------|--------------------|
| `(0, 1)` | 0 + 1 × 10 | 10 |
| `(10, 1)` | 10 + 1 × 10 | 20 |
| `(0, 2)` | 0 + 2 × 10 | 20 |
| `(5, 2)` | 5 + 2 × 10 | 25 |

### 7. USDA example

*File: bounce.usda*

```usda
#usda 1.0
(
    defaultPrim = "Ball"
    startTimeCode = 0
    endTimeCode = 20
)

def Xform "Ball"
{
    double3 xformOp:translate.timeSamples = {
        0: (0, 0, 0),
        10: (0, 5, 0),
        20: (0, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
```

*File: shot.usda*

```usda
#usda 1.0
(
    startTimeCode = 0
    endTimeCode = 40
)

def "Ball_A" (
    prepend references = @./bounce.usda@
)
{
}

def "Ball_B" (
    prepend references = @./bounce.usda@ (offset = 10)
)
{
}

def "Ball_C" (
    prepend references = @./bounce.usda@ (scale = 2)
)
{
}
```

Notes: `(offset = 10)` starts Ball_B's bounce 10 frames later. `(scale = 2)` makes Ball_C's bounce last twice as long. When both are present, they are separated by `;`, e.g. `(offset = 5; scale = 2)`.

### 8. Python example

```python
from pxr import Sdf, Usd

BOUNCE = """#usda 1.0
(
    defaultPrim = "Ball"
)
def Xform "Ball"
{
    double3 xformOp:translate.timeSamples = {
        0: (0, 0, 0),
        10: (0, 5, 0),
        20: (0, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
"""
with open("bounce.usda", "w") as f:
    f.write(BOUNCE)

stage = Usd.Stage.CreateInMemory()
offsets = {"Ball_A": Sdf.LayerOffset(),          # identity (0, 1)
           "Ball_B": Sdf.LayerOffset(10),        # start 10 frames later
           "Ball_C": Sdf.LayerOffset(0, 2)}      # half speed
for name, lo in offsets.items():
    stage.DefinePrim("/" + name).GetReferences().AddReference("bounce.usda", lo)

frames = [0, 5, 10, 15, 20, 30, 40]
print("frame ", frames)
for name in offsets:
    attr = stage.GetPrimAtPath("/" + name).GetAttribute("xformOp:translate")
    heights = [attr.Get(t)[1] for t in frames]
    print(name, heights, "samples at", attr.GetTimeSamples())

lo = Sdf.LayerOffset(5, 2)
print("layer t=10 -> stage t =", lo * 10)
print("stage t=25 -> layer t =", lo.GetInverse() * 25)
print(stage.GetRootLayer().ExportToString().split("\n", 1)[1].strip())
```

**Expected output**

```text
frame  [0, 5, 10, 15, 20, 30, 40]
Ball_A [0.0, 2.5, 5.0, 2.5, 0.0, 0.0, 0.0] samples at [0.0, 10.0, 20.0]
Ball_B [0.0, 0.0, 0.0, 2.5, 5.0, 0.0, 0.0] samples at [10.0, 20.0, 30.0]
Ball_C [0.0, 1.25, 2.5, 3.75, 5.0, 2.5, 0.0] samples at [0.0, 20.0, 40.0]
layer t=10 -> stage t = 25.0
stage t=25 -> layer t = 10.0
def "Ball_A" (
    prepend references = @bounce.usda@
)
{
}

def "Ball_B" (
    prepend references = @bounce.usda@ (offset = 10)
)
{
}

def "Ball_C" (
    prepend references = @bounce.usda@ (scale = 2)
)
{
}
```

Check one value by hand: Ball_C at stage frame 15 → layer time (15 − 0) / 2 = 7.5 → height 0.75 × 5 = 3.75. Ball_B at frame 5 → layer time −5, before the first sample, so the first value (0) is held.

### 9. Real-world use case

Crowd animation: one walk-cycle asset is referenced by 1,000 extras, each with a different offset so they do not move in lockstep. In games cinematics, the same flag-waving animation is reused on many flags with offsets. In manufacturing simulation, the same robot-arm motion is replayed on several cells, each starting when its part arrives.

### 10. Common mistakes

> [!MISTAKE] Getting the direction wrong. `offset = 10` makes the animation happen **later** on the stage (layer frame 0 shows at stage frame 10), not earlier.

> [!MISTAKE] Expecting `scale = 2` to make the animation faster. Scale stretches layer time: `2` means twice as long, i.e. half speed. Use `0.5` for double speed.

> [!MISTAKE] Adding an offset to a reference whose attribute only has a default value. Nothing changes, because offsets affect time samples only.

### 11. Exam traps

> [!TRAP] Formula look-alikes. The correct mapping is `stage = offset + scale × layer`. A distractor might show `stage = (layer + offset) × scale`; with offset 5 and scale 2 that gives 30 instead of 25 for layer time 10.

> [!TRAP] "Layer offsets can only be set on sublayers." False. References, internal references, and payloads each carry their own `layerOffset`.

### 12. Practice questions

**Q1.** A reference has `(offset = 24; scale = 0.5)`. A key is at layer time 48. At what stage time does it appear?
A. 24 · B. 48 · C. 72 · D. 120

**Q2.** Which Python call references `walk.usda` (through its `defaultPrim`) so that its animation starts 30 frames later?
A. `refs.AddReference("walk.usda", Sdf.LayerOffset(30))`
B. `refs.AddReference("walk.usda", Sdf.LayerOffset(0, 30))`
C. `refs.AddReference("walk.usda", Sdf.LayerOffset(-30))`
D. `refs.AddInternalReference("walk.usda", 30)`

**Q3.** A layer at 48 `timeCodesPerSecond` is referenced into a 24 tcps stage with no authored offset. A sample is at layer time 48. At what stage time is it?

**Answers**

**Q1 — B.** 24 + 0.5 × 48 = 24 + 24 = 48. C (72) forgets the scale: 24 + 48.
**Q2 — A.** `LayerOffset(offset=30)`. B is a scale of 30; C moves it earlier; D is not a valid call for a file.
**Q3 — 24.** USD adds an automatic scale of 24/48 = 0.5 (one second of the layer = one second of the stage).

### 13. Exam takeaways

> [!KEY]
> - `Sdf.LayerOffset(offset, scale)`; default `(0, 1)`.
> - `stageTime = offset + scale × layerTime`. Positive offset = later; scale 2 = slower.
> - Offsets affect time samples, not default values; outside the samples, values are held.
> - Each reference has its own offset, so one animation file can drive many prims at different times.

---

## 16.5 Why adding a reference may fail

### 1. What is it?

A list of the common reasons why a reference you wrote does not bring in the content you expect, and how to see the cause.

### 2. Why do we need it?

A failed reference rarely crashes anything. The stage opens, the prim exists, and it is simply empty or missing parts. If you do not know where USD reports these problems, you can lose hours. The exam's reading list names "reasons adding a reference may fail" and "Pcp composition errors" directly.

### 3. Beginner explanation

Your catalog link can break in a few ways: the catalog is not on the shelf (missing file), the item number does not exist (wrong prim path), nobody marked "the product" (no `defaultPrim`), or the link points back at itself (a loop). The shop still opens; that one shelf is just empty, and a note is pinned on the notice board (the error list).

Where the analogy breaks: some mistakes are refused immediately at authoring time (badly written prim paths), not later.

### 4. Technical explanation

Two moments can fail:

1. **Authoring time** (when you call `AddReference`). A prim path that is not empty or not an absolute prim path (`"Chair"`, `"/Chair.size"`, `"/Chair{v=a}"`) raises `Tf.ErrorException` and nothing is written.
2. **Composition time** (when the stage composes). Problems become **composition errors**: they are printed as warnings and collected in `stage.GetCompositionErrors()`. Each error object has `errorType` and `rootSite.path` (the prim where it happened). For one prim, `prim.GetPrimIndex().localErrors` lists them.

| Cause | What you see (verified on 26.08) |
|-------|----------------------------------|
| File cannot be found or opened (wrong path, wrong anchoring, parse error) | `Pcp.ErrorType_InvalidAssetPath` |
| No `defaultPrim` and no prim path | `Pcp.ErrorType_UnresolvedPrimPath` (`<defaultPrim>` in message) |
| Prim path or `defaultPrim` names a prim that does not exist | `Pcp.ErrorType_UnresolvedPrimPath` |
| Prim references itself or an ancestor | `Pcp.ErrorType_ArcCycle` |
| Layer offset scale ≤ 0 | `Pcp.ErrorType_InvalidReferenceOffset`; USD uses no offset |
| Relationship in the asset targets a prim outside the referenced prim | No composition error; target is dropped with a warning when you call `GetTargets()` |

> [!NOTE] Other causes exist but are not reference-specific: the referencing prim is inactive (Chapter 4), the layer is muted (Chapter 15), or a stronger opinion hides the value (Chapter 21).

> [!VERSION] Verified on USD 26.08: `Usd.Stage.GetCompositionErrors()` returns `Pcp` error objects; `AddReference` returns `True` even when composition later fails.

### 5. Mental model

```text
 AddReference(...)
     |
     +-- bad prim path syntax? --> Tf.ErrorException now (nothing authored)
     |
     v  authored OK (returns True)
 stage composes
     |
     +-- file? ----------> no  --> InvalidAssetPath
     +-- prim / default? -> no  --> UnresolvedPrimPath
     +-- loops back? ----> yes --> ArcCycle
     +-- scale <= 0? ----> yes --> InvalidReferenceOffset
     v
 content appears  (check: stage.GetCompositionErrors() == [])
```

### 6. Simple example

You reference `@props/cup.usda@` from `shots/s01.usda`. The file is at `props/cup.usda` next to `shots/`. USD anchors to `shots/` and looks for `shots/props/cup.usda`, which does not exist: `InvalidAssetPath`. The fix is `@../props/cup.usda@`.

### 7. USDA example

This layer parses, but three of its four references fail when composed (assume `good.usda` exists and has `defaultPrim`, `nodefault.usda` exists without one, and `missing.usda` does not exist).

```usda
#usda 1.0

def "Broken"
{
    def "MissingFile" (
        prepend references = @./missing.usda@
    )
    {
    }

    def "NoDefaultPrim" (
        prepend references = @./nodefault.usda@
    )
    {
    }

    def "WrongPath" (
        prepend references = @./good.usda@</Nope>
    )
    {
    }

    def "Works" (
        prepend references = @./good.usda@
    )
    {
    }
}
```

### 8. Python example

```python
from pxr import Sdf, Tf, Usd

files = {
    "good.usda": '#usda 1.0\n(\n    defaultPrim = "Chair"\n)\n'
                 'def Xform "Chair"\n{\n    def Cube "Seat" {}\n}\n',
    "nodefault.usda": '#usda 1.0\ndef Xform "Chair"\n{\n}\n',
}
for name, text in files.items():
    with open(name, "w") as f:
        f.write(text)

stage = Usd.Stage.CreateInMemory()
def ref(path, *args):
    stage.DefinePrim(path).GetReferences().AddReference(*args)

ref("/MissingFile", "missing.usda")
ref("/NoDefaultPrim", "nodefault.usda")
ref("/WrongPath", "good.usda", "/Nope")
ref("/BadScale", Sdf.Reference("good.usda", Sdf.Path(), Sdf.LayerOffset(0, -1)))
ref("/Works", "good.usda")
cyc = stage.DefinePrim("/Loop/Child")
cyc.GetReferences().AddInternalReference("/Loop")

for err in sorted(stage.GetCompositionErrors(), key=lambda e: str(e.rootSite.path)):
    print(f"{str(err.rootSite.path):15} {err.errorType}")

works = stage.GetPrimAtPath("/Works")
print("Works children:", [c.GetName() for c in works.GetChildren()])

try:
    ref("/Relative", "good.usda", "Chair")      # not an absolute prim path
except Tf.ErrorException:
    print("authoring refused: prim path must be absolute")
```

**Expected output**

```text
/BadScale       Pcp.ErrorType_InvalidReferenceOffset
/Loop/Child     Pcp.ErrorType_ArcCycle
/MissingFile    Pcp.ErrorType_InvalidAssetPath
/NoDefaultPrim  Pcp.ErrorType_UnresolvedPrimPath
/WrongPath      Pcp.ErrorType_UnresolvedPrimPath
Works children: ['Seat']
authoring refused: prim path must be absolute
```

The errors are sorted by path here so the output is stable; `GetCompositionErrors()` itself does not promise an order. You will also see matching warnings on stderr. Note that `/BadScale` still gets its content; only the offset is ignored.

The next script shows the relationship case, which produces **no** composition error:

```python
from pxr import Usd

ASSET = """#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair"
{
    rel look = </Looks/Wood>
    rel seat = </Chair/Seat>
    def Cube "Seat" {}
}
def Scope "Looks"
{
    def "Wood" {}
}
"""
with open("asset.usda", "w") as f:
    f.write(ASSET)

stage = Usd.Stage.CreateInMemory()
chair = stage.DefinePrim("/World/Chair_01")
chair.GetReferences().AddReference("asset.usda")
print("seat targets:", chair.GetRelationship("seat").GetTargets())
print("look targets:", chair.GetRelationship("look").GetTargets())
print("composition errors:", len(stage.GetCompositionErrors()))
```

**Expected output**

```text
seat targets: [Sdf.Path('/World/Chair_01/Seat')]
look targets: []
composition errors: 0
```

`seat` points inside the referenced prim, so it was remapped. `look` points to `/Looks`, a sibling that the reference does not bring in, so the target is dropped (stderr warning: "refers to a path outside the scope of the reference"). This is why material assets keep their `Looks` scope **inside** the root prim (Chapter 23).

### 9. Real-world use case

A layout artist reports "the hero car is invisible in shot 12." The pipeline TD opens the shot in Python, prints `stage.GetCompositionErrors()`, and sees `InvalidAssetPath` for `@../assets/car.usda@`: the shot file had moved one folder deeper. Many studios run this check automatically at publish time.

### 10. Common mistakes

> [!MISTAKE] Checking only the return value of `AddReference`. It reports authoring success, not composition success. Check `stage.GetCompositionErrors()` after authoring.

> [!MISTAKE] Keeping materials in a root scope beside the asset's root prim. Bindings to them break when the asset is referenced. Put `Looks` under the `defaultPrim`.

> [!MISTAKE] Ignoring stderr. USD's warnings name the prim, the asset path, and the reason.

### 11. Exam traps

> [!TRAP] "A missing referenced file stops the stage from opening." False. The stage opens; that arc contributes nothing, and an `InvalidAssetPath` error is recorded.

> [!TRAP] "Relationship targets outside the referenced prim are remapped to the new location." False. Only targets inside the referenced subtree are remapped; outside targets are ignored.

> [!TRAP] Wrong prim path and missing `defaultPrim` are the **same** error type (`UnresolvedPrimPath`), not two different ones.

### 12. Practice questions

**Q1.** Which call shows composition problems for the whole stage?
A. `stage.Validate()` · B. `stage.GetCompositionErrors()` · C. `prim.GetReferences().GetErrors()` · D. `Sdf.Layer.GetErrors()`

**Q2.** Select two. Which mistakes cause `Pcp.ErrorType_UnresolvedPrimPath`?
A. The asset file does not exist.
B. The reference names `</Car>`, but the file only has `/Truck`.
C. The file has no `defaultPrim` and the reference has no prim path.
D. The layer offset scale is −1.

**Q3.** `AddReference("chair.usda", "Chair")` is called. What happens?

**Answers**

**Q1 — B.** The other methods do not exist.
**Q2 — B, C.** A gives `InvalidAssetPath`; D gives `InvalidReferenceOffset`.
**Q3** — A `Tf.ErrorException` is raised at authoring time, because the prim path must be empty or absolute (`/Chair`). Nothing is authored.

### 13. Exam takeaways

> [!KEY]
> - Bad prim-path syntax fails at authoring; everything else fails at composition and the stage still opens.
> - Missing file → `InvalidAssetPath`; missing prim or `defaultPrim` → `UnresolvedPrimPath`; loops → `ArcCycle`.
> - Use `stage.GetCompositionErrors()` (or `prim.GetPrimIndex().localErrors`) and read stderr.
> - Relationship targets outside the referenced prim are dropped silently from the result.

---

## 16.6 References vs. sublayers

### 1. What is it?

A comparison of the two most-used ways to bring another file into a scene. A **sublayer** adds a whole layer to your layer stack (Chapter 15). A **reference** brings one prim's subtree from a layer into one prim of your stage.

### 2. Why do we need it?

Objective 1.3 asks you to compare referencing, payloads, and sublayers and choose among them. Picking the wrong one causes real bugs: duplicated prims at the wrong paths, or overrides that cannot win.

### 3. Beginner explanation

A **sublayer** is another transparent sheet stacked on the projector: it covers the whole picture, at the same positions. A **reference** is a sticker of one catalog part that you can place anywhere on your sheet, as many times as you like.

Where the analogy breaks: a sublayer's sheet sits *in your own stack*, so it counts as local (L). A sticker's contents are always weaker than anything written on your sheets.

### 4. Technical explanation

| Question | Sublayer | Reference |
|----------|----------|-----------|
| What comes in? | Every prim in the layer, at the **same paths** | One target prim and its subtree, **renamed** to the referencing prim |
| Where is it authored? | Layer metadata: `subLayers = [@a.usda@]` | Prim metadata: `references = @a.usda@</X>` |
| Python | `layer.subLayerPaths.append(...)` | `prim.GetReferences().AddReference(...)` |
| Strength | Part of the local layer stack (**L**), ordered by position in `subLayers` | **R** arc: weaker than every local opinion |
| Use many times at different paths? | No | Yes |
| Layer offset? | Yes (per sublayer) | Yes (per reference) |
| Can target a prim? | No | Yes (or `defaultPrim`) |
| Typical use | Departments' work layers on one shot; overrides for a whole scene | Assets placed into sets and shots |

Both are always loaded. A payload (Chapter 17) is like a reference that can be left unloaded, and is weaker (**P** comes after **R**).

### 5. Mental model

```text
 SUBLAYER: same paths, whole layer, inside your stack (L)
   root.usda  [ /Set/Table  /Set/Lamp ]
   + base.usda[ /Set/Table  /Set/Rug  ]   -> /Set/Table, /Set/Lamp, /Set/Rug

 REFERENCE: one prim, new path, separate stack (R)
   /Set/Rug_01 --R--> rug.usda</Rug>    -> /Set/Rug_01/...
   /Set/Rug_02 --R--> rug.usda</Rug>    -> /Set/Rug_02/...
```

### 6. Simple example

The animation department writes `anim.usda` with overrides for every character in the shot. Lighting writes `light.usda`. The shot file **sublayers** both. Each character is **referenced** into the shot from its asset file. Both arcs are used, each for its own job.

### 7. USDA example

*File: shot.usda*

```usda
#usda 1.0
(
    subLayers = [
        @./shot_anim.usda@,
        @./shot_layout.usda@
    ]
)

def Xform "Set"
{
    def "Rug_01" (
        prepend references = @./rug.usda@
    )
    {
    }

    def "Rug_02" (
        prepend references = @./rug.usda@
    )
    {
    }
}
```

Notes: `subLayers` is in the layer header and lists whole layers (strongest first). `references` is on individual prims; the same rug is used twice at two paths.

### 8. Python example

This script puts the same prim path in a sublayer and in a reference, then shows which wins and what each brings in.

```python
from pxr import Usd

files = {
    "base.usda": """#usda 1.0
def Sphere "Ball"
{
    double radius = 3
}
def Xform "Extra" {}
""",
    "ball_asset.usda": """#usda 1.0
(
    defaultPrim = "Ball"
)
def Sphere "Ball"
{
    double radius = 1
    custom string madeBy = "asset"
}
def Xform "Unused" {}
""",
}
for name, text in files.items():
    with open(name, "w") as f:
        f.write(text)

stage = Usd.Stage.CreateInMemory()
stage.GetRootLayer().subLayerPaths.append("base.usda")      # whole layer
ball = stage.OverridePrim("/Ball")
ball.GetReferences().AddReference("ball_asset.usda")         # one prim

print("prims:", [str(p.GetPath()) for p in stage.Traverse()])
print("radius:", ball.GetAttribute("radius").Get())
print("madeBy:", ball.GetAttribute("madeBy").Get())
stack = ball.GetAttribute("radius").GetPropertyStack()
print("radius opinions, strongest first:",
      [spec.layer.identifier.split("/")[-1] for spec in stack])
```

**Expected output**

```text
prims: ['/Ball', '/Extra']
radius: 3.0
madeBy: asset
radius opinions, strongest first: ['base.usda', 'ball_asset.usda']
```

What to notice:

- The sublayer brought **both** of its root prims (`/Ball`, `/Extra`) at their own paths.
- The reference brought only `/Ball`'s content; its sibling `/Unused` did not appear.
- `radius` is 3: the sublayer's opinion is local (L) and beats the referenced one (R).
- `madeBy` exists only in the reference, so it comes through.

### 9. Real-world use case

In a VFX shot, the shot file sublayers department layers (layout, animation, FX, lighting) so each team edits its own file at the same prim paths (Chapter 15). Inside the layout layer, every prop and character is a reference to a published asset. In a digital twin, a plant file sublayers a "live sensor overrides" layer and references each machine's asset.

### 10. Common mistakes

> [!MISTAKE] Sublayering an asset file to "add a chair." The chair appears at its own root path (e.g. `/Chair`), and you cannot place a second copy. Reference it instead.

> [!MISTAKE] Referencing a department's work layer into a shot. Its opinions become weaker than every local opinion, so lighting tweaks may "not work." Sublayer department layers instead.

### 11. Exam traps

> [!TRAP] "Sublayers and references have the same strength if they are in the same file." False. Sublayer content is local (L); referenced content is R and always weaker than any local opinion.

> [!TRAP] "You can sublayer a single prim." False. Sublayers are whole layers; only references and payloads can target a prim.

### 12. Practice questions

**Q1.** You need 30 copies of a tree asset at different positions. Which arc fits best?
A. Sublayer the tree file 30 times · B. Reference the tree file from 30 prims · C. One sublayer with 30 offsets · D. Copy the tree with `Sdf.CopySpec`

**Q2.** Select two. Which are true of sublayers but **not** of references?
A. They bring every prim at its original path.
B. They can carry a layer offset.
C. Their opinions are part of the local layer stack.
D. They can target a specific prim path.

**Answers**

**Q1 — B.** References place one asset at many paths. D works but loses the live link to the asset.
**Q2 — A, C.** Both arcs accept layer offsets (B); only references target a prim (D).

### 13. Exam takeaways

> [!KEY]
> - Sublayer = whole layer, same paths, local strength (L).
> - Reference = one prim subtree, new path, R strength, reusable many times.
> - Shots sublayer department layers and reference assets.
> - Payload = reference you can unload, and slightly weaker (Chapter 17).

---

## Chapter lab(s)

- **Lab 13 — External and internal references, `defaultPrim`** (★☆☆). You build a prop asset with and without `defaultPrim`, reference it into a room, add internal references to a class template, and read the composition errors.
- **Lab 14 — Same animation at different time offsets** (★★☆). You reference one animated asset into a crowd of prims with different `Sdf.LayerOffset` values and verify the times by sampling the stage (Obj 1.4).

Both labs are in Part X (`python-labs/`).

## USDA reading exercises

**Exercise 16-A.** Given these two files, what is `/Shot/Bird_2`'s `wingAngle` at stage time 20?

*File: flap.usda*

```usda
#usda 1.0
(
    defaultPrim = "Bird"
)

def Xform "Bird"
{
    double wingAngle.timeSamples = {
        0: 0,
        10: 90,
    }
}
```

*File: shot.usda*

```usda
#usda 1.0

def "Shot"
{
    def "Bird_2" (
        prepend references = @./flap.usda@ (offset = 5; scale = 2)
    )
    {
    }
}
```

**Exercise 16-B.** `prop.usda` contains only `def Xform "Prop" {}` and no layer metadata. A shot writes `def "P" ( prepend references = @./prop.usda@ ) {}`. What is `/P`'s type, what error is recorded, and give two ways to fix it.

**Exercise 16-C.** In this layer, what is the composed `size` of `/Crate_B`, and which arc supplied it?

```usda
#usda 1.0

class Cube "_Crate"
{
    double size = 4
}

def "Crate_B" (
    prepend references = </_Crate>
)
{
}
```

**Answers**

**16-A — 67.5.** Layer time = (20 − 5) / 2 = 7.5. Linear interpolation between 0 and 90: 0.75 × 90 = 67.5.

**16-B** — Type is empty (`''`); error `Pcp.ErrorType_UnresolvedPrimPath`. Fix 1: add `defaultPrim = "Prop"` to `prop.usda`. Fix 2: write the prim path explicitly, `@./prop.usda@</Prop>`.

**16-C — 4,** from the internal reference to `/_Crate` (an R arc). `Crate_B` is a `Cube` because it receives the template's type too.

---

## Chapter review

### Summary

- A reference brings one target prim and its subtree into a referencing prim, renaming paths.
- Authoring: `prim.GetReferences().AddReference(assetPath, primPath, layerOffset)`; it writes `prepend references`.
- Without a prim path, the referenced layer's `defaultPrim` is used; without one, `UnresolvedPrimPath`.
- Internal references (`</Path>`, `AddInternalReference`) reuse prims from the same layer stack.
- References are the R arc: weaker than all local opinions, stronger than payloads.
- `Sdf.LayerOffset(offset, scale)`: `stageTime = offset + scale × layerTime`.
- Different offsets on several references let one animation play at different times (Obj 1.4).
- Composition failures do not stop the stage; read `stage.GetCompositionErrors()` and stderr.
- Relationship targets outside the referenced subtree are dropped.
- Sublayers = whole layers, same paths, local strength; references = one prim, any path, R strength.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `@file.usda@` with no `<path>` | `defaultPrim` of that file is used |
| `</Path>` with no `@…@` | Internal reference |
| `(offset = a; scale = b)` | stage = a + b × layer |
| Prim exists but is empty after referencing | `GetCompositionErrors()`: missing file, missing prim/`defaultPrim` |
| "Same asset placed many times" | References (or payloads), not sublayers |
| "Department layers at the same paths" | Sublayers |
| Local `over` vs. referenced value | Local wins (L before R) |
| `Tf.ErrorException` from `AddReference` | Prim path not absolute or not a prim path |
| Material binding lost after referencing | Target outside the referenced prim |

### Review questions

**R16-01** · Obj 1.3 · Single choice
Which statement about a reference is correct?
A. It copies the target prim's data into the referencing layer.
B. It brings the target prim and its descendants, mapped to the referencing prim's path.
C. It brings every root prim of the referenced layer.
D. It is stronger than local opinions.

**R16-02** · Obj 1.3 · Single choice
`asset.usda` defines one root prim, `/Robot`, and has `defaultPrim = "Robot"`. Another file needs `/Robot`. Which reference brings it in?
A. `@asset.usda@` · B. `@asset.usda@</Asset>` · C. `</Robot>` · D. `subLayers = [@asset.usda@]`

**R16-03** · Obj 1.4 · Single choice
A reference has `(offset = 12)`. The asset's first sample is at layer time 0. At which stage time is it?
A. −12 · B. 0 · C. 12 · D. 24

**R16-04** · Obj 1.4 · Single choice
Which `Sdf.LayerOffset` plays a referenced animation at double speed, starting at stage time 0?
A. `Sdf.LayerOffset(0, 2)` · B. `Sdf.LayerOffset(0, 0.5)` · C. `Sdf.LayerOffset(2)` · D. `Sdf.LayerOffset(0.5)`

**R16-05** · Obj 1.4 · Python reading
What does this print? (Marked "not run automatically" so the answer is not printed next to the question; run it yourself after answering.)

```{.python .norun}
from pxr import Sdf

lo = Sdf.LayerOffset(10, 3)
print(lo * 4)
```

A. 14.0 · B. 22.0 · C. 42.0 · D. 52.0

**R16-06** · Obj 1.3 · Select two.
After `prim.GetReferences().AddReference("lamp.usda")`, nothing appears under the prim. Which checks are useful?
A. Print `stage.GetCompositionErrors()`.
B. Check that `lamp.usda` has a `defaultPrim`.
C. Check the return value of `AddReference`.
D. Check the stage's `upAxis`.

**R16-07** · Obj 1.3 · USDA reading
`base.usda` (a sublayer of the root layer) sets `/Car.color = "blue"`. The root layer has `over "Car" ( prepend references = @car.usda@ ) {}`, and `car.usda`'s default prim sets `color = "red"`. What is the composed color?
A. red · B. blue · C. empty · D. It is an error

**R16-08** · Obj 1.3 · Single choice
Which USDA line is an internal reference?
A. `prepend references = @./x.usda@</X>` · B. `prepend references = </X>` · C. `prepend payload = </X>` · D. `prepend inherits = </X>`

**R16-09** · Obj 1.3 · Single choice
The prim `/A/B` adds an internal reference to `/A`. What happens?
A. `/A/B` gets a copy of `/A`, including `/A/B` again.
B. A `Pcp.ErrorType_ArcCycle` composition error; the arc is ignored.
C. `AddInternalReference` raises an exception.
D. The stage fails to open.

**R16-10** · Obj 1.3 · Select two.
Which are true for sublayers but not for references?
A. Content keeps its original prim paths.
B. Content is weaker than every local opinion.
C. Opinions are part of the local layer stack.
D. The same file can be placed at many prim paths.

**R16-11** · Obj 1.3 · Single choice
An asset's root prim `/Chair` has `rel material = </Looks/Oak>`, where `/Looks` is a root sibling of `/Chair`. After referencing the asset at `/Room/Chair_1`, what does `GetTargets()` on `material` return?
A. `[/Looks/Oak]` · B. `[/Room/Chair_1/Looks/Oak]` · C. `[/Room/Looks/Oak]` · D. `[]`

**R16-12** · Obj 1.4 · Single choice
Three prims reference `walk.usda` with offsets 0, 8, and 16 (scale 1). The walk cycle has samples from 0 to 24. Which is true at stage time 4?
A. All three show the pose at layer time 4.
B. Prim 1 shows layer time 4; prims 2 and 3 hold their first pose.
C. Prims 2 and 3 show layer times 12 and 20.
D. Prims 2 and 3 have no value.

### Review answers

**R16-01 — B** (Obj 1.3). The reference is a live link (not A); only the target subtree comes in (not C); R is weaker than L (not D). Review: §16.1.

**R16-02 — A** (Obj 1.3). No prim path means "use `defaultPrim`". B names a prim `/Asset` that does not exist (`UnresolvedPrimPath`); C is internal (same layer stack); D is a sublayer and brings all root prims at their own paths. Review: §16.2.

**R16-03 — C** (Obj 1.4). 12 + 1 × 0 = 12. A positive offset moves the animation later. Review: §16.4.

**R16-04 — B** (Obj 1.4). Scale 0.5 compresses layer time: layer time 10 appears at stage time 5. A is half speed; C and D are offsets with scale 1. Review: §16.4.

**R16-05 — B** (Obj 1.4). `lo * 4` = 10 + 3 × 4 = 22, printed as `22.0`. C would be (4 + 10) × 3; D is not a possible combination of the formula. Review: §16.4.

**R16-06 — A, B** (Obj 1.3). Composition errors list the cause; a missing `defaultPrim` is the most common one. `AddReference` returns `True` even when composition fails (C), and `upAxis` is unrelated (D). Review: §16.5.

**R16-07 — B** (Obj 1.3). The sublayer is in the local layer stack (L), so its "blue" beats the referenced "red" (R). Review: §16.6.

**R16-08 — B** (Obj 1.3). Prim path only, keyword `references`. C is an internal payload; D is an inherit. Review: §16.3.

**R16-09 — B** (Obj 1.3). Verified: the reference is authored, then composition reports `ArcCycle` and ignores it; the stage opens. Review: §16.3, §16.5.

**R16-10 — A, C** (Obj 1.3). B and D describe references. Review: §16.6.

**R16-11 — D** (Obj 1.3). The target is outside the referenced subtree, so it is dropped (with a warning). Keep `Looks` under the root prim. Review: §16.5.

**R16-12 — B** (Obj 1.4). Prim 2 is at layer time 4 − 8 = −4 and prim 3 at −12, both before the first sample, so the first pose is held. Review: §16.4.

## Further reading

- [S04] OpenUSD Glossary — entries "References", "Default Prim", "LayerOffset", "LIVERPS": https://openusd.org/release/glossary.html
- [S05] OpenUSD tutorials — "Referencing Layers" and "Transformations, Time-sampled Animation, and Layer Offsets": https://openusd.org/release/tut_usd_tutorials.html
- [S06] OpenUSD API reference — `UsdReferences`, `SdfReference`, `SdfLayerOffset`, `UsdStage::GetCompositionErrors`: https://openusd.org/release/api/index.html
- [S08] OpenUSD FAQ — sublayers versus references: https://openusd.org/release/usdfaq.html
- [S14] NVIDIA Learn OpenUSD — "Creating Composition Arcs": https://docs.nvidia.com/learn-openusd/latest/index.html
