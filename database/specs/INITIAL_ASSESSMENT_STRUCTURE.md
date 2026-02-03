# Initial Assessment JSON Structure Specification

## Overview

The initial assessment in BioBasics is a questionnaire presented to new users to gauge their existing medical knowledge and personalize their learning path. Questions and options are stored as structured JSON in the `content` column.

Unlike course quizzes or section tests, initial assessment options have **score values** instead of correct/incorrect flags, allowing for weighted scoring to categorize users into knowledge tiers.

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
  "questionText": "How confident are you in performing CPR?",
  "questionType": "scale",
  "category": "emergency_response",
  "orderIndex": 1,
  "options": [ ... ]
}
```

| Field          | Type    | Required | Max Length | Description                                               |
|----------------|---------|----------|------------|-----------------------------------------------------------|
| `id`           | string  | Yes      | 50         | Unique identifier within the assessment (e.g., `q-001`)   |
| `questionText` | string  | Yes      | 1000       | The question being asked                                  |
| `questionType` | string  | Yes      | -          | One of: `"multiple_choice"`, `"true_false"`, `"scale"`    |
| `category`     | string  | No       | 100        | Category for grouping/analysis (e.g., `"emergency"`)      |
| `orderIndex`   | integer | Yes      | -          | Display order (1-based, must be sequential)               |
| `options`      | array   | Yes      | -          | Array of answer option objects (min 2 elements)           |

---

## Answer Option Structure

```json
{
  "id": "opt-001",
  "text": "Very confident - I'm certified",
  "scoreValue": 5,
  "orderIndex": 1
}
```

| Field        | Type    | Required | Max Length | Description                                    |
|--------------|---------|----------|------------|------------------------------------------------|
| `id`         | string  | Yes      | 50         | Unique option identifier within the question   |
| `text`       | string  | Yes      | 500        | The answer option text                         |
| `scoreValue` | integer | Yes      | -          | Score contribution for this answer (0+)        |
| `orderIndex` | integer | Yes      | -          | Display order of options                       |

---

## Question Type Specifications

### Multiple Choice (`multiple_choice`)
- **Options required:** 2-6 options
- **Score values:** Each option has its own score (can be same or different)
- **Use case:** Knowledge assessment with weighted answers

### True/False (`true_false`)
- **Options required:** Exactly 2 options
- **Option texts:** Should be `"True"` and `"False"`
- **Score values:** Typically 1 for correct, 0 for incorrect
- **Use case:** Fact-checking existing knowledge

### Scale (`scale`)
- **Options required:** 3-7 options
- **Score values:** Typically ascending (0, 1, 2, 3, 4) or (1, 2, 3, 4, 5)
- **Use case:** Self-assessment of confidence/familiarity levels

---

## Category Guidelines

Categories help analyze user knowledge across different domains:

| Category             | Description                                    |
|----------------------|------------------------------------------------|
| `emergency_response` | CPR, choking, bleeding, shock                  |
| `mental_health`      | Stress, anxiety, depression awareness          |
| `nutrition`          | Diet, vitamins, hydration                      |
| `first_aid`          | Wounds, burns, fractures                       |
| `chronic_conditions` | Diabetes, hypertension, asthma management      |
| `general_wellness`   | Exercise, sleep, preventive care               |

---

## Complete Example

```json
{
  "version": "1.0",
  "questions": [
    {
      "id": "q-001",
      "questionText": "How confident are you in performing CPR on an adult?",
      "questionType": "scale",
      "category": "emergency_response",
      "orderIndex": 1,
      "options": [
        {
          "id": "opt-001",
          "text": "Not at all confident",
          "scoreValue": 0,
          "orderIndex": 1
        },
        {
          "id": "opt-002",
          "text": "Slightly confident",
          "scoreValue": 1,
          "orderIndex": 2
        },
        {
          "id": "opt-003",
          "text": "Moderately confident",
          "scoreValue": 2,
          "orderIndex": 3
        },
        {
          "id": "opt-004",
          "text": "Very confident",
          "scoreValue": 3,
          "orderIndex": 4
        },
        {
          "id": "opt-005",
          "text": "Extremely confident - I'm certified",
          "scoreValue": 4,
          "orderIndex": 5
        }
      ]
    },
    {
      "id": "q-002",
      "questionText": "The correct compression rate for adult CPR is 100-120 compressions per minute.",
      "questionType": "true_false",
      "category": "emergency_response",
      "orderIndex": 2,
      "options": [
        {
          "id": "opt-001",
          "text": "True",
          "scoreValue": 1,
          "orderIndex": 1
        },
        {
          "id": "opt-002",
          "text": "False",
          "scoreValue": 0,
          "orderIndex": 2
        }
      ]
    },
    {
      "id": "q-003",
      "questionText": "Which of the following is a sign of a heart attack?",
      "questionType": "multiple_choice",
      "category": "emergency_response",
      "orderIndex": 3,
      "options": [
        {
          "id": "opt-001",
          "text": "Pain in the jaw or arm",
          "scoreValue": 2,
          "orderIndex": 1
        },
        {
          "id": "opt-002",
          "text": "Itchy skin",
          "scoreValue": 0,
          "orderIndex": 2
        },
        {
          "id": "opt-003",
          "text": "Runny nose",
          "scoreValue": 0,
          "orderIndex": 3
        },
        {
          "id": "opt-004",
          "text": "I don't know",
          "scoreValue": 0,
          "orderIndex": 4
        }
      ]
    },
    {
      "id": "q-004",
      "questionText": "How often do you read about health and wellness topics?",
      "questionType": "scale",
      "category": "general_wellness",
      "orderIndex": 4,
      "options": [
        {
          "id": "opt-001",
          "text": "Never",
          "scoreValue": 0,
          "orderIndex": 1
        },
        {
          "id": "opt-002",
          "text": "Rarely (few times a year)",
          "scoreValue": 1,
          "orderIndex": 2
        },
        {
          "id": "opt-003",
          "text": "Sometimes (monthly)",
          "scoreValue": 2,
          "orderIndex": 3
        },
        {
          "id": "opt-004",
          "text": "Often (weekly)",
          "scoreValue": 3,
          "orderIndex": 4
        },
        {
          "id": "opt-005",
          "text": "Very often (daily)",
          "scoreValue": 4,
          "orderIndex": 5
        }
      ]
    },
    {
      "id": "q-005",
      "questionText": "Do you have any medical or healthcare background?",
      "questionType": "multiple_choice",
      "category": "general_wellness",
      "orderIndex": 5,
      "options": [
        {
          "id": "opt-001",
          "text": "No medical background",
          "scoreValue": 0,
          "orderIndex": 1
        },
        {
          "id": "opt-002",
          "text": "Took a first aid course",
          "scoreValue": 2,
          "orderIndex": 2
        },
        {
          "id": "opt-003",
          "text": "Healthcare student",
          "scoreValue": 4,
          "orderIndex": 3
        },
        {
          "id": "opt-004",
          "text": "Healthcare professional",
          "scoreValue": 5,
          "orderIndex": 4
        }
      ]
    }
  ]
}
```

---

## Scoring and User Categorization

### Total Score Calculation

```
User Total Score = Sum of scoreValue for all selected answers
Max Possible Score = Sum of max scoreValue for each question
Percentage = (User Total Score / Max Possible Score) × 100
```

### Category Score Calculation

```
Category Score = Sum of scoreValue for answers in that category
Category Max = Sum of max scoreValue for questions in that category
```

### Suggested Knowledge Tiers

| Tier         | Percentage Range | Recommended Path                          |
|--------------|------------------|-------------------------------------------|
| Beginner     | 0-30%            | Start from fundamentals                   |
| Intermediate | 31-60%           | Skip basics, focus on gaps                |
| Advanced     | 61-100%          | Focus on advanced topics and refreshers   |

---

## Validation Rules

### Assessment Level
1. `content` field MUST be valid JSON (enforced by SQL constraint)
2. `version` field MUST be present
3. `questions` array MUST contain at least 1 question

### Question Level
1. All `id` values MUST be unique within the assessment
2. `orderIndex` values MUST be sequential starting from 1
3. `questionType` MUST be one of the allowed values
4. `category` is optional but recommended for analysis
5. `options` array MUST contain at least 2 options

### Option Level
1. All option `id` values MUST be unique within the question
2. `orderIndex` values MUST be sequential starting from 1
3. `scoreValue` MUST be a non-negative integer
4. For `scale`: options should have ascending score values
5. For `true_false`: exactly 2 options

---

## Version History

| Version | Date       | Changes                          |
|---------|------------|----------------------------------|
| 1.0     | 2026-02-03 | Initial specification            |
