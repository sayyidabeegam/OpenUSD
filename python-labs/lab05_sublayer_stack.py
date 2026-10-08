"""Lab 05 — Build a sublayer stack and see who wins."""
import os
import tempfile
from pxr import Usd

os.chdir(tempfile.mkdtemp())
open("a.usda", "w").write("""#usda 1.0
def Sphere "Ball"
{
    double radius = 1
}
""")
open("b.usda", "w").write("""#usda 1.0
over "Ball"
{
    double radius = 2
}
""")
open("root.usda", "w").write("""#usda 1.0
(
    subLayers = [
        @./b.usda@,
        @./a.usda@
    ]
)
""")
stage = Usd.Stage.Open("root.usda")
print("stack:")
for lyr in stage.GetLayerStack(includeSessionLayers=False):
    print(" ", lyr.GetDisplayName())
radius = stage.GetPrimAtPath("/Ball").GetAttribute("radius")
print("radius:", radius.Get())
stage.MuteLayer(os.path.abspath("b.usda"))
print("muted radius:", radius.Get())
