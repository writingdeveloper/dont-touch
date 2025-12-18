"""Proximity analysis for hand-head detection."""
import time
import math
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .hand_tracker import HandLandmarks
from .pose_tracker import HeadRegion
from utils.i18n import t


class AlertState(Enum):
    """Current alert state."""
    IDLE = "idle"
    DETECTING = "detecting"  # Hand near head, counting
    ALERT = "alert"  # Alert triggered
    COOLDOWN = "cooldown"  # Waiting after alert


@dataclass
class AnalysisResult:
    """Result of proximity analysis."""
    state: AlertState
    is_hand_near_head: bool
    proximity_duration: float  # Seconds hand has been near head
    closest_distance: float  # Normalized distance (0-1)
    time_until_alert: float  # Seconds until alert triggers
    message: str


class ProximityAnalyzer:
    """Analyzes hand-head proximity and manages alert timing."""

    def __init__(self,
                 distance_threshold: float = 0.15,
                 trigger_time: float = 3.0,
                 cooldown_time: float = 10.0):
        """Initialize the analyzer.

        Args:
            distance_threshold: Normalized distance (0-1) to consider "near"
            trigger_time: Seconds hand must be near head to trigger alert
            cooldown_time: Seconds to wait between alerts
        """
        self.distance_threshold = distance_threshold
        self.trigger_time = trigger_time
        self.cooldown_time = cooldown_time

        # State tracking
        self._state = AlertState.IDLE
        self._proximity_start_time: Optional[float] = None
        self._cooldown_start_time: Optional[float] = None
        self._alert_callback: Optional[callable] = None
        self._statistics_callback: Optional[callable] = None
        self._min_distance_during_detection: float = 1.0

    def set_alert_callback(self, callback: callable) -> None:
        """Set callback to be called when alert triggers."""
        self._alert_callback = callback

    def set_statistics_callback(self, callback: callable) -> None:
        """Set callback to be called for statistics logging.

        Callback receives: (duration: float, closest_distance: float)
        """
        self._statistics_callback = callback

    def set_thresholds(self,
                       distance_threshold: Optional[float] = None,
                       trigger_time: Optional[float] = None,
                       cooldown_time: Optional[float] = None) -> None:
        """Update threshold values."""
        if distance_threshold is not None:
            self.distance_threshold = distance_threshold
        if trigger_time is not None:
            self.trigger_time = trigger_time
        if cooldown_time is not None:
            self.cooldown_time = cooldown_time

    def analyze(self,
                hands: List[HandLandmarks],
                head: Optional[HeadRegion]) -> AnalysisResult:
        """Analyze current frame for hand-head proximity.

        Args:
            hands: List of detected hands
            head: Detected head region (or None)

        Returns:
            AnalysisResult with current state and metrics
        """
        current_time = time.time()

        # Check cooldown state
        if self._state == AlertState.COOLDOWN:
            if self._cooldown_start_time:
                elapsed = current_time - self._cooldown_start_time
                if elapsed >= self.cooldown_time:
                    self._state = AlertState.IDLE
                    self._cooldown_start_time = None
                else:
                    remaining = self.cooldown_time - elapsed
                    # Still check if hand is near head during cooldown
                    # (for UI to know whether to keep alert showing)
                    is_near = False
                    closest_dist = 1.0
                    if head is not None and hands:
                        closest_dist = self._calculate_closest_distance(hands, head)
                        is_near = closest_dist < self.distance_threshold
                    return AnalysisResult(
                        state=AlertState.COOLDOWN,
                        is_hand_near_head=is_near,
                        proximity_duration=0,
                        closest_distance=closest_dist,
                        time_until_alert=0,
                        message=t('analyzer_cooldown').replace("{remaining:.1f}", f"{remaining:.1f}")
                    )

        # No head detected
        if head is None:
            self._reset_detection()
            return AnalysisResult(
                state=AlertState.IDLE,
                is_hand_near_head=False,
                proximity_duration=0,
                closest_distance=1.0,
                time_until_alert=self.trigger_time,
                message=t('analyzer_no_face')
            )

        # No hands detected
        if not hands:
            self._reset_detection()
            return AnalysisResult(
                state=AlertState.IDLE,
                is_hand_near_head=False,
                proximity_duration=0,
                closest_distance=1.0,
                time_until_alert=self.trigger_time,
                message=t('analyzer_monitoring')
            )

        # Calculate distances
        closest_distance = self._calculate_closest_distance(hands, head)
        is_near = closest_distance < self.distance_threshold

        if is_near:
            # Start or continue detection
            if self._proximity_start_time is None:
                self._proximity_start_time = current_time
                self._state = AlertState.DETECTING
                self._min_distance_during_detection = closest_distance
            else:
                # Track minimum distance during this detection period
                self._min_distance_during_detection = min(
                    self._min_distance_during_detection, closest_distance
                )

            duration = current_time - self._proximity_start_time
            time_until_alert = max(0, self.trigger_time - duration)

            # Check if should trigger alert
            if duration >= self.trigger_time:
                self._trigger_alert(duration)
                return AnalysisResult(
                    state=AlertState.ALERT,
                    is_hand_near_head=True,
                    proximity_duration=duration,
                    closest_distance=closest_distance,
                    time_until_alert=0,
                    message=t('analyzer_warning')
                )

            return AnalysisResult(
                state=AlertState.DETECTING,
                is_hand_near_head=True,
                proximity_duration=duration,
                closest_distance=closest_distance,
                time_until_alert=time_until_alert,
                message=t('analyzer_detecting').replace("{time_until_alert:.1f}", f"{time_until_alert:.1f}")
            )
        else:
            # Hand moved away
            self._reset_detection()
            return AnalysisResult(
                state=AlertState.IDLE,
                is_hand_near_head=False,
                proximity_duration=0,
                closest_distance=closest_distance,
                time_until_alert=self.trigger_time,
                message=t('analyzer_monitoring')
            )

    def _calculate_closest_distance(self,
                                   hands: List[HandLandmarks],
                                   head: HeadRegion) -> float:
        """Calculate closest distance between any hand and head region."""
        head_center = head.head_center
        head_top = head.head_top
        head_width = head.head_width

        min_distance = float('inf')

        for hand in hands:
            # Check multiple points on the hand
            check_points = [
                hand.center,
                hand.index_finger_tip,
                hand.middle_finger_tip,
                hand.wrist
            ]

            for point in check_points:
                # Calculate distance to head region
                # Use elliptical distance to account for head shape
                dx = (point[0] - head_center[0]) / (head_width / 2 + 0.1)
                dy = (point[1] - head_top[1]) / (abs(head_center[1] - head_top[1]) + 0.1)

                # Consider point inside head region if within bounds
                if 0 <= dy <= 1.5:  # Within head height range
                    distance = abs(dx) - 1  # Distance from edge
                    if distance < 0:
                        distance = 0  # Inside head region
                else:
                    distance = math.sqrt(dx**2 + max(0, dy - 1)**2)

                min_distance = min(min_distance, max(0, distance * 0.2))

        return min_distance

    def _trigger_alert(self, duration: float) -> None:
        """Trigger alert and start cooldown."""
        self._state = AlertState.COOLDOWN
        self._cooldown_start_time = time.time()
        self._proximity_start_time = None

        # Log to statistics
        if self._statistics_callback:
            self._statistics_callback(duration, self._min_distance_during_detection)

        # Reset min distance tracking
        self._min_distance_during_detection = 1.0

        if self._alert_callback:
            self._alert_callback()

    def _reset_detection(self) -> None:
        """Reset detection state."""
        if self._state == AlertState.DETECTING:
            self._state = AlertState.IDLE
        self._proximity_start_time = None

    def reset(self) -> None:
        """Fully reset analyzer state."""
        self._state = AlertState.IDLE
        self._proximity_start_time = None
        self._cooldown_start_time = None
