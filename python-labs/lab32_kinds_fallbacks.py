"""Lab 32 — Kind.Registry tree; no Python Register."""
from pxr import Kind, Usd, UsdGeom

print("all", sorted(Kind.Registry.GetAllKinds()))
print("HasKind door", Kind.Registry.HasKind("door"))
print("base component", Kind.Registry.GetBaseKind("component"))
print("base assembly", Kind.Registry.GetBaseKind("assembly"))
print("base group", Kind.Registry.GetBaseKind("group"))
print("base model", repr(Kind.Registry.GetBaseKind("model")))
print("component IsA model", Kind.Registry.IsA("component", "model"))
print("subcomponent IsA model",
      Kind.Registry.IsA("subcomponent", "model"))
print("component IsA group", Kind.Registry.IsA("component", "group"))
print("has Register", hasattr(Kind.Registry, "Register"))

stage = Usd.Stage.CreateInMemory()
chair = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
Usd.ModelAPI(chair).SetKind("component")
print("Chair IsComponent", chair.IsComponent())
Usd.ModelAPI(chair).SetKind("door")
print("kind door still GetKind", Usd.ModelAPI(chair).GetKind())
print("Chair IsComponent with door", chair.IsComponent())
