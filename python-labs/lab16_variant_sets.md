# Lab 16 — Variant sets and `GetVariantEditContext`

**Domain / objectives:** Composition 1.7 · **Chapter:** 18 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Add a `size` variant set with **`small`** (height 1) and **`big`** (height 3). Select first, then author inside **`GetVariantEditContext()`**. List names with the **correct APIs**.

## Background
A variant set is opinions behind a named switch on one prim (Ch 18). **Select the variant, then** enter `with vset.GetVariantEditContext():`. If you skip selection, the edit target is invalid and opinions land as **direct** opinions that apply to every variant — no error. **`GetNames()`** is on **`Usd.VariantSets`** (the list of set names). **`GetVariantNames()`** is on **`Usd.VariantSet`** (the variants inside one set). `GetNames()` does not exist on `VariantSet`.

## Steps
1. `set names: ['size']` from `GetVariantSets().GetNames()`.
2. `variant names: ['big', 'small']` from `GetVariantNames()` (sorted, not insertion order).
3. Selection `small` → height `1.0`.
4. Selection `big` → height `3.0`. The last `SetVariantSelection` leaves selection `big`.

## Full script (identical to `lab16_variant_sets.py`)

```python
"""Lab 16 — Variant set authoring with GetVariantEditContext."""
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
box = UsdGeom.Cube.Define(stage, "/Box").GetPrim()
vset = box.GetVariantSets().AddVariantSet("size")
for name, h in [("small", 1.0), ("big", 3.0)]:
    vset.AddVariant(name)
    vset.SetVariantSelection(name)
    with vset.GetVariantEditContext():
        box.CreateAttribute("height", Sdf.ValueTypeNames.Double).Set(h)
print("set names:", box.GetVariantSets().GetNames())
print("variant names:", vset.GetVariantNames())
vset.SetVariantSelection("small")
print("small height:", box.GetAttribute("height").Get())
vset.SetVariantSelection("big")
print("big height:", box.GetAttribute("height").Get())
print("selection:", vset.GetVariantSelection())
```

**Expected output**
```text
set names: ['size']
variant names: ['big', 'small']
small height: 1.0
big height: 3.0
selection: big
```

## Check your understanding
1. What happens if you call `GetVariantEditContext()` with no selection?
2. Which object has `GetNames()` — `VariantSet` or `VariantSets`?
3. Why is `variant names` `['big', 'small']` even though `small` was added first?

**Answers**
1. Edits become **direct opinions** on the prim (every variant). No warning.
2. **`VariantSets`** (plural). On `VariantSet` use **`GetVariantNames()`**.
3. `GetVariantNames()` returns them **sorted**, not in insertion order.

## Stretch challenge
Add a third variant `medium` **without** calling `SetVariantSelection` first, then author height 2 inside the context. Solution: height 2 becomes a direct opinion and shows up for `small` and `big` too (Ch 18 trap).
