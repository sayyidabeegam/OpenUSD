# Lab 23 — Native instancing: prototypes, proxies, de-instance

**Domain / objectives:** Content Aggregation 2.2 · **Chapter:** 24 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Mark two internal references **`instanceable`**, prove they share one **`GetPrototype()`**, that **`GetMaster` is gone**, that default **`Traverse()` skips instance children**, and that **`SetInstanceable(False)`** lets one copy become unique.

## Background
**Native instancing** shares one prototype prim tree among matching instanceable prims (Ch 24). Author `instanceable` on the **referencing** prims, not only on the source. `IsInstanceable()` is the flag; `IsInstance()` means USD actually built a prototype. Descendants of an instance are **instance proxies**: `GetPrimAtPath` finds them, `Traverse()` does not. Source edits reach every instance. Nested `over` under an instanceable prim is ignored — de-instance that copy instead.

> [!VERSION] Verified on USD 26.08. `GetMaster()` was renamed `GetPrototype()` in USD 21.x and is absent from this wheel.

## Steps
1. A and B are both instanceable **and** instances.
2. `GetMaster exists: False`. One prototype `/__Prototype_1`; A and B share it.
3. `Traverse` lists `/Room/A` and `/Room/B` but **not** `/Room/A/Seat`.
4. The proxy Seat is valid; source `Set(3)` updates **both**.
5. De-instance B and set size 9: A stays 3, B is 9 and `IsInstance` False.

## Full script (identical to `lab23_native_instancing.py`)

```python
"""Lab 23 — Native instancing: prototypes, proxies, de-instance."""
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
UsdGeom.Xform.Define(stage, "/Chair")
UsdGeom.Cube.Define(stage, "/Chair/Seat").GetSizeAttr().Set(1.0)
a = stage.DefinePrim("/Room/A")
a.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
a.SetInstanceable(True)
b = stage.DefinePrim("/Room/B")
b.GetReferences().AddInternalReference(Sdf.Path("/Chair"))
b.SetInstanceable(True)
print("A IsInstanceable/IsInstance:", a.IsInstanceable(), a.IsInstance())
print("B IsInstanceable/IsInstance:", b.IsInstanceable(), b.IsInstance())
print("GetMaster exists:", hasattr(Usd.Prim, "GetMaster"))
print("prototypes:", [str(p.GetPath()) for p in stage.GetPrototypes()])
print("A proto is B proto:", a.GetPrototype() == b.GetPrototype())
print("Traverse:", [str(p.GetPath()) for p in stage.Traverse()])
seat = stage.GetPrimAtPath("/Room/A/Seat")
print("proxy Seat valid:", seat.IsValid(),
      "IsInstanceProxy:", seat.IsInstanceProxy())
print("shared size:", seat.GetAttribute("size").Get())
stage.GetPrimAtPath("/Chair/Seat").GetAttribute("size").Set(3.0)
print("after source A,B:",
      stage.GetPrimAtPath("/Room/A/Seat").GetAttribute("size").Get(),
      stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Get())
b.SetInstanceable(False)
stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Set(9.0)
print("after B unique A,B:",
      stage.GetPrimAtPath("/Room/A/Seat").GetAttribute("size").Get(),
      stage.GetPrimAtPath("/Room/B/Seat").GetAttribute("size").Get(),
      "B IsInstance", b.IsInstance())
```

**Expected output**
```text
A IsInstanceable/IsInstance: True True
B IsInstanceable/IsInstance: True True
GetMaster exists: False
prototypes: ['/__Prototype_1']
A proto is B proto: True
Traverse: ['/Chair', '/Chair/Seat', '/Room', '/Room/A', '/Room/B']
proxy Seat valid: True IsInstanceProxy: True
shared size: 1.0
after source A,B: 3.0 3.0
after B unique A,B: 3.0 9.0 B IsInstance False
```

## Check your understanding
1. Where do you author `instanceable = true`?
2. Why is `/Room/A/Seat` missing from `Traverse()`?
3. Does de-instancing B also de-instance A?

**Answers**
1. On each **referencing** prim that should share a prototype — not only on `/Chair`.
2. Default traversal **does not walk into instances**. Use `GetPrimAtPath` or `Usd.TraverseInstanceProxies`.
3. **No.** Only B leaves the prototype. A stays an instance at size 3.

## Stretch challenge
While B is still instanceable, try `Set(9)` on `/Room/B/Seat`. Solution: the write is ignored or does not stick on the proxy; de-instance first (Ch 24.4).
