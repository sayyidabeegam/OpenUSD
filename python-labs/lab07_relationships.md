# Lab 07 — Relationships and targets

**Domain / objectives:** Data Modeling 5.4 · **Chapter:** 5 · **Time:** 20 min · **Difficulty:** ★☆☆

## Goal
Author a **relationship** `looks` on `/A` targeting `/B`. Prove it is a relationship, not an attribute.

## Background
Relationships store **prim or property paths**, not numeric values. Material binding (`rel material:binding`, Ch 40) is the exam-facing relationship. `HasRelationship` / `HasAttribute` tell the two property kinds apart. `GetTargets()` returns `Sdf.Path` objects — print `str(t)` for a stable string (Ch 5).

## Steps
1. Run the script.
2. Targets list `['/B']`.
3. `HasAttribute looks` is False — the name is a relationship.

## Full script (identical to `lab07_relationships.py`)

```python
"""Lab 07 — Relationships and targets."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
a = UsdGeom.Xform.Define(stage, "/A").GetPrim()
UsdGeom.Xform.Define(stage, "/B")
rel = a.CreateRelationship("looks")
rel.AddTarget("/B")
print("targets:", [str(t) for t in rel.GetTargets()])
print("HasRelationship:", a.HasRelationship("looks"))
print("HasAttribute looks:", a.HasAttribute("looks"))
```

**Expected output**
```text
targets: ['/B']
HasRelationship: True
HasAttribute looks: False
```

## Check your understanding
1. Can a relationship hold `2.0`?
2. What API adds a second target?
3. Material binding uses which property kind?

**Answers**
1. **No.** Targets are paths. Use an attribute for numbers.
2. **`AddTarget`** again (list-op prepend/append on the spec).
3. A **relationship** (`material:binding`).

## Stretch challenge
`rel.AddTarget("/A")` then print targets. Solution: `['/B', '/A']` (order is authoring order unless you list-edit).
