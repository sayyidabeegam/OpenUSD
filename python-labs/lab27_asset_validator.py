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
