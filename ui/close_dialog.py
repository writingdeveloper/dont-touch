"""Close confirmation dialog."""
import customtkinter as ctk
from tkinter import font as tkfont

from utils.i18n import t


class CloseDialog(ctk.CTkToplevel):
    """Dialog asking user to choose between minimize and exit."""

    def __init__(self, parent: ctk.CTk):
        super().__init__(parent)

        self._result = "cancel"

        # Window setup
        self.title(t('close_dialog_title'))
        self.minsize(350, 160)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Build UI
        self._create_ui()

        # Auto-size window to fit content
        self.update_idletasks()
        width = max(self.winfo_reqwidth(), 400)
        height = max(self.winfo_reqheight(), 180)

        # Center on parent
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Handle window close (X button)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _create_ui(self) -> None:
        """Create dialog UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Question icon and text
        question_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        question_frame.pack(pady=(0, 20))

        icon_label = ctk.CTkLabel(
            question_frame,
            text="❓",
            font=ctk.CTkFont(size=32)
        )
        icon_label.pack(side="left", padx=(0, 10))

        text_label = ctk.CTkLabel(
            question_frame,
            text=t('close_dialog_message'),
            font=ctk.CTkFont(size=14),
            wraplength=300
        )
        text_label.pack(side="left", fill="x", expand=True)

        # Button frame using grid for equal distribution
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Minimize button
        minimize_btn = ctk.CTkButton(
            button_frame,
            text=t('close_dialog_minimize'),
            height=36,
            corner_radius=8,
            fg_color="#17a2b8",
            hover_color="#138496",
            command=self._on_minimize
        )
        minimize_btn.grid(row=0, column=0, padx=3, sticky="ew")

        # Exit button
        exit_btn = ctk.CTkButton(
            button_frame,
            text=t('close_dialog_exit'),
            height=36,
            corner_radius=8,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self._on_exit
        )
        exit_btn.grid(row=0, column=1, padx=3, sticky="ew")

        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text=t('close_dialog_cancel'),
            height=36,
            corner_radius=8,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self._on_cancel
        )
        cancel_btn.grid(row=0, column=2, padx=3, sticky="ew")

    def _on_minimize(self) -> None:
        """Handle minimize choice."""
        self._result = "minimize"
        self.destroy()

    def _on_exit(self) -> None:
        """Handle exit choice."""
        self._result = "exit"
        self.destroy()

    def _on_cancel(self) -> None:
        """Handle cancel choice."""
        self._result = "cancel"
        self.destroy()

    def get_result(self) -> str:
        """Wait for dialog to close and return result.

        Returns:
            'minimize', 'exit', or 'cancel'
        """
        self.wait_window()
        return self._result
