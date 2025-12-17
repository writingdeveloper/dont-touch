"""
Don't Touch - 발모벽 감지 경고 앱
Hair Pulling Detection Warning App

Main entry point for the application.
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import Config
from utils.i18n import init_language, t
from utils.statistics import StatisticsManager
from utils.updater import check_for_updates_async, UpdateInfo, open_download_page
from ui import MainWindow, SystemTray, SettingsWindow
from ui.statistics_window import StatisticsWindow
from ui.about_window import AboutWindow


class Application:
    """Main application controller."""

    def __init__(self):
        self.config = Config()

        # Initialize language based on saved preference or system language
        init_language(self.config.settings.language)

        # Initialize statistics manager
        self.stats_manager = StatisticsManager()

        self.main_window = None
        self.system_tray = None
        self.settings_window = None
        self.statistics_window = None
        self.about_window = None

    def run(self) -> None:
        """Run the application."""
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

        # Start minimized if configured
        if self.config.settings.start_minimized:
            self.main_window.withdraw()
        else:
            self.main_window.deiconify()

        # Check for updates in background (after window is ready)
        self.main_window.after(2000, self._check_for_updates)

        # Run main loop
        self.main_window.mainloop()

    def _show_window(self) -> None:
        """Show main window from tray."""
        if self.main_window:
            self.main_window.show_window()

    def _quit_app(self) -> None:
        """Quit the application."""
        if self.system_tray:
            self.system_tray.stop()
        if self.main_window:
            self.main_window._on_close()

    def _toggle_monitoring(self) -> None:
        """Toggle monitoring from tray."""
        if self.main_window:
            self.main_window._toggle_monitoring()
            is_running = self.main_window._is_running
            self.system_tray.set_monitoring_state(is_running)

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
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
