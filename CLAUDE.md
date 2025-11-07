# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Ultimate Fishing Bot v4.0** - A complete architectural rewrite of v3, implementing a modular automation system for game fishing with computer vision, intelligent state management, and GUI automation.

This is a **defensive automation research project** demonstrating advanced computer vision, thread-safe state coordination, and Windows automation techniques.

**Current Status:** ~95% implemented, fully functional core engines with hotkey system.

## Quick Reference

### Most Important Files
- [main.py](main.py:1) - Entry point (162 lines)
- [core/fishing_engine.py](core/fishing_engine.py:1) - Main fishing loop coordinator
- [core/game_state.py](core/game_state.py:1) - Thread-safe state management
- [core/template_engine.py](core/template_engine.py:1) - OpenCV detection system
- [ui/main_window.py](ui/main_window.py:1) - GUI (290KB, 8 tabs - modify carefully)
- [config/default_config.json](config/default_config.json:1) - Default configuration

### Critical Concepts
1. **Thread-Safety:** Always use locks and check `action_in_progress` flag before operations
2. **State Coordination:** `GameState` class coordinates all components - check state before actions
3. **Priority System:** feeding > rod maintenance > cleaning (never overlap)
4. **Callback Pattern:** Components communicate via registered callbacks, not direct calls
5. **Template Caching:** Templates loaded once and cached - don't reload repeatedly

### Most Common Tasks
- **Add new feature:** Check `GameState` flags → Use locks → Register callbacks → Update UI
- **Fix detection issue:** Adjust confidence in `template_confidence` config section
- **Debug stuck bot:** Check logs for `action_in_progress=True` stuck state
- **Add new template:** Save PNG to `templates/` → Add to config → Use `detect_template()`
- **Modify timing:** Edit `InputManager.timing_config` or UI Tab 7 (Anti-Detection)

## Essential Commands

### Running the Application
```bash
# Main entry point
python main.py

# Force clean start (clears Python cache)
FORCE_CLEAN_AND_RUN.bat
```

### Installation
```bash
# Install all dependencies (Python 3.13+ compatible)
pip install -r requirements.txt

# Verify installation
python -c "import cv2, numpy, mss, keyboard, pyautogui; print('OK')"
```

### Testing Components
```bash
# Test full integration
python test_full_integration.py

# Test hotkeys
python test_hotkeys_simple.py

# Test license system
python test_new_license.py

# Test specific button clicks
python test_button_click.py
```

## Core Architecture

### Modular Structure (v4.0 Rewrite)

The v4 architecture splits the monolithic v3 (~20k lines) into specialized, thread-safe modules:

```
core/
├── fishing_engine.py          # Main fishing cycle coordinator
├── template_engine.py         # OpenCV template matching
├── rod_manager.py             # 6-rod system with maintenance
├── inventory_manager.py       # Auto-clean system
├── feeding_system.py          # Automatic feeding
├── chest_manager.py           # Unified chest operations
├── input_manager.py           # Mouse/keyboard control
├── hotkey_manager.py          # Global hotkey system
├── game_state.py              # Thread-safe state coordination
└── config_manager.py          # Configuration management

ui/
├── main_window.py             # 8-tab GUI (290KB, complex)
├── control_panel.py           # Control interface
└── license_dialog.py          # License activation

utils/
├── i18n.py                    # 3-language support (PT/EN/RU)
├── license_manager.py         # Hardware fingerprinting
└── logging_manager.py         # Advanced logging system
```

### Component Dependency Graph

```
                    ConfigManager (base)
                          ↓
    ┌────────────────────┼────────────────────┐
    ↓                    ↓                     ↓
TemplateEngine      InputManager         GameState
    ↓                    ↓                     ↓
    └────────────────────┼─────────────────────┘
                         ↓
                   ChestManager
                         ↓
         ┌───────────────┼───────────────┐
         ↓               ↓                ↓
    RodManager    FeedingSystem   InventoryManager
         ↓               ↓                ↓
         └───────────────┼────────────────┘
                         ↓
                  FishingEngine
                         ↓
                   HotkeyManager
                         ↓
                    MainWindow (UI)
```

**Dependency Rules:**
- Lower layers never import from higher layers
- All components depend on `ConfigManager` and `GameState`
- `FishingEngine` orchestrates all other engines
- `MainWindow` is the top layer (imports everything, imported by nothing)

### Critical Coordination System

**Thread-Safety Model:**
- All core engines use `threading.RLock()` for safe state access
- `GameState` class provides centralized state coordination
- Operations use priority system: feeding > rod maintenance > cleaning

**State Flags:**
```python
game_state.fishing_active      # Main fishing loop active
game_state.inventory_open      # Inventory UI visible
game_state.chest_open          # Chest UI visible
game_state.action_in_progress  # Prevents overlapping actions
game_state.paused              # Bot paused
```

**Key Principle:** Never execute overlapping actions. Check state flags before any operation.

### Rod Management System (6 Rods, 3 Pairs)

Based on proven v3 logic (`perform_rod_switch_sequence_SLOTS_REAIS()`):

```python
rod_pairs = [(1,2), (3,4), (5,6)]
slot_positions = {
    1: (709, 1005),   2: (805, 1005),   3: (899, 1005),
    4: (992, 1005),   5: (1092, 1005),  6: (1188, 1005)
}
```

**Rod States:** COM_ISCA (with bait), SEM_ISCA (no bait), QUEBRADA (broken), VAZIO (empty)

**Switching Logic:**
1. Detect current rod status via template matching
2. Find pair partner's status
3. Prioritize rods with bait (COM_ISCA)
4. Track usage count (20 initial, 10 after reload)
5. Trigger maintenance when needed (Page Down hotkey)

### Template Detection System

**Critical Templates** (in `templates/` directory):
- `catch.png` - Fish caught detection (confidence: 0.8)
- `VARANOBAUCI.png` - Rod with bait (0.8)
- `enbausi.png` - Rod without bait (0.7)
- `varaquebrada.png` - Broken rod (0.7)
- `inventory.png` - Inventory open detection
- `filefrito.png` - Food item for feeding

**Detection Flow:**
```python
template_engine.detect_template(name, confidence_threshold)
# Returns: TemplateResult(found, confidence, location, size, name)
```

Cache system stores loaded templates for performance. Screen capture uses `mss` library.

### Fishing Cycle (FishingEngine)

**Execution Flow:**

```
User presses F9
    ↓
HotkeyManager triggers start callback
    ↓
FishingEngine.start_fishing()
    ↓
Check GameState (not already active, not paused)
    ↓
Set fishing_active = True
    ↓
Start main_fishing_loop() in background thread
    ↓
Loop:
  1. Check priorities (feeding needed? maintenance needed? cleaning needed?)
  2. Execute priority action if any
  3. Perform fishing cycle:
     - Phase 1: Cast (right-click 1.6s)
     - Phase 2: Fast clicking (7.5s)
     - Phase 3: A/D movements until catch or timeout (122s)
  4. Detect fish caught via template_engine
  5. Update statistics
  6. Increment fish counter
  7. Trigger auto-systems if thresholds met
  8. Repeat
```

**Thread Interaction:**
- Main thread: UI updates via `root.after()`
- Fishing thread: Main cycle execution
- Input threads: Continuous clicking/camera movement
- Detection thread: Template matching in parallel

All threads coordinate via `GameState` and use locks to prevent conflicts.



**3-Phase Fishing Sequence:**
1. **Cast Phase:** Right-click 1.6s to cast rod
2. **Fast Phase:** Rapid left-clicks for 7.5s
3. **Slow Phase:** A/D key movements + clicks until fish caught or 122s timeout

**Automatic Triggers:**
- **Auto-feeding:** Every X catches or Y minutes (configurable)
- **Auto-clean:** Every N catches (default: 1)
- **Auto-rod-switch:** When rod breaks or runs out of bait

### Hotkey System (HotkeyManager)

**Global Hotkeys:**
```
F9         - Start bot
F1         - Pause/Resume
F2         - Stop bot
ESC        - Emergency stop (releases all inputs)
F4         - Toggle UI visibility
F6         - Manual feeding
F5         - Manual inventory cleaning
Page Down  - Rod maintenance
TAB        - Manual rod switch
F8/F11     - Macros (prepared for future use)
```

All hotkeys are thread-safe and callback-based. Emergency stop (ESC) immediately releases all keyboard/mouse inputs.

### Anti-Detection System

**Timing Variations** to mimic human behavior:

```python
# InputManager timing config
timing_config = {
    'click_delay': 1.0 / 12,           # Base: 83ms between clicks (12/sec)
    'movement_a_duration': (1.2, 1.8), # Camera left: randomized
    'movement_d_duration': (1.0, 1.4), # Camera right: randomized
    'movement_pause': (0.2, 0.5),      # Pause between movements
    'fish_catch_delay': 3.0,           # Delay after catching fish
}
```

**Click Variation:** Adds random jitter to click timing (min_delay: 0.08s, max_delay: 0.15s).

**Movement Variation:** A/D camera movements use randomized durations within configured ranges.

**Natural Breaks:** Configurable breaks after N catches (default: 50 catches → 45min break).

These variations are configured in UI Tab 7 (Anti-Detection) and saved to `config.json`.

### Feeding System

**Coordinates** (from v3, verified working):
```python
feeding_positions = {
    "slot1": (1306, 858),   # First food slot in chest
    "slot2": (1403, 877),   # Second food slot
    "eat": (1083, 373)      # Eat button location
}
```

**Process:**
1. Open chest (ChestManager)
2. Locate food in chest via template matching
3. Transfer food to inventory
4. Click "eat" button N times (configurable)
5. Close chest

**Triggers:** Time-based OR catch-based (user configurable in UI)

**Background Analysis:** During feeding, `RodViewerBackground` analyzes rod status to detect maintenance needs early, avoiding mid-cycle interruptions.

### Callback Architecture

**Component Communication Pattern:**

```python
# Register callback for chest operations
chest_manager.register_operation_callback(
    ChestOperation.FEEDING,  # or MAINTENANCE, CLEANING
    callback_function
)

# Callback signature
def callback_function(is_open: bool):
    if is_open:
        # Chest opened, execute operation
    else:
        # Chest closed, cleanup
```

**Key Callbacks:**
- `FishingEngine` → state callbacks for UI updates
- `ChestManager` → operation callbacks per type (FEEDING/MAINTENANCE/CLEANING)
- `HotkeyManager` → hotkey press callbacks
- All callbacks are thread-safe and executed in component's thread context

**ChestOperationCoordinator:** Prevents simultaneous chest operations using operation-specific callbacks and state flags. Only one operation can access chest at a time.

### License System

**Migration from v3:** Fully compatible with v3 licensing server.

**Flow:**
1. `check_license()` - Validates saved license on startup
2. If no valid license → Show `LicenseDialog`
3. User enters key → `activate_license()` saves to server
4. `validate_license()` confirms activation

**Development License:** Automatically generated if no license server available.

## Configuration System

### Main Config (`config/default_config.json`)

**Critical Sections:**
- `coordinates` - All UI positions (slots, feeding, chest areas)
- `template_confidence` - Per-template detection thresholds
- `rod_system` - Rod pair configuration and usage tracking
- `feeding` - Trigger modes and timing
- `auto_clean` - Cleaning interval and chest side
- `hotkeys` - Hotkey mappings

**User Config:** Saved to `data/config.json` (auto-created, overrides defaults)

### Coordinate System (1920x1080)

All coordinates are for 1920x1080 resolution. Critical areas:

```python
inventory_area = [633, 541, 1233, 953]
chest_area = [1214, 117, 1834, 928]
inventory_chest_divider_x = 1243  # Left=inventory, Right=chest
```

## Internationalization

3 languages fully supported: Portuguese (PT), English (EN), Russian (RU)

```python
from utils.i18n import i18n, _
i18n.set_language('pt')  # or 'en', 'ru'
text = _('ui.start_button')  # Returns translated text
```

Translation files in `locales/{pt_BR,en_US,ru_RU}/ui.json`

## Logging System

**Log Files** (in `data/logs/`):
- `fishing_bot_YYYY-MM-DD.log` - Main application log
- `ui_YYYY-MM-DD.log` - UI events
- `fishing_YYYY-MM-DD.log` - Fishing cycle details
- `performance_YYYY-MM-DD.log` - Performance metrics

**Logging Levels:** DEBUG, INFO, WARNING, ERROR (configurable per component)

## Development Guidelines

### Working with the Modular System

1. **Import Core Modules:**
   ```python
   from core.fishing_engine import FishingEngine
   from core.template_engine import TemplateEngine
   from core.game_state import GameState
   ```

2. **Always Check State Before Actions:**
   ```python
   if game_state.action_in_progress:
       return  # Don't overlap operations
   ```

3. **Use Locks for Shared State:**
   ```python
   with self.state_lock:
       self.fishing_active = True
   ```

4. **Template Matching Pattern:**
   ```python
   result = template_engine.detect_template('catch', confidence=0.8)
   if result.found:
       x, y = result.location
   ```

### Unicode/Encoding Handling

Windows console encoding can be problematic. Use `_safe_print()` wrapper:

```python
def _safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)
```

All modules include this function for emoji/Portuguese character safety.

### UI Development (main_window.py)

**Warning:** `main_window.py` is 290KB with 8 complex tabs. Changes should be surgical.

**Tab Structure:**
1. General - Basic settings
2. Templates - Confidence configuration
3. Feeding - Auto-feeding setup
4. Auto-Clean - Inventory management
5. Rod Management - Rod system config
6. Chest - Chest operation settings
7. Anti-Detection - Timing variations
8. Statistics - Real-time stats display

**UI Update Pattern:**
```python
def update_ui():
    if hasattr(self, 'root'):
        self.root.after(0, self._update_stats_safe)
```

Always use `root.after()` for thread-safe UI updates from background threads.

### Code Patterns

**1. Safe Print Pattern** (in every module):
```python
def _safe_print(text):
    """Print with fallback for Unicode/emoji characters"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)
```

**2. Thread-Safe State Access:**
```python
with self.state_lock:
    if self.action_in_progress:
        return False
    self.action_in_progress = True
    # Perform operation
    self.action_in_progress = False
```

**3. Config Access Pattern:**
```python
# Get with fallback
value = config_manager.get('section.key', default_value)

# Check existence
if config_manager.has('section.key'):
    value = config_manager.get('section.key')
```

**4. Template Detection Pattern:**
```python
result = template_engine.detect_template('template_name', confidence=0.8)
if result.found:
    x, y = result.location
    input_manager.click(x, y)
```

**5. Callback Registration:**
```python
# Register
component.register_callback(callback_type, handler_function)

# Handler
def handler_function(data):
    with self.lock:
        # Thread-safe handling
        pass
```

**6. Component Initialization Order:**
```python
# 1. Config first
config = ConfigManager()

# 2. Non-dependent components
template_engine = TemplateEngine(config)
input_manager = InputManager(config)

# 3. State coordination
game_state = GameState()

# 4. Dependent components
chest_manager = ChestManager(template_engine, input_manager, game_state)
rod_manager = RodManager(template_engine, input_manager, config, game_state, chest_manager)

# 5. Main engine last
fishing_engine = FishingEngine(template_engine, rod_manager, input_manager, game_state)
```

**7. Error Handling Pattern:**
```python
try:
    # Operation
    result = perform_action()
    _safe_print(f"✅ Action completed: {result}")
except Exception as e:
    _safe_print(f"❌ Error in action: {e}")
    logger.error(f"Action failed", exc_info=True)
    return False
```

## Testing Strategy

### Integration Testing
```bash
# Full system test
python test_full_integration.py

# Tests template loading, UI creation, hotkey registration
```

### Component Testing
```bash
# Individual components
python test_hotkeys_simple.py        # Hotkey system
python test_integration_simple.py    # Core integration
python test_button_click.py          # UI interaction
```

### Manual Testing Checklist

From `TESTING_CHECKLIST.md`:
1. Launch application → verify no errors
2. Press F9 → fishing starts
3. Catch fish → auto-clean triggers
4. After 3 catches → auto-feeding triggers
5. Press F1 → pause works
6. Press ESC → emergency stop releases inputs

## Migration from v3

See `MIGRATION_V3_TO_V4.md` for complete migration guide.

**Key Changes:**
- Monolithic v3 split into modular v4 components
- Thread-safety improved with proper locks
- License system maintains v3 compatibility
- All v3 coordinates preserved (tested and working)
- HotkeyManager replaces inline keyboard handling

**Coordinate Migration:** Direct copy from v3 `config.json` is supported.

## Important Files

### Documentation
- `README.md` - User-facing documentation
- `QUICK_START.md` - 5-minute setup guide
- `IMPLEMENTATION_STATUS.md` - Component completion status
- `TESTING_CHECKLIST.md` - QA checklist

### Entry Points
- `main.py` - Main application entry (162 lines)
- `FORCE_CLEAN_AND_RUN.bat` - Clean start script

### Core State Files
- `config/default_config.json` - Default configuration
- `data/config.json` - User configuration (auto-created)
- `data/license.key` - License key storage

## Common Issues

### Templates Not Found
Ensure `templates/` directory exists with all 40+ template images. Most critical: `catch.png`

### Hotkeys Not Working
Run as administrator on Windows. `keyboard` library requires elevated privileges for global hotkeys.

### Unicode Errors
All modules use `_safe_print()` wrapper. If adding new print statements, use this function.

### Thread Deadlocks
Always acquire locks in consistent order:
1. `state_lock` (GameState)
2. Component-specific locks (`rod_lock`, `feeding_lock`, etc.)

### Performance Issues
- Template cache should hit on repeated detections
- MSS screen capture is optimized (don't initialize multiple instances)
- Reduce detection interval in `performance.detection_interval_ms`

### Emergency Stop Behavior

When ESC is pressed, `InputManager.emergency_stop()` executes:

1. **Release All Keys:** Iterates through `keyboard_state.keys_down` and releases each
2. **Reset Mouse State:** Sets `left_button_down` and `right_button_down` to False
3. **Stop Continuous Actions:** Flags `continuous_actions.clicking` and `moving_camera` to False
4. **Clear Game State Flags:**
   - `fishing_active = False`
   - `action_in_progress = False`
   - `inventory_open = False`
   - `chest_open = False`
5. **Terminate Active Threads:** Stops all background threads in `active_threads`

This ensures the bot can be safely stopped at any point without leaving inputs in pressed state.

## Debugging Guide

### Reading Logs Effectively

**Log Structure:**
```
[TIMESTAMP] [LEVEL] [MODULE] Message
2025-10-10 14:32:15 INFO  [FishingEngine] 🐟 Peixe #1 capturado!
```

**Key Patterns to Search:**
- `ERROR` - Critical failures
- `⚠️` - Warnings (often encoding or template issues)
- `❌` - Failed operations
- `✅` - Successful operations
- `🔍` - Detection events

**Common Error Locations:**
- Template not found → Check `[TemplateEngine]` logs
- Coordinate issues → Check `[InputManager]` logs
- State conflicts → Check `[GameState]` logs
- Hotkey failures → Check `[HotkeyManager]` logs

### Enable Verbose Logging

Edit `data/config.json`:
```json
{
  "logging": {
    "level": "DEBUG",  // Change from INFO to DEBUG
    "enabled": true
  }
}
```

Restart application to see detailed trace of all operations.

### Template Debugging

**Verify Template Loading:**
```python
python -c "from core.template_engine import TemplateEngine; t = TemplateEngine(); print(t.template_cache.keys())"
```

**Test Specific Template:**
```python
from core.template_engine import TemplateEngine
te = TemplateEngine()
result = te.detect_template('catch', confidence=0.7)
print(f"Found: {result.found}, Confidence: {result.confidence}")
```

### State Debugging

Check current state in logs:
```
[GameState] fishing_active=True, action_in_progress=False, chest_open=False
```

If bot appears frozen, look for `action_in_progress=True` stuck state.

## Template System Details

### Template Categories

Templates are organized by function:

**Rod Templates:**
- `VARANOBAUCI.png` - Rod with bait equipped
- `enbausi.png` - Rod without bait
- `varaquebrada.png` - Broken rod
- `comiscavara.png` / `semiscavara.png` - Rod states in hand

**Fish Templates:**
- `catch.png` - CRITICAL: Fish caught indicator
- `salmon.png`, `shark.png`, `herring.png`, etc. - Specific fish types

**Food Templates:**
- `filefrito.png` - Fried fish (food item)
- `eat.png` - Eat button

**UI Templates:**
- `inventory.png` - Inventory screen open
- `loot.png` - Loot/chest interface

**Bait Templates:**
- `carneurso.png` - Bear meat (priority 1)
- `carnedelobo.png` - Wolf meat (priority 2)
- `grub.png` - Grub (priority 4)
- `minhoca.png` / `worm.png` - Worm (priority 5)

### Adding New Templates

1. Capture screenshot of element (PNG format)
2. Save to `templates/` directory
3. Add confidence threshold to `config/default_config.json`:
   ```json
   "template_confidence": {
     "new_template": 0.75
   }
   ```
4. Use in code:
   ```python
   result = template_engine.detect_template('new_template')
   ```

### Batch Detection

For detecting multiple templates efficiently:
```python
templates_to_check = ['catch', 'VARANOBAUCI', 'enbausi']
results = template_engine.detect_multiple(templates_to_check)
# Returns dict: {'catch': TemplateResult(...), ...}
```

## Platform Notes

**Windows-Specific:**
- Uses `pywin32` for Windows API calls
- `pyautogui` with Windows coordinate system
- COM port selection requires `pyserial` (for future Arduino integration)

**Resolution:** Optimized for 1920x1080. Other resolutions need coordinate recalibration.

## Performance Considerations

### ⚡ OPTIMIZATIONS IMPLEMENTED (v4.0.1)

**See `PERFORMANCE_OPTIMIZATIONS.md` for full details.**

**Summary of Improvements:**
- ✅ Singleton MSS Instance (↓1.6s per cycle)
- ✅ ROI Detection for 20+ templates (↓3-5s per cycle)
- ✅ Batch Detection documented (↓1.4s per cycle)
- **Total: ↓75-80% detection overhead (8-10s → 2s per cycle)**

### Critical Performance Points

**1. Template Matching with ROI (OPTIMIZED):**
- ✅ ROI auto-applied for known templates (`catch`, `VARANOBAUCI`, etc.)
- `catch` detection: 66.7% faster using right 1/3 of screen `[1280, 0, 1920, 1080]`
- Inventory items: 70% faster using `inventory_area` `[633, 541, 1233, 953]`
- Chest items: 70% faster using `chest_area` `[1214, 117, 1834, 928]`
- Disable ROI if needed: `detect_template('name', use_roi=False)`

**2. MSS Screen Capture (OPTIMIZED):**
- ✅ Singleton `_mss_instance` created once and reused
- ✅ Automatic cleanup in `__del__()`
- ✅ Thread-safe for single capture thread
- ~1000 instances/cycle eliminated (was: 1079 → now: 1)

**3. Thread Overhead:**
- Each continuous action (clicking, camera movement) spawns thread
- Threads must be properly joined on stop
- Too many threads = context switching overhead
- Current design: 3-4 active threads maximum

**4. UI Updates:**
- Never update UI directly from background thread (will crash)
- Always use `root.after(0, callback)` pattern
- Batch updates: don't update every detection, update every N detections
- Statistics update interval: 500ms minimum

**5. Detection Frequency:**
- `detection_interval_ms` in config (default: 100ms)
- Lower = more responsive, higher CPU usage
- Higher = less responsive, lower CPU usage
- Sweet spot: 100-200ms

**Expected Performance:**
- CPU Usage: 5-15% on modern systems
- RAM Usage: ~200MB
- Detection latency: <50ms
- Fishing cycle: 15-122 seconds depending on catch time

## Future Phases

**Phase 2 (Planned):**
- WebSocket server for distributed operation
- Arduino Leonardo integration for physical input
- Multi-client coordination

**Phase 3 (Planned):**
- Analytics dashboard
- Performance visualization
- Web-based remote control

Dependencies for future phases are commented out in `requirements.txt`.
