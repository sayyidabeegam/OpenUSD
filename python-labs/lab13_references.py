"""Lab 13 — defaultPrim, explicit paths, UnresolvedPrimPath, internal refs."""
import os
import tempfile
from pxr import Sdf, Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
open("box.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Box"
)
def Cube "Box"
{
    double size = 2
}
""")
open("nodefault.usda", "w").write("""#usda 1.0
def Cube "Box"
{
    double size = 9
}
""")
open("explicit.usda", "w").write("""#usda 1.0
def Cube "Skip"
{
    double size = 99
}
def Cube "Only"
{
    double size = 1
}
""")
stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/_Tmpl").GetRadiusAttr().Set(4)
a = stage.DefinePrim("/A")
print("A authored:", a.GetReferences().AddReference("box.usda"))
b = stage.DefinePrim("/B")
print("B authored:", b.GetReferences().AddReference("nodefault.usda"))
c = stage.DefinePrim("/C")
print("C authored:", c.GetReferences().AddReference(
    "explicit.usda", Sdf.Path("/Only")
))
d = stage.DefinePrim("/D")
print("D authored:", d.GetReferences().AddInternalReference("/_Tmpl"))
print("A type/size:", a.GetTypeName(), a.GetAttribute("size").Get())
print("B type/size:", repr(b.GetTypeName()), b.GetAttribute("size").Get())
print("C type/size:", c.GetTypeName(), c.GetAttribute("size").Get())
print("Skip on stage?:", bool(stage.GetPrimAtPath("/Skip")))
print("D type/radius:", d.GetTypeName(), d.GetAttribute("radius").Get())
for err in sorted(stage.GetCompositionErrors(),
                  key=lambda e: str(e.rootSite.path)):
    print("error at", err.rootSite.path, "->", err.errorType)
