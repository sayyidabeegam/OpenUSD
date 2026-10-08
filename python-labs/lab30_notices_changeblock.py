"""Lab 30 — ObjectsChanged resync vs info, ChangeBlock, DefinePrim trap."""
from pxr import Sdf, Tf, Usd, UsdGeom

hits = []


def on_changed(notice, sender):
    hits.append((
        [str(p) for p in notice.GetResyncedPaths()],
        [str(p) for p in notice.GetChangedInfoOnlyPaths()],
    ))


stage = Usd.Stage.CreateInMemory()
listener = Tf.Notice.Register(
    Usd.Notice.ObjectsChanged, on_changed, stage)
UsdGeom.Xform.Define(stage, "/W")
print("after define", hits)
hits.clear()
stage.GetPrimAtPath("/W").CreateAttribute(
    "a", Sdf.ValueTypeNames.Double).Set(1.0)
print("n after create+set", len(hits))
for h in hits:
    print(" resync", h[0], "info", h[1])
hits.clear()
parent = stage.GetRootLayer().GetPrimAtPath("/W")
with Sdf.ChangeBlock():
    for i in range(3):
        Sdf.PrimSpec(parent, f"S{i}", Sdf.SpecifierDef, "Sphere")
print("inside block", len(hits), [h[0] for h in hits])
hits.clear()
for i in range(3, 6):
    Sdf.PrimSpec(parent, f"S{i}", Sdf.SpecifierDef, "Sphere")
print("outside block", len(hits), [h[0] for h in hits])
try:
    with Sdf.ChangeBlock():
        UsdGeom.Sphere.Define(stage, "/W/Bad")
except Tf.ErrorException:
    print("Define inside block: Tf.ErrorException")
listener.Revoke()
print("revoked")
