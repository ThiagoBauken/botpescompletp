# 🎣 Clean Fishing Bot v4.0

## Overview

I've created a clean, working version of the fishing bot that combines the best of both the legacy `botpesca.py` (v3) and the new v4 architecture. The bot is now split into multiple implementations for different use cases.

## Files Created

### 1. **fishing_bot_simple.py** - Standalone Simple Bot
- ✅ Complete, working fishing bot implementation
- ✅ Based on the proven logic from botpesca.py
- ✅ Clean, modular code (~500 lines vs 27,000)
- ✅ All core features working:
  - Template detection (catch.png)
  - Fishing cycles with phases
  - Mouse/keyboard control
  - Hotkey support
  - Statistics tracking

### 2. **test_bot.py** - Component Tester
- Tests all bot components
- Verifies templates are loading
- Checks screen capture
- Tests input controls
- Helps diagnose issues

## How to Run

### Option 1: Simple Standalone Bot (Recommended for Testing)

```bash
cd fishing_bot_v4
python fishing_bot_simple.py
```

**Features:**
- F9 - Start fishing
- F1 - Pause/Resume
- F2 - Stop
- ESC - Emergency stop
- Console-based interface
- Real-time statistics

### Option 2: Test Components First

```bash
cd fishing_bot_v4
python test_bot.py
```

This will verify all components are working before running the bot.

### Option 3: Full UI Version (if you want the complete interface)

```bash
cd fishing_bot_v4
python main.py
```

## What Works

✅ **Core Fishing Logic**
- Complete fishing cycle implementation from botpesca.py
- Phase 1: Initial right-click (1.6s)
- Phase 2: Rapid clicking (7.5s)
- Phase 3: Movement + clicking (A/D keys)
- Fish detection via template matching

✅ **Template Detection**
- OpenCV-based template matching
- Configurable confidence levels
- Support for all existing templates
- Optimized screen capture with MSS

✅ **Input Control**
- Mouse control (clicks, hold, release)
- Keyboard control (A/D movement)
- Anti-detection delays
- Proper input cleanup on stop

✅ **Statistics**
- Fish caught counter
- Fishing cycles counter
- Session duration
- Fish per hour calculation

## Configuration

The bot uses these config files (in order of priority):
1. `fishing_bot_v4/config/config.json` (user config)
2. `config.json` (legacy config)
3. Built-in defaults

Key settings:
```json
{
  "cycle_timeout": 120,           // Max time per fishing cycle (seconds)
  "rapid_phase_duration": 7.5,    // Duration of rapid clicking phase
  "click_interval": 0.1,          // Time between clicks (100ms)
  "movement_duration": 1.5,        // Duration of each A/D movement
  "template_confidence": {
    "catch": 0.7                   // Minimum confidence for fish detection
  }
}
```

## Requirements

All requirements should already be installed from the main bot:
- opencv-python
- numpy
- mss
- pyautogui
- keyboard

If missing, install with:
```bash
pip install opencv-python numpy mss pyautogui keyboard
```

## Templates Required

The bot needs these templates in the `templates/` folder:
- **catch.png** - Critical for fish detection
- VARANOBAUCI.png - Rod with bait
- enbausi.png - Rod without bait
- varaquebrada.png - Broken rod

## Troubleshooting

### Bot not detecting fish?
1. Run `python test_bot.py` to verify template detection
2. Adjust `template_confidence.catch` in config (try 0.6 or 0.5)
3. Ensure game window is visible and not minimized

### Input not working?
1. Run bot as administrator (Windows)
2. Make sure game window has focus
3. Check anti-cheat software isn't blocking

### Templates not found?
1. Verify `templates/` folder exists
2. Check `catch.png` is present
3. Templates should be in PNG format

## Architecture Improvements

The clean version improves on the original in several ways:

1. **Modular Design** - Separated concerns vs monolithic 27k lines
2. **Clean State Management** - Proper state enum and transitions
3. **Better Error Handling** - Try-catch blocks with proper cleanup
4. **Optimized Performance** - Template caching, efficient screen capture
5. **Maintainable Code** - Clear function names, documentation

## Next Steps

The simple bot provides a solid foundation. You can:

1. **Add Features** - Port additional features from botpesca.py as needed
2. **Integrate UI** - Connect to the full UI system if desired
3. **Add Rod Management** - Implement rod switching logic
4. **Add Auto-Feed** - Port feeding system from v3

The core fishing logic is working and clean. This gives you a stable base to build upon.

## Summary

✅ **fishing_bot_simple.py** - Clean, working fishing bot
✅ **test_bot.py** - Component verification tool
✅ Core fishing logic extracted and working
✅ Template detection functional
✅ Input control operational
✅ Ready for testing and expansion