"""Lab 08 — Metadata, customData, assetInfo, stage metadata."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
print("default upAxis:", UsdGeom.GetStageUpAxis(stage))
print("default meters:", UsdGeom.GetStageMetersPerUnit(stage))
UsdGeom.SetStageUpAxis(stage, "Z")
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
world = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(world.GetPrim())
prim = world.GetPrim()
prim.SetCustomDataByKey("dept", "layout")
prim.SetAssetInfoByKey("identifier", "world")
print("upAxis:", UsdGeom.GetStageUpAxis(stage))
print("meters:", UsdGeom.GetStageMetersPerUnit(stage))
print("defaultPrim:", stage.GetDefaultPrim().GetName())
print("dept:", prim.GetCustomDataByKey("dept"))
print("asset id:", prim.GetAssetInfoByKey("identifier"))
