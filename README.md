# Don't Touch 🛡️

**Hair Pulling Prevention Assistant for Trichotillomania**

[한국어](docs/README_KO.md) | [日本語](docs/README_JA.md) | [中文](docs/README_ZH.md) | [Español](docs/README_ES.md) | [Русский](docs/README_RU.md)

---

## Introduction

Don't Touch is a desktop application designed to help correct the habit of unconsciously touching or pulling hair (Trichotillomania).

Using your webcam, it tracks hand movements in real-time and alerts you when your hand approaches your face or head, helping you become aware of the habit.

## Key Features

- 🎥 **Real-time Detection** - Track hand and face positions via webcam
- 🔔 **Instant Alerts** - Audio and visual warnings when hands approach head
- 📊 **Statistics & Tracking** - Daily/weekly touch count recording and analysis
- 📅 **Calendar View** - Monthly habit overview at a glance
- 🔥 **Streak Feature** - Track consecutive touch-free days for motivation
- ⚙️ **Customizable Settings** - Adjust sensitivity, alert sounds, cooldown time
- 🌐 **Multi-language Support** - Korean, English, Japanese, Chinese, Spanish, Russian
- 🖥️ **System Tray** - Runs quietly in the background
- 🔄 **Auto Update Check** - Notifies when new version is available
- 📷 **Preview Toggle** - Turn off camera preview to save CPU while detection continues

## Download & Installation

### Windows

1. Download `DontTouch_Setup_x.x.x.exe` from the [Releases](https://github.com/writingdeveloper/dont-touch/releases) page
2. Run the installer and follow the setup wizard
3. Launch from Start Menu or Desktop shortcut

**Installer Features:**
- Desktop & Start Menu shortcuts
- Optional Windows startup registration
- Easy uninstall via Control Panel
- Automatic updates notification

> ⚠️ **Windows Security Warning**
>
> Since this app is not yet code-signed, Windows may display a security warning:
>
> **Windows SmartScreen:**
> 1. Click "More info"
> 2. Click "Run anyway"
>
> **Windows 11 Smart App Control:**
> - If Smart App Control is enabled in "Evaluation" or "On" mode, the app may be blocked
> - Temporarily disable Smart App Control: Settings → Privacy & Security → Windows Security → App & Browser Control → Smart App Control → Off
> - Re-enable after installation if desired
>
> 🔐 **Code Signing Coming Soon**: We plan to implement code signing through [SignPath](https://signpath.io) for open-source projects to eliminate these warnings in future releases.

### Requirements

- Windows 10/11 (64-bit)
- Webcam (built-in or external)

## How to Use

### Basic Usage

1. **Launch the app** - Run from Start Menu or Desktop shortcut
2. **Start monitoring** - Click the "Start" button
3. **Work as usual** - The app monitors in the background
4. **Receive alerts** - Get notified when hands approach your head

### Adjust Settings

- **Sensitivity** - Lower values mean more sensitive detection
- **Trigger Time** - Waiting time before alert triggers
- **Cooldown** - Waiting time between consecutive alerts

### System Tray

- Continues running in tray even when window is closed
- Click tray icon to open/close window
- Right-click for quick menu access

## View Statistics

- **Daily Graph** - Analyze touch patterns by time of day
- **Weekly Graph** - View touch status by day of week
- **Calendar** - Visualize monthly touch counts
- **Streak** - Check consecutive touch-free days

## FAQ

### Webcam isn't working
- Check if another app is using the webcam
- Make sure webcam drivers are up to date
- Verify the app has camera permissions

### Detection is too sensitive / not sensitive enough
- Adjust sensitivity in settings
- Try increasing or decreasing trigger time

### I want to change the alert sound
- You can select alert sounds or mute in settings

## Privacy

- All data is stored **locally only**
- Webcam footage is **never sent to servers**
- **No internet connection required** (works offline)

## Feedback & Support

- **Bug Reports**: [GitHub Issues](https://github.com/writingdeveloper/dont-touch/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/writingdeveloper/dont-touch/issues)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Habits start with awareness. Build healthy habits with Don't Touch! 💪</b>
</p>
