# Lab 10 — Time samples, `Get()` vs `Get(t)`, linear vs held

**Domain / objectives:** Data Modeling 5.2 · Composition 1.4 · **Chapter:** 10 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Author two translate samples, prove that **`Get()` with no time is `None`** when there is no default, then compare **linear** interpolation at the midpoint with **held**.

## Background
A still photograph is the **default** (`Get()` / `TimeCode.Default()`). A flip-book is **time samples**. Numeric queries **ignore the default**; they only look at samples (Ch 10). Translate ops have **no schema fallback**, so `Get()` is `None` until you author a default. Stage interpolation starts as **linear** (`Usd.InterpolationTypeLinear`). Held keeps the **previous** sample.

Print `Gf.Vec3d` as `tuple(...)` so the output is plain numbers, not a type name.

## Steps
1. Run the script. `Get(): None` — samples are not a default.
2. `Get(1)` is the first key `(0.0, 0.0, 0.0)`.
3. Midpoint `Get(6)` under linear is `(5.0, 0.0, 0.0)`.
4. After `SetInterpolationType(Held)`, `Get(6)` stays `(0.0, 0.0, 0.0)`.
5. `GetTimeSamples()` lists `[1.0, 11.0]`.

## Full script (identical to `lab10_time_samples.py`)

```python
"""Lab 10 — Time samples, Get() vs Get(t), linear vs held."""
from pxr import Gf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
xf = UsdGeom.Xform.Define(stage, "/Ball")
attr = xf.AddTranslateOp().GetAttr()
attr.Set(Gf.Vec3d(0, 0, 0), 1)
attr.Set(Gf.Vec3d(10, 0, 0), 11)
print("Get():", attr.Get())
print("Get(1):", tuple(attr.Get(1)))
print("Get(6) linear:", tuple(attr.Get(6)))
print("interp:", stage.GetInterpolationType())
stage.SetInterpolationType(Usd.InterpolationTypeHeld)
print("Get(6) held:", tuple(attr.Get(6)))
print("samples:", attr.GetTimeSamples())
```

**Expected output**
```text
Get(): None
Get(1): (0.0, 0.0, 0.0)
Get(6) linear: (5.0, 0.0, 0.0)
interp: Usd.InterpolationTypeLinear
Get(6) held: (0.0, 0.0, 0.0)
samples: [1.0, 11.0]
```

## Check your understanding
1. Why is `Get()` `None` instead of `(0, 0, 0)`?
2. Held at t=6 uses which key?
3. What is the default interpolation type?

**Answers**
1. There is **no authored default** and translate has **no fallback**. Samples are only for numeric times.
2. The **previous** sample (t=1 → origin). Not the next key.
3. **Linear** (`Usd.InterpolationTypeLinear`).

## Stretch challenge
Author a default with `attr.Set(Gf.Vec3d(9, 9, 9))` (no time) and print `Get()` again. Solution: `Get()` becomes `(9, 9, 9)`; `Get(1)` and `Get(6)` are unchanged — numeric queries still ignore the default.
