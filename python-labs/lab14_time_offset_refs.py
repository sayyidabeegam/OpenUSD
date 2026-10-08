"""Lab 14 — Same animation, two layer offsets on references."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("anim.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Ball"
)
def Xform "Ball"
{
    double3 xformOp:translate.timeSamples = {
        0: (0, 0, 0),
        10: (10, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
""")
stage = Usd.Stage.CreateInMemory()
a = stage.DefinePrim("/A")
a.GetReferences().AddReference("anim.usda")
b = stage.DefinePrim("/B")
b.GetReferences().AddReference("anim.usda", Sdf.LayerOffset(10))
attr_a = a.GetAttribute("xformOp:translate")
attr_b = b.GetAttribute("xformOp:translate")
print("A samples:", attr_a.GetTimeSamples())
print("B samples:", attr_b.GetTimeSamples())
print("A at 0:", tuple(attr_a.Get(0)))
print("A at 10:", tuple(attr_a.Get(10)))
print("B at 10:", tuple(attr_b.Get(10)))
print("B at 20:", tuple(attr_b.Get(20)))
lo = Sdf.LayerOffset(10)
print("offset*0:", lo * 0)
print("offset*10:", lo * 10)
