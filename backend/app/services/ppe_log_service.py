from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ppe_log import PPEComplianceLog
from app.services.compliance_state import ComplianceInterval


def save_compliance_interval(
    db: Session,
    interval: ComplianceInterval,
    video_id: UUID,
) -> PPEComplianceLog:
    """
    Persist one completed PPE compliance interval.

    start_timestamp and end_timestamp represent elapsed seconds
    inside the analyzed video.

    Example:

        start_timestamp = 12.5
        end_timestamp   = 18.0

    These values must remain numeric video offsets. They must not
    be converted into datetime values.
    """

    if interval.end_timestamp is None:
        raise ValueError(
            "Cannot save an open PPE compliance interval."
        )

    start_timestamp = float(
        interval.start_timestamp
    )

    end_timestamp = float(
        interval.end_timestamp
    )

    if end_timestamp < start_timestamp:
        raise ValueError(
            "PPE compliance interval end_timestamp cannot be "
            "earlier than start_timestamp."
        )

    status = interval.status

    if status.value == "FULL_PPE":
        helmet_detected = True
        vest_detected = True

    elif status.value == "HELMET_MISSING":
        helmet_detected = False
        vest_detected = True

    elif status.value == "VEST_MISSING":
        helmet_detected = True
        vest_detected = False

    elif status.value == "NO_PPE":
        helmet_detected = False
        vest_detected = False

    else:
        raise ValueError(
            f"Unsupported PPE compliance status: {status}"
        )

    log = PPEComplianceLog(
        worker_id=interval.worker_id,
        video_id=video_id,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        helmet_detected=helmet_detected,
        vest_detected=vest_detected,
        compliance_status=status,
    )

    db.add(log)

    return log