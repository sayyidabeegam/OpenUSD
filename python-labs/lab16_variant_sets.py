"""Lab 16 — Variant set authoring with GetVariantEditContext."""
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
box = UsdGeom.Cube.Define(stage, "/Box").GetPrim()
vset = box.GetVariantSets().AddVariantSet("size")
for name, h in [("small", 1.0), ("big", 3.0)]:
    vset.AddVariant(name)
    vset.SetVariantSelection(name)
    with vset.GetVariantEditContext():
        box.CreateAttribute("height", Sdf.ValueTypeNames.Double).Set(h)
print("set names:", box.GetVariantSets().GetNames())
print("variant names:", vset.GetVariantNames())
vset.SetVariantSelection("small")
print("small height:", box.GetAttribute("height").Get())
vset.SetVariantSelection("big")
print("big height:", box.GetAttribute("height").Get())
print("selection:", vset.GetVariantSelection())
