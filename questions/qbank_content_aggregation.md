# Question Bank — Content Aggregation (CA)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 2.1–2.5 (Content Aggregation, 10%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 40 questions. This file holds **CA-001–CA-040** (domain complete).

Work the stems first. Answers and explanations are grouped at the end.

---

**CA-001** · Obj 2.4 · Difficulty: Easy · Type: Single choice

Where do you author `instanceable = true` so many chairs share a prototype?

A. Only on every `Seat` mesh inside the published asset
B. On each **referencing** prim (instance root) in the assembly
C. Stage metadata next to `upAxis`
D. On the session layer only

---

**CA-002** · Obj 2.4 · Difficulty: Easy · Type: Single choice

On USD 26.08, the API for the shared native-instance prototype is:

A. `prim.GetMaster()`
B. `prim.GetPrototype()` (`GetMaster` is **absent**)
C. `UsdGeom.PointInstancer.GetPrototype`
D. `Kind.Registry.GetPrototype`

---

**CA-003** · Obj 2.4 · Difficulty: Medium · Type: Single choice

Two instanceable prims reference the same chair. `a.GetPrototype() == b.GetPrototype()`?

A. False — one prototype per path
B. True if their composition (refs/variants/inherits) matches
C. True only after Flatten
D. Prototypes exist only for PointInstancer

---

**CA-004** · Obj 2.4 · Difficulty: Medium · Type: Single choice

Default `Traverse()` on a stage with instanceable `/Room/A` that has `/Room/A/Seat`?

A. Lists `/Room/A/Seat`
B. Lists `/Room/A` (and `/Room/B`) but **skips** instance-proxy children
C. Skips the instance roots too
D. Raises

---

**CA-005** · Obj 2.4 · Difficulty: Medium · Type: Multiple select
Select two.

`IsInstanceable()` vs `IsInstance()`?

A. `IsInstanceable` is the authored flag
B. `IsInstance` means USD actually built a prototype for that prim
C. They are always equal
D. `IsInstance` is the old name for `GetMaster`

---

**CA-006** · Obj 2.2 · Difficulty: Medium · Type: Single choice

Edit **one** instance’s nested `Seat` color **without** de-instancing (Obj 2.2). Legal place?

A. `OverridePrim("/Room/A/Seat")` and set `displayColor`
B. A **primvar / inherit / variant** on the **instance root** `/Room/A` (shader must read it)
C. `GetMaster().Clear()`
D. Mute the assembly

---

**CA-007** · Obj 2.2 · Difficulty: Medium · Type: Single choice

`OverridePrim("/Room/A/Seat")` while A is instanceable. Result on 26.08?

A. Unique color on A only
B. `Tf.ErrorException` — authoring to an instance proxy is not allowed
C. Silent write to all instances
D. Converts A to a PointInstancer

---

**CA-008** · Obj 2.2 · Difficulty: Easy · Type: Single choice

The instance **root** `/Room/A` is a proxy?

A. Yes — never author there
B. **No** — the root is the instance; **descendants** are proxies; root primvars/variants/inherits are legal
C. Only if `kind = component`
D. Only in USDA

---

**CA-009** · Obj 2.2 · Difficulty: Medium · Type: Multiple select
Select two.

To tint **all** instanced chairs the same without breaking instancing:

A. Author `displayColor` (or material) on the **source** `/Chair`
B. Nested over on every `/Room/*/Seat` proxy
C. A `class` they all **inherit** from the instance roots
D. `SetInstanceable(False)` on every copy

---

**CA-010** · Obj 2.5 · Difficulty: Medium · Type: Single choice

Remove or override a property on **one** instanced component’s nested gprim in an assembly (Obj 2.5)?

A. Block the proxy path while instanceable
B. `SetInstanceable(False)` on that instance root, then author the nested override; siblings keep the prototype
C. `GetMaster()` and `RemoveProperty`
D. Delete `/__Prototype_1`

---

**CA-011** · Obj 2.5 · Difficulty: Medium · Type: Single choice

After de-instancing B and setting Seat size 9, lab 23: A’s size?

A. Also 9
B. Stays at the prototype/source value (3 in the lab); B is unique
C. `None`
D. Both become non-instanceable automatically

---

**CA-012** · Obj 2.5 · Difficulty: Easy · Type: Single choice

De-instance **every** chair “so we can edit.” Pipeline cost?

A. None — instancing is free either way
B. You throw away the **memory** win; prefer root primvars/variants unless the copy is a true hero
C. Hydra requires it
D. PointInstancer appears automatically

---

**CA-013** · Obj 2.1 · Difficulty: Easy · Type: Single choice

Required PointInstancer properties to instance anything?

A. Only `positions`
B. `prototypes` relationship, `protoIndices`, and `positions`
C. `kind = assembly`
D. `instanceable = true` on each point

---

**CA-014** · Obj 2.1 · Difficulty: Medium · Type: Single choice

`GetInstanceCount()` equals?

A. `len(positions)` even if protoIndices is shorter
B. `len(protoIndices)`
C. Number of prototype targets
D. Traverse prim count

---

**CA-015** · Obj 2.1 · Difficulty: Medium · Type: Single choice

Adding a third prototype from a **stronger** layer with `rel.AddTarget(path)` and **no** position argument typically authors:

A. `append` (safe, last index)
B. **`prepend`** (`ListPositionBackOfPrependList`) — new proto at index **0**, shifting every `protoIndices` meaning
C. A new PointInstancer
D. Nothing

---

**CA-016** · Obj 2.1 · Difficulty: Medium · Type: Single choice

Safe append of `/Forest/Protos/Bush` so Pine=0 and Oak=1 stay put?

A. Default `AddTarget`
B. `AddTarget(path, Usd.ListPositionBackOfAppendList)`
C. `SetInstanceable(True)` on Bush
D. `InvisId(2)`

---

**CA-017** · Obj 2.1 · Difficulty: Medium · Type: Python-reading

Lab 24: after append with BackOfAppendList, `targets` names?

A. `Bush, Pine, Oak`
B. `Pine, Oak, Bush`
C. `Oak, Pine, Bush`
D. Empty

---

**CA-018** · Obj 2.1 · Difficulty: Easy · Type: Single choice

Why put prototypes under a `class` child (`SpecifierClass`)?

A. Class prims cannot hold geometry
B. `Traverse()` **skips** class descendants, so the forest walk is the instancer prim not every pine mesh
C. Required by LIVERPS
D. PointInstancer forbids `def` prototypes

---

**CA-019** · Obj 2.3 · Difficulty: Easy · Type: Single choice

Hide **one** PointInstancer instance efficiently (Obj 2.3)?

A. `MakeInvisible()` on the PointInstancer prim (hides **all**)
B. `InvisId(id, time)` / `invisibleIds`
C. Deactivate the whole `/Forest` prim
D. `SetInstanceable(False)`

---

**CA-020** · Obj 2.3 · Difficulty: Medium · Type: Single choice

`InvisId(1, Default)` then `GetInstanceCount()`?

A. 2
B. **Still 3** — hide is a mask, not a delete
C. 0
D. Raises

---

**CA-021** · Obj 2.3 · Difficulty: Medium · Type: Single choice

After hiding id 1, `ComputeMaskAtTime` in the lab?

A. `[False, False, False]`
B. `[True, False, True]`
C. `[1]`
D. `None`

---

**CA-022** · Obj 2.3 · Difficulty: Medium · Type: Multiple select
Select two.

`ComputeInstanceTransformsAtTime` after hiding the middle instance (positions 0, 2, 4)?

A. Translations at 0 and 4 remain; the hidden one is omitted from that compute
B. Count stays 3
C. Positions array is rewritten to two samples
D. `MakeInvisible` was called on `/Forest`

---

**CA-023** · Obj 2.3 · Difficulty: Medium · Type: Single choice

`InvisId` signature that failed in early drafts?

A. `InvisId(id, time)` — **time is required**
B. `InvisId(id)` alone is the documented 26.08 form
C. `InvisId(PointInstancer, int)` 
D. `prim.MakeInvisible(id)`

---

**CA-024** · Obj 2.4 · Difficulty: Medium · Type: Single choice

PointInstancer `IsA(Gprim)` vs `IsA(Boundable)`?

A. Both True
B. **Not** a Gprim; **is** Boundable
C. Is a Gprim; not Boundable
D. Neither

---

**CA-025** · Obj 2.4 · Difficulty: Medium · Type: Single choice

80,000 identical stadium seats vs one unique broadcast booth. Pairing?

A. Native instance or PointInstancer seats; ordinary reference for the booth
B. Native-instance the booth with the seats so they share one prototype
C. 80,000 full `def` copies
D. One payload for the whole stadium is enough instancing

---

**CA-026** · Obj 2.4 · Difficulty: Easy · Type: Single choice

Native instances vs PointInstancer grain?

A. Native: one prim per copy (proxies, names, variants); PI: arrays on **one** prim for huge crowds
B. PI always uses GetPrototype
C. Native cannot share geometry
D. PI requires instanceable=true on each point

---

**CA-027** · Obj 2.4 · Difficulty: Medium · Type: Multiple select
Select two.

Matching native instances **split** into two prototypes when:

A. They pick different variant selections
B. They inherit different classes / extra local arcs
C. They have different prim **names** only (`Chair_0` vs `Chair_1`)
D. They sit under the same assembly

---

**CA-028** · Obj 2.4 · Difficulty: Medium · Type: Single choice

`/Kitchen/Clutter/Mug` has `kind = component` but `IsComponent()` is False. Why?

A. Kind `component` is illegal
B. Model hierarchy **broke**: un-kinded ancestor; GetKind can still say component
C. Mug is instanceable
D. Need Flatten

---

**CA-029** · Obj 2.4 · Difficulty: Medium · Type: Single choice

`Usd.PrimIsModel` traversal lists Kitchen, Props, Chair_0 but not Mug. Reason?

A. Bug
B. Non-models are **pruned**; Clutter is not a model so children are not visited
C. Mug is USDC
D. Chair_0 is a payload so it cannot be a model

---

**CA-030** · Obj 2.4 · Difficulty: Easy · Type: Single choice

`Kind.Registry.IsA("assembly", "group")`?

A. False
B. **True** — assembly is-a group
C. Raises
D. Only after `Register`

---

**CA-031** · Obj 2.1 · Difficulty: Medium · Type: Single choice

After adding Bush you must also:

A. Nothing — protoIndices auto-extend
B. Author **`protoIndices`** (and usually `positions`) entries that **index** the new prototype
C. Set `instanceable` on Forest
D. `ComputeExtentFromPlugins` on each tree prim only

---

**CA-032** · Obj 2.5 · Difficulty: Medium · Type: Single choice

Source `/Chair/Seat` size Set(3) while A and B are instances. Both seats read 3. That is:

A. A bug
B. **Source edits broadcast** through the prototype — intended
C. Only A updates
D. Forbidden; you must de-instance first

---

**CA-033** · Obj 2.2 · Difficulty: Hard · Type: Single choice

Exporter picks `/Room/A/Seat` (proxy) for a unique `displayColor`. Correct rewrite?

A. Write color on the proxy anyway
B. Write a primvar on **instance root** `/Room/A` (or de-instance if a nested unique mesh is required)
C. Write on `/__Prototype_1/Seat` as the per-instance API
D. Convert to PointInstancer `displayColors` always

---

**CA-034** · Obj 2.3 · Difficulty: Easy · Type: Single choice

`inactiveIds` vs `invisibleIds` (conceptually)?

A. Identical
B. Invisible hides for imaging; inactive is a stronger omit (no load/eval of that id) — both are per-id, not `MakeInvisible` on the prim
C. inactiveIds is LIVERPS
D. Only invisibleIds exists in OpenUSD

---

**CA-035** · Obj 2.4 · Difficulty: Medium · Type: Single choice

`stage.GetPrototypes()` in lab 23 listed:

A. `/Chair` only
B. `/__Prototype_1` (implicit prototype prims, not the source path)
C. `/Room/A/Seat`
D. Empty until Flatten

---

**CA-036** · Obj 2.1 · Difficulty: Medium · Type: Multiple select
Select two.

Same-layer explicit `SetTargets([Pine, Oak])` then `AddTarget(Bush)` without position — lab used BackOfAppendList because:

A. Stronger-layer default prepend is the exam trap
B. Append keeps indices 0,1 stable
C. Prepend is always safer
D. PointInstancer ignores list-ops

---

**CA-037** · Obj 2.4 · Difficulty: Medium · Type: Single choice

Different variant on B than A. Shared prototype?

A. Always shared
B. Often a **second** prototype — composition differs
C. Instancing breaks entirely
D. B cannot be instanceable

---

**CA-038** · Obj 2.5 · Difficulty: Medium · Type: Single choice

Blocking a property on the **instance root** (not a proxy child) while staying instanceable?

A. Illegal always
B. Legal for root-level opinions; nested proxy `Block()` is the illegal one
C. Only via GetMaster
D. Only via PointInstancer mask

---

**CA-039** · Obj 2.4 · Difficulty: Easy · Type: Single choice

`GetPrimAtPath("/Room/A/Seat")` on an instance proxy?

A. Invalid always
B. Valid handle; `IsInstanceProxy()` True; readable; not in default Traverse
C. Raises
D. Equals GetPrototype()

---

**CA-040** · Obj 2.3 · Difficulty: Medium · Type: Single choice

Hide 50,000 of 2,000,000 PI instances every frame. Prefer?

A. 50,000 native `visibility=invisible` prims
B. `invisibleIds` / `InvisId` on the instancer (array update)
C. Delete protoIndices entries each frame
D. `MuteLayer` on the shot

---

## Answers

**CA-001 — Answer: B.** Instanceable at the use site. Review: §24.1, lab 23.

**CA-002 — Answer: B.** Verified `GetMaster` missing. Review: §24.2.

**CA-003 — Answer: B.** Shared proto when composition matches. Review: lab 23.

**CA-004 — Answer: B.** Traverse skips proxies. Review: lab 23.

**CA-005 — Answer: A, B.** Flag vs built instance. Review: §24.1.

**CA-006 — Answer: B.** Obj 2.2 legal edit sites. Review: §24.4–24.5.

**CA-007 — Answer: B.** Proxy authoring raises. Review: lab 23, COMP-027.

**CA-008 — Answer: B.** Root vs proxy. Review: §24.3.

**CA-009 — Answer: A, C.** Source or inherited class. Review: §24.4.

**CA-010 — Answer: B.** De-instance one hero. Review: §24.6, Obj 2.5.

**CA-011 — Answer: B.** Verified A stays 3, B 9. Review: lab 23.

**CA-012 — Answer: B.** Don’t de-instance the crowd. Review: §24.5.

**CA-013 — Answer: B.** Three required fields. Review: §25.2.

**CA-014 — Answer: B.** Count = protoIndices length. Review: lab 24.

**CA-015 — Answer: B.** Default AddTarget prepends in a stronger layer. Review: §25.3.

**CA-016 — Answer: B.** BackOfAppendList. Review: lab 24.

**CA-017 — Answer: B.** Pine, Oak, Bush. Review: lab 24.

**CA-018 — Answer: B.** Class skipped by Traverse. Review: lab 24.

**CA-019 — Answer: B.** InvisId / invisibleIds. Review: §25.4.

**CA-020 — Answer: B.** Count still 3. Review: lab 24.

**CA-021 — Answer: B.** Mask `[True, False, True]`. Review: lab 24.

**CA-022 — Answer: A, B.** Transforms omit hidden; count unchanged. Review: lab 24.

**CA-023 — Answer: A.** Time argument required. Review: lab 24 notes.

**CA-024 — Answer: B.** Boundable, not Gprim. Review: lab 24.

**CA-025 — Answer: A.** Style by scale. Review: §26.1.

**CA-026 — Answer: A.** Prim-per-copy vs arrays. Review: §25.1, §26.1.

**CA-027 — Answer: A, B.** Variant/inherit split prototypes. Names alone don’t. Review: §24.2, §24.5.

**CA-028 — Answer: B.** Broken model chain. Review: lab 22.

**CA-029 — Answer: B.** PrimIsModel prunes. Review: lab 22.

**CA-030 — Answer: B.** assembly is-a group. Review: lab 22. `Kind.Registry.Register` does not exist in Python 26.08.

**CA-031 — Answer: B.** Indices must reference the new proto. Review: §25.3.

**CA-032 — Answer: B.** Source broadcasts. Review: lab 23.

**CA-033 — Answer: B.** Don’t bake unique color on a proxy. Review: §24.4.

**CA-034 — Answer: B.** Two per-id hides. Review: §25.4.

**CA-035 — Answer: B.** `/__Prototype_1`. Review: lab 23.

**CA-036 — Answer: A, B.** Exam trap is prepend. Review: §25.3.

**CA-037 — Answer: B.** Different composition → another prototype. Review: §24.5.

**CA-038 — Answer: B.** Root Block vs proxy Block. Review: §24.6, Obj 2.5.

**CA-039 — Answer: B.** Readable proxy handle. Review: lab 23.

**CA-040 — Answer: B.** Array hide at PI scale. Review: §25.4, §26.1.

---

*Content Aggregation domain complete: CA-001–CA-040 (target 40).*
