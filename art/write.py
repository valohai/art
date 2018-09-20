import io
import json
import logging
import os
import posixpath
import shutil

from art.s3 import s3_write

log = logging.getLogger(__name__)


def _write_file(dest, source_fp):
    if dest.startswith("s3://"):
        s3_write(dest, source_fp)
    elif dest.startswith("/"):  # Local path
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as dest_fp:
            shutil.copyfileobj(source_fp, dest_fp)
        log.info("Wrote to local file: %s", dest)
    else:
        raise ValueError("Invalid destination: %s" % dest)


def write(config, *, dest, path_suffix, manifest):
    dest = posixpath.join(dest, path_suffix)
    for dest_filename, fileinfo in manifest["files"].items():
        dest_path = posixpath.join(dest, dest_filename)
        with open(os.path.join(config.work_dir, fileinfo["path"]), "rb") as infp:
            _write_file(dest_path, infp)
    manifest_data = json.dumps(
        manifest, sort_keys=True, ensure_ascii=False, indent=2
    ).encode()
    _write_file(posixpath.join(dest, ".manifest.json"), io.BytesIO(manifest_data))
