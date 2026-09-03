from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class CachedIdentity:
    track_id: int
    worker_id: UUID


class IdentityCache:
    """
    Associates a ByteTrack track ID with a known worker.

    Unknown identities are never stored.

    Track IDs are intentionally treated as temporary tracking identities,
    not permanent worker identities. The monitor removes them when a
    track has been absent long enough.
    """

    def __init__(self) -> None:
        self._cache: dict[int, CachedIdentity] = {}

    def get(self, track_id: int) -> UUID | None:
        cached = self._cache.get(track_id)

        if cached is None:
            return None

        return cached.worker_id

    def set(
        self,
        track_id: int,
        worker_id: UUID,
    ) -> None:
        self._cache[track_id] = CachedIdentity(
            track_id=track_id,
            worker_id=worker_id,
        )

    def contains(self, track_id: int) -> bool:
        return track_id in self._cache

    def remove(self, track_id: int) -> UUID | None:
        cached = self._cache.pop(track_id, None)

        if cached is None:
            return None

        return cached.worker_id

    def clear(self) -> None:
        self._cache.clear()

    def active_tracks(self) -> list[int]:
        return list(self._cache.keys())

    def get_cached_identity(
        self,
        track_id: int,
    ) -> CachedIdentity | None:
        """
        Return the complete cached record when the caller needs both
        the track ID and worker ID.
        """
        return self._cache.get(track_id)

    def worker_tracks(self, worker_id: UUID) -> list[int]:
        """
        Return all currently cached track IDs associated with a worker.
        """

        return [
            track_id
            for track_id, cached in self._cache.items()
            if cached.worker_id == worker_id
        ]