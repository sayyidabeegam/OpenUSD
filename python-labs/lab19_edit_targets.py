"""Lab 19 — Edit targets, EditContext, offset mapping, local stack."""
import os
import tempfile
from pxr import Sdf, Tf, Usd

os.chdir(tempfile.mkdtemp())
open("anim.usda", "w").write("""#usda 1.0
def "Ball"
{
}
""")
open("shot.usda", "w").write("""#usda 1.0
(
    subLayers = [
        @anim.usda@ (offset = 10)
    ]
)
""")
stage = Usd.Stage.Open("shot.usda")
anim = Sdf.Layer.Find("anim.usda")
print("default target:", stage.GetEditTarget().GetLayer().GetDisplayName())

stage.SetEditTarget(stage.GetEditTargetForLocalLayer(anim))
tx = stage.GetPrimAtPath("/Ball").CreateAttribute(
    "tx", Sdf.ValueTypeNames.Double
)
tx.Set(1.0, 20)
stage.SetEditTarget(Usd.EditTarget(anim))
tx.Set(2.0, 20)
print("anim samples:",
      anim.GetAttributeAtPath("/Ball.tx").GetInfo("timeSamples"))

stage.SetEditTarget(stage.GetRootLayer())
with Usd.EditContext(stage, stage.GetSessionLayer()):
    stage.GetPrimAtPath("/Ball").SetMetadata("comment", "try bigger")
print("restored:", stage.GetEditTarget().GetLayer().GetDisplayName())
print("session comment:",
      stage.GetSessionLayer().GetPrimAtPath("/Ball").comment)

try:
    stage.SetEditTarget(Sdf.Layer.CreateAnonymous("elsewhere"))
except Tf.ErrorException as err:
    print("not in stack:", "not in the local LayerStack" in str(err))
