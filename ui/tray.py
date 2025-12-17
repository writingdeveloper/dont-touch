"""System tray functionality."""
import threading
from pathlib import Path
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray

from utils.i18n import t


# Path to the app icon
APP_ICON_PATH = Path(__file__).parent.parent / "assets" / "icon.ico"


class SystemTray:
    """System tray icon and menu."""

    def __init__(self,
                 on_show: Optional[Callable] = None,
                 on_quit: Optional[Callable] = None,
                 on_toggle: Optional[Callable] = None):
        self.on_show = on_show
        self.on_quit = on_quit
        self.on_toggle = on_toggle

        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None
        self._is_monitoring = False

    def _load_app_icon(self) -> Image.Image:
        """Load the application icon from file."""
        try:
            if APP_ICON_PATH.exists():
                # Load ico file and get the best size for tray (usually 64x64 or 32x32)
                icon = Image.open(APP_ICON_PATH)
                # Convert to RGBA if needed
                if icon.mode != 'RGBA':
                    icon = icon.convert('RGBA')
                # Resize to standard tray icon size
                icon = icon.resize((64, 64), Image.Resampling.LANCZOS)
                return icon
        except Exception as e:
            print(f"Failed to load app icon: {e}")

        # Fallback to generated icon
        return self._create_fallback_icon()

    def _create_fallback_icon(self, color: str = "green") -> Image.Image:
        """Create a fallback icon image if app icon is not available."""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw a hand symbol
        colors = {
            "green": (0, 200, 0, 255),
            "yellow": (255, 200, 0, 255),
            "red": (255, 0, 0, 255),
            "gray": (128, 128, 128, 255)
        }
        fill_color = colors.get(color, colors["green"])

        # Simple circle with hand icon
        draw.ellipse([4, 4, size-4, size-4], fill=fill_color, outline=(255, 255, 255, 255))

        # Draw a simple X for "don't touch"
        draw.line([20, 20, size-20, size-20], fill=(255, 255, 255, 255), width=4)
        draw.line([20, size-20, size-20, 20], fill=(255, 255, 255, 255), width=4)

        return image

    def _create_menu(self) -> pystray.Menu:
        """Create the tray menu."""
        toggle_text = t('tray_stop') if self._is_monitoring else t('tray_start')

        return pystray.Menu(
            pystray.MenuItem(t('tray_open'), self._on_show_click, default=True),
            pystray.MenuItem(toggle_text, self._on_toggle_click),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(t('tray_exit'), self._on_quit_click)
        )

    def _on_show_click(self, icon, item) -> None:
        """Handle show menu item click."""
        if self.on_show:
            self.on_show()

    def _on_toggle_click(self, icon, item) -> None:
        """Handle toggle menu item click."""
        if self.on_toggle:
            self.on_toggle()
        self._update_menu()

    def _on_quit_click(self, icon, item) -> None:
        """Handle quit menu item click."""
        self.stop()
        if self.on_quit:
            self.on_quit()

    def _update_menu(self) -> None:
        """Update the menu items."""
        if self._icon:
            self._icon.menu = self._create_menu()

    def start(self) -> None:
        """Start the system tray icon."""
        if self._icon is not None:
            return

        self._icon = pystray.Icon(
            "dont-touch",
            self._load_app_icon(),
            t('tray_tooltip'),
            menu=self._create_menu()
        )

        # Run in background thread
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the system tray icon."""
        if self._icon:
            self._icon.stop()
            self._icon = None

    def set_monitoring_state(self, is_monitoring: bool) -> None:
        """Update the monitoring state indicator."""
        self._is_monitoring = is_monitoring

        if self._icon:
            # Always use app icon, just update menu
            self._icon.icon = self._load_app_icon()
            self._update_menu()

    def set_alert_state(self) -> None:
        """Set icon to alert state (red)."""
        # Keep using app icon for consistency
        pass

    def set_detecting_state(self) -> None:
        """Set icon to detecting state (yellow)."""
        # Keep using app icon for consistency
        pass

    def show_notification(self, title: str, message: str) -> None:
        """Show a system notification."""
        if self._icon:
            self._icon.notify(message, title)

    def update_language(self) -> None:
        """Update tray menu text after language change."""
        if self._icon:
            self._icon.title = t('tray_tooltip')
            self._update_menu()
