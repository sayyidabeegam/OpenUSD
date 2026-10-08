"""Lab 21 — Prim stack, property stack, ResolveInfo, composition arcs."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("lamp.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Lamp"
)
def Xform "Lamp"
{
    double height = 1
}
""")
stage = Usd.Stage.CreateNew("shot.usda")
cls = stage.CreateClassPrim("/_Look")
cls.CreateAttribute("height", Sdf.ValueTypeNames.Double).Set(9)
prim = stage.DefinePrim("/Lamp")
prim.GetReferences().AddReference("lamp.usda")
prim.GetInherits().AddInherit("/_Look")
prim.CreateAttribute("height", Sdf.ValueTypeNames.Double).Set(2)
attr = prim.GetAttribute("height")
print("value:", attr.Get())
print("prim stack:")
for spec in prim.GetPrimStack():
    print(" ", spec.layer.GetDisplayName(), spec.path)
print("property stack:")
for spec in attr.GetPropertyStack():
    print(" ", spec.layer.GetDisplayName(), spec.path, spec.default)
info = attr.GetResolveInfo()
print("resolve:", info.GetSource(), info.GetNode().arcType)
print("arcs:")
for arc in Usd.PrimCompositionQuery(prim).GetCompositionArcs():
    print(" ", arc.GetArcType(), str(arc.GetTargetNode().path))
print("errors:", len(stage.GetCompositionErrors()))
