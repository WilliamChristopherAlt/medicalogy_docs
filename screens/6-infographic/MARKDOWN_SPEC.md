# BioBasics Wiki Markdown Specification

## Overview

This document specifies the custom markdown format used for **wiki/infographic pages** in BioBasics. The markdown is converted to styled HTML for rendering medical encyclopedia articles.

---

## Supported Syntax

### Headers

Standard markdown headers for content hierarchy:

```markdown
# H1 - Page Title
## H2 - Major Sections
### H3 - Subsections
```

| Syntax | Output | Usage |
|--------|--------|-------|
| `# Title` | H1 | Page title (use only once) |
| `## Section` | H2 | Major sections |
| `### Subsection` | H3 | Subsections within a section |

---

### Text Formatting

```markdown
**bold text**
*italic text*
```

| Syntax | Output | Usage |
|--------|--------|-------|
| `**text**` | **bold** | Emphasis, key terms, warnings |
| `*text*` | *italic* | Medical terminology, subtle emphasis |

---

### Links

#### Internal Wiki Links

Use double brackets to link to other wiki pages:

```markdown
[[blood clot]]
[[myocardium]]
[[coronary arteries]]
```

These create internal links to other BioBasics wiki pages. The term inside the brackets becomes both the link text and the page reference.

#### External Links

Standard markdown syntax for external URLs:

```markdown
[American Heart Association](https://www.heart.org/en/health-topics/heart-attack)
[text to display](https://example.com)
```

---

### Images

Custom syntax with position control:

```markdown
![position|alt text](image_url)
```

#### Position Options:

| Position | Behavior |
|----------|----------|
| `left` | Image floats left, text wraps around right |
| `right` | Image floats right, text wraps around left |
| `center` | Image centered, full width, no text wrap |

#### Examples:

```markdown
![left|Diagram of heart](https://example.com/heart.jpg)
![right|Person clutching chest](https://example.com/symptoms.jpg)
![center|Cross-section of artery](https://example.com/artery.jpg)
```

#### Image Descriptions

Add a description immediately after an image using italic text:

```markdown
![center|Atherosclerosis progression](https://example.com/image.jpg)
*Progression of atherosclerosis leading to arterial blockage*
```

The italic line directly after an image becomes a styled caption.

---

### Horizontal Rules

Use `---` to create section dividers:

```markdown
## Section One

Content here...

---

## Section Two

More content...
```

---

### Bullet Lists

Standard markdown unordered lists:

```markdown
- First item
- Second item
- **Bold item**: With description
- *Italic item*: Another description
```

Supports inline formatting within list items.

---

### Tables

Standard markdown table syntax:

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

Tables support inline formatting:

```markdown
| Category | Risk Factors |
|----------|-------------|
| **Modifiable** | Smoking, high blood pressure, obesity |
| *Lifestyle* | Excessive alcohol, chronic stress |
```

---

### Special Sections

#### Sources Section

A `## Sources` section at the end of the document receives special styling:

```markdown
## Sources

- [American Heart Association](https://www.heart.org)
- [Mayo Clinic](https://www.mayoclinic.org)
- [WHO - Cardiovascular Diseases](https://www.who.int)
```

Sources are displayed in a dedicated references section with appropriate styling.

---

## Full Page Example

```markdown
# Myocardial Infarction (Heart Attack)

A **myocardial infarction** (MI), commonly known as a *heart attack*, occurs when blood flow to a part of the [[cardiac muscle]] is blocked. This represents one of the most serious [[cardiovascular emergencies]].

---

## Understanding the Condition

![left|Heart diagram](https://example.com/heart.jpg)

The [[myocardium]] requires constant oxygen supply. According to the [American Heart Association](https://www.heart.org), prompt treatment is critical.

---

## Risk Factors

| Category | Factors |
|----------|---------|
| **Modifiable** | Smoking, hypertension, obesity |
| **Non-modifiable** | Age, family history |

---

## Warning Signs

Common symptoms include:

- **Chest discomfort**: Pressure or pain lasting minutes
- **Upper body pain**: Arms, back, neck, jaw
- **Shortness of breath**: With or without chest pain

---

## Sources

- [American Heart Association](https://www.heart.org)
- [National Heart, Lung, and Blood Institute](https://www.nhlbi.nih.gov)
```

---

## Rendering Notes

- The `md_to_html.py` converter transforms this markdown into styled HTML
- Wiki links (`[[term]]`) create clickable links to internal pages
- External links open in new tabs with appropriate security attributes
- Images are responsive and maintain aspect ratio
- Tables are horizontally scrollable on mobile devices
- The Sources section is visually distinct from main content

---

## Best Practices

1. **Use one H1** for the page title
2. **Separate sections** with horizontal rules (`---`)
3. **Link medical terms** using wiki links (`[[term]]`)
4. **Cite external sources** with markdown links
5. **Position images** appropriately for content flow
6. **Add captions** to important images
7. **Always include** a Sources section at the end
