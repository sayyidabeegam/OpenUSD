from pxr import Usd, Sdf, Pcp, Tf, UsdUtils
open("asset.usda", "w").write('''#usda 1.0
def Xform "Chair" {}
''')
open("cyc_a.usda", "w").write('''#usda 1.0
( defaultPrim = "A" )
def "A" ( references = @cyc_b.usda@ ) {}
''')
open("cyc_b.usda", "w").write('''#usda 1.0
( defaultPrim = "B" )
def "B" ( references = @cyc_a.usda@ ) {}
''')
open("shot.usda", "w").write('''#usda 1.0
(
    subLayers = [@missing_layer.usda@]
)
def "MissingFile" ( references = @nothere.usda@</X> ) {}
def "MissingPrim" ( references = @asset.usda@</Sofa> ) {}
def "NoDefault" ( references = @asset.usda@ ) {}
def "Cycle" ( references = @cyc_a.usda@ ) {}
def "BadVariant" (
    variants = { string look = "purple" }
    prepend variantSets = "look"
) {
    variantSet "look" = { "red" { } }
}
def "Inner" ( references = </NotThere> ) {}
''')
d = UsdUtils.CoalescingDiagnosticDelegate()
stage = Usd.Stage.Open("shot.usda")
for e in stage.GetCompositionErrors():
    print(type(e).__name__, e.errorType, "|", e.rootSite)
    print("   ", str(e))
print("diag:")
for x in d.TakeUncoalescedDiagnostics():
    print("  ", x.diagnosticCodeString, x.sourceFunction, x.commentary[:300])
print(stage.GetPrimAtPath("/BadVariant").GetVariantSet("look").GetVariantSelection())
print([n for n in dir(Pcp.ErrorBase) if not n.startswith('_')])
for p in stage.Traverse():
    print(p.GetPath(), p.GetChildrenNames())
print(stage.GetPrimAtPath("/MissingFile").GetPrimIndex().DumpToString()[:600])
