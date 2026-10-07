# Chapter 3 — Layers

> **Exam domain:** Composition (23%) · **Objectives:** 1.3 (sublayers vs references vs payloads), 1.5 (multi-user layering)
> **Study day:** 1 · **Est. time:** 90 min
> **Prerequisites:** Chapter 2

## Learning goals

- Explain what a **layer** is (`Sdf.Layer`) and how it differs from a stage.
- Identify the **root layer** and the **session layer**.
- Author **sublayers** and predict which opinion wins in a layer stack.
- Use an **anonymous layer** for scratch work.
- State the first rule of strength: in one layer stack, **stronger layers win**.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Layer | One document of scene description (`Sdf.Layer`) |
| Opinion | An authored value (or other authored decision) in a layer |
| Root layer | The layer the stage was opened from |
| Session layer | Strongest anonymous scratch layer on the stage |
| Sublayer | A layer included by another layer's `subLayers` list |
| Layer stack | The ordered list of layers that contribute locally (session + root + sublayers) |
| Anonymous layer | A layer with no file on disk (`anonymous = True`) |

---

## 3.1 What a layer is

### 1. What is it?

A **layer** is one document of USD scene description. On disk it is often a `.usda` / `.usdc` / `.usd` file. In code it is an `Sdf.Layer`.

### 2. Why do we need it?

You cannot collaborate if everyone writes into one giant file. Layers let departments, tools, and versions each own a document. Composition combines them.

### 3. Beginner explanation

A layer is one transparent sheet. You can draw a whole picture on it, or only a red circle in the corner.

Where the analogy breaks: a layer can also *point at* other sheets (sublayers, references, payloads). Those pointers are themselves opinions.

### 4. Technical explanation

- Create with `Sdf.Layer.CreateNew(path)`, `Sdf.Layer.FindOrOpen(path)`, `Sdf.Layer.CreateAnonymous(".usda")`.
- `layer.ExportToString()` / `Export(path)` / `ImportFromString(text)`.
- `layer.anonymous` is True for in-memory layers.
- The **identifier** is how USD names the layer (usually a path, or `anon:0x…:tmp.usda`).
- You usually author through `Usd` on a stage (which writes into some layer). You use `Sdf` when you care about the document itself.

### 5. Mental model

Layer = file-like document of opinions. Stage = projector that stacks documents.

### 6. Simple example

`chair_geo.usda` contains the mesh. `chair_look.usda` contains only material bindings. Both are layers. Neither is "the stage" until something opens them.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair"
{
    def Mesh "Geo"
    {
    }
}
```

This entire file is **one layer**.

### 8. Python example

```python
from pxr import Sdf

layer = Sdf.Layer.CreateAnonymous(".usda")
print("anonymous:", layer.anonymous)
print("format:", layer.GetFileFormat().formatId)
ok = layer.ImportFromString(
    '#usda 1.0\n'
    'def Xform "Chair" {\n'
    '}\n'
)
print("imported:", ok)
print("prim at /Chair:", bool(layer.GetPrimAtPath("/Chair")))
print(layer.ExportToString())
```

**Expected output**

```text
anonymous: True
format: usda
imported: True
prim at /Chair: True
#usda 1.0

def Xform "Chair"
{
}

```

### 9. Real-world use case

A lighting TD's working file is a small layer that sublayers or overrides the shot. The lighting file is what they check into version control that day — not a copy of the whole show.

### 10. Common mistakes

> [!MISTAKE] Opening a layer with `Sdf.Layer.FindOrOpen` and expecting composed references to be resolved. `Sdf` sees **this file**. Composition happens on a `Usd.Stage`.

### 11. Exam traps

> [!TRAP] Using "layer" and "prim" as synonyms. A layer contains many prim *specs*. A prim on the stage may be assembled from many layers.

### 12. Practice questions

**FUN-013** · Difficulty: Easy · Type: Single choice

`Sdf.Layer` represents:

A. A renderer  
B. One document of authored scene description  
C. The composed stage  
D. A Hydra delegate  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Layer = document (`Sdf`). Stage = composed view (`Usd`).
> - Anonymous layers have no file until you export them.

---

## 3.2 The root layer

### 1. What is it?

The **root layer** is the layer you passed to `Open` / `CreateNew` / `CreateInMemory`. `stage.GetRootLayer()` returns it.

### 2. Why do we need it?

Every composition has to start somewhere. The root layer is that starting document. Its `subLayers` list, its references, and its metadata (`defaultPrim`, units) set the stage's context.

### 3. Beginner explanation

If the stage is a book you are reading, the root layer is the book you pulled off the shelf. It may tell you to also read other chapters (sublayers) or other books (references).

### 4. Technical explanation

- Edits go to the **edit target**, which defaults to the root layer (Ch 15).
- `GetLayerStack(includeSessionLayers=False)` starts with the root, then sublayers.
- Flattening (`Usd.Stage.Flatten`, Ch 34) bakes the composed scene into a new root.

### 5. Mental model

Root layer = the handle of the stage.

### 6. Simple example

`usdview shot.usda` → root layer is `shot.usda`.

### 7. USDA example

A root layer that only lists sublayers (no prims of its own):

```usda
#usda 1.0
(
    defaultPrim = "World"
    subLayers = [
        @./anim.usda@,
        @./layout.usda@
    ]
)
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory("myroot.usda")
UsdGeom.Xform.Define(stage, "/World")
root = stage.GetRootLayer()
print("root anonymous:", root.anonymous)
print("root is edit target:", stage.GetEditTarget().GetLayer() == root)
print("prims authored on root:", list(root.rootPrims.keys()))
```

**Expected output**

```text
root anonymous: True
root is edit target: True
prims authored on root: ['World']
```

### 9. Real-world use case

A shot's root layer may be almost empty except `subLayers` and a few overrides. That is a feature: the root is the "assembly sheet" for the shot.

### 10. Common mistakes

> [!MISTAKE] Assuming the root layer contains every prim you see on the stage. References bring prims from elsewhere (Ch 16).

### 11. Exam traps

> [!TRAP] "The root layer is always the strongest layer." The **session** layer is stronger than the root.

### 12. Practice questions

**COMP-PRE-001** · Difficulty: Easy · Type: Single choice

Which layer is stronger than the root layer on a newly opened stage?

A. The weakest sublayer  
B. The session layer  
C. Nothing; root always wins  
D. The payload layer  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Root layer = the file you opened.
> - Session is stronger than root.
> - Default edit target is the root layer.

---

## 3.3 The session layer

### 1. What is it?

The **session layer** is an anonymous layer USD creates on every stage. It is the **strongest** layer in the local layer stack. `stage.GetSessionLayer()` returns it.

### 2. Why do we need it?

Viewers and tools need a place to put temporary overrides (hide this prim, mute that layer, try a variant) without dirtying the artist's file.

### 3. Beginner explanation

Session layer = sticky notes on the projector glass. They sit on top of every sheet. Throw them away when you leave the room.

Where the analogy breaks: you *can* export the session layer if you want to keep the notes. USD will not do that for you on `stage.Save()`.

### 4. Technical explanation

- Always anonymous.
- First in `GetLayerStack()` (default `includeSessionLayers=True`).
- Author into it with `Usd.EditContext(stage, stage.GetSessionLayer())` (Ch 15).
- `Save()` does not write it to the root file.

### 5. Mental model

```text
[session]   strongest, scratch
[root]
[sublayers]
```

### 6. Simple example

usdview's display purposes and "hide" often live as session opinions so closing the viewer leaves the file clean.

### 7. USDA example

A session opinion looks like any other overlay. USD stores it in memory, not in your shot file:

```usda
#usda 1.0

over "World"
{
    over "Ball"
    {
        double radius = 99
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.GetRadiusAttr().Set(1.0)

with Usd.EditContext(stage, stage.GetSessionLayer()):
    ball.GetRadiusAttr().Set(99.0)

print("composed radius:", ball.GetRadiusAttr().Get())
print("root USDA:")
print(stage.GetRootLayer().ExportToString())
print("session USDA:")
print(stage.GetSessionLayer().ExportToString())
```

**Expected output**

```text
composed radius: 99.0
root USDA:
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 1
    }
}


session USDA:
#usda 1.0

over "World"
{
    over "Ball"
    {
        double radius = 99
    }
}

```

### 9. Real-world use case

A debug tool solo's one character by deactivating everyone else on the session layer. The shot file is unchanged.

### 10. Common mistakes

> [!MISTAKE] Authoring "just to try it" without an EditContext, then saving — you just wrote the experiment into the root layer.

### 11. Exam traps

> [!TRAP] "Session layer is weaker because it is temporary." Temporary ≠ weak. It is the strongest local layer.

### 12. Practice questions

**COMP-PRE-002** · Difficulty: Medium · Type: Single choice

You set radius=99 on the session layer and radius=1 on the root. What does `Get()` return?

A. 1  
B. 99  
C. Average of 1 and 99  
D. An error  

**Answer:** B. Stronger session wins.

### 13. Exam takeaways

> [!KEY]
> - Session layer: strongest, anonymous, not saved with the root.
> - Use it for temporary overrides.

---

## 3.4 Sublayers and the layer stack

### 1. What is it?

A **sublayer** is a layer listed in another layer's `subLayers` metadata. Together, the session layer, the root, and those sublayers form the **local layer stack**.

### 2. Why do we need it?

Obj 1.3 and 1.5: sublayers are how one *workstream* (layout, anim, lighting) owns a file **in the same namespace** as the shot. Many users edit the same `/World/Hero` without copying the prim.

### 3. Beginner explanation

Sublayers are extra transparent sheets **in the same pile** as the root. They describe the **same prim paths**.

Where the analogy breaks: **references** (Ch 16) bring in another pile *under a prim*. Sublayers *are* this pile. That distinction is an exam favourite.

### 4. Technical explanation

- USDA: `subLayers = [ @strong.usda@, @weak.usda@ ]`
- **List order: stronger first.** The first sublayer is stronger than the second.
- The root is stronger than all of its sublayers.
- The session layer is stronger than the root.
- Full local order: **session → root → sublayer[0] → sublayer[1] → …**
- Sublayers compose in the **same namespace** (no path prefix).
- Layer offsets on sublayers shift time (Ch 10, 15).

Verified on USD 26.08: with `subLayers = [strong.usda, weak.usda]`, a radius of 5 in strong and 1 in weak composes to **5**.

### 5. Mental model

```text
session          (strongest)
root.usda        subLayers = [ @strong@, @weak@ ]
  strong.usda
  weak.usda      (weakest)
```

### 6. Simple example

Shot root lists `lgt.usda` then `anim.usda` then `layout.usda`. Lighting can override the hero's visibility without editing animation's file.

### 7. USDA example

*File: weak.usda*

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

*File: strong.usda*

```usda
#usda 1.0

over "World"
{
    over "Ball"
    {
        double radius = 5
    }
}
```

*File: root.usda*

```usda
#usda 1.0
(
    subLayers = [
        @strong.usda@,
        @weak.usda@
    ]
)
```

Composed radius of `/World/Ball` is 5.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom

weak = Sdf.Layer.CreateAnonymous("weak.usda")
strong = Sdf.Layer.CreateAnonymous("strong.usda")
root = Sdf.Layer.CreateAnonymous("root.usda")
weak.ImportFromString(
    '#usda 1.0\n'
    'def Xform "World" {\n'
    '    def Sphere "Ball" {\n'
    '        double radius = 1\n'
    '    }\n'
    '}\n'
)
strong.ImportFromString(
    '#usda 1.0\n'
    'over "World" {\n'
    '    over "Ball" {\n'
    '        double radius = 5\n'
    '    }\n'
    '}\n'
)
root.subLayerPaths = [strong.identifier, weak.identifier]
stage = Usd.Stage.Open(root)
radius = UsdGeom.Sphere(stage.GetPrimAtPath("/World/Ball")).GetRadiusAttr().Get()
print("composed radius:", radius)
print("stack (no session):")
for layer in stage.GetLayerStack(includeSessionLayers=False):
    print(" ", layer.identifier.split(":")[-1])
```

**Expected output**

```text
composed radius: 5.0
stack (no session):
  root.usda
  strong.usda
  weak.usda
```

### 9. Real-world use case

Multi-user shots: each department gets a sublayer in a known order. This is Obj 1.5. References are the wrong tool when everyone needs to edit the *same* `/World/Hero` path.

### 10. Common mistakes

> [!MISTAKE] Writing `subLayers = [@weak@, @strong@]` and expecting the last file to win. **First listed sublayer is stronger.**

> [!MISTAKE] Using a sublayer when you meant a reference: sublayers do not remap namespace and do not create a reusable asset boundary.

### 11. Exam traps

> [!TRAP] "Sublayers, references, and payloads are three names for the same arc." They are not. Compare table in the takeaways; full treatment in Ch 16–17.

> [!TRAP] Reading USDA `subLayers` bottom-up like some DCC GUIs. In the **file**, first = stronger.

### 12. Practice questions

**COMP-PRE-003** · Difficulty: Medium · Type: Single choice

Root has `subLayers = [@A.usda@, @B.usda@]`. A says radius=2, B says radius=8. No root opinion. Composed radius?

A. 2  
B. 8  
C. 10  
D. Undefined  

**COMP-PRE-004** · Difficulty: Medium · Type: Single choice

When should you pick a **sublayer** instead of a **reference**?

A. You want to reuse a chair as `/Set/Chair_01` and `/Set/Chair_02`  
B. You want layout and animation to edit the same `/World/Hero` in one shot  
C. You want to skip loading heavy geometry until needed  
D. You want a zip package of textures  

**Answers**

**COMP-PRE-003 — Answer: A.** A is listed first, so A is stronger.

**COMP-PRE-004 — Answer: B.** A is references. C is payloads. D is USDZ.

### 13. Exam takeaways

> [!KEY]
> - Sublayer order in the file: **first = stronger**.
> - Local stack: session → root → sublayers.
> - Sublayers share namespace; references (Ch 16) nest an asset under a prim; payloads (Ch 17) are unloadable references.

---

## 3.5 Anonymous layers

### 1. What is it?

An **anonymous layer** exists only in memory. `layer.anonymous` is True. Identifiers look like `anon:0x…:name.usda`.

### 2. Why do we need it?

Tests, session layers, procedural content, and "try this override" all need documents that are not files yet.

### 3. Beginner explanation

A scratch page. If you never export it, it disappears with the process.

### 4. Technical explanation

- `Sdf.Layer.CreateAnonymous(".usda")` or `CreateAnonymous("hint.usda")`.
- `Usd.Stage.CreateInMemory()` makes anonymous root + session.
- You may still `Export("disk.usda")` to materialize it.
- Anonymous layers can be sublayers of each other (as in §3.4's Python).

### 5. Mental model

Anonymous = no path on disk. Still a real layer.

### 6. Simple example

This book's tests use anonymous layers so they do not clutter your project folder.

### 7. USDA example

There is no "anonymous" keyword in USDA. Anonymity is a runtime property. The contents still look like any layer:

```usda
#usda 1.0
def Sphere "Scratch" {}
```

### 8. Python example

```python
from pxr import Sdf

layer = Sdf.Layer.CreateAnonymous("scratch.usda")
print("anonymous:", layer.anonymous)
print("identifier contains 'anon:':", layer.identifier.startswith("anon:"))
print("identifier ends with:", layer.identifier.split(":")[-1])
```

**Expected output**

```text
anonymous: True
identifier contains 'anon:': True
identifier ends with: scratch.usda
```

### 9. Real-world use case

A DCC exporter builds an anonymous layer, validates it, then exports to the publish path only if checks pass.

### 10. Common mistakes

> [!MISTAKE] Calling `Save()` on a stage whose root is anonymous and expecting a file. Export it, or CreateNew with a path.

### 11. Exam traps

> [!TRAP] "Anonymous layers cannot contribute opinions." They can. Session layers do it all day.

### 12. Practice questions

**FUN-014** · Difficulty: Easy · Type: Single choice

The session layer is:

A. Always a file named `session.usda`  
B. Anonymous and strongest locally  
C. Weaker than all sublayers  
D. Only used in usdview  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Anonymous layers are real layers without a disk path.
> - Session layers are anonymous.

---

## 3.6 Opinions and "strongest wins" (first look)

### 1. What is it?

An **opinion** is an authored decision in a layer: a value, a specifier, a metadata field, a list of references. When two opinions disagree, **the stronger one wins**. In one layer stack, strength is stack order.

### 2. Why do we need it?

This is the seed of LIVERPS (Ch 21). If you only remember one composition sentence for Day 1, remember: **stronger opinions win; weaker ones remain as backups.**

### 3. Beginner explanation

Two sticky notes on the same recipe step: the one on top is what the kitchen does. The lower note is still there if you peel the top one off (unmute, delete the override).

Where the analogy breaks: "stronger" is not "later in time". A weaker file can be newer on disk and still lose.

### 4. Technical explanation

- For a scalar attribute in the **same** layer stack, the strongest authored value is the composed value.
- A layer with **no opinion** on that attribute does not block weaker opinions.
- `over` vs `def` is about *defining namespace*, not about value strength (Ch 4, Ch 20). An `over` in a stronger layer still wins the value.
- Across composition **arcs** (references, inherits, …) strength follows LIVERPS, not only layer-stack order. That is Part III.

### 5. Mental model

Ask the stack from the top: "Do you have a value for `radius`?" The first yes wins.

### 6. Simple example

Root has no radius. Strong sublayer says 5. Weak sublayer says 1. Result: 5. If you delete the 5, result becomes 1 — the weak opinion was waiting.

### 7. USDA example

See §3.4. The `over` in `strong.usda` wins over the `def` in `weak.usda` because of **stack position**, not because `over` is magically stronger than `def`.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom

weak = Sdf.Layer.CreateAnonymous("weak.usda")
root = Sdf.Layer.CreateAnonymous("root.usda")
weak.ImportFromString(
    '#usda 1.0\n'
    'def Sphere "Ball" {\n'
    '    double radius = 1\n'
    '}\n'
)
root.subLayerPaths = [weak.identifier]
stage = Usd.Stage.Open(root)
ball = UsdGeom.Sphere(stage.GetPrimAtPath("/Ball"))
print("from weak only:", ball.GetRadiusAttr().Get())
with Usd.EditContext(stage, stage.GetSessionLayer()):
    ball.GetRadiusAttr().Set(7)
print("after session override:", ball.GetRadiusAttr().Get())
```

**Expected output**

```text
from weak only: 1.0
after session override: 7.0
```

### 9. Real-world use case

Animation publishes translation. Layout had placed the character. Animation's sublayer is stronger, so the animated translation wins. Layout's value is still in `layout.usda` if animation's curve is deleted.

### 10. Common mistakes

> [!MISTAKE] Believing "the file I saved last wins". Strength is stack order, not mtime.

> [!MISTAKE] Believing `def` beats `over` for values. Specifiers are not value strength.

### 11. Exam traps

> [!TRAP] Combining two numbers (1 and 5 become 6). USD does not add opinions. One wins.

> [!TRAP] Forgetting the session layer when predicting a usdview override.

### 12. Practice questions

**COMP-PRE-005** · Difficulty: Easy · Type: Single choice

Two opinions for the same attribute in one layer stack. The composed value is:

A. The sum  
B. The weaker value  
C. The stronger authored value  
D. Always the root layer's value, even if it has no opinion  

**Answer:** C. D is wrong because "no opinion" does not block weaker values.

### 13. Exam takeaways

> [!KEY]
> - Strongest authored opinion wins. Weaker opinions remain underneath.
> - Stack order ≠ file modification time.
> - Specifier (`def`/`over`) ≠ value strength.
> - LIVERPS generalizes this idea across arcs (Ch 21).

---

## Chapter lab(s)

Labs 04–05 (root/session; sublayer stack) belong here. Run this chapter's scripts until those lab files exist.

## USDA reading exercises

**USDA-03.** Root `subLayers = [@A@, @B@]`. A has no radius. B has `radius = 3`. Composed radius?  
**Answer:** 3. No opinion in A lets B show through.

**USDA-04.** Same stack, plus session `radius = 9`. Composed radius?  
**Answer:** 9.

## Chapter review

### Summary

- Layers are documents; stages compose them.
- Session > root > sublayers (first listed sublayer stronger than the next).
- Sublayers share namespace — that is why they are the multi-user shot pattern.
- Strongest opinion wins; absence is not a blocker.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| subLayers list | First = stronger; same namespace |
| Reference vs sublayer | Reuse under a prim vs collaborate on the same paths |
| usdview hide that didn't save | Session layer |
| Two numbers combined | They don't; one wins |

### Chapter questions

**Q1.** Python type for a layer?  
**Q2.** Full local strength order?  
**Q3.** Does `Save()` write the session layer into the root file?  
**Q4.** Sublayer vs reference in one sentence.  
**Q5.** `subLayers = [@A@, @B@]`; who wins?  
**Q6.** What is an opinion?  
**Q7.** Does a stronger layer with *no* radius block a weaker radius?  
**Q8.** Why are sublayers the usual multi-user shot design (Obj 1.5)?

**Answers**

1. `Sdf.Layer`.  
2. Session, root, then sublayers in list order.  
3. No.  
4. Sublayer: same namespace, same stack. Reference: nest an asset under a prim (Ch 16).  
5. A.  
6. An authored decision in a layer.  
7. No.  
8. Departments edit the same prim paths in separate files without copying the scene.

## Further reading

- Glossary: Layer, Layer Stack, Sublayer, Opinion — https://openusd.org/release/glossary.html  
- FAQ: Sublayers vs references — https://openusd.org/release/usdfaq.html  
