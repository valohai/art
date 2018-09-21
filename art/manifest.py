import logging
import time
from subprocess import CalledProcessError

from art.files import get_files_for_manifest
from art.git import describe

log = logging.getLogger(__name__)


def generate_manifest(config):
    try:
        rev_description = describe(config)
    except CalledProcessError:
        rev_description = None

    return {
        "ctime": time.time(),
        "rev": rev_description,
        "name": config.name,
        "repo": {"url": config.repo_url, "ref": config.ref},
        "files": get_files_for_manifest(config),
    }
