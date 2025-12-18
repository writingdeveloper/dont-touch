# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Don't Touch is a desktop application for detecting and warning users when their hand approaches their face/head. Designed to help people with trichotillomania (hair-pulling disorder), it uses webcam-based real-time detection with MediaPipe.

## Development Commands

```bash
# Run the application (requires Python 3.12.7, uses venv)
run.bat
# Or manually:
# venv\Scripts\activate && python main.py

# Build installer (requires Inno Setup 6)
build_installer.bat
# Output: installer_output/DontTouch_Setup_x.x.x.exe

# Manual build steps:
# 1. Build application (folder mode)
pyinstaller build_installer.spec
# Output: dist/DontTouch/

# 2. Create installer with Inno Setup
# Open installer.iss in Inno Setup and compile
```

## Architecture

### Detection Pipeline (detector/)

Webcam frames flow through: Camera → HandTracker → PoseTracker → ProximityAnalyzer

**ProximityAnalyzer** uses a state machine:
- `IDLE` → `DETECTING` (hand near head) → `ALERT` (threshold reached) → `COOLDOWN` → `IDLE`

The analyzer calculates elliptical distance between hand landmarks and head region, triggering alerts when hands remain near the head for `trigger_time` seconds.

### UI Layer (ui/)

Built with CustomTkinter. MainWindow runs capture in a background thread, updating UI via `after()` scheduling at ~30 FPS. SystemTray uses pystray for background operation.

### Key Patterns

- **Callback-based communication**: Components use `set_alert_callback()`, `set_statistics_callback()` patterns
- **Threaded capture**: Video processing in background thread, UI updates on main thread
- **Singleton I18n**: `utils.i18n.I18n` class manages translations

### Internationalization

Translations in `locales/{lang}.json` (ko, en, ja, zh, es, ru). Use `t('key')` function for all user-facing strings.

### Configuration

Settings persist to `~/.dont-touch/config.json`. Key settings in `AppConfig`:
- `sensitivity` (0.0-1.0): Lower = more sensitive detection
- `trigger_time`: Seconds before alert
- `cooldown_time`: Seconds between alerts
- `frame_skip`: Process every Nth frame for performance

### Version Management

When releasing a new version, update these files:
- `utils/updater.py` → `APP_VERSION = "x.x.x"`
- `installer.iss` → `#define MyAppVersion "x.x.x"`

### Update Checker (utils/updater.py)

Uses GitHub Releases API to check for updates:
- `check_for_updates_async()`: Background version check
- Compares semantic versions (e.g., "1.0.0" vs "1.0.1")
- Called on app startup (after 2 seconds delay)
- Also available via About window button

### UI Windows (ui/)

- `main_window.py`: Main application window with camera preview
- `settings.py`: Settings configuration dialog
- `statistics_window.py`: Statistics display with calendar and charts
- `about_window.py`: About dialog with version info and update check
- `tray.py`: System tray integration

### Installer (Inno Setup)

`installer.iss` creates Windows installer with:
- Multi-language support (6 languages)
- Desktop/Start Menu shortcuts
- Windows startup registration option
- Automatic uninstaller
- Previous version detection and upgrade
