# from __future__ import annotations

# from dataclasses import dataclass

# from app.vision.ppe_detector import Detection
# from app.vision.tracker import TrackedPerson


# @dataclass(frozen=True)
# class PPEStatus:
#     track_id: int
#     helmet_detected: bool
#     vest_detected: bool


# def _area(
#     box: tuple[float, float, float, float],
# ) -> float:
#     x1, y1, x2, y2 = box

#     width = max(0.0, x2 - x1)
#     height = max(0.0, y2 - y1)

#     return width * height


# def _intersection_area(
#     box_a: tuple[float, float, float, float],
#     box_b: tuple[float, float, float, float],
# ) -> float:
#     ax1, ay1, ax2, ay2 = box_a
#     bx1, by1, bx2, by2 = box_b

#     ix1 = max(ax1, bx1)
#     iy1 = max(ay1, by1)
#     ix2 = min(ax2, bx2)
#     iy2 = min(ay2, by2)

#     width = max(0.0, ix2 - ix1)
#     height = max(0.0, iy2 - iy1)

#     return width * height


# def calculate_overlap_ratio(
#     person_box: tuple[float, float, float, float],
#     ppe_box: tuple[float, float, float, float],
# ) -> float:
#     """
#     Return the fraction of the PPE bounding box that overlaps
#     the person's bounding box.

#     A value of 1.0 means the entire PPE box is inside the
#     person's box.
#     """

#     ppe_area = _area(ppe_box)

#     if ppe_area <= 0.0:
#         return 0.0

#     return _intersection_area(
#         person_box,
#         ppe_box,
#     ) / ppe_area


# def _center(
#     box: tuple[float, float, float, float],
# ) -> tuple[float, float]:
#     x1, y1, x2, y2 = box

#     return (
#         (x1 + x2) / 2.0,
#         (y1 + y2) / 2.0,
#     )


# def _normalized_center_distance(
#     person_box: tuple[float, float, float, float],
#     ppe_box: tuple[float, float, float, float],
# ) -> float:
#     """
#     Return a normalized distance between the person and PPE centers.

#     0.0 = same center.
#     Larger values indicate greater separation.
#     """

#     px, py = _center(person_box)
#     qx, qy = _center(ppe_box)

#     person_width = max(
#         1.0,
#         person_box[2] - person_box[0],
#     )

#     person_height = max(
#         1.0,
#         person_box[3] - person_box[1],
#     )

#     dx = abs(px - qx) / person_width
#     dy = abs(py - qy) / person_height

#     return (dx * dx + dy * dy) ** 0.5


# def _horizontal_position_score(
#     person_box: tuple[float, float, float, float],
#     ppe_box: tuple[float, float, float, float],
# ) -> float:
#     """
#     Score how horizontally centered the PPE is relative
#     to the person.

#     1.0 = perfectly centered.
#     0.0 = far outside the expected horizontal region.
#     """

#     px, _ = _center(person_box)
#     qx, _ = _center(ppe_box)

#     person_width = max(
#         1.0,
#         person_box[2] - person_box[0],
#     )

#     normalized_offset = abs(qx - px) / person_width

#     return max(
#         0.0,
#         1.0 - normalized_offset,
#     )


# def _vertical_position_score(
#     person_box: tuple[float, float, float, float],
#     ppe_box: tuple[float, float, float, float],
#     top_ratio: float,
#     bottom_ratio: float,
# ) -> float:
#     """
#     Score whether PPE is located in an expected vertical
#     region of the person.
#     """

#     _, py = _center(ppe_box)

#     person_y1 = person_box[1]
#     person_height = max(
#         1.0,
#         person_box[3] - person_box[1],
#     )

#     relative_y = (
#         py - person_y1
#     ) / person_height

#     if relative_y < top_ratio:
#         return max(
#             0.0,
#             1.0 - (
#                 top_ratio - relative_y
#             ) / max(top_ratio, 0.01),
#         )

#     if relative_y > bottom_ratio:
#         return max(
#             0.0,
#             1.0 - (
#                 relative_y - bottom_ratio
#             ) / max(
#                 1.0 - bottom_ratio,
#                 0.01,
#             ),
#         )

#     # Inside the expected region.
#     region_center = (
#         top_ratio + bottom_ratio
#     ) / 2.0

#     region_half_width = max(
#         (bottom_ratio - top_ratio) / 2.0,
#         0.01,
#     )

#     distance = abs(
#         relative_y - region_center
#     )

#     return max(
#         0.0,
#         1.0 - (
#             distance / region_half_width
#         ) * 0.25,
#     )


# def _helmet_score(
#     person: TrackedPerson,
#     detection: Detection,
#     min_confidence: float,
#     min_overlap: float = 0.65,
# ) -> float | None:
#     if detection.confidence < min_confidence:
#         return None

#     person_box = person.bbox
#     helmet_box = detection.bbox

#     overlap = calculate_overlap_ratio(
#         person_box,
#         helmet_box,
#     )

#     if overlap < min_overlap:
#         return None

#     horizontal_score = _horizontal_position_score(
#         person_box,
#         helmet_box,
#     )

#     vertical_score = _vertical_position_score(
#         person_box,
#         helmet_box,
#         top_ratio=0.00,
#         bottom_ratio=0.40,
#     )

#     distance = _normalized_center_distance(
#         person_box,
#         helmet_box,
#     )

#     distance_score = max(
#         0.0,
#         1.0 - distance,
#     )

#     confidence_score = max(
#         0.0,
#         min(1.0, detection.confidence),
#     )

#     return (
#         0.30 * horizontal_score
#         + 0.25 * vertical_score
#         + 0.20 * distance_score
#         + 0.15 * overlap
#         + 0.10 * confidence_score
#     )


# def _vest_score(
#     person: TrackedPerson,
#     detection: Detection,
#     min_confidence: float,
#     min_overlap: float = 0.65,
# ) -> float | None:
#     if detection.confidence < min_confidence:
#         return None

#     person_box = person.bbox
#     vest_box = detection.bbox

#     overlap = calculate_overlap_ratio(
#         person_box,
#         vest_box,
#     )

#     if overlap < min_overlap:
#         return None

#     horizontal_score = _horizontal_position_score(
#         person_box,
#         vest_box,
#     )

#     vertical_score = _vertical_position_score(
#         person_box,
#         vest_box,
#         top_ratio=0.10,
#         bottom_ratio=0.85,
#     )

#     distance = _normalized_center_distance(
#         person_box,
#         vest_box,
#     )

#     distance_score = max(
#         0.0,
#         1.0 - distance,
#     )

#     confidence_score = max(
#         0.0,
#         min(1.0, detection.confidence),
#     )

#     return (
#         0.25 * horizontal_score
#         + 0.30 * vertical_score
#         + 0.20 * distance_score
#         + 0.15 * overlap
#         + 0.10 * confidence_score
#     )


# def _assign_helmet_detections(
#     tracked_persons: list[TrackedPerson],
#     helmet_detections: list[Detection],
#     min_confidence: float,
#     min_overlap: float = 0.65,
# ) -> dict[int, int]:
#     """
#     Assign each helmet detection to at most one person.

#     Returns:
#         track_id -> helmet_detection_index
#     """

#     candidates: list[
#         tuple[float, int, int]
#     ] = []

#     for person_index, person in enumerate(
#         tracked_persons
#     ):
#         for detection_index, detection in enumerate(
#             helmet_detections
#         ):
#             score = _helmet_score(
#                 person,
#                 detection,
#                 min_confidence,
#                 min_overlap=min_overlap,
#             )

#             if score is None:
#                 continue

#             candidates.append(
#                 (
#                     score,
#                     person_index,
#                     detection_index,
#                 )
#             )

#     # Highest-quality associations are considered first.
#     #
#     # Tie-break by person index and detection index to keep
#     # the result deterministic.
#     candidates.sort(
#         key=lambda item: (
#             -item[0],
#             item[1],
#             item[2],
#         )
#     )

#     assigned_people: set[int] = set()
#     assigned_detections: set[int] = set()

#     assignments: dict[int, int] = {}

#     for (
#         _score,
#         person_index,
#         detection_index,
#     ) in candidates:

#         if person_index in assigned_people:
#             continue

#         if detection_index in assigned_detections:
#             continue

#         track_id = tracked_persons[
#             person_index
#         ].track_id

#         assignments[track_id] = detection_index

#         assigned_people.add(
#             person_index
#         )

#         assigned_detections.add(
#             detection_index
#         )

#     return assignments


# def _assign_vest_detections(
#     tracked_persons: list[TrackedPerson],
#     vest_detections: list[Detection],
#     min_confidence: float,
#     min_overlap: float = 0.65,
# ) -> dict[int, int]:
#     """
#     Assign each vest detection to at most one person.

#     Returns:
#         track_id -> vest_detection_index
#     """

#     candidates: list[
#         tuple[float, int, int]
#     ] = []

#     for person_index, person in enumerate(
#         tracked_persons
#     ):
#         for detection_index, detection in enumerate(
#             vest_detections
#         ):
#             score = _vest_score(
#                 person,
#                 detection,
#                 min_confidence,
#                 min_overlap=min_overlap,
#             )

#             if score is None:
#                 continue

#             candidates.append(
#                 (
#                     score,
#                     person_index,
#                     detection_index,
#                 )
#             )

#     candidates.sort(
#         key=lambda item: (
#             -item[0],
#             item[1],
#             item[2],
#         )
#     )

#     assigned_people: set[int] = set()
#     assigned_detections: set[int] = set()

#     assignments: dict[int, int] = {}

#     for (
#         _score,
#         person_index,
#         detection_index,
#     ) in candidates:

#         if person_index in assigned_people:
#             continue

#         if detection_index in assigned_detections:
#             continue

#         track_id = tracked_persons[
#             person_index
#         ].track_id

#         assignments[track_id] = detection_index

#         assigned_people.add(
#             person_index
#         )

#         assigned_detections.add(
#             detection_index
#         )

#     return assignments


# def associate_ppe(
#     tracked_persons: list[TrackedPerson],
#     detections: list[Detection],
#     min_helmet_conf: float ,
#     min_vest_conf: float ,
#     min_overlap: float = 0.65,
# ) -> list[PPEStatus]:
#     """
#     Associate Helmet and Vest detections with tracked persons.

#     IMPORTANT:
#     This function is designed to receive ALL tracked persons
#     and ALL detections from one frame.

#     Each helmet detection may belong to only one worker.
#     Each vest detection may belong to only one worker.

#     min_overlap acts as a same-box stability check: a PPE detection
#     must overlap the person box closely enough to be considered the
#     same worker's equipment. This prevents jitter and duplicate PPE
#     assignments from repeatedly changing a worker's compliance state.
#     """

#     if not 0.0 <= min_overlap <= 1.0:
#         raise ValueError("min_overlap must be between 0.0 and 1.0")

#     if not tracked_persons:
#         return []

#     helmets = [
#         detection
#         for detection in detections
#         if detection.class_name.lower() == "helmet"
#     ]

#     vests = [
#         detection
#         for detection in detections
#         if detection.class_name.lower() == "vest"
#     ]

#     helmet_assignments = _assign_helmet_detections(
#         tracked_persons=tracked_persons,
#         helmet_detections=helmets,
#         min_confidence=min_helmet_conf,
#         min_overlap=min_overlap,
#     )

#     vest_assignments = _assign_vest_detections(
#         tracked_persons=tracked_persons,
#         vest_detections=vests,
#         min_confidence=min_vest_conf,
#         min_overlap=min_overlap,
#     )

#     results: list[PPEStatus] = []

#     for person in tracked_persons:
#         track_id = person.track_id

#         results.append(
#             PPEStatus(
#                 track_id=track_id,
#                 helmet_detected=(
#                     track_id in helmet_assignments
#                 ),
#                 vest_detected=(
#                     track_id in vest_assignments
#                 ),
#             )
#         )

#     return results
from __future__ import annotations

from dataclasses import dataclass

from app.vision.ppe_detector import Detection
from app.vision.tracker import TrackedPerson


@dataclass(frozen=True)
class PPEStatus:
    track_id: int
    helmet_detected: bool
    vest_detected: bool


# ============================================================
# Geometry helpers
# ============================================================


def _area(
    box: tuple[float, float, float, float],
) -> float:
    x1, y1, x2, y2 = box

    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)

    return width * height


def _intersection_area(
    box_a: tuple[float, float, float, float],
    box_b: tuple[float, float, float, float],
) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    width = max(0.0, ix2 - ix1)
    height = max(0.0, iy2 - iy1)

    return width * height


def calculate_overlap_ratio(
    person_box: tuple[float, float, float, float],
    ppe_box: tuple[float, float, float, float],
) -> float:
    """
    Return the fraction of the PPE bounding box that overlaps
    the person's bounding box.

    1.0 = entire PPE box is inside the person box.
    0.0 = no overlap.
    """

    ppe_area = _area(ppe_box)

    if ppe_area <= 0.0:
        return 0.0

    return _intersection_area(
        person_box,
        ppe_box,
    ) / ppe_area


def _center(
    box: tuple[float, float, float, float],
) -> tuple[float, float]:
    x1, y1, x2, y2 = box

    return (
        (x1 + x2) / 2.0,
        (y1 + y2) / 2.0,
    )


def _normalized_center_distance(
    person_box: tuple[float, float, float, float],
    ppe_box: tuple[float, float, float, float],
) -> float:
    """
    Distance between PPE center and person center,
    normalized by the person dimensions.

    This is retained as a supporting signal. It is deliberately
    not the dominant helmet signal because a helmet is naturally
    above the center of the full person box.
    """

    px, py = _center(person_box)
    qx, qy = _center(ppe_box)

    person_width = max(
        1.0,
        person_box[2] - person_box[0],
    )

    person_height = max(
        1.0,
        person_box[3] - person_box[1],
    )

    dx = abs(px - qx) / person_width
    dy = abs(py - qy) / person_height

    return (dx * dx + dy * dy) ** 0.5


def _horizontal_position_score(
    person_box: tuple[float, float, float, float],
    ppe_box: tuple[float, float, float, float],
) -> float:
    """
    Score horizontal alignment between PPE center and
    person center.

    1.0 = perfectly centered.
    0.0 = far away horizontally.
    """

    person_cx, _ = _center(person_box)
    ppe_cx, _ = _center(ppe_box)

    person_width = max(
        1.0,
        person_box[2] - person_box[0],
    )

    normalized_offset = (
        abs(ppe_cx - person_cx)
        / person_width
    )

    return max(
        0.0,
        1.0 - normalized_offset,
    )


def _vertical_position_score(
    person_box: tuple[float, float, float, float],
    ppe_box: tuple[float, float, float, float],
    top_ratio: float,
    bottom_ratio: float,
) -> float:
    """
    Score whether the PPE is in the expected vertical
    region of the person.

    The score remains tolerant near the edges of the region,
    which is useful when body posture changes.
    """

    _, ppe_cy = _center(ppe_box)

    person_y1 = person_box[1]

    person_height = max(
        1.0,
        person_box[3] - person_box[1],
    )

    relative_y = (
        ppe_cy - person_y1
    ) / person_height

    if relative_y < top_ratio:
        distance = top_ratio - relative_y

        return max(
            0.0,
            1.0 - (
                distance
                / max(
                    top_ratio + 0.10,
                    0.10,
                )
            ),
        )

    if relative_y > bottom_ratio:
        distance = relative_y - bottom_ratio

        return max(
            0.0,
            1.0 - (
                distance
                / max(
                    (1.0 - bottom_ratio) + 0.10,
                    0.10,
                )
            ),
        )

    region_center = (
        top_ratio + bottom_ratio
    ) / 2.0

    region_half_width = max(
        (bottom_ratio - top_ratio) / 2.0,
        0.01,
    )

    distance = abs(
        relative_y - region_center
    )

    return max(
        0.0,
        1.0
        - (
            0.25
            * distance
            / region_half_width
        ),
    )


# ============================================================
# Helmet scoring
# ============================================================


def _helmet_score(
    person: TrackedPerson,
    detection: Detection,
    min_confidence: float,
    min_overlap: float,
    min_association_score: float,
) -> float | None:
    """
    Helmet must be physically close to the worker's estimated
    head position.

    Scoring:
        35% head proximity
        30% vertical/head position
        15% horizontal alignment
        10% overlap
        10% YOLO confidence
    """

    # --------------------------------------------------------
    # 1. YOLO confidence gate
    # --------------------------------------------------------

    if detection.confidence < min_confidence:
        return None

    person_box = person.bbox
    helmet_box = detection.bbox

    person_x1, person_y1, person_x2, person_y2 = person_box

    person_width = person_x2 - person_x1
    person_height = person_y2 - person_y1

    if person_width <= 0.0 or person_height <= 0.0:
        return None

    # --------------------------------------------------------
    # 2. Bounding-box overlap
    #
    # Keep this as a supporting signal, not the main test.
    # --------------------------------------------------------

    overlap = calculate_overlap_ratio(
        person_box,
        helmet_box,
    )

    if overlap < min_overlap:
        return None

    # --------------------------------------------------------
    # 3. Helmet center
    # --------------------------------------------------------

    helmet_cx, helmet_cy = _center(
        helmet_box
    )

    # --------------------------------------------------------
    # 4. Estimate head center
    #
    # Approximately 12% down from the top of the person box.
    # --------------------------------------------------------

    head_center_x = (
        person_x1 + person_x2
    ) / 2.0

    head_center_y = (
        person_y1
        + 0.12 * person_height
    )

    # --------------------------------------------------------
    # 5. Normalized distance from helmet to head
    # --------------------------------------------------------

    head_dx = (
        helmet_cx - head_center_x
    ) / person_width

    head_dy = (
        helmet_cy - head_center_y
    ) / person_height

    head_distance = (
        head_dx * head_dx
        + head_dy * head_dy
    ) ** 0.5

    # --------------------------------------------------------
    # HARD REJECTION
    #
    # If the helmet is too far from the estimated head,
    # it is NOT considered worn, regardless of YOLO confidence
    # or body-box overlap.
    # --------------------------------------------------------

    MAX_HEAD_DISTANCE = 0.35

    if head_distance > MAX_HEAD_DISTANCE:
        return None

    # --------------------------------------------------------
    # 6. Head proximity score
    # --------------------------------------------------------

    head_proximity_score = max(
        0.0,
        1.0
        - (
            head_distance
            / MAX_HEAD_DISTANCE
        ),
    )

    # --------------------------------------------------------
    # 7. Horizontal alignment
    # --------------------------------------------------------

    horizontal_score = _horizontal_position_score(
        person_box,
        helmet_box,
    )

    # --------------------------------------------------------
    # 8. Vertical head position
    # --------------------------------------------------------

    vertical_score = _vertical_position_score(
        person_box,
        helmet_box,
        top_ratio=0.00,
        bottom_ratio=0.35,
    )

    # --------------------------------------------------------
    # 9. YOLO confidence
    # --------------------------------------------------------

    confidence_score = max(
        0.0,
        min(
            1.0,
            detection.confidence,
        ),
    )

    # --------------------------------------------------------
    # 10. Final helmet association score
    # --------------------------------------------------------

    score = (
        0.35 * head_proximity_score
        + 0.30 * vertical_score
        + 0.15 * horizontal_score
        + 0.10 * overlap
        + 0.10 * confidence_score
    )

    if score < min_association_score:
        return None

    return score

# ============================================================
# Vest scoring
# ============================================================


def _vest_score(
    person: TrackedPerson,
    detection: Detection,
    min_confidence: float,
    min_overlap: float,
    min_association_score: float,
) -> float | None:
    """
    Calculate how strongly a vest belongs to a worker.

    Vest weighting:

        25% horizontal position
        30% torso/vertical position
        20% center distance
        15% bounding-box overlap
        10% YOLO confidence
    """

    if detection.confidence < min_confidence:
        return None

    person_box = person.bbox
    vest_box = detection.bbox

    person_width = (
        person_box[2] - person_box[0]
    )

    person_height = (
        person_box[3] - person_box[1]
    )

    if person_width <= 0.0 or person_height <= 0.0:
        return None

    # --------------------------------------------------------
    # Bounding-box overlap
    # --------------------------------------------------------

    overlap = calculate_overlap_ratio(
        person_box,
        vest_box,
    )

    if overlap < min_overlap:
        return None

    # --------------------------------------------------------
    # Horizontal alignment
    # --------------------------------------------------------

    horizontal_score = _horizontal_position_score(
        person_box,
        vest_box,
    )

    # --------------------------------------------------------
    # Torso vertical position
    # --------------------------------------------------------

    vertical_score = _vertical_position_score(
        person_box,
        vest_box,
        top_ratio=0.10,
        bottom_ratio=0.85,
    )

    # --------------------------------------------------------
    # Center distance
    # --------------------------------------------------------

    center_distance = _normalized_center_distance(
        person_box,
        vest_box,
    )

    distance_score = max(
        0.0,
        1.0 - center_distance,
    )

    # --------------------------------------------------------
    # YOLO confidence
    # --------------------------------------------------------

    confidence_score = max(
        0.0,
        min(
            1.0,
            detection.confidence,
        ),
    )

    # --------------------------------------------------------
    # Final vest association score
    # --------------------------------------------------------

    score = (
        0.25 * horizontal_score
        + 0.30 * vertical_score
        + 0.20 * distance_score
        + 0.15 * overlap
        + 0.10 * confidence_score
    )

    if score < min_association_score:
        return None

    return score


# ============================================================
# Helmet assignment
# ============================================================


def _assign_helmet_detections(
    tracked_persons: list[TrackedPerson],
    helmet_detections: list[Detection],
    min_confidence: float,
    min_overlap: float,
    min_association_score: float,
) -> dict[int, int]:
    """
    Assign each helmet detection to at most one worker.

    Returns:

        track_id -> helmet_detection_index
    """

    candidates: list[
        tuple[float, int, int]
    ] = []

    for person_index, person in enumerate(
        tracked_persons
    ):
        for detection_index, detection in enumerate(
            helmet_detections
        ):
            score = _helmet_score(
                person=person,
                detection=detection,
                min_confidence=min_confidence,
                min_overlap=min_overlap,
                min_association_score=min_association_score,
            )

            if score is None:
                continue

            candidates.append(
                (
                    score,
                    person_index,
                    detection_index,
                )
            )

    # Highest score first.
    #
    # Track ID and detection index provide deterministic
    # tie-breaking.
    candidates.sort(
        key=lambda item: (
            -item[0],
            tracked_persons[
                item[1]
            ].track_id,
            item[2],
        )
    )

    assigned_people: set[int] = set()
    assigned_detections: set[int] = set()

    assignments: dict[int, int] = {}

    for (
        _score,
        person_index,
        detection_index,
    ) in candidates:

        # One helmet per person.
        if person_index in assigned_people:
            continue

        # One person per helmet detection.
        if detection_index in assigned_detections:
            continue

        track_id = tracked_persons[
            person_index
        ].track_id

        assignments[
            track_id
        ] = detection_index

        assigned_people.add(
            person_index
        )

        assigned_detections.add(
            detection_index
        )

    return assignments


# ============================================================
# Vest assignment
# ============================================================


def _assign_vest_detections(
    tracked_persons: list[TrackedPerson],
    vest_detections: list[Detection],
    min_confidence: float,
    min_overlap: float,
    min_association_score: float,
) -> dict[int, int]:
    """
    Assign each vest detection to at most one worker.

    Returns:

        track_id -> vest_detection_index
    """

    candidates: list[
        tuple[float, int, int]
    ] = []

    for person_index, person in enumerate(
        tracked_persons
    ):
        for detection_index, detection in enumerate(
            vest_detections
        ):
            score = _vest_score(
                person=person,
                detection=detection,
                min_confidence=min_confidence,
                min_overlap=min_overlap,
                min_association_score=min_association_score,
            )

            if score is None:
                continue

            candidates.append(
                (
                    score,
                    person_index,
                    detection_index,
                )
            )

    candidates.sort(
        key=lambda item: (
            -item[0],
            tracked_persons[
                item[1]
            ].track_id,
            item[2],
        )
    )

    assigned_people: set[int] = set()
    assigned_detections: set[int] = set()

    assignments: dict[int, int] = {}

    for (
        _score,
        person_index,
        detection_index,
    ) in candidates:

        # One vest per person.
        if person_index in assigned_people:
            continue

        # One person per vest detection.
        if detection_index in assigned_detections:
            continue

        track_id = tracked_persons[
            person_index
        ].track_id

        assignments[
            track_id
        ] = detection_index

        assigned_people.add(
            person_index
        )

        assigned_detections.add(
            detection_index
        )

    return assignments


# ============================================================
# Public association function
# ============================================================


def associate_ppe(
    tracked_persons: list[TrackedPerson],
    detections: list[Detection],
    min_helmet_conf: float,
    min_vest_conf: float,
    min_overlap: float = 0.35,
    helmet_min_overlap: float | None = None,
    vest_min_overlap: float = 0.55,
    min_association_score: float = 0.35,
) -> list[PPEStatus]:
    """
    Associate Helmet and Vest detections with tracked workers.

    One-to-one rules:

        one helmet detection -> at most one worker
        one vest detection   -> at most one worker

    Recommended defaults:

        helmet_min_overlap = 0.35
        vest_min_overlap   = 0.55
        min_association_score = 0.35

    The caller can still override these values when needed.
    """

    if not 0.0 <= min_overlap <= 1.0:
        raise ValueError(
            "min_overlap must be between 0.0 and 1.0"
        )

    if helmet_min_overlap is None:
        helmet_min_overlap = min_overlap

    if not 0.0 <= helmet_min_overlap <= 1.0:
        raise ValueError(
            "helmet_min_overlap must be between 0.0 and 1.0"
        )

    if not 0.0 <= vest_min_overlap <= 1.0:
        raise ValueError(
            "vest_min_overlap must be between 0.0 and 1.0"
        )

    if not 0.0 <= min_association_score <= 1.0:
        raise ValueError(
            "min_association_score must be between 0.0 and 1.0"
        )

    if not tracked_persons:
        return []

    # --------------------------------------------------------
    # Extract PPE detections
    # --------------------------------------------------------

    helmets = [
        detection
        for detection in detections
        if detection.class_name.lower()
        in {
            "helmet",
            "hard_hat",
            "head_protection",
        }
    ]

    vests = [
        detection
        for detection in detections
        if detection.class_name.lower()
        in {
            "vest",
            "safety_vest",
            "torso_protection",
        }
    ]

    # --------------------------------------------------------
    # One-to-one assignment
    # --------------------------------------------------------

    helmet_assignments = _assign_helmet_detections(
        tracked_persons=tracked_persons,
        helmet_detections=helmets,
        min_confidence=min_helmet_conf,
        min_overlap=helmet_min_overlap,
        min_association_score=min_association_score,
    )

    vest_assignments = _assign_vest_detections(
        tracked_persons=tracked_persons,
        vest_detections=vests,
        min_confidence=min_vest_conf,
        min_overlap=vest_min_overlap,
        min_association_score=min_association_score,
    )

    # --------------------------------------------------------
    # Build final status for every tracked person
    # --------------------------------------------------------

    results: list[PPEStatus] = []

    for person in tracked_persons:
        track_id = person.track_id

        results.append(
            PPEStatus(
                track_id=track_id,
                helmet_detected=(
                    track_id in helmet_assignments
                ),
                vest_detected=(
                    track_id in vest_assignments
                ),
            )
        )

    return results