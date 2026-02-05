# BioBasics Wiki Markdown Specification

## Overview

This document specifies the custom markdown format used for wiki/infographic pages in BioBasics.

---

## Supported Syntax

### Headers

```markdown
# H1 - Page Title
## H2 - Major Sections
### H3 - Subsections
```

| Syntax | Usage |
|--------|-------|
| `# Title` | Page title (use only once) |
| `## Section` | Major sections |
| `### Subsection` | Subsections |

---

### Text Formatting

```markdown
*bold text*
/italic text/
```

| Syntax | Output |
|--------|--------|
| `*text*` | bold (white) |
| `/text/` | italic (white) |

---

### Links

#### Internal Wiki Links (Yellow)

```markdown
[display text|slug]
```

Examples:
```markdown
[blood clot|blood-clot]
[heart muscle|myocardium]
[coronary arteries|coronary-arteries]
```

#### External Links (Green)

```markdown
{display text|url}
```

Examples:
```markdown
{American Heart Association|https://www.heart.org}
{Mayo Clinic|https://www.mayoclinic.org}
```

---

### Images

```markdown
![position|alt text](image_url)
```

| Position | Behavior |
|----------|----------|
| `left` | Float left, text wraps right |
| `right` | Float right, text wraps left |
| `center` | Centered, full width |

#### Image Captions

```markdown
![center|Atherosclerosis](https://example.com/image.jpg)
/Caption text here/
```

---

### Horizontal Rules

```markdown
---
```

---

### Bullet Lists

For tight spacing (grouped items), wrap with `[[[` and `]]]`:

```markdown
[[[
- First item
- Second item
- Third item
]]]
```

Without wrapper, items have more spacing:

```markdown
- First item
- Second item
- Third item
```

---

### Numbered Lists

For tight spacing (grouped items), wrap with `[[[` and `]]]`:

```markdown
[[[
1. First step
2. Second step
3. Third step
]]]
```

Without wrapper, items have more spacing:

```markdown
1. First step
2. Second step
3. Third step
```

---

### Tables

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
```

---

## Syntax Summary

| Element | Syntax | Color |
|---------|--------|-------|
| Bold | `*text*` | White |
| Italic | `/text/` | White |
| Internal Link | `[text|slug]` | Yellow |
| External Link | `{text|url}` | Green |
| Image | `![position|alt](url)` | - |
| Caption | `/caption/` | Gray |
| Bullet List | `- item` | - |
| Numbered List | `1. item` | - |
| List Block (tight) | `[[[` ... `]]]` | - |
| Divider | `---` | - |

---

## Example

```markdown
# Heart Attack

A *myocardial infarction* occurs when blood flow to the [cardiac muscle|cardiac-muscle] is blocked.

---

## Risk Factors

According to the {American Heart Association|https://www.heart.org}, risk factors include:

[[[
- *Smoking* damages blood vessels
- *High blood pressure* strains the heart
- *Obesity* increases workload
]]]

---

## The Process

[[[
1. *Plaque formation* buildup in arteries
2. *Plaque rupture* cap breaks
3. *Clot formation* blocks blood flow
]]]

---

## Sources

[[[
- {American Heart Association|https://www.heart.org}
- {Mayo Clinic|https://www.mayoclinic.org}
]]]
```
