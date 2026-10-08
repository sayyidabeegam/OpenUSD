"""Lab 26 — USD does not convert units; you add scale and rotateX."""
import os
import tempfile
from pxr import Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
print("fallback:", UsdGeom.GetStageUpAxis(Usd.Stage.CreateInMemory()),
      UsdGeom.GetStageMetersPerUnit(Usd.Stage.CreateInMemory()))

asset = Usd.Stage.CreateNew("chair_m.usda")
UsdGeom.SetStageMetersPerUnit(asset, UsdGeom.LinearUnits.meters)
UsdGeom.SetStageUpAxis(asset, UsdGeom.Tokens.z)
root = UsdGeom.Xform.Define(asset, "/Chair")
cube = UsdGeom.Cube.Define(asset, "/Chair/Geom")
cube.GetSizeAttr().Set(1.0)
cube.AddTranslateOp().Set((0, 0, 0.5))
asset.SetDefaultPrim(root.GetPrim())
asset.Save()

shot = Usd.Stage.CreateInMemory()
UsdGeom.SetStageMetersPerUnit(shot, UsdGeom.LinearUnits.centimeters)
UsdGeom.SetStageUpAxis(shot, UsdGeom.Tokens.y)
UsdGeom.Xform.Define(shot, "/World")
prim = shot.DefinePrim("/World/Chair")
prim.GetReferences().AddReference("chair_m.usda")
chair = UsdGeom.Xformable(prim)


def world_range(stage, path):
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"])
    r = cache.ComputeWorldBound(
        stage.GetPrimAtPath(path)).ComputeAlignedRange()
    fix = lambda v: tuple(round(c, 3) + 0.0 for c in v)
    return fix(r.GetMin()), fix(r.GetMax())


geom = UsdGeom.Cube(shot.GetPrimAtPath("/World/Chair/Geom"))
print("composed size:", geom.GetSizeAttr().Get())
print("shot metrics:", UsdGeom.GetStageUpAxis(shot),
      UsdGeom.GetStageMetersPerUnit(shot))
print("before:", world_range(shot, "/World/Chair"))

src = Usd.Stage.Open("chair_m.usda")
print("asset metrics:", UsdGeom.GetStageUpAxis(src),
      UsdGeom.GetStageMetersPerUnit(src))
factor = (UsdGeom.GetStageMetersPerUnit(src)
          / UsdGeom.GetStageMetersPerUnit(shot))
if UsdGeom.GetStageUpAxis(src) != UsdGeom.GetStageUpAxis(shot):
    chair.AddRotateXOp().Set(-90.0)
chair.AddScaleOp().Set((factor, factor, factor))
print("factor:", factor)
print("after:", world_range(shot, "/World/Chair"))
