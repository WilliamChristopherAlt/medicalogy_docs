"""
Medicalogy Medical Wiki Markdown to HTML Converter (v3)
Converts custom medical markdown format to styled HTML pages.
"""

import re
from typing import List, Tuple, Optional, Dict


class MedicalogyMarkdownConverter:
    """
    Converts Medicalogy custom markdown to HTML.

    Supported syntax:
    - Headers: # H1, ## H2, ### H3
    - Bold: **text**
    - Italic: *text*
    - Wiki links (internal): [[term]] - creates internal page links
    - External links: [text](url) - creates external links
    - Images: ![position|alt text](url) where position is left, right, or center
    - Image descriptions: /description text/ immediately after image
    - Horizontal rules: ---
    - Bullet lists: - item
    - Numbered lists: 1. item
    - Tight lists (inside [[[ ]]] blocks)
    - Tables: | Header | Header |
    - Sources section (special formatting)
    - Discussion section with comments/replies/likes (auto-added)
    - Table of contents (auto-generated from h2/h3 headers)
    - Article metadata (view count, last viewed, tags, related articles)
    """

    def __init__(self):
        self.in_table = False
        self.in_list = False
        self.in_ordered_list = False
        self.table_headers = []
        self.toc_entries: List[Dict] = []
        self.article_title = ""

    def convert(self, markdown_text: str,
                view_count: int = 0,
                last_viewed_at: str = "",
                tags: List[str] = None,
                related_articles: List[Dict] = None) -> str:
        """
        Convert markdown text to a complete HTML document.

        Args:
            markdown_text: The markdown content
            view_count: Number of times article has been viewed
            last_viewed_at: Formatted datetime string of last view
            tags: List of tag name strings
            related_articles: List of dicts with 'title', 'slug', 'category' keys
        """
        if tags is None:
            tags = []
        if related_articles is None:
            related_articles = []

        # Reset state
        self.in_table = False
        self.in_list = False
        self.in_ordered_list = False
        self.table_headers = []
        self.toc_entries = []
        self.article_title = ""

        lines = markdown_text.strip().split('\n')

        # First pass: extract headers for TOC
        self._extract_toc(lines)

        # Second pass: convert content
        body_html = self._convert_lines(lines)

        # Generate components
        top_meta_html = self._generate_top_metadata(view_count, last_viewed_at, tags)
        sidebar_html = self._generate_article_sidebar(related_articles)
        discussion_html = self._generate_discussion_section()

        return self._wrap_in_html(top_meta_html, sidebar_html, body_html + discussion_html)

    # ------------------------------------------------------------------ #
    #  TOC extraction
    # ------------------------------------------------------------------ #

    def _extract_toc(self, lines: List[str]) -> None:
        """Extract h2/h3 headers from markdown for the table of contents."""
        for line in lines:
            line = line.strip()
            if not line.startswith('#'):
                continue
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if not match:
                continue
            level = len(match.group(1))
            text = match.group(2)

            # Strip inline formatting to get plain text (v2 syntax)
            clean = re.sub(r'\*([^\*]+)\*', r'\1', text)        # *bold*
            clean = re.sub(r'/([^/\n]+)/', r'\1', clean)        # /italic/
            clean = re.sub(r'\[([^|\]]+)\|[^\]]+\]', r'\1', clean)   # [text|slug]
            clean = re.sub(r'\{([^|]+)\|[^}]+\}', r'\1', clean)      # {text|url}

            if level == 1 and not self.article_title:
                self.article_title = clean

            # Only h2/h3 in TOC, skip Sources header
            if level in (2, 3) and 'Sources' not in clean:
                self.toc_entries.append({
                    'level': level,
                    'text': clean,
                    'id': self._generate_header_id(clean),
                })

    def _generate_header_id(self, text: str) -> str:
        """Generate a URL-safe ID from header text."""
        hid = text.lower()
        hid = re.sub(r'[^\w\s-]', '', hid)
        hid = re.sub(r'\s+', '-', hid)
        return hid

    # ------------------------------------------------------------------ #
    #  Sidebar (article TOC + related articles — right-hand column)
    # ------------------------------------------------------------------ #

    def _generate_article_sidebar(self, related_articles: List[Dict]) -> str:
        """Generate the right-hand article sidebar (TOC + related articles)."""
        parts = ['<aside class="article-sidebar">']

        # Table of Contents
        if self.toc_entries:
            parts.append('<div class="sidebar-section-card toc-section">')
            parts.append('<h3 class="sidebar-card-title">Table of Contents</h3>')
            parts.append('<nav class="toc-nav"><ul class="toc-list">')
            for entry in self.toc_entries:
                indent = 'toc-h3' if entry['level'] == 3 else 'toc-h2'
                parts.append(f'<li class="toc-item {indent}">')
                parts.append(f'<a href="#{entry["id"]}" class="toc-link">{entry["text"]}</a>')
                parts.append('</li>')
            parts.append('</ul></nav>')
            parts.append('</div>')

        # Related Articles
        if related_articles:
            parts.append('<div class="sidebar-section-card related-section">')
            parts.append('<h3 class="sidebar-card-title">Related Articles</h3>')
            parts.append('<ul class="related-list">')
            for article in related_articles:
                parts.append('<li class="related-item">')
                parts.append(f'<a href="/wiki/{article.get("slug", "")}" class="related-link">')
                parts.append(f'<span class="related-title">{article.get("title", "")}</span>')
                if article.get('category'):
                    parts.append(f'<span class="related-category">{article["category"]}</span>')
                parts.append('</a></li>')
            parts.append('</ul></div>')

        parts.append('</aside>')
        return '\n'.join(parts)

    # ------------------------------------------------------------------ #
    #  Top metadata bar
    # ------------------------------------------------------------------ #

    def _generate_top_metadata(self, view_count: int, last_viewed_at: str,
                                tags: List[str]) -> str:
        """Generate the top metadata bar (views, last viewed, tag chips)."""
        parts = ['<div class="article-meta-info">']

        parts.append('<div class="meta-stats">')
        parts.append(f'<span class="meta-views">{view_count:,} views</span>')
        if last_viewed_at:
            parts.append('<span class="meta-separator">•</span>')
            parts.append(f'<span class="meta-last-viewed">Last viewed: {last_viewed_at}</span>')
        parts.append('</div>')

        if tags:
            parts.append('<div class="meta-tags">')
            for tag in tags:
                slug = tag.lower().replace(' ', '-')
                parts.append(f'<a href="/wiki/tag/{slug}" class="tag-chip">{tag}</a>')
            parts.append('</div>')

        parts.append('</div>')
        return '\n'.join(parts)

    # ------------------------------------------------------------------ #
    #  Line-by-line markdown conversion
    # ------------------------------------------------------------------ #

    def _convert_lines(self, lines: List[str]) -> str:
        """Convert lines of markdown to HTML body content."""
        parts = []
        i = 0
        in_tight_block = False  # inside [[[ ... ]]]

        while i < len(lines):
            line = lines[i].strip()

            # Tight list block delimiters
            if line == '[[[':
                in_tight_block = True
                i += 1
                continue
            if line == ']]]':
                in_tight_block = False
                if self.in_list:
                    parts.append('</ul>')
                    self.in_list = False
                if self.in_ordered_list:
                    parts.append('</ol>')
                    self.in_ordered_list = False
                i += 1
                continue

            # Empty line — close open list/table if not in tight block
            if not line:
                if not in_tight_block:
                    if self.in_list:
                        parts.append('</ul>')
                        self.in_list = False
                    if self.in_ordered_list:
                        parts.append('</ol>')
                        self.in_ordered_list = False
                i += 1
                continue

            # Horizontal rule
            if line == '---':
                self._close_list(parts)
                self._close_table(parts)
                parts.append('<hr class="section-divider">')
                i += 1
                continue

            # Headers
            if line.startswith('#'):
                self._close_list(parts)
                self._close_table(parts)
                parts.append(self._convert_header(line))
                i += 1
                continue

            # Images
            if line.startswith('!['):
                self._close_list(parts)
                image_html, _ = self._convert_image(line)
                parts.append(image_html)
                # Optional inline caption: /caption text/
                if i + 1 < len(lines):
                    nxt = lines[i + 1].strip()
                    if nxt.startswith('/') and nxt.endswith('/') and len(nxt) > 2:
                        caption = nxt[1:-1].strip()
                        parts.append(f'<p class="image-description">{caption}</p>')
                        i += 1
                i += 1
                continue

            # Bullet list items
            if line.startswith('- '):
                if self.in_ordered_list:
                    parts.append('</ol>')
                    self.in_ordered_list = False
                if not self.in_list:
                    cls = 'bullet-list tight' if in_tight_block else 'bullet-list'
                    parts.append(f'<ul class="{cls}">')
                    self.in_list = True
                parts.append(f'<li>{self._convert_inline(line[2:].strip())}</li>')
                i += 1
                continue

            # Numbered list items
            numbered = re.match(r'^(\d+)\.\s+(.+)$', line)
            if numbered:
                if self.in_list:
                    parts.append('</ul>')
                    self.in_list = False
                if not self.in_ordered_list:
                    cls = 'ordered-list tight' if in_tight_block else 'ordered-list'
                    parts.append(f'<ol class="{cls}">')
                    self.in_ordered_list = True
                parts.append(f'<li>{self._convert_inline(numbered.group(2).strip())}</li>')
                i += 1
                continue

            # Table rows
            if line.startswith('|') and '|' in line[1:]:
                if not self.in_table:
                    parts.append('<div class="table-wrapper"><table class="wiki-table">')
                    self.in_table = True

                is_header_row = (len(self.table_headers) == 0)
                row_html = self._convert_table_row(line, is_first=is_header_row)

                # Next line is a separator row → wrap previous as <thead>
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('|--'):
                    parts.append(f'<thead><tr>{row_html}</tr></thead><tbody>')
                    i += 2  # skip separator
                    continue
                else:
                    parts.append(f'<tr>{row_html}</tr>')
                    i += 1
                    continue
            else:
                self._close_table(parts)

            # Regular paragraph
            self._close_list(parts)
            parts.append(f'<p>{self._convert_inline(line)}</p>')
            i += 1

        # Close any still-open elements
        self._close_list(parts)
        self._close_table(parts)

        return '\n'.join(parts)

    # ------------------------------------------------------------------ #
    #  Element converters
    # ------------------------------------------------------------------ #

    def _close_list(self, parts: list) -> None:
        if self.in_list:
            parts.append('</ul>')
            self.in_list = False
        if self.in_ordered_list:
            parts.append('</ol>')
            self.in_ordered_list = False

    def _close_table(self, parts: list) -> None:
        if self.in_table:
            parts.append('</tbody></table></div>')
            self.in_table = False
            self.table_headers = []

    def _convert_header(self, line: str) -> str:
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if not match:
            return line
        level = len(match.group(1))
        text = self._convert_inline(match.group(2))
        plain = re.sub(r'<[^>]+>', '', text)
        hid = self._generate_header_id(plain)
        if level == 2 and 'Sources' in text:
            return f'<h{level} id="{hid}" class="sources-header">{text}</h{level}>'
        return f'<h{level} id="{hid}">{text}</h{level}>'

    def _convert_image(self, line: str) -> Tuple[str, Optional[str]]:
        match = re.match(r'!\[([^\]]+)\]\(([^\)]+)\)', line)
        if not match:
            return line, None
        alt_with_pos = match.group(1)
        url = match.group(2)
        if '|' in alt_with_pos:
            position, alt_text = alt_with_pos.split('|', 1)
            position = position.strip().lower()
            alt_text = alt_text.strip()
        else:
            position = 'center'
            alt_text = alt_with_pos.strip()
        if position not in ('left', 'right', 'center'):
            position = 'center'
        html = (f'<div class="image-container image-{position}">'
                f'<img src="{url}" alt="{alt_text}" loading="lazy" />'
                f'</div>')
        return html, alt_text

    def _convert_table_row(self, line: str, is_first: bool = False) -> str:
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if is_first:
            self.table_headers = cells
            return ''.join(f'<th>{self._convert_inline(c)}</th>' for c in cells)
        return ''.join(f'<td>{self._convert_inline(c)}</td>' for c in cells)

    def _convert_inline(self, text: str) -> str:
        """Convert inline v2 wiki syntax to HTML.

        Syntax reference:
          *bold text*           → <strong>
          /italic text/         → <em>
          [display|slug]        → internal wiki link  <a class="wiki-link">
          {display|url}         → external link       <a class="external-link">
        """
        # 1. Save external links {text|url} first — URLs may contain /  * [ chars
        saved: List[str] = []

        def save_ext(m):
            saved.append(f'<a href="{m.group(2)}" class="external-link">{m.group(1)}</a>')
            return f'__EXT_{len(saved) - 1}__'

        text = re.sub(r'\{([^|]+)\|([^}]+)\}', save_ext, text)

        # 2. Internal wiki links: [display text|slug]
        text = re.sub(
            r'\[([^|\]]+)\|([^\]]+)\]',
            lambda m: f'<a href="#{m.group(2)}" class="wiki-link">{m.group(1)}</a>',
            text,
        )

        # 3. Bold: *text*  (must come before italic so we don't double-process)
        text = re.sub(r'\*([^\*\n]+)\*', r'<strong>\1</strong>', text)

        # 4. Italic: /text/  (skip URLs — already saved above)
        text = re.sub(r'/([^/\n<>]+)/', r'<em>\1</em>', text)

        # 5. Restore external links
        for i, link_html in enumerate(saved):
            text = text.replace(f'__EXT_{i}__', link_html)

        return text

    # ------------------------------------------------------------------ #
    #  Discussion section (static scaffold, populated by JS)
    # ------------------------------------------------------------------ #

    def _generate_discussion_section(self) -> str:
        return '''
        <hr class="section-divider">

        <div class="discussion-section">
            <h2 class="discussion-header">Discussion</h2>
            <p class="discussion-intro">Share your thoughts, ask questions, or discuss this topic with the community.</p>

            <div class="comment-input-container">
                <div class="user-avatar" style="background: linear-gradient(135deg, #58cc02, #89e219);">
                    <span>You</span>
                </div>
                <div class="comment-input-wrapper">
                    <textarea
                        id="mainCommentInput"
                        class="comment-input"
                        placeholder="Share your thoughts or ask a question..."
                        rows="3"
                    ></textarea>
                    <button class="comment-submit-btn" onclick="addComment()">Post Comment</button>
                </div>
            </div>

            <div id="commentsContainer" class="comments-container"></div>
        </div>
        '''

    # ------------------------------------------------------------------ #
    #  Full HTML wrapper
    # ------------------------------------------------------------------ #

    def _wrap_in_html(self, top_meta_content: str, sidebar_content: str,
                      body_content: str) -> str:
        title = self.article_title or 'Medicalogy Medical Wiki'
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f7f7f7;
            --bg-card: #ffffff;
            --bg-hover: #f0f0f0;

            --accent-primary: #1cb0f6;
            --accent-primary-dark: #1899d6;
            --accent-primary-light: #84d8ff;

            --accent-success: #58cc02;
            --accent-success-dark: #46a302;
            --accent-success-bg: #d7ffb8;

            --accent-warning: #ff9600;
            --accent-warning-dark: #e68600;

            --accent-error: #ff4b4b;
            --accent-purple: #ce82ff;
            --accent-purple-dark: #9c52d0;

            --text-primary: #3c3c3c;
            --text-secondary: #777777;
            --text-muted: #afafaf;

            --border-color: #e5e5e5;
            --border-dark: #cecece;

            --border-radius: 16px;
            --border-radius-sm: 12px;
            --transition: all 0.2s ease;
            --sidebar-width: 280px;
            --navbar-height: 70px;

            --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
            --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
            --shadow-button: 0 4px 0 var(--border-dark);
        }}

        body {{
            font-family: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.7;
            overflow-x: hidden;
        }}

        /* ===== NAVBAR ===== */
        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--navbar-height);
            background: var(--bg-primary);
            border-bottom: 2px solid var(--border-color);
            display: flex;
            align-items: center;
            padding: 0 30px;
            z-index: 1000;
            box-shadow: var(--shadow-sm);
        }}

        .mobile-menu-btn {{
            display: none;
            width: 44px;
            height: 44px;
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
        }}

        .hamburger-icon {{
            width: 22px;
            height: 22px;
            stroke: var(--text-secondary);
            fill: none;
        }}

        .navbar-logo {{
            font-family: 'Nunito', sans-serif;
            font-size: 1.6rem;
            font-weight: 800;
            color: var(--accent-primary);
            text-decoration: none;
            margin-right: 40px;
            white-space: nowrap;
            letter-spacing: -0.5px;
        }}

        .navbar-search {{
            flex: 1;
            max-width: 500px;
            position: relative;
        }}

        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            width: 18px;
            height: 18px;
            stroke: var(--text-muted);
            fill: none;
            pointer-events: none;
        }}

        .search-input {{
            width: 100%;
            padding: 12px 20px 12px 44px;
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius);
            color: var(--text-primary);
            font-family: 'Nunito', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            transition: var(--transition);
        }}

        .search-input::placeholder {{ color: var(--text-muted); }}

        .search-input:focus {{
            outline: none;
            border-color: var(--accent-primary);
            background: var(--bg-primary);
            box-shadow: 0 0 0 4px rgba(28, 176, 246, 0.15);
        }}

        .navbar-actions {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-left: auto;
        }}

        .nav-streak-indicator {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 14px;
            background: var(--bg-primary);
            border: 2px solid var(--accent-warning);
            border-radius: var(--border-radius-sm);
        }}

        .nav-streak-icon {{
            width: 24px;
            height: 24px;
            fill: var(--accent-warning);
        }}

        .nav-streak-count {{
            font-weight: 800;
            color: var(--accent-warning-dark);
            font-size: 1rem;
        }}

        .nav-streak-label {{
            font-size: 0.85rem;
            color: var(--accent-warning-dark);
            font-weight: 600;
        }}

        .notification-btn {{
            position: relative;
            width: 44px;
            height: 44px;
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition);
        }}

        .notification-btn:hover {{
            background: var(--bg-hover);
            border-color: var(--border-dark);
        }}

        .notification-icon {{
            width: 22px;
            height: 22px;
            stroke: var(--text-secondary);
            fill: none;
        }}

        .notification-badge {{
            position: absolute;
            top: -6px;
            right: -6px;
            width: 22px;
            height: 22px;
            background: var(--accent-error);
            border-radius: 50%;
            border: 2px solid var(--bg-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 800;
            color: white;
        }}

        .account-menu {{ position: relative; }}

        .account-btn {{
            width: 44px;
            height: 44px;
            background: var(--accent-primary);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: white;
            font-size: 1rem;
            transition: var(--transition);
            box-shadow: 0 3px 0 var(--accent-primary-dark);
        }}

        .account-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 0 var(--accent-primary-dark);
        }}

        .account-btn:active {{
            transform: translateY(0);
            box-shadow: 0 1px 0 var(--accent-primary-dark);
        }}

        .account-dropdown {{
            position: absolute;
            top: calc(100% + 10px);
            right: 0;
            width: 200px;
            background: var(--bg-primary);
            border-radius: var(--border-radius-sm);
            box-shadow: var(--shadow-lg);
            border: 2px solid var(--border-color);
            overflow: hidden;
            display: none;
        }}

        .account-dropdown.active {{ display: block; }}

        .dropdown-item {{
            padding: 12px 16px;
            color: var(--text-secondary);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            transition: var(--transition);
            border-bottom: 2px solid var(--border-color);
            font-weight: 700;
            font-size: 0.95rem;
        }}

        .dropdown-item:last-child {{ border-bottom: none; }}
        .dropdown-item:hover {{ background: var(--bg-hover); color: var(--text-primary); }}

        .dropdown-icon {{
            width: 18px;
            height: 18px;
            stroke: currentColor;
            fill: none;
        }}

        /* ===== SIDEBAR ===== */
        .sidebar {{
            position: fixed;
            left: 0;
            top: var(--navbar-height);
            width: var(--sidebar-width);
            height: calc(100vh - var(--navbar-height));
            background: var(--bg-primary);
            border-right: 2px solid var(--border-color);
            overflow-y: auto;
            padding: 20px 0;
            z-index: 900;
        }}

        .sidebar::-webkit-scrollbar {{ width: 4px; }}
        .sidebar::-webkit-scrollbar-track {{ background: transparent; }}
        .sidebar::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 2px; }}

        .sidebar-section {{
            margin-bottom: 4px;
            padding: 0 16px;
        }}

        .sidebar-title {{
            font-size: 0.75rem;
            font-weight: 800;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
            margin-top: 16px;
            padding-left: 12px;
        }}

        .sidebar-nav {{ list-style: none; }}
        .nav-item {{ margin-bottom: 4px; }}

        .nav-link {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: var(--border-radius-sm);
            transition: var(--transition);
            font-weight: 700;
            border: 2px solid transparent;
            font-family: 'Nunito', sans-serif;
            font-size: 1rem;
            line-height: 1.7;
            background: none;
            width: 100%;
            text-align: left;
            cursor: pointer;
            box-sizing: border-box;
        }}

        .nav-link:hover {{ background: var(--bg-secondary); color: var(--text-primary); }}

        .nav-link.active {{
            background: rgba(28, 176, 246, 0.1);
            color: var(--accent-primary);
            border-color: var(--accent-primary);
        }}

        .nav-icon {{
            width: 24px;
            height: 24px;
            stroke: currentColor;
            fill: none;
            flex-shrink: 0;
        }}

        .nav-text {{ flex: 1; font-size: 1rem; }}

        .nav-link.has-submenu .nav-icon.chevron {{
            margin-left: auto;
            transition: transform 0.3s ease;
            flex-shrink: 0;
        }}

        .nav-link.has-submenu.expanded .nav-icon.chevron {{
            transform: rotate(180deg);
        }}

        .submenu {{
            list-style: none;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding-left: 52px;
            margin-top: -6px;
        }}

        .submenu.expanded {{ max-height: 500px; }}
        .submenu-item {{ margin-bottom: 0; }}

        .submenu-link {{
            display: block;
            padding: 4px 12px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: var(--border-radius-sm);
            font-size: 0.95rem;
            font-weight: 600;
            transition: var(--transition);
        }}

        .submenu-link:hover {{ background: var(--bg-secondary); color: var(--accent-primary); }}
        .submenu-link.active {{ color: var(--accent-primary); font-weight: 700; }}

        .sidebar-overlay {{
            display: none;
            position: fixed;
            top: var(--navbar-height);
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.4);
            z-index: 850;
        }}

        .sidebar-overlay.active {{ display: block; }}

        /* ===== MAIN WRAPPER ===== */
        .main-wrapper {{
            margin-left: var(--sidebar-width);
            margin-top: var(--navbar-height);
            min-height: calc(100vh - var(--navbar-height));
        }}

        /* ===== RESPONSIVE ===== */
        @media (max-width: 1100px) {{
            :root {{ --sidebar-width: 0px; }}

            .sidebar {{
                width: 280px;
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }}

            .sidebar.mobile-open {{ transform: translateX(0); }}
            .main-wrapper {{ margin-left: 0; }}
            .mobile-menu-btn {{ display: flex; }}
            .navbar-search {{ display: none; }}
        }}

        @media (max-width: 600px) {{
            .navbar {{ padding: 0 16px; }}
            .navbar-logo {{ font-size: 1.3rem; margin-right: 16px; }}
            .nav-streak-label {{ display: none; }}
        }}

        /* ===== ARTICLE CONTENT ===== */
        h1 {{
            font-family: 'Nunito', sans-serif;
            font-size: 2.8rem;
            font-weight: 800;
            color: var(--accent-primary);
            margin-bottom: 32px;
            letter-spacing: -1px;
            line-height: 1.2;
        }}

        h2 {{
            font-family: 'Nunito', sans-serif;
            font-size: 1.7rem;
            font-weight: 800;
            color: var(--text-primary);
            margin: 48px 0 24px;
            padding-left: 16px;
            border-left: 5px solid var(--accent-primary);
            letter-spacing: -0.3px;
        }}

        h2.sources-header {{
            color: var(--accent-success-dark);
            border-left-color: var(--accent-success);
        }}

        h2.discussion-header {{
            color: var(--accent-warning-dark);
            border-left-color: var(--accent-warning);
        }}

        h3 {{
            font-family: 'Nunito', sans-serif;
            font-size: 1.3rem;
            font-weight: 800;
            color: var(--accent-primary-dark);
            margin: 32px 0 16px;
        }}

        p {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-bottom: 18px;
            line-height: 1.8;
        }}

        strong {{ color: var(--text-primary); font-weight: 700; }}
        em {{ color: var(--text-primary); font-style: italic; }}
        a {{ text-decoration: none; transition: var(--transition); }}

        a.wiki-link {{
            color: var(--accent-primary);
            border-bottom: 2px dotted var(--accent-primary-light);
            font-weight: 600;
        }}

        a.wiki-link:hover {{
            color: var(--accent-primary-dark);
            border-bottom-style: solid;
        }}

        a.external-link {{ color: var(--accent-success); font-weight: 600; }}
        a.external-link:hover {{ color: var(--accent-success-dark); text-decoration: underline; }}

        .image-container {{
            margin: 32px 0;
            border-radius: var(--border-radius);
            overflow: hidden;
            box-shadow: var(--shadow-lg);
            border: 2px solid var(--border-color);
        }}

        .image-container img {{
            width: 100%;
            height: auto;
            display: block;
            transition: transform 0.3s ease;
        }}

        .image-container:hover img {{ transform: scale(1.02); }}

        .image-left {{ float: left; max-width: 45%; margin: 8px 24px 16px 0; }}
        .image-right {{ float: right; max-width: 45%; margin: 8px 0 16px 24px; }}
        .image-center {{ clear: both; max-width: 100%; margin: 40px auto; }}

        .image-description {{
            font-size: 0.95rem;
            color: var(--text-muted);
            font-style: italic;
            text-align: center;
            margin-top: -24px;
            margin-bottom: 32px;
        }}

        hr.section-divider {{
            border: none;
            height: 3px;
            background: var(--border-color);
            margin: 48px 0;
            border-radius: 2px;
            clear: both;
        }}

        ul.bullet-list {{
            list-style: none;
            padding-left: 0;
            margin: 20px 0;
            overflow: hidden;
        }}

        ul.bullet-list li {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            padding-left: 32px;
            margin-bottom: 12px;
            position: relative;
            line-height: 1.7;
        }}

        ul.bullet-list li::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 10px;
            width: 10px;
            height: 10px;
            background: var(--accent-primary);
            border-radius: 50%;
        }}

        ul.bullet-list.tight {{ margin: 12px 0; clear: both; }}
        ul.bullet-list.tight li {{ margin-bottom: 6px; line-height: 1.5; }}

        ol.ordered-list {{
            list-style: none;
            padding-left: 0;
            overflow: hidden;
            margin: 20px 0;
            counter-reset: item;
        }}

        ol.ordered-list li {{
            font-size: 1.1rem;
            color: var(--text-secondary);
            padding-left: 40px;
            margin-bottom: 12px;
            position: relative;
            line-height: 1.7;
            counter-increment: item;
        }}

        ol.ordered-list li::before {{
            content: counter(item);
            position: absolute;
            left: 0;
            top: 2px;
            width: 26px;
            height: 26px;
            background: var(--accent-primary);
            color: white;
            font-weight: 800;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
        }}

        ol.ordered-list.tight {{ margin: 12px 0; clear: both; }}
        ol.ordered-list.tight li {{ margin-bottom: 6px; line-height: 1.5; }}

        .table-wrapper {{
            overflow-x: auto;
            margin: 32px 0;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-md);
            border: 2px solid var(--border-color);
        }}

        .wiki-table {{ width: 100%; border-collapse: collapse; background: var(--bg-primary); }}
        .wiki-table thead {{ background: var(--accent-primary); }}

        .wiki-table th {{
            font-family: 'Nunito', sans-serif;
            font-size: 0.95rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 16px 20px;
            text-align: left;
            color: white;
        }}

        .wiki-table td {{
            font-size: 1rem;
            padding: 14px 20px;
            color: var(--text-secondary);
            border-bottom: 2px solid var(--border-color);
        }}

        .wiki-table tbody tr {{ transition: var(--transition); }}
        .wiki-table tbody tr:hover {{ background: rgba(28, 176, 246, 0.05); }}
        .wiki-table tbody tr:last-child td {{ border-bottom: none; }}

        /* ===== DISCUSSION ===== */
        .discussion-section {{
            margin-top: 64px;
            padding: 32px;
            background: var(--bg-primary);
            border-radius: var(--border-radius);
            border: 2px solid var(--border-color);
            box-shadow: var(--shadow-md);
        }}

        .discussion-intro {{ color: var(--text-muted); font-size: 1rem; margin-bottom: 24px; }}

        .user-avatar {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Nunito', sans-serif;
            font-weight: 800;
            font-size: 0.85rem;
            color: white;
            flex-shrink: 0;
        }}

        .comment-input-container {{ display: flex; gap: 16px; margin-bottom: 32px; }}
        .comment-input-wrapper {{ flex: 1; display: flex; flex-direction: column; gap: 12px; }}

        .comment-input {{
            width: 100%;
            padding: 14px 18px;
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            color: var(--text-primary);
            font-family: 'Nunito', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            resize: vertical;
            transition: var(--transition);
        }}

        .comment-input:focus {{
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 4px rgba(28, 176, 246, 0.15);
        }}

        .comment-submit-btn {{
            align-self: flex-end;
            padding: 12px 28px;
            background: var(--accent-success);
            border: none;
            border-radius: var(--border-radius-sm);
            color: white;
            font-family: 'Nunito', sans-serif;
            font-weight: 800;
            font-size: 0.95rem;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 4px 0 var(--accent-success-dark);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .comment-submit-btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 0 var(--accent-success-dark); }}
        .comment-submit-btn:active {{ transform: translateY(2px); box-shadow: 0 2px 0 var(--accent-success-dark); }}

        .comments-container {{ display: flex; flex-direction: column; gap: 16px; }}

        .comment-card {{
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: var(--border-radius);
            border: 2px solid var(--border-color);
            transition: var(--transition);
        }}

        .comment-card:hover {{ border-color: var(--accent-primary-light); }}

        .comment-header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }}
        .comment-author {{ font-family: 'Nunito', sans-serif; font-weight: 800; font-size: 1rem; color: var(--text-primary); }}
        .comment-time {{ color: var(--text-muted); font-size: 0.85rem; font-weight: 600; }}
        .comment-content {{ color: var(--text-secondary); font-size: 1rem; line-height: 1.7; margin-bottom: 14px; }}
        .comment-actions {{ display: flex; gap: 12px; align-items: center; }}

        .action-btn {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            color: var(--text-muted);
            font-family: 'Nunito', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            padding: 8px 12px;
            border-radius: var(--border-radius-sm);
        }}

        .action-btn:hover {{ background: var(--bg-hover); border-color: var(--border-dark); color: var(--text-primary); }}
        .action-btn.liked {{ background: rgba(28, 176, 246, 0.1); border-color: var(--accent-primary); color: var(--accent-primary); }}
        .action-btn.disliked {{ background: rgba(255, 75, 75, 0.1); border-color: var(--accent-error); color: var(--accent-error); }}
        .action-btn .icon {{ width: 18px; height: 18px; display: inline-block; }}
        .action-btn svg {{ width: 18px; height: 18px; fill: currentColor; transition: var(--transition); }}

        .replies-container {{
            margin-top: 16px;
            padding-left: 32px;
            border-left: 3px solid var(--accent-primary-light);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .reply-card {{
            background: var(--bg-primary);
            padding: 16px;
            border-radius: var(--border-radius-sm);
            border: 2px solid var(--border-color);
        }}

        .reply-input-container {{ display: flex; gap: 10px; margin-top: 12px; padding-left: 32px; }}

        .reply-input {{
            flex: 1;
            padding: 10px 14px;
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            color: var(--text-primary);
            font-family: 'Nunito', sans-serif;
            font-size: 0.95rem;
            font-weight: 600;
            transition: var(--transition);
        }}

        .reply-input:focus {{ outline: none; border-color: var(--accent-primary); }}

        .reply-submit-btn {{
            padding: 10px 18px;
            background: var(--accent-primary);
            border: none;
            border-radius: var(--border-radius-sm);
            color: white;
            font-family: 'Nunito', sans-serif;
            font-weight: 800;
            font-size: 0.85rem;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 3px 0 var(--accent-primary-dark);
        }}

        .reply-submit-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 0 var(--accent-primary-dark); }}

        /* ===== BACK TO TOP ===== */
        .back-to-top {{
            position: fixed;
            bottom: 32px;
            right: 32px;
            width: 56px;
            height: 56px;
            background: var(--accent-primary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 0 var(--accent-primary-dark), var(--shadow-lg);
            transition: var(--transition);
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
        }}

        .back-to-top.visible {{ opacity: 1; pointer-events: all; }}
        .back-to-top:hover {{ transform: translateY(-4px); box-shadow: 0 8px 0 var(--accent-primary-dark), var(--shadow-lg); }}
        .back-to-top:active {{ transform: translateY(0); box-shadow: 0 2px 0 var(--accent-primary-dark); }}
        .back-to-top::after {{ content: '↑'; font-size: 1.8rem; font-weight: 800; color: white; }}

        /* ===== RESPONSIVE (content) ===== */
        @media (max-width: 768px) {{
            h1 {{ font-size: 2rem; }}
            h2 {{ font-size: 1.4rem; }}
            h3 {{ font-size: 1.15rem; }}
            .image-left, .image-right {{ float: none; max-width: 100%; margin: 24px 0; }}
            .table-wrapper {{ margin: 24px -16px; border-radius: 0; }}
            .back-to-top {{ bottom: 20px; right: 20px; width: 48px; height: 48px; }}
            .discussion-section {{ padding: 20px; }}
            .comment-input-container, .reply-input-container {{ flex-direction: column; }}
            .comment-submit-btn, .reply-submit-btn {{ align-self: stretch; }}
            .replies-container {{ padding-left: 16px; }}
        }}

        .clearfix::after {{ content: ""; display: table; clear: both; }}

        /* ===== BOOKMARK ===== */
        .bookmark-container {{ display: flex; justify-content: flex-end; margin-bottom: 20px; }}

        .bookmark-btn {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            background: var(--bg-primary);
            border: 2px solid var(--accent-warning);
            border-radius: var(--border-radius-sm);
            color: var(--accent-warning);
            font-family: 'Nunito', sans-serif;
            font-weight: 800;
            font-size: 0.9rem;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 3px 0 var(--accent-warning-dark);
        }}

        .bookmark-btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 0 var(--accent-warning-dark); }}
        .bookmark-btn:active {{ transform: translateY(1px); box-shadow: 0 2px 0 var(--accent-warning-dark); }}
        .bookmark-btn.bookmarked {{ background: var(--accent-warning); color: white; }}
        .bookmark-icon {{ width: 20px; height: 20px; transition: var(--transition); }}
        .bookmark-btn.bookmarked .bookmark-icon {{ fill: white; }}
        .bookmark-text {{ text-transform: uppercase; letter-spacing: 0.5px; }}

        @keyframes bookmarkPulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.2); }}
            100% {{ transform: scale(1); }}
        }}

        .bookmark-btn.animate .bookmark-icon {{ animation: bookmarkPulse 0.3s ease-out; }}

        /* ===== TOP METADATA ===== */
        .article-meta-info {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px 20px;
            margin-bottom: 24px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border-color);
        }}

        .meta-stats {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .meta-separator {{ color: var(--accent-primary); font-weight: 800; }}
        .meta-views, .meta-last-viewed {{ color: var(--text-secondary); }}
        .meta-tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-left: auto; }}

        /* ===== PAGE LAYOUT ===== */
        .page-wrapper {{
            display: flex;
            gap: 32px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 32px 32px 100px;
            position: relative;
        }}

        .article-content {{
            flex: 1;
            min-width: 0;
            max-width: 900px;
            order: 1;
            background: var(--bg-primary);
            border-radius: var(--border-radius);
            border: 2px solid var(--border-color);
            padding: 32px 40px;
            box-shadow: var(--shadow-md);
        }}

        .article-sidebar {{
            width: 280px;
            flex-shrink: 0;
            position: sticky;
            top: calc(var(--navbar-height) + 24px);
            height: fit-content;
            max-height: calc(100vh - var(--navbar-height) - 48px);
            overflow-y: auto;
            order: 2;
        }}

        /* Article sidebar cards use different class names from left nav sidebar */
        .sidebar-section-card {{
            background: var(--bg-primary);
            border-radius: var(--border-radius);
            border: 2px solid var(--border-color);
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: var(--shadow-sm);
        }}

        .sidebar-card-title {{
            font-family: 'Nunito', sans-serif;
            font-size: 0.8rem;
            font-weight: 800;
            color: var(--accent-primary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 0 0 12px 0;
            padding: 0;
        }}

        .toc-nav {{ max-height: 350px; overflow-y: auto; }}
        .toc-list {{ list-style: none; padding: 0; margin: 0; }}
        .toc-item {{ margin-bottom: 4px; }}
        .toc-item:last-child {{ margin-bottom: 0; }}
        .toc-item.toc-h3 {{ padding-left: 16px; }}

        .toc-link {{
            display: block;
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
            padding: 6px 10px;
            border-radius: 8px;
            border-left: 3px solid transparent;
            transition: var(--transition);
            text-decoration: none;
        }}

        .toc-link:hover {{ color: var(--accent-primary); background: rgba(28, 176, 246, 0.1); border-left-color: var(--accent-primary); }}
        .toc-link.active {{ color: var(--accent-primary); background: rgba(28, 176, 246, 0.15); border-left-color: var(--accent-primary); font-weight: 700; }}

        .tag-chip {{
            display: inline-block;
            padding: 6px 12px;
            background: rgba(28, 176, 246, 0.1);
            border: 2px solid var(--accent-primary-light);
            border-radius: 20px;
            color: var(--accent-primary);
            font-family: 'Nunito', sans-serif;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: var(--transition);
            text-decoration: none;
        }}

        .tag-chip:hover {{ background: var(--accent-primary); border-color: var(--accent-primary); color: white; transform: translateY(-2px); }}

        .related-list {{ list-style: none; padding: 0; margin: 0; }}
        .related-item {{ margin-bottom: 8px; }}
        .related-item:last-child {{ margin-bottom: 0; }}

        .related-link {{
            display: block;
            padding: 12px 14px;
            background: var(--bg-secondary);
            border: 2px solid transparent;
            border-radius: var(--border-radius-sm);
            text-decoration: none;
            transition: var(--transition);
        }}

        .related-link:hover {{ background: rgba(88, 204, 2, 0.1); border-color: var(--accent-success); transform: translateX(4px); }}
        .related-title {{ display: block; color: var(--text-primary); font-size: 0.9rem; font-weight: 700; margin-bottom: 2px; }}
        .related-category {{ display: block; color: var(--accent-success); font-family: 'Nunito', sans-serif; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}

        .article-sidebar::-webkit-scrollbar {{ width: 6px; }}
        .article-sidebar::-webkit-scrollbar-track {{ background: transparent; }}
        .article-sidebar::-webkit-scrollbar-thumb {{ background: var(--border-color); border-radius: 3px; }}
        .article-sidebar::-webkit-scrollbar-thumb:hover {{ background: var(--accent-primary); }}
        .toc-nav::-webkit-scrollbar {{ width: 4px; }}
        .toc-nav::-webkit-scrollbar-track {{ background: transparent; }}
        .toc-nav::-webkit-scrollbar-thumb {{ background: var(--accent-primary-light); border-radius: 2px; }}

        @media (max-width: 1100px) {{
            .article-meta-info {{ flex-direction: column; align-items: flex-start; }}
            .meta-tags {{ margin-left: 0; }}
            .page-wrapper {{ flex-direction: column; padding: 16px 16px 80px; }}
            .article-content {{ padding: 24px 20px; }}
            .article-sidebar {{ width: 100%; position: relative; top: 0; max-height: none; order: -1; }}
            .toc-section {{ display: none; }}
        }}

        @media (max-width: 600px) {{
            .meta-stats {{ flex-direction: column; align-items: flex-start; gap: 5px; }}
            .meta-separator {{ display: none; }}
        }}
    </style>
</head>
<body>
    <!-- NAVIGATION BAR -->
    <nav class="navbar">
        <button class="mobile-menu-btn" onclick="toggleMobileSidebar()">
            <svg class="hamburger-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
        </button>

        <a href="/" class="navbar-logo">Medicalogy</a>

        <div class="navbar-actions">
            <div class="nav-streak-indicator">
                <svg class="nav-streak-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path d="M12 2c1.5 3 4 5 6 8-2-1-4 0-5 2 0 0 0-1-1-2-1-1-2-1-3 0 0-3-3-5-5-8 1 4 0 8-2 12-1 2-1 4 0 6 1 3 4 4 7 4 4 0 7-2 8-5 1-2 1-5-1-8-1-2-3-4-4-9z"/>
                </svg>
                <span class="nav-streak-count">7</span>
            </div>

            <button class="notification-btn">
                <svg class="notification-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                <span class="notification-badge">3</span>
            </button>

            <div class="account-menu">
                <button class="account-btn" onclick="toggleAccountMenu()">JD</button>
                <div class="account-dropdown" id="accountDropdown">
                    <a href="/settings" class="dropdown-item">
                        <svg class="dropdown-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="3"></circle>
                            <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path>
                        </svg>
                        <span>Settings</span>
                    </a>
                    <a href="/logout" class="dropdown-item">
                        <svg class="dropdown-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                            <polyline points="16 17 21 12 16 7"></polyline>
                            <line x1="21" y1="12" x2="9" y2="12"></line>
                        </svg>
                        <span>Log out</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <!-- SIDEBAR OVERLAY (Mobile) -->
    <div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleMobileSidebar()"></div>

    <!-- SIDEBAR -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-section">
            <ul class="sidebar-nav">
                <li class="nav-item">
                    <a href="/dashboard" class="nav-link">
                        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="3" width="7" height="7"></rect>
                            <rect x="14" y="3" width="7" height="7"></rect>
                            <rect x="14" y="14" width="7" height="7"></rect>
                            <rect x="3" y="14" width="7" height="7"></rect>
                        </svg>
                        <span class="nav-text">Dashboard</span>
                    </a>
                </li>
            </ul>
        </div>

        <div class="sidebar-section">
            <h3 class="sidebar-title">Learning</h3>
            <ul class="sidebar-nav">
                <li class="nav-item">
                    <a href="/themes" class="nav-link">
                        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                        </svg>
                        <span class="nav-text">Themes</span>
                    </a>
                </li>
                <li class="nav-item">
                    <button class="nav-link has-submenu expanded" onclick="toggleSubmenu(event, 'themesSubmenu')">
                        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
                            <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path>
                        </svg>
                        <span class="nav-text">Enrolled Themes</span>
                        <svg class="nav-icon chevron" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    </button>
                    <ul class="submenu expanded" id="themesSubmenu">
                        <li class="submenu-item"><a href="/emergency-care" class="submenu-link">Emergency Care</a></li>
                        <li class="submenu-item"><a href="/mental-health" class="submenu-link">Mental Health</a></li>
                        <li class="submenu-item"><a href="/nutrition" class="submenu-link">Nutrition</a></li>
                    </ul>
                </li>
            </ul>
        </div>

        <div class="sidebar-section">
            <h3 class="sidebar-title">Resources</h3>
            <ul class="sidebar-nav">
                <li class="nav-item">
                    <a href="/encyclopedia" class="nav-link active">
                        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                        </svg>
                        <span class="nav-text">Encyclopedia</span>
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/bookmarks" class="nav-link">
                        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                        </svg>
                        <span class="nav-text">Bookmarks</span>
                    </a>
                </li>
                <li class="nav-item">
                    <button class="nav-link has-submenu expanded" onclick="toggleSubmenu(event, 'recentSubmenu')">
                        <svg class="nav-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        <span class="nav-text">Recent Articles</span>
                        <svg class="nav-icon chevron" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    </button>
                    <ul class="submenu expanded" id="recentSubmenu">
                        <li class="submenu-item"><a href="/wiki/myocardial-infarction" class="submenu-link">Myocardial Infarction</a></li>
                        <li class="submenu-item"><a href="/wiki/stroke-recognition" class="submenu-link">Stroke Recognition</a></li>
                        <li class="submenu-item"><a href="/wiki/type-2-diabetes" class="submenu-link">Type 2 Diabetes</a></li>
                        <li class="submenu-item"><a href="/wiki/anxiety-overview" class="submenu-link">Anxiety Disorders</a></li>
                        <li class="submenu-item"><a href="/wiki/cpr-guide" class="submenu-link">CPR Guide</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </aside>

    <!-- MAIN CONTENT WRAPPER -->
    <div class="main-wrapper">
        <div class="page-wrapper">
            <main class="article-content clearfix">
                {top_meta_content}

                <!-- Bookmark Button -->
                <div class="bookmark-container">
                    <button class="bookmark-btn" id="bookmarkBtn" onclick="toggleBookmark()">
                        <svg class="bookmark-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                        </svg>
                        <span class="bookmark-text">Bookmark</span>
                    </button>
                </div>

                {body_content}
            </main>

            {sidebar_content}
        </div>
    </div>

    <div class="back-to-top" id="backToTop"></div>

    <script>
        // ---- Mobile sidebar ----
        function toggleMobileSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            sidebar.classList.toggle('mobile-open');
            overlay.classList.toggle('active');
        }}

        // ---- Account dropdown ----
        function toggleAccountMenu() {{
            document.getElementById('accountDropdown').classList.toggle('active');
        }}

        document.addEventListener('click', (e) => {{
            const menu = document.querySelector('.account-menu');
            const dropdown = document.getElementById('accountDropdown');
            if (menu && dropdown && !menu.contains(e.target)) {{
                dropdown.classList.remove('active');
            }}
        }});

        // ---- Enrolled Themes submenu ----
        function toggleSubmenu(event, submenuId) {{
            event.preventDefault();
            const link = event.currentTarget;
            const submenu = document.getElementById(submenuId);
            link.classList.toggle('expanded');
            submenu.classList.toggle('expanded');
        }}

        // ---- TOC active state ----
        document.addEventListener('DOMContentLoaded', () => {{
            const tocLinks = document.querySelectorAll('.toc-link');
            const headers = document.querySelectorAll('h2[id], h3[id]');

            if (tocLinks.length > 0 && headers.length > 0) {{
                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            tocLinks.forEach(l => l.classList.remove('active'));
                            const active = document.querySelector(`.toc-link[href="#${{entry.target.id}}"]`);
                            if (active) active.classList.add('active');
                        }}
                    }});
                }}, {{ rootMargin: '-20% 0% -80% 0%', threshold: 0 }});

                headers.forEach(h => observer.observe(h));
            }}

            renderComments();
            initBookmark();
        }});

        // ---- Discussion ----
        let comments = [
            {{
                id: 1,
                author: "Dr. Sarah Chen",
                avatar: "linear-gradient(135deg, #1cb0f6, #1899d6)",
                time: "2 hours ago",
                content: "Excellent comprehensive overview! I'd add that the 'golden hour' concept is crucial - every minute of delay increases mortality by 7-10%. Early recognition and calling 911 immediately cannot be overstated.",
                likes: 24, dislikes: 1, userVote: null,
                replies: [
                    {{ id: 101, author: "Medical Student Mike", avatar: "linear-gradient(135deg, #ff9600, #e68600)", time: "1 hour ago", content: "That's a great point Dr. Chen. In our recent simulation training, we practiced recognizing STEMI symptoms within 60 seconds. The time pressure really hits home.", likes: 8, dislikes: 0, userVote: null }},
                    {{ id: 102, author: "Emergency Nurse Amy", avatar: "linear-gradient(135deg, #ce82ff, #a855f7)", time: "45 minutes ago", content: "Absolutely! In the ER, we've seen outcomes dramatically improve when patients arrive within that first hour. Public education about symptoms is so important.", likes: 12, dislikes: 0, userVote: null }}
                ]
            }},
            {{
                id: 2,
                author: "James Rodriguez",
                avatar: "linear-gradient(135deg, #58cc02, #46a302)",
                time: "5 hours ago",
                content: "I survived a heart attack last year. The information here is spot-on. I experienced the 'atypical' symptoms - mainly extreme fatigue and jaw pain. Almost didn't call 911 because I thought it was just stress. Trust your gut and call for help!",
                likes: 45, dislikes: 0, userVote: null,
                replies: [
                    {{ id: 201, author: "Dr. Sarah Chen", avatar: "linear-gradient(135deg, #1cb0f6, #1899d6)", time: "4 hours ago", content: "Thank you for sharing your experience, James. Your story highlights why we need to educate people about atypical presentations, especially in certain demographics. I'm glad you're here to tell your story!", likes: 18, dislikes: 0, userVote: null }},
                    {{ id: 202, author: "Heart Health Advocate", avatar: "linear-gradient(135deg, #ff4b4b, #dc2626)", time: "3 hours ago", content: "Stories like yours save lives. Many people, especially women and diabetics, don't present with classic chest pain. Spreading awareness is crucial.", likes: 15, dislikes: 0, userVote: null }}
                ]
            }},
            {{
                id: 3,
                author: "Cardiologist Mark",
                avatar: "linear-gradient(135deg, #84d8ff, #1cb0f6)",
                time: "1 day ago",
                content: "One thing I'd emphasize: cardiac rehabilitation is not optional. Studies show it reduces 5-year mortality by 25-30%. Yet compliance rates are only around 30%. We need to do better educating patients about its importance.",
                likes: 31, dislikes: 2, userVote: null, replies: []
            }},
            {{
                id: 4,
                author: "Fitness Coach Lisa",
                avatar: "linear-gradient(135deg, #ff9600, #ff4b4b)",
                time: "1 day ago",
                content: "Question: The article mentions 150 minutes/week of moderate exercise. For someone recovering from an MI, how soon can they start exercising and how should they progress safely?",
                likes: 7, dislikes: 0, userVote: null,
                replies: [
                    {{ id: 401, author: "Cardiologist Mark", avatar: "linear-gradient(135deg, #84d8ff, #1cb0f6)", time: "1 day ago", content: "Great question! Typically, patients start gentle walking within days post-MI. A supervised cardiac rehab program usually begins 2-6 weeks after. They'll do stress testing to establish safe heart rate zones. Progress is gradual and monitored closely.", likes: 22, dislikes: 0, userVote: null }}
                ]
            }}
        ];

        let commentIdCounter = 5;
        let replyIdCounter = 500;

        function renderComments() {{
            const container = document.getElementById('commentsContainer');
            container.innerHTML = '';
            comments.forEach(c => container.appendChild(createCommentElement(c)));
        }}

        function createCommentElement(comment) {{
            const div = document.createElement('div');
            div.className = 'comment-card';
            div.dataset.commentId = comment.id;
            div.innerHTML = `
                <div class="comment-header">
                    <div class="user-avatar" style="background: ${{comment.avatar}};"><span>${{comment.author.charAt(0)}}</span></div>
                    <div>
                        <div class="comment-author">${{comment.author}}</div>
                        <div class="comment-time">${{comment.time}}</div>
                    </div>
                </div>
                <div class="comment-content">${{comment.content}}</div>
                <div class="comment-actions">
                    <button class="action-btn like-btn ${{comment.userVote === 'like' ? 'liked' : ''}}" onclick="voteComment(${{comment.id}}, 'like')">
                        <span class="icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg></span>
                        <span class="count">${{comment.likes}}</span>
                    </button>
                    <button class="action-btn dislike-btn ${{comment.userVote === 'dislike' ? 'disliked' : ''}}" onclick="voteComment(${{comment.id}}, 'dislike')">
                        <span class="icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path></svg></span>
                        <span class="count">${{comment.dislikes}}</span>
                    </button>
                    <button class="action-btn" onclick="toggleReplyInput(${{comment.id}})">
                        <span class="icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg></span>
                        <span>Reply (${{comment.replies.length}})</span>
                    </button>
                </div>
                <div id="replies-${{comment.id}}" class="replies-container" style="display: ${{comment.replies.length > 0 ? 'flex' : 'none'}};">
                    ${{comment.replies.map(r => createReplyHTML(r, comment.id)).join('')}}
                </div>
                <div id="reply-input-${{comment.id}}" class="reply-input-container" style="display: none;">
                    <div class="user-avatar" style="background: linear-gradient(135deg, #58cc02, #89e219);"><span>You</span></div>
                    <input type="text" class="reply-input" placeholder="Write a reply..." id="reply-text-${{comment.id}}">
                    <button class="reply-submit-btn" onclick="addReply(${{comment.id}})">Reply</button>
                </div>
            `;
            return div;
        }}

        function createReplyHTML(reply, parentId) {{
            return `
                <div class="reply-card" data-reply-id="${{reply.id}}">
                    <div class="comment-header">
                        <div class="user-avatar" style="background: ${{reply.avatar}};"><span>${{reply.author.charAt(0)}}</span></div>
                        <div>
                            <div class="comment-author">${{reply.author}}</div>
                            <div class="comment-time">${{reply.time}}</div>
                        </div>
                    </div>
                    <div class="comment-content">${{reply.content}}</div>
                    <div class="comment-actions">
                        <button class="action-btn like-btn ${{reply.userVote === 'like' ? 'liked' : ''}}" onclick="voteReply(${{parentId}}, ${{reply.id}}, 'like')">
                            <span class="icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg></span>
                            <span class="count">${{reply.likes}}</span>
                        </button>
                        <button class="action-btn dislike-btn ${{reply.userVote === 'dislike' ? 'disliked' : ''}}" onclick="voteReply(${{parentId}}, ${{reply.id}}, 'dislike')">
                            <span class="icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path></svg></span>
                            <span class="count">${{reply.dislikes}}</span>
                        </button>
                    </div>
                </div>
            `;
        }}

        function addComment() {{
            const input = document.getElementById('mainCommentInput');
            const content = input.value.trim();
            if (!content) {{ alert('Please write a comment first!'); return; }}
            comments.unshift({{ id: commentIdCounter++, author: "You", avatar: "linear-gradient(135deg, #58cc02, #89e219)", time: "Just now", content, likes: 0, dislikes: 0, userVote: null, replies: [] }});
            input.value = '';
            renderComments();
        }}

        function addReply(commentId) {{
            const input = document.getElementById(`reply-text-${{commentId}}`);
            const content = input.value.trim();
            if (!content) {{ alert('Please write a reply first!'); return; }}
            const comment = comments.find(c => c.id === commentId);
            if (!comment) return;
            comment.replies.push({{ id: replyIdCounter++, author: "You", avatar: "linear-gradient(135deg, #58cc02, #89e219)", time: "Just now", content, likes: 0, dislikes: 0, userVote: null }});
            input.value = '';
            renderComments();
            document.getElementById(`replies-${{commentId}}`).style.display = 'flex';
        }}

        function toggleReplyInput(commentId) {{
            const el = document.getElementById(`reply-input-${{commentId}}`);
            const visible = el.style.display !== 'none';
            el.style.display = visible ? 'none' : 'flex';
            if (!visible) document.getElementById(`reply-text-${{commentId}}`).focus();
        }}

        function voteComment(commentId, voteType) {{
            const comment = comments.find(c => c.id === commentId);
            if (!comment) return;
            if (comment.userVote === voteType) {{
                comment[voteType === 'like' ? 'likes' : 'dislikes']--;
                comment.userVote = null;
            }} else {{
                if (comment.userVote === 'like') comment.likes--;
                else if (comment.userVote === 'dislike') comment.dislikes--;
                comment[voteType === 'like' ? 'likes' : 'dislikes']++;
                comment.userVote = voteType;
            }}
            renderComments();
        }}

        function voteReply(commentId, replyId, voteType) {{
            const comment = comments.find(c => c.id === commentId);
            if (!comment) return;
            const reply = comment.replies.find(r => r.id === replyId);
            if (!reply) return;
            if (reply.userVote === voteType) {{
                reply[voteType === 'like' ? 'likes' : 'dislikes']--;
                reply.userVote = null;
            }} else {{
                if (reply.userVote === 'like') reply.likes--;
                else if (reply.userVote === 'dislike') reply.dislikes--;
                reply[voteType === 'like' ? 'likes' : 'dislikes']++;
                reply.userVote = voteType;
            }}
            renderComments();
        }}

        // ---- Back to top ----
        const backToTop = document.getElementById('backToTop');
        window.addEventListener('scroll', () => backToTop.classList.toggle('visible', window.scrollY > 300));
        backToTop.addEventListener('click', () => window.scrollTo({{ top: 0, behavior: 'smooth' }}));

        // ---- Smooth anchor scroll ----
        document.querySelectorAll('a[href^="#"]').forEach(a => {{
            a.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }});
        }});

        // ---- Ctrl+Enter to post comment ----
        document.getElementById('mainCommentInput').addEventListener('keydown', e => {{
            if (e.key === 'Enter' && e.ctrlKey) addComment();
        }});

        // ---- Bookmark ----
        const BOOKMARK_KEY = 'medicalogy_bookmarked_' + window.location.pathname;

        function initBookmark() {{
            const btn = document.getElementById('bookmarkBtn');
            if (localStorage.getItem(BOOKMARK_KEY) === 'true') {{
                btn.classList.add('bookmarked');
                btn.querySelector('.bookmark-text').textContent = 'Bookmarked';
            }}
        }}

        function toggleBookmark() {{
            const btn = document.getElementById('bookmarkBtn');
            const bookmarked = btn.classList.contains('bookmarked');
            btn.classList.add('animate');
            setTimeout(() => btn.classList.remove('animate'), 300);
            if (bookmarked) {{
                btn.classList.remove('bookmarked');
                btn.querySelector('.bookmark-text').textContent = 'Bookmark';
                localStorage.removeItem(BOOKMARK_KEY);
                showBookmarkNotification('Bookmark removed');
            }} else {{
                btn.classList.add('bookmarked');
                btn.querySelector('.bookmark-text').textContent = 'Bookmarked';
                localStorage.setItem(BOOKMARK_KEY, 'true');
                showBookmarkNotification('Page bookmarked!');
            }}
        }}

        function showBookmarkNotification(message) {{
            const existing = document.querySelector('.bookmark-notification');
            if (existing) existing.remove();
            const n = document.createElement('div');
            n.className = 'bookmark-notification';
            n.textContent = message;
            n.style.cssText = `position:fixed;top:90px;left:50%;transform:translateX(-50%) translateY(-100px);background:var(--accent-success);color:white;padding:14px 28px;border-radius:var(--border-radius-sm);font-family:'Nunito',sans-serif;font-weight:800;font-size:0.95rem;z-index:10000;box-shadow:0 4px 0 var(--accent-success-dark);transition:transform 0.4s cubic-bezier(0.4,0,0.2,1);`;
            document.body.appendChild(n);
            requestAnimationFrame(() => {{ n.style.transform = 'translateX(-50%) translateY(0)'; }});
            setTimeout(() => {{
                n.style.transform = 'translateX(-50%) translateY(-100px)';
                setTimeout(() => n.remove(), 400);
            }}, 2000);
        }}
    </script>
</body>
</html>"""


# ------------------------------------------------------------------ #
#  File-level helpers
# ------------------------------------------------------------------ #

def convert_file(input_path: str, output_path: str,
                 view_count: int = 0,
                 last_viewed_at: str = "",
                 tags: list = None,
                 related_articles: list = None) -> None:
    """
    Convert a Medicalogy markdown file to HTML.

    Args:
        input_path: Path to input .md file
        output_path: Path to output .html file
        view_count: Number of views for the article
        last_viewed_at: Formatted datetime string
        tags: List of tag strings
        related_articles: List of dicts with 'title', 'slug', 'category'
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    converter = MedicalogyMarkdownConverter()
    html_content = converter.convert(
        markdown_content,
        view_count=view_count,
        last_viewed_at=last_viewed_at,
        tags=tags or [],
        related_articles=related_articles or [],
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Converted {input_path} → {output_path}")


def main():
    """Main entry point with hardcoded paths and sample metadata."""
    input_path = r'medicalogy_docs\screens\6-infographic\markdown.md'
    output_path = r'medicalogy_docs\screens\6-infographic\demo.html'

    sample_tags = [
        "Cardiology",
        "Emergency Medicine",
        "Heart Disease",
        "First Aid",
        "Cardiovascular",
    ]

    sample_related_articles = [
        {"title": "Coronary Artery Disease",       "slug": "coronary-artery-disease",       "category": "Cardiology"},
        {"title": "Cardiac Arrest vs Heart Attack", "slug": "cardiac-arrest-vs-heart-attack", "category": "Emergency Medicine"},
        {"title": "Blood Pressure Management",      "slug": "blood-pressure-management",      "category": "Cardiovascular Health"},
        {"title": "Atherosclerosis",                "slug": "atherosclerosis",                "category": "Cardiology"},
        {"title": "CPR Basics",                     "slug": "cpr-basics",                     "category": "First Aid"},
    ]

    convert_file(
        input_path,
        output_path,
        view_count=12847,
        last_viewed_at="2 minutes ago",
        tags=sample_tags,
        related_articles=sample_related_articles,
    )


if __name__ == "__main__":
    main()