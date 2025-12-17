"""Statistics management for tracking face-touching events."""
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class TouchEvent:
    """A single face-touching event."""
    timestamp: str  # ISO format datetime
    duration: float  # How long hand was near face before alert (seconds)
    closest_distance: float  # Minimum distance detected


@dataclass
class DailyStats:
    """Statistics for a single day."""
    date: str  # YYYY-MM-DD format
    total_touches: int
    total_duration: float  # Total seconds hands were near face
    avg_duration: float  # Average duration per touch
    first_touch: Optional[str]  # Time of first touch (HH:MM)
    last_touch: Optional[str]  # Time of last touch (HH:MM)
    hourly_distribution: Dict[int, int]  # Hour (0-23) -> count


@dataclass
class WeeklyStats:
    """Statistics for a week."""
    start_date: str
    end_date: str
    total_touches: int
    daily_average: float
    best_day: Optional[str]  # Day with fewest touches
    worst_day: Optional[str]  # Day with most touches
    daily_counts: Dict[str, int]  # Date -> count


class StatisticsManager:
    """Manages statistics tracking and persistence using SQLite."""

    DEFAULT_DB_DIR = Path.home() / ".dont-touch"
    DB_FILE = "statistics.db"

    def __init__(self, db_dir: Optional[Path] = None):
        self.db_dir = db_dir or self.DEFAULT_DB_DIR
        self.db_path = self.db_dir / self.DB_FILE
        self._ensure_db_dir()
        self._init_database()

    def _ensure_db_dir(self) -> None:
        """Create database directory if it doesn't exist."""
        self.db_dir.mkdir(parents=True, exist_ok=True)

    def _init_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Events table - stores individual touch events
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS touch_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    duration REAL NOT NULL,
                    closest_distance REAL NOT NULL,
                    date TEXT NOT NULL,
                    hour INTEGER NOT NULL
                )
            ''')

            # Daily summaries table - cached daily statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    date TEXT PRIMARY KEY,
                    total_touches INTEGER NOT NULL,
                    total_duration REAL NOT NULL,
                    first_touch TEXT,
                    last_touch TEXT,
                    hourly_distribution TEXT
                )
            ''')

            # Create indexes for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_date ON touch_events(date)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_timestamp ON touch_events(timestamp)
            ''')

            conn.commit()

    def log_event(self, duration: float, closest_distance: float) -> None:
        """Log a new face-touching event.

        Args:
            duration: How long the hand was near face before alert (seconds)
            closest_distance: The minimum distance detected
        """
        now = datetime.now()
        timestamp = now.isoformat()
        date = now.strftime("%Y-%m-%d")
        hour = now.hour

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO touch_events (timestamp, duration, closest_distance, date, hour)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, duration, closest_distance, date, hour))
            conn.commit()

        # Update daily summary cache
        self._update_daily_summary(date)

    def _update_daily_summary(self, date: str) -> None:
        """Update the cached daily summary for a given date."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get all events for the date
            cursor.execute('''
                SELECT timestamp, duration, hour FROM touch_events
                WHERE date = ?
                ORDER BY timestamp
            ''', (date,))

            events = cursor.fetchall()
            if not events:
                return

            total_touches = len(events)
            total_duration = sum(e[1] for e in events)
            first_touch = datetime.fromisoformat(events[0][0]).strftime("%H:%M")
            last_touch = datetime.fromisoformat(events[-1][0]).strftime("%H:%M")

            # Calculate hourly distribution
            hourly = {}
            for e in events:
                hour = e[2]
                hourly[hour] = hourly.get(hour, 0) + 1

            cursor.execute('''
                INSERT OR REPLACE INTO daily_summaries
                (date, total_touches, total_duration, first_touch, last_touch, hourly_distribution)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, total_touches, total_duration, first_touch, last_touch, json.dumps(hourly)))

            conn.commit()

    def get_daily_stats(self, date: Optional[str] = None) -> Optional[DailyStats]:
        """Get statistics for a specific date.

        Args:
            date: Date in YYYY-MM-DD format. Defaults to today.

        Returns:
            DailyStats object or None if no data for the date.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT total_touches, total_duration, first_touch, last_touch, hourly_distribution
                FROM daily_summaries
                WHERE date = ?
            ''', (date,))

            row = cursor.fetchone()
            if not row:
                return DailyStats(
                    date=date,
                    total_touches=0,
                    total_duration=0.0,
                    avg_duration=0.0,
                    first_touch=None,
                    last_touch=None,
                    hourly_distribution={}
                )

            total_touches, total_duration, first_touch, last_touch, hourly_json = row
            hourly = json.loads(hourly_json) if hourly_json else {}
            # Convert string keys to int
            hourly = {int(k): v for k, v in hourly.items()}

            return DailyStats(
                date=date,
                total_touches=total_touches,
                total_duration=total_duration,
                avg_duration=total_duration / total_touches if total_touches > 0 else 0.0,
                first_touch=first_touch,
                last_touch=last_touch,
                hourly_distribution=hourly
            )

    def get_weekly_stats(self, start_date: Optional[str] = None) -> WeeklyStats:
        """Get statistics for a week starting from the given date.

        Args:
            start_date: Start date in YYYY-MM-DD format. Defaults to 7 days ago.

        Returns:
            WeeklyStats object.
        """
        if start_date is None:
            start = datetime.now() - timedelta(days=6)
            start_date = start.strftime("%Y-%m-%d")
        else:
            start = datetime.strptime(start_date, "%Y-%m-%d")

        end = start + timedelta(days=6)
        end_date = end.strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, total_touches
                FROM daily_summaries
                WHERE date >= ? AND date <= ?
                ORDER BY date
            ''', (start_date, end_date))

            rows = cursor.fetchall()

        daily_counts = {}
        total_touches = 0
        best_day = None
        worst_day = None
        min_touches = float('inf')
        max_touches = 0

        # Fill in all days in the range
        for i in range(7):
            d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_counts[d] = 0

        for date, count in rows:
            daily_counts[date] = count
            total_touches += count

            if count <= min_touches:
                min_touches = count
                best_day = date
            if count >= max_touches:
                max_touches = count
                worst_day = date

        days_with_data = len([c for c in daily_counts.values() if c > 0])
        daily_average = total_touches / 7  # Always divide by 7 for weekly average

        return WeeklyStats(
            start_date=start_date,
            end_date=end_date,
            total_touches=total_touches,
            daily_average=daily_average,
            best_day=best_day if min_touches < float('inf') else None,
            worst_day=worst_day if max_touches > 0 else None,
            daily_counts=daily_counts
        )

    def get_monthly_calendar(self, year: int, month: int) -> Dict[int, int]:
        """Get touch counts for each day of a month (for calendar display).

        Args:
            year: Year (e.g., 2024)
            month: Month (1-12)

        Returns:
            Dictionary mapping day number (1-31) to touch count.
        """
        start_date = f"{year:04d}-{month:02d}-01"

        # Calculate end of month
        if month == 12:
            end_date = f"{year + 1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month + 1:02d}-01"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, total_touches
                FROM daily_summaries
                WHERE date >= ? AND date < ?
            ''', (start_date, end_date))

            rows = cursor.fetchall()

        calendar_data = {}
        for date_str, count in rows:
            day = int(date_str.split("-")[2])
            calendar_data[day] = count

        return calendar_data

    def get_streak_info(self) -> Dict[str, Any]:
        """Get information about touch-free streaks.

        Returns:
            Dictionary with streak information:
            - current_streak: Days since last touch (0 if touched today)
            - best_streak: Longest streak of touch-free days
            - last_touch_date: Date of most recent touch
        """
        today = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get the most recent date with touches
            cursor.execute('''
                SELECT date FROM daily_summaries
                WHERE total_touches > 0
                ORDER BY date DESC
                LIMIT 1
            ''')

            row = cursor.fetchone()
            if not row:
                return {
                    "current_streak": 0,
                    "best_streak": 0,
                    "last_touch_date": None
                }

            last_touch_date = row[0]

            # Calculate current streak (days since last touch)
            last_touch = datetime.strptime(last_touch_date, "%Y-%m-%d")
            today_dt = datetime.strptime(today, "%Y-%m-%d")
            current_streak = (today_dt - last_touch).days
            if last_touch_date == today:
                current_streak = 0

            # Get all dates with data to calculate best streak
            cursor.execute('''
                SELECT date, total_touches FROM daily_summaries
                ORDER BY date
            ''')

            all_data = cursor.fetchall()

        # Calculate best streak (longest gap between touch days)
        best_streak = 0
        prev_touch_date = None

        for date_str, count in all_data:
            if count > 0:
                if prev_touch_date:
                    d1 = datetime.strptime(prev_touch_date, "%Y-%m-%d")
                    d2 = datetime.strptime(date_str, "%Y-%m-%d")
                    gap = (d2 - d1).days - 1  # Days between touches
                    best_streak = max(best_streak, gap)
                prev_touch_date = date_str

        return {
            "current_streak": current_streak,
            "best_streak": best_streak,
            "last_touch_date": last_touch_date
        }

    def get_hourly_pattern(self, days: int = 7) -> Dict[int, int]:
        """Get aggregated hourly touch pattern over recent days.

        Args:
            days: Number of days to include in the analysis.

        Returns:
            Dictionary mapping hour (0-23) to total touch count.
        """
        start_date = (datetime.now() - timedelta(days=days-1)).strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT hour, COUNT(*) as count
                FROM touch_events
                WHERE date >= ?
                GROUP BY hour
                ORDER BY hour
            ''', (start_date,))

            rows = cursor.fetchall()

        # Initialize all hours to 0
        hourly = {h: 0 for h in range(24)}
        for hour, count in rows:
            hourly[hour] = count

        return hourly

    def get_recent_events(self, limit: int = 10) -> List[TouchEvent]:
        """Get the most recent touch events.

        Args:
            limit: Maximum number of events to return.

        Returns:
            List of TouchEvent objects, most recent first.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT timestamp, duration, closest_distance
                FROM touch_events
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            rows = cursor.fetchall()

        return [
            TouchEvent(timestamp=r[0], duration=r[1], closest_distance=r[2])
            for r in rows
        ]

    def get_total_stats(self) -> Dict[str, Any]:
        """Get overall statistics since tracking began.

        Returns:
            Dictionary with total statistics.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total touches and duration
            cursor.execute('''
                SELECT COUNT(*), COALESCE(SUM(duration), 0)
                FROM touch_events
            ''')
            total_touches, total_duration = cursor.fetchone()

            # First and last event dates
            cursor.execute('''
                SELECT MIN(date), MAX(date)
                FROM touch_events
            ''')
            first_date, last_date = cursor.fetchone()

            # Days tracked
            cursor.execute('''
                SELECT COUNT(DISTINCT date)
                FROM touch_events
            ''')
            days_with_touches = cursor.fetchone()[0]

        return {
            "total_touches": total_touches,
            "total_duration": total_duration,
            "avg_duration": total_duration / total_touches if total_touches > 0 else 0,
            "first_date": first_date,
            "last_date": last_date,
            "days_with_touches": days_with_touches,
            "avg_per_day": total_touches / days_with_touches if days_with_touches > 0 else 0
        }

    def clear_old_data(self, days_to_keep: int = 90) -> int:
        """Remove data older than specified days.

        Args:
            days_to_keep: Number of days of data to keep.

        Returns:
            Number of events deleted.
        """
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Count events to be deleted
            cursor.execute('''
                SELECT COUNT(*) FROM touch_events WHERE date < ?
            ''', (cutoff_date,))
            count = cursor.fetchone()[0]

            # Delete old events
            cursor.execute('''
                DELETE FROM touch_events WHERE date < ?
            ''', (cutoff_date,))

            # Delete old summaries
            cursor.execute('''
                DELETE FROM daily_summaries WHERE date < ?
            ''', (cutoff_date,))

            conn.commit()

        return count
