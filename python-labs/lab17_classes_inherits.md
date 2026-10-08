# Lab 17 — Classes, inherits, and a local override

**Domain / objectives:** Composition 1.1, 1.6 · **Chapter:** 19 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Create a **`class`** prim, inherit it on `/A` and `/B`, **broadcast** one edit, then author a **local** value on `/A` that `/B` does not pick up. Print inherit paths as strings.

## Background
A **`class`** (`CreateClassPrim`) is abstract: `IsAbstract()` is True and **`Traverse()` skips it**; **`TraverseAll()`** includes it (Ch 19). An **inherits** arc is a live link — later edits to the class reach every inheritor. **Local** opinions beat inherits (L before I in LIVERPS). `GetAllDirectInherits()` returns `Sdf.Path` objects; print `str(p)` for stable output.

## Steps
1. Both start at size `2.0` from `/_Look`.
2. One `Set(5)` on the class broadcasts: A and B become `5.0`.
3. Local `Set(9)` on `/A` only: A is `9.0`, B stays `5.0`.
4. Direct inherits: `['/_Look']`.
5. `/A` is not abstract; `/_Look` is. `Traverse` lists `A, B`; `TraverseAll` lists `_Look, A, B`.

## Full script (identical to `lab17_classes_inherits.py`)

```python
"""Lab 17 — Class prims, inherit broadcast, local override."""
from pxr import Sdf, Usd

stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_Look")
cls.CreateAttribute("size", Sdf.ValueTypeNames.Double).Set(2)
a = stage.DefinePrim("/A", "Xform")
b = stage.DefinePrim("/B", "Xform")
a.GetInherits().AddInherit("/_Look")
b.GetInherits().AddInherit("/_Look")
print("before A/B:", a.GetAttribute("size").Get(),
      b.GetAttribute("size").Get())
cls.GetAttribute("size").Set(5)
print("after broadcast A/B:", a.GetAttribute("size").Get(),
      b.GetAttribute("size").Get())
a.GetAttribute("size").Set(9)
print("local A, B stays:", a.GetAttribute("size").Get(),
      b.GetAttribute("size").Get())
print("direct inherits:",
      [str(p) for p in a.GetInherits().GetAllDirectInherits()])
print("A abstract?:", a.IsAbstract(), "class abstract?:", cls.IsAbstract())
print("Traverse:", [p.GetName() for p in stage.Traverse()])
print("TraverseAll:", [p.GetName() for p in stage.TraverseAll()])
```

**Expected output**
```text
before A/B: 2.0 2.0
after broadcast A/B: 5.0 5.0
local A, B stays: 9.0 5.0
direct inherits: ['/_Look']
A abstract?: False class abstract?: True
Traverse: ['A', 'B']
TraverseAll: ['_Look', 'A', 'B']
```

## Check your understanding
1. Does editing the class copy values once, or stay live?
2. Why is `/_Look` missing from `Traverse()`?
3. Can a local opinion on `/A` be weaker than the class?

**Answers**
1. **Live.** The next `Set` on the class updates every inheritor that has no stronger opinion.
2. It is **abstract**. Default traversal skips `Usd.PrimIsAbstract`.
3. **No.** Local (L) beats inherits (I).

## Stretch challenge
`a.GetAttribute("size").Clear()` after the local 9. Solution: `/A` returns to `5.0` (the class) because the local opinion is gone; `/B` is unchanged.
