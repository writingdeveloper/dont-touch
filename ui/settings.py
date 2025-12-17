"""Settings window UI."""
import customtkinter as ctk
from typing import Callable, Optional

from utils import Config


class SettingsWindow(ctk.CTkToplevel):
    """Settings configuration window."""

    def __init__(self, parent: ctk.CTk, config: Config,
                 on_save: Optional[Callable] = None):
        super().__init__(parent)

        self.config = config
        self.settings = config.settings
        self.on_save = on_save

        # Window setup
        self.title("설정")
        self.geometry("400x500")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._create_ui()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _create_ui(self) -> None:
        """Create settings UI."""
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)

        # Detection Settings Section
        self._create_section_header(main_frame, "감지 설정", 0)

        # Sensitivity slider
        sensitivity_frame = ctk.CTkFrame(main_frame)
        sensitivity_frame.grid(row=1, column=0, sticky="ew", pady=5)
        sensitivity_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sensitivity_frame, text="민감도:").grid(row=0, column=0, padx=10, pady=5)
        self.sensitivity_slider = ctk.CTkSlider(
            sensitivity_frame,
            from_=0.05,
            to=0.5,
            number_of_steps=45
        )
        self.sensitivity_slider.set(self.settings.sensitivity)
        self.sensitivity_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.sensitivity_label = ctk.CTkLabel(sensitivity_frame, text=f"{self.settings.sensitivity:.2f}")
        self.sensitivity_label.grid(row=0, column=2, padx=10, pady=5)
        self.sensitivity_slider.configure(command=self._update_sensitivity_label)

        # Trigger time slider
        trigger_frame = ctk.CTkFrame(main_frame)
        trigger_frame.grid(row=2, column=0, sticky="ew", pady=5)
        trigger_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(trigger_frame, text="경고 시간(초):").grid(row=0, column=0, padx=10, pady=5)
        self.trigger_slider = ctk.CTkSlider(
            trigger_frame,
            from_=1,
            to=10,
            number_of_steps=18
        )
        self.trigger_slider.set(self.settings.trigger_time)
        self.trigger_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.trigger_label = ctk.CTkLabel(trigger_frame, text=f"{self.settings.trigger_time:.1f}")
        self.trigger_label.grid(row=0, column=2, padx=10, pady=5)
        self.trigger_slider.configure(command=self._update_trigger_label)

        # Cooldown time slider
        cooldown_frame = ctk.CTkFrame(main_frame)
        cooldown_frame.grid(row=3, column=0, sticky="ew", pady=5)
        cooldown_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cooldown_frame, text="대기 시간(초):").grid(row=0, column=0, padx=10, pady=5)
        self.cooldown_slider = ctk.CTkSlider(
            cooldown_frame,
            from_=5,
            to=30,
            number_of_steps=25
        )
        self.cooldown_slider.set(self.settings.cooldown_time)
        self.cooldown_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.cooldown_label = ctk.CTkLabel(cooldown_frame, text=f"{self.settings.cooldown_time:.0f}")
        self.cooldown_label.grid(row=0, column=2, padx=10, pady=5)
        self.cooldown_slider.configure(command=self._update_cooldown_label)

        # Alert Settings Section
        self._create_section_header(main_frame, "알림 설정", 4)

        # Sound enabled
        self.sound_var = ctk.BooleanVar(value=self.settings.sound_enabled)
        sound_check = ctk.CTkCheckBox(
            main_frame,
            text="소리 알림",
            variable=self.sound_var
        )
        sound_check.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        # Popup enabled
        self.popup_var = ctk.BooleanVar(value=self.settings.popup_enabled)
        popup_check = ctk.CTkCheckBox(
            main_frame,
            text="팝업 알림",
            variable=self.popup_var
        )
        popup_check.grid(row=6, column=0, sticky="w", padx=10, pady=5)

        # App Settings Section
        self._create_section_header(main_frame, "앱 설정", 7)

        # Start minimized
        self.start_minimized_var = ctk.BooleanVar(value=self.settings.start_minimized)
        start_min_check = ctk.CTkCheckBox(
            main_frame,
            text="최소화 상태로 시작",
            variable=self.start_minimized_var
        )
        start_min_check.grid(row=8, column=0, sticky="w", padx=10, pady=5)

        # Frame skip
        frameskip_frame = ctk.CTkFrame(main_frame)
        frameskip_frame.grid(row=9, column=0, sticky="ew", pady=5)
        frameskip_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frameskip_frame, text="프레임 스킵:").grid(row=0, column=0, padx=10, pady=5)
        self.frameskip_slider = ctk.CTkSlider(
            frameskip_frame,
            from_=1,
            to=5,
            number_of_steps=4
        )
        self.frameskip_slider.set(self.settings.frame_skip)
        self.frameskip_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.frameskip_label = ctk.CTkLabel(frameskip_frame, text=f"{self.settings.frame_skip}")
        self.frameskip_label.grid(row=0, column=2, padx=10, pady=5)
        self.frameskip_slider.configure(command=self._update_frameskip_label)

        # Help text
        help_text = ctk.CTkLabel(
            main_frame,
            text="(높을수록 CPU 사용량 감소, 반응 속도 저하)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        help_text.grid(row=10, column=0, sticky="w", padx=10)

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Reset button
        reset_btn = ctk.CTkButton(
            button_frame,
            text="초기화",
            command=self._reset_settings
        )
        reset_btn.grid(row=0, column=0, padx=5)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="취소",
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=1, padx=5)

        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text="저장",
            command=self._save_settings
        )
        save_btn.grid(row=0, column=2, padx=5)

    def _create_section_header(self, parent: ctk.CTkFrame, text: str, row: int) -> None:
        """Create a section header."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=row, column=0, sticky="w", padx=5, pady=(15, 5))

    def _update_sensitivity_label(self, value: float) -> None:
        """Update sensitivity label."""
        self.sensitivity_label.configure(text=f"{value:.2f}")

    def _update_trigger_label(self, value: float) -> None:
        """Update trigger time label."""
        self.trigger_label.configure(text=f"{value:.1f}")

    def _update_cooldown_label(self, value: float) -> None:
        """Update cooldown time label."""
        self.cooldown_label.configure(text=f"{value:.0f}")

    def _update_frameskip_label(self, value: float) -> None:
        """Update frame skip label."""
        self.frameskip_label.configure(text=f"{int(value)}")

    def _reset_settings(self) -> None:
        """Reset settings to defaults."""
        from utils.config import AppConfig
        defaults = AppConfig()

        self.sensitivity_slider.set(defaults.sensitivity)
        self.trigger_slider.set(defaults.trigger_time)
        self.cooldown_slider.set(defaults.cooldown_time)
        self.sound_var.set(defaults.sound_enabled)
        self.popup_var.set(defaults.popup_enabled)
        self.start_minimized_var.set(defaults.start_minimized)
        self.frameskip_slider.set(defaults.frame_skip)

        # Update labels
        self._update_sensitivity_label(defaults.sensitivity)
        self._update_trigger_label(defaults.trigger_time)
        self._update_cooldown_label(defaults.cooldown_time)
        self._update_frameskip_label(defaults.frame_skip)

    def _save_settings(self) -> None:
        """Save settings and close."""
        # Update settings
        self.settings.sensitivity = self.sensitivity_slider.get()
        self.settings.trigger_time = self.trigger_slider.get()
        self.settings.cooldown_time = self.cooldown_slider.get()
        self.settings.sound_enabled = self.sound_var.get()
        self.settings.popup_enabled = self.popup_var.get()
        self.settings.start_minimized = self.start_minimized_var.get()
        self.settings.frame_skip = int(self.frameskip_slider.get())

        # Save to file
        self.config.save()

        # Callback
        if self.on_save:
            self.on_save()

        self.destroy()
