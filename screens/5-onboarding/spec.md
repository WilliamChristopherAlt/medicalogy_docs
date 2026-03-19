# Initial Assessment JSON Structure Specification

## Overview

The initial assessment in Medicalogy is a placement test presented to new users to gauge their existing medical knowledge and personalise their learning path. Questions and options are stored as structured JSON in the `initial_assessment.content` column.

Each question is tagged with a `sectionSlug` that maps to `section.slug` in the Learning Service. This is the field the Assessment Service uses to bucket results into `initial_user_section_proficiency` rows after scoring — one row per `(user, assessment, section)`.

Options use `isCorrect` (boolean). Proficiency is measured by `questions_correct / questions_seen` per section.

---

## Root Structure

```json
{
  "version": "1.0",
  "questions": [ ... ]
}
```

| Field       | Type   | Required | Description                                       |
|-------------|--------|----------|---------------------------------------------------|
| `version`   | string | Yes      | Schema version for forward compatibility          |
| `questions` | array  | Yes      | Ordered array of question objects (min 1 element) |

---

## Question Object

```json
{
  "id": "q-001",
  "questionText": "What is the correct compression rate for adult CPR?",
  "questionType": "multiple_choice",
  "sectionSlug": "emergency-care-fundamentals",
  "orderIndex": 1,
  "options": [ ... ]
}
```

| Field          | Type    | Required | Max Length | Description                                                       |
|----------------|---------|----------|------------|-------------------------------------------------------------------|
| `id`           | string  | Yes      | 50         | Unique identifier within the assessment (e.g., `q-001`)           |
| `questionText` | string  | Yes      | 1000       | The question being asked                                          |
| `questionType` | string  | Yes      | -          | One of: `"multiple_choice"`, `"true_false"`                       |
| `sectionSlug` | string  | Yes      | 300        | Slug of the section this question tests (maps to `section.slug`)      |
| `orderIndex`   | integer | Yes      | -          | Display order (1-based, must be sequential)                       |
| `options`      | array   | Yes      | -          | Array of answer option objects (min 2 elements)                   |

---

## Answer Option Structure

```json
{
  "id": "opt-001",
  "text": "100-120 compressions per minute",
  "isCorrect": true,
  "orderIndex": 1
}
```

| Field        | Type    | Required | Max Length | Description                                      |
|--------------|---------|----------|------------|--------------------------------------------------|
| `id`         | string  | Yes      | 50         | Unique option identifier within the question     |
| `text`       | string  | Yes      | 500        | The answer option text                           |
| `isCorrect`  | boolean | Yes      | -          | `true` for the correct answer, `false` otherwise |
| `orderIndex` | integer | Yes      | -          | Display order of options                         |

---

## Question Type Specifications

### Multiple Choice (`multiple_choice`)
- **Options required:** 2–6 options
- **Correct answers:** Exactly 1 option with `isCorrect: true`
- **Use case:** Knowledge assessment with one correct answer

### True/False (`true_false`)
- **Options required:** Exactly 2 options
- **Option texts:** Must be `"True"` and `"False"`
- **Correct answers:** Exactly 1 option with `isCorrect: true`
- **Use case:** Fact-checking existing knowledge

---

## Scoring

The Assessment Service scores the test after submission and writes one `initial_user_section_proficiency` row per section that appeared:

```
questions_correct = count of questions where user picked the option with isCorrect: true
questions_seen    = count of questions shown to the user for that sectionSlug
```

| Threshold | Effect |
|-----------|--------|
| questions_correct / questions_seen ≥ 0.80 | Roadmap shows section as "Already known" — courses skippable, no order dependency |
| questions_correct / questions_seen < 0.80  | Normal locked flow — courses unlock in order |

---

## Complete Example

```json
{
  "version": "1.0",
  "questions": [
    {
      "id": "q-001",
      "questionText": "What is the correct compression rate for adult CPR?",
      "questionType": "multiple_choice",
      "sectionSlug": "emergency-care-fundamentals",
      "orderIndex": 1,
      "options": [
        { "id": "opt-001", "text": "60-80 compressions per minute",   "isCorrect": false, "orderIndex": 1 },
        { "id": "opt-002", "text": "100-120 compressions per minute",  "isCorrect": true,  "orderIndex": 2 },
        { "id": "opt-003", "text": "140-160 compressions per minute",  "isCorrect": false, "orderIndex": 3 },
        { "id": "opt-004", "text": "I don't know",                     "isCorrect": false, "orderIndex": 4 }
      ]
    },
    {
      "id": "q-002",
      "questionText": "Back blows should be delivered between the shoulder blades when someone is choking.",
      "questionType": "true_false",
      "sectionSlug": "emergency-care-fundamentals",
      "orderIndex": 2,
      "options": [
        { "id": "opt-001", "text": "True",  "isCorrect": true,  "orderIndex": 1 },
        { "id": "opt-002", "text": "False", "isCorrect": false, "orderIndex": 2 }
      ]
    },
    {
      "id": "q-003",
      "questionText": "Which macronutrient is the body's primary energy source?",
      "questionType": "multiple_choice",
      "sectionSlug": "nutrition-basics",
      "orderIndex": 3,
      "options": [
        { "id": "opt-001", "text": "Protein",       "isCorrect": false, "orderIndex": 1 },
        { "id": "opt-002", "text": "Carbohydrates",  "isCorrect": true,  "orderIndex": 2 },
        { "id": "opt-003", "text": "Fat",            "isCorrect": false, "orderIndex": 3 },
        { "id": "opt-004", "text": "Vitamins",       "isCorrect": false, "orderIndex": 4 }
      ]
    },
    {
      "id": "q-004",
      "questionText": "The human heart has four chambers.",
      "questionType": "true_false",
      "sectionSlug": "cardiovascular-anatomy",
      "orderIndex": 4,
      "options": [
        { "id": "opt-001", "text": "True",  "isCorrect": true,  "orderIndex": 1 },
        { "id": "opt-002", "text": "False", "isCorrect": false, "orderIndex": 2 }
      ]
    },
    {
      "id": "q-005",
      "questionText": "Which of the following is a common symptom of depression?",
      "questionType": "multiple_choice",
      "sectionSlug": "mental-health-awareness",
      "orderIndex": 5,
      "options": [
        { "id": "opt-001", "text": "Increased energy",         "isCorrect": false, "orderIndex": 1 },
        { "id": "opt-002", "text": "Persistent low mood",      "isCorrect": true,  "orderIndex": 2 },
        { "id": "opt-003", "text": "Improved concentration",   "isCorrect": false, "orderIndex": 3 },
        { "id": "opt-004", "text": "Decreased need for sleep", "isCorrect": false, "orderIndex": 4 }
      ]
    }
  ]
}
```

---

## Validation Rules

### Assessment Level
1. `content` MUST be valid JSON (enforced by SQL `ISJSON()` constraint)
2. `version` MUST be present
3. `questions` array MUST contain at least 1 question

### Question Level
1. All `id` values MUST be unique within the assessment
2. `orderIndex` values MUST be sequential starting from 1
3. `questionType` MUST be one of: `multiple_choice`, `true_false`
4. `sectionSlug` MUST match an existing `section.slug` in the Learning Service
5. `options` MUST contain at least 2 elements

### Option Level
1. All option `id` values MUST be unique within the question
2. `orderIndex` values MUST be sequential starting from 1
3. Exactly 1 option per question MUST have `isCorrect: true`
4. For `true_false`: exactly 2 options, texts must be `"True"` and `"False"`

---

## Version History

| Version | Date       | Changes                                                                                                                                                                        |
|---------|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0     | 2026-02-03 | Initial specification                                                                                                                                                          |
| 1.1     | 2026-03-19 | Removed `scale` question type and `scoreValue`; replaced with `isCorrect`. Removed `category`; replaced with `sectionSlug` (maps to `section.slug`). Aligned to v5 schema `initial_user_section_proficiency`. |