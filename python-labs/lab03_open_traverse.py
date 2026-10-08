"""Lab 03 — Open and traverse a stage."""
import os
import tempfile
from pxr import Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
stage = Usd.Stage.CreateNew("hello.usda")
world = UsdGeom.Xform.Define(stage, "/World")
UsdGeom.Sphere.Define(stage, "/World/Ball")
stage.SetDefaultPrim(world.GetPrim())
stage.GetRootLayer().Save()

opened = Usd.Stage.Open("hello.usda")
print("root ends:", os.path.basename(opened.GetRootLayer().identifier))
print("prims:")
for prim in opened.Traverse():
    print(" ", prim.GetPath(), prim.GetTypeName())
ball = opened.GetPrimAtPath("/World/Ball")
print("Ball valid:", ball.IsValid(), "type:", ball.GetTypeName())
print("missing valid:", opened.GetPrimAtPath("/Nope").IsValid())
