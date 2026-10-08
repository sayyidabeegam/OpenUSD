"""Lab 28 — ComputeAllDependencies, Flatten vs FLS, USDZ STORE."""
import os
import tempfile
import zipfile
from pxr import Sdf, Usd, UsdGeom, UsdUtils

os.chdir(tempfile.mkdtemp())
os.makedirs("tex", exist_ok=True)
open("tex/wood.png", "wb").write(b"PNG")
open("geo.usda", "w").write("""#usda 1.0
over "L"
{
    asset tex = @./tex/wood.png@
}
""")
open("ref.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Bolt"
)
def Cube "Bolt"
{
}
""")
open("entry.usda", "w").write("""#usda 1.0
(
    defaultPrim = "L"
    subLayers = [
        @./geo.usda@
    ]
)
def Xform "L"
{
    asset missing = @./gone.jpg@
    def "Bolt" (
        prepend references = @./ref.usda@
    )
    {
    }
}
""")
layers, assets, unresolved = UsdUtils.ComputeAllDependencies("entry.usda")
print("layers:", sorted(os.path.basename(l.realPath) for l in layers))
print("assets:", sorted(os.path.basename(a) for a in assets))
print("unresolved:", sorted(os.path.basename(u) for u in unresolved))

stage = Usd.Stage.Open("entry.usda")
root = stage.GetRootLayer()
print("Export has tex:", root.GetAttributeAtPath("/L.tex") is not None)
flat = stage.Flatten()
bolt = flat.GetPrimAtPath("/L/Bolt")
print("Flatten Bolt type:", bolt.typeName)
print("Flatten Bolt has ref:", bool(bolt.referenceList.prependedItems))
ls = UsdUtils.FlattenLayerStack(stage)
bolt2 = ls.GetPrimAtPath("/L/Bolt")
print("FLS Bolt type:", bolt2.typeName or "-")
print("FLS Bolt has ref:", bool(bolt2.referenceList.prependedItems))
print("FLS subLayers empty:", list(ls.subLayerPaths) == [])

pkg = Usd.Stage.CreateNew("root.usda")
UsdGeom.Xform.Define(pkg, "/Asset")
pkg.SetDefaultPrim(pkg.GetPrimAtPath("/Asset"))
open("tex.png", "wb").write(
    bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"\x00" * 8)
pkg.GetPrimAtPath("/Asset").CreateAttribute(
    "tex", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath("./tex.png"))
pkg.GetRootLayer().Save()
print("usdz:", UsdUtils.CreateNewUsdzPackage("root.usda", "out.usdz"))
print("contents:", zipfile.ZipFile("out.usdz").namelist())
print("compress:",
      [i.compress_type for i in zipfile.ZipFile("out.usdz").infolist()])
