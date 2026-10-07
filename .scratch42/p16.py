import os, json
from pxr import Tf, Trace, Usd
for n in ["PXR_ENABLE_GLOBAL_TRACE", "TF_FATAL_VERBOSE_SYMBOLS", "USD_ABC_READ_FLAGS"]:
    print(n, repr(Tf.GetEnvSetting(n)))
c = Trace.Collector()
c.Clear()
c.enabled = True
c.BeginEvent("ManualEvent")
s = Usd.Stage.CreateInMemory()
c.EndEvent("ManualEvent")
c.enabled = False
r = Trace.Reporter.globalReporter
r.UpdateTraceTrees()
main = [n for n in r.aggregateTreeRoot.children if n.key == "Main Thread"]
print([ch.key for ch in main[0].children])
r.ReportChromeTracingToFile("trace.json")
data = json.load(open("trace.json"))
print(type(data).__name__, list(data)[:3] if isinstance(data, dict) else len(data))
names = {e.get("name") for e in data["traceEvents"]} if isinstance(data, dict) else set()
print("ManualEvent" in names)
help(Trace.Reporter.Report)
