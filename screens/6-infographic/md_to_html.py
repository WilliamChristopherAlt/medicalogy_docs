"""
BioBasics Medical Wiki Markdown to HTML Converter
Converts custom medical markdown format to styled HTML pages
"""

import re
from typing import List, Tuple, Optional


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
    """
    
    def __init__(self):
        self.in_table = False
        self.in_list = False
        self.table_headers = []
        
    def convert(self, markdown_text: str) -> str:
        """Convert markdown text to complete HTML document."""
        lines = markdown_text.strip().split('\n')
        body_html = self._convert_lines(lines)
        
        return self._wrap_in_html(body_html)
    
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
        """Convert header markdown to HTML."""
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            level = len(match.group(1))
            text = self._convert_inline(match.group(2))
            
            # Special styling for Sources header
            if level == 2 and 'Sources' in text:
                return f'<h{level} class="sources-header">{text}</h{level}>'
            
            return f'<h{level}>{text}</h{level}>'
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
    
    def _wrap_in_html(self, body_content: str) -> str:
        """Wrap content in complete HTML document with BioBasics styling."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioBasics Medical Wiki</title>
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
        }}

        /* Clear floats */
        .clearfix::after {{
            content: "";
            display: table;
            clear: both;
        }}
    </style>
</head>
<body>
    <div class="container clearfix">
        {body_content}
    </div>

    <div class="back-to-top" id="backToTop">
    </div>

    <script>
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
    </script>
</body>
</html>"""


def convert_file(input_path: str, output_path: str) -> None:
    """
    Convert a BioBasics markdown file to HTML.
    
    Args:
        input_path: Path to input .md file
        output_path: Path to output .html file
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    converter = BioBasicsMarkdownConverter()
    html_content = converter.convert(markdown_content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Converted {input_path} to {output_path}")


def main():
    """Main function with hardcoded input and output paths."""
    input_path = r'test\7-infographic\markdown.md'
    output_path = r'test\7-infographic\demo.html'
    
    convert_file(input_path, output_path)


if __name__ == "__main__":
    main()