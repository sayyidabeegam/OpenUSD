# Lab 36 — Debugging toolkit: delegate, Trace, MallocTag

**Domain / objectives:** Debugging 6.5 · **Chapter:** 43 · **Time:** 30 min · **Difficulty:** ★★★

## Goal
Capture a missing-reference **warning** with **`UsdUtils.CoalescingDiagnosticDelegate`**, pair it with **`GetCompositionErrors()`**, prove **Trace starts disabled**, and show **`Tf.MallocTag` reports 0 bytes** on this usd-core wheel.

## Background
Construct the delegate **before** `Stage.Open` or you miss the warning (Ch 43). The class is **`UsdUtils.CoalescingDiagnosticDelegate`**, not `Tf.CoalescingDiagnosticDelegate`. `sourceFileName` may be a full path — **basename** it. Trace = **time**; MallocTag = **bytes**. `MallocTag.Initialize()` can return False while `IsInitialized()` becomes True; total bytes stay **0** on the pip wheel.

> [!VERSION] Verified on USD 26.08. `Tf.MallocTag.GetTotalBytes()` is 0 after Initialize on usd-core.

## Steps
1. One uncoalesced item; code `TF_DIAGNOSTIC_WARNING_TYPE`; commentary mentions `missing.usda`; source `stage.cpp`.
2. One Pcp composition error as well.
3. Trace enabled default False; collector label is the global collector.
4. MallocTag: before False, Initialize returned False, after True, **total bytes 0**.

## Full script (identical to `lab36_debugging_toolkit.py`)

```python
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
```

**Expected output**
```text
n: 1
code: TF_DIAGNOSTIC_WARNING_TYPE
warning: True
mentions missing: True
source file: stage.cpp
pcp errors: 1
trace enabled default: False
collector label: TraceRegistry global collector
malloc before: False
Initialize returned: False
malloc after: True
total bytes: 0
```

## Check your understanding
1. When must you construct the coalescing delegate?
2. Trace vs MallocTag — which measures time?
3. Does `Initialize()` returning False mean MallocTag is broken?

**Answers**
1. **Before** `Stage.Open`. After misses the warning.
2. **Trace** is time. MallocTag is bytes.
3. **No** on this wheel. `IsInitialized()` is True; bytes stay 0 because the pip allocator is untagged.

## Stretch challenge
Call `TakeUncoalescedDiagnostics()` a second time. Solution: empty — the first take **drains** the queue (Ch 43.3).
