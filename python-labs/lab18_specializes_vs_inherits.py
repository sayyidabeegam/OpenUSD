"""Lab 18 — Inherits beat references; specializes lose to them."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("asset.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Mat"
)
def "Mat"
{
    double roughness = 0.2
}
""")
stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_base")
cls.CreateAttribute("roughness", Sdf.ValueTypeNames.Double).Set(0.9)
cls.CreateAttribute("metallic", Sdf.ValueTypeNames.Double).Set(1.0)
inh = stage.DefinePrim("/ViaInherit")
inh.GetReferences().AddReference("asset.usda")
inh.GetInherits().AddInherit("/_base")
spc = stage.DefinePrim("/ViaSpecialize")
spc.GetReferences().AddReference("asset.usda")
spc.GetSpecializes().AddSpecialize("/_base")
print("inherit roughness/metallic:",
      inh.GetAttribute("roughness").Get(),
      inh.GetAttribute("metallic").Get())
print("specialize roughness/metallic:",
      spc.GetAttribute("roughness").Get(),
      spc.GetAttribute("metallic").Get())
print("HasAuthoredInherits:", inh.HasAuthoredInherits())
print("HasAuthoredSpecializes:", spc.HasAuthoredSpecializes())
inh.CreateAttribute("roughness", Sdf.ValueTypeNames.Double).Set(0.5)
spc.CreateAttribute("roughness", Sdf.ValueTypeNames.Double).Set(0.5)
print("local on both:", inh.GetAttribute("roughness").Get(),
      spc.GetAttribute("roughness").Get())
inh.GetAttribute("roughness").Clear()
spc.GetAttribute("roughness").Clear()
print("after Clear inherit/specialize:",
      inh.GetAttribute("roughness").Get(),
      spc.GetAttribute("roughness").Get())
