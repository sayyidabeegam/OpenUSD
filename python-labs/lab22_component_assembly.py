"""Lab 22 — Component, assembly, group, and a broken model chain."""
import os
import tempfile
from pxr import Kind, Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
open("chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    kind = "component"
)
{
    def Cube "Seat"
    {
        double size = 1
    }
}
""")
stage = Usd.Stage.CreateInMemory()
kitchen = UsdGeom.Xform.Define(stage, "/Kitchen").GetPrim()
Usd.ModelAPI(kitchen).SetKind("assembly")
props = UsdGeom.Xform.Define(stage, "/Kitchen/Props").GetPrim()
Usd.ModelAPI(props).SetKind("group")
c0 = stage.DefinePrim("/Kitchen/Props/Chair_0")
c0.GetReferences().AddReference("chair.usda")
UsdGeom.Xform.Define(stage, "/Kitchen/Clutter")
mug = UsdGeom.Xform.Define(stage, "/Kitchen/Clutter/Mug").GetPrim()
Usd.ModelAPI(mug).SetKind("component")
print("assembly is-a group:", Kind.Registry.IsA("assembly", "group"))
print(f"{'path':28} {'kind':13} model group component")
for prim in stage.Traverse():
    kind = Usd.ModelAPI(prim).GetKind() or "-"
    print(f"{str(prim.GetPath()):28} {kind:13} {prim.IsModel()!s:5} "
          f"{prim.IsGroup()!s:5} {prim.IsComponent()}")
print("model traversal:")
for prim in stage.Traverse(Usd.PrimIsModel):
    print(" ", prim.GetPath())
print("Chair_0 type:", c0.GetTypeName(),
      "kind:", Usd.ModelAPI(c0).GetKind())
