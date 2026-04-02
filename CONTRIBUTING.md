# Contributing — How to Add Material

This is the guide for Nicholas (and future contributors) on how to add new content without breaking the structure.

---

## Where Does New Content Go?

| Type of content | Where to put it |
|-----------------|----------------|
| New video / reading / course | `resources/RESOURCES.md` — add a row to the right table |
| New concept doc (deep reference) | `concepts/` — new `.md` file, add row to README table |
| New week or curriculum change | `curriculum/` — edit the relevant week file or add a new one |
| Student question answered | `faq/` — add to the relevant file, or create a new one |
| Runnable code example | `examples/<topic>/` — new subfolder, update `examples/README.md` |
| Large supplementary reference | `resources/` — keeps it out of the main navigation |

---

## Adding a Video

Open `resources/RESOURCES.md` and add a row to the Videos table:

```markdown
| [Video Title](https://youtube.com/...) | Speaker Name | Week X — one-line description of why |
```

Also add it to the relevant weekly curriculum file under the Videos section.

---

## Adding a Concept Doc

1. Create `concepts/your-topic.md`
2. Use this header:
```markdown
# [Topic Name]

## The Core Idea
[One paragraph — what this is and why it matters]

---
## [Section 1]
...
## Further Reading
- [Link](url)
```
3. Add a row to the `## 📚 Concepts` table in `README.md`

---

## Answering a Student Question

1. Open the relevant `faq/` file (or create a new one)
2. Add a `## Question text` section with the answer
3. If you create a new file, add it to the table in `faq/README.md`

**Format:**
```markdown
## [Question as a student would ask it?]

[Answer — direct and specific. Include code blocks where relevant.]
```

---

## Adding an Example

1. Create `examples/<topic>/` folder
2. Add your `.py` script(s) with a comment block at the top:
```python
"""
What this demonstrates: [one sentence]
Prerequisites: [list packages]
Expected output: [what should happen when you run it]
"""
```
3. Add a row to `examples/README.md`

---

## File Naming Conventions

- `kebab-case` for all file names
- No numbers in filenames (they force renaming when order changes)
- Concept docs: descriptive noun phrases (`agent-harness.md`, not `02-harness.md`)
- Curriculum files: `week-NN-topic.md` or `weeks-NN-NN-topic.md`

---

## Before You Push

- [ ] All internal links resolve (check with a relative path, not absolute)
- [ ] New files appear in the right README table
- [ ] No content duplicated across files (link instead of copy)
