import json
import logging
import time
from subprocess import CalledProcessError

from art.files import get_files_for_manifest
from art.git import describe

log = logging.getLogger(__name__)


class Manifest(dict):
    def as_json_bytes(self):
        return json.dumps(
            self, sort_keys=True, ensure_ascii=False, indent=2
        ).encode()

    @classmethod
    def generate(cls, config):
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
