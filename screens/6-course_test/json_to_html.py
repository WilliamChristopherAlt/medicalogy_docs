#!/usr/bin/env python3
"""
BioBasics Course JSON to HTML Converter
Converts course JSON structure into an interactive HTML demonstration.
"""

import json
import sys
from pathlib import Path


def load_course_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'version' not in data or 'screens' not in data:
            raise ValueError("Invalid course JSON: missing 'version' or 'screens'")
        if not isinstance(data['screens'], list) or len(data['screens']) == 0:
            raise ValueError("Invalid course JSON: 'screens' must be a non-empty array")
        return data
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading course: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# SVG icons (inline, matching demo_v2 exactly)
# ---------------------------------------------------------------------------

SVG_BOOK = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>'
SVG_QUIZ = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
SVG_TF   = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'
SVG_MATCH = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>'
SVG_BULB = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="9" y1="18" x2="15" y2="18"></line><line x1="10" y1="22" x2="14" y2="22"></line><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"></path></svg>'
SVG_TF_CHECK = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'
SVG_TF_X    = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>'
SVG_MEDAL = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="6"></circle><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"></path></svg>'
SVG_CHEVRON_RIGHT = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>'
SVG_ARROW_LEFT  = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>'
SVG_ARROW_RIGHT = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>'


# ---------------------------------------------------------------------------
# Screen generators
# ---------------------------------------------------------------------------

def generate_infographic_html(screen_id, content):
    image_html = ""
    if content.get('imageFileName'):
        image_html = f'''
                    <div class="infographic-image">
                        <img src="{content['imageFileName']}" alt="Educational infographic" />
                    </div>'''
    summary = content.get('summaryText', '')
    return f'''
                <div class="screen infographic-screen" id="{screen_id}" data-type="infographic">
                <div class="screen-header">
                    <span class="screen-type-label label-learn">{SVG_BOOK} Learn</span>
                </div>
                <div class="screen-body">
                    {image_html}
                    <div class="summary-text">{summary}</div>
                </div>
            </div>'''


def generate_multiple_choice_html(screen_id, content):
    options_html = []
    for option in content.get('options', []):
        correct = str(option.get('isCorrect', False)).lower()
        opt_id  = option['id']
        text    = option['text']
        options_html.append(f'''
                        <button class="quiz-option" data-correct="{correct}" data-option-id="{opt_id}">
                            <span class="option-label">{opt_id.upper()}</span>
                            <span class="option-text">{text}</span>
                            <span class="option-feedback"></span>
                        </button>''')

    explanation     = content.get('explanation', '')
    explanation_html = f'''
                    <div class="explanation hidden">
                        <div class="explanation-icon">{SVG_BULB}</div>
                        <p>{explanation}</p>
                    </div>''' if explanation else ''

    return f'''
                <div class="screen quiz-screen" id="{screen_id}" data-type="quiz-mc">
                <div class="screen-header">
                    <span class="screen-type-label label-quiz">{SVG_QUIZ} Quiz Time</span>
                </div>
                <div class="screen-body">
                    <div class="question-text">{content.get('questionText', '')}</div>
                    <div class="quiz-options">
                        {''.join(options_html)}
                    </div>
                    {explanation_html}
                </div>
            </div>'''


def generate_true_false_html(screen_id, content):
    correct_answer  = content.get('correctAnswer', True)
    true_correct    = str(correct_answer).lower()
    false_correct   = str(not correct_answer).lower()
    explanation     = content.get('explanation', '')
    explanation_html = f'''
                    <div class="explanation hidden">
                        <div class="explanation-icon">{SVG_BULB}</div>
                        <p>{explanation}</p>
                    </div>''' if explanation else ''

    return f'''
                <div class="screen quiz-screen" id="{screen_id}" data-type="quiz-tf">
                <div class="screen-header">
                    <span class="screen-type-label label-quiz">{SVG_TF} True or False</span>
                </div>
                <div class="screen-body">
                    <div class="question-text">{content.get('questionText', '')}</div>
                    <div class="quiz-options tf-options">
                        <button class="quiz-option tf-option" data-correct="{true_correct}" data-value="true">
                            <span class="option-label tf-check">{SVG_TF_CHECK}</span>
                            <span class="option-text">True</span>
                            <span class="option-feedback"></span>
                        </button>
                        <button class="quiz-option tf-option" data-correct="{false_correct}" data-value="false">
                            <span class="option-label tf-x">{SVG_TF_X}</span>
                            <span class="option-text">False</span>
                            <span class="option-feedback"></span>
                        </button>
                    </div>
                    {explanation_html}
                </div>
            </div>'''


def generate_matching_html(screen_id, content):
    sentence        = content.get('sentence', '').replace('\n', '<br>')
    correct_answers = content.get('correctAnswers', [])
    wrong_answers   = content.get('wrongAnswers', [])

    for i, answer in enumerate(correct_answers, 1):
        sentence = sentence.replace(
            f'<{i}>',
            f'<span class="blank" data-blank-id="{i}" data-correct="{answer}">___________</span>'
        )

    all_answers  = correct_answers + wrong_answers
    options_html = ''.join(
        f'\n                            <button class="answer-option" draggable="true" data-answer="{a}">{a}</button>'
        for a in all_answers
    )

    return f'''
                <div class="screen quiz-screen matching-screen" id="{screen_id}" data-type="quiz-match">
                <div class="screen-header">
                    <span class="screen-type-label label-match">{SVG_MATCH} Fill in the Blanks</span>
                </div>
                <div class="screen-body">
                    <div class="question-text">Complete the sentences with the correct answers:</div>
                    <p class="matching-sentence">{sentence}</p>
                    <div class="answer-bank">
                        <h3 class="bank-title">Tap or drag to fill the blanks:</h3>
                        <div class="answer-options">{options_html}
                        </div>
                    </div>
                    <button class="check-matching-btn hidden">Check Answers</button>
                    <div class="explanation matching-explanation hidden">
                        <div class="explanation-icon">{SVG_BULB}</div>
                        <p class="explanation-result"></p>
                    </div>
                </div>
            </div>'''


def generate_screen_html(screen):
    screen_id   = screen['id']
    screen_type = screen['type']
    content     = screen['content']

    if screen_type == 'infographic':
        return generate_infographic_html(screen_id, content)

    if screen_type == 'quiz':
        qtype = content.get('questionType')
        if qtype == 'multiple_choice':
            return generate_multiple_choice_html(screen_id, content)
        if qtype == 'true_false':
            return generate_true_false_html(screen_id, content)
        if qtype == 'matching':
            return generate_matching_html(screen_id, content)

    return f'<div class="screen" id="{screen_id}">Unknown screen type: {screen_type}</div>'


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f7f7f7;
            --bg-card: #ffffff;
            --bg-hover: #f0f0f0;

            --accent-primary: #1cb0f6;
            --accent-primary-dark: #1899d6;
            --accent-primary-light: #84d8ff;

            --accent-success: #58cc02;
            --accent-success-dark: #46a302;
            --accent-success-light: #d7f5b1;

            --accent-warning: #ff9600;
            --accent-warning-dark: #e68600;

            --accent-error: #ff4b4b;
            --accent-error-dark: #dc2626;
            --accent-error-light: #ffdfe0;

            --accent-purple: #ce82ff;

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
        }

        body {
            font-family: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
        }

        /* ===== NAVBAR ===== */
        .navbar {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: var(--navbar-height);
            background: var(--bg-primary);
            border-bottom: 2px solid var(--border-color);
            display: flex;
            align-items: center;
            padding: 0 30px;
            z-index: 1000;
            box-shadow: var(--shadow-sm);
        }

        .mobile-menu-btn {
            display: none;
            width: 44px; height: 44px;
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            align-items: center; justify-content: center;
            margin-right: 12px;
        }

        .hamburger-icon { width: 22px; height: 22px; stroke: var(--text-secondary); fill: none; }

        .navbar-logo {
            font-family: 'Nunito', sans-serif;
            font-size: 1.6rem; font-weight: 800;
            color: var(--accent-primary);
            text-decoration: none;
            margin-right: 40px; white-space: nowrap; letter-spacing: -0.5px;
        }

        .navbar-actions { display: flex; align-items: center; gap: 16px; margin-left: auto; }

        .nav-streak-indicator {
            display: flex; align-items: center; gap: 6px;
            padding: 8px 14px;
            background: var(--bg-primary);
            border: 2px solid var(--accent-warning);
            border-radius: var(--border-radius-sm);
        }
        .nav-streak-icon { width: 24px; height: 24px; fill: var(--accent-warning); }
        .nav-streak-count { font-weight: 800; color: var(--accent-warning-dark); font-size: 1rem; }

        .notification-btn {
            position: relative;
            width: 44px; height: 44px;
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            transition: var(--transition);
        }
        .notification-btn:hover { background: var(--bg-hover); border-color: var(--border-dark); }
        .notification-icon { width: 22px; height: 22px; stroke: var(--text-secondary); fill: none; }
        .notification-badge {
            position: absolute; top: -6px; right: -6px;
            width: 22px; height: 22px;
            background: var(--accent-error);
            border-radius: 50%; border: 2px solid var(--bg-primary);
            display: flex; align-items: center; justify-content: center;
            font-size: 0.7rem; font-weight: 800; color: white;
        }

        .account-menu { position: relative; }
        .account-btn {
            width: 44px; height: 44px;
            background: var(--accent-primary); border: none; border-radius: 50%;
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            font-weight: 800; color: white; font-size: 1rem;
            transition: var(--transition);
            box-shadow: 0 3px 0 var(--accent-primary-dark);
        }
        .account-btn:hover  { transform: translateY(-2px); box-shadow: 0 5px 0 var(--accent-primary-dark); }
        .account-btn:active { transform: translateY(0);    box-shadow: 0 1px 0 var(--accent-primary-dark); }

        .account-dropdown {
            position: absolute; top: calc(100% + 10px); right: 0;
            width: 200px; background: var(--bg-primary);
            border-radius: var(--border-radius-sm);
            box-shadow: var(--shadow-lg);
            border: 2px solid var(--border-color);
            overflow: hidden; display: none;
        }
        .account-dropdown.active { display: block; }

        .dropdown-item {
            padding: 12px 16px; color: var(--text-secondary);
            text-decoration: none; display: flex; align-items: center; gap: 10px;
            cursor: pointer; transition: var(--transition);
            border-bottom: 2px solid var(--border-color);
            font-weight: 700; font-size: 0.95rem;
        }
        .dropdown-item:last-child { border-bottom: none; }
        .dropdown-item:hover { background: var(--bg-hover); color: var(--text-primary); }
        .dropdown-icon { width: 18px; height: 18px; stroke: currentColor; fill: none; }

        /* ===== SIDEBAR ===== */
        .sidebar {
            position: fixed; left: 0; top: var(--navbar-height);
            width: var(--sidebar-width);
            height: calc(100vh - var(--navbar-height));
            background: var(--bg-primary);
            border-right: 2px solid var(--border-color);
            overflow-y: auto; padding: 20px 0; z-index: 900;
        }
        .sidebar::-webkit-scrollbar { width: 4px; }
        .sidebar::-webkit-scrollbar-track { background: transparent; }
        .sidebar::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 2px; }

        .sidebar-section { margin-bottom: 4px; padding: 0 16px; }
        .sidebar-title {
            font-size: 0.75rem; font-weight: 800; color: var(--text-muted);
            text-transform: uppercase; letter-spacing: 1px;
            margin-bottom: 4px; margin-top: 16px; padding-left: 12px;
        }
        .sidebar-nav { list-style: none; }
        .nav-item { margin-bottom: 4px; }
        .nav-link {
            display: flex; align-items: center; gap: 12px;
            padding: 12px 16px; color: var(--text-secondary);
            text-decoration: none; border-radius: var(--border-radius-sm);
            transition: var(--transition); font-weight: 700;
            border: 2px solid transparent;
            font-family: 'Nunito', sans-serif;
            font-size: 1rem;
            line-height: 1.7;
            background: none;
            width: 100%;
            text-align: left;
            cursor: pointer;
            box-sizing: border-box;
        }
        .nav-link:hover { background: var(--bg-secondary); color: var(--text-primary); }
        .nav-link.active {
            background: rgba(28, 176, 246, 0.1);
            color: var(--accent-primary);
            border-color: var(--accent-primary);
        }
        .nav-icon { width: 24px; height: 24px; stroke: currentColor; fill: none; flex-shrink: 0; }
        .nav-text { flex: 1; font-size: 1rem; }

        .nav-link.has-submenu .nav-icon.chevron { margin-left: auto; transition: transform 0.3s ease; flex-shrink: 0; }
        .nav-link.has-submenu.expanded .nav-icon.chevron { transform: rotate(180deg); }

        .submenu {
            list-style: none; max-height: 0; overflow: hidden;
            transition: max-height 0.3s ease;
            padding-left: 52px; margin-top: -6px;
        }
        .submenu.expanded { max-height: 500px; }
        .submenu-item { margin-bottom: 0; }
        .submenu-link {
            display: block; padding: 4px 12px;
            color: var(--text-secondary); text-decoration: none;
            border-radius: var(--border-radius-sm);
            font-size: 0.95rem; font-weight: 600; transition: var(--transition);
        }
        .submenu-link:hover { background: var(--bg-secondary); color: var(--accent-primary); }
        .submenu-link.active { color: var(--accent-primary); font-weight: 700; }

        .sidebar-overlay {
            display: none; position: fixed;
            top: var(--navbar-height); left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.4); z-index: 850;
        }
        .sidebar-overlay.active { display: block; }

        /* ===== MAIN WRAPPER ===== */
        .main-wrapper {
            margin-left: var(--sidebar-width);
            margin-top: var(--navbar-height);
            min-height: calc(100vh - var(--navbar-height));
            background: #f0f4f8;
        }
        .container { max-width: 780px; margin: 0 auto; padding: 36px 32px 120px; }

        /* ===== COURSE HEADER ===== */
        .course-header { margin-bottom: 24px; }
        .course-breadcrumb { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
        .course-breadcrumb svg { width: 18px; height: 18px; stroke: var(--text-muted); fill: none; flex-shrink: 0; }
        .breadcrumb-item { font-size: 1rem; font-weight: 700; color: var(--text-muted); }
        .breadcrumb-item.active { color: var(--text-primary); font-weight: 800; font-size: 1rem; }

        /* ===== PROGRESS ===== */
        .progress-container {
            margin-bottom: 24px; background: white;
            border-radius: var(--border-radius); padding: 16px 20px;
            border: 2px solid var(--border-color); box-shadow: var(--shadow-sm);
        }
        .progress-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .progress-label { font-size: 0.75rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; }
        .progress-count { font-size: 0.85rem; font-weight: 800; color: var(--accent-primary); }
        .progress-bar { background: var(--border-color); height: 8px; border-radius: 20px; overflow: hidden; }
        .progress-fill {
            height: 100%; background: var(--accent-success);
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); border-radius: 20px;
        }

        /* ===== SCREEN CARDS ===== */
        .screen {
            background: var(--bg-primary);
            border-radius: var(--border-radius);
            border: 2px solid var(--border-color);
            box-shadow: 0 2px 0 var(--border-dark), var(--shadow-sm);
            overflow: hidden; margin-bottom: 0;
            display: none;
            animation: slideUp 0.25s ease-out;
        }
        .screen-header { padding: 20px 32px 18px; border-bottom: 2px solid var(--border-color); }
        .infographic-screen .screen-header { background: rgba(28,176,246,0.05); border-bottom-color: rgba(28,176,246,0.15); }
        .quiz-screen .screen-header        { background: rgba(88,204,2,0.05);  border-bottom-color: rgba(88,204,2,0.15);  }
        .matching-screen .screen-header    { background: rgba(255,150,0,0.05); border-bottom-color: rgba(255,150,0,0.15); }
        .screen-body { padding: 32px; }
        .screen.active { display: block; }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(12px); }
            to   { opacity: 1; transform: translateY(0);    }
        }

        .screen-type-label svg { width: 13px; height: 13px; stroke: currentColor; fill: none; flex-shrink: 0; }
        .screen-type-label {
            display: inline-flex; align-items: center; gap: 7px;
            padding: 5px 12px; border-radius: 20px;
            font-size: 0.7rem; font-weight: 800;
            text-transform: uppercase; letter-spacing: 0.8px;
        }
        .label-learn { background: rgba(28,176,246,0.12); color: var(--accent-primary-dark);  border: 1.5px solid rgba(28,176,246,0.3); }
        .label-quiz  { background: rgba(88,204,2,0.12);  color: var(--accent-success-dark);  border: 1.5px solid rgba(88,204,2,0.3);  }
        .label-match { background: rgba(255,150,0,0.12); color: var(--accent-warning-dark);  border: 1.5px solid rgba(255,150,0,0.3); }

        .screen-icon  { display: none; }
        .screen-title { display: none; }

        .infographic-image {
            margin: 0 0 20px; border-radius: var(--border-radius-sm);
            overflow: hidden; border: 2px solid var(--border-color);
        }
        .infographic-image img {
            width: 100%; height: 240px; object-fit: cover;
            display: block; transition: transform 0.3s ease;
        }
        .infographic-image:hover img { transform: scale(1.02); }

        .summary-text { font-size: 1.05rem; line-height: 1.8; color: var(--text-secondary); font-weight: 600; }

        /* ===== QUIZ OPTIONS ===== */
        .question-text { font-size: 1.25rem; font-weight: 800; color: var(--text-primary); margin-bottom: 24px; line-height: 1.5; }
        .quiz-options  { display: flex; flex-direction: column; gap: 12px; margin-bottom: 0; }
        .tf-options    { flex-direction: row; gap: 14px; }

        .quiz-option {
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            padding: 16px 20px;
            font-size: 1rem; font-weight: 700; color: var(--text-primary);
            cursor: pointer; transition: var(--transition);
            display: flex; align-items: center; gap: 14px;
            text-align: left; font-family: 'Nunito', sans-serif;
        }
        .quiz-option:hover:not(.answered) {
            border-color: var(--accent-primary);
            background: rgba(28,176,246,0.06);
            transform: translateY(-1px); box-shadow: var(--shadow-sm);
        }
        .quiz-option:active:not(.answered) { transform: translateY(0); }
        .tf-option { flex: 1; justify-content: center; font-size: 1rem; }

        .option-label {
            width: 34px; height: 34px; border-radius: 50%;
            background: white; border: 2px solid var(--border-color);
            display: flex; align-items: center; justify-content: center;
            font-weight: 900; font-size: 0.85rem; color: var(--text-secondary);
            flex-shrink: 0; transition: var(--transition);
        }
        .option-text { flex: 1; }
        .option-feedback { margin-left: auto; font-size: 1.1rem; font-weight: 800; }

        .quiz-option.answered { pointer-events: none; }

        .quiz-option.correct  { background: rgba(88,204,2,0.08);  border-color: var(--accent-success); }
        .quiz-option.correct .option-label  { background: var(--accent-success); border-color: var(--accent-success); color: white; }
        .quiz-option.incorrect { background: rgba(255,75,75,0.06); border-color: var(--accent-error); }
        .quiz-option.incorrect .option-label { background: var(--accent-error);   border-color: var(--accent-error);   color: white; }

        .quiz-option.correct  .option-feedback::before { content: ''; width: 10px; height: 10px; background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2346a302' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E") center/contain no-repeat; display: inline-block; }
        .quiz-option.incorrect .option-feedback::before { content: ''; width: 10px; height: 10px; background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23dc2626' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='6' x2='6' y2='18'%3E%3C/line%3E%3Cline x1='6' y1='6' x2='18' y2='18'%3E%3C/line%3E%3C/svg%3E") center/contain no-repeat; display: inline-block; }
        .option-feedback { opacity: 0; transition: opacity 0.2s; }
        .quiz-option.correct  .option-feedback,
        .quiz-option.incorrect .option-feedback { opacity: 1; }

        /* ===== EXPLANATION ===== */
        .explanation {
            background: rgba(28,176,246,0.05);
            border: 2px solid rgba(28,176,246,0.2);
            border-radius: var(--border-radius-sm);
            padding: 16px 18px; margin-top: 16px;
            animation: fadeIn 0.3s ease;
            display: flex; gap: 12px; align-items: flex-start;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-6px); }
            to   { opacity: 1; transform: translateY(0);    }
        }
        .explanation-icon { flex-shrink: 0; margin-top: 1px; color: var(--accent-primary); display: flex; }
        .explanation p { color: var(--text-secondary); font-size: 0.92rem; font-weight: 600; line-height: 1.65; margin: 0; }
        .hidden { display: none !important; }

        /* ===== MATCHING / FILL IN BLANKS ===== */
        .matching-sentence { font-size: 1rem; font-weight: 700; color: var(--text-primary); line-height: 3.2; margin: 0 0 24px; }
        .blank {
            display: inline-block; min-width: 60px; max-width: 160px;
            padding: 3px 8px; background: var(--bg-secondary);
            border: 2px dashed var(--border-dark); border-radius: 8px;
            text-align: center; margin: 0 3px; transition: var(--transition);
            cursor: pointer; font-weight: 800; font-size: 0.85rem;
            vertical-align: middle; line-height: 1.4;
        }
        .blank:hover { border-color: var(--accent-primary); background: rgba(28,176,246,0.05); }
        .blank.filled  { background: rgba(28,176,246,0.08); border-style: solid; border-color: var(--accent-primary); color: var(--accent-primary); }
        .blank.correct { background: rgba(88,204,2,0.1);   border-color: var(--accent-success); border-style: solid; color: var(--accent-success-dark); }
        .blank.incorrect { background: rgba(255,75,75,0.08); border-color: var(--accent-error); border-style: solid; color: var(--accent-error-dark); font-size: 0.8rem; }

        .answer-bank { margin: 0 0 4px; }
        .bank-title { font-size: 0.72rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
        .answer-options { display: flex; flex-wrap: wrap; gap: 8px; }
        .answer-option {
            background: white; border: 2px solid var(--border-color);
            border-radius: 8px; padding: 8px 16px;
            color: var(--text-primary); font-family: 'Nunito', sans-serif;
            font-size: 0.9rem; font-weight: 700; cursor: grab;
            transition: var(--transition); box-shadow: 0 2px 0 var(--border-dark);
        }
        .answer-option:hover { border-color: var(--accent-primary); transform: translateY(-1px); box-shadow: 0 3px 0 var(--accent-primary-dark); }
        .answer-option:active { cursor: grabbing; transform: translateY(1px); box-shadow: none; }
        .answer-option.used { opacity: 0.25; pointer-events: none; }

        .check-matching-btn {
            background: var(--accent-primary); border: none;
            border-radius: var(--border-radius-sm); padding: 12px 28px;
            color: white; font-family: 'Nunito', sans-serif;
            font-size: 0.9rem; font-weight: 800; cursor: pointer;
            transition: var(--transition); margin-top: 20px;
            text-transform: uppercase; letter-spacing: 0.5px;
            box-shadow: 0 3px 0 var(--accent-primary-dark);
        }
        .check-matching-btn:hover  { transform: translateY(-1px); box-shadow: 0 4px 0 var(--accent-primary-dark); }
        .check-matching-btn:active { transform: translateY(1px);  box-shadow: none; }
        .matching-explanation { border-color: rgba(255,150,0,0.3); background: rgba(255,150,0,0.05); }

        /* ===== NAVIGATION ===== */
        .navigation { display: flex; gap: 12px; margin-top: 16px; }
        .nav-btn {
            flex: 1; background: white;
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-sm);
            padding: 14px 24px; color: var(--text-secondary);
            font-family: 'Nunito', sans-serif; font-size: 0.95rem; font-weight: 800;
            cursor: pointer; transition: var(--transition);
            text-transform: uppercase; letter-spacing: 0.5px;
            box-shadow: 0 3px 0 var(--border-dark);
            display: flex; align-items: center; justify-content: center; gap: 8px;
        }
        .nav-btn svg { flex-shrink: 0; }
        .badge-icon { display: flex; justify-content: center; margin-bottom: 16px; color: var(--accent-warning); }
        .badge-icon svg { stroke: var(--accent-warning); }
        .nav-btn:disabled { opacity: 0.3; cursor: not-allowed; box-shadow: none; }
        .nav-btn:not(:disabled):hover { border-color: var(--border-dark); color: var(--text-primary); transform: translateY(-1px); box-shadow: 0 4px 0 var(--border-dark); }
        .nav-btn:not(:disabled):active { transform: translateY(1px); box-shadow: none; }
        #nextBtn:not(:disabled) { background: var(--accent-success); border-color: var(--accent-success-dark); color: white; box-shadow: 0 3px 0 var(--accent-success-dark); }
        #nextBtn:not(:disabled):hover { transform: translateY(-1px); box-shadow: 0 5px 0 var(--accent-success-dark); }

        /* ===== COMPLETION BADGE ===== */
        .completion-badge {
            text-align: center; padding: 48px 32px;
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius);
            box-shadow: 0 2px 0 var(--border-dark), var(--shadow-sm);
            margin-top: 16px; display: none;
            animation: fadeIn 0.5s ease;
        }
        .completion-badge.show { display: block; }
        .badge-icon { font-size: 4rem; margin-bottom: 16px; display: block; }
        .badge-title { font-size: 2rem; font-weight: 900; color: var(--accent-success-dark); margin-bottom: 10px; letter-spacing: -1px; }
        .badge-message { font-size: 1rem; color: var(--text-secondary); font-weight: 600; line-height: 1.7; }
        .badge-stats { display: flex; justify-content: center; gap: 16px; margin-top: 24px; flex-wrap: wrap; }
        .badge-stat { padding: 12px 20px; background: var(--bg-secondary); border: 2px solid var(--border-color); border-radius: var(--border-radius-sm); text-align: center; }
        .stat-value { font-size: 1.5rem; font-weight: 900; color: var(--accent-primary); display: block; }
        .stat-label { font-size: 0.7rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

        /* ===== RESPONSIVE ===== */
        @media (max-width: 1100px) {
            :root { --sidebar-width: 0px; }
            .sidebar { width: 280px; transform: translateX(-100%); transition: transform 0.3s ease; }
            .sidebar.mobile-open { transform: translateX(0); }
            .main-wrapper { margin-left: 0; }
            .mobile-menu-btn { display: flex; }
            .navbar-search { display: none; }
        }
        @media (max-width: 600px) {
            .navbar { padding: 0 16px; }
            .navbar-logo { font-size: 1.3rem; margin-right: 16px; }
            .nav-streak-label { display: none; }
            .course-title { font-size: 2rem; }
            .screen { padding: 28px 20px; }
            .tf-options { flex-direction: column; }
            .navigation { flex-direction: column; }
        }
"""


# ---------------------------------------------------------------------------
# JavaScript
# ---------------------------------------------------------------------------

JS = """
        // ===== SIDEBAR & NAVBAR =====
        function toggleMobileSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            sidebar.classList.toggle('mobile-open');
            overlay.classList.toggle('active');
        }

        function toggleAccountMenu() {
            const dropdown = document.getElementById('accountDropdown');
            dropdown.classList.toggle('active');
        }

        document.addEventListener('click', (e) => {
            const accountMenu = document.querySelector('.account-menu');
            const dropdown = document.getElementById('accountDropdown');
            if (accountMenu && dropdown && !accountMenu.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });

        function toggleSubmenu(event, submenuId) {
            event.preventDefault();
            const link = event.currentTarget;
            const submenu = document.getElementById(submenuId);
            link.classList.toggle('expanded');
            submenu.classList.toggle('expanded');
        }

        // ===== COURSE LOGIC =====
        let currentScreen = 0;
        const screens = document.querySelectorAll('.screen');
        const totalScreens = screens.length;

        showScreen(0);

        function showScreen(index) {
            screens.forEach(s => s.classList.remove('active'));
            screens[index].classList.add('active');
            currentScreen = index;
            updateProgress();
            updateNavigation();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function updateProgress() {
            const progress = ((currentScreen + 1) / totalScreens) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            document.getElementById('progressCount').textContent = `${currentScreen + 1} / ${totalScreens}`;
        }

        function updateNavigation() {
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            prevBtn.disabled = currentScreen === 0;
            nextBtn.innerHTML = currentScreen === totalScreens - 1
                ? 'Finish Course'
                : 'Continue <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>';
        }

        function nextScreen() {
            if (currentScreen < totalScreens - 1) {
                showScreen(currentScreen + 1);
            } else {
                document.getElementById('completionBadge').classList.add('show');
                document.getElementById('nextBtn').disabled = true;
            }
        }

        function previousScreen() {
            if (currentScreen > 0) showScreen(currentScreen - 1);
        }

        // Quiz interaction
        document.querySelectorAll('.quiz-option').forEach(option => {
            option.addEventListener('click', function () {
                if (this.classList.contains('answered')) return;
                const isCorrect = this.dataset.correct === 'true';
                const screen = this.closest('.screen');

                screen.querySelectorAll('.quiz-option').forEach(opt => opt.classList.add('answered'));

                if (isCorrect) {
                    this.classList.add('correct');
                } else {
                    this.classList.add('incorrect');
                    screen.querySelectorAll('.quiz-option').forEach(opt => {
                        if (opt.dataset.correct === 'true') opt.classList.add('correct');
                    });
                }

                const explanation = screen.querySelector('.explanation');
                if (explanation) explanation.classList.remove('hidden');
            });
        });

        // Matching/drag-and-drop
        const blanks = document.querySelectorAll('.blank');
        const answerOptions = document.querySelectorAll('.answer-option');
        let draggedAnswer = null;

        answerOptions.forEach(option => {
            option.addEventListener('dragstart', function () {
                draggedAnswer = this;
                this.style.opacity = '0.5';
            });
            option.addEventListener('dragend', function () {
                this.style.opacity = '1';
            });
            option.addEventListener('click', function () {
                if (this.classList.contains('used')) return;
                document.querySelectorAll('.answer-option').forEach(o => o.style.outline = 'none');
                this.style.outline = '3px solid var(--accent-primary)';
                draggedAnswer = this;
            });
        });

        blanks.forEach(blank => {
            blank.addEventListener('dragover', e => { e.preventDefault(); blank.style.borderColor = 'var(--accent-primary)'; });
            blank.addEventListener('dragleave', () => { blank.style.borderColor = ''; });
            blank.addEventListener('drop', function (e) {
                e.preventDefault();
                if (!draggedAnswer || draggedAnswer.classList.contains('used')) return;
                fillBlank(this, draggedAnswer);
            });
            blank.addEventListener('click', function () {
                if (!draggedAnswer || draggedAnswer.classList.contains('used')) return;
                fillBlank(this, draggedAnswer);
                draggedAnswer.style.outline = 'none';
            });
        });

        function fillBlank(blank, source) {
            blank.textContent = source.dataset.answer;
            blank.dataset.userAnswer = source.dataset.answer;
            blank.classList.add('filled');
            blank.style.borderColor = '';
            source.classList.add('used');
            draggedAnswer = null;
            checkMatchingComplete();
        }

        function checkMatchingComplete() {
            const screen = document.querySelector('.matching-screen.active');
            if (!screen) return;
            const allBlanks = screen.querySelectorAll('.blank');
            const allFilled = Array.from(allBlanks).every(b => b.classList.contains('filled'));
            if (allFilled) screen.querySelector('.check-matching-btn').classList.remove('hidden');
        }

        document.querySelectorAll('.check-matching-btn').forEach(btn => {
            btn.addEventListener('click', function () {
                const screen = this.closest('.screen');
                const allBlanks = screen.querySelectorAll('.blank');
                let correct = 0;
                allBlanks.forEach(blank => {
                    if (blank.dataset.userAnswer === blank.dataset.correct) {
                        blank.classList.add('correct');
                        correct++;
                    } else {
                        blank.classList.add('incorrect');
                        blank.textContent = blank.dataset.userAnswer + ' > ' + blank.dataset.correct;
                    }
                });
                const explanation = screen.querySelector('.matching-explanation');
                explanation.querySelector('.explanation-result').textContent =
                    correct === allBlanks.length
                        ? 'Perfect! All answers are correct!'
                        : `You got ${correct} out of ${allBlanks.length} correct. Corrections shown above.`;
                explanation.classList.remove('hidden');
                this.disabled = true;
                this.style.opacity = '0.4';
            });
        });

        document.addEventListener('keydown', e => {
            if (e.key === 'ArrowRight') nextScreen();
            else if (e.key === 'ArrowLeft') previousScreen();
        });
"""


# ---------------------------------------------------------------------------
# HTML shell
# ---------------------------------------------------------------------------

NAVBAR_HTML = """
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
    </nav>"""

SIDEBAR_HTML = """
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
                        <li class="submenu-item"><a href="/emergency-care" class="submenu-link active">Emergency Care</a></li>
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
                    <a href="/encyclopedia" class="nav-link">
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
    </aside>"""


def generate_html(course_data):
    screens_html  = '\n'.join(generate_screen_html(s) for s in course_data['screens'])
    total_screens = len(course_data['screens'])
    quiz_count    = sum(1 for s in course_data['screens'] if s.get('type') == 'quiz')

    theme_name  = course_data.get('themeName',  'Emergency Care')
    course_name = course_data.get('courseName', 'Choking Emergency')
    lesson_name = course_data.get('lessonName', 'Essential First Aid Skills')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioBasics Course Demo - {course_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <style>{CSS}
    </style>
</head>
<body>
{NAVBAR_HTML}
{SIDEBAR_HTML}

    <!-- MAIN CONTENT WRAPPER -->
    <div class="main-wrapper">
        <div class="container">

            <header class="course-header">
                <div class="course-breadcrumb">
                    <span class="breadcrumb-item">{theme_name}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    <span class="breadcrumb-item">{course_name}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                    <span class="breadcrumb-item active">{lesson_name}</span>
                </div>
            </header>

            <div class="progress-container">
                <div class="progress-meta">
                    <span class="progress-label">Progress</span>
                    <span class="progress-count" id="progressCount">1 / {total_screens}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressBar" style="width: 8%"></div>
                </div>
            </div>

            <div id="screensContainer">
                {screens_html}
            </div>

            <div class="navigation">
                <button class="nav-btn" id="prevBtn" onclick="previousScreen()" style="display:flex;align-items:center;justify-content:center;gap:8px;">{SVG_ARROW_LEFT} Back</button>
                <button class="nav-btn" id="nextBtn" onclick="nextScreen()" style="display:flex;align-items:center;justify-content:center;gap:8px;">Continue {SVG_ARROW_RIGHT}</button>
            </div>

            <div class="completion-badge" id="completionBadge">
                <span class="badge-icon">{SVG_MEDAL}</span>
                <h2 class="badge-title">Course Completed!</h2>
                <p class="badge-message">
                    You've completed the {course_name} course.<br>
                    You're now equipped with life-saving knowledge.
                </p>
                <div class="badge-stats">
                    <div class="badge-stat">
                        <span class="stat-value">{total_screens}</span>
                        <span class="stat-label">Lessons</span>
                    </div>
                    <div class="badge-stat">
                        <span class="stat-value">{quiz_count}</span>
                        <span class="stat-label">Quizzes</span>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>{JS}
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    input_path  = r"medicalogy_docs\screens\5-course_test\json_demo.json"
    output_path = r"medicalogy_docs\screens\5-course_test\demo.html"

    print(f"Loading course from: {input_path}")
    course_data = load_course_json(input_path)

    print("Generating HTML...")
    print(f"  - Version:       {course_data['version']}")
    print(f"  - Total screens: {len(course_data['screens'])}")

    html_content = generate_html(course_data)

    print(f"Writing HTML to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Successfully generated {output_path}")
    print("  Open this file in a web browser to view the interactive course demo.")


if __name__ == "__main__":
    main()