# USDA reading exercises

**Original exercises.** Not NVIDIA exam content. Each item shows one or more USDA files, then a composed-value / existence question. Answers are at the end. Verified by opening the layers with `usd-core` 26.8.

Target: 30. This file currently holds **U-001–U-030** (complete).

One-line `{ double x = 1 }` bodies **do not parse** — every file here is multiline.

---

### U-001 · Sublayer strength · Obj 1.5

File: `strong.usda`

```usda
#usda 1.0
over "Ball"
{
    double radius = 3
}
```

File: `weak.usda`

```usda
#usda 1.0
over "Ball"
{
    double radius = 7
}
```

File: `root.usda`

```usda
#usda 1.0
(
    subLayers = [
        @./strong.usda@,
        @./weak.usda@
    ]
)
def Sphere "Ball"
{
}
```

**Question:** What is composed `/Ball.radius`?

---

### U-002 · Inherit vs reference · Obj 1.1

File: `asset.usda`

```usda
#usda 1.0
(
    defaultPrim = "X"
)
def Sphere "X"
{
    double radius = 1
}
```

File: `shot.usda`

```usda
#usda 1.0
class "_I"
{
    double radius = 3
}

def "Ball" (
    prepend inherits = </_I>
    prepend references = @asset.usda@
)
{
}
```

**Question:** What is composed `/Ball.radius`?

---

### U-003 · Local vs variant · Obj 1.8

```usda
#usda 1.0
def "Asset" (
    prepend variantSets = "size"
    variants = {
        string size = "big"
    }
)
{
    double height = 1
    variantSet "size" = {
        "big" {
            double height = 3
        }
    }
}
```

**Question:** Selection is `big`. Composed `height`?

---

### U-004 · `over` alone · Obj 1.8

```usda
#usda 1.0
over "Hero"
{
    int hp = 10
}
```

**Question:** Is `/Hero` defined? Does `Traverse()` list it?

---

### U-005 · Missing `defaultPrim` · Obj 1.3

File: `nodefault.usda`

```usda
#usda 1.0
def Cube "Box"
{
    double size = 9
}
```

Python: `prim.GetReferences().AddReference("nodefault.usda")` (no explicit path).

**Question:** Composed type name of `prim`, and composition error family?

---

### U-006 · Layer offset samples · Obj 1.4

File: `anim.usda`

```usda
#usda 1.0
(
    defaultPrim = "Ball"
)
def Xform "Ball"
{
    double tx.timeSamples = {
        0: 0,
        10: 10,
    }
}
```

File: `shot.usda`

```usda
#usda 1.0
def "B" (
    prepend references = @anim.usda@ (
        offset = 10
    )
)
{
}
```

**Question:** Composed `tx` time-sample times on `/B`?

---

### U-007 · `LoadNone` · Obj 1.3

File: `hi.usda`

```usda
#usda 1.0
(
    defaultPrim = "Root"
)
def Xform "Root"
{
    def Cube "Hi"
    {
    }
}
```

File: `city.usda`

```usda
#usda 1.0
def Xform "W"
{
    def Xform "A" (
        prepend payload = @./hi.usda@
    )
    {
    }
    def Xform "C" (
        prepend references = @./hi.usda@
    )
    {
    }
}
```

Opened with `Usd.Stage.Open("city.usda", Usd.Stage.LoadNone)`.

**Question:** Does `/W/C/Hi` exist? Does `/W/A/Hi` exist?

---

### U-008 · Reference vs specialize · Obj 1.6

```usda
#usda 1.0
def Sphere "Asset"
{
    double radius = 1
}

def "_S"
{
    double radius = 7
}

def "Ball" (
    prepend references = </Asset>
    prepend specializes = </_S>
)
{
}
```

**Question:** Composed `/Ball.radius`?

---

### U-009 · Mute · Obj 1.8 / 6.2

Same files as U-001. After `stage.MuteLayer(strongIdentifier)`:

**Question:** Composed `/Ball.radius`?

---

### U-010 · Inherit broadcast · Obj 1.1

```usda
#usda 1.0
class "_Look"
{
    float roughness = 0.2
}

def "A" (
    prepend inherits = </_Look>
)
{
    float roughness = 0.9
}

def "B" (
    prepend inherits = </_Look>
)
{
}
```

**Question:** Composed `/A.roughness` and `/B.roughness`?

---

### U-011 · Prepend vs append references · Obj 1.1

File: `r1.usda` — Sphere `radius = 2` with `defaultPrim = "X"`.  
File: `r2.usda` — Sphere `radius = 8` with `defaultPrim = "X"`.

```usda
#usda 1.0
def "P" (
    prepend references = @r1.usda@
    append references = @r2.usda@
)
{
}
```

**Question:** Composed `/P.radius`?

---

### U-012 · Inherit vs variant · Obj 1.1 / 1.6

```usda
#usda 1.0
class "_I"
{
    double radius = 3
}

def Sphere "Ball" (
    prepend inherits = </_I>
    prepend variantSets = "look"
    variants = {
        string look = "hi"
    }
)
{
    variantSet "look" = {
        "hi" {
            double radius = 10
        }
    }
}
```

**Question:** Composed `/Ball.radius`?

---

### U-013 · Three sublayers · Obj 1.5

`l1`/`l2`/`l3` author `radius` 1, 2, 3. Root:

```usda
#usda 1.0
(
    subLayers = [
        @./l1.usda@,
        @./l2.usda@,
        @./l3.usda@
    ]
)
def Sphere "Ball"
{
}
```

**Question:** Composed radius?

---

### U-014 · Explicit reference path · Obj 1.3

File: `ex.usda` has `def Cube "Only" { double size = 1 }` and **no** `defaultPrim`.

```usda
#usda 1.0
def "P" (
    prepend references = @ex.usda@</Only>
)
{
}
```

**Question:** Composed type and `size` of `/P`?

---

### U-015 · Stronger default vs weaker samples · Obj 1.8

Stronger sublayer: `double radius = 5`.  
Weaker sublayer: samples `{ 0: 0, 10: 10 }`.

**Question:** `Get()`, `Get(10)`, and `GetTimeSamples()`?

---

### U-016 · Nested `over` under `instanceable` · Obj 1.10 / 2.5

File: `chair.usda` — `defaultPrim = "Chair"`, Cube `/Chair/Seat` `size = 1`.

```usda
#usda 1.0
def Xform "Room"
{
    def "A" (
        prepend references = @chair.usda@
        instanceable = true
    )
    {
        over "Seat"
        {
            double size = 9
        }
    }
}
```

**Question:** Composed `/Room/A/Seat.size`? Does default `Traverse()` list `/Room/A/Seat`?

---

### U-017 · Variant with no selection · Obj 1.7

```usda
#usda 1.0
def "Asset" (
    prepend variantSets = "size"
)
{
    variantSet "size" = {
        "big" {
            double height = 3
        }
        "small" {
            double height = 1
        }
    }
}
```

**Question:** Composed `height` with no selection authored?

---

### U-018 · Layer offset with scale · Obj 1.4

Asset samples at layer times 0 and 10. Reference `Sdf.LayerOffset(10, 2)` (offset 10, scale 2).

**Question:** Composed sample times?

---

### U-019 · `delete` list-op · Obj 1.1

Weaker layer: `prepend references = [@r1.usda@, @r2.usda@]` (radii 2 and 8).  
Stronger: `delete references = [@r1.usda@]`.

**Question:** Composed radius?

---

### U-020 · Relationship list-edit · Obj 1.6

Weaker: `rel looks = </MatA>`. Stronger sublayer: `prepend rel looks = </MatB>`.

**Question:** Composed `looks` targets (strongest first)?

---

### U-021 · Implied inherits · Obj 1.1

Asset `Char` inherits `/_Look` with `roughness = 0.2`. Shot:

```usda
#usda 1.0
class "_Look"
{
    float roughness = 0.9
}

def "Hero" (
    prepend references = @char.usda@
)
{
}
```

**Question:** Composed `/Hero.roughness`?

---

### U-022 · Relocates · Obj 1.8

Asset `/Bot/Rig/Arm` Sphere `radius = 1`. Shot:

```usda
#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)
def "Bot" (
    prepend references = @./bot.usda@
)
{
    over "Rig"
    {
        over "Arm"
        {
            double radius = 9
        }
    }
    over "Arm"
    {
        double radius = 3
    }
}
```

**Question:** Does `/Bot/Rig/Arm` exist? `/Bot/Arm.radius`?

---

### U-023 · Broken model chain · Obj 2.4

```usda
#usda 1.0
def Xform "Kitchen" (
    kind = "assembly"
)
{
    def Xform "Clutter"
    {
        def Xform "Mug" (
            kind = "component"
        )
        {
        }
    }
    def Xform "Props" (
        kind = "group"
    )
    {
        def Xform "Chair" (
            kind = "component"
        )
        {
        }
    }
}
```

**Question:** `Mug.GetKind()` / `IsComponent()`? `Chair.IsComponent()`?

---

### U-024 · Explicit `references` list · Obj 1.1

Weaker prepends `r1` then `r2`. Stronger authors `references = [@r2.usda@]` (explicit, no prepend).

**Question:** Composed radius (r1=2, r2=8)?

---

### U-025 · Bind without Apply (USDA) · Obj 8.3

```usda
#usda 1.0
def Mesh "Board"
{
    rel material:binding = </Looks/Paint>
}

def Xform "Looks"
{
    def Material "Paint"
    {
    }
}
```

**Question:** `HasRelationship("material:binding")`? `HasAPI(MaterialBindingAPI)`?

---

### U-026 · Local vs inherit · Obj 1.1

```usda
#usda 1.0
class "_I"
{
    double radius = 3
}

def Sphere "Ball" (
    prepend inherits = </_I>
)
{
    double radius = 1
}
```

**Question:** Composed radius?

---

### U-027 · Schema fallback in USDA · Obj 5.2

```usda
#usda 1.0
def Sphere "S"
{
}
```

**Question:** Composed `radius` (nothing authored)?

---

### U-028 · `defaultPrim` present · Obj 1.3

Contrast U-005. File `box.usda`:

```usda
#usda 1.0
(
    defaultPrim = "Box"
)
def Cube "Box"
{
    double size = 9
}
```

`AddReference("box.usda")` with no path.

**Question:** Type and `size`?

---

### U-029 · Imageable purpose · Obj 5.5 / 6.4

```usda
#usda 1.0
def Mesh "M"
{
    uniform token purpose = "guide"
}
```

**Question:** Authored `purpose`? Why might it vanish in the default usdview pass?

---

### U-030 · Typeless `def` vs `over` · Obj 1.8

File A is U-004 (`over "Hero"`). File B:

```usda
#usda 1.0
def "Hero"
{
    int hp = 10
}
```

**Question:** For B, is `/Hero` defined and in `Traverse()`? Type name?

---

## Answers

**U-001 — 3.** First listed sublayer (`strong.usda`) wins over `weak` (7) and over the unauthored Sphere fallback. Resolution: local stack, first sublayer. Review: §15.1.

**U-002 — 3.** Inherits beat references (I before R). Review: §21.2, lab 18.

**U-003 — 1.** Local `height = 1` is L; variant `3` is V; L beats V even when `size = big`. Review: §18.6.

**U-004 — Not defined; Traverse empty.** `over` overlays; it does not define. `GetPrimAtPath` still returns a handle. Review: §20.1.

**U-005 — Type `''`; `Pcp.ErrorType_UnresolvedPrimPath`.** `AddReference` returns True. Missing `defaultPrim` is not `InvalidAssetPath` (that is a missing *file*). Review: §16.2, lab 14.

**U-006 — `[10.0, 20.0]`.** `stageTime = offset + scale * layerTime` with offset 10, scale 1. Review: §16.4.

**U-007 — `/W/C/Hi` True (reference still loads); `/W/A/Hi` False (payload unloaded).** Review: §17.2, lab 16.

**U-008 — 1.** References beat specializes. Review: §19.3.

**U-009 — 7.** Muting `strong.usda` drops it from the stack; `weak` 7 remains. Review: §15.4.

**U-010 — A `0.9`, B `0.2`.** Local on A does not change B; B still inherits the class. Review: §19.2, lab 18.

**U-011 — 2.** Prepend (`r1`) is stronger than append (`r2`). Review: §14.4.

**U-012 — 3.** Inherits beat the selected variant’s `10`. Review: §21.2.

**U-013 — 1.** First listed sublayer wins. Review: §15.1.

**U-014 — `Cube`, `size` 1.** Explicit `</Only>` does not need `defaultPrim`. Review: §16.2.

**U-015 — `Get()`/`Get(10)` = 5; samples `[]`.** Stronger default wins at every time. Review: §21.3.

**U-016 — `size` 1.0; Traverse is `['/Room', '/Room/A']` (no Seat).** Nested over on a proxy is ignored; proxies are skipped. Review: lab 23.

**U-017 — `None` (attribute not composed).** No selection → variant opinions off. Review: §18.2.

**U-018 — `[10.0, 30.0]`.** `10 + 2 * {0, 10}`. Review: §16.4.

**U-019 — 8.** Delete removes `r1`; `r2` remains. Review: §14.4.

**U-020 — `['/MatB', '/MatA']`.** List-ops compose; prepend is stronger. Review: §14.4.

**U-021 — ~0.9.** Shot `class "_Look"` contributes via implied inherits. Review: §19.5.

**U-022 — `/Bot/Rig/Arm` does not exist; `/Bot/Arm.radius` is 3.** Source-path over (`9`) is ignored (Pcp warning). Review: §20.3.

**U-023 — Mug kind `component` but `IsComponent`/`IsModel` False; Chair True/True.** Un-kinded `Clutter` breaks the model chain. Review: lab 22.

**U-024 — 8.** Explicit list replaces weaker prepends. Review: §14.4.

**U-025 — Rel True; HasAPI False.** Bind-without-Apply in USDA. Review: lab 34.

**U-026 — 1.** Local beats inherit. Review: §19.2.

**U-027 — 1.0.** Sphere schema fallback. Review: §13.1.

**U-028 — `Cube`, `size` 9.** `defaultPrim` supplies the target. Review: §16.2.

**U-029 — `guide`.** Default purpose mask omits `guide`/`proxy`. Review: §13.5.

**U-030 — Defined, in Traverse, type `''` (typeless).** `def` without a type still defines. Review: §20.1.

---

*USDA reading exercises complete: U-001–U-030 (target 30).*

