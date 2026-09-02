# from dataclasses import dataclass

# from app.vision.ppe_detector import Detection
# from app.vision.tracker import TrackedPerson


# @dataclass(frozen=True)
# class PPEStatus:
#     """
#     PPE state associated with one tracked person.
#     """

#     track_id: int
#     helmet_detected: bool
#     vest_detected: bool


# def calculate_iou(
#     box_a: tuple[float, float, float, float],
#     box_b: tuple[float, float, float, float],
# ) -> float:
#     """
#     Calculate Intersection over Union (IoU) between two boxes.

#     Boxes use:
#         (x1, y1, x2, y2)
#     """

#     ax1, ay1, ax2, ay2 = box_a
#     bx1, by1, bx2, by2 = box_b

#     intersection_x1 = max(ax1, bx1)
#     intersection_y1 = max(ay1, by1)
#     intersection_x2 = min(ax2, bx2)
#     intersection_y2 = min(ay2, by2)

#     intersection_width = max(
#         0.0,
#         intersection_x2 - intersection_x1,
#     )

#     intersection_height = max(
#         0.0,
#         intersection_y2 - intersection_y1,
#     )

#     intersection_area = (
#         intersection_width * intersection_height
#     )

#     if intersection_area == 0:
#         return 0.0

#     area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
#     area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)

#     union_area = area_a + area_b - intersection_area

#     if union_area <= 0:
#         return 0.0

#     return intersection_area / union_area


# def associate_ppe(
#     tracked_persons: list[TrackedPerson],
#     detections: list[Detection],
#     iou_threshold: float = 0.01,
# ) -> list[PPEStatus]:
#     """
#     Associate Helmet and Vest detections with tracked persons.

#     A PPE detection is associated with a person when its bounding
#     box has sufficient overlap with the person's bounding box.

#     Args:
#         tracked_persons:
#             Persons already assigned track IDs by ByteTrack.

#         detections:
#             YOLO detections containing Person, Helmet and Vest.

#         iou_threshold:
#             Minimum IoU required for PPE/person association.

#     Returns:
#         PPEStatus for every tracked person.
#     """

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

#     results: list[PPEStatus] = []

#     for person in tracked_persons:
#         helmet_detected = any(
#             calculate_iou(
#                 person.bbox,
#                 helmet.bbox,
#             )
#             >= iou_threshold
#             for helmet in helmets
#         )

#         vest_detected = any(
#             calculate_iou(
#                 person.bbox,
#                 vest.bbox,
#             )
#             >= iou_threshold
#             for vest in vests
#         )

#         results.append(
#             PPEStatus(
#                 track_id=person.track_id,
#                 helmet_detected=helmet_detected,
#                 vest_detected=vest_detected,
#             )
#         )

#     return results
# from dataclasses import dataclass

# from app.vision.ppe_detector import Detection
# from app.vision.tracker import TrackedPerson


# @dataclass(frozen=True)
# class PPEStatus:
#     """
#     PPE state associated with one tracked person.
#     """

#     track_id: int
#     helmet_detected: bool
#     vest_detected: bool


# def associate_ppe(
#     tracked_persons: list[TrackedPerson],
#     detections: list[Detection],
#     min_helmet_conf: float = 0.80,
#     min_vest_conf: float = 0.40,
# ) -> list[PPEStatus]:
#     """
#     Associate Helmet and Vest detections with tracked persons using relative
#     spatial geometry and confidence thresholds.

#     Args:
#         tracked_persons:
#             Persons already assigned track IDs by ByteTrack.

#         detections:
#             YOLO detections containing Person, Helmet, Vest, etc.

#         min_helmet_conf:
#             Minimum confidence required to accept a helmet detection.

#         min_vest_conf:
#             Minimum confidence required to accept a vest detection.

#     Returns:
#         PPEStatus for every tracked person.
#     """
#     results: list[PPEStatus] = []

#     for person in tracked_persons:
#         wx1, wy1, wx2, wy2 = person.bbox
#         worker_height = wy2 - wy1
#         worker_width = wx2 - wx1

#         # Skip invalid bounding boxes
#         if worker_height <= 0 or worker_width <= 0:
#             results.append(
#                 PPEStatus(
#                     track_id=person.track_id,
#                     helmet_detected=False,
#                     vest_detected=False,
#                 )
#             )
#             continue

#         helmet_detected = False
#         vest_detected = False

#         for det in detections:
#             class_name = det.class_name.lower()
#             conf = det.confidence
#             px1, py1, px2, py2 = det.bbox

#             # Center coordinates of the PPE bounding box
#             ppe_cx = (px1 + px2) / 2.0
#             ppe_cy = (py1 + py2) / 2.0

#             # --- 1. HELMET VALIDATION ---
#             if class_name in ["helmet", "hard_hat", "head_protection"]:
#                 if conf < min_helmet_conf:
#                     continue

#                 # Must be horizontally inside the person box
#                 is_horizontally_inside = wx1 <= ppe_cx <= wx2
#                 # Must lie strictly within top 25% of the person's bounding box height
#                 is_in_head_zone = wy1 <= ppe_cy <= (wy1 + 0.25 * worker_height)

#                 if is_horizontally_inside and is_in_head_zone:
#                     helmet_detected = True

#             # --- 2. VEST VALIDATION ---
#             elif class_name in ["vest", "safety_vest", "torso_protection"]:
#                 if conf < min_vest_conf:
#                     continue

#                 # Must be horizontally inside the person box
#                 is_horizontally_inside = wx1 <= ppe_cx <= wx2
#                 # Must lie in the central torso region (20% to 75% of person height)
#                 is_in_torso_zone = (
#                     wy1 + 0.20 * worker_height
#                 ) <= ppe_cy <= (wy1 + 0.75 * worker_height)

#                 if is_horizontally_inside and is_in_torso_zone:
#                     vest_detected = True

#         results.append(
#             PPEStatus(
#                 track_id=person.track_id,
#                 helmet_detected=helmet_detected,
#                 vest_detected=vest_detected,
#             )
#         )

#     return results
from dataclasses import dataclass
from app.vision.ppe_detector import Detection
from app.vision.tracker import TrackedPerson


@dataclass(frozen=True)
class PPEStatus:
    track_id: int
    helmet_detected: bool
    vest_detected: bool


def calculate_overlap_ratio(person_box: tuple[float, float, float, float], ppe_box: tuple[float, float, float, float]) -> float:
    """
    Calculates what fraction of the PPE bounding box lies INSIDE the person bounding box.
    This handles bending, sideways angles, and changing aspect ratios cleanly.
    """
    px1, py1, px2, py2 = person_box
    bx1, by1, bx2, by2 = ppe_box

    ix1 = max(px1, bx1)
    iy1 = max(py1, by1)
    ix2 = min(px2, bx2)
    iy2 = min(py2, by2)

    inter_w = max(0.0, ix2 - ix1)
    inter_h = max(0.0, iy2 - iy1)
    intersection_area = inter_w * inter_h

    ppe_area = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    if ppe_area <= 0:
        return 0.0

    return intersection_area / ppe_area


def associate_ppe(
    tracked_persons: list[TrackedPerson],
    detections: list[Detection],
    min_helmet_conf: float = 0.40,
    min_vest_conf: float = 0.40,  # Lowered for sideways/backwards posture detections
    min_overlap: float = 0.50,    # At least 50% of the vest/helmet must lie inside the person box
) -> list[PPEStatus]:
    results: list[PPEStatus] = []

    for person in tracked_persons:
        wx1, wy1, wx2, wy2 = person.bbox
        worker_height = wy2 - wy1

        if worker_height <= 0:
            results.append(PPEStatus(track_id=person.track_id, helmet_detected=False, vest_detected=False))
            continue

        helmet_detected = False
        vest_detected = False

        for det in detections:
            class_name = det.class_name.lower()
            conf = det.confidence

            # Calculate how much of the PPE item is inside the worker bounding box
            overlap = calculate_overlap_ratio(person.bbox, det.bbox)

            # --- 1. HELMET CHECK ---
            if class_name in ["helmet", "hard_hat", "head_protection"]:
                if conf >= min_helmet_conf and overlap >= min_overlap:
                    # Optional check: ensure helmet is in upper half of person box
                    ppe_cy = (det.bbox[1] + det.bbox[3]) / 2.0
                    if ppe_cy <= (wy1 + 0.40 * worker_height):
                        helmet_detected = True

            # --- 2. VEST CHECK ---
            elif class_name in ["vest", "safety_vest", "torso_protection"]:
                if conf >= min_vest_conf and overlap >= min_overlap:
                    vest_detected = True

        results.append(
            PPEStatus(
                track_id=person.track_id,
                helmet_detected=helmet_detected,
                vest_detected=vest_detected,
            )
        )

    return results