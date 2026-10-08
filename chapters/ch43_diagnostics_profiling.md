# Chapter 43 — Diagnostics and Profiling Tools

> **Exam domain:** Debugging & Troubleshooting (11%) · **Objectives:** 6.5 · **Study day:** 12 · **Est. time:** 90 min
> **Prerequisites:** Ch 42 (scene debugging), Ch 8 / 34 (notices, ChangeBlock), Ch 22 (composition errors)

Chapter 42 asked *what is wrong with the stage*. This chapter asks *how USD talks while it works*: **status**, **warnings**, **errors**, **TfDebug** symbols, **diagnostic delegates** that capture those messages in Python, **Trace** timing, **TfMallocTag** memory, and **Pcp composition errors** as objects you can assert on. That is Obj 6.5 in one sitting.

`usd-core` 26.8 includes all of these Python modules. It still has no usdview profiler UI.

## Learning goals

- Emit and catch `Tf.Status`, `Tf.Warn`, and `Tf.ErrorException`.
- List, enable, and disable `Tf.Debug` symbols (and know `TF_DEBUG`).
- Capture warnings with `UsdUtils.CoalescingDiagnosticDelegate`.
- Turn `Trace.Collector` on, mark events, and update the global reporter.
- Initialize `Tf.MallocTag` and read `GetTotalBytes` (including the 0-byte `usd-core` case).
- Read `stage.GetCompositionErrors()` as the structured form of open-time warnings.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Tf** | The C++/Python foundation library: diagnostics, debug bits, errors. |
| **Status** | An informational diagnostic (`Tf.Status`). |
| **Warning** | A non-fatal diagnostic (`Tf.Warn`); composition failures often arrive as warnings. |
| **ErrorException** | Python exception raised for USD coding/runtime errors. |
| **TfDebug symbol** | A named switch (`USD_CHANGES`, `PCP_PRIM_INDEX`, …) that prints extra logs when enabled. |
| **Diagnostic delegate** | An object that *receives* diagnostics instead of (or as well as) printing them. |
| **Coalescing** | Grouping identical diagnostics so a storm of the same warning is one item. |
| **Trace** | USD's instrumentation timer (`Trace.Collector` / `Trace.Reporter`). |
| **MallocTag** | Optional allocator tagging so you can see which subsystem allocated bytes. |
| **Pcp error** | A composition-error object (`errorType`, `rootSite`) on the stage. |

---

## 43.1 Tf errors, warnings, status

### 1. What is it?
USD's messaging API lives on **`Tf`**. **`Tf.Status(msg)`** is info, **`Tf.Warn(msg)`** is a warning, **`Tf.RaiseCodingError(msg)`** raises **`Tf.ErrorException`**. Failed layer parses and many API misuses raise `ErrorException` automatically.

### 2. Why do we need it?
Print statements in your exporter are not what Hydra or `usdchecker` emit. Matching the exam (and production logs) means recognizing `Warning: in … --` lines and catching `ErrorException` instead of a bare `Exception` when you want USD-only failures.

### 3. Beginner explanation
Status is a polite note. Warning is a yellow flag you can keep driving through. `ErrorException` is the referee stopping play. All three share a log format: `Kind: in <function> at line N of <file> -- message`.

*Where the analogy breaks:* composition "errors" (missing references) are usually **warnings** at open time, not `ErrorException`. The stage still opens. Chapter 42 / §43.6 collect them as Pcp objects.

### 4. Technical explanation
- `Tf.Status("…")` / `Tf.Warn("…")` write to **stderr**, not stdout. `check_code_blocks.py` will not see them; you still emit them so a human (or a delegate, §43.3) does.
- `Tf.RaiseCodingError("…")` and `Tf.RaiseRuntimeError("…")` raise **`Tf.ErrorException`**. The message includes `Python coding error: …`. Catch `Tf.ErrorException`, not `RuntimeError`.
- `Sdf.Layer.ImportFromString("not usda")` and similar parse failures also raise `ErrorException`.
- `Tf.Fatal` / fatal diagnostic types abort; do not call them in libraries. Types you will see on captured diagnostics: `Tf.TF_DIAGNOSTIC_WARNING_TYPE`, `TF_DIAGNOSTIC_STATUS_TYPE`, `TF_DIAGNOSTIC_CODING_ERROR_TYPE`, …
- `Tf.Error` is a class for posted C++ errors; Python pipelines usually see `ErrorException` or a delegate item, not a manual `Tf.Error()` call.

### 5. Mental model

```text
stderr:   Status   Warn     (keep going)
Python:   raise Tf.ErrorException   (catch me)
fatal:    abort                     (do not use in tools)
```

### 6. Simple example
`Tf.Status("ch43-status")` and `Tf.Warn("ch43-warn")` print on stderr. `RaiseCodingError("ch43-boom")` is caught as `ErrorException` containing `ch43-boom`.

### 7. USDA example

There is no USDA for a Tf call. A **bad** USDA string is what triggers `ErrorException` from the parser:

```usda
#usda 1.0

def Sphere "Ok"
{
    double radius = 1
}
```

That file is valid. The Python example deliberately feeds `"not usda"` to `ImportFromString` to show the exception path.

### 8. Python example

```python
from pxr import Tf, Sdf

print("emitting Status and Warn on stderr")
Tf.Status("ch43-status")
Tf.Warn("ch43-warn")
try:
    Tf.RaiseCodingError("ch43-boom")
except Tf.ErrorException as err:
    print("caught:", type(err).__name__)
    print("has boom:", "ch43-boom" in str(err))
layer = Sdf.Layer.CreateAnonymous(".usda")
try:
    layer.ImportFromString("not usda")
    print("import ok")
except Tf.ErrorException:
    print("import raised ErrorException")
```

**Expected output**
```text
emitting Status and Warn on stderr
caught: ErrorException
has boom: True
import raised ErrorException
```

Stderr also shows `Status: … ch43-status` and `Warning: … ch43-warn` plus the coding-error dump. Those lines are not part of stdout.

### 9. Real-world use case
A batch importer wraps each `Stage.Open` and each `ImportFromString` in `except Tf.ErrorException`. Corrupt files fail that file, not the whole farm job. Status lines (`imported 12 shots`) stay on stderr for the farm log.

### 10. Common mistakes
> [!MISTAKE] Catching `Exception` around `Stage.Open` and swallowing composition warnings. Open *succeeds*; warnings are not exceptions. Use a delegate or `GetCompositionErrors()`.

> [!MISTAKE] Looking for Tf messages on stdout. They are on **stderr**.

> [!MISTAKE] Calling `Tf.Fatal` from an exporter to "fail loudly." It aborts the DCC.

### 11. Exam traps
> [!TRAP] "A missing reference raises `ErrorException`." It warns; the stage opens; Pcp lists the error.

> [!TRAP] `Tf.Warn` returns a bool you must check. It returns None; it *emits*.

> [!TRAP] `ErrorException` is a `RuntimeError` subclass you can catch as `RuntimeError` only — catch **`Tf.ErrorException`** to avoid eating unrelated bugs.

### 12. Practice questions
1. Where do `Tf.Status` and `Tf.Warn` write?
2. What exception type does `RaiseCodingError` raise?
3. Does `Stage.Open` of a file with a missing reference raise?

**Answers**
1. **stderr.**
2. **`Tf.ErrorException`.**
3. **No** (warning + Pcp error). Invalid USDA text *does* raise.

### 13. Exam takeaways
> [!KEY]
> - Status/Warn → stderr; coding/runtime problems → `Tf.ErrorException`.
> - Missing references are warnings, not exceptions.
> - Catch `Tf.ErrorException` around parse/open of untrusted files.
> - Fatal diagnostics abort; do not use them in pipeline tools.

---

## 43.2 `TfDebug` and `TF_DEBUG`

### 1. What is it?
**TfDebug** is a set of **named switches**. When `USD_CHANGES` is enabled, USD prints change-processing chatter. Python: `Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)`. The environment variable **`TF_DEBUG`** enables the same names before the process starts (`TF_DEBUG=USD_CHANGES`).

### 2. Why do we need it?
Stack dumps (§42) tell you *who won*. Debug symbols tell you *what USD did internally* (recompositions, layer loads, prim indexing). Obj 6.5 names TfDebug explicitly.

### 3. Beginner explanation
Think of extra verbose stickers on factory machines. Off, the floor is quiet. Flip `USD_CHANGES`, and the change-processing machine narrates every notice. `TF_DEBUG` is the wall switch you flip before entering the building (process start). `SetDebugSymbolsByName` is the switch on the machine after you are inside.

*Where the analogy breaks:* enabling a symbol can flood stderr. Enable one name, reproduce, disable.

### 4. Technical explanation
- `Tf.Debug.GetDebugSymbolNames()` → list of strings (58 names in usd-core 26.8, including `USD_CHANGES`, `PCP_PRIM_INDEX`, `PCP_CHANGES`, `SDF_ASSET`, …).
- `Tf.Debug.GetDebugSymbolDescription("USD_CHANGES")` → `"USD change processing"` (verified).
- `Tf.Debug.IsDebugSymbolNameEnabled(name)` → bool, default **False**.
- `Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)` → `['USD_CHANGES']` (the names it actually flipped). Pass `False` to turn off. Unknown names yield an empty list, not an exception.
- **`TF_DEBUG`**: colon- or space-separated names, or glob-like patterns depending on build. Set **before** launching Python. Changing the env var *after* import does not retroactively enable symbols.
- `Tf.Debug.SetOutputFile` can redirect debug prints. Default is stderr.
- These prints are *not* composition errors and are *not* captured by `GetCompositionErrors()`. A delegate (§43.3) may see them as status/warnings depending on how the symbol logs.

> [!VERSION] Verified on USD 26.08. Symbol *names* are stable enough for the exam (`USD_CHANGES`, `PCP_PRIM_INDEX`); the exact count (58 here) can grow. Do not memorize the count.

### 5. Mental model

```text
TF_DEBUG=USD_CHANGES python job.py     # before process
Tf.Debug.SetDebugSymbolsByName(name, True)   # after import
Tf.Debug.IsDebugSymbolNameEnabled(name)      # query
```

### 6. Simple example
`USD_CHANGES` starts off. `SetDebugSymbolsByName("USD_CHANGES", True)` returns `['USD_CHANGES']` and `IsDebugSymbolNameEnabled` becomes True. Turning it off returns to False.

### 7. USDA example

Debug symbols are process state, not USD files. A tiny layer you might watch under `USD_CHANGES`:

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 1
    }
}
```

Enabling `USD_CHANGES` then setting `radius` prints change chatter on stderr (not shown; not deterministic enough to snapshot).

### 8. Python example

```python
from pxr import Tf

print("USD_CHANGES enabled:",
      Tf.Debug.IsDebugSymbolNameEnabled("USD_CHANGES"))
print("description:",
      Tf.Debug.GetDebugSymbolDescription("USD_CHANGES"))
got = Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)
print("set returned:", got)
print("USD_CHANGES enabled:",
      Tf.Debug.IsDebugSymbolNameEnabled("USD_CHANGES"))
Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", False)
print("after off:", Tf.Debug.IsDebugSymbolNameEnabled("USD_CHANGES"))
print("has USD_CHANGES:",
      "USD_CHANGES" in Tf.Debug.GetDebugSymbolNames())
```

**Expected output**
```text
USD_CHANGES enabled: False
description: USD change processing
set returned: ['USD_CHANGES']
USD_CHANGES enabled: True
after off: False
has USD_CHANGES: True
```

Always turn symbols off when the capture is done so later tests stay quiet.

### 9. Real-world use case
A recomposition loop makes usdview hitch. A TD relaunches with `TF_DEBUG=PCP_PRIM_INDEX,USD_CHANGES`, repeats the edit, and sees prim indexes rebuilt on every keystroke because a script authors in a `ChangeBlock`-less loop (Chapter 34). The fix is batching, not a faster machine.

### 10. Common mistakes
> [!MISTAKE] Setting `os.environ["TF_DEBUG"]` after `from pxr import Usd`. Too late for many symbols. Set it in the shell, or use `SetDebugSymbolsByName`.

> [!MISTAKE] Leaving `USD_CHANGES` on in a farm job. Logs explode; disk fills.

> [!MISTAKE] Treating debug prints as `GetCompositionErrors()`. Different channels.

### 11. Exam traps
> [!TRAP] "`TF_DEBUG` is a prim metadata flag." It is a **process environment variable**.

> [!TRAP] `SetDebugSymbolsByName` raises on unknown names. It returns an **empty list**.

> [!TRAP] `USD_CHANGES` is on by default in usd-core. It is **off**.

### 12. Practice questions
1. Which call enables `USD_CHANGES` after import?
2. What does `GetDebugSymbolDescription("USD_CHANGES")` return?
3. When must `TF_DEBUG` be set to affect startup?

**Answers**
1. **`Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)`.**
2. **`"USD change processing"`.**
3. **Before launching the process** (before importing `pxr` for many symbols).

### 13. Exam takeaways
> [!KEY]
> - Obj 6.5: TfDebug names are strings; default off; `SetDebugSymbolsByName` / `TF_DEBUG`.
> - `USD_CHANGES` = change processing chatter.
> - Unknown names → empty list. Turn symbols off after use.
> - Debug logs ≠ Pcp composition errors.

---

## 43.3 Diagnostic delegates (`UsdUtils.CoalescingDiagnosticDelegate`)

### 1. What is it?
A **diagnostic delegate** is a Python object that **receives** Tf diagnostics. **`UsdUtils.CoalescingDiagnosticDelegate()`** (no arguments) installs itself while it lives, then lets you **`TakeUncoalescedDiagnostics()`** (every message) or **`TakeCoalescedDiagnostics()`** (grouped duplicates).

### 2. Why do we need it?
Farm tests cannot read a human's stderr. A missing reference would otherwise be a warning you never asserted on. The delegate turns that warning into a list of objects with `commentary`, `diagnosticCode`, and `sourceFileName`. Obj 6.5 names diagnostic delegates.

### 3. Beginner explanation
A delegate is a tape recorder plugged into the factory PA. USD still shouts; you also get a cassette. Uncoalesced is every shout. Coalesced is "the same shout 400 times, here is one copy plus a count."

*Where the analogy breaks:* constructing the delegate *is* plugging it in. There is no separate `Register` call. Let it go out of scope (or keep a reference until you `Take*`) so you do not leak it.

### 4. Technical explanation
- `delegate = UsdUtils.CoalescingDiagnosticDelegate()` starts capturing immediately.
- **`TakeUncoalescedDiagnostics()`** → list of `_DiagnosticBase`: `.commentary` (message text), `.diagnosticCode` (`Tf.TF_DIAGNOSTIC_WARNING_TYPE`, …), `.diagnosticCodeString` (`"TF_DIAGNOSTIC_WARNING_TYPE"`), `.sourceFileName` (e.g. `stage.cpp`), `.sourceLineNumber`, `.sourceFunction`. Taking **clears** the queue.
- **`TakeCoalescedDiagnostics()`** groups identical messages. After a take, the other queue may be empty — call the `Take*` that matches how you want to assert, not both unless you know which one drains first.
- Helpers: `DumpUncoalescedDiagnostics()`, `DumpCoalescedDiagnosticsToStdout()`, `DumpCoalescedDiagnosticsToStderr()`.
- Opening a stage with `@./missing.usda@` yields one uncoalesced item, warning type, commentary containing `missing.usda` (verified).
- Delegates do **not** replace `GetCompositionErrors()`. Use both: delegate for the log line, Pcp for the typed error.
- `Tf.DiagnosticTrap` exists as a context helper in some bindings; in 26.8's Python it has no extra public methods — prefer the coalescing delegate.

> [!VERSION] Verified on USD 26.08. `UsdUtils.CoalescingDiagnosticDelegate` is present. There is no `UsdUtils.DiagnosticDelegate` base you subclass in this wheel; use the coalescing class.

### 5. Mental model

```text
delegate = CoalescingDiagnosticDelegate()   # plug in
Stage.Open(...)                             # warnings recorded
items = delegate.TakeUncoalescedDiagnostics()
        items[0].diagnosticCodeString == TF_DIAGNOSTIC_WARNING_TYPE
        "missing.usda" in items[0].commentary
```

### 6. Simple example
Open `shot.usda` that references `missing.usda`. `TakeUncoalescedDiagnostics()` has length 1, code string `TF_DIAGNOSTIC_WARNING_TYPE`, commentary mentions `missing.usda`.

### 7. USDA example

```usda
#usda 1.0

def "A" (
    prepend references = @./missing.usda@
)
{
}
```

- Valid USDA. The *target file* is what is missing.
- Open emits a warning the delegate records.

### 8. Python example

```python
import os
from pxr import Tf, Usd, UsdUtils

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
```

**Expected output**
```text
n: 1
code: TF_DIAGNOSTIC_WARNING_TYPE
warning: True
mentions missing: True
source file: stage.cpp
pcp errors: 1
```

Same incident, two APIs: one log line, one Pcp error.

### 9. Real-world use case
CI opens every published asset under a delegate and fails the build if any item is a warning mentioning `Could not open asset`. That catches broken references even when the publisher forgot `GetCompositionErrors()`.

### 10. Common mistakes
> [!MISTAKE] Creating the delegate *after* `Stage.Open`. You missed the warning.

> [!MISTAKE] Calling both `TakeCoalesced` and `TakeUncoalesced` and expecting both to be full. The first take drains.

> [!MISTAKE] Asserting on `commentary ==` the full string. It contains absolute paths. Assert `in` (`"missing.usda" in commentary`).

### 11. Exam traps
> [!TRAP] The delegate class is `Tf.CoalescingDiagnosticDelegate`. It is **`UsdUtils.CoalescingDiagnosticDelegate`**.

> [!TRAP] Captured missing-reference diagnostics are `TF_DIAGNOSTIC_CODING_ERROR_TYPE`. They are **warnings**.

> [!TRAP] You must `Apply` the delegate on a prim. It is process-global while the object lives.

### 12. Practice questions
1. Which method returns each diagnostic as its own item?
2. What `diagnosticCodeString` does a missing reference produce?
3. When do you construct the delegate relative to `Stage.Open`?

**Answers**
1. **`TakeUncoalescedDiagnostics()`.**
2. **`TF_DIAGNOSTIC_WARNING_TYPE`.**
3. **Before** `Open`, so the warning is recorded.

### 13. Exam takeaways
> [!KEY]
> - `UsdUtils.CoalescingDiagnosticDelegate()` starts capturing on construct.
> - Uncoalesced = every message; coalesced = grouped. Take clears the queue.
> - Missing refs: warning delegate item *and* a Pcp error.
> - Match substrings in `commentary`, not full paths.

---

## 43.4 `Trace` collector and reports

### 1. What is it?
**Trace** is USD's built-in timer. **`Trace.Collector()`** is the global collector: set **`enabled = True`**, **`BeginEvent("name")` / `EndEvent("name")`**, then **`Trace.Reporter.globalReporter.UpdateTraceTrees()`**. `ReportTimes()` prints an aggregate table (stderr/stdout depending on the call).

### 2. Why do we need it?
Obj 6.5 lists Trace. When a flatten is slow, you want *which* USD function ate the seconds, not a generic Python profiler that cannot see C++ (`Pcp`, crate reads). Trace is that C++-aware timeline.

### 3. Beginner explanation
BeginEvent / EndEvent are start/stop buttons labelled with a string (`"ch43"`). The collector is off by default so production does not pay for the stopwatch. The global reporter is the printout you ask for after the race.

*Where the analogy breaks:* timings are **not deterministic**. Never snapshot milliseconds in a test. Snapshot that the collector toggled and that your event name was used.

### 4. Technical explanation
- `c = Trace.Collector()` returns the **global** collector (`GetLabel()` → `"TraceRegistry global collector"`). `c.enabled` default **False**. `c.pythonTracingEnabled` can also wrap Python functions (noisier).
- `c.BeginEvent("ch43")` / `c.EndEvent("ch43")` must pair. Mismatches drop events.
- `Trace.Reporter.globalReporter` (`GetLabel()` → `"Trace global reporter"`). Call **`UpdateTraceTrees()`** before reading. `ReportTimes()` prints "Total time for each key" with millisecond rows (including your `"ch43"`). `ReportChromeTracingToFile(path)` writes a Chrome-tracing JSON for `chrome://tracing`.
- `c.Clear()` / `reporter.ClearTree()` reset. Leave `enabled = False` when done.
- Trace does not require a stage. You can time any Python + USD mix.

> [!VERSION] Verified on USD 26.08. `Trace.Collector`, `Trace.Reporter.globalReporter`, `BeginEvent` / `EndEvent`, `ReportTimes`, `ReportChromeTracingToFile` are present.

### 5. Mental model

```text
enabled False  →  no cost
enabled True   →  BeginEvent("name") … work … EndEvent("name")
               →  globalReporter.UpdateTraceTrees()
               →  ReportTimes() / Chrome JSON
```

### 6. Simple example
Default `enabled` False. Turn on, `BeginEvent("ch43")`, `sum(range(1000))` (= 499500), `EndEvent`, turn off. Reporter label is `Trace global reporter`.

### 7. USDA example

Trace is not authored in USDA. Any stage you time is fine:

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 1
}
```

Wrap `Usd.Stage.Open` / `Flatten` with Begin/End in real jobs.

### 8. Python example

```python
from pxr import Trace

c = Trace.Collector()
print("enabled default:", c.enabled)
c.enabled = True
c.BeginEvent("ch43")
total = sum(range(1000))
c.EndEvent("ch43")
print("enabled after on:", c.enabled)
c.enabled = False
print("enabled after off:", c.enabled)
print("sum:", total)
print("collector label:", c.GetLabel())
rep = Trace.Reporter.globalReporter
rep.UpdateTraceTrees()
print("reporter label:", rep.GetLabel())
```

**Expected output**
```text
enabled default: False
enabled after on: True
enabled after off: False
sum: 499500
collector label: TraceRegistry global collector
reporter label: Trace global reporter
```

`ReportTimes()` would print a `ch43` row with a tiny millisecond value; we omit it because the number changes.

### 9. Real-world use case
A nightly flatten of a city set jumps from 4 s to 40 s. Trace around `UsdUtils.FlattenLayerStack` vs `stage.Export` (Chapter 34) shows Export spending its time in asset-path remapping. The TD switches the publish path to FlattenLayerStack for that show.

### 10. Common mistakes
> [!MISTAKE] Reading the reporter without `UpdateTraceTrees()`. Empty report.

> [!MISTAKE] Leaving `enabled = True` in production. Every `GetAttribute` pays.

> [!MISTAKE] Asserting `ReportTimes` milliseconds in CI. They jitter.

### 11. Exam traps
> [!TRAP] `Trace.Collector()` constructs a *new* collector each time. It is the **global** collector (same object).

> [!TRAP] Trace is part of `UsdUtils`. It is **`from pxr import Trace`**.

> [!TRAP] Collector is on by default so you always get timings. Default is **False**.

### 12. Practice questions
1. What attribute turns tracing on?
2. Which reporter object do you call `UpdateTraceTrees` on?
3. Why not snapshot `ReportTimes` output in this book?

**Answers**
1. **`collector.enabled = True`.**
2. **`Trace.Reporter.globalReporter`.**
3. **Milliseconds are not deterministic.**

### 13. Exam takeaways
> [!KEY]
> - `Trace.Collector().enabled` default False; `BeginEvent` / `EndEvent` pair.
> - `Trace.Reporter.globalReporter.UpdateTraceTrees()` then report.
> - Chrome JSON via `ReportChromeTracingToFile`.
> - Time values jitter; API names do not.

---

## 43.5 `TfMallocTag`

### 1. What is it?
**`Tf.MallocTag`** tags heap allocations with a subsystem name so you can ask **who allocated how many bytes**. `Initialize()`, `IsInitialized()`, `GetTotalBytes()`, `GetMaxTotalBytes()`, `GetCallTree().GetPrettyPrintString()`.

### 2. Why do we need it?
Obj 6.5 lists TfMallocTag next to Trace: time vs memory. A stage that is "slow" is sometimes just "huge." MallocTag is how USD-aware builds answer that without a generic heap profiler.

### 3. Beginner explanation
Every dollar spent in a store gets a sticker: "produce," "hardware." At the end you add up stickers. MallocTag is those stickers on `malloc`. `GetPrettyPrintString()` is the receipt.

*Where the analogy breaks:* the stickers are compiled into USD. The **pip `usd-core` wheel may initialize the API and still count 0 bytes** because tagging was not compiled in. The exam still expects the API names.

### 4. Technical explanation
- `Tf.MallocTag.IsInitialized()` starts **False**. `Initialize()` returns **False** on this wheel but `IsInitialized()` becomes **True** (verified 26.08). Treat "initialized" as "the module is ready," not "bytes will be nonzero."
- `GetTotalBytes()` / `GetMaxTotalBytes()` → **0** here. A studio *debug/tagging* build of OpenUSD returns real numbers after you open a large stage.
- `GetCallTree()` → `CallTree` with `GetPrettyPrintString()`, `GetCallSites()`, `GetRoot()`, `Report`. The pretty string starts with `Malloc Tag Report` and `Total bytes = 0` on this wheel.
- `SetDebugMatchList` / `SetCapturedMallocStacksMatchList` filter tags (advanced).
- Use MallocTag for **which USD subsystem** grew (Pcp vs Imaging vs Crate). Use OS tools (`ps`, `heaptrack`) for the whole process.

> [!VERSION] Verified on USD 26.08 `usd-core`: `Initialize` returns False, `IsInitialized` True, `GetTotalBytes` 0. Full OpenUSD builds with malloc tagging report nonzero bytes. Teach the API; do not promise nonzero counts from pip.

### 5. Mental model

```text
MallocTag.Initialize()     → IsInitialized True (even if bytes stay 0)
GetTotalBytes()            → 0 on usd-core; nonzero on tagged builds
GetCallTree().GetPrettyPrintString()  → "Malloc Tag Report"
```

### 6. Simple example
Call `Initialize`, print `IsInitialized` True, `GetTotalBytes` 0, pretty-print starts with the report banner.

### 7. USDA example

Memory tagging does not live in USDA. Opening a large layer is the usual workload you wrap:

```usda
#usda 1.0

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 1
    }
}
```

### 8. Python example

```python
from pxr import Tf

print("before:", Tf.MallocTag.IsInitialized())
result = Tf.MallocTag.Initialize()
print("Initialize returned:", result)
print("after:", Tf.MallocTag.IsInitialized())
print("total bytes:", Tf.MallocTag.GetTotalBytes())
print("max bytes:", Tf.MallocTag.GetMaxTotalBytes())
text = Tf.MallocTag.GetCallTree().GetPrettyPrintString()
print("report banner:", "Malloc Tag Report" in text)
print("report has Total bytes:", "Total bytes" in text)
```

**Expected output**
```text
before: False
Initialize returned: False
after: True
total bytes: 0
max bytes: 0
report banner: True
report has Total bytes: True
```

`Initialize returned: False` with `after: True` is the usd-core pattern, not a bug in your script.

### 9. Real-world use case
A lighting DCC build (tagged) shows Pcp indexes at 4 GB after loading a city. Instancing (Chapter 24) and payloads (Chapter 17) drop the tag. The same script on `usd-core` still "works"; it just prints 0, so TDs run it on the DCC's interpreter for real numbers.

### 10. Common mistakes
> [!MISTAKE] Treating `Initialize() == False` as fatal. Check `IsInitialized()` too.

> [!MISTAKE] Comparing `GetTotalBytes()` across pip and a studio build. Different compilation.

> [!MISTAKE] Using MallocTag to find a Python list leak. It tags **USD's** allocator, not all of CPython.

### 11. Exam traps
> [!TRAP] MallocTag is in `UsdUtils`. It is **`Tf.MallocTag`**.

> [!TRAP] "If total bytes is 0, Initialize failed and you cannot call GetCallTree." You can; the report says 0.

> [!TRAP] Trace and MallocTag are the same tool. Trace = **time**; MallocTag = **bytes**.

### 12. Practice questions
1. Which module owns MallocTag?
2. On usd-core 26.8, what does `GetTotalBytes()` return after `Initialize`?
3. Trace vs MallocTag: which measures time?

**Answers**
1. **`Tf`** (`Tf.MallocTag`).
2. **0** (tagging not compiled in).
3. **Trace.**

### 13. Exam takeaways
> [!KEY]
> - `Tf.MallocTag.Initialize` / `IsInitialized` / `GetTotalBytes` / `GetCallTree`.
> - usd-core may report **0 bytes**; studio tagged builds do not.
> - Trace = time, MallocTag = memory. Obj 6.5 expects both names.
> - `Initialize() == False` can still leave `IsInitialized` True.

---

## 43.6 Pcp composition errors

### 1. What is it?
**Pcp** (the composition engine) records **typed errors** on the stage: `stage.GetCompositionErrors()`. Each item has **`errorType`** (enum) and **`rootSite`** (where it was introduced). This is the structured twin of the warning in §43.1 / §43.3 and of the playbook in §42.4.

### 2. Why do we need it?
Stderr text is for humans. Tests and Obj 6.5 want an object: `Pcp.ErrorType_InvalidAssetPath` vs `UnresolvedPrimPath`. You already used the API in Chapter 42; here you connect it to diagnostics (same warning, two APIs) and to the other Obj 6.5 tools.

### 3. Beginner explanation
The factory PA shouted "could not open missing.usda" (warning). The incident log binder has a form with a **type code** and a **site** (Pcp error). Delegates copy the shout; `GetCompositionErrors` copies the form.

*Where the analogy breaks:* not every warning is a Pcp error (Tf.Warn from your own code is not). Not every Pcp error stays a warning if a future version promotes it.

### 4. Technical explanation
- `stage.GetCompositionErrors()` → list of Pcp error objects. Public fields in 26.08: **`errorType`**, **`rootSite`**. `str(err)` is the message (contains `@missing.usda@`, paths).
- Types you must recognize:
  - `Pcp.ErrorType_InvalidAssetPath` — file cannot be opened.
  - `Pcp.ErrorType_UnresolvedPrimPath` — file opened, prim path / defaultPrim failed.
  - `Pcp.ErrorType_ArcCycle` — circular composition (mentioned in Ch 22).
- `rootSite` prints like `@shot.usda@,@anon:…:shot-session.usda@</A>` — the layer stack plus the introducing prim. Do not snapshot the anon id; check `"</A>" in str(err.rootSite)` or similar.
- Errors are filled when the stage **opens / recomposes**. They sit on the stage until composition changes. Opening under `LoadNone` still reports missing *reference* files (references load); missing *payload* files report when that payload is loaded.
- Pipeline pattern: `if stage.GetCompositionErrors(): fail_publish()`. Combine with a delegate if you also care about non-Pcp warnings.

### 5. Mental model

```text
Stage.Open
   stderr warning     →  CoalescingDiagnosticDelegate  (text)
   Pcp error object   →  GetCompositionErrors()        (type + site)
```

Same missing file, both channels.

### 6. Simple example
`shot.usda` references `missing.usda`. Errors length 1, `errorType` is `InvalidAssetPath`, `str(err)` contains `missing.usda`, `rootSite` mentions `</A>`.

### 7. USDA example

```usda
#usda 1.0

def "A" (
    prepend references = @./missing.usda@
)
{
}
```

Identical to §43.3's file on purpose: one incident, two APIs.

### 8. Python example

```python
from pxr import Usd, Pcp

open("shot.usda", "w").write("""#usda 1.0
def "A" (
    prepend references = @./missing.usda@
)
{
}
""")
stage = Usd.Stage.Open("shot.usda")
errs = stage.GetCompositionErrors()
print("n:", len(errs))
print("type:", errs[0].errorType)
print("is InvalidAssetPath:",
      errs[0].errorType == Pcp.ErrorType_InvalidAssetPath)
print("mentions missing:", "missing.usda" in str(errs[0]))
print("site has /A:", "</A>" in str(errs[0].rootSite))
```

**Expected output**
```text
n: 1
type: Pcp.ErrorType_InvalidAssetPath
is InvalidAssetPath: True
mentions missing: True
site has /A: True
```

Import **`Pcp`** to compare enum values; `str(err.errorType)` also contains `InvalidAssetPath`.

### 9. Real-world use case
A publisher fails the job when *any* `GetCompositionErrors()` item is `InvalidAssetPath` or `UnresolvedPrimPath`, and emails `str(err)` plus the layer display name. Lighting still uses the delegate when they care about Tf.Warn from their own shaders.

### 10. Common mistakes
> [!MISTAKE] Parsing stderr instead of `GetCompositionErrors()` in tests. Fragile paths, locale, and line numbers.

> [!MISTAKE] Assuming `rootSite` is a `Sdf.Path`. It is a Pcp site; `str()` it.

> [!MISTAKE] Clearing errors with `Tf.Status`. Only a recomposition that fixes the arc clears them.

### 11. Exam traps
> [!TRAP] `GetCompositionErrors` lives on `Pcp.Cache`. You call it on **`Usd.Stage`**.

> [!TRAP] `InvalidAssetPath` means the referencing prim is invalid. The prim is defined; the *asset* is missing.

> [!TRAP] Pcp errors are TfDebug symbols. They are **objects**; TfDebug is optional chatter *about* composition.

### 12. Practice questions
1. Name the two fields on a 26.08 Pcp error object.
2. Missing file vs missing defaultPrim: which `errorType`s?
3. Which stage method returns them?

**Answers**
1. **`errorType`** and **`rootSite`.**
2. **`InvalidAssetPath`** vs **`UnresolvedPrimPath`.**
3. **`stage.GetCompositionErrors()`.**

### 13. Exam takeaways
> [!KEY]
> - Pcp errors = typed composition failures on the stage (`errorType`, `rootSite`).
> - Same missing file also warns (delegate). Tests should use the enum.
> - `InvalidAssetPath` ≠ `UnresolvedPrimPath`; both leave a defined empty prim.
> - Obj 6.5 ties this to TfDebug, delegates, Trace, and MallocTag — five tools, five jobs.

---

## Chapter lab(s)

**Lab 36 — Debugging toolkit: diagnostics delegate, TfDebug, Trace** (★★★, Obj 6.5). You capture a missing-reference warning with `CoalescingDiagnosticDelegate`, assert `GetCompositionErrors()[0].errorType`, toggle `USD_CHANGES`, and wrap a flatten in `Trace.Collector` Begin/End events. Stretch: `MallocTag.GetPrettyPrintString()` banner check.

Chapter 42's Lab 21 remains the composition-stack lab; this lab is the *instrumentation* lab.

## USDA reading exercise(s)

**Exercise 43-A.** This file opens. Does Python raise `Tf.ErrorException`? What do you call to see the failure in-process?

```usda
#usda 1.0

def "Chair" (
    prepend references = @./does_not_exist.usda@
)
{
}
```

**Exercise 43-B.** A TD sets `os.environ["TF_DEBUG"] = "USD_CHANGES"` on the line *after* `from pxr import Usd`, then authors an attribute, and sees no extra logs. Why?

**Exercise 43-C.** `MallocTag.GetTotalBytes()` is 0 after loading a city set in the book's `.venv`. Is Initialize broken?

## Chapter review

### Summary
- Status/Warn → stderr; `RaiseCodingError` → `Tf.ErrorException`. Missing refs warn, they do not raise.
- TfDebug: named symbols, default off, `SetDebugSymbolsByName` / `TF_DEBUG`.
- `UsdUtils.CoalescingDiagnosticDelegate` captures diagnostics; take uncoalesced or coalesced.
- Trace: global collector `enabled`, Begin/End, `Reporter.globalReporter`.
- MallocTag: Initialize / GetTotalBytes / GetCallTree; usd-core often stays at 0 bytes.
- Pcp: `GetCompositionErrors()` for typed failures (`InvalidAssetPath`, `UnresolvedPrimPath`).

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| `Warning: in _ReportErrors … Could not open asset` | Delegate + `GetCompositionErrors` |
| `Tf.ErrorException` / `Python coding error` | Parse or `RaiseCodingError`, not a missing ref |
| `TF_DEBUG=USD_CHANGES` | Process env, set before launch |
| `SetDebugSymbolsByName` → `[]` | Unknown symbol name |
| `TakeUncoalescedDiagnostics` empty | Delegate created too late, or already taken |
| `diagnosticCodeString` WARNING | Missing ref is a warning |
| Trace report empty | Forgot `UpdateTraceTrees` or `enabled` |
| `GetTotalBytes() == 0` | usd-core without tagging, not necessarily an empty stage |
| `Pcp.ErrorType_UnresolvedPrimPath` | File opened; prim path / defaultPrim failed |

### Review questions

**Q43.1** · Obj 6.5 · Easy · Single choice
`Tf.Warn("x")` writes to:
A. stdout · B. stderr · C. the session layer · D. `GetCompositionErrors()`

**Q43.2** · Obj 6.5 · Easy · Single choice
`Tf.RaiseCodingError("x")` raises:
A. `RuntimeError` · B. `Tf.ErrorException` · C. `Sdf.Error` · D. nothing; it warns

**Q43.3** · Obj 6.5 · Medium · Single choice
`Stage.Open` of USDA that references a missing file:
A. Raises `ErrorException` · B. Returns None · C. Returns a stage and warns · D. Hangs until the file appears

**Q43.4** · Obj 6.5 · Easy · Single choice
Which call enables `USD_CHANGES` in an already-running interpreter?
A. `os.environ["TF_DEBUG"] = "USD_CHANGES"` · B. `Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)` · C. `stage.SetDebug("USD_CHANGES")` · D. `UsdUtils.EnableDebug()`

**Q43.5** · Obj 6.5 · Easy · Single choice
`GetDebugSymbolDescription("USD_CHANGES")` is:
A. `"USD change processing"` · B. `"composition"` · C. `""` · D. `None` until enabled

**Q43.6** · Obj 6.5 · Medium · Select two.
`UsdUtils.CoalescingDiagnosticDelegate`:
A. Starts capturing on construction · B. Must be `Apply`'d on the root prim · C. `TakeUncoalescedDiagnostics` returns each message · D. Lives in `Tf`

**Q43.7** · Obj 6.5 · Medium · Single choice
A captured missing-reference diagnostic's `diagnosticCodeString` is:
A. `TF_DIAGNOSTIC_CODING_ERROR_TYPE` · B. `TF_DIAGNOSTIC_WARNING_TYPE` · C. `TF_DIAGNOSTIC_STATUS_TYPE` · D. `PCP_ERROR`

**Q43.8** · Obj 6.5 · Easy · Single choice
Trace lives in:
A. `UsdUtils` · B. `Tf` · C. `Trace` · D. `Usd`

**Q43.9** · Obj 6.5 · Medium · Single choice
Default `Trace.Collector().enabled` is:
A. True · B. False · C. None until `Initialize` · D. True in usdview only

**Q43.10** · Obj 6.5 · Easy · Single choice
`Tf.MallocTag` measures:
A. Time · B. Bytes allocated (when tagging is compiled in) · C. Prim count · D. Layer count

**Q43.11** · Obj 6.5 · Medium · Single choice
usd-core 26.8 after `MallocTag.Initialize()`: `GetTotalBytes()` is typically:
A. The size of the crate file · B. 0 · C. Always an exception · D. `-1`

**Q43.12** · Obj 6.5 · Medium · Select two.
A 26.08 Pcp error object has:
A. `errorType` · B. `GetPropertyStack` · C. `rootSite` · D. `TfDebugSymbol`

**Q43.13** · Obj 6.5 · Medium · Single choice
Missing file vs missing `defaultPrim`:
A. Both `InvalidAssetPath` · B. `InvalidAssetPath` vs `UnresolvedPrimPath` · C. Both raise `ErrorException` · D. Both are TfDebug symbols

### Answers

**Q43.1 — B.** Review: §43.1.

**Q43.2 — B.** Review: §43.1.

**Q43.3 — C.** Review: §43.1, §43.6.

**Q43.4 — B.** Env var after import is too late. Review: §43.2.

**Q43.5 — A.** Review: §43.2.

**Q43.6 — A, C.** Module is `UsdUtils`, not `Tf`; no `Apply`. Review: §43.3.

**Q43.7 — B.** Review: §43.3.

**Q43.8 — C.** `from pxr import Trace`. Review: §43.4.

**Q43.9 — B.** Review: §43.4.

**Q43.10 — B.** Review: §43.5.

**Q43.11 — B.** Tagging not in the pip wheel. Review: §43.5.

**Q43.12 — A, C.** Review: §43.6.

**Q43.13 — B.** Review: §43.6 / §42.4.

### USDA exercise answers

**43-A — No `ErrorException`.** The stage opens. Call `GetCompositionErrors()` (and optionally a `CoalescingDiagnosticDelegate` constructed *before* Open). `errorType` is `InvalidAssetPath`.

**43-B — `TF_DEBUG` must be set before the process (or before `pxr` is imported) for many symbols.** Use `Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)` after import instead.

**43-C — No.** On usd-core, `Initialize` can return False, `IsInitialized` True, and bytes stay 0 because malloc tagging was not compiled in. Run a studio/debug build for real counts.

## Further reading

- [S06] OpenUSD API — Tf diagnostic, TfDebug, Trace, TfMallocTag, UsdUtilsCoalescingDiagnosticDelegate, PcpError: https://openusd.org/release/api/index.html
- [S14] NVIDIA Learn OpenUSD — debugging and diagnostics: https://docs.nvidia.com/learn-openusd/latest/index.html
- Chapter 34 (notices / ChangeBlock, which `USD_CHANGES` narrates), Chapter 42 (when to use Pcp errors vs visual queries)
