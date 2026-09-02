from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

import numpy as np
from sqlalchemy.orm import Session

from app.services.compliance_state import (
    ComplianceInterval,
    ComplianceStateManager,
)
from app.services.identity_cache import IdentityCache
from app.services.ppe_compliance import evaluate_compliance
from app.services.ppe_log_service import save_compliance_interval
from app.vision.frame_extractor import (
    extract_frames_with_timestamps,
)
from app.vision.ppe_association import associate_ppe
from app.vision.ppe_detector import YOLOPPEDetector
from app.vision.tracker import PersonTracker


# ---------------------------------------------------------
# Types
# ---------------------------------------------------------

IdentityResolver = Callable[
    [np.ndarray],
    Awaitable[UUID | None],
]


@dataclass(frozen=True)
class MonitorResult:
    """
    Final result returned after processing a video/source.
    """

    video_id: UUID
    processed_frames: int
    recognized_workers: int
    unknown_attempts: int
    compliance_events: int


# ---------------------------------------------------------
# Main Phase 7 Monitor
# ---------------------------------------------------------


class PPEMonitor:
    """
    Main Phase 7 orchestration service.

    Complete pipeline:

        Frame
          ↓
        YOLO
          ↓
        ByteTrack
          ↓
        Identity Cache
          ↓
        Face Recognition
          ↓
        PPE Association
          ↓
        Compliance Evaluation
          ↓
        Compliance State Manager
          ↓
        PostgreSQL
    """

    def __init__(
        self,
        db: Session,
        video_id: UUID,
        identity_resolver: IdentityResolver,
        model_path: str | None = None,
        confidence_threshold: float = 0.25,
        frame_skip: int = 5,
        max_missing_frames: int = 10,
    ) -> None:
        self.db = db
        self.video_id = video_id
        self.identity_resolver = identity_resolver

        self.detector = YOLOPPEDetector(
            model_path=model_path,
            confidence_threshold=confidence_threshold,
        )

        self.tracker = PersonTracker()

        self.identity_cache = IdentityCache()

        self.compliance_state = ComplianceStateManager()

        self.frame_skip = frame_skip
        self.max_missing_frames = max_missing_frames

        # track_id -> number of consecutive processed frames
        # where the track was not detected.
        self._missing_tracks: dict[int, int] = {}

    # =====================================================
    # PUBLIC API
    # =====================================================

    async def process_source(
        self,
        source: str | int,
    ) -> MonitorResult:
        """
        Process a complete video source.

        `source` can be:

            "videos/construction.mp4"

        or a webcam index:

            0
        """

        processed_frames = 0
        unknown_attempts = 0
        compliance_events = 0

        recognized_workers: set[UUID] = set()

        last_timestamp = 0.0

        try:
            for packet in extract_frames_with_timestamps(
                source=source,
                frame_skip=self.frame_skip,
            ):
                processed_frames += 1
                last_timestamp = packet.timestamp

                frame_result = await self.process_frame(
                    frame=packet.frame,
                    timestamp=packet.timestamp,
                    recognized_workers=recognized_workers,
                )

                unknown_attempts += (
                    frame_result["unknown_attempts"]
                )

                compliance_events += (
                    frame_result["compliance_events"]
                )

                # Commit completed intervals periodically.
                #
                # We do not need to commit every frame.
                if processed_frames % 100 == 0:
                    self.db.commit()

        finally:
            # When the source ends, every open interval must
            # be closed.
            compliance_events += self._close_all_workers(
                timestamp=last_timestamp,
            )

        self.db.commit()

        return MonitorResult(
            video_id=self.video_id,
            processed_frames=processed_frames,
            recognized_workers=len(recognized_workers),
            unknown_attempts=unknown_attempts,
            compliance_events=compliance_events,
        )

    async def process_frame(
        self,
        frame: np.ndarray,
        timestamp: float,
        recognized_workers: set[UUID] | None = None,
    ) -> dict[str, int]:
        """
        Process one frame through Phase 7.

        Timestamp is always video-relative seconds.
        """

        if recognized_workers is None:
            recognized_workers = set()

        # -------------------------------------------------
        # STEP 1
        # YOLO
        #
        # One YOLO inference gives us:
        #   Person
        #   Helmet
        #   Vest
        # -------------------------------------------------

        detections = self.detector.detect(frame)

        # -------------------------------------------------
        # STEP 2
        # ByteTrack
        #
        # Only Person detections are tracked.
        # -------------------------------------------------

        tracked_persons = self.tracker.update(
            detections
        )

        active_track_ids = {
            person.track_id
            for person in tracked_persons
        }

        # Handle tracks that temporarily disappear.
        compliance_events = self._update_missing_tracks(
            active_track_ids=active_track_ids,
            timestamp=timestamp,
        )

        unknown_attempts = 0

        # -------------------------------------------------
        # STEP 3
        # Process every tracked person
        # -------------------------------------------------

        for person in tracked_persons:

            track_id = person.track_id

            # -------------------------------------------------
            # STEP 4
            # Identity Cache
            # -------------------------------------------------

            worker_id = self.identity_cache.get(
                track_id
            )

            # -------------------------------------------------
            # STEP 5
            # Face Recognition
            #
            # Only called when track_id does not already
            # have a worker_id.
            # -------------------------------------------------

            if worker_id is None:

                person_crop = self._crop_person(
                    frame=frame,
                    bbox=person.bbox,
                )

                if person_crop is None:
                    unknown_attempts += 1
                    continue

                worker_id = await self.identity_resolver(
                    person_crop
                )

                # -------------------------------------------------
                # UNKNOWN
                #
                # Never cache UNKNOWN.
                # Never create compliance state.
                # Retry on the next frame.
                # -------------------------------------------------

                if worker_id is None:
                    unknown_attempts += 1
                    continue

                # -------------------------------------------------
                # SUCCESSFUL IDENTITY
                # -------------------------------------------------

                self.identity_cache.set(
                    track_id=track_id,
                    worker_id=worker_id,
                )

            recognized_workers.add(worker_id)

            # -------------------------------------------------
            # STEP 6
            # PPE Association
            #
            # We already ran YOLO once above.
            # Do NOT run YOLO again.
            # -------------------------------------------------

            ppe_results = associate_ppe(
                tracked_persons=[person],
                detections=detections,
            )

            if not ppe_results:
                continue

            ppe_status = ppe_results[0]

            # -------------------------------------------------
            # STEP 7
            # Compliance Evaluation
            # -------------------------------------------------

            compliance_status = evaluate_compliance(
                helmet_detected=(
                    ppe_status.helmet_detected
                ),
                vest_detected=(
                    ppe_status.vest_detected
                ),
            )

            # -------------------------------------------------
            # STEP 8
            # Compliance State Manager
            # -------------------------------------------------

            completed_interval = (
                self.compliance_state.update(
                    worker_id=worker_id,
                    status=compliance_status,
                    timestamp=timestamp,
                )
            )

            # -------------------------------------------------
            # STEP 9
            # State changed
            #
            # The previous interval is now complete.
            # Save it to PostgreSQL.
            # -------------------------------------------------

            if completed_interval is not None:

                self._save_interval(
                    completed_interval
                )

                compliance_events += 1

        return {
            "unknown_attempts": unknown_attempts,
            "compliance_events": compliance_events,
        }

    # =====================================================
    # IDENTITY / FRAME HELPERS
    # =====================================================

    @staticmethod
    def _crop_person(
        frame: np.ndarray,
        bbox: tuple[
            float,
            float,
            float,
            float,
        ],
    ) -> np.ndarray | None:
        """
        Crop a Person bounding box from the frame.

        The crop is passed to the existing Phase 3
        Face Recognition Service through identity_resolver.
        """

        height, width = frame.shape[:2]

        x1, y1, x2, y2 = bbox

        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(width, int(x2))
        y2 = min(height, int(y2))

        if x2 <= x1 or y2 <= y1:
            return None

        crop = frame[
            y1:y2,
            x1:x2,
        ]

        if crop.size == 0:
            return None

        return crop

    # =====================================================
    # TRACK LOSS HANDLING
    # =====================================================

    def _update_missing_tracks(
        self,
        active_track_ids: set[int],
        timestamp: float,
    ) -> int:
        """
        Handle ByteTrack tracks that temporarily disappear.

        A worker is NOT immediately removed when one frame is
        missed.

        If the track remains missing long enough:

            track_id
                ↓
            close worker interval
                ↓
            remove identity cache

        This prevents one bad frame from breaking a worker's
        full-day timeline.
        """

        compliance_events = 0

        cached_track_ids = set(
            self.identity_cache.active_tracks()
        )

        known_track_ids = (
            cached_track_ids
            | set(self._missing_tracks.keys())
        )

        for track_id in known_track_ids:

            if track_id in active_track_ids:

                self._missing_tracks.pop(
                    track_id,
                    None,
                )

                continue

            missed = (
                self._missing_tracks.get(
                    track_id,
                    0,
                )
                + 1
            )

            self._missing_tracks[track_id] = missed

            if missed < self.max_missing_frames:
                continue

            # ---------------------------------------------
            # Track has disappeared permanently.
            # ---------------------------------------------

            worker_id = self.identity_cache.get(
                track_id
            )

            if worker_id is not None:

                completed_interval = (
                    self.compliance_state.close_worker(
                        worker_id=worker_id,
                        timestamp=timestamp,
                    )
                )

                if completed_interval is not None:

                    self._save_interval(
                        completed_interval
                    )

                    compliance_events += 1

            self.identity_cache.remove(
                track_id
            )

            self._missing_tracks.pop(
                track_id,
                None,
            )

        return compliance_events

    # =====================================================
    # DATABASE
    # =====================================================

    def _save_interval(
        self,
        interval: ComplianceInterval,
    ) -> None:
        """
        Save one completed compliance interval.
        """

        save_compliance_interval(
            db=self.db,
            interval=interval,
            video_id=self.video_id,
        )

    def _close_all_workers(
        self,
        timestamp: float,
    ) -> int:
        """
        Close all open worker intervals when the source ends.
        """

        events = 0

        for worker_id in list(
            self.compliance_state.active_workers()
        ):

            interval = (
                self.compliance_state.close_worker(
                    worker_id=worker_id,
                    timestamp=timestamp,
                )
            )

            if interval is None:
                continue

            self._save_interval(interval)

            events += 1

        return events