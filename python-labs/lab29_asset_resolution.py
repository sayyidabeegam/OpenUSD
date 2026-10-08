"""Lab 29 — Naive vs anchored Resolve, search path, Stage.Open context."""
import os
import tempfile
from pxr import Ar, Sdf, Usd

os.chdir(tempfile.mkdtemp())
os.makedirs("assets/tex", exist_ok=True)
open("assets/tex/wood.png", "wb").write(b"PNG")
open("assets/chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair"
{
    asset tex = @./tex/wood.png@
}
""")
open("shot.usda", "w").write("""#usda 1.0
def Xform "W"
{
    def "C" (
        prepend references = @chair.usda@
    )
    {
    }
}
""")
os.makedirs("searchA/tex", exist_ok=True)
open("searchA/tex/wood.png", "wb").write(b"A")

r = Ar.GetResolver()
print("resolver:", type(r).__name__)
print("underlying:", type(Ar.GetUnderlyingResolver()).__name__)
print("AnchorRelativePath:", hasattr(r, "AnchorRelativePath"))
print("naive ./tex/wood.png:", bool(r.Resolve("./tex/wood.png")))
layer = Sdf.Layer.FindOrOpen("assets/chair.usda")
abs_path = layer.ComputeAbsolutePath("./tex/wood.png")
print("Resolve abs:", bool(r.Resolve(abs_path)))
ident = r.CreateIdentifier(
    "./tex/wood.png", Ar.ResolvedPath(layer.realPath))
print("CreateIdentifier then Resolve:", bool(r.Resolve(ident)))
print("no-anchor ident:", r.CreateIdentifier("./tex/wood.png"))
print("dependent tex/wood.png:", r.IsContextDependentPath("tex/wood.png"))
print("dependent ./tex/wood.png:", r.IsContextDependentPath("./tex/wood.png"))
print("unbound tex/wood.png:", bool(r.Resolve("tex/wood.png")))
ctx = Ar.DefaultResolverContext([os.path.abspath("searchA")])
with Ar.ResolverContextBinder(Ar.ResolverContext(ctx)):
    print("bound tex/wood.png:", bool(r.Resolve("tex/wood.png")))
    print("bound ./tex/wood.png:", bool(r.Resolve("./tex/wood.png")))
print("after unbind:", bool(r.Resolve("tex/wood.png")))
rc = Ar.ResolverContext(
    Ar.DefaultResolverContext([os.path.abspath("assets")]))
ok = Usd.Stage.Open("shot.usda", pathResolverContext=rc)
bad = Usd.Stage.Open("shot.usda")
print("with ctx errors/type:", len(ok.GetCompositionErrors()),
      ok.GetPrimAtPath("/W/C").GetTypeName())
print("no ctx errors:", len(bad.GetCompositionErrors()),
      type(bad.GetCompositionErrors()[0]).__name__)
