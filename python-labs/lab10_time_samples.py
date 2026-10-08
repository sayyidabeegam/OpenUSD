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
