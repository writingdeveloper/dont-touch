"""Settings window UI."""
import customtkinter as ctk
from typing import Callable, Optional

from utils import Config
from utils.startup import StartupManager
from utils.i18n import t, get_language, set_language, get_supported_languages, SUPPORTED_LANGUAGES


class SettingsWindow(ctk.CTkToplevel):
    """Settings configuration window."""

    def __init__(self, parent: ctk.CTk, config: Config,
                 on_save: Optional[Callable] = None,
                 on_language_change: Optional[Callable] = None):
        super().__init__(parent)

        self.config = config
        self.settings = config.settings
        self.on_save = on_save
        self.on_language_change = on_language_change
        self._initial_language = get_language()

        # Window setup
        self.title(t('settings_title'))
        self.geometry("400x650")
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
        self._create_section_header(main_frame, t('settings_detection'), 0)

        # Sensitivity slider
        sensitivity_frame = ctk.CTkFrame(main_frame)
        sensitivity_frame.grid(row=1, column=0, sticky="ew", pady=5)
        sensitivity_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sensitivity_frame, text=t('settings_sensitivity')).grid(row=0, column=0, padx=10, pady=5)
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

        ctk.CTkLabel(trigger_frame, text=t('settings_trigger_time')).grid(row=0, column=0, padx=10, pady=5)
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

        ctk.CTkLabel(cooldown_frame, text=t('settings_cooldown_time')).grid(row=0, column=0, padx=10, pady=5)
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
        self._create_section_header(main_frame, t('settings_alerts'), 4)

        # Sound enabled
        self.sound_var = ctk.BooleanVar(value=self.settings.sound_enabled)
        sound_check = ctk.CTkCheckBox(
            main_frame,
            text=t('settings_sound'),
            variable=self.sound_var
        )
        sound_check.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        # Popup enabled
        self.popup_var = ctk.BooleanVar(value=self.settings.popup_enabled)
        popup_check = ctk.CTkCheckBox(
            main_frame,
            text=t('settings_popup'),
            variable=self.popup_var
        )
        popup_check.grid(row=6, column=0, sticky="w", padx=10, pady=5)

        # Fullscreen alert
        self.fullscreen_alert_var = ctk.BooleanVar(value=self.settings.fullscreen_alert)
        fullscreen_check = ctk.CTkCheckBox(
            main_frame,
            text=t('settings_fullscreen_alert'),
            variable=self.fullscreen_alert_var
        )
        fullscreen_check.grid(row=7, column=0, sticky="w", padx=10, pady=5)

        # Fullscreen alert help text
        fullscreen_help = ctk.CTkLabel(
            main_frame,
            text=t('settings_fullscreen_alert_help'),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        fullscreen_help.grid(row=8, column=0, sticky="w", padx=25)

        # App Settings Section
        self._create_section_header(main_frame, t('settings_app'), 9)

        # Auto start with Windows
        self.auto_start_var = ctk.BooleanVar(value=StartupManager.is_registered())
        auto_start_check = ctk.CTkCheckBox(
            main_frame,
            text=t('settings_autostart'),
            variable=self.auto_start_var
        )
        auto_start_check.grid(row=10, column=0, sticky="w", padx=10, pady=5)

        # Start minimized
        self.start_minimized_var = ctk.BooleanVar(value=self.settings.start_minimized)
        start_min_check = ctk.CTkCheckBox(
            main_frame,
            text=t('settings_start_minimized'),
            variable=self.start_minimized_var
        )
        start_min_check.grid(row=11, column=0, sticky="w", padx=10, pady=5)

        # Frame skip
        frameskip_frame = ctk.CTkFrame(main_frame)
        frameskip_frame.grid(row=12, column=0, sticky="ew", pady=5)
        frameskip_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frameskip_frame, text=t('settings_frame_skip')).grid(row=0, column=0, padx=10, pady=5)
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
            text=t('settings_frame_skip_help'),
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        help_text.grid(row=13, column=0, sticky="w", padx=10)

        # Language Settings Section
        self._create_section_header(main_frame, t('settings_language'), 14)

        # Language selector
        lang_frame = ctk.CTkFrame(main_frame)
        lang_frame.grid(row=15, column=0, sticky="ew", pady=5)
        lang_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(lang_frame, text=t('settings_language_label')).grid(row=0, column=0, padx=10, pady=5)

        # Build language options: Auto + all supported languages
        self._lang_options = [t('settings_language_auto')]
        self._lang_codes = ['']  # Empty string means auto-detect
        for code, name in SUPPORTED_LANGUAGES.items():
            self._lang_options.append(name)
            self._lang_codes.append(code)

        # Get current selection
        current_lang = self.settings.language
        if current_lang and current_lang in SUPPORTED_LANGUAGES:
            current_index = self._lang_codes.index(current_lang)
        else:
            current_index = 0  # Auto

        self.language_var = ctk.StringVar(value=self._lang_options[current_index])
        self.language_dropdown = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.language_var,
            values=self._lang_options,
            width=200
        )
        self.language_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Button frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Reset button
        reset_btn = ctk.CTkButton(
            button_frame,
            text=t('settings_reset'),
            command=self._reset_settings
        )
        reset_btn.grid(row=0, column=0, padx=5)

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=t('settings_cancel'),
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=1, padx=5)

        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text=t('settings_save'),
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
        self.fullscreen_alert_var.set(defaults.fullscreen_alert)
        self.auto_start_var.set(defaults.auto_start)
        self.start_minimized_var.set(defaults.start_minimized)
        self.frameskip_slider.set(defaults.frame_skip)
        self.language_var.set(self._lang_options[0])  # Auto

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
        self.settings.fullscreen_alert = self.fullscreen_alert_var.get()
        self.settings.auto_start = self.auto_start_var.get()
        self.settings.start_minimized = self.start_minimized_var.get()
        self.settings.frame_skip = int(self.frameskip_slider.get())

        # Update language setting
        selected_lang_name = self.language_var.get()
        selected_index = self._lang_options.index(selected_lang_name)
        selected_lang_code = self._lang_codes[selected_index]
        self.settings.language = selected_lang_code

        # Apply language change
        language_changed = False
        if selected_lang_code:
            # Manual language selection
            if get_language() != selected_lang_code:
                set_language(selected_lang_code)
                language_changed = True
        else:
            # Auto-detect language
            from utils.i18n import init_language
            new_lang = init_language(None)
            if new_lang != self._initial_language:
                language_changed = True

        # Update Windows startup registration
        StartupManager.set_startup(self.settings.auto_start)

        # Save to file
        self.config.save()

        # Callback for settings update
        if self.on_save:
            self.on_save()

        # Callback for language change (to update all UI)
        if language_changed and self.on_language_change:
            self.on_language_change()

        self.destroy()
