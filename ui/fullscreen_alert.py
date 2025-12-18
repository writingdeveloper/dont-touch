"""Fullscreen alert window for strong visual feedback."""
import customtkinter as ctk
from typing import Optional, Callable
import ctypes

from utils.i18n import t


def get_physical_screen_size() -> tuple[int, int]:
    """Get physical screen size in pixels using Windows API."""
    user32 = ctypes.windll.user32
    width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
    return width, height


class FullscreenAlert(ctk.CTkToplevel):
    """Fullscreen alert window that covers the entire screen."""

    def __init__(self, parent: Optional[ctk.CTk] = None,
                 can_dismiss_callback: Optional[Callable[[], bool]] = None):
        super().__init__(parent)

        # Callback to check if dismiss is allowed (hand not near face)
        self._can_dismiss_callback = can_dismiss_callback

        # Window setup - fullscreen, always on top
        self.overrideredirect(True)  # Remove window decorations
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)  # Slight transparency

        # Get physical screen dimensions
        screen_width, screen_height = get_physical_screen_size()

        # Get CustomTkinter's scale factor to compensate
        try:
            ctk_scale = ctk.ScalingTracker.get_window_scaling(self)
        except Exception:
            ctk_scale = 1.0

        # CustomTkinter scales geometry internally, so we need to compensate
        # by dividing by the scale factor to get correct physical size
        adjusted_width = int(screen_width / ctk_scale)
        adjusted_height = int(screen_height / ctk_scale)

        # Set geometry with adjusted dimensions
        self.geometry(f"{adjusted_width}x{adjusted_height}+0+0")

        # Red background
        self.configure(fg_color="#dc3545")

        # Auto-hide timer
        self._hide_timer: Optional[str] = None

        # Shake animation state
        self._shake_count = 0

        # Build UI
        self._create_ui()

        # Click/key to dismiss - bind to window and all children
        self.bind("<Button-1>", self._on_click)
        self.bind("<Key>", self._on_key)
        self.center_frame.bind("<Button-1>", self._on_click)
        self.warning_icon.bind("<Button-1>", self._on_click)
        self.alert_title.bind("<Button-1>", self._on_click)
        self.alert_message.bind("<Button-1>", self._on_click)
        self.dismiss_hint.bind("<Button-1>", self._on_click)

        # Hide initially
        self.withdraw()

    def _create_ui(self) -> None:
        """Create the alert UI."""
        # Center container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.grid(row=0, column=0)

        # Font sizes (CustomTkinter handles DPI scaling automatically)
        icon_size = 120
        title_size = 48
        message_size = 28
        hint_size = 16
        pad_small = 15
        pad_medium = 20
        pad_large = 30

        # Warning icon (large)
        self.warning_icon = ctk.CTkLabel(
            self.center_frame,
            text="⚠️",
            font=ctk.CTkFont(size=icon_size),
            text_color="white"
        )
        self.warning_icon.pack(pady=(0, pad_medium))

        # Alert title
        self.alert_title = ctk.CTkLabel(
            self.center_frame,
            text=t('alert_title'),
            font=ctk.CTkFont(size=title_size, weight="bold"),
            text_color="white"
        )
        self.alert_title.pack(pady=(0, pad_small))

        # Alert message
        self.alert_message = ctk.CTkLabel(
            self.center_frame,
            text=t('alert_subtitle'),
            font=ctk.CTkFont(size=message_size),
            text_color="#ffcccc"
        )
        self.alert_message.pack(pady=(0, pad_large))

        # Dismiss hint
        self.dismiss_hint = ctk.CTkLabel(
            self.center_frame,
            text=t('fullscreen_alert_dismiss'),
            font=ctk.CTkFont(size=hint_size),
            text_color="#ff9999"
        )
        self.dismiss_hint.pack(pady=(pad_medium, 0))

    def show_alert(self) -> None:
        """Show the fullscreen alert until user dismisses it."""
        # Cancel any existing timer (for backwards compatibility)
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

        # No auto-hide - user must dismiss manually

    def hide_alert(self) -> None:
        """Hide the fullscreen alert."""
        if self._hide_timer:
            self.after_cancel(self._hide_timer)
            self._hide_timer = None
        self.withdraw()

    def _on_click(self, event) -> None:
        """Handle click to dismiss."""
        self._try_dismiss()

    def _on_key(self, event) -> None:
        """Handle key press to dismiss."""
        self._try_dismiss()

    def _try_dismiss(self) -> None:
        """Try to dismiss the alert, checking if hand is still near face."""
        # Check if dismiss is allowed
        if self._can_dismiss_callback and not self._can_dismiss_callback():
            # Hand still near face - show feedback and don't dismiss
            self._show_cannot_dismiss_feedback()
            return

        # Hand is away from face - allow dismiss
        self.hide_alert()

    def _show_cannot_dismiss_feedback(self) -> None:
        """Show visual feedback that alert cannot be dismissed yet."""
        # Update message to indicate hand must be moved away
        self.dismiss_hint.configure(
            text=t('fullscreen_alert_move_hand'),
            text_color="#ffff00"  # Yellow for emphasis
        )

        # Shake animation
        self._shake_count = 0
        self._shake_animation()

    def _shake_animation(self) -> None:
        """Animate a shake effect to indicate cannot dismiss."""
        if self._shake_count >= 6:
            # Reset position and restore hint text after animation
            self.center_frame.place_forget()
            self.center_frame.grid(row=0, column=0)
            self.after(1500, self._restore_dismiss_hint)
            return

        # Alternate left/right offset
        offset = 15 if self._shake_count % 2 == 0 else -15
        self._shake_count += 1

        # Move center frame
        self.center_frame.grid_forget()
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center", x=offset)

        # Continue animation
        self.after(50, self._shake_animation)

    def _restore_dismiss_hint(self) -> None:
        """Restore the dismiss hint to original text."""
        self.dismiss_hint.configure(
            text=t('fullscreen_alert_dismiss'),
            text_color="#ff9999"
        )

    def update_language(self) -> None:
        """Update UI text after language change."""
        self.alert_title.configure(text=t('alert_title'))
        self.alert_message.configure(text=t('alert_subtitle'))
        self.dismiss_hint.configure(text=t('fullscreen_alert_dismiss'))
