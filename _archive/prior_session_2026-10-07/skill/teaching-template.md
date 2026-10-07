# Teaching Template

## The 13-step concept template

Apply to every concept, in this order. Use these exact level-3 headings so the book is consistent and searchable.

```markdown
## N.M <Concept name>

### What is it?
One or two plain sentences. No jargon that hasn't been defined yet.

### Why do we need it?
The problem it solves. What breaks or becomes painful without it.

### Beginner explanation
An everyday analogy (e.g. transparent overlays on a projector for layers).
State where the analogy stops being accurate.

### Technical explanation
Precise definition using correct OpenUSD terms. Name the classes/APIs involved
(e.g. `Usd.Stage`, `Sdf.Layer`). Mention version-sensitive behavior here.

### Mental model
A one-line rule or a small diagram the reader can recall in the exam.

### Simple example
A tiny scenario in words or a minimal snippet, before any full code.

### USDA example
A complete `.usda` snippet (starts with `#usda 1.0` unless marked fragment)
plus a line-by-line reading guide.

### Python example
Self-contained runnable code (imports included) and an "Expected output" block.

### Real-world use case
How a studio, game, manufacturing, or AEC pipeline uses this.

### Common mistakes
Bulleted list: mistake → why it happens → fix.

### Exam traps
::: {.exam-trap}
Distractors and confusions the exam is likely to exploit.
:::

### Practice questions
2–4 original questions. Answers and explanations at the end of the chapter.

### Exam takeaways
::: {.takeaways}
3–6 bullets the reader must remember.
:::
```

## Chapter skeleton

```markdown
# Chapter NN — <Title> {#chNN}

::: {.chapter-meta}
**Exam domain:** <domain> (<weight>%) · **Objectives:** Obj x.y, x.z
**Study day:** Day N · **Estimated time:** 90 min · **Prerequisites:** Chapter NN
:::

## Learning goals
By the end of this chapter you can: (4–6 action verbs: explain, author, debug...)

## NN.1 <Concept>        ← 13-step template
## NN.2 <Concept>        ← 13-step template
...

## Putting it together
A short worked scenario combining the chapter's concepts.

## Chapter summary
## Exam takeaways (chapter-level box)
## Practice questions (all questions from the chapter, numbered NN-Q1...)
## Answers and explanations
## Labs for this chapter (lab IDs and one-line goals)
## Sources for this chapter (source names; full URLs live in the bibliography)
```

## Beginner-level writing rules

- Define every term at first use; bold it and add it to the glossary list in the master plan.
- One idea per paragraph. Paragraphs ≤ 5 lines in print.
- Prefer concrete names (`/World/Chair`, `chair_geo.usda`) over `foo`/`bar`.
- Never forward-reference without saying where it is explained ("see Chapter 25").
- Show the USDA before the Python when introducing a concept: readers must learn to *read* scene description.
- After every non-trivial example, tell the reader what to look at ("Notice the `over` specifier on line 4").
- Use consistent terminology: "opinion", "layer stack", "composition arc", "prim", "property". Never say "node" or "object" for a prim.
