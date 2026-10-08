"""Lab 17 — Class prims, inherit broadcast, local override."""
from pxr import Sdf, Usd

stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_Look")
cls.CreateAttribute("size", Sdf.ValueTypeNames.Double).Set(2)
a = stage.DefinePrim("/A", "Xform")
b = stage.DefinePrim("/B", "Xform")
a.GetInherits().AddInherit("/_Look")
b.GetInherits().AddInherit("/_Look")
print("before A/B:", a.GetAttribute("size").Get(),
      b.GetAttribute("size").Get())
cls.GetAttribute("size").Set(5)
print("after broadcast A/B:", a.GetAttribute("size").Get(),
      b.GetAttribute("size").Get())
a.GetAttribute("size").Set(9)
print("local A, B stays:", a.GetAttribute("size").Get(),
      b.GetAttribute("size").Get())
print("direct inherits:",
      [str(p) for p in a.GetInherits().GetAllDirectInherits()])
print("A abstract?:", a.IsAbstract(), "class abstract?:", cls.IsAbstract())
print("Traverse:", [p.GetName() for p in stage.Traverse()])
print("TraverseAll:", [p.GetName() for p in stage.TraverseAll()])
