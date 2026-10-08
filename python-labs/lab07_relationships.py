"""Lab 07 — Relationships and targets."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
a = UsdGeom.Xform.Define(stage, "/A").GetPrim()
UsdGeom.Xform.Define(stage, "/B")
rel = a.CreateRelationship("looks")
rel.AddTarget("/B")
print("targets:", [str(t) for t in rel.GetTargets()])
print("HasRelationship:", a.HasRelationship("looks"))
print("HasAttribute looks:", a.HasAttribute("looks"))
