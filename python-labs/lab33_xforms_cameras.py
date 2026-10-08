"""Lab 33 — xformOpOrder, XformCache, UsdGeom.Camera → Gf.Camera."""
from pxr import Gf, Tf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
xf = UsdGeom.Xform.Define(stage, "/Box")
xf.AddTranslateOp().Set(Gf.Vec3d(1, 0, 0))
print("order:", list(xf.GetPrim().GetAttribute("xformOpOrder").Get()))
try:
    xf.AddTranslateOp()
except Tf.ErrorException:
    print("second AddTranslateOp: Tf.ErrorException")
child = UsdGeom.Xform.Define(stage, "/Box/Lid")
child.AddTranslateOp().Set(Gf.Vec3d(0, 2, 0))
cache = UsdGeom.XformCache(Usd.TimeCode.Default())
print("world Box:", tuple(
    cache.GetLocalToWorldTransform(xf.GetPrim()).ExtractTranslation()))
print("world Lid:", tuple(
    cache.GetLocalToWorldTransform(
        child.GetPrim()).ExtractTranslation()))

cam = UsdGeom.Camera.Define(stage, "/ShotCam")
print("fallback focal/hAperture:", cam.GetFocalLengthAttr().Get(),
      round(cam.GetHorizontalApertureAttr().Get(), 3))
cam.AddTranslateOp().Set(Gf.Vec3d(0, 0, 10))
cam.GetFocalLengthAttr().Set(35.0)
gf = cam.GetCamera(Usd.TimeCode.Default())
print(type(gf).__name__, gf.projection)
print("hFOV", round(gf.GetFieldOfView(Gf.Camera.FOVHorizontal), 2))
print("position", tuple(gf.transform.ExtractTranslation()))
