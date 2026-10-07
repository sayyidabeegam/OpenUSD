# Teaching Template

## Chapter skeleton

Every file in `chapters/` uses this structure:

```markdown
# Chapter NN — Title

> **Exam domain:** Composition (23%) · **Objectives:** 1.3, 1.6 · **Study day:** 5 · **Est. time:** 90 min
> **Prerequisites:** Ch 3, Ch 4

## Learning goals
- 3–6 bullets, each starting with a verb ("Explain…", "Author…", "Debug…")

## Key terms
| Term | One-line definition |

## NN.1 <Concept>        ← 13-step concept block (below)
## NN.2 <Concept>
...

## Chapter lab(s)
Short pointer + summary of labNN (full lab lives in python-labs/)

## USDA reading exercise(s)
1–3 short exercises with answers at chapter end

## Chapter review
- Summary (≤ 10 bullets)
- Exam takeaways table: "If you see… → think…"
- 8–15 chapter questions (answers + explanations at end of chapter)

## Further reading
Source names + URLs (optional reading; never required)
```

## 13-step concept block

Use for EVERY concept section, in this exact order and with these exact headings.
Small concepts may have short steps (1–3 sentences) but no step may be skipped.

```markdown
### 1. What is it?
One or two plain sentences. No jargon that hasn't been defined.

### 2. Why do we need it?
The problem it solves. What breaks without it.

### 3. Beginner explanation
Everyday analogy (e.g. transparent sheets stacked on an overhead projector for layers).

### 4. Technical explanation
Precise behavior, terminology, rules, edge cases. Name the Usd/Sdf classes involved.

### 5. Mental model
A sentence or diagram the reader can recall in the exam. Prefer a monochrome diagram.

### 6. Simple example
Smallest possible scenario, in words or a tiny table.

### 7. USDA example
Complete, parseable `#usda 1.0` snippet with line-by-line notes.

### 8. Python example
Complete runnable script (imports included) + "Expected output" block with the REAL output.

### 9. Real-world use case
Film/VFX, games, manufacturing/digital twin, or AEC example.

### 10. Common mistakes
2–4 bullets in `> [!MISTAKE]` callouts with the fix.

### 11. Exam traps
2–4 bullets in `> [!TRAP]` callouts: look-alike answers, wording tricks.

### 12. Practice questions
2–3 original questions; answers + 1–2 sentence explanations directly after, under "Answers".

### 13. Exam takeaways
3–5 bullets in a `> [!KEY]` callout.
```

## Writing voice

- Second person, short sentences, active voice.
- Introduce a term in **bold** the first time, then use it consistently.
- Show, then tell: example first when it helps a beginner.
- Analogy must be followed by "where the analogy breaks".
- One concept per section. If a section needs a sub-concept, give it its own block.

## Reusable analogies (keep consistent across chapters)

| Concept | Analogy |
|---------|---------|
| Layer stack | Transparent sheets on a projector; top sheet wins |
| Reference | Linking a reusable part from a catalog |
| Payload | A reference you can choose not to load (lazy-loaded box in storage) |
| Variant set | A switch with named positions |
| Inherits | A style sheet every instance follows, even later edits |
| Specializes | A default that anything else can override |
| Instancing | Rubber stamp: one prototype, many stamps |
| Value resolution | Asking a ladder of opinions, strongest rung answers |
