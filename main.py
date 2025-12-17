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
from ui import MainWindow, SystemTray, SettingsWindow


class Application:
    """Main application controller."""

    def __init__(self):
        self.config = Config()
        self.main_window = None
        self.system_tray = None
        self.settings_window = None

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

        # Start minimized if configured
        if self.config.settings.start_minimized:
            self.main_window.withdraw()
        else:
            self.main_window.deiconify()

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
            on_save=self._on_settings_save
        )

    def _on_settings_save(self) -> None:
        """Handle settings saved."""
        self.main_window.update_settings()
        self.settings_window = None


def main():
    """Main entry point."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
