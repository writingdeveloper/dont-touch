"""Main window UI using CustomTkinter."""
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable

from detector import Camera, HandTracker, PoseTracker, ProximityAnalyzer
from detector.analyzer import AlertState
from utils import Config, AlertManager
from utils.i18n import t, get_language
from ui.fullscreen_alert import FullscreenAlert


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self, config: Config):
        super().__init__()

        self.config = config
        self.settings = config.settings

        # Window setup
        self.title("Don't Touch")
        self.geometry(f"{self.settings.window_width}x{self.settings.window_height}")
        self.minsize(900, 600)

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize components
        self.camera = Camera()
        self.hand_tracker = HandTracker()
        self.pose_tracker = PoseTracker()
        self.analyzer = ProximityAnalyzer(
            distance_threshold=self.settings.sensitivity,
            trigger_time=self.settings.trigger_time,
            cooldown_time=self.settings.cooldown_time
        )

        self.alert_manager = AlertManager(
            sound_enabled=self.settings.sound_enabled,
            popup_enabled=self.settings.popup_enabled,
            on_popup=self._show_alert_popup
        )

        self.analyzer.set_alert_callback(self.alert_manager.trigger_alert)

        # State
        self._is_running = False
        self._frame_count = 0
        self._update_thread: Optional[threading.Thread] = None
        self._current_frame: Optional[np.ndarray] = None
        self._frame_lock = threading.Lock()

        # Callbacks
        self._on_minimize_to_tray: Optional[Callable] = None
        self._on_settings_click: Optional[Callable] = None
        self._on_statistics_click: Optional[Callable] = None
        self._on_about_click: Optional[Callable] = None

        # Build UI
        self._create_ui()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Handle window resize
        self.bind("<Configure>", self._on_resize)
        self._last_resize_time = 0

    def _on_resize(self, event) -> None:
        """Handle window resize event."""
        # Throttle resize events
        current_time = time.time()
        if current_time - self._last_resize_time < 0.1:
            return
        self._last_resize_time = current_time

    def _create_ui(self) -> None:
        """Create the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Top bar
        self._create_top_bar()

        # Video display
        self._create_video_display()

        # Bottom status bar
        self._create_status_bar()

        # Alert overlay (hidden by default)
        self._create_alert_overlay()

        # Fullscreen alert window (created on demand)
        self._fullscreen_alert: Optional[FullscreenAlert] = None

    def _create_top_bar(self) -> None:
        """Create top control bar."""
        top_frame = ctk.CTkFrame(self.main_frame, height=70, corner_radius=15)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_frame.grid_columnconfigure(1, weight=1)

        # App icon and title section
        title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # Title with icon
        self.title_label = ctk.CTkLabel(
            title_frame,
            text=f"🛡️ {t('app_title')}",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(side="left")

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            title_frame,
            text=f"  |  {t('app_subtitle')}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.pack(side="left", padx=(5, 0))

        # Spacer
        spacer = ctk.CTkFrame(top_frame, fg_color="transparent")
        spacer.grid(row=0, column=1, sticky="ew")

        # Control buttons frame
        control_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        control_frame.grid(row=0, column=2, padx=15, pady=15, sticky="e")

        # Start/Stop button with better styling
        self.start_button = ctk.CTkButton(
            control_frame,
            text=t('btn_start'),
            width=90,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838",
            command=self._toggle_monitoring
        )
        self.start_button.pack(side="left", padx=3)

        # Statistics button
        self.statistics_button = ctk.CTkButton(
            control_frame,
            text=t('btn_statistics'),
            width=75,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=12),
            fg_color="#9c27b0",
            hover_color="#7b1fa2",
            command=self._open_statistics
        )
        self.statistics_button.pack(side="left", padx=2)

        # Settings button
        self.settings_button = ctk.CTkButton(
            control_frame,
            text=t('btn_settings'),
            width=75,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=12),
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self._open_settings
        )
        self.settings_button.pack(side="left", padx=2)

        # About button
        self.about_button = ctk.CTkButton(
            control_frame,
            text=t('btn_about'),
            width=70,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=12),
            fg_color="#2196f3",
            hover_color="#1976d2",
            command=self._open_about
        )
        self.about_button.pack(side="left", padx=2)

        # Minimize button
        self.minimize_button = ctk.CTkButton(
            control_frame,
            text=t('btn_minimize'),
            width=80,
            height=36,
            corner_radius=18,
            font=ctk.CTkFont(size=12),
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self._minimize_to_tray
        )
        self.minimize_button.pack(side="left", padx=2)

    def _create_video_display(self) -> None:
        """Create video display area."""
        self.video_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.video_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

        # Preview toggle switch frame (top-right corner of video area)
        self.preview_toggle_frame = ctk.CTkFrame(self.video_frame, fg_color="transparent")
        self.preview_toggle_frame.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)

        self.preview_label = ctk.CTkLabel(
            self.preview_toggle_frame,
            text=t('preview_label'),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.preview_label.pack(side="left", padx=(0, 5))

        self._preview_enabled = True
        self.preview_switch = ctk.CTkSwitch(
            self.preview_toggle_frame,
            text="",
            width=40,
            command=self._toggle_preview,
            onvalue=True,
            offvalue=False
        )
        self.preview_switch.select()  # Default on
        self.preview_switch.pack(side="left")

        # Hide toggle initially (only show when monitoring)
        self.preview_toggle_frame.place_forget()

        # Welcome message frame (shown when camera is not active)
        self.welcome_frame = ctk.CTkFrame(self.video_frame, fg_color="transparent")
        self.welcome_frame.grid(row=0, column=0)

        # Camera icon
        camera_icon = ctk.CTkLabel(
            self.welcome_frame,
            text="📷",
            font=ctk.CTkFont(size=48)
        )
        camera_icon.pack(pady=(20, 10))

        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self.welcome_frame,
            text=t('camera_preview'),
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.welcome_label.pack(pady=5)

        # Instruction
        self.instruction_label = ctk.CTkLabel(
            self.welcome_frame,
            text=t('camera_instruction'),
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.instruction_label.pack(pady=(0, 20))

        # Video label - centered without stretching
        self.video_label = ctk.CTkLabel(
            self.video_frame,
            text=""
        )
        self.video_label.grid(row=0, column=0)  # Centered, not stretched
        self.video_label.grid_remove()  # Hide initially

    def _create_status_bar(self) -> None:
        """Create bottom status bar."""
        status_frame = ctk.CTkFrame(self.main_frame, height=80, corner_radius=15)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        status_frame.grid_columnconfigure(1, weight=1)

        # Status indicator section
        status_indicator_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_indicator_frame.grid(row=0, column=0, padx=15, pady=15)

        # Status indicator with label
        self.status_indicator = ctk.CTkLabel(
            status_indicator_frame,
            text="●",
            font=ctk.CTkFont(size=28),
            text_color="gray"
        )
        self.status_indicator.pack(side="left", padx=(0, 8))

        # Status message
        self.status_label = ctk.CTkLabel(
            status_indicator_frame,
            text=t('status_standby'),
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.status_label.pack(side="left")

        # Center info section
        info_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=15)

        self.info_label = ctk.CTkLabel(
            info_frame,
            text=t('status_standby_desc'),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack()

        # Progress section
        progress_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        progress_frame.grid(row=0, column=2, padx=15, pady=15)

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text=t('detection_progress'),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.progress_label.pack(pady=(0, 5))

        # Progress bar (for detection countdown)
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=180,
            height=12,
            corner_radius=6
        )
        self.progress_bar.pack()
        self.progress_bar.set(0)

    def _create_alert_overlay(self) -> None:
        """Create alert overlay (initially hidden)."""
        self.alert_overlay = ctk.CTkFrame(
            self,
            fg_color="#dc3545",
            corner_radius=20
        )

        # Warning icon
        warning_icon = ctk.CTkLabel(
            self.alert_overlay,
            text="⚠️",
            font=ctk.CTkFont(size=36)
        )
        warning_icon.pack(pady=(15, 5))

        self.alert_label = ctk.CTkLabel(
            self.alert_overlay,
            text=t('alert_title'),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        self.alert_label.pack(pady=(0, 5))

        self.alert_subtitle = ctk.CTkLabel(
            self.alert_overlay,
            text=t('alert_subtitle'),
            font=ctk.CTkFont(size=14),
            text_color="#ffcccc"
        )
        self.alert_subtitle.pack(pady=(0, 15))

    def _toggle_monitoring(self) -> None:
        """Toggle monitoring on/off."""
        if self._is_running:
            self._stop_monitoring()
        else:
            self._start_monitoring()

    def _start_monitoring(self) -> None:
        """Start camera monitoring."""
        if self._is_running:
            return

        if not self.camera.start():
            self.status_label.configure(text=t('camera_error'))
            self.status_indicator.configure(text_color="red")
            self.info_label.configure(text=t('camera_error_help'), text_color="#dc3545")
            return

        self._is_running = True
        self.start_button.configure(
            text=t('btn_stop'),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.status_indicator.configure(text_color="#28a745")
        self.status_label.configure(text=t('status_monitoring'))
        self.info_label.configure(text=t('status_monitoring_desc'), text_color="gray")

        # Show preview toggle switch
        self.preview_toggle_frame.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)

        # Show video label, hide welcome frame
        self.welcome_frame.grid_remove()
        self.video_label.grid()

        # Start update thread
        self._update_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._update_thread.start()

        # Start UI update
        self._update_ui()

    def _stop_monitoring(self) -> None:
        """Stop camera monitoring."""
        self._is_running = False
        self.camera.stop()

        self.start_button.configure(
            text=t('btn_start'),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.status_indicator.configure(text_color="gray")
        self.status_label.configure(text=t('status_standby'))
        self.info_label.configure(text=t('status_standby_desc'), text_color="gray")
        self.progress_bar.set(0)

        # Hide preview toggle switch
        self.preview_toggle_frame.place_forget()

        # Show welcome frame, hide video label
        # Recreate video_label to avoid TclError with stale image references
        self._recreate_video_label()
        self.video_label.grid_remove()
        self.welcome_frame.grid()

    def _toggle_preview(self) -> None:
        """Toggle camera preview on/off for resource saving."""
        self._preview_enabled = self.preview_switch.get()

        if not self._preview_enabled:
            # Recreate video_label to avoid TclError with deleted images
            self._recreate_video_label()
            self.video_label.configure(text=t('preview_off_message'))
        else:
            # Recreate video_label to start fresh
            self._recreate_video_label()

    def _recreate_video_label(self) -> None:
        """Recreate video_label to avoid TclError with stale image references."""
        # Destroy old label
        if hasattr(self, 'video_label') and self.video_label is not None:
            self.video_label.destroy()

        # Create new label
        self.video_label = ctk.CTkLabel(
            self.video_frame,
            text=""
        )
        self.video_label.grid(row=0, column=0)

    def _capture_loop(self) -> None:
        """Background thread for frame capture and processing."""
        while self._is_running:
            self._frame_count += 1

            # Frame skip for performance
            if self._frame_count % self.settings.frame_skip != 0:
                time.sleep(0.01)
                continue

            ret, frame_bgr = self.camera.read_frame()
            if not ret or frame_bgr is None:
                continue

            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

            # Process with MediaPipe (always needed for detection)
            hands = self.hand_tracker.process(frame_rgb)
            head = self.pose_tracker.process(frame_rgb)

            # Analyze proximity (always needed for alerts)
            result = self.analyzer.analyze(hands, head)

            # Only do visual processing if preview is enabled
            # This saves CPU by skipping: drawing, overlay, color conversion, frame storage
            if self._preview_enabled:
                # Draw visualizations
                display_frame = frame_bgr.copy()

                # Draw hand landmarks
                if hands:
                    display_frame = self.hand_tracker.draw_landmarks(display_frame, hands)

                # Draw head region
                if head:
                    display_frame = self.pose_tracker.draw_landmarks(display_frame, head)

                # Add status overlay
                display_frame = self._draw_status_overlay(display_frame, result)

                # Convert for display
                display_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

                with self._frame_lock:
                    self._current_frame = display_rgb
                    self._current_result = result
            else:
                # Only store result for status bar updates (no frame processing)
                with self._frame_lock:
                    self._current_frame = None
                    self._current_result = result

            time.sleep(0.01)

    def _draw_status_overlay(self, frame: np.ndarray, result) -> np.ndarray:
        """Draw status information on frame with Korean text support."""
        h, w = frame.shape[:2]

        # Background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (280, 75), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

        # Convert BGR to RGB for PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(pil_image)

        # Try to load Korean font
        try:
            # Windows Korean fonts
            font_large = ImageFont.truetype("malgun.ttf", 18)
            font_small = ImageFont.truetype("malgun.ttf", 14)
        except OSError:
            try:
                # Alternative: Windows Gothic
                font_large = ImageFont.truetype("msgothic.ttc", 18)
                font_small = ImageFont.truetype("msgothic.ttc", 14)
            except OSError:
                # Fallback to default
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

        # Status text color (RGB for PIL)
        color = (0, 255, 0)  # Green
        if result.state == AlertState.DETECTING:
            color = (255, 255, 0)  # Yellow
        elif result.state == AlertState.ALERT:
            color = (255, 0, 0)  # Red
        elif result.state == AlertState.COOLDOWN:
            color = (128, 128, 128)  # Gray

        # Draw status message
        draw.text((20, 18), result.message, font=font_large, fill=color)

        # Distance indicator - format the value into the translation
        dist_text = t('distance_label').replace("{value:.2f}", f"{result.closest_distance:.2f}")
        draw.text((20, 45), dist_text, font=font_small, fill=(255, 255, 255))

        # Convert back to BGR for OpenCV
        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return frame

    def _update_ui(self) -> None:
        """Update UI with current frame (called from main thread)."""
        if not self._is_running:
            return

        with self._frame_lock:
            frame = self._current_frame
            result = getattr(self, '_current_result', None)

        if frame is not None:
            # Get actual display area size
            self.video_frame.update_idletasks()
            display_width = self.video_frame.winfo_width() - 20
            display_height = self.video_frame.winfo_height() - 20

            if display_width > 100 and display_height > 100:
                h, w = frame.shape[:2]

                # Calculate scale to fit within display area while maintaining aspect ratio
                scale_w = display_width / w
                scale_h = display_height / h
                scale = min(scale_w, scale_h)

                # Calculate new dimensions
                new_w = int(w * scale)
                new_h = int(h * scale)

                # Ensure valid dimensions
                if new_w > 0 and new_h > 0:
                    # Resize frame first using OpenCV
                    if scale < 1.0:
                        frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                    else:
                        frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                    # Convert to PIL Image (already resized)
                    image = Image.fromarray(frame_resized)

                    # Use ImageTk.PhotoImage directly for accurate sizing
                    photo = ImageTk.PhotoImage(image)

                    try:
                        self.video_label.configure(image=photo, text="")
                        self.video_label._image = photo  # Keep reference
                    except Exception:
                        pass  # Ignore if label is being recreated

        if result is not None:
            # Update status bar based on state
            if result.state == AlertState.IDLE:
                self.status_indicator.configure(text_color="#28a745")
                self.status_label.configure(text=t('status_normal'))
                self.info_label.configure(text=t('status_normal_desc'), text_color="#28a745")
            elif result.state == AlertState.DETECTING:
                self.status_indicator.configure(text_color="#ffc107")
                self.status_label.configure(text=t('status_detecting'))
                self.info_label.configure(text=t('status_detecting_desc'), text_color="#ffc107")
            elif result.state == AlertState.ALERT:
                self.status_indicator.configure(text_color="#dc3545")
                self.status_label.configure(text=t('status_warning'))
                self.info_label.configure(text=t('status_warning_desc'), text_color="#dc3545")
            elif result.state == AlertState.COOLDOWN:
                self.status_indicator.configure(text_color="#6c757d")
                self.status_label.configure(text=t('status_cooldown'))
                self.info_label.configure(text=t('status_cooldown_desc'), text_color="#6c757d")

            # Update progress bar
            if result.state == AlertState.DETECTING:
                progress = 1 - (result.time_until_alert / self.settings.trigger_time)
                self.progress_bar.set(progress)
            else:
                self.progress_bar.set(0)

        # Schedule next update
        self.after(33, self._update_ui)  # ~30 FPS

    def _show_alert_popup(self, message: str) -> None:
        """Show alert overlay or fullscreen alert based on settings."""
        # Check if fullscreen alert is enabled
        if self.settings.fullscreen_alert:
            self._show_fullscreen_alert()
        else:
            # Show overlay with better positioning
            self.alert_overlay.place(relx=0.5, rely=0.5, anchor="center",
                                      relwidth=0.6, relheight=0.25)

            # Hide after 2 seconds
            self.after(2000, self._hide_alert_popup)

    def _show_fullscreen_alert(self) -> None:
        """Show fullscreen alert window."""
        # Create fullscreen alert if not exists
        if self._fullscreen_alert is None:
            self._fullscreen_alert = FullscreenAlert(self)

        # Show the fullscreen alert
        self._fullscreen_alert.show_alert(duration_ms=3000)

    def _hide_alert_popup(self) -> None:
        """Hide alert overlay."""
        self.alert_overlay.place_forget()

    def _open_settings(self) -> None:
        """Open settings window."""
        if self._on_settings_click:
            self._on_settings_click()

    def _open_statistics(self) -> None:
        """Open statistics window."""
        if self._on_statistics_click:
            self._on_statistics_click()

    def _open_about(self) -> None:
        """Open about window."""
        if self._on_about_click:
            self._on_about_click()

    def _minimize_to_tray(self) -> None:
        """Minimize to system tray."""
        if self._on_minimize_to_tray:
            self._on_minimize_to_tray()
        self.withdraw()

    def set_on_minimize_to_tray(self, callback: Callable) -> None:
        """Set callback for minimize to tray action."""
        self._on_minimize_to_tray = callback

    def set_on_settings_click(self, callback: Callable) -> None:
        """Set callback for settings button click."""
        self._on_settings_click = callback

    def set_on_statistics_click(self, callback: Callable) -> None:
        """Set callback for statistics button click."""
        self._on_statistics_click = callback

    def set_on_about_click(self, callback: Callable) -> None:
        """Set callback for about button click."""
        self._on_about_click = callback

    def show_window(self) -> None:
        """Show the window (from tray)."""
        self.deiconify()
        self.lift()
        self.focus_force()

    def update_settings(self) -> None:
        """Apply updated settings."""
        self.analyzer.set_thresholds(
            distance_threshold=self.settings.sensitivity,
            trigger_time=self.settings.trigger_time,
            cooldown_time=self.settings.cooldown_time
        )
        self.alert_manager.set_sound_enabled(self.settings.sound_enabled)
        self.alert_manager.set_popup_enabled(self.settings.popup_enabled)

    def update_language(self) -> None:
        """Update UI text after language change."""
        # Title
        self.title_label.configure(text=f"🛡️ {t('app_title')}")
        self.subtitle_label.configure(text=f"  |  {t('app_subtitle')}")

        # Buttons
        if self._is_running:
            self.start_button.configure(text=t('btn_stop'))
        else:
            self.start_button.configure(text=t('btn_start'))
        self.statistics_button.configure(text=t('btn_statistics'))
        self.settings_button.configure(text=t('btn_settings'))
        self.about_button.configure(text=t('btn_about'))
        self.minimize_button.configure(text=t('btn_minimize'))

        # Welcome screen
        self.welcome_label.configure(text=t('camera_preview'))
        self.instruction_label.configure(text=t('camera_instruction'))

        # Status bar
        if not self._is_running:
            self.status_label.configure(text=t('status_standby'))
            self.info_label.configure(text=t('status_standby_desc'))
        self.progress_label.configure(text=t('detection_progress'))

        # Alert overlay
        self.alert_label.configure(text=t('alert_title'))
        self.alert_subtitle.configure(text=t('alert_subtitle'))

        # Preview toggle
        self.preview_label.configure(text=t('preview_label'))
        if not self._preview_enabled:
            self.video_label.configure(text=t('preview_off_message'))

        # Fullscreen alert
        if self._fullscreen_alert is not None:
            self._fullscreen_alert.update_language()

    def _on_close(self) -> None:
        """Handle window close."""
        self._stop_monitoring()
        self.hand_tracker.close()
        self.pose_tracker.close()
        self.destroy()
