"""Lab 02 — Your first stage: Xform + Sphere, save as USDA."""
import os
import tempfile
from pxr import Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
stage = Usd.Stage.CreateNew("hello.usda")
world = UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.GetRadiusAttr().Set(2.0)
stage.SetDefaultPrim(world.GetPrim())
stage.GetRootLayer().Save()
print(stage.GetRootLayer().ExportToString(), end="")
print("defaultPrim:", stage.GetDefaultPrim().GetName())
print("radius:", ball.GetRadiusAttr().Get())
print("file exists:", os.path.isfile("hello.usda"))
