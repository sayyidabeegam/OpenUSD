"""Lab 15 — LoadNone vs references, FindLoadable, OpenMasked."""
import os
import tempfile
from pxr import Usd

os.chdir(tempfile.mkdtemp())
open("hi.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Root"
)
def Xform "Root"
{
    def Cube "Hi"
    {
    }
}
""")
open("city.usda", "w").write("""#usda 1.0
def Xform "World"
{
    def Xform "A" (
        prepend payload = @./hi.usda@
    )
    {
    }
    def Xform "B" (
        prepend payload = @./hi.usda@
    )
    {
    }
    def Xform "C" (
        prepend references = @./hi.usda@
    )
    {
    }
}
""")
none = Usd.Stage.Open("city.usda", Usd.Stage.LoadNone)
print("LoadNone C/Hi:", bool(none.GetPrimAtPath("/World/C/Hi")))
print("LoadNone A/Hi:", bool(none.GetPrimAtPath("/World/A/Hi")))
print("loadable:", [str(p) for p in none.FindLoadable()])
print("load set:", [str(p) for p in none.GetLoadSet()])
none.Load("/World/A")
print("after Load A, A/Hi:", bool(none.GetPrimAtPath("/World/A/Hi")))
print("after Load A, B/Hi:", bool(none.GetPrimAtPath("/World/B/Hi")))
mask = Usd.StagePopulationMask(["/World/A"])
masked = Usd.Stage.OpenMasked("city.usda", mask)
print("masked A:", bool(masked.GetPrimAtPath("/World/A")))
print("masked B:", bool(masked.GetPrimAtPath("/World/B")))
print("masked C:", bool(masked.GetPrimAtPath("/World/C")))
print("masked A/Hi (payload LoadAll):",
      bool(masked.GetPrimAtPath("/World/A/Hi")))
