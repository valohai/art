import argparse
import atexit
import logging
import os
import shutil
import tempfile

from art.config import ArtConfig, FileMapEntry
from art.git import git_clone
from art.manifest import generate_manifest
from art.prepare import run_prepare, update_config_from_work_dir
from art.write import write


def get_argument_parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--git-source")
    ap.add_argument("--git-ref", default="master")
    ap.add_argument("--local-source")
    ap.add_argument("--dest", "-d")
    ap.add_argument("--suffix", "-s", dest="suffixes", action="append")
    ap.add_argument("--suffix-description", action="store_true")
    ap.add_argument(
        "--debug", dest="log_level", const=logging.DEBUG, action="store_const"
    )
    ap.add_argument("--file", dest="files", action="append")
    return ap


def run_command(argv=None):
    ap = get_argument_parser()
    args = ap.parse_args(argv)
    logging.basicConfig(level=(args.log_level or logging.INFO))

    config = ArtConfig()
    config.update_from({"dest": args.dest})
    if args.git_source:
        config.repo_url = args.git_source
        config.ref = args.git_ref
        config.work_dir = tempfile.mkdtemp(prefix="art-git-")
        git_clone(config)
        atexit.register(shutil.rmtree, config.work_dir)
    elif args.local_source:
        config.repo_url = config.work_dir = os.path.abspath(args.local_source)
    else:
        ap.error("Either a git source or a local source must be defined")

    update_config_from_work_dir(config)
    if not config.dest:
        ap.error("No destination specified (on command line or in config in source)")

    if config.dest.startswith("./"):
        config.dest = os.path.abspath(config.dest)

    for file in args.files or ():
        config.file_map.append(FileMapEntry(source=file))

    run_prepare(config)
    manifest = generate_manifest(config)
    if not manifest["files"]:
        ap.error("No files were copied (use config or --file?)")
    suffixes = []
    if args.suffix_description and manifest["rev"]["description"]:
        suffixes.append(manifest["rev"]["description"])
    suffixes.extend(args.suffixes or ())
    if not suffixes:
        raise ValueError("No write destinations (use --suffix?)")
    for suffix in suffixes:
        write(config, dest=config.dest, path_suffix=suffix, manifest=manifest)


if __name__ == "__main__":
    run_command()
