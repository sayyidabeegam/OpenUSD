# Chapter 17 — Payloads

> **Exam domain:** Composition (23%) · **Objectives:** 1.3 · **Study day:** 5 · **Est. time:** 90 min
> **Prerequisites:** Ch 2 (opening stages, traversal), Ch 14 (LIVERPS, list editing), Ch 15 (layer stacks), Ch 16 (references, `defaultPrim`, layer offsets)

## Learning goals

- Explain what a payload is and how it differs from a reference.
- Open a stage with everything or nothing loaded, and load or unload parts of it with `Load`, `Unload`, and `LoadAndUnload`.
- Describe a stage's load state with `Usd.StageLoadRules` (`AllRule`, `OnlyRule`, `NoneRule`).
- Open only part of a scene's namespace with `Usd.StagePopulationMask` and `Usd.Stage.OpenMasked`.
- Place payloads correctly in LIVERPS and choose between payloads, references, and sublayers.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Payload** | A composition arc like a reference, whose content is composed only when the prim is **loaded**. |
| **Loaded / unloaded** | Whether a prim's payload content is currently composed into the stage. |
| **Load set** | The list of payload prims that are currently loaded (`stage.GetLoadSet()`). |
| **Initial load set** | Whether payloads are loaded when a stage opens: `Usd.Stage.LoadAll` (default) or `Usd.Stage.LoadNone`. |
| **Load rules** | `Usd.StageLoadRules`: a set of path → rule entries that fully describes what is loaded. |
| **Population mask** | `Usd.StagePopulationMask`: a set of paths that limits which prims the stage composes at all. |
| **Working set** | The part of a large scene a user actually has loaded and is working on. |

---

## 17.1 What a payload is

### 1. What is it?

A **payload** is a composition arc that works like a reference (Chapter 16), with one extra power: you can choose **not to load** it. When unloaded, the prim stays on the stage, but the content behind the payload is not read or composed.

### 2. Why do we need it?

A city scene may hold 20,000 buildings with gigabytes of geometry. Opening all of it to fix one street lamp wastes minutes and memory. Payloads let you open the scene's structure quickly and load only the parts you need.

### 3. Beginner explanation

A payload is **a reference you can choose not to load**, like a labelled box in storage. The inventory list (the stage) always shows the box and its label. You only carry the box in and open it when you need what is inside.

Where the analogy breaks: the "box" can also hold opinions that affect a prim that is already present (for example its type or attributes). While unloaded, those opinions are missing too, not only the child prims.

### 4. Technical explanation

- Stored as prim metadata `payload` (USDA keyword is singular: `prepend payload = @geo.usda@`). Each entry is an `Sdf.Payload(assetPath, primPath, layerOffset)`.
- Python: `prim.GetPayloads()` returns `Usd.Payloads` with `AddPayload`, `AddInternalPayload`, `RemovePayload`, `ClearPayloads`, `SetPayloads`.
- Like references: an asset path plus optional prim path (otherwise the target layer's `defaultPrim`), an optional `Sdf.LayerOffset`, list-edited, namespace-mapped, and failure reasons are the same (Chapter 16.5).
- Unlike references: composed only when the prim is loaded. `prim.IsLoaded()` tells you the state; `prim.HasAuthoredPayloads()` tells you whether the prim has a payload.
- **Traversal trap:** `stage.Traverse()` uses the default predicate, which skips unloaded prims. Use `stage.TraverseAll()` (or `GetPrimAtPath`) to see them.
- Payloads are the **P** in LIVERPS, just after R: weaker than references (Section 17.5).

> [!VERSION] Older code uses `prim.SetPayload(...)`, `prim.ClearPayload()`, and `prim.HasPayload()`. They still exist in USD 26.08, but the list-edited `prim.GetPayloads()` API and `HasAuthoredPayloads()` are the current form. Verified on USD 26.08.

### 5. Mental model

```text
  stage (always present)                 storage
  /City
    /Block_01  [payload] ---- unloaded -- [ block_01_geo.usda ]  not read
    /Block_02  [payload] ==== loaded ==== [ block_02_geo.usda ]
       /Buildings ... (composed from the payload)
```

### 6. Simple example

| State | `/City/Block_02` exists? | Its children exist? | `IsLoaded()` |
|-------|--------------------------|---------------------|--------------|
| Unloaded | yes | no | `False` |
| Loaded | yes | yes | `True` |

### 7. USDA example

*File: tree_geo.usda*

```usda
#usda 1.0
(
    defaultPrim = "Tree"
)

def Xform "Tree"
{
    def Cylinder "Trunk"
    {
    }
}
```

*File: forest.usda*

```usda
#usda 1.0

def Xform "Forest"
{
    def Xform "TreeA" (
        prepend payload = @./tree_geo.usda@
    )
    {
    }

    def Xform "TreeB" (
        prepend payload = @./tree_geo.usda@
    )
    {
    }
}
```

Notes: `payload` (singular) is the keyword. No `<…>` prim path is given, so `defaultPrim` (`Tree`) is used. `TreeA` and `TreeB` are typed `Xform` locally, so they keep their type even when unloaded.

### 8. Python example

```python
from pxr import Usd

GEO = """#usda 1.0
(
    defaultPrim = "Tree"
)
def Xform "Tree"
{
    def Cylinder "Trunk" {}
}
"""
with open("tree_geo.usda", "w") as f:
    f.write(GEO)

stage = Usd.Stage.CreateNew("forest.usda")
for name in ["TreeA", "TreeB"]:
    tree = stage.DefinePrim(f"/Forest/{name}", "Xform")
    tree.GetPayloads().AddPayload("./tree_geo.usda")
stage.Save()

closed = Usd.Stage.Open("forest.usda", Usd.Stage.LoadNone)
print("Traverse:   ", [str(p.GetPath()) for p in closed.Traverse()])
print("TraverseAll:", [str(p.GetPath()) for p in closed.TraverseAll()])
tree_a = closed.GetPrimAtPath("/Forest/TreeA")
print("TreeA:", tree_a.GetTypeName(), "loaded =", tree_a.IsLoaded(),
      "has payload =", tree_a.HasAuthoredPayloads())

opened = Usd.Stage.Open("forest.usda")              # default: LoadAll
trunks = [str(p.GetPath()) for p in opened.Traverse() if p.GetName() == "Trunk"]
print("LoadAll trunks:", trunks)
print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
Traverse:    ['/Forest']
TraverseAll: ['/Forest', '/Forest/TreeA', '/Forest/TreeB']
TreeA: Xform loaded = False has payload = True
LoadAll trunks: ['/Forest/TreeA/Trunk', '/Forest/TreeB/Trunk']
#usda 1.0

def "Forest"
{
    def Xform "TreeA" (
        prepend payload = @./tree_geo.usda@
    )
    {
    }

    def Xform "TreeB" (
        prepend payload = @./tree_geo.usda@
    )
    {
    }
}
```

Notice that the same file gives two different stages depending on how it is opened. The file never stores "loaded" or "unloaded".

### 9. Real-world use case

Asset structure guidelines (Chapter 23) put each asset's heavy geometry behind a payload in the asset's entry file. Set dressers open a whole film set unloaded, see every asset's name and transform, and load only the area around the camera. Digital-twin viewers load factory halls on demand as the user walks through them.

### 10. Common mistakes

> [!MISTAKE] Writing `prepend payloads = ...` in USDA. The keyword is `payload` (singular); `references` is plural. Let Python author it if unsure.

> [!MISTAKE] Concluding "the prims are missing" because `stage.Traverse()` does not list them. Unloaded prims are skipped by the default traversal; use `TraverseAll()` or check `IsLoaded()`.

### 11. Exam traps

> [!TRAP] "An unloaded payload prim does not exist on the stage." False. The prim exists (with its local opinions); only the payload's content is missing.

> [!TRAP] "Payloads are loaded lazily by default." Not in the sense of opening: `Usd.Stage.Open` loads **all** payloads unless you pass `Usd.Stage.LoadNone`.

### 12. Practice questions

**Q1.** Which USDA line authors a payload?
A. `prepend payloads = @geo.usda@` · B. `prepend payload = @geo.usda@` · C. `prepend references = @geo.usda@ (payload = true)` · D. `subLayers = [@geo.usda@]`

**Q2.** A stage is opened with `Usd.Stage.LoadNone`. `/Set/Car` has a payload and is typed `Xform` in the root layer. What does `stage.GetPrimAtPath("/Set/Car").GetTypeName()` return, and is `/Set/Car/Body` (from the payload) valid?

**Answers**

**Q1 — B.** A uses a wrong plural; C and D are other things.
**Q2** — `"Xform"` (a local opinion), and `/Set/Car/Body` is not valid until `/Set/Car` is loaded.

### 13. Exam takeaways

> [!KEY]
> - Payload = reference that can be unloaded; same targeting rules (asset path, prim path or `defaultPrim`, layer offset).
> - Unloaded prim exists; payload content (children and opinions) does not.
> - `prim.GetPayloads().AddPayload(...)` writes `prepend payload`.
> - Default `Traverse()` skips unloaded prims.

---

## 17.2 Loading and unloading (`Load`, `Unload`, `InitialLoadSet`)

### 1. What is it?

The stage methods that decide which payloads are composed: the **initial load set** given to `Usd.Stage.Open`, and `Load`, `Unload`, and `LoadAndUnload` for changes while the stage is open.

### 2. Why do we need it?

Users move around a large scene. They need to bring in one building, drop another, and do it without reopening the stage. This is **working set management**, named in the exam's reading list.

### 3. Beginner explanation

When you arrive at the storage room you either carry in every box (`LoadAll`) or none (`LoadNone`). Later you fetch some boxes and return others.

Where the analogy breaks: loading a box also loads boxes **inside** it, unless you say otherwise (`Usd.LoadWithoutDescendants`).

### 4. Technical explanation

- `Usd.Stage.Open(path, load)`: `load` is `Usd.Stage.LoadAll` (default) or `Usd.Stage.LoadNone`, the values of the enum `Usd.Stage.InitialLoadSet`. The same argument exists on `CreateNew`, `CreateInMemory`, and `OpenMasked`.
- `stage.Load(path, policy)`: loads `path`, its ancestors, and by default its descendants (`Usd.LoadWithDescendants`). With `Usd.LoadWithoutDescendants`, nested payloads below stay unloaded. Returns the prim. With no path, it loads everything from `/`.
- `stage.Unload(path)`: unloads `path` and all descendants. With no path, unloads everything.
- `stage.LoadAndUnload(loadSet, unloadSet)`: both at once, recomposing only once. Use it for many paths.
- `prim.Load()` and `prim.Unload()` are shortcuts.
- `stage.GetLoadSet()` lists loaded payload prims. `stage.FindLoadable(rootPath)` lists all prims with payloads below a path (loaded or not).
- Load state is **stage state**, not scene description. Loading does not write to any layer and is not saved.

### 5. Mental model

```text
 Open(LoadNone)        Load("/City/B1")          Unload("/City/B1")
 /City                 /City                     /City
   /B1  [unloaded]       /B1  [loaded]             /B1  [unloaded]
                           /Room1 [loaded]
                             /Wall
 (Load = this prim + ancestors + descendants, unless LoadWithoutDescendants)
```

### 6. Simple example

`city.usda` has `/City/B1` with a payload to a building, and the building has `/Room1` with a payload to a room.

| Call | Load set |
|------|----------|
| `Open(..., LoadNone)` | `[]` |
| `Load("/City/B1", Usd.LoadWithoutDescendants)` | `[/City/B1]` |
| `Load("/City/B1")` | `[/City/B1, /City/B1/Room1]` |
| `Unload("/City/B1")` | `[]` |

### 7. USDA example

*File: room.usda*

```usda
#usda 1.0
(
    defaultPrim = "Room"
)

def Xform "Room"
{
    def Cube "Wall"
    {
    }
}
```

*File: bldg.usda*

```usda
#usda 1.0
(
    defaultPrim = "Bldg"
)

def Xform "Bldg"
{
    def Xform "Room1" (
        prepend payload = @./room.usda@
    )
    {
    }
}
```

*File: city.usda*

```usda
#usda 1.0

def Xform "City"
{
    def Xform "B1" (
        prepend payload = @./bldg.usda@
    )
    {
    }
}
```

Notes: this is a **nested payload**. `/City/B1/Room1` only exists after `/City/B1` is loaded, because it comes from inside `bldg.usda`.

### 8. Python example

```python
from pxr import Usd

files = {
    "room.usda": '#usda 1.0\n(\n    defaultPrim = "Room"\n)\n'
                 'def Xform "Room"\n{\n    def Cube "Wall" {}\n}\n',
    "bldg.usda": '#usda 1.0\n(\n    defaultPrim = "Bldg"\n)\n'
                 'def Xform "Bldg"\n{\n'
                 '    def Xform "Room1" ( prepend payload = @./room.usda@ )\n'
                 '    {\n    }\n}\n',
    "city.usda": '#usda 1.0\ndef Xform "City"\n{\n'
                 '    def Xform "B1" ( prepend payload = @./bldg.usda@ )\n'
                 '    {\n    }\n}\n',
}
for name, text in files.items():
    with open(name, "w") as f:
        f.write(text)

def show(stage, label):
    names = [p.GetName() for p in stage.Traverse()]
    loaded = [str(p) for p in stage.GetLoadSet()]
    print(f"{label:18} prims={names}")
    print(f"{'':18} loadSet={loaded}")

stage = Usd.Stage.Open("city.usda", Usd.Stage.LoadNone)
show(stage, "opened LoadNone")
stage.Load("/City/B1", Usd.LoadWithoutDescendants)
show(stage, "load B1 only")
print("loadable:", [str(p) for p in stage.FindLoadable()])
stage.Load("/City/B1")
show(stage, "load B1 + nested")
stage.Unload("/City/B1")
show(stage, "unload B1")
stage.LoadAndUnload(["/City/B1"], [])
show(stage, "LoadAndUnload")
print("root layer dirty?", stage.GetRootLayer().dirty)
```

**Expected output**

```text
opened LoadNone    prims=['City']
                   loadSet=[]
load B1 only       prims=['City', 'B1']
                   loadSet=['/City/B1']
loadable: ['/City/B1', '/City/B1/Room1']
load B1 + nested   prims=['City', 'B1', 'Room1', 'Wall']
                   loadSet=['/City/B1', '/City/B1/Room1']
unload B1          prims=['City']
                   loadSet=[]
LoadAndUnload      prims=['City', 'B1', 'Room1', 'Wall']
                   loadSet=['/City/B1', '/City/B1/Room1']
root layer dirty? False
```

`FindLoadable` found `/City/B1/Room1` only after `B1` was loaded, because that payload is inside `bldg.usda`. `dirty` is `False`: loading changed no layer.

### 9. Real-world use case

A layout tool shows a scene outliner with a "load / unload" checkbox per asset; each click calls `Load` or `Unload`. A batch render farm job opens shots with `LoadAll`. A pipeline script that only edits transforms opens shots with `LoadNone`, which is much faster.

### 10. Common mistakes

> [!MISTAKE] Calling `Load` in a loop over thousands of paths. Each call recomposes. Collect the paths and call `LoadAndUnload` once.

> [!MISTAKE] Expecting `stage.Save()` to remember what was loaded. It does not. Store working sets in your own tool's settings, or re-apply load rules (Section 17.3).

### 11. Exam traps

> [!TRAP] `Usd.Stage.LoadAll` / `Usd.Stage.LoadNone` (initial load set when opening) are not the same as `Usd.StageLoadRules.LoadAll()` / `LoadNone()` (static constructors that make rule objects). Read which class the question names.

> [!TRAP] "`Load(path)` loads only that prim." By default it also loads all payloads below it. Only `Usd.LoadWithoutDescendants` stops that.

### 12. Practice questions

**Q1.** Which call opens a stage without composing any payload?
A. `Usd.Stage.Open(p, Usd.Stage.LoadNone)` · B. `Usd.Stage.Open(p).Unload()` · C. `Usd.Stage.OpenMasked(p)` · D. `Usd.Stage.Open(p, Usd.LoadWithoutDescendants)`

**Q2.** Select two. After `stage.Load("/Set/House")` on a stage opened with `LoadNone`, which are true?
A. Payloads nested inside `/Set/House` are also loaded.
B. The root layer now contains a "loaded" flag.
C. `stage.GetLoadSet()` includes `/Set/House`.
D. All other payloads on the stage are loaded too.

**Answers**

**Q1 — A.** B opens everything first and then unloads, so it composes payloads. C needs a mask and loads all by default. D passes a load policy where an initial load set is expected.
**Q2 — A, C.** Load state is not authored (B), and other subtrees are not touched (D).

### 13. Exam takeaways

> [!KEY]
> - `Usd.Stage.Open(path, Usd.Stage.LoadNone)` opens with nothing loaded; the default is `LoadAll`.
> - `Load(path)` loads ancestors and descendants; `Usd.LoadWithoutDescendants` limits it.
> - Use `LoadAndUnload` for batches; `GetLoadSet` and `FindLoadable` to inspect.
> - Load state is never saved in a layer.

---

## 17.3 `Usd.StageLoadRules`

### 1. What is it?

`Usd.StageLoadRules` is an object that describes the entire load state of a stage as a short list of **path → rule** entries. `Load` and `Unload` edit these rules for you; you can also build rules yourself and apply them with `stage.SetLoadRules(rules)`.

### 2. Why do we need it?

A list of 10,000 loaded paths is clumsy. Rules are compact ("load nothing, except everything under `/City/Block_7`"), can be stored by a tool, and applied in one step to any stage.

### 3. Beginner explanation

Instead of a list of every box you carried in, you write instructions: "No boxes, except **everything** in aisle 7, and **only the top box** in aisle 9."

Where the analogy breaks: rules apply to future boxes too. If aisle 7 later gets new boxes (new payloads), the "everything" rule loads them automatically.

### 4. Technical explanation

- Three rule values: `Usd.StageLoadRules.AllRule` (load this prim and all descendants), `OnlyRule` (load this prim's payload, not descendants'), `NoneRule` (load nothing here or below).
- For any path, the **closest ancestor-or-self entry** decides; `rules.GetEffectiveRuleForPath(path)` returns it.
- An **empty** rules object (`Usd.StageLoadRules()`) means "load everything". `Usd.StageLoadRules.LoadAll()` and `LoadNone()` are constructors for the two starting points.
- Edit methods: `AddRule(path, rule)`, `LoadWithDescendants(path)`, `LoadWithoutDescendants(path)`, `Unload(path)`, `LoadAndUnload(...)`, `SetRules(...)`, `Minimize()`. Query: `IsLoaded(path)`, `IsLoadedWithAllDescendants(path)`, `GetRules()`.
- `LoadWithDescendants`/`LoadWithoutDescendants`/`Unload` also remove rules for descendants of `path`, so the new instruction is the only one that applies there.
- Stage: `stage.GetLoadRules()` and `stage.SetLoadRules(rules)`.

### 5. Mental model

```text
 rules: (/ , NoneRule) (/Forest/TreeB , AllRule)

 path                  closest entry      loaded?
 /Forest/TreeA         /  -> NoneRule     no
 /Forest/TreeB         /Forest/TreeB All  yes
 /Forest/TreeB/Leaves  /Forest/TreeB All  yes
```

### 6. Simple example

| Rules | `/A` (payload) | `/A/B` (nested payload) | `/C` (payload) |
|-------|----------------|-------------------------|----------------|
| empty `Usd.StageLoadRules()` | loaded | loaded | loaded |
| `LoadNone()` + `(/A, AllRule)` | loaded | loaded | unloaded |
| `LoadNone()` + `(/A, OnlyRule)` | loaded | unloaded | unloaded |

### 7. USDA example

Load rules are not scene description, so there is no USDA syntax for them. This is the scene they act on in the Python example (`forest3.usda`):

```usda
#usda 1.0

def Xform "Forest"
{
    def Xform "TreeA" (
        prepend payload = @./tree_geo.usda@
    )
    {
    }

    def Xform "TreeB" (
        prepend payload = @./tree_geo.usda@
    )
    {
    }

    def Xform "TreeC" (
        prepend payload = @./tree_geo.usda@
    )
    {
    }
}
```

### 8. Python example

```python
from pxr import Usd

GEO = '#usda 1.0\n(\n    defaultPrim = "Tree"\n)\n' \
      'def Xform "Tree"\n{\n    def Cylinder "Trunk" {}\n}\n'
with open("tree_geo.usda", "w") as f:
    f.write(GEO)
stage = Usd.Stage.CreateNew("forest3.usda")
for name in ["TreeA", "TreeB", "TreeC"]:
    stage.DefinePrim(f"/Forest/{name}", "Xform").GetPayloads().AddPayload(
        "./tree_geo.usda")
stage.Save()

R = Usd.StageLoadRules
rules = R.LoadNone()
rules.AddRule("/Forest/TreeB", R.AllRule)
print(rules)
print("TreeA:", rules.IsLoaded("/Forest/TreeA"),
      "TreeB:", rules.IsLoaded("/Forest/TreeB"),
      "rule for TreeB/Trunk:", rules.GetEffectiveRuleForPath("/Forest/TreeB/Trunk"))

work = Usd.Stage.Open("forest3.usda")       # LoadAll ...
work.SetLoadRules(rules)                     # ... then apply the rules
print("loadSet:", [str(p) for p in work.GetLoadSet()])

work.Load("/Forest/TreeC")                   # Load/Unload edit the rules
work.Unload("/Forest/TreeB")
for path, rule in work.GetLoadRules().GetRules():
    print(" ", path, rule)
print("loadSet:", [str(p) for p in work.GetLoadSet()])
print("empty rules load everything:", R().IsLoaded("/Forest/TreeA"))
```

**Expected output**

```text
UsdStageLoadRules([ (</>, NoneRule) (</Forest/TreeB>, AllRule) ])
TreeA: False TreeB: True rule for TreeB/Trunk: Usd.StageLoadRules.AllRule
loadSet: ['/Forest/TreeB']
  / Usd.StageLoadRules.NoneRule
  /Forest/TreeB Usd.StageLoadRules.NoneRule
  /Forest/TreeC Usd.StageLoadRules.AllRule
loadSet: ['/Forest/TreeC']
empty rules load everything: True
```

`Load("/Forest/TreeC")` added an `AllRule` entry, and `Unload("/Forest/TreeB")` replaced TreeB's `AllRule` with a `NoneRule`. The rules object is the stage's whole load state.

### 9. Real-world use case

A layout application saves the artist's working set as load rules in its own session file. Next morning it reopens the shot with `LoadNone` and calls `SetLoadRules` once; the artist sees exactly what they had loaded yesterday, plus any new assets added under an `AllRule` area.

### 10. Common mistakes

> [!MISTAKE] Thinking an empty `Usd.StageLoadRules()` loads nothing. Empty means **load all**. Start from `Usd.StageLoadRules.LoadNone()` to build "nothing except…".

> [!MISTAKE] Using `OnlyRule` to load an asset and its nested payloads. `OnlyRule` loads that prim's own payload only; use `AllRule`.

### 11. Exam traps

> [!TRAP] Rule names look like method names: `AllRule`/`OnlyRule`/`NoneRule` are **values**; `LoadWithDescendants`/`LoadWithoutDescendants`/`Unload` are **methods** that write those values.

> [!TRAP] "Load rules are saved with the layer." False. They belong to the stage object and live only in memory.

### 12. Practice questions

**Q1.** Rules are `(/, NoneRule) (/Set, AllRule) (/Set/Truck, NoneRule)`. Which of these payload prims are loaded: `/Set/Car`, `/Set/Truck`, `/Props/Cup`?

**Q2.** Which rule loads a prim's payload but leaves payloads nested below it unloaded?
A. `AllRule` · B. `OnlyRule` · C. `NoneRule` · D. `Usd.Stage.LoadNone`

**Answers**

**Q1** — Only `/Set/Car`. Its closest entry is `/Set` (All). `/Set/Truck` has its own NoneRule; `/Props/Cup` falls back to `/` (None).
**Q2 — B.** `OnlyRule`; D is an initial load set, not a rule.

### 13. Exam takeaways

> [!KEY]
> - `Usd.StageLoadRules` = path → `AllRule` / `OnlyRule` / `NoneRule`; the closest entry wins.
> - Empty rules = load everything; `LoadNone()` is the "nothing except" starting point.
> - `stage.SetLoadRules(rules)` applies them in one step; `Load`/`Unload` edit them.
> - Rules are stage state, not authored data.

---

## 17.4 Population masks (`OpenMasked`)

### 1. What is it?

A **population mask** (`Usd.StagePopulationMask`) is a set of prim paths. A stage opened with `Usd.Stage.OpenMasked(path, mask)` composes only those prims, their descendants, and their ancestors. Everything else is not on the stage at all.

### 2. Why do we need it?

Payloads only help where the asset author put them. A mask works on any file: a tool that only needs `/World/Cameras` can skip composing the rest of a huge scene, whether or not it uses payloads.

### 3. Beginner explanation

The storage room inventory itself is torn in half: you take only the pages for aisle 7. Boxes in other aisles do not even appear on your list.

Where the analogy breaks: the pages for the *path to* aisle 7 (its ancestors) are kept, so you can still reach it.

### 4. Technical explanation

- Build: `Usd.StagePopulationMask(["/World/Cams"])` or `Usd.StagePopulationMask().Add("/World/Cams")`. `Usd.StagePopulationMask.All()` includes everything.
- Open: `Usd.Stage.OpenMasked(filePath or layer, mask, load=Usd.Stage.LoadAll)`. Masks and load sets combine: the mask decides which prims exist; load rules decide which payloads are composed inside the mask.
- For each mask path, the stage includes the prim, **all its descendants**, and its **ancestors** (but not the ancestors' other children).
- Prims outside the mask are absent: `GetPrimAtPath` returns an invalid prim, and traversal does not visit them.
- Change later: `stage.SetPopulationMask(mask)`, `stage.GetPopulationMask()`. `stage.ExpandPopulationMask()` grows the mask to include targets of relationships and attribute connections of prims already in it.
- Query: `mask.Includes(path)` (path is on the stage), `mask.IncludesSubtree(path)` (path and everything below it are).

### 5. Mental model

```text
 file:            /Forest            mask = [/Forest/TreeB]
                  /Forest/TreeA
                  /Forest/TreeB      stage: /Forest          (ancestor)
                  /Forest/TreeB/Trunk       /Forest/TreeB    (mask path)
                  /Lights                   /Forest/TreeB/Trunk (descendant)
                                     absent: /Forest/TreeA, /Lights
```

### 6. Simple example

| Mask | `/Forest` | `/Forest/TreeA` | `/Forest/TreeB/Trunk` | `/Lights` |
|------|-----------|-----------------|------------------------|-----------|
| `[/Forest/TreeB]` | yes (ancestor) | no | yes | no |
| `[/Forest]` | yes | yes | yes | no |
| `All()` | yes | yes | yes | yes |

### 7. USDA example

Masks are not scene description; there is no USDA for them. This is the layer used below (`forest_rel.usda`); note the relationship from `TreeA` to `TreeB`:

```usda
#usda 1.0

def Xform "Forest"
{
    def Xform "TreeA"
    {
        rel neighbor = </Forest/TreeB>
    }

    def Xform "TreeB"
    {
        def Cylinder "Trunk"
        {
        }
    }
}

def Scope "Lights"
{
}
```

### 8. Python example

```python
from pxr import Usd

SCENE = """#usda 1.0
def Xform "Forest"
{
    def Xform "TreeA"
    {
        rel neighbor = </Forest/TreeB>
    }
    def Xform "TreeB"
    {
        def Cylinder "Trunk" {}
    }
}
def Scope "Lights" {}
"""
with open("forest_rel.usda", "w") as f:
    f.write(SCENE)

mask = Usd.StagePopulationMask(["/Forest/TreeB"])
stage = Usd.Stage.OpenMasked("forest_rel.usda", mask)
print("masked:", [str(p.GetPath()) for p in stage.Traverse()])
print("TreeA valid?", stage.GetPrimAtPath("/Forest/TreeA").IsValid())
print("Includes /Forest:", mask.Includes("/Forest"),
      "IncludesSubtree /Forest:", mask.IncludesSubtree("/Forest"))

stage.SetPopulationMask(Usd.StagePopulationMask(["/Forest/TreeA"]))
print("TreeA mask:", [str(p.GetPath()) for p in stage.Traverse()])
stage.ExpandPopulationMask()                 # follow TreeA.neighbor
print("expanded:", stage.GetPopulationMask())
print("now:", [str(p.GetPath()) for p in stage.Traverse()])
```

**Expected output**

```text
masked: ['/Forest', '/Forest/TreeB', '/Forest/TreeB/Trunk']
TreeA valid? False
Includes /Forest: True IncludesSubtree /Forest: False
TreeA mask: ['/Forest', '/Forest/TreeA']
expanded: UsdStagePopulationMask([ /Forest/TreeA /Forest/TreeB ])
now: ['/Forest', '/Forest/TreeA', '/Forest/TreeB', '/Forest/TreeB/Trunk']
```

### 9. Real-world use case

A render-farm "camera export" job opens a 50 GB shot with a mask of `/Shot/Cameras` and finishes in seconds. A digital-twin dashboard opens only `/Plant/Line_3` of a whole factory. A review tool opens one character in isolation and then calls `ExpandPopulationMask()` so its materials, found through bindings, come along.

### 10. Common mistakes

> [!MISTAKE] Masking to one prim and finding its material binding target missing. Bindings are relationships to prims that may be outside the mask. Call `stage.ExpandPopulationMask()` or add the material paths to the mask.

> [!MISTAKE] Using a mask to save memory but still loading every payload inside it. Combine: `OpenMasked(path, mask, Usd.Stage.LoadNone)` and load what you need.

### 11. Exam traps

> [!TRAP] "A population mask is the same as unloading." No. Unloaded prims still exist on the stage; prims outside a mask do not exist at all (invalid prim).

> [!TRAP] "Masking `/A/B` also gives `/A`'s other children." No. Ancestors are included as path holders only; their other children are excluded.

### 12. Practice questions

**Q1.** A stage is opened with mask `[/World/Car]`. Which prim is **not** on the stage?
A. `/World` · B. `/World/Car` · C. `/World/Car/Wheel` · D. `/World/Truck`

**Q2.** Select two. Which are true?
A. `Usd.Stage.OpenMasked` accepts an initial load set.
B. Prims outside the mask exist but are unloaded.
C. `ExpandPopulationMask()` can add relationship targets to the mask.
D. Masks are saved in the root layer.

**Answers**

**Q1 — D.** Ancestors (A), the mask path (B), and descendants (C) are included; siblings are not.
**Q2 — A, C.** Outside prims do not exist (B); masks are stage state (D).

### 13. Exam takeaways

> [!KEY]
> - `Usd.Stage.OpenMasked(path, Usd.StagePopulationMask([...]))` composes only part of the namespace.
> - Included: mask paths, their descendants, their ancestors (not the ancestors' other children).
> - Outside the mask = invalid prim, not "unloaded".
> - Masks work on any scene; payloads only where authored. Combine both for big scenes.

---

## 17.5 Payloads vs. references: strength and use cases

### 1. What is it?

A comparison of payloads and references: where each sits in strength order (LIVERPS), and when to use which.

### 2. Why do we need it?

Objective 1.3 asks you to compare referencing, payloads, and sublayers. Exam questions test both the strength order (R is stronger than P) and the design choice (which arc to use for heavy data).

### 3. Beginner explanation

Both are catalog links. The **reference** is a part bolted to your design: always there. The **payload** is the box in storage: present only when fetched. When both describe the same thing, the bolted-on part's description wins.

Where the analogy breaks: "stronger" is not about loading. A loaded payload is still weaker than a reference on the same prim.

### 4. Technical explanation

- LIVERPS: Local, Inherits, VariantSets, rElocates, **References**, **Payloads**, Specializes. On one prim, any reference opinion beats any payload opinion for the same property.
- Opinions only in the payload still apply when loaded (nothing stronger competes).
- When unloaded, payload opinions disappear, so values may change, not just children.
- Choosing:

| Need | Use |
|------|-----|
| Always-needed, lightweight data (asset interface, transforms, look selection) | Reference |
| Heavy data the user may skip (geometry, high-res textures, simulation caches) | Payload |
| Whole layer at the same paths (department or override layer) | Sublayer |
| Open only part of any scene, regardless of arcs | Population mask |

- Common asset pattern (Chapter 23): the shot **references** an asset's entry file; inside it, the asset root has a **payload** to its geometry. The shot can still unload it, because payloads inside referenced files remain loadable from the stage.

### 5. Mental model

```text
 strength on one prim (strongest first):
   L  local layer stack        <- your overrides
   I  inherits
   V  variant sets
   E  relocates
   R  references   ---+
   P  payloads     ---+  "R before P": reference beats payload
   S  specializes

 R and P: same targeting rules; only P can be unloaded.
```

### 6. Simple example

`/X` references `a.usda` (`radius = 1`) and has a payload to `b.usda` (`radius = 2`, `tag = "fromPayload"`).

| State | `radius` | `tag` |
|-------|----------|-------|
| Loaded | 1 (reference wins) | `"fromPayload"` |
| Unloaded | 1 | does not exist |

### 7. USDA example

```usda
#usda 1.0

def "X" (
    prepend payload = @./b.usda@
    prepend references = @./a.usda@
)
{
}
```

Notes: the order in which the two fields are written in the file does not matter; strength comes from the arc type (R before P), not from line order.

### 8. Python example

```python
from pxr import Usd

files = {
    "a.usda": '#usda 1.0\n(\n    defaultPrim = "M"\n)\n'
              'def Sphere "M"\n{\n    double radius = 1\n}\n',
    "b.usda": '#usda 1.0\n(\n    defaultPrim = "M"\n)\n'
              'def Sphere "M"\n{\n    double radius = 2\n'
              '    custom string tag = "fromPayload"\n}\n',
    "shot.usda": '#usda 1.0\ndef "X" (\n'
                 '    prepend payload = @./b.usda@\n'
                 '    prepend references = @./a.usda@\n)\n{\n}\n',
}
for name, text in files.items():
    with open(name, "w") as f:
        f.write(text)

def report(stage, label):
    x = stage.GetPrimAtPath("/X")
    tag = x.GetAttribute("tag")
    print(f"{label:9} loaded={x.IsLoaded()} radius={x.GetAttribute('radius').Get()}"
          f" tag={tag.Get() if tag else None}")

stage = Usd.Stage.Open("shot.usda")
report(stage, "loaded")
query = Usd.PrimCompositionQuery(stage.GetPrimAtPath("/X"))
for arc in query.GetCompositionArcs():
    print("  arc:", arc.GetArcType(), arc.GetTargetLayer().identifier.split("/")[-1])
stage.Unload("/X")
report(stage, "unloaded")
```

**Expected output**

```text
loaded    loaded=True radius=1.0 tag=fromPayload
  arc: Pcp.ArcTypeRoot shot.usda
  arc: Pcp.ArcTypeReference a.usda
  arc: Pcp.ArcTypePayload b.usda
unloaded  loaded=False radius=1.0 tag=None
```

`Usd.PrimCompositionQuery` lists the arcs strongest first: the root layer, then the reference, then the payload (Chapter 22 covers this tool).

### 9. Real-world use case

In a games studio's level editor, each building is referenced (so its transform and collision proxy are always present) and its high-detail interior is a payload loaded only when the designer enters it. In a factory digital twin, each machine's metadata (serial number, sensor IDs) is in the referenced interface, and its CAD-derived meshes are behind a payload.

### 10. Common mistakes

> [!MISTAKE] Putting overrides for an asset in a payload and expecting them to beat its reference. They lose (P is weaker than R). Put overrides in the local layer stack.

> [!MISTAKE] Putting everything behind payloads, including the data needed to place and select assets. Unloaded assets then have no transform or `kind`. Keep the interface in a reference (or local opinions) and only the heavy data in the payload.

### 11. Exam traps

> [!TRAP] "Payloads are stronger than references because they are loaded later." Wrong reasoning. Load timing has nothing to do with strength: R beats P.

> [!TRAP] "Payloads replace references in modern USD." No. Both arcs exist and are used together; each has its own job.

### 12. Practice questions

**Q1.** On one prim, a reference sets `color = red` and a loaded payload sets `color = blue`. A sublayer of the root layer has no opinion. What is `color`?
A. red · B. blue · C. empty · D. depends on line order in the file

**Q2.** Select two. Which data typically belongs behind a payload?
A. A 2-million-polygon mesh
B. The asset's `kind` and root transform
C. A simulation cache of 500 frames
D. The shot's camera

**Answers**

**Q1 — A.** References (R) are stronger than payloads (P); line order does not matter.
**Q2 — A, C.** Heavy, optional data. `kind`/transform and cameras must always be available.

### 13. Exam takeaways

> [!KEY]
> - LIVERPS: R before P — a reference beats a payload on the same prim.
> - Payload opinions vanish when unloaded; values can change, not only children.
> - Reference the lightweight interface, payload the heavy data, sublayer whole layers.
> - Payloads inside referenced files are still loadable from the stage.

---

## Chapter lab(s)

- **Lab 15 — Payloads, load rules, population masks** (★★☆). You build a city of payload-backed blocks, open it with `LoadNone`, load a working set with `Load` and `LoadAndUnload`, save and reapply it as `Usd.StageLoadRules`, and finally open one block alone with `OpenMasked`, timing each approach.

The lab is in Part X (`python-labs/`).

## USDA reading exercises

**Exercise 17-A.** Using `room.usda`, `bldg.usda`, and `city.usda` from Section 17.2, the stage is opened with `Usd.Stage.LoadNone`, then `stage.Load("/City/B1", Usd.LoadWithoutDescendants)` runs. List the prims visited by `stage.Traverse()` and by `stage.TraverseAll()`.

**Exercise 17-B.** In this layer, `a.usda`'s default prim has `double size = 5` and `b.usda`'s default prim has `double size = 9` and `double depth = 2`. The stage is opened with `LoadAll`. What are `size` and `depth` on `/Crate`? What changes after `stage.Unload("/Crate")`?

```usda
#usda 1.0

def "Crate" (
    prepend payload = @./b.usda@
    prepend references = @./a.usda@
)
{
}
```

**Answers**

**17-A** — `Traverse()`: `/City`, `/City/B1`. `TraverseAll()`: `/City`, `/City/B1`, `/City/B1/Room1`. `Room1` exists (it comes from the loaded `bldg.usda`) but is unloaded, so the default traversal skips it, and `Wall` does not exist yet.

**17-B** — Loaded: `size = 5` (reference beats payload), `depth = 2` (only the payload has it). After unloading: `size` is still 5; `depth` no longer exists.

---

## Chapter review

### Summary

- A payload is a reference that can be left unloaded; keyword `payload`, API `prim.GetPayloads()`.
- Unloaded payload prims exist but have none of the payload's content; `Traverse()` skips them.
- `Usd.Stage.Open(path, Usd.Stage.LoadNone)` opens with nothing loaded; the default is `LoadAll`.
- `Load` / `Unload` / `LoadAndUnload` manage the working set; `Load` includes descendants unless `Usd.LoadWithoutDescendants`.
- `Usd.StageLoadRules` (AllRule, OnlyRule, NoneRule) describes load state compactly; empty rules load all.
- Load state and masks are stage state; nothing is written to layers.
- `Usd.Stage.OpenMasked` with a `Usd.StagePopulationMask` composes only mask paths, their descendants and ancestors.
- Prims outside a mask are invalid; `ExpandPopulationMask()` follows relationships.
- In LIVERPS, references are stronger than payloads (R before P).
- Reference the light interface, payload the heavy data, sublayer whole layers.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `prepend payload = @…@` | Payload arc: loadable, weaker than references |
| "open quickly, load later" | `Usd.Stage.Open(path, Usd.Stage.LoadNone)` + `Load` |
| Prim present but children missing | Unloaded payload (`IsLoaded()` is `False`) |
| `Traverse()` misses prims that `GetPrimAtPath` finds | Default predicate skips unloaded prims; use `TraverseAll()` |
| `AllRule` / `OnlyRule` / `NoneRule` | `Usd.StageLoadRules` |
| "Only this part of the namespace" | `Usd.Stage.OpenMasked` + `Usd.StagePopulationMask` |
| `GetPrimAtPath` returns invalid in a masked stage | Prim is outside the mask |
| Reference and payload disagree | Reference wins |

### Review questions

**R17-01** · Obj 1.3 · Single choice
What is the main difference between a payload and a reference?
A. Payloads cannot target a prim path.
B. Payloads can be unloaded, so their content is composed only on demand.
C. Payloads bring in the whole layer at the same paths.
D. Payloads are stronger than local opinions.

**R17-02** · Obj 1.3 · Single choice
Which call opens a stage with no payloads composed?
A. `Usd.Stage.Open("s.usda", Usd.Stage.LoadNone)`
B. `Usd.Stage.Open("s.usda", Usd.StageLoadRules.NoneRule)`
C. `Usd.Stage.Open("s.usda", load=False)`
D. `Usd.Stage.OpenMasked("s.usda", Usd.StagePopulationMask())` with the default load set

**R17-03** · Obj 1.3 · Select two.
A stage was opened with `LoadNone`. `/Set/Tree` has a payload. Which are true before anything is loaded?
A. `stage.GetPrimAtPath("/Set/Tree")` is valid.
B. `stage.Traverse()` visits `/Set/Tree`.
C. `stage.FindLoadable()` includes `/Set/Tree`.
D. `/Set/Tree`'s payload children are valid prims.

**R17-04** · Obj 1.3 · Single choice
`/City/B1` has a payload; inside it, `/City/B1/Room1` has another. After `stage.Load("/City/B1")` on a `LoadNone` stage, what is the load set?
A. `[]` · B. `[/City/B1]` · C. `[/City/B1, /City/B1/Room1]` · D. `[/City]`

**R17-05** · Obj 1.3 · Single choice
Which `Usd.StageLoadRules` object loads everything?
A. `Usd.StageLoadRules()` (empty) · B. `Usd.StageLoadRules.LoadNone()` · C. One entry `(/, OnlyRule)` · D. One entry `(/, NoneRule)`

**R17-06** · Obj 1.3 · Single choice
Rules: `(/, NoneRule) (/Set, OnlyRule)`. `/Set` has a payload, and `/Set/Car` (from inside it) has another. What is loaded?
A. Nothing · B. `/Set` only · C. `/Set` and `/Set/Car` · D. Everything

**R17-07** · Obj 1.3 · Single choice
A stage is opened with mask `[/World/Cams/Main]`. Which prim is on the stage?
A. `/World/Lights` · B. `/World/Cams/Alt` · C. `/World/Cams` · D. `/Props`

**R17-08** · Obj 1.3 · Select two.
Which statements about population masks are true?
A. Prims outside the mask are returned as invalid prims.
B. A mask only affects prims that have payloads.
C. `ExpandPopulationMask()` can add relationship targets.
D. Masks are written to the root layer on `Save()`.

**R17-09** · Obj 1.3 · USDA reading
`/Lamp` has `prepend references = @./lamp_a.usda@` (`intensity = 10`) and `prepend payload = @./lamp_b.usda@` (`intensity = 50`). The stage is fully loaded and has no local `intensity`. What is `intensity`?
A. 10 · B. 50 · C. 60 · D. no value

**R17-10** · Obj 1.3 · Single choice
A team wants every asset's transform and `kind` always available, but its heavy geometry optional. Which structure fits?
A. Put everything in a payload.
B. Reference the asset interface; put geometry behind a payload inside it.
C. Sublayer every asset into the shot.
D. Put the geometry in a variant set.

**R17-11** · Obj 1.3 · Python reading
A forest file has payload prims `/Forest/TreeA` and `/Forest/TreeB`. What does this print? (Not run automatically: it needs that forest file; Section 17.1 shows how to create it.)

```{.python .norun}
from pxr import Usd

stage = Usd.Stage.Open("forest.usda", Usd.Stage.LoadNone)
stage.Load("/Forest/TreeA")
print([str(p) for p in stage.GetLoadSet()], stage.GetRootLayer().dirty)
```

A. `['/Forest/TreeA'] False` · B. `['/Forest/TreeA'] True` · C. `['/Forest/TreeA', '/Forest/TreeB'] False` · D. `[] False`

**R17-12** · Obj 1.3 · Single choice
Which is true about payloads inside a referenced asset?
A. They are always loaded and cannot be unloaded from the referencing stage.
B. They are loadable and unloadable from the referencing stage like any payload.
C. They turn into references.
D. They are ignored.

### Review answers

**R17-01 — B** (Obj 1.3). Payloads target prims like references (not A), only sublayers bring whole layers (not C), and P is weaker than L (not D). Review: §17.1.

**R17-02 — A** (Obj 1.3). B passes a rule value where an initial load set is expected; C is not a valid argument; D loads all payloads by default, and an empty mask excludes every prim (verified: the stage is empty). Review: §17.2.

**R17-03 — A, C** (Obj 1.3). The prim exists and is loadable, but the default traversal skips unloaded prims (B), and its payload children do not exist yet (D). Review: §17.1, §17.2.

**R17-04 — C** (Obj 1.3). `Load` defaults to `Usd.LoadWithDescendants`, so the nested payload loads too (verified in §17.2). Review: §17.2.

**R17-05 — A** (Obj 1.3). Empty rules mean "load all". B and D load nothing; C loads only the root's own payload (if any). Review: §17.3.

**R17-06 — B** (Obj 1.3). `OnlyRule` loads `/Set`'s payload but not payloads below it. Review: §17.3.

**R17-07 — C** (Obj 1.3). `/World/Cams` is an ancestor of the mask path. Siblings (B) and other branches (A, D) are excluded. Review: §17.4.

**R17-08 — A, C** (Obj 1.3). Masks apply to all prims (not B) and are stage state (not D). Review: §17.4.

**R17-09 — A** (Obj 1.3). The reference (R) beats the payload (P). Opinions do not add up (not C). Review: §17.5.

**R17-10 — B** (Obj 1.3). This is the standard asset pattern. A hides the interface when unloaded; C cannot place assets at new paths; D does not provide on-demand loading. Review: §17.5.

**R17-11 — A** (Obj 1.3). Only TreeA is loaded, and loading writes nothing to the layer, so `dirty` stays `False` (behavior verified in §17.2). Review: §17.2.

**R17-12 — B** (Obj 1.3). Payloads keep working through references; the stage's load rules apply to them. Review: §17.5.

## Further reading

- [S04] OpenUSD Glossary — entries "Payload", "Load / Unload", "LIVERPS": https://openusd.org/release/glossary.html
- [S06] OpenUSD API reference — `UsdPayloads`, `UsdStage` (Load, Unload, LoadAndUnload, OpenMasked), `UsdStageLoadRules`, `UsdStagePopulationMask`: https://openusd.org/release/api/index.html
- [S11] Maximizing USD Performance (payloads and working sets): https://openusd.org/release/maxperf.html
- [S14] NVIDIA Learn OpenUSD — "Creating Composition Arcs" and "Asset Modularity and Instancing": https://docs.nvidia.com/learn-openusd/latest/index.html
- [S15] NVIDIA Omniverse USD code samples — "Add a Payload": https://docs.omniverse.nvidia.com/usd/latest/index.html
- [S16] Principles of Scalable Asset Structure in OpenUSD: https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
