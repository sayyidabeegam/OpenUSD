# Question Bank — Debugging and Troubleshooting (DBG)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 6.1–6.5 (Debugging, 11%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 44 questions. This file holds **DBG-001–DBG-044** (domain complete).

Work the stems first. Answers and explanations are grouped at the end.

---

**DBG-001** · Obj 6.1 · Difficulty: Easy · Type: Single choice

What does `Sdf.ChangeBlock` delay?

A. The writes themselves (nothing hits the layer until exit)
B. **Notices** (`ObjectsChanged`); specs are still authored immediately
C. Composition until `Flatten()`
D. Disk `Save()`

---

**DBG-002** · Obj 6.1 · Difficulty: Medium · Type: Single choice

Three `CreateAttribute`+`Set` pairs without a block produced how many `ObjectsChanged` notices in lab 09?

A. 3
B. **6** (create is one notice, set is another)
C. 1
D. 0

---

**DBG-003** · Obj 6.1 · Difficulty: Medium · Type: Single choice

The same lab’s two `Sdf.AttributeSpec` authors **inside** `ChangeBlock` produced how many notices?

A. 6
B. 2
C. **1**
D. 0 — Sdf cannot notify

---

**DBG-004** · Obj 6.1 · Difficulty: Medium · Type: Single choice

`UsdGeom.Sphere.Define` of a **new child** inside `Sdf.ChangeBlock` on USD 26.08?

A. Always succeeds
B. Can raise `Tf.ErrorException`; author `Sdf.PrimSpec` instead
C. Silently no-ops
D. Converts the block into Flatten

---

**DBG-005** · Obj 6.1 · Difficulty: Easy · Type: Multiple select
Select two.

When is a ChangeBlock the right performance fix (Obj 6.1)?

A. Thousands of spec edits in one burst (importers, converters)
B. A single `Set` of one attribute
C. Batching Sdf child prims so listeners see one coalesced `ObjectsChanged`
D. Replacing `MuteLayer`

---

**DBG-006** · Obj 6.1 · Difficulty: Medium · Type: Single choice

CreateAttribute then Set on `/W.a` produced two notices. Typical split?

A. Both info-only
B. First **resync** of `/W.a`, then **info-only** on `/W.a`
C. First info, then resync of the stage root
D. Notices do not distinguish resync vs info

---

**DBG-007** · Obj 6.1 · Difficulty: Easy · Type: Single choice

Unregister an `ObjectsChanged` listener with:

A. `Tf.Notice.Revoke` (that name is wrong)
B. `listener.Revoke()` (the key returned by `Tf.Notice.Register`)
C. `del notice`
D. `stage.MuteLayer`

---

**DBG-008** · Obj 6.2 · Difficulty: Medium · Type: Single choice

A TD authored `radius = 9` but usdview still shows 1. First composition debug step?

A. Reinstall Python
B. `GetPropertyStack` / `GetPrimStack` (strongest first) and check mute, edit target, LIVERPS, variant selection
C. `MallocTag.GetTotalBytes()`
D. Convert to OBJ

---

**DBG-009** · Obj 6.2 · Difficulty: Medium · Type: Multiple select
Select two.

Opinions that **do not take effect** often sit in which traps?

A. Muted layer; weaker arc (specialize vs reference); instance **proxy** nested over
B. Weaker time samples beating a **stronger** default (they do not)
C. Wrong edit target; local opinion beating a variant; relocate **source** path
D. `formatId usd` on a `.usd` crate file

---

**DBG-010** · Obj 6.2 · Difficulty: Medium · Type: Single choice

`OverridePrim` on `/Room/A/Seat` while `/Room/A` is instanceable. Debug result?

A. Per-instance size wins
B. `Tf.ErrorException`: authoring to an instance proxy is not allowed
C. Silent prototype edit
D. `GetMaster()` fixes it

---

**DBG-011** · Obj 6.2 · Difficulty: Medium · Type: Single choice

Variant `size=big` authors `height=3`; the prim also has local `height=1`. Composed height is 1. Debug lesson?

A. Variants beat local
B. **L beats V**; the “variant did nothing” report is LIVERPS, not a broken variant set
C. USD averaged 2
D. Need OpenMasked

---

**DBG-012** · Obj 6.2 · Difficulty: Easy · Type: Single choice

`GetPrimStack()` order?

A. Weakest first
B. **Strongest first**
C. Alphabetical
D. Payloads only

---

**DBG-013** · Obj 6.2 · Difficulty: Medium · Type: Single choice

Session layer has `radius=9`, root has `1`. Composed is 9 but `Save()` of the root still writes 1. Debug?

A. Composition is broken
B. Session opinions are **not** in the root file; inspect session / change edit target before Save
C. Mute the session to publish 9 into the root automatically
D. Flatten is the only Save

---

**DBG-014** · Obj 6.3 · Difficulty: Medium · Type: Single choice

`AddReference("no_such_file.usda")` composition error type?

A. `UnresolvedPrimPath`
B. `InvalidAssetPath` (missing file)
C. None; returns False
D. `Tf.MallocTag`

---

**DBG-015** · Obj 6.3 · Difficulty: Medium · Type: Single choice

File exists but has no `defaultPrim` and the reference omits a prim path. Error type?

A. `InvalidAssetPath`
B. `UnresolvedPrimPath`
C. `ErrorInvalidAssetPath` from Ar (no such file)
D. No error; first root prim is used

---

**DBG-016** · Obj 6.3 · Difficulty: Medium · Type: Multiple select
Select two.

`Resolve("./tex/wood.png")` is False from the wrong cwd, but the shot still renders the texture. Why can both be true?

A. Composition **anchors** `@./tex/...@` to the **layer**, not to process cwd
B. Raw `Resolve` of `./` uses cwd — a common false “missing texture” panic
C. `AnchorRelativePath` is required in 26.08
D. Search paths apply to `./` paths

---

**DBG-017** · Obj 6.3 · Difficulty: Medium · Type: Single choice

`Open("shot.usda")` without context: `@chair.usda@` (no `./`) → `ErrorInvalidAssetPath`. Fix?

A. Flatten
B. `Stage.Open(..., pathResolverContext=)` with a search path / `DefaultResolverContext`
C. `LoadNone`
D. `MuteLayer` on the shot

---

**DBG-018** · Obj 6.3 · Difficulty: Easy · Type: Single choice

`ComputeAllDependencies` third tuple slot for a missing `@./gone.jpg@`?

A. layers
B. assets (resolved)
C. **unresolved**
D. payloads only

---

**DBG-019** · Obj 6.4 · Difficulty: Medium · Type: Single choice

CAD mesh looks subdivided/smooth though points are a tessellation. Debug `subdivisionScheme`?

A. Authored `none` already
B. Fallback **`catmullClark`** if unauthored — set `none`
C. Fallback `loop`
D. Scheme is ignored by Hydra

---

**DBG-020** · Obj 6.4 · Difficulty: Medium · Type: Single choice

Points were scaled 100×; viewer still culls the mesh. Check?

A. `MallocTag`
B. Stale **`extent`**
C. `formatId`
D. `GetMaster`

---

**DBG-021** · Obj 6.4 · Difficulty: Medium · Type: Multiple select
Select two.

Mesh exists in Traverse but not in the default camera. Likely?

A. `purpose = guide` or `proxy` vs default purpose mask
B. `visibility` computed `invisible` (parent hide)
C. `ExtractExternalReferences` empty second list
D. USDA encoding

---

**DBG-022** · Obj 6.4 · Difficulty: Medium · Type: Single choice

Z-up meters chair in a Y-up cm shot looks on its side and tiny. USD converted units automatically?

A. Yes
B. **No** — debug metrics on the **asset file**, then rotateX/scale on the reference
C. Yes if referenced
D. `upAxis` on the composed stage rotates children

---

**DBG-023** · Obj 6.4 · Difficulty: Easy · Type: Single choice

UVs look flipped in a glTF viewer after export. First mapping check?

A. `v_gltf = 1 - v_usd`
B. `u_gltf = metersPerUnit`
C. Drop UVs
D. `subdivisionScheme`

---

**DBG-024** · Obj 6.5 · Difficulty: Easy · Type: Single choice

Python class that captured the missing-reference **warning** in lab 36?

A. `Tf.CoalescingDiagnosticDelegate`
B. `UsdUtils.CoalescingDiagnosticDelegate`
C. `Trace.Collector`
D. `Usd.Notice.ObjectsChanged`

---

**DBG-025** · Obj 6.5 · Difficulty: Medium · Type: Single choice

When must you construct that delegate to see `Stage.Open` warnings?

A. After Open
B. **Before** `Stage.Open`
C. After Flatten
D. Only if `usdchecker` is installed

---

**DBG-026** · Obj 6.5 · Difficulty: Medium · Type: Single choice

Lab 36 `sourceFileName` printed `stage.cpp`. How should you assert in portable tests?

A. Full absolute path equality
B. `os.path.basename(...)` — the field may be a full path
C. Ignore source entirely; it is always empty
D. It is always `usdview.cpp`

---

**DBG-027** · Obj 6.5 · Difficulty: Easy · Type: Single choice

Trace vs MallocTag?

A. Trace = bytes; MallocTag = seconds
B. Trace = **time**; MallocTag = **bytes**
C. Both measure FPS
D. Both require Hydra

---

**DBG-028** · Obj 6.5 · Difficulty: Medium · Type: Python-reading

On usd-core 26.8 lab 36: `MallocTag.Initialize()` returned False, then `IsInitialized()` True, `GetTotalBytes()`?

A. A large positive count
B. **0**
C. Raises
D. `None`

---

**DBG-029** · Obj 6.5 · Difficulty: Easy · Type: Single choice

`Trace.Collector()` default `enabled`?

A. True
B. **False**
C. None
D. Follows `TF_DEBUG`

---

**DBG-030** · Obj 6.5 · Difficulty: Medium · Type: Single choice

Enable extra change-processing logs after `import pxr`?

A. `TF_DEBUG` only works as a Python function of that name
B. `Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)`
C. `stage.SetDebug(True)`
D. `Usd.GetVersion()`

---

**DBG-031** · Obj 6.5 · Difficulty: Easy · Type: Single choice

Process-start equivalent of that switch?

A. `USD_LOG=1`
B. `TF_DEBUG=USD_CHANGES`
C. `PCP=1`
D. `HYDRA_DEBUG=1` on usd-core always

---

**DBG-032** · Obj 6.5 · Difficulty: Medium · Type: Single choice

`SetDebugSymbolsByName("NOT_A_SYMBOL", True)` on 26.08?

A. Raises
B. Returns **empty list**; unknown names are ignored
C. Creates the symbol
D. Crashes

---

**DBG-033** · Obj 6.5 · Difficulty: Medium · Type: Multiple select
Select two.

Missing `@./missing.usda@` reference. Lab 36 saw:

A. Coalescing delegate item with `TF_DIAGNOSTIC_WARNING_TYPE`
B. `len(GetCompositionErrors()) == 1`
C. `ComplianceChecker` error
D. MallocTag bytes > 0 as proof of the miss

---

**DBG-034** · Obj 6.2 · Difficulty: Hard · Type: Single choice

Stronger sublayer default `radius=5`; weaker sublayer has samples. `Get(10)` is 5 and `GetTimeSamples()` is `[]`. Debug?

A. Samples always win
B. Stronger **default wins at all times**; weaker samples do not leak
C. Need Held interpolation
D. Bug in usd-core

---

**DBG-035** · Obj 6.3 · Difficulty: Medium · Type: Single choice

`ExtractExternalReferences(shot)` lists no textures; Compute lists `wood.png`. Debug conclusion?

A. Compute is wrong
B. Extract is **one file**; textures live on a **sublayer**
C. PNG cannot be a dependency
D. Need `usdcat`

---

**DBG-036** · Obj 6.1 · Difficulty: Medium · Type: Single choice

Three `Sdf.PrimSpec` children **inside** one ChangeBlock vs three **outside**. Notice counts?

A. 3 and 3
B. **1** (all three paths) vs **3**
C. 0 and 3
D. 3 and 1

---

**DBG-037** · Obj 6.4 · Difficulty: Medium · Type: Single choice

`displayColor` interpolation `vertex` with a faceVarying-length array. Visual symptom?

A. Perfect colors
B. Wrong mapping (seams/colors); length must match interpolation
C. Stage fails to open
D. Extent becomes None

---

**DBG-038** · Obj 6.5 · Difficulty: Easy · Type: Single choice

`GetDebugSymbolDescription("USD_CHANGES")` (verified book text)?

A. `"USD change processing"`
B. `"malloc"`
C. `""`
D. Raises

---

**DBG-039** · Obj 6.2 · Difficulty: Medium · Type: Single choice

Relocate `{</Bot/Rig/Arm>: </Bot/Arm>}`. TD overs `/Bot/Rig/Arm`. Radius unchanged. Debug?

A. Relocates ignore all overs
B. Author at the **destination**; source-path opinions do not apply
C. Relocates only work on payloads
D. Need ChangeBlock

---

**DBG-040** · Obj 6.3 · Difficulty: Medium · Type: Single choice

Custom resolver missing in the DCC; identifiers fail. Checklist?

A. `PXR_PLUGINPATH_NAME` + plugin built for **this** USD version, set **before** init
B. `AnchorRelativePath`
C. `GetMaster()`
D. USDA only

---

**DBG-041** · Obj 6.4 · Difficulty: Medium · Type: Single choice

`OpenMasked` vs `LoadNone` when debugging a “missing” `/World/B` that is a **reference**?

A. They are identical
B. `LoadNone` still **loads references**; a population **mask** omits B entirely
C. `LoadNone` omits references; mask loads them
D. MuteLayer is the only tool

---

**DBG-042** · Obj 6.5 · Difficulty: Medium · Type: Single choice

`Initialize()` returning False while `IsInitialized()` becomes True means?

A. MallocTag is broken; abort
B. On this **usd-core wheel**, tagging may not count bytes (`GetTotalBytes()` 0) even though the API is “on”
C. Trace is now on
D. You must call Initialize twice

---

**DBG-043** · Obj 6.1 · Difficulty: Medium · Type: Multiple select
Select two.

Safe inside `Sdf.ChangeBlock` on 26.08?

A. `Sdf.PrimSpec` / `Sdf.AttributeSpec` on an existing parent spec
B. `UsdGeom.Sphere.Define` of a brand-new child path
C. Attribute create+set on an **already defined** prim via Sdf (lab 09)
D. `stage.DefinePrim` of new nested paths (same trap as Sphere.Define)

---

**DBG-044** · Obj 6.2 · Difficulty: Easy · Type: Single choice

Eight-step “why doesn’t my opinion win?” (Ch 22/42) should include mute, stack, LIVERPS, variant, instance, relocate, edit target, and:

A. `usdview` Layer Stack / property stack (or Python equivalents)
B. Reinstalling the OS
C. Converting to glTF first
D. `GetPrototype` on non-instanceable prims only

---

## Answers

**DBG-001 — Answer: B.** Notices delayed; writes happen. Review: §8.5, §34.5, lab 09.

**DBG-002 — Answer: B.** Verified 6. Review: lab 09.

**DBG-003 — Answer: C.** Verified 1. Review: lab 09.

**DBG-004 — Answer: B.** Verified Tf.ErrorException. Review: lab 30, §34.5.

**DBG-005 — Answer: A, C.** Burst Sdf authoring and coalesced notices. Review: §6.1, §44.4.

**DBG-006 — Answer: B.** Verified lab 30. Review: §34.4.

**DBG-007 — Answer: B.** `listener.Revoke()`. Review: lab 09/30.

**DBG-008 — Answer: B.** Stacks first. Review: §22.6, §42.

**DBG-009 — Answer: A, C.** B is the reverse of COMP-042; D is not a strength bug. Review: §22.6.

**DBG-010 — Answer: B.** Instance proxy. Review: §24.3, lab 23.

**DBG-011 — Answer: B.** L beats V. Review: §18.6, §21.2.

**DBG-012 — Answer: B.** Strongest first. Review: §14.5, lab 21.

**DBG-013 — Answer: B.** Session vs root Save. Review: §15.3, lab 04.

**DBG-014 — Answer: B.** Missing file. Review: §16.5, §42.

**DBG-015 — Answer: B.** Missing defaultPrim. Review: §16.2, lab 14.

**DBG-016 — Answer: A, B.** Layer anchor vs cwd. Review: §33.2, lab 29.

**DBG-017 — Answer: B.** pathResolverContext. Review: lab 29.

**DBG-018 — Answer: C.** Third slot unresolved. Review: §32.4, lab 28.

**DBG-019 — Answer: B.** catmullClark fallback. Review: lab 11, §13.5.

**DBG-020 — Answer: B.** Stale extent. Review: §13.2, Obj 5.6/6.4.

**DBG-021 — Answer: A, B.** Purpose and visibility. Review: §13.5, §42.

**DBG-022 — Answer: B.** No auto unit convert. Review: lab 26.

**DBG-023 — Answer: A.** UV V-flip. Review: §27.4.

**DBG-024 — Answer: B.** UsdUtils, not Tf. Review: lab 36, §43.

**DBG-025 — Answer: B.** Construct first. Review: lab 36.

**DBG-026 — Answer: B.** Basename sourceFileName. Review: lab 36.

**DBG-027 — Answer: B.** Time vs bytes. Review: §43.

**DBG-028 — Answer: B.** Verified 0 bytes. Review: lab 36.

**DBG-029 — Answer: B.** Trace default False. Review: lab 36.

**DBG-030 — Answer: B.** SetDebugSymbolsByName. Review: §43.2.

**DBG-031 — Answer: B.** TF_DEBUG env. Review: §43.2.

**DBG-032 — Answer: B.** Unknown → empty list. Review: §43.2.

**DBG-033 — Answer: A, B.** Warning + Pcp error. Review: lab 36.

**DBG-034 — Answer: B.** Stronger default hides samples. Review: §21.3.

**DBG-035 — Answer: B.** Extract vs Compute. Review: §32.4.

**DBG-036 — Answer: B.** 1 vs 3. Review: lab 30.

**DBG-037 — Answer: B.** Interpolation length. Review: §11.3.

**DBG-038 — Answer: A.** Verified description. Review: §43.2.

**DBG-039 — Answer: B.** Relocate destination. Review: §20.3.

**DBG-040 — Answer: A.** Plugin path + ABI. Review: §33.5, §35.2.

**DBG-041 — Answer: B.** Mask vs LoadNone. Review: §17.4, lab 16.

**DBG-042 — Answer: B.** usd-core MallocTag 0 bytes. Review: lab 36.

**DBG-043 — Answer: A, C.** Sdf specs OK; Usd Define of new children is the trap (B, D). Review: labs 09–30.

**DBG-044 — Answer: A.** Introspection UI/API. Review: §22.6, §42.

---

*Debugging domain complete: DBG-001–DBG-044 (target 44).*
