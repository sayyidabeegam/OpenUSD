from pxr import Tf
r = Tf.MallocTag.Initialize()
print("init ->", repr(r), Tf.MallocTag.IsInitialized())
from pxr import Usd, UsdGeom
s = Usd.Stage.CreateInMemory()
for i in range(2000):
    UsdGeom.Xform.Define(s, "/X%d" % i)
print(Tf.MallocTag.GetTotalBytes(), Tf.MallocTag.GetMaxTotalBytes())
t = Tf.MallocTag.GetCallTree()
root = t.GetRoot()
print([n for n in dir(root) if not n.startswith('_')])
print(root.siteName, root.nBytes, len(root.children))
print(len(t.GetCallSites()))
print(t.GetPrettyPrintString()[:800])
