"""Lab 04 — Root layer, session layer, export to string."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
ball = UsdGeom.Sphere.Define(stage, "/Ball")
ball.GetRadiusAttr().Set(1.0)
stack = stage.GetLayerStack(includeSessionLayers=True)
print("n layers:", len(stack))
print("first is session:", stack[0] == stage.GetSessionLayer())
print("second is root:", stack[1] == stage.GetRootLayer())
print("edit target is root:",
      stage.GetEditTarget().GetLayer() == stage.GetRootLayer())
stage.SetEditTarget(stage.GetSessionLayer())
ball.GetRadiusAttr().Set(9.0)
print("radius:", ball.GetRadiusAttr().Get())
print("winning layer is session:",
      ball.GetRadiusAttr().GetPropertyStack()[0].layer
      == stage.GetSessionLayer())
print("root still has:",
      stage.GetRootLayer().GetAttributeAtPath("/Ball.radius").default)
