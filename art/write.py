import io
import logging
import os
import posixpath
import shutil
from typing import IO, Any, Callable, Dict, Optional
from urllib.parse import parse_qsl

from art.config import ArtConfig
from art.manifest import Manifest
from art.s3 import s3_write

log = logging.getLogger(__name__)


def _write_file(
    dest: str,
    source_fp: IO[bytes],
    *,
    options: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
) -> None:
    if options is None:
        options = {}
    writer = _get_writer_for_dest(dest)
    writer(dest, source_fp, options=options, dry_run=dry_run)


def _get_writer_for_dest(dest: str) -> Callable:  # type: ignore[type-arg]
    if dest.startswith("s3://"):
        return s3_write
    if dest.startswith("/"):  # Local path
        return local_write
    raise ValueError(f"Invalid destination: {dest}")


def local_write(dest: str, source_fp: IO[bytes], *, options: Dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        log.info("Dry-run: Would have written local file %s", dest)
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as dest_fp:
        shutil.copyfileobj(source_fp, dest_fp)
    log.info("Wrote to local file: %s", dest)


def write(
    config: ArtConfig,
    *,
    dest: str,
    path_suffix: str,
    manifest: Manifest,
    dry_run: bool,
    wrap_filename: Optional[str] = None,
) -> None:
    options = {}
    if "?" in dest:
        dest, options_str = dest.split("?", 2)
        options.update(dict(parse_qsl(options_str)))

    dest = posixpath.join(dest, path_suffix)
    for dest_filename, fileinfo in manifest["files"].items():
        dest_path = posixpath.join(dest, dest_filename)
        local_path = os.path.join(config.work_dir, fileinfo["path"])
        with open(local_path, "rb") as infp:
            _write_file(dest_path, infp, options=options, dry_run=dry_run)

    _write_file(
        dest=posixpath.join(dest, ".manifest.json"),
        source_fp=io.BytesIO(manifest.as_json_bytes()),
        options=options,
        dry_run=dry_run,
    )

    if config.wrap and wrap_filename:
        with open(wrap_filename, "rb") as infp:
            _write_file(
                dest=posixpath.join(dest, config.wrap),
                source_fp=infp,
                options=options,
                dry_run=dry_run,
            )
