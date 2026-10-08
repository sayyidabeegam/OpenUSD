# Lab 27 — Asset validator (`UsdValidation`)

**Domain / objectives:** Data Exchange 4.6 · **Chapter:** 30 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Run built-in **StageMetadataChecker** validators on an empty-metrics stage, then author **upAxis**, **metersPerUnit**, and **defaultPrim** until both checkers return **0** errors. Prove **`UsdUtils.ComplianceChecker` is gone**.

## Background
Obj 4.6 is "write a validator for the integrity of an exported asset." On USD 26.08 the library is **`pxr.UsdValidation`** (Ch 30). `usdchecker` is a CLI on full builds; **usd-core has no CLI**. `UsdUtils.ComplianceChecker` was removed in 26.08. Two metadata checkers: `usdGeomValidators:StageMetadataChecker` (up axis, meters) and `usdValidation:StageMetadataChecker` (`defaultPrim`). Do not print `GetMessage()` here — it embeds the anonymous layer id.

> [!VERSION] Verified on USD 26.08. `hasattr(UsdUtils, "ComplianceChecker")` is False.

## Steps
1. `ComplianceChecker: False`.
2. Before authoring metrics: three Errors (missing meters, missing upAxis, missing defaultPrim).
3. After `SetStageUpAxis`, `SetStageMetersPerUnit`, `SetDefaultPrim`: both checkers return **0**.

## Full script (identical to `lab27_asset_validator.py`)

```python
"""Lab 27 — UsdValidation StageMetadataChecker; no ComplianceChecker."""
from pxr import Usd, UsdGeom, UsdUtils, UsdValidation

print("ComplianceChecker:", hasattr(UsdUtils, "ComplianceChecker"))
reg = UsdValidation.ValidationRegistry()
geom = reg.GetOrLoadValidatorByName(
    "usdGeomValidators:StageMetadataChecker")
core = reg.GetOrLoadValidatorByName(
    "usdValidation:StageMetadataChecker")

stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/Ball")
print("before:")
for validator in (geom, core):
    for err in validator.Validate(stage):
        print(err.GetName(), err.GetType())

UsdGeom.SetStageUpAxis(stage, "Y")
UsdGeom.SetStageMetersPerUnit(stage, 1)
stage.SetDefaultPrim(stage.GetPrimAtPath("/Ball"))
print("after geom/core counts:",
      len(list(geom.Validate(stage))),
      len(list(core.Validate(stage))))
```

**Expected output**
```text
ComplianceChecker: False
before:
MissingMetersPerUnitMetadata UsdValidation.ValidationErrorType.Error
MissingUpAxisMetadata UsdValidation.ValidationErrorType.Error
MissingDefaultPrim UsdValidation.ValidationErrorType.Error
after geom/core counts: 0 0
```

## Check your understanding
1. What replaced `UsdUtils.ComplianceChecker`?
2. Does missing `usdchecker` on PATH mean you cannot validate?
3. Which checker reports `MissingDefaultPrim`?

**Answers**
1. **`pxr.UsdValidation`** (`ValidationRegistry`, `ValidationContext`).
2. **No.** Call validators from Python. The CLI is only on full OpenUSD builds.
3. **`usdValidation:StageMetadataChecker`**. Geom checker covers upAxis and metersPerUnit.

## Stretch challenge
Skip `SetDefaultPrim` and reprint core's error names. Solution: `MissingDefaultPrim` remains; geom count is 0 (axis and meters are set).
