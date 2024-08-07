from __future__ import annotations

import dataclasses

from art.cloudfront import execute_cloudfront_invalidations


@dataclasses.dataclass(frozen=True)
class ArtContext:
    dry_run: bool = False
    _cloudfront_invalidations: dict[str, set[str]] = dataclasses.field(default_factory=dict)

    def add_cloudfront_invalidation(self, dist_id: str, path: str) -> None:
        self._cloudfront_invalidations.setdefault(dist_id, set()).add(path)

    def execute_post_run_tasks(self) -> None:
        if self._cloudfront_invalidations:
            execute_cloudfront_invalidations(self._cloudfront_invalidations)
            self._cloudfront_invalidations.clear()
