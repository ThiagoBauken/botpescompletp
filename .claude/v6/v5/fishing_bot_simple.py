#!/usr/bin/env python3
"""
🎣 Simplified Fishing Bot v4.0
Clean, working implementation based on the functional logic from botpesca.py
"""

import time
import threading
import cv2
import numpy as np
import mss
import pyautogui
import keyboard
import os
import json
from enum import Enum
from typing import Optional, Dict, Any

class BotState(Enum):
    """Bot states"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    FISHING = "fishing"

class SimpleFishingBot:
    """
    Simplified, clean fishing bot implementation
    Based on the working logic from botpesca.py
    """

    def __init__(self):
        """Initialize the bot with minimal configuration"""
        print("🎣 Initializing Simple Fishing Bot v4.0...")

        # Core state
        self.state = BotState.STOPPED
        self.running = False
        self.paused = False
        self.licensed = True  # Skip license check for testing

        # Threading
        self.fishing_thread = None
        self.stop_event = threading.Event()

        # Statistics
        self.stats = {
            'fish_caught': 0,
            'session_start': 0,
            'last_catch': 0,
            'cycles': 0
        }

        # Configuration
        self.config = self.load_config()

        # Template cache
        self.templates = {}
        self.load_templates()

        # Screen capture
        self.sct = mss.mss()

        # Anti-detection
        pyautogui.MINIMUM_DURATION = 0.1
        pyautogui.MINIMUM_SLEEP = 0.05
        pyautogui.PAUSE = 0.01

        print("✅ Bot initialized successfully!")

    def load_config(self) -> Dict[str, Any]:
        """Load configuration with defaults"""
        default_config = {
            'cycle_timeout': 120,
            'rapid_phase_duration': 7.5,
            'click_interval': 0.1,
            'movement_duration': 1.5,
            'initial_hold_time': 1.6,
            'template_confidence': {
                'catch': 0.7,
                'VARANOBAUCI': 0.8,
                'enbausi': 0.7,
                'varaquebrada': 0.7
            },
            'screen_region': None  # Full screen by default
        }

        # Try to load user config
        config_path = "fishing_bot_v4/config/config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    print(f"✅ Loaded config from {config_path}")
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")

        return default_config

    def load_templates(self):
        """Load all templates from templates folder"""
        templates_folder = "templates"
        if not os.path.exists(templates_folder):
            print("❌ Templates folder not found!")
            return

        # Critical templates
        critical = ['catch.png', 'VARANOBAUCI.png', 'enbausi.png', 'varaquebrada.png']

        for template_file in os.listdir(templates_folder):
            if template_file.endswith('.png'):
                template_path = os.path.join(templates_folder, template_file)
                template = cv2.imread(template_path)

                if template is not None:
                    # Convert to grayscale for better matching
                    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                    self.templates[template_file] = template_gray

                    if template_file in critical:
                        print(f"  ✅ Critical template loaded: {template_file}")
                    else:
                        print(f"  📋 Template loaded: {template_file}")

        print(f"✅ Loaded {len(self.templates)} templates")

    def detect_template(self, template_name: str, confidence: float = None) -> tuple:
        """
        Detect a template on screen using OpenCV
        Returns (found, confidence_value, position)
        """
        if template_name not in self.templates:
            # Try with .png extension
            if f"{template_name}.png" in self.templates:
                template_name = f"{template_name}.png"
            else:
                return False, 0.0, None

        try:
            # Capture screen
            if self.config['screen_region']:
                region = self.config['screen_region']
                screenshot = self.sct.grab(region)
            else:
                screenshot = self.sct.grab(self.sct.monitors[1])

            # Convert to numpy array and grayscale
            img = np.array(screenshot)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            # Get template
            template = self.templates[template_name]

            # Template matching
            result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Check confidence
            if confidence is None:
                base_name = template_name.replace('.png', '')
                confidence = self.config['template_confidence'].get(base_name, 0.7)

            if max_val >= confidence:
                return True, max_val, max_loc

            return False, max_val, None

        except Exception as e:
            print(f"❌ Error detecting template {template_name}: {e}")
            return False, 0.0, None

    def start(self):
        """Start the bot - based on botpesca.py F9 logic"""
        if not self.licensed:
            print("❌ Bot not licensed!")
            return

        if self.running:
            print("⚠️ Bot already running!")
            return

        print("\n⚡ STARTING FISHING BOT...")
        print("="*50)

        # Capture initial mouse position
        initial_pos = pyautogui.position()
        print(f"📍 Initial position captured: {initial_pos}")

        # Start bot
        self.running = True
        self.paused = False
        self.state = BotState.RUNNING
        self.stats['session_start'] = time.time()

        # Start fishing thread
        self.stop_event.clear()
        self.fishing_thread = threading.Thread(target=self.fishing_loop, daemon=True)
        self.fishing_thread.start()

        print("✅ Bot started successfully!")

    def stop(self):
        """Stop the bot - F2"""
        if not self.running:
            print("⚠️ Bot not running!")
            return

        print("🛑 Stopping bot...")

        # Signal stop
        self.running = False
        self.paused = False
        self.stop_event.set()

        # Release all keys/buttons
        pyautogui.keyUp('a')
        pyautogui.keyUp('d')
        pyautogui.mouseUp()

        # Wait for thread
        if self.fishing_thread and self.fishing_thread.is_alive():
            self.fishing_thread.join(timeout=5)

        self.state = BotState.STOPPED

        # Show stats
        self.show_stats()
        print("✅ Bot stopped!")

    def pause(self):
        """Pause/Resume the bot - F1"""
        if not self.running:
            print("⚠️ Bot not running!")
            return

        self.paused = not self.paused

        if self.paused:
            print("⏸️ Bot paused")
            self.state = BotState.PAUSED
        else:
            print("▶️ Bot resumed")
            self.state = BotState.RUNNING

    def fishing_loop(self):
        """
        Main fishing loop - based on botpesca.py working logic
        """
        print("🔄 Fishing loop started...")

        while self.running and not self.stop_event.is_set():
            try:
                # Check if paused
                if self.paused:
                    time.sleep(0.5)
                    continue

                # Start fishing cycle
                self.stats['cycles'] += 1
                print(f"\n🎣 Starting fishing cycle #{self.stats['cycles']}...")

                # Execute complete fishing cycle
                fish_caught = self.execute_fishing_cycle()

                if fish_caught:
                    self.stats['fish_caught'] += 1
                    self.stats['last_catch'] = time.time()
                    print(f"🐟 Fish caught! Total: {self.stats['fish_caught']}")
                else:
                    print("⏰ Cycle completed without catch")

                # Small pause between cycles
                time.sleep(0.5)

            except Exception as e:
                print(f"❌ Error in fishing loop: {e}")
                time.sleep(2)

        print("🔄 Fishing loop ended")

    def execute_fishing_cycle(self) -> bool:
        """
        Execute complete fishing cycle - EXACT logic from botpesca.py
        Returns True if fish was caught
        """
        try:
            cycle_start = time.time()
            timeout = self.config['cycle_timeout']

            # PHASE 1: Start fishing (right click for 1.6s)
            print("  🎣 Phase 1: Starting fishing (right click 1.6s)...")
            pyautogui.mouseDown(button='right')
            time.sleep(self.config['initial_hold_time'])
            pyautogui.mouseUp(button='right')

            # PHASE 2: Rapid phase (7.5s of clicks)
            print("  ⚡ Phase 2: Rapid clicking (7.5s)...")
            if self.execute_rapid_phase():
                return True

            # PHASE 3: Slow phase (A/D + clicks until timeout)
            print("  🐢 Phase 3: Movement phase (A/D + clicks)...")
            if self.execute_slow_phase(cycle_start, timeout):
                return True

            print("  ⏰ Timeout reached")
            return False

        except Exception as e:
            print(f"  ❌ Error in fishing cycle: {e}")
            # Release all inputs
            pyautogui.keyUp('a')
            pyautogui.keyUp('d')
            pyautogui.mouseUp()
            return False

    def execute_rapid_phase(self) -> bool:
        """
        Rapid clicking phase - 7.5s
        Returns True if fish caught
        """
        rapid_duration = self.config['rapid_phase_duration']
        click_interval = self.config['click_interval']
        start_time = time.time()

        while time.time() - start_time < rapid_duration:
            # Check if should stop
            if not self.running or self.paused:
                return False

            # Click
            pyautogui.click()

            # Check for catch
            found, confidence, _ = self.detect_template('catch')
            if found:
                print(f"    🐟 Fish detected! Confidence: {confidence:.3f}")
                self.execute_catch_sequence()
                return True

            # Wait for next click
            time.sleep(click_interval)

        return False

    def execute_slow_phase(self, cycle_start: float, timeout: float) -> bool:
        """
        Slow phase with A/D movement + clicks
        Returns True if fish caught
        """
        movement_duration = self.config['movement_duration']
        click_interval = self.config['click_interval']
        current_key = 'a'

        while time.time() - cycle_start < timeout:
            # Check if should stop
            if not self.running or self.paused:
                return False

            # Start movement
            pyautogui.keyDown(current_key)
            movement_start = time.time()

            # Click during movement
            while time.time() - movement_start < movement_duration:
                # Check if should stop
                if not self.running or self.paused:
                    pyautogui.keyUp(current_key)
                    return False

                # Click
                pyautogui.click()

                # Check for catch
                found, confidence, _ = self.detect_template('catch')
                if found:
                    pyautogui.keyUp(current_key)
                    print(f"    🐟 Fish detected! Confidence: {confidence:.3f}")
                    self.execute_catch_sequence()
                    return True

                # Wait for next click
                time.sleep(click_interval)

            # Release key
            pyautogui.keyUp(current_key)

            # Switch direction
            current_key = 'd' if current_key == 'a' else 'a'

            # Small pause between movements
            time.sleep(0.2)

        return False

    def execute_catch_sequence(self):
        """Execute sequence when fish is caught"""
        print("    🎯 Executing catch sequence...")

        # Release all inputs
        pyautogui.keyUp('a')
        pyautogui.keyUp('d')
        pyautogui.mouseUp()

        # Wait for fish collection
        time.sleep(3.0)

        print("    ✅ Fish collected!")

    def show_stats(self):
        """Show session statistics"""
        if self.stats['session_start'] > 0:
            duration = time.time() - self.stats['session_start']
            print(f"\n📊 Session Statistics:")
            print(f"  🐟 Fish caught: {self.stats['fish_caught']}")
            print(f"  🔄 Cycles: {self.stats['cycles']}")
            print(f"  ⏱️ Duration: {duration:.1f}s ({duration/60:.1f} min)")
            if duration > 0:
                rate = (self.stats['fish_caught'] / duration) * 3600
                print(f"  📈 Rate: {rate:.1f} fish/hour")

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        print("⌨️ Setting up hotkeys...")

        # Clear existing hotkeys
        keyboard.unhook_all()

        # Register hotkeys
        keyboard.add_hotkey('f9', self.start, suppress=True)
        keyboard.add_hotkey('f1', self.pause, suppress=True)
        keyboard.add_hotkey('f2', self.stop, suppress=True)
        keyboard.add_hotkey('esc', self.emergency_stop, suppress=True)

        print("✅ Hotkeys configured:")
        print("  F9 - Start bot")
        print("  F1 - Pause/Resume")
        print("  F2 - Stop bot")
        print("  ESC - Emergency stop")

    def emergency_stop(self):
        """Emergency stop - ESC"""
        print("🚨 EMERGENCY STOP!")

        # Force stop everything
        self.running = False
        self.paused = False
        self.stop_event.set()

        # Release all inputs
        pyautogui.keyUp('a')
        pyautogui.keyUp('d')
        pyautogui.mouseUp()

        # Clear hotkeys
        keyboard.unhook_all()

        print("✅ Emergency stop completed")

    def run(self):
        """Run the bot with hotkey support"""
        try:
            print("\n" + "="*60)
            print("🎣 SIMPLE FISHING BOT v4.0 - READY")
            print("="*60)

            # Setup hotkeys
            self.setup_hotkeys()

            print("\nBot ready! Press F9 to start fishing.")
            print("Press CTRL+C to exit.\n")

            # Keep running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.emergency_stop()
            print("✅ Bot shut down successfully")

def main():
    """Main entry point"""
    print("\n🎣 Simple Fishing Bot v4.0")
    print("="*60)

    # Check for templates
    if not os.path.exists("templates"):
        print("❌ Templates folder not found!")
        print("Please ensure templates folder exists with catch.png")
        return

    # Create and run bot
    bot = SimpleFishingBot()
    bot.run()

if __name__ == "__main__":
    main()