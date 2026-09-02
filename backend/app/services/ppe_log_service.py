# from uuid import UUID

# from sqlalchemy.orm import Session

# from app.models.ppe_log import PPEComplianceLog
# from app.services.compliance_state import ComplianceInterval


# def save_compliance_interval(
#     db: Session,
#     interval: ComplianceInterval,
#     video_id: UUID,
# ) -> PPEComplianceLog:
#     """
#     Persist one completed PPE compliance interval.

#     The timestamp values are elapsed seconds inside the source video,
#     not server/system timestamps.
#     """

#     if interval.end_timestamp is None:
#         raise ValueError("Cannot save an open PPE compliance interval.")

#     if interval.end_timestamp < interval.start_timestamp:
#         raise ValueError(
#             "PPE compliance interval end_timestamp cannot be "
#             "earlier than start_timestamp."
#         )

#     log = PPEComplianceLog(
#         worker_id=interval.worker_id,
#         video_id=video_id,
#         start_timestamp=interval.start_timestamp,
#         end_timestamp=interval.end_timestamp,
#         helmet_detected=interval.helmet_detected,
#         vest_detected=interval.vest_detected,
#         compliance_status=interval.status,
#     )

#     db.add(log)

#     return log
from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.ppe_log import PPEComplianceLog
from app.services.compliance_state import ComplianceInterval


def save_compliance_interval(
    db: Session,
    interval: ComplianceInterval,
    video_id: UUID,
    base_time: datetime | None = None,
) -> PPEComplianceLog:
    """
    Persist one completed PPE compliance interval.
    """
    if interval.end_timestamp is None:
        raise ValueError("Cannot save an open PPE compliance interval.")

    if interval.end_timestamp < interval.start_timestamp:
        raise ValueError(
            "PPE compliance interval end_timestamp cannot be "
            "earlier than start_timestamp."
        )

    # Base reference point (defaults to current UTC time)
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    # Convert float video offsets to UTC datetime objects
    start_dt = base_time + timedelta(seconds=interval.start_timestamp)
    end_dt = base_time + timedelta(seconds=interval.end_timestamp)

    # Resolve boolean flags from enum status
    status_str = str(getattr(interval.status, "value", interval.status)).upper()
    if "FULL_PPE" in status_str or status_str == "COMPLIANT":
        helmet_detected, vest_detected = True, True
    elif "HELMET_MISSING" in status_str or "NO_HELMET" in status_str:
        helmet_detected, vest_detected = False, True
    elif "VEST_MISSING" in status_str or "NO_VEST" in status_str:
        helmet_detected, vest_detected = True, False
    else:  # NO_PPE / NON_COMPLIANT
        helmet_detected, vest_detected = False, False

    log = PPEComplianceLog(
        worker_id=interval.worker_id,
        video_id=video_id,
        start_timestamp=start_dt,  # Converts to TIMESTAMPTZ
        end_timestamp=end_dt,      # Converts to TIMESTAMPTZ
        helmet_detected=helmet_detected,
        vest_detected=vest_detected,
        compliance_status=interval.status,
    )

    db.add(log)
    return log