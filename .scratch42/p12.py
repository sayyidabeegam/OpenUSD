import os
from pxr import Usd, Sdf, Ar, UsdGeom, Pcp
open("base.usda", "w").write('''#usda 1.0
def Xform "World" {
    double size = 1
}
over "OnlyOver" {}
''')
open("fix.usda", "w").write('''#usda 1.0
over "World" {
    double size = 5
}
''')
open("shot.usda", "w").write('''#usda 1.0
(
    subLayers = [@fix.usda@, @base.usda@]
)
''')
stage = Usd.Stage.Open("shot.usda")
print([os.path.basename(l.identifier) if not l.anonymous else "session"
       for l in stage.GetLayerStack()])
print([os.path.basename(l.identifier) if not l.anonymous else "session"
       for l in stage.GetLayerStack(includeSessionLayers=False)])
print(sorted(os.path.basename(l.identifier) if not l.anonymous else "session"
       for l in stage.GetUsedLayers()))
print(list(stage.GetRootLayer().subLayerPaths))
a = stage.GetAttributeAtPath("/World.size")
print(a.Get())
print([(os.path.basename(s.layer.identifier), s.default) for s in a.GetPropertyStack()])
ri = a.GetResolveInfo()
print(ri.GetSource(), ri.GetNode().layerStack.identifier.rootLayer.identifier if ri.GetNode() else None)
print(type(ri.GetNode()), [n for n in dir(ri.GetNode()) if not n.startswith('_')][:60])
fixlayer = Sdf.Layer.Find(os.path.abspath("fix.usda"))
ident = fixlayer.identifier
stage.MuteLayer(ident)
print("expired", fixlayer.expired)
print(a.Get(), [os.path.basename(x) for x in stage.GetMutedLayers()], stage.IsLayerMuted(ident))
stage.UnmuteLayer(ident)
print(a.Get())
print([str(p.GetPath()) for p in stage.Traverse()])
print([str(p.GetPath()) for p in stage.TraverseAll()])
p = stage.GetPrimAtPath("/OnlyOver")
print(p.IsValid(), p.IsDefined(), p.GetSpecifier())
print(stage.GetPrimAtPath("/Nope"), bool(stage.GetPrimAtPath("/Nope")))
r = Ar.GetResolver()
print(type(r).__name__, [n for n in dir(r) if not n.startswith('_')])
print(os.path.basename(str(r.Resolve("base.usda"))), bool(r.Resolve("base.usda")), repr(str(r.Resolve("missing.usda"))), bool(r.Resolve("missing.usda")))
print(r.CreateIdentifier("base.usda", Ar.ResolvedPath(os.path.abspath("shot.usda"))).replace(os.getcwd(), "."))
print([n for n in dir(Ar.DefaultResolver) if not n.startswith('_')])
print([n for n in dir(Ar) if not n.startswith('_')])
print(Usd.ResolveInfoSource.names if hasattr(Usd.ResolveInfoSource,'names') else dir(Usd.ResolveInfoSource))
