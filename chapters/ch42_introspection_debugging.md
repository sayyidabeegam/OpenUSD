# Chapter 42 — Stage Introspection and Composition Debugging

> **Exam domain:** Debugging & Troubleshooting (11%) · **Objectives:** 6.2, 6.3, 6.4 · **Study day:** 12 · **Est. time:** 110 min
> **Prerequisites:** Ch 15 (layer stacks, edit targets), Ch 16–18 (references, payloads, variants), Ch 21 (LIVERPS), Ch 22.5–22.6 (composition stacks), Ch 33 (asset resolution), Ch 39–41 (what "looks wrong" means)

When a composed stage is wrong, the data is almost never gone. It is in a layer you are not looking at, on a path you did not type, behind a payload you did not load, or weaker than another opinion. This chapter is a **symptom playbook**: inspect the stack, find missing prims, see who won, repair broken arcs and asset paths, and explain visual bugs. Chapter 22 taught the APIs (`GetPrimStack`, `GetPropertyStack`, `PrimCompositionQuery`). Here you *use* them against the bugs the exam names in Obj 6.2, 6.3, and 6.4.

Diagnostics (`TfDebug`, Trace) wait until Chapter 43. Performance knobs wait until Chapter 44.

## Learning goals

- Print a layer stack, name the edit target, and mute a layer to test who is contributing.
- Distinguish invalid, inactive, undefined, unloaded, and instance-proxy prims.
- Read a property stack and resolve-info to explain why an opinion did not win (Obj 6.2).
- Diagnose missing references, missing `defaultPrim`, bad variant selections, and composition errors.
- Find unresolved asset paths with `ComputeAllDependencies` (Obj 6.3).
- Map unexpected pictures to purpose, visibility, extents, subdivision, units, and bindings (Obj 6.4).
- Follow a fixed debugging order instead of guessing.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Layer stack** | The session layer (optional) + root layer + sublayers, strongest first. |
| **Edit target** | The layer (or variant site) new `Usd` edits write into. |
| **Muted layer** | A layer the stage is told to ignore (`MuteLayer`). |
| **Invalid prim** | `GetPrimAtPath` returned a handle with `IsValid() == False` (no such path). |
| **Inactive prim** | Exists but `active = false`; children are pruned from composition. |
| **Undefined prim** | An `over` with no `def` anywhere; `IsDefined()` is False. |
| **Unloaded prim** | A payload (or ancestor payload) not loaded; children are missing. |
| **Property stack** | The list of specs for one property, strongest first. |
| **Composition error** | A Pcp error captured on the stage (`GetCompositionErrors()`). |
| **Unresolved asset** | A path `ComputeAllDependencies` could not turn into a file. |

---

## 42.1 Inspecting layers and layer stacks

### 1. What is it?
A composed value is the winner among **layers** in a **layer stack**. Introspection starts by listing those layers, the **edit target** (where your Python writes), and whether any layer is **muted**.

### 2. Why do we need it?
If you do not know which files are in play, you will "fix" the asset while the shot's stronger sublayer keeps winning, or you will author into the session layer and lose the edit on reopen. Obj 6.2 often starts with "which layer?"

### 3. Beginner explanation
Think of a stack of transparent sheets on a projector (Chapter 3). Debugging is flipping through the sheets: which sheet is on top (session), which is the cardboard backing (root), which overlays you slipped in (sublayers, first-listed stronger), and whether someone taped a "skip me" note on a sheet (mute).

*Where the analogy breaks:* a reference is not another sheet in *this* stack. It is a stack of its own, reached by an arc. `GetLayerStack()` does not list referenced files; `GetPrimStack()` / `GetUsedLayers()` do.

### 4. Technical explanation
- `stage.GetLayerStack(includeSessionLayers=True)` returns `[session, root, sublayer0, sublayer1, …]` **strongest first**. `False` drops the session layer. The session layer's display name is `<rootDisplay>-session.usda` (verified: `root.usda` → `root-session.usda`).
- **Root is stronger than every sublayer.** First-listed sublayer is stronger than later ones. Session is stronger than the root. Same rule as Chapter 15.
- `stage.GetEditTarget().GetLayer()` is where `Usd` APIs author. Default is the root layer. `SetEditTarget(stage.GetSessionLayer())` makes session edits: they win, and they vanish if you do not export the session layer.
- `stage.MuteLayer(identifier)` / `UnmuteLayer` / `GetMutedLayers()` / `IsLayerMuted`. Identifier is the resolved layer id (use `os.path.abspath("b.usda")` for a file you opened relatively). Muting removes that layer's opinions; composition recomputes.
- `stage.GetUsedLayers()` is every layer the composed scene actually opened (root, session, sublayers, **and** referenced/payload layers). Broader than `GetLayerStack()`.
- `GetDisplayName()` is the short name for logs; `identifier` may be an absolute path. Print display names in this book so output stays portable.
- usdview's **Layer Stack** tab is this list. `usd-core` has no usdview; Python is the stand-in.

### 5. Mental model

```text
strongest  session     (includeSessionLayers=True)
           root        (always; default edit target)
           sublayer[0] (first in subLayers = stronger)
           sublayer[1]
weakest    …

MuteLayer(id)  →  that sheet is pulled out of the projector
GetUsedLayers  →  this stack PLUS referenced / payload files
```

### 6. Simple example
Root lists sublayers `[b.usda, a.usda]`. `a` defs a Sphere radius 1; `b` overs radius 2. Composed radius is **2**. Mute `b` → **1**. Session sets 9 → **9**, winning layer `root-session.usda`.

### 7. USDA example

*File: a.usda*

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 1
    }
}
```

*File: b.usda*

```usda
#usda 1.0

over "World"
{
    over "Ball"
    {
        double radius = 2
    }
}
```

*File: root.usda*

```usda
#usda 1.0
(
    subLayers = [
        @./b.usda@,
        @./a.usda@
    ]
)
```

- `b` is listed first, so it beats `a`. The root file itself authors nothing on `radius`.
- Session is not a file on disk until you export it.

### 8. Python example

```python
import os
from pxr import Usd

files = {
    "a.usda": """#usda 1.0
def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 1
    }
}
""",
    "b.usda": """#usda 1.0
over "World"
{
    over "Ball"
    {
        double radius = 2
    }
}
""",
    "root.usda": """#usda 1.0
(
    subLayers = [
        @./b.usda@,
        @./a.usda@
    ]
)
""",
}
for name, text in files.items():
    with open(name, "w") as f:
        f.write(text)

stage = Usd.Stage.Open("root.usda")
print("edit target:", stage.GetEditTarget().GetLayer().GetDisplayName())
print("with session:")
for lyr in stage.GetLayerStack(includeSessionLayers=True):
    print(" ", lyr.GetDisplayName())
print("no session:")
for lyr in stage.GetLayerStack(includeSessionLayers=False):
    print(" ", lyr.GetDisplayName())
ball = stage.GetPrimAtPath("/World/Ball").GetAttribute("radius")
print("radius:", ball.Get())
ident_b = os.path.abspath("b.usda")
stage.MuteLayer(ident_b)
print("muted:", [os.path.basename(x) for x in stage.GetMutedLayers()])
print("radius muted b:", ball.Get())
stage.UnmuteLayer(ident_b)
print("radius unmuted:", ball.Get())
stage.SetEditTarget(stage.GetSessionLayer())
ball.Set(9)
print("radius session:", ball.Get())
print("winning layer:", ball.GetPropertyStack()[0].layer.GetDisplayName())
```

**Expected output**
```text
edit target: root.usda
with session:
  root-session.usda
  root.usda
  b.usda
  a.usda
no session:
  root.usda
  b.usda
  a.usda
radius: 2.0
muted: ['b.usda']
radius muted b: 1.0
radius unmuted: 2.0
radius session: 9.0
winning layer: root-session.usda
```

Muting is a *test*, not a fix. If muting `b` "repairs" the value, you found the layer that was winning.

### 9. Real-world use case
A lighting TD swears they set radius in `shot_light.usda`. You print the layer stack and see `shot_anim.usda` listed *before* it (stronger). Mute anim: the light value appears. The fix is a conversation about sublayer order, not another override in a weaker file.

### 10. Common mistakes
> [!MISTAKE] Calling `GetLayerStack()` and wondering where the referenced asset is. Use `GetUsedLayers()` or `prim.GetPrimStack()`.

> [!MISTAKE] Authoring on the default edit target (root) when you meant a sublayer. Check `GetEditTarget()` before every debug `Set`.

> [!MISTAKE] Muting with the USDA token `@./b.usda@` as the id. `MuteLayer` wants the resolved identifier (`abspath` of the opened file).

### 11. Exam traps
> [!TRAP] "The first sublayer is weakest." First-listed sublayer is **strongest among sublayers**. The root still beats all of them.

> [!TRAP] Session layer is not in `GetLayerStack()` by default. Pass `includeSessionLayers=True` (and it is the default in 26.08 if you omit the flag — this book always passes it so the call is readable).

> [!TRAP] Muting a layer deletes it from disk. Mute is per-stage and in-memory.

### 12. Practice questions
1. Root has `subLayers = [@./b.usda@, @./a.usda@]`. Who wins between `a` and `b`?
2. After `SetEditTarget(session)` and `Set(9)`, which display name does `GetPropertyStack()[0].layer` show?
3. Does `GetLayerStack()` include a referenced `lamp.usda`?

**Answers**
1. **`b`** (first-listed sublayer).
2. **`root-session.usda`** (or `<root>-session.usda`).
3. **No.** That file is on a reference arc; use `GetUsedLayers()` / prim stack.

### 13. Exam takeaways
> [!KEY]
> - Stack = session > root > sublayers (first-listed stronger).
> - Print `GetLayerStack` and `GetEditTarget` before chasing a value.
> - `MuteLayer` is a diagnostic: if the bug vanishes, you found the winning layer.
> - Referenced files are not in this stack.

---

## 42.2 Missing prims

### 1. What is it?
A "missing prim" is several different states that look the same in a viewport: **invalid path**, **inactive**, **undefined `over`**, **unloaded payload**, or **instance proxy skipped by `Traverse()`**. You distinguish them with `IsValid`, `IsActive`, `IsDefined`, `IsLoaded`, `IsInstanceProxy`, and `Traverse` vs `TraverseAll`.

### 2. Why do we need it?
Guessing "the reference is broken" when the prim is only inactive wastes an hour. Each state has a different fix. Obj 6.2 includes "the prim I authored is not on the stage."

### 3. Beginner explanation
You look for a coworker at their desk. They might have the wrong office number (invalid path), be on leave (inactive), be a nameplate with no person yet (`over` / undefined), be in a locked archive (unloaded payload), or be a photocopied extra that the lobby directory does not list (`Traverse` skips instance proxies).

*Where the analogy breaks:* an inactive prim's *children* become invalid handles, not merely inactive. You cannot walk into the locked office's closet.

### 4. Technical explanation
- **`GetPrimAtPath("/World/Nope")` always returns a handle.** Ask `IsValid()`. False means no spec composed at that path.
- **Inactive:** `prim.SetActive(False)` / metadata `active = false`. `IsValid()` True, `IsActive()` False, `IsDefined()` True. `Traverse()` skips it and its descendants. `TraverseAll()` includes it. Children: `GetPrimAtPath` on a child returns **invalid** (not composed).
- **Undefined `over`:** specifier `Sdf.SpecifierOver`, `IsDefined()` False, empty type name. `Traverse()` skips it; `TraverseAll()` includes it. Usually a typo (`over "Wrold"`).
- **Payload vs reference, `LoadNone`:** `Usd.Stage.Open(path, Usd.Stage.LoadNone)` **still loads references**. Payloads stay unloaded: `IsLoaded()` False, `GetTypeName()` `''`, children invalid. `stage.Load("/World/Lazy")` populates them. `Traverse()` skips unloaded payloads; `TraverseAll()` includes the payload root but not its unloaded children.
- **Instancing:** `Traverse()` visits instance roots, not descendants. `GetPrimAtPath("/World/A/S")` is valid with `IsInstanceProxy()` True. Edits below the instance root do not stick (Chapter 24).
- Also check: wrong `defaultPrim` (prim exists *inside* the asset at `/Only`, not at the referencing path); muted layer that held the `def`; composition error (next section).

### 5. Mental model

```text
handle = GetPrimAtPath(p)
         │
         ├─ not IsValid          → path never composed (typo, child of inactive,
         │                          unloaded payload child, muted def)
         ├─ IsValid, not Active  → deactivated; children invalid
         ├─ IsValid, not Defined → stray over
         ├─ IsValid, not Loaded  → payload (or ancestor) unloaded
         └─ IsInstanceProxy      → live view of a prototype; Traverse skipped it
```

### 6. Simple example
Stage opened with `LoadNone`. `/World/Loaded` (reference) is an Xform with `/Geo`. `/World/Lazy` (payload) is defined, unloaded, no `/Geo`. `/World/Nope` is inactive; `/World/Nope/Hidden` is invalid. `/World/TypoBall` is an undefined over.

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    def "Loaded" (
        prepend references = @./asset.usda@
    )
    {
    }

    def "Lazy" (
        prepend payload = @./asset.usda@
    )
    {
    }

    def "Nope" (
        active = false
    )
    {
        def Sphere "Hidden"
        {
        }
    }

    over "TypoBall"
    {
        double radius = 4
    }
}
```

- `Loaded` vs `Lazy` is the reference/payload split. Same target file; different load rules.
- `TypoBall` has no matching `def` anywhere.

### 8. Python example

```python
from pxr import Usd

asset = """#usda 1.0
(
    defaultPrim = "Prop"
)
def Xform "Prop"
{
    def Cube "Geo"
    {
        double size = 1
    }
}
"""
shot = """#usda 1.0
def Xform "World"
{
    def "Loaded" (
        prepend references = @./asset.usda@
    )
    {
    }
    def "Lazy" (
        prepend payload = @./asset.usda@
    )
    {
    }
    def "Nope" (
        active = false
    )
    {
        def Sphere "Hidden" {}
    }
    over "TypoBall"
    {
        double radius = 4
    }
}
"""
open("asset.usda", "w").write(asset)
open("shot.usda", "w").write(shot)

st = Usd.Stage.Open("shot.usda", Usd.Stage.LoadNone)
print("missing valid:", st.GetPrimAtPath("/World/Missing").IsValid())
nope = st.GetPrimAtPath("/World/Nope")
print("Nope valid/active/defined:",
      nope.IsValid(), nope.IsActive(), nope.IsDefined())
hid = st.GetPrimAtPath("/World/Nope/Hidden")
print("Hidden valid:", hid.IsValid())
lazy = st.GetPrimAtPath("/World/Lazy")
print("Lazy loaded/type:", lazy.IsLoaded(), repr(lazy.GetTypeName()))
loaded = st.GetPrimAtPath("/World/Loaded")
print("Loaded loaded/type:", loaded.IsLoaded(), repr(loaded.GetTypeName()))
print("Loaded/Geo:", st.GetPrimAtPath("/World/Loaded/Geo").IsValid())
print("Lazy/Geo unloaded:", st.GetPrimAtPath("/World/Lazy/Geo").IsValid())
print("traverse:", [str(p.GetPath()) for p in st.Traverse()])
print("traverseAll:", [str(p.GetPath()) for p in st.TraverseAll()])
typo = st.GetPrimAtPath("/World/TypoBall")
print("TypoBall specifier:", typo.GetSpecifier(),
      "defined:", typo.IsDefined(), "type:", repr(typo.GetTypeName()))
st.Load("/World/Lazy")
print("Lazy after Load type:",
      repr(st.GetPrimAtPath("/World/Lazy").GetTypeName()),
      "Geo:", st.GetPrimAtPath("/World/Lazy/Geo").IsValid())
```

**Expected output**
```text
missing valid: False
Nope valid/active/defined: True False True
Hidden valid: False
Lazy loaded/type: False ''
Loaded loaded/type: True 'Xform'
Loaded/Geo: True
Lazy/Geo unloaded: False
traverse: ['/World', '/World/Loaded', '/World/Loaded/Geo']
traverseAll: ['/World', '/World/Loaded', '/World/Loaded/Geo', '/World/Lazy', '/World/Nope', '/World/TypoBall']
TypoBall specifier: Sdf.SpecifierOver defined: False type: ''
Lazy after Load type: 'Xform' Geo: True
```

`LoadNone` did **not** unload the reference. Only the payload stayed empty.

### 9. Real-world use case
A shot opens with `LoadNone` for speed (Chapter 17, 44). Layout cannot see set dressing parented under payloads and files a "missing assets" ticket. `TraverseAll` still lists the payload roots; `IsLoaded()` is the tell. Loading that branch restores `/Geo`.

### 10. Common mistakes
> [!MISTAKE] Treating `GetPrimAtPath` returning an object as "the prim exists." Always `IsValid()`.

> [!MISTAKE] Opening with `LoadNone` to "load nothing" and panicking that references vanished. They did not.

> [!MISTAKE] Using `Traverse()` to hunt instance internals or inactive prims. Use `GetPrimAtPath` + `TraverseAll`.

### 11. Exam traps
> [!TRAP] Child of an inactive prim is inactive. It is **invalid** (not composed).

> [!TRAP] `over "Ball"` with no `def` is a composed prim you can `GetAttribute` on — but `IsDefined()` is False and `Traverse()` skips it.

> [!TRAP] `IsInstanceProxy()` True means the prim is missing. It is present; `Traverse()` just does not yield it.

### 12. Practice questions
1. `LoadNone`: is a referenced prim loaded?
2. Inactive parent. Is `GetPrimAtPath(parent/child).IsValid()` True?
3. Why might `/World/A/S` be valid but absent from `Traverse()`?

**Answers**
1. **Yes.** Payloads are the ones left unloaded.
2. **False.** Children of inactive prims do not compose.
3. **`A` is instanceable** — `S` is an instance proxy.

### 13. Exam takeaways
> [!KEY]
> - Valid / active / defined / loaded / proxy are five different questions.
> - Inactive children are invalid. Undefined overs are `SpecifierOver`.
> - `LoadNone` still loads references. Payloads need `Load`.
> - `Traverse` is a filtered walk; `TraverseAll` + `GetPrimAtPath` for debugging.

---

## 42.3 Wrong opinions winning

### 1. What is it?
The prim is there, the attribute exists, and the value is still "wrong." A **stronger opinion** won: stronger layer, stronger LIVERPS arc, a **value block**, or **time samples vs Default**. `GetPropertyStack()` lists every spec strongest-first; `GetResolveInfo()` names the kind of value that won (Obj 6.2).

### 2. Why do we need it?
Without the stack you will add a fourth override instead of deleting or moving the one that already wins. Chapter 22.6 is the ten-point checklist; this section is the measurement.

### 3. Beginner explanation
Several people shout a number. The property stack is the attendance list in speaking order. The first name is who the stage heard. Resolve-info is *what kind* of sentence they used: a default, a time sample, a clip, a block ("nobody speak").

*Where the analogy breaks:* a quieter person (weaker spec) is still on the list. You can read their number; it just does not compose.

### 4. Technical explanation
- `attr.GetPropertyStack()` → `[Sdf.PropertySpec, …]`, strongest first. Each spec has `.layer`, `.path`, `.default`. The winning layer is `[0].layer`.
- Strength inside one stack: **session > root > earlier sublayers > later sublayers** for *local* specs, then weaker **arcs** (references, payloads, specializes) unless a stronger arc (inherits, variant, relocates) applies — LIVERPS, Chapter 21.
- `attr.GetResolveInfo(time)`: `GetSource()` is `Usd.ResolveInfoSourceDefault`, `TimeSamples`, `ValueClips`, `Spline`, `Fallback`, or `None`. `ValueIsBlocked()` is True when a stronger spec authored `None` (a **block**). `Get()` then returns `None`.
- **Default vs samples:** `Get()` with no time uses `Usd.TimeCode.Default()`. An authored default can still come back at Default even when samples exist. `Get(1)` at a numeric time uses samples (`ResolveInfoSourceTimeSamples`). Viewports usually play numeric time — `Get()` in a debug print can disagree with the picture.
- `GetPrimStack()` is the same idea for the prim itself (who contributed specs, including empty overs).
- Full arc list: `Usd.PrimCompositionQuery(prim).GetCompositionArcs()` (Chapter 22.5). Filter with `GetDirectReferences(prim)` when you only care about references.

> [!VERSION] Verified on USD 26.08. There is no `ResolveInfo` method that returns a layer; use `GetPropertyStack()[0].layer`. `GetMaster` does not exist; instancing uses `GetPrototype`.

### 5. Mental model

```text
GetPropertyStack()[0]   = who won (layer + path + default)
GetResolveInfo().source = how they won (default / samples / clips / block)

If your spec is on the list but not [0], you lost a strength fight.
If your spec is not on the list, you authored the wrong path or layer.
```

### 6. Simple example
Root local `height = 1`, stronger-than-reference lighting sublayer `height = 2`, referenced asset `height = 0.5`. Stack: shot (1), light (2), asset (0.5). Winner: **1** (root beats sublayers *and* the reference). Moon has default 9 and samples 1 / 4: `Get()` is 9, `Get(1)` is 1. Blocked sphere: `Get()` is `None`, `ValueIsBlocked` True.

### 7. USDA example

*File: shot.usda* (root) plus a lighting sublayer and a referenced asset:

```usda
#usda 1.0
(
    subLayers = [
        @./light.usda@
    ]
)

def Xform "World"
{
    def "Lamp_1" (
        prepend references = @./refsrc.usda@
    )
    {
        double height = 1
    }

    def Sphere "Moon"
    {
        double radius = 9
        double radius.timeSamples = {
            1: 1,
            24: 4,
        }
    }

    def Sphere "Blocked"
    {
        double radius = None
    }
}
```

- Root local `1` is stronger than `light.usda`'s `2` and the reference's `0.5`.
- `radius = None` is a block, not "radius zero."

### 8. Python example

```python
from pxr import Usd

open("refsrc.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Lamp"
)
def Xform "Lamp"
{
    double height = 0.5
}
""")
open("light.usda", "w").write("""#usda 1.0
over "World"
{
    over "Lamp_1"
    {
        double height = 2
    }
}
""")
open("shot.usda", "w").write("""#usda 1.0
(
    subLayers = [
        @./light.usda@
    ]
)
def Xform "World"
{
    def "Lamp_1" (
        prepend references = @./refsrc.usda@
    )
    {
        double height = 1
    }
    def Sphere "Moon"
    {
        double radius = 9
        double radius.timeSamples = {
            1: 1,
            24: 4,
        }
    }
    def Sphere "Blocked"
    {
        double radius = None
    }
}
""")

so = Usd.Stage.Open("shot.usda")
h = so.GetPrimAtPath("/World/Lamp_1").GetAttribute("height")
print("height:", h.Get())
print("property stack:")
for spec in h.GetPropertyStack():
    print(" ", spec.layer.GetDisplayName(), spec.path, spec.default)
print("resolve source:", h.GetResolveInfo().GetSource())
print("winning layer:", h.GetPropertyStack()[0].layer.GetDisplayName())
moon = so.GetPrimAtPath("/World/Moon").GetAttribute("radius")
print("moon Get():", moon.Get())
print("moon Get(1):", moon.Get(1),
      "src", moon.GetResolveInfo(1).GetSource())
print("moon Default:", moon.Get(Usd.TimeCode.Default()),
      "src", moon.GetResolveInfo(Usd.TimeCode.Default()).GetSource())
blk = so.GetPrimAtPath("/World/Blocked").GetAttribute("radius")
print("blocked Get:", blk.Get(),
      "ValueIsBlocked", blk.GetResolveInfo().ValueIsBlocked())
```

**Expected output**
```text
height: 1.0
property stack:
  shot.usda /World/Lamp_1.height 1.0
  light.usda /World/Lamp_1.height 2.0
  refsrc.usda /Lamp.height 0.5
resolve source: Usd.ResolveInfoSourceDefault
winning layer: shot.usda
moon Get(): 9.0
moon Get(1): 1.0 src Usd.ResolveInfoSourceTimeSamples
moon Default: 9.0 src Usd.ResolveInfoSourceDefault
blocked Get: None ValueIsBlocked True
```

If you expected lighting's `2` to win, you swapped root vs sublayer strength. Root local wins.

### 9. Real-world use case
Anim publishes `radius` samples on a ball. A debug script prints `Get()` and reports 9 all day while usdview at frame 1 shows 1. The TD "fixes" the default, which still never plays. Reading `GetResolveInfo(1).GetSource()` would have said `TimeSamples` in one call.

### 10. Common mistakes
> [!MISTAKE] Comparing `Get()` to the viewport without passing the viewport's time code.

> [!MISTAKE] Deleting the referenced asset's value because you see it on the stack. It is weaker; leave the asset, change the winner or remove the stronger spec.

> [!MISTAKE] Reading `radius = None` as "use the fallback 1." It **blocks**; weaker radii never apply.

### 11. Exam traps
> [!TRAP] "A sublayer always beats the root." The root beats sublayers. First-listed sublayer beats later sublayers.

> [!TRAP] Local reference opinion vs sublayer: both can be "local" in LIVERPS if they sit in the root layer stack. Order in the stack decides.

> [!TRAP] `Get()` ignoring samples "because samples always win." At `TimeCode.Default()`, an authored default still resolves as `SourceDefault` (verified above).

### 12. Practice questions
1. Stack lists shot 1, light 2, asset 0.5. Composed value?
2. What does `ValueIsBlocked()` True imply for `Get()`?
3. `Get()` is 9, usdview at frame 1 is 1. First call to make?

**Answers**
1. **1** (first spec).
2. **`Get()` is `None`**; weaker values are hidden.
3. **`Get(1)` and `GetResolveInfo(1).GetSource()`** — likely time samples.

### 13. Exam takeaways
> [!KEY]
> - Obj 6.2: `GetPropertyStack()[0]` is the winner; the rest lost.
> - Root > sublayers > referenced opinions (unless a stronger arc).
> - Blocks (`None`) are winners that contribute no number.
> - Pass the same time code the viewport uses.

---

## 42.4 Broken references, payloads, variants

### 1. What is it?
Arcs fail in three common ways: **the file cannot be opened** (`InvalidAssetPath`), **the file opens but the prim path is missing** (`UnresolvedPrimPath`, often no `defaultPrim`), or **the variant selection names a set member that does not exist** so the variant opinions never apply.

### 2. Why do we need it?
A referencing prim still *exists* (`IsDefined()` True) when the asset is missing — it is just an empty Xform with no type. The viewport looks like a missing model. `GetCompositionErrors()` is the difference between "USD ate my mesh" and "typo in the path" (Obj 6.2 / 6.3).

### 3. Beginner explanation
A library request can fail because the building is gone (missing file), the building is there but the catalog has no default shelf (`defaultPrim` missing and you did not pass `</Only>`), or you asked for the "tiny" edition of a book that only comes in small/big (bad variant selection).

*Where the analogy breaks:* USD still creates the referencing prim. You get an empty shelf label, not a crash.

### 4. Technical explanation
- `stage.GetCompositionErrors()` → Pcp errors. Opening the stage also prints them as **warnings** on stderr. Types you will see:
  - `Pcp.ErrorType_InvalidAssetPath` — file not found / unreadable (`@./missing.usda@`).
  - `Pcp.ErrorType_UnresolvedPrimPath` — file found, target prim not (message says `<defaultPrim>` when the reference omitted a prim path and the layer has no default).
- A failed reference: prim `IsDefined()` True, `GetTypeName()` `''`, no children from the asset.
- **Fix for no defaultPrim:** add `( defaultPrim = "Only" )` on the asset, or reference `@./nodef.usda@</Only>` with an explicit prim path (Chapter 16).
- **Variants:** `prim.GetVariantSets().HasVariantSet("size")` can be True (the set exists on the asset) while `GetVariantSelection("size")` is `"tiny"` and no `"tiny"` block exists. Attributes inside the real variants (`h`) then do not compose. Fallbacks (Chapter 38) only apply when **no** selection is authored. An authored wrong name blocks the fallback.
- Payloads use the same error types when the file is missing; when the file is fine but **unloaded**, there is often **no** composition error — go back to §42.2 `IsLoaded()`.
- `Usd.PrimCompositionQuery.GetDirectReferences(prim)` lists reference arcs that *did* bind, with `GetTargetLayer()`.

### 5. Mental model

```text
empty referencing prim
   ├─ GetCompositionErrors()
   │     InvalidAssetPath      → fix the @path@ (typo, cwd, resolver)
   │     UnresolvedPrimPath    → defaultPrim or explicit </Prim>
   └─ no error, IsLoaded False → payload not loaded
variant set exists, attribute missing
   └─ selection string not in the set (authored "tiny")
```

### 6. Simple example
`BadRef` → missing file → `InvalidAssetPath`, type `''`. `NoDefault` → `nodef.usda` has `def Sphere "Only"` but no defaultPrim → `UnresolvedPrimPath`, `/NoDefault/Only` invalid. Same file with `@./nodef.usda@</Only>` becomes a Sphere. `Var` selects `tiny`; `h` is missing.

### 7. USDA example

```usda
#usda 1.0

def Xform "World"
{
    def "BadRef" (
        prepend references = @./missing.usda@
    )
    {
    }

    def "NoDefault" (
        prepend references = @./nodef.usda@
    )
    {
    }

    def "Var" (
        prepend references = @./var.usda@
        variants = {
            string size = "tiny"
        }
    )
    {
    }
}
```

- All three prims compose as empty containers until you fix the arc or the selection.
- `var.usda` (not shown) has `defaultPrim` and variant names `small` / `big` only.

### 8. Python example

```python
from pxr import Usd

open("nodef.usda", "w").write("""#usda 1.0
def Sphere "Only"
{
    double radius = 1
}
""")
open("var.usda", "w").write("""#usda 1.0
(
    defaultPrim = "P"
)
def Xform "P" (
    prepend variantSets = "size"
)
{
    variantSet "size" = {
        "small" {
            double h = 1
        }
        "big" {
            double h = 3
        }
    }
}
""")
open("shot.usda", "w").write("""#usda 1.0
def Xform "World"
{
    def "BadRef" (
        prepend references = @./missing.usda@
    )
    {
    }
    def "NoDefault" (
        prepend references = @./nodef.usda@
    )
    {
    }
    def "Var" (
        prepend references = @./var.usda@
        variants = {
            string size = "tiny"
        }
    )
    {
    }
}
""")
open("ok.usda", "w").write("""#usda 1.0
def "X" (
    prepend references = @./nodef.usda@</Only>
)
{
}
""")

sb = Usd.Stage.Open("shot.usda")
print("error types:")
for err in sb.GetCompositionErrors():
    print(" ", err.errorType)
bad = sb.GetPrimAtPath("/World/BadRef")
print("BadRef defined/type:", bad.IsDefined(), repr(bad.GetTypeName()))
print("NoDefault/Only:", sb.GetPrimAtPath("/World/NoDefault/Only").IsValid())
var = sb.GetPrimAtPath("/World/Var")
print("selection:", var.GetVariantSets().GetVariantSelection("size"))
print("has h:", var.HasAttribute("h"), "Get h:", var.GetAttribute("h").Get())
ok = Usd.Stage.Open("ok.usda")
print("explicit path type:", ok.GetPrimAtPath("/X").GetTypeName(),
      "radius:", ok.GetPrimAtPath("/X").GetAttribute("radius").Get())
```

**Expected output**
```text
error types:
  Pcp.ErrorType_UnresolvedPrimPath
  Pcp.ErrorType_InvalidAssetPath
BadRef defined/type: True ''
NoDefault/Only: False
selection: tiny
has h: False Get h: None
explicit path type: Sphere radius: 1.0
```

Stderr also warns while the stage opens; the exam-facing API is `GetCompositionErrors()`.

### 9. Real-world use case
A set-dressing USD references `chair.usda` without a prim path. The chair file's `defaultPrim` was removed in a "cleanup." Every chair in the shot becomes an empty Xform. `UnresolvedPrimPath` … `<defaultPrim>` is the signature. Either restore defaultPrim or switch to `@chair.usda@</Chair>`.

### 10. Common mistakes
> [!MISTAKE] Checking only `IsValid()` on the referencing prim. It is valid. Check **type, children, and composition errors**.

> [!MISTAKE] Authoring `variants = { string size = "tiny" }` to "clear" a selection. That *is* a selection; it will not fall back to `small`.

> [!MISTAKE] Treating an unloaded payload as `InvalidAssetPath`. No error; `IsLoaded()` is False.

### 11. Exam traps
> [!TRAP] Missing `defaultPrim` is `InvalidAssetPath`. It is **`UnresolvedPrimPath`** (file opened). Missing *file* is `InvalidAssetPath`.

> [!TRAP] "Empty type name means the prim is invalid." Defined, valid, untyped.

> [!TRAP] Variant fallbacks rescue an authored wrong name. Fallbacks apply only when the selection is **missing**.

### 12. Practice questions
1. File missing. Which `errorType`?
2. File present, no defaultPrim, no prim path in the reference. Which `errorType`?
3. Selection `"tiny"` on a set that has `small`/`big`. Does `h` inside `small` compose?

**Answers**
1. **`Pcp.ErrorType_InvalidAssetPath`.**
2. **`Pcp.ErrorType_UnresolvedPrimPath`.**
3. **No.** The authored selection matches nothing.

### 13. Exam takeaways
> [!KEY]
> - Failed arcs leave an empty but valid prim. Read `GetCompositionErrors()`.
> - Missing file ≠ missing defaultPrim (InvalidAssetPath vs UnresolvedPrimPath).
> - Explicit `@file@</Prim>` bypasses defaultPrim.
> - Wrong authored variant name is not a missing selection; fallbacks will not fire.

---

## 42.5 Asset-path problems

### 1. What is it?
Even when composition succeeds, **asset-valued attributes** (`inputs:file`, `assetInfo`, media) can point at files the resolver cannot find. Obj 6.3: resolve issues related to asset management. The pipeline tools are `UsdUtils.ComputeAllDependencies`, `ExtractExternalReferences`, and anchored `ComputeAbsolutePath` (Chapter 33).

### 2. Why do we need it?
usdview shows a grey PreviewSurface because `wood.png` never resolved; Hydra does not always scream. A packaging job that only copies `.usda` leaves textures behind. Computing dependencies *before* publish is the debug step that belongs in the exporter (Chapter 32).

### 3. Beginner explanation
A recipe says "add the packet marked `@./tex.png@`." Composition found the recipe book. Asset resolution walks to the pantry. `ComputeAllDependencies` is the clipboard of everything the recipe needs; **unresolved** is the list of packets that were not on the shelf.

*Where the analogy breaks:* `Ar.GetResolver().Resolve("./tex.png")` uses the **process current directory**, not the layer that authored the path. The pantry key is the layer's location (`ComputeAbsolutePath` / `CreateIdentifier`), not cwd — except in these scripts, cwd *is* the layer directory, which hides the bug.

### 4. Technical explanation
- `UsdUtils.ComputeAllDependencies(layerPath)` → `(layers, assets, unresolved)` **recursive**. Layers are `Sdf.Layer` handles; assets are resolved file paths; unresolved are identifier strings that failed.
- `UsdUtils.ExtractExternalReferences(layerPath)` → `(sublayers, refs_and_assets, payloads)` for **one file**, no recursion. Useful to see what *this* layer wrote, including a broken `@missing.png@`.
- `Sdf.Layer.ComputeAbsolutePath("./tex.png")` anchors to that layer. Naive `Ar.GetResolver().Resolve("./tex.png")` is cwd (Chapter 33). A path **without** `./` is context-dependent: it may resolve only with a resolver context.
- After composition, `attribute.Get()` on an `asset` input returns `Sdf.AssetPath`. `str(val)` looks like `@./tex.png@`. `val.resolvedPath` is empty when resolution failed.
- Common breaks: wrong relative path (`@textures/wood.png@` vs `@./wood.png@`), published USDA moved without its sidecar files, resolver search path not set, Windows vs POSIX separators, URI the default resolver does not handle.

> [!VERSION] Verified on USD 26.08. `Ar.AnchorRelativePath` is gone; use `CreateIdentifier` + `ComputeAbsolutePath`.

### 5. Mental model

```text
ComputeAllDependencies(root)
   layers      = every USD file pulled in
   assets      = textures / audio / … that resolved
   unresolved  = the bug list  ← start here

ExtractExternalReferences(one layer) = what that file spelled, even if broken
```

### 6. Simple example
`shot.usda` references `look.usda`, which has `asset inputs:file = @./tex.png@` next to a real `tex.png`. Dependencies: layers `look`+`shot`, assets `tex.png`, unresolved empty. `look2.usda` points at `missing.png`: unresolved `['missing.png']`. `Resolve("missing.png")` is False.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Wood"
)

def Material "Wood"
{
    def Shader "Tex"
    {
        uniform token info:id = "UsdUVTexture"
        asset inputs:file = @missing.png@
    }
}
```

- Composition of this Material succeeds. The *texture* does not.
- `@missing.png@` has no `./`; default resolver will not treat it as next-to-the-layer unless a context says so.

### 8. Python example

```python
import os
from pxr import Usd, Sdf, UsdUtils, Ar

open("tex.png", "w").write("x")
open("look.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Wood"
)
def Material "Wood"
{
    def Shader "Tex"
    {
        uniform token info:id = "UsdUVTexture"
        asset inputs:file = @./tex.png@
    }
}
""")
open("look2.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Wood"
)
def Material "Wood"
{
    def Shader "Tex"
    {
        uniform token info:id = "UsdUVTexture"
        asset inputs:file = @missing.png@
    }
}
""")
open("shot.usda", "w").write("""#usda 1.0
def "Looks" (
    prepend references = @./look.usda@
)
{
}
""")

layers, assets, unresolved = UsdUtils.ComputeAllDependencies("shot.usda")
print("layers:", sorted(os.path.basename(l.identifier) for l in layers))
print("assets:", sorted(os.path.basename(a) for a in assets))
print("unresolved:", list(unresolved))
_, _, u2 = UsdUtils.ComputeAllDependencies("look2.usda")
print("look2 unresolved:", list(u2))
print("extract look2:", UsdUtils.ExtractExternalReferences("look2.usda"))
r = Ar.GetResolver()
print("missing.png resolved:", bool(r.Resolve("missing.png")))
print("./tex.png resolved:", bool(r.Resolve("./tex.png")))
layer = Sdf.Layer.FindOrOpen("look.usda")
print("anchor ./tex.png:",
      os.path.basename(layer.ComputeAbsolutePath("./tex.png")))
st = Usd.Stage.Open("shot.usda")
val = st.GetPrimAtPath("/Looks/Tex").GetAttribute("inputs:file").Get()
print("authored file:", val)
print("resolvedPath nonempty:", bool(str(val.resolvedPath)))
```

**Expected output**
```text
layers: ['look.usda', 'shot.usda']
assets: ['tex.png']
unresolved: []
look2 unresolved: ['missing.png']
extract look2: ([], ['missing.png'], [])
missing.png resolved: False
./tex.png resolved: True
anchor ./tex.png: tex.png
authored file: @./tex.png@
resolvedPath nonempty: True
```

`ExtractExternalReferences` lists `missing.png` even though it does not resolve; `ComputeAllDependencies` puts it in **unresolved**.

### 9. Real-world use case
A lookdev package ships `wood.usda` + `wood.png`. Someone copies only the USDA into the shot tree. Storm shows grey. `ComputeAllDependencies` on the published layer lists `wood.png` under unresolved. The fix is packaging (Chapter 31 USDZ / `LocalizeAsset`), not a new shader.

### 10. Common mistakes
> [!MISTAKE] Calling `Resolve("./tex.png")` from a unittest whose cwd is not the layer directory, then "fixing" the USDA. Anchor with `ComputeAbsolutePath` on the layer.

> [!MISTAKE] Treating `ExtractExternalReferences` as recursive. It is one file.

> [!MISTAKE] Checking only composition errors for a missing texture. Textures are not composition arcs.

### 11. Exam traps
> [!TRAP] `ComputeAllDependencies` third tuple element is "all asset paths." It is **unresolved only**. Successful textures are in the second element.

> [!TRAP] `@./x@` and `@x@` always resolve the same. Only `./` (or an absolute path) is clearly file-relative for the default resolver.

> [!TRAP] Empty `resolvedPath` means the attribute is unauthored. It can be authored *and* unresolved.

### 12. Practice questions
1. Which `ComputeAllDependencies` list is the bug list for missing files?
2. Why can `Resolve("./tex.png")` succeed in a lab script and fail in production?
3. Does a missing `inputs:file` create a `GetCompositionErrors()` entry?

**Answers**
1. The **third**: `unresolved`.
2. The lab cwd is the layer folder; production cwd is not. Anchor to the layer.
3. **No.** It is an asset path, not a composition arc.

### 13. Exam takeaways
> [!KEY]
> - Obj 6.3: `ComputeAllDependencies` → `(layers, assets, unresolved)`.
> - `ExtractExternalReferences` is one-file and includes broken paths.
> - Anchor relatives to the **layer**, not cwd (`ComputeAbsolutePath`).
> - Missing textures rarely show up as composition errors.

---

## 42.6 Unexpected visual results

### 1. What is it?
The stage is composed, assets resolve, and the picture is still wrong. Obj 6.4: **unexpected visual results** come from geometry, imaging purpose, units, materials, and lights — not from LIVERPS. You measure them with UsdGeom / UsdShade / UsdLux queries.

### 2. Why do we need it?
A "broken reference" ticket that is actually `subdivisionScheme = catmullClark` on a CAD mesh, or `purpose = proxy` on the set, trains you to pick the wrong API. The exam mixes composition stems with visual stems; this section is the visual half.

### 3. Beginner explanation
You developed the photograph (composition) and the print looks odd. Maybe the paper is the wrong size (units / upAxis), the subject is marked "lobby snapshot only" (purpose), the statue is still in the crate (extent / visibility), the clay was never painted (material bind), or the sculptor left the smoothing on (subdivision).

*Where the analogy breaks:* Hydra may skip drawing without a USD error. `GetCompositionErrors()` can be empty while the mesh is invisible.

### 4. Technical explanation
Checklist (each item is a prior chapter; here you only *query*):

| Symptom | Query | Typical cause |
|---------|-------|----------------|
| Melted / rounded CAD | `UsdGeom.Mesh.GetSubdivisionSchemeAttr().Get()` | Unauthored → fallback **`catmullClark`**. Set `"none"`. Ch 39. |
| Flickers / disappears when framed | `extent` `HasAuthoredValue()` | Missing or stale extent. Ch 13. |
| Missing in beauty, present in preview | `Imageable.ComputePurpose()` | Inherited `proxy` / `guide`. Ch 39.6. |
| Whole group gone | `ComputeVisibility()` | Ancestor `invisible`. Token `"visible"` is invalid; authored values are `inherited` / `invisible`. |
| Grey clay | `HasAPI(MaterialBindingAPI)`, `ComputeBoundMaterial()` | No bind, or PreviewSurface not connected. Ch 40. |
| Wrong scale | `UsdGeom.GetStageMetersPerUnit` | 0.01 vs 1. Ch 28. |
| On its side | `UsdGeom.GetStageUpAxis` | Y vs Z. Ch 28. |
| Wrong color | primvar `displayColor` vs shader `diffuseColor` leftover `.connect` | Ch 40.2 / 40.5. |
| Transform ignored | op not in `xformOpOrder`; instance proxy | Ch 39.1, 24. |
| Dim scene | DistantLight intensity 1 (fallback is 50000) | Ch 41. |

`ComputePurpose()` inherits. A child with no authored purpose under `purpose = "proxy"` computes **proxy** — beauty renderers skip it.

`ComputeVisibility()` on a drawing prim often returns **`inherited`**, which still draws. **`invisible`** means skipped. Do not expect the string `"visible"`.

`usd-core` cannot rasterize; these queries are what you can prove without usdview.

### 5. Mental model

```text
empty GetCompositionErrors()
        │
        ├─ purpose proxy/guide     → not a composition bug
        ├─ visibility invisible    → ancestor or self
        ├─ scheme catmullClark     → CAD looks soft
        ├─ no extent               → culling / selection weirdness
        ├─ no bound material       → grey
        └─ units / upAxis          → size and orientation
```

### 6. Simple example
Y-up studio file referenced into a Z-up shot: upAxis Z, metersPerUnit 1. Mesh `Soft` has no extent, scheme catmullClark, inherits purpose proxy, visibility inherited, no MaterialBindingAPI. Mesh `Hidden` is invisible with an authored extent.

### 7. USDA example

```usda
#usda 1.0
(
    upAxis = "Z"
    metersPerUnit = 1
)

def Xform "Set"
{
    uniform token purpose = "proxy"

    def Mesh "Soft"
    {
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        token visibility = "inherited"
    }

    def Mesh "Hidden"
    {
        token visibility = "invisible"
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        float3[] extent = [(-1, -1, -1), (1, 1, 1)]
    }
}
```

- `Soft` will not appear in a render-purpose viewport: computed purpose is `proxy`.
- Unauthored `subdivisionScheme` is still `catmullClark` when you `Get()`.

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade

open("vis.usda", "w").write("""#usda 1.0
(
    upAxis = "Z"
    metersPerUnit = 1
)

def Xform "Set"
{
    uniform token purpose = "proxy"

    def Mesh "Soft"
    {
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        token visibility = "inherited"
    }

    def Mesh "Hidden"
    {
        token visibility = "invisible"
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        float3[] extent = [(-1, -1, -1), (1, 1, 1)]
    }
}
""")
sv = Usd.Stage.Open("vis.usda")
print("upAxis:", UsdGeom.GetStageUpAxis(sv))
print("metersPerUnit:", UsdGeom.GetStageMetersPerUnit(sv))
soft = UsdGeom.Mesh(sv.GetPrimAtPath("/Set/Soft"))
print("scheme:", soft.GetSubdivisionSchemeAttr().Get())
print("extent authored:", soft.GetExtentAttr().HasAuthoredValue())
print("purpose Set:",
      UsdGeom.Imageable(sv.GetPrimAtPath("/Set")).GetPurposeAttr().Get())
print("ComputePurpose Soft:",
      UsdGeom.Imageable(soft.GetPrim()).ComputePurpose())
print("ComputeVisibility Soft:",
      UsdGeom.Imageable(soft.GetPrim()).ComputeVisibility())
print("ComputeVisibility Hidden:",
      UsdGeom.Imageable(sv.GetPrimAtPath("/Set/Hidden")).ComputeVisibility())
print("HasAPI MaterialBindingAPI:",
      soft.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
print("bound valid:",
      bool(UsdShade.MaterialBindingAPI(soft.GetPrim()).ComputeBoundMaterial()[0]))
```

**Expected output**
```text
upAxis: Z
metersPerUnit: 1.0
scheme: catmullClark
extent authored: False
purpose Set: proxy
ComputePurpose Soft: proxy
ComputeVisibility Soft: inherited
ComputeVisibility Hidden: invisible
HasAPI MaterialBindingAPI: False
bound valid: False
```

Five visual bugs, zero composition errors.

### 9. Real-world use case
A CAD-to-USD exporter (Chapter 29) forgets `subdivisionScheme = none` and `extent`. Storm shows a melted bracket that vanishes when the camera dollies. Composition stacks look perfect. The visual checklist catches both in two `Get()` calls.

### 10. Common mistakes
> [!MISTAKE] Debugging a proxy-purpose asset in a render-purpose viewport. Compute purpose before recomposing.

> [!MISTAKE] Looking for `visibility = "visible"`. The drawing value is **`inherited`**.

> [!MISTAKE] Blaming LIVERPS for DistantLight intensity 1. That is a UsdLux fallback (Chapter 41), not a weaker layer.

### 11. Exam traps
> [!TRAP] Unauthored `subdivisionScheme` means no subdivision. Fallback is **catmullClark**.

> [!TRAP] Imageable `purpose` (`proxy`) vs material `purpose` (`preview`). Different schemas (Ch 39 vs 40).

> [!TRAP] `ComputeBoundMaterial` invalid means the Material prim is missing. It often means **no bind** on this mesh.

### 12. Practice questions
1. Unauthored mesh `subdivisionScheme`. What does `Get()` return?
2. Child under `purpose = "proxy"` with no own purpose. `ComputePurpose()`?
3. `ComputeVisibility()` returns `inherited`. Is the prim hidden?

**Answers**
1. **`catmullClark`.**
2. **`proxy`.**
3. **No** (unless a renderer also skips it for purpose). `invisible` means hidden.

### 13. Exam takeaways
> [!KEY]
> - Obj 6.4: empty composition errors do not mean the picture is right.
> - Query purpose, visibility, scheme, extent, bind, metersPerUnit, upAxis.
> - `inherited` visibility draws; `proxy` purpose often does not (in beauty).
> - CAD + default subdivision is the classic "melted mesh."

---

## 42.7 A systematic debugging procedure

### 1. What is it?
A **fixed order** of questions so you do not skip from "grey mesh" to rewriting the asset. Each step is a section of this chapter. Stop at the first failed check; that is the bug class.

### 2. Why do we need it?
Random `usdcat` and extra `over`s create new bugs. Obj 6.2–6.4 span composition, assets, and imaging. One procedure covers all three without mixing the tools.

### 3. Beginner explanation
A medic does not start with surgery. Airway, breathing, circulation — then the interesting injury. USD debugging is: **can I find the prim, is it live, did arcs work, who won the value, do files exist, why is the picture wrong?**

*Where the analogy breaks:* later steps can still be wrong after an early pass. If you fix a missing payload and the mesh is still melted, continue down the list.

### 4. Technical explanation

**The eight-step order (verified APIs):**

1. **Layer stack and edit target.** `GetLayerStack(includeSessionLayers=True)`, `GetEditTarget()`, `GetMutedLayers()`. Are you looking at / writing the layer you think?
2. **Prim identity.** `GetPrimAtPath` → `IsValid`, `IsActive`, `IsDefined`, `IsLoaded`, `IsInstanceProxy`. `Traverse` vs `TraverseAll`.
3. **Composition errors.** `GetCompositionErrors()`. InvalidAssetPath vs UnresolvedPrimPath vs none.
4. **Arcs.** `PrimCompositionQuery` / `GetDirectReferences`. Variant `GetVariantSelection`. Payload `IsLoaded`.
5. **Opinion winner.** `GetPropertyStack()`, `GetResolveInfo(time)` with the **viewport time**. Check blocks and Default vs samples.
6. **Asset paths.** `ComputeAllDependencies` unresolved list; `resolvedPath` on asset attributes.
7. **Visual queries.** Purpose, visibility, subdivisionScheme, extent, material bind, metersPerUnit, upAxis, light intensity.
8. **Only then** flatten / export a snapshot (`Flatten`, Chapter 34) if you need a single-file repro. Flattening is a diagnostic copy, not a fix.

Write the answers down. The exam loves stems that skip a step (e.g. flatten first, which bakes the wrong winner).

### 5. Mental model

```text
1 stack/target → 2 prim flags → 3 Pcp errors → 4 arcs/variants
       → 5 property stack + time → 6 unresolved assets → 7 visual
              → 8 freeze a flatten only for a bug file
```

Never start at 8. Never skip 2 because `Traverse()` "didn't list it."

### 6. Simple example
Grey proxy set from §42.6. Steps 1–6 pass (no errors, prims valid). Step 7: `ComputePurpose` is `proxy`, no bind, scheme `catmullClark`. Three visual findings, zero composition work.

### 7. USDA example

The same `vis.usda` as §42.6. The procedure does not need a new file format; it needs discipline on that file.

```usda
#usda 1.0
(
    upAxis = "Z"
    metersPerUnit = 1
)

def Xform "Set"
{
    uniform token purpose = "proxy"

    def Mesh "Soft"
    {
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade

open("vis.usda", "w").write("""#usda 1.0
(
    upAxis = "Z"
    metersPerUnit = 1
)

def Xform "Set"
{
    uniform token purpose = "proxy"

    def Mesh "Soft"
    {
        int[] faceVertexCounts = [3]
        int[] faceVertexIndices = [0, 1, 2]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        token visibility = "inherited"
    }
}
""")
sv = Usd.Stage.Open("vis.usda")
prim = sv.GetPrimAtPath("/Set/Soft")
print("1 edit target:", sv.GetEditTarget().GetLayer().GetDisplayName())
print("1 muted:", sv.GetMutedLayers())
print("2 valid/active/defined/loaded:",
      prim.IsValid(), prim.IsActive(), prim.IsDefined(), prim.IsLoaded())
print("3 errors:", len(sv.GetCompositionErrors()))
print("4 variant sets:", prim.GetVariantSets().GetNames())
print("5 has points:", prim.GetAttribute("points").IsValid())
print("6 unresolved skip (no assets in this file)")
img = UsdGeom.Imageable(prim)
mesh = UsdGeom.Mesh(prim)
print("7 purpose:", img.ComputePurpose())
print("7 visibility:", img.ComputeVisibility())
print("7 scheme:", mesh.GetSubdivisionSchemeAttr().Get())
print("7 extent authored:", mesh.GetExtentAttr().HasAuthoredValue())
print("7 bound:",
      bool(UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]))
print("7 upAxis/meters:", UsdGeom.GetStageUpAxis(sv),
      UsdGeom.GetStageMetersPerUnit(sv))
```

**Expected output**
```text
1 edit target: vis.usda
1 muted: []
2 valid/active/defined/loaded: True True True True
3 errors: 0
4 variant sets: []
5 has points: True
6 unresolved skip (no assets in this file)
7 purpose: proxy
7 visibility: inherited
7 scheme: catmullClark
7 extent authored: False
7 bound: False
7 upAxis/meters: Z 1.0
```

Stop at step 7: purpose, subdivision, extent, bind, units. Do not rebuild the mesh.

### 9. Real-world use case
A new hire dumps `FlattenLayerStack` into Slack for every ticket. Half the time the flatten *hides* the weaker asset opinion they were supposed to keep. The eight-step list in the studio wiki (this section) cuts those tickets to a stack dump and a purpose print.

### 10. Common mistakes
> [!MISTAKE] Flattening first. You lose the evidence of *which layer* won.

> [!MISTAKE] Skipping step 2 because the outliner (Traverse) is empty. Payloads, inactives, and proxies live off that list.

> [!MISTAKE] Mixing step 7 into step 5 ("the value is wrong" when the value is fine and purpose is proxy).

### 11. Exam traps
> [!TRAP] Stems that offer "open usdview Composition tab" as the only fix. Know the Python equivalents; usdview is not in `usd-core`.

> [!TRAP] "Add a stronger `over` in the session layer" as a universal repair. That hides the real layer bug and will not survive reopen.

> [!TRAP] One failed check means skip the rest forever. Fix it, then continue if the symptom remains.

### 12. Practice questions
1. What is step 1 of the procedure?
2. Why is flatten last?
3. A prim is missing from `Traverse()` but `GetPrimAtPath` is valid and `IsLoaded` is False. Which step caught it, and what is it?

**Answers**
1. **Layer stack, edit target, mutes.**
2. **It bakes the winner and erases which layer/arc produced it.**
3. **Step 2 — unloaded payload** (or ancestor payload).

### 13. Exam takeaways
> [!KEY]
> - Order: stack → prim flags → Pcp errors → arcs → property stack → assets → visual → flatten last.
> - First failed check names the bug class (6.2 vs 6.3 vs 6.4).
> - Python stand-ins exist for every usdview tab you will see named on the exam.
> - Extra overs are not a debugging strategy.

---

## Chapter lab(s)

**Lab 21 — Composition introspection toolkit** (★★☆, Obj 1.8, 6.2; Ch 22 and 42). You plant a wrong-winner, a missing reference, and a muted sublayer, then recover each with `GetLayerStack`, `GetPropertyStack`, and `GetCompositionErrors`.

Chapter 33's Lab 29 (asset-path validation) covers §42.5. Lab 36 (Ch 43) adds TfDebug / Trace once the *scene* bug is understood.

## USDA reading exercise(s)

**Exercise 42-A.** `radius` on `/World/Ball` is 4 in a debug `Get()`, but the artist edited `anim.usda` to 7. Why?

```usda
#usda 1.0
(
    subLayers = [
        @./anim.usda@
    ]
)

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 4
    }
}
```

**Exercise 42-B.** `/World/Set` is an empty Xform. `set.usda` on disk contains `def Xform "Set" { def Mesh "Wall" {} }` and has no `defaultPrim`. What error type, and how do you fix it without renaming prims?

```usda
#usda 1.0

def "World"
{
    def "Set" (
        prepend references = @./set.usda@
    )
    {
    }
}
```

**Exercise 42-C.** Beauty render is empty; Storm's "proxy" purpose view shows the set. Composition errors: none. Name the most likely authored opinion.

```usda
#usda 1.0

def Xform "World"
{
    uniform token purpose = "proxy"

    def Mesh "Hall"
    {
        int[] faceVertexCounts = [4]
        int[] faceVertexIndices = [0, 1, 2, 3]
        point3f[] points = [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]
    }
}
```

## Chapter review

### Summary
- Inspect session > root > sublayers; mute to test; watch the edit target.
- Missing prim = invalid / inactive / undefined / unloaded / proxy — five tests.
- `GetPropertyStack()[0]` is Obj 6.2. Blocks and Default-vs-samples fool `Get()`.
- `InvalidAssetPath` vs `UnresolvedPrimPath`; wrong variant names are not fallbacks.
- `ComputeAllDependencies` unresolved list is Obj 6.3.
- Visual bugs (Obj 6.4) are purpose, visibility, scheme, extent, bind, units, lights.
- Procedure order beats random overs; flatten last.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Value changes after mute | That layer was the winner |
| Session display name `*-session.usda` | Edit target / unsaved debug edit |
| `LoadNone` but references still there | Payloads are the ones unloaded |
| Child of `active = false` | Invalid, not inactive |
| `SpecifierOver`, `IsDefined` False | Typo `over`, no `def` |
| Stack[0] not your layer | Strength (root vs sublayer vs arc) |
| `Get()` ≠ viewport | Pass the numeric time; samples vs Default |
| `radius = None` | Value block |
| `InvalidAssetPath` | Missing file |
| `UnresolvedPrimPath` / `<defaultPrim>` | Add defaultPrim or `</Prim>` |
| Variant selection `tiny` | Authored wrong name; no fallback |
| `unresolved: ['wood.png']` | Asset path, not a composition error |
| Empty beauty, proxy view OK | `ComputePurpose` → proxy |
| Melted CAD | `subdivisionScheme` fallback catmullClark |

### Review questions

**Q42.1** · Obj 6.2 · Easy · Single choice
Among sublayers `@./b.usda@, @./a.usda@`, who wins?
A. `a` · B. `b` · C. Neither; the root must author the value · D. The session layer always

**Q42.2** · Obj 6.2 · Easy · Single choice
`GetLayerStack(includeSessionLayers=True)` lists the session layer:
A. Last (weakest) · B. First (strongest) · C. Not at all · D. Only if saved to disk

**Q42.3** · Obj 6.2 · Medium · Single choice
`Usd.Stage.Open(path, Usd.Stage.LoadNone)` loads:
A. Nothing · B. References only, not payloads · C. Payloads only · D. Only the root layer's defs

**Q42.4** · Obj 6.2 · Medium · Select two.
An inactive prim `/A` with child `/A/B`:
A. `/A.IsValid()` True · B. `/A/B.IsValid()` True · C. `/A/B.IsValid()` False · D. `Traverse()` yields `/A/B`

**Q42.5** · Obj 6.2 · Medium · Single choice
Property stack: shot 1, light 2, asset 0.5. Composed height?
A. 0.5 · B. 2 · C. 1 · D. Average

**Q42.6** · Obj 6.2 · Medium · Single choice
`GetResolveInfo().ValueIsBlocked()` True. `Get()` returns:
A. Schema fallback · B. Next stack spec's value · C. `None` · D. 0

**Q42.7** · Obj 6.2 · Medium · Single choice
Missing referenced file. `errorType` is:
A. `UnresolvedPrimPath` · B. `InvalidAssetPath` · C. `ArcCycle` · D. None; the prim is invalid

**Q42.8** · Obj 6.2 · Medium · Single choice
Referenced file opens, no `defaultPrim`, no prim path in the arc. `errorType` is:
A. `InvalidAssetPath` · B. `UnresolvedPrimPath` · C. None · D. `LayerOffset`

**Q42.9** · Obj 6.3 · Easy · Single choice
`ComputeAllDependencies` returns `(layers, assets, unresolved)`. Missing textures appear in:
A. `layers` · B. `assets` · C. `unresolved` · D. `GetCompositionErrors()`

**Q42.10** · Obj 6.4 · Easy · Single choice
Unauthored `subdivisionScheme` `Get()` is:
A. `none` · B. `catmullClark` · C. `loop` · D. `None`

**Q42.11** · Obj 6.4 · Medium · Select two.
Beauty render empty, proxy view full, no Pcp errors. Likely queries:
A. `ComputePurpose()` · B. `GetCompositionErrors()` will be nonempty · C. Inherited `purpose = proxy` · D. `MuteLayer` of the root

**Q42.12** · Obj 6.4 · Easy · Single choice
`ComputeVisibility()` on a drawing mesh usually prints:
A. `visible` · B. `inherited` · C. `draw` · D. `True`

**Q42.13** · Obj 6.2 · Medium · Single choice
Where should flatten sit in the debugging procedure?
A. Step 1, to simplify · B. After muting every layer · C. Last, as a repro snapshot · D. Never; it is illegal

### Answers

**Q42.1 — B.** First-listed sublayer is stronger. Review: §42.1.

**Q42.2 — B.** Session is strongest. Review: §42.1.

**Q42.3 — B.** References still load. Review: §42.2.

**Q42.4 — A, C.** Parent valid+inactive; child not composed. Review: §42.2.

**Q42.5 — C.** First spec wins. Review: §42.3.

**Q42.6 — C.** A block contributes `None`. Review: §42.3.

**Q42.7 — B.** File cannot open. The referencing prim is still defined. Review: §42.4.

**Q42.8 — B.** `<defaultPrim>` in the message. Review: §42.4.

**Q42.9 — C.** Successful files are `assets`; failures are `unresolved`. Review: §42.5.

**Q42.10 — B.** Review: §42.6 / Ch 39.

**Q42.11 — A, C.** Composition is fine; imaging purpose is not. Review: §42.6.

**Q42.12 — B.** `"visible"` is not the authored token. Review: §42.6.

**Q42.13 — C.** Flatten last so you do not erase the stack evidence. Review: §42.7.

### USDA exercise answers

**42-A — The root layer's local `radius = 4` is stronger than the `anim.usda` sublayer.** First-listed sublayer still loses to the root. Move the 4 into anim, remove it from the root, or reorder so a *stronger* layer than the root holds the 7 (session / a new stronger sublayer above the root — which is impossible for a sublayer; the 4 must leave the root).

**42-B — `Pcp.ErrorType_UnresolvedPrimPath`.** Fix: `( defaultPrim = "Set" )` on `set.usda`, or `prepend references = @./set.usda@</Set>`.

**42-C — `uniform token purpose = "proxy"` on `/World`, inherited by `Hall`.** `ComputePurpose()` is `proxy`. Beauty skips it; a proxy-purpose view draws it. Not a missing reference.

## Further reading

- [S06] OpenUSD API — UsdStage GetLayerStack, GetCompositionErrors, UsdPrim GetPrimStack, UsdAttribute GetPropertyStack / GetResolveInfo, UsdPrimCompositionQuery: https://openusd.org/release/api/index.html
- [S06] UsdUtils ComputeAllDependencies, ExtractExternalReferences: https://openusd.org/release/api/usd_utils_page_front.html
- [S14] NVIDIA Learn OpenUSD — composition debugging: https://docs.nvidia.com/learn-openusd/latest/index.html
- Chapter 22.5–22.6 (API tables and the ten-point opinion checklist), Chapter 33 (resolver anchoring), Chapter 39–41 (visual queries)
