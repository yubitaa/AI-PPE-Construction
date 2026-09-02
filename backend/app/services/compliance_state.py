from dataclasses import dataclass
from uuid import UUID

from app.models.ppe_log import PPEStatus


@dataclass
class ComplianceInterval:
    """
    One continuous PPE compliance period for a worker.
    """

    worker_id: UUID
    status: PPEStatus
    start_timestamp: float
    end_timestamp: float | None = None


@dataclass
class WorkerComplianceState:
    """
    Current open compliance interval for a worker.
    """

    worker_id: UUID
    current_status: PPEStatus
    interval_start: float


class ComplianceStateManager:
    """
    Maintains the current PPE compliance state for each worker.

    The manager does not write directly to PostgreSQL.

    It determines when:
        - an interval starts
        - an interval continues
        - an interval closes
        - a new interval starts after a state change
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
        Update a worker's current compliance state.

        Returns a completed interval only when the compliance
        state changes.
        """

        current = self._states.get(worker_id)

        # First observation.
        if current is None:
            self._states[worker_id] = WorkerComplianceState(
                worker_id=worker_id,
                current_status=status,
                interval_start=timestamp,
            )

            return None

        # Same state:
        # keep the existing interval open.
        if current.current_status == status:
            return None

        # State changed:
        # close the previous interval.
        completed_interval = ComplianceInterval(
            worker_id=worker_id,
            status=current.current_status,
            start_timestamp=current.interval_start,
            end_timestamp=timestamp,
        )

        # Start the new interval.
        self._states[worker_id] = WorkerComplianceState(
            worker_id=worker_id,
            current_status=status,
            interval_start=timestamp,
        )

        return completed_interval

    def close_worker(
        self,
        worker_id: UUID,
        timestamp: float,
    ) -> ComplianceInterval | None:
        """
        Close the worker's currently open interval.

        Used when:
            - the worker disappears permanently
            - the video ends
        """

        current = self._states.pop(worker_id, None)

        if current is None:
            return None

        return ComplianceInterval(
            worker_id=worker_id,
            status=current.current_status,
            start_timestamp=current.interval_start,
            end_timestamp=timestamp,
        )

    def get_state(
        self,
        worker_id: UUID,
    ) -> WorkerComplianceState | None:
        """
        Return the worker's current compliance state.
        """

        return self._states.get(worker_id)

    def active_workers(self) -> list[UUID]:
        """
        Return workers that currently have an open interval.
        """

        return list(self._states.keys())