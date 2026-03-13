#!/usr/bin/env python3

import hashlib
import json
import uuid
from pathlib import Path
from typing import Any


# ============================================================
# GENERATION PROFILE (spec-friendly switches)
# ============================================================
# If specs change later, update this profile instead of rewriting logic.
GENERATION_PROFILE = {
    "store_content_as_filename": True,
    "image_reference_mode": "media_file_name",  # media_file_name | remote_url
}

# ============================================================
# FULL-FLEDGED DEBUG TARGETS
# ============================================================
# These slugs will receive richer, long-form content for debugging/demo quality.
FULL_FLEDGED_ARTICLE_SLUGS = {
    "airway-emergencies-recognition",
    "mood-disorders-recognition-and-care",
}
FULL_FLEDGED_COURSE_SLUGS = {
    "recognizing-choking-in-adults",
    "suicide-risk-rapid-screen",
}


SCRIPT_DIR = Path(__file__).resolve().parent
LAYOUT_FILE = SCRIPT_DIR / "content_layout.json"
OUTPUT_DIR = SCRIPT_DIR / "generated"
CONTENT_FILES_DIR = SCRIPT_DIR / "content_files"
COURSE_CONTENT_DIR = CONTENT_FILES_DIR / "courses"
ARTICLE_CONTENT_DIR = CONTENT_FILES_DIR / "articles"
MEDIA_DATASET_DIR = SCRIPT_DIR / "medicalogy medias"
FINAL_DATA_FILE = OUTPUT_DIR / "mockup_data.json"
MANIFEST_FILE = OUTPUT_DIR / "manifest.json"
PIPELINE_SQL_FILE = SCRIPT_DIR / "pipeline.sql"
SCHEMA_FILE = SCRIPT_DIR.parent / "database" / "versions" / "schema v4.sql"


def stable_uuid(key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"medicalogy:{key}")).upper()


def stable_int(key: str) -> int:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def sql_escape(text: str) -> str:
    return text.replace("'", "''")


def nvarchar(value: str) -> str:
    return f"N'{sql_escape(value)}'"


def quote_guid(guid: str) -> str:
    return f"'{guid}'"


def read_layout() -> dict[str, Any]:
    if not LAYOUT_FILE.exists():
        raise FileNotFoundError(f"Missing layout file: {LAYOUT_FILE}")

    with LAYOUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_media_files() -> list[str]:
    if not MEDIA_DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Missing media dataset folder: {MEDIA_DATASET_DIR}. "
            "Create it and add common media files before generation."
        )

    files = sorted(
        [
            file.name
            for file in MEDIA_DATASET_DIR.iterdir()
            if file.is_file() and file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".avif"}
        ]
    )

    if not files:
        raise ValueError(f"No media files found in: {MEDIA_DATASET_DIR}")

    return files


def pick_media_file(media_files: list[str], seed_key: str) -> str:
    return media_files[stable_int(seed_key) % len(media_files)]


SECTION_PROFILES: dict[str, dict[str, str]] = {
    "airway-emergencies": {
        "core": "rapid airway patency check and oxygenation support",
        "immediate": "open airway, call support, and monitor breathing continuously",
        "escalation": "stridor, cyanosis, decreasing consciousness, or no airflow",
        "pitfall": "delaying escalation while obstruction signs are worsening",
    },
    "cardiac-emergencies": {
        "core": "early recognition of ischemia or arrest and immediate protocol activation",
        "immediate": "assess circulation, start CPR when indicated, and prepare AED",
        "escalation": "persistent chest pain, hypotension, altered mental status, or pulselessness",
        "pitfall": "waiting for definitive tests before starting first-line emergency care",
    },
    "trauma-first-response": {
        "core": "ABCDE trauma survey with hemorrhage control",
        "immediate": "secure scene safety, identify life threats, and control major bleeding",
        "escalation": "airway compromise, shock signs, uncontrolled bleeding, or reduced GCS",
        "pitfall": "focusing on minor injuries before treating life-threatening problems",
    },
    "anxiety-spectrum-disorders": {
        "core": "symptom pattern recognition and functional impairment assessment",
        "immediate": "establish safety, rule out medical mimics, and use calm communication",
        "escalation": "severe distress, suicidality, substance risk, or inability to self-care",
        "pitfall": "labeling all somatic symptoms as psychological without clinical screening",
    },
    "mood-disorders": {
        "core": "structured mood episode assessment and risk stratification",
        "immediate": "evaluate mood symptoms, sleep, appetite, and suicide risk",
        "escalation": "active suicidality, psychosis, severe functional decline, or mania",
        "pitfall": "missing bipolar features before initiating antidepressant plans",
    },
    "crisis-intervention": {
        "core": "immediate safety planning and de-escalation",
        "immediate": "reduce stimulation, use simple language, and define immediate safety steps",
        "escalation": "imminent self-harm risk, violence risk, or inability to maintain safety",
        "pitfall": "arguing with a distressed patient instead of stabilizing first",
    },
    "sleep-and-stress-medicine": {
        "core": "sleep pattern assessment and stress-load management",
        "immediate": "identify sleep disruptors and start behavior-based interventions",
        "escalation": "persistent insomnia with safety risk, severe depression, or substance misuse",
        "pitfall": "using sedative-only strategies without behavioral foundations",
    },
    "balanced-nutrition-principles": {
        "core": "balanced macro/micronutrient planning",
        "immediate": "assess dietary intake and set one realistic nutritional goal",
        "escalation": "rapid weight loss, malnutrition signs, or high-risk metabolic markers",
        "pitfall": "giving generic advice that ignores patient context and affordability",
    },
    "clinical-nutrition-in-chronic-disease": {
        "core": "condition-specific nutrition adjustment and adherence",
        "immediate": "align meal strategy with diagnosis, meds, and lab priorities",
        "escalation": "poor control despite adherence, renal risk markers, or recurrent admissions",
        "pitfall": "applying one diet template to all chronic disease profiles",
    },
    "metabolic-syndrome-and-obesity": {
        "core": "cardiometabolic risk clustering and staged intervention",
        "immediate": "screen waist, blood pressure, glucose, and lipid indicators",
        "escalation": "rapid progression, organ complications, or failure of first-line plans",
        "pitfall": "focusing on weight alone without metabolic risk tracking",
    },
    "prevention-and-infection-control": {
        "core": "transmission prevention through hygiene and PPE",
        "immediate": "perform hand hygiene and select PPE by transmission route",
        "escalation": "clustered cases, high-risk exposure, or protocol breach",
        "pitfall": "incorrect donning/doffing sequence causing self-contamination",
    },
    "respiratory-infections": {
        "core": "triage severity and supportive respiratory care",
        "immediate": "assess respiratory rate, oxygenation, and danger symptoms",
        "escalation": "hypoxia, work of breathing increase, hemodynamic instability",
        "pitfall": "underestimating deterioration in older or comorbid patients",
    },
    "gastrointestinal-infections": {
        "core": "dehydration risk assessment and rehydration planning",
        "immediate": "estimate fluid deficit and start oral or IV rehydration appropriately",
        "escalation": "severe dehydration, blood in stool, persistent vomiting, or shock",
        "pitfall": "delayed fluid replacement while waiting for confirmatory testing",
    },
    "vector-borne-diseases": {
        "core": "early recognition of endemic vector-borne illness patterns",
        "immediate": "screen travel/exposure history and warning signs",
        "escalation": "bleeding signs, neurologic symptoms, organ dysfunction, or severe fever",
        "pitfall": "ignoring local epidemiology during early triage",
    },
    "prenatal-care-pathways": {
        "core": "risk-based prenatal follow-up and maternal-fetal monitoring",
        "immediate": "confirm gestational age, vitals, and baseline screening",
        "escalation": "hypertension, bleeding, reduced fetal movement, or severe symptoms",
        "pitfall": "missing early warning signs between scheduled visits",
    },
    "newborn-care-essentials": {
        "core": "early neonatal assessment and stabilization",
        "immediate": "check breathing, temperature, feeding ability, and jaundice status",
        "escalation": "poor feeding, lethargy, cyanosis, fever/hypothermia, or apnea",
        "pitfall": "delaying referral when danger signs persist",
    },
    "common-pediatric-illnesses": {
        "core": "pediatric triage with dehydration and respiratory red-flag detection",
        "immediate": "use age-based assessment and parental symptom timeline",
        "escalation": "respiratory distress, altered consciousness, persistent high fever",
        "pitfall": "using adult thresholds for pediatric vital signs",
    },
}


def section_profile(theme_name: str, section: dict[str, Any]) -> dict[str, str]:
    section_slug = section["slug"]
    if section_slug in SECTION_PROFILES:
        return SECTION_PROFILES[section_slug]
    return {
        "core": f"structured practice in {section['name'].lower()}",
        "immediate": f"apply first-line protocol steps for {section['name'].lower()}",
        "escalation": "persistent instability after first-line interventions",
        "pitfall": "inconsistent reassessment and documentation",
    }


def sentence_start(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def validate_layout(layout: dict[str, Any]) -> None:
    themes = layout.get("themes", [])
    if len(themes) != 5:
        raise ValueError(f"Expected exactly 5 themes, got {len(themes)}")

    theme_slugs: set[str] = set()
    section_slugs: set[str] = set()
    course_slugs: set[str] = set()
    article_slugs: set[str] = set()

    for theme in themes:
        theme_slug = theme["slug"]
        if theme_slug in theme_slugs:
            raise ValueError(f"Duplicate theme slug: {theme_slug}")
        theme_slugs.add(theme_slug)

        sections = theme.get("sections", [])
        if len(sections) < 3 or len(sections) > 4:
            raise ValueError(
                f"Theme '{theme_slug}' must have 3-4 sections, got {len(sections)}"
            )

        for section in sections:
            section_slug = section["slug"]
            if section_slug in section_slugs:
                raise ValueError(f"Duplicate section slug: {section_slug}")
            section_slugs.add(section_slug)

            infographic_slug = section["infographic"]["slug"]
            if infographic_slug in article_slugs:
                raise ValueError(f"Duplicate infographic slug: {infographic_slug}")
            article_slugs.add(infographic_slug)

            courses = section.get("courses", [])
            if len(courses) < 3 or len(courses) > 6:
                raise ValueError(
                    f"Section '{section_slug}' must have 3-6 courses, got {len(courses)}"
                )

            for course in courses:
                course_slug = course["slug"]
                if course_slug in course_slugs:
                    raise ValueError(f"Duplicate course slug: {course_slug}")
                course_slugs.add(course_slug)


def build_mcq(course_name: str, objective: str) -> dict[str, Any]:
    return {
        "questionType": "multiple_choice",
        "questionText": f"Which action best supports this course objective: {objective}?",
        "explanation": (
            f"The best answer directly helps learners apply '{objective}' while studying {course_name}."
        ),
        "options": [
            {"id": "a", "text": "Use a structured checklist and verify outcomes", "isCorrect": True},
            {"id": "b", "text": "Skip baseline assessment to save time", "isCorrect": False},
            {"id": "c", "text": "Rely only on memory without documentation", "isCorrect": False},
            {"id": "d", "text": "Delay escalation despite red flags", "isCorrect": False},
        ],
    }


def build_clinical_mcq(course_name: str, objective: str, profile: dict[str, str]) -> dict[str, Any]:
    return {
        "questionType": "multiple_choice",
        "questionText": f"In {course_name}, which action best supports '{objective}'?",
        "explanation": "Correct answers prioritize patient safety, reassessment, and timely escalation.",
        "options": [
            {"id": "a", "text": sentence_start(profile["immediate"]), "isCorrect": True},
            {"id": "b", "text": sentence_start(profile["pitfall"]), "isCorrect": False},
            {"id": "c", "text": "Delay reassessment until symptoms are severe", "isCorrect": False},
            {"id": "d", "text": "Use treatment decisions without baseline documentation", "isCorrect": False},
        ],
    }


def build_escalation_true_false(profile: dict[str, str]) -> dict[str, Any]:
    return {
        "questionType": "true_false",
        "questionText": f"Escalation is required when {profile['escalation']}.",
        "explanation": "Early escalation reduces preventable deterioration and delays in definitive care.",
        "correctAnswer": True,
    }


def build_true_false(course_name: str, objective: str) -> dict[str, Any]:
    return {
        "questionType": "true_false",
        "questionText": f"A clear plan for '{objective}' improves consistency in {course_name}.",
        "explanation": "Structured plans reduce omissions and improve safe, repeatable care.",
        "correctAnswer": True,
    }


def build_matching() -> dict[str, Any]:
    return {
        "questionType": "matching",
        "sentence": (
            "Start with <1> to establish baseline status.\n"
            "Use <2> to deliver standardized intervention.\n"
            "Document <3> to support continuity and quality review."
        ),
        "correctAnswers": ["assessment", "protocol", "outcomes"],
        "wrongAnswers": ["guesswork", "delay", "omission"],
    }


def build_default_course_content(
    theme_name: str,
    section_slug: str,
    section_name: str,
    course: dict[str, Any],
    media_files: list[str],
) -> dict[str, Any]:
    objectives = course.get("objectives", [])
    first_obj = objectives[0] if objectives else "apply core concepts"
    second_obj = objectives[1] if len(objectives) > 1 else "use a safe and consistent workflow"
    profile = section_profile(theme_name, {"slug": section_slug, "name": section_name})

    image_1 = pick_media_file(media_files, f"{course['slug']}:screen-1")
    image_3 = pick_media_file(media_files, f"{course['slug']}:screen-3")

    return {
        "version": "1.1",
        "screens": [
            {
                "id": "screen-001",
                "type": "infographic",
                "orderIndex": 1,
                "content": {
                    "imageFileName": image_1,
                    "summaryText": (
                        f"{course['name']} in {section_name} focuses on {profile['core']}. "
                        f"Primary objective: {first_obj}."
                    ),
                },
            },
            {
                "id": "screen-002",
                "type": "quiz",
                "orderIndex": 2,
                "content": build_clinical_mcq(course["name"], first_obj, profile),
            },
            {
                "id": "screen-003",
                "type": "infographic",
                "orderIndex": 3,
                "content": {
                    "imageFileName": image_3,
                    "summaryText": (
                        f"Immediate priority: {profile['immediate']}. "
                        f"Practical emphasis: {second_obj}."
                    ),
                },
            },
            {
                "id": "screen-004",
                "type": "quiz",
                "orderIndex": 4,
                "content": build_escalation_true_false(profile),
            },
            {
                "id": "screen-005",
                "type": "quiz",
                "orderIndex": 5,
                "content": build_matching(),
            },
        ],
    }


def build_full_fledged_course_content(
    theme_name: str,
    section_slug: str,
    section_name: str,
    course: dict[str, Any],
    media_files: list[str],
) -> dict[str, Any]:
    objectives = course.get("objectives", [])
    objective_a = objectives[0] if objectives else "Perform structured first-line assessment"
    objective_b = objectives[1] if len(objectives) > 1 else "Apply protocol-based interventions"
    objective_c = objectives[2] if len(objectives) > 2 else "Escalate care safely"
    profile = section_profile(theme_name, {"slug": section_slug, "name": section_name})

    image_a = pick_media_file(media_files, f"{course['slug']}:full:a")
    image_b = pick_media_file(media_files, f"{course['slug']}:full:b")
    image_c = pick_media_file(media_files, f"{course['slug']}:full:c")
    image_d = pick_media_file(media_files, f"{course['slug']}:full:d")

    return {
        "version": "2.0",
        "meta": {
            "contentDepth": "full-fledged",
            "theme": theme_name,
            "section": section_name,
            "course": course["name"],
            "estimatedDurationMinutes": course["estimated_duration_minutes"],
        },
        "screens": [
            {
                "id": "screen-001",
                "type": "infographic",
                "orderIndex": 1,
                "content": {
                    "imageFileName": image_a,
                    "summaryText": (
                        f"{course['name']} introduces a complete practice flow in {section_name}: "
                        f"{profile['core']}."
                    ),
                },
            },
            {
                "id": "screen-002",
                "type": "infographic",
                "orderIndex": 2,
                "content": {
                    "imageFileName": image_b,
                    "summaryText": (
                        f"Core principle set: {profile['immediate']}, closed-loop communication, "
                        "and explicit reassessment after each intervention."
                    ),
                },
            },
            {
                "id": "screen-003",
                "type": "quiz",
                "orderIndex": 3,
                "content": {
                    "questionType": "multiple_choice",
                    "questionText": f"Which action best demonstrates objective: {objective_a}?",
                    "explanation": "Choose the option that creates immediate safety and measurable clinical value.",
                    "options": [
                        {"id": "a", "text": sentence_start(profile["immediate"]), "isCorrect": True},
                        {"id": "b", "text": "Begin treatment before any assessment", "isCorrect": False},
                        {"id": "c", "text": "Wait for specialist input before basic checks", "isCorrect": False},
                        {"id": "d", "text": "Use only subjective impressions", "isCorrect": False},
                    ],
                },
            },
            {
                "id": "screen-004",
                "type": "infographic",
                "orderIndex": 4,
                "content": {
                    "imageFileName": image_c,
                    "summaryText": (
                        f"Objective focus: {objective_b}. "
                        f"Avoid common pitfall: {profile['pitfall']}."
                    ),
                },
            },
            {
                "id": "screen-005",
                "type": "quiz",
                "orderIndex": 5,
                "content": {
                    "questionType": "true_false",
                    "questionText": f"Escalation is required when {profile['escalation']}.",
                    "explanation": "Timely escalation prevents avoidable deterioration and delays in definitive treatment.",
                    "correctAnswer": True,
                },
            },
            {
                "id": "screen-006",
                "type": "quiz",
                "orderIndex": 6,
                "content": {
                    "questionType": "matching",
                    "sentence": (
                        "Step 1: <1> the patient and context.\n"
                        "Step 2: <2> protocol-based interventions.\n"
                        "Step 3: <3> outcomes and escalation criteria."
                    ),
                    "correctAnswers": ["Assess", "Implement", "Document"],
                    "wrongAnswers": ["Guess", "Delay", "Ignore"],
                },
            },
            {
                "id": "screen-007",
                "type": "infographic",
                "orderIndex": 7,
                "content": {
                    "imageFileName": image_d,
                    "summaryText": (
                        f"Final objective: {objective_c}. "
                        f"Escalation trigger: {profile['escalation']}."
                    ),
                },
            },
            {
                "id": "screen-008",
                "type": "quiz",
                "orderIndex": 8,
                "content": {
                    "questionType": "multiple_choice",
                    "questionText": "What is the best escalation trigger?",
                    "explanation": "Escalation should be based on persistent or worsening high-risk findings.",
                    "options": [
                        {"id": "a", "text": sentence_start(profile["escalation"]), "isCorrect": True},
                        {"id": "b", "text": "Escalate only when all signs are normal", "isCorrect": False},
                        {"id": "c", "text": "Never escalate if resources are limited", "isCorrect": False},
                        {"id": "d", "text": "Escalate only at patient request", "isCorrect": False},
                    ],
                },
            },
        ],
    }


def build_default_infographic_markdown(theme: dict[str, Any], section: dict[str, Any], media_files: list[str]) -> str:
    infographic = section["infographic"]
    profile = section_profile(theme["name"], section)
    image = pick_media_file(media_files, f"{infographic['slug']}:std:hero")
    lines = [
        f"# {infographic['title']}",
        "",
        infographic["intro"],
        "",
        f"![center|{infographic['title']} visual]({image})",
        "/Section snapshot for quick clinical orientation./",
        "",
        "---",
        "",
        "## Why This Matters",
        "",
        (
            f"This infographic belongs to the theme *{theme['name']}* and section "
            f"*{section['name']}*. It provides concise guidance on {profile['core']}."
        ),
        "",
        "## Key Focus Points",
        "",
        "[[[",
    ]

    for point in infographic.get("focus_points", []):
        lines.append(f"- *{point}*")

    lines.extend(
        [
            "]]]",
            "",
            "",
            "## Red Flags",
            "",
            "[[[",
            f"- *Escalate when:* {profile['escalation']}",
            f"- *Avoid:* {profile['pitfall']}",
            "]]]",
        ]
    )

    lines.extend(
        [
            "",
            "## Section Learning Units",
            "",
            "| Course | Focus |",
            "|--------|-------|",
        ]
    )

    for course in section.get("courses", []):
        lines.append(f"| {course['name']} | {course['description']} |")

    lines.extend(["", "## Sources", "", "[[["])

    for source in infographic.get("sources", []):
        lines.append(f"- {{Reference|{source}}}")

    lines.extend(["]]]", ""])
    return "\n".join(lines)


def build_full_fledged_infographic_markdown(
    theme: dict[str, Any],
    section: dict[str, Any],
    media_files: list[str],
) -> str:
    infographic = section["infographic"]
    profile = section_profile(theme["name"], section)

    image_a = pick_media_file(media_files, f"{infographic['slug']}:article:a")
    image_b = pick_media_file(media_files, f"{infographic['slug']}:article:b")

    lines = [
        f"# {infographic['title']}",
        "",
        (
            f"{infographic['intro']} This page is a full-fledged reference article with practical pathways, "
            "risk markers, and implementation guidance."
        ),
        "",
        f"![center|{infographic['title']} visual]({image_a})",
        "/Core visual for section-level orientation./",
        "",
        "---",
        "",
        "## Clinical Context",
        "",
        (
            f"Within *{theme['name']}*, the section *{section['name']}* addresses time-sensitive decisions, "
            f"structured communication, and measurable safety outcomes around {profile['core']}."
        ),
        "",
        "## Structured Focus",
        "",
        "[[[",
    ]

    for point in infographic.get("focus_points", []):
        lines.append(f"- *{point}* with practical actions and reassessment checkpoints")

    lines.extend(
        [
            "]]]",
            "",
            "## Decision Matrix",
            "",
            "| Situation | Immediate Action | Escalation Trigger |",
            "|-----------|------------------|--------------------|",
            f"| Stable but symptomatic | {profile['immediate'].capitalize()} | No improvement after first cycle |",
            "| Progressive deterioration | Activate rapid team support | Persistent red flags after reassessment |",
            f"| High-risk baseline | Parallel treatment and monitoring | {profile['escalation'].capitalize()} |",
            "",
            f"![right|Team care visual]({image_b})",
            "/Multidisciplinary coordination improves reliability in complex scenarios./",
            "",
            "## Safety Checkpoints",
            "",
            "[[[",
            f"- *Immediate action:* {profile['immediate']}",
            f"- *Escalation trigger:* {profile['escalation']}",
            f"- *Common pitfall:* {profile['pitfall']}",
            "]]]",
            "",
            "## Section Learning Units",
            "",
            "[[[",
        ]
    )

    for idx, course in enumerate(section.get("courses", []), start=1):
        lines.append(f"{idx}. *{course['name']}* - {course['description']}")

    lines.extend(
        [
            "]]]",
            "",
            "## References",
            "",
            "[[[",
        ]
    )

    for source in infographic.get("sources", []):
        lines.append(f"- {{Reference|{source}}}")

    lines.extend(["]]]", ""])
    return "\n".join(lines)


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    COURSE_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLE_CONTENT_DIR.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_course_content(
    theme_name: str,
    section_slug: str,
    section_name: str,
    course: dict[str, Any],
    media_files: list[str],
) -> tuple[dict[str, Any], bool]:
    if course["slug"] in FULL_FLEDGED_COURSE_SLUGS:
        return build_full_fledged_course_content(theme_name, section_slug, section_name, course, media_files), True
    return build_default_course_content(theme_name, section_slug, section_name, course, media_files), False


def build_article_markdown(
    theme: dict[str, Any],
    section: dict[str, Any],
    media_files: list[str],
) -> tuple[str, bool]:
    if section["infographic"]["slug"] in FULL_FLEDGED_ARTICLE_SLUGS:
        return build_full_fledged_infographic_markdown(theme, section, media_files), True
    return build_default_infographic_markdown(theme, section, media_files), False


def theme_tag_name(theme_slug: str) -> str:
    mapping = {
        "emergency-care-fundamentals": "emergency",
        "mental-health-clinical-foundations": "mental-health",
        "nutrition-and-metabolic-health": "nutrition",
        "infectious-disease-essentials": "infection",
        "maternal-and-child-health": "maternal-child",
    }
    return mapping.get(theme_slug, "emergency")


def build_schema_reset_block() -> str:
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Missing schema file: {SCHEMA_FILE}")

    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    reset_sql = [
        "-- ============================================================================",
        "-- FULL RESET + RECREATE",
        "-- ============================================================================",
        "USE master;",
        "GO",
        "IF DB_ID('medicalogy') IS NOT NULL",
        "BEGIN",
        "    ALTER DATABASE medicalogy SET SINGLE_USER WITH ROLLBACK IMMEDIATE;",
        "    DROP DATABASE medicalogy;",
        "END",
        "GO",
        "",
        "-- ============================================================================",
        "-- SCHEMA CREATION",
        "-- ============================================================================",
        schema_sql.strip(),
    ]
    return "\n".join(reset_sql)


def build_section_test_content(section_name: str) -> str:
    payload = {
        "version": "1.0",
        "questions": [
            {
                "id": "q-001",
                "orderIndex": 1,
                "difficultyLevel": "easy",
                "content": {
                    "questionType": "multiple_choice",
                    "questionText": f"What is the first priority in {section_name}?",
                    "explanation": "Start with a rapid, structured assessment and immediate safety actions.",
                    "options": [
                        {"id": "a", "text": "Run structured first-line assessment", "isCorrect": True},
                        {"id": "b", "text": "Delay intervention", "isCorrect": False},
                        {"id": "c", "text": "Skip reassessment", "isCorrect": False},
                    ],
                },
            },
            {
                "id": "q-002",
                "orderIndex": 2,
                "difficultyLevel": "medium",
                "content": {
                    "questionType": "true_false",
                    "questionText": "Escalation is needed when red flags persist after first-line interventions.",
                    "explanation": "Persistent instability requires escalation.",
                    "correctAnswer": True,
                },
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def build_initial_assessment_content() -> str:
    payload = {
        "version": "1.0",
        "questions": [
            {
                "id": "ia-001",
                "orderIndex": 1,
                "content": {
                    "questionType": "multiple_choice",
                    "questionText": "How confident are you with emergency first response basics?",
                    "options": [
                        {"id": "a", "text": "Beginner", "isCorrect": False},
                        {"id": "b", "text": "Intermediate", "isCorrect": True},
                        {"id": "c", "text": "Advanced", "isCorrect": False},
                    ],
                },
            },
            {
                "id": "ia-002",
                "orderIndex": 2,
                "content": {
                    "questionType": "true_false",
                    "questionText": "You are comfortable with structured clinical checklists.",
                    "correctAnswer": True,
                },
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def generate_data(layout: dict[str, Any], media_files: list[str]) -> dict[str, Any]:
    ensure_dirs()

    final_data: dict[str, Any] = {
        "version": layout.get("version", "1.0"),
        "language": layout.get("language", "en"),
        "contentStorageMode": "file_name_reference",
        "themes": [],
    }

    sql_lines: list[str] = [
        "-- Auto-generated by medicalogy_docs/mockup_data/generation.py",
        "-- Source layout: content_layout.json",
        "-- Full-fledge pipeline: RESET DB + CREATE TABLES + INSERT ALL TABLES",
        "-- Content strategy: SQL stores only file names for course/article content",
        "",
    ]

    theme_count = 0
    section_count = 0
    course_count = 0
    article_count = 0
    full_fledged_article_count = 0
    full_fledged_course_count = 0

    theme_rows: list[dict[str, Any]] = []
    section_rows: list[dict[str, Any]] = []
    course_rows: list[dict[str, Any]] = []
    article_rows: list[dict[str, Any]] = []

    # ------------------------------------------------------------------------
    # AUTH SERVICE SEED DATA
    # ------------------------------------------------------------------------
    demographic_adult_id = stable_uuid("demographic:adult")
    demographic_young_id = stable_uuid("demographic:young")

    admin_user_id = stable_uuid("user:admin")
    learner_user_id = stable_uuid("user:learner")

    sql_lines.extend(
        [
            "-- AUTH SERVICE INSERTS",
            (
                "INSERT INTO user_demographic (id, name, description, min_age, max_age) VALUES "
                f"({quote_guid(demographic_adult_id)}, {nvarchar('Adult Learner')}, {nvarchar('General adult learner profile')}, 18, 65);"
            ),
            (
                "INSERT INTO user_demographic (id, name, description, min_age, max_age) VALUES "
                f"({quote_guid(demographic_young_id)}, {nvarchar('Young Adult Learner')}, {nvarchar('Young healthcare-oriented learner profile')}, 16, 30);"
            ),
            (
                "INSERT INTO [user] (id, email, username, password_hash, user_demographic_id, date_of_birth, location, phone_number, oauth_provider, oauth_provider_id, role, is_active, is_verified, last_login_at) VALUES "
                f"({quote_guid(admin_user_id)}, {nvarchar('admin@medicalogy.io')}, {nvarchar('admin')}, {nvarchar('hashed_admin_password')}, {quote_guid(demographic_adult_id)}, '1990-05-14', {nvarchar('Ho Chi Minh City')}, {nvarchar('+84-900-111-222')}, NULL, NULL, {nvarchar('ADMIN')}, 1, 1, GETDATE());"
            ),
            (
                "INSERT INTO [user] (id, email, username, password_hash, user_demographic_id, date_of_birth, location, phone_number, oauth_provider, oauth_provider_id, role, is_active, is_verified, last_login_at) VALUES "
                f"({quote_guid(learner_user_id)}, {nvarchar('learner@medicalogy.io')}, {nvarchar('learner')}, {nvarchar('hashed_learner_password')}, {quote_guid(demographic_young_id)}, '2001-11-08', {nvarchar('Da Nang')}, {nvarchar('+84-933-456-789')}, {nvarchar('google')}, {nvarchar('google-learner-001')}, {nvarchar('USER')}, 1, 1, GETDATE());"
            ),
            (
                "INSERT INTO refresh_token (id, user_id, token_hash, expires_at, revoked) VALUES "
                f"({quote_guid(stable_uuid('refresh:learner'))}, {quote_guid(learner_user_id)}, {nvarchar('hash_refresh_learner_001')}, DATEADD(DAY, 30, GETDATE()), 0);"
            ),
            (
                "INSERT INTO user_setting (user_id, daily_reminder_time, theme_preference, daily_goal_courses) VALUES "
                f"({quote_guid(admin_user_id)}, '08:00:00', {nvarchar('light')}, 2);"
            ),
            (
                "INSERT INTO user_setting (user_id, daily_reminder_time, theme_preference, daily_goal_courses) VALUES "
                f"({quote_guid(learner_user_id)}, '19:30:00', {nvarchar('dark')}, 3);"
            ),
            (
                "INSERT INTO user_profile (user_id, display_name, avatar_url, bio, occupation, medical_background) VALUES "
                f"({quote_guid(admin_user_id)}, {nvarchar('Medicalogy Admin')}, {nvarchar('admin-avatar.png')}, {nvarchar('Platform administrator for content quality')}, {nvarchar('Administrator')}, 1);"
            ),
            (
                "INSERT INTO user_profile (user_id, display_name, avatar_url, bio, occupation, medical_background) VALUES "
                f"({quote_guid(learner_user_id)}, {nvarchar('Alex Learner')}, {nvarchar('learner-avatar.png')}, {nvarchar('Focused on emergency and clinical foundations')}, {nvarchar('Medical Student')}, 1);"
            ),
            "",
        ]
    )

    for theme_index, theme in enumerate(layout["themes"], start=1):
        theme_id = stable_uuid(f"theme:{theme['slug']}")
        theme_count += 1

        sql_lines.append(
            "INSERT INTO theme (id, name, slug, description, icon_file_name, color_code, order_index) VALUES "
            f"({quote_guid(theme_id)}, {nvarchar(theme['name'])}, {nvarchar(theme['slug'])}, "
            f"{nvarchar(theme['description'])}, {nvarchar(theme['icon_file_name'])}, {nvarchar(theme['color_code'])}, {theme_index});"
        )
        theme_rows.append({"id": theme_id, "name": theme["name"], "slug": theme["slug"]})

        theme_out: dict[str, Any] = {
            "id": theme_id,
            "name": theme["name"],
            "slug": theme["slug"],
            "description": theme["description"],
            "orderIndex": theme_index,
            "sections": [],
        }

        for section_index, section in enumerate(theme["sections"], start=1):
            section_id = stable_uuid(f"section:{theme['slug']}:{section['slug']}")
            section_count += 1

            sql_lines.append(
                "INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES "
                f"({quote_guid(section_id)}, {quote_guid(theme_id)}, {nvarchar(section['name'])}, "
                f"{nvarchar(section['slug'])}, {section_index}, {section['estimated_duration_minutes']});"
            )
            section_rows.append(
                {
                    "id": section_id,
                    "theme_id": theme_id,
                    "name": section["name"],
                    "slug": section["slug"],
                }
            )

            article_markdown, is_full_article = build_article_markdown(theme, section, media_files)
            article_file_name = f"{section['infographic']['slug']}.md"
            article_file = ARTICLE_CONTENT_DIR / article_file_name
            write_text(article_file, article_markdown)

            article_id = stable_uuid(f"article:{section['infographic']['slug']}")
            article_count += 1
            if is_full_article:
                full_fledged_article_count += 1

            article_content_ref = article_file_name if GENERATION_PROFILE["store_content_as_filename"] else article_markdown
            sql_lines.append(
                "INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES "
                f"({quote_guid(article_id)}, {quote_guid(theme_id)}, {nvarchar(section['infographic']['title'])}, "
                f"{nvarchar(section['infographic']['slug'])}, {nvarchar(article_content_ref)}, {quote_guid(admin_user_id)}, 1, GETDATE());"
            )
            article_rows.append(
                {
                    "id": article_id,
                    "theme_id": theme_id,
                    "theme_slug": theme["slug"],
                    "name": section["infographic"]["title"],
                    "slug": section["infographic"]["slug"],
                }
            )

            section_out: dict[str, Any] = {
                "id": section_id,
                "name": section["name"],
                "slug": section["slug"],
                "orderIndex": section_index,
                "estimatedDurationMinutes": section["estimated_duration_minutes"],
                "infographic": {
                    "id": article_id,
                    "title": section["infographic"]["title"],
                    "slug": section["infographic"]["slug"],
                    "contentFile": article_file_name,
                    "contentDepth": "full-fledged" if is_full_article else "standard",
                },
                "courses": [],
            }

            for course_index, course in enumerate(section["courses"], start=1):
                course_id = stable_uuid(f"course:{section['slug']}:{course['slug']}")
                course_count += 1

                course_content, is_full_course = build_course_content(
                    theme["name"],
                    section["slug"],
                    section["name"],
                    course,
                    media_files,
                )
                if is_full_course:
                    full_fledged_course_count += 1

                course_file_name = f"{course['slug']}.json"
                course_file = COURSE_CONTENT_DIR / course_file_name
                write_json(course_file, course_content)

                course_content_ref = course_file_name if GENERATION_PROFILE["store_content_as_filename"] else json.dumps(course_content, ensure_ascii=False)
                sql_lines.append(
                    "INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES "
                    f"({quote_guid(course_id)}, {quote_guid(section_id)}, {nvarchar(course['name'])}, {nvarchar(course['description'])}, "
                    f"{nvarchar(course['slug'])}, {course_index}, {course['estimated_duration_minutes']}, {nvarchar(course['difficulty_level'])}, 1, {nvarchar(course_content_ref)});"
                )
                course_rows.append(
                    {
                        "id": course_id,
                        "section_id": section_id,
                        "name": course["name"],
                        "slug": course["slug"],
                    }
                )

                section_out["courses"].append(
                    {
                        "id": course_id,
                        "name": course["name"],
                        "slug": course["slug"],
                        "description": course["description"],
                        "difficultyLevel": course["difficulty_level"],
                        "orderIndex": course_index,
                        "estimatedDurationMinutes": course["estimated_duration_minutes"],
                        "contentFile": course_file_name,
                        "contentDepth": "full-fledged" if is_full_course else "standard",
                    }
                )

            theme_out["sections"].append(section_out)

        final_data["themes"].append(theme_out)
        sql_lines.append("")

    # ------------------------------------------------------------------------
    # LEARNING PROGRESS TABLES
    # ------------------------------------------------------------------------
    sql_lines.extend(
        [
            "-- LEARNING PROGRESS INSERTS",
            (
                "INSERT INTO user_theme_enrollment (user_id, theme_id, status, enrolled_at, finished_at) VALUES "
                f"({quote_guid(learner_user_id)}, {quote_guid(theme_rows[0]['id'])}, {nvarchar('finished')}, DATEADD(DAY, -30, GETDATE()), DATEADD(DAY, -1, GETDATE()));"
            ),
        ]
    )

    if len(theme_rows) > 1:
        sql_lines.append(
            (
                "INSERT INTO user_theme_enrollment (user_id, theme_id, status, enrolled_at, finished_at) VALUES "
                f"({quote_guid(learner_user_id)}, {quote_guid(theme_rows[1]['id'])}, {nvarchar('enrolled')}, DATEADD(DAY, -7, GETDATE()), NULL);"
            )
        )

    for idx, row in enumerate(course_rows[:6], start=1):
        sql_lines.append(
            (
                "INSERT INTO user_course (user_id, course_id, quizzes_correct, completed_at) VALUES "
                f"({quote_guid(learner_user_id)}, {quote_guid(row['id'])}, {3 + (idx % 3)}, DATEADD(DAY, -{idx}, GETDATE()));"
            )
        )

    sql_lines.extend(
        [
            (
                "INSERT INTO user_daily_streak (user_id, current_streak, longest_streak, last_activity_date, streak_started_at, total_active_days) VALUES "
                f"({quote_guid(learner_user_id)}, 12, 20, CAST(GETDATE() AS DATE), DATEADD(DAY, -12, CAST(GETDATE() AS DATE)), 45);"
            ),
            "",
        ]
    )

    # ------------------------------------------------------------------------
    # ASSESSMENT TABLES
    # ------------------------------------------------------------------------
    sql_lines.append("-- ASSESSMENT INSERTS")
    for section in section_rows:
        test_name = f"{section['name']} Final Assessment"
        test_content = build_section_test_content(section["name"])
        sql_lines.append(
            (
                "INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES "
                f"({quote_guid(section['id'])}, {nvarchar(test_name)}, 70.00, 30, 3, 1, {nvarchar(test_content)});"
            )
        )

    initial_assessment_id = stable_uuid("initial_assessment:v1")
    initial_assessment_content = build_initial_assessment_content()
    sql_lines.append(
        (
            "INSERT INTO initial_assessment (id, name, version, is_active, content) VALUES "
            f"({quote_guid(initial_assessment_id)}, {nvarchar('Learner Placement Assessment')}, 1, 1, {nvarchar(initial_assessment_content)});"
        )
    )

    for idx, section in enumerate(section_rows[:3], start=1):
        sql_lines.append(
            (
                "INSERT INTO user_section_test (user_id, section_test_id, quizzes_correct, total_questions, passed, completed_at) VALUES "
                f"({quote_guid(learner_user_id)}, {quote_guid(section['id'])}, {6 + idx}, 10, 1, DATEADD(DAY, -{idx}, GETDATE()));"
            )
        )

    sql_lines.extend(
        [
            (
                "INSERT INTO user_initial_assessment (user_id, initial_assessment_id, quizzes_correct, total_questions, completed_at) VALUES "
                f"({quote_guid(learner_user_id)}, {quote_guid(initial_assessment_id)}, 7, 10, DATEADD(DAY, -60, GETDATE()));"
            ),
            "",
        ]
    )

    # ------------------------------------------------------------------------
    # DICTIONARY SOCIAL TABLES
    # ------------------------------------------------------------------------
    sql_lines.append("-- DICTIONARY TAG/SOCIAL INSERTS")
    tag_defs = [
        ("tag:emergency", "emergency"),
        ("tag:mental-health", "mental-health"),
        ("tag:nutrition", "nutrition"),
        ("tag:infection", "infection"),
        ("tag:maternal-child", "maternal-child"),
    ]
    tag_rows: list[dict[str, str]] = []
    for key, name in tag_defs:
        tag_id = stable_uuid(key)
        tag_rows.append({"id": tag_id, "name": name})
        sql_lines.append(
            f"INSERT INTO tag (id, name) VALUES ({quote_guid(tag_id)}, {nvarchar(name)});"
        )

    tag_by_name = {row["name"]: row for row in tag_rows}
    for article in article_rows:
        theme_tag = theme_tag_name(article["theme_slug"])
        tag = tag_by_name[theme_tag]
        sql_lines.append(
            (
                "INSERT INTO article_tag (article_id, tag_id) VALUES "
                f"({quote_guid(article['id'])}, {quote_guid(tag['id'])});"
            )
        )

    if len(article_rows) >= 2:
        sql_lines.append(
            (
                "INSERT INTO article_related (article_id, related_article_id) VALUES "
                f"({quote_guid(article_rows[0]['id'])}, {quote_guid(article_rows[1]['id'])});"
            )
        )
        sql_lines.append(
            (
                "INSERT INTO article_related (article_id, related_article_id) VALUES "
                f"({quote_guid(article_rows[1]['id'])}, {quote_guid(article_rows[0]['id'])});"
            )
        )

    for idx, article in enumerate(article_rows[:8], start=1):
        sql_lines.append(
            (
                "INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES "
                f"({quote_guid(learner_user_id)}, {quote_guid(article['id'])}, {1 + (idx % 4)}, DATEADD(DAY, -{idx + 15}, GETDATE()), DATEADD(DAY, -{idx}, GETDATE()));"
            )
        )

    parent_comment_id = stable_uuid("comment:parent")
    reply_comment_id = stable_uuid("comment:reply")
    target_article_id = article_rows[0]["id"]
    sql_lines.extend(
        [
            (
                "INSERT INTO user_article_comment (id, user_id, article_id, parent_comment_id, comment_text, is_approved) VALUES "
                f"({quote_guid(parent_comment_id)}, {quote_guid(learner_user_id)}, {quote_guid(target_article_id)}, NULL, {nvarchar('This article is detailed and practical.')}, 1);"
            ),
            (
                "INSERT INTO user_article_comment (id, user_id, article_id, parent_comment_id, comment_text, is_approved) VALUES "
                f"({quote_guid(reply_comment_id)}, {quote_guid(admin_user_id)}, {quote_guid(target_article_id)}, {quote_guid(parent_comment_id)}, {nvarchar('Thanks for the feedback. More updates are coming.')}, 1);"
            ),
            (
                "INSERT INTO user_comment_vote (user_id, comment_id, vote_type) VALUES "
                f"({quote_guid(admin_user_id)}, {quote_guid(parent_comment_id)}, {nvarchar('like')});"
            ),
        ]
    )

    for article in article_rows[:5]:
        bookmark_id = stable_uuid(f"bookmark:{learner_user_id}:{article['id']}")
        sql_lines.append(
            (
                "INSERT INTO user_bookmark (id, user_id, article_id) VALUES "
                f"({quote_guid(bookmark_id)}, {quote_guid(learner_user_id)}, {quote_guid(article['id'])});"
            )
        )
    sql_lines.append("")

    # ------------------------------------------------------------------------
    # NOTIFICATION TABLES
    # ------------------------------------------------------------------------
    sql_lines.append("-- NOTIFICATION INSERTS")
    notif_types = [
        "streak_reminder",
        "course_recommendation",
        "test_result",
        "comment_reply",
        "system_log",
        "security",
        "achievement",
        "content_update",
    ]

    for notif_type in notif_types:
        sql_lines.append(
            (
                "INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES "
                f"({quote_guid(learner_user_id)}, {nvarchar(notif_type)}, 1, 1, 1);"
            )
        )

    notif_seed_rows = [
        ("streak_reminder", None, None, "Keep your streak alive!", "You are one activity away from extending your streak."),
        ("course_recommendation", "course", course_rows[0]["id"], "Recommended next course", f"Try {course_rows[0]['name']} next."),
        ("test_result", "section_test", section_rows[0]["id"], "Assessment result", f"You passed {section_rows[0]['name']} Final Assessment."),
        ("comment_reply", "comment", parent_comment_id, "New reply", "Your comment received a reply from an admin."),
        ("system_log", None, None, "System maintenance", "Platform maintenance completed successfully."),
        ("security", None, None, "Security alert", "A new login was detected on your account."),
        ("achievement", "course", course_rows[1]["id"], "Achievement unlocked", "You completed 5 courses this week."),
        ("content_update", "article", article_rows[0]["id"], "Article updated", f"{article_rows[0]['name']} has been updated."),
    ]

    for idx, (ntype, rtype, rid, title, content_text) in enumerate(notif_seed_rows, start=1):
        notif_id = stable_uuid(f"notification:{idx}:{ntype}")
        rid_sql = quote_guid(rid) if rid else "NULL"
        rtype_sql = nvarchar(rtype) if rtype else "NULL"
        is_read = 1 if idx % 3 == 0 else 0
        read_at_sql = "DATEADD(HOUR, -1, GETDATE())" if is_read else "NULL"
        sql_lines.append(
            (
                "INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES "
                f"({quote_guid(notif_id)}, {quote_guid(learner_user_id)}, {nvarchar(ntype)}, {rtype_sql}, {rid_sql}, {is_read}, {read_at_sql}, DATEADD(HOUR, -{idx}, GETDATE()), DATEADD(HOUR, -{idx}, GETDATE()));"
            )
        )

    sql_lines.append("")

    insert_sql = "\n".join(sql_lines).strip()
    full_pipeline_sql = build_schema_reset_block() + "\n\n-- ============================================================================\n-- FULL DATA INSERTS\n-- ============================================================================\n" + insert_sql + "\n"

    write_json(FINAL_DATA_FILE, final_data)
    write_json(
        MANIFEST_FILE,
        {
            "themeCount": theme_count,
            "sectionCount": section_count,
            "courseCount": course_count,
            "articleCount": article_count,
            "fullFledgedArticleCount": full_fledged_article_count,
            "fullFledgedCourseCount": full_fledged_course_count,
            "fullFledgedArticleSlugs": sorted(FULL_FLEDGED_ARTICLE_SLUGS),
            "fullFledgedCourseSlugs": sorted(FULL_FLEDGED_COURSE_SLUGS),
            "contentFolders": {
                "articles": str(ARTICLE_CONTENT_DIR.relative_to(SCRIPT_DIR)).replace("\\", "/"),
                "courses": str(COURSE_CONTENT_DIR.relative_to(SCRIPT_DIR)).replace("\\", "/"),
                "media": str(MEDIA_DATASET_DIR.relative_to(SCRIPT_DIR)).replace("\\", "/"),
            },
            "finalDataFile": str(FINAL_DATA_FILE.relative_to(SCRIPT_DIR)).replace("\\", "/"),
            "sqlFile": str(PIPELINE_SQL_FILE.relative_to(SCRIPT_DIR)).replace("\\", "/"),
        },
    )
    write_text(PIPELINE_SQL_FILE, full_pipeline_sql)

    return {
        "themeCount": theme_count,
        "sectionCount": section_count,
        "courseCount": course_count,
        "articleCount": article_count,
        "fullFledgedArticleCount": full_fledged_article_count,
        "fullFledgedCourseCount": full_fledged_course_count,
        "seededTableCount": 25,
    }


def main() -> None:
    print("=== Full-fledged debug targets ===")
    print(f"Articles: {sorted(FULL_FLEDGED_ARTICLE_SLUGS)}")
    print(f"Courses:  {sorted(FULL_FLEDGED_COURSE_SLUGS)}")
    print("==================================")

    layout = read_layout()
    validate_layout(layout)
    media_files = get_media_files()
    summary = generate_data(layout, media_files)

    print("Mockup data generation completed.")
    print(f"Themes:   {summary['themeCount']}")
    print(f"Sections: {summary['sectionCount']}")
    print(f"Courses:  {summary['courseCount']}")
    print(f"Articles: {summary['articleCount']}")
    print(f"Full-fledged articles: {summary['fullFledgedArticleCount']}")
    print(f"Full-fledged courses:  {summary['fullFledgedCourseCount']}")
    print(f"Seeded tables: {summary['seededTableCount']}")
    print(f"Output JSON root: {FINAL_DATA_FILE}")
    print(f"Output SQL file:  {PIPELINE_SQL_FILE}")


if __name__ == "__main__":
    main()
