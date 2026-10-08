"""Lab 36 — CoalescingDiagnosticDelegate, Trace, MallocTag 0 bytes."""
import os
import tempfile
from pxr import Tf, Trace, Usd, UsdUtils

os.chdir(tempfile.mkdtemp())
open("shot.usda", "w").write("""#usda 1.0
def "A" (
    prepend references = @./missing.usda@
)
{
}
""")
delegate = UsdUtils.CoalescingDiagnosticDelegate()
stage = Usd.Stage.Open("shot.usda")
items = delegate.TakeUncoalescedDiagnostics()
print("n:", len(items))
print("code:", items[0].diagnosticCodeString)
print("warning:",
      items[0].diagnosticCode == Tf.TF_DIAGNOSTIC_WARNING_TYPE)
print("mentions missing:", "missing.usda" in items[0].commentary)
print("source file:", os.path.basename(items[0].sourceFileName))
print("pcp errors:", len(stage.GetCompositionErrors()))

c = Trace.Collector()
print("trace enabled default:", c.enabled)
c.enabled = True
c.BeginEvent("lab36")
c.EndEvent("lab36")
c.enabled = False
print("collector label:", c.GetLabel())

print("malloc before:", Tf.MallocTag.IsInitialized())
print("Initialize returned:", Tf.MallocTag.Initialize())
print("malloc after:", Tf.MallocTag.IsInitialized())
print("total bytes:", Tf.MallocTag.GetTotalBytes())
