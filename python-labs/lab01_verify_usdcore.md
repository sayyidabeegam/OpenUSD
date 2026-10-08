# Lab 01 — Install and verify `usd-core`

**Domain / objectives:** Foundations · **Chapter:** F5 · **Time:** 15 min · **Difficulty:** ★☆☆

## Goal
Prove that the book's Python environment can import OpenUSD 26.08 and that the pip wheel has **no** `usdcat` / `usdview` on `PATH`.

## Background
The study environment uses **`usd-core` 26.8**, which is OpenUSD **26.08**. `Usd.GetVersion()` returns `(0, 26, 8)` — the leading month zero is dropped. Schema domains (`UsdGeom`, `UsdShade`, `UsdLux`) import; command-line tools and Hydra do **not** ship with this wheel (Ch F5, Ch 31, Ch 41).

## Steps
1. Activate `.venv` and run the script with `.venv/bin/python python-labs/lab01_verify_usdcore.py`.
2. Confirm the version tuple is `(0, 26, 8)`.
3. Confirm `usdcat` and `usdview` print `False`. Later labs use Python stand-ins (`ExportToString`, `UsdValidation`).

## Full script (identical to `lab01_verify_usdcore.py`)

```python
"""Lab 01 — Install and verify usd-core (USD 26.08)."""
import shutil
from pxr import Usd, UsdGeom, UsdShade, UsdLux

print("USD version:", Usd.GetVersion())
print("has UsdGeom:", bool(UsdGeom.Sphere))
print("has UsdShade:", bool(UsdShade.Material))
print("has UsdLux:", bool(UsdLux.DistantLight))
print("usdcat on PATH:", bool(shutil.which("usdcat")))
print("usdview on PATH:", bool(shutil.which("usdview")))
```

**Expected output**
```text
USD version: (0, 26, 8)
has UsdGeom: True
has UsdShade: True
has UsdLux: True
usdcat on PATH: False
usdview on PATH: False
```

## Check your understanding
1. Why is the pip version `26.8` but the release `26.08`?
2. Does a missing `usdcat` mean USD is broken?
3. Which module defines `DistantLight`?

**Answers**
1. The package drops the month's leading zero; `GetVersion()` is `(0, 26, 8)`.
2. No — `usd-core` never ships CLI tools. Use Python equivalents.
3. **`UsdLux`**, not `UsdGeom`.

## Stretch challenge
Import `UsdImaging` and catch `ImportError`. (It should fail on this wheel.) Solution: `from pxr import UsdImaging` raises `ImportError`; that is expected (Ch 41.4).
