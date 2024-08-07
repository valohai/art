from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class ArtContext:
    dry_run: bool = False
