from typing import Generator, Union
import cv2
import numpy as np
from dataclasses import dataclass

def extract_frames(
    source: Union[str, int], 
    frame_skip: int = 5
) -> Generator[np.ndarray, None, None]:
    """
    Ingests frames from a video file path or live webcam index using OpenCV.
    
    :param source: Path to a video file (str, e.g., 'uploads/video.mp4') 
                   or webcam index (int, e.g., 0 for default webcam).
    :param frame_skip: Process 1 frame every N frames to save CPU/GPU computation.
    """
    # Open the video stream or camera device
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise ValueError(f"Unable to open video source: {source}")

    frame_count = 0
    try:
        while cap.isOpened():
            # Read single frame from source
            ret, frame = cap.read()
            
            # End of file or camera stream disconnected
            if not ret:
                break

            # Frame injection point: yield frame if matching skip interval
            if frame_count % frame_skip == 0:
                #A standard function uses return to return everything at once. A generator uses yield to give you items one by one on demand.  
                yield frame # its like return but it returns one frame at a time instead of all frames at once. for saving memory and processing time.

            frame_count += 1
    finally:
        # Guarantee hardware camera lock or video file handle is released
        cap.release()



@dataclass(frozen=True)
class FramePacket:
    """
    One processed frame with its position in the source.
    """

    frame: np.ndarray
    frame_number: int
    timestamp: float


def extract_frames_with_timestamps(
    source: Union[str, int],
    frame_skip: int = 30,
) -> Generator[FramePacket, None, None]:
    """
    Extract frames while preserving the source frame number
    and video-relative timestamp.

    Works with:
        - pre-recorded video path
        - webcam index
    """

    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise ValueError(
            f"Unable to open video source: {source}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)

    # Webcam/video sources may not report a useful FPS.
    if fps <= 0:
        fps = 30.0

    frame_number = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            if frame_number % frame_skip == 0:
                timestamp = frame_number / fps

                yield FramePacket(
                    frame=frame,
                    frame_number=frame_number,
                    timestamp=timestamp,
                )

            frame_number += 1

    finally:
        cap.release()