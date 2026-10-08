# Chapter 24 — Native Scenegraph Instancing

> **Exam domain:** Content Aggregation (10%) · **Objectives:** 1.10, 2.2, 2.4, 2.5 · **Study day:** 8 · **Est. time:** 120 min
> **Prerequisites:** Ch 16 (references), Ch 18 (variants), Ch 19 (inherits), Ch 20 (overs), Ch 22.4 (instanced components)

Native instancing is OpenUSD's "rubber stamp": many prims share one prototype in memory. The exam asks you to turn it on, find the prototype, explain instance proxies, and change one copy's look **without** authoring on a proxy (Obj 1.10, 2.5).

## Learning goals

- Mark referencing prims `instanceable` and confirm they become instances.
- Find the prototype with `GetPrototype` / `GetPrototypes` (never `GetMaster`).
- Describe instance proxies and why default `Traverse()` skips them.
- Edit a shared look at the source, or uninstance one copy, without writing on a proxy.
- Vary copies with inherits, variants, and primvars on the **instance root**.
- Remove or hide parts of an instanced component using a class or variant, not a nested `over`.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Native instancing** | Sharing one prototype prim tree among many instanceable prims |
| **`instanceable`** | Metadata on a prim: "I am willing to be an instance" |
| **Instance** | A prim for which `IsInstance()` is True; it has a prototype |
| **Instance root** | That prim itself (you may author on it) |
| **Prototype** | The hidden, shared prim tree (`/__Prototype_N`); not saved in the layer |
| **Instance proxy** | A descendant you see under an instance; it stands for a prototype prim |
| **`GetMaster`** | Removed name. Use `GetPrototype` (USD 21.x+) |
| **De-instance** | `SetInstanceable(False)` so that copy is unique again |

---

## 24.1 `instanceable`

### 1. What is it?

**`instanceable`** is prim metadata. When it is true, and the prim's composed descendants match other instanceable prims, USD may make those prims **instances** of one shared prototype.

### 2. Why do we need it?

A stadium of 5 000 identical seats should not compose 5 000 copies of the mesh in memory. Instancing keeps one seat in the prototype and stamps it everywhere. Payloads help load time; instancing helps **memory** and **compose time** once the asset is loaded (Chapter 26).

### 3. Beginner explanation

Think of a **rubber stamp**. You carve the chair once (`/Chair`). Each `instanceable` reference is an ink stamp on the page. The ink is shared. Changing the carving changes every stamp. Writing on one *ink print* with a pen is not allowed — that is authoring on a proxy (24.3).

*Where the analogy breaks:* stamps that select a different variant, or inherit a different class, are carved differently: USD makes **another** prototype (24.5). The source `/Chair` remains in the scene; it is not the prototype path.

### 4. Technical explanation

- Author `instanceable = true` in USDA, or `prim.SetInstanceable(True)` in Python. `IsInstanceable()` is the authored/composed flag. `IsInstance()` is True only when USD actually built a prototype for that prim.
- Typical pattern: a typeless `def` that **references** an asset (or internally references a prototype prim) and is instanceable. The referenced subtree is what gets shared.
- Matching instances share a prototype when their composition (references, variant selections, inherits, …) is the same. Different selections → different prototypes.
- Default `Traverse()` visits the instance **root** but **not** its proxy descendants. `GetPrimAtPath("/Room/A/Seat")` still works.
- Prototypes are **not** written to the layer. Saving the stage does not create `/__Prototype_1` specs.

> [!VERSION] Verified on USD 26.08. Native instancing "master" prims were renamed "prototype" and `GetMaster`/`GetMasters` were deprecated in USD 20.11; the deprecated master API was **removed** in 21.08. Use `GetPrototype()`.

### 5. Mental model

```text
  /Chair          (source prim; ordinary, editable)
     Seat

  /Room/A  instanceable=true, references </Chair>   ---\
  /Room/B  instanceable=true, references </Chair>   ---+--> prototype /__Prototype_1
                                                            Seat (shared)
```

### 6. Simple example

Two instanceable internal references to `/Chair`. Both `IsInstance()` True. `Traverse()` lists `/Chair`, `/Chair/Seat`, `/Room`, `/Room/A`, `/Room/B` — not `/Room/A/Seat`.

### 7. USDA example

```usda
#usda 1.0

def Xform "Chair"
{
    def Cube "Seat"
    {
    }
}

def Xform "Room"
{
    def "A" (
        instanceable = true
        prepend references = </Chair>
    )
    {
    }

    def "B" (
        instanceable = true
        prepend references = </Chair>
    )
    {
    }
}
```

Line notes: `instanceable = true` is prim metadata next to the reference. The source `/Chair` stays a normal prim. A and B are the instance roots.

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/Chair")
UsdGeom.Cube.Define(stage, "/Chair/Seat")
a = stage.DefinePrim("/Room/A")
a.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
a.SetInstanceable(True)
b = stage.DefinePrim("/Room/B")
b.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
b.SetInstanceable(True)
print("A IsInstanceable/IsInstance:", a.IsInstanceable(), a.IsInstance())
print("B IsInstanceable/IsInstance:", b.IsInstanceable(), b.IsInstance())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
A IsInstanceable/IsInstance: True True
B IsInstanceable/IsInstance: True True
Traverse: ['/Chair', '/Chair/Seat', '/Room', '/Room/A', '/Room/B']
#usda 1.0

def Xform "Chair"
{
    def Cube "Seat"
    {
    }
}

def "Room"
{
    def "A" (
        instanceable = true
        prepend references = </Chair>
    )
    {
    }

    def "B" (
        instanceable = true
        prepend references = </Chair>
    )
    {
    }
}

```

### 9. Real-world use case

A city block references `streetlamp.usda` two hundred times with `instanceable = true`. Memory holds one lamp prototype. Layout still sees two hundred roots to place.

### 10. Common mistakes

> [!MISTAKE] Setting `instanceable` on the **source** `/Chair` only. The *referencing* prims must be instanceable.

> [!MISTAKE] Expecting `Traverse()` to list `/Room/A/Seat`. Use `GetPrimAtPath` or `Usd.TraverseInstanceProxies()`.

### 11. Exam traps

> [!TRAP] "`instanceable` copies the mesh into the referencing layer." It shares a prototype; the layer only stores the flag and the reference.

> [!TRAP] "`IsInstanceable` and `IsInstance` are the same." The flag can be true on a prim that is not currently an instance (for example it has no sharable composition yet).

### 12. Practice questions

**CA-024a** · Obj 2.2 · Difficulty: Easy · Type: Single choice
Where do you author `instanceable = true` for native instancing of a referenced chair?

A. Only on `/Chair` in the asset file
B. On each referencing prim that should be an instance
C. As layer metadata
D. On every descendant mesh

**CA-024b** · Obj 2.2 · Difficulty: Medium · Type: Single choice
Default `stage.Traverse()` on a stage with instanceable `/Room/A` referencing `/Chair/Seat` visits:

A. `/Room/A` but not `/Room/A/Seat`
B. `/Room/A/Seat` but not `/Room/A`
C. `/__Prototype_1` only
D. Nothing under `/Room`

**Answers**

**CA-024a — B.** The instance roots are the referencing prims. Review: §24.1.

**CA-024b — A.** Proxy descendants are skipped. Review: §24.1, §24.3.

### 13. Exam takeaways

> [!KEY]
> - `instanceable = true` on the referencing prim.
> - `IsInstance()` means a prototype exists.
> - `Traverse()` skips proxy children; the source prim remains editable.
> - Prototypes are not saved into the layer.

---

## 24.2 Prototypes (`GetPrototype`)

### 1. What is it?

A **prototype** is the shared prim tree USD builds for a set of matching instances. You reach it with `prim.GetPrototype()` or `stage.GetPrototypes()`. Its path looks like `/__Prototype_1`.

### 2. Why do we need it?

Debugging "why do these two chairs differ?" starts with: do they share a prototype? If not, their composition differs (variant, inherit, extra local child).

### 3. Beginner explanation

The prototype is the **carving of the rubber stamp**, stored in a drawer labeled `/__Prototype_1`. You do not ship the drawer as a file. `GetInstances()` on the prototype lists every stamp that uses that carving.

*Where the analogy breaks:* the carving is composed from the source asset plus the instance roots' matching arcs. It is not a literal copy of `/Chair`'s path.

### 4. Technical explanation

- `instance.GetPrototype()` returns the prototype prim, or an invalid prim if `IsInstance()` is False.
- `stage.GetPrototypes()` lists all prototypes on the stage.
- `prototype.IsPrototype()` is True. `Usd.Prim.IsPrototypePath(path)` is True for `/__Prototype_1`.
- `prototype.GetInstances()` returns the instance roots that share it.
- `GetMaster` does **not** exist on USD 26.08.
- Editing a prototype prim directly is not how pipelines work; edit the **source** (`/Chair`) or the instance **root**. Prototype paths are runtime.

### 5. Mental model

```text
  GetPrototype()          GetInstances()
  /Room/A  ------------>  /__Prototype_1  ------------>  /Room/A, /Room/B
  /Room/B  ------------/
```

### 6. Simple example

A and B from 24.1 share `/__Prototype_1`. `A.GetPrototype() == B.GetPrototype()`.

### 7. USDA example

The USDA is the same as Section 24.1. Prototypes never appear in the saved file. The next Python block prints the runtime paths.

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/Chair")
UsdGeom.Cube.Define(stage, "/Chair/Seat")
for name in ("A", "B"):
    p = stage.DefinePrim("/Room/" + name)
    p.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
    p.SetInstanceable(True)
a = stage.GetPrimAtPath("/Room/A")
b = stage.GetPrimAtPath("/Room/B")
proto = a.GetPrototype()
print("prototype path:", proto.GetPath())
print("IsPrototype:", proto.IsPrototype())
print("GetPrototypes:", [str(p.GetPath()) for p in stage.GetPrototypes()])
print("instances of proto:", [str(p.GetPath()) for p in proto.GetInstances()])
print("A.GetPrototype() is B.GetPrototype():",
      a.GetPrototype() == b.GetPrototype())
print("hasattr GetMaster:", hasattr(a, "GetMaster"))
```

**Expected output**

```text
prototype path: /__Prototype_1
IsPrototype: True
GetPrototypes: ['/__Prototype_1']
instances of proto: ['/Room/A', '/Room/B']
A.GetPrototype() is B.GetPrototype(): True
hasattr GetMaster: False
```

### 9. Real-world use case

A tooling script groups instanceable furniture by `GetPrototype()` to count unique composed variants in a shot: "12 lamp prototypes, 4 800 instances."

### 10. Common mistakes

> [!MISTAKE] Searching the USDA for `/__Prototype_1`. It will not be there. Use Python or usdview's instance UI.

> [!MISTAKE] Calling `GetMaster()`. Use `GetPrototype()`.

### 11. Exam traps

> [!TRAP] "The prototype is `/Chair`." `/Chair` is the source. The prototype is a runtime prim under `/__Prototype_N`.

> [!TRAP] "Two instanceable references always share one prototype." Different variant selections split them (24.5).

### 12. Practice questions

**CA-024c** · Obj 2.2 · Difficulty: Easy · Type: Single choice
The current API to get the shared tree for an instance is:

A. `GetMaster()`
B. `GetPrototype()`
C. `GetPayloads()`
D. `GetParent()`

**CA-024d** · Obj 2.2 · Difficulty: Medium · Type: Single choice
`stage.GetPrototypes()` returns:

A. Every referenced asset root
B. The runtime prototype prims for native instances
C. PointInstancer prototypes
D. Class prims

**Answers**

**CA-024c — B.** `GetMaster` is gone. Review: §24.2.

**CA-024d — B.** Point instancing is Chapter 25. Review: §24.2.

### 13. Exam takeaways

> [!KEY]
> - `GetPrototype()`, `GetPrototypes()`, `GetInstances()`.
> - Prototype paths are runtime, not authored.
> - Matching composition → shared prototype.
> - Never write `GetMaster` in new code.

---

## 24.3 Instance proxies

### 1. What is it?

An **instance proxy** is a prim at a path *under* an instance root, for example `/Room/A/Seat`. It is a window onto the corresponding prototype prim. `IsInstanceProxy()` is True. You can read it; you cannot author on it.

### 2. Why do we need it?

Tools still need to pick "the seat of chair A" for bounding boxes, selection, and queries. Proxies give a path in instance namespace without duplicating data. Obj 2.5 is about editing **without** treating that path like a normal prim.

### 3. Beginner explanation

A proxy is a **photograph of the stamp's seat**. You can look at it. You cannot scribble on the photograph and expect only that stamp to change. Scribbling is rejected: "authoring to an instance proxy is not allowed."

*Where the analogy breaks:* `GetPrimInPrototype()` tells you which prototype prim the photograph shows. Changing the carving (`/Chair/Seat`) changes every photograph.

### 4. Technical explanation

- `GetPrimAtPath("/Room/A/Seat")` is valid. `IsInstanceProxy()` True. `GetPrimInPrototype()` → `/__Prototype_1/Seat`.
- Default `Traverse()` and `TraverseAll()` skip proxies. `stage.Traverse(Usd.TraverseInstanceProxies())` includes them.
- `Set`, `OverridePrim`, `CreateAttribute`, `Clear` on a proxy raise `Tf.ErrorException` (USD 26.08: `_ValidateEditPrim`).
- The instance **root** (`/Room/A`) is not a proxy. You may author metadata, variants, inherits, and primvars there (24.5).
- Reading attributes on a proxy returns the composed prototype values.

### 5. Mental model

```text
  /Room/A            instance root   -- author here OK
      /Seat          instance proxy  -- read OK, write FORBIDDEN
                       |
                       v
                   /__Prototype_1/Seat
```

### 6. Simple example

`/Room/A/Seat.size` can be read. Setting it raises. Traversal with `TraverseInstanceProxies` lists the Seat paths.

### 7. USDA example

Same setup as 24.1. Proxies are not extra USDA; they exist only on the composed stage.

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/Chair")
UsdGeom.Cube.Define(stage, "/Chair/Seat")
for name in ("A", "B"):
    p = stage.DefinePrim("/Room/" + name)
    p.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
    p.SetInstanceable(True)
seat = stage.GetPrimAtPath("/Room/A/Seat")
print("Seat IsInstanceProxy:", seat.IsInstanceProxy())
print("Seat GetPrimInPrototype:", seat.GetPrimInPrototype().GetPath())
print("TraverseInstanceProxies:",
      [str(p.GetPath())
       for p in stage.Traverse(Usd.TraverseInstanceProxies())])
try:
    seat.GetAttribute("size").Set(9)
except Exception as err:
    print("set on proxy:", type(err).__name__)
```

**Expected output**

```text
Seat IsInstanceProxy: True
Seat GetPrimInPrototype: /__Prototype_1/Seat
TraverseInstanceProxies: ['/Chair', '/Chair/Seat', '/Room', '/Room/A', '/Room/A/Seat', '/Room/B', '/Room/B/Seat']
set on proxy: ErrorException
```

### 9. Real-world use case

A viewer highlights `/Room/A/Seat` when the artist clicks that mesh. The pick path is a proxy. The exporter must not try to bake a unique `displayColor` onto that path; it writes a primvar on `/Room/A` instead.

### 10. Common mistakes

> [!MISTAKE] Hand-writing `over "Seat"` under an instanceable prim in USDA. It may parse, but composition ignores it (Chapter 22.4). Prefer a variant or class.

> [!MISTAKE] Using `TraverseAll()` to "see everything including proxies." On 26.08 `TraverseAll()` still skipped proxies in the verified example. Use `TraverseInstanceProxies()`.

### 11. Exam traps

> [!TRAP] "Proxies are invalid prims." They are valid. They are not editable.

> [!TRAP] "The instance root is a proxy." The root is the instance; its descendants are proxies.

### 12. Practice questions

**CA-024e** · Obj 2.5 · Difficulty: Medium · Type: Single choice
Setting `size` on `/Room/A/Seat` when `/Room/A` is an instance:

A. Changes only chair A
B. Changes every instance
C. Raises; authoring to an instance proxy is not allowed
D. Silently writes into the prototype file

**CA-024f** · Obj 2.2 · Difficulty: Easy · Type: Single choice
Which traversal includes `/Room/A/Seat`?

A. `stage.Traverse()`
B. `stage.TraverseAll()`
C. `stage.Traverse(Usd.TraverseInstanceProxies())`
D. `stage.GetPrototypes()`

**Answers**

**CA-024e — C.** Verified ErrorException. Review: §24.3.

**CA-024f — C.** Review: §24.3.

### 13. Exam takeaways

> [!KEY]
> - Proxies are readable paths under an instance; `IsInstanceProxy()` is True.
> - Writes to proxies fail.
> - `TraverseInstanceProxies()` is the walker that includes them.
> - `GetPrimInPrototype()` maps a proxy to the shared prim.

---

## 24.4 Editing look without breaking instancing

### 1. What is it?

You still need to change how instances look. The legal places are: the **source** prim (all copies), the **instance root** (that copy's arcs and primvars), or **de-instancing** that copy with `SetInstanceable(False)`.

### 2. Why do we need it?

Obj 2.5: vary a copy without destroying sharing for everyone else. Artists who "just over the seat" break the rule in 24.3.

### 3. Beginner explanation

Three legal pens:

1. Sharpen the **carving** (`/Chair/Seat`) — every stamp changes.
2. Write on the **stamp handle** (`/Room/B`) — variants, inherits, primvars.
3. Throw away the stamp for one chair (`SetInstanceable(False)`) and draw freely on that copy.

*Where the analogy breaks:* option 2 may create a **second prototype** (a second carving) for that handle's unique combination. Other chairs keep the first prototype. Sharing is not "broken"; it is split.

### 4. Technical explanation

| Edit | Where | Instances | Sharing |
|------|-------|-----------|---------|
| Change source `/Chair/Seat.size` | Source prim | All that use that source | Kept |
| Primvar / inherit / variant on `/Room/B` | Instance root | That copy (and any with the same combo) | Split if combo differs |
| `SetInstanceable(False)` then edit `/Room/B/Seat` | No longer an instance | That copy only | That copy leaves the prototype |
| `over "Seat"` under `/Room/B` while instanceable | Proxy | Rejected or ignored | Do not do this |

De-instancing is the escape hatch when a copy must be truly unique (a hero smashed chair). It costs memory for that copy.

### 5. Mental model

```text
  shared edit:     /Chair/Seat.size = 3     -> A and B both 3
  unique edit:     B.instanceable = false
                   /Room/B/Seat.size = 9    -> A stays 3, B is 9
```

### 6. Simple example

Two instances, source size 1. Set source to 3: both 3. De-instance B and set B's seat to 9: A stays 3, B is 9, B `IsInstance()` is False.

### 7. USDA example

*After de-instancing B in Python, the layer stores `instanceable = false` (or omits the flag) and a nested `over "Seat"` that is now legal because B is not an instance.*

```usda
#usda 1.0

def Xform "Chair"
{
    def Cube "Seat"
    {
        double size = 3
    }
}

def "Room"
{
    def "A" (
        instanceable = true
        prepend references = </Chair>
    )
    {
    }

    def "B" (
        prepend references = </Chair>
    )
    {
        over "Seat"
        {
            double size = 9
        }
    }
}
```

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/Chair")
UsdGeom.Cube.Define(stage, "/Chair/Seat").GetSizeAttr().Set(1.0)
for name in ("A", "B"):
    p = stage.DefinePrim("/Room/" + name)
    p.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
    p.SetInstanceable(True)
print("shared size A,B:",
      stage.GetPrimAtPath("/Room/A/Seat").GetAttribute("size").Get(),
      stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Get())
stage.GetPrimAtPath("/Chair/Seat").GetAttribute("size").Set(3.0)
print("after source edit A,B:",
      stage.GetPrimAtPath("/Room/A/Seat").GetAttribute("size").Get(),
      stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Get())
stage.GetPrimAtPath("/Room/B").SetInstanceable(False)
stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Set(9.0)
print("after B unique:",
      stage.GetPrimAtPath("/Room/A/Seat").GetAttribute("size").Get(),
      stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Get(),
      "B IsInstance", stage.GetPrimAtPath("/Room/B").IsInstance())
```

**Expected output**

```text
shared size A,B: 1.0 1.0
after source edit A,B: 3.0 3.0
after B unique: 3.0 9.0 B IsInstance False
```

### 9. Real-world use case

A set dresser instances 40 chairs. Chair 12 is on fire in this shot. They `SetInstanceable(False)` on that one copy and swap in a burned mesh. The other 39 keep sharing.

### 10. Common mistakes

> [!MISTAKE] De-instancing every copy "so we can edit." You throw away the memory win. Prefer root primvars and variants.

> [!MISTAKE] Editing `/__Prototype_1/Seat` in a tool that shows it. Edit `/Chair/Seat` instead.

### 11. Exam traps

> [!TRAP] "De-instancing A also de-instances B." Only the prim you call `SetInstanceable(False)` on leaves.

> [!TRAP] "Source edits do not affect instances because instances are copies." Native instances are not copies; they share the prototype fed by that source.

### 12. Practice questions

**CA-024g** · Obj 2.5 · Difficulty: Medium · Type: Single choice
You want every instanced lamp dimmer. Where do you author?

A. Each proxy `/Yard/Lamp_###/Bulb`
B. The source asset's bulb (or a class they all inherit)
C. `SetInstanceable(False)` on all lamps first
D. The session layer's `/__Prototype_1`

**CA-024h** · Obj 2.5 · Difficulty: Easy · Type: Single choice
After `SetInstanceable(False)` on `/Room/B`, authoring `/Room/B/Seat.size`:

A. Is still forbidden
B. Is allowed; B is no longer an instance
C. Changes A as well
D. Deletes the reference

**Answers**

**CA-024g — B.** Shared look belongs on the source or a shared class. Review: §24.4.

**CA-024h — B.** Review: §24.4.

### 13. Exam takeaways

> [!KEY]
> - Shared look: edit the source (or a shared class).
> - Per-copy look: instance-root arcs and primvars, or de-instance.
> - De-instance is the unique-hero escape hatch.
> - Never author on a proxy.

---

## 24.5 Overriding instances: inherits, variants, primvars on instance roots

### 1. What is it?

The instance **root** is a normal prim for composition arcs. You may set variant selections, add inherits, and author primvars there. Those opinions stay on the root; descendants remain proxies.

### 2. Why do we need it?

This is the intended way to make chair A "bare" and chair B "full," or to tint one row of seats red, without de-instancing.

### 3. Beginner explanation

The stamp **handle** can have a switch (variant), a style tag (inherit), and a color sticker (primvar). Different handle settings may mean a different carving (a second prototype). Stickers on the handle inherit down to the stamped mesh at render time (Chapter 11).

*Where the analogy breaks:* two roots with the same variant and inherits still share one prototype. Only a **different** combo splits.

### 4. Technical explanation

Verified on USD 26.08:

- `GetVariantSet("trim").SetVariantSelection("bare")` on an instance root keeps `IsInstance()` True. A and B then have **two** prototypes if B did not select `bare`.
- `GetInherits().AddInherit(/_Look)` on the root is legal. Implied inherits (Chapter 19) still apply.
- Primvars authored on the root (`primvars:displayColor`) keep instancing. `UsdGeom.PrimvarsAPI(proxy).FindPrimvarsWithInheritance()` sees them on descendants. `GetAttribute("primvars:displayColor")` on the proxy itself may be empty; inheritance is a primvar lookup, not a copied attribute spec.
- Authoring a nested `over` child still targets a proxy and fails or is ignored.

### 5. Mental model

```text
  /Room/A (instance root)
     variants.trim = "bare"     -> prototype 2 (cushion off)
     primvars:displayColor      -> inherited onto proxies
     inherits = </_Look>        -> may split prototype if B lacks it
  /Room/A/Seat (proxy)          -> still not editable
```

### 6. Simple example

Chair asset with `trim` variants `full` and `bare` (`bare` deactivates Cushion). Instance A selects `bare`, B does not. Two prototypes. A's cushion is inactive; B's is active. Both remain instances.

### 7. USDA example

*File: chair.usda* (trim variants)

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    prepend variantSets = "trim"
)
{
    def Cube "Seat"
    {
        double size = 1
    }
    def Cube "Cushion"
    {
        double size = 0.2
    }
    variantSet "trim" = {
        "full" {
        }
        "bare" {
            over "Cushion" (
                active = false
            )
            {
            }
        }
    }
}
```

*File: room.usda* (A selects `bare`)

```usda
#usda 1.0

def "Room"
{
    def "A" (
        instanceable = true
        prepend references = @./chair.usda@
        variants = {
            string trim = "bare"
        }
    )
    {
    }

    def "B" (
        instanceable = true
        prepend references = @./chair.usda@
    )
    {
    }
}
```

### 8. Python example

```python
from pxr import Sdf, Usd, UsdGeom

with open("chair.usda", "w") as f:
    f.write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    prepend variantSets = "trim"
)
{
    def Cube "Seat"
    {
        double size = 1
    }
    def Cube "Cushion"
    {
        double size = 0.2
    }
    variantSet "trim" = {
        "full" {
        }
        "bare" {
            over "Cushion" (
                active = false
            )
            {
            }
        }
    }
}
""")

stage = Usd.Stage.CreateNew("room.usda")
for name in ("A", "B"):
    p = stage.DefinePrim("/Room/" + name)
    p.GetReferences().AddReference("./chair.usda")
    p.SetInstanceable(True)
stage.GetPrimAtPath("/Room/A").GetVariantSet("trim").SetVariantSelection(
    "bare")
print("A IsInstance:", stage.GetPrimAtPath("/Room/A").IsInstance())
print("same prototype:",
      stage.GetPrimAtPath("/Room/A").GetPrototype() ==
      stage.GetPrimAtPath("/Room/B").GetPrototype())
print("A Cushion active:",
      stage.GetPrimAtPath("/Room/A/Cushion").IsActive())
print("B Cushion active:",
      stage.GetPrimAtPath("/Room/B/Cushion").IsActive())
print("num prototypes:", len(stage.GetPrototypes()))

st2 = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(st2, "/Chair")
UsdGeom.Cube.Define(st2, "/Chair/Seat")
root = st2.DefinePrim("/Room/A")
root.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
root.SetInstanceable(True)
root.CreateAttribute(
    "primvars:displayColor",
    Sdf.ValueTypeNames.Color3fArray).Set([(0.2, 0.3, 0.4)])
print("still instance:", root.IsInstance())
api = UsdGeom.PrimvarsAPI(st2.GetPrimAtPath("/Room/A/Seat"))
pv = [x for x in api.FindPrimvarsWithInheritance()
      if x.GetPrimvarName() == "displayColor"][0]
c = pv.Get()[0]
print("inherited color:", (round(c[0], 1), round(c[1], 1), round(c[2], 1)))
```

**Expected output**

```text
A IsInstance: True
same prototype: False
A Cushion active: False
B Cushion active: True
num prototypes: 2
still instance: True
inherited color: (0.2, 0.3, 0.4)
```

### 9. Real-world use case

A stadium tints home-side seats with `primvars:displayColor` on each instance root and uses a `wear` variant (`new` / `worn`) on rows near the tunnels. Most seats still share a handful of prototypes, not 50 000 unique meshes.

### 10. Common mistakes

> [!MISTAKE] Authoring `primvars:displayColor` on the proxy mesh. Put it on the instance root and let it inherit.

> [!MISTAKE] Expecting two different variant selections to keep one prototype. Different composition → different prototype. That is still instancing; each group shares internally.

### 11. Exam traps

> [!TRAP] "A variant selection on the root de-instances the prim." It stays an instance; it may join another prototype.

> [!TRAP] "Inherited primvars must be queried with `GetAttribute` on the child." Use `PrimvarsAPI.FindPrimvarsWithInheritance`.

### 12. Practice questions

**CA-024i** · Obj 2.5 · Difficulty: Medium · Type: Select two.
Which authoring on an instance root is allowed and keeps `IsInstance()` True?

A. `SetVariantSelection` on a variant set
B. `primvars:displayColor` on the root
C. `over "Seat" { double size = 4 }`
D. `Set` on `/Room/A/Seat.size`

**CA-024j** · Obj 2.2 · Difficulty: Medium · Type: Single choice
A selects `trim=bare`, B leaves the default. They:

A. Must share one prototype
B. Can be two prototypes and both still instances
C. Both become non-instances
D. Lose their references

**Answers**

**CA-024i — A and B.** Nested overs and proxy Sets are the forbidden pair. Review: §24.5.

**CA-024j — B.** Verified: two prototypes, both `IsInstance()`. Review: §24.5.

### 13. Exam takeaways

> [!KEY]
> - Instance-root variants, inherits, and primvars are the supported per-copy knobs.
> - Different combos split prototypes; that is still instancing.
> - Primvars inherit to descendants; query with `PrimvarsAPI`.
> - Nested `over` on a proxy is not a supported knob.

---

## 24.6 Removing properties from instanced component prims

### 1. What is it?

Obj 1.10 / 2.5: hide or strip a property or child on *some* instanced copies (no cushion, no extra bolt) without editing proxies and without exploding instancing for everyone.

### 2. Why do we need it?

Assemblies instance components, then a shot needs one component without a part. `Clear()` on the proxy fails. A local `over "Cushion" (active = false)` under the instance is the trap Chapter 22.4 already named.

### 3. Beginner explanation

You cannot erase ink from one stamp print. You either switch that handle to a "bare" setting (variant / inherited class that deactivates the part) or stop using a stamp for that chair (de-instance) and then deactivate.

*Where the analogy breaks:* the class or variant is authored **once** and reused. You are not hand-deactivating 400 proxies.

### 4. Technical explanation

Legal patterns (verified on 26.08):

1. **Variant on the asset**, selected on the instance root — Section 24.5 `trim=bare`.
2. **Inherited class** with `over "Cushion" (active = false)`. The instance root `prepend inherits = </_HideCushion>`. That copy stays an instance; it gets its own prototype if others do not inherit the class.
3. **De-instance**, then `SetActive(False)` on the now-real child.
4. **Do not instance** that particular copy from the start.

Illegal / ignored: `Clear()` on a proxy attribute; nested `over` under an instanceable prim.

`active = false` hides the child from default traversal; the spec can remain in the asset. That is usually what "remove this part" means in USD. Deleting from the published asset would remove it for every instance.

### 5. Mental model

```text
  WANT: chair A with no Cushion, chairs B…Z unchanged and still instanced

  DO:    A.inherits = /_HideCushion     or  A.variants.trim = "bare"
  DON'T: over "A" { over "Cushion" (active = false) }  while A is instanceable
  DON'T: GetPrimAtPath("/A/Cushion").Clear() or SetActive on the proxy
```

### 6. Simple example

`_HideCushion` class deactivates `Cushion`. Instance A inherits it; B does not. A's cushion is inactive; B's is not. Two prototypes; both instanceable.

### 7. USDA example

```usda
#usda 1.0

class "_HideCushion"
{
    over "Cushion" (
        active = false
    )
    {
    }
}

def Xform "Chair"
{
    def Cube "Seat"
    {
    }
    def Cube "Cushion"
    {
    }
}

def "A" (
    instanceable = true
    prepend references = </Chair>
    prepend inherits = </_HideCushion>
)
{
}

def "B" (
    instanceable = true
    prepend references = </Chair>
)
{
}
```

### 8. Python example

```python
from pxr import Usd

with open("hide.usda", "w") as f:
    f.write("""#usda 1.0
class "_HideCushion"
{
    over "Cushion" (
        active = false
    )
    {
    }
}
def Xform "Chair"
{
    def Cube "Seat"
    {
    }
    def Cube "Cushion"
    {
    }
}
def "A" (
    instanceable = true
    prepend references = </Chair>
    prepend inherits = </_HideCushion>
)
{
}
def "B" (
    instanceable = true
    prepend references = </Chair>
)
{
}
""")

stage = Usd.Stage.Open("hide.usda")
print("A IsInstance:", stage.GetPrimAtPath("/A").IsInstance())
print("A Cushion active:", stage.GetPrimAtPath("/A/Cushion").IsActive())
print("B Cushion active:", stage.GetPrimAtPath("/B/Cushion").IsActive())
print("same prototype:",
      stage.GetPrimAtPath("/A").GetPrototype() ==
      stage.GetPrimAtPath("/B").GetPrototype())
try:
    stage.GetPrimAtPath("/B/Seat").GetAttribute("size").Clear()
except Exception as err:
    print("Clear on proxy:", type(err).__name__)
```

**Expected output**

```text
A IsInstance: True
A Cushion active: False
B Cushion active: True
same prototype: False
Clear on proxy: ErrorException
```

### 9. Real-world use case

A digital-twin robot is instanced at twenty stations. Station 7 has no camera. The cell layer inherits `_NoCamera` on that one instance root, which deactivates `OptionalCamera`. The other nineteen keep the camera prototype.

### 10. Common mistakes

> [!MISTAKE] `over "Cushion" (active = false)` nested under the instanceable prim in the assembly. Composition ignores it. Put the `over` in a class or variant the root **selects**.

> [!MISTAKE] Editing the published component to delete Cushion. Every instance loses it.

### 11. Exam traps

> [!TRAP] "Splitting the prototype means instancing failed." A still has a prototype; it just is not B's.

> [!TRAP] Obj 1.10 is not "call Clear on the proxy." It is class / variant / de-instance.

### 12. Practice questions

**CA-024k** · Obj 1.10 · Difficulty: Medium · Type: Single choice
Best way to hide `Cushion` on one instanced chair in an assembly?

A. `Clear()` on the proxy's `size`
B. Nested `over "Cushion"` under the instanceable prim
C. Instance-root inherit of a class that deactivates `Cushion`, or a `bare` variant
D. Mute the component layer

**CA-024l** · Obj 1.10 · Difficulty: Easy · Type: Select two.
Which are legal for Obj 1.10?

A. Variant selection on the instance root
B. `SetInstanceable(False)` then deactivate the child
C. `SetActive(False)` on the proxy while still instanced
D. `GetMaster().SetActive(False)`

**Answers**

**CA-024k — C.** Review: §24.6.

**CA-024l — A and B.** C is a proxy write. D uses the removed name and would hit a prototype. Review: §24.6.

### 13. Exam takeaways

> [!KEY]
> - Remove/hide instanced parts with a root variant or inherited class, or de-instance.
> - Proxy `Clear` / nested `over` is the wrong answer to Obj 1.10.
> - A second prototype for that combo is expected and fine.
> - Do not delete the part from the published asset unless every copy should lose it.

---

## Chapter lab(s)

Lab 23 (native instancing and instance proxies) belongs with this chapter. Chapter 22.4 is the companion "don't nest overs under instances" drill.

## USDA reading exercises

**Exercise 24-A.** Using the USDA in 24.1, is `/Room/A/Seat` on the stage? Does default `Traverse()` visit it? Can you set its `size`?

**Exercise 24-B.** Using 24.5's `room.usda`, how many prototypes are there, and is A's cushion active?

**Answers**

**24-A.** Yes, it is a valid instance proxy. Default `Traverse()` does not visit it. Setting `size` raises `ErrorException`. Review: §24.1, §24.3.

**24-B.** Two prototypes. A's cushion is inactive (`trim=bare`). Review: §24.5.

---

## Chapter review

### Summary

- Native instancing: `instanceable = true` on referencing prims; they share a runtime prototype.
- `GetPrototype` / `GetPrototypes` / `GetInstances`. `GetMaster` is gone.
- Instance roots are editable; descendant proxies are not. `Traverse()` skips proxies.
- Shared edits go on the source. Unique heroes `SetInstanceable(False)`.
- Per-copy look: variants, inherits, primvars on the root (may split prototypes).
- Obj 1.10: hide parts with a class or variant on the root, not a proxy `over`.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `instanceable = true` | Native instancing on that referencing prim |
| `/__Prototype_1` | Runtime prototype, not in the USDA |
| `GetMaster` | Old name; answer is `GetPrototype` |
| `IsInstanceProxy` | Read-only descendant; do not `Set` |
| `Traverse()` misses `/A/Seat` | Need `TraverseInstanceProxies()` |
| Two instanceable chairs, two prototypes | Different variant/inherit combo |
| Nested `over "Seat"` under instance | Wrong; ignored or error (Obj 1.10) |
| Tint one row of seats | Primvar on each instance root |
| One smashed chair | `SetInstanceable(False)` |

### Review questions

**R24-01** · Obj 2.2 · Single choice
`IsInstance()` is True when:
A. `instanceable` is authored, even with no reference
B. USD has built a prototype for that prim
C. The prim is a class
D. The prim is a payload

**R24-02** · Obj 2.2 · Single choice
Prototypes are stored:
A. As `/__Prototype_N` specs in the root layer
B. Only at runtime on the stage
C. In `customData`
D. As payloads

**R24-03** · Obj 2.5 · Single choice
Authoring to `/Room/A/Seat` while A is an instance:
A. Edits only A
B. Edits the asset file
C. Is not allowed
D. Creates a specialize arc

**R24-04** · Obj 2.5 · Single choice
`stage.Traverse(Usd.TraverseInstanceProxies())` is for:
A. Opening payloads
B. Including proxy descendants
C. Flattening
D. Listing class prims

**R24-05** · Obj 2.5 · Select two.
Legal ways to change one copy's look:
A. Primvar on the instance root
B. Variant selection on the instance root
C. `Set` on a proxy attribute
D. `GetMaster().GetChild("Seat").Set…`

**R24-06** · Obj 2.2 · Single choice
A and B are instanceable references to the same asset. A selects `trim=bare`. Result:
A. Both de-instance
B. Possibly two prototypes; both can stay instances
C. USD error
D. A loses its reference

**R24-07** · Obj 1.10 · Single choice
Obj 1.10 "remove properties from instanced component prims" is solved by:
A. Nested `over` under the instance
B. Class/variant on the instance root, or de-instance then edit
C. `usdcat --strip`
D. Muting the session layer

**R24-08** · Obj 2.4 · Single choice
Native instancing is mainly for:
A. Replacing references
B. Sharing composed descendants in memory across many copies
C. Unloading geometry
D. Changing `upAxis`

**R24-09** · Obj 2.5 · Single choice
After `SetInstanceable(False)` on B, B.IsInstance() is:
A. True
B. False, and `/Room/B/Seat` may be authored
C. True, but proxies become editable
D. Undefined

**R24-10** · Obj 2.2 · Single choice
`hasattr(prim, "GetMaster")` on USD 26.08 is:
A. True
B. False
C. True only on prototypes
D. True only in C++

**R24-11** · Obj 2.5 · Single choice
A primvar `displayColor` on the instance root is read on a descendant with:
A. `child.GetAttribute("primvars:displayColor").Get()` only
B. `UsdGeom.PrimvarsAPI(child).FindPrimvarsWithInheritance()`
C. `GetPrototype().GetDisplayColor()`
D. `GetMaster()`

**R24-12** · Obj 1.10 · Select two.
Which keep instancing while hiding a child on one copy?
A. Inherit `_HideChild` on that root
B. Select a variant that deactivates the child
C. `Clear()` on the proxy
D. Delete the child from the published asset (also hides it on every other copy)

### Review answers

**R24-01 — B.** The flag is `IsInstanceable`; `IsInstance` means a prototype exists. Review: §24.1.

**R24-02 — B.** Review: §24.2.

**R24-03 — C.** Review: §24.3.

**R24-04 — B.** Review: §24.3.

**R24-05 — A and B.** Review: §24.5.

**R24-06 — B.** Review: §24.5.

**R24-07 — B.** Review: §24.6.

**R24-08 — B.** Payloads are C. Review: §24.1.

**R24-09 — B.** Review: §24.4.

**R24-10 — B.** Review: §24.2.

**R24-11 — B.** Review: §24.5.

**R24-12 — A and B.** D affects every copy. Review: §24.6.

## Further reading

- [S04] OpenUSD Glossary — "Instancing", "Prototype", "Instance Proxy": https://openusd.org/release/glossary.html
- [S06] OpenUSD API — `UsdPrim::GetPrototype`, `UsdStage::GetPrototypes`, `UsdTraverseInstanceProxies`: https://openusd.org/release/api/index.html
- [S14] NVIDIA Learn OpenUSD — Asset modularity and instancing: https://docs.nvidia.com/learn-openusd/latest/index.html
- [S11] Maximizing USD Performance — instancing: https://openusd.org/release/maxperf.html
