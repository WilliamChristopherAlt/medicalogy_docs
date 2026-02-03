# Content JSON Structure Specification

## Overview

This document specifies the JSON structure for **course content** and **section test content** stored in their respective `content` columns.

---

# Part 1: Course Content

A course consists of an ordered array of **screens**. Each screen is either an **infographic** (educational content) or a **quiz** (assessment).

## Root Structure

```json
{
  "version": "1.0",
  "screens": [ ... ]
}
```

| Field      | Type   | Required | Description                                      |
|------------|--------|----------|--------------------------------------------------|
| `version`  | string | Yes      | Schema version for forward compatibility         |
| `screens`  | array  | Yes      | Ordered array of screen objects (min 1 element)  |

---

## Screen Object (Base)

```json
{
  "id": "screen-001",
  "type": "infographic",
  "orderIndex": 1,
  "content": { ... }
}
```

| Field        | Type   | Required | Description                                      |
|--------------|--------|----------|--------------------------------------------------|
| `id`         | string | Yes      | Unique identifier within the course              |
| `type`       | string | Yes      | One of: `"infographic"`, `"quiz"`                |
| `orderIndex` | int    | Yes      | Display order (1-based, sequential)              |
| `content`    | object | Yes      | Type-specific content (see below)                |

---

## Screen Content by Type

### Infographic (`infographic`)

```json
{
  "id": "screen-001",
  "type": "infographic",
  "orderIndex": 1,
  "content": {
    "imageFileName": "choking_step1.png",
    "summaryText": "If someone is choking, first ask them 'Are you choking?' and look for signs..."
  }
}
```

| Field           | Type   | Required | Max Length | Description                           |
|-----------------|--------|----------|------------|---------------------------------------|
| `imageFileName` | string | No       | 255        | Filename of infographic image         |
| `summaryText`   | string | Yes      | 2000       | Educational text                      |

---

### Quiz

See **Part 3: Question Content Types** for the content structure. Quiz screens use the same question content structure without `difficultyLevel`.

```json
{
  "id": "screen-002",
  "type": "quiz",
  "orderIndex": 2,
  "content": { /* question content - see Part 3 */ }
}
```

---

## Course Example

```json
{
  "version": "1.0",
  "screens": [
    {
      "id": "screen-001",
      "type": "infographic",
      "orderIndex": 1,
      "content": {
        "imageFileName": "choking_recognition.png",
        "summaryText": "Choking occurs when an object blocks the airway."
      }
    },
    {
      "id": "screen-002",
      "type": "quiz",
      "orderIndex": 2,
      "content": {
        "questionType": "multiple_choice",
        "questionText": "What is the universal sign that someone is choking?",
        "explanation": "The universal choking sign is recognized worldwide.",
        "options": [
          { "id": "a", "text": "Waving hands frantically", "isCorrect": false },
          { "id": "b", "text": "Clutching the throat", "isCorrect": true }
        ]
      }
    }
  ]
}
```

---

# Part 2: Section Test Content

A section test consists of an ordered array of **questions** with difficulty levels.

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

## Question Object (Base)

```json
{
  "id": "q-001",
  "orderIndex": 1,
  "difficultyLevel": "medium",
  "content": { ... }
}
```

| Field             | Type   | Required | Description                                    |
|-------------------|--------|----------|------------------------------------------------|
| `id`              | string | Yes      | Unique identifier within the test              |
| `orderIndex`      | int    | Yes      | Display order (1-based, sequential)            |
| `difficultyLevel` | string | Yes      | One of: `"easy"`, `"medium"`, `"hard"`         |
| `content`         | object | Yes      | Question content (see Part 3)                  |

---

## Section Test Example

```json
{
  "version": "1.0",
  "questions": [
    {
      "id": "q-001",
      "orderIndex": 1,
      "difficultyLevel": "easy",
      "content": {
        "questionType": "multiple_choice",
        "questionText": "What is the universal sign that someone is choking?",
        "explanation": "The universal choking sign is recognized worldwide.",
        "options": [
          { "id": "a", "text": "Waving hands frantically", "isCorrect": false },
          { "id": "b", "text": "Clutching the throat", "isCorrect": true }
        ]
      }
    },
    {
      "id": "q-002",
      "orderIndex": 2,
      "difficultyLevel": "medium",
      "content": {
        "questionType": "matching",
        "sentence": "Call <1> for emergencies.\nPerform <2> if not breathing.",
        "correctAnswers": ["911", "CPR"],
        "wrongAnswers": ["123", "AED"]
      }
    }
  ]
}
```

---

# Part 3: Question Content Types

These content structures are used by both **course quizzes** and **section test questions**.

## Multiple Choice (`questionType: "multiple_choice"`)

```json
{
  "questionType": "multiple_choice",
  "questionText": "What is the universal sign that someone is choking?",
  "explanation": "The universal choking sign is recognized worldwide.",
  "options": [
    { "id": "a", "text": "Waving hands frantically", "isCorrect": false },
    { "id": "b", "text": "Clutching the throat with both hands", "isCorrect": true },
    { "id": "c", "text": "Pointing at their mouth", "isCorrect": false }
  ]
}
```

| Field          | Type   | Required | Max Length | Description                                    |
|----------------|--------|----------|------------|------------------------------------------------|
| `questionType` | string | Yes      | -          | `"multiple_choice"`                            |
| `questionText` | string | Yes      | 1000       | The question being asked                       |
| `explanation`  | string | No       | 2000       | Explanation shown after answering              |
| `options`      | array  | Yes      | -          | 2-6 options, exactly 1 with `isCorrect: true`  |

**Option structure:**

| Field       | Type    | Required | Description                    |
|-------------|---------|----------|--------------------------------|
| `id`        | string  | Yes      | Unique within this question    |
| `text`      | string  | Yes      | The answer text                |
| `isCorrect` | boolean | Yes      | `true` for the correct answer  |

---

## True/False (`questionType: "true_false"`)

```json
{
  "questionType": "true_false",
  "questionText": "Back blows should be delivered between the shoulder blades.",
  "explanation": "Back blows are most effective when delivered to the upper back.",
  "correctAnswer": true
}
```

| Field           | Type    | Required | Max Length | Description                        |
|-----------------|---------|----------|------------|------------------------------------|
| `questionType`  | string  | Yes      | -          | `"true_false"`                     |
| `questionText`  | string  | Yes      | 1000       | The statement to evaluate          |
| `explanation`   | string  | No       | 2000       | Explanation shown after answering  |
| `correctAnswer` | boolean | Yes      | -          | `true` or `false`                  |

---

## Matching (`questionType: "matching"`)

Fill-in-the-blank style where users match answers to numbered placeholders.

```json
{
  "questionType": "matching",
  "sentence": "If you see a fainted person, call <1>.\nIf they aren't breathing perform <2>.",
  "correctAnswers": ["911", "CPR"],
  "wrongAnswers": ["123", "abc", "wrong answer"]
}
```

| Field            | Type   | Required | Description                                                    |
|------------------|--------|----------|----------------------------------------------------------------|
| `questionType`   | string | Yes      | `"matching"`                                                   |
| `sentence`       | string | Yes      | Text with `<1>`, `<2>`, etc. placeholders. `\n` for newlines.  |
| `correctAnswers` | array  | Yes      | Ordered array: `correctAnswers[0]` → `<1>`, `[1]` → `<2>`, etc.|
| `wrongAnswers`   | array  | Yes      | Distractor options displayed alongside correct answers         |

App displays all answers (correct + wrong) shuffled for user to drag/select into blanks.

---

# Part 4: Validation Rules

# Part 4: Validation Rules

## Course Content
1. `version` MUST be present
2. `screens` array MUST contain at least 1 screen
3. All screen `id` values MUST be unique
4. `orderIndex` values MUST be sequential starting from 1

## Section Test Content
1. `version` MUST be present
2. `questions` array MUST contain at least 1 question
3. All question `id` values MUST be unique
4. `orderIndex` values MUST be sequential starting from 1
5. `difficultyLevel` MUST be one of: `easy`, `medium`, `hard`

## Infographic Content
1. `summaryText` MUST be non-empty

## Multiple Choice
1. `questionText` MUST be non-empty
2. `options` MUST have 2-6 items
3. Exactly 1 option MUST have `isCorrect: true`

## True/False
1. `questionText` MUST be non-empty
2. `correctAnswer` MUST be `true` or `false`

## Matching
1. `sentence` MUST contain at least one placeholder (`<1>`)
2. `correctAnswers` length MUST match number of placeholders
3. `wrongAnswers` MUST have at least 1 item

---

## Version History

| Version | Date       | Changes             |
|---------|------------|---------------------|
| 1.0     | 2026-02-03 | Initial specification |
