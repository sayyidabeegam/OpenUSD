from pxr import Trace, Usd
c = Trace.Collector()
print(c is Trace.Collector(), c.GetLabel())
c.enabled = True
@Trace.TraceFunction
def build():
    s = Usd.Stage.CreateInMemory()
    for i in range(10):
        s.DefinePrim("/P%d" % i)
with Trace.TraceScope("MyScope"):
    build()
c.enabled = False
r = Trace.Reporter.globalReporter
r.UpdateTraceTrees()
root = r.aggregateTreeRoot
print([n for n in dir(root) if not n.startswith('_')])
def walk(n, d=0):
    if d < 3:
        for ch in n.children:
            print("  "*d, ch.key, ch.count)
            walk(ch, d+1)
walk(root)
txt = open("x.txt","w"); 
r.Report("x.txt")
t = open("x.txt").read()
import re
print([l.strip() for l in t.splitlines() if "MyScope" in l or "build" in l][:4])
r.ClearTree()
