#!/usr/bin/env python3
"""
BioBasics Course JSON to HTML Converter
Converts course JSON structure into an interactive HTML demonstration.
"""

import json
import sys
from pathlib import Path


def load_course_json(filepath):
    """Load and validate course JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Basic validation
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


def generate_infographic_html(screen_id, content):
    """Generate HTML for an infographic screen."""
    image_html = ""
    if content.get('imageFileName'):
        image_html = f'''
            <div class="infographic-image">
                <img src="{content['imageFileName']}" alt="Educational infographic" />
            </div>
        '''
    
    return f'''
        <div class="screen infographic-screen" id="{screen_id}" data-type="infographic">
            <div class="screen-content">
                <div class="screen-icon">📚</div>
                <h2 class="screen-title">Learn</h2>
                {image_html}
                <div class="summary-text">
                    <p>{content.get('summaryText', '')}</p>
                </div>
            </div>
        </div>
    '''


def generate_multiple_choice_html(screen_id, content):
    """Generate HTML for a multiple choice quiz."""
    options_html = []
    for option in content.get('options', []):
        correct_class = 'correct' if option.get('isCorrect', False) else 'incorrect'
        options_html.append(f'''
            <button class="quiz-option" 
                    data-correct="{str(option.get('isCorrect', False)).lower()}"
                    data-option-id="{option['id']}">
                <span class="option-label">{option['id'].upper()}</span>
                <span class="option-text">{option['text']}</span>
                <span class="option-feedback">
                    <span class="feedback-icon"></span>
                </span>
            </button>
        ''')
    
    explanation = content.get('explanation', '')
    explanation_html = f'''
        <div class="explanation hidden">
            <div class="explanation-icon">💡</div>
            <p>{explanation}</p>
        </div>
    ''' if explanation else ''
    
    return f'''
        <div class="screen quiz-screen" id="{screen_id}" data-type="quiz-mc">
            <div class="screen-content">
                <div class="screen-icon">❓</div>
                <h2 class="screen-title">Quiz Time</h2>
                <div class="question-text">
                    <p>{content.get('questionText', '')}</p>
                </div>
                <div class="quiz-options">
                    {''.join(options_html)}
                </div>
                {explanation_html}
            </div>
        </div>
    '''


def generate_true_false_html(screen_id, content):
    """Generate HTML for a true/false quiz."""
    correct_answer = content.get('correctAnswer', True)
    explanation = content.get('explanation', '')
    
    explanation_html = f'''
        <div class="explanation hidden">
            <div class="explanation-icon">💡</div>
            <p>{explanation}</p>
        </div>
    ''' if explanation else ''
    
    return f'''
        <div class="screen quiz-screen" id="{screen_id}" data-type="quiz-tf">
            <div class="screen-content">
                <div class="screen-icon">✓✗</div>
                <h2 class="screen-title">True or False?</h2>
                <div class="question-text">
                    <p>{content.get('questionText', '')}</p>
                </div>
                <div class="quiz-options tf-options">
                    <button class="quiz-option tf-option" 
                            data-correct="{str(correct_answer).lower()}"
                            data-value="true">
                        <span class="option-label">✓</span>
                        <span class="option-text">True</span>
                        <span class="option-feedback">
                            <span class="feedback-icon"></span>
                        </span>
                    </button>
                    <button class="quiz-option tf-option" 
                            data-correct="{str(not correct_answer).lower()}"
                            data-value="false">
                        <span class="option-label">✗</span>
                        <span class="option-text">False</span>
                        <span class="option-feedback">
                            <span class="feedback-icon"></span>
                        </span>
                    </button>
                </div>
                {explanation_html}
            </div>
        </div>
    '''


def generate_matching_html(screen_id, content):
    """Generate HTML for a matching quiz."""
    sentence = content.get('sentence', '').replace('\n', '<br>')
    correct_answers = content.get('correctAnswers', [])
    wrong_answers = content.get('wrongAnswers', [])
    
    # Combine and create answer options
    all_answers = correct_answers + wrong_answers
    
    # Create blanks in sentence
    for i, answer in enumerate(correct_answers, 1):
        sentence = sentence.replace(f'<{i}>', 
            f'<span class="blank" data-blank-id="{i}" data-correct="{answer}">___________</span>')
    
    # Create draggable answer options
    options_html = []
    for answer in all_answers:
        options_html.append(f'''
            <button class="answer-option" draggable="true" data-answer="{answer}">
                {answer}
            </button>
        ''')
    
    return f'''
        <div class="screen quiz-screen matching-screen" id="{screen_id}" data-type="quiz-match">
            <div class="screen-content">
                <div class="screen-icon">🔗</div>
                <h2 class="screen-title">Fill in the Blanks</h2>
                <div class="question-text">
                    <p class="matching-sentence">{sentence}</p>
                </div>
                <div class="answer-bank">
                    <h3 class="bank-title">Drag answers to fill the blanks:</h3>
                    <div class="answer-options">
                        {''.join(options_html)}
                    </div>
                </div>
                <button class="check-matching-btn hidden">Check Answers</button>
                <div class="explanation matching-explanation hidden">
                    <div class="explanation-icon">💡</div>
                    <p class="explanation-result"></p>
                </div>
            </div>
        </div>
    '''


def generate_screen_html(screen):
    """Generate HTML for a screen based on its type."""
    screen_id = screen['id']
    screen_type = screen['type']
    content = screen['content']
    
    if screen_type == 'infographic':
        return generate_infographic_html(screen_id, content)
    elif screen_type == 'quiz':
        question_type = content.get('questionType')
        if question_type == 'multiple_choice':
            return generate_multiple_choice_html(screen_id, content)
        elif question_type == 'true_false':
            return generate_true_false_html(screen_id, content)
        elif question_type == 'matching':
            return generate_matching_html(screen_id, content)
    
    return f'<div class="screen" id="{screen_id}">Unknown screen type: {screen_type}</div>'


def generate_html(course_data):
    """Generate complete HTML page from course data."""
    screens_html = []
    for screen in course_data['screens']:
        screens_html.append(generate_screen_html(screen))
    
    total_screens = len(course_data['screens'])
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioBasics Course Demo - Choking Emergency</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Crimson+Pro:wght@300;400;600&display=swap" rel="stylesheet">
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
            --success: #00ff88;
            --error: #ff4757;
            --border-radius: 24px;
            --transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        body {{
            font-family: 'Crimson Pro', serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
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
            padding: 40px 20px;
            position: relative;
            z-index: 1;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 60px;
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
        
        .course-title {{
            font-family: 'Space Mono', monospace;
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
            letter-spacing: -2px;
        }}
        
        .course-subtitle {{
            font-size: 1.3rem;
            color: var(--text-secondary);
            font-weight: 300;
        }}
        
        .progress-bar {{
            background: var(--bg-secondary);
            height: 8px;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 40px;
            box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-tertiary));
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 20px;
            position: relative;
            overflow: hidden;
        }}
        
        .progress-fill::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            right: 0;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,0.3),
                transparent
            );
            animation: shimmer 2s infinite;
        }}
        
        @keyframes shimmer {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .screen {{
            background: var(--bg-card);
            border-radius: var(--border-radius);
            padding: 50px 40px;
            margin-bottom: 30px;
            box-shadow: 
                0 20px 60px rgba(0,0,0,0.4),
                0 0 0 1px rgba(255,255,255,0.05);
            display: none;
            animation: slideIn 0.6s ease-out;
            position: relative;
            overflow: hidden;
        }}
        
        .screen::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-tertiary));
        }}
        
        .screen.active {{
            display: block;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .screen-content {{
            position: relative;
            z-index: 1;
        }}
        
        .screen-icon {{
            font-size: 3rem;
            margin-bottom: 20px;
            display: inline-block;
            animation: bounce 2s ease-in-out infinite;
        }}
        
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        .screen-title {{
            font-family: 'Space Mono', monospace;
            font-size: 1.8rem;
            margin-bottom: 30px;
            color: var(--accent-primary);
            letter-spacing: 1px;
        }}
        
        .infographic-image {{
            margin: 30px 0;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}
        
        .infographic-image img {{
            width: 100%;
            height: auto;
            display: block;
            transition: transform 0.4s ease;
        }}
        
        .infographic-image:hover img {{
            transform: scale(1.02);
        }}
        
        .summary-text, .question-text {{
            font-size: 1.2rem;
            line-height: 1.8;
            color: var(--text-secondary);
            margin: 25px 0;
        }}
        
        .quiz-options {{
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin: 30px 0;
        }}
        
        .tf-options {{
            flex-direction: row;
            gap: 20px;
        }}
        
        .quiz-option {{
            background: var(--bg-secondary);
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 20px 25px;
            font-size: 1.1rem;
            color: var(--text-primary);
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            gap: 15px;
            position: relative;
            overflow: hidden;
            font-family: 'Crimson Pro', serif;
        }}
        
        .tf-option {{
            flex: 1;
            justify-content: center;
            font-size: 1.3rem;
        }}
        
        .quiz-option::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s ease;
        }}
        
        .quiz-option:hover {{
            transform: translateX(5px);
            border-color: var(--accent-primary);
            box-shadow: 0 8px 25px rgba(0, 245, 208, 0.2);
        }}
        
        .quiz-option:hover::before {{
            left: 100%;
        }}
        
        .option-label {{
            font-family: 'Space Mono', monospace;
            font-weight: 700;
            font-size: 1.4rem;
            color: var(--accent-tertiary);
            min-width: 40px;
            text-align: center;
        }}
        
        .option-text {{
            flex: 1;
        }}
        
        .option-feedback {{
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .feedback-icon {{
            font-size: 1.5rem;
        }}
        
        .quiz-option.answered {{
            pointer-events: none;
        }}
        
        .quiz-option.correct {{
            background: rgba(0, 255, 136, 0.1);
            border-color: var(--success);
        }}
        
        .quiz-option.correct .option-feedback {{
            opacity: 1;
        }}
        
        .quiz-option.correct .feedback-icon::before {{
            content: '✓';
            color: var(--success);
        }}
        
        .quiz-option.incorrect {{
            background: rgba(255, 71, 87, 0.1);
            border-color: var(--error);
        }}
        
        .quiz-option.incorrect .option-feedback {{
            opacity: 1;
        }}
        
        .quiz-option.incorrect .feedback-icon::before {{
            content: '✗';
            color: var(--error);
        }}
        
        .explanation {{
            background: rgba(0, 245, 208, 0.05);
            border-left: 4px solid var(--accent-primary);
            border-radius: 12px;
            padding: 25px;
            margin-top: 25px;
            animation: fadeIn 0.5s ease;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .explanation-icon {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}
        
        .explanation p {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            line-height: 1.7;
        }}
        
        .hidden {{
            display: none !important;
        }}
        
        /* Matching Quiz Styles */
        .matching-sentence {{
            font-size: 1.3rem;
            line-height: 2;
            margin: 30px 0;
        }}
        
        .blank {{
            display: inline-block;
            min-width: 120px;
            padding: 8px 15px;
            background: var(--bg-secondary);
            border: 2px dashed rgba(0, 245, 208, 0.3);
            border-radius: 8px;
            text-align: center;
            margin: 0 5px;
            transition: var(--transition);
            cursor: pointer;
            position: relative;
        }}
        
        .blank:hover {{
            border-color: var(--accent-primary);
            background: rgba(0, 245, 208, 0.05);
        }}
        
        .blank.filled {{
            background: var(--bg-secondary);
            border-style: solid;
            border-color: var(--accent-primary);
            color: var(--accent-primary);
            font-weight: 600;
        }}
        
        .blank.correct {{
            background: rgba(0, 255, 136, 0.1);
            border-color: var(--success);
            color: var(--success);
        }}
        
        .blank.incorrect {{
            background: rgba(255, 71, 87, 0.1);
            border-color: var(--error);
            color: var(--error);
        }}
        
        .answer-bank {{
            margin: 40px 0;
        }}
        
        .bank-title {{
            font-family: 'Space Mono', monospace;
            font-size: 1rem;
            color: var(--text-muted);
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .answer-options {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }}
        
        .answer-option {{
            background: var(--bg-secondary);
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 12px 20px;
            color: var(--text-primary);
            cursor: grab;
            transition: var(--transition);
            font-family: 'Crimson Pro', serif;
            font-size: 1.1rem;
        }}
        
        .answer-option:hover {{
            transform: scale(1.05);
            border-color: var(--accent-primary);
            box-shadow: 0 5px 15px rgba(0, 245, 208, 0.2);
        }}
        
        .answer-option:active {{
            cursor: grabbing;
        }}
        
        .answer-option.used {{
            opacity: 0.3;
            pointer-events: none;
        }}
        
        .check-matching-btn {{
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border: none;
            border-radius: 12px;
            padding: 15px 40px;
            color: var(--bg-primary);
            font-family: 'Space Mono', monospace;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            margin-top: 30px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .check-matching-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 245, 208, 0.3);
        }}
        
        .matching-explanation {{
            border-left-color: var(--accent-secondary);
            background: rgba(255, 107, 157, 0.05);
        }}
        
        .navigation {{
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-top: 40px;
        }}
        
        .nav-btn {{
            background: var(--bg-secondary);
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 15px 30px;
            color: var(--text-primary);
            font-family: 'Space Mono', monospace;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: var(--transition);
            text-transform: uppercase;
            letter-spacing: 1px;
            flex: 1;
        }}
        
        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        
        .nav-btn:not(:disabled):hover {{
            background: var(--accent-primary);
            color: var(--bg-primary);
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 245, 208, 0.3);
        }}
        
        .completion-badge {{
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, rgba(0, 245, 208, 0.1), rgba(255, 107, 157, 0.1));
            border-radius: var(--border-radius);
            margin-top: 40px;
            display: none;
            animation: fadeIn 0.8s ease;
        }}
        
        .completion-badge.show {{
            display: block;
        }}
        
        .badge-icon {{
            font-size: 5rem;
            margin-bottom: 20px;
            animation: rotate 3s ease-in-out infinite;
        }}
        
        @keyframes rotate {{
            0%, 100% {{ transform: rotate(-5deg); }}
            50% {{ transform: rotate(5deg); }}
        }}
        
        .badge-title {{
            font-family: 'Space Mono', monospace;
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }}
        
        .badge-message {{
            font-size: 1.3rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}
        
        @media (max-width: 768px) {{
            .course-title {{
                font-size: 2.5rem;
            }}
            
            .screen {{
                padding: 30px 25px;
            }}
            
            .tf-options {{
                flex-direction: column;
            }}
            
            .navigation {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1 class="course-title">Choking Emergency</h1>
            <p class="course-subtitle">Essential First Aid Skills</p>
        </header>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressBar" style="width: 0%"></div>
        </div>
        
        <div id="screensContainer">
            {''.join(screens_html)}
        </div>
        
        <div class="navigation">
            <button class="nav-btn" id="prevBtn" onclick="previousScreen()">← Previous</button>
            <button class="nav-btn" id="nextBtn" onclick="nextScreen()">Next →</button>
        </div>
        
        <div class="completion-badge" id="completionBadge">
            <div class="badge-icon">🏆</div>
            <h2 class="badge-title">Course Completed!</h2>
            <p class="badge-message">
                Congratulations! You've completed the Choking Emergency course.<br>
                You're now equipped with life-saving knowledge.
            </p>
        </div>
    </div>
    
    <script>
        let currentScreen = 0;
        const totalScreens = {total_screens};
        const screens = document.querySelectorAll('.screen');
        
        // Initialize first screen
        showScreen(0);
        
        function showScreen(index) {{
            screens.forEach(screen => screen.classList.remove('active'));
            screens[index].classList.add('active');
            
            currentScreen = index;
            updateProgress();
            updateNavigation();
            
            // Reset scroll position
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function updateProgress() {{
            const progress = ((currentScreen + 1) / totalScreens) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
        }}
        
        function updateNavigation() {{
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            prevBtn.disabled = currentScreen === 0;
            
            if (currentScreen === totalScreens - 1) {{
                nextBtn.textContent = 'Finish Course';
            }} else {{
                nextBtn.textContent = 'Next →';
            }}
        }}
        
        function nextScreen() {{
            if (currentScreen < totalScreens - 1) {{
                showScreen(currentScreen + 1);
            }} else {{
                // Show completion badge
                document.getElementById('completionBadge').classList.add('show');
                document.getElementById('nextBtn').disabled = true;
            }}
        }}
        
        function previousScreen() {{
            if (currentScreen > 0) {{
                showScreen(currentScreen - 1);
            }}
        }}
        
        // Quiz interaction handlers
        document.querySelectorAll('.quiz-option').forEach(option => {{
            option.addEventListener('click', function() {{
                if (this.classList.contains('answered')) return;
                
                const isCorrect = this.dataset.correct === 'true';
                const screen = this.closest('.screen');
                
                // Mark all options as answered
                screen.querySelectorAll('.quiz-option').forEach(opt => {{
                    opt.classList.add('answered');
                }});
                
                // Mark this option as correct or incorrect
                if (isCorrect) {{
                    this.classList.add('correct');
                }} else {{
                    this.classList.add('incorrect');
                    // Also highlight the correct answer
                    screen.querySelectorAll('.quiz-option').forEach(opt => {{
                        if (opt.dataset.correct === 'true') {{
                            opt.classList.add('correct');
                        }}
                    }});
                }}
                
                // Show explanation if available
                const explanation = screen.querySelector('.explanation');
                if (explanation) {{
                    explanation.classList.remove('hidden');
                }}
            }});
        }});
        
        // Matching quiz drag and drop
        const blanks = document.querySelectorAll('.blank');
        const answerOptions = document.querySelectorAll('.answer-option');
        
        let draggedAnswer = null;
        
        answerOptions.forEach(option => {{
            option.addEventListener('dragstart', function(e) {{
                draggedAnswer = this;
                this.style.opacity = '0.5';
            }});
            
            option.addEventListener('dragend', function() {{
                this.style.opacity = '1';
            }});
            
            // Also support click to select for mobile
            option.addEventListener('click', function() {{
                if (this.classList.contains('used')) return;
                
                // Remove previous selection
                document.querySelectorAll('.answer-option').forEach(opt => {{
                    opt.style.outline = 'none';
                }});
                
                // Mark as selected
                this.style.outline = '3px solid var(--accent-primary)';
                draggedAnswer = this;
            }});
        }});
        
        blanks.forEach(blank => {{
            blank.addEventListener('dragover', function(e) {{
                e.preventDefault();
                this.style.borderColor = 'var(--accent-primary)';
            }});
            
            blank.addEventListener('dragleave', function() {{
                this.style.borderColor = '';
            }});
            
            blank.addEventListener('drop', function(e) {{
                e.preventDefault();
                if (!draggedAnswer || draggedAnswer.classList.contains('used')) return;
                
                this.textContent = draggedAnswer.dataset.answer;
                this.dataset.userAnswer = draggedAnswer.dataset.answer;
                this.classList.add('filled');
                this.style.borderColor = '';
                
                draggedAnswer.classList.add('used');
                draggedAnswer = null;
                
                // Check if all blanks are filled
                checkMatchingComplete();
            }});
            
            // Click support for mobile
            blank.addEventListener('click', function() {{
                if (!draggedAnswer || draggedAnswer.classList.contains('used')) return;
                
                this.textContent = draggedAnswer.dataset.answer;
                this.dataset.userAnswer = draggedAnswer.dataset.answer;
                this.classList.add('filled');
                
                draggedAnswer.classList.add('used');
                draggedAnswer.style.outline = 'none';
                draggedAnswer = null;
                
                checkMatchingComplete();
            }});
        }});
        
        function checkMatchingComplete() {{
            const screen = document.querySelector('.matching-screen.active');
            if (!screen) return;
            
            const allBlanks = screen.querySelectorAll('.blank');
            const allFilled = Array.from(allBlanks).every(blank => blank.classList.contains('filled'));
            
            if (allFilled) {{
                const checkBtn = screen.querySelector('.check-matching-btn');
                checkBtn.classList.remove('hidden');
            }}
        }}
        
        // Check matching answers button
        document.querySelectorAll('.check-matching-btn').forEach(btn => {{
            btn.addEventListener('click', function() {{
                const screen = this.closest('.screen');
                const allBlanks = screen.querySelectorAll('.blank');
                let correctCount = 0;
                
                allBlanks.forEach(blank => {{
                    const userAnswer = blank.dataset.userAnswer;
                    const correctAnswer = blank.dataset.correct;
                    
                    if (userAnswer === correctAnswer) {{
                        blank.classList.add('correct');
                        correctCount++;
                    }} else {{
                        blank.classList.add('incorrect');
                        blank.textContent = userAnswer + ' ✗ → ' + correctAnswer;
                    }}
                }});
                
                // Show result
                const explanation = screen.querySelector('.matching-explanation');
                const result = explanation.querySelector('.explanation-result');
                
                if (correctCount === allBlanks.length) {{
                    result.textContent = '🎉 Perfect! All answers are correct!';
                }} else {{
                    result.textContent = `You got ${{correctCount}} out of ${{allBlanks.length}} correct. The correct answers are shown above.`;
                }}
                
                explanation.classList.remove('hidden');
                this.disabled = true;
                this.style.opacity = '0.5';
            }});
        }});
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'ArrowRight') {{
                nextScreen();
            }} else if (e.key === 'ArrowLeft') {{
                previousScreen();
            }}
        }});
    </script>
</body>
</html>
'''
    
    return html


def main():
    """Main execution function."""
    # HARDCODED PATHS - Change these to match your file locations
    input_path = r"test\5-course_test\json_demo.json"  # Path to your course JSON file
    output_path = r"test\5-course_test\course_demo.html"  # Where to save the generated HTML
    
    print(f"Loading course from: {input_path}")
    course_data = load_course_json(input_path)
    
    print(f"Generating HTML...")
    print(f"  - Version: {course_data['version']}")
    print(f"  - Total screens: {len(course_data['screens'])}")
    
    html_content = generate_html(course_data)
    
    print(f"Writing HTML to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Successfully generated {output_path}")
    print(f"  Open this file in a web browser to view the interactive course demo.")


if __name__ == "__main__":
    main()