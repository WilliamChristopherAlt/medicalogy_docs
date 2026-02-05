"""
BioBasics Medical Wiki Markdown to HTML Converter
Converts custom medical markdown format to styled HTML pages with interactive discussion section
"""

import re
from typing import List, Tuple, Optional, Dict


class BioBasicsMarkdownConverter:
    """
    Converts BioBasics custom markdown to HTML with medical wiki styling.
    
    Supported syntax:
    - Headers: # H1, ## H2, ### H3
    - Bold: **text**
    - Italic: *text*
    - Wiki links (internal): [[term]] - creates internal page links
    - External links: [text](url) - creates external links
    - Images: ![position|alt text](url) where position is left, right, or center
    - Image descriptions: *description text* immediately after image
    - Horizontal rules: ---
    - Bullet lists: - item
    - Tables: | Header | Header |
    - Sources section (special formatting)
    - Discussion section with comments, replies, likes/dislikes (auto-added)
    - Table of contents (auto-generated from headers)
    - Article metadata (view count, last viewed, tags, related articles)
    """
    
    def __init__(self):
        self.in_table = False
        self.in_list = False
        self.table_headers = []
        self.toc_entries: List[Dict] = []  # Stores {level, text, id} for TOC
        self.article_title = ""
        
    def convert(self, markdown_text: str, 
                view_count: int = 0,
                last_viewed_at: str = "",
                tags: List[str] = None,
                related_articles: List[Dict] = None) -> str:
        """
        Convert markdown text to complete HTML document.
        
        Args:
            markdown_text: The markdown content
            view_count: Number of times article has been viewed
            last_viewed_at: Formatted datetime string of last view
            tags: List of tag names
            related_articles: List of dicts with 'title', 'slug', 'category' keys
        """
        if tags is None:
            tags = []
        if related_articles is None:
            related_articles = []
            
        # Reset state
        self.toc_entries = []
        self.article_title = ""
        
        lines = markdown_text.strip().split('\n')
        
        # First pass: extract headers for TOC
        self._extract_toc(lines)
        
        # Second pass: convert content
        body_html = self._convert_lines(lines)
        
        # Generate top metadata bar (view count, last viewed, tags)
        top_meta_html = self._generate_top_metadata(view_count, last_viewed_at, tags)
        
        # Generate sidebar content (TOC + related articles only)
        sidebar_html = self._generate_sidebar(related_articles)
        
        # Add discussion section after the main content
        discussion_html = self._generate_discussion_section()
        
        return self._wrap_in_html(top_meta_html, sidebar_html, body_html + discussion_html)
    
    def _extract_toc(self, lines: List[str]) -> None:
        """Extract headers from markdown for table of contents."""
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                match = re.match(r'^(#{1,6})\s+(.+)$', line)
                if match:
                    level = len(match.group(1))
                    text = match.group(2)
                    # Remove inline formatting for TOC text
                    clean_text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
                    clean_text = re.sub(r'\*([^\*]+)\*', r'\1', clean_text)
                    clean_text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', clean_text)
                    clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_text)
                    
                    # Generate ID from text
                    header_id = self._generate_header_id(clean_text)
                    
                    # Store title for h1
                    if level == 1 and not self.article_title:
                        self.article_title = clean_text
                    
                    # Only include h2 and h3 in TOC (skip h1 title and Sources)
                    if level in [2, 3] and 'Sources' not in clean_text:
                        self.toc_entries.append({
                            'level': level,
                            'text': clean_text,
                            'id': header_id
                        })
    
    def _generate_header_id(self, text: str) -> str:
        """Generate a URL-safe ID from header text."""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        header_id = text.lower()
        header_id = re.sub(r'[^\w\s-]', '', header_id)
        header_id = re.sub(r'\s+', '-', header_id)
        return header_id
    
    def _generate_sidebar(self, related_articles: List[Dict]) -> str:
        """Generate the sidebar with TOC and related articles."""
        html_parts = []
        
        html_parts.append('<aside class="article-sidebar">')
        
        # Table of Contents
        if self.toc_entries:
            html_parts.append('<div class="sidebar-section toc-section">')
            html_parts.append('<h3 class="sidebar-title">Table of Contents</h3>')
            html_parts.append('<nav class="toc-nav">')
            html_parts.append('<ul class="toc-list">')
            
            for entry in self.toc_entries:
                indent_class = 'toc-h3' if entry['level'] == 3 else 'toc-h2'
                html_parts.append(f'<li class="toc-item {indent_class}">')
                html_parts.append(f'<a href="#{entry["id"]}" class="toc-link">{entry["text"]}</a>')
                html_parts.append('</li>')
            
            html_parts.append('</ul>')
            html_parts.append('</nav>')
            html_parts.append('</div>')
        
        # Related Articles
        if related_articles:
            html_parts.append('<div class="sidebar-section related-section">')
            html_parts.append('<h3 class="sidebar-title">Related Articles</h3>')
            html_parts.append('<ul class="related-list">')
            for article in related_articles:
                html_parts.append('<li class="related-item">')
                html_parts.append(f'<a href="/wiki/{article.get("slug", "")}" class="related-link">')
                html_parts.append(f'<span class="related-title">{article.get("title", "")}</span>')
                if article.get('category'):
                    html_parts.append(f'<span class="related-category">{article["category"]}</span>')
                html_parts.append('</a>')
                html_parts.append('</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        html_parts.append('</aside>')
        
        return '\n'.join(html_parts)
    
    def _generate_top_metadata(self, view_count: int, last_viewed_at: str, tags: List[str]) -> str:
        """Generate the top metadata section with view count, last viewed, and tags."""
        html_parts = []
        
        html_parts.append('<div class="article-meta-info">')
        
        # View stats (italic)
        html_parts.append('<div class="meta-stats">')
        html_parts.append(f'<span class="meta-views">{view_count:,} views</span>')
        if last_viewed_at:
            html_parts.append('<span class="meta-separator">•</span>')
            html_parts.append(f'<span class="meta-last-viewed">Last viewed: {last_viewed_at}</span>')
        html_parts.append('</div>')
        
        # Tags
        if tags:
            html_parts.append('<div class="meta-tags">')
            for tag in tags:
                html_parts.append(f'<a href="/wiki/tag/{tag.lower().replace(" ", "-")}" class="tag-chip">{tag}</a>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _convert_lines(self, lines: List[str]) -> str:
        """Convert lines of markdown to HTML body content."""
        html_parts = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines unless closing a list
            if not line:
                if self.in_list:
                    html_parts.append('</ul>')
                    self.in_list = False
                i += 1
                continue
            
            # Check for horizontal rule
            if line == '---':
                if self.in_list:
                    html_parts.append('</ul>')
                    self.in_list = False
                if self.in_table:
                    html_parts.append('</tbody></table></div>')
                    self.in_table = False
                    self.table_headers = []
                html_parts.append('<hr class="section-divider">')
                i += 1
                continue
            
            # Check for headers
            if line.startswith('#'):
                if self.in_list:
                    html_parts.append('</ul>')
                    self.in_list = False
                if self.in_table:
                    html_parts.append('</table>')
                    self.in_table = False
                    
                header_html = self._convert_header(line)
                html_parts.append(header_html)
                i += 1
                continue
            
            # Check for images
            if line.startswith('!['):
                if self.in_list:
                    html_parts.append('</ul>')
                    self.in_list = False
                    
                image_html, description = self._convert_image(line)
                html_parts.append(image_html)
                
                # Check next line for description (italic text)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('*') and not next_line.startswith('**'):
                        desc_text = next_line.strip('*').strip()
                        html_parts.append(f'<p class="image-description">{desc_text}</p>')
                        i += 1  # Skip description line
                
                i += 1
                continue
            
            # Check for bullet lists
            if line.startswith('- '):
                if not self.in_list:
                    html_parts.append('<ul class="bullet-list">')
                    self.in_list = True
                
                list_item = self._convert_inline(line[2:].strip())
                html_parts.append(f'<li>{list_item}</li>')
                i += 1
                continue
            
            # Check for tables
            if line.startswith('|') and '|' in line[1:]:
                if not self.in_table:
                    html_parts.append('<div class="table-wrapper"><table class="wiki-table">')
                    self.in_table = True
                
                table_row = self._convert_table_row(line, is_first=(len(self.table_headers) == 0))
                
                # Check if next line is separator (header row)
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('|--'):
                    html_parts.append(f'<thead><tr>{table_row}</tr></thead><tbody>')
                    i += 2  # Skip separator line
                    continue
                else:
                    html_parts.append(f'<tr>{table_row}</tr>')
                    i += 1
                    continue
            else:
                # Close table if we were in one
                if self.in_table:
                    html_parts.append('</tbody></table></div>')
                    self.in_table = False
                    self.table_headers = []
            
            # Regular paragraph
            if self.in_list:
                html_parts.append('</ul>')
                self.in_list = False
                
            paragraph_html = self._convert_paragraph(line)
            html_parts.append(paragraph_html)
            i += 1
        
        # Close any open elements
        if self.in_list:
            html_parts.append('</ul>')
        if self.in_table:
            html_parts.append('</tbody></table></div>')
        
        return '\n'.join(html_parts)
    
    def _convert_header(self, line: str) -> str:
        """Convert header markdown to HTML with ID for TOC linking."""
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = self._convert_inline(match.group(2))
            
            # Generate ID from plain text (without inline formatting)
            plain_text = re.sub(r'<[^>]+>', '', text)
            header_id = self._generate_header_id(plain_text)
            
            # Special styling for Sources header
            if level == 2 and 'Sources' in text:
                return f'<h{level} id="{header_id}" class="sources-header">{text}</h{level}>'
            
            return f'<h{level} id="{header_id}">{text}</h{level}>'
        return line
    
    def _convert_image(self, line: str) -> Tuple[str, Optional[str]]:
        """Convert image markdown to HTML with positioning."""
        # Pattern: ![position|alt](url)
        match = re.match(r'!\[([^\]]+)\]\(([^\)]+)\)', line)
        if match:
            alt_with_pos = match.group(1)
            url = match.group(2)
            
            # Split position and alt text
            if '|' in alt_with_pos:
                position, alt_text = alt_with_pos.split('|', 1)
                position = position.strip().lower()
                alt_text = alt_text.strip()
            else:
                position = 'center'
                alt_text = alt_with_pos.strip()
            
            # Validate position
            if position not in ['left', 'right', 'center']:
                position = 'center'
            
            html = f'<div class="image-container image-{position}">'
            html += f'<img src="{url}" alt="{alt_text}" loading="lazy" />'
            html += '</div>'
            
            return html, alt_text
        
        return line, None
    
    def _convert_table_row(self, line: str, is_first: bool = False) -> str:
        """Convert table row markdown to HTML."""
        cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove first and last empty
        
        if is_first:
            self.table_headers = cells
            return ''.join(f'<th>{self._convert_inline(cell)}</th>' for cell in cells)
        else:
            return ''.join(f'<td>{self._convert_inline(cell)}</td>' for cell in cells)
    
    def _convert_paragraph(self, line: str) -> str:
        """Convert paragraph with inline formatting."""
        converted = self._convert_inline(line)
        return f'<p>{converted}</p>'
    
    def _convert_inline(self, text: str) -> str:
        """Convert inline markdown (bold, italic, links) to HTML."""
        # Convert internal wiki links first: [[term]]
        text = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="#\1" class="wiki-link">\1</a>', text)
        
        # Convert external links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2" class="external-link" target="_blank" rel="noopener">\1</a>', text)
        
        # Convert bold: **text**
        text = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', text)
        
        # Convert italic: *text* (but not already processed)
        text = re.sub(r'(?<!\*)\*(?!\*)([^\*]+)\*(?!\*)', r'<em>\1</em>', text)
        
        return text
    
    def _generate_discussion_section(self) -> str:
        """Generate the discussion/comments section with dummy data."""
        return '''
        <hr class="section-divider">
        
        <div class="discussion-section">
            <h2 class="discussion-header">Discussion</h2>
            <p class="discussion-intro">Share your thoughts, ask questions, or discuss this topic with the community.</p>
            
            <!-- Comment Input Area -->
            <div class="comment-input-container">
                <div class="user-avatar" style="background: linear-gradient(135deg, #ff6b9d, #ffd93d);">
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
            
            <!-- Comments Container -->
            <div id="commentsContainer" class="comments-container">
                <!-- Comments will be dynamically added here -->
            </div>
        </div>
        '''
    
    def _wrap_in_html(self, top_meta_content: str, sidebar_content: str, body_content: str) -> str:
        """Wrap content in complete HTML document with BioBasics styling and discussion functionality."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.article_title or 'BioBasics Medical Wiki'}</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Crimson+Pro:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #0a0e27;
            --bg-secondary: #1a1f3a;
            --bg-card: #252d4a;
            --accent-primary: #00f5d0;
            --accent-secondary: #ff6b9d;
            --accent-tertiary: #ffd93d;
            --text-primary: #ffffff;
            --text-secondary: #b8c5d6;
            --text-muted: #6b7a94;
            --border-radius: 24px;
            --transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            --global-sidebar-width: 280px;
            --navbar-height: 70px;
        }}

        body {{
            font-family: 'Crimson Pro', serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.8;
            overflow-x: hidden;
            position: relative;
        }}

        body::before {{
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: 
                radial-gradient(circle at 20% 30%, rgba(0, 245, 208, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(255, 107, 157, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(255, 217, 61, 0.05) 0%, transparent 50%);
            animation: pulse 20s ease-in-out infinite;
            z-index: 0;
            pointer-events: none;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: translate(0, 0) scale(1); }}
            50% {{ transform: translate(-5%, 5%) scale(1.1); }}
        }}

        /* ===== GLOBAL NAVIGATION BAR ===== */
        .global-navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--navbar-height);
            background: rgba(26, 31, 58, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0, 245, 208, 0.1);
            display: flex;
            align-items: center;
            padding: 0 30px;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}

        .global-navbar-logo {{
            font-family: 'Space Mono', monospace;
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
            margin-right: 40px;
            white-space: nowrap;
        }}

        .global-navbar-search {{
            flex: 1;
            max-width: 500px;
            position: relative;
        }}

        .global-search-input {{
            width: 100%;
            padding: 12px 15px 12px 45px;
            background: var(--bg-card);
            border: 2px solid transparent;
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'Crimson Pro', serif;
            font-size: 0.95rem;
            transition: var(--transition);
        }}

        .global-search-input:focus {{
            outline: none;
            border-color: var(--accent-primary);
            background: var(--bg-primary);
        }}

        .global-navbar-actions {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-left: auto;
        }}

        .global-streak-indicator {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--bg-card);
            border-radius: 10px;
            border: 1px solid rgba(255, 217, 61, 0.3);
        }}

        .global-streak-icon {{
            width: 24px;
            height: 24px;
            fill: var(--accent-tertiary);
        }}

        .global-streak-count {{
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            color: var(--accent-tertiary);
            font-size: 0.9rem;
        }}

        .global-notification-btn {{
            position: relative;
            width: 40px;
            height: 40px;
            background: var(--bg-card);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition);
        }}

        .global-notification-btn:hover {{
            background: rgba(0, 245, 208, 0.1);
        }}

        .global-notification-icon {{
            width: 22px;
            height: 22px;
            fill: var(--text-secondary);
        }}

        .global-notification-badge {{
            position: absolute;
            top: -4px;
            right: -4px;
            width: 20px;
            height: 20px;
            background: var(--accent-secondary);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Space Mono', monospace;
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--bg-primary);
        }}

        .global-account-btn {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            color: var(--bg-primary);
            font-size: 0.9rem;
            transition: var(--transition);
        }}

        .global-account-btn:hover {{
            transform: scale(1.1);
            box-shadow: 0 5px 20px rgba(0, 245, 208, 0.3);
        }}

        /* ===== GLOBAL SIDEBAR ===== */
        .global-sidebar {{
            position: fixed;
            left: 0;
            top: var(--navbar-height);
            width: var(--global-sidebar-width);
            height: calc(100vh - var(--navbar-height));
            background: rgba(26, 31, 58, 0.8);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(0, 245, 208, 0.1);
            overflow-y: auto;
            padding: 20px 0;
            z-index: 900;
        }}

        .global-sidebar-section {{
            margin-bottom: 30px;
            padding: 0 20px;
        }}

        .global-sidebar-title {{
            font-family: 'Space Mono', monospace;
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
            padding-left: 10px;
        }}

        .global-sidebar-nav {{
            list-style: none;
        }}

        .global-nav-item {{
            margin-bottom: 4px;
        }}

        .global-nav-link {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 15px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 10px;
            transition: var(--transition);
            position: relative;
        }}

        .global-nav-link:hover {{
            background: rgba(0, 245, 208, 0.1);
            color: var(--text-primary);
        }}

        .global-nav-link.active {{
            background: rgba(0, 245, 208, 0.15);
            color: var(--accent-primary);
            font-weight: 600;
        }}

        .global-nav-icon {{
            width: 20px;
            height: 20px;
            fill: currentColor;
            flex-shrink: 0;
        }}

        .global-nav-text {{
            flex: 1;
            font-size: 0.95rem;
        }}

        .global-submenu {{
            list-style: none;
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            margin-left: 32px;
            margin-top: 4px;
        }}

        .global-submenu.expanded {{
            max-height: 500px;
        }}

        .global-submenu-link {{
            display: block;
            padding: 8px 15px;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: var(--transition);
        }}

        .global-submenu-link:hover {{
            background: rgba(255, 107, 157, 0.1);
            color: var(--text-primary);
        }}

        /* ===== MAIN CONTENT WRAPPER ===== */
        .main-content-wrapper {{
            margin-left: var(--global-sidebar-width);
            margin-top: var(--navbar-height);
            min-height: calc(100vh - var(--navbar-height));
            position: relative;
            z-index: 1;
        }}

        .global-mobile-menu-btn {{
            display: none;
        }}

        @media (max-width: 1100px) {{
            :root {{
                --global-sidebar-width: 0px;
            }}

            .global-sidebar {{
                width: 280px;
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }}

            .global-sidebar.mobile-open {{
                transform: translateX(0);
            }}

            .main-content-wrapper {{
                margin-left: 0;
            }}

            .global-navbar {{
                padding: 0 15px;
            }}

            .global-navbar-search {{
                display: none;
            }}

            .global-mobile-menu-btn {{
                display: flex;
                width: 40px;
                height: 40px;
                background: var(--bg-card);
                border: none;
                border-radius: 10px;
                cursor: pointer;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
            }}
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 60px 40px 100px;
            position: relative;
            z-index: 1;
        }}

        /* Headers */
        h1 {{
            font-family: 'Space Mono', monospace;
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 40px;
            letter-spacing: -2px;
            animation: fadeInDown 0.8s ease-out;
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        h2 {{
            font-family: 'Space Mono', monospace;
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent-primary);
            margin: 50px 0 25px;
            padding-left: 20px;
            border-left: 4px solid var(--accent-primary);
            letter-spacing: 0.5px;
            animation: fadeIn 0.6s ease-out;
        }}

        h2.sources-header {{
            color: var(--accent-secondary);
            border-left-color: var(--accent-secondary);
        }}

        h2.discussion-header {{
            color: var(--accent-tertiary);
            border-left-color: var(--accent-tertiary);
        }}

        h3 {{
            font-family: 'Space Mono', monospace;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--accent-tertiary);
            margin: 35px 0 20px;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Paragraphs */
        p {{
            font-size: 1.15rem;
            color: var(--text-secondary);
            margin-bottom: 20px;
            line-height: 1.9;
        }}

        /* Inline formatting */
        strong {{
            color: var(--text-primary);
            font-weight: 700;
        }}

        em {{
            color: var(--accent-tertiary);
            font-style: italic;
        }}

        a {{
            text-decoration: none;
            border-bottom: 2px solid transparent;
            transition: var(--transition);
        }}

        a.wiki-link {{
            color: var(--accent-tertiary);
            border-bottom: 1px dotted var(--accent-tertiary);
        }}

        a.wiki-link:hover {{
            color: var(--accent-primary);
            border-bottom-color: var(--accent-primary);
        }}

        a.external-link {{
            color: var(--accent-primary);
        }}

        a.external-link:hover {{
            border-bottom-color: var(--accent-primary);
            color: var(--accent-secondary);
        }}

        /* Images */
        .image-container {{
            margin: 40px 0;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
            animation: fadeIn 0.8s ease-out;
        }}

        .image-container img {{
            width: 100%;
            height: auto;
            display: block;
            transition: transform 0.4s ease;
        }}

        .image-container:hover img {{
            transform: scale(1.02);
        }}

        .image-left {{
            float: left;
            max-width: 45%;
            margin: 10px 30px 20px 0;
        }}

        .image-right {{
            float: right;
            max-width: 45%;
            margin: 10px 0 20px 30px;
        }}

        .image-center {{
            clear: both;
            max-width: 100%;
            margin: 50px auto;
        }}

        .image-description {{
            font-size: 1rem;
            color: var(--text-muted);
            font-style: italic;
            text-align: center;
            margin-top: -30px;
            margin-bottom: 40px;
        }}

        /* Horizontal Rules */
        hr.section-divider {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(0, 245, 208, 0.3), transparent);
            margin: 60px 0;
            clear: both;
        }}

        /* Bullet Lists */
        ul.bullet-list {{
            list-style: none;
            padding-left: 0;
            margin: 25px 0;
        }}

        ul.bullet-list li {{
            font-size: 1.15rem;
            color: var(--text-secondary);
            padding-left: 35px;
            margin-bottom: 15px;
            position: relative;
            line-height: 1.8;
        }}

        ul.bullet-list li::before {{
            content: '▹';
            position: absolute;
            left: 0;
            color: var(--accent-primary);
            font-size: 1.5rem;
            font-weight: 700;
        }}

        /* Tables */
        .table-wrapper {{
            overflow-x: auto;
            margin: 40px 0;
            border-radius: 16px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}

        .wiki-table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-card);
            border-radius: 16px;
            overflow: hidden;
        }}

        .wiki-table thead {{
            background: linear-gradient(135deg, rgba(0, 245, 208, 0.2), rgba(255, 107, 157, 0.2));
        }}

        .wiki-table th {{
            font-family: 'Space Mono', monospace;
            font-size: 1rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 20px;
            text-align: left;
            color: var(--text-primary);
            border-bottom: 2px solid var(--accent-primary);
        }}

        .wiki-table td {{
            font-size: 1.1rem;
            padding: 18px 20px;
            color: var(--text-secondary);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .wiki-table tbody tr {{
            transition: var(--transition);
        }}

        .wiki-table tbody tr:hover {{
            background: rgba(0, 245, 208, 0.05);
        }}

        .wiki-table tbody tr:last-child td {{
            border-bottom: none;
        }}

        /* Discussion Section */
        .discussion-section {{
            margin-top: 80px;
            padding: 40px;
            background: var(--bg-card);
            border-radius: var(--border-radius);
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .discussion-intro {{
            color: var(--text-muted);
            font-size: 1.1rem;
            margin-bottom: 30px;
        }}

        /* User Avatar */
        .user-avatar {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            font-size: 0.8rem;
            color: var(--bg-primary);
            flex-shrink: 0;
        }}

        /* Comment Input */
        .comment-input-container {{
            display: flex;
            gap: 15px;
            margin-bottom: 40px;
        }}

        .comment-input-wrapper {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .comment-input {{
            width: 100%;
            padding: 15px;
            background: var(--bg-secondary);
            border: 2px solid transparent;
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'Crimson Pro', serif;
            font-size: 1rem;
            resize: vertical;
            transition: var(--transition);
        }}

        .comment-input:focus {{
            outline: none;
            border-color: var(--accent-primary);
            background: var(--bg-primary);
        }}

        .comment-submit-btn {{
            align-self: flex-end;
            padding: 12px 30px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border: none;
            border-radius: 8px;
            color: var(--bg-primary);
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            transition: var(--transition);
        }}

        .comment-submit-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 245, 208, 0.3);
        }}

        .comment-submit-btn:active {{
            transform: translateY(0);
        }}

        /* Comments Container */
        .comments-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        /* Comment Card */
        .comment-card {{
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 16px;
            transition: var(--transition);
        }}

        .comment-card:hover {{
            background: rgba(26, 31, 58, 0.8);
        }}

        .comment-header {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 12px;
        }}

        .comment-author {{
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            font-size: 1rem;
            color: var(--text-primary);
        }}

        .comment-time {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}

        .comment-content {{
            color: var(--text-secondary);
            font-size: 1.05rem;
            line-height: 1.7;
            margin-bottom: 15px;
        }}

        .comment-actions {{
            display: flex;
            gap: 20px;
            align-items: center;
        }}

        .action-btn {{
            display: flex;
            align-items: center;
            gap: 8px;
            background: none;
            border: none;
            color: var(--text-muted);
            font-family: 'Space Mono', monospace;
            font-size: 0.9rem;
            cursor: pointer;
            transition: var(--transition);
            padding: 5px 10px;
            border-radius: 6px;
        }}

        .action-btn:hover {{
            background: var(--bg-card);
            color: var(--text-primary);
        }}

        .action-btn.liked {{
            color: var(--accent-primary);
        }}

        .action-btn.disliked {{
            color: var(--accent-secondary);
        }}

        .action-btn .icon {{
            width: 18px;
            height: 18px;
            display: inline-block;
        }}

        .action-btn svg {{
            width: 18px;
            height: 18px;
            fill: currentColor;
            transition: var(--transition);
        }}

        /* Reply Section */
        .replies-container {{
            margin-top: 20px;
            padding-left: 40px;
            border-left: 2px solid rgba(0, 245, 208, 0.2);
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .reply-card {{
            background: var(--bg-primary);
            padding: 15px;
            border-radius: 12px;
        }}

        .reply-input-container {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
            padding-left: 40px;
        }}

        .reply-input {{
            flex: 1;
            padding: 10px 15px;
            background: var(--bg-primary);
            border: 2px solid transparent;
            border-radius: 8px;
            color: var(--text-primary);
            font-family: 'Crimson Pro', serif;
            font-size: 0.95rem;
            transition: var(--transition);
        }}

        .reply-input:focus {{
            outline: none;
            border-color: var(--accent-primary);
        }}

        .reply-submit-btn {{
            padding: 10px 20px;
            background: linear-gradient(135deg, var(--accent-tertiary), var(--accent-primary));
            border: none;
            border-radius: 8px;
            color: var(--bg-primary);
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            font-size: 0.85rem;
            cursor: pointer;
            transition: var(--transition);
        }}

        .reply-submit-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 217, 61, 0.3);
        }}

        /* Back to top button */
        .back-to-top {{
            position: fixed;
            bottom: 40px;
            right: 40px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(0, 245, 208, 0.3);
            transition: var(--transition);
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
        }}

        .back-to-top.visible {{
            opacity: 1;
            pointer-events: all;
        }}

        .back-to-top:hover {{
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 15px 40px rgba(0, 245, 208, 0.5);
        }}

        .back-to-top::after {{
            content: '↑';
            font-size: 2rem;
            font-weight: 700;
            color: var(--bg-primary);
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 40px 20px 80px;
            }}

            h1 {{
                font-size: 2.5rem;
            }}

            h2 {{
                font-size: 1.6rem;
            }}

            h3 {{
                font-size: 1.3rem;
            }}

            .image-left,
            .image-right {{
                float: none;
                max-width: 100%;
                margin: 30px 0;
            }}

            .table-wrapper {{
                margin: 30px -20px;
            }}

            .back-to-top {{
                bottom: 20px;
                right: 20px;
                width: 50px;
                height: 50px;
            }}

            .discussion-section {{
                padding: 20px;
            }}

            .comment-input-container,
            .reply-input-container {{
                flex-direction: column;
            }}

            .comment-submit-btn,
            .reply-submit-btn {{
                align-self: stretch;
            }}

            .replies-container {{
                padding-left: 20px;
            }}
        }}

        /* Clear floats */
        .clearfix::after {{
            content: "";
            display: table;
            clear: both;
        }}

        /* Bookmark Button */
        .bookmark-container {{
            display: flex;
            justify-content: flex-end;
            margin-bottom: 20px;
        }}

        .bookmark-btn {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 24px;
            background: var(--bg-card);
            border: 2px solid var(--accent-tertiary);
            border-radius: 12px;
            color: var(--accent-tertiary);
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }}

        .bookmark-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--accent-tertiary), var(--accent-primary));
            opacity: 0;
            transition: var(--transition);
            z-index: 0;
        }}

        .bookmark-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(255, 217, 61, 0.3);
        }}

        .bookmark-btn:hover::before {{
            opacity: 0.1;
        }}

        .bookmark-btn.bookmarked {{
            background: linear-gradient(135deg, var(--accent-tertiary), var(--accent-primary));
            border-color: transparent;
            color: var(--bg-primary);
        }}

        .bookmark-btn.bookmarked:hover {{
            box-shadow: 0 10px 30px rgba(255, 217, 61, 0.5);
        }}

        .bookmark-icon {{
            width: 20px;
            height: 20px;
            position: relative;
            z-index: 1;
            transition: var(--transition);
        }}

        .bookmark-btn.bookmarked .bookmark-icon {{
            fill: var(--bg-primary);
        }}

        .bookmark-text {{
            position: relative;
            z-index: 1;
        }}

        .bookmark-btn:active {{
            transform: translateY(-1px);
        }}

        /* Bookmark animation */
        @keyframes bookmarkPulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.2); }}
            100% {{ transform: scale(1); }}
        }}

        .bookmark-btn.animate .bookmark-icon {{
            animation: bookmarkPulse 0.3s ease-out;
        }}

        /* ===== TOP METADATA (inside main content) ===== */
        .article-meta-info {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px 20px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .meta-stats {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-style: italic;
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        .meta-separator {{
            color: var(--accent-tertiary);
        }}

        .meta-views,
        .meta-last-viewed {{
            color: var(--text-secondary);
        }}

        .meta-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-left: auto;
        }}

        /* ===== SIDEBAR STYLES ===== */
        .page-wrapper {{
            display: flex;
            gap: 40px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 60px 40px 100px;
            position: relative;
            z-index: 1;
        }}

        .article-content {{
            flex: 1;
            min-width: 0;
            max-width: 900px;
            order: 1;
        }}

        .article-sidebar {{
            width: 280px;
            flex-shrink: 0;
            position: sticky;
            top: 40px;
            height: fit-content;
            max-height: calc(100vh - 80px);
            overflow-y: auto;
            order: 2;
        }}

        .sidebar-section {{
            background: var(--bg-card);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
        }}

        .sidebar-section:first-child {{
            margin-top: 0;
        }}

        .sidebar-title {{
            font-family: 'Space Mono', monospace;
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--accent-primary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 0 0 12px 0;
            padding: 0;
        }}

        /* Table of Contents */
        .toc-nav {{
            max-height: 350px;
            overflow-y: auto;
        }}

        .toc-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .toc-item {{
            margin-bottom: 6px;
        }}

        .toc-item:last-child {{
            margin-bottom: 0;
        }}

        .toc-item.toc-h3 {{
            padding-left: 16px;
        }}

        .toc-link {{
            display: block;
            color: var(--text-secondary);
            font-size: 0.85rem;
            padding: 5px 10px;
            border-radius: 6px;
            border-left: 2px solid transparent;
            transition: var(--transition);
            text-decoration: none;
        }}

        .toc-link:hover {{
            color: var(--accent-primary);
            background: rgba(0, 245, 208, 0.1);
            border-left-color: var(--accent-primary);
        }}

        .toc-link.active {{
            color: var(--accent-primary);
            background: rgba(0, 245, 208, 0.15);
            border-left-color: var(--accent-primary);
            font-weight: 600;
        }}

        /* Tags (in top bar) */
        .tag-chip {{
            display: inline-block;
            padding: 5px 12px;
            background: var(--bg-secondary);
            border: 1px solid rgba(0, 245, 208, 0.3);
            border-radius: 20px;
            color: var(--accent-primary);
            font-family: 'Space Mono', monospace;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            transition: var(--transition);
            text-decoration: none;
        }}

        .tag-chip:hover {{
            background: rgba(0, 245, 208, 0.15);
            border-color: var(--accent-primary);
            transform: translateY(-2px);
        }}

        /* Related Articles */
        .related-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .related-item {{
            margin-bottom: 10px;
        }}

        .related-item:last-child {{
            margin-bottom: 0;
        }}

        .related-link {{
            display: block;
            padding: 10px 12px;
            background: var(--bg-secondary);
            border-radius: 10px;
            text-decoration: none;
            transition: var(--transition);
        }}

        .related-link:hover {{
            background: rgba(255, 107, 157, 0.1);
            transform: translateX(4px);
        }}

        .related-title {{
            display: block;
            color: var(--text-primary);
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 3px;
        }}

        .related-category {{
            display: block;
            color: var(--accent-secondary);
            font-family: 'Space Mono', monospace;
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Sidebar scrollbar */
        .article-sidebar::-webkit-scrollbar {{
            width: 4px;
        }}

        .article-sidebar::-webkit-scrollbar-track {{
            background: transparent;
        }}

        .article-sidebar::-webkit-scrollbar-thumb {{
            background: var(--bg-card);
            border-radius: 2px;
        }}

        .article-sidebar::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-primary);
        }}

        /* TOC scrollbar */
        .toc-nav::-webkit-scrollbar {{
            width: 3px;
        }}

        .toc-nav::-webkit-scrollbar-track {{
            background: transparent;
        }}

        .toc-nav::-webkit-scrollbar-thumb {{
            background: rgba(0, 245, 208, 0.3);
            border-radius: 2px;
        }}

        /* Responsive */
        @media (max-width: 1100px) {{
            .article-meta-info {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .meta-tags {{
                margin-left: 0;
            }}

            .page-wrapper {{
                flex-direction: column;
                padding: 0 20px 80px;
            }}

            .article-sidebar {{
                width: 100%;
                position: relative;
                top: 0;
                max-height: none;
                order: -1;
            }}

            .toc-section {{
                display: none;
            }}
        }}

        @media (max-width: 600px) {{
            .meta-stats {{
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }}

            .meta-separator {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <!-- GLOBAL NAVIGATION BAR -->
    <nav class="global-navbar">
        <button class="global-mobile-menu-btn" onclick="toggleGlobalSidebar()">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
        </button>
        <a href="/" class="global-navbar-logo">BioBasics</a>
        <div class="global-navbar-search">
            <input type="text" class="global-search-input" placeholder="Search articles..." style="padding-left: 15px;">
        </div>
        <div class="global-navbar-actions">
            <div class="global-streak-indicator">
                <svg class="global-streak-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2c1.5 3 4 5 6 8-2-1-4 0-5 2 0 0 0-1-1-2-1-1-2-1-3 0 0-3-3-5-5-8 1 4 0 8-2 12-1 2-1 4 0 6 1 3 4 4 7 4 4 0 7-2 8-5 1-2 1-5-1-8-1-2-3-4-4-9z"/>
                </svg>
                <span class="global-streak-count">7</span>
            </div>
            <button class="global-notification-btn">
                <svg class="global-notification-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                <span class="global-notification-badge">3</span>
            </button>
            <button class="global-account-btn">JD</button>
        </div>
    </nav>

    <!-- GLOBAL SIDEBAR -->
    <aside class="global-sidebar" id="globalSidebar">
        <div class="global-sidebar-section">
            <ul class="global-sidebar-nav">
                <li class="global-nav-item">
                    <a href="/dashboard" class="global-nav-link">
                        <svg class="global-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="7" height="7"></rect>
                            <rect x="14" y="3" width="7" height="7"></rect>
                            <rect x="14" y="14" width="7" height="7"></rect>
                            <rect x="3" y="14" width="7" height="7"></rect>
                        </svg>
                        <span class="global-nav-text">Dashboard</span>
                    </a>
                </li>
            </ul>
        </div>
        <div class="global-sidebar-section">
            <h3 class="global-sidebar-title">Learning</h3>
            <ul class="global-sidebar-nav">
                <li class="global-nav-item">
                    <a href="/themes" class="global-nav-link">
                        <svg class="global-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                        </svg>
                        <span class="global-nav-text">Themes</span>
                    </a>
                </li>
            </ul>
        </div>
        <div class="global-sidebar-section">
            <h3 class="global-sidebar-title">Resources</h3>
            <ul class="global-sidebar-nav">
                <li class="global-nav-item">
                    <a href="/encyclopedia" class="global-nav-link active">
                        <svg class="global-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                        </svg>
                        <span class="global-nav-text">Encyclopedia</span>
                    </a>
                </li>
                <li class="global-nav-item">
                    <a href="/bookmarks" class="global-nav-link">
                        <svg class="global-nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                        </svg>
                        <span class="global-nav-text">Bookmarks</span>
                    </a>
                </li>
            </ul>
        </div>
    </aside>

    <!-- MAIN CONTENT WRAPPER -->
    <div class="main-content-wrapper">
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

    <div class="back-to-top" id="backToTop">
    </div>

    <script>
        // Global sidebar toggle for mobile
        function toggleGlobalSidebar() {{
            const sidebar = document.getElementById('globalSidebar');
            sidebar.classList.toggle('mobile-open');
        }}

        // TOC Active State Tracking
        document.addEventListener('DOMContentLoaded', () => {{
            const tocLinks = document.querySelectorAll('.toc-link');
            const headers = document.querySelectorAll('h2[id], h3[id]');
            
            if (tocLinks.length > 0 && headers.length > 0) {{
                const observerOptions = {{
                    rootMargin: '-20% 0% -80% 0%',
                    threshold: 0
                }};
                
                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            tocLinks.forEach(link => link.classList.remove('active'));
                            const activeLink = document.querySelector(`.toc-link[href="#${{entry.target.id}}"]`);
                            if (activeLink) {{
                                activeLink.classList.add('active');
                            }}
                        }}
                    }});
                }}, observerOptions);
                
                headers.forEach(header => observer.observe(header));
            }}
        }});

        // Discussion System State
        let comments = [
            {{
                id: 1,
                author: "Dr. Sarah Chen",
                avatar: "linear-gradient(135deg, #00f5d0, #0066cc)",
                time: "2 hours ago",
                content: "Excellent comprehensive overview! I'd add that the 'golden hour' concept is crucial - every minute of delay increases mortality by 7-10%. Early recognition and calling 911 immediately cannot be overstated.",
                likes: 24,
                dislikes: 1,
                userVote: null,
                replies: [
                    {{
                        id: 101,
                        author: "Medical Student Mike",
                        avatar: "linear-gradient(135deg, #ffd93d, #ff9500)",
                        time: "1 hour ago",
                        content: "That's a great point Dr. Chen. In our recent simulation training, we practiced recognizing STEMI symptoms within 60 seconds. The time pressure really hits home.",
                        likes: 8,
                        dislikes: 0,
                        userVote: null
                    }},
                    {{
                        id: 102,
                        author: "Emergency Nurse Amy",
                        avatar: "linear-gradient(135deg, #ff6b9d, #c71585)",
                        time: "45 minutes ago",
                        content: "Absolutely! In the ER, we've seen outcomes dramatically improve when patients arrive within that first hour. Public education about symptoms is so important.",
                        likes: 12,
                        dislikes: 0,
                        userVote: null
                    }}
                ]
            }},
            {{
                id: 2,
                author: "James Rodriguez",
                avatar: "linear-gradient(135deg, #9d50bb, #6e48aa)",
                time: "5 hours ago",
                content: "I survived a heart attack last year. The information here is spot-on. I experienced the 'atypical' symptoms - mainly extreme fatigue and jaw pain. Almost didn't call 911 because I thought it was just stress. Trust your gut and call for help!",
                likes: 45,
                dislikes: 0,
                userVote: null,
                replies: [
                    {{
                        id: 201,
                        author: "Dr. Sarah Chen",
                        avatar: "linear-gradient(135deg, #00f5d0, #0066cc)",
                        time: "4 hours ago",
                        content: "Thank you for sharing your experience, James. Your story highlights why we need to educate people about atypical presentations, especially in certain demographics. I'm glad you're here to tell your story!",
                        likes: 18,
                        dislikes: 0,
                        userVote: null
                    }},
                    {{
                        id: 202,
                        author: "Heart Health Advocate",
                        avatar: "linear-gradient(135deg, #ee0979, #ff6a00)",
                        time: "3 hours ago",
                        content: "Stories like yours save lives. Many people, especially women and diabetics, don't present with classic chest pain. Spreading awareness is crucial.",
                        likes: 15,
                        dislikes: 0,
                        userVote: null
                    }}
                ]
            }},
            {{
                id: 3,
                author: "Cardiologist Mark",
                avatar: "linear-gradient(135deg, #667eea, #764ba2)",
                time: "1 day ago",
                content: "One thing I'd emphasize: cardiac rehabilitation is not optional. Studies show it reduces 5-year mortality by 25-30%. Yet compliance rates are only around 30%. We need to do better educating patients about its importance.",
                likes: 31,
                dislikes: 2,
                userVote: null,
                replies: []
            }},
            {{
                id: 4,
                author: "Fitness Coach Lisa",
                avatar: "linear-gradient(135deg, #f093fb, #f5576c)",
                time: "1 day ago",
                content: "Question: The article mentions 150 minutes/week of moderate exercise. For someone recovering from an MI, how soon can they start exercising and how should they progress safely?",
                likes: 7,
                dislikes: 0,
                userVote: null,
                replies: [
                    {{
                        id: 401,
                        author: "Cardiologist Mark",
                        avatar: "linear-gradient(135deg, #667eea, #764ba2)",
                        time: "1 day ago",
                        content: "Great question! Typically, patients start gentle walking within days post-MI. A supervised cardiac rehab program usually begins 2-6 weeks after. They'll do stress testing to establish safe heart rate zones. Progress is gradual and monitored closely.",
                        likes: 22,
                        dislikes: 0,
                        userVote: null
                    }}
                ]
            }}
        ];

        let commentIdCounter = 5;
        let replyIdCounter = 500;

        // Initialize comments on page load
        document.addEventListener('DOMContentLoaded', () => {{
            renderComments();
        }});

        // Render all comments
        function renderComments() {{
            const container = document.getElementById('commentsContainer');
            container.innerHTML = '';
            
            comments.forEach(comment => {{
                const commentElement = createCommentElement(comment);
                container.appendChild(commentElement);
            }});
        }}

        // Create comment element
        function createCommentElement(comment) {{
            const div = document.createElement('div');
            div.className = 'comment-card';
            div.dataset.commentId = comment.id;
            
            div.innerHTML = `
                <div class="comment-header">
                    <div class="user-avatar" style="background: ${{comment.avatar}};">
                        <span>${{comment.author.charAt(0)}}</span>
                    </div>
                    <div>
                        <div class="comment-author">${{comment.author}}</div>
                        <div class="comment-time">${{comment.time}}</div>
                    </div>
                </div>
                <div class="comment-content">${{comment.content}}</div>
                <div class="comment-actions">
                    <button class="action-btn like-btn ${{comment.userVote === 'like' ? 'liked' : ''}}" onclick="voteComment(${{comment.id}}, 'like')">
                        <span class="icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                            </svg>
                        </span>
                        <span class="count">${{comment.likes}}</span>
                    </button>
                    <button class="action-btn dislike-btn ${{comment.userVote === 'dislike' ? 'disliked' : ''}}" onclick="voteComment(${{comment.id}}, 'dislike')">
                        <span class="icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                            </svg>
                        </span>
                        <span class="count">${{comment.dislikes}}</span>
                    </button>
                    <button class="action-btn" onclick="toggleReplyInput(${{comment.id}})">
                        <span class="icon">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </span>
                        <span>Reply (${{comment.replies.length}})</span>
                    </button>
                </div>
                <div id="replies-${{comment.id}}" class="replies-container" style="display: ${{comment.replies.length > 0 ? 'flex' : 'none'}};">
                    ${{comment.replies.map(reply => createReplyHTML(reply, comment.id)).join('')}}
                </div>
                <div id="reply-input-${{comment.id}}" class="reply-input-container" style="display: none;">
                    <div class="user-avatar" style="background: linear-gradient(135deg, #ff6b9d, #ffd93d);">
                        <span>You</span>
                    </div>
                    <input type="text" class="reply-input" placeholder="Write a reply..." id="reply-text-${{comment.id}}">
                    <button class="reply-submit-btn" onclick="addReply(${{comment.id}})">Reply</button>
                </div>
            `;
            
            return div;
        }}

        // Create reply HTML
        function createReplyHTML(reply, parentId) {{
            return `
                <div class="reply-card" data-reply-id="${{reply.id}}">
                    <div class="comment-header">
                        <div class="user-avatar" style="background: ${{reply.avatar}};">
                            <span>${{reply.author.charAt(0)}}</span>
                        </div>
                        <div>
                            <div class="comment-author">${{reply.author}}</div>
                            <div class="comment-time">${{reply.time}}</div>
                        </div>
                    </div>
                    <div class="comment-content">${{reply.content}}</div>
                    <div class="comment-actions">
                        <button class="action-btn like-btn ${{reply.userVote === 'like' ? 'liked' : ''}}" onclick="voteReply(${{parentId}}, ${{reply.id}}, 'like')">
                            <span class="icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                                </svg>
                            </span>
                            <span class="count">${{reply.likes}}</span>
                        </button>
                        <button class="action-btn dislike-btn ${{reply.userVote === 'dislike' ? 'disliked' : ''}}" onclick="voteReply(${{parentId}}, ${{reply.id}}, 'dislike')">
                            <span class="icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                                </svg>
                            </span>
                            <span class="count">${{reply.dislikes}}</span>
                        </button>
                    </div>
                </div>
            `;
        }}

        // Add new comment
        function addComment() {{
            const input = document.getElementById('mainCommentInput');
            const content = input.value.trim();
            
            if (!content) {{
                alert('Please write a comment first!');
                return;
            }}
            
            const newComment = {{
                id: commentIdCounter++,
                author: "You",
                avatar: "linear-gradient(135deg, #ff6b9d, #ffd93d)",
                time: "Just now",
                content: content,
                likes: 0,
                dislikes: 0,
                userVote: null,
                replies: []
            }};
            
            comments.unshift(newComment);
            input.value = '';
            renderComments();
        }}

        // Add reply to comment
        function addReply(commentId) {{
            const input = document.getElementById(`reply-text-${{commentId}}`);
            const content = input.value.trim();
            
            if (!content) {{
                alert('Please write a reply first!');
                return;
            }}
            
            const comment = comments.find(c => c.id === commentId);
            if (!comment) return;
            
            const newReply = {{
                id: replyIdCounter++,
                author: "You",
                avatar: "linear-gradient(135deg, #ff6b9d, #ffd93d)",
                time: "Just now",
                content: content,
                likes: 0,
                dislikes: 0,
                userVote: null
            }};
            
            comment.replies.push(newReply);
            input.value = '';
            renderComments();
            
            // Show replies container
            const repliesContainer = document.getElementById(`replies-${{commentId}}`);
            repliesContainer.style.display = 'flex';
        }}

        // Toggle reply input visibility
        function toggleReplyInput(commentId) {{
            const replyInput = document.getElementById(`reply-input-${{commentId}}`);
            const isVisible = replyInput.style.display !== 'none';
            replyInput.style.display = isVisible ? 'none' : 'flex';
            
            if (!isVisible) {{
                document.getElementById(`reply-text-${{commentId}}`).focus();
            }}
        }}

        // Vote on comment
        function voteComment(commentId, voteType) {{
            const comment = comments.find(c => c.id === commentId);
            if (!comment) return;
            
            // If clicking the same vote, remove it
            if (comment.userVote === voteType) {{
                if (voteType === 'like') {{
                    comment.likes--;
                }} else {{
                    comment.dislikes--;
                }}
                comment.userVote = null;
            }} else {{
                // Remove previous vote if exists
                if (comment.userVote === 'like') {{
                    comment.likes--;
                }} else if (comment.userVote === 'dislike') {{
                    comment.dislikes--;
                }}
                
                // Add new vote
                if (voteType === 'like') {{
                    comment.likes++;
                }} else {{
                    comment.dislikes++;
                }}
                comment.userVote = voteType;
            }}
            
            renderComments();
        }}

        // Vote on reply
        function voteReply(commentId, replyId, voteType) {{
            const comment = comments.find(c => c.id === commentId);
            if (!comment) return;
            
            const reply = comment.replies.find(r => r.id === replyId);
            if (!reply) return;
            
            // If clicking the same vote, remove it
            if (reply.userVote === voteType) {{
                if (voteType === 'like') {{
                    reply.likes--;
                }} else {{
                    reply.dislikes--;
                }}
                reply.userVote = null;
            }} else {{
                // Remove previous vote if exists
                if (reply.userVote === 'like') {{
                    reply.likes--;
                }} else if (reply.userVote === 'dislike') {{
                    reply.dislikes--;
                }}
                
                // Add new vote
                if (voteType === 'like') {{
                    reply.likes++;
                }} else {{
                    reply.dislikes++;
                }}
                reply.userVote = voteType;
            }}
            
            renderComments();
        }}

        // Back to top functionality
        const backToTop = document.getElementById('backToTop');
        
        window.addEventListener('scroll', () => {{
            if (window.scrollY > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});

        backToTop.addEventListener('click', () => {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});

        // Allow Enter key to submit comments/replies
        document.getElementById('mainCommentInput').addEventListener('keydown', (e) => {{
            if (e.key === 'Enter' && e.ctrlKey) {{
                addComment();
            }}
        }});

        // Bookmark functionality
        const BOOKMARK_KEY = 'biobasics_bookmarked_' + window.location.pathname;
        
        function initBookmark() {{
            const isBookmarked = localStorage.getItem(BOOKMARK_KEY) === 'true';
            const bookmarkBtn = document.getElementById('bookmarkBtn');
            
            if (isBookmarked) {{
                bookmarkBtn.classList.add('bookmarked');
                bookmarkBtn.querySelector('.bookmark-text').textContent = 'Bookmarked';
            }}
        }}

        function toggleBookmark() {{
            const bookmarkBtn = document.getElementById('bookmarkBtn');
            const isCurrentlyBookmarked = bookmarkBtn.classList.contains('bookmarked');
            
            // Add animation class
            bookmarkBtn.classList.add('animate');
            setTimeout(() => bookmarkBtn.classList.remove('animate'), 300);
            
            if (isCurrentlyBookmarked) {{
                // Remove bookmark
                bookmarkBtn.classList.remove('bookmarked');
                bookmarkBtn.querySelector('.bookmark-text').textContent = 'Bookmark';
                localStorage.removeItem(BOOKMARK_KEY);
                showBookmarkNotification('Bookmark removed');
            }} else {{
                // Add bookmark
                bookmarkBtn.classList.add('bookmarked');
                bookmarkBtn.querySelector('.bookmark-text').textContent = 'Bookmarked';
                localStorage.setItem(BOOKMARK_KEY, 'true');
                showBookmarkNotification('Page bookmarked!');
            }}
        }}

        function showBookmarkNotification(message) {{
            // Remove existing notification if any
            const existingNotif = document.querySelector('.bookmark-notification');
            if (existingNotif) {{
                existingNotif.remove();
            }}
            
            // Create notification element
            const notification = document.createElement('div');
            notification.className = 'bookmark-notification';
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%) translateY(-100px);
                background: linear-gradient(135deg, var(--accent-tertiary), var(--accent-primary));
                color: var(--bg-primary);
                padding: 12px 24px;
                border-radius: 8px;
                font-family: 'Space Mono', monospace;
                font-weight: 700;
                font-size: 0.9rem;
                z-index: 10000;
                box-shadow: 0 10px 30px rgba(255, 217, 61, 0.4);
                transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            `;
            
            document.body.appendChild(notification);
            
            // Animate in
            requestAnimationFrame(() => {{
                notification.style.transform = 'translateX(-50%) translateY(0)';
            }});
            
            // Remove after delay
            setTimeout(() => {{
                notification.style.transform = 'translateX(-50%) translateY(-100px)';
                setTimeout(() => notification.remove(), 400);
            }}, 2000);
        }}

        // Initialize bookmark state on page load
        document.addEventListener('DOMContentLoaded', () => {{
            initBookmark();
        }});
    </script>
</body>
</html>"""


def convert_file(input_path: str, output_path: str,
                 view_count: int = 0,
                 last_viewed_at: str = "",
                 tags: list = None,
                 related_articles: list = None) -> None:
    """
    Convert a BioBasics markdown file to HTML.
    
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
    
    converter = BioBasicsMarkdownConverter()
    html_content = converter.convert(
        markdown_content,
        view_count=view_count,
        last_viewed_at=last_viewed_at,
        tags=tags or [],
        related_articles=related_articles or []
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Converted {input_path} to {output_path}")


def main():
    """Main function with hardcoded input and output paths and sample metadata."""
    input_path = r'markdown.md'
    output_path = r'demo.html'
    
    # Sample metadata for demonstration
    sample_tags = [
        "Cardiology",
        "Emergency Medicine", 
        "Heart Disease",
        "First Aid",
        "Cardiovascular"
    ]
    
    sample_related_articles = [
        {
            "title": "Coronary Artery Disease",
            "slug": "coronary-artery-disease",
            "category": "Cardiology"
        },
        {
            "title": "Cardiac Arrest vs Heart Attack",
            "slug": "cardiac-arrest-vs-heart-attack",
            "category": "Emergency Medicine"
        },
        {
            "title": "Blood Pressure Management",
            "slug": "blood-pressure-management",
            "category": "Cardiovascular Health"
        },
        {
            "title": "Atherosclerosis",
            "slug": "atherosclerosis",
            "category": "Cardiology"
        },
        {
            "title": "CPR Basics",
            "slug": "cpr-basics",
            "category": "First Aid"
        }
    ]
    
    convert_file(
        input_path, 
        output_path,
        view_count=12847,
        last_viewed_at="2 minutes ago",
        tags=sample_tags,
        related_articles=sample_related_articles
    )


if __name__ == "__main__":
    main()