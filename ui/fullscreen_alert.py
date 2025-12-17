"""Fullscreen alert window for strong visual feedback."""
import customtkinter as ctk
from typing import Optional, Callable
import threading

from utils.i18n import t


class FullscreenAlert(ctk.CTkToplevel):
    """Fullscreen alert window that covers the entire screen."""

    def __init__(self, parent: Optional[ctk.CTk] = None):
        super().__init__(parent)

        # Window setup - fullscreen, always on top
        self.overrideredirect(True)  # Remove window decorations
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)  # Slight transparency

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

        # Red background
        self.configure(fg_color="#dc3545")

        # Build UI
        self._create_ui()

        # Auto-hide timer
        self._hide_timer: Optional[str] = None

        # Click to dismiss
        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>", self._on_key)

        # Hide initially
        self.withdraw()

    def _create_ui(self) -> None:
        """Create the alert UI."""
        # Center container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0)

        # Warning icon (large)
        self.warning_icon = ctk.CTkLabel(
            center_frame,
            text="⚠️",
            font=ctk.CTkFont(size=120),
            text_color="white"
        )
        self.warning_icon.pack(pady=(0, 20))

        # Alert title
        self.alert_title = ctk.CTkLabel(
            center_frame,
            text=t('alert_title'),
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="white"
        )
        self.alert_title.pack(pady=(0, 15))

        # Alert message
        self.alert_message = ctk.CTkLabel(
            center_frame,
            text=t('alert_subtitle'),
            font=ctk.CTkFont(size=28),
            text_color="#ffcccc"
        )
        self.alert_message.pack(pady=(0, 30))

        # Dismiss hint
        self.dismiss_hint = ctk.CTkLabel(
            center_frame,
            text=t('fullscreen_alert_dismiss'),
            font=ctk.CTkFont(size=16),
            text_color="#ff9999"
        )
        self.dismiss_hint.pack(pady=(20, 0))

    def show_alert(self, duration_ms: int = 3000) -> None:
        """Show the fullscreen alert for specified duration."""
        # Cancel any existing timer
        if self._hide_timer:
            self.after_cancel(self._hide_timer)
            self._hide_timer = None

        # Update texts (in case language changed)
        self.alert_title.configure(text=t('alert_title'))
        self.alert_message.configure(text=t('alert_subtitle'))
        self.dismiss_hint.configure(text=t('fullscreen_alert_dismiss'))

        # Show window
        self.deiconify()
        self.lift()
        self.focus_force()

        # Schedule auto-hide
        self._hide_timer = self.after(duration_ms, self.hide_alert)

    def hide_alert(self) -> None:
        """Hide the fullscreen alert."""
        if self._hide_timer:
            self.after_cancel(self._hide_timer)
            self._hide_timer = None
        self.withdraw()

    def _on_click(self, event) -> None:
        """Handle click to dismiss."""
        self.hide_alert()

    def _on_key(self, event) -> None:
        """Handle key press to dismiss."""
        self.hide_alert()

    def update_language(self) -> None:
        """Update UI text after language change."""
        self.alert_title.configure(text=t('alert_title'))
        self.alert_message.configure(text=t('alert_subtitle'))
        self.dismiss_hint.configure(text=t('fullscreen_alert_dismiss'))
