# -*- coding: utf-8 -*-
"""
Fix ALL emoji print statements in main_window.py
Replace emojis with ASCII equivalents for Windows console compatibility
"""

import re

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_emoji_prints(content):
    """Replace all emoji characters in print statements with ASCII"""

    replacements = [
        # Module-level prints
        ('print("⚠️', 'print("[WARN]'),
        ('print("✅', 'print("[OK]'),
        ('print("❌', 'print("[ERROR]'),
        ('print("🔧', 'print("[CONFIG]'),
        ('print("💾', 'print("[SAVE]'),
        ('print("🔄', 'print("[RELOAD]'),
        ('print("🧪', 'print("[TEST]'),
        ('print("📊', 'print("[INFO]'),
        ('print("🎣', 'print("[FISHING]'),
        ('print("🍖', 'print("[FEED]'),
        ('print("🧹', 'print("[CLEAN]'),
        ('print("🔌', 'print("[ARDUINO]'),
        ('print("🐟', 'print("[CATCH]'),
        ('print("🎮', 'print("[GAME]'),
        ('print("📖', 'print("[DOC]'),
        ('print("🎯', 'print("[TARGET]'),

        # Format strings
        ('print(f"⚠️', 'print(f"[WARN]'),
        ('print(f"✅', 'print(f"[OK]'),
        ('print(f"❌', 'print(f"[ERROR]'),
        ('print(f"🔧', 'print(f"[CONFIG]'),
        ('print(f"💾', 'print(f"[SAVE]'),
        ('print(f"🔄', 'print(f"[RELOAD]'),
        ('print(f"🧪', 'print(f"[TEST]'),
        ('print(f"📊', 'print(f"[INFO]'),
        ('print(f"🎣', 'print(f"[FISHING]'),
        ('print(f"🍖', 'print(f"[FEED]'),
        ('print(f"🧹', 'print(f"[CLEAN]'),
        ('print(f"🔌', 'print(f"[ARDUINO]'),
        ('print(f"🐟', 'print(f"[CATCH]'),
        ('print(f"🎮', 'print(f"[GAME]'),
        ('print(f"📖', 'print(f"[DOC]'),
        ('print(f"🎯', 'print(f"[TARGET]'),
    ]

    count = 0
    for old, new in replacements:
        if old in content:
            occurrences = content.count(old)
            content = content.replace(old, new)
            count += occurrences
            print(f"  [OK] Replaced {occurrences} occurrences")

    return content, count

def main():
    print("[INFO] Fixing ALL emoji prints in main_window.py...")

    filepath = r"c:\Users\Thiago\Desktop\v5\ui\main_window.py"
    content = read_file(filepath)

    print(f"[INFO] File size: {len(content)} bytes")
    print(f"[INFO] Applying replacements...")

    content, count = fix_emoji_prints(content)

    write_file(filepath, content)
    print(f"\n[OK] Fixed {count} emoji print statements!")
    print(f"[INFO] File saved: {filepath}")

if __name__ == '__main__':
    main()
