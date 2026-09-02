from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
from ultralytics import YOLO


@dataclass(frozen=True)
class Detection:
    """
    Represents one object detected in a video frame.

    bbox format:
        (x1, y1, x2, y2)
    """

    class_name: str
    bbox: tuple[float, float, float, float]
    confidence: float


class PPEDetector(Protocol):
    """
    Common interface for all Phase 7 detectors.
    """

    def detect(self, frame: np.ndarray) -> list[Detection]:
        ...


class MockPPEDetector:
    """
    Temporary detector used for testing.
    """

    def detect(self, frame: np.ndarray) -> list[Detection]:
        return []


class YOLOPPEDetector:
    """
    Real Phase 6 YOLO PPE detector.

    The trained model detects:
        0 -> Person
        1 -> Helmet
        2 -> Vest
    """

    def __init__(
        self,
        model_path: str | None = None,
        confidence_threshold: float = 0.25,
    ):
        if model_path is None:
            project_root = Path(__file__).resolve().parents[3]
            model_path = project_root / "models" / "ppe" / "best.pt"

        self.model_path = Path(model_path)
        self.confidence_threshold = confidence_threshold

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {self.model_path}"
            )

        self.model = YOLO(str(self.model_path))

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Run YOLO inference on one OpenCV BGR frame bypassing the automatic warmup.
        """

        # Bypass automatic warmup / torchvision check using model.predict directly
        results = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            verbose=False,
            stream=False,
        )

        detections: list[Detection] = []

        for result in results:
            if result.boxes is None:
                continue

            boxes = result.boxes

            for box in boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                class_name = self.model.names[class_id]

                detections.append(
                    Detection(
                        class_name=class_name,
                        bbox=(
                            float(x1),
                            float(y1),
                            float(x2),
                            float(y2),
                        ),
                        confidence=confidence,
                    )
                )

        return detections