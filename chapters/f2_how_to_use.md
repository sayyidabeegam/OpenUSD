# How to Use This Book

## What is inside

| Part | Content | Exam weight |
|------|---------|-------------|
| Front matter | Exam overview, 14-day plan, lab setup | — |
| I | OpenUSD fundamentals (Ch 1–7) | Not scored directly; everything depends on it |
| II | Data modeling (Ch 8–13) | 13% |
| III | Composition (Ch 14–22) | 23% |
| IV | Content aggregation (Ch 23–26) | 10% |
| V | Data exchange (Ch 27–31) | 15% |
| VI | Pipeline development (Ch 32–35) | 14% |
| VII | Customizing USD (Ch 36–38) | 6% |
| VIII | Visualization (Ch 39–41) | 8% |
| IX | Debugging and performance (Ch 42–44) | 11% |
| X | Python labs, USDA workbook, question bank, mock exams, flashcards, cheat sheets, final checklist | — |
| Back matter | Glossary, references, objective coverage matrix | — |

Read Parts I–IX in order. Later chapters assume earlier ones. Part X is used throughout the 14 days according to the schedule.

## How every concept is taught

Each concept section follows the same 13 steps, always in this order. Once you know the pattern, you can find what you need quickly, for example by skipping straight to "Exam traps" during revision.

| Step | Heading | What you get |
|------|---------|--------------|
| 1 | What is it? | A one- or two-sentence definition |
| 2 | Why do we need it? | The problem it solves |
| 3 | Beginner explanation | An everyday analogy, and where the analogy breaks |
| 4 | Technical explanation | Precise rules and the OpenUSD classes involved |
| 5 | Mental model | One picture or sentence to remember in the exam |
| 6 | Simple example | The smallest possible case |
| 7 | USDA example | The concept written in USD's text format |
| 8 | Python example | A complete runnable script and its real output |
| 9 | Real-world use case | How studios and companies use it |
| 10 | Common mistakes | Errors people make, and the fix |
| 11 | Exam traps | Wording and look-alike answers to watch for |
| 12 | Practice questions | 2–3 questions with answers directly after |
| 13 | Exam takeaways | 3–5 points to memorize |

Each chapter starts with learning goals and key terms. It ends with a summary, a "If you see… → think…" table, 8–15 review questions, and their answers.

## Boxes used in this book

Boxes are told apart by their **label and border style**, not by color, so they work in black-and-white print.

> [!EXAM TIP] Advice about what the exam emphasizes or how to approach a question type.

> [!TRAP] A common way exam questions mislead you.

> [!MISTAKE] An error people often make in real code or files, and how to fix it.

> [!VERSION] Behavior that differs between OpenUSD versions. The book is verified on USD 26.08.

> [!KEY] A fact you must memorize.

> [!NOTE] Optional extra depth. Safe to skip on a first read.

## Code conventions

- **Python** examples are complete scripts: imports included, nothing hidden. Each runnable example is followed by **Expected output**, the real output from USD 26.08.
- **USDA** examples are complete text layers starting with `#usda 1.0`. When an example uses several files, each starts with a caption such as *File: chair.usda*.
- A code block labelled **not run automatically** needs something extra, such as command-line arguments, a C++ compiler, or a tool not included in `usd-core`. The text explains why.
- OpenUSD's documentation is written in C++ terms. The Python name is usually the same without the prefix: C++ `UsdStage::Open()` is Python `Usd.Stage.Open()`, and C++ `SdfPath` is Python `Sdf.Path`.

| C++ name | Python name |
|----------|-------------|
| `UsdStage` | `Usd.Stage` |
| `UsdPrim` | `Usd.Prim` |
| `SdfLayer` | `Sdf.Layer` |
| `SdfPath` | `Sdf.Path` |
| `UsdGeomMesh` | `UsdGeom.Mesh` |
| `GfVec3f` | `Gf.Vec3f` |
| `VtArray<int>` | `Vt.IntArray` |
| `TfToken` | a plain Python `str` |

## Lab difficulty

★☆☆ guided, short · ★★☆ some problem-solving · ★★★ open-ended, combines several chapters

## How to study with this book

1. **Read actively.** Before reading a "Python example", predict its output. Then compare.
2. **Type the code.** Typing the labs yourself teaches far more than reading them.
3. **Answer before you look.** Cover the answers to practice questions with a sheet of paper.
4. **Track weak areas.** After every checkpoint and mock exam, write your per-domain scores in the 14-day tracker (F4). Re-read the chapters for any domain under 70%.
5. **Use the cheat sheets last.** They are for revision, not first learning.

> [!EXAM TIP] Composition is 23% of the exam, and it shows up again inside debugging, pipeline, and content-aggregation questions. If you have extra time anywhere, spend it on Part III.
