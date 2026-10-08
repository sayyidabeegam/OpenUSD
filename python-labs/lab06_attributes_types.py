"""Lab 06 — Attributes and value types."""
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/P").GetPrim()
count = prim.CreateAttribute("count", Sdf.ValueTypeNames.Int)
count.Set(3)
mass = prim.CreateAttribute("mass", Sdf.ValueTypeNames.Float)
mass.Set(1.5)
tint = prim.CreateAttribute("tint", Sdf.ValueTypeNames.Color3f)
tint.Set((0.2, 0.4, 0.8))
pos = prim.CreateAttribute("pos", Sdf.ValueTypeNames.Point3f)
pos.Set((1, 2, 3))
print("count", count.GetTypeName(), count.Get())
print("mass", mass.GetTypeName(), mass.Get())
print("tint", tint.GetTypeName(), tint.Get())
print("pos", pos.GetTypeName(), pos.Get())
print("authored:", sorted(prim.GetAuthoredPropertyNames()))
