import io
import logging
import os
import tarfile
import tempfile
from typing import Optional

from art.config import ArtConfig
from art.manifest import Manifest

log = logging.getLogger(__name__)


def create_wrapfile(config: ArtConfig, manifest: Manifest) -> Optional[str]:
    if not config.wrap:
        return None
    wrap_temp = tempfile.mktemp(prefix="art-wrap-", suffix=".tar")
    wrap_tar = tarfile.open(wrap_temp, "w")
    wrap_tar.addfile(
        tarinfo=tarfile.TarInfo(name=".manifest.json"),
        fileobj=io.BytesIO(manifest.as_json_bytes()),
    )
    for dest_filename, fileinfo in manifest["files"].items():
        local_path = os.path.join(config.work_dir, fileinfo["path"])
        wrap_tar.add(local_path, dest_filename)
    wrap_tar.close()
    log.info("Created wrapfile: %d bytes" % os.stat(wrap_temp).st_size)
    return wrap_temp
