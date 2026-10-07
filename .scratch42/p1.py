from pxr import Tf, UsdUtils, Usd
Tf.Warn("hello warn")
Tf.Status("hello status")
try:
    Tf.RaiseRuntimeError("boom")
except Tf.ErrorException as e:
    print("caught", type(e).__name__, repr(str(e))[:200])
try:
    Tf.RaiseCodingError("cboom")
except Tf.ErrorException as e:
    print("caught2", str(e)[:200])
d = UsdUtils.CoalescingDiagnosticDelegate()
Tf.Warn("w1"); Tf.Warn("w1"); Tf.Status("s1")
s = Usd.Stage.CreateInMemory()
s.GetPrimAtPath("/nope")
cd = d.TakeCoalescedDiagnostics()
print(len(cd))
for x in cd:
    print([n for n in dir(x) if not n.startswith('_')])
    print(x.sharedItem.sourceFunction, x.sharedItem.sourceLineNumber, x.unsharedItems)
    break
d2 = UsdUtils.CoalescingDiagnosticDelegate()
Tf.Warn("a"); Tf.Status("b")
ud = d2.TakeUncoalescedDiagnostics()
for x in ud:
    print([n for n in dir(x) if not n.startswith('_')])
    print(x.commentary, x.diagnosticCode, x.diagnosticCodeString, x.sourceFileName)
