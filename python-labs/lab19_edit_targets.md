# Lab 19 — Edit targets, `EditContext`, and offset mapping

**Domain / objectives:** Composition 1.1, 1.5 · **Chapter:** 15 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
See the **default edit target** (root layer), write a sample through **`GetEditTargetForLocalLayer`** so offset math is applied, write another through a **bare `Usd.EditTarget`**, park a comment in the **session layer** with **`Usd.EditContext`**, and fail to target a layer that is **not in the local stack**.

## Background
`Usd` writes go to the **edit target**, which starts as the root layer (Ch 15). `GetEditTargetForLocalLayer(layer)` includes that sublayer's **layer offset**, so `Set(value, stage_time)` stores at **layer** time: `(20 − 10) / 1 = 10`. A bare `Usd.EditTarget(layer)` stores the stage time unchanged (sample at 20). `with Usd.EditContext(stage, target):` sets the target for the block and **restores** it. The target layer must be in the **local layer stack** (session, root, or a sublayer). A referenced-only or anonymous layer raises `Tf.ErrorException`.

## Steps
1. Default target display name is `shot.usda`.
2. `anim samples: {10.0: 1.0, 20.0: 2.0}` — mapped time then unmapped time.
3. After the `with` block, the target is `shot.usda` again. The comment lives on the **session** prim spec.
4. Targeting an anonymous layer prints `not in stack: True`.

## Full script (identical to `lab19_edit_targets.py`)

```python
"""Lab 19 — Edit targets, EditContext, offset mapping, local stack."""
import os
import tempfile
from pxr import Sdf, Tf, Usd

os.chdir(tempfile.mkdtemp())
open("anim.usda", "w").write("""#usda 1.0
def "Ball"
{
}
""")
open("shot.usda", "w").write("""#usda 1.0
(
    subLayers = [
        @anim.usda@ (offset = 10)
    ]
)
""")
stage = Usd.Stage.Open("shot.usda")
anim = Sdf.Layer.Find("anim.usda")
print("default target:", stage.GetEditTarget().GetLayer().GetDisplayName())

stage.SetEditTarget(stage.GetEditTargetForLocalLayer(anim))
tx = stage.GetPrimAtPath("/Ball").CreateAttribute(
    "tx", Sdf.ValueTypeNames.Double
)
tx.Set(1.0, 20)
stage.SetEditTarget(Usd.EditTarget(anim))
tx.Set(2.0, 20)
print("anim samples:",
      anim.GetAttributeAtPath("/Ball.tx").GetInfo("timeSamples"))

stage.SetEditTarget(stage.GetRootLayer())
with Usd.EditContext(stage, stage.GetSessionLayer()):
    stage.GetPrimAtPath("/Ball").SetMetadata("comment", "try bigger")
print("restored:", stage.GetEditTarget().GetLayer().GetDisplayName())
print("session comment:",
      stage.GetSessionLayer().GetPrimAtPath("/Ball").comment)

try:
    stage.SetEditTarget(Sdf.Layer.CreateAnonymous("elsewhere"))
except Tf.ErrorException as err:
    print("not in stack:", "not in the local LayerStack" in str(err))
```

**Expected output**
```text
default target: shot.usda
anim samples: {10.0: 1.0, 20.0: 2.0}
restored: shot.usda
session comment: try bigger
not in stack: True
```

## Check your understanding
1. At what layer time is a sample stored if you `Set(..., 20)` through `GetEditTargetForLocalLayer` on a sublayer with offset 10?
2. Does `EditContext` leave the session layer as the target after the block?
3. Can you `SetEditTarget` a layer that is only reached through a reference?

**Answers**
1. **10.** `(stageTime − offset) / scale = (20 − 10) / 1`.
2. **No.** It restores the previous target (`shot.usda` here).
3. **No.** The layer must be in the local layer stack.

## Stretch challenge
Mute `anim.usda` and try `SetEditTarget(anim)` again. Solution: a muted layer is not in the stack, so you get the same `Tf.ErrorException` (Ch 15.3).
