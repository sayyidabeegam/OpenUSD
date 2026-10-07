from pxr import Tf, Usd, Sdf, UsdGeom, UsdUtils
print(Tf.Error, Tf.Warning, Tf.StatusObject, Tf.DiagnosticType)
print(list(Tf.DiagnosticType.allValues))
print(issubclass(Tf.ErrorException, RuntimeError), Tf.ErrorException.__mro__)
try:
    Usd.Stage.Open("does_not_exist.usda")
except Tf.ErrorException as e:
    print("open:", type(e).__name__, len(e.args), type(e.args[0]) if e.args else None)
    for a in e.args:
        print("   arg", type(a).__name__, [n for n in dir(a) if not n.startswith('_')])
        try:
            print("   ", a.commentary, a.errorCode, a.sourceFunction)
        except Exception as x:
            print("   x", x)
        break
s = Usd.Stage.CreateInMemory()
try:
    s.DefinePrim("relative/path")
except Tf.ErrorException as e:
    print("define:", e.args[0].commentary if e.args else str(e))
p = Sdf.Path("not a path")
print("badpath", p, p.isEmpty)
try:
    s.GetPrimAtPath("/X").GetAttribute("a").Get()
except Exception as e:
    print("null prim:", type(e).__name__)
d = UsdUtils.CoalescingDiagnosticDelegate()
Sdf.Path("not a path")
for x in d.TakeUncoalescedDiagnostics():
    print("diag", x.diagnosticCodeString, x.commentary)
