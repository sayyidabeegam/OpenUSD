"""Lab 34 — PreviewSurface, Apply then Bind, ComputeSurfaceSource."""
from pxr import Sdf, Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/World/Board")
UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
    "displayColor", Sdf.ValueTypeNames.Color3fArray,
    UsdGeom.Tokens.constant
).Set([(0.2, 0.5, 0.9)])
mat = UsdShade.Material.Define(stage, "/Looks/Paint")
ps = UsdShade.Shader.Define(stage, "/Looks/Paint/Preview")
ps.CreateIdAttr("UsdPreviewSurface")
ps.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((1, 0, 0))
ps.CreateOutput("surface", Sdf.ValueTypeNames.Token)
mat.CreateSurfaceOutput().ConnectToSource(ps.GetOutput("surface"))
UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(mat)
print("HasAPI without Apply:",
      mesh.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
print("has rel:", mesh.GetPrim().HasRelationship("material:binding"))
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
print("HasAPI after Apply:",
      mesh.GetPrim().HasAPI(UsdShade.MaterialBindingAPI))
bound = UsdShade.MaterialBindingAPI(mesh.GetPrim()).ComputeBoundMaterial()[0]
print("bound:", bound.GetPath())
print("shader id:", ps.GetIdAttr().Get())
print("surface source len:", len(mat.ComputeSurfaceSource()))
