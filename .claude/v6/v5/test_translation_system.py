# -*- coding: utf-8 -*-
"""
Test Dynamic Translation System
Verifica se o sistema de tradução dinâmica está funcionando
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[INFO] Testing Dynamic Translation System...")
print()

# Test 1: i18n Manager
print("[TEST 1] i18n Manager Loading...")
try:
    from utils.i18n import i18n
    print(f"  [OK] i18n loaded. Current language: {i18n.current_language}")
    print(f"  [OK] Available languages: {list(i18n.translations.keys())}")
except Exception as e:
    print(f"  [ERROR] {e}")
    sys.exit(1)

# Test 2: Translation Keys
print("\n[TEST 2] Translation Keys...")
test_keys = [
    'tabs.control_tab',
    'ui.bot_status',
    'ui.stopped',
    'ui.detailed_statistics',
    'ui.fish_caught',
    'ui.enable_auto_clean',
    'ui.include_baits_clean',
    'ui.next_clean_in'
]

for lang in ['pt', 'en', 'es', 'ru']:
    print(f"\n  Language: {lang}")
    i18n.set_language(lang)
    for key in test_keys[:4]:  # Test first 4 keys
        text = i18n.get_text(key)
        status = "OK" if text != key else "MISSING"
        # Remove emojis to avoid Windows console issues
        text_safe = text.encode('ascii', 'ignore').decode('ascii')
        print(f"    [{status}] {key}: {text_safe[:30]}")

# Test 3: Widget Registration System
print("\n[TEST 3] Widget Registration System...")
try:
    import tkinter as tk
    from ui.main_window import FishingBotUI

    # Create minimal UI instance
    print("  [INFO] Creating FishingBotUI instance...")
    ui = FishingBotUI()

    # Check if translatable_widgets dict exists
    if hasattr(ui, 'translatable_widgets'):
        print(f"  [OK] translatable_widgets dict exists")
        print(f"  [OK] Categories: {list(ui.translatable_widgets.keys())}")
    else:
        print(f"  [ERROR] translatable_widgets dict not found")

    # Check if register method exists
    if hasattr(ui, 'register_translatable_widget'):
        print(f"  [OK] register_translatable_widget() method exists")
    else:
        print(f"  [ERROR] register_translatable_widget() method not found")

    # Check if update method exists
    if hasattr(ui, 'update_ui_texts'):
        print(f"  [OK] update_ui_texts() method exists")
    else:
        print(f"  [ERROR] update_ui_texts() method not found")

    # Check if any widgets were registered
    total_registered = sum(len(widgets) for widgets in ui.translatable_widgets.values())
    print(f"  [INFO] Total widgets registered: {total_registered}")

    if total_registered > 0:
        print(f"  [OK] Widgets are being registered!")
        for widget_type, widgets in ui.translatable_widgets.items():
            if widgets:
                print(f"    - {widget_type}: {len(widgets)} widgets")
                # Show first 3 widget IDs
                for i, widget_id in enumerate(list(widgets.keys())[:3]):
                    print(f"      {i+1}. {widget_id}")
    else:
        print(f"  [WARN] No widgets registered yet (may need to open UI)")

    # Don't start mainloop, just destroy
    ui.main_window.destroy()
    print(f"  [OK] UI instance created and destroyed successfully")

except Exception as e:
    print(f"  [ERROR] {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check JSON files integrity
print("\n[TEST 4] JSON Files Integrity...")
import json

for lang_code, locale_dir in [('pt', 'pt_BR'), ('en', 'en_US'), ('es', 'es_ES'), ('ru', 'ru_RU')]:
    filepath = os.path.join('locales', locale_dir, 'ui.json')
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        ui_section = data.get('ui', {})
        tabs_section = data.get('tabs', {})

        print(f"  [{lang_code}] {len(ui_section)} ui keys, {len(tabs_section)} tab keys")

        # Check for specific keys
        required_keys = ['bot_status', 'enable_auto_clean', 'include_baits_clean', 'next_clean_in']
        missing = [k for k in required_keys if k not in ui_section]
        if missing:
            print(f"      [WARN] Missing keys: {missing}")
        else:
            print(f"      [OK] All required keys present")

    except Exception as e:
        print(f"  [{lang_code}] [ERROR] {e}")

print("\n[SUMMARY] Translation system testing complete!")
print("[INFO] If all tests passed, the system is ready for dynamic language switching.")
