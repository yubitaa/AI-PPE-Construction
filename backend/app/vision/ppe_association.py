# # from dataclasses import dataclass

# # from app.vision.ppe_detector import Detection
# # from app.vision.tracker import TrackedPerson


# # @dataclass(frozen=True)
# # class PPEStatus:
# #     """
# #     PPE state associated with one tracked person.
# #     """

# #     track_id: int
# #     helmet_detected: bool
# #     vest_detected: bool


# # def calculate_iou(
# #     box_a: tuple[float, float, float, float],
# #     box_b: tuple[float, float, float, float],
# # ) -> float:
# #     """
# #     Calculate Intersection over Union (IoU) between two boxes.

# #     Boxes use:
# #         (x1, y1, x2, y2)
# #     """

# #     ax1, ay1, ax2, ay2 = box_a
# #     bx1, by1, bx2, by2 = box_b

# #     intersection_x1 = max(ax1, bx1)
# #     intersection_y1 = max(ay1, by1)
# #     intersection_x2 = min(ax2, bx2)
# #     intersection_y2 = min(ay2, by2)

# #     intersection_width = max(
# #         0.0,
# #         intersection_x2 - intersection_x1,
# #     )

# #     intersection_height = max(
# #         0.0,
# #         intersection_y2 - intersection_y1,
# #     )

# #     intersection_area = (
# #         intersection_width * intersection_height
# #     )

# #     if intersection_area == 0:
# #         return 0.0

# #     area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
# #     area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)

# #     union_area = area_a + area_b - intersection_area

# #     if union_area <= 0:
# #         return 0.0

# #     return intersection_area / union_area


# # def associate_ppe(
# #     tracked_persons: list[TrackedPerson],
# #     detections: list[Detection],
# #     iou_threshold: float = 0.01,
# # ) -> list[PPEStatus]:
# #     """
# #     Associate Helmet and Vest detections with tracked persons.

# #     A PPE detection is associated with a person when its bounding
# #     box has sufficient overlap with the person's bounding box.

# #     Args:
# #         tracked_persons:
# #             Persons already assigned track IDs by ByteTrack.

# #         detections:
# #             YOLO detections containing Person, Helmet and Vest.

# #         iou_threshold:
# #             Minimum IoU required for PPE/person association.

# #     Returns:
# #         PPEStatus for every tracked person.
# #     """

# #     helmets = [
# #         detection
# #         for detection in detections
# #         if detection.class_name.lower() == "helmet"
# #     ]

# #     vests = [
# #         detection
# #         for detection in detections
# #         if detection.class_name.lower() == "vest"
# #     ]

# #     results: list[PPEStatus] = []

# #     for person in tracked_persons:
# #         helmet_detected = any(
# #             calculate_iou(
# #                 person.bbox,
# #                 helmet.bbox,
# #             )
# #             >= iou_threshold
# #             for helmet in helmets
# #         )

# #         vest_detected = any(
# #             calculate_iou(
# #                 person.bbox,
# #                 vest.bbox,
# #             )
# #             >= iou_threshold
# #             for vest in vests
# #         )

# #         results.append(
# #             PPEStatus(
# #                 track_id=person.track_id,
# #                 helmet_detected=helmet_detected,
# #                 vest_detected=vest_detected,
# #             )
# #         )

# #     return results
# # from dataclasses import dataclass

# # from app.vision.ppe_detector import Detection
# # from app.vision.tracker import TrackedPerson


# # @dataclass(frozen=True)
# # class PPEStatus:
# #     """
# #     PPE state associated with one tracked person.
# #     """

# #     track_id: int
# #     helmet_detected: bool
# #     vest_detected: bool


# # def associate_ppe(
# #     tracked_persons: list[TrackedPerson],
# #     detections: list[Detection],
# #     min_helmet_conf: float = 0.80,
# #     min_vest_conf: float = 0.40,
# # ) -> list[PPEStatus]:
# #     """
# #     Associate Helmet and Vest detections with tracked persons using relative
# #     spatial geometry and confidence thresholds.

# #     Args:
# #         tracked_persons:
# #             Persons already assigned track IDs by ByteTrack.

# #         detections:
# #             YOLO detections containing Person, Helmet, Vest, etc.

# #         min_helmet_conf:
# #             Minimum confidence required to accept a helmet detection.

# #         min_vest_conf:
# #             Minimum confidence required to accept a vest detection.

# #     Returns:
# #         PPEStatus for every tracked person.
# #     """
# #     results: list[PPEStatus] = []

# #     for person in tracked_persons:
# #         wx1, wy1, wx2, wy2 = person.bbox
# #         worker_height = wy2 - wy1
# #         worker_width = wx2 - wx1

# #         # Skip invalid bounding boxes
# #         if worker_height <= 0 or worker_width <= 0:
# #             results.append(
# #                 PPEStatus(
# #                     track_id=person.track_id,
# #                     helmet_detected=False,
# #                     vest_detected=False,
# #                 )
# #             )
# #             continue

# #         helmet_detected = False
# #         vest_detected = False

# #         for det in detections:
# #             class_name = det.class_name.lower()
# #             conf = det.confidence
# #             px1, py1, px2, py2 = det.bbox

# #             # Center coordinates of the PPE bounding box
# #             ppe_cx = (px1 + px2) / 2.0
# #             ppe_cy = (py1 + py2) / 2.0

# #             # --- 1. HELMET VALIDATION ---
# #             if class_name in ["helmet", "hard_hat", "head_protection"]:
# #                 if conf < min_helmet_conf:
# #                     continue

# #                 # Must be horizontally inside the person box
# #                 is_horizontally_inside = wx1 <= ppe_cx <= wx2
# #                 # Must lie strictly within top 25% of the person's bounding box height
# #                 is_in_head_zone = wy1 <= ppe_cy <= (wy1 + 0.25 * worker_height)

# #                 if is_horizontally_inside and is_in_head_zone:
# #                     helmet_detected = True

# #             # --- 2. VEST VALIDATION ---
# #             elif class_name in ["vest", "safety_vest", "torso_protection"]:
# #                 if conf < min_vest_conf:
# #                     continue

# #                 # Must be horizontally inside the person box
# #                 is_horizontally_inside = wx1 <= ppe_cx <= wx2
# #                 # Must lie in the central torso region (20% to 75% of person height)
# #                 is_in_torso_zone = (
# #                     wy1 + 0.20 * worker_height
# #                 ) <= ppe_cy <= (wy1 + 0.75 * worker_height)

# #                 if is_horizontally_inside and is_in_torso_zone:
# #                     vest_detected = True

# #         results.append(
# #             PPEStatus(
# #                 track_id=person.track_id,
# #                 helmet_detected=helmet_detected,
# #                 vest_detected=vest_detected,
# #             )
# #         )

# #     return results
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


# # ---------------------------------------------------------
# # Geometry helpers
# # ---------------------------------------------------------


# def calculate_overlap_ratio(
#     person_box: tuple[float, float, float, float],
#     ppe_box: tuple[float, float, float, float],
# ) -> float:
#     """
#     Calculate what fraction of the PPE bounding box lies
#     inside the person bounding box.

#     Boxes use:
#         (x1, y1, x2, y2)

#     This is used as supporting geometry, not as the only
#     association rule.
#     """

#     px1, py1, px2, py2 = person_box
#     bx1, by1, bx2, by2 = ppe_box

#     ix1 = max(px1, bx1)
#     iy1 = max(py1, by1)
#     ix2 = min(px2, bx2)
#     iy2 = min(py2, by2)

#     intersection_width = max(
#         0.0,
#         ix2 - ix1,
#     )

#     intersection_height = max(
#         0.0,
#         iy2 - iy1,
#     )

#     intersection_area = (
#         intersection_width * intersection_height
#     )

#     ppe_width = max(
#         0.0,
#         bx2 - bx1,
#     )

#     ppe_height = max(
#         0.0,
#         by2 - by1,
#     )

#     ppe_area = ppe_width * ppe_height

#     if ppe_area <= 0.0:
#         return 0.0

#     return intersection_area / ppe_area


# def _center(
#     box: tuple[float, float, float, float],
# ) -> tuple[float, float]:
#     """
#     Return the center point of a bounding box.
#     """

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
#     Calculate normalized distance between the center of the
#     person and the center of the PPE object.

#     The result is approximately scale-independent because
#     distance is normalized by the person dimensions.
#     """

#     px1, py1, px2, py2 = person_box

#     person_width = max(
#         1.0,
#         px2 - px1,
#     )

#     person_height = max(
#         1.0,
#         py2 - py1,
#     )

#     person_cx, person_cy = _center(person_box)
#     ppe_cx, ppe_cy = _center(ppe_box)

#     dx = (ppe_cx - person_cx) / person_width
#     dy = (ppe_cy - person_cy) / person_height

#     return (dx * dx + dy * dy) ** 0.5


# def _horizontal_position_score(
#     person_box: tuple[float, float, float, float],
#     ppe_box: tuple[float, float, float, float],
# ) -> float:
#     """
#     Score how well the PPE center is horizontally aligned
#     with the person center.

#     Returns a value between approximately 0 and 1.
#     """

#     px1, _, px2, _ = person_box

#     person_width = max(
#         1.0,
#         px2 - px1,
#     )

#     person_cx, _ = _center(person_box)
#     ppe_cx, _ = _center(ppe_box)

#     horizontal_distance = abs(
#         ppe_cx - person_cx
#     ) / person_width

#     return max(
#         0.0,
#         1.0 - horizontal_distance,
#     )


# # ---------------------------------------------------------
# # Candidate scoring
# # ---------------------------------------------------------


# def _helmet_score(
#     person: TrackedPerson,
#     detection: Detection,
#     min_confidence: float,
# ) -> float | None:
#     """
#     Calculate how strongly a helmet detection belongs to a
#     tracked person.

#     Returns:
#         A score when the detection is a valid candidate.
#         None when it should not be associated.

#     Helmet geometry:
#         - helmet must be horizontally close to the person
#         - helmet should be around the head region
#         - a small amount above the Person box is allowed
#         - confidence contributes to the final score
#     """

#     if detection.confidence < min_confidence:
#         return None

#     x1, y1, x2, y2 = person.bbox

#     width = x2 - x1
#     height = y2 - y1

#     if width <= 0.0 or height <= 0.0:
#         return None

#     ppe_cx, ppe_cy = _center(
#         detection.bbox
#     )

#     # -----------------------------------------------------
#     # Head region
#     #
#     # A helmet can extend slightly above the person's
#     # detected bounding box, so do not require it to be
#     # completely inside the person box.
#     # -----------------------------------------------------

#     head_x1 = x1 - (0.15 * width)
#     head_x2 = x2 + (0.15 * width)

#     head_y1 = y1 - (0.20 * height)
#     head_y2 = y1 + (0.40 * height)

#     if not (
#         head_x1 <= ppe_cx <= head_x2
#         and
#         head_y1 <= ppe_cy <= head_y2
#     ):
#         return None

#     overlap = calculate_overlap_ratio(
#         person.bbox,
#         detection.bbox,
#     )

#     horizontal_score = _horizontal_position_score(
#         person.bbox,
#         detection.bbox,
#     )

#     center_distance = _normalized_center_distance(
#         person.bbox,
#         detection.bbox,
#     )

#     distance_score = max(
#         0.0,
#         1.0 - center_distance,
#     )

#     confidence_score = min(
#         1.0,
#         max(
#             0.0,
#             detection.confidence,
#         ),
#     )

#     # -----------------------------------------------------
#     # Weighted score
#     #
#     # Geometry is more important than confidence.
#     # -----------------------------------------------------

#     score = (
#         (0.40 * horizontal_score)
#         + (0.25 * distance_score)
#         + (0.20 * overlap)
#         + (0.15 * confidence_score)
#     )

#     return score


# def _vest_score(
#     person: TrackedPerson,
#     detection: Detection,
#     min_confidence: float,
# ) -> float | None:
#     """
#     Calculate how strongly a vest detection belongs to a
#     tracked person.

#     Vest detections should be located in the person's torso
#     region.
#     """

#     if detection.confidence < min_confidence:
#         return None

#     x1, y1, x2, y2 = person.bbox

#     width = x2 - x1
#     height = y2 - y1

#     if width <= 0.0 or height <= 0.0:
#         return None

#     ppe_cx, ppe_cy = _center(
#         detection.bbox
#     )

#     # -----------------------------------------------------
#     # Torso region
#     # -----------------------------------------------------

#     torso_x1 = x1 - (0.10 * width)
#     torso_x2 = x2 + (0.10 * width)

#     torso_y1 = y1 + (0.15 * height)
#     torso_y2 = y1 + (0.80 * height)

#     if not (
#         torso_x1 <= ppe_cx <= torso_x2
#         and
#         torso_y1 <= ppe_cy <= torso_y2
#     ):
#         return None

#     overlap = calculate_overlap_ratio(
#         person.bbox,
#         detection.bbox,
#     )

#     horizontal_score = _horizontal_position_score(
#         person.bbox,
#         detection.bbox,
#     )

#     center_distance = _normalized_center_distance(
#         person.bbox,
#         detection.bbox,
#     )

#     distance_score = max(
#         0.0,
#         1.0 - center_distance,
#     )

#     confidence_score = min(
#         1.0,
#         max(
#             0.0,
#             detection.confidence,
#         ),
#     )

#     score = (
#         (0.35 * horizontal_score)
#         + (0.25 * distance_score)
#         + (0.25 * overlap)
#         + (0.15 * confidence_score)
#     )

#     return score


# # ---------------------------------------------------------
# # Main association
# # ---------------------------------------------------------


# def _assign_helmet_detections(
#     tracked_persons: list[TrackedPerson],
#     helmets: list[Detection],
#     min_confidence: float,
# ) -> set[int]:
#     """
#     Assign each helmet detection to at most ONE tracked
#     person.

#     A greedy highest-score assignment is used.

#     This prevents the same helmet detection from being
#     simultaneously assigned to multiple workers.
#     """

#     candidates: list[
#         tuple[
#             float,
#             int,
#             int,
#         ]
#     ] = []

#     for person_index, person in enumerate(
#         tracked_persons
#     ):
#         for helmet_index, helmet in enumerate(
#             helmets
#         ):
#             score = _helmet_score(
#                 person=person,
#                 detection=helmet,
#                 min_confidence=min_confidence,
#             )

#             if score is None:
#                 continue

#             candidates.append(
#                 (
#                     score,
#                     person_index,
#                     helmet_index,
#                 )
#             )

#     # Highest-quality assignments first.
#     candidates.sort(
#         key=lambda item: (
#             -item[0],
#             tracked_persons[
#                 item[1]
#             ].track_id,
#             item[2],
#         )
#     )

#     assigned_people: set[int] = set()
#     assigned_helmets: set[int] = set()

#     helmet_assignments: set[int] = set()

#     for (
#         _score,
#         person_index,
#         helmet_index,
#     ) in candidates:

#         # Each person gets at most one helmet.
#         if person_index in assigned_people:
#             continue

#         # Each helmet can belong to only one person.
#         if helmet_index in assigned_helmets:
#             continue

#         assigned_people.add(
#             person_index
#         )

#         assigned_helmets.add(
#             helmet_index
#         )

#         helmet_assignments.add(
#             person_index
#         )

#     return helmet_assignments


# def _assign_vest_detections(
#     tracked_persons: list[TrackedPerson],
#     vests: list[Detection],
#     min_confidence: float,
# ) -> set[int]:
#     """
#     Assign each vest detection to at most ONE tracked
#     person.

#     This prevents the same vest detection from being shared
#     between overlapping workers.
#     """

#     candidates: list[
#         tuple[
#             float,
#             int,
#             int,
#         ]
#     ] = []

#     for person_index, person in enumerate(
#         tracked_persons
#     ):
#         for vest_index, vest in enumerate(
#             vests
#         ):
#             score = _vest_score(
#                 person=person,
#                 detection=vest,
#                 min_confidence=min_confidence,
#             )

#             if score is None:
#                 continue

#             candidates.append(
#                 (
#                     score,
#                     person_index,
#                     vest_index,
#                 )
#             )

#     candidates.sort(
#         key=lambda item: (
#             -item[0],
#             tracked_persons[
#                 item[1]
#             ].track_id,
#             item[2],
#         )
#     )

#     assigned_people: set[int] = set()
#     assigned_vests: set[int] = set()

#     vest_assignments: set[int] = set()

#     for (
#         _score,
#         person_index,
#         vest_index,
#     ) in candidates:

#         # Each person gets at most one vest.
#         if person_index in assigned_people:
#             continue

#         # Each vest can belong to only one person.
#         if vest_index in assigned_vests:
#             continue

#         assigned_people.add(
#             person_index
#         )

#         assigned_vests.add(
#             vest_index
#         )

#         vest_assignments.add(
#             person_index
#         )

#     return vest_assignments


# def associate_ppe(
#     tracked_persons: list[TrackedPerson],
#     detections: list[Detection],
#     min_helmet_conf: float = 0.40,
#     min_vest_conf: float = 0.40,
#     min_overlap: float = 0.0,
# ) -> list[PPEStatus]:
#     """
#     Associate Helmet and Vest detections with tracked persons.

#     The association is deterministic and one-to-one:

#         one helmet detection -> at most one person
#         one vest detection   -> at most one person

#     Association is based primarily on body-region geometry
#     and secondarily on overlap and detection confidence.

#     Args:
#         tracked_persons:
#             Persons already assigned track IDs by ByteTrack.

#         detections:
#             YOLO detections containing Person, Helmet and Vest.

#         min_helmet_conf:
#             Minimum confidence required for helmet detections.

#         min_vest_conf:
#             Minimum confidence required for vest detections.

#         min_overlap:
#             Kept for API compatibility with earlier versions.

#             The previous implementation depended heavily on
#             this value. The new implementation does not use
#             overlap as a hard gate because helmets may extend
#             above the Person bounding box.

#     Returns:
#         PPEStatus for every tracked person.
#     """

#     if not tracked_persons:
#         return []

#     helmets = [
#         detection
#         for detection in detections
#         if detection.class_name.lower()
#         in {
#             "helmet",
#             "hard_hat",
#             "head_protection",
#         }
#     ]

#     vests = [
#         detection
#         for detection in detections
#         if detection.class_name.lower()
#         in {
#             "vest",
#             "safety_vest",
#             "torso_protection",
#         }
#     ]

#     # -----------------------------------------------------
#     # Determine which tracked person owns each PPE object.
#     # -----------------------------------------------------

#     helmet_assignments = _assign_helmet_detections(
#         tracked_persons=tracked_persons,
#         helmets=helmets,
#         min_confidence=min_helmet_conf,
#     )

#     vest_assignments = _assign_vest_detections(
#         tracked_persons=tracked_persons,
#         vests=vests,
#         min_confidence=min_vest_conf,
#     )

#     # -----------------------------------------------------
#     # Build final status for every tracked person.
#     # -----------------------------------------------------

#     results: list[PPEStatus] = []

#     for person_index, person in enumerate(
#         tracked_persons
#     ):
#         results.append(
#             PPEStatus(
#                 track_id=person.track_id,
#                 helmet_detected=(
#                     person_index
#                     in helmet_assignments
#                 ),
#                 vest_detected=(
#                     person_index
#                     in vest_assignments
#                 ),
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
    """
    PPE state associated with one tracked person.
    """

    track_id: int
    helmet_detected: bool
    vest_detected: bool


# ---------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------


def calculate_overlap_ratio(
    person_box: tuple[float, float, float, float],
    ppe_box: tuple[float, float, float, float],
) -> float:
    """
    Calculate what fraction of the PPE bounding box lies
    inside the person bounding box.

    Boxes use:
        (x1, y1, x2, y2)

    This is used as supporting geometry, not as the only
    association rule.
    """

    px1, py1, px2, py2 = person_box
    bx1, by1, bx2, by2 = ppe_box

    ix1 = max(px1, bx1)
    iy1 = max(py1, by1)
    ix2 = min(px2, bx2)
    iy2 = min(py2, by2)

    intersection_width = max(
        0.0,
        ix2 - ix1,
    )

    intersection_height = max(
        0.0,
        iy2 - iy1,
    )

    intersection_area = (
        intersection_width * intersection_height
    )

    ppe_width = max(
        0.0,
        bx2 - bx1,
    )

    ppe_height = max(
        0.0,
        by2 - by1,
    )

    ppe_area = ppe_width * ppe_height

    if ppe_area <= 0.0:
        return 0.0

    return intersection_area / ppe_area


def _center(
    box: tuple[float, float, float, float],
) -> tuple[float, float]:
    """
    Return the center point of a bounding box.
    """

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
    Calculate normalized distance between the center of the
    person and the center of the PPE object.

    The result is approximately scale-independent because
    distance is normalized by the person dimensions.
    """

    px1, py1, px2, py2 = person_box

    person_width = max(
        1.0,
        px2 - px1,
    )

    person_height = max(
        1.0,
        py2 - py1,
    )

    person_cx, person_cy = _center(person_box)
    ppe_cx, ppe_cy = _center(ppe_box)

    dx = (ppe_cx - person_cx) / person_width
    dy = (ppe_cy - person_cy) / person_height

    return (dx * dx + dy * dy) ** 0.5


def _horizontal_position_score(
    person_box: tuple[float, float, float, float],
    ppe_box: tuple[float, float, float, float],
) -> float:
    """
    Score how well the PPE center is horizontally aligned
    with the person center.

    Returns a value between approximately 0 and 1.
    """

    px1, _, px2, _ = person_box

    person_width = max(
        1.0,
        px2 - px1,
    )

    person_cx, _ = _center(person_box)
    ppe_cx, _ = _center(ppe_box)

    horizontal_distance = abs(
        ppe_cx - person_cx
    ) / person_width

    return max(
        0.0,
        1.0 - horizontal_distance,
    )


# ---------------------------------------------------------
# Candidate scoring
# ---------------------------------------------------------


def _helmet_score(
    person: TrackedPerson,
    detection: Detection,
    min_confidence: float,
) -> float | None:
    """
    Calculate how strongly a helmet detection belongs to a
    tracked person.

    Returns:
        A score when the detection is a valid candidate.
        None when it should not be associated.

    Helmet geometry:
        - helmet must be horizontally close to the person
        - helmet should be around the head region
        - a small amount above the Person box is allowed
        - confidence contributes to the final score
    """

    if detection.confidence < min_confidence:
        return None

    x1, y1, x2, y2 = person.bbox

    width = x2 - x1
    height = y2 - y1

    if width <= 0.0 or height <= 0.0:
        return None

    ppe_cx, ppe_cy = _center(
        detection.bbox
    )

    # -----------------------------------------------------
    # Head region
    #
    # A helmet can extend slightly above the person's
    # detected bounding box, so do not require it to be
    # completely inside the person box.
    # -----------------------------------------------------

    head_x1 = x1 - (0.15 * width)
    head_x2 = x2 + (0.15 * width)

    head_y1 = y1 - (0.20 * height)
    head_y2 = y1 + (0.40 * height)

    if not (
        head_x1 <= ppe_cx <= head_x2
        and
        head_y1 <= ppe_cy <= head_y2
    ):
        return None

    overlap = calculate_overlap_ratio(
        person.bbox,
        detection.bbox,
    )

    horizontal_score = _horizontal_position_score(
        person.bbox,
        detection.bbox,
    )

    center_distance = _normalized_center_distance(
        person.bbox,
        detection.bbox,
    )

    distance_score = max(
        0.0,
        1.0 - center_distance,
    )

    confidence_score = min(
        1.0,
        max(
            0.0,
            detection.confidence,
        ),
    )

    # -----------------------------------------------------
    # Weighted score
    #
    # Geometry is more important than confidence.
    # -----------------------------------------------------

    score = (
        (0.40 * horizontal_score)
        + (0.25 * distance_score)
        + (0.20 * overlap)
        + (0.15 * confidence_score)
    )

    return score


def _vest_score(
    person: TrackedPerson,
    detection: Detection,
    min_confidence: float,
) -> float | None:
    """
    Calculate how strongly a vest detection belongs to a
    tracked person.

    Vest detections should be located in the person's torso
    region.
    """

    if detection.confidence < min_confidence:
        return None

    x1, y1, x2, y2 = person.bbox

    width = x2 - x1
    height = y2 - y1

    if width <= 0.0 or height <= 0.0:
        return None

    ppe_cx, ppe_cy = _center(
        detection.bbox
    )

    # -----------------------------------------------------
    # Torso region
    # -----------------------------------------------------

    torso_x1 = x1 - (0.10 * width)
    torso_x2 = x2 + (0.10 * width)

    torso_y1 = y1 + (0.15 * height)
    torso_y2 = y1 + (0.80 * height)

    if not (
        torso_x1 <= ppe_cx <= torso_x2
        and
        torso_y1 <= ppe_cy <= torso_y2
    ):
        return None

    overlap = calculate_overlap_ratio(
        person.bbox,
        detection.bbox,
    )

    horizontal_score = _horizontal_position_score(
        person.bbox,
        detection.bbox,
    )

    center_distance = _normalized_center_distance(
        person.bbox,
        detection.bbox,
    )

    distance_score = max(
        0.0,
        1.0 - center_distance,
    )

    confidence_score = min(
        1.0,
        max(
            0.0,
            detection.confidence,
        ),
    )

    score = (
        (0.35 * horizontal_score)
        + (0.25 * distance_score)
        + (0.25 * overlap)
        + (0.15 * confidence_score)
    )

    return score


# ---------------------------------------------------------
# Main association
# ---------------------------------------------------------


def _assign_helmet_detections(
    tracked_persons: list[TrackedPerson],
    helmets: list[Detection],
    min_confidence: float,
) -> set[int]:
    """
    Assign each helmet detection to at most ONE tracked
    person.

    A greedy highest-score assignment is used.

    This prevents the same helmet detection from being
    simultaneously assigned to multiple workers.
    """

    candidates: list[
        tuple[
            float,
            int,
            int,
        ]
    ] = []

    for person_index, person in enumerate(
        tracked_persons
    ):
        for helmet_index, helmet in enumerate(
            helmets
        ):
            score = _helmet_score(
                person=person,
                detection=helmet,
                min_confidence=min_confidence,
            )

            if score is None:
                continue

            candidates.append(
                (
                    score,
                    person_index,
                    helmet_index,
                )
            )

    # Highest-quality assignments first.
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
    assigned_helmets: set[int] = set()

    helmet_assignments: set[int] = set()

    for (
        _score,
        person_index,
        helmet_index,
    ) in candidates:

        # Each person gets at most one helmet.
        if person_index in assigned_people:
            continue

        # Each helmet can belong to only one person.
        if helmet_index in assigned_helmets:
            continue

        assigned_people.add(
            person_index
        )

        assigned_helmets.add(
            helmet_index
        )

        helmet_assignments.add(
            person_index
        )

    return helmet_assignments


def _assign_vest_detections(
    tracked_persons: list[TrackedPerson],
    vests: list[Detection],
    min_confidence: float,
) -> set[int]:
    """
    Assign each vest detection to at most ONE tracked
    person.

    This prevents the same vest detection from being shared
    between overlapping workers.
    """

    candidates: list[
        tuple[
            float,
            int,
            int,
        ]
    ] = []

    for person_index, person in enumerate(
        tracked_persons
    ):
        for vest_index, vest in enumerate(
            vests
        ):
            score = _vest_score(
                person=person,
                detection=vest,
                min_confidence=min_confidence,
            )

            if score is None:
                continue

            candidates.append(
                (
                    score,
                    person_index,
                    vest_index,
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
    assigned_vests: set[int] = set()

    vest_assignments: set[int] = set()

    for (
        _score,
        person_index,
        vest_index,
    ) in candidates:

        # Each person gets at most one vest.
        if person_index in assigned_people:
            continue

        # Each vest can belong to only one person.
        if vest_index in assigned_vests:
            continue

        assigned_people.add(
            person_index
        )

        assigned_vests.add(
            vest_index
        )

        vest_assignments.add(
            person_index
        )

    return vest_assignments


def associate_ppe(
    tracked_persons: list[TrackedPerson],
    detections: list[Detection],
    min_helmet_conf: float = 0.40,
    min_vest_conf: float = 0.40,
    min_overlap: float = 0.0,
) -> list[PPEStatus]:
    """
    Associate Helmet and Vest detections with tracked persons.
    Matches front workers first based on Y-axis depth ordering.
    """

    if not tracked_persons:
        return []

    # -----------------------------------------------------
    # DEPTH SORTING (Front-to-Back)
    # The worker lower on the screen (larger y2 / bbox[3]) 
    # is closer to the camera and gets matching priority.
    # -----------------------------------------------------
    sorted_persons = sorted(
        tracked_persons,
        key=lambda person: person.bbox[3],
        reverse=True,
    )

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

    # -----------------------------------------------------
    # Determine which tracked person owns each PPE object.
    # Passing sorted_persons ensures front workers claim PPE first.
    # -----------------------------------------------------

    helmet_assignments = _assign_helmet_detections(
        tracked_persons=sorted_persons,
        helmets=helmets,
        min_confidence=min_helmet_conf,
    )

    vest_assignments = _assign_vest_detections(
        tracked_persons=sorted_persons,
        vests=vests,
        min_confidence=min_vest_conf,
    )

    # -----------------------------------------------------
    # Build final status for every tracked person.
    # -----------------------------------------------------

    results: list[PPEStatus] = []

    for person_index, person in enumerate(sorted_persons):
        results.append(
            PPEStatus(
                track_id=person.track_id,
                helmet_detected=(
                    person_index in helmet_assignments
                ),
                vest_detected=(
                    person_index in vest_assignments
                ),
            )
        )

    return results