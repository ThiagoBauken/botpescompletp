#!/usr/bin/env python3
"""
Test script for verifying bot components
"""

import os
import cv2
import numpy as np
import mss
import time
import pyautogui

def test_templates():
    """Test if templates are loading correctly"""
    print("\n🔍 Testing Template Loading...")
    print("="*50)

    templates_folder = "templates"
    if not os.path.exists(templates_folder):
        templates_folder = "../templates"

    if not os.path.exists(templates_folder):
        print("❌ Templates folder not found!")
        return False

    critical = ['catch.png', 'VARANOBAUCI.png', 'enbausi.png', 'varaquebrada.png']
    templates_found = []

    for template_file in os.listdir(templates_folder):
        if template_file.endswith('.png'):
            template_path = os.path.join(templates_folder, template_file)
            template = cv2.imread(template_path)

            if template is not None:
                h, w = template.shape[:2]
                if template_file in critical:
                    print(f"  ✅ Critical: {template_file} ({w}x{h})")
                else:
                    print(f"  📋 Template: {template_file} ({w}x{h})")
                templates_found.append(template_file)

    print(f"\nTotal templates found: {len(templates_found)}")

    # Check critical templates
    for critical_template in critical:
        if critical_template not in templates_found:
            print(f"  ❌ Missing critical template: {critical_template}")
            return False

    print("✅ All critical templates found!")
    return True

def test_screen_capture():
    """Test screen capture with MSS"""
    print("\n📸 Testing Screen Capture...")
    print("="*50)

    try:
        sct = mss.mss()

        # Capture full screen
        screenshot = sct.grab(sct.monitors[1])
        img = np.array(screenshot)

        h, w = img.shape[:2]
        print(f"  ✅ Screen captured: {w}x{h}")

        # Test conversion to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        print(f"  ✅ Grayscale conversion successful")

        return True

    except Exception as e:
        print(f"  ❌ Screen capture failed: {e}")
        return False

def test_template_matching():
    """Test template matching on current screen"""
    print("\n🎯 Testing Template Detection...")
    print("="*50)

    try:
        # Load catch template
        template_path = "templates/catch.png"
        if not os.path.exists(template_path):
            template_path = "../templates/catch.png"

        if not os.path.exists(template_path):
            print("  ❌ catch.png not found!")
            return False

        template = cv2.imread(template_path)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Capture screen
        sct = mss.mss()
        screenshot = sct.grab(sct.monitors[1])
        img = np.array(screenshot)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

        # Template matching
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"  📊 Match confidence: {max_val:.3f}")
        print(f"  📍 Best match location: {max_loc}")

        if max_val >= 0.7:
            print("  ✅ Template would be detected (confidence >= 0.7)")
        else:
            print("  ⚠️ Template not detected (confidence < 0.7)")
            print("  💡 This is normal if game is not running or fish not on screen")

        return True

    except Exception as e:
        print(f"  ❌ Template matching failed: {e}")
        return False

def test_mouse_control():
    """Test mouse control"""
    print("\n🖱️ Testing Mouse Control...")
    print("="*50)

    try:
        # Get current position
        current_pos = pyautogui.position()
        print(f"  📍 Current position: {current_pos}")

        # Test mouse movement (small movement)
        pyautogui.moveRel(10, 0, duration=0.1)
        pyautogui.moveRel(-10, 0, duration=0.1)
        print(f"  ✅ Mouse movement successful")

        # Test click (non-intrusive)
        print(f"  💡 Click test skipped (to avoid unwanted actions)")

        return True

    except Exception as e:
        print(f"  ❌ Mouse control failed: {e}")
        return False

def test_keyboard_control():
    """Test keyboard control"""
    print("\n⌨️ Testing Keyboard Control...")
    print("="*50)

    try:
        import keyboard

        # Test if keyboard module is available
        print(f"  ✅ Keyboard module available")

        # Test key press simulation
        print(f"  💡 Key press test skipped (to avoid unwanted actions)")

        return True

    except ImportError:
        print(f"  ❌ Keyboard module not installed")
        print(f"  💡 Run: pip install keyboard")
        return False
    except Exception as e:
        print(f"  ❌ Keyboard control failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration...")
    print("="*50)

    config_paths = [
        "config/config.json",
        "config/default_config.json",
        "../config.json"
    ]

    config_found = False
    for path in config_paths:
        if os.path.exists(path):
            print(f"  ✅ Config found: {path}")
            config_found = True

    if not config_found:
        print("  ⚠️ No config file found (will use defaults)")

    return True

def main():
    """Run all tests"""
    print("\n🧪 FISHING BOT v4.0 - COMPONENT TEST")
    print("="*60)

    tests = [
        ("Templates", test_templates),
        ("Screen Capture", test_screen_capture),
        ("Template Matching", test_template_matching),
        ("Mouse Control", test_mouse_control),
        ("Keyboard Control", test_keyboard_control),
        ("Configuration", test_config)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    all_passed = True
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}: {name}")
        if not success:
            all_passed = False

    print("="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Bot should work correctly!")
    else:
        print("⚠️ Some tests failed - Check the issues above")

    print("\nTo run the bot:")
    print("  python fishing_bot_simple.py")
    print("\nOr to run the full UI version:")
    print("  python main.py")

if __name__ == "__main__":
    main()