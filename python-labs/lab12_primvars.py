"""Lab 12 — Indexed vertex displayColor primvar."""
from pxr import Sdf, Usd, UsdGeom, Vt

stage = Usd.Stage.CreateInMemory()
api = UsdGeom.PrimvarsAPI(UsdGeom.Mesh.Define(stage, "/Body"))
pv = api.CreatePrimvar(
    "displayColor", Sdf.ValueTypeNames.Color3fArray, UsdGeom.Tokens.vertex
)
pv.Set([(1, 0, 0), (0, 1, 0)])
pv.SetIndices(Vt.IntArray([0, 1, 0, 1]))
print("interpolation:", pv.GetInterpolation())
print("indexed:", pv.IsIndexed())
print("indices:", list(pv.GetIndices()))
print("values:", [tuple(v) for v in pv.Get()])
