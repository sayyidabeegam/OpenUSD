# Cheat sheet — List editing

**USD 26.08** · Obj 1.1 · Ch 14.4 · Fields: references, payloads, inherits, specializes, `apiSchemas`, relationship targets, `subLayers` (order is stack strength).

A **list op** is either an **explicit** list or a set of **edits**. Stronger layers edit weaker lists instead of recopying them.

## USDA forms

| Form | Meaning |
|------|---------|
| `references = [@a@, @b@]` | **Explicit** whole list; weaker opinions discarded |
| `references = None` | Explicit **empty** — strips every weaker item |
| `prepend references = @c@` | Insert at **front** (stronger among same-letter arcs) |
| `append references = @d@` | Insert at **back** (weaker) |
| `delete references = @a@` | Remove `a` contributed by a **weaker** layer |

Do not mix explicit `references =` and `prepend references =` in one spec — the parser keeps the **last** statement.

Legacy `add` / `reorder`: do not author new ones.

## Compose order (26.08)

1. Apply layers **weakest → strongest**.  
2. Inside one spec: **delete**, then **prepend**, then **append**.  
3. Prepend of an item already present **moves** it to the front.  
4. Delete of a missing item is a no-op.  
5. Same-spec `delete` + `prepend` of the **same** `@a@` does **not** drop `a`. Put `delete` on a **stronger** layer.

**Verified:** weaker `prepend @r1@` (`radius=2`) + `append @r2@` (`8`) → composed **2**. Stronger-layer `delete @r1@` → **8**.

```text
 weakest : prepend [a, b]              → [a, b]
 stronger: delete [b]; append [c]      → [a, c]
 strongest: prepend [n]                → [n, a, c]   front = strongest arc
           OR explicit [x]             → [x]
```

`subLayers = [@paint@, @layout@]`: **paint** is strongest (first listed).

## Python (`Usd.ListPosition*`)

| Call | Typical list-op |
|------|-----------------|
| `GetReferences().AddReference(path)` | Prepend (`FrontOfPrependList`) — Ch 14 |
| `RemoveReference(Sdf.Reference(...))` | `delete` |
| `SetReferences([...])` | Explicit |
| `ClearReferences()` | Clears **this layer's** opinion |
| Same pattern | `GetInherits`, `GetSpecializes`, `GetPayloads`, `AddTarget` |

Positions: `FrontOfPrependList` · `BackOfPrependList` · `FrontOfAppendList` · `BackOfAppendList`.

### PointInstancer `prototypes` (verified 26.08)

Default `AddTarget("/PI/Tree")` after Bush was **`[Bush, Tree]`** — index 0 stayed Bush.  
**Do not assume** default is `FrontOfPrependList` for `AddTarget`.

| Goal | Call |
|------|------|
| New proto at **index 0** (shifts others) | `AddTarget(path, FrontOfPrependList)` |
| New proto at **end** (index 0 safe) | `AddTarget(path, BackOfAppendList)` |

`protoIndices` are integers into this list — shifting index 0 retargets every instance.

## Relationships

`AddTarget` / `RemoveTarget` / `SetTargets` / `GetTargets()`.  
`GetForwardedTargets()` walks rel-to-rel (`/A.r` → `/B.r` → `/C` yields `/C`).

## Exam moves (Obj 1.1)

| Intent | List-op |
|--------|---------|
| Shot wins over asset ref | Local `over` (LIVERPS), not a weaker append |
| Drop one weaker ref | `delete` on a **stronger** layer |
| Replace the whole set | Explicit list on the shot |
| Keep asset additions flowing | Prefer prepend/append, not explicit copy |
