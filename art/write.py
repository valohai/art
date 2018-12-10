import io
import logging
import os
import posixpath
import shutil
from urllib.parse import parse_qsl

from art.s3 import s3_write

log = logging.getLogger(__name__)


def _write_file(dest, source_fp, options=None):
    if options is None:
        options = {}
    if dest.startswith("s3://"):
        s3_write(dest, source_fp, options=options)
    elif dest.startswith("/"):  # Local path
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as dest_fp:
            shutil.copyfileobj(source_fp, dest_fp)
        log.info("Wrote to local file: %s", dest)
    else:
        raise ValueError("Invalid destination: %s" % dest)


def write(config, *, dest, path_suffix, manifest, wrap_filename=None):
    if "?" in dest:
        dest, options = dest.split("?", 2)
        options = dict(parse_qsl(options))
    else:
        options = {}

    dest = posixpath.join(dest, path_suffix)
    for dest_filename, fileinfo in manifest["files"].items():
        dest_path = posixpath.join(dest, dest_filename)
        local_path = os.path.join(config.work_dir, fileinfo["path"])
        with open(local_path, "rb") as infp:
            _write_file(dest_path, infp, options=options)

    _write_file(
        dest=posixpath.join(dest, ".manifest.json"),
        source_fp=io.BytesIO(manifest.as_json_bytes()),
        options=options,
    )

    if config.wrap and wrap_filename:
        with open(wrap_filename, "rb") as infp:
            _write_file(
                dest=posixpath.join(dest, config.wrap), source_fp=infp, options=options
            )
