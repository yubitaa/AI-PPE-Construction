from dataclasses import dataclass
from uuid import UUID

from app.models.ppe_log import PPEStatus


@dataclass
class TemporalPPEState:
    """
    Temporal state for one worker.

    stable_status:
        The PPE status currently trusted by the system.

    candidate_status:
        A newly observed status that has not yet remained
        stable long enough to be accepted.

    candidate_count:
        Number of consecutive processed observations that
        produced candidate_status.
    """

    stable_status: PPEStatus | None = None
    candidate_status: PPEStatus | None = None
    candidate_count: int = 0


class PPETemporalFilter:
    """
    Prevents short-lived PPE detection errors from changing
    the worker's compliance state.

    A new status must be observed for a configurable number
    of consecutive processed frames before it becomes the
    stable status.

    Example:

        FULL
        FULL
        HELMET_MISSING
        FULL
        FULL

    remains:

        FULL

    when required_confirmations is 2 or greater.

    But:

        FULL
        FULL
        HELMET_MISSING
        HELMET_MISSING

    becomes:

        FULL -> HELMET_MISSING

    when required_confirmations == 2.
    """

    def __init__(
        self,
        required_confirmations: int = 2,
    ) -> None:
        if required_confirmations < 1:
            raise ValueError(
                "required_confirmations must be at least 1."
            )

        self.required_confirmations = (
            required_confirmations
        )

        self._states: dict[
            UUID,
            TemporalPPEState,
        ] = {}

    def update(
        self,
        worker_id: UUID,
        observed_status: PPEStatus,
    ) -> PPEStatus | None:
        """
        Process one new PPE observation.

        Returns:

            PPEStatus
                when the stable status changes.

            None
                when there is no stable status change.

        The first observation for a worker becomes the initial
        stable status immediately. This prevents the system
        from waiting before establishing the worker's initial
        compliance state.
        """

        state = self._states.setdefault(
            worker_id,
            TemporalPPEState(),
        )

        # -------------------------------------------------
        # First observation.
        # -------------------------------------------------

        if state.stable_status is None:
            state.stable_status = observed_status
            state.candidate_status = None
            state.candidate_count = 0

            return observed_status

        # -------------------------------------------------
        # Observation agrees with current stable state.
        #
        # Any pending transition is cancelled.
        # -------------------------------------------------

        if observed_status == state.stable_status:
            state.candidate_status = None
            state.candidate_count = 0

            return None

        # -------------------------------------------------
        # New candidate status.
        # -------------------------------------------------

        if (
            state.candidate_status
            != observed_status
        ):
            state.candidate_status = observed_status
            state.candidate_count = 1

            return None

        # -------------------------------------------------
        # Same candidate seen again.
        # -------------------------------------------------

        state.candidate_count += 1

        if (
            state.candidate_count
            < self.required_confirmations
        ):
            return None

        # -------------------------------------------------
        # Candidate has now been stable long enough.
        # Accept the transition.
        # -------------------------------------------------

        previous_status = state.stable_status

        state.stable_status = observed_status
        state.candidate_status = None
        state.candidate_count = 0

        # Only return the newly accepted state.
        if previous_status != observed_status:
            return observed_status

        return None

    def get_stable_status(
        self,
        worker_id: UUID,
    ) -> PPEStatus | None:
        """
        Return the currently trusted PPE status.
        """

        state = self._states.get(worker_id)

        if state is None:
            return None

        return state.stable_status

    def reset_worker(
        self,
        worker_id: UUID,
    ) -> None:
        """
        Remove temporal state for one worker.
        """

        self._states.pop(
            worker_id,
            None,
        )

    def reset_all(self) -> None:
        """
        Remove temporal state for all workers.
        """

        self._states.clear()

    def active_workers(self) -> list[UUID]:
        """
        Return worker IDs currently tracked by the temporal
        filter.
        """

        return list(
            self._states.keys()
        )