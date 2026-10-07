from pxr import Usd, Sdf, UsdGeom, UsdShade
open("payload.usda", "w").write('''#usda 1.0
( defaultPrim = "Heavy" )
def Xform "Heavy" {
    def Sphere "Ball" {}
}
''')
open("scene.usda", "w").write('''#usda 1.0
def Xform "World" {
    def Xform "Lamp" ( active = false ) {
        def Sphere "Bulb" {}
    }
    def Xform "Tree" ( payload = @payload.usda@ ) {}
    over "Ghost" {
        def Sphere "Inside" {}
    }
    def Xform "Car" (
        variants = { string trim = "base" }
        prepend variantSets = "trim"
    ) {
        variantSet "trim" = {
            "base" { }
            "sport" {
                def Cube "Spoiler" {}
            }
        }
    }
}
''')
st = Usd.Stage.Open("scene.usda", Usd.Stage.LoadNone)
print("Traverse:", [str(p.GetPath()) for p in st.Traverse()])
print("All:", [str(p.GetPath()) for p in st.TraverseAll()])
for path in ["/World/Lamp/Bulb", "/World/Tree/Ball", "/World/Ghost/Inside",
             "/World/Car/Spoiler", "/world/Car"]:
    p = st.GetPrimAtPath(path)
    print(path, bool(p), p.IsActive() if p else "-", p.IsLoaded() if p else "-")
lamp = st.GetPrimAtPath("/World/Lamp")
print("lamp", lamp.IsActive(), lamp.GetChildrenNames())
tree = st.GetPrimAtPath("/World/Tree")
print("tree", tree.IsLoaded(), tree.HasAuthoredPayloads(), sorted(str(x) for x in st.FindLoadable()))
mask = Usd.StagePopulationMask(["/World/Car"])
ms = Usd.Stage.OpenMasked("scene.usda", mask)
print("masked", [str(p.GetPath()) for p in ms.Traverse()])
ghost = st.GetPrimAtPath("/World/Ghost/Inside")
print("ghost inside", ghost.IsDefined(), ghost.GetParent().IsDefined())
print(Usd.PrimDefaultPredicate, Usd.PrimAllPrimsPredicate)
# stale extent
s = Usd.Stage.CreateInMemory()
m = UsdGeom.Mesh.Define(s, "/M")
pts = [(0, 0, 0), (1, 0, 0), (1, 1, 0)]
m.CreatePointsAttr(pts)
m.CreateExtentAttr(UsdGeom.PointBased.ComputeExtent(pts))
m.GetPointsAttr().Set([(0, 0, 0), (10, 0, 0), (10, 10, 0)])
print("stale", m.GetExtentAttr().Get(), UsdGeom.Boundable.ComputeExtentFromPlugins(m, Usd.TimeCode.Default()))
bc = UsdGeom.BBoxCache(Usd.TimeCode.Default(), [UsdGeom.Tokens.default_])
print("bbox", bc.ComputeWorldBound(m.GetPrim()).ComputeAlignedRange())
# material without API
mat = UsdShade.Material.Define(s, "/Mat")
prim = m.GetPrim()
rel = prim.CreateRelationship("material:binding")
rel.SetTargets(["/Mat"])
print("hasAPI", prim.HasAPI(UsdShade.MaterialBindingAPI))
bm, r = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
print("bound w/o API:", bool(bm))
UsdShade.MaterialBindingAPI.Apply(prim)
bm, r = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
print("bound with API:", bm.GetPath() if bm else None)
