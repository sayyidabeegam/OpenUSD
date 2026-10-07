import os
from pxr import Usd, Sdf, Pcp
open("asset.usda", "w").write('''#usda 1.0
(
    defaultPrim = "Lamp"
)
def Xform "Lamp"
{
    double brightness = 9
}
''')
open("layout.usda", "w").write('''#usda 1.0
over "Lamp"
{
    double brightness = 2
}
''')
open("shot.usda", "w").write('''#usda 1.0
(
    subLayers = [@layout.usda@]
)
def "Lamp" (
    references = @asset.usda@
)
{
}
''')
s = Usd.Stage.Open("shot.usda")
a = s.GetAttributeAtPath("/Lamp.brightness")
print(a.Get())
for spec in a.GetPropertyStack():
    print(os.path.basename(spec.layer.identifier), spec.default)
ri = a.GetResolveInfo()
print(ri.GetSource(), ri.GetNode().arcType, ri.GetNode().path)
s.GetSessionLayer().ImportFromString('#usda 1.0\nover "Lamp" { double brightness = 0 }\n'.replace("{ ", "{\n").replace(" }", "\n}"))
print(a.Get(), [os.path.basename(x.layer.identifier) if not x.layer.anonymous else "session" for x in a.GetPropertyStack()])
s.GetSessionLayer().Clear()
a.Set(50.0, Usd.TimeCode(1))
print(a.Get(), a.Get(1), a.GetResolveInfo().GetSource(), a.GetResolveInfo(1).GetSource())
print(s.GetEditTarget().GetLayer().identifier == s.GetRootLayer().identifier)
q = Usd.PrimCompositionQuery(s.GetPrimAtPath("/Lamp"))
for arc in q.GetCompositionArcs():
    print(arc.GetArcType(), os.path.basename(arc.GetTargetNode().layerStack.identifier.rootLayer.identifier))
print("RI default:", a.GetResolveInfo(Usd.TimeCode.Default()).GetSource())
print("RI default node layer:", os.path.basename(str(a.GetResolveInfo(Usd.TimeCode.Default()).GetNode().layerStack.identifier.rootLayer.identifier)))
