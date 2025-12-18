"""Loading window shown during app initialization."""
import customtkinter as ctk
import ctypes
import time
from pathlib import Path
from PIL import Image

from utils.i18n import t


def center_window_on_screen(window, width: int, height: int, borderless: bool = False) -> str:
    """Center a CustomTkinter window on screen, accounting for DPI scaling.

    Args:
        window: CTk window instance
        width: Window width
        height: Window height
        borderless: True if window uses overrideredirect(True)

    Returns:
        Geometry string like "400x300+100+200"
    """
    # Get the window scaling factor from CustomTkinter
    try:
        scale_factor = window._get_window_scaling()
    except Exception:
        scale_factor = 1.0

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # For borderless windows (overrideredirect=True), CustomTkinter doesn't
    # apply scaling to geometry, so we use raw pixel coordinates
    if borderless:
        # Use physical pixel coordinates directly
        x = int((screen_width - width * scale_factor) / 2)
        y = int((screen_height - height * scale_factor) / 2)
    else:
        # For normal windows, CustomTkinter scales geometry internally
        # So we need to DIVIDE by scale_factor to get correct position
        x = int(((screen_width / 2) - (width / 2)) / scale_factor)
        y = int(((screen_height / 2) - (height / 2)) / scale_factor)

    return f"{width}x{height}+{x}+{y}"

# Path to the app icon
APP_ICON_PATH = Path(__file__).parent.parent / "assets" / "icon.ico"


class LoadingWindow(ctk.CTk):
    """Loading window displayed during app startup with progress steps."""

    # Loading steps with their progress percentages and icons
    LOADING_STEPS = [
        ("loading_step_init", 0, "⚙️"),
        ("loading_step_config", 15, "📁"),
        ("loading_step_camera", 35, "📷"),
        ("loading_step_ai", 55, "🧠"),
        ("loading_step_ui", 75, "🎨"),
        ("loading_step_ready", 95, "✅"),
    ]

    def __init__(self):
        super().__init__()

        # Set AppUserModelID for proper taskbar icon display on Windows
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("DontTouch.App")
        except Exception:
            pass

        # Window setup
        self.title("Don't Touch")
        self._width = 420
        self._height = 240
        self.resizable(False, False)

        # Remove window decorations for cleaner look
        self.overrideredirect(True)

        # Set window icon (for taskbar)
        if APP_ICON_PATH.exists():
            self.iconbitmap(str(APP_ICON_PATH))
            # Also set the icon using after_idle to ensure it's applied after window is created
            self.after_idle(lambda: self.iconbitmap(str(APP_ICON_PATH)))

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Progress tracking
        self._current_step = 0
        self._target_progress = 0
        self._current_progress = 0
        self._start_time = time.time()
        self._dot_count = 0
        self._dot_animation_id = None

        # Load app icon for display (use .ico file directly)
        self._app_icon = None
        if APP_ICON_PATH.exists():
            try:
                self._app_icon = ctk.CTkImage(
                    light_image=Image.open(APP_ICON_PATH),
                    dark_image=Image.open(APP_ICON_PATH),
                    size=(48, 48)
                )
            except Exception:
                pass

        # Build UI
        self._create_ui()

        # Keep on top
        self.attributes("-topmost", True)

        # Center on screen (accounting for DPI scaling)
        # borderless=True because we use overrideredirect(True)
        self.update_idletasks()
        geometry = center_window_on_screen(self, self._width, self._height, borderless=True)
        self.geometry(geometry)


        # Start animations
        self._animate_progress()
        self._animate_dots()

    def _create_ui(self) -> None:
        """Create the loading UI."""
        # Main frame with gradient-like effect
        main_frame = ctk.CTkFrame(
            self,
            corner_radius=20,
            border_width=2,
            border_color="#4a9eff",
            fg_color=("#0d1117", "#0d1117")
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Header frame with icon and title
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(25, 10))

        # App icon
        if self._app_icon:
            icon_label = ctk.CTkLabel(
                header_frame,
                image=self._app_icon,
                text=""
            )
            icon_label.pack(side="left", padx=(30, 10))

            # Title next to icon
            title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_frame.pack(side="left", fill="y")

            title_label = ctk.CTkLabel(
                title_frame,
                text="Don't Touch",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#ffffff"
            )
            title_label.pack(anchor="w")

            subtitle_label = ctk.CTkLabel(
                title_frame,
                text=t('app_subtitle'),
                font=ctk.CTkFont(size=12),
                text_color="#8b949e"
            )
            subtitle_label.pack(anchor="w")
        else:
            # Fallback without icon
            title_label = ctk.CTkLabel(
                header_frame,
                text="🛡️ Don't Touch",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#ffffff"
            )
            title_label.pack()

            subtitle_label = ctk.CTkLabel(
                header_frame,
                text=t('app_subtitle'),
                font=ctk.CTkFont(size=12),
                text_color="#8b949e"
            )
            subtitle_label.pack()

        # Status frame with icon and text
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(15, 8))

        # Step icon
        self.step_icon_label = ctk.CTkLabel(
            status_frame,
            text=self.LOADING_STEPS[0][2],
            font=ctk.CTkFont(size=16),
        )
        self.step_icon_label.pack(side="left", padx=(40, 8))

        # Loading step text with animated dots
        self.step_label = ctk.CTkLabel(
            status_frame,
            text=t(self.LOADING_STEPS[0][0]),
            font=ctk.CTkFont(size=14),
            text_color="#c9d1d9"
        )
        self.step_label.pack(side="left")

        # Animated dots label
        self.dots_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#c9d1d9"
        )
        self.dots_label.pack(side="left", anchor="w")

        # Progress bar container
        progress_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        progress_container.pack(fill="x", padx=40, pady=(5, 5))

        # Progress bar background (track)
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            width=320,
            height=12,
            corner_radius=6,
            mode="determinate",
            progress_color="#4a9eff",
            fg_color="#21262d"
        )
        self.progress_bar.pack(pady=(0, 5))
        self.progress_bar.set(0)

        # Bottom info frame
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=40, pady=(5, 20))

        # Percentage label on left
        self.percent_label = ctk.CTkLabel(
            bottom_frame,
            text="0%",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#4a9eff"
        )
        self.percent_label.pack(side="left")

        # Elapsed time on right
        self.time_label = ctk.CTkLabel(
            bottom_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#6e7681"
        )
        self.time_label.pack(side="right")

    def _animate_progress(self) -> None:
        """Animate progress bar smoothly."""
        # Smoothly interpolate towards target
        if self._current_progress < self._target_progress:
            # Easing function for smoother animation
            diff = self._target_progress - self._current_progress
            increment = max(0.3, diff * 0.08)
            self._current_progress += increment

            if self._current_progress > self._target_progress:
                self._current_progress = self._target_progress

            self.progress_bar.set(self._current_progress / 100)
            self.percent_label.configure(text=f"{int(self._current_progress)}%")

        # Update elapsed time
        elapsed = time.time() - self._start_time
        self.time_label.configure(text=f"{elapsed:.1f}s")

        # Schedule next animation frame
        self.after(16, self._animate_progress)  # ~60fps

    def _animate_dots(self) -> None:
        """Animate loading dots."""
        self._dot_count = (self._dot_count + 1) % 4
        dots = "." * self._dot_count
        self.dots_label.configure(text=dots)

        # Schedule next dot animation
        self._dot_animation_id = self.after(400, self._animate_dots)

    def set_step(self, step_index: int) -> None:
        """Set the current loading step."""
        if 0 <= step_index < len(self.LOADING_STEPS):
            self._current_step = step_index
            step_key, progress, icon = self.LOADING_STEPS[step_index]
            self._target_progress = progress
            self.step_label.configure(text=t(step_key))
            self.step_icon_label.configure(text=icon)

    def advance_step(self) -> None:
        """Advance to the next loading step."""
        if self._current_step < len(self.LOADING_STEPS) - 1:
            self.set_step(self._current_step + 1)

    def set_progress(self, progress: float) -> None:
        """Set progress directly (0-100)."""
        self._target_progress = max(0, min(100, progress))

    def complete(self) -> None:
        """Mark loading as complete."""
        self._target_progress = 100
        self.step_label.configure(text=t('loading_step_complete'))
        self.step_icon_label.configure(text="🚀")
        self.dots_label.configure(text="")
        if self._dot_animation_id:
            self.after_cancel(self._dot_animation_id)
