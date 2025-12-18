"""Statistics window UI with calendar and charts."""
import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
from pathlib import Path
from typing import Optional, Dict, Callable

from utils.statistics import StatisticsManager, DailyStats
from utils.i18n import t

# Path to the app icon
APP_ICON_PATH = Path(__file__).parent.parent / "assets" / "icon.ico"


class SummaryCard(ctk.CTkFrame):
    """Modern summary card widget."""

    def __init__(self, parent: ctk.CTkFrame, title: str, value: str,
                 icon: str = "", color: str = "#3b8ed0"):
        super().__init__(parent, corner_radius=12)

        self.grid_columnconfigure(0, weight=1)

        # Icon and value row (centered)
        value_frame = ctk.CTkFrame(self, fg_color="transparent")
        value_frame.pack(pady=(15, 5))

        if icon:
            icon_label = ctk.CTkLabel(
                value_frame,
                text=icon,
                font=ctk.CTkFont(size=24)
            )
            icon_label.pack(side="left", padx=(0, 8))

        self.value_label = ctk.CTkLabel(
            value_frame,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color
        )
        self.value_label.pack(side="left")

        # Title (centered)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.title_label.pack(pady=(0, 15))

    def update_value(self, value: str) -> None:
        """Update the displayed value."""
        self.value_label.configure(text=value)


class CalendarWidget(ctk.CTkFrame):
    """Calendar widget showing monthly touch statistics."""

    def __init__(self, parent: ctk.CTkFrame, stats_manager: StatisticsManager,
                 on_date_select: Optional[Callable[[str], None]] = None):
        super().__init__(parent, corner_radius=12)

        self.stats_manager = stats_manager
        self.on_date_select = on_date_select

        # Current displayed month
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.selected_date: Optional[str] = None

        self.grid_columnconfigure(0, weight=1)
        self._create_ui()

    def _create_ui(self) -> None:
        """Create calendar UI."""
        # Navigation header
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=36,
            height=36,
            corner_radius=18,
            fg_color="#404040",
            hover_color="#505050",
            command=self._prev_month
        )
        self.prev_btn.pack(side="left")

        self.month_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.month_label.pack(side="left", expand=True)

        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=36,
            height=36,
            corner_radius=18,
            fg_color="#404040",
            hover_color="#505050",
            command=self._next_month
        )
        self.next_btn.pack(side="right")

        # Calendar grid container
        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        # Configure grid columns
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)

        self._render_calendar()

    def _render_calendar(self) -> None:
        """Render the calendar for current month."""
        # Clear existing widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Update month label
        month_names = [
            t('month_1'), t('month_2'), t('month_3'), t('month_4'),
            t('month_5'), t('month_6'), t('month_7'), t('month_8'),
            t('month_9'), t('month_10'), t('month_11'), t('month_12')
        ]
        self.month_label.configure(text=f"{self.current_year} {month_names[self.current_month - 1]}")

        # Day headers
        day_names = [
            t('day_sun'), t('day_mon'), t('day_tue'), t('day_wed'),
            t('day_thu'), t('day_fri'), t('day_sat')
        ]
        for i, day in enumerate(day_names):
            # Sunday in red, Saturday in blue
            if i == 0:
                text_color = "#ff6b6b"
            elif i == 6:
                text_color = "#74b9ff"
            else:
                text_color = "gray"

            label = ctk.CTkLabel(
                self.calendar_frame,
                text=day,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=text_color
            )
            label.grid(row=0, column=i, pady=(0, 8), sticky="ew")

        # Get touch data for this month
        touch_data = self.stats_manager.get_monthly_calendar(self.current_year, self.current_month)

        # Get calendar for this month (Sunday start)
        cal = calendar.Calendar(firstweekday=6)  # Sunday start
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        # Find max touches for color scaling
        max_touches = max(touch_data.values()) if touch_data else 1

        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")

        for week_num, week in enumerate(month_days, start=1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    label = ctk.CTkLabel(self.calendar_frame, text="", width=44, height=44)
                    label.grid(row=week_num, column=day_num, padx=1, pady=1)
                else:
                    date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day:02d}"
                    touches = touch_data.get(day, 0)

                    # Determine background color based on touch count
                    if touches == 0:
                        # No touches - subtle green
                        bg_color = "#1e3a2f"
                        text_color = "#6fcf97"
                    else:
                        # Touches - gradient from yellow to red based on intensity
                        intensity = min(touches / max(max_touches, 1), 1.0)
                        if intensity < 0.5:
                            # Yellow to orange
                            r = int(255)
                            g = int(200 - 100 * intensity)
                            b = int(50)
                        else:
                            # Orange to red
                            r = int(255 - 50 * (intensity - 0.5))
                            g = int(100 - 100 * (intensity - 0.5))
                            b = int(50)
                        bg_color = f"#{r:02x}{g:02x}{b:02x}"
                        text_color = "white"

                    # Highlight today
                    if date_str == today_str:
                        border_color = "#3b8ed0"
                        border_width = 3
                    else:
                        border_color = None
                        border_width = 0

                    # Create day cell
                    cell_frame = ctk.CTkFrame(
                        self.calendar_frame,
                        fg_color=bg_color,
                        width=44,
                        height=44,
                        corner_radius=8,
                        border_color=border_color,
                        border_width=border_width
                    )
                    cell_frame.grid(row=week_num, column=day_num, padx=1, pady=1)
                    cell_frame.grid_propagate(False)

                    # Day number
                    day_label = ctk.CTkLabel(
                        cell_frame,
                        text=str(day),
                        font=ctk.CTkFont(size=13, weight="bold" if touches > 0 else "normal"),
                        text_color=text_color
                    )
                    day_label.place(relx=0.5, rely=0.35, anchor="center")

                    # Touch count (if any)
                    if touches > 0:
                        count_label = ctk.CTkLabel(
                            cell_frame,
                            text=str(touches),
                            font=ctk.CTkFont(size=9),
                            text_color=text_color
                        )
                        count_label.place(relx=0.5, rely=0.72, anchor="center")

                    # Bind click event
                    cell_frame.bind("<Button-1>", lambda e, d=date_str: self._on_day_click(d))
                    day_label.bind("<Button-1>", lambda e, d=date_str: self._on_day_click(d))
                    if touches > 0:
                        count_label.bind("<Button-1>", lambda e, d=date_str: self._on_day_click(d))

    def _on_day_click(self, date_str: str) -> None:
        """Handle day click."""
        self.selected_date = date_str
        if self.on_date_select:
            self.on_date_select(date_str)

    def _prev_month(self) -> None:
        """Go to previous month."""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._render_calendar()

    def _next_month(self) -> None:
        """Go to next month."""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._render_calendar()

    def refresh(self) -> None:
        """Refresh the calendar display."""
        self._render_calendar()


class HourlyChartWidget(ctk.CTkFrame):
    """Bar chart showing hourly touch distribution."""

    def __init__(self, parent: ctk.CTkFrame, stats_manager: StatisticsManager):
        super().__init__(parent, corner_radius=12)

        self.stats_manager = stats_manager
        self.grid_columnconfigure(0, weight=1)
        self._create_ui()

    def _create_ui(self) -> None:
        """Create chart UI."""
        # Title
        title = ctk.CTkLabel(
            self,
            text=t('stats_hourly_pattern'),
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        title.pack(anchor="w", padx=15, pady=(15, 10))

        # Chart container
        self.chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._render_chart()

    def _render_chart(self) -> None:
        """Render the hourly chart."""
        # Clear existing
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        hourly_data = self.stats_manager.get_hourly_pattern(days=7)
        max_count = max(hourly_data.values()) if hourly_data else 1

        # Create bars for each hour
        for hour in range(24):
            self.chart_frame.grid_columnconfigure(hour, weight=1)

            count = hourly_data.get(hour, 0)
            height_pct = (count / max_count * 100) if max_count > 0 else 0

            # Bar container
            bar_container = ctk.CTkFrame(self.chart_frame, fg_color="transparent", height=70)
            bar_container.grid(row=0, column=hour, sticky="s", padx=0)
            bar_container.grid_propagate(False)

            # Bar
            bar_height = max(3, int(height_pct * 0.65))

            # Color gradient based on time of day
            if 6 <= hour < 12:
                bar_color = "#f39c12"  # Morning - orange
            elif 12 <= hour < 18:
                bar_color = "#e74c3c"  # Afternoon - red
            elif 18 <= hour < 22:
                bar_color = "#9b59b6"  # Evening - purple
            else:
                bar_color = "#3498db"  # Night - blue

            if count == 0:
                bar_color = "#404040"

            bar = ctk.CTkFrame(bar_container, fg_color=bar_color, width=12, height=bar_height, corner_radius=3)
            bar.place(relx=0.5, rely=1.0, anchor="s")

            # Hour label (show every 4 hours)
            if hour % 4 == 0:
                hour_label = ctk.CTkLabel(
                    self.chart_frame,
                    text=f"{hour}",
                    font=ctk.CTkFont(size=10),
                    text_color="gray"
                )
                hour_label.grid(row=1, column=hour, sticky="n", pady=(2, 0))

    def refresh(self) -> None:
        """Refresh the chart."""
        self._render_chart()


class DailyDetailWidget(ctk.CTkFrame):
    """Widget showing detailed stats for a specific day."""

    def __init__(self, parent: ctk.CTkFrame, stats_manager: StatisticsManager):
        super().__init__(parent, corner_radius=12)

        self.stats_manager = stats_manager
        self.grid_columnconfigure(0, weight=1)
        self._create_ui()

    def _create_ui(self) -> None:
        """Create detail UI."""
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        # Date icon
        date_icon = ctk.CTkLabel(
            header_frame,
            text="📅",
            font=ctk.CTkFont(size=20)
        )
        date_icon.pack(side="left", padx=(0, 10))

        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=t('stats_today'),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(side="left")

        # Stats container
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=15, pady=(0, 15))

        self._render_stats(datetime.now().strftime("%Y-%m-%d"))

    def _render_stats(self, date_str: str) -> None:
        """Render stats for the given date."""
        # Clear existing
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats = self.stats_manager.get_daily_stats(date_str)

        # Parse date for display
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_str == datetime.now().strftime("%Y-%m-%d"):
                date_display = t('stats_today')
            else:
                # Format with weekday
                weekdays = [
                    t('day_mon'), t('day_tue'), t('day_wed'), t('day_thu'),
                    t('day_fri'), t('day_sat'), t('day_sun')
                ]
                weekday = weekdays[date_obj.weekday()]
                date_display = f"{date_obj.month}/{date_obj.day} ({weekday})"
        except ValueError:
            date_display = date_str

        self.title_label.configure(text=date_display)

        if stats is None or stats.total_touches == 0:
            no_data_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            no_data_frame.pack(fill="x", pady=20)

            no_data_icon = ctk.CTkLabel(
                no_data_frame,
                text="✨",
                font=ctk.CTkFont(size=32)
            )
            no_data_icon.pack()

            no_data_label = ctk.CTkLabel(
                no_data_frame,
                text=t('stats_no_data'),
                text_color="gray",
                font=ctk.CTkFont(size=13)
            )
            no_data_label.pack(pady=(5, 0))
            return

        # Stats in grid
        stats_grid = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x")
        stats_grid.grid_columnconfigure((0, 1), weight=1)

        # Total touches
        self._create_stat_row(stats_grid, 0, "🖐️", t('stats_total_touches'), str(stats.total_touches))

        # Average duration
        self._create_stat_row(stats_grid, 1, "⏱️", t('stats_avg_duration'), f"{stats.avg_duration:.1f}s")

        # First/Last touch
        if stats.first_touch:
            self._create_stat_row(stats_grid, 2, "🌅", t('stats_first_touch'), stats.first_touch)
        if stats.last_touch:
            self._create_stat_row(stats_grid, 3, "🌙", t('stats_last_touch'), stats.last_touch)

        # Peak hour
        if stats.hourly_distribution:
            peak_hour = max(stats.hourly_distribution, key=stats.hourly_distribution.get)
            peak_count = stats.hourly_distribution[peak_hour]
            self._create_stat_row(stats_grid, 4, "📈", t('stats_peak_hour'), f"{peak_hour}:00 ({peak_count})")

    def _create_stat_row(self, parent: ctk.CTkFrame, row: int, icon: str, label: str, value: str) -> None:
        """Create a stat display row with icon."""
        row_frame = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=8, height=40)
        row_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=3)
        row_frame.grid_propagate(False)

        # Icon
        icon_label = ctk.CTkLabel(row_frame, text=icon, font=ctk.CTkFont(size=14))
        icon_label.pack(side="left", padx=(12, 8))

        # Label
        label_widget = ctk.CTkLabel(
            row_frame,
            text=label,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        label_widget.pack(side="left")

        # Value
        value_widget = ctk.CTkLabel(
            row_frame,
            text=value,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        value_widget.pack(side="right", padx=12)

    def show_date(self, date_str: str) -> None:
        """Show stats for a specific date."""
        self._render_stats(date_str)

    def refresh(self) -> None:
        """Refresh current display."""
        self._render_stats(datetime.now().strftime("%Y-%m-%d"))


class StatisticsWindow(ctk.CTkToplevel):
    """Statistics and calendar window."""

    def __init__(self, parent: ctk.CTk, stats_manager: StatisticsManager):
        super().__init__(parent)

        self.stats_manager = stats_manager

        # Window setup
        self.title(t('stats_title'))
        self.geometry("700x750")
        self.minsize(650, 600)

        # Set window icon
        if APP_ICON_PATH.exists():
            self.after(200, lambda: self.iconbitmap(str(APP_ICON_PATH)))

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
        """Create statistics UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)

        # ========== Summary Cards (Top Row) ==========
        self._create_summary_section(main_frame)

        # ========== Calendar (Full Width) ==========
        self.calendar = CalendarWidget(
            main_frame,
            self.stats_manager,
            on_date_select=self._on_date_select
        )
        self.calendar.grid(row=1, column=0, sticky="ew", pady=(15, 0))

        # ========== Legend ==========
        legend_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        legend_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self._create_legend(legend_frame)

        # ========== Daily Detail ==========
        self.daily_detail = DailyDetailWidget(main_frame, self.stats_manager)
        self.daily_detail.grid(row=3, column=0, sticky="ew", pady=(15, 0))

        # ========== Hourly Chart ==========
        self.hourly_chart = HourlyChartWidget(main_frame, self.stats_manager)
        self.hourly_chart.grid(row=4, column=0, sticky="ew", pady=(15, 0))

        # Close button
        close_btn = ctk.CTkButton(
            self,
            text=t('stats_close'),
            height=36,
            corner_radius=18,
            command=self.destroy
        )
        close_btn.grid(row=1, column=0, pady=15)

    def _create_summary_section(self, parent: ctk.CTkFrame) -> None:
        """Create summary statistics section with modern cards."""
        # Get stats data
        total_stats = self.stats_manager.get_total_stats()
        weekly_stats = self.stats_manager.get_weekly_stats()
        streak_info = self.stats_manager.get_streak_info()

        # Summary cards container
        summary_frame = ctk.CTkFrame(parent, fg_color="transparent")
        summary_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        summary_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Total touches card
        card1 = SummaryCard(
            summary_frame,
            t('stats_total_all_time'),
            str(total_stats['total_touches']),
            icon="🖐️",
            color="#e74c3c"
        )
        card1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Daily average card
        card2 = SummaryCard(
            summary_frame,
            t('stats_weekly_avg'),
            f"{weekly_stats.daily_average:.1f}",
            icon="📊",
            color="#f39c12"
        )
        card2.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Streak card
        streak_days = streak_info['current_streak']
        card3 = SummaryCard(
            summary_frame,
            t('stats_streak'),
            t('stats_days').replace("{n}", str(streak_days)),
            icon="🏆",
            color="#27ae60"
        )
        card3.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def _create_legend(self, parent: ctk.CTkFrame) -> None:
        """Create color legend for calendar."""
        legend_inner = ctk.CTkFrame(parent, fg_color="transparent")
        legend_inner.pack(anchor="center")

        # Good (no touches)
        good_box = ctk.CTkFrame(legend_inner, fg_color="#1e3a2f", width=16, height=16, corner_radius=4)
        good_box.pack(side="left", padx=(0, 5))
        good_label = ctk.CTkLabel(legend_inner, text="0", font=ctk.CTkFont(size=11), text_color="gray")
        good_label.pack(side="left", padx=(0, 20))

        # Medium
        med_box = ctk.CTkFrame(legend_inner, fg_color="#f39c12", width=16, height=16, corner_radius=4)
        med_box.pack(side="left", padx=(0, 5))
        med_label = ctk.CTkLabel(legend_inner, text="1-5", font=ctk.CTkFont(size=11), text_color="gray")
        med_label.pack(side="left", padx=(0, 20))

        # High
        high_box = ctk.CTkFrame(legend_inner, fg_color="#e74c3c", width=16, height=16, corner_radius=4)
        high_box.pack(side="left", padx=(0, 5))
        high_label = ctk.CTkLabel(legend_inner, text="6+", font=ctk.CTkFont(size=11), text_color="gray")
        high_label.pack(side="left")

    def _on_date_select(self, date_str: str) -> None:
        """Handle date selection from calendar."""
        self.daily_detail.show_date(date_str)
