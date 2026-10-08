# Chapter 30 — Validating USD Assets

> **Exam domain:** Data Exchange (15%) · **Objectives:** 4.6 · **Study day:** 9 · **Est. time:** 90 min
> **Prerequisites:** Ch 2 (stage metadata), Ch 13 (extents), Ch 27 (validate step), Ch 29 (exporter hooks)

Obj 4.6 is "write a validator for the integrity of an OpenUSD asset exported from a DCC." This chapter shows why, how `usdchecker` fits, the **UsdValidation** framework on USD 26.08, what happened to `ComplianceChecker`, and a pipeline checker you can actually run with `usd-core`.

## Learning goals

- Explain why export without validation ships broken `defaultPrim`, units, and extents.
- Describe `usdchecker` and its Python equivalent on `usd-core`.
- Load built-in validators by name and read `ValidationError` fields.
- State that `UsdUtils.ComplianceChecker` is gone in 26.08.
- Write a small integrity checker for `defaultPrim`, `upAxis`, `metersPerUnit`, and extents (Obj 4.6).

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Validator** | A named check that inspects a stage (or prims/layers) and returns errors |
| **`UsdValidation`** | The `pxr` module for validators, errors, and fixers (USD 24.08+) |
| **`ValidationRegistry`** | Catalog of installed validators and suites |
| **`ValidationError`** | One finding: name, type (Error/Warn/Info), message, sites |
| **`ValidationContext`** | A bundle of validators you run together |
| **`usdchecker`** | CLI that runs UsdValidation on a file (full USD builds; not in `usd-core`) |
| **`ComplianceChecker`** | Legacy Python class **removed in 26.08** |
| **Integrity checker** | Studio code that asks "is this published asset usable?" |

---

## 30.1 Why validate

### 1. What is it?

**Validation** is running automated checks on a USD asset after export (or before publish) so missing metadata, broken references, and illegal bindings are caught before another department opens the file.

### 2. Why do we need it?

Exporters forget `upAxis`, `metersPerUnit`, `defaultPrim`, and `extent` (Chapters 28–29). Those files "open" but frame wrong, cannot be referenced, or fail in usdview. A human spot-check does not scale. Obj 4.6 wants a **written** checker, not a hope.

### 3. Beginner explanation

Validation is the **weigh-station after the truck is loaded**. The crate is already on the truck (the layer exists). The station asks: do you have a destination (`defaultPrim`)? Did you write the scale (`metersPerUnit`)? Is the box labeled up (`upAxis`)?

*Where the analogy breaks:* a weigh-station that silently throws cargo overboard is a bad hook (Chapter 29). Validators **report**. You fix the exporter, then run them again.

### 4. Technical explanation

Typical integrity questions:

| Question | Built-in validator (26.08) |
|----------|----------------------------|
| `upAxis` and `metersPerUnit` authored? | `usdGeomValidators:StageMetadataChecker` |
| `defaultPrim` valid? | `usdValidation:StageMetadataChecker` |
| References resolve? | `usdUtilsValidators:MissingReferenceValidator` |
| Material bind applied `MaterialBindingAPI`? | `usdShadeValidators:MaterialBindingApiAppliedValidator` |

A DCC exporter should run these (and your studio checks) in the **validate** step after hooks (Chapter 29). Fail the publish if `GetType()` is `Error`.

### 5. Mental model

```text
  export --> hooks --> [ validators ] --errors--> fix exporter
                            |
                          clean --> publish
```

### 6. Simple example

A stage with only `def Sphere "Ball"` produces three errors: missing meters, missing up axis, missing defaultPrim. After setting those three, the same validators return nothing.

### 7. USDA example

*File: bad.usda — opens, but fails integrity*

```usda
#usda 1.0

def Sphere "Ball"
{
    double radius = 1
}
```

*File: good.usda*

```usda
#usda 1.0
(
    defaultPrim = "Ball"
    metersPerUnit = 1
    upAxis = "Y"
)

def Sphere "Ball"
{
    double radius = 1
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdValidation

reg = UsdValidation.ValidationRegistry()
geom = reg.GetOrLoadValidatorByName(
    "usdGeomValidators:StageMetadataChecker")
core = reg.GetOrLoadValidatorByName(
    "usdValidation:StageMetadataChecker")

stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/Ball")
print("before:")
for validator in (geom, core):
    for err in validator.Validate(stage):
        print(err.GetName(), err.GetType())

UsdGeom.SetStageUpAxis(stage, "Y")
UsdGeom.SetStageMetersPerUnit(stage, 1)
stage.SetDefaultPrim(stage.GetPrimAtPath("/Ball"))
print("after geom/core counts:",
      len(list(geom.Validate(stage))),
      len(list(core.Validate(stage))))
```

**Expected output**

```text
before:
MissingMetersPerUnitMetadata UsdValidation.ValidationErrorType.Error
MissingUpAxisMetadata UsdValidation.ValidationErrorType.Error
MissingDefaultPrim UsdValidation.ValidationErrorType.Error
after geom/core counts: 0 0
```

Do not print `GetMessage()` in tests that use anonymous layers: the message embeds the layer identifier, which changes.

### 9. Real-world use case

A game studio's publish server rejects any component that fails `StageMetadataChecker` or has `UnresolvableDependency`. Artists see the error names in the DCC export log, not a late-night "the chair is two kilometers tall" ticket.

### 10. Common mistakes

> [!MISTAKE] Validating only in usdview by eye. Automation is the objective.

> [!MISTAKE] Treating warnings as leftover noise. Read `GetType()`: `Error` fails the publish; `Warn` / `Info` may still be policy.

### 11. Exam traps

> [!TRAP] "If `Stage.Open` succeeded, the asset is valid." Open succeeds with missing metadata and with unresolved references (composition errors).

> [!TRAP] "One StageMetadataChecker does everything." There are two: geom (units/up) and usdValidation (defaultPrim).

### 12. Practice questions

**DE-030a** · Obj 4.6 · Difficulty: Easy · Type: Select two.
A Sphere stage with no layer metadata fails:

A. `MissingUpAxisMetadata`
B. `MissingMetersPerUnitMetadata`
C. `MissingDefaultPrim` from the *geom* checker
D. `GetMaster` missing

**DE-030b** · Obj 4.6 · Difficulty: Medium · Type: Single choice
Which checker reports a missing `defaultPrim` on USD 26.08?

A. `usdGeomValidators:StageMetadataChecker`
B. `usdValidation:StageMetadataChecker`
C. `UsdUtils.ComplianceChecker`
D. `Tf.MakeValidIdentifier`

**Answers**

**DE-030a — A and B.** `MissingDefaultPrim` comes from the other checker (B in 030b). Review: §30.1.

**DE-030b — B.** Review: §30.1, §30.3.

### 13. Exam takeaways

> [!KEY]
> - Validation reports integrity; it does not open-or-fail the stage.
> - Two StageMetadata checkers: units/up vs defaultPrim.
> - Run validators after exporter hooks.
> - Obj 4.6 = write (or run) these checks on DCC exports.

---

## 30.2 `usdchecker`

### 1. What is it?

**`usdchecker`** is the command-line tool that runs UsdValidation on a USD file and prints errors. Full OpenUSD builds ship it. **`usd-core` does not.**

### 2. Why do we need it?

Build servers and exam reading lists name `usdchecker`. You must know the command, what it uses internally, and the Python stand-in for this book's environment.

### 3. Beginner explanation

`usdchecker` is the **same weigh-station as a CLI**: you pass a file, it prints Error/Warn lines. Under the hood since USD 26.03 it calls UsdValidation, not the old ComplianceChecker.

*Where the analogy breaks:* flags and output format differ across USD versions. Learn the *framework* (30.3), not a screenshot of one CLI banner.

### 4. Technical explanation

```text
usdchecker asset.usda
```

- Exit code is non-zero when errors are found (typical; treat that as "the build failed").
- Since **26.03**, `usdchecker` is built on **UsdValidation**.
- On `usd-core` 26.8: no `usdchecker` binary. Equivalent:

  `ValidationContext([v1, v2, ...]).Validate(stage)`

> [!VERSION] Verified on USD 26.08. `usdchecker` switched to UsdValidation in 26.03. Older study material still says it wraps `UsdUtils.ComplianceChecker` — that path is gone (30.4).

### 5. Mental model

```text
  full USD:     usdchecker file.usda   -->  UsdValidation
  usd-core:     ValidationContext.Validate(stage)  -->  same errors
```

### 6. Simple example

`usdchecker good.usda` is quiet. `usdchecker bad.usda` prints `MissingUpAxisMetadata` and friends. The Python block below is the `usd-core` stand-in.

### 7. USDA example

Use `good.usda` / `bad.usda` from 30.1. The CLI takes those files. The checker script parses USDA; it does not run the CLI.

### 8. Python example

`usdchecker` itself is not runnable with `usd-core`. This is the equivalent:

```python
from pxr import Usd, UsdGeom, UsdValidation

reg = UsdValidation.ValidationRegistry()
ctx = UsdValidation.ValidationContext([
    reg.GetOrLoadValidatorByName(
        "usdGeomValidators:StageMetadataChecker"),
    reg.GetOrLoadValidatorByName(
        "usdValidation:StageMetadataChecker"),
])

stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/Ball")
print("usdchecker-equivalent errors:")
for err in ctx.Validate(stage):
    print(err.GetName())
```

**Expected output**

```text
usdchecker-equivalent errors:
MissingMetersPerUnitMetadata
MissingUpAxisMetadata
MissingDefaultPrim
```

The CLI invocation (not run here) looks like:

```{.bash .norun}
usdchecker bad.usda
```

### 9. Real-world use case

CI runs `usdchecker` on every published `*_component.usda`. Developers without the CLI run the same two validators in a pytest using `usd-core`.

### 10. Common mistakes

> [!MISTAKE] Assuming `pip install usd-core` gave you `usdchecker`. It did not (F5, V-001).

> [!MISTAKE] Grepping CLI help from a 24.x blog and expecting ComplianceChecker flags.

### 11. Exam traps

> [!TRAP] "`usdchecker` is a Hydra tool." It is a validation CLI.

> [!TRAP] "You cannot validate without usdchecker." Python UsdValidation is the API.

### 12. Practice questions

**DE-030c** · Obj 4.6 · Difficulty: Easy · Type: Single choice
On `usd-core` 26.8, `usdchecker` is:

A. On the PATH
B. Not installed; use `UsdValidation` in Python
C. Named `usdview --check`
D. `UsdUtils.ComplianceChecker`

**DE-030d** · Obj 4.6 · Difficulty: Medium · Type: Single choice
Since USD 26.03, `usdchecker` is powered by:

A. `ComplianceChecker`
B. UsdValidation
C. `Tf.MallocTag`
D. Alembic

**Answers**

**DE-030c — B.** Review: §30.2, F5.

**DE-030d — B.** Review: §30.2.

### 13. Exam takeaways

> [!KEY]
> - `usdchecker file.usda` on full builds.
> - 26.03+: UsdValidation under the hood.
> - `usd-core`: `ValidationContext.Validate`.
> - Same error names either way.

---

## 30.3 The UsdValidation framework

### 1. What is it?

**`pxr.UsdValidation`** is the library: a **registry** of validators, **errors** they return, optional **fixers**, and a **context** that runs several validators at once.

### 2. Why do we need it?

Obj 4.6 on a modern USD means this API, not a home-grown print loop only. Built-in checks already cover metadata, missing references, and material-binding schema application.

### 3. Beginner explanation

The registry is a **phone book** of inspectors. You look up `"usdGeomValidators:StageMetadataChecker"`, ask it to `Validate(stage)`, and get a list of tickets (`ValidationError`). A context is several inspectors walking the site together.

*Where the analogy breaks:* some validators are time-dependent (`isTimeDependent` on metadata). Most asset-integrity checks are not.

### 4. Technical explanation

Verified on USD 26.08 (`usd-core` ships **28** validators):

| Class | Role |
|-------|------|
| `ValidationRegistry` | `GetOrLoadValidatorByName`, `GetAllValidatorMetadata`, `HasValidator` |
| `Validator` | `Validate(stage)` → errors; `GetMetadata()` |
| `ValidationError` | `GetName()`, `GetMessage()`, `GetType()`, `GetErrorAsString()`, `GetSites()`, `GetIdentifier()` |
| `ValidationErrorType` | `Error`, `Warn`, `Info`, `None_` |
| `ValidationContext` | `ValidationContext([v1, v2]).Validate(stage)` |
| `ValidationFixer` | Optional auto-fix attached to an error (`GetFixers`) |
| `ValidatorSuite` | Named group; `GetOrLoadAllValidatorSuites()` may be empty on `usd-core` |

Names are `plugin:ValidatorName`. Useful ones for exporters:

- `usdGeomValidators:StageMetadataChecker`
- `usdValidation:StageMetadataChecker`
- `usdUtilsValidators:MissingReferenceValidator` → `UnresolvableDependency`
- `usdShadeValidators:MaterialBindingApiAppliedValidator`

`RegisterPrimValidator` / `RegisterStageValidator` exist for **plugins**. Passing a Python `lambda` does **not** match the C++ signature on 26.08. Studio checkers in Python are ordinary functions (30.5) unless you ship a C++/plugin validator.

> [!VERSION] UsdValidation first phase / registry in 24.08; Python bindings for validator types in 24.11; separate `pxr.UsdValidation` library (and `ValidationContext` Python wrappings) in 25.02. This book verifies 26.08.

### 5. Mental model

```text
  Registry.GetOrLoadValidatorByName("plugin:Name")
                 |
                 v
           validator.Validate(stage)
                 |
                 v
           [ ValidationError, ... ]
              GetName / GetType / GetMessage
```

### 6. Simple example

Ask the registry how many validators exist and whether the two metadata checkers and the missing-reference checker are present. Run a context on a complete Sphere: no errors.

### 7. USDA example

No new syntax. Validators read the composed stage produced from any USDA in this chapter.

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdValidation

reg = UsdValidation.ValidationRegistry()
names = sorted(m.name for m in reg.GetAllValidatorMetadata())
print("nValidators:", len(names))
for needle in (
        "StageMetadataChecker",
        "MissingReferenceValidator",
        "MaterialBindingApiAppliedValidator"):
    print(needle, ":", [n for n in names if needle in n])

geom = reg.GetOrLoadValidatorByName(
    "usdGeomValidators:StageMetadataChecker")
core = reg.GetOrLoadValidatorByName(
    "usdValidation:StageMetadataChecker")
stage = Usd.Stage.CreateInMemory()
UsdGeom.Sphere.Define(stage, "/Ball")
UsdGeom.SetStageUpAxis(stage, "Y")
UsdGeom.SetStageMetersPerUnit(stage, 1)
stage.SetDefaultPrim(stage.GetPrimAtPath("/Ball"))
ctx = UsdValidation.ValidationContext([geom, core])
print("context errors:", [e.GetName() for e in ctx.Validate(stage)])
print("ErrorType values:",
      [v.name for v in UsdValidation.ValidationErrorType.allValues])
```

**Expected output**

```text
nValidators: 28
StageMetadataChecker : ['usdGeomValidators:StageMetadataChecker', 'usdValidation:StageMetadataChecker']
MissingReferenceValidator : ['usdUtilsValidators:MissingReferenceValidator']
MaterialBindingApiAppliedValidator : ['usdShadeValidators:MaterialBindingApiAppliedValidator']
context errors: []
ErrorType values: ['None_', 'Error', 'Warn', 'Info']
```

### 9. Real-world use case

A pipeline registers extra C++ validators under `studioValidators:KindChecker` via `plugInfo.json` (Chapter 36). The same `ValidationContext` list in CI includes both Pixar names and studio names.

### 10. Common mistakes

> [!MISTAKE] Hard-coding `GetMessage()` in tests. Messages include layer identifiers. Assert `GetName()` and `GetType()`.

> [!MISTAKE] Expecting suites to be populated on `usd-core`. `GetOrLoadAllValidatorSuites()` returned none here; load validators by name.

### 11. Exam traps

> [!TRAP] "`Validate` writes a report layer." It returns error objects. Nothing is authored.

> [!TRAP] "MaterialBindingApiAppliedValidator is a geom validator." It is `usdShadeValidators:`.

### 12. Practice questions

**DE-030e** · Obj 4.6 · Difficulty: Medium · Type: Single choice
`ValidationError.GetType()` for missing `upAxis` is:

A. `Warn`
B. `Error`
C. `Info`
D. `None_`

**DE-030f** · Obj 4.6 · Difficulty: Easy · Type: Select two.
Methods on `ValidationError` include:

A. `GetName`
B. `GetMessage`
C. `Flatten`
D. `GetMaster`

**Answers**

**DE-030e — B.** Review: §30.1.

**DE-030f — A and B.** Review: §30.3.

### 13. Exam takeaways

> [!KEY]
> - Registry → named validator → `Validate` → errors.
> - Context runs several validators.
> - Assert `GetName()`, not the layer path in the message.
> - Python cannot `Register*Validator(lambda)` on 26.08; use a function (30.5) or a plugin.

---

## 30.4 Legacy: `UsdUtils.ComplianceChecker`

### 1. What is it?

**`UsdUtils.ComplianceChecker`** was the old Python class `usdchecker` used before UsdValidation. **It is not in USD 26.08.**

### 2. Why do we need it?

Exam reading lists and older NVIDIA material still mention it. You must recognize the name, know it is gone, and pick UsdValidation instead — not invent a call that will `AttributeError`.

### 3. Beginner explanation

ComplianceChecker is a **retired inspector**. The office directory still lists the name. The person has left. Ask for UsdValidation.

*Where the analogy breaks:* some studios still run USD 24.x in production. Their docs are not wrong *for that version*. This book and the 26.08 runtime do not have the class.

### 4. Technical explanation

| Release | Fact |
|---------|------|
| 26.03 | `usdchecker` built on UsdValidation; ComplianceChecker dropped from the CLI |
| 26.05 | ComplianceChecker warns when used |
| **26.08** | **Removed entirely** from `UsdUtils` |

The next snippet is a fragment (no import); the runnable check is in step 8.

```{.python .norun}
hasattr(UsdUtils, "ComplianceChecker")  # False on 26.08
```

If a question shows `UsdUtils.ComplianceChecker()`, the current-correct action is "use `UsdValidation.ValidationRegistry`."

> [!VERSION] Verified on USD 26.08: `hasattr(UsdUtils, "ComplianceChecker")` is False. Do not use it in runnable examples.

### 5. Mental model

```text
  24.x  usdchecker  -->  ComplianceChecker
  26.03 usdchecker  -->  UsdValidation
  26.08 Python      -->  UsdValidation only  (no ComplianceChecker)
```

### 6. Simple example

`from pxr import UsdUtils` then `hasattr(UsdUtils, "ComplianceChecker")` prints `False`.

### 7. USDA example

None. This is an API-history fact, not a file format.

### 8. Python example

```python
from pxr import UsdUtils

print("ComplianceChecker:", hasattr(UsdUtils, "ComplianceChecker"))
```

**Expected output**

```text
ComplianceChecker: False
```

### 9. Real-world use case

A studio upgrading from 24.11 to 26.08 deletes `ComplianceChecker` imports from their publish script and loops `ValidationRegistry().GetOrLoadValidatorByName(...)` instead. The error *names* change; the policy (fail on missing defaultPrim) stays.

### 10. Common mistakes

> [!MISTAKE] Copy-pasting `ComplianceChecker()` from a 2024 blog into a 26.08 environment. It raises `AttributeError`.

### 11. Exam traps

> [!TRAP] A distractor that still says "call ComplianceChecker." That is the legacy answer. Prefer UsdValidation.

> [!TRAP] "Removed means validation is gone." The replacement is UsdValidation.

### 12. Practice questions

**DE-030g** · Obj 4.6 · Difficulty: Easy · Type: Single choice
On USD 26.08, `UsdUtils.ComplianceChecker` is:

A. The required API for Obj 4.6
B. Absent
C. Renamed `GetMaster`
D. A Hydra delegate

**DE-030h** · Obj 4.6 · Difficulty: Medium · Type: Single choice
An old script calls `ComplianceChecker()`. You should:

A. Ignore validation
B. Switch to `UsdValidation` validators
C. Install `usdview` only
D. Set `PXR_PLUGINPATH_NAME` to restore it

**Answers**

**DE-030g — B.** Review: §30.4.

**DE-030h — B.** Review: §30.4, §30.3.

### 13. Exam takeaways

> [!KEY]
> - ComplianceChecker is removed in 26.08.
> - Replacement: UsdValidation.
> - Older material is a version trap, not current code.

---

## 30.5 Writing your own validator

### 1. What is it?

A **studio integrity checker** is a function you write that inspects a stage and returns problem strings (or `ValidationError`s if you ship a plugin). Obj 4.6 is satisfied by a real checker that a DCC exporter can call.

### 2. Why do we need it?

Built-ins do not know that *your* components must have `kind = component` and an authored `extent`. That is pipeline policy. You write it.

### 3. Beginner explanation

Built-in validators are **city fire codes**. Your function is the **factory's own checklist**: every shipped crate has a default lid, a stamped size, and a kind label.

*Where the analogy breaks:* you may later wrap the same rules in a C++ UsdValidation plugin so `usdchecker` runs them. Until then, a Python function in the exporter's validate step is enough and is what `usd-core` can run.

### 4. Technical explanation

A practical Obj 4.6 checker (verified):

1. `defaultPrim` is set.
2. Root layer has `upAxis` and `metersPerUnit` (`pseudoRoot.HasInfo`).
3. Every Boundable with `kind == component` has an authored `extent`.

Call it after hooks (Chapter 29.6). Non-empty list → fail the export.

You can add: legal identifiers, `factory:partId` present, no `UnresolvableDependency` from `MissingReferenceValidator`, `MaterialBindingAPI` applied when a `material:binding` exists.

Plugin path (not runnable as a lambda on 26.08): implement a C++/Python plugin, `RegisterStageValidator` with the metadata the C++ signature expects, ship `plugInfo.json` (Chapters 36–37).

### 5. Mental model

```text
  pipeline_check(stage) -> ["missing defaultPrim", "no extent on /Crate", ...]
  empty list            -> publish
```

### 6. Simple example

A Mesh `/Crate` with `kind = component` and nothing else fails four ways: defaultPrim, upAxis, metersPerUnit, extent. An Xform root with metadata and `defaultPrim` passes (Xform is not Boundable, so no extent demand).

### 7. USDA example

*The failing input:*

```usda
#usda 1.0

def Mesh "Crate" (
    kind = "component"
)
{
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom


def pipeline_check(stage):
    problems = []
    if not stage.GetDefaultPrim():
        problems.append("missing defaultPrim")
    root = stage.GetRootLayer()
    if not root.pseudoRoot.HasInfo("upAxis"):
        problems.append("missing upAxis")
    if not root.pseudoRoot.HasInfo("metersPerUnit"):
        problems.append("missing metersPerUnit")
    for prim in stage.Traverse():
        if (prim.GetMetadata("kind") == "component"
                and prim.IsA(UsdGeom.Boundable)):
            ext = UsdGeom.Boundable(prim).GetExtentAttr()
            if not ext.HasAuthoredValue():
                problems.append(f"no extent on {prim.GetPath()}")
    return problems


bad = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(bad, "/Crate")
mesh.GetPrim().SetMetadata("kind", "component")
print("bad:", pipeline_check(bad))

good = Usd.Stage.CreateInMemory()
UsdGeom.SetStageUpAxis(good, "Y")
UsdGeom.SetStageMetersPerUnit(good, 1)
root = UsdGeom.Xform.Define(good, "/Crate")
good.SetDefaultPrim(root.GetPrim())
root.GetPrim().SetMetadata("kind", "component")
print("good:", pipeline_check(good))
```

**Expected output**

```text
bad: ['missing defaultPrim', 'missing upAxis', 'missing metersPerUnit', 'no extent on /Crate']
good: []
```

This is a validator you can attach to a DCC export. Lab 27 expands it.

### 9. Real-world use case

A CAD exporter calls `pipeline_check` plus `MissingReferenceValidator`. The CAD GUI lists the four strings above next to the export button. Artists learn to fill metadata because the button stays red otherwise.

### 10. Common mistakes

> [!MISTAKE] Demanding `extent` on Xforms. Xform is not Boundable. Check `IsA(UsdGeom.Boundable)`.

> [!MISTAKE] Using schema fallback (`HasValue()`) as "authored extent." Fallback is not an authored opinion. Use `HasAuthoredValue()`.

### 11. Exam traps

> [!TRAP] "Obj 4.6 requires `usdGenSchema`." That is custom schemas (Ch 37). A checker function is a validator.

> [!TRAP] "You must `RegisterPrimValidator` from Python for the exam answer to count." The objective is integrity of the asset. A function that returns problems counts; plugins are the production wrap.

### 12. Practice questions

**DE-030i** · Obj 4.6 · Difficulty: Medium · Type: Select two.
A component Mesh with no metadata and no extent should fail a studio checker for:

A. missing `defaultPrim` / stage metrics
B. missing authored `extent`
C. missing `/__Prototype_1`
D. `GetMaster`

**DE-030j** · Obj 4.6 · Difficulty: Easy · Type: Single choice
`pipeline_check` should run:

A. Before extract
B. After write/hooks, before publish
C. Instead of composition
D. Only inside usdview

**Answers**

**DE-030i — A and B.** Review: §30.5.

**DE-030j — B.** Review: §30.5, Ch 29.

### 13. Exam takeaways

> [!KEY]
> - Obj 4.6: a real function (or plugin) that flags unusable exports.
> - Check `defaultPrim`, units, upAxis, extents on Boundable components.
> - Combine with built-in UsdValidation names.
> - Python lambdas cannot `Register*Validator` on 26.08; plugins or plain functions.

---

## Chapter lab(s)

Lab 27 (asset validator) is this chapter's lab: wrap `pipeline_check` plus `MissingReferenceValidator` around the Lab 25 converter output.

## USDA reading exercises

**Exercise 30-A.** `bad.usda` from 30.1 is opened and both StageMetadata checkers run. List the three `GetName()` values.

**Exercise 30-B.** A Mesh `/Crate` has `kind = component`, `defaultPrim`, `upAxis`, and `metersPerUnit`, but no `extent`. What does `pipeline_check` report?

**Answers**

**30-A.** `MissingMetersPerUnitMetadata`, `MissingUpAxisMetadata`, `MissingDefaultPrim`.

**30-B.** `['no extent on /Crate']`.

---

## Chapter review

### Summary

- Validate after export so missing metadata and broken refs never publish.
- `usdchecker` = CLI on full builds; UsdValidation is the library; `usd-core` has no CLI.
- Two StageMetadata checkers (geom units/up, usdValidation defaultPrim).
- `ValidationRegistry`, `Validator.Validate`, `ValidationContext`, error `GetName`/`GetType`.
- `ComplianceChecker` removed in 26.08.
- Write `pipeline_check` (Obj 4.6); add built-in validators for refs and bindings.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Obj 4.6 | Integrity checker + UsdValidation |
| `usdchecker` | CLI; 26.03+ UsdValidation; missing in usd-core |
| `ComplianceChecker` | Legacy; gone in 26.08 |
| `MissingDefaultPrim` | `usdValidation:StageMetadataChecker` |
| `MissingUpAxisMetadata` | `usdGeomValidators:StageMetadataChecker` |
| `UnresolvableDependency` | `usdUtilsValidators:MissingReferenceValidator` |
| `MaterialBindingApiAppliedValidator` | Bindings need `Apply` |
| Anonymous layer in `GetMessage()` | Assert `GetName()` instead |

### Review questions

**R30-01** · Obj 4.6 · Single choice
`Stage.Open` of a file with no `upAxis`:
A. Always raises
B. Succeeds; validation reports `MissingUpAxisMetadata`
C. Creates a payload
D. Sets Y automatically and errors

**R30-02** · Obj 4.6 · Select two.
USD 26.08 metadata checkers:
A. `usdGeomValidators:StageMetadataChecker`
B. `usdValidation:StageMetadataChecker`
C. `UsdUtils.ComplianceChecker`
D. `GetMaster`

**R30-03** · Obj 4.6 · Single choice
`usd-core` includes:
A. `usdchecker` binary
B. `pxr.UsdValidation`
C. `ComplianceChecker`
D. usdview

**R30-04** · Obj 4.6 · Single choice
`ValidationContext([v1, v2]).Validate(stage)` returns:
A. A new layer
B. A sequence of `ValidationError`
C. `True` only
D. A prototype

**R30-05** · Obj 4.6 · Single choice
Missing-reference built-in name:
A. `usdUtilsValidators:MissingReferenceValidator`
B. `usdGeomValidators:EncapsulationChecker`
C. `Kind.Registry`
D. `Ar.Resolver`

**R30-06** · Obj 4.6 · Single choice
`ComplianceChecker` in 26.08:
A. Required
B. Removed
C. Renamed `GetPrototype`
D. A suite with 28 validators

**R30-07** · Obj 4.6 · Select two.
A studio `pipeline_check` should flag:
A. Missing `defaultPrim`
B. Component Boundable without authored extent
C. Session-layer existence
D. UTF-8 in comments

**R30-08** · Obj 4.6 · Single choice
`HasAuthoredValue()` on extent vs `HasValue()`:
A. The same
B. Authored is the integrity check; `HasValue` may be fallback
C. Authored is always True on Mesh
D. Neither exists

**R30-09** · Obj 4.6 · Single choice
Registering a Python `lambda` with `RegisterStageValidator` on 26.08:
A. Always works
B. Does not match the C++ signature
C. Replaces usdchecker
D. Enables Hydra

**R30-10** · Obj 4.6 · Single choice
When to run validation in an exporter?
A. After write and hooks, before publish
B. Before extract
C. Only on the DCC undo stack
D. Instead of `Save`

**R30-11** · Obj 4.6 · Single choice
`GetType()` for the metadata misses in 30.1:
A. `Warn`
B. `Error`
C. `Info`
D. `None_`

**R30-12** · Obj 4.6 · Single choice
`usdchecker` since 26.03 uses:
A. ComplianceChecker
B. UsdValidation
C. `Sdf.ChangeBlock`
D. PointInstancer

### Review answers

**R30-01 — B.** Review: §30.1.

**R30-02 — A and B.** Review: §30.3.

**R30-03 — B.** Review: §30.2, §30.3.

**R30-04 — B.** Review: §30.3.

**R30-05 — A.** Review: §30.3.

**R30-06 — B.** Review: §30.4.

**R30-07 — A and B.** Review: §30.5.

**R30-08 — B.** Review: §30.5.

**R30-09 — B.** Review: §30.3, §30.5.

**R30-10 — A.** Review: §30.1, §30.5.

**R30-11 — B.** Review: §30.1.

**R30-12 — B.** Review: §30.2.

## Further reading

- [S06] OpenUSD API — `UsdValidation` (ValidationRegistry, ValidationContext): https://openusd.org/release/api/index.html
- [S04] OpenUSD Glossary — usdchecker, validation: https://openusd.org/release/glossary.html
- [S14] NVIDIA Learn OpenUSD — validating assets: https://docs.nvidia.com/learn-openusd/latest/index.html
