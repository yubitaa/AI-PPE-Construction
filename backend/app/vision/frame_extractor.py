from typing import Generator, Union
import cv2
import numpy as np


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