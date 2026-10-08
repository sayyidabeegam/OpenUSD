# Lab 31 — Codeless custom schema (`schema.usda` vs registry)

**Domain / objectives:** Customizing USD 3.4, 3.6 · **Chapter:** 37 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Show **`usdGenSchema` is missing** from usd-core, that **Cube is registered** (fallback size 2), that **`MaterialBindingAPI` is an applied API**, and that **parsing `schema.usda` does not register `Door`**.

## Background
A custom schema starts as **`schema.usda`**: `over "GLOBAL"` with `libraryName` / `skipCodeGeneration`, plus `class` prims that inherit `</Typed>` or `</APISchemaBase>` (Ch 37). **`usdGenSchema`** turns that into plugin files. **Parse ≠ register.** Codeless still needs generated USDA + `plugInfo.json`; it only skips C++ wrappers. This wheel already contains Pixar's Cube. `FindConcretePrimDefinition("Door")` stays `None` until a plugin loads.

> [!VERSION] Verified on USD 26.08: `shutil.which("usdGenSchema")` is `None`.

## Steps
1. `usdGenSchema None`. Cube registered; size fallback `2.0`; `IsConcrete` True.
2. `MaterialBindingAPI` is an applied API schema.
3. Door is **not** registered.
4. Sdf parses `GLOBAL` and `Door`; `skipCodeGeneration` is True; Door **still** unregistered.

## Full script (identical to `lab31_codeless_schema.py`)

```python
"""Lab 31 — schema.usda parses; SchemaRegistry needs usdGenSchema."""
import shutil
from pxr import Sdf, Usd

print("usdGenSchema", shutil.which("usdGenSchema"))
sr = Usd.SchemaRegistry()
print("Cube registered",
      sr.FindConcretePrimDefinition("Cube") is not None)
print("Cube size fallback",
      sr.FindConcretePrimDefinition("Cube").GetAttributeFallbackValue(
          "size"))
print("IsConcrete Cube", sr.IsConcrete("Cube"))
print("IsAppliedAPISchema MaterialBindingAPI",
      sr.IsAppliedAPISchema("MaterialBindingAPI"))
print("Door registered",
      sr.FindConcretePrimDefinition("Door") is not None)

lyr = Sdf.Layer.CreateAnonymous(".usda")
lyr.ImportFromString("""#usda 1.0
over "GLOBAL" (
    customData = {
        string libraryName = "studio"
        bool skipCodeGeneration = 1
    }
)
{
}
class "Door" (
    inherits = </Typed>
)
{
    bool sliding = 0
}
""")
print("parsed classes:", [p.name for p in lyr.rootPrims])
print("skipCodeGeneration",
      lyr.GetPrimAtPath("/GLOBAL").customData.get("skipCodeGeneration"))
print("Door still unregistered",
      sr.FindConcretePrimDefinition("Door") is None)
```

**Expected output**
```text
usdGenSchema None
Cube registered True
Cube size fallback 2.0
IsConcrete Cube True
IsAppliedAPISchema MaterialBindingAPI True
Door registered False
parsed classes: ['GLOBAL', 'Door']
skipCodeGeneration True
Door still unregistered True
```

## Check your understanding
1. If Sdf parses `schema.usda`, can you `def Door` in usdview?
2. Does codeless mean no `plugInfo.json`?
3. What is Cube's fallback `size`?

**Answers**
1. **No.** Parse ≠ register. You need `usdGenSchema` output loaded as a plugin.
2. **No.** Codeless skips **C++ wrappers**. JSON + generated USDA still ship.
3. **2.0** from the built-in concrete definition.

## Stretch challenge
`sr.IsTyped("Cube")` and `sr.IsTyped("MaterialBindingAPI")`. Solution: Cube True (IsA type); MaterialBindingAPI False (applied API, Ch 37.4).
