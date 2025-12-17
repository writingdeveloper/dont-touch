"""Main window UI using CustomTkinter."""
import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable

from detector import Camera, HandTracker, PoseTracker, ProximityAnalyzer
from detector.analyzer import AlertState
from utils import Config, AlertManager


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self, config: Config):
        super().__init__()

        self.config = config
        self.settings = config.settings

        # Window setup
        self.title("Don't Touch - 발모벽 감지")
        self.geometry(f"{self.settings.window_width}x{self.settings.window_height}")
        self.minsize(640, 480)

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

        # Build UI
        self._create_ui()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

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

    def _create_top_bar(self) -> None:
        """Create top control bar."""
        top_frame = ctk.CTkFrame(self.main_frame, height=50)
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        top_frame.grid_columnconfigure(1, weight=1)

        # Start/Stop button
        self.start_button = ctk.CTkButton(
            top_frame,
            text="▶ 시작",
            width=100,
            command=self._toggle_monitoring
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            top_frame,
            text="발모벽 감지 시스템",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=1, padx=10, pady=10)

        # Settings button
        self.settings_button = ctk.CTkButton(
            top_frame,
            text="⚙ 설정",
            width=100,
            command=self._open_settings
        )
        self.settings_button.grid(row=0, column=2, padx=10, pady=10)

        # Minimize button
        self.minimize_button = ctk.CTkButton(
            top_frame,
            text="─ 트레이로",
            width=100,
            command=self._minimize_to_tray
        )
        self.minimize_button.grid(row=0, column=3, padx=10, pady=10)

    def _create_video_display(self) -> None:
        """Create video display area."""
        self.video_frame = ctk.CTkFrame(self.main_frame)
        self.video_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

        # Video label
        self.video_label = ctk.CTkLabel(
            self.video_frame,
            text="카메라를 시작하려면 '시작' 버튼을 클릭하세요",
            font=ctk.CTkFont(size=14)
        )
        self.video_label.grid(row=0, column=0, sticky="nsew")

    def _create_status_bar(self) -> None:
        """Create bottom status bar."""
        status_frame = ctk.CTkFrame(self.main_frame, height=60)
        status_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        status_frame.grid_columnconfigure(1, weight=1)

        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=24),
            text_color="gray"
        )
        self.status_indicator.grid(row=0, column=0, padx=10, pady=10)

        # Status message
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="대기 중",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=0, column=1, sticky="w", padx=10, pady=10)

        # Progress bar (for detection countdown)
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.grid(row=0, column=2, padx=10, pady=10)
        self.progress_bar.set(0)

    def _create_alert_overlay(self) -> None:
        """Create alert overlay (initially hidden)."""
        self.alert_overlay = ctk.CTkFrame(
            self,
            fg_color=("red", "darkred")
        )
        self.alert_label = ctk.CTkLabel(
            self.alert_overlay,
            text="⚠️ 경고! 손이 머리 근처에 있습니다!",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        self.alert_label.pack(expand=True)

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
            self.status_label.configure(text="카메라를 열 수 없습니다!")
            self.status_indicator.configure(text_color="red")
            return

        self._is_running = True
        self.start_button.configure(text="⏹ 중지")
        self.status_indicator.configure(text_color="green")
        self.status_label.configure(text="모니터링 중...")

        # Start update thread
        self._update_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._update_thread.start()

        # Start UI update
        self._update_ui()

    def _stop_monitoring(self) -> None:
        """Stop camera monitoring."""
        self._is_running = False
        self.camera.stop()

        self.start_button.configure(text="▶ 시작")
        self.status_indicator.configure(text_color="gray")
        self.status_label.configure(text="대기 중")
        self.progress_bar.set(0)

        # Reset video display
        self.video_label.configure(
            image=None,
            text="카메라를 시작하려면 '시작' 버튼을 클릭하세요"
        )

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

            # Process with MediaPipe
            hands = self.hand_tracker.process(frame_rgb)
            head = self.pose_tracker.process(frame_rgb)

            # Analyze proximity
            result = self.analyzer.analyze(hands, head)

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

            time.sleep(0.01)

    def _draw_status_overlay(self, frame: np.ndarray, result) -> np.ndarray:
        """Draw status information on frame."""
        h, w = frame.shape[:2]

        # Background for text
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 80), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

        # Status text
        color = (0, 255, 0)  # Green
        if result.state == AlertState.DETECTING:
            color = (0, 255, 255)  # Yellow
        elif result.state == AlertState.ALERT:
            color = (0, 0, 255)  # Red
        elif result.state == AlertState.COOLDOWN:
            color = (128, 128, 128)  # Gray

        cv2.putText(frame, result.message, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Distance indicator
        dist_text = f"Distance: {result.closest_distance:.2f}"
        cv2.putText(frame, dist_text, (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame

    def _update_ui(self) -> None:
        """Update UI with current frame (called from main thread)."""
        if not self._is_running:
            return

        with self._frame_lock:
            frame = self._current_frame
            result = getattr(self, '_current_result', None)

        if frame is not None:
            # Resize frame to fit display
            display_width = self.video_frame.winfo_width() - 20
            display_height = self.video_frame.winfo_height() - 20

            if display_width > 0 and display_height > 0:
                h, w = frame.shape[:2]
                scale = min(display_width / w, display_height / h)
                new_w = int(w * scale)
                new_h = int(h * scale)

                frame_resized = cv2.resize(frame, (new_w, new_h))
                image = Image.fromarray(frame_resized)
                photo = ctk.CTkImage(light_image=image, dark_image=image,
                                     size=(new_w, new_h))

                self.video_label.configure(image=photo, text="")
                self.video_label._image = photo  # Keep reference

        if result is not None:
            # Update status bar
            self.status_label.configure(text=result.message)

            # Update indicator color
            if result.state == AlertState.IDLE:
                self.status_indicator.configure(text_color="green")
            elif result.state == AlertState.DETECTING:
                self.status_indicator.configure(text_color="yellow")
            elif result.state == AlertState.ALERT:
                self.status_indicator.configure(text_color="red")
            elif result.state == AlertState.COOLDOWN:
                self.status_indicator.configure(text_color="gray")

            # Update progress bar
            if result.state == AlertState.DETECTING:
                progress = 1 - (result.time_until_alert / self.settings.trigger_time)
                self.progress_bar.set(progress)
            else:
                self.progress_bar.set(0)

        # Schedule next update
        self.after(33, self._update_ui)  # ~30 FPS

    def _show_alert_popup(self, message: str) -> None:
        """Show alert overlay."""
        # Show overlay
        self.alert_overlay.place(relx=0.5, rely=0.5, anchor="center",
                                  relwidth=0.8, relheight=0.2)
        self.alert_label.configure(text=message)

        # Hide after 2 seconds
        self.after(2000, self._hide_alert_popup)

    def _hide_alert_popup(self) -> None:
        """Hide alert overlay."""
        self.alert_overlay.place_forget()

    def _open_settings(self) -> None:
        """Open settings window."""
        if self._on_settings_click:
            self._on_settings_click()

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

    def _on_close(self) -> None:
        """Handle window close."""
        self._stop_monitoring()
        self.hand_tracker.close()
        self.pose_tracker.close()
        self.destroy()
