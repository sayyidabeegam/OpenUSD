"""Lab 37 — Capstone: component, assembly, validate, dependencies."""
import os
import tempfile
from pxr import Kind, Usd, UsdGeom, UsdUtils, UsdValidation

os.chdir(tempfile.mkdtemp())
open("chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
    metersPerUnit = 1
    upAxis = "Y"
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
reg = UsdValidation.ValidationRegistry()
geom = reg.GetOrLoadValidatorByName(
    "usdGeomValidators:StageMetadataChecker")
core = reg.GetOrLoadValidatorByName(
    "usdValidation:StageMetadataChecker")
chair = Usd.Stage.Open("chair.usda")
print("chair errors:",
      len(list(geom.Validate(chair))) + len(list(core.Validate(chair))))
print("chair kind:", Usd.ModelAPI(chair.GetDefaultPrim()).GetKind())
print("assembly is-a group:", Kind.Registry.IsA("assembly", "group"))

kitchen = Usd.Stage.CreateNew("kitchen.usda")
root = UsdGeom.Xform.Define(kitchen, "/Kitchen").GetPrim()
Usd.ModelAPI(root).SetKind("assembly")
kitchen.SetDefaultPrim(root)
UsdGeom.SetStageUpAxis(kitchen, "Y")
UsdGeom.SetStageMetersPerUnit(kitchen, 1)
props = UsdGeom.Xform.Define(kitchen, "/Kitchen/Props").GetPrim()
Usd.ModelAPI(props).SetKind("group")
c0 = kitchen.DefinePrim("/Kitchen/Props/Chair_0")
c0.GetReferences().AddReference("chair.usda")
kitchen.GetRootLayer().Save()
print("Chair_0 IsComponent:", c0.IsComponent())
print("Chair_0 type:", c0.GetTypeName())
layers, assets, unresolved = UsdUtils.ComputeAllDependencies(
    "kitchen.usda")
print("layers:", sorted(os.path.basename(l.realPath) for l in layers))
print("unresolved:", unresolved)
print("USD version:", Usd.GetVersion())
