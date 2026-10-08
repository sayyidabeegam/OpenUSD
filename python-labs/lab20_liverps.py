"""Lab 20 — LIVERPS: local, inherit, variant, specialize vs a reference."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("asset.usda", "w").write("""#usda 1.0
(
    defaultPrim = "X"
)
def Sphere "X"
{
    double radius = 1
}
""")
stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_I")
cls.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(3)

lvr = stage.DefinePrim("/LvsR")
lvr.GetReferences().AddReference("asset.usda")
lvr.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(2)

ivr = stage.DefinePrim("/IvsR")
ivr.GetReferences().AddReference("asset.usda")
ivr.GetInherits().AddInherit("/_I")

vvr = stage.DefinePrim("/VvsR")
vvr.GetReferences().AddReference("asset.usda")
vset = vvr.GetVariantSets().AddVariantSet("look")
vset.AddVariant("hi")
vset.SetVariantSelection("hi")
with vset.GetVariantEditContext():
    vvr.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(10)

base = stage.DefinePrim("/_S")
base.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(7)
svr = stage.DefinePrim("/SvsR")
svr.GetReferences().AddReference("asset.usda")
svr.GetSpecializes().AddSpecialize("/_S")


def radius(path):
    return stage.GetPrimAtPath(path).GetAttribute("radius").Get()


print("L vs R (local 2, ref 1):", radius("/LvsR"))
print("I vs R (inherit 3, ref 1):", radius("/IvsR"))
print("V vs R (variant 10, ref 1):", radius("/VvsR"))
print("S vs R (specialize 7, ref 1):", radius("/SvsR"))
