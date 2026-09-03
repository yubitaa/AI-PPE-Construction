from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.models.ppe_log import PPEStatus


@dataclass
class ComplianceInterval:
    worker_id: UUID
    status: PPEStatus
    start_timestamp: float
    end_timestamp: float | None = None


@dataclass
class WorkerComplianceState:
    worker_id: UUID
    current_status: PPEStatus
    interval_start: float


class ComplianceStateManager:
    """
    Maintains one active PPE compliance interval per worker.

    Timestamps are always video-relative seconds.
    """

    def __init__(self) -> None:
        self._states: dict[UUID, WorkerComplianceState] = {}

    def update(
        self,
        worker_id: UUID,
        status: PPEStatus,
        timestamp: float,
    ) -> ComplianceInterval | None:
        """
        Update a worker's stable compliance state.

        If the status has not changed, nothing is closed.

        If the status changes, the previous interval is completed
        at the supplied video timestamp and the new interval begins
        at that same timestamp.
        """

        current = self._states.get(worker_id)

        if current is None:
            self._states[worker_id] = WorkerComplianceState(
                worker_id=worker_id,
                current_status=status,
                interval_start=float(timestamp),
            )
            return None

        if current.current_status == status:
            return None

        completed = ComplianceInterval(
            worker_id=worker_id,
            status=current.current_status,
            start_timestamp=current.interval_start,
            end_timestamp=float(timestamp),
        )

        self._states[worker_id] = WorkerComplianceState(
            worker_id=worker_id,
            current_status=status,
            interval_start=float(timestamp),
        )

        return completed

    def close_worker(
        self,
        worker_id: UUID,
        timestamp: float | None,
    ) -> ComplianceInterval | None:
        """
        Close the worker's active interval.

        When timestamp is provided, it is the video-relative moment
        at which the worker's tracked presence ended.

        If timestamp is None, the interval is closed using its existing
        start timestamp. This is only a defensive fallback; normal
        video processing should provide the actual final timestamp.
        """

        current = self._states.pop(worker_id, None)

        if current is None:
            return None

        end_timestamp = (
            float(timestamp)
            if timestamp is not None
            else current.interval_start
        )

        # Never produce a negative-duration interval.
        if end_timestamp < current.interval_start:
            end_timestamp = current.interval_start

        return ComplianceInterval(
            worker_id=worker_id,
            status=current.current_status,
            start_timestamp=current.interval_start,
            end_timestamp=end_timestamp,
        )

    def get_state(
        self,
        worker_id: UUID,
    ) -> WorkerComplianceState | None:
        return self._states.get(worker_id)

    def active_workers(self) -> list[UUID]:
        return list(self._states.keys())

    def clear(self) -> None:
        self._states.clear()