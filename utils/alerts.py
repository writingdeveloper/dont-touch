"""Alert management for notifications."""
import threading
import os
from pathlib import Path
from typing import Optional, Callable
import winsound


class AlertManager:
    """Manages visual and audio alerts."""

    DEFAULT_ALERT_SOUND = Path(__file__).parent.parent / "assets" / "alert.wav"

    def __init__(self,
                 sound_enabled: bool = True,
                 popup_enabled: bool = True,
                 on_popup: Optional[Callable[[str], None]] = None):
        self.sound_enabled = sound_enabled
        self.popup_enabled = popup_enabled
        self.on_popup = on_popup  # Callback for popup display
        self._sound_thread: Optional[threading.Thread] = None

    def trigger_alert(self, message: str = "손이 머리 근처에 있습니다!") -> None:
        """Trigger both sound and popup alerts."""
        if self.sound_enabled:
            self._play_sound()

        if self.popup_enabled and self.on_popup:
            self.on_popup(message)

    def _play_sound(self) -> None:
        """Play alert sound in a separate thread."""
        def play():
            try:
                if self.DEFAULT_ALERT_SOUND.exists():
                    winsound.PlaySound(
                        str(self.DEFAULT_ALERT_SOUND),
                        winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                else:
                    # Fallback to system beep
                    winsound.Beep(1000, 500)  # 1000Hz for 500ms
            except Exception as e:
                print(f"Failed to play sound: {e}")

        # Don't block the main thread
        if self._sound_thread is None or not self._sound_thread.is_alive():
            self._sound_thread = threading.Thread(target=play, daemon=True)
            self._sound_thread.start()

    def set_sound_enabled(self, enabled: bool) -> None:
        """Enable or disable sound alerts."""
        self.sound_enabled = enabled

    def set_popup_enabled(self, enabled: bool) -> None:
        """Enable or disable popup alerts."""
        self.popup_enabled = enabled

    def set_popup_callback(self, callback: Callable[[str], None]) -> None:
        """Set the callback function for popup alerts."""
        self.on_popup = callback
