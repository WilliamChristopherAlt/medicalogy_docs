"""
Korean Reading Trainer - Brute force letter/word recognition
User types romanization only. Progress tracked per item.
"""

import json
import random
from datetime import datetime
from pathlib import Path

PROGRESS_FILE = Path(__file__).parent / "korean_progress.json"

# ============================================================
# LEVEL DEFINITIONS
# ============================================================

LEVELS = {
    1: {
        "name": "Basic Vowels",
        "items": [
            ("ㅏ", "a"), ("ㅓ", "eo"), ("ㅗ", "o"), ("ㅜ", "u"), ("ㅡ", "eu"), ("ㅣ", "i"),
            ("ㅐ", "ae"), ("ㅔ", "e"), ("ㅑ", "ya"), ("ㅕ", "yeo"), ("ㅛ", "yo"), ("ㅠ", "yu"),
            ("ㅒ", "yae"), ("ㅖ", "ye"), ("ㅘ", "wa"), ("ㅙ", "wae"), ("ㅚ", "oe"), ("ㅝ", "wo"),
            ("ㅞ", "we"), ("ㅟ", "wi"), ("ㅢ", "ui"),
        ]
    },
    2: {
        "name": "Basic Consonants", 
        "items": [
            ("ㄱ", "g"), ("ㄴ", "n"), ("ㄷ", "d"), ("ㄹ", "r"), ("ㅁ", "m"),
            ("ㅂ", "b"), ("ㅅ", "s"), ("ㅇ", "ng"), ("ㅈ", "j"), ("ㅎ", "h"),
        ]
    },
    3: {
        "name": "Advanced Consonants",
        "items": [
            ("ㅊ", "ch"), ("ㅋ", "k"), ("ㅌ", "t"), ("ㅍ", "p"),
            ("ㄲ", "kk"), ("ㄸ", "tt"), ("ㅃ", "pp"), ("ㅆ", "ss"), ("ㅉ", "jj"),
        ]
    },
}

# For syllable generation (levels 4+)
INITIALS = [
    ("ㄱ", "g"), ("ㄴ", "n"), ("ㄷ", "d"), ("ㄹ", "r"), ("ㅁ", "m"),
    ("ㅂ", "b"), ("ㅅ", "s"), ("ㅇ", ""), ("ㅈ", "j"), ("ㅎ", "h"),
    ("ㅊ", "ch"), ("ㅋ", "k"), ("ㅌ", "t"), ("ㅍ", "p"),
]

MEDIALS = [
    ("ㅏ", "a"), ("ㅓ", "eo"), ("ㅗ", "o"), ("ㅜ", "u"), ("ㅡ", "eu"), ("ㅣ", "i"),
    ("ㅐ", "ae"), ("ㅔ", "e"), ("ㅑ", "ya"), ("ㅕ", "yeo"), ("ㅛ", "yo"), ("ㅠ", "yu"),
]

FINALS = [
    ("", ""), ("ㄱ", "k"), ("ㄴ", "n"), ("ㄷ", "t"), ("ㄹ", "l"), 
    ("ㅁ", "m"), ("ㅂ", "p"), ("ㅇ", "ng"),
]

# Unicode composition
INITIAL_MAP = {
    "ㄱ": 0, "ㄲ": 1, "ㄴ": 2, "ㄷ": 3, "ㄸ": 4, "ㄹ": 5, "ㅁ": 6, "ㅂ": 7, "ㅃ": 8,
    "ㅅ": 9, "ㅆ": 10, "ㅇ": 11, "ㅈ": 12, "ㅉ": 13, "ㅊ": 14, "ㅋ": 15, "ㅌ": 16, "ㅍ": 17, "ㅎ": 18
}
MEDIAL_MAP = {
    "ㅏ": 0, "ㅐ": 1, "ㅑ": 2, "ㅒ": 3, "ㅓ": 4, "ㅔ": 5, "ㅕ": 6, "ㅖ": 7, "ㅗ": 8,
    "ㅘ": 9, "ㅙ": 10, "ㅚ": 11, "ㅛ": 12, "ㅜ": 13, "ㅝ": 14, "ㅞ": 15, "ㅟ": 16, "ㅠ": 17,
    "ㅡ": 18, "ㅢ": 19, "ㅣ": 20
}
FINAL_MAP = {
    "": 0, "ㄱ": 1, "ㄲ": 2, "ㄳ": 3, "ㄴ": 4, "ㄵ": 5, "ㄶ": 6, "ㄷ": 7, "ㄹ": 8,
    "ㄺ": 9, "ㄻ": 10, "ㄼ": 11, "ㄽ": 12, "ㄾ": 13, "ㄿ": 14, "ㅀ": 15, "ㅁ": 16,
    "ㅂ": 17, "ㅄ": 18, "ㅅ": 19, "ㅆ": 20, "ㅇ": 21, "ㅈ": 22, "ㅊ": 23, "ㅋ": 24,
    "ㅌ": 25, "ㅍ": 26, "ㅎ": 27
}


def compose_syllable(initial_k, medial_k, final_k=""):
    """Compose Korean syllable from jamo components."""
    i = INITIAL_MAP.get(initial_k)
    m = MEDIAL_MAP.get(medial_k)
    f = FINAL_MAP.get(final_k, 0)
    if i is None or m is None:
        return None
    return chr(0xAC00 + (i * 21 + m) * 28 + f)


def generate_syllable():
    """Generate random syllable with romanization."""
    init_k, init_r = random.choice(INITIALS)
    med_k, med_r = random.choice(MEDIALS)
    fin_k, fin_r = random.choice(FINALS)
    
    syl = compose_syllable(init_k, med_k, fin_k)
    if syl is None:
        return generate_syllable()
    return (syl, init_r + med_r + fin_r)


def generate_word(num_syllables):
    """Generate random word with romanization."""
    korean, roman = "", ""
    for _ in range(num_syllables):
        s_k, s_r = generate_syllable()
        korean += s_k
        roman += s_r
    return (korean, roman)


def generate_level_items(level_num, count=15):
    """Generate items for levels 4+."""
    items = []
    seen = set()
    
    while len(items) < count:
        if level_num == 4:
            k, r = generate_syllable()
        elif level_num == 5:
            k, r = generate_word(2)
        elif level_num == 6:
            k, r = generate_word(3)
        elif level_num == 7:
            w1_k, w1_r = generate_word(random.randint(1, 2))
            w2_k, w2_r = generate_word(random.randint(1, 2))
            k, r = f"{w1_k} {w2_k}", f"{w1_r} {w2_r}"
        elif level_num == 8:
            words = [generate_word(random.randint(1, 2)) for _ in range(3)]
            k = " ".join(w[0] for w in words)
            r = " ".join(w[1] for w in words)
        else:
            num_words = min(level_num - 5, 5)
            words = [generate_word(random.randint(1, 3)) for _ in range(num_words)]
            k = " ".join(w[0] for w in words)
            r = " ".join(w[1] for w in words)
        
        if k not in seen:
            seen.add(k)
            items.append([k, r])
    
    return items


def get_level_name(level_num):
    """Get display name for level."""
    if level_num <= 3:
        return LEVELS[level_num]["name"]
    names = {
        4: "Syllables",
        5: "2-Syllable Words",
        6: "3-Syllable Words",
        7: "2-Word Phrases",
        8: "3-Word Phrases",
    }
    return names.get(level_num, f"Sentences (Level {level_num})")


# ============================================================
# PROGRESS MANAGEMENT
# ============================================================

def create_new_progress():
    """Create fresh progress file."""
    progress = {
        "created": datetime.now().isoformat(),
        "current_level": 1,
        "levels": {},
        "history": []
    }
    
    # Init levels 1-3 with predefined items
    for lvl in [1, 2, 3]:
        progress["levels"][str(lvl)] = {
            "name": LEVELS[lvl]["name"],
            "items": [[k, r] for k, r in LEVELS[lvl]["items"]],
            "stats": {k: {"streak": 0, "correct": 0, "total": 0} 
                     for k, r in LEVELS[lvl]["items"]}
        }
    
    save_progress(progress)
    print(f"✨ Created new progress file")
    return progress


def load_progress():
    """Load or create progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return create_new_progress()


def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def ensure_level(progress, level_num):
    """Ensure level exists in progress, generate if needed."""
    lvl_key = str(level_num)
    if lvl_key not in progress["levels"]:
        if level_num <= 3:
            items = [[k, r] for k, r in LEVELS[level_num]["items"]]
            name = LEVELS[level_num]["name"]
        else:
            items = generate_level_items(level_num)
            name = get_level_name(level_num)
        
        progress["levels"][lvl_key] = {
            "name": name,
            "items": items,
            "stats": {item[0]: {"streak": 0, "correct": 0, "total": 0} for item in items}
        }
        save_progress(progress)
    return progress["levels"][lvl_key]


# ============================================================
# GAME LOGIC
# ============================================================

def get_level_summary(level_data):
    """Calculate level statistics."""
    items = level_data["items"]
    stats = level_data["stats"]
    
    total = len(items)
    mastered = sum(1 for k, r in items if stats.get(k, {}).get("streak", 0) >= 3)
    
    total_correct = sum(s.get("correct", 0) for s in stats.values())
    total_attempts = sum(s.get("total", 0) for s in stats.values())
    accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
    
    return {
        "total": total,
        "mastered": mastered,
        "accuracy": accuracy,
        "attempts": total_attempts
    }


def is_level_complete(level_data):
    """Level complete when ALL items mastered (3 streak each)."""
    items = level_data["items"]
    stats = level_data["stats"]
    return all(stats.get(k, {}).get("streak", 0) >= 3 for k, r in items)


def pick_item(level_data):
    """Pick next item - prioritize non-mastered, weight by fewer attempts."""
    items = level_data["items"]
    stats = level_data["stats"]
    
    # Get non-mastered items
    non_mastered = []
    for korean, roman in items:
        s = stats.get(korean, {"streak": 0, "total": 0})
        if s["streak"] < 3:
            non_mastered.append((korean, roman, s["total"]))
    
    if not non_mastered:
        # All mastered - shouldn't happen if level_complete check is done first
        item = random.choice(items)
        return item[0], item[1]
    
    # Weight: items with fewer attempts get shown more
    weights = [1.0 / (attempts + 1) for _, _, attempts in non_mastered]
    total_w = sum(weights)
    weights = [w / total_w for w in weights]
    
    idx = random.choices(range(len(non_mastered)), weights=weights)[0]
    return non_mastered[idx][0], non_mastered[idx][1]


def record_attempt(progress, level_num, korean, is_correct):
    """Record an attempt and update stats."""
    lvl_key = str(level_num)
    stats = progress["levels"][lvl_key]["stats"]
    
    if korean not in stats:
        stats[korean] = {"streak": 0, "correct": 0, "total": 0}
    
    s = stats[korean]
    s["total"] += 1
    if is_correct:
        s["correct"] += 1
        s["streak"] += 1
    else:
        s["streak"] = 0
    
    # Log to history
    progress["history"].append({
        "level": level_num,
        "korean": korean,
        "correct": is_correct,
        "timestamp": datetime.now().isoformat()
    })
    
    save_progress(progress)
    return s["streak"]


# ============================================================
# UI
# ============================================================

def show_summary(level_data, level_num):
    """Display level summary."""
    summary = get_level_summary(level_data)
    print("\n" + "=" * 50)
    print(f"  📊 Level {level_num}: {level_data['name']}")
    print("=" * 50)
    print(f"  Mastered: {summary['mastered']}/{summary['total']}")
    print(f"  Accuracy: {summary['accuracy']:.1f}%")
    print(f"  Attempts: {summary['attempts']}")
    if summary['mastered'] == summary['total']:
        print("  ✅ LEVEL COMPLETE!")
    else:
        remaining = summary['total'] - summary['mastered']
        print(f"  Remaining: {remaining} items need 3-streak")
    print("=" * 50)


def show_card(korean, streak):
    """Display flashcard."""
    flames = "🔥" * min(streak, 3) if streak > 0 else "   "
    print(f"\n  {flames} Streak: {streak}/3")
    print("  " + "-" * 30)
    print(f"\n       {korean}\n")
    print("  " + "-" * 30)


def show_level_menu(progress):
    """Show level selection menu."""
    print("\n" + "=" * 50)
    print("  📋 LEVEL SELECT")
    print("=" * 50)
    
    for lvl in range(1, 10):
        name = get_level_name(lvl)
        lvl_key = str(lvl)
        
        if lvl_key in progress["levels"]:
            level_data = progress["levels"][lvl_key]
            summary = get_level_summary(level_data)
            status = "✅" if summary["mastered"] == summary["total"] else f"{summary['mastered']}/{summary['total']}"
        else:
            status = "🔒"
        
        marker = "→" if lvl == progress["current_level"] else " "
        print(f"  {marker} {lvl}. {name} [{status}]")
    
    print()
    print("  Enter 1-9 to select level (resets that level)")
    print("  Enter 0 to quit")
    print("  Press Enter to continue practicing")
    print("=" * 50)


def select_level(progress, level_num):
    """Select a level - resets that level's data."""
    lvl_key = str(level_num)
    
    # Generate/reset level data
    if level_num <= 3:
        items = [[k, r] for k, r in LEVELS[level_num]["items"]]
        name = LEVELS[level_num]["name"]
    else:
        items = generate_level_items(level_num)
        name = get_level_name(level_num)
    
    progress["levels"][lvl_key] = {
        "name": name,
        "items": items,
        "stats": {item[0]: {"streak": 0, "correct": 0, "total": 0} for item in items}
    }
    
    progress["current_level"] = level_num
    save_progress(progress)
    
    print(f"\n  ✨ Level {level_num} reset! Starting fresh...")
    return progress


def main():
    print("\n" + "=" * 50)
    print("  🇰🇷 KOREAN READING TRAINER")
    print("=" * 50)
    print("  Type the romanization for each character/word")
    print("  Master each item with 3 correct answers in a row")
    print("  Master all items to advance to next level")
    print()
    print("  Type 0 to open level menu / quit")
    print("=" * 50)
    
    progress = load_progress()
    level_num = progress["current_level"]
    
    level_data = ensure_level(progress, level_num)
    show_summary(level_data, level_num)
    input("\n  Press Enter to start...")
    
    while True:
        level_data = ensure_level(progress, level_num)
        
        # Check level completion
        if is_level_complete(level_data):
            print("\n" + "=" * 50)
            print(f"  🎉 LEVEL {level_num} COMPLETE! 🎉")
            print("=" * 50)
            
            level_num += 1
            progress["current_level"] = level_num
            save_progress(progress)
            
            level_data = ensure_level(progress, level_num)
            show_summary(level_data, level_num)
            input("\n  Press Enter for next level...")
            continue
        
        # Pick and show item
        korean, romanization = pick_item(level_data)
        streak = level_data["stats"].get(korean, {}).get("streak", 0)
        
        show_card(korean, streak)
        
        user_input = input("  > ").strip().lower()
        
        # Check for menu (0)
        if user_input == '0':
            show_level_menu(progress)
            choice = input("  > ").strip()
            if choice == '0':
                print("\n  안녕히 가세요! 👋\n")
                show_summary(level_data, level_num)
                break
            elif choice.isdigit() and 1 <= int(choice) <= 20:
                new_level = int(choice)
                progress = select_level(progress, new_level)
                level_num = new_level
                level_data = progress["levels"][str(level_num)]
                show_summary(level_data, level_num)
            continue
        
        # Check answer
        correct = user_input == romanization.lower()
        new_streak = record_attempt(progress, level_num, korean, correct)
        
        # Update local reference
        level_data = progress["levels"][str(level_num)]
        
        if correct:
            if new_streak >= 3:
                print(f"  ✅ Correct! 🌟 MASTERED!")
            else:
                print(f"  ✅ Correct! ({new_streak}/3)")
        else:
            print(f"  ❌ Wrong!")
            print(f"     Answer: {romanization}")


if __name__ == "__main__":
    main()
