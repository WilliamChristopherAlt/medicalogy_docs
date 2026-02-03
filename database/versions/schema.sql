-- ============================================================================
-- BioBasics Database Schema - FINAL REVISION
-- Database: medicalogy
-- SQL Server Implementation
-- ============================================================================
-- 
-- SYSTEM OVERVIEW:
-- 4-Level Content Hierarchy: Theme → Section → Course → Screen
-- Simplified Progress Tracking: user-course, user-section-test, initial assessment
-- Article System: Medical encyclopedia with categories, tags, comments, views
-- 
-- ============================================================================

USE master;
GO

-- Create database if not exists
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'medicalogy')
BEGIN
    CREATE DATABASE medicalogy;
END
GO

USE medicalogy;
GO

-- ============================================================================
-- SECTION 1: USER MANAGEMENT & AUTHENTICATION
-- ============================================================================

-- User demographic enumeration
CREATE TABLE user_demographic (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(500),
    min_age INT,
    max_age INT,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Main user table
CREATE TABLE [user] (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    email NVARCHAR(255) NOT NULL UNIQUE,
    username NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    user_demographic_id UNIQUEIDENTIFIER NOT NULL,
    date_of_birth DATE,
    location NVARCHAR(200),
    is_active BIT DEFAULT 1,
    is_verified BIT DEFAULT 0,
    last_login_at DATETIME2,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_demographic_id) REFERENCES user_demographic(id)
);

-- User settings and preferences
CREATE TABLE user_setting (
    user_id UNIQUEIDENTIFIER PRIMARY KEY,
    notification_enabled BIT DEFAULT 1,
    daily_reminder_time TIME,
    email_notifications BIT DEFAULT 1,
    push_notifications BIT DEFAULT 1,
    theme_preference NVARCHAR(20) DEFAULT 'light',
    daily_goal_courses INT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE,
    CONSTRAINT chk_theme_preference CHECK (theme_preference IN ('light', 'dark', 'auto'))
);

-- User profile additional information
CREATE TABLE user_profile (
    user_id UNIQUEIDENTIFIER PRIMARY KEY,
    display_name NVARCHAR(200),
    avatar_url NVARCHAR(500),
    bio NVARCHAR(1000),
    occupation NVARCHAR(200),
    medical_background BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE
);

-- ============================================================================
-- SECTION 2: CONTENT HIERARCHY (4 LEVELS)
-- ============================================================================

-- Level 1: Theme/Domain (e.g., "Emergency", "Mental Health", "Nutrition")
CREATE TABLE theme (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name NVARCHAR(200) NOT NULL,
    slug NVARCHAR(300) NOT NULL UNIQUE,
    description NVARCHAR(1000),
    icon_file_name NVARCHAR(255),
    color_code NVARCHAR(20),
    order_index INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Level 2: Section (e.g., "Choking", "CPR", "Electrocution")
CREATE TABLE section (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    theme_id UNIQUEIDENTIFIER NOT NULL,
    name NVARCHAR(200) NOT NULL,
    slug NVARCHAR(300) NOT NULL,
    description NVARCHAR(1000),
    order_index INT NOT NULL,
    estimated_duration_minutes INT,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (theme_id) REFERENCES theme(id)
);

-- Level 3: Course (short 5-10 minute learning units)
CREATE TABLE course (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    section_id UNIQUEIDENTIFIER NOT NULL,
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(1000),
    order_index INT NOT NULL,
    estimated_duration_minutes INT DEFAULT 7,
    difficulty_level NVARCHAR(20) DEFAULT 'beginner',
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (section_id) REFERENCES section(id),
    CONSTRAINT chk_difficulty_level CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced'))
);

-- Level 4: Screen (individual infographic or quiz within a course)
CREATE TABLE screen (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    course_id UNIQUEIDENTIFIER NOT NULL,
    screen_type NVARCHAR(20) NOT NULL,
    order_index INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES course(id),
    CONSTRAINT chk_screen_type CHECK (screen_type IN ('infographic', 'quiz'))
);

-- Infographic content for screens
CREATE TABLE screen_infographic (
    screen_id UNIQUEIDENTIFIER PRIMARY KEY,
    image_file_name NVARCHAR(255),
    summary_text NVARCHAR(2000),
    FOREIGN KEY (screen_id) REFERENCES screen(id) ON DELETE CASCADE
);

-- Quiz questions for screens
CREATE TABLE screen_quiz (
    screen_id UNIQUEIDENTIFIER PRIMARY KEY,
    question_text NVARCHAR(1000) NOT NULL,
    question_type NVARCHAR(20) DEFAULT 'multiple_choice',
    explanation NVARCHAR(2000),
    FOREIGN KEY (screen_id) REFERENCES screen(id) ON DELETE CASCADE,
    CONSTRAINT chk_quiz_question_type CHECK (question_type IN ('multiple_choice', 'true_false', 'matching'))
);

-- Quiz answer options
CREATE TABLE quiz_answer_option (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    screen_quiz_id UNIQUEIDENTIFIER NOT NULL,
    option_text NVARCHAR(500) NOT NULL,
    is_correct BIT DEFAULT 0,
    order_index INT NOT NULL,
    explanation NVARCHAR(1000),
    FOREIGN KEY (screen_quiz_id) REFERENCES screen_quiz(screen_id) ON DELETE CASCADE
);

-- ============================================================================
-- SECTION 3: ASSESSMENTS
-- ============================================================================

-- Section test (comprehensive test at end of section)
CREATE TABLE section_test (
    section_id UNIQUEIDENTIFIER PRIMARY KEY,
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(1000),
    passing_score_percentage DECIMAL(5,2) DEFAULT 70.00,
    time_limit_minutes INT DEFAULT 30,
    max_attempts INT,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (section_id) REFERENCES section(id)
);

-- Section test questions
CREATE TABLE section_test_question (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    section_test_id UNIQUEIDENTIFIER NOT NULL,
    question_text NVARCHAR(1000) NOT NULL,
    question_type NVARCHAR(20) DEFAULT 'multiple_choice',
    explanation NVARCHAR(2000),
    points INT DEFAULT 1,
    difficulty_level NVARCHAR(20) DEFAULT 'medium',
    order_index INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (section_test_id) REFERENCES section_test(section_id) ON DELETE CASCADE,
    CONSTRAINT chk_test_question_type CHECK (question_type IN ('multiple_choice', 'true_false', 'matching')),
    CONSTRAINT chk_test_difficulty_level CHECK (difficulty_level IN ('easy', 'medium', 'hard'))
);

-- Section test answer options
CREATE TABLE section_test_answer_option (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    section_test_question_id UNIQUEIDENTIFIER NOT NULL,
    option_text NVARCHAR(500) NOT NULL,
    is_correct BIT DEFAULT 0,
    order_index INT NOT NULL,
    explanation NVARCHAR(1000),
    FOREIGN KEY (section_test_question_id) REFERENCES section_test_question(id) ON DELETE CASCADE
);

-- Initial assessment questionnaire
CREATE TABLE initial_assessment (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(1000),
    version INT DEFAULT 1,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Initial assessment questions
CREATE TABLE initial_assessment_question (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    initial_assessment_id UNIQUEIDENTIFIER NOT NULL,
    question_text NVARCHAR(1000) NOT NULL,
    question_type NVARCHAR(20) DEFAULT 'multiple_choice',
    category NVARCHAR(100),
    order_index INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (initial_assessment_id) REFERENCES initial_assessment(id) ON DELETE CASCADE,
    CONSTRAINT chk_initial_question_type CHECK (question_type IN ('multiple_choice', 'true_false', 'scale'))
);

-- Initial assessment answer options
CREATE TABLE initial_assessment_answer_option (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    initial_assessment_question_id UNIQUEIDENTIFIER NOT NULL,
    option_text NVARCHAR(500) NOT NULL,
    score_value INT DEFAULT 0,
    order_index INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (initial_assessment_question_id) REFERENCES initial_assessment_question(id) ON DELETE CASCADE
);

-- ============================================================================
-- SECTION 4: USER PROGRESS TRACKING (SIMPLIFIED)
-- ============================================================================

-- User course progress - existence means they've done it
CREATE TABLE user_course (
    user_id UNIQUEIDENTIFIER NOT NULL,
    course_id UNIQUEIDENTIFIER NOT NULL,
    quizzes_correct INT DEFAULT 0,
    completed_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, course_id),
    FOREIGN KEY (user_id) REFERENCES [user](id),
    FOREIGN KEY (course_id) REFERENCES course(id)
);

-- User section test results - existence means they've taken it
CREATE TABLE user_section_test (
    user_id UNIQUEIDENTIFIER NOT NULL,
    section_test_id UNIQUEIDENTIFIER NOT NULL,
    quizzes_correct INT DEFAULT 0,
    total_questions INT NOT NULL,
    passed BIT DEFAULT 0,
    completed_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, section_test_id),
    FOREIGN KEY (user_id) REFERENCES [user](id),
    FOREIGN KEY (section_test_id) REFERENCES section_test(section_id)
);

-- User initial assessment results - existence means they've taken it
CREATE TABLE user_initial_assessment (
    user_id UNIQUEIDENTIFIER NOT NULL,
    initial_assessment_id UNIQUEIDENTIFIER NOT NULL,
    quizzes_correct INT DEFAULT 0,
    total_questions INT NOT NULL,
    completed_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, initial_assessment_id),
    FOREIGN KEY (user_id) REFERENCES [user](id),
    FOREIGN KEY (initial_assessment_id) REFERENCES initial_assessment(id)
);

-- ============================================================================
-- SECTION 5: DAILY STREAK
-- ============================================================================

-- Daily streak tracking
CREATE TABLE user_daily_streak (
    user_id UNIQUEIDENTIFIER PRIMARY KEY,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    last_activity_date DATE,
    streak_started_at DATE,
    total_active_days INT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id) ON DELETE CASCADE
);

-- ============================================================================
-- SECTION 6: ARTICLE SYSTEM (MEDICAL ENCYCLOPEDIA)
-- ============================================================================

-- Article categories
CREATE TABLE category (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name NVARCHAR(200) NOT NULL UNIQUE,
    description NVARCHAR(1000),
    order_index INT NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Article tags
CREATE TABLE tag (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name NVARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME2 DEFAULT GETDATE()
);

-- Articles (medical encyclopedia entries)
CREATE TABLE article (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    category_id UNIQUEIDENTIFIER NOT NULL,
    terminology NVARCHAR(300) NOT NULL UNIQUE,
    slug NVARCHAR(300) NOT NULL UNIQUE,
    content_html NVARCHAR(MAX) NOT NULL,
    author_admin_id UNIQUEIDENTIFIER,
    is_published BIT DEFAULT 0,
    published_at DATETIME2,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (author_admin_id) REFERENCES [user](id)
);

-- Article tags (many-to-many)
CREATE TABLE article_tag (
    article_id UNIQUEIDENTIFIER NOT NULL,
    tag_id UNIQUEIDENTIFIER NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
);

-- Related articles (many-to-many, bidirectional)
CREATE TABLE article_related (
    article_id UNIQUEIDENTIFIER NOT NULL,
    related_article_id UNIQUEIDENTIFIER NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (article_id, related_article_id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    FOREIGN KEY (related_article_id) REFERENCES article(id),
    CONSTRAINT chk_no_self_relation CHECK (article_id != related_article_id)
);

-- User article views (tracking who viewed what)
CREATE TABLE user_article_view (
    user_id UNIQUEIDENTIFIER NOT NULL,
    article_id UNIQUEIDENTIFIER NOT NULL,
    view_count INT DEFAULT 1,
    first_viewed_at DATETIME2 DEFAULT GETDATE(),
    last_viewed_at DATETIME2 DEFAULT GETDATE(),
    PRIMARY KEY (user_id, article_id),
    FOREIGN KEY (user_id) REFERENCES [user](id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE
);

-- User article comments
CREATE TABLE user_article_comment (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,
    article_id UNIQUEIDENTIFIER NOT NULL,
    comment_text NVARCHAR(MAX) NOT NULL,
    is_approved BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE
);

-- ============================================================================
-- SECTION 7: USER BOOKMARKS
-- ============================================================================

-- User bookmarks (for articles only)
CREATE TABLE user_bookmark (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,
    article_id UNIQUEIDENTIFIER NOT NULL,
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id),
    FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
    CONSTRAINT uq_user_bookmark UNIQUE (user_id, article_id)
);

-- ============================================================================
-- SECTION 8: NOTIFICATIONS
-- ============================================================================

-- System notifications
CREATE TABLE notification (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,
    notification_type NVARCHAR(50) NOT NULL,
    title NVARCHAR(200) NOT NULL,
    message NVARCHAR(1000),
    reference_type NVARCHAR(50),
    reference_id UNIQUEIDENTIFIER,
    is_read BIT DEFAULT 0,
    read_at DATETIME2,
    sent_at DATETIME2 DEFAULT GETDATE(),
    created_at DATETIME2 DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES [user](id),
    CONSTRAINT chk_notification_type CHECK (notification_type IN ('streak_reminder', 'course_recommendation', 'system', 'test_result', 'comment_reply')),
    CONSTRAINT chk_reference_type CHECK (reference_type IN ('course', 'section', 'test', 'article', 'none') OR reference_type IS NULL)
);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

PRINT 'BioBasics database schema created successfully!';
PRINT 'Total tables created: 31';
GO