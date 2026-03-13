-- ============================================================================
-- FULL RESET + RECREATE
-- ============================================================================
USE master;
GO
IF DB_ID('medicalogy') IS NOT NULL
BEGIN
    ALTER DATABASE medicalogy SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE medicalogy;
END
GO

-- ============================================================================
-- SCHEMA CREATION
-- ============================================================================
-- ============================================================================
-- BioBasics Database Schema - v4
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

CREATE TABLE user_profile (
    user_id            UNIQUEIDENTIFIER PRIMARY KEY,
    display_name       NVARCHAR(200),
    avatar_url         NVARCHAR(500),
    bio                NVARCHAR(1000),
    occupation         NVARCHAR(200),
    medical_background BIT DEFAULT 0,
    created_at         DATETIME2 DEFAULT GETDATE(),
    updated_at         DATETIME2 DEFAULT GETDATE(),
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

-- Existence of a row = placement test has been taken
CREATE TABLE user_initial_assessment (
    user_id               UNIQUEIDENTIFIER NOT NULL,
    initial_assessment_id UNIQUEIDENTIFIER NOT NULL,
    quizzes_correct       INT DEFAULT 0,
    total_questions       INT NOT NULL,
    completed_at          DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, initial_assessment_id),
    FOREIGN KEY (initial_assessment_id) REFERENCES initial_assessment(id)
    -- No FK on user_id: cross-service reference
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
PRINT 'Total tables created: 25';
PRINT 'Note: JSON content structures documented in:';
PRINT '  - CONTENT_STRUCTURE.md';
PRINT '  - INITIAL_ASSESSMENT_STRUCTURE.md';
GO

-- ============================================================================
-- FULL DATA INSERTS
-- ============================================================================
-- Auto-generated by medicalogy_docs/mockup_data/generation.py
-- Source layout: content_layout.json
-- Full-fledge pipeline: RESET DB + CREATE TABLES + INSERT ALL TABLES
-- Content strategy: SQL stores only file names for course/article content

-- AUTH SERVICE INSERTS
INSERT INTO user_demographic (id, name, description, min_age, max_age) VALUES ('91AD376F-27B7-5CD3-A169-C2657F60CCD4', N'Adult Learner', N'General adult learner profile', 18, 65);
INSERT INTO user_demographic (id, name, description, min_age, max_age) VALUES ('1297D519-F7F8-5DC7-B74B-84A867416469', N'Young Adult Learner', N'Young healthcare-oriented learner profile', 16, 30);
INSERT INTO [user] (id, email, username, password_hash, user_demographic_id, date_of_birth, location, phone_number, oauth_provider, oauth_provider_id, role, is_active, is_verified, last_login_at) VALUES ('99D4855E-74F5-516C-AED8-421404E0CE83', N'admin@medicalogy.io', N'admin', N'hashed_admin_password', '91AD376F-27B7-5CD3-A169-C2657F60CCD4', '1990-05-14', N'Ho Chi Minh City', N'+84-900-111-222', NULL, NULL, N'ADMIN', 1, 1, GETDATE());
INSERT INTO [user] (id, email, username, password_hash, user_demographic_id, date_of_birth, location, phone_number, oauth_provider, oauth_provider_id, role, is_active, is_verified, last_login_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'learner@medicalogy.io', N'learner', N'hashed_learner_password', '1297D519-F7F8-5DC7-B74B-84A867416469', '2001-11-08', N'Da Nang', N'+84-933-456-789', N'google', N'google-learner-001', N'USER', 1, 1, GETDATE());
INSERT INTO refresh_token (id, user_id, token_hash, expires_at, revoked) VALUES ('95A28DF0-B59E-5E8C-BDB0-EDACE092CEA4', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'hash_refresh_learner_001', DATEADD(DAY, 30, GETDATE()), 0);
INSERT INTO user_setting (user_id, daily_reminder_time, theme_preference, daily_goal_courses) VALUES ('99D4855E-74F5-516C-AED8-421404E0CE83', '08:00:00', N'light', 2);
INSERT INTO user_setting (user_id, daily_reminder_time, theme_preference, daily_goal_courses) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '19:30:00', N'dark', 3);
INSERT INTO user_profile (user_id, display_name, avatar_url, bio, occupation, medical_background) VALUES ('99D4855E-74F5-516C-AED8-421404E0CE83', N'Medicalogy Admin', N'admin-avatar.png', N'Platform administrator for content quality', N'Administrator', 1);
INSERT INTO user_profile (user_id, display_name, avatar_url, bio, occupation, medical_background) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'Alex Learner', N'learner-avatar.png', N'Focused on emergency and clinical foundations', N'Medical Student', 1);

INSERT INTO theme (id, name, slug, description, icon_file_name, color_code, order_index) VALUES ('5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'Emergency Care Fundamentals', N'emergency-care-fundamentals', N'Core emergency response skills for high-risk situations.', N'emergency.svg', N'#EF4444', 1);
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('48189D58-BFAD-5845-A461-21A7055AC581', '5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'Airway Emergencies', N'airway-emergencies', 1, 45);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0', '5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'Airway Emergencies: Recognition and First Actions', N'airway-emergencies-recognition', N'airway-emergencies-recognition.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('249FF179-0178-5B27-8BD5-8A4386A5E224', '48189D58-BFAD-5845-A461-21A7055AC581', N'Recognizing Choking in Adults', N'Identify warning signs of mild and severe choking.', N'recognizing-choking-in-adults', 1, 8, N'beginner', 1, N'recognizing-choking-in-adults.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('8BFC0C2D-A6C2-5B51-84B7-58DAE8ABCB1D', '48189D58-BFAD-5845-A461-21A7055AC581', N'Heimlich Maneuver Basics', N'Perform abdominal thrusts safely and effectively.', N'heimlich-maneuver-basics', 2, 9, N'beginner', 1, N'heimlich-maneuver-basics.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('97BDA129-743C-581D-9E9F-AA909B909B1C', '48189D58-BFAD-5845-A461-21A7055AC581', N'Infant Airway Rescue', N'Use age-appropriate airway rescue for infants under one year.', N'infant-airway-rescue', 3, 10, N'intermediate', 1, N'infant-airway-rescue.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('7E7A7674-0826-51D8-9992-5C72F54D175D', '48189D58-BFAD-5845-A461-21A7055AC581', N'Unconscious Airway Management', N'Respond when airway obstruction progresses to unconsciousness.', N'unconscious-airway-management', 4, 9, N'intermediate', 1, N'unconscious-airway-management.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('976DDEC8-5E7A-53C4-BEEF-FB9E081CB291', '5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'Cardiac Emergencies', N'cardiac-emergencies', 2, 50);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('E8C813F4-1FA7-59DE-852C-2A2C606D8AA9', '5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'Cardiac Emergencies: Time-Critical Response', N'cardiac-emergencies-time-critical-response', N'cardiac-emergencies-time-critical-response.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('73F7A26E-D751-51D5-BF08-6F74604CC86B', '976DDEC8-5E7A-53C4-BEEF-FB9E081CB291', N'Heart Attack Red Flags', N'Recognize classic and atypical myocardial infarction symptoms.', N'heart-attack-red-flags', 1, 8, N'beginner', 1, N'heart-attack-red-flags.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('D9DEE909-1235-5CC0-883B-45921F5C8A76', '976DDEC8-5E7A-53C4-BEEF-FB9E081CB291', N'High-Quality CPR Essentials', N'Deliver effective chest compressions and rescue breaths.', N'high-quality-cpr-essentials', 2, 10, N'intermediate', 1, N'high-quality-cpr-essentials.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('59348BC4-213F-59EB-BE51-B84CC00C8354', '976DDEC8-5E7A-53C4-BEEF-FB9E081CB291', N'Automated External Defibrillator Use', N'Operate an AED safely during cardiac arrest.', N'automated-external-defibrillator-use', 3, 9, N'intermediate', 1, N'automated-external-defibrillator-use.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('22DD9098-9F46-5FB6-8F3A-0541D1A50FDD', '976DDEC8-5E7A-53C4-BEEF-FB9E081CB291', N'Post-Resuscitation Stabilization', N'Stabilize the patient after return of spontaneous circulation.', N'post-resuscitation-stabilization', 4, 10, N'advanced', 1, N'post-resuscitation-stabilization.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('77D05DE7-E13E-57AB-A53F-B21F497C0BDB', '5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'Trauma First Response', N'trauma-first-response', 3, 40);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('467402F7-7291-576F-936D-497810EA99E4', '5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'Trauma First Response: Priorities on Scene', N'trauma-first-response-priorities', N'trauma-first-response-priorities.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('D8D2FDE5-A30A-5712-A2BE-DC5F52DFA8A9', '77D05DE7-E13E-57AB-A53F-B21F497C0BDB', N'Primary Survey ABCDE', N'Apply the ABCDE framework in trauma response.', N'primary-survey-abcde', 1, 8, N'beginner', 1, N'primary-survey-abcde.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('891EC708-53E4-55F4-A7D6-6B41AA9F15AA', '77D05DE7-E13E-57AB-A53F-B21F497C0BDB', N'Bleeding Control and Tourniquet Use', N'Control external hemorrhage using direct pressure and tourniquets.', N'bleeding-control-and-tourniquet-use', 2, 9, N'intermediate', 1, N'bleeding-control-and-tourniquet-use.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('A942712F-E30C-5CF5-ADD5-530D9B32A13F', '77D05DE7-E13E-57AB-A53F-B21F497C0BDB', N'Suspected Fracture Immobilization', N'Immobilize fractures to prevent further harm.', N'suspected-fracture-immobilization', 3, 8, N'intermediate', 1, N'suspected-fracture-immobilization.json');

INSERT INTO theme (id, name, slug, description, icon_file_name, color_code, order_index) VALUES ('8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Mental Health Clinical Foundations', N'mental-health-clinical-foundations', N'Practical clinical knowledge for common mental health conditions.', N'mental-health.svg', N'#8B5CF6', 2);
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('3D900B49-C0B2-5B8D-855D-E7F1F7E9B1FA', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Anxiety Spectrum Disorders', N'anxiety-spectrum-disorders', 1, 38);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('9D8816C7-75B1-5433-ACFD-0B1CD01C0E75', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Anxiety Disorders: Early Detection and Support', N'anxiety-disorders-early-detection', N'anxiety-disorders-early-detection.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('C45E93C1-725B-5EC5-A954-83AB021DC293', '3D900B49-C0B2-5B8D-855D-E7F1F7E9B1FA', N'Generalized Anxiety Basics', N'Understand diagnostic features of generalized anxiety disorder.', N'generalized-anxiety-basics', 1, 8, N'beginner', 1, N'generalized-anxiety-basics.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('977B80F3-482C-54AB-9D61-9E60B6CC8AC1', '3D900B49-C0B2-5B8D-855D-E7F1F7E9B1FA', N'Panic Attack Triage', N'Perform rapid triage and reassurance for panic presentations.', N'panic-attack-triage', 2, 9, N'intermediate', 1, N'panic-attack-triage.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('FBF2AE55-A5D3-58F4-BED7-363FB3FB3783', '3D900B49-C0B2-5B8D-855D-E7F1F7E9B1FA', N'Social Anxiety in Practice', N'Assess social anxiety impact in school and work settings.', N'social-anxiety-in-practice', 3, 8, N'beginner', 1, N'social-anxiety-in-practice.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('91A80008-C3A5-5C14-9EB7-45A90D7598FF', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Mood Disorders', N'mood-disorders', 2, 42);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('00AA7DEC-04F3-50FD-8DA5-1B5B1AE0BFDE', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Mood Disorders: Recognition and Initial Care', N'mood-disorders-recognition-and-care', N'mood-disorders-recognition-and-care.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('00816BD4-E074-5C15-906B-F6B2CAB0D805', '91A80008-C3A5-5C14-9EB7-45A90D7598FF', N'Major Depression Core Features', N'Identify clinical indicators of major depressive episodes.', N'major-depression-core-features', 1, 8, N'beginner', 1, N'major-depression-core-features.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('89D6F65B-D3FC-5C43-BB48-2BBD6B77A3C9', '91A80008-C3A5-5C14-9EB7-45A90D7598FF', N'Bipolar Spectrum Overview', N'Differentiate bipolar patterns from unipolar depression.', N'bipolar-spectrum-overview', 2, 9, N'intermediate', 1, N'bipolar-spectrum-overview.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('0116FD42-6915-5CA2-96EB-B2B440622E47', '91A80008-C3A5-5C14-9EB7-45A90D7598FF', N'Behavioral Activation Basics', N'Use simple activation strategies for low mood.', N'behavioral-activation-basics', 3, 8, N'beginner', 1, N'behavioral-activation-basics.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('EE588991-4507-5922-BFE6-66A7EEF10ACE', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Crisis Intervention', N'crisis-intervention', 3, 50);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('445C1DD0-AC29-5D3E-8F68-3B27147F855D', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Crisis Intervention: Immediate Safety Protocols', N'crisis-intervention-safety-protocols', N'crisis-intervention-safety-protocols.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('ED971A4C-765A-5070-A154-B6C23D8B4389', 'EE588991-4507-5922-BFE6-66A7EEF10ACE', N'Verbal De-escalation Skills', N'Use language and posture to reduce escalating distress.', N'verbal-de-escalation-skills', 1, 9, N'intermediate', 1, N'verbal-de-escalation-skills.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('AF06E2A9-41C0-5275-9E6C-3BAC8DA0E176', 'EE588991-4507-5922-BFE6-66A7EEF10ACE', N'Suicide Risk Rapid Screen', N'Apply a structured approach to immediate suicide risk assessment.', N'suicide-risk-rapid-screen', 2, 10, N'advanced', 1, N'suicide-risk-rapid-screen.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('2B24D8C4-5CBA-578F-9B9A-C536A77ACB27', 'EE588991-4507-5922-BFE6-66A7EEF10ACE', N'Safety Planning in Outpatient Care', N'Create actionable safety plans with patients and families.', N'safety-planning-in-outpatient-care', 3, 9, N'intermediate', 1, N'safety-planning-in-outpatient-care.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('F16D2078-B74B-5D7E-8586-1856505AD5A5', 'EE588991-4507-5922-BFE6-66A7EEF10ACE', N'Coordinating Urgent Referral', N'Transfer care effectively to emergency or specialist services.', N'coordinating-urgent-referral', 4, 8, N'intermediate', 1, N'coordinating-urgent-referral.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('CD38B9CE-CBBF-58E5-B325-A7174494FA5E', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Sleep and Stress Medicine', N'sleep-and-stress-medicine', 4, 36);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('C816A38D-8C60-5F4D-9C88-2ED482BDA676', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'Sleep and Stress: Restoring Daily Function', N'sleep-and-stress-restoring-function', N'sleep-and-stress-restoring-function.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('07ACBBFF-218E-5252-9F7D-46449B75B64D', 'CD38B9CE-CBBF-58E5-B325-A7174494FA5E', N'Sleep Hygiene Essentials', N'Establish practical sleep routines for better recovery.', N'sleep-hygiene-essentials', 1, 7, N'beginner', 1, N'sleep-hygiene-essentials.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('5838038B-13E0-5260-82FA-33EE7148DF7A', 'CD38B9CE-CBBF-58E5-B325-A7174494FA5E', N'Stress Response and Cortisol', N'Understand stress hormone dynamics and symptom patterns.', N'stress-response-and-cortisol', 2, 8, N'intermediate', 1, N'stress-response-and-cortisol.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('E2ED48B0-CF0E-55A0-92BA-382EA25098CC', 'CD38B9CE-CBBF-58E5-B325-A7174494FA5E', N'Mindfulness for Clinical Settings', N'Apply brief mindfulness tools in high-pressure environments.', N'mindfulness-for-clinical-settings', 3, 8, N'beginner', 1, N'mindfulness-for-clinical-settings.json');

INSERT INTO theme (id, name, slug, description, icon_file_name, color_code, order_index) VALUES ('99099D54-D8CA-5388-A985-1DFE481E6A37', N'Nutrition and Metabolic Health', N'nutrition-and-metabolic-health', N'Evidence-based nutrition and metabolism principles for clinical care.', N'nutrition.svg', N'#10B981', 3);
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('BE96C81D-8A33-512C-B792-341B644AD433', '99099D54-D8CA-5388-A985-1DFE481E6A37', N'Balanced Nutrition Principles', N'balanced-nutrition-principles', 1, 34);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('0FEDC67A-3CD2-5577-A847-A5D8930DD46B', '99099D54-D8CA-5388-A985-1DFE481E6A37', N'Balanced Nutrition: Building Better Daily Intake', N'balanced-nutrition-building-better-intake', N'balanced-nutrition-building-better-intake.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('89835020-7780-55A5-8EA9-EE51704AF533', 'BE96C81D-8A33-512C-B792-341B644AD433', N'Macronutrients 101', N'Understand protein, carbohydrate, and fat functions.', N'macronutrients-101', 1, 7, N'beginner', 1, N'macronutrients-101.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('A76250EF-3947-520F-9CB5-8608A8FD44C3', 'BE96C81D-8A33-512C-B792-341B644AD433', N'Micronutrient Deficiency Clues', N'Recognize clinical signs of common deficiencies.', N'micronutrient-deficiency-clues', 2, 8, N'intermediate', 1, N'micronutrient-deficiency-clues.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('DD75FFA4-0B0E-502B-BFCA-873FBB9CBFCD', 'BE96C81D-8A33-512C-B792-341B644AD433', N'Healthy Plate Counseling', N'Deliver practical dietary counseling using plate models.', N'healthy-plate-counseling', 3, 8, N'beginner', 1, N'healthy-plate-counseling.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('7B982497-FDEC-598E-BB55-8E5A5A4C1FC2', '99099D54-D8CA-5388-A985-1DFE481E6A37', N'Clinical Nutrition in Chronic Disease', N'clinical-nutrition-in-chronic-disease', 2, 46);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('B628B13F-8EDE-56DA-B479-50C3888432B2', '99099D54-D8CA-5388-A985-1DFE481E6A37', N'Clinical Nutrition: Tailoring Diet for Disease', N'clinical-nutrition-tailoring-diet', N'clinical-nutrition-tailoring-diet.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('8E5FCDE0-5CB3-5731-83C1-3519512EE7E4', '7B982497-FDEC-598E-BB55-8E5A5A4C1FC2', N'Nutrition for Type 2 Diabetes', N'Plan carbohydrate and fiber strategies for glycemic control.', N'nutrition-for-type-2-diabetes', 1, 9, N'intermediate', 1, N'nutrition-for-type-2-diabetes.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('C37DFE19-4BA1-5153-B292-371643B46255', '7B982497-FDEC-598E-BB55-8E5A5A4C1FC2', N'DASH Diet in Practice', N'Implement DASH principles for blood pressure reduction.', N'dash-diet-in-practice', 2, 8, N'beginner', 1, N'dash-diet-in-practice.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('B0E00D8B-A0D0-5778-A0E0-5775A9A01266', '7B982497-FDEC-598E-BB55-8E5A5A4C1FC2', N'Nutrition in Chronic Kidney Disease', N'Adjust protein, sodium, and potassium intake in CKD.', N'nutrition-in-chronic-kidney-disease', 3, 10, N'advanced', 1, N'nutrition-in-chronic-kidney-disease.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('3585AC2B-DFD8-5F4E-ADC1-3CCF1378F0DC', '7B982497-FDEC-598E-BB55-8E5A5A4C1FC2', N'Counseling for Long-Term Adherence', N'Use behavior change methods to improve nutrition adherence.', N'counseling-for-long-term-adherence', 4, 8, N'intermediate', 1, N'counseling-for-long-term-adherence.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('16DF3BF9-1C97-543A-814A-086AC5165EE8', '99099D54-D8CA-5388-A985-1DFE481E6A37', N'Metabolic Syndrome and Obesity', N'metabolic-syndrome-and-obesity', 3, 38);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('2D624867-0C31-5FCB-BACF-FBD23E5BED9B', '99099D54-D8CA-5388-A985-1DFE481E6A37', N'Metabolic Syndrome: Integrated Risk Management', N'metabolic-syndrome-integrated-risk-management', N'metabolic-syndrome-integrated-risk-management.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('568ABDC0-2DF8-5B10-912B-6F5895BD3572', '16DF3BF9-1C97-543A-814A-086AC5165EE8', N'Metabolic Syndrome Criteria', N'Use standardized criteria to identify metabolic syndrome.', N'metabolic-syndrome-criteria', 1, 8, N'beginner', 1, N'metabolic-syndrome-criteria.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('2E0F3A85-4F28-5C50-89B8-2AAA6CBC1141', '16DF3BF9-1C97-543A-814A-086AC5165EE8', N'Obesity Assessment and Staging', N'Assess obesity severity using BMI and clinical staging.', N'obesity-assessment-and-staging', 2, 8, N'intermediate', 1, N'obesity-assessment-and-staging.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('A5D280F7-4C7A-50B3-8EE5-911A50AD6556', '16DF3BF9-1C97-543A-814A-086AC5165EE8', N'Lifestyle Intervention Planning', N'Build realistic diet and physical activity plans for weight reduction.', N'lifestyle-intervention-planning', 3, 9, N'beginner', 1, N'lifestyle-intervention-planning.json');

INSERT INTO theme (id, name, slug, description, icon_file_name, color_code, order_index) VALUES ('77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Infectious Disease Essentials', N'infectious-disease-essentials', N'Clinical essentials for prevention, diagnosis, and response to infectious diseases.', N'infectious.svg', N'#3B82F6', 4);
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('06FFBA0F-E7D6-54FB-92AF-E0DFEE0D0688', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Prevention and Infection Control', N'prevention-and-infection-control', 1, 33);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('D8412AD6-6700-5DCC-86AB-754C99345652', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Infection Control: Core Prevention Protocols', N'infection-control-core-prevention-protocols', N'infection-control-core-prevention-protocols.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('9CF805C8-7130-514D-89EA-A48B06AAF9A3', '06FFBA0F-E7D6-54FB-92AF-E0DFEE0D0688', N'Hand Hygiene Compliance', N'Apply hand hygiene standards in patient care workflows.', N'hand-hygiene-compliance', 1, 7, N'beginner', 1, N'hand-hygiene-compliance.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('2C5DED51-1F8B-55A6-AF4B-FD3572A29EC2', '06FFBA0F-E7D6-54FB-92AF-E0DFEE0D0688', N'PPE Selection and Donning', N'Select and wear PPE based on transmission risk.', N'ppe-selection-and-donning', 2, 8, N'intermediate', 1, N'ppe-selection-and-donning.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('C42D4E6B-7354-500F-860B-C77F188CCF00', '06FFBA0F-E7D6-54FB-92AF-E0DFEE0D0688', N'Isolation Precaution Types', N'Differentiate contact, droplet, and airborne precautions.', N'isolation-precaution-types', 3, 8, N'beginner', 1, N'isolation-precaution-types.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('723A6431-0E95-5600-91C2-E3E03847ABE4', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Respiratory Infections', N'respiratory-infections', 2, 44);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('F9B07620-02B5-52FE-B583-6E1843028DC3', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Respiratory Infections: Clinical Triage and Care', N'respiratory-infections-clinical-triage', N'respiratory-infections-clinical-triage.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('EB6FE3E4-0401-5B51-A1FD-E5E9C57EBCB5', '723A6431-0E95-5600-91C2-E3E03847ABE4', N'Viral vs Bacterial Patterns', N'Use history and exam clues to distinguish likely etiologies.', N'viral-vs-bacterial-patterns', 1, 8, N'beginner', 1, N'viral-vs-bacterial-patterns.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('DFFB9D29-863C-5A2D-AD46-0E883A185EB5', '723A6431-0E95-5600-91C2-E3E03847ABE4', N'Community-Acquired Pneumonia Basics', N'Assess and manage uncomplicated community-acquired pneumonia.', N'community-acquired-pneumonia-basics', 2, 9, N'intermediate', 1, N'community-acquired-pneumonia-basics.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('EA501A5F-6BB6-5314-ABB3-EA67DC031FBD', '723A6431-0E95-5600-91C2-E3E03847ABE4', N'Influenza Risk Stratification', N'Stratify flu risk and prioritize treatment timing.', N'influenza-risk-stratification', 3, 8, N'beginner', 1, N'influenza-risk-stratification.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('025B177B-6919-5245-A13A-0867C8173BE3', '723A6431-0E95-5600-91C2-E3E03847ABE4', N'Oxygen Therapy Fundamentals', N'Provide safe oxygen support in respiratory distress.', N'oxygen-therapy-fundamentals', 4, 9, N'intermediate', 1, N'oxygen-therapy-fundamentals.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('BF413914-D7C6-5530-80B4-EF8A668593E2', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Gastrointestinal Infections', N'gastrointestinal-infections', 3, 36);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('CA4CA7DC-AAEA-56D3-9D77-F5F4D82DBB00', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Gastrointestinal Infections: Hydration and Risk Control', N'gastrointestinal-infections-hydration-and-risk', N'gastrointestinal-infections-hydration-and-risk.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('DA279085-4922-58A8-960D-BC28FB8ED685', 'BF413914-D7C6-5530-80B4-EF8A668593E2', N'Acute Gastroenteritis Assessment', N'Assess dehydration risk in acute gastroenteritis.', N'acute-gastroenteritis-assessment', 1, 8, N'beginner', 1, N'acute-gastroenteritis-assessment.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('D8AA8B0A-FE8A-5576-9477-69CC81BB8E06', 'BF413914-D7C6-5530-80B4-EF8A668593E2', N'Oral Rehydration Therapy', N'Use oral rehydration correctly across age groups.', N'oral-rehydration-therapy', 2, 7, N'beginner', 1, N'oral-rehydration-therapy.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('14D398CE-8BC3-56C3-9D27-9FCB51941911', 'BF413914-D7C6-5530-80B4-EF8A668593E2', N'Foodborne Illness Investigation', N'Trace likely sources and provide preventive guidance.', N'foodborne-illness-investigation', 3, 8, N'intermediate', 1, N'foodborne-illness-investigation.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('794CDC75-4B9A-5DE5-9178-1B95DC51705C', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Vector-Borne Diseases', N'vector-borne-diseases', 4, 35);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('663377C7-8D10-5709-B5DB-7BB4BBA05B01', '77D325CC-5CDB-5323-97AF-03847F47A7BB', N'Vector-Borne Diseases: Prevention and Early Detection', N'vector-borne-diseases-prevention-and-detection', N'vector-borne-diseases-prevention-and-detection.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('92B737E1-E04A-5736-86A4-D7862EA7B979', '794CDC75-4B9A-5DE5-9178-1B95DC51705C', N'Dengue Warning Signs', N'Recognize warning signs and progression risk in dengue infection.', N'dengue-warning-signs', 1, 8, N'intermediate', 1, N'dengue-warning-signs.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('FFAB13FF-C687-5D36-97F3-FCD0071B8A35', '794CDC75-4B9A-5DE5-9178-1B95DC51705C', N'Malaria Rapid Recognition', N'Identify malaria patterns in febrile patients.', N'malaria-rapid-recognition', 2, 8, N'intermediate', 1, N'malaria-rapid-recognition.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('83E2D8EE-AF2F-5169-9DBA-09188DA423E6', '794CDC75-4B9A-5DE5-9178-1B95DC51705C', N'Community Vector Control', N'Design practical community-level vector reduction plans.', N'community-vector-control', 3, 7, N'beginner', 1, N'community-vector-control.json');

INSERT INTO theme (id, name, slug, description, icon_file_name, color_code, order_index) VALUES ('5CC4C039-5E34-54DC-8D9A-C5C606C55B1A', N'Maternal and Child Health', N'maternal-and-child-health', N'Foundational care pathways for pregnancy, newborn, and pediatric health.', N'maternal-child.svg', N'#F59E0B', 5);
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('FF91D008-4FED-52AA-B1B0-587C339B78C5', '5CC4C039-5E34-54DC-8D9A-C5C606C55B1A', N'Prenatal Care Pathways', N'prenatal-care-pathways', 1, 37);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('49937705-94B5-5EFB-8379-6BEB36654C83', '5CC4C039-5E34-54DC-8D9A-C5C606C55B1A', N'Prenatal Care: Structured Monitoring from First Visit', N'prenatal-care-structured-monitoring', N'prenatal-care-structured-monitoring.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('A9EB15B5-BF5B-5CF7-AC14-4F9786203F04', 'FF91D008-4FED-52AA-B1B0-587C339B78C5', N'First Antenatal Visit Essentials', N'Perform structured assessments during the first prenatal visit.', N'first-antenatal-visit-essentials', 1, 8, N'beginner', 1, N'first-antenatal-visit-essentials.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('8267B45C-9508-51A5-B21B-6C1C36EC6D8B', 'FF91D008-4FED-52AA-B1B0-587C339B78C5', N'Hypertensive Disorders in Pregnancy', N'Identify and triage hypertensive complications in pregnancy.', N'hypertensive-disorders-in-pregnancy', 2, 10, N'advanced', 1, N'hypertensive-disorders-in-pregnancy.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('C79EB38D-0DAB-5C39-BC19-FB649907B7B7', 'FF91D008-4FED-52AA-B1B0-587C339B78C5', N'Gestational Diabetes Monitoring', N'Apply screening and monitoring workflows for gestational diabetes.', N'gestational-diabetes-monitoring', 3, 9, N'intermediate', 1, N'gestational-diabetes-monitoring.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('F131981F-E4A7-5868-B990-AE70C3896305', '5CC4C039-5E34-54DC-8D9A-C5C606C55B1A', N'Newborn Care Essentials', N'newborn-care-essentials', 2, 44);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('B481FC61-F649-5EA8-9563-F0A7C3D1657A', '5CC4C039-5E34-54DC-8D9A-C5C606C55B1A', N'Newborn Care: The First 28 Days', N'newborn-care-first-28-days', N'newborn-care-first-28-days.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('CB31EEE0-8A0B-5156-B92F-ECBBAF30CA71', 'F131981F-E4A7-5868-B990-AE70C3896305', N'Immediate Newborn Assessment', N'Perform immediate post-delivery neonatal checks.', N'immediate-newborn-assessment', 1, 8, N'beginner', 1, N'immediate-newborn-assessment.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('059C8C49-94A4-567E-90FE-10A2B57553D8', 'F131981F-E4A7-5868-B990-AE70C3896305', N'Breastfeeding Support Basics', N'Support early breastfeeding initiation and latch quality.', N'breastfeeding-support-basics', 2, 8, N'beginner', 1, N'breastfeeding-support-basics.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('104F7887-DC23-54E0-9A8C-C91D6565A254', 'F131981F-E4A7-5868-B990-AE70C3896305', N'Neonatal Jaundice Monitoring', N'Monitor and triage jaundice severity in newborns.', N'neonatal-jaundice-monitoring', 3, 9, N'intermediate', 1, N'neonatal-jaundice-monitoring.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('1742D7BF-CD02-5BEA-A3C8-611B841E8361', 'F131981F-E4A7-5868-B990-AE70C3896305', N'Neonatal Danger Signs', N'Detect life-threatening neonatal warning signs early.', N'neonatal-danger-signs', 4, 8, N'intermediate', 1, N'neonatal-danger-signs.json');
INSERT INTO section (id, theme_id, name, slug, order_index, estimated_duration_minutes) VALUES ('BBBBB0B4-4C54-5827-B51B-F67F2BD3CB3C', '5CC4C039-5E34-54DC-8D9A-C5C606C55B1A', N'Common Pediatric Illnesses', N'common-pediatric-illnesses', 3, 39);
INSERT INTO article (id, theme_id, name, slug, content_markdown, author_admin_id, is_published, published_at) VALUES ('680FDCD8-ED12-5389-8273-ECC6C7ED7B97', '5CC4C039-5E34-54DC-8D9A-C5C606C55B1A', N'Pediatric Illnesses: Practical Frontline Management', N'pediatric-illnesses-frontline-management', N'pediatric-illnesses-frontline-management.md', '99D4855E-74F5-516C-AED8-421404E0CE83', 1, GETDATE());
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('DF845977-68A7-571D-A9AC-BE54FDE31C22', 'BBBBB0B4-4C54-5827-B51B-F67F2BD3CB3C', N'Pediatric Fever Triage', N'Assess fever severity and red flags in children.', N'pediatric-fever-triage', 1, 8, N'beginner', 1, N'pediatric-fever-triage.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('CDB1FAFE-499A-55D7-8B5D-097C58FC34DF', 'BBBBB0B4-4C54-5827-B51B-F67F2BD3CB3C', N'Acute Pediatric Respiratory Symptoms', N'Differentiate common respiratory presentations in children.', N'acute-pediatric-respiratory-symptoms', 2, 9, N'intermediate', 1, N'acute-pediatric-respiratory-symptoms.json');
INSERT INTO course (id, section_id, name, description, slug, order_index, estimated_duration_minutes, difficulty_level, is_active, content_file_name) VALUES ('246A1FF5-74CE-5A65-9AC0-11D443178B03', 'BBBBB0B4-4C54-5827-B51B-F67F2BD3CB3C', N'Pediatric Dehydration Management', N'Treat mild to moderate dehydration in children.', N'pediatric-dehydration-management', 3, 8, N'beginner', 1, N'pediatric-dehydration-management.json');

-- LEARNING PROGRESS INSERTS
INSERT INTO user_theme_enrollment (user_id, theme_id, status, enrolled_at, finished_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '5B7E35FF-572D-55BF-BB0D-3F7980368B7A', N'finished', DATEADD(DAY, -30, GETDATE()), DATEADD(DAY, -1, GETDATE()));
INSERT INTO user_theme_enrollment (user_id, theme_id, status, enrolled_at, finished_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '8655B47E-76C4-5DF7-B630-60B1F01259E0', N'enrolled', DATEADD(DAY, -7, GETDATE()), NULL);
INSERT INTO user_course (user_id, course_id, quizzes_correct, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '249FF179-0178-5B27-8BD5-8A4386A5E224', 4, DATEADD(DAY, -1, GETDATE()));
INSERT INTO user_course (user_id, course_id, quizzes_correct, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '8BFC0C2D-A6C2-5B51-84B7-58DAE8ABCB1D', 5, DATEADD(DAY, -2, GETDATE()));
INSERT INTO user_course (user_id, course_id, quizzes_correct, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '97BDA129-743C-581D-9E9F-AA909B909B1C', 3, DATEADD(DAY, -3, GETDATE()));
INSERT INTO user_course (user_id, course_id, quizzes_correct, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '7E7A7674-0826-51D8-9992-5C72F54D175D', 4, DATEADD(DAY, -4, GETDATE()));
INSERT INTO user_course (user_id, course_id, quizzes_correct, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '73F7A26E-D751-51D5-BF08-6F74604CC86B', 5, DATEADD(DAY, -5, GETDATE()));
INSERT INTO user_course (user_id, course_id, quizzes_correct, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'D9DEE909-1235-5CC0-883B-45921F5C8A76', 3, DATEADD(DAY, -6, GETDATE()));
INSERT INTO user_daily_streak (user_id, current_streak, longest_streak, last_activity_date, streak_started_at, total_active_days) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 12, 20, CAST(GETDATE() AS DATE), DATEADD(DAY, -12, CAST(GETDATE() AS DATE)), 45);

-- ASSESSMENT INSERTS
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('48189D58-BFAD-5845-A461-21A7055AC581', N'Airway Emergencies Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Airway Emergencies?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('976DDEC8-5E7A-53C4-BEEF-FB9E081CB291', N'Cardiac Emergencies Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Cardiac Emergencies?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('77D05DE7-E13E-57AB-A53F-B21F497C0BDB', N'Trauma First Response Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Trauma First Response?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('3D900B49-C0B2-5B8D-855D-E7F1F7E9B1FA', N'Anxiety Spectrum Disorders Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Anxiety Spectrum Disorders?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('91A80008-C3A5-5C14-9EB7-45A90D7598FF', N'Mood Disorders Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Mood Disorders?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('EE588991-4507-5922-BFE6-66A7EEF10ACE', N'Crisis Intervention Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Crisis Intervention?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('CD38B9CE-CBBF-58E5-B325-A7174494FA5E', N'Sleep and Stress Medicine Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Sleep and Stress Medicine?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('BE96C81D-8A33-512C-B792-341B644AD433', N'Balanced Nutrition Principles Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Balanced Nutrition Principles?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('7B982497-FDEC-598E-BB55-8E5A5A4C1FC2', N'Clinical Nutrition in Chronic Disease Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Clinical Nutrition in Chronic Disease?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('16DF3BF9-1C97-543A-814A-086AC5165EE8', N'Metabolic Syndrome and Obesity Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Metabolic Syndrome and Obesity?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('06FFBA0F-E7D6-54FB-92AF-E0DFEE0D0688', N'Prevention and Infection Control Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Prevention and Infection Control?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('723A6431-0E95-5600-91C2-E3E03847ABE4', N'Respiratory Infections Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Respiratory Infections?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('BF413914-D7C6-5530-80B4-EF8A668593E2', N'Gastrointestinal Infections Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Gastrointestinal Infections?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('794CDC75-4B9A-5DE5-9178-1B95DC51705C', N'Vector-Borne Diseases Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Vector-Borne Diseases?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('FF91D008-4FED-52AA-B1B0-587C339B78C5', N'Prenatal Care Pathways Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Prenatal Care Pathways?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('F131981F-E4A7-5868-B990-AE70C3896305', N'Newborn Care Essentials Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Newborn Care Essentials?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO section_test (section_id, name, passing_score_percentage, time_limit_minutes, max_attempts, is_active, content) VALUES ('BBBBB0B4-4C54-5827-B51B-F67F2BD3CB3C', N'Common Pediatric Illnesses Final Assessment', 70.00, 30, 3, 1, N'{"version": "1.0", "questions": [{"id": "q-001", "orderIndex": 1, "difficultyLevel": "easy", "content": {"questionType": "multiple_choice", "questionText": "What is the first priority in Common Pediatric Illnesses?", "explanation": "Start with a rapid, structured assessment and immediate safety actions.", "options": [{"id": "a", "text": "Run structured first-line assessment", "isCorrect": true}, {"id": "b", "text": "Delay intervention", "isCorrect": false}, {"id": "c", "text": "Skip reassessment", "isCorrect": false}]}}, {"id": "q-002", "orderIndex": 2, "difficultyLevel": "medium", "content": {"questionType": "true_false", "questionText": "Escalation is needed when red flags persist after first-line interventions.", "explanation": "Persistent instability requires escalation.", "correctAnswer": true}}]}');
INSERT INTO initial_assessment (id, name, version, is_active, content) VALUES ('A11D5CDA-0592-5A27-B9E9-19F785E94DA1', N'Learner Placement Assessment', 1, 1, N'{"version": "1.0", "questions": [{"id": "ia-001", "orderIndex": 1, "content": {"questionType": "multiple_choice", "questionText": "How confident are you with emergency first response basics?", "options": [{"id": "a", "text": "Beginner", "isCorrect": false}, {"id": "b", "text": "Intermediate", "isCorrect": true}, {"id": "c", "text": "Advanced", "isCorrect": false}]}}, {"id": "ia-002", "orderIndex": 2, "content": {"questionType": "true_false", "questionText": "You are comfortable with structured clinical checklists.", "correctAnswer": true}}]}');
INSERT INTO user_section_test (user_id, section_test_id, quizzes_correct, total_questions, passed, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '48189D58-BFAD-5845-A461-21A7055AC581', 7, 10, 1, DATEADD(DAY, -1, GETDATE()));
INSERT INTO user_section_test (user_id, section_test_id, quizzes_correct, total_questions, passed, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '976DDEC8-5E7A-53C4-BEEF-FB9E081CB291', 8, 10, 1, DATEADD(DAY, -2, GETDATE()));
INSERT INTO user_section_test (user_id, section_test_id, quizzes_correct, total_questions, passed, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '77D05DE7-E13E-57AB-A53F-B21F497C0BDB', 9, 10, 1, DATEADD(DAY, -3, GETDATE()));
INSERT INTO user_initial_assessment (user_id, initial_assessment_id, quizzes_correct, total_questions, completed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'A11D5CDA-0592-5A27-B9E9-19F785E94DA1', 7, 10, DATEADD(DAY, -60, GETDATE()));

-- DICTIONARY TAG/SOCIAL INSERTS
INSERT INTO tag (id, name) VALUES ('4AC8BBE5-263F-58B4-98A2-70374CD198FF', N'emergency');
INSERT INTO tag (id, name) VALUES ('A55D5F33-E860-5A7D-A9F6-9FDCF9D27B80', N'mental-health');
INSERT INTO tag (id, name) VALUES ('F441D76B-B6FB-58FD-BEE2-72599D32F2DE', N'nutrition');
INSERT INTO tag (id, name) VALUES ('29C9701B-B34C-5218-86A1-39C61828541C', N'infection');
INSERT INTO tag (id, name) VALUES ('7175A6AE-74BD-51EB-A155-99FD4140A0DD', N'maternal-child');
INSERT INTO article_tag (article_id, tag_id) VALUES ('FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0', '4AC8BBE5-263F-58B4-98A2-70374CD198FF');
INSERT INTO article_tag (article_id, tag_id) VALUES ('E8C813F4-1FA7-59DE-852C-2A2C606D8AA9', '4AC8BBE5-263F-58B4-98A2-70374CD198FF');
INSERT INTO article_tag (article_id, tag_id) VALUES ('467402F7-7291-576F-936D-497810EA99E4', '4AC8BBE5-263F-58B4-98A2-70374CD198FF');
INSERT INTO article_tag (article_id, tag_id) VALUES ('9D8816C7-75B1-5433-ACFD-0B1CD01C0E75', 'A55D5F33-E860-5A7D-A9F6-9FDCF9D27B80');
INSERT INTO article_tag (article_id, tag_id) VALUES ('00AA7DEC-04F3-50FD-8DA5-1B5B1AE0BFDE', 'A55D5F33-E860-5A7D-A9F6-9FDCF9D27B80');
INSERT INTO article_tag (article_id, tag_id) VALUES ('445C1DD0-AC29-5D3E-8F68-3B27147F855D', 'A55D5F33-E860-5A7D-A9F6-9FDCF9D27B80');
INSERT INTO article_tag (article_id, tag_id) VALUES ('C816A38D-8C60-5F4D-9C88-2ED482BDA676', 'A55D5F33-E860-5A7D-A9F6-9FDCF9D27B80');
INSERT INTO article_tag (article_id, tag_id) VALUES ('0FEDC67A-3CD2-5577-A847-A5D8930DD46B', 'F441D76B-B6FB-58FD-BEE2-72599D32F2DE');
INSERT INTO article_tag (article_id, tag_id) VALUES ('B628B13F-8EDE-56DA-B479-50C3888432B2', 'F441D76B-B6FB-58FD-BEE2-72599D32F2DE');
INSERT INTO article_tag (article_id, tag_id) VALUES ('2D624867-0C31-5FCB-BACF-FBD23E5BED9B', 'F441D76B-B6FB-58FD-BEE2-72599D32F2DE');
INSERT INTO article_tag (article_id, tag_id) VALUES ('D8412AD6-6700-5DCC-86AB-754C99345652', '29C9701B-B34C-5218-86A1-39C61828541C');
INSERT INTO article_tag (article_id, tag_id) VALUES ('F9B07620-02B5-52FE-B583-6E1843028DC3', '29C9701B-B34C-5218-86A1-39C61828541C');
INSERT INTO article_tag (article_id, tag_id) VALUES ('CA4CA7DC-AAEA-56D3-9D77-F5F4D82DBB00', '29C9701B-B34C-5218-86A1-39C61828541C');
INSERT INTO article_tag (article_id, tag_id) VALUES ('663377C7-8D10-5709-B5DB-7BB4BBA05B01', '29C9701B-B34C-5218-86A1-39C61828541C');
INSERT INTO article_tag (article_id, tag_id) VALUES ('49937705-94B5-5EFB-8379-6BEB36654C83', '7175A6AE-74BD-51EB-A155-99FD4140A0DD');
INSERT INTO article_tag (article_id, tag_id) VALUES ('B481FC61-F649-5EA8-9563-F0A7C3D1657A', '7175A6AE-74BD-51EB-A155-99FD4140A0DD');
INSERT INTO article_tag (article_id, tag_id) VALUES ('680FDCD8-ED12-5389-8273-ECC6C7ED7B97', '7175A6AE-74BD-51EB-A155-99FD4140A0DD');
INSERT INTO article_related (article_id, related_article_id) VALUES ('FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0', 'E8C813F4-1FA7-59DE-852C-2A2C606D8AA9');
INSERT INTO article_related (article_id, related_article_id) VALUES ('E8C813F4-1FA7-59DE-852C-2A2C606D8AA9', 'FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0');
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0', 2, DATEADD(DAY, -16, GETDATE()), DATEADD(DAY, -1, GETDATE()));
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'E8C813F4-1FA7-59DE-852C-2A2C606D8AA9', 3, DATEADD(DAY, -17, GETDATE()), DATEADD(DAY, -2, GETDATE()));
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '467402F7-7291-576F-936D-497810EA99E4', 4, DATEADD(DAY, -18, GETDATE()), DATEADD(DAY, -3, GETDATE()));
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '9D8816C7-75B1-5433-ACFD-0B1CD01C0E75', 1, DATEADD(DAY, -19, GETDATE()), DATEADD(DAY, -4, GETDATE()));
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '00AA7DEC-04F3-50FD-8DA5-1B5B1AE0BFDE', 2, DATEADD(DAY, -20, GETDATE()), DATEADD(DAY, -5, GETDATE()));
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '445C1DD0-AC29-5D3E-8F68-3B27147F855D', 3, DATEADD(DAY, -21, GETDATE()), DATEADD(DAY, -6, GETDATE()));
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'C816A38D-8C60-5F4D-9C88-2ED482BDA676', 4, DATEADD(DAY, -22, GETDATE()), DATEADD(DAY, -7, GETDATE()));
INSERT INTO user_article_view (user_id, article_id, view_count, first_viewed_at, last_viewed_at) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '0FEDC67A-3CD2-5577-A847-A5D8930DD46B', 1, DATEADD(DAY, -23, GETDATE()), DATEADD(DAY, -8, GETDATE()));
INSERT INTO user_article_comment (id, user_id, article_id, parent_comment_id, comment_text, is_approved) VALUES ('27E41F2E-9054-5614-9BC9-BF996FE2991A', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0', NULL, N'This article is detailed and practical.', 1);
INSERT INTO user_article_comment (id, user_id, article_id, parent_comment_id, comment_text, is_approved) VALUES ('FD34FC2A-3D85-5C4B-8D8B-BEB65D112514', '99D4855E-74F5-516C-AED8-421404E0CE83', 'FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0', '27E41F2E-9054-5614-9BC9-BF996FE2991A', N'Thanks for the feedback. More updates are coming.', 1);
INSERT INTO user_comment_vote (user_id, comment_id, vote_type) VALUES ('99D4855E-74F5-516C-AED8-421404E0CE83', '27E41F2E-9054-5614-9BC9-BF996FE2991A', N'like');
INSERT INTO user_bookmark (id, user_id, article_id) VALUES ('1EF42ACE-7540-5C7A-A202-77F73B699501', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0');
INSERT INTO user_bookmark (id, user_id, article_id) VALUES ('792B5F8D-4F31-5DF7-AD30-FCCE7AAF9D27', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', 'E8C813F4-1FA7-59DE-852C-2A2C606D8AA9');
INSERT INTO user_bookmark (id, user_id, article_id) VALUES ('812C8744-049E-54CA-B641-CE343781C78B', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '467402F7-7291-576F-936D-497810EA99E4');
INSERT INTO user_bookmark (id, user_id, article_id) VALUES ('642A29F9-1618-5BB8-9602-8FC6C82F29C9', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '9D8816C7-75B1-5433-ACFD-0B1CD01C0E75');
INSERT INTO user_bookmark (id, user_id, article_id) VALUES ('02EA350F-7A5E-5F83-9F7D-9E108990A345', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', '00AA7DEC-04F3-50FD-8DA5-1B5B1AE0BFDE');

-- NOTIFICATION INSERTS
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'streak_reminder', 1, 1, 1);
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'course_recommendation', 1, 1, 1);
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'test_result', 1, 1, 1);
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'comment_reply', 1, 1, 1);
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'system_log', 1, 1, 1);
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'security', 1, 1, 1);
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'achievement', 1, 1, 1);
INSERT INTO user_notification_preference (user_id, notification_type, in_app_enabled, email_enabled, push_enabled) VALUES ('D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'content_update', 1, 1, 1);
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('A3738060-11AD-555A-9431-AFD98CE4B23B', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'streak_reminder', NULL, NULL, 0, NULL, DATEADD(HOUR, -1, GETDATE()), DATEADD(HOUR, -1, GETDATE()));
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('BA96A814-E6DF-5B9E-93C8-46A4BECBCE7D', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'course_recommendation', N'course', '249FF179-0178-5B27-8BD5-8A4386A5E224', 0, NULL, DATEADD(HOUR, -2, GETDATE()), DATEADD(HOUR, -2, GETDATE()));
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('F78573B1-1941-54E4-B66A-8B69F1C03B90', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'test_result', N'section_test', '48189D58-BFAD-5845-A461-21A7055AC581', 1, DATEADD(HOUR, -1, GETDATE()), DATEADD(HOUR, -3, GETDATE()), DATEADD(HOUR, -3, GETDATE()));
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('1F5FAFAC-F5AE-5A64-87FE-FBAA813153EB', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'comment_reply', N'comment', '27E41F2E-9054-5614-9BC9-BF996FE2991A', 0, NULL, DATEADD(HOUR, -4, GETDATE()), DATEADD(HOUR, -4, GETDATE()));
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('21E6798D-4E83-582B-9DF6-0D57C454BC8F', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'system_log', NULL, NULL, 0, NULL, DATEADD(HOUR, -5, GETDATE()), DATEADD(HOUR, -5, GETDATE()));
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('17136460-73F8-5111-ACD4-E663F4E7CE05', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'security', NULL, NULL, 1, DATEADD(HOUR, -1, GETDATE()), DATEADD(HOUR, -6, GETDATE()), DATEADD(HOUR, -6, GETDATE()));
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('1DD21DCE-2BF9-5DF9-BF53-D566C3A0341D', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'achievement', N'course', '8BFC0C2D-A6C2-5B51-84B7-58DAE8ABCB1D', 0, NULL, DATEADD(HOUR, -7, GETDATE()), DATEADD(HOUR, -7, GETDATE()));
INSERT INTO notification (id, user_id, notification_type, reference_type, reference_id, is_read, read_at, sent_at, created_at) VALUES ('AB0111DE-B857-5286-B0DB-37904A0182D7', 'D0FD63AB-7DD9-5AF6-BB78-C901E7442B98', N'content_update', N'article', 'FCB8E1A5-48FD-5767-83C7-E4D6E89C94F0', 0, NULL, DATEADD(HOUR, -8, GETDATE()), DATEADD(HOUR, -8, GETDATE()));
