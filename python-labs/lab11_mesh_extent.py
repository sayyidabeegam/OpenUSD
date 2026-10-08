"""Lab 11 — Mesh topology, subdivisionScheme, ComputeExtentFromPlugins."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Tri")
mesh.GetPointsAttr().Set([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
mesh.GetFaceVertexCountsAttr().Set([3])
mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])
print("scheme fallback:", mesh.GetSubdivisionSchemeAttr().Get())
mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
print("scheme authored:", mesh.GetSubdivisionSchemeAttr().Get())
print("extent authored?:", mesh.GetExtentAttr().HasAuthoredValue())
print("extent before:", mesh.GetExtentAttr().Get())
computed = UsdGeom.Boundable.ComputeExtentFromPlugins(
    UsdGeom.Boundable(mesh.GetPrim()), Usd.TimeCode.Default()
)
print("computed:", [tuple(v) for v in computed])
mesh.GetExtentAttr().Set(computed)
print("extent after:", [tuple(v) for v in mesh.GetExtentAttr().Get()])
