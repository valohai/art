import argparse
import atexit
import logging
import os
import shutil
import tempfile
from typing import List, Optional

from art.config import ArtConfig, FileMapEntry
from art.excs import Problem
from art.git import git_clone
from art.manifest import Manifest
from art.prepare import fork_configs_from_work_dir, run_prepare
from art.wrap import create_wrapfile
from art.write import write


def get_argument_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    source_group = ap.add_argument_group("Source options")
    source_group.add_argument(
        "--git-source", metavar="URL", help="Git repository URL (passed to `git clone`)"
    )
    source_group.add_argument(
        "--git-ref", default="master", help="Git reference (default %(default)s)"
    )
    source_group.add_argument("--local-source", help="Local source path")
    source_group.add_argument(
        "--config-file",
        default="art.yaml",
        help="Configuration filename within the source (default %(default)s)",
    )

    dest_group = ap.add_argument_group("Destination options")

    dest_group.add_argument(
        "--dest",
        "-d",
        dest="dests",
        default=[],
        action="append",
        help="Destination base path, e.g. `./dist`, `s3://artifacts/foo",
    )
    dest_group.add_argument(
        "--suffix",
        "-s",
        dest="suffixes",
        action="append",
        help="Destination suffix (e.g. `release`)",
    )
    dest_group.add_argument(
        "--suffix-description",
        action="store_true",
        help="Attempt to derive a suffix from the `git describe` of the source",
    )
    ap.add_argument(
        "--debug",
        dest="log_level",
        const=logging.DEBUG,
        action="store_const",
        help="Be debuggingly verbose",
    )
    ap.add_argument(
        "--file",
        dest="files",
        action="append",
        default=[],
        help=(
            "Add a file glob for adding to the destination. "
            "You should probably use a configuration file instead."
        ),
    )
    return ap


def run_command(argv: Optional[List[str]] = None) -> None:
    ap = get_argument_parser()
    args = ap.parse_args(argv)
    logging.basicConfig(level=(args.log_level or logging.INFO))

    config_args = {"dests": list(args.dests), "name": ""}
    is_git = False
    if args.git_source:
        config_args.update(
            repo_url=args.git_source,
            ref=args.git_ref,
            work_dir=tempfile.mkdtemp(prefix="art-git-"),
        )
        is_git = True
    elif args.local_source:
        work_dir = os.path.abspath(args.local_source)
        config_args.update(
            repo_url=work_dir,
            work_dir=work_dir,
        )
    else:
        ap.error("Either a git source or a local source must be defined")

    config = ArtConfig(**config_args)  # type: ignore[arg-type]

    if is_git:
        git_clone(config)
        atexit.register(shutil.rmtree, config.work_dir)

    for config in fork_configs_from_work_dir(config, filename=args.config_file):
        try:
            process_config_postfork(args, config)
        except Problem as p:
            ap.error("config %s: %s" % (config.name, p))


def clean_dest(dest: str) -> str:
    if dest.startswith("./"):
        dest = os.path.abspath(dest)
    return dest


def process_config_postfork(args: argparse.Namespace, config: ArtConfig) -> None:
    if not config.dests:
        raise Problem(
            "No destination(s) specified (on command line or in config in source)"
        )
    config.dests = [clean_dest(dest) for dest in config.dests]
    for file in args.files:
        config.file_map.append(FileMapEntry(source=file))
    run_prepare(config)
    manifest = Manifest.generate(config)
    if not manifest["files"]:
        raise Problem("No files were copied (use config or --file?)")
    suffixes = []
    if args.suffix_description and manifest["rev"]["description"]:
        suffixes.append(manifest["rev"]["description"])
    suffixes.extend(args.suffixes or ())
    if not suffixes:
        raise Problem("No write destinations (use --suffix?)")
    wrap_temp = create_wrapfile(config, manifest)
    for dest in config.dests:
        for suffix in suffixes:
            write(
                config,
                dest=dest,
                path_suffix=suffix,
                manifest=manifest,
                wrap_filename=wrap_temp,
            )
    if wrap_temp:
        os.unlink(wrap_temp)


if __name__ == "__main__":
    run_command()
