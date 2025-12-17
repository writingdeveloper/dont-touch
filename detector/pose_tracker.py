"""Pose tracking module using MediaPipe."""
import cv2
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass

from mediapipe import solutions


@dataclass
class HeadRegion:
    """Container for head region data."""
    # Normalized coordinates (0-1)
    nose: Tuple[float, float, float]
    left_ear: Optional[Tuple[float, float, float]]
    right_ear: Optional[Tuple[float, float, float]]
    left_shoulder: Tuple[float, float, float]
    right_shoulder: Tuple[float, float, float]

    @property
    def head_center(self) -> Tuple[float, float]:
        """Get approximate center of head (x, y)."""
        return (self.nose[0], self.nose[1])

    @property
    def head_top(self) -> Tuple[float, float]:
        """Estimate top of head position."""
        # Estimate head top as above nose
        # Head height is roughly equal to distance from nose to shoulder center
        shoulder_y = (self.left_shoulder[1] + self.right_shoulder[1]) / 2
        head_height = abs(shoulder_y - self.nose[1]) * 0.7  # Rough estimate
        return (self.nose[0], max(0, self.nose[1] - head_height))

    @property
    def head_width(self) -> float:
        """Estimate head width based on shoulders or ears."""
        if self.left_ear and self.right_ear:
            return abs(self.left_ear[0] - self.right_ear[0]) * 1.2
        # Fallback: use shoulder width scaled down
        shoulder_width = abs(self.left_shoulder[0] - self.right_shoulder[0])
        return shoulder_width * 0.5


class PoseTracker:
    """Tracks body pose using MediaPipe Pose solution."""

    # MediaPipe Pose landmark indices
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    def __init__(self,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):

        self.mp_pose = solutions.pose
        self.mp_drawing = solutions.drawing_utils

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process(self, frame_rgb: np.ndarray) -> Optional[HeadRegion]:
        """Process a frame and return head region data.

        Args:
            frame_rgb: RGB image as numpy array.

        Returns:
            HeadRegion with head position data, or None if not detected.
        """
        results = self.pose.process(frame_rgb)

        if not results.pose_landmarks:
            return None

        landmarks = results.pose_landmarks.landmark

        def get_landmark(idx: int) -> Optional[Tuple[float, float, float]]:
            lm = landmarks[idx]
            if lm.visibility < 0.3:  # Low visibility threshold
                return None
            return (lm.x, lm.y, lm.z)

        nose = get_landmark(self.NOSE)
        if nose is None:
            return None

        left_shoulder = get_landmark(self.LEFT_SHOULDER)
        right_shoulder = get_landmark(self.RIGHT_SHOULDER)

        if left_shoulder is None or right_shoulder is None:
            return None

        return HeadRegion(
            nose=nose,
            left_ear=get_landmark(self.LEFT_EAR),
            right_ear=get_landmark(self.RIGHT_EAR),
            left_shoulder=left_shoulder,
            right_shoulder=right_shoulder
        )

    def draw_landmarks(self, frame_bgr: np.ndarray, head_region: Optional[HeadRegion]) -> np.ndarray:
        """Draw head region indicator on frame.

        Args:
            frame_bgr: BGR image to draw on.
            head_region: HeadRegion data to visualize.

        Returns:
            Frame with landmarks drawn.
        """
        if head_region is None:
            return frame_bgr

        frame = frame_bgr.copy()
        h, w = frame.shape[:2]

        # Draw head bounding area
        head_top = head_region.head_top
        head_center = head_region.head_center
        head_width = head_region.head_width

        # Calculate bounding box
        top_y = int(head_top[1] * h)
        center_y = int(head_center[1] * h)
        center_x = int(head_center[0] * w)
        half_width = int(head_width * w / 2)

        # Draw rectangle around head region
        cv2.rectangle(
            frame,
            (center_x - half_width, top_y),
            (center_x + half_width, center_y + int((center_y - top_y) * 0.3)),
            (0, 255, 255),  # Yellow
            2
        )

        return frame

    def close(self) -> None:
        """Release resources."""
        self.pose.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
