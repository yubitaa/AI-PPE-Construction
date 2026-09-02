from dataclasses import dataclass

import numpy as np
import supervision as sv

from app.vision.ppe_detector import Detection


@dataclass(frozen=True)
class TrackedPerson:
    """
    A person detection associated with a persistent track ID.
    """

    track_id: int
    bbox: tuple[float, float, float, float]
    confidence: float


class PersonTracker:
    """
    ByteTrack wrapper used by Phase 7.

    Only Person detections are passed to ByteTrack.
    """

    def __init__(self) -> None:
        self.tracker = sv.ByteTrack()

    def update(
        self,
        detections: list[Detection],
    ) -> list[TrackedPerson]:
        """
        Update ByteTrack with Person detections.

        Returns:
            A list of tracked persons with persistent track IDs.
        """

        person_detections = [
            detection
            for detection in detections
            if detection.class_name.lower() == "person"
        ]

        if not person_detections:
            return []

        xyxy = np.array(
            [d.bbox for d in person_detections],
            dtype=np.float32,
        )

        confidence = np.array(
            [d.confidence for d in person_detections],
            dtype=np.float32,
        )

        class_id = np.zeros(
            len(person_detections),
            dtype=np.int32,
        )

        sv_detections = sv.Detections(
            xyxy=xyxy,
            confidence=confidence,
            class_id=class_id,
        )

        tracked = self.tracker.update_with_detections(
            sv_detections
        )

        results: list[TrackedPerson] = []

        for i in range(len(tracked)):
            tracker_id = tracked.tracker_id[i]

            if tracker_id is None:
                continue

            results.append(
                TrackedPerson(
                    track_id=int(tracker_id),
                    bbox=tuple(
                        float(value)
                        for value in tracked.xyxy[i]
                    ),
                    confidence=float(
                        tracked.confidence[i]
                    ),
                )
            )

        return results
