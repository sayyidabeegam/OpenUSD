import os
from pxr import Usd, Sdf, Ar, UsdGeom, UsdValidation
os.makedirs("lib", exist_ok=True)
open("lib/chair.usda", "w").write('''#usda 1.0
( defaultPrim = "Chair" )
def Xform "Chair" {}
''')
open("shot.usda", "w").write('''#usda 1.0
def "SearchRef" ( references = @chair.usda@ ) {}
def "AnchoredRef" ( references = @./chair.usda@ ) {}
def "Good" ( references = @./lib/chair.usda@ ) {}
''')
def report(stage, tag):
    errs = sorted(str(e.rootSite.path) for e in stage.GetCompositionErrors())
    print(tag, errs)
report(Usd.Stage.Open("shot.usda"), "no search path:")
ctx = Ar.DefaultResolverContext([os.path.abspath("lib")])
report(Usd.Stage.Open("shot.usda", pathResolverContext=ctx), "with context:")
print(Ar.IsPackageRelativePath("a.usdz[b.usda]"))

s = Usd.Stage.CreateInMemory()
m = UsdGeom.Mesh.Define(s, "/M")
print("orient", m.GetOrientationAttr().Get(), "subdiv", m.GetSubdivisionSchemeAttr().Get())
print("purpose", m.GetPurposeAttr().Get(), "vis", m.GetVisibilityAttr().Get())
print("upAxis", UsdGeom.GetStageUpAxis(s), "mpu", UsdGeom.GetStageMetersPerUnit(s))
print("normals interp", m.GetNormalsInterpolation())
m.CreatePointsAttr([(0,0,0),(1,0,0),(1,1,0)])
print("extent authored", m.GetExtentAttr().HasAuthoredValue())
print(UsdGeom.Boundable.ComputeExtentFromPlugins(m, Usd.TimeCode.Default()))
print([n for n in dir(UsdGeom.Mesh) if 'Valid' in n or 'Extent' in n])
print([n for n in dir(UsdGeom.Primvar) if 'Valid' in n or 'Element' in n])
reg = UsdValidation.ValidationRegistry()
print(sorted(str(n) for n in reg.GetAllValidatorNames()))
