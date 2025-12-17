"""Camera module for webcam capture using OpenCV."""
import cv2
import numpy as np
from typing import Optional, Tuple


class Camera:
    """Handles webcam capture and frame processing."""

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        self._is_running = False

    def start(self) -> bool:
        """Start the camera capture."""
        if self._is_running:
            return True

        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)  # DirectShow for Windows

        if not self.cap.isOpened():
            # Try without DirectShow
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            return False

        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self._is_running = True
        return True

    def stop(self) -> None:
        """Stop the camera capture."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self._is_running = False

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera.

        Returns:
            Tuple of (success, frame). Frame is BGR format.
        """
        if not self._is_running or self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None

        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        return True, frame

    def get_frame_rgb(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame and convert to RGB format.

        Returns:
            Tuple of (success, frame). Frame is RGB format.
        """
        ret, frame = self.read_frame()
        if not ret or frame is None:
            return False, None

        return True, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    @property
    def is_running(self) -> bool:
        """Check if camera is running."""
        return self._is_running

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
