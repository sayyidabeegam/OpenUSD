"""Lab 23 — Native instancing: prototypes, proxies, de-instance."""
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/Chair")
UsdGeom.Cube.Define(stage, "/Chair/Seat").GetSizeAttr().Set(1.0)
a = stage.DefinePrim("/Room/A")
a.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
a.SetInstanceable(True)
b = stage.DefinePrim("/Room/B")
b.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
b.SetInstanceable(True)
print("A IsInstanceable/IsInstance:", a.IsInstanceable(), a.IsInstance())
print("B IsInstanceable/IsInstance:", b.IsInstanceable(), b.IsInstance())
print("GetMaster exists:", hasattr(Usd.Prim, "GetMaster"))
print("prototypes:", [str(p.GetPath()) for p in stage.GetPrototypes()])
print("A proto is B proto:", a.GetPrototype() == b.GetPrototype())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
seat = stage.GetPrimAtPath("/Room/A/Seat")
print("proxy Seat valid:", seat.IsValid(),
      "IsInstanceProxy:", seat.IsInstanceProxy())
print("shared size:", seat.GetAttribute("size").Get())
stage.GetPrimAtPath("/Chair/Seat").GetAttribute("size").Set(3.0)
print("after source A,B:",
      stage.GetPrimAtPath("/Room/A/Seat").GetAttribute("size").Get(),
      stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Get())
b.SetInstanceable(False)
stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Set(9.0)
print("after B unique A,B:",
      stage.GetPrimAtPath("/Room/A/Seat").GetAttribute("size").Get(),
      stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Get(),
      "B IsInstance", b.IsInstance())
