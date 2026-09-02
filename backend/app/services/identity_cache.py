from dataclasses import dataclass
from uuid import UUID


@dataclass
class CachedIdentity:
    """
    Identity information associated with an active ByteTrack track.
    """

    track_id: int
    worker_id: UUID


class IdentityCache:
    """
    Maps ByteTrack track IDs to worker UUIDs.

    Identity is cached separately from PPE compliance state.

    UNKNOWN identities are never stored.
    """

    def __init__(self) -> None:
        self._cache: dict[int, CachedIdentity] = {}

    def get(self, track_id: int) -> UUID | None:
        """
        Return the worker UUID associated with a track.

        Returns None when the track has not been identified.
        """

        identity = self._cache.get(track_id)

        if identity is None:
            return None

        return identity.worker_id

    def set(
        self,
        track_id: int,
        worker_id: UUID,
    ) -> None:
        """
        Store a valid track_id -> worker_id relationship.
        """

        self._cache[track_id] = CachedIdentity(
            track_id=track_id,
            worker_id=worker_id,
        )

    def contains(self, track_id: int) -> bool:
        """
        Check whether this track already has an identity.
        """

        return track_id in self._cache

    def remove(self, track_id: int) -> None:
        """
        Remove a track from the identity cache.
        """

        self._cache.pop(track_id, None)

    def clear(self) -> None:
        """
        Clear all cached identities.
        """

        self._cache.clear()

    def active_tracks(self) -> list[int]:
        """
        Return all currently cached track IDs.
        """

        return list(self._cache.keys())