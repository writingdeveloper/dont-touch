"""About window UI."""
import customtkinter as ctk
import webbrowser
from datetime import datetime
from typing import Optional

from utils.i18n import t
from utils.updater import (
    check_for_updates_async,
    UpdateInfo,
    open_download_page,
    get_current_version,
    APP_VERSION,
    GITHUB_RELEASES_URL
)

GITHUB_URL = "https://github.com/writingdeveloper/dont-touch"


class AboutWindow(ctk.CTkToplevel):
    """About information window."""

    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)

        # Window setup
        self.title(t('about_title'))
        self.geometry("450x550")
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
        """Create about UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # App icon and title
        icon_label = ctk.CTkLabel(
            main_frame,
            text="🛡️",
            font=ctk.CTkFont(size=64)
        )
        icon_label.grid(row=0, column=0, pady=(10, 5))

        title_label = ctk.CTkLabel(
            main_frame,
            text="Don't Touch",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=1, column=0, pady=(0, 5))

        # Version
        version_label = ctk.CTkLabel(
            main_frame,
            text=f"{t('about_version')} {APP_VERSION}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        version_label.grid(row=2, column=0, pady=(0, 20))

        # Description section
        self._create_section_header(main_frame, t('about_description_title'), 3)

        desc_label = ctk.CTkLabel(
            main_frame,
            text=t('about_description'),
            font=ctk.CTkFont(size=13),
            wraplength=380,
            justify="left"
        )
        desc_label.grid(row=4, column=0, sticky="w", padx=10, pady=(5, 15))

        # Features section
        self._create_section_header(main_frame, t('about_features_title'), 5)

        features = [
            t('about_feature_1'),
            t('about_feature_2'),
            t('about_feature_3'),
            t('about_feature_4'),
        ]

        features_text = "\n".join([f"• {f}" for f in features])
        features_label = ctk.CTkLabel(
            main_frame,
            text=features_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        )
        features_label.grid(row=6, column=0, sticky="w", padx=10, pady=(5, 15))

        # Technology section
        self._create_section_header(main_frame, t('about_tech_title'), 7)

        tech_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        tech_frame.grid(row=8, column=0, sticky="ew", padx=10, pady=(5, 15))

        technologies = [
            ("MediaPipe", t('about_tech_mediapipe')),
            ("CustomTkinter", t('about_tech_customtkinter')),
            ("OpenCV", t('about_tech_opencv')),
        ]

        for i, (name, desc) in enumerate(technologies):
            tech_item = ctk.CTkFrame(tech_frame)
            tech_item.pack(fill="x", pady=2)

            name_label = ctk.CTkLabel(
                tech_item,
                text=name,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=120,
                anchor="w"
            )
            name_label.pack(side="left", padx=10, pady=5)

            desc_label = ctk.CTkLabel(
                tech_item,
                text=desc,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            desc_label.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Links section
        self._create_section_header(main_frame, t('about_links_title'), 9)

        links_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        links_frame.grid(row=10, column=0, sticky="ew", padx=10, pady=(5, 15))
        links_frame.grid_columnconfigure((0, 1), weight=1)

        # GitHub button
        github_btn = ctk.CTkButton(
            links_frame,
            text=f"🔗 {t('about_github')}",
            command=self._open_github,
            fg_color="#333333",
            hover_color="#555555"
        )
        github_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Report issue button
        issue_btn = ctk.CTkButton(
            links_frame,
            text=f"🐛 {t('about_report_issue')}",
            command=self._open_issues,
            fg_color="#d73a49",
            hover_color="#cb2431"
        )
        issue_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Update check button
        self.update_btn = ctk.CTkButton(
            links_frame,
            text=f"🔄 {t('about_check_update')}",
            command=self._check_for_updates,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.update_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Update status label (hidden by default)
        self.update_status_label = ctk.CTkLabel(
            links_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.update_status_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))

        # License section
        self._create_section_header(main_frame, t('about_license_title'), 11)

        license_label = ctk.CTkLabel(
            main_frame,
            text=t('about_license'),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        license_label.grid(row=12, column=0, sticky="w", padx=10, pady=(5, 15))

        # Copyright (dynamic year)
        current_year = datetime.now().year
        copyright_text = t('about_copyright').replace("2024", str(current_year))
        copyright_label = ctk.CTkLabel(
            main_frame,
            text=copyright_text,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        copyright_label.grid(row=13, column=0, pady=(10, 5))

        # Close button
        close_btn = ctk.CTkButton(
            self,
            text=t('about_close'),
            command=self.destroy,
            width=120
        )
        close_btn.grid(row=1, column=0, pady=15)

    def _create_section_header(self, parent: ctk.CTkFrame, text: str, row: int) -> None:
        """Create a section header."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=row, column=0, sticky="w", padx=5, pady=(10, 0))

    def _open_github(self) -> None:
        """Open GitHub repository in browser."""
        webbrowser.open(GITHUB_URL)

    def _open_issues(self) -> None:
        """Open GitHub issues page in browser."""
        webbrowser.open(f"{GITHUB_URL}/issues")

    def _check_for_updates(self) -> None:
        """Check for updates."""
        self.update_btn.configure(state="disabled", text=f"🔄 {t('about_checking_update')}")
        self.update_status_label.configure(text="", text_color="gray")
        check_for_updates_async(self._on_update_check_complete)

    def _on_update_check_complete(self, update_info: Optional[UpdateInfo]) -> None:
        """Handle update check completion."""
        # Schedule UI update on main thread
        self.after(0, lambda: self._update_ui_after_check(update_info))

    def _update_ui_after_check(self, update_info: Optional[UpdateInfo]) -> None:
        """Update UI after update check (must run on main thread)."""
        self.update_btn.configure(state="normal", text=f"🔄 {t('about_check_update')}")

        if update_info is None:
            # Check failed
            self.update_status_label.configure(
                text=t('update_check_failed'),
                text_color="#dc3545"
            )
        elif update_info.is_update_available:
            # Update available
            self.update_status_label.configure(
                text=t('update_new_version').format(version=update_info.latest_version),
                text_color="#28a745"
            )
            # Change button to download
            self.update_btn.configure(
                text=f"⬇️ {t('update_download')}",
                command=open_download_page,
                fg_color="#007bff",
                hover_color="#0056b3"
            )
        else:
            # Up to date
            self.update_status_label.configure(
                text=t('update_up_to_date'),
                text_color="#28a745"
            )
