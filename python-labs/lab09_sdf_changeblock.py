"""Lab 09 — Authoring with Sdf specs + Sdf.ChangeBlock."""
from pxr import Sdf, Tf, Usd, UsdGeom


class Counter:
    def __init__(self):
        self.n = 0

    def __call__(self, notice, sender):
        self.n += 1


stage = Usd.Stage.CreateInMemory()
lis = Counter()
key = Tf.Notice.Register(Usd.Notice.ObjectsChanged, lis, stage)
prim = UsdGeom.Xform.Define(stage, "/W").GetPrim()
lis.n = 0
prim.CreateAttribute("a", Sdf.ValueTypeNames.Int).Set(1)
prim.CreateAttribute("b", Sdf.ValueTypeNames.Int).Set(2)
prim.CreateAttribute("c", Sdf.ValueTypeNames.Int).Set(3)
print("without block:", lis.n)
lis.n = 0
with Sdf.ChangeBlock():
    spec = stage.GetRootLayer().GetPrimAtPath("/W")
    Sdf.AttributeSpec(spec, "d", Sdf.ValueTypeNames.Int)
    spec.properties["d"].default = 4
    Sdf.AttributeSpec(spec, "e", Sdf.ValueTypeNames.Int)
    spec.properties["e"].default = 5
print("with block:", lis.n)
print("d via Usd:", prim.GetAttribute("d").Get())
print("spec typeName:", spec.typeName)
key.Revoke()
print("revoked")
