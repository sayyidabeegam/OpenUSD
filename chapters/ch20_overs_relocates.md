# Chapter 20 — Overs and Relocates

> **Exam domain:** Composition (23%) · **Objectives:** 1.8, 6.2 · **Study day:** 6 · **Est. time:** 90 min
> **Prerequisites:** Ch 4 (specifiers), Ch 14 (LIVERPS, prim index), Ch 15 (layer stacks), Ch 16 (references)

Chapter 4 taught `def`, `over`, and `class`. This chapter puts `over` to work on composed stages: how a shot layer overrides a referenced asset without defining a second copy, and how **relocates** move a prim that arrived through a weaker arc. Both topics sit on the exam's "why didn't my opinion take effect?" list (Obj 1.8 / 6.2).

## Learning goals

- Choose `over` rather than a typeless `def` when overlaying an existing prim.
- Override referenced children from the shot without editing the asset file.
- Explain why a lone `over` does not appear in `Traverse()`, and why an extra `over` child is not defined.
- Author relocates as layer metadata and predict the new namespace.
- Name the relocate limits that hide opinions (source-path edits, missing destination parent).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **`over`** | Specifier meaning "overlay": opinions here, but this spec does not define the prim. |
| **Typeless `def`** | A `def` with no schema type. It **does** define the prim. |
| **Composed specifier** | The specifier you read on the stage (`prim.GetSpecifier()`), after all specs combine. |
| **Local override** | An opinion in the local layer stack (L) on a prim that also has a reference (R). Local wins. |
| **Relocate** | Layer metadata that moves a composed prim from a source path to a destination path. |
| **Relocation source** | The old path. Opinions authored there after the relocate are ignored. |
| **Relocation destination** | The new path. Author overrides here. Descendants move with the prim. |
| **`Sdf.Layer.relocates`** | Python field: a list of `(source, target)` `Sdf.Path` pairs. |

---

## 20.1 `over` vs. typeless `def`

### 1. What is it?

An **`over`** is a prim spec that adds opinions without claiming "this prim exists because of me." A **typeless `def`** is a `def` with an empty type name. It looks similar in USDA — neither writes `Xform` or `Sphere` — but only the `def` defines the prim.

### 2. Why do we need it?

Shot layers, department layers, and material layers almost never own the asset. They need to change a color, a pose, or a radius on a prim that some other file `def`'d. If they also `def` that prim, they plant a second existence claim. If they `over` it, they add notes and leave existence to the asset.

### 3. Beginner explanation

Think of a **museum label next to a statue**. The statue (`def` in the asset) is the object. The label (`over` in the shot) can say "this one is on loan" without being a second statue. A typeless `def` is like building a blank pedestal and calling it the exhibit: something now exists there even if it has no type.

*Where the analogy breaks:* a stronger `over` still wins **values**. Specifiers are about existence, not about which number wins (Chapter 4.3, Chapter 14.2).

### 4. Technical explanation

Verified on USD 26.08:

| Authoring | USDA | Python | `IsDefined()` alone | In `Traverse()` alone |
|----------|------|--------|---------------------|------------------------|
| Overlay | `over "Hero" { … }` | `stage.OverridePrim("/Hero")` | **False** | **No** |
| Typeless define | `def "Hero" { … }` | `stage.DefinePrim("/Hero")` | **True** | **Yes** |
| Typed define | `def Sphere "Hero" { … }` | `stage.DefinePrim("/Hero", "Sphere")` | True | Yes |

- `prim.GetSpecifier()` on the **stage** is the composed specifier. A local `over` on top of a referenced `def` still reports `Sdf.SpecifierDef`, because a `def` somewhere in the prim stack defines it.
- `OverridePrim("/A/B")` authors `over "A"` for the missing parent as well (Chapter 4).
- `DefinePrim` on a path that already exists as a composed prim authors a `def` spec in the edit target. Prefer `over` in overlay layers so you do not accidentally define a prim that should only exist when the reference is present.
- An `over` child that **no** weaker layer defines is a valid prim (`GetPrimAtPath` works) but `IsDefined()` is False and `Traverse()` skips it. A `def` child in the same place is defined and is visited.

The NVIDIA reading list names this contrast as "over vs typeless def". Exam items love the look-alike USDA.

### 5. Mental model

```text
  def  = plant a flag  ("this prim exists")
  over = write on a flag that should already be there
  class = plant a flag in the templates drawer (abstract)

  Existence comes from any def (or class) in the prim stack.
  Values come from the strongest opinion, even if that opinion is an over.
```

### 6. Simple example

Open a file that contains only `over "Hero" { int hp = 10 }`. `/Hero` is not defined; `Traverse()` is empty. Change `over` to `def` and `/Hero` appears, still with no type name.

### 7. USDA example

*File: overlay.usda — an overlay alone does not define the prim*

```usda
#usda 1.0

over "Hero"
{
    int hp = 10
}
```

*File: typeless.usda — a typeless def does define the prim*

```usda
#usda 1.0

def "Hero"
{
    int hp = 10
}
```

Line notes: both files omit a type name. Only the specifier differs. `overlay.usda` opened as a stage is an empty traversal; `typeless.usda` yields `/Hero`.

### 8. Python example

```python
from pxr import Usd

stage = Usd.Stage.CreateInMemory()
hero = stage.OverridePrim("/Hero")
npc = stage.DefinePrim("/Npc")
print("Hero specifier/defined:", hero.GetSpecifier(), hero.IsDefined())
print("Npc specifier/defined:", npc.GetSpecifier(), npc.IsDefined())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
print("TraverseAll:", [str(p.GetPath()) for p in stage.TraverseAll()])
```

**Expected output**

```text
Hero specifier/defined: Sdf.SpecifierOver False
Npc specifier/defined: Sdf.SpecifierDef True
Traverse: ['/Npc']
TraverseAll: ['/Hero', '/Npc']
```

`TraverseAll()` visits undefined overs. Default `Traverse()` does not. That gap is a common "the prim vanished" report.

### 9. Real-world use case

A lighting department's `shot_lgt.usda` is a stack of `over` prims: lights that layout already `def`'d, plus `over "Chair_03"` to dim a practical lamp. Lighting never `def`s `/World/Chair_03`. If layout drops that chair, the lighting overs remain in the file but the prim is no longer defined, and the shot does not grow a ghost chair.

### 10. Common mistakes

> [!MISTAKE] Using `def "Hero"` in a shot "because it has no type, so it is soft." A typeless `def` still defines `/Hero`. If the reference is missing you get an empty but defined prim. Use `over`.

> [!MISTAKE] Opening an overlay-only layer in usdview and concluding the file is empty. The overs are there; nothing defines them. Open the composed stage (asset + overlay) instead.

### 11. Exam traps

> [!TRAP] "`over` is weaker than `def`." False for values. Strength is the layer stack and LIVERPS. Specifier is existence.

> [!TRAP] "Typeless prims are illegal." They are legal. The FAQ question is over versus *typeless def*, not typed versus typeless.

### 12. Practice questions

**COMP-020a** · Obj 1.8 · Difficulty: Easy · Type: Single choice
A layer contains only `over "Ball" { double radius = 2 }`. You open that layer as the root. Which is true?

A. `/Ball` is defined and `Traverse()` visits it
B. `/Ball` is not defined; `Traverse()` skips it
C. USD refuses to open the layer
D. `/Ball` becomes a class prim

**COMP-020b** · Obj 1.8 · Difficulty: Medium · Type: Single choice
A shot authors `def "Chair" ( prepend references = @chair.usda@ )`. `chair.usda` defines `Xform "Chair"`. What does `GetSpecifier()` return on the composed `/Chair`?

A. `Sdf.SpecifierOver`
B. `Sdf.SpecifierDef`
C. `Sdf.SpecifierClass`
D. Empty, because the shot's `def` is typeless

**Answers**

**COMP-020a — B.** An `over` alone does not define. Review: §20.1 (and Ch 4.3).

**COMP-020b — B.** The asset (and the shot) both `def` the prim. The composed specifier is `Def`. Typeless-ness of the shot spec does not erase the asset's `def`. Review: §20.1.

### 13. Exam takeaways

> [!KEY]
> - `over` overlays; `def` defines. Type name is a separate field.
> - Prefer `over` in shot and department layers.
> - `Traverse()` skips undefined overs; `TraverseAll()` does not.
> - Composed `GetSpecifier()` can be `Def` even when *this* layer wrote `over`.

---

## 20.2 Overriding referenced content

### 1. What is it?

**Overriding referenced content** means authoring local opinions on a prim that also has a reference (or payload) arc. The local opinions sit at **L** in LIVERPS, so they win over the asset's opinions at **R** (or **P**). The asset file is not edited.

### 2. Why do we need it?

You reuse one chair 40 times. Chair 7 must be larger. Chair 12 must hide its back. You do not fork `chair.usda` 40 times. You `over` the children on those copies in the shot.

### 3. Beginner explanation

The catalog page is the reference. A sticky note on *this* copy of the chair is the `over`. The sticky note wins for that copy only.

*Where the analogy breaks:* the sticky note is stored in **your** file, at the **composed path** (`/Room/Chair_B/Seat`), not inside the catalog. USD writes `over "Seat"` under the referencing prim. You never open `chair.usda`.

### 4. Technical explanation

- Setting an attribute on a composed child authors an `over` spec in the edit target automatically. You do not have to call `OverridePrim` first. `OverridePrim` alone, with no property, may write nothing.
- The nested USDA is:

  ```text
  def "Chair_B" ( prepend references = @./chair.usda@ )
  {
      over "Seat" { double size = 4 }
  }
  ```

- The composed specifier of `/Room/Chair_B/Seat` stays `Sdf.SpecifierDef` (the asset defined it). The spec in the *shot* is an `over`. `GetPrimStack()` shows both (Chapter 22).
- Local `over` can change attribute values, metadata (`active = false`), variant selections (Chapter 18), and can `def` **new** children that the asset does not have.
- An `over` child that the asset does not define is **not** defined. `Traverse()` will not visit it. If you mean to add a new prim, `def` it.
- `active = false` on a referenced child hides it from default traversal. The prim is still valid; `IsActive()` is False. This is a standard way to "remove" a part of an instance-unrelated asset (instanced components have extra rules: Chapter 22.4, Chapter 24).
- A **value block** (`double size = None`) stops weaker values from showing through. `Get()` returns `None`. Schema fallbacks can still make `HasValue()` True (Cube's fallback `size` is 2, for example). Blocking is stronger than "not authored."
- Strength: anything in the local layer stack, including these overs, is **L**. It beats inherits, variants, relocates, references, payloads, and specializes on that prim (Chapter 21).

> [!EXAM TIP] Obj 1.8 / 6.2: "I set a value and nothing changed." First question: did you author on the composed path in a layer that is actually in the local stack, or did you edit the asset / the relocate source / a muted layer / an instance proxy?

### 5. Mental model

```text
  chair.usda                         room.usda (local, stronger)
  def Xform "Chair"                  def "Chair_B" (references = @chair@)
      Seat.size = 1                      over "Seat" { size = 4 }   <-- wins
      Back.size = 2                      over "Back" (active = false)

  Composed /Room/Chair_B:
      Seat.size = 4
      Back exists but is inactive (Traverse skips it)
```

### 6. Simple example

Two referenced chairs. Only B's seat is enlarged. Only B's back is deactivated. Chair A still matches the asset.

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
    def Cube "Back"
    {
        double size = 2
    }
}
```

*File: room.usda*

```usda
#usda 1.0

def Xform "Room"
{
    def "Chair_A" (
        prepend references = @./chair.usda@
    )
    {
    }

    def "Chair_B" (
        prepend references = @./chair.usda@
    )
    {
        over "Seat"
        {
            double size = 4
        }
        over "Back" (
            active = false
        )
        {
        }
    }
}
```

Line notes: `Chair_A` has an empty body — it is a pure reference. `Chair_B` adds two nested overs. `active = false` is prim metadata in the spec's parentheses, not an attribute.

### 8. Python example

```python
from pxr import Usd

with open("chair.usda", "w") as f:
    f.write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair"
{
    def Cube "Seat"
    {
        double size = 1
    }
    def Cube "Back"
    {
        double size = 2
    }
}
""")

stage = Usd.Stage.CreateNew("room.usda")
for name in ("Chair_A", "Chair_B"):
    prim = stage.DefinePrim("/Room/" + name)
    prim.GetReferences().AddReference("./chair.usda")

seat_b = stage.GetPrimAtPath("/Room/Chair_B/Seat")
seat_b.GetAttribute("size").Set(4.0)
stage.GetPrimAtPath("/Room/Chair_B/Back").SetActive(False)

for path in ("/Room/Chair_A/Seat", "/Room/Chair_B/Seat"):
    prim = stage.GetPrimAtPath(path)
    print(path, "size =", prim.GetAttribute("size").Get(),
          "specifier =", prim.GetSpecifier())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
print(stage.GetRootLayer().ExportToString())
```

**Expected output**

```text
/Room/Chair_A/Seat size = 1.0 specifier = Sdf.SpecifierDef
/Room/Chair_B/Seat size = 4.0 specifier = Sdf.SpecifierDef
Traverse: ['/Room', '/Room/Chair_A', '/Room/Chair_A/Seat', '/Room/Chair_A/Back', '/Room/Chair_B', '/Room/Chair_B/Seat']
#usda 1.0

def "Room"
{
    def "Chair_A" (
        prepend references = @./chair.usda@
    )
    {
    }

    def "Chair_B" (
        prepend references = @./chair.usda@
    )
    {
        over "Seat"
        {
            double size = 4
        }

        over "Back" (
            active = false
        )
        {
        }
    }
}

```

`Set(4.0)` authored `over "Seat"` for you. Chair B's back is gone from `Traverse()` because it is inactive, not because it was deleted from the asset.

### 9. Real-world use case

A digital-twin factory references one `robot.usda` at twenty stations. Station 3's cell layer overs `/Cell/Robot/Gripper` to set a different payload mass and deactivates `/Cell/Robot/OptionalCamera`. Manufacturing still publishes one robot asset.

### 10. Common mistakes

> [!MISTAKE] Editing `chair.usda` to change one copy. Every copy changes. Fix: `over` the child on that copy's referencing prim.

> [!MISTAKE] Adding a new part with `over "Cushion"`. The cushion is not defined, so `Traverse()` and renderers skip it. `def` the new part.

> [!MISTAKE] Calling `OverridePrim("/Room/Chair_B/Seat")` and saving, then wondering why the layer did not change. With no property authored, USD may write no spec. Set a value (or metadata).

### 11. Exam traps

> [!TRAP] "The composed specifier of an overridden Seat is `Over`." It stays `Def` if the asset defined it. Look at `GetPrimStack()` for the shot's `over` spec.

> [!TRAP] "Local `over` is weaker than the reference because the asset `def`'d the prim." L is stronger than R. The specifier does not change LIVERPS.

### 12. Practice questions

**COMP-020c** · Obj 1.8 · Difficulty: Medium · Type: Single choice
`/Room/Chair_B` references `chair.usda`. The shot sets `/Room/Chair_B/Seat.size` to 4. Where is that 4 stored?

A. Inside `chair.usda`, replacing size 1
B. As `over "Seat"` under `Chair_B` in the shot layer
C. In the session layer only
D. As a payload on `Chair_B`

**COMP-020d** · Obj 1.8 · Difficulty: Medium · Type: Select two.
A referencing prim adds `over "Cushion" { double height = 0.2 }` and the asset has no Cushion. Which are true?

A. `GetPrimAtPath("…/Cushion")` is valid
B. `IsDefined()` is True
C. `Traverse()` visits Cushion
D. `TraverseAll()` visits Cushion

**Answers**

**COMP-020c — B.** Composition is non-destructive. The shot authors a nested `over`. Review: §20.2.

**COMP-020d — A and D.** An overlay-only child is valid but not defined, so default traversal skips it. Review: §20.1, §20.2.

### 13. Exam takeaways

> [!KEY]
> - Override referenced content with nested `over` at the composed path.
> - `Set` on a composed attribute authors that `over` for you.
> - Local L opinions beat the referenced asset.
> - New prims need `def`; `over` alone will not define them.
> - Deactivate a child with `over "Name" (active = false)`, not by editing the asset.

---

## 20.3 Relocates: what and why

### 1. What is it?

A **relocate** is layer metadata that says: "the prim that composition would have put at *source path* now lives at *destination path*." The prim and its descendants move. The source path becomes invalid. Relocates are the **E** (rElocates) in LIVERPS.

### 2. Why do we need it?

A referenced rig ships joints under `/Robot/Rig/Arm`. Your animation tools, constraints, or a client contract want `/Bot/Arm`. You must not edit the rig file (another department owns it; many shots reference it). A relocate in *your* layer moves the namespace for this composition only.

### 3. Beginner explanation

Think of **relabeling a folder without copying the files**. The catalog still stores `Rig/Arm`. Your scene's directory listing shows `Arm` next to `Rig`. Everyone who looks at your scene uses the new path.

*Where the analogy breaks:* the old path is not an alias. `/Bot/Rig/Arm` is **invalid** after the relocate. Relationships that still point at the old path do **not** retarget automatically (Section 20.4).

### 4. Technical explanation

- Authoring is **layer** metadata, not prim metadata:

  ```text
  (
      relocates = { </Bot/Rig/Arm>: </Bot/Arm> }
  )
  ```

- Python: `layer.relocates` is a **list of pairs**, not a dict. Each pair is `(Sdf.Path(source), Sdf.Path(dest))`. `layer.HasRelocates()` / `layer.ClearRelocates()` exist on USD 26.08. There is no `Usd.Prim` relocate API.
- Relocates apply to prims that arrive through **weaker composition** (typically a reference or payload in this layer stack). They are not a "rename this `def` I just wrote in the same layer" tool (Section 20.4).
- Descendants move with the prim: `/Bot/Rig/Arm/Hand` becomes `/Bot/Arm/Hand`.
- `Usd.PrimCompositionQuery` lists a `Pcp.ArcTypeRelocate` node on the destination. Target path of that arc is the source path.
- Flattening (`stage.Flatten()`) bakes the **new** namespace. The flattened layer has no `relocates` metadata and no `Rig/Arm`.
- Strength: E sits between VariantSets and References. Local opinions at the **destination** still beat the relocated content. Chapter 21 puts this in LIVERPS puzzles.

> [!VERSION] Verified on USD 26.08. Relocates as a composition arc landed in the USD 24.x series (authoring work in 24.05; composition in 24.08). `Usd.PrimCompositionQuery` reports relocate arcs (26.03+). Older material spells the strength order **LIVRPS** and omits E; the other six letters keep the same order.

### 5. Mental model

```text
  robot.usda                         scene.usda
  /Robot/Rig/Arm                     relocates { /Bot/Rig/Arm : /Bot/Arm }
       |                             def "Bot" (references = @robot@)
       |                                    |
       +---- composed, then moved --------> /Bot/Arm          (valid)
                                            /Bot/Rig          (empty of Arm)
                                            /Bot/Rig/Arm      (invalid)
```

### 6. Simple example

Reference a robot. Relocate `/Bot/Rig/Arm` to `/Bot/Arm`. Children of `/Bot` become `Rig` and `Arm`. `Rig` no longer contains `Arm`. `Hand` under `Arm` moved too.

### 7. USDA example

*File: robot.usda*

```usda
#usda 1.0
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
            def Sphere "Hand"
            {
                double radius = 0.2
            }
        }
    }
}
```

*File: scene.usda*

```usda
#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)

def Xform "Bot" (
    prepend references = @./robot.usda@
)
{
}
```

Line notes: `relocates` sits in the **layer** metadata block (the parentheses after `#usda 1.0`), beside `subLayers` and `defaultPrim`. Paths are wrapped in `<…>`. Several entries are separated by commas.

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
            def Sphere "Hand"
            {
                double radius = 0.2
            }
        }
    }
}
""")
write("scene.usda", """#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)
def Xform "Bot" (
    prepend references = @./robot.usda@
)
{
}
""")

stage = Usd.Stage.Open("scene.usda")
bot = stage.GetPrimAtPath("/Bot")
print("children of /Bot:", list(bot.GetChildrenNames()))
print("children of /Bot/Rig:",
      list(stage.GetPrimAtPath("/Bot/Rig").GetChildrenNames()))
arm = stage.GetPrimAtPath("/Bot/Arm")
print("/Bot/Arm length =", arm.GetAttribute("length").Get())
hand = stage.GetPrimAtPath("/Bot/Arm/Hand")
print("/Bot/Arm/Hand radius =", hand.GetAttribute("radius").Get())
print("/Bot/Rig/Arm valid:", stage.GetPrimAtPath("/Bot/Rig/Arm").IsValid())
print("layer.HasRelocates():", stage.GetRootLayer().HasRelocates())
print("layer.relocates:", stage.GetRootLayer().relocates)
for arc in Usd.PrimCompositionQuery(arm).GetCompositionArcs():
    print(f"{str(arc.GetArcType()):24}",
          arc.GetTargetLayer().GetDisplayName(), arc.GetTargetPrimPath())
```

**Expected output**

```text
children of /Bot: ['Rig', 'Arm']
children of /Bot/Rig: []
/Bot/Arm length = 1.0
/Bot/Arm/Hand radius = 0.2
/Bot/Rig/Arm valid: False
layer.HasRelocates(): True
layer.relocates: [(Sdf.Path('/Bot/Rig/Arm'), Sdf.Path('/Bot/Arm'))]
Pcp.ArcTypeRoot          scene.usda /Bot/Arm
Pcp.ArcTypeRelocate      scene.usda /Bot/Rig/Arm
Pcp.ArcTypeReference     robot.usda /Robot/Rig/Arm
```

The query lists L, then E, then R: local root, relocate, then the referenced spec that supplied `Arm`. Hand moved as a descendant; you did not relocate Hand separately.

### 9. Real-world use case

A game character pipeline references a vendor skeleton whose joints sit under `Root/Hips/Spine/…`. The studio's animation layer relocates `…/LeftHand` to `/Hero/Hand_L` so gameplay code and IK setups use a stable, short path. The vendor file is never forked.

### 10. Common mistakes

> [!MISTAKE] Writing `relocates` inside a prim's metadata parentheses. It is **layer** metadata at the top of the file.

> [!MISTAKE] Expecting `/Bot/Rig/Arm` to keep working as an alias. It is invalid. Update paths, constraints, and relationship targets to `/Bot/Arm`.

### 11. Exam traps

> [!TRAP] "Relocates are prim metadata like `references`." They are layer metadata, like `subLayers`.

> [!TRAP] "E is weaker than R, so the reference wins over the relocate." The relocate **moves** the referenced prim; it is not a second value that fights `length`. Local opinions at the destination still beat the relocated values.

### 12. Practice questions

**COMP-020e** · Obj 1.8 · Difficulty: Easy · Type: Single choice
Where do you author a relocate?

A. On the prim, next to `references`
B. In layer metadata: `relocates = { </old>: </new> }`
C. As an attribute `relocate:from`
D. Only in the session layer

**COMP-020f** · Obj 1.8 · Difficulty: Medium · Type: Single choice
After `relocates = { </Bot/Rig/Arm>: </Bot/Arm> }` on a referenced robot, which is true?

A. `/Bot/Rig/Arm` and `/Bot/Arm` are both valid aliases
B. `/Bot/Arm` is valid; `/Bot/Rig/Arm` is not
C. `/Bot/Arm` is valid only if you also `def` it
D. The relocate is ignored because references are stronger

**Answers**

**COMP-020e — B.** Layer metadata. Python stores a list of path pairs on `Sdf.Layer.relocates`. Review: §20.3.

**COMP-020f — B.** The source path is invalid; descendants live under the destination. Review: §20.3.

### 13. Exam takeaways

> [!KEY]
> - Relocates rename composed namespace without editing the referenced file.
> - Layer metadata, list of `(source, dest)` paths in Python.
> - Source path becomes invalid; children move with the prim.
> - E in LIVERPS, between variants and references.
> - `PrimCompositionQuery` shows `Pcp.ArcTypeRelocate`.

---

## 20.4 Relocates authoring and limitations

### 1. What is it?

This section is the **rules of the road**: how to author relocates in Python, where to put overrides after a move, and the limits that make an opinion disappear (Obj 1.8).

### 2. Why do we need it?

Most relocate bugs are not "USD forgot the move." They are "I authored at the old path," "the destination's parent does not exist," or "I tried to rename a local `def` with a relocate." The exam asks you to identify which of those happened.

### 3. Beginner explanation

After you relabel the folder, notes stuck to the **old** folder name are thrown away. Notes on the **new** folder name stick. You also cannot relabel a folder that only exists as a sticky note in the same drawer — relocates move content that arrived from somewhere weaker, such as a referenced catalog.

*Where the analogy breaks:* USD does not always raise. An opinion at the source becomes a composition error (`Pcp.ErrorOpinionAtRelocationSource`) and is ignored. A destination whose parent is missing can fail **silently**: `GetCompositionErrors()` may be empty and the prim simply never appears.

### 4. Technical explanation

Verified on USD 26.08:

**Authoring in Python.** Assign a list of tuples. A dict of strings is not accepted.
The next snippet is a fragment (no imports); the full script is in step 8.

```{.python .norun}
layer.relocates = [
    (Sdf.Path("/Bot/Rig/Arm"), Sdf.Path("/Bot/Arm")),
]
```

USDA still looks like a map. That spelling difference is an exam favorite.

**Overrides go at the destination.** Nested `over "Arm" { double length = 4 }` under `/Bot` wins. Nested `over "Rig" { over "Arm" { … } }` is an opinion at the source. USD warns, records `ErrorOpinionAtRelocationSource`, and keeps the referenced value.

**Relocates of local defs in the same layer.** If `/A/B` is `def`'d in the same layer that relocates `/A/B` → `/A/C`, the local spec sits at the source, so it is ignored. `/A/C` does not receive it. Use a reference (or a weaker sublayer) as the source of the prim you want to move, or just author the prim at the path you want.

**Destination parent.** Relocating to `/Missing/Arm` when `/Missing` does not exist yields an invalid destination. The prim index may still record the mapping; `GetCompositionErrors()` can still be empty. Create the parent (or relocate to a path whose parent already exists).

**Relationships.** A relationship authored as `rel driver = </Bot/Rig/Arm>` still reports that target after the relocate. USD does not rewrite it to `/Bot/Arm`. Update targets yourself.

**Where in the stack.** A relocate in any layer of the **local** layer stack applies. A weaker sublayer can hold the `relocates` map while a stronger layer overs the destination. Payloads relocate the same way as references once they are loaded.

**Not a delete tool.** An empty destination path `<>` is ill-formed. To hide a prim, deactivate it (`active = false`) or unload a payload (Chapter 17).

**Several relocates.** One layer may list many pairs. You can move `Arm` and `Head` in the same map.

### 5. Mental model

```text
  After relocates { /Bot/Rig/Arm : /Bot/Arm }:

  WRITE HERE              IGNORED (error)
  /Bot/Arm.length = 4     /Bot/Rig/Arm.length = 9

  Also ignored: a def of /Bot/Rig/Arm in the SAME layer as the relocate
  (that spec is at the source path).
```

### 6. Simple example

The same scene as 20.3, plus two overs: one at `/Bot/Arm` (length 4, wins) and one at `/Bot/Rig/Arm` (length 9, ignored, composition error).

### 7. USDA example

*File: scene_bad.usda* (uses `robot.usda` from 20.3)

```usda
#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)

def Xform "Bot" (
    prepend references = @./robot.usda@
)
{
    over "Rig"
    {
        over "Arm"
        {
            double length = 9
        }
    }
    over "Arm"
    {
        double length = 4
    }
}
```

Line notes: the `over "Arm"` directly under `Bot` is the destination. The `over "Arm"` under `Rig` is the source and will be ignored.

### 8. Python example

```python
from pxr import Sdf, Usd

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
write("scene_bad.usda", """#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)
def Xform "Bot" (
    prepend references = @./robot.usda@
)
{
    over "Rig"
    {
        over "Arm"
        {
            double length = 9
        }
    }
    over "Arm"
    {
        double length = 4
    }
}
""")

stage = Usd.Stage.Open("scene_bad.usda")
print("length at /Bot/Arm:",
      stage.GetPrimAtPath("/Bot/Arm").GetAttribute("length").Get())
print("errors:")
for err in stage.GetCompositionErrors():
    print(" ", type(err).__name__)

layer = Sdf.Layer.CreateAnonymous(".usda")
layer.relocates = [
    (Sdf.Path("/Bot/Rig/Arm"), Sdf.Path("/Bot/Arm")),
]
print("Python relocates:", layer.relocates)
print("HasRelocates:", layer.HasRelocates())
print(layer.ExportToString())
layer.ClearRelocates()
print("after ClearRelocates:", layer.relocates, layer.HasRelocates())
```

**Expected output**

```text
length at /Bot/Arm: 4.0
errors:
  ErrorOpinionAtRelocationSource
Python relocates: [(Sdf.Path('/Bot/Rig/Arm'), Sdf.Path('/Bot/Arm'))]
HasRelocates: True
#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)


after ClearRelocates: [] False
```

The warning on stderr (not shown above) matches the error: the source-path opinion is ignored. Length 4 from the destination `over` wins. Assigning `layer.relocates = { "/Bot/Rig/Arm": "/Bot/Arm" }` (a dict of strings) raises `TypeError` on 26.08.

### 9. Real-world use case

A manufacturing digital twin references a vendor robot and relocates flange frames to `/Cell/TCP`. The cell's animation layer overs `/Cell/TCP` to key the tool pose. A new artist who keys `/Cell/Robot/Rig/Flange` instead sees no motion and a composition error — the classic Obj 1.8 relocate bug.

### 10. Common mistakes

> [!MISTAKE] Assigning a Python `dict` to `layer.relocates`. Use a list of `(Sdf.Path, Sdf.Path)` tuples.

> [!MISTAKE] Relocating a prim `def`'d in the same layer, then wondering why the destination is empty. The `def` is an opinion at the source, so it is thrown away. Reference the prim, or author it at the destination to begin with.

> [!MISTAKE] Relocating to `/NewRoot/Arm` without defining `/NewRoot`. The destination prim never appears; check `GetPrimAtPath` rather than assuming an error list.

### 11. Exam traps

> [!TRAP] "The source-path `over` is weaker, so the destination `over` wins, but both apply." The source-path opinion does not apply at all.

> [!TRAP] "Relationships to the old path follow the relocate." They do not. `GetTargets()` still returns the old path.

### 12. Practice questions

**COMP-020g** · Obj 1.8 · Difficulty: Medium · Type: Single choice
A layer relocates `/Bot/Rig/Arm` to `/Bot/Arm` and also authors `over "Rig" { over "Arm" { double length = 9 } }`. The referenced arm has `length = 1`. What is composed `/Bot/Arm.length`?

A. 9
B. 1, and `GetCompositionErrors()` includes `ErrorOpinionAtRelocationSource`
C. 1, with no composition error
D. The stage fails to open

**COMP-020h** · Obj 6.2 · Difficulty: Medium · Type: Select two.
Which situations make a relocate look like it "did nothing"?

A. The destination's parent prim does not exist
B. You authored the override at the source path
C. You used `prepend relocates` on the prim
D. The referenced file uses USDA instead of USDC

**Answers**

**COMP-020g — B.** Source-path opinions are ignored and reported. Review: §20.4.

**COMP-020h — A and B.** There is no `prepend relocates` prim field (C). File format does not matter (D). Review: §20.4.

### 13. Exam takeaways

> [!KEY]
> - Python: list of `(Sdf.Path, Sdf.Path)` pairs; USDA: a map in layer metadata.
> - Author overrides at the **destination** path.
> - Source-path opinions → `ErrorOpinionAtRelocationSource`, ignored.
> - Destination parent must exist; missing parent can fail silently.
> - Relationships do not retarget. Relocates do not rename local defs in the same layer.

---

## Chapter lab(s)

There is no dedicated lab number for this chapter. Lab 13 (references) already authors nested overs. Lab 20 (LIVERPS) includes a relocate. Lab 21 (introspection) prints `GetPrimStack` for an `over` on a referenced child.

## USDA reading exercises

**Exercise 20-A.** `prop.usda` defines `def Xform "Prop" { def Cube "Lid" { double size = 1 } }`. A shot contains:

```usda
#usda 1.0

def "P" (
    prepend references = @./prop.usda@
)
{
    over "Lid"
    {
        double size = 3
    }
    over "Tag"
    {
        string label = "hot"
    }
}
```

What is `/P/Lid.size`? Is `/P/Tag` defined? Which prims does `Traverse()` visit?

**Exercise 20-B.** Using `robot.usda` from Section 20.3, the shot's layer metadata is `relocates = { </Hero/Rig/Arm>: </Hero/Arm> }` and the shot `def`s `/Hero` with a reference to `robot.usda`. An animator sets `/Hero/Rig/Arm.length = 8`. What is `/Hero/Arm.length`, and why?

**Answers**

**20-A.** `size = 3` (local over beats the referenced 1). `/P/Tag` is not defined (overlay-only child). `Traverse()` visits `/P` and `/P/Lid` only. Verified by composing the files.

**20-B.** `length` stays `1` (the referenced value). The animator's opinion is at the relocation **source**, so USD ignores it and records `ErrorOpinionAtRelocationSource`. The animator should set `/Hero/Arm.length`. Review: §20.4.

---

## Chapter review

### Summary

- `over` adds opinions without defining; a typeless `def` defines. Prefer `over` in overlay layers.
- `Traverse()` skips undefined overs; `TraverseAll()` lists them.
- Nested `over` under a referencing prim overrides that copy only; the asset is unchanged.
- `Set` on a composed child authors the nested `over` for you. Composed `GetSpecifier()` can still be `Def`.
- New children need `def`. Deactivate existing children with `active = false`.
- Relocates are layer metadata mapping source → destination; Python uses a list of path pairs.
- After a relocate the source path is invalid; descendants move; overrides go at the destination.
- Source-path opinions are ignored (`ErrorOpinionAtRelocationSource`). Missing destination parents can fail silently.
- Relationships do not follow relocates. Relocates are the E in LIVERPS.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `over "X"` in a shot | Overlay; existence comes from a `def` elsewhere |
| Typeless `def "X"` in a shot | This **defines** X, even with no type |
| Prim missing from `Traverse()` but valid | Undefined `over`, inactive, abstract, or unloaded |
| Nested `over "Seat"` under a reference | Local L override of that copy |
| `relocates = { </old>: </new> }` | Layer metadata; E in LIVERPS |
| `/old` invalid after a move | Expected; use `/new` |
| `ErrorOpinionAtRelocationSource` | You authored at the old path |
| Relocate "did nothing" | Missing dest parent, or source was a local `def` |
| `layer.relocates = { "a": "b" }` | TypeError; use a list of `Sdf.Path` pairs |

### Review questions

**R20-01** · Obj 1.8 · Single choice
What is the difference between `over "Hero"` and `def "Hero"` in a layer opened by itself?

A. None; both define a typeless prim
B. `over` does not define; `def` does
C. `over` is weaker for values
D. `def` is illegal without a type

**R20-02** · Obj 1.8 · Single choice
A shot `over`s a referenced Cube's `size`. What is the composed specifier of that Cube?

A. `Sdf.SpecifierOver`
B. `Sdf.SpecifierDef`
C. `Sdf.SpecifierClass`
D. Undefined

**R20-03** · Obj 1.8 · Single choice
Which USDA hides a referenced child without editing the asset?

A. `delete "Back"`
B. `over "Back" (active = false) {}`
C. `over "Back" { double size = 0 }`
D. `class "Back" {}`

**R20-04** · Obj 1.8 · Select two.
You want a new locator under a referenced lamp. Which authors a defined child?

A. `over "Locator" {}`
B. `def Xform "Locator" {}`
C. `def "Locator" {}`
D. `class "Locator" {}`

**R20-05** · Obj 1.8 · Single choice
Where must `relocates` be authored?

A. Prim metadata on the moved prim
B. Layer metadata of a layer in the local stack
C. Attribute `xformOp:relocate`
D. Only inside the referenced file

**R20-06** · Obj 1.8 · Single choice
After relocating `/Bot/Rig/Arm` to `/Bot/Arm`, `GetPrimAtPath("/Bot/Rig/Arm")` returns:

A. A valid alias of `/Bot/Arm`
B. An invalid prim
C. The `Rig` prim
D. A class prim

**R20-07** · Obj 6.2 · Single choice
Which Python assignment is correct on USD 26.08?

A. `layer.relocates = {"/A": "/B"}`
B. `layer.relocates = [(Sdf.Path("/A"), Sdf.Path("/B"))]`
C. `prim.GetRelocates().Add("/A", "/B")`
D. `layer.SetRelocate("/A", "/B")`

**R20-08** · Obj 6.2 · USDA reading
`robot.usda` defines `/Robot/Rig/Arm` with `length = 1`. The shot relocates that arm to `/Bot/Arm` and authors `over "Arm" { double length = 4 }` under `/Bot`. What is `/Bot/Arm.length`?

A. 1 · B. 4 · C. 5 · D. no value

**R20-09** · Obj 6.2 · Single choice
A relationship on `/Bot` still targets `</Bot/Rig/Arm>` after that path was relocated to `/Bot/Arm`. `GetTargets()` returns:

A. `[/Bot/Arm]` automatically
B. `[/Bot/Rig/Arm]`
C. An empty list
D. A composition error and no targets

**R20-10** · Obj 1.8 · Select two.
Which are valid reasons a local opinion does not show up on a composed prim (Obj 1.8)?

A. It was authored at a relocation source path
B. It is an `over` on a child that nothing `def`s, and you looked at `Traverse()`
C. USDA was used instead of USDC
D. The opinion is in the session layer

**R20-11** · Obj 6.2 · Single choice
You relocate `/A/B` to `/A/C` in the same layer that `def`s `/A/B`. What happens?

A. `/A/C` becomes a copy of `/A/B`
B. The local `def` is ignored (source-path opinion); `/A/C` does not receive it
C. USD raises at parse time
D. Both paths remain valid aliases

**R20-12** · Obj 1.8 · Single choice
LIVERPS: relocates (E) sit immediately:

A. Before Local
B. Between VariantSets and References
C. After Specializes
D. Between Payloads and Specializes

### Review answers

**R20-01 — B.** Specifier is existence. Review: §20.1.

**R20-02 — B.** The asset `def`'d the Cube; composed specifier stays Def. Review: §20.2.

**R20-03 — B.** Deactivate with metadata on an `over`. Review: §20.2.

**R20-04 — B and C.** Either `def` defines the child (typed or typeless). `over` does not; `class` is abstract. Review: §20.1, §20.2.

**R20-05 — B.** Layer metadata. Review: §20.3.

**R20-06 — B.** Source path is invalid. Review: §20.3.

**R20-07 — B.** List of `Sdf.Path` pairs. No prim API (C, D). Dict of strings fails (A). Review: §20.4.

**R20-08 — B.** Destination `over` is local and wins. Review: §20.3, §20.4.

**R20-09 — B.** Targets are not rewritten. Review: §20.4.

**R20-10 — A and B.** Session-layer opinions *do* take effect (they are strongest local). File format is irrelevant. Review: §20.1, §20.4.

**R20-11 — B.** Relocates are not a local rename. Review: §20.4.

**R20-12 — B.** L I V **E** R P S. Review: §20.3.

## Further reading

- [S04] OpenUSD Glossary — "Specifier", "overs", "LIVERPS Strength Ordering", "Relocates": https://openusd.org/release/glossary.html
- [S08] USD FAQ — "over vs. typeless def": https://openusd.org/release/usdfaq.html
- [S06] OpenUSD API — `UsdStage::OverridePrim`, `SdfLayer::GetRelocates`, `UsdPrimCompositionQuery`: https://openusd.org/release/api/index.html
- [S14] NVIDIA Learn OpenUSD — Composition arcs: https://docs.nvidia.com/learn-openusd/latest/index.html
