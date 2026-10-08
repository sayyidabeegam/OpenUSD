# Lab 32 — Kind registry and an unregistered custom kind

**Domain / objectives:** Customizing USD 3.3 · **Chapter:** 38 · **Time:** 20 min · **Difficulty:** ★★☆

## Goal
Print the built-in **kind tree**, prove **`Kind.Registry.Register` does not exist**, and show that `SetKind("door")` still authors the token but **`IsComponent()` becomes False**.

## Background
Built-in kinds: `model`, `group`, `assembly`, `component`, `subcomponent` (Ch 6, 23, 38). `assembly` is-a `group` is-a `model`. `component` is-a `model` but **not** a group. `subcomponent` is **not** a model. Custom kinds are declared in **`plugInfo.json`**, not Python. `GetKind()` returns whatever token you authored; `IsComponent()` / `IsModel()` consult the registry **and** the hierarchy.

## Steps
1. `GetAllKinds()` lists the five built-ins. `HasKind("door")` is False.
2. Bases: component→model, assembly→group, group→model, model→`''`.
3. `component IsA model` True; `subcomponent IsA model` False; `component IsA group` False.
4. `has Register` False.
5. Chair with `component` is `IsComponent` True. After `SetKind("door")`, GetKind is `door` but IsComponent is **False**.

## Full script (identical to `lab32_kinds_fallbacks.py`)

```python
"""Lab 32 — Kind.Registry tree; no Python Register."""
from pxr import Kind, Usd, UsdGeom

print("all", sorted(Kind.Registry.GetAllKinds()))
print("HasKind door", Kind.Registry.HasKind("door"))
print("base component", Kind.Registry.GetBaseKind("component"))
print("base assembly", Kind.Registry.GetBaseKind("assembly"))
print("base group", Kind.Registry.GetBaseKind("group"))
print("base model", repr(Kind.Registry.GetBaseKind("model")))
print("component IsA model", Kind.Registry.IsA("component", "model"))
print("subcomponent IsA model",
      Kind.Registry.IsA("subcomponent", "model"))
print("component IsA group", Kind.Registry.IsA("component", "group"))
print("has Register", hasattr(Kind.Registry, "Register"))

stage = Usd.Stage.CreateInMemory()
chair = UsdGeom.Xform.Define(stage, "/Chair").GetPrim()
Usd.ModelAPI(chair).SetKind("component")
print("Chair IsComponent", chair.IsComponent())
Usd.ModelAPI(chair).SetKind("door")
print("kind door still GetKind", Usd.ModelAPI(chair).GetKind())
print("Chair IsComponent with door", chair.IsComponent())
```

**Expected output**
```text
all ['assembly', 'component', 'group', 'model', 'subcomponent']
HasKind door False
base component model
base assembly group
base group model
base model ''
component IsA model True
subcomponent IsA model False
component IsA group False
has Register False
Chair IsComponent True
kind door still GetKind door
Chair IsComponent with door False
```

## Check your understanding
1. How do you register a custom kind `prop` on USD 26.08 Python?
2. Is `subcomponent` a model kind?
3. Can `GetKind()` return a token the registry does not know?

**Answers**
1. You **cannot** call `Kind.Registry.Register` — it does not exist. Ship **`plugInfo.json`**.
2. **No.** `IsA("subcomponent", "model")` is False.
3. **Yes.** Metadata stores the string; `IsModel`/`IsComponent` then fail closed.

## Stretch challenge
`Kind.Registry.IsModel("assembly")` and `IsComponent("assembly")`. Solution: True and False — assembly is a group/model, not a component.
