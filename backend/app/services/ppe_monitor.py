# from __future__ import annotations

# from collections.abc import Awaitable, Callable
# from dataclasses import dataclass
# from uuid import UUID

# import numpy as np
# from sqlalchemy.orm import Session

# from app.services.compliance_state import ComplianceStateManager
# from app.services.identity_cache import IdentityCache
# from app.services.ppe_compliance import evaluate_compliance
# from app.services.ppe_log_service import save_compliance_interval
# from app.services.ppe_temporal_filter import PPETemporalFilter
# from app.vision.frame_extractor import extract_frames_with_timestamps
# from app.vision.ppe_association import associate_ppe
# from app.vision.ppe_detector import YOLOPPEDetector
# from app.vision.tracker import PersonTracker


# IdentityResolver = Callable[
#     [np.ndarray],
#     Awaitable[UUID | None],
# ]


# @dataclass(frozen=True)
# class MonitorResult:
#     """
#     Final result returned after processing a complete source.
#     """

#     video_id: UUID
#     processed_frames: int
#     recognized_workers: int
#     unknown_attempts: int
#     compliance_events: int


# @dataclass(frozen=True)
# class MonitorConfig:
#     """
#     Phase 7 runtime configuration.

#     frame_skip:
#         Process one frame every N source frames.

#     confidence_threshold:
#         Minimum confidence used by the YOLO detector.

#     helmet_confidence / vest_confidence:
#         Minimum confidence used by PPE association.

#     temporal_confirmations:
#         Number of consecutive observations required to confirm
#         a new PPE state after the worker already has a stable state.

#     max_missing_frames:
#         Number of processed frames a cached track may disappear
#         before it is closed.
#     """

#     frame_skip: int = 5
#     confidence_threshold: float = 0.25
#     helmet_confidence: float = 0.40
#     vest_confidence: float = 0.40
#     temporal_confirmations: int = 2
#     max_missing_frames: int = 10


# class PPEMonitor:
#     """
#     Main Phase 7 orchestration service.
#     """

#     def __init__(
#         self,
#         db: Session,
#         video_id: UUID,
#         identity_resolver: IdentityResolver,
#         model_path: str | None = None,
#         config: MonitorConfig | None = None,
#     ) -> None:
#         self.db = db
#         self.video_id = video_id
#         self.identity_resolver = identity_resolver

#         self.config = config or MonitorConfig()

#         if self.config.frame_skip < 1:
#             raise ValueError(
#                 "frame_skip must be >= 1"
#             )

#         if self.config.max_missing_frames < 1:
#             raise ValueError(
#                 "max_missing_frames must be >= 1"
#             )

#         self.detector = YOLOPPEDetector(
#             model_path=model_path,
#             confidence_threshold=self.config.confidence_threshold,
#         )

#         self.tracker = PersonTracker()

#         self.identity_cache = IdentityCache()

#         self.compliance_state = ComplianceStateManager()

#         self.temporal_filter = PPETemporalFilter(
#             required_confirmations=(
#                 self.config.temporal_confirmations
#             ),
#         )

#         # track_id -> number of consecutive processed frames
#         # in which this track was absent.
#         self._missing_tracks: dict[int, int] = {}

#     # =========================================================
#     # PUBLIC API
#     # =========================================================

#     async def process_source(
#         self,
#         source: str | int,
#     ) -> MonitorResult:
#         """
#         Process a complete video/source.

#         All timestamps are video-relative seconds.
#         """

#         processed_frames = 0
#         unknown_attempts = 0
#         compliance_events = 0

#         recognized_workers: set[UUID] = set()

#         last_timestamp: float | None = None

#         try:
#             for packet in extract_frames_with_timestamps(
#                 source=source,
#                 frame_skip=self.config.frame_skip,
#             ):
#                 processed_frames += 1
#                 last_timestamp = float(packet.timestamp)

#                 frame_result = await self.process_frame(
#                     frame=packet.frame,
#                     timestamp=float(packet.timestamp),
#                     recognized_workers=recognized_workers,
#                 )

#                 unknown_attempts += (
#                     frame_result["unknown_attempts"]
#                 )

#                 compliance_events += (
#                     frame_result["compliance_events"]
#                 )

#                 if processed_frames % 100 == 0:
#                     self.db.commit()

#         finally:
#             # Close all active workers at the final processed
#             # video timestamp.
#             if last_timestamp is not None:
#                 compliance_events += self._close_all_workers(
#                     timestamp=last_timestamp,
#                 )

#         self.db.commit()

#         return MonitorResult(
#             video_id=self.video_id,
#             processed_frames=processed_frames,
#             recognized_workers=len(recognized_workers),
#             unknown_attempts=unknown_attempts,
#             compliance_events=compliance_events,
#         )

#     async def process_frame(
#         self,
#         frame: np.ndarray,
#         timestamp: float,
#         recognized_workers: set[UUID] | None = None,
#     ) -> dict[str, int]:
#         """
#         Process one sampled frame.

#         Pipeline:

#             YOLO
#               ↓
#             ByteTrack
#               ↓
#             global PPE association
#               ↓
#             identity cache / face recognition
#               ↓
#             raw compliance state
#               ↓
#             temporal stability
#               ↓
#             ComplianceStateManager
#               ↓
#             PostgreSQL
#         """

#         if recognized_workers is None:
#             recognized_workers = set()

#         # -----------------------------------------------------
#         # STEP 1 — YOLO
#         # -----------------------------------------------------

#         detections = self.detector.detect(frame)

#         # -----------------------------------------------------
#         # STEP 2 — ByteTrack
#         # -----------------------------------------------------

#         tracked_persons = self.tracker.update(
#             detections
#         )

#         active_track_ids = {
#             person.track_id
#             for person in tracked_persons
#         }

#         compliance_events = self._update_missing_tracks(
#             active_track_ids=active_track_ids,
#             timestamp=timestamp,
#         )

#         unknown_attempts = 0

#         if not tracked_persons:
#             return {
#                 "unknown_attempts": unknown_attempts,
#                 "compliance_events": compliance_events,
#             }

#         # -----------------------------------------------------
#         # STEP 3 — GLOBAL PPE ASSOCIATION
#         #
#         # Run ONCE for the entire frame.
#         #
#         # This is essential for deterministic one-to-one
#         # helmet/vest assignment.
#         # -----------------------------------------------------

#         ppe_results = associate_ppe(
#             tracked_persons=tracked_persons,
#             detections=detections,
#             min_helmet_conf=(
#                 self.config.helmet_confidence
#             ),
#             min_vest_conf=(
#                 self.config.vest_confidence
#             ),
#         )

#         ppe_by_track_id = {
#             result.track_id: result
#             for result in ppe_results
#         }

#         # -----------------------------------------------------
#         # STEP 4 — IDENTITY + COMPLIANCE
#         # -----------------------------------------------------

#         for person in tracked_persons:
#             track_id = person.track_id

#             worker_id = self.identity_cache.get(
#                 track_id
#             )

#             # -------------------------------------------------
#             # STEP 5 — FACE RECOGNITION WHEN NOT CACHED
#             # -------------------------------------------------

#             if worker_id is None:
#                 person_crop = self._crop_person(
#                     frame=frame,
#                     bbox=person.bbox,
#                 )

#                 if person_crop is None:
#                     unknown_attempts += 1
#                     continue

#                 worker_id = await self.identity_resolver(
#                     person_crop
#                 )

#                 # UNKNOWN is never cached and never logged.
#                 if worker_id is None:
#                     unknown_attempts += 1
#                     continue

#                 self.identity_cache.set(
#                     track_id=track_id,
#                     worker_id=worker_id,
#                 )

#             recognized_workers.add(worker_id)

#             # -------------------------------------------------
#             # STEP 6 — GET PPE ASSOCIATION RESULT
#             # -------------------------------------------------

#             ppe_status = ppe_by_track_id.get(
#                 track_id
#             )

#             if ppe_status is None:
#                 continue

#             # -------------------------------------------------
#             # STEP 7 — RAW COMPLIANCE
#             # -------------------------------------------------

#             compliance_status = evaluate_compliance(
#                 helmet_detected=(
#                     ppe_status.helmet_detected
#                 ),
#                 vest_detected=(
#                     ppe_status.vest_detected
#                 ),
#             )

#             # -------------------------------------------------
#             # STEP 8 — TEMPORAL STABILITY
#             # -------------------------------------------------

#             stable_status = self.temporal_filter.update(
#                 worker_id=worker_id,
#                 observed_status=compliance_status,
#             )

#             # None means the new status has not yet been
#             # confirmed by enough consecutive observations.
#             if stable_status is None:
#                 continue

#             # -------------------------------------------------
#             # STEP 9 — COMPLIANCE INTERVAL STATE
#             # -------------------------------------------------

#             completed_interval = (
#                 self.compliance_state.update(
#                     worker_id=worker_id,
#                     status=stable_status,
#                     timestamp=timestamp,
#                 )
#             )

#             # -------------------------------------------------
#             # STEP 10 — SAVE COMPLETED INTERVAL
#             # -------------------------------------------------

#             if completed_interval is not None:
#                 self._save_interval(
#                     completed_interval
#                 )
#                 compliance_events += 1

#         return {
#             "unknown_attempts": unknown_attempts,
#             "compliance_events": compliance_events,
#         }

#     # =========================================================
#     # IDENTITY / FRAME HELPERS
#     # =========================================================

#     @staticmethod
#     def _crop_person(
#         frame: np.ndarray,
#         bbox: tuple[
#             float,
#             float,
#             float,
#             float,
#         ],
#     ) -> np.ndarray | None:
#         """
#         Crop a tracked person for the existing Phase 3
#         face-recognition resolver.
#         """

#         height, width = frame.shape[:2]

#         x1, y1, x2, y2 = bbox

#         x1 = max(0, min(width, int(x1)))
#         y1 = max(0, min(height, int(y1)))
#         x2 = max(0, min(width, int(x2)))
#         y2 = max(0, min(height, int(y2)))

#         if x2 <= x1 or y2 <= y1:
#             return None

#         crop = frame[
#             y1:y2,
#             x1:x2,
#         ]

#         if crop.size == 0:
#             return None

#         return crop

#     # =========================================================
#     # DATABASE
#     # =========================================================

#     def _save_interval(
#         self,
#         interval,
#     ) -> None:
#         """
#         Save one completed interval using the current video's ID.

#         Timestamps remain video-relative seconds.
#         """

#         save_compliance_interval(
#             db=self.db,
#             interval=interval,
#             video_id=self.video_id,
#         )

#     # =========================================================
#     # TRACK LOSS
#     # =========================================================

#     def _update_missing_tracks(
#         self,
#         active_track_ids: set[int],
#         timestamp: float,
#     ) -> int:
#         """
#         Handle tracks that temporarily disappear.

#         A missing track is kept alive for max_missing_frames
#         processed frames.

#         Once that threshold is reached:

#             track
#               ↓
#             close active compliance interval
#               ↓
#             reset temporal PPE state
#               ↓
#             remove cached identity
#         """

#         compliance_events = 0

#         cached_track_ids = set(
#             self.identity_cache.active_tracks()
#         )

#         known_track_ids = (
#             cached_track_ids
#             | set(self._missing_tracks.keys())
#         )

#         for track_id in known_track_ids:
#             if track_id in active_track_ids:
#                 self._missing_tracks.pop(
#                     track_id,
#                     None,
#                 )
#                 continue

#             missed = (
#                 self._missing_tracks.get(
#                     track_id,
#                     0,
#                 )
#                 + 1
#             )

#             self._missing_tracks[track_id] = missed

#             if missed >= self.config.max_missing_frames:
#                 compliance_events += self._close_track(
#                     track_id=track_id,
#                     timestamp=timestamp,
#                 )

#         return compliance_events

#     def _close_track(
#         self,
#         track_id: int,
#         timestamp: float,
#     ) -> int:
#         """
#         Fully close one lost tracking identity.
#         """

#         compliance_events = 0

#         worker_id = self.identity_cache.get(
#             track_id
#         )

#         if worker_id is not None:
#             interval = (
#                 self.compliance_state.close_worker(
#                     worker_id=worker_id,
#                     timestamp=timestamp,
#                 )
#             )

#             if interval is not None:
#                 self._save_interval(interval)
#                 compliance_events += 1

#             self.temporal_filter.reset_worker(
#                 worker_id
#             )

#         self.identity_cache.remove(
#             track_id
#         )

#         self._missing_tracks.pop(
#             track_id,
#             None,
#         )

#         return compliance_events

#     # =========================================================
#     # VIDEO END
#     # =========================================================

#     def _close_all_workers(
#         self,
#         timestamp: float,
#     ) -> int:
#         """
#         Close all active compliance intervals at the last
#         processed video timestamp.
#         """

#         compliance_events = 0

#         for worker_id in list(
#             self.compliance_state.active_workers()
#         ):
#             interval = (
#                 self.compliance_state.close_worker(
#                     worker_id=worker_id,
#                     timestamp=timestamp,
#                 )
#             )

#             if interval is not None:
#                 self._save_interval(interval)
#                 compliance_events += 1

#             self.temporal_filter.reset_worker(
#                 worker_id
#             )

#         self.identity_cache.clear()
#         self._missing_tracks.clear()

#         return compliance_events
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

import numpy as np
from sqlalchemy.orm import Session

from app.services.compliance_state import ComplianceStateManager
from app.services.identity_cache import IdentityCache
from app.services.ppe_compliance import evaluate_compliance
from app.services.ppe_log_service import save_compliance_interval
from app.services.ppe_temporal_filter import PPETemporalFilter
from app.vision.frame_extractor import extract_frames_with_timestamps
from app.vision.ppe_association import associate_ppe
from app.vision.ppe_detector import YOLOPPEDetector
from app.vision.tracker import PersonTracker


IdentityResolver = Callable[
    [np.ndarray],
    Awaitable[UUID | None],
]


@dataclass(frozen=True)
class MonitorResult:
    """
    Final result returned after processing a complete source.
    """

    video_id: UUID
    processed_frames: int
    recognized_workers: int
    unknown_attempts: int
    compliance_events: int


@dataclass(frozen=True)
class MonitorConfig:
    """
    Phase 7 runtime configuration.

    frame_skip:
        Process one frame every N source frames.

    confidence_threshold:
        Minimum confidence used by the YOLO detector.

    helmet_confidence / vest_confidence:
        Minimum confidence used by PPE association.

    temporal_confirmations:
        Number of consecutive observations required to confirm
        a new PPE state after the worker already has a stable state.

    max_missing_frames:
        Number of processed frames a cached track may disappear
        before it is closed.
    """

    frame_skip: int = 5
    confidence_threshold: float = 0.25
    helmet_confidence: float = 0.40
    vest_confidence: float = 0.40
    temporal_confirmations: int = 5
    max_missing_frames: int = 10


class PPEMonitor:
    """
    Main Phase 7 orchestration service.
    """

    def __init__(
        self,
        db: Session,
        video_id: UUID,
        identity_resolver: IdentityResolver,
        model_path: str | None = None,
        config: MonitorConfig | None = None,
    ) -> None:
        self.db = db
        self.video_id = video_id
        self.identity_resolver = identity_resolver

        self.config = config or MonitorConfig()

        if self.config.frame_skip < 1:
            raise ValueError(
                "frame_skip must be >= 1"
            )

        if self.config.max_missing_frames < 1:
            raise ValueError(
                "max_missing_frames must be >= 1"
            )

        self.detector = YOLOPPEDetector(
            model_path=model_path,
            confidence_threshold=self.config.confidence_threshold,
        )

        self.tracker = PersonTracker()

        self.identity_cache = IdentityCache()

        self.compliance_state = ComplianceStateManager()

        self.temporal_filter = PPETemporalFilter(
            required_confirmations=(
                self.config.temporal_confirmations
            ),
        )

        # track_id -> number of consecutive processed frames
        # in which this track was absent.
        self._missing_tracks: dict[int, int] = {}

    # =========================================================
    # PUBLIC API
    # =========================================================

    async def process_source(
        self,
        source: str | int,
    ) -> MonitorResult:
        """
        Process a complete video/source.

        All timestamps are video-relative seconds.
        """

        processed_frames = 0
        unknown_attempts = 0
        compliance_events = 0

        recognized_workers: set[UUID] = set()

        last_timestamp: float | None = None

        try:
            for packet in extract_frames_with_timestamps(
                source=source,
                frame_skip=self.config.frame_skip,
            ):
                processed_frames += 1
                last_timestamp = float(packet.timestamp)

                frame_result = await self.process_frame(
                    frame=packet.frame,
                    timestamp=float(packet.timestamp),
                    recognized_workers=recognized_workers,
                )

                unknown_attempts += (
                    frame_result["unknown_attempts"]
                )

                compliance_events += (
                    frame_result["compliance_events"]
                )

                if processed_frames % 100 == 0:
                    self.db.commit()

        finally:
            # Close all active workers at the final processed
            # video timestamp.
            if last_timestamp is not None:
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
        Process one sampled frame.

        Pipeline:

            YOLO
              ↓
            ByteTrack
              ↓
            overlap check (freeze overlap tracks)
              ↓
            global PPE association
              ↓
            identity cache / face recognition
              ↓
            raw compliance state
              ↓
            temporal stability
              ↓
            ComplianceStateManager
              ↓
            PostgreSQL
        """

        if recognized_workers is None:
            recognized_workers = set()

        # -----------------------------------------------------
        # STEP 1 — YOLO
        # -----------------------------------------------------

        detections = self.detector.detect(frame)

        # -----------------------------------------------------
        # STEP 2 — ByteTrack
        # -----------------------------------------------------

        tracked_persons = self.tracker.update(
            detections
        )

        active_track_ids = {
            person.track_id
            for person in tracked_persons
        }

        compliance_events = self._update_missing_tracks(
            active_track_ids=active_track_ids,
            timestamp=timestamp,
        )

        unknown_attempts = 0

        if not tracked_persons:
            return {
                "unknown_attempts": unknown_attempts,
                "compliance_events": compliance_events,
            }

        # -----------------------------------------------------
        # STEP 2.5 — OVERLAP DETECTION
        # Find workers overlapping in the frame.
        # -----------------------------------------------------
        overlapping_track_ids: set[int] = set()
        for i, p1 in enumerate(tracked_persons):
            for p2 in tracked_persons[i + 1:]:
                if self._compute_bbox_overlap(p1.bbox, p2.bbox) > 0.25:
                    overlapping_track_ids.add(p1.track_id)
                    overlapping_track_ids.add(p2.track_id)

        # -----------------------------------------------------
        # STEP 3 — GLOBAL PPE ASSOCIATION
        # -----------------------------------------------------

        ppe_results = associate_ppe(
            tracked_persons=tracked_persons,
            detections=detections,
            min_helmet_conf=(
                self.config.helmet_confidence
            ),
            min_vest_conf=(
                self.config.vest_confidence
            ),
        )

        ppe_by_track_id = {
            result.track_id: result
            for result in ppe_results
        }

        # -----------------------------------------------------
        # STEP 4 — IDENTITY + COMPLIANCE
        # -----------------------------------------------------

        for person in tracked_persons:
            track_id = person.track_id

            worker_id = self.identity_cache.get(
                track_id
            )

            # -------------------------------------------------
            # STEP 5 — FACE RECOGNITION WHEN NOT CACHED
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

                # UNKNOWN is never cached and never logged.
                if worker_id is None:
                    unknown_attempts += 1
                    continue

                self.identity_cache.set(
                    track_id=track_id,
                    worker_id=worker_id,
                )

            recognized_workers.add(worker_id)

            # -------------------------------------------------
            # STEP 6 — GET PPE ASSOCIATION RESULT
            # -------------------------------------------------

            ppe_status = ppe_by_track_id.get(
                track_id
            )

            if ppe_status is None:
                continue

            # -------------------------------------------------
            # STEP 7 — RAW COMPLIANCE
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
            # STEP 7.5 — FREEZE STATE DURING OVERLAP
            # Skip updating temporal state during physical overlap
            # to prevent occlusion/state leakage.
            # -------------------------------------------------

            if track_id in overlapping_track_ids:
                continue

            # -------------------------------------------------
            # STEP 8 — TEMPORAL STABILITY
            # -------------------------------------------------

            stable_status = self.temporal_filter.update(
                worker_id=worker_id,
                observed_status=compliance_status,
            )

            # None means the new status has not yet been
            # confirmed by enough consecutive observations.
            if stable_status is None:
                continue

            # -------------------------------------------------
            # STEP 9 — COMPLIANCE INTERVAL STATE
            # -------------------------------------------------

            completed_interval = (
                self.compliance_state.update(
                    worker_id=worker_id,
                    status=stable_status,
                    timestamp=timestamp,
                )
            )

            # -------------------------------------------------
            # STEP 10 — SAVE COMPLETED INTERVAL
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

    # =========================================================
    # IDENTITY / FRAME HELPERS
    # =========================================================

    @staticmethod
    def _compute_bbox_overlap(
        boxA: tuple[float, float, float, float],
        boxB: tuple[float, float, float, float],
    ) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes."""
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0.0, xB - xA) * max(0.0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        unionArea = float(boxAArea + boxBArea - interArea)
        if unionArea <= 0:
            return 0.0

        return interArea / unionArea

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
        Crop a tracked person for the existing Phase 3
        face-recognition resolver.
        """

        height, width = frame.shape[:2]

        x1, y1, x2, y2 = bbox

        x1 = max(0, min(width, int(x1)))
        y1 = max(0, min(height, int(y1)))
        x2 = max(0, min(width, int(x2)))
        y2 = max(0, min(height, int(y2)))

        if x2 <= x1 or y2 <= y1:
            return None

        crop = frame[
            y1:y2,
            x1:x2,
        ]

        if crop.size == 0:
            return None

        return crop

    # =========================================================
    # DATABASE
    # =========================================================

    def _save_interval(
        self,
        interval,
    ) -> None:
        """
        Save one completed interval using the current video's ID.

        Timestamps remain video-relative seconds.
        """

        save_compliance_interval(
            db=self.db,
            interval=interval,
            video_id=self.video_id,
        )

    # =========================================================
    # TRACK LOSS
    # =========================================================

    def _update_missing_tracks(
        self,
        active_track_ids: set[int],
        timestamp: float,
    ) -> int:
        """
        Handle tracks that temporarily disappear.

        A missing track is kept alive for max_missing_frames
        processed frames.

        Once that threshold is reached:

            track
              ↓
            close active compliance interval
              ↓
            reset temporal PPE state
              ↓
            remove cached identity
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

            if missed >= self.config.max_missing_frames:
                compliance_events += self._close_track(
                    track_id=track_id,
                    timestamp=timestamp,
                )

        return compliance_events

    def _close_track(
        self,
        track_id: int,
        timestamp: float,
    ) -> int:
        """
        Fully close one lost tracking identity.
        """

        compliance_events = 0

        worker_id = self.identity_cache.get(
            track_id
        )

        if worker_id is not None:
            interval = (
                self.compliance_state.close_worker(
                    worker_id=worker_id,
                    timestamp=timestamp,
                )
            )

            if interval is not None:
                self._save_interval(interval)
                compliance_events += 1

            self.temporal_filter.reset_worker(
                worker_id
            )

        self.identity_cache.remove(
            track_id
        )

        self._missing_tracks.pop(
            track_id,
            None,
        )

        return compliance_events

    # =========================================================
    # VIDEO END
    # =========================================================

    def _close_all_workers(
        self,
        timestamp: float,
    ) -> int:
        """
        Close all active compliance intervals at the last
        processed video timestamp.
        """

        compliance_events = 0

        for worker_id in list(
            self.compliance_state.active_workers()
        ):
            interval = (
                self.compliance_state.close_worker(
                    worker_id=worker_id,
                    timestamp=timestamp,
                )
            )

            if interval is not None:
                self._save_interval(interval)
                compliance_events += 1

            self.temporal_filter.reset_worker(
                worker_id
            )

        self.identity_cache.clear()
        self._missing_tracks.clear()

        return compliance_events