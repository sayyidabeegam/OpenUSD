from pxr import Trace, Usd
import io, contextlib
print([n for n in dir(Trace.Collector) if not n.startswith('_')])
print([n for n in dir(Trace.Reporter) if not n.startswith('_')])
c = Trace.Collector()
print(c.enabled)
c.enabled = True
@Trace.TraceFunction
def build():
    s = Usd.Stage.CreateInMemory()
    for i in range(10):
        s.DefinePrim("/P%d" % i)
    return s
with Trace.TraceScope("MyScope"):
    build()
c.enabled = False
r = Trace.Reporter.globalReporter
print(type(r).__name__)
r.UpdateTraceTrees()
import tempfile, os
r.Report("rep.txt")
txt = open("rep.txt").read()
print("MyScope" in txt, "build" in txt)
print(txt[:1500])
