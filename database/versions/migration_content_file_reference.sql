-- ============================================================
-- MIGRATION: Store content as file name references only
-- Target schema: schema v4
-- ============================================================
-- This migration enforces:
-- 1) course.content_file_name stores only '*.json' file names
-- 2) article.content_markdown stores only '*.md' file names
--
-- IMPORTANT:
-- - Run this only after converting existing rows from raw JSON/Markdown
--   into file names (for example: 'recognizing-choking-in-adults.json').
-- ============================================================

-- 1) Course: drop JSON validation constraint if it exists
IF EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'chk_content_is_json'
)
BEGIN
    ALTER TABLE course DROP CONSTRAINT chk_content_is_json;
END
GO

-- 2) Course: rename content -> content_file_name (if needed), then enforce .json
IF COL_LENGTH('course', 'content_file_name') IS NULL
BEGIN
    EXEC sp_rename 'course.content', 'content_file_name', 'COLUMN';
END
GO

ALTER TABLE course ALTER COLUMN content_file_name NVARCHAR(255) NOT NULL;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'chk_course_content_file_name'
)
BEGIN
    ALTER TABLE course
    ADD CONSTRAINT chk_course_content_file_name
    CHECK (RIGHT(content_file_name, 5) = '.json');
END
GO

-- 3) Article: make content_markdown filename-sized and enforce .md extension
ALTER TABLE article ALTER COLUMN content_markdown NVARCHAR(255) NOT NULL;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'chk_article_content_file_name'
)
BEGIN
    ALTER TABLE article
    ADD CONSTRAINT chk_article_content_file_name
    CHECK (RIGHT(content_markdown, 3) = '.md');
END
GO

-- 4) Safety checks (optional)
-- SELECT TOP 20 id, slug, content_file_name FROM course;
-- SELECT TOP 20 id, slug, content_markdown FROM article;

PRINT 'Migration completed: content fields now store file names only.';
