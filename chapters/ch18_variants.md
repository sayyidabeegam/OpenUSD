# Chapter 18 — Variant Sets

> **Exam domain:** Composition (23%) · **Objectives:** 1.7 (also 1.1, 1.6) · **Study day:** 6 · **Est. time:** 100 min
> **Prerequisites:** Ch 3 (layers), Ch 4 (prims, specifiers), Ch 14 (opinions, strength, LIVERPS first look), Ch 15 (edit targets), Ch 16 (references), Ch 17 (payloads)

## Learning goals

- Explain what a variant set, a variant, and a variant selection are, and how they appear in USDA.
- Author opinions inside a variant with `GetVariantEditContext()`, and avoid the "no selection" trap.
- Build nested variant sets and predict which sets exist for a given selection.
- Configure fallback selections with `Usd.Stage.SetGlobalVariantFallbacks()` at the right time.
- Decide when a variant set is the right tool for structuring an asset, and when it is not (Obj 1.7).
- Predict the winning value when direct opinions, variant opinions, and selections compete (Obj 1.1, 1.6).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Variant set** | A named switch on a prim, such as `color` or `lod`, that holds several alternatives. |
| **Variant** | One named alternative inside a variant set, such as `red` or `high`. It stores opinions. |
| **Variant selection** | A prim metadata opinion (`variants = { string color = "red" }`) naming which variant is active. |
| **Variant opinion** | An opinion authored inside a variant. It only counts when that variant is selected. |
| **Variant edit target** | An edit target that sends new opinions into one variant instead of onto the prim directly. |
| **Nested variant set** | A variant set authored inside a variant of another set. |
| **Fallback selection** | The variant USD picks when no selection is authored anywhere. |
| **Direct (local) opinion** | An opinion authored on the prim itself in a layer, not inside a variant or another arc. |
| **Variant spec path** | The `Sdf` path of a variant's contents, written `/Chair{color=red}`. |

---

## 18.1 Variant sets and variants

### 1. What is it?

A **variant set** is a named switch on a prim. Each position of the switch is a **variant**. Each variant holds its own opinions, and only the selected variant contributes to the composed stage.

### 2. Why do we need it?

Real assets come in versions: a chair in red, blue, or green; a tree at high, medium, or low detail. Without variant sets you would need one file per version and would have to swap references to switch. With a variant set, all versions live in one asset, and anyone downstream switches by changing a single string.

### 3. Beginner explanation

Think of a light switch with named positions, or a car radio with preset buttons. The radio contains every station's preset, but only one plays at a time. Pressing another button changes what you hear without rebuilding the radio.

Where the analogy breaks: a radio button only plays sound. A variant can change anything on the prim and its children: attribute values, child prims, references, payloads, even other variant sets.

### 4. Technical explanation

- A variant set belongs to one prim. You get it through `prim.GetVariantSets()` (a `Usd.VariantSets` object), then `AddVariantSet(name)` or `GetVariantSet(name)` returns a `Usd.VariantSet`.
- `Usd.VariantSet.AddVariant(name)` creates a variant. `GetVariantNames()` lists them (USD 26.08 returns them sorted by name).
- The list of set names is prim metadata `variantSets`, list-edited like other lists (Chapter 14). Python authors `prepend variantSets`.
- The selection is a separate prim metadata dictionary, `variants`. It maps set name to variant name.
- In `Sdf` terms, a variant's contents live at a **variant spec path** such as `/Chair{color=red}`. Its child prims live below it, for example `/Chair{color=red}Cushion`.
- Variant names follow identifier rules with extras: `low-res`, `1k`, and `a|b` are valid; names with `.` or spaces are rejected (checked on 26.08).
- Variants are the **V** in LIVERPS: they are stronger than references, payloads, and specializes, and weaker than local opinions and inherits.

### 5. Mental model

```text
  Prim "Chair"
  +-- variant set "color"      (the switch)
  |     +-- "blue"   { opinions... }
  |     +-- "green"  { opinions... }
  |     +-- "red"    { opinions... }   <-- selection: color = "red"
  |
  Only the selected variant's opinions enter composition.
```

### 6. Simple example

| Variant set | Variants | Selection | What you see |
|-------------|----------|-----------|--------------|
| `color` | `red`, `blue`, `green` | `blue` | The blue chair |

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    variants = {
        string color = "blue"
    }
    prepend variantSets = "color"
)
{
    variantSet "color" = {
        "blue" {
            color3f[] primvars:displayColor = [(0, 0, 1)]
        }
        "red" {
            color3f[] primvars:displayColor = [(1, 0, 0)]
        }
    }
}
```

Line by line:
- `variants = { string color = "blue" }` is the **selection**. It is prim metadata.
- `prepend variantSets = "color"` declares that this prim has a set called `color`.
- `variantSet "color" = { ... }` holds the variants. Each `"name" { ... }` block is a variant with its own opinions.
- Each variant body must span several lines. A one-line body such as `"red" { int x = 1 }` fails to parse.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
chair = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()

vsets = chair.GetVariantSets()
color = vsets.AddVariantSet("color")
for name in ["red", "blue", "green"]:
    color.AddVariant(name)

print("sets:", vsets.GetNames())
print("variants:", color.GetVariantNames())
print("selection:", repr(color.GetVariantSelection()))
color.SetVariantSelection("blue")
print("selection:", color.GetVariantSelection())
print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
sets: ['color']
variants: ['blue', 'green', 'red']
selection: ''
selection: blue
#usda 1.0

def Xform "Chair" (
    variants = {
        string color = "blue"
    }
    prepend variantSets = "color"
)
{
    variantSet "color" = {
        "blue" {

        }
        "green" {

        }
        "red" {

        }
    }
}
```

Notice: the variants were added in the order red, blue, green, but are listed alphabetically. Before you select anything, the selection is the empty string.

### 9. Real-world use case

A furniture retailer's digital catalog stores each sofa once, with a `fabric` variant set (`linen`, `velvet`, `leather`) and a `legs` variant set (`oak`, `steel`). The web configurator only changes selections; it never copies geometry.

### 10. Common mistakes

> [!MISTAKE] Expecting `GetVariantNames()` to keep the order you added variants. It returns sorted names. If order matters for a UI, store the order yourself (for example in `customData`).

> [!MISTAKE] Writing a variant body on one line in hand-edited USDA (`"red" { int x = 1 }`). The text parser rejects it. Put each opinion on its own line.

> [!MISTAKE] Using a name with a dot, such as `v1.2`, as a variant name. It is rejected. Use `v1_2` or `v1-2`.

### 11. Exam traps

> [!TRAP] "A variant set is a separate file." No. Variant sets and their variants live inside a layer, on a prim. A variant may *contain* a reference or payload to another file, but the set itself is scene description in the same layer.

> [!TRAP] Confusing `variantSets` (the list of set names) with `variants` (the selection dictionary). Questions often show both and ask which one switches the look.

### 12. Practice questions

1. In USDA, which metadata on a prim decides which variant is active?
   A. `variantSets` B. `variants` C. `variantSet` D. `kind`
2. A prim has variant set `lod` with variants `high` and `low`. How many variants contribute opinions to the composed prim at one time?
3. What is the `Sdf` path of the contents of variant `low` in set `lod` on `/Tree`?

**Answers**

1. **B.** `variants = { string lod = "low" }` is the selection. `variantSets` only lists the set names; `variantSet "lod" = {...}` holds the variants' contents.
2. **One per set.** Only the selected variant of each set contributes. Unselected variants are stored but ignored.
3. **`/Tree{lod=low}`.** Variant contents use the `{set=variant}` path syntax.

### 13. Exam takeaways

> [!KEY]
> - Variant set = a named switch on a prim; variant = one position; selection = which position.
> - `variantSets` lists set names; `variants` holds selections. Both are prim metadata.
> - Only the selected variant's opinions compose. Variants are the **V** in LIVERPS.
> - Variant content paths look like `/Prim{set=variant}`.

---

## 18.2 Selections and authoring inside variants

### 1. What is it?

**Authoring inside a variant** means writing opinions into one variant instead of onto the prim directly. You do it by selecting the variant and then using a **variant edit target**, usually through `GetVariantEditContext()`.

### 2. Why do we need it?

Normal authoring writes **direct opinions** on the prim. Those would apply no matter which variant is selected. To make "red" actually mean red, the red color must be stored *inside* the `red` variant.

### 3. Beginner explanation

Imagine a binder with tabbed sections. To write in the "red" section, you first open the binder to the "red" tab, then write. If you forget to open a tab, you write on the binder's cover, and it shows up whichever tab is open.

Where the analogy breaks: USD does not warn you when you write on the cover. The binder simply ends up with a note on the cover.

### 4. Technical explanation

- `vset.SetVariantSelection(name)` authors the selection at the stage's current edit target (Chapter 15).
- `vset.GetVariantEditTarget()` returns a `Usd.EditTarget` that maps prim paths into the selected variant: `/Chair` becomes `/Chair{color=red}`.
- `vset.GetVariantEditContext()` returns a Python context manager. Inside the `with` block, the stage's edit target is that variant target. It is equivalent to `Usd.EditContext(stage, vset.GetVariantEditTarget())`.
- The variant edit target always uses the **currently selected** variant. You must select first.
- If no variant is selected, the variant edit target is invalid (`IsValid()` is `False`) and `GetVariantEditContext()` leaves the edit target unchanged, so edits land as direct opinions. No error or warning is printed (verified on 26.08).
- Selecting a variant name that does not exist is not an error. The selection is authored, but no variant opinions compose.
- Attributes you create inside one variant exist only when that variant is selected. Create (not just `Get`) the attribute inside each variant.
- `vset.ClearVariantSelection()` removes the authored selection at the current edit target.

### 5. Mental model

```text
  SetVariantSelection("red")         GetVariantEditContext()
           |                                   |
           v                                   v
  variants = {color="red"}       edit target -> /Chair{color=red}
                                               |
                                   chair.CreateAttribute(...).Set(...)
                                               |
                                               v
                                 written INSIDE variant "red"
```

### 6. Simple example

| Step | Call | Where the opinion lands |
|------|------|-------------------------|
| 1 | `SetVariantSelection("red")` | `variants` metadata on `/Chair` |
| 2 | inside `GetVariantEditContext()`: `Set("glossy red")` | `/Chair{color=red}.paint` |
| 3 | outside the context: `Set("primer")` | `/Chair.paint` (direct) |

### 7. USDA example

```usda
#usda 1.0

def Xform "Chair" (
    variants = {
        string color = "red"
    }
    prepend variantSets = "color"
)
{
    variantSet "color" = {
        "blue" {
            string paint = "matte blue"
        }
        "red" {
            string paint = "glossy red"

            def Sphere "Knob"
            {
            }
        }
    }
}
```

Notes: the `red` variant adds a child prim `Knob`. When `blue` is selected, `/Chair/Knob` does not exist. Variants can add whole prims, not only values.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
chair = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
color = chair.GetVariantSets().AddVariantSet("color")

paint = {"red": "glossy red", "blue": "matte blue"}
for name, value in paint.items():
    color.AddVariant(name)
    color.SetVariantSelection(name)          # 1. select the variant first
    with color.GetVariantEditContext():      # 2. edits now go inside it
        attr = chair.CreateAttribute("paint", Sdf.ValueTypeNames.String)
        attr.Set(value)

target = color.GetVariantEditTarget()
print("edit target maps /Chair to:", target.MapToSpecPath("/Chair"))
for name in ["red", "blue", "purple"]:
    color.SetVariantSelection(name)
    print(name, "->", chair.GetAttribute("paint").Get())
```

**Expected output**

```text
edit target maps /Chair to: /Chair{color=blue}
red -> glossy red
blue -> matte blue
purple -> None
```

The next script shows the silent mistake: no selection, so the "variant" edit goes onto the prim directly.

```python
from pxr import Usd, Sdf

stage = Usd.Stage.CreateInMemory()
chair = stage.DefinePrim("/Chair", "Xform")
color = chair.GetVariantSets().AddVariantSet("color")
color.AddVariant("red")
print("target valid:", color.GetVariantEditTarget().IsValid())

with color.GetVariantEditContext():          # no selection made!
    chair.CreateAttribute("paint", Sdf.ValueTypeNames.String).Set("red")

layer = stage.GetRootLayer()
print("on /Chair:", list(layer.GetPrimAtPath("/Chair").properties.keys()))
print("in variant:", list(layer.GetPrimAtPath("/Chair{color=red}").properties.keys()))
```

**Expected output**

```text
target valid: False
on /Chair: ['paint']
in variant: []
```

### 9. Real-world use case

In a games pipeline, a build script loops over `damage` variants (`intact`, `dented`, `wrecked`) of a vehicle. For each one it selects the variant, enters the edit context, and references the matching geometry file. Level designers then switch damage states with one selection.

### 10. Common mistakes

> [!MISTAKE] Calling `GetVariantEditContext()` before `SetVariantSelection()`. Edits silently become direct opinions that apply to every variant. Always select first, or check `GetVariantEditTarget().IsValid()`.

> [!MISTAKE] Creating an attribute inside the `red` variant, then calling `chair.GetAttribute("paint").Set(...)` inside the `blue` variant. With `blue` selected the attribute does not exist yet, so `Set` raises an error ("Empty typeName"). Use `CreateAttribute` in every variant.

> [!MISTAKE] Leaving the final selection at whatever the loop set last. After authoring all variants, set the selection you want shipped as the default.

### 11. Exam traps

> [!TRAP] "Selecting a variant that does not exist raises an error." False. The selection is authored and the prim just gets no variant opinions. This is a common cause of "my variant shows nothing" bugs.

> [!TRAP] A question may show `Usd.EditContext(stage, vset.GetVariantEditTarget())`. That is the same as `vset.GetVariantEditContext()`; both are correct.

### 12. Practice questions

1. You call `vset.GetVariantEditContext()` without ever selecting a variant, then set `size = 3`. Where is the opinion stored?
   A. Inside the first variant B. Inside every variant C. Directly on the prim D. Nowhere; an error is raised
2. Which two expressions, used as `with <expression>:`, send the edits in the block into the selected variant? Select two.
   A. `vset.GetVariantEditTarget()` B. `stage.GetEditTarget()` C. `Usd.EditContext(stage, vset.GetVariantEditTarget())` D. `vset.GetVariantEditContext()` E. `prim.GetVariantSets()`
3. What does `chair.GetAttribute("paint").Get()` return when the selection is `purple` and no `purple` variant exists?

**Answers**

1. **C.** With no selection the variant edit target is invalid, the edit target is left unchanged, and the opinion becomes direct.
2. **C, D.** Both are context managers that switch the stage's edit target to the variant for the duration of the block. A returns an `Usd.EditTarget`, which is not a context manager; B returns the stage's current target; E returns the variant sets object.
3. **`None`.** The attribute only exists inside `red` and `blue`, so with an unknown selection there is no opinion and no attribute.

### 13. Exam takeaways

> [!KEY]
> - Select first, then author inside `with vset.GetVariantEditContext():`.
> - The variant edit target maps `/Prim` to `/Prim{set=variant}`.
> - No selection means edits go onto the prim directly, silently.
> - An unknown selection is not an error; it just yields no variant opinions.

---

## 18.3 Nested variants

### 1. What is it?

A **nested variant set** is a variant set authored *inside* a variant of another set. For example, each `model` variant (`sedan`, `truck`) can carry its own `trim` set.

### 2. Why do we need it?

Some choices only make sense under another choice. A sedan may offer `base` and `sport` trims while a truck offers none. Nesting expresses "this option depends on that option" and avoids impossible combinations.

### 3. Beginner explanation

A restaurant menu: you first pick "pizza" or "salad". Only if you pick pizza do you see the "crust" choices. The crust question lives inside the pizza choice.

Where the analogy breaks: in USD, nothing stops you from authoring a `trim` selection even when the truck is chosen. The selection is simply ignored because no `trim` set exists there.

### 4. Technical explanation

- To nest, select the outer variant, enter its edit context, then call `prim.GetVariantSets().AddVariantSet("trim")`. To author inside an inner variant, select it and enter a second edit context inside the first.
- The `Sdf` path of nested content chains the selections: `/Car{model=sedan}{trim=sport}`.
- The inner set exists in the composed prim **only** when an outer variant that defines it is selected. `GetVariantSets().GetNames()` changes with the outer selection.
- A selection for the inner set can be authored inside the outer variant (a default per model) or directly on the prim. A direct selection is stronger than one authored inside a variant (direct beats variant; see 18.6).

### 5. Mental model

```text
  /Car
  +-- model = sedan ----+-- trim = base   { label = "sedan-base" }
  |                     +-- trim = sport  { label = "sedan-sport" }
  +-- model = truck  ---(no trim set here)
```

### 6. Simple example

| `model` | Sets on the prim | Possible `trim` |
|---------|------------------|-----------------|
| `sedan` | `model`, `trim` | `base`, `sport` |
| `truck` | `model` | none |

### 7. USDA example

```usda
#usda 1.0

def Xform "Car" (
    variants = {
        string model = "sedan"
    }
    prepend variantSets = "model"
)
{
    variantSet "model" = {
        "sedan" (
            variants = {
                string trim = "base"
            }
            prepend variantSets = "trim"
        ) {
            variantSet "trim" = {
                "base" {
                    string label = "sedan-base"
                }
                "sport" {
                    string label = "sedan-sport"
                }
            }
        }
        "truck" {
            string label = "truck"
        }
    }
}
```

Notes: the `sedan` variant has its own metadata block `( ... )` that declares the nested `trim` set and selects `base` by default. The `truck` variant has no `trim` set at all.

### 8. Python example

```python
from pxr import Usd, Sdf

stage = Usd.Stage.CreateInMemory()
car = stage.DefinePrim("/Car", "Xform")
model = car.GetVariantSets().AddVariantSet("model")

model.AddVariant("sedan")
model.SetVariantSelection("sedan")
with model.GetVariantEditContext():
    trim = car.GetVariantSets().AddVariantSet("trim")
    for t in ["base", "sport"]:
        trim.AddVariant(t)
        trim.SetVariantSelection(t)
        with trim.GetVariantEditContext():
            attr = car.CreateAttribute("label", Sdf.ValueTypeNames.String)
            attr.Set("sedan-" + t)
    trim.SetVariantSelection("base")         # default trim for sedans

model.AddVariant("truck")
model.SetVariantSelection("truck")
with model.GetVariantEditContext():
    car.CreateAttribute("label", Sdf.ValueTypeNames.String).Set("truck")

for m in ["sedan", "truck"]:
    model.SetVariantSelection(m)
    print(m, car.GetVariantSets().GetNames(), car.GetAttribute("label").Get())

model.SetVariantSelection("sedan")
car.GetVariantSet("trim").SetVariantSelection("sport")
print("sedan+sport:", car.GetAttribute("label").Get())
print(stage.GetRootLayer().GetPrimAtPath("/Car{model=sedan}{trim=sport}").path)
```

**Expected output**

```text
sedan ['model', 'trim'] sedan-base
truck ['model'] truck
sedan+sport: sedan-sport
/Car{model=sedan}{trim=sport}
```

### 9. Real-world use case

An automotive configurator nests `interior` options inside each `trimLevel` variant, because luxury interiors are only offered on top trims. A digital-twin factory model nests `toolHead` variants inside each `robotModel` variant.

### 10. Common mistakes

> [!MISTAKE] Authoring the inner set while the stage edit target is the plain layer. The `trim` set then lives on the prim directly and appears for every model. Create it inside the outer variant's edit context.

> [!MISTAKE] Nesting deeply "just because". Every level multiplies the combinations a reviewer must test. Use independent (sibling) sets when choices really are independent, such as `color` and `size`.

### 11. Exam traps

> [!TRAP] "Nested variant sets are always visible on the prim." No. An inner set appears only when an outer variant that defines it is selected.

> [!TRAP] Sibling sets vs. nested sets: `color` and `size` on the same prim are *independent* and both always present. Nesting is only for *dependent* choices.

### 12. Practice questions

1. With the USDA example above, which variant sets does `/Car` report when `model = "truck"`?
2. A selection `trim = "sport"` is authored directly on `/Car`, and `trim = "base"` is authored inside `{model=sedan}`. With `model = "sedan"`, which trim is active?
3. True or false: `/Car{model=sedan}{trim=sport}` is a valid `Sdf` path to nested variant content.

**Answers**

1. **Only `model`.** The `trim` set is defined inside `sedan`, so it does not exist for `truck`.
2. **`sport`.** The direct selection is a direct opinion; the one inside the variant is a variant opinion, which is weaker.
3. **True.** Nested selections chain in the path.

### 13. Exam takeaways

> [!KEY]
> - Nest by authoring a set inside an outer variant's edit context.
> - Inner sets exist only under outer variants that define them.
> - Use nesting for dependent choices, sibling sets for independent ones.
> - Nested content path: `/Prim{outer=a}{inner=b}`.

---

## 18.4 Fallback selections

### 1. What is it?

A **fallback selection** is the variant USD chooses for a set when no selection is authored for it in any layer. You register fallbacks for the whole process with `Usd.Stage.SetGlobalVariantFallbacks()`.

### 2. Why do we need it?

Without any selection, a variant set contributes nothing. An asset might show no geometry at all. Fallbacks let a site or application say "if nobody chose, use `lod = low`", for example so a lightweight viewer opens heavy scenes quickly.

### 3. Beginner explanation

A thermostat that nobody has touched still runs at its factory setting. The factory setting is the fallback. The moment someone turns the dial, their choice wins.

Where the analogy breaks: the USD "factory setting" is not stored in the asset file. It belongs to the program opening the file, so two programs can show different defaults for the same file.

### 4. Technical explanation

- `Usd.Stage.SetGlobalVariantFallbacks({"lod": ["medium", "low"]})` takes a dict of set name to an **ordered list** of variant names. USD uses the first name in the list that exists on the prim.
- `Usd.Stage.GetGlobalVariantFallbacks()` returns the current dict (empty `{}` by default).
- Fallbacks are read **when a stage is opened**. Stages opened before the call keep their old behavior, even after `Reload()`. Set fallbacks first, then open stages.
- Any authored selection, in any layer, beats a fallback. `vset.BlockVariantSelection()` authors an empty selection (`string lod = ""`), which hides weaker selections so the fallback applies again.
- `vset.GetVariantSelection()` returns the *composed* selection, including a fallback. `prim.GetVariantSets().GetAllVariantSelections()` returns only *authored* selections.
- In Python, `vset.HasAuthoredVariantSelection()` returns the authored name, or `None` if nothing is authored (not `True`/`False`).
- Sites can also declare fallbacks in a plugin's `plugInfo.json` (see Chapter 38, 38.2).

> [!VERSION] Verified on USD 26.08: fallbacks set after opening a stage do not affect that stage; `BlockVariantSelection()` exists and authors an empty selection; `HasAuthoredVariantSelection()` returns a string or `None` in Python.

### 5. Mental model

```text
  Is a selection authored anywhere (strongest wins)?
        |yes                        |no (or blocked with "")
        v                           v
   use that variant          global fallback list for this set?
                               |yes                     |no
                               v                        v
                     first listed variant      no variant applies
                     that exists on the prim
```

### 6. Simple example

| Authored selection | Global fallback for `lod` | Variant used |
|--------------------|---------------------------|--------------|
| none | none | none (set contributes nothing) |
| none | `["medium", "low"]` | `low` (no `medium` on the prim) |
| `high` | `["low"]` | `high` |
| `""` (blocked) | `["low"]` | `low` |

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Tree"
)

def Xform "Tree" (
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" {
            int polys = 5000
        }
        "low" {
            int polys = 50
        }
    }
}
```

Notes: there is no `variants = {...}` line, so no selection is authored. What you see depends entirely on the opening program's fallbacks.

### 8. Python example

```python
from pxr import Usd

TREE = """#usda 1.0
def Xform "Tree" (
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" {
            int polys = 5000
        }
        "low" {
            int polys = 50
        }
    }
}
"""
with open("tree.usda", "w") as f:
    f.write(TREE)

print("fallbacks:", Usd.Stage.GetGlobalVariantFallbacks())
early = Usd.Stage.Open("tree.usda")
print("no selection:", early.GetPrimAtPath("/Tree").GetAttribute("polys").Get())

Usd.Stage.SetGlobalVariantFallbacks({"lod": ["medium", "low"]})
early.Reload()
print("early stage after setting:", early.GetPrimAtPath("/Tree")
      .GetAttribute("polys").Get())

late = Usd.Stage.Open("tree.usda")
tree = late.GetPrimAtPath("/Tree")
lod = tree.GetVariantSet("lod")
print("stage opened after setting:", tree.GetAttribute("polys").Get())
print("composed selection:", lod.GetVariantSelection())
print("authored selections:", tree.GetVariantSets().GetAllVariantSelections())
print("authored?", lod.HasAuthoredVariantSelection())

lod.SetVariantSelection("high")
print("authored high:", tree.GetAttribute("polys").Get())
lod.BlockVariantSelection()
print("blocked:", tree.GetAttribute("polys").Get(), repr(lod.GetVariantSelection()))
```

**Expected output**

```text
fallbacks: {}
no selection: None
early stage after setting: None
stage opened after setting: 50
composed selection: low
authored selections: {}
authored? None
authored high: 5000
blocked: 50 'low'
```

Notice: the stage opened *before* `SetGlobalVariantFallbacks` still shows `None`, even after `Reload()`. `medium` does not exist, so the next name in the list, `low`, is used.

### 9. Real-world use case

A studio's review tool sets `{"lod": ["proxy"], "shadingVariant": ["preview"]}` at startup, before opening any stage, so animators get fast scenes. The final render farm process sets no fallbacks and relies on the selections authored in the shot.

### 10. Common mistakes

> [!MISTAKE] Calling `SetGlobalVariantFallbacks()` after the stage is open and wondering why nothing changed. Call it at application startup, before `Usd.Stage.Open()`.

> [!MISTAKE] Using `GetAllVariantSelections()` to find out what is displayed. It lists only authored selections and misses fallbacks. Use `GetVariantSelection()` on each set.

> [!MISTAKE] Testing `if vset.HasAuthoredVariantSelection() == True:`. In Python it returns a name or `None`. Test `is not None`.

### 11. Exam traps

> [!TRAP] "Fallbacks are stored in the asset file." No. They come from the application process (or plugins). An authored `variants = {...}` in the file is a selection, not a fallback.

> [!TRAP] "A fallback beats a weak-layer selection." No. Any authored selection beats a fallback. Only a blocked (empty) selection lets the fallback through.

### 12. Practice questions

1. When must `Usd.Stage.SetGlobalVariantFallbacks()` be called to affect a stage?
   A. Any time before `Save()` B. Before the stage is opened C. After `Reload()` D. Inside a variant edit context
2. Fallbacks are `{"lod": ["medium", "low"]}`. The prim has variants `high` and `low` and no authored selection. Which variant is used?
3. Which two statements are true? Select two.
   A. `GetAllVariantSelections()` includes fallback selections. B. `GetVariantSelection()` reports a fallback selection. C. An authored selection in a weak sublayer beats a fallback. D. Fallbacks are saved into the root layer.

**Answers**

1. **B.** Fallbacks are read when the stage is opened.
2. **`low`.** The first listed name that exists on the prim wins; `medium` does not exist.
3. **B, C.** `GetAllVariantSelections()` lists authored selections only, and fallbacks are never written to layers.

### 13. Exam takeaways

> [!KEY]
> - `Usd.Stage.SetGlobalVariantFallbacks({set: [ordered names]})` — set it **before** opening stages.
> - First existing name in the list wins; any authored selection beats every fallback.
> - `BlockVariantSelection()` authors `""` so the fallback applies again.
> - `GetVariantSelection()` = composed (includes fallback); `GetAllVariantSelections()` = authored only.

---

## 18.5 When variants are / are not appropriate

### 1. What is it?

This section is a decision guide (Obj 1.7): which kinds of variation belong in a variant set, and which belong in another tool such as separate assets, payloads, sublayers, inherits, or primvars.

### 2. Why do we need it?

Variants are easy to add, so people overuse them. Misused variants bloat files, break instancing, multiply test combinations, and confuse downstream users. Choosing the right tool keeps assets small and predictable.

### 3. Beginner explanation

A switch is perfect for "one of a few fixed choices" (off, low, high). It is a poor fit for "any value on a dial" (exact temperature) or "a different appliance entirely". Use a variant like a switch: a small number of named, discrete, mutually exclusive alternatives of the same thing.

Where the analogy breaks: a variant can hold a lot of data, including references and payloads, so "small switch" describes the number of choices, not their size.

### 4. Technical explanation

Variants fit when the alternatives are:
- **Discrete and named:** `lod = high/medium/low`, `look = clean/dirty`, `model = sedan/truck`.
- **Mutually exclusive:** only one per set at a time.
- **Versions of the same asset:** same role and interface (same prim path, same purpose).
- **Chosen per use, not per frame:** a selection cannot be animated; it is metadata, not a time-sampled attribute.

Variants are a poor fit when:
- **The values are continuous or per-instance random** (a color per tree in a forest). Use primvars or attributes on the instance instead (Chapter 11).
- **The alternatives must change over time.** Selections cannot be time-sampled; use visibility or attribute animation.
- **The choices are independent and many.** 5 colors × 4 sizes × 3 materials as one set is 60 variants; use separate sibling sets, or better, parameters.
- **Different departments own the alternatives.** Use separate layers (sublayers, Chapter 15) so people do not edit the same file.
- **Instancing matters at scale.** Instances with different selections compose differently, so each distinct selection creates a separate prototype (Chapter 24). Many selections means many prototypes.
- **You only want to avoid loading data.** That is the job of payloads (Chapter 17). A variant may contain a payload, but variant sets themselves do not defer loading.
- **The alternatives are unrelated assets.** A chair and a lamp should be two assets, not variants.

All variants are stored in the file even when unused, so a set with 30 heavy variants makes the asset file large. Put heavy per-variant data behind references or payloads inside each variant.

### 5. Mental model

```text
  Is it a small set of named, exclusive versions of ONE asset,
  chosen per use (not per frame), owned by one team?
        |yes                                   |no
        v                                      v
   VARIANT SET                       continuous/per-instance -> primvar/attribute
                                     changes over time      -> animated attribute
                                     defer loading only     -> payload
                                     separate owners        -> sublayers
                                     unrelated things       -> separate assets
                                     shared tweaks to many  -> inherits (Ch 19)
```

### 6. Simple example

| Need | Best tool |
|------|-----------|
| Tree at high/medium/low detail | Variant set `lod` |
| 10 000 trees, each a slightly different green | Primvar on each instance |
| Light turns on at frame 100 | Animated attribute |
| Don't load the city until needed | Payload |
| Lighting and animation teams edit the same shot | Separate sublayers |

### 7. USDA example

A good pattern: each `lod` variant holds only a payload to its own geometry file, so the asset file stays tiny.

```usda
#usda 1.0
(
    defaultPrim = "Tree"
)

def Xform "Tree" (
    kind = "component"
    variants = {
        string lod = "low"
    }
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" (
            prepend payload = @tree_high.usda@
        ) {
        }
        "low" (
            prepend payload = @tree_low.usda@
        ) {
        }
    }
}
```

Notes: arcs such as `payload` and `references` can be authored inside a variant's metadata block. The payload files are not needed to parse this layer.

### 8. Python example

Different selections on instanceable prims produce different prototypes (Chapter 24 covers instancing in depth):

```python
from pxr import Usd

ROCK = """#usda 1.0
(
    defaultPrim = "Rock"
)
def Xform "Rock" (
    variants = {
        string shape = "round"
    }
    prepend variantSets = "shape"
)
{
    variantSet "shape" = {
        "flat" {
            def Cube "Geo"
            {
            }
        }
        "round" {
            def Sphere "Geo"
            {
            }
        }
    }
}
"""
with open("rock.usda", "w") as f:
    f.write(ROCK)

stage = Usd.Stage.CreateInMemory()
for i in range(6):
    rock = stage.DefinePrim(f"/World/Rock{i}")
    rock.GetReferences().AddReference("rock.usda")
    rock.SetInstanceable(True)
    if i % 2:
        rock.GetVariantSet("shape").SetVariantSelection("flat")

print("instances:", 6)
print("prototypes:", len(stage.GetPrototypes()))
```

**Expected output**

```text
instances: 6
prototypes: 2
```

With 2 selections you get 2 prototypes. If every rock had its own variant, instancing would save nothing.

### 9. Real-world use case

An AEC firm models a building's window module with a `glazing` variant set (`single`, `double`, `triple`). That is a good fit: few named, exclusive options. The exact tint per window, chosen by a solar study, is stored as a primvar instead, because it is continuous and differs per window.

### 10. Common mistakes

> [!MISTAKE] Trying to animate a variant selection over time. Selections are metadata and have no time samples. Animate visibility or attributes instead.

> [!MISTAKE] Packing heavy geometry for 20 variants directly into one file. Every variant is stored and parsed. Reference or payload each variant's data from its own file.

> [!MISTAKE] Giving each of thousands of instances its own variant selection "for variety". It splits instancing into many prototypes. Vary instances with primvars or a few shared selections.

### 11. Exam traps

> [!TRAP] "Use a variant set so the heavy version is not loaded." Loading control is a **payload** feature. A variant only changes *which* opinions compose; combine both if you need both.

> [!TRAP] Look for "per frame", "continuous", "per instance", or "different team" in a scenario. Each of those words usually points away from variants.

### 12. Practice questions

1. Which scenarios are good fits for a variant set? Select two.
   A. A prop available as `clean`, `worn`, and `broken` B. A character's arm rotation per frame C. A vehicle with `left-hand drive` and `right-hand drive` builds D. A unique hue for each of 50 000 grass blades
2. A team wants heavy high-detail geometry to stay unloaded until requested, and to choose between `high` and `low` detail. What combination fits best?
3. Why can giving every instance a different variant selection hurt performance?

**Answers**

1. **A, C.** Both are small sets of named, exclusive versions of one asset. B changes over time; D is continuous and per instance.
2. **A `lod` variant set whose variants each contain a payload.** The variant picks the version; the payload defers loading.
3. **Each distinct selection composes differently, so instancing creates a separate prototype for each one**, reducing sharing.

### 13. Exam takeaways

> [!KEY]
> - Variants: few, named, mutually exclusive versions of one asset, chosen per use.
> - Not variants: per-frame changes, continuous or per-instance values, separate owners, unrelated assets.
> - Selections cannot be animated.
> - Each distinct selection on instances means another prototype.
> - Variants select; payloads defer loading. Combine them for heavy LODs.

---

## 18.6 Variant selection strength surprises

### 1. What is it?

This section explains how variant opinions and variant selections compete with other opinions. Two separate questions are answered by strength: **which variant is selected**, and **does a variant opinion beat other opinions**.

### 2. Why do we need it?

The most common variant bug is "I switched the variant and nothing changed". It is almost always a strength problem: a direct opinion somewhere is stronger than the variant's opinion. Knowing the rules lets you diagnose it in seconds (Obj 1.1, 1.6, and 1.8 in Chapter 22).

### 3. Beginner explanation

Recall the ladder of opinions: the strongest rung answers. A variant's opinions sit on a rung *below* the direct opinions of the same layer stack (the stack of sublayers from Chapter 15). A sticky note written directly on the prim beats anything in the variant binder, even if the binder sits on a higher sheet of the projector stack.

Where the analogy breaks: when a whole asset is referenced, its entire ladder hangs *below* the referencing layer stack's ladder. Then a variant in the shot beats a direct opinion inside the asset.

### 4. Technical explanation

Composition evaluates LIVERPS **per layer stack** (Chapter 14, Chapter 21). Four rules follow:

1. **Direct beats variant within one layer stack.** All direct (L) opinions from every layer of a layer stack are stronger than variant (V) opinions in that layer stack. This holds even when the variant is in a stronger sublayer and the direct opinion is in a weaker sublayer.
2. **The selection is an ordinary opinion.** The `variants` metadata resolves like any value: the strongest authored selection wins. A shot layer's selection beats the asset's own selection; a stronger sublayer's selection beats a weaker one; the session layer beats them all.
3. **A stronger layer stack's variant beats a weaker layer stack's direct opinion.** A variant authored in the shot (on the referencing prim) beats a direct opinion inside the referenced asset, because the asset is a reference (R), evaluated below the shot's L, I, and V.
4. **An asset's direct opinion hides its own variant.** If the asset author left a direct value on the prim, switching that asset's variant changes nothing for that property.

### 5. Mental model

```text
  STRONGEST
   shot layer stack:   L  (direct, all sublayers)      rule 1: L > V
                       I
                       V  (variants authored in shot)  rule 3: beats asset's L
                       R --> asset layer stack:
                               L  (asset direct)       rule 4: hides asset V
                               I
                               V  (asset variants)
                               ...
   WEAKEST
  Selection = strongest authored `variants` value      rule 2
```

### 6. Simple example

| Where the opinions are | Winner |
|------------------------|--------|
| Shot weak sublayer direct `finish = A`; shot strong sublayer variant `finish = B` | A (rule 1) |
| Asset selects `color = red`; shot selects `color = blue` | blue (rule 2) |
| Shot variant `tag = S`; asset direct `tag = D` | S (rule 3) |
| Asset direct `tag = D`; asset variant `tag = V` | D (rule 4) |

### 7. USDA example

File: asset.usda

```usda
#usda 1.0
(
    defaultPrim = "Chair"
)

def Xform "Chair" (
    variants = {
        string color = "red"
    }
    prepend variantSets = "color"
)
{
    string tag = "asset-direct"
    variantSet "color" = {
        "blue" {
            string paint = "blue"
            string tag = "from-blue"
        }
        "red" {
            string paint = "red"
            string tag = "from-red"
        }
    }
}
```

File: strong.usda (the stronger sublayer of the shot)

```usda
#usda 1.0

over "Chair" (
    variants = {
        string color = "blue"
        string fit = "big"
    }
    prepend variantSets = "fit"
)
{
    variantSet "fit" = {
        "big" {
            string finish = "strong-variant"
            string tag = "shot-variant"
        }
    }
}
```

The shot root layer `shot.usda` sublayers `strong.usda` then `weak.usda`, and its `/Chair` references `asset.usda`. `weak.usda` holds one direct opinion: `string finish = "weak-direct"`.

### 8. Python example

```python
from pxr import Usd

FILES = {
    "asset.usda": """#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    variants = {
        string color = "red"
    }
    prepend variantSets = "color"
)
{
    string tag = "asset-direct"
    variantSet "color" = {
        "blue" {
            string paint = "blue"
            string tag = "from-blue"
        }
        "red" {
            string paint = "red"
            string tag = "from-red"
        }
    }
}
""",
    "weak.usda": """#usda 1.0
over "Chair" (
    variants = {
        string color = "red"
    }
)
{
    string finish = "weak-direct"
}
""",
    "strong.usda": """#usda 1.0
over "Chair" (
    variants = {
        string color = "blue"
        string fit = "big"
    }
    prepend variantSets = "fit"
)
{
    variantSet "fit" = {
        "big" {
            string finish = "strong-variant"
            string tag = "shot-variant"
        }
    }
}
""",
    "shot.usda": """#usda 1.0
(
    subLayers = [@strong.usda@, @weak.usda@]
)
over "Chair" (
    prepend references = @asset.usda@
)
{
}
""",
}
for name, text in FILES.items():
    with open(name, "w") as f:
        f.write(text)

shot = Usd.Stage.Open("shot.usda")
chair = shot.GetPrimAtPath("/Chair")
print("rule 2  color selection:", chair.GetVariantSet("color").GetVariantSelection())
print("        paint:", chair.GetAttribute("paint").Get())
print("rule 1  finish:", chair.GetAttribute("finish").Get())
print("rule 3  tag:", chair.GetAttribute("tag").Get())
for spec in chair.GetAttribute("finish").GetPropertyStack():
    print("        finish stack:", spec.layer.identifier.split("/")[-1], spec.path)

asset = Usd.Stage.Open("asset.usda")
achair = asset.GetPrimAtPath("/Chair")
for choice in ["red", "blue"]:
    achair.GetVariantSet("color").SetVariantSelection(choice)
    print(f"rule 4  asset alone, {choice}: tag =", achair.GetAttribute("tag").Get())
```

**Expected output**

```text
rule 2  color selection: blue
        paint: blue
rule 1  finish: weak-direct
rule 3  tag: shot-variant
        finish stack: weak.usda /Chair.finish
        finish stack: strong.usda /Chair{fit=big}.finish
rule 4  asset alone, red: tag = asset-direct
rule 4  asset alone, blue: tag = asset-direct
```

Read the `finish` property stack (strongest first, Chapter 22): the weak sublayer's direct spec comes *before* the strong sublayer's variant spec.

### 9. Real-world use case

A layout artist sets `lod = high` in the shot, but one tree stays low-poly. Inspecting the property stack shows the asset author left a direct `points` opinion on the prim, outside the variants (rule 4). The fix is in the asset: move the direct opinion into the variants. Meanwhile, a lighting artist overrides the tree's look by authoring a `look` variant in the shot's layer; it wins over the asset's direct values (rule 3).

### 10. Common mistakes

> [!MISTAKE] Leaving "default" values directly on an asset prim *and* inside its variants. The direct value always wins in that layer stack, so the variant appears broken. Keep switchable properties only inside the variants.

> [!MISTAKE] Putting a variant in a stronger sublayer and expecting it to beat a direct opinion in a weaker sublayer. Within one layer stack, direct beats variant regardless of sublayer order. Author a direct opinion in the stronger sublayer instead.

> [!MISTAKE] Changing the selection in the asset file and expecting the shot to update, when the shot already authors its own selection. The shot's selection is stronger; change it there (or remove it).

### 11. Exam traps

> [!TRAP] "The stronger sublayer always wins." Only when comparing opinions of the same arc type. Direct opinions in any sublayer beat variant opinions in any sublayer of the same layer stack.

> [!TRAP] "Variants are weaker than local opinions, so a shot variant cannot beat an asset's local value." It can. "Local" means local to the *same* layer stack. The referenced asset's local opinions are inside the reference arc, which is weaker than the shot's variants.

> [!TRAP] Selection strength and variant-opinion strength are two separate questions. First find the winning selection, then compare that variant's opinions with the other opinions.

### 12. Practice questions

1. Layer stack: `strong.usda` (stronger) has a variant opinion `size = 2` in the selected variant; `weak.usda` has a direct `size = 1` on the same prim. What is `size`?
2. An asset selects `look = clean`. The shot that references it selects `look = dirty` in its root layer. Which look is used, and why?
3. Select two. Which opinions beat a direct opinion authored inside a referenced asset?
   A. A variant opinion authored in the referencing shot layer B. A variant opinion inside the same asset C. A direct opinion in the shot's weakest sublayer D. A fallback variant selection

**Answers**

1. **1.** Direct (L) beats variant (V) within one layer stack, regardless of sublayer order.
2. **`dirty`.** The selection is an ordinary opinion, and the shot's root layer is stronger than the referenced asset.
3. **A, C.** Anything in the shot's layer stack (its L, I, V) is stronger than the reference's content. B is weaker than the asset's own direct opinion; D only picks a variant when no selection is authored.

### 13. Exam takeaways

> [!KEY]
> - Within one layer stack: direct (L) beats variant (V), whatever the sublayer order.
> - The selection itself resolves by normal strength; the strongest authored selection wins.
> - A variant in the referencing layer stack beats direct opinions inside the referenced asset.
> - An asset's direct opinion hides that asset's own variant opinions for that property.
> - Debug with `GetPropertyStack()`: it lists specs strongest first.

---

## Chapter lab(s)

**Lab 16 — Variant sets: create, author, select, nest** (`python-labs/lab16_*.md`, Obj 1.7). You build a prop asset with `color` and `lod` variant sets, author inside each variant with edit contexts, nest a `trim` set, then reference the asset into a shot and switch selections from the shot layer. Finally you register a global fallback before opening the stage and confirm which variant appears.

## USDA reading exercises

**Exercise 18-A.** One layer:

```usda
#usda 1.0

def "Lamp" (
    variants = {
        string power = "eco"
    }
    prepend variantSets = "power"
)
{
    int watts = 60
    variantSet "power" = {
        "bright" {
            int watts = 100
        }
        "eco" {
            int watts = 9
            bool led = 1
        }
    }
}
```

What are the composed values of `watts` and `led`?

**Exercise 18-B.** Two files. `prop.usda` defines `/Prop` with variant set `size` (`small`: `double scale = 0.5`; `large`: `double scale = 2`) and selection `small`. The shot:

```usda
#usda 1.0

def "Prop" (
    prepend references = @prop.usda@
    variants = {
        string size = "large"
    }
)
{
}
```

What is `scale` on `/Prop` in the shot? What would it be if the shot's `variants` line were `string size = ""`, the process had fallbacks `{"size": ["small"]}`, and the stage were opened after the fallbacks were set?

## Chapter review

### Summary

- A variant set is a named switch on a prim; each variant stores opinions; only the selected variant composes.
- `variantSets` lists set names; `variants` holds the selection dictionary.
- Author into a variant by selecting it, then using `GetVariantEditContext()`; with no selection, edits silently become direct opinions.
- Nested sets live inside an outer variant and exist only when that variant is selected.
- `Usd.Stage.SetGlobalVariantFallbacks()` must be called before opening a stage; any authored selection beats a fallback.
- `BlockVariantSelection()` authors `""` so fallbacks apply again.
- Use variants for a few named, exclusive versions of one asset; not for animation, continuous or per-instance values, or loading control.
- Within one layer stack, direct opinions beat variant opinions, whatever the sublayer order.
- The strongest authored selection wins; a shot's variant beats direct opinions inside a referenced asset.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `variants = { string x = "..." }` | The selection (prim metadata) |
| `/Prim{set=variant}` | Path to a variant's contents |
| "Switching the variant does nothing" | A direct opinion is stronger (check `GetPropertyStack`) |
| Edits made "in a variant" show in every variant | No selection before `GetVariantEditContext()` |
| Fallbacks have no effect | They were set after the stage was opened |
| "Animate the variant" | Not possible; selections are not time-sampled |
| "Avoid loading heavy data" | Payload (possibly inside a variant) |
| Thousands of instances, each its own variant | Too many prototypes; use primvars |
| Nested set "missing" | The outer variant that defines it is not selected |

### Review questions

**R18-01** · Obj 1.7 · Single choice
Which situation is the best fit for a variant set?
A. A robot arm's joint angle sampled every frame
B. A product shipped in `standard`, `pro`, and `max` editions
C. A random scale for each of 100 000 pebbles
D. Two departments editing the same asset at the same time

**R18-02** · Obj 1.1 · Single choice
In one layer stack, `strong.usda` (stronger sublayer) authors `radius = 5` inside the selected variant, and `weak.usda` authors a direct `radius = 1` on the same prim. What is `radius`?
A. 5, because the stronger sublayer wins
B. 1, because direct opinions beat variant opinions in the same layer stack
C. 5, because variants are evaluated last
D. A composition error is reported

**R18-03** · Obj 1.7 · Select two.
Which statements about variant selections are true?
A. A selection can be time-sampled to switch at frame 50.
B. A selection is prim metadata resolved by normal strength ordering.
C. A selection naming a variant that does not exist raises an exception.
D. A shot layer can select a variant defined inside a referenced asset.
E. Selections can only be authored in the asset's root layer.

**R18-04** · Obj 1.6 · Python reading
```{.python .norun}
vset = prim.GetVariantSets().AddVariantSet("lod")
vset.AddVariant("high")
with vset.GetVariantEditContext():
    prim.CreateAttribute("polys", Sdf.ValueTypeNames.Int).Set(9000)
```
Where is the `polys` opinion stored?
A. In `/Prim{lod=high}`
B. Directly on `/Prim`
C. In the session layer
D. Nowhere; the edit raises an error

(This fragment is not run: it assumes an existing `prim`.)

**R18-05** · Obj 1.7 · Single choice
A viewer should show `lod = proxy` for any asset whose files author no `lod` selection. What should it do?
A. Author `variants = {lod = "proxy"}` into every asset file
B. Call `Usd.Stage.SetGlobalVariantFallbacks({"lod": ["proxy"]})` before opening stages
C. Call `SetGlobalVariantFallbacks` after opening, then `Reload()`
D. Use `BlockVariantSelection()` on every prim

**R18-06** · Obj 1.1 · Single choice
An asset's `/Tree` has a direct `string season = "summer"` and also `season` values inside each `look` variant. A shot references the asset and selects `look = "winter"` but authors nothing else. What is `season`?
A. `winter`
B. `summer`
C. Empty, because the opinions conflict
D. Whatever the global fallback says

**R18-07** · Obj 1.1 · Single choice
Same asset as R18-06. The shot instead authors, on its own `/Tree`, a variant set `shotLook` with selected variant `snow` containing `season = "snow"`. What is `season`?
A. `summer`, because local opinions beat variants
B. `snow`, because the shot's variant is in a stronger layer stack than the asset's direct opinion
C. `winter`
D. A composition error

**R18-08** · Obj 1.7 · Select two.
Which are good reasons *not* to use a variant set?
A. The alternatives must change over the course of an animation.
B. There are three named, mutually exclusive looks.
C. Each of many instances needs a unique value.
D. The alternatives are versions of the same asset with the same interface.

**R18-09** · Obj 1.7 · Single choice
Fallbacks are `{"lod": ["medium", "low"]}`. A prim has `lod` variants `high` and `low`; the weakest sublayer selects `high`. What is used?
A. `medium` B. `low` C. `high` D. No variant

**R18-10** · Obj 1.7 · USDA reading
```usda
#usda 1.0

def "Bot" (
    variants = {
        string arm = "claw"
    }
    prepend variantSets = "arm"
)
{
    variantSet "arm" = {
        "claw" (
            prepend variantSets = "grip"
        ) {
            variantSet "grip" = {
                "soft" {
                    int force = 1
                }
            }
        }
        "drill" {
            int rpm = 3000
        }
    }
}
```
Which variant sets does `/Bot` report, and what is `force`?
A. `arm` and `grip`; `force` is 1
B. `arm` and `grip`; `force` has no value
C. Only `arm`; `force` is 1
D. Only `arm`; `force` has no value

**R18-11** · Obj 1.2 · Single choice
Eight instanceable prims reference the same asset. Four select `shape = a`, four select `shape = b`. How many prototypes does the stage create?
A. 1 B. 2 C. 4 D. 8

**R18-12** · Obj 1.6 · Single choice
Which LIVERPS position do variant opinions occupy relative to inherits and references?
A. Weaker than references, stronger than payloads
B. Stronger than inherits, weaker than local
C. Weaker than inherits, stronger than references
D. Weakest of all arcs

## Answers

### USDA reading exercises

**18-A.** `watts = 60`, `led = 1` (true). The direct `watts = 60` beats the `eco` variant's `watts = 9` (direct beats variant in the same layer stack). `led` has no direct opinion, so the selected `eco` variant supplies it.

**18-B.** `scale = 2`. The shot's selection `large` is stronger than the asset's `small`. With `string size = ""` in the shot, the empty selection is the strongest authored opinion and blocks the asset's `small`, so no authored selection applies. The fallback `small` then gives `scale = 0.5`. (If no fallback were set, there would be no `scale` at all.)

### Review questions

**R18-01 — B.** A few named, exclusive editions of one product. A is per-frame animation, C is per-instance continuous data (primvars), D is a layering problem (sublayers). Review: §18.5.

**R18-02 — B.** Within one layer stack, all direct opinions beat all variant opinions. Sublayer order only decides between opinions of the same kind. Review: §18.6.

**R18-03 — B, D.** Selections are metadata (no time samples), resolved by strength, and can target sets defined in a referenced asset. An unknown name is not an error. Review: §18.2, §18.6.

**R18-04 — B.** No variant was selected, so the variant edit target is invalid and the edit lands as a direct opinion, silently. Review: §18.2.

**R18-05 — B.** Fallbacks come from the process and must be set before opening. A changes assets; C does not affect an already-open stage; D only removes selections. Review: §18.4.

**R18-06 — B.** The asset's direct opinion beats the asset's own variant opinions (rule 4). The shot's selection does switch the variant, but the variant's `season` is weaker. Review: §18.6.

**R18-07 — B.** The shot's variant opinion sits in the shot layer stack, which is evaluated before the reference arc that brings in the asset (rule 3). Review: §18.6.

**R18-08 — A, C.** Selections cannot animate, and per-instance unique values belong in primvars or attributes. B and D describe good variant use. Review: §18.5.

**R18-09 — C.** Any authored selection, even in the weakest sublayer, beats fallbacks. Review: §18.4.

**R18-10 — B.** `claw` is selected, so the nested `grip` set exists. But no `grip` selection is authored (and no fallback is given), so the `soft` variant does not apply and `force` has no value. Review: §18.3, §18.4.

**R18-11 — B.** Instances that compose identically share a prototype; two distinct selections give two prototypes. Review: §18.5.

**R18-12 — C.** LIVERPS: Local, Inherits, Variants, rElocates, References, Payloads, Specializes. Review: §18.1, Chapter 21.

## Further reading

Optional. Everything needed for the exam is explained above.

- [S04] OpenUSD Glossary — entries "VariantSet", "Variant", "LIVERPS". https://openusd.org/release/glossary.html
- [S05] OpenUSD Tutorials — "Authoring Variants". https://openusd.org/release/tut_usd_tutorials.html
- [S06] OpenUSD API Reference — `UsdVariantSet`, `UsdVariantSets`, `UsdStage::SetGlobalVariantFallbacks`. https://openusd.org/release/api/index.html
- [S14] NVIDIA Learn OpenUSD — "Creating Composition Arcs" (variant sets). https://docs.nvidia.com/learn-openusd/latest/index.html
- [S16] Principles of Scalable Asset Structure in OpenUSD (variants in asset interfaces). https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
