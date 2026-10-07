# Chapter 19 — Inherits, Classes, and Specializes

> **Exam domain:** Composition (23%) · **Objectives:** 1.1, 1.6 · **Study day:** 6 · **Est. time:** 90 min
> **Prerequisites:** Ch 4 (specifiers `def`, `over`, `class`), Ch 14 (strength, LIVERPS first look), Ch 15 (layer stacks), Ch 16 (references), Ch 18 (variants)

## Learning goals

- Explain what a `class` prim is and why it is abstract.
- Author inherits arcs and use a class to broadcast one edit to many prims.
- Explain specializes as the weakest arc and predict when its opinions win or lose.
- Choose between inherits and specializes with a decision table (Obj 1.1).
- Predict how a class override in a shot reaches every referenced copy of an asset (implied inherits).
- Place inherits (**I**) and specializes (**S**) correctly in LIVERPS (Obj 1.6).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **`class` prim** | A prim with the `class` specifier. It is abstract: it holds opinions but is not traversed or rendered by default. |
| **Abstract prim** | A prim that is a `class` or is under one. `prim.IsAbstract()` returns `True`. |
| **Inherits arc** | A composition arc that makes a prim pick up all opinions from another prim path in the same layer stack. The **I** in LIVERPS. |
| **Broadcast edit** | One edit on a class that changes every prim inheriting from it. |
| **Specializes arc** | Like inherits, but its opinions are the weakest of all arcs. The **S** in LIVERPS. |
| **Base / source prim** | The prim an inherits or specializes arc points to. |
| **Implied inherits** | When an asset with an inherits arc is referenced, the class path is also looked up in the referencing layer stack, so the shot can override the class. |
| **Direct (local) opinion** | An opinion authored on the prim itself in a layer stack, not through any arc. |

---

## 19.1 `class` prims

### 1. What is it?

A **`class` prim** is a prim written with the `class` specifier instead of `def` or `over`. It is a container of shared opinions that other prims point to. USD treats it as **abstract**: it exists on the stage, but default traversal and renderers skip it.

### 2. Why do we need it?

You want one place to store settings shared by many prims, for example "all street lamps are 60 W". If that place were a normal `def` prim, it would also appear in the scene as an extra lamp. A `class` prim holds the settings without becoming visible content.

### 3. Beginner explanation

A class is like a style sheet in a word processor: the "Heading" style is not a heading on any page, but every heading follows it.

Where the analogy breaks: a style sheet only formats text, while a class can also contain child prims, relationships, variant sets, and even a prim type.

### 4. Technical explanation

- Specifier `Sdf.SpecifierClass`. Create it with `stage.CreateClassPrim(path)` in Python or `class "Name"` in USDA.
- A class prim **is defined** (`IsDefined()` is `True`) and **is abstract** (`IsAbstract()` is `True`). Its descendants are abstract too.
- `stage.Traverse()` uses the default predicate, which excludes abstract prims. `stage.TraverseAll()` includes them. The predicate term is `Usd.PrimIsAbstract`.
- A class can have a type, for example `class Xform "_class_Lamp"`. A typeless prim that inherits from it then composes the type `Xform` (verified on 26.08).
- Naming convention: prefix class names with `_class_` (for example `_class_Tree`) and place them at the root of the layer. This is a convention, not a rule.
- Any prim can be the target of an inherits arc, even a `def`. Using `class` just keeps the source out of the rendered scene.

### 5. Mental model

```text
  Stage
  +-- class "_class_Lamp"     abstract: skipped by Traverse(), not rendered
  |     +-- Bulb              abstract too (child of a class)
  +-- def "LampA"  --inherits-->  /_class_Lamp
  +-- def "LampB"  --inherits-->  /_class_Lamp
```

### 6. Simple example

| Prim | Specifier | `IsAbstract()` | In `Traverse()`? |
|------|-----------|----------------|------------------|
| `/_class_Lamp` | `class` | `True` | No |
| `/_class_Lamp/Bulb` | `def` | `True` | No |
| `/LampA` | `def` | `False` | Yes |

### 7. USDA example

```usda
#usda 1.0

class Xform "_class_Lamp"
{
    int watts = 60

    def Sphere "Bulb"
    {
    }
}

def "LampA" (
    prepend inherits = </_class_Lamp>
)
{
}
```

Line by line:
- `class Xform "_class_Lamp"` — a typed class prim holding shared opinions.
- `def Sphere "Bulb"` inside the class — every inheriting prim gets a `Bulb` child.
- `prepend inherits = </_class_Lamp>` — the inherits arc. The target is a **prim path** in angle brackets, not a file path.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_class_Lamp")
UsdGeom.Sphere.Define(stage, "/_class_Lamp/Bulb")

lamp = stage.DefinePrim("/LampA")
lamp.GetInherits().AddInherit("/_class_Lamp")

print("specifier:", cls.GetSpecifier())
print("abstract:", cls.IsAbstract(), "defined:", cls.IsDefined())
print("child abstract:", stage.GetPrimAtPath("/_class_Lamp/Bulb").IsAbstract())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
print("TraverseAll:", [str(p.GetPath()) for p in stage.TraverseAll()])
print("LampA/Bulb type:", stage.GetPrimAtPath("/LampA/Bulb").GetTypeName())
```

**Expected output**

```text
specifier: Sdf.SpecifierClass
abstract: True defined: True
child abstract: True
Traverse: ['/LampA', '/LampA/Bulb']
TraverseAll: ['/_class_Lamp', '/_class_Lamp/Bulb', '/LampA', '/LampA/Bulb']
LampA/Bulb type: Sphere
```

### 9. Real-world use case

A film studio's set-dressing layer defines `class "_class_StreetLamp"`. Hundreds of lamps on a street inherit it. The class never renders, but every lamp gets its bulb child and default settings from it.

### 10. Common mistakes

> [!MISTAKE] Writing the shared source as `def` and then seeing an extra copy in the render. Use `class` so the source is abstract.

> [!MISTAKE] Looking for a class with `stage.Traverse()` and concluding it does not exist. Use `stage.GetPrimAtPath()` or `stage.TraverseAll()`.

### 11. Exam traps

> [!TRAP] "A `class` prim is not defined." It *is* defined (`class` is a defining specifier like `def`). It is **abstract**, which is a different property. `over` is the specifier that does not define a prim.

> [!TRAP] "Inherits can only target `class` prims." Any prim path works. `class` is a convention that keeps the source out of the scene.

### 12. Practice questions

1. What do `IsDefined()` and `IsAbstract()` return for a prim authored as `class "_class_Rock"`?
2. Which call lists a class prim during traversal?
   A. `stage.Traverse()` B. `stage.TraverseAll()` C. `stage.GetPseudoRoot().GetChildren()` filtered by `IsActive()` D. `Usd.PrimRange(stage.GetPseudoRoot())`
3. A child prim `def Mesh "Geo"` is authored under a class. Is `Geo` abstract?

**Answers**

1. **`True` and `True`.** `class` defines the prim and makes it abstract.
2. **B.** `TraverseAll()` ignores the default predicate. `Traverse()` and a default `Usd.PrimRange` skip abstract prims.
3. **Yes.** Every descendant of a class is abstract.

### 13. Exam takeaways

> [!KEY]
> - `class` specifier → abstract prim: defined, but skipped by `Traverse()` and renderers.
> - Descendants of a class are abstract too.
> - Convention: root-level `_class_Name`.
> - Inherits/specializes target prim paths (`</Path>`), never asset paths.

---

## 19.2 Inherits and broadcast edits

### 1. What is it?

An **inherits arc** makes a prim pick up every opinion of another prim (usually a class). Because the link is live, one edit on the class is a **broadcast edit**: it reaches every inheriting prim.

### 2. Why do we need it?

Without inherits, changing "all lamps to 60 W" means editing hundreds of prims and hoping you found them all. With inherits, you change the class once. Individual prims can still override the shared value locally.

### 3. Beginner explanation

A school dress code is the class. Every student follows it, and when the school changes the rule, everyone follows the new rule tomorrow. A student with a doctor's note (a local opinion) can still wear something different.

Where the analogy breaks: in USD the "note" always wins for that student. There is no way for the class to force a value over a direct opinion in the same layer stack.

### 4. Technical explanation

- Python: `prim.GetInherits().AddInherit(path)`; also `RemoveInherit`, `SetInherits`, `ClearInherits`, `GetAllDirectInherits()`. `prim.HasAuthoredInherits()` tells whether any are authored.
- USDA: `inherits = </Path>` with list-editing (`prepend`, `append`, `delete`; Chapter 14). Python's `AddInherit` writes `prepend` by default.
- Inherits are **I** in LIVERPS: weaker than local opinions, stronger than variants, references, payloads, and specializes.
- So in one layer stack: a prim's direct opinion beats its class; the class beats the prim's variant opinions and anything coming through its references.
- With several inherits, the first listed is strongest: `inherits = [</_A>, </_B>]` → `_A` wins where both have opinions.
- The target path is resolved in the same layer stack. If nothing is authored at that path, nothing is inherited, and no composition error is reported. This lets a stronger layer add the class later.
- Classes can include child prims; every inheriting prim gets those children (namespace inheritance).

### 5. Mental model

```text
     edit once                     /_class_Lamp  watts = 60
                                  /      |       \
                         inherits/       |        \inherits
                               v         v         v
                          LampA      LampB       LampC
                          60         60          100  <- direct opinion wins
```

### 6. Simple example

| Step | `/_class_Lamp.watts` | LampA | LampB | LampC (direct `100`) |
|------|----------------------|-------|-------|----------------------|
| Start | 40 | 40 | 40 | 100 |
| Edit class to 60 | 60 | 60 | 60 | 100 |

### 7. USDA example

```usda
#usda 1.0

class "_class_Lamp"
{
    int watts = 60
}

def Xform "LampA" (
    prepend inherits = </_class_Lamp>
)
{
}

def Xform "LampC" (
    prepend inherits = </_class_Lamp>
    variants = {
        string mode = "eco"
    }
    prepend variantSets = "mode"
)
{
    int watts = 100
    variantSet "mode" = {
        "eco" {
            int watts = 9
        }
    }
}
```

Notes: `LampA.watts` is 60 (from the class). `LampC.watts` is 100: its direct opinion beats the class, and the class would also beat the `eco` variant's 9 (I is stronger than V).

### 8. Python example

```python
from pxr import Usd, Sdf

stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_class_Lamp")
cls.CreateAttribute("watts", Sdf.ValueTypeNames.Int).Set(40)

lamps = []
for name in ["LampA", "LampB", "LampC"]:
    lamp = stage.DefinePrim(f"/{name}", "Xform")
    lamp.GetInherits().AddInherit("/_class_Lamp")
    lamps.append(lamp)
lamps[2].CreateAttribute("watts", Sdf.ValueTypeNames.Int).Set(100)

def report(label):
    values = [(p.GetName(), p.GetAttribute("watts").Get()) for p in lamps]
    print(label, values)

report("before:")
cls.GetAttribute("watts").Set(60)            # one broadcast edit
report("after: ")
print("LampA inherits:", lamps[0].GetInherits().GetAllDirectInherits())
```

**Expected output**

```text
before: [('LampA', 40), ('LampB', 40), ('LampC', 100)]
after:  [('LampA', 60), ('LampB', 60), ('LampC', 100)]
LampA inherits: [Sdf.Path('/_class_Lamp')]
```

### 9. Real-world use case

A crowd of 2 000 soldiers inherits `_class_Soldier`. The art director decides all helmets should be darker. One edit to the class's helmet color updates every soldier, while the hero soldier, who has a direct override, keeps his unique look.

### 10. Common mistakes

> [!MISTAKE] Editing a class and expecting it to beat a prim's own direct opinion. Direct opinions in the same layer stack always win. Remove the direct opinion if the class should control it.

> [!MISTAKE] Writing a file path as the inherit target (`inherits = @lib.usda@</_class_Lamp>`). Inherits take only a prim path. To get a class from another file, reference or sublayer that file so the class is in your layer stack.

> [!MISTAKE] Expecting an error when the class path is misspelled. Nothing is reported; the prim simply inherits nothing. Check `GetAllDirectInherits()` and the class path.

### 11. Exam traps

> [!TRAP] "Inherits copy values at authoring time." No. The arc is live; later edits to the class appear immediately in every inheritor.

> [!TRAP] "Variants beat inherits because variants are on the prim itself." No. LIVERPS: I comes before V. A class opinion beats a variant opinion in the same layer stack.

### 12. Practice questions

1. `/A` inherits `/_class_X` (`size = 1`) and has a selected variant with `size = 2`, all in one layer. What is `/A.size`?
2. `inherits = [</_Red>, </_Blue>]`, both classes author `color`. Which wins?
3. Select two. Which are true about inherits?
   A. Later edits to the class reach all inheritors. B. The target can be any prim path. C. The class beats direct opinions on the inheritor. D. The target must be in a different file.

**Answers**

1. **1.** Inherits (I) beat variants (V).
2. **`_Red`.** The first entry in the list is the strongest.
3. **A, B.** C is reversed (direct beats class); D is wrong (the target is a path in the same layer stack).

### 13. Exam takeaways

> [!KEY]
> - Inherits = live link to another prim's opinions; edit the class once, every inheritor updates.
> - LIVERPS: L > **I** > V > R > P > S. Direct opinions beat the class; the class beats variants, references, payloads.
> - First listed inherit is strongest.
> - Missing class path = silently nothing inherited.

---

## 19.3 Specializes as weakest fallback

### 1. What is it?

A **specializes arc** works like inherits: a prim gets opinions from a base prim and receives broadcast edits. The difference is strength: specializes opinions are the **weakest of all**, weaker even than the prim's references and payloads, and weaker than the prim's own opinions wherever they come from.

### 2. Why do we need it?

Sometimes you want "a default that anything else can override". Example: a material library has a generic `Metal` and a `Gold` that refines it. A shot may adjust `Metal` for every metal, but must never override what makes `Gold` gold. Inherits cannot guarantee that (Section 19.4 shows why); specializes can.

### 3. Beginner explanation

A recipe card says "season to taste: 1 tsp salt". That is a default. Anything the cook writes on their own copy of the recipe wins, and so does anything a guest chef adds. The default only fills in what nobody else decided.

Where the analogy breaks: if the *recipe author* updates the default card, every cook's copy that did not decide on salt gets the new amount. The fallback is still live, like inherits.

### 4. Technical explanation

- Python: `prim.GetSpecializes().AddSpecialize(path)`; also `RemoveSpecialize`, `SetSpecializes`, `ClearSpecializes`. `prim.HasAuthoredSpecializes()`.
- USDA: `specializes = </Path>` with the usual list-editing forms.
- Specializes is **S**, last in LIVERPS. Within one layer stack: local > inherits > variants > references > payloads > specializes.
- Specializes opinions also stay weaker than everything brought in through the prim's other arcs, *across* layer stacks. Even when the specialized base is overridden in the strongest shot layer, that override loses to a direct opinion inside a referenced asset.
- Still a broadcast: properties that nothing else authors receive the base's value, including an override of the base made in a stronger layer (Section 19.5).
- Like inherits, the target is a prim path in the same layer stack, and a missing target is silently empty.

### 5. Mental model

```text
  STRONGEST
    L  local (direct) opinions
    I  inherits           <- base beats references
    V  variants
    E  relocates
    R  references         <- referenced asset's values
    P  payloads
    S  specializes        <- base only fills what nothing above authored
  WEAKEST
```

### 6. Simple example

`/ViaInherit` and `/ViaSpecialize` both reference an asset with `roughness = 0.2`, and both point to a class with `roughness = 0.9` in the shot layer.

| Prim | Arc to class | Result |
|------|--------------|--------|
| `/ViaInherit` | inherits | 0.9 (I beats R) |
| `/ViaSpecialize` | specializes | 0.2 (R beats S) |

### 7. USDA example

File: shot.usda (it references an `asset.usda` whose `/Mat` has `double roughness = 0.2`)

```usda
#usda 1.0

class "_base"
{
    double roughness = 0.9
}

def "ViaInherit" (
    prepend inherits = </_base>
    prepend references = @asset.usda@
)
{
}

def "ViaSpecialize" (
    prepend specializes = </_base>
    prepend references = @asset.usda@
)
{
}
```

### 8. Python example

```python
from pxr import Usd

with open("asset.usda", "w") as f:
    f.write("""#usda 1.0
(
    defaultPrim = "Mat"
)
def "Mat"
{
    double roughness = 0.2
}
""")
with open("shot.usda", "w") as f:
    f.write("""#usda 1.0
class "_base"
{
    double roughness = 0.9
    double metallic = 1.0
}
def "ViaInherit" (
    prepend inherits = </_base>
    prepend references = @asset.usda@
)
{
}
def "ViaSpecialize" (
    prepend specializes = </_base>
    prepend references = @asset.usda@
)
{
}
""")

stage = Usd.Stage.Open("shot.usda")
for path in ["/ViaInherit", "/ViaSpecialize"]:
    prim = stage.GetPrimAtPath(path)
    print(path, "roughness =", prim.GetAttribute("roughness").Get(),
          "metallic =", prim.GetAttribute("metallic").Get())

query = Usd.PrimCompositionQuery(stage.GetPrimAtPath("/ViaSpecialize"))
for arc in query.GetCompositionArcs():           # strongest first
    print(" ", arc.GetArcType(), arc.GetTargetNode().path)
```

**Expected output**

```text
/ViaInherit roughness = 0.9 metallic = 1.0
/ViaSpecialize roughness = 0.2 metallic = 1.0
  Pcp.ArcTypeRoot /ViaSpecialize
  Pcp.ArcTypeReference /Mat
  Pcp.ArcTypeSpecialize /_base
```

Notice: `metallic`, which the asset does not author, comes from `_base` in both cases. Specializes still fills gaps. The composition query lists arcs strongest first, and the specialize arc is last.

### 9. Real-world use case

A manufacturing digital twin has a material library: `Steel` is the base, `BrushedSteel` and `PaintedSteel` specialize it. A plant engineer tweaks `Steel.density` for a new supplier, and every steel variant that does not set its own density picks it up. `PaintedSteel`'s own color is never overwritten by changes to `Steel`.

### 10. Common mistakes

> [!MISTAKE] Using specializes when the shot must be able to force a value on every copy. Specializes loses to the asset's own values. Use inherits for "override everything" broadcasts.

> [!MISTAKE] Thinking specializes is a one-time copy. It is live: unauthored properties track the base.

> [!MISTAKE] Expecting the specialized base to beat a reference "because the base is in the stronger root layer". Layer position does not rescue specializes; it is always weakest.

### 11. Exam traps

> [!TRAP] "Specializes is the same as inherits." Same broadcast idea, opposite end of LIVERPS. The difference shows whenever another arc (variant, reference, payload) also has an opinion.

> [!TRAP] "Specializes opinions never apply." They do apply, whenever nothing stronger authors that property.

### 12. Practice questions

1. `/P` references an asset with `size = 3` and specializes `/_base` (`size = 7`) in the root layer. What is `size`?
2. Same as question 1, but the arc is `inherits` instead of `specializes`. What is `size`?
3. Where does specializes sit in LIVERPS?

**Answers**

1. **3.** References beat specializes.
2. **7.** Inherits beat references.
3. **Last (S): the weakest arc.**

### 13. Exam takeaways

> [!KEY]
> - Specializes = live broadcast like inherits, but the **weakest** arc (S, last in LIVERPS).
> - Loses to local, inherits, variants, references, and payloads — even when the base is in a stronger layer.
> - Still supplies values nothing else authors.
> - Typical use: material libraries and "refinement" relationships.

---

## 19.4 Inherits vs. specializes: decision table

### 1. What is it?

A side-by-side comparison to choose the right arc for shared opinions (Obj 1.1: changing the strength of an opinion by choosing the arc that carries it).

### 2. Why do we need it?

Both arcs broadcast, so beginners pick at random. The wrong choice either lets a shot override something it must not touch (inherits where specializes was needed) or blocks an override the shot needs (specializes where inherits was needed).

### 3. Beginner explanation

Inherits is a **style sheet every instance follows, even after later edits**, and it can overrule what an asset author wrote. Specializes is **a default that anything else can override**.

Where the analogy breaks: both are equally "live"; they differ only in how strong their opinions are.

### 4. Technical explanation

The behaviors below were verified on USD 26.08 with an asset `tree.usda` whose `/Tree` inherits `/_class_Tree` and specializes `/_spec_Tree`, referenced into a shot that overrides both classes.

| Question | Inherits | Specializes |
|----------|----------|-------------|
| LIVERPS position | I (second strongest) | S (weakest) |
| Live broadcast of later edits? | Yes | Yes |
| Asset's direct opinion vs. asset's own class | Direct wins | Direct wins |
| Shot's class override vs. asset's direct opinion | **Shot class wins** | **Asset direct wins** |
| Shot's class override vs. asset's own class | Shot wins | Shot wins |
| Base vs. the prim's references/payloads (same stack) | Base wins | References/payloads win |
| Base vs. the prim's variants | Base wins | Variants win |
| Typical use | Shot-wide or show-wide overrides of all copies | Material libraries, "refinements" of a base |

### 5. Mental model

```text
                Can a shot override of the base beat the asset's own value?
                          |                              |
                    yes, it must                   no, it must not
                          v                              v
                      INHERITS                      SPECIALIZES
         ("style sheet that rules all")     ("default anyone can override")
```

### 6. Simple example

| Property on `/Tree` | Asset authors | Shot class override | Inherits result | Specializes result |
|---------------------|---------------|---------------------|-----------------|--------------------|
| leaves / season | direct value | new value | shot value | asset value |
| bark / height | only in asset's class | new value | shot value | shot value |

### 7. USDA example

File: tree.usda

```usda
#usda 1.0
(
    defaultPrim = "Tree"
)

class "_class_Tree"
{
    string bark = "brown-class"
}

class "_spec_Tree"
{
    string height = "tall-spec"
}

def Xform "Tree" (
    prepend inherits = </_class_Tree>
    prepend specializes = </_spec_Tree>
)
{
    string leaves = "green-local"
    string season = "summer-local"
}
```

File: shot.usda

```usda
#usda 1.0

class "_class_Tree"
{
    string leaves = "autumn-shot"
    string bark = "grey-shot"
}

class "_spec_Tree"
{
    string season = "winter-shot"
    string height = "short-shot"
}

def "TreeA" (
    prepend references = @tree.usda@
)
{
}
```

### 8. Python example

```python
from pxr import Usd

FILES = {
    "tree.usda": """#usda 1.0
(
    defaultPrim = "Tree"
)
class "_class_Tree"
{
    string bark = "brown-class"
}
class "_spec_Tree"
{
    string height = "tall-spec"
}
def Xform "Tree" (
    prepend inherits = </_class_Tree>
    prepend specializes = </_spec_Tree>
)
{
    string leaves = "green-local"
    string season = "summer-local"
}
""",
    "shot.usda": """#usda 1.0
class "_class_Tree"
{
    string leaves = "autumn-shot"
    string bark = "grey-shot"
}
class "_spec_Tree"
{
    string season = "winter-shot"
    string height = "short-shot"
}
def "TreeA" (
    prepend references = @tree.usda@
)
{
}
""",
}
for name, text in FILES.items():
    with open(name, "w") as f:
        f.write(text)

stage = Usd.Stage.Open("shot.usda")          # keep the stage alive
tree = stage.GetPrimAtPath("/TreeA")
rows = [("leaves", "inherits, asset direct"), ("bark", "inherits, asset class"),
        ("season", "specializes, asset direct"), ("height", "specializes, asset class")]
for attr, case in rows:
    print(f"{attr:7}{case:27}-> {tree.GetAttribute(attr).Get()}")
```

**Expected output**

```text
leaves inherits, asset direct     -> autumn-shot
bark   inherits, asset class      -> grey-shot
season specializes, asset direct  -> summer-local
height specializes, asset class   -> short-shot
```

Read it row by row: through inherits, the shot beats everything in the asset. Through specializes, the shot beats only the asset's own specialized base, never the asset's direct value.

### 9. Real-world use case

Games: every enemy inherits `_class_Enemy` so a balance designer can change all enemies' `health` from the level layer, even if a prefab author set one. Rendering: every car paint specializes `_spec_CarPaint`, so a look-dev artist's tweak to the base never overwrites the red of `FerrariRed`.

### 10. Common mistakes

> [!MISTAKE] Choosing inherits for a material library. A shot override of the base then clobbers every specific material's authored values. Use specializes.

> [!MISTAKE] Choosing specializes for a "fix all copies" shot override. The asset's own values keep winning. Use inherits.

### 11. Exam traps

> [!TRAP] In a single layer stack with no other arcs, inherits and specializes give the same result (direct opinions win, the base fills the rest). Exam items that test the difference always involve a reference, payload, or variant. Look for it.

> [!TRAP] Both arcs broadcast. An answer saying "specializes does not receive later edits to the base" is wrong.

### 12. Practice questions

1. A shot must change the `wheelColor` of every referenced copy of a car, even copies whose asset authored a wheel color. Inherits or specializes?
2. Select two. In which cases do inherits and specializes produce **different** results?
   A. Prim with only a direct opinion and the base, in one layer B. Prim that references an asset authoring the property C. Prim with a selected variant authoring the property D. Prim with no opinion except the base's
3. In the Python example, why is `height` `short-shot` even though it goes through specializes?

**Answers**

1. **Inherits.** Only inherits lets the shot's base override beat the asset's direct opinion.
2. **B, C.** Inherits beats references and variants; specializes loses to them. In A and D both arcs give the same result.
3. **The asset authors `height` only in its own specialized base**, and the shot's override of that base is stronger than the asset's base. No direct opinion competes.

### 13. Exam takeaways

> [!KEY]
> - Both broadcast; they differ only in strength (I strong, S weakest).
> - Shot must override all copies → inherits.
> - Asset-specific values must survive base changes → specializes.
> - The difference only appears when another arc (variant, reference, payload) also has an opinion.

---

## 19.5 Implied inherits across references

### 1. What is it?

When a prim with an inherits arc is brought into a shot by a reference, USD also looks for the inherited class path in the **shot's** layer stack. This is called an **implied inherit**: the inherit is "implied" into the referencing layer stack. The same happens for specializes.

### 2. Why do we need it?

An asset is referenced many times. Without implied inherits, the only way to change all copies would be to edit the asset file (affecting every shot) or every copy (tedious). Implied inherits let one shot override the class once and reach every copy *in that shot only*.

### 3. Beginner explanation

A franchise restaurant follows the head office's rule book (the asset's class). Each city's manager can post an extra sheet titled with the same rule-book name on the local notice board, and every branch in that city follows it. Other cities are unaffected.

Where the analogy breaks: the "same name" matters literally. The shot's class must be at the exact same path, such as `/_class_Tree`; a different name is not linked.

### 4. Technical explanation

- In the asset, `/Tree` inherits `/_class_Tree`. When `/World/Forest/A` references `/Tree`, the reference maps `/Tree` → `/World/Forest/A`. The class path `/_class_Tree` is outside the referenced prim, so it keeps its path, and USD adds an inherit to `/_class_Tree` in the **shot's** layer stack.
- That implied arc lives in the shot's layer stack, so its opinions are stronger than anything inside the reference, including the asset's direct opinions (Section 19.4).
- It works wherever the asset is placed (`/TreeA`, `/World/Forest/A`, …): all copies follow the same root-level shot class.
- The shot does not need to author any `inherits` itself. It only authors opinions at the class path; a `class` specifier is the clean way to do it.
- `Usd.PrimCompositionQuery` shows the implied arc: `arc.IsImplicit()` returns `True` and the target node's layer stack is the shot's.
- `GetAllDirectInherits()` on a copy returns `/_class_Tree`, the path as seen in the shot's namespace.

### 5. Mental model

```text
  shot.usda layer stack                     tree.usda layer stack
  ---------------------                     ---------------------
  class "_class_Tree" { leaves=autumn } <-.  class "_class_Tree" { leaves=green }
                                          |        ^
  /World/Forest/A --reference-->  /Tree --'--------'  inherits </_class_Tree>
  /World/Forest/B --reference-->  /Tree      (implied: also look in the shot)

  Strength for A:  shot L > shot I (implied class) > ... > R: asset L > asset I
```

### 6. Simple example

| Shot authors | `/World/Forest/A.leaves` | `/World/Forest/B.leaves` |
|--------------|--------------------------|--------------------------|
| nothing | `green` (asset class) | `green` |
| `class "_class_Tree" { leaves = "autumn" }` | `autumn` | `autumn` |

### 7. USDA example

File: tree.usda

```usda
#usda 1.0
(
    defaultPrim = "Tree"
)

class "_class_Tree"
{
    string leaves = "green"
}

def Xform "Tree" (
    prepend inherits = </_class_Tree>
)
{
}
```

File: forest.usda

```usda
#usda 1.0

class "_class_Tree"
{
    string leaves = "autumn"
}

def Xform "World"
{
    def Xform "Forest"
    {
        def "A" (
            prepend references = @tree.usda@
        )
        {
        }

        def "B" (
            prepend references = @tree.usda@
        )
        {
        }
    }
}
```

Notes: `forest.usda` never writes `inherits`. Its `_class_Tree` is picked up by both copies because of the asset's inherits arc.

### 8. Python example

```python
from pxr import Usd, Sdf

with open("tree.usda", "w") as f:
    f.write("""#usda 1.0
(
    defaultPrim = "Tree"
)
class "_class_Tree"
{
    string leaves = "green"
}
def Xform "Tree" (
    prepend inherits = </_class_Tree>
)
{
}
""")

stage = Usd.Stage.CreateInMemory()
copies = []
for name in ["A", "B"]:
    prim = stage.DefinePrim(f"/World/Forest/{name}")
    prim.GetReferences().AddReference("tree.usda")
    copies.append(prim)

def leaves():
    return [p.GetAttribute("leaves").Get() for p in copies]

print("before shot class:", leaves())
shot_class = stage.CreateClassPrim("/_class_Tree")     # in the shot's root layer
shot_class.CreateAttribute("leaves", Sdf.ValueTypeNames.String).Set("autumn")
print("after shot class: ", leaves())
print("direct inherits:", copies[0].GetInherits().GetAllDirectInherits())

query = Usd.PrimCompositionQuery(copies[0])
for arc in query.GetCompositionArcs():
    layer = arc.GetTargetNode().layerStack.identifier.rootLayer
    origin = "tree.usda" if layer.identifier.endswith("tree.usda") else "shot"
    print(" ", arc.GetArcType(), arc.GetTargetNode().path, origin,
          "implicit" if arc.IsImplicit() else "")
```

**Expected output**

```text
before shot class: ['green', 'green']
after shot class:  ['autumn', 'autumn']
direct inherits: [Sdf.Path('/_class_Tree')]
  Pcp.ArcTypeRoot /World/Forest/A shot
  Pcp.ArcTypeInherit /_class_Tree shot implicit
  Pcp.ArcTypeReference /Tree tree.usda
  Pcp.ArcTypeInherit /_class_Tree tree.usda
```

The implied inherit (`implicit`, in the shot) is listed before the reference: it is stronger than everything in `tree.usda`.

### 9. Real-world use case

In a film sequence, a forest of 500 referenced trees must look autumnal in shot 12 only. The shot's lighting layer authors `class "_class_Tree"` with new leaf colors. All 500 trees change in shot 12; the published tree asset and every other shot are untouched.

### 10. Common mistakes

> [!MISTAKE] Overriding the class at a different path in the shot (for example `/World/_class_Tree`). Implied inherits use the asset's class path exactly, here `/_class_Tree`.

> [!MISTAKE] Editing the class inside the published asset to fix one shot. That changes every shot that uses the asset. Override the class in the shot instead.

> [!MISTAKE] Expecting a shot override of a *specialized* base to beat the asset's direct values. Implied specializes exist too, but stay weakest (Section 19.4).

### 11. Exam traps

> [!TRAP] "The shot must add `inherits` to every copy to override the class." No. The asset's inherits arc is implied into the shot automatically; the shot only authors the class.

> [!TRAP] "A shot's class override is weaker than the asset's direct opinion, because local beats inherits." "Local" means local to the same layer stack. The implied inherit is in the stronger shot layer stack, so it beats everything inside the reference.

### 12. Practice questions

1. An asset's `/Rock` inherits `/_class_Rock`. A shot references it at `/Set/Rock_01` and `/Set/Rock_02`. At which path must the shot author overrides to change both?
2. Using `Usd.PrimCompositionQuery`, how can you tell an implied inherit from an authored one?
3. Select two. The shot authors `class "_class_Rock" { color = "grey" }`. Which values does `/Set/Rock_01.color` take?
   A. `grey` if the asset authors `color` only on `_class_Rock` B. `grey` even if the asset authors `color` directly on `/Rock` C. The asset's direct value, because local beats inherits D. No value, because the shot never authored `inherits`

**Answers**

1. **`/_class_Rock`** — the same path the asset's inherits arc names.
2. **`arc.IsImplicit()` returns `True`** for the implied arc, and its target node is in the shot's layer stack.
3. **A, B.** The implied class opinion is in the shot's layer stack, stronger than all reference content. C misreads "local"; D ignores implied inherits.

### 13. Exam takeaways

> [!KEY]
> - Referencing an asset that inherits `/_class_X` also links `/_class_X` in the referencing layer stack.
> - The shot's class override beats everything inside the reference, including direct opinions.
> - Same exact path required; the shot need not author `inherits` itself.
> - Implied specializes exist too but remain weakest.
> - `PrimCompositionQuery`: `IsImplicit()` marks implied arcs.

---

## Chapter lab(s)

**Lab 17 — Classes and inherits: broadcast edits** (`python-labs/lab17_*.md`, Obj 1.1). You create a `_class_` prim, make many prims inherit it, broadcast edits, add local overrides, then reference the asset into a shot and override the class there (implied inherits).

**Lab 18 — Specializes vs. inherits side by side** (`python-labs/lab18_*.md`, Obj 1.6). You build the same asset twice, once with inherits and once with specializes, reference both into a shot, override the base in the shot, and record which values win and why.

## USDA reading exercises

**Exercise 19-A.** One layer:

```usda
#usda 1.0

class "_class_Chair"
{
    string fabric = "wool"
    int legs = 4
}

def "Chair1" (
    prepend inherits = </_class_Chair>
    variants = {
        string style = "bar"
    }
    prepend variantSets = "style"
)
{
    string fabric = "leather"
    variantSet "style" = {
        "bar" {
            int legs = 3
            double height = 1.1
        }
    }
}
```

What are `fabric`, `legs`, and `height` on `/Chair1`?

**Exercise 19-B.** `lib.usda` has `class "_spec_Paint" { string finish = "matte"  string coat = "single" }` and `def "RedPaint" (specializes = </_spec_Paint>) { string finish = "gloss" }`. The shot references `lib.usda</RedPaint>` at `/Car/Paint` and authors `class "_spec_Paint" { string finish = "satin"  string coat = "double" }`. What are `finish` and `coat` on `/Car/Paint`? What changes if `RedPaint` used `inherits` instead?

## Chapter review

### Summary

- A `class` prim is defined but abstract: skipped by `Traverse()` and renderers; its children are abstract too.
- Inherits (I) is a live link: edit the class once and every inheritor updates (broadcast).
- Direct opinions beat the class in the same layer stack; the class beats variants, references, payloads, and specializes.
- With several inherits, the first listed is strongest; a missing target is silently empty.
- Specializes (S) also broadcasts but is the weakest arc; it only fills properties nothing else authors.
- A shot override of a specialized base never beats the asset's own values; a shot override of an inherited class does.
- Implied inherits: a shot can override `/_class_X` and reach every referenced copy of an asset that inherits `/_class_X`.
- Implied arcs are reported by `Usd.PrimCompositionQuery` with `IsImplicit() == True`.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `class "_class_X"` | Abstract source of shared opinions |
| "Change every copy in this shot" | Override the inherited class in the shot (implied inherits) |
| "Material library", "refinement", "base material" | Specializes |
| Class edit has no effect on one prim | That prim has a direct opinion |
| Shot override of a base loses to an asset value | The arc is specializes |
| Base beats a referenced value | The arc is inherits |
| `inherits = [</_A>, </_B>]` | `_A` wins where both author |
| Class not found by `Traverse()` | Abstract; use `TraverseAll()` or `GetPrimAtPath()` |

### Review questions

**R19-01** · Obj 1.6 · Single choice
Which list orders these arcs from strongest to weakest?
A. Inherits, References, Variants, Specializes
B. Inherits, Variants, References, Specializes
C. Variants, Inherits, Specializes, References
D. References, Inherits, Variants, Specializes

**R19-02** · Obj 1.1 · Single choice
`/Lamp` inherits `/_class_Lamp` (`watts = 60`) and has a direct `watts = 100` in the same layer. The class is changed to `watts = 75`. What is `/Lamp.watts`?
A. 60 B. 75 C. 100 D. 175

**R19-03** · Obj 1.1 · Single choice
A referenced asset `/Car` authors `color = "red"` directly and inherits `/_class_Car`. The shot authors `class "_class_Car" { color = "blue" }`. What is the color of the referenced car in the shot?
A. `red`, because local beats inherits
B. `blue`, because the implied inherit in the shot is stronger than the reference
C. `red`, because the shot never authored `inherits`
D. A composition error

**R19-04** · Obj 1.1 · Single choice
Same as R19-03, but the asset uses `specializes = </_class_Car>`. What is the color?
A. `red` B. `blue` C. No value D. Composition error

**R19-05** · Obj 1.6 · Select two.
Which statements about `class` prims are true?
A. `IsDefined()` returns `True`.
B. `stage.Traverse()` visits them.
C. Their child prims are abstract.
D. They can only be targets of inherits, not specializes.
E. They must be in a separate file.

**R19-06** · Obj 1.1 · USDA reading
```usda
#usda 1.0

class "_base"
{
    int level = 1
}

def "P" (
    prepend specializes = </_base>
    variants = {
        string v = "a"
    }
    prepend variantSets = "v"
)
{
    variantSet "v" = {
        "a" {
            int level = 2
        }
    }
}
```
What is `/P.level`? What would it be with `inherits` instead of `specializes`?
A. 1; 1 B. 2; 1 C. 2; 2 D. 1; 2

**R19-07** · Obj 1.1 · Single choice
A material library must allow look-dev to tweak the generic `Metal` base for a show, without ever overriding values that `Gold` authors itself. Which arc should `Gold` use to `Metal`?
A. inherits B. specializes C. references D. sublayer

**R19-08** · Obj 1.6 · Select two.
Which are true about specializes?
A. It is the weakest arc in LIVERPS.
B. It receives later edits to the base for properties nothing else authors.
C. A base override in the strongest layer beats the prim's references.
D. It requires an asset path.

**R19-09** · Obj 1.1 · Single choice
`/Q` has `inherits = </_Missing>`, and nothing is authored at `/_Missing`. What happens?
A. A composition error stops the stage from opening
B. `/Q` becomes abstract
C. Nothing is inherited; no error is reported
D. `/Q` becomes inactive

**R19-10** · Obj 1.1 · Single choice
An asset's `/Tree` inherits `/_class_Tree`. A shot references it at `/World/T1` and wants to override the class for all trees. Which shot path should hold the override?
A. `/World/T1/_class_Tree`
B. `/World/_class_Tree`
C. `/_class_Tree`
D. `/Tree/_class_Tree`

**R19-11** · Obj 1.6 · Python reading
What does this print? (Not run automatically here, so the output does not give the answer away; the answer key shows the verified result.)
```{.python .norun}
from pxr import Usd, Sdf

stage = Usd.Stage.CreateInMemory()
for name, size in [("/_A", 1), ("/_B", 2)]:
    cls = stage.CreateClassPrim(name)
    cls.CreateAttribute("size", Sdf.ValueTypeNames.Int).Set(size)
p = stage.DefinePrim("/P")
p.GetInherits().SetInherits(["/_B", "/_A"])
print(p.GetAttribute("size").Get())
```

A. 1 B. 2 C. 3 D. None

## Answers

### USDA reading exercises

**19-A.** `fabric = "leather"` (direct beats inherits), `legs = 4` (inherits beat variants, so the class's 4 beats the variant's 3), `height = 1.1` (only the variant authors it).

**19-B.** `finish = "gloss"`, `coat = "double"`. Through specializes, `RedPaint`'s own `gloss` beats the shot's base override; `coat` is authored only on the base, and the shot's base override is stronger than the library's base. With `inherits`, `finish` would be `satin` (and `coat` still `double`): the implied class in the shot beats everything inside the reference.

### Review questions

**R19-01 — B.** LIVERPS: Local, Inherits, Variants, rElocates, References, Payloads, Specializes. Review: §19.3.

**R19-02 — C.** The direct opinion wins in the same layer stack; the class edit reaches only prims without a direct opinion. Review: §19.2.

**R19-03 — B.** The asset's inherits arc is implied into the shot, and the shot's class is stronger than everything inside the reference. "Local beats inherits" only applies within one layer stack. Review: §19.5.

**R19-04 — A.** Specializes is always weakest; the asset's direct value wins even over a shot override of the base. Review: §19.4.

**R19-05 — A, C.** `class` defines an abstract prim; children are abstract; `Traverse()` skips them; they can be targets of either arc; they live in any layer. Review: §19.1.

**R19-06 — B.** With specializes, the variant (V) beats the base (S): 2. With inherits, the class (I) beats the variant: 1. Review: §19.3, §19.2.

**R19-07 — B.** Specializes lets base tweaks flow in while `Gold`'s own values always win. Inherits would let a show override of `Metal` clobber `Gold`. Review: §19.4.

**R19-08 — A, B.** C is false (references beat specializes regardless of layer). D is false (the target is a prim path). Review: §19.3.

**R19-09 — C.** A missing inherit target simply contributes nothing; verified on 26.08 with no composition errors. Review: §19.2.

**R19-10 — C.** Implied inherits use the asset's class path unchanged: `/_class_Tree`. Review: §19.5.

**R19-11 — B.** `SetInherits` writes an explicit list `[/_B, /_A]`; the first listed is strongest, so `_B`'s 2 wins. Review: §19.2.

## Further reading

Optional. Everything needed for the exam is explained above.

- [S04] OpenUSD Glossary — entries "Inherits", "Specializes", "Class", "LIVERPS". https://openusd.org/release/glossary.html
- [S06] OpenUSD API Reference — `UsdInherits`, `UsdSpecializes`, `UsdPrimCompositionQuery`. https://openusd.org/release/api/index.html
- [S14] NVIDIA Learn OpenUSD — "Creating Composition Arcs" (inherits and specializes). https://docs.nvidia.com/learn-openusd/latest/index.html
- [S16] Principles of Scalable Asset Structure in OpenUSD (classes for broadcast overrides). https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
