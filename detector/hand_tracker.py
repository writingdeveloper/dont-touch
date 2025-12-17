"""Hand tracking module using MediaPipe."""
import cv2
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass

import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2


@dataclass
class HandLandmarks:
    """Container for hand landmark data."""
    landmarks: List[Tuple[float, float, float]]  # (x, y, z) normalized coordinates
    handedness: str  # "Left" or "Right"

    @property
    def wrist(self) -> Tuple[float, float, float]:
        """Get wrist position (landmark 0)."""
        return self.landmarks[0]

    @property
    def index_finger_tip(self) -> Tuple[float, float, float]:
        """Get index finger tip position (landmark 8)."""
        return self.landmarks[8]

    @property
    def middle_finger_tip(self) -> Tuple[float, float, float]:
        """Get middle finger tip position (landmark 12)."""
        return self.landmarks[12]

    @property
    def center(self) -> Tuple[float, float, float]:
        """Get approximate center of hand (average of key landmarks)."""
        key_landmarks = [0, 5, 9, 13, 17]  # Wrist and finger bases
        x = sum(self.landmarks[i][0] for i in key_landmarks) / len(key_landmarks)
        y = sum(self.landmarks[i][1] for i in key_landmarks) / len(key_landmarks)
        z = sum(self.landmarks[i][2] for i in key_landmarks) / len(key_landmarks)
        return (x, y, z)


class HandTracker:
    """Tracks hands using MediaPipe Hands solution."""

    def __init__(self,
                 max_num_hands: int = 2,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):

        self.mp_hands = solutions.hands
        self.mp_drawing = solutions.drawing_utils
        self.mp_drawing_styles = solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def process(self, frame_rgb: np.ndarray) -> List[HandLandmarks]:
        """Process a frame and return detected hands.

        Args:
            frame_rgb: RGB image as numpy array.

        Returns:
            List of HandLandmarks for each detected hand.
        """
        results = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return []

        hands_data = []
        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            landmarks = [
                (lm.x, lm.y, lm.z)
                for lm in hand_landmarks.landmark
            ]
            hand_data = HandLandmarks(
                landmarks=landmarks,
                handedness=handedness.classification[0].label
            )
            hands_data.append(hand_data)

        return hands_data

    def draw_landmarks(self, frame_bgr: np.ndarray, hands: List[HandLandmarks]) -> np.ndarray:
        """Draw hand landmarks on frame.

        Args:
            frame_bgr: BGR image to draw on.
            hands: List of HandLandmarks to draw.

        Returns:
            Frame with landmarks drawn.
        """
        frame = frame_bgr.copy()

        for hand in hands:
            # Create a landmark list for drawing
            landmark_list = landmark_pb2.NormalizedLandmarkList()
            for x, y, z in hand.landmarks:
                landmark = landmark_list.landmark.add()
                landmark.x = x
                landmark.y = y
                landmark.z = z

            self.mp_drawing.draw_landmarks(
                frame,
                landmark_list,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )

        return frame

    def close(self) -> None:
        """Release resources."""
        self.hands.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
