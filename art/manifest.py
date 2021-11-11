import json
import logging
import time
from subprocess import CalledProcessError
from typing import Any, Dict, Optional

from art.config import ArtConfig
from art.files import get_files_for_manifest
from art.git import describe

log = logging.getLogger(__name__)


class Manifest(dict):  # type: ignore[type-arg]
    def as_json_bytes(self) -> bytes:
        return json.dumps(self, sort_keys=True, ensure_ascii=False, indent=2).encode()

    @classmethod
    def generate(cls, config: ArtConfig) -> "Manifest":
        rev_description: Optional[Dict[str, Any]]
        try:
            rev_description = describe(config)
        except CalledProcessError:
            rev_description = None

        data = {
            "ctime": time.time(),
            "rev": rev_description,
            "name": config.name,
            "repo": {"url": config.repo_url, "ref": config.ref},
            "files": get_files_for_manifest(config),
        }
        return cls(data)
