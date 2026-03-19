-- ============================================================================
-- BioBasics Database Schema - v5
-- Database: medicalogy
-- SQL Server Implementation
-- ============================================================================
--
-- MICROSERVICES (5 services + API Gateway):
--   1. Auth Service        (port 8081)
--   2. Learning Service    (port 8082)
--   3. Assessment Service  (port 8083)
--   4. Dictionary Service  (port 8084)  ← owns article/encyclopedia tables
--   5. Notification Service
--   API Gateway            (port 8080)  ← no DB
--
-- CHANGES FROM v4:
--   [user]
--     - password_hash: NOT NULL → NULL (OAuth users have no password)
--     - user_demographic_id: NOT NULL → NULL (OAuth JIT provisioning)
--     - ADD oauth_provider NVARCHAR(50)       ('google', 'facebook', NULL = local)
--     - ADD oauth_provider_id NVARCHAR(255)   (provider's own user ID)
--     - ADD role NVARCHAR(10) DEFAULT 'USER'  (USER | ADMIN — stamped into JWT)
--     - ADD UNIQUE constraint on (oauth_provider, oauth_provider_id)
--   NEW: refresh_token table
--   NEW: user_theme_enrollment table
--   user_setting: removed coarse notification bits → user_notification_preference
--
-- CHANGES FROM v5 (this version):
--   [user_initial_assessment]
--     - REMOVED quizzes_correct  (aggregate score replaced by per-theme table)
--     - REMOVED total_questions  (aggregate score replaced by per-theme table)
--   [user_profile]
--     - REMOVED medical_background  (redundant — initial_user_section_proficiency captures this)
--   NEW: initial_user_section_proficiency
--     - Per-theme breakdown of placement test results
--     - FK to initial_assessment; cross-service refs to user + theme
--     - Stores questions_seen, questions_correct, knowledge_level per theme
--     - knowledge_level derived by app at scoring time (beginner/intermediate/advanced)
--     - Requires each question in initial_assessment.content to carry a themeId
-- ============================================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'medicalogy')
BEGIN
    CREATE DATABASE medicalogy;
END
GO

USE medicalogy;
GO

-- ============================================================================
-- SERVICE 1: AUTH SERVICE
-- Tables: user_demographic, [user], refresh_token, user_setting, user_profile
-- ============================================================================

CREATE TABLE user_demographic (
    id          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name        NVARCHAR(100) NOT NULL,
    description NVARCHAR(500),
    min_age     INT,
    max_age     INT,
    created_at  DATETIME2 DEFAULT GETDATE(),
    updated_at  DATETIME2 DEFAULT GETDATE()
);

-- password_hash is NULL for OAuth-only accounts
-- user_demographic_id is NULL until user completes onboarding
-- role is stamped into the JWT by Auth Service
CREATE TABLE [user] (
    id                  UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    email               NVARCHAR(255) NOT NULL UNIQUE,
    username            NVARCHAR(100) NOT NULL UNIQUE,
    password_hash       NVARCHAR(255) NULL,                     -- NULL for OAuth users
    user_demographic_id UNIQUEIDENTIFIER NULL,                  -- NULL until onboarding complete
    date_of_birth       DATE,
    location            NVARCHAR(200),
    phone_number        NVARCHAR(30),
    oauth_provider      NVARCHAR(50) NULL,                      -- 'google', 'facebook', NULL = local
    oauth_provider_id   NVARCHAR(255) NULL,                     -- provider's own user ID
    role                NVARCHAR(10) NOT NULL DEFAULT 'USER',    -- USER | ADMIN
    is_active           BIT DEFAULT 1,
    is_verified         BIT DEFAULT 0,
    last_login_at       DATETIME2,
    created_at          DATETIME2 DEFAULT GETDATE(),
    updated_at          DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_demographic_id) REFERENCES user_demographic(id),
    CONSTRAINT chk_role CHECK (role IN ('USER', 'ADMIN')),
    CONSTRAINT uq_oauth_provider UNIQUE (oauth_provider, oauth_provider_id)
);

-- Auth Service stores and manages refresh tokens explicitly
-- Revocation done by deleting or setting revoked = 1
CREATE TABLE refresh_token (
    id         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id    UNIQUEIDENTIFIER NOT NULL,
    token_hash NVARCHAR(512) NOT NULL UNIQUE,  -- never store plain token
    expires_at DATETIME2 NOT NULL,
    revoked    BIT DEFAULT 0,
    revoked_at DATETIME2,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE
);

-- notification channel toggles removed — now in user_notification_preference
CREATE TABLE user_setting (
    user_id             UNIQUEIDENTIFIER PRIMARY KEY,
    daily_reminder_time TIME,
    theme_preference    NVARCHAR(20) DEFAULT 'light',
    daily_goal_courses  INT DEFAULT 1,
    created_at          DATETIME2 DEFAULT GETDATE(),
    updated_at          DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE,
    CONSTRAINT chk_theme_preference CHECK (theme_preference IN ('light', 'dark', 'auto'))
);

-- medical_background removed: captured with more granularity by initial_user_section_proficiency
CREATE TABLE user_profile (
    user_id      UNIQUEIDENTIFIER PRIMARY KEY,
    display_name NVARCHAR(200),
    avatar_url   NVARCHAR(500),
    bio          NVARCHAR(1000),
    occupation   NVARCHAR(200),
    created_at   DATETIME2 DEFAULT GETDATE(),
    updated_at   DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE
);

-- ============================================================================
-- SERVICE 2: LEARNING SERVICE
-- Tables: theme, section, course, user_theme_enrollment, user_course,
--         user_daily_streak
-- ============================================================================

-- Level 1
CREATE TABLE theme (
    id             UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name           NVARCHAR(200) NOT NULL,
    slug           NVARCHAR(300) NOT NULL UNIQUE,
    description    NVARCHAR(1000),
    icon_file_name NVARCHAR(255),
    color_code     NVARCHAR(20),
    order_index    INT NOT NULL,
    created_at     DATETIME2 DEFAULT GETDATE(),
    updated_at     DATETIME2 DEFAULT GETDATE()
);

-- Level 2
CREATE TABLE section (
    id                         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    theme_id                   UNIQUEIDENTIFIER NOT NULL,
    name                       NVARCHAR(200) NOT NULL,
    slug                       NVARCHAR(300) NOT NULL,
    order_index                INT NOT NULL,
    estimated_duration_minutes INT,
    created_at                 DATETIME2 DEFAULT GETDATE(),
    updated_at                 DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (theme_id) REFERENCES theme(id)
);

-- Level 3: called "lesson" in the SDD — course is the authoritative name here
-- Content strategy: database stores filename references only (not raw JSON payload)
-- Actual course files are loaded from mockup content storage
CREATE TABLE course (
    id                         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    section_id                 UNIQUEIDENTIFIER NOT NULL,
    name                       NVARCHAR(200) NOT NULL,
    description                NVARCHAR(1000),
    slug                       NVARCHAR(300) NOT NULL,
    order_index                INT NOT NULL,
    estimated_duration_minutes INT DEFAULT 7,
    difficulty_level           NVARCHAR(20) DEFAULT 'beginner',
    is_active                  BIT DEFAULT 1,
    content_file_name          NVARCHAR(255) NOT NULL,
    created_at                 DATETIME2 DEFAULT GETDATE(),
    updated_at                 DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (section_id) REFERENCES section(id),
    CONSTRAINT chk_difficulty_level CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    CONSTRAINT chk_course_content_file_name CHECK (RIGHT(content_file_name, 5) = '.json')
);

-- No row = not enrolled. status 'enrolled' = active. status 'finished' = all sections done.
CREATE TABLE user_theme_enrollment (
    user_id     UNIQUEIDENTIFIER NOT NULL,
    theme_id    UNIQUEIDENTIFIER NOT NULL,
    status      NVARCHAR(20) NOT NULL DEFAULT 'enrolled',  -- enrolled | finished
    enrolled_at DATETIME2 DEFAULT GETDATE(),
    finished_at DATETIME2,                                 -- NULL until status = 'finished'
    PRIMARY KEY (user_id, theme_id),
    FOREIGN KEY (theme_id) REFERENCES theme(id),
    -- No FK on user_id: cross-service reference
    CONSTRAINT chk_theme_enrollment_status CHECK (status IN ('enrolled', 'finished'))
);

-- Existence of a row = completed. No row = not started.
CREATE TABLE user_course (
    user_id         UNIQUEIDENTIFIER NOT NULL,
    course_id       UNIQUEIDENTIFIER NOT NULL,
    quizzes_correct INT DEFAULT 0,
    completed_at    DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, course_id),
    FOREIGN KEY (course_id) REFERENCES course(id)
    -- No FK on user_id: cross-service reference
);

-- Valid activity that increments streak: completing a course or a section test
CREATE TABLE user_daily_streak (
    user_id            UNIQUEIDENTIFIER PRIMARY KEY,
    current_streak     INT DEFAULT 0,
    longest_streak     INT DEFAULT 0,
    last_activity_date DATE,
    streak_started_at  DATE,
    total_active_days  INT DEFAULT 0,
    created_at         DATETIME2 DEFAULT GETDATE(),
    updated_at         DATETIME2 DEFAULT GETDATE()
    -- No FK on user_id: cross-service reference
);

-- ============================================================================
-- SERVICE 3: ASSESSMENT SERVICE
-- Tables: section_test, initial_assessment, user_section_test,
--         user_initial_assessment
-- ============================================================================

-- Comprehensive test at the end of a section
-- Questions stored as structured JSON — see CONTENT_STRUCTURE.md
CREATE TABLE section_test (
    section_id               UNIQUEIDENTIFIER PRIMARY KEY,
    name                     NVARCHAR(200) NOT NULL,
    passing_score_percentage DECIMAL(5,2) DEFAULT 70.00,
    time_limit_minutes       INT DEFAULT 30,
    max_attempts             INT,
    is_active                BIT DEFAULT 1,
    content                  NVARCHAR(MAX) NOT NULL,
    created_at               DATETIME2 DEFAULT GETDATE(),
    updated_at               DATETIME2 DEFAULT GETDATE(),
    -- No FK on section_id: cross-service reference to Learning Service (section table)
    CONSTRAINT chk_section_test_content_is_json CHECK (ISJSON(content) = 1)
);

-- Placement test taken at the start to personalise the learning path
-- Questions stored as structured JSON — see INITIAL_ASSESSMENT_STRUCTURE.md
CREATE TABLE initial_assessment (
    id         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name       NVARCHAR(200) NOT NULL,
    version    INT DEFAULT 1,
    is_active  BIT DEFAULT 1,
    content    NVARCHAR(MAX) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT chk_initial_assessment_content_is_json CHECK (ISJSON(content) = 1)
);

-- Existence of a row = test has been taken
CREATE TABLE user_section_test (
    user_id         UNIQUEIDENTIFIER NOT NULL,
    section_test_id UNIQUEIDENTIFIER NOT NULL,
    quizzes_correct INT DEFAULT 0,
    total_questions INT NOT NULL,
    passed          BIT DEFAULT 0,
    completed_at    DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, section_test_id),
    FOREIGN KEY (section_test_id) REFERENCES section_test(section_id)
    -- No FK on user_id: cross-service reference
);

-- Existence of a row = placement test has been taken.
-- No aggregate score stored here — per-section breakdown lives in
-- initial_user_section_proficiency. completed_at is the onboarding timestamp.
CREATE TABLE user_initial_assessment (
    user_id               UNIQUEIDENTIFIER NOT NULL,
    initial_assessment_id UNIQUEIDENTIFIER NOT NULL,
    completed_at          DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, initial_assessment_id),
    FOREIGN KEY (initial_assessment_id) REFERENCES initial_assessment(id)
    -- No FK on user_id: cross-service reference
);

-- Per-section score from the placement test.
-- One row per (user, assessment, section).
-- Used ONLY for UI display on the roadmap. No writes to user_course ever.
-- Roadmap reads this:
--   questions_correct / questions_seen >= 0.80
--   → section shown with "You already know this section" indicator. Courses still locked.
--   questions_correct / questions_seen < 0.80 OR no row
--   → normal locked flow, no UI change.
-- Each question in initial_assessment.content must carry a sectionSlug so the
--   app can bucket answers into these rows when scoring.
CREATE TABLE initial_user_section_proficiency (
    user_id               UNIQUEIDENTIFIER NOT NULL,
    initial_assessment_id UNIQUEIDENTIFIER NOT NULL,
    section_id            UNIQUEIDENTIFIER NOT NULL,
    questions_seen        INT NOT NULL,
    questions_correct     INT NOT NULL DEFAULT 0,
    assessed_at           DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, initial_assessment_id, section_id),
    FOREIGN KEY (initial_assessment_id) REFERENCES initial_assessment(id),
    -- No FK on user_id:   cross-service reference to Auth Service
    -- No FK on section_id: cross-service reference to Learning Service
    CONSTRAINT chk_section_proficiency_questions_correct
        CHECK (questions_correct >= 0 AND questions_correct <= questions_seen)
);

-- ============================================================================
-- SERVICE 4: DICTIONARY SERVICE
-- Tables: tag, article, article_tag, article_related, user_article_view,
--         user_article_comment, user_comment_vote, user_bookmark
-- Note: "Dictionary Service" in the SDD is the medical encyclopedia —
--       these article tables are what it owns.
-- ============================================================================

CREATE TABLE tag (
    id         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name       NVARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE article (
    id               UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    theme_id         UNIQUEIDENTIFIER NOT NULL,
    name             NVARCHAR(300) NOT NULL,
    slug             NVARCHAR(300) NOT NULL UNIQUE,
    content_markdown NVARCHAR(255) NOT NULL,
    author_admin_id  UNIQUEIDENTIFIER,           -- cross-service ref to [user].id
    is_published     BIT DEFAULT 0,
    published_at     DATETIME2,
    created_at       DATETIME2 DEFAULT GETDATE(),
    updated_at       DATETIME2 DEFAULT GETDATE(),
    CONSTRAINT chk_article_content_file_name CHECK (RIGHT(content_markdown, 3) = '.md')
    -- No FK on theme_id: cross-service reference to Learning Service (theme table)
    -- No FK on author_admin_id: cross-service reference to Auth Service ([user] table)
);

CREATE TABLE article_tag (
    article_id UNIQUEIDENTIFIER NOT NULL,
    tag_id     UNIQUEIDENTIFIER NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
);

-- Bidirectional related articles
CREATE TABLE article_related (
    article_id         UNIQUEIDENTIFIER NOT NULL,
    related_article_id UNIQUEIDENTIFIER NOT NULL,
    created_at         DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (article_id, related_article_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (related_article_id) REFERENCES article(id),
    CONSTRAINT chk_no_self_relation CHECK (article_id != related_article_id)
);

CREATE TABLE user_article_view (
    user_id         UNIQUEIDENTIFIER NOT NULL,
    article_id      UNIQUEIDENTIFIER NOT NULL,
    view_count      INT DEFAULT 1,
    first_viewed_at DATETIME2 DEFAULT GETDATE(),
    last_viewed_at  DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, article_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE
    -- No FK on user_id: cross-service reference
);

-- Admin must approve before visible. parent_comment_id NULL = top-level, otherwise = reply.
CREATE TABLE user_article_comment (
    id                UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id           UNIQUEIDENTIFIER NOT NULL,
    article_id        UNIQUEIDENTIFIER NOT NULL,
    parent_comment_id UNIQUEIDENTIFIER NULL,
    comment_text      NVARCHAR(MAX) NOT NULL,
    is_approved       BIT DEFAULT 0,
    created_at        DATETIME2 DEFAULT GETDATE(),
    updated_at        DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES user_article_comment(id)
    -- No FK on user_id: cross-service reference
);

CREATE TABLE user_comment_vote (
    user_id    UNIQUEIDENTIFIER NOT NULL,
    comment_id UNIQUEIDENTIFIER NOT NULL,
    vote_type  NVARCHAR(10) NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, comment_id),
    FOREIGN KEY (comment_id) REFERENCES user_article_comment(id) ON DELETE CASCADE,
    -- No FK on user_id: cross-service reference
    CONSTRAINT chk_vote_type CHECK (vote_type IN ('like', 'dislike'))
);

CREATE TABLE user_bookmark (
    id         UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id    UNIQUEIDENTIFIER NOT NULL,
    article_id UNIQUEIDENTIFIER NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    -- No FK on user_id: cross-service reference
    CONSTRAINT uq_user_bookmark UNIQUE (user_id, article_id)
);

-- ============================================================================
-- SERVICE 5: NOTIFICATION SERVICE
-- Tables: notification, user_notification_preference
--
-- Notification types and what they reference:
-- ─────────────────────────────────────────────────────────────────────────────
-- streak_reminder       reference_type NULL            reference_id NULL
--                       → pull current_streak from user_daily_streak live
--
-- course_recommendation reference_type 'course'        reference_id = course.id
--                       → render course.name
--
-- test_result           reference_type 'section_test'  reference_id = section_test.section_id
--                       → render section.name + user_section_test.passed
--
-- comment_reply         reference_type 'comment'       reference_id = parent comment.id
--                       → follow comment → article to render article.name
--
-- system_log            reference_type NULL             reference_id NULL
--                       → fixed copy (maintenance, downtime, etc.)
--
-- security              reference_type NULL             reference_id NULL
--                       → fixed copy; event fired by Auth Service
--                         (new login, password changed, email changed)
--
-- achievement           reference_type 'course'         reference_id = course.id
--                    OR reference_type 'section_test'   reference_id = section_test.section_id
--                       → fixed copy + entity name (streak milestone, section/theme complete)
--
-- content_update        reference_type 'article'        reference_id = article.id
--                    OR reference_type 'course'          reference_id = course.id
--                       → render entity.name for content the user has engaged with
-- ─────────────────────────────────────────────────────────────────────────────
-- ============================================================================

CREATE TABLE notification (
    id                UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id           UNIQUEIDENTIFIER NOT NULL,
    notification_type NVARCHAR(50) NOT NULL,
    reference_type    NVARCHAR(50),
    reference_id      UNIQUEIDENTIFIER,
    is_read           BIT DEFAULT 0,
    read_at           DATETIME2,
    sent_at           DATETIME2 DEFAULT GETDATE(),
    created_at        DATETIME2 DEFAULT GETDATE(),
    -- No FK on user_id: cross-service reference
    CONSTRAINT chk_notification_type CHECK (notification_type IN (
        'streak_reminder',
        'course_recommendation',
        'test_result',
        'comment_reply',
        'system_log',
        'security',
        'achievement',
        'content_update'
    )),
    CONSTRAINT chk_reference_type CHECK (
        reference_type IN ('course', 'section_test', 'comment', 'article')
        OR reference_type IS NULL
    )
);

CREATE TABLE user_notification_preference (
    user_id           UNIQUEIDENTIFIER NOT NULL,
    notification_type NVARCHAR(50) NOT NULL,
    in_app_enabled    BIT DEFAULT 1,
    email_enabled     BIT DEFAULT 1,
    push_enabled      BIT DEFAULT 1,
    PRIMARY KEY (user_id, notification_type),
    -- No FK on user_id: cross-service reference
    CONSTRAINT chk_pref_notification_type CHECK (notification_type IN (
        'streak_reminder',
        'course_recommendation',
        'test_result',
        'comment_reply',
        'system_log',
        'security',
        'achievement',
        'content_update'
    ))
);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

PRINT 'BioBasics database schema v5 created successfully!';
PRINT 'Total tables created: 26';
PRINT 'Note: JSON content structures documented in:';
PRINT '  - CONTENT_STRUCTURE.md';
PRINT '  - INITIAL_ASSESSMENT_STRUCTURE.md';
GO