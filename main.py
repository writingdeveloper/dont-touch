"""
Don't Touch - 발모벽 감지 경고 앱
Hair Pulling Detection Warning App

Main entry point for the application.
"""
import sys
import os
import argparse
import time
import threading

# Enable DPI awareness on Windows for correct screen positioning
if sys.platform == 'win32':
    try:
        import ctypes
        # Per-monitor DPI aware (Windows 8.1+)
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # System DPI aware fallback (Windows Vista+)
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import Config
from utils.i18n import init_language, t
from utils.statistics import StatisticsManager
from utils.updater import check_for_updates_async, UpdateInfo, open_download_page
from ui import MainWindow, SystemTray, SettingsWindow
from ui.statistics_window import StatisticsWindow
from ui.about_window import AboutWindow
from ui.loading_window import LoadingWindow


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Don't Touch - Face Touch Detection")
    parser.add_argument('--minimized', action='store_true',
                        help='Start minimized to system tray')
    return parser.parse_args()


class Application:
    """Main application controller."""

    def __init__(self, start_minimized: bool = False):
        self.config = Config()
        self.start_minimized = start_minimized

        # Initialize language based on saved preference or system language
        init_language(self.config.settings.language)

        # Initialize statistics manager
        self.stats_manager = StatisticsManager()

        self.main_window = None
        self.system_tray = None
        self.settings_window = None
        self.statistics_window = None
        self.about_window = None
        self.loading_window = None
        self._loading_start_time = None
        self._app_ready = False

    def run(self) -> None:
        """Run the application."""
        # Show loading window first (only if not starting minimized)
        if not self.start_minimized:
            self.loading_window = LoadingWindow()
            self._loading_start_time = time.time()
            self.loading_window.update()

            # Start app initialization in background thread
            init_thread = threading.Thread(target=self._initialize_app, daemon=True)
            init_thread.start()

            # Run loading window event loop until app is ready
            self._run_loading_loop()

            # Destroy loading window before showing main window
            self.loading_window.destroy()
            self.loading_window = None
        else:
            # Initialize directly if starting minimized
            self._initialize_app_sync()

        # Create main window
        self.main_window = MainWindow(self.config)

        # Set up system tray
        self.system_tray = SystemTray(
            on_show=self._show_window,
            on_quit=self._quit_app,
            on_toggle=self._toggle_monitoring
        )
        self.system_tray.start()

        # Connect main window callbacks
        self.main_window.set_on_minimize_to_tray(self._on_minimize)
        self.main_window.set_on_settings_click(self._open_settings)
        self.main_window.set_on_statistics_click(self._open_statistics)
        self.main_window.set_on_about_click(self._open_about)

        # Connect statistics logging callback
        self.main_window.analyzer.set_statistics_callback(self._log_touch_event)

        # Set close dialog callback
        self.main_window.set_on_close_request(self._on_close_request)

        # Start minimized if --minimized flag is passed (startup)
        if self.start_minimized:
            self.main_window.withdraw()
        else:
            self.main_window.deiconify()
            # Bring main window to front after loading
            self.main_window.lift()
            self.main_window.attributes("-topmost", True)
            self.main_window.after(100, lambda: self.main_window.attributes("-topmost", False))
            self.main_window.focus_force()

        # Check for updates in background (after window is ready)
        self.main_window.after(2000, self._check_for_updates)

        # Auto-start detection if enabled
        if self.config.settings.auto_start_detection:
            self.main_window.after(500, self._auto_start_detection)

        # Run main loop
        self.main_window.mainloop()

    def _initialize_app(self) -> None:
        """Initialize app components in background thread."""
        # Step 1: Config (already done in __init__)
        self._loading_step = 1
        time.sleep(0.3)

        # Step 2: Camera module
        self._loading_step = 2
        try:
            import cv2
        except Exception:
            pass
        time.sleep(0.3)

        # Step 3: AI modules
        self._loading_step = 3
        try:
            import mediapipe
            from detector import HandTracker, PoseTracker, ProximityAnalyzer
        except Exception:
            pass
        time.sleep(0.3)

        # Step 4: UI modules
        self._loading_step = 4
        try:
            import customtkinter
            from PIL import Image
        except Exception:
            pass
        time.sleep(0.3)

        # Step 5: Ready
        self._loading_step = 5

        # Mark initialization as complete
        self._app_ready = True

    def _initialize_app_sync(self) -> None:
        """Initialize app synchronously (for minimized startup)."""
        # Quick init without delays
        try:
            import cv2
            import mediapipe
            from detector import HandTracker, PoseTracker, ProximityAnalyzer
        except Exception:
            pass
        self._app_ready = True

    def _run_loading_loop(self) -> None:
        """Run the loading window event loop until app is ready and minimum time passed."""
        MIN_LOADING_TIME = 5.0  # Minimum 5 seconds
        self._loading_step = 0
        last_step = -1

        while True:
            # Update loading step display
            if hasattr(self, '_loading_step') and self._loading_step != last_step:
                last_step = self._loading_step
                self.loading_window.set_step(self._loading_step)

            # Update loading window
            try:
                self.loading_window.update()
            except Exception:
                break

            # Check if minimum time has passed and app is ready
            elapsed = time.time() - self._loading_start_time
            if elapsed >= MIN_LOADING_TIME and self._app_ready:
                # Show complete state briefly
                self.loading_window.complete()
                self.loading_window.update()
                time.sleep(0.3)
                break

            # Small sleep to prevent CPU spinning
            time.sleep(0.016)  # ~60fps

    def _show_window(self) -> None:
        """Show main window from tray."""
        if self.main_window:
            self.main_window.show_window()

    def _quit_app(self) -> None:
        """Quit the application (from tray menu - no dialog)."""
        if self.system_tray:
            self.system_tray.stop()
        if self.main_window:
            self.main_window._force_close()

    def _toggle_monitoring(self) -> None:
        """Toggle monitoring from tray."""
        if self.main_window:
            self.main_window._toggle_monitoring()
            is_running = self.main_window._is_running
            self.system_tray.set_monitoring_state(is_running)

    def _auto_start_detection(self) -> None:
        """Auto-start detection when app launches."""
        if self.main_window and not self.main_window._is_running:
            self.main_window._start_monitoring()
            if self.system_tray:
                self.system_tray.set_monitoring_state(True)

    def _on_minimize(self) -> None:
        """Handle minimize to tray."""
        if self.system_tray:
            is_running = self.main_window._is_running
            self.system_tray.set_monitoring_state(is_running)

    def _open_settings(self) -> None:
        """Open settings window."""
        if self.settings_window is not None:
            try:
                self.settings_window.focus()
                return
            except:
                pass

        self.settings_window = SettingsWindow(
            self.main_window,
            self.config,
            on_save=self._on_settings_save,
            on_language_change=self._on_language_change
        )

    def _on_settings_save(self) -> None:
        """Handle settings saved."""
        self.main_window.update_settings()
        self.settings_window = None

    def _open_statistics(self) -> None:
        """Open statistics window."""
        if self.statistics_window is not None:
            try:
                self.statistics_window.focus()
                return
            except:
                pass

        self.statistics_window = StatisticsWindow(
            self.main_window,
            self.stats_manager
        )
        self.statistics_window.protocol("WM_DELETE_WINDOW", self._on_statistics_close)

    def _on_statistics_close(self) -> None:
        """Handle statistics window close."""
        if self.statistics_window:
            self.statistics_window.destroy()
        self.statistics_window = None

    def _open_about(self) -> None:
        """Open about window."""
        if self.about_window is not None:
            try:
                self.about_window.focus()
                return
            except:
                pass

        self.about_window = AboutWindow(self.main_window)
        self.about_window.protocol("WM_DELETE_WINDOW", self._on_about_close)

    def _on_about_close(self) -> None:
        """Handle about window close."""
        if self.about_window:
            self.about_window.destroy()
        self.about_window = None

    def _log_touch_event(self, duration: float, closest_distance: float) -> None:
        """Log a touch event to statistics."""
        self.stats_manager.log_event(duration, closest_distance)

    def _on_language_change(self) -> None:
        """Handle language change - update all UI components."""
        if self.main_window:
            self.main_window.update_language()
        if self.system_tray:
            self.system_tray.update_language()

    def _on_close_request(self) -> str:
        """Handle close button request - show dialog to choose minimize or exit.

        Returns:
            'minimize' to minimize to tray, 'exit' to quit, 'cancel' to cancel
        """
        from ui.close_dialog import CloseDialog
        dialog = CloseDialog(self.main_window)
        return dialog.get_result()

    def _check_for_updates(self) -> None:
        """Check for updates in background."""
        check_for_updates_async(self._on_update_check_complete)

    def _on_update_check_complete(self, update_info: UpdateInfo) -> None:
        """Handle update check completion."""
        if update_info and update_info.is_update_available:
            # Schedule UI update on main thread
            if self.main_window:
                self.main_window.after(0, lambda: self._show_update_dialog(update_info))

    def _show_update_dialog(self, update_info: UpdateInfo) -> None:
        """Show update available dialog."""
        import customtkinter as ctk
        from tkinter import messagebox

        # Create a simple dialog
        result = messagebox.askyesno(
            t('update_available_title'),
            t('update_available_message').format(
                current=update_info.current_version,
                latest=update_info.latest_version
            ),
            parent=self.main_window
        )

        if result:
            open_download_page()


def main():
    """Main entry point."""
    args = parse_args()
    app = Application(start_minimized=args.minimized)
    app.run()


if __name__ == "__main__":
    main()
