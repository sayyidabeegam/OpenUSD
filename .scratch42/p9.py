from pxr import Tf
help(Tf.MallocTag.Initialize)
print(Tf.MallocTag.IsInitialized())
r = Tf.MallocTag.Initialize()
print("init ->", r)
print(Tf.MallocTag.IsInitialized(), Tf.MallocTag.GetTotalBytes(), Tf.MallocTag.GetMaxTotalBytes())
t = Tf.MallocTag.GetCallTree()
print(type(t), [n for n in dir(t) if not n.startswith('_')])
